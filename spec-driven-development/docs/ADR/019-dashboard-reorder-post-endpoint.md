---
id: ADR-019
type: spec
status: accepted
owner: principal-architect
updated: 2026-06-26
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

## Alternatives Considered

- **A JS drag/drop library (REJECTED -- Article V / kickoff "do-NOT").** Adds a JavaScript-framework dependency. Vanilla HTML5 drag events ship the value with zero deps.
- **`'unsafe-inline'` script-src (REJECTED -- security regression).** Relaxing to `'unsafe-inline'` would permit any inline script. A per-script sha256 hash is strictly tighter and self-pinning.
- **Modifying `render_html`'s meta CSP to add `script-src` (REJECTED -- Article X).** `render_html` is byte-locked. The CSP is widened by post-processing its output in `inject_drag_html`, leaving the locked function and `TestS1FootprintLockGuard` intact.
- **Auto-retrying a blocked move with `force=true` (REJECTED -- ADR-017 Level-2).** Forcing past a dependency lock is an irreversible-intent human decision. The drag layer surfaces the 409 reason and routes the operator to the CLI; it never escalates on its own.
- **A separate write server / new port (REJECTED -- needless surface).** Reusing the existing localhost `DashboardHandler` with one additive route keeps the attack surface minimal and the operator workflow single-origin.
