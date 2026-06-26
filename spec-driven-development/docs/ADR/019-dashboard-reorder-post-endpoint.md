---
id: ADR-019
type: spec
status: accepted
owner: principal-architect
updated: 2026-06-27
feature: SDD-041
---

# ADR-019: Dashboard `POST /reorder` write endpoint -- localhost-only, hash-pinned drag script, force-free

- Date: 2026-06-26
- Status: **Accepted** (owner pre-approved autonomous start of F-31; design ratified in this ADR)
- Authors: Principal Software Developer (SDD-041 / F-31 implementation slot)
- Feature: SDD-041 (true browser drag-and-drop backlog reorder)
- Builds on: ADR-017 (backlog reorder safeguards), SDD-036 (lifecycle pipeline + keyboard reorder control)

## Context

SDD-036 shipped a keyboard-accessible reorder control (`render_reorder_control`) whose buttons print a `python cli/backlog_reorder.py move ...` command for the human to run. The owner asked for the next increment: **true pointer drag-and-drop** on the live dashboard, so a leader can drag a lifecycle card to a new rank in-meeting without copying a CLI command.

Three hard constraints shape the design:

1. **Article X footprint lock.** `render_html` and the four other S1 functions are byte-locked to commit `257b081` (`TestS1FootprintLockGuard`). The drag layer cannot touch them; it must be additive post-processing of their output.
2. **Article V stdlib-only / no JS framework.** No third-party Python deps and no JavaScript framework. The drag handler must be vanilla `http.server` + vanilla JS.
3. **Reorder safeguards (ADR-017).** The dashboard already has a safeguarded mutator -- `backlog_reorder.move` -- that enforces the dependency-lock, appends an append-only audit row, and treats `--force` as a Level-2 human escalation. The drag layer must reuse it verbatim, not re-implement ordering logic.

Until now `DashboardHandler` was read-only (`do_GET` only). A drag gesture needs a write path, which is a new pattern (the dashboard mutating state) and therefore an ADR-worthy Level-1 decision.

## Decision

1. **`POST /reorder` is the only write endpoint.** `DashboardHandler.do_POST` routes `POST /reorder` and nothing else (any other path -> 404). `do_GET` is unchanged. The body is `{"item": "<FEATURE-ID>", "to_rank": <int>}` JSON.
2. **Localhost-only.** `serve()` binds `127.0.0.1` (unchanged). The write endpoint is reachable only from the operator's own machine; it is not exposed on a routable interface.
3. **Validation before mutation, via a pure helper.** `handle_reorder_request(sdd_root, payload) -> (status, body)` is a pure, unit-testable function. It rejects (400) a non-dict payload, an `item` not matching `^[A-Z]{2,}-\d{2,3}$`, or a `to_rank` that is not a non-negative `int` (`bool` is rejected even though it subclasses `int`). It then delegates to `backlog_reorder.move(sdd_root, item=item, to_rank=to_rank, force=force)`.
4. **Force is never auto-applied by a drag gesture (ADR-017).** The injected JS posts only `{item, to_rank}` -- there is no `force` field on the wire. A dependency-locked move returns **409** `{"status":"blocked","reason":...}`; the UI surfaces the reason and tells the operator that forcing is a Level-2 decision to be done with the CLI `--force`. The endpoint accepts an explicit `force` only from a deliberate non-drag client; it is never synthesized server-side or by the drag layer.
5. **One hash-pinned vanilla-JS block.** `inject_drag_html` appends exactly one `<script>` (the drag handlers + the `fetch('/reorder', ...)` call) and is wired as the LAST inject step in `build()`. The script:
   - is **inert as a static file** -- it no-ops unless `location.protocol` is `http(s)`, so the `file://` `state.html` stays keyboard-only;
   - is **CSP-pinned by sha256 hash, never `'unsafe-inline'`**. The hash is computed at import time over the exact script body, so editing the body re-pins automatically and any tamper fails closed under browser CSP enforcement.
6. **CSP widened only for that one script.** The locked `render_html` meta CSP is `default-src 'none'; style-src 'unsafe-inline'; img-src 'self'` -- no `script-src` and no `connect-src`. `inject_drag_html` post-processes the assembled document (NOT `render_html`) to append `script-src 'sha256-<hash>'` and `connect-src 'self'` to the meta CSP, and `DashboardHandler._send` adds the same `script-src 'sha256-<hash>'` to the response-header CSP. The browser enforces the intersection of both, so the inline handler and its same-origin POST are permitted while everything else stays denied.

## Consequences

- Positive: drag-to-reorder works on the live (`http://127.0.0.1`) dashboard while every move still flows through the ADR-017 safeguards (dependency-lock + append-only audit). No ordering logic is duplicated.
- Positive: the static `state.html` is unchanged in spirit -- still keyboard-operable, drag script inert -- so opening the file offline is safe and identical to before plus one dormant script.
- Positive: no `'unsafe-inline'` for scripts. The single script is hash-pinned; the CSP surface grows by exactly one hash plus `connect-src 'self'`.
- Positive: `render_html` and the S1 lock are untouched (`TestS1FootprintLockGuard` stays PASS); all new behavior lives in additive helpers, `inject_drag_html`, and the HTTP handler.
- Negative: the dashboard is no longer strictly read-only -- it has one mutating route. Mitigated by localhost-only binding, strict input validation, the single-route allowlist, and reuse of the safeguarded mutator.
- Negative: live drag interaction cannot be proven by the Python test suite -- the visual feel requires a human in a browser. The tests prove the wire contract (validation, status codes, audit delegation, force-never-sent), the single-script invariant, the CSP widening, and the static inertness; in-browser drag acceptance is a human step.

## Correction (rebuild)

- Date: 2026-06-27
- Status: still **Accepted** -- this corrects the render surface only; the write endpoint, validation helper, safeguarded mutator, CSP hash-pin, and force-free wire contract above are all unchanged and correct.

The first SDD-041 increment wired the drag layer onto the **lifecycle cards**. Three render-side defects made it non-functional for the owner, none of them in the endpoint:

1. **Wrong key.** Draggable lifecycle cards carried spec-directory names, not the canonical `SDD-xxx` ids. The posted `item` failed `handle_reorder_request`'s `^[A-Z]{2,}-\d{2,3}$` gate, so every drop returned **400**.
2. **Wrong targets.** The cards surfaced already-DONE features, so even a valid move had no prioritization value.
3. **Dead buttons.** The up/down controls did not post to `/reorder`.

The endpoint (`handle_reorder_request`, `do_POST`), `backlog_reorder.move`, the CSP hash-pin, and the force policy were all correct -- the fault was purely the render/key surface. The rebuild therefore:

- Adds a **dedicated, visible Backlog section** (`inject_backlog_reorder_html`, `<section class="zone-backlog-reorder">` with `<h2 id="backlog-reorder-heading">`) injected into the assembled document, keyed by the **canonical `SDD-xxx` ids** from `backlog_reorder.load_order` (overlay-aware, includes DONE for rank-correctness).
- Makes the section an **OPEN-only priorities view**: it renders **only OPEN rows** (`<div class="backlog-row" draggable="true" data-pid="SDD-xxx" data-rank="N">`), each carrying a **real description** -- `id + title + priority + status` (`backlog-title`/`backlog-priority`/`backlog-status` spans, never a bare duplicated id) -- plus a working `data-to-rank` up/down button pair (`_render_backlog_buttons`). **DONE rows are not rendered at all** (Option A); the section is a clean list of work that still needs ranking.
- **Descriptions come from an additive metadata helper.** `_backlog_reorder_meta(sdd_root)` seeds titles/priority/status from the canonical `load_backlog` items, then positionally parses every BACKLOG.md table row (tolerant of the variable 10-vs-11 column `--`-RICE rows) so even rows `load_backlog`'s numeric-RICE regex skips still get a real title and status. This is why no shown row falls back to a bare id. `load_backlog` itself is left untouched (no markdown-view scope creep).
- **Button targets use full-order indices.** `data-rank` is each item's absolute index in the full overlay-aware `load_order` (DONE included, for rank-correctness); the up/down buttons point at the **adjacent OPEN item's full-order index**, so a move skips over any interleaved DONE id and still posts a valid absolute `to_rank` to `move()`.
- **Removes lifecycle-card drag entirely** -- lifecycle cards are static again; the reorder affordance lives only in the Backlog section. `inject_backlog_reorder_html` runs immediately before `inject_drag_html` (still the last inject) so its draggable rows arm the existing drag + CSP layer; the drag script selector is `.backlog-row[draggable="true"]` and button wiring is `.backlog-up,.backlog-down`.
- **OPEN/DONE rule (stated assumption):** a row is OPEN (shown + draggable) iff its BACKLOG.md line does not contain the token `DONE` -- the same rule `backlog_reorder.load_backlog_entries` uses. IMPLEMENTED/Approved/Design/Pending all count as OPEN; only `DONE` is excluded from the render.
- **Cross-project ids removed from source.** Six `IAI-0x` rows (insights_ai retrospective intake) were stale contamination in `backlog/BACKLOG.md` and in the `backlog/display-order.json` overlay; both sources are cleaned so the regenerated `exec/state.{md,html}` and `exec/work-index.md` carry only `SDD-xxx` ids.
- **Real-pipeline integration test (`TestSdd041BacklogReorderSection`).** It builds the dashboard via `build(sdd_root=..., write=False)["html"]`, extracts the real rendered `data-pid`s from the Backlog section, and asserts each returns **200/ok** from the actual `handle_reorder_request` (no monkeypatch), that a drag move persists to `display-order.json` + appends `reorder-audit.jsonl` on disk, that up/down buttons carry the adjacent OPEN item's full-order rank, that **DONE rows are not rendered** (and a DONE id interleaved in the order is skipped while full-order ranks stay correct), that every shown row carries a **non-empty title** (no bare-id fallback, including for `--`-RICE rows), and that a dependency-locked move returns **409/blocked** -- closing the original 400 gap by binding render output to the live endpoint.

## Alternatives Considered

- **A JS drag/drop library (REJECTED -- Article V / kickoff "do-NOT").** Adds a JavaScript-framework dependency. Vanilla HTML5 drag events ship the value with zero deps.
- **`'unsafe-inline'` script-src (REJECTED -- security regression).** Relaxing to `'unsafe-inline'` would permit any inline script. A per-script sha256 hash is strictly tighter and self-pinning.
- **Modifying `render_html`'s meta CSP to add `script-src` (REJECTED -- Article X).** `render_html` is byte-locked. The CSP is widened by post-processing its output in `inject_drag_html`, leaving the locked function and `TestS1FootprintLockGuard` intact.
- **Auto-retrying a blocked move with `force=true` (REJECTED -- ADR-017 Level-2).** Forcing past a dependency lock is an irreversible-intent human decision. The drag layer surfaces the 409 reason and routes the operator to the CLI; it never escalates on its own.
- **A separate write server / new port (REJECTED -- needless surface).** Reusing the existing localhost `DashboardHandler` with one additive route keeps the attack surface minimal and the operator workflow single-origin.
