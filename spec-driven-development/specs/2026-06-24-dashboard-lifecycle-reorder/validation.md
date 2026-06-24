---
id: SDD-20260611DASHREORDER-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-11
feature: 2026-06-24-dashboard-lifecycle-reorder
---

# VALIDATION: SDD-036 -- Lifecycle pipeline + 4-card docs row + drag-to-reorder safeguards

- Feature ID: SDD-036
- Spec: [`spec.md`](./spec.md) | Plan: [`plan.md`](./plan.md) | Tasks: [`tasks.md`](./tasks.md)
- ADR: [ADR-017](../../docs/ADR/017-backlog-reorder-safeguards.md) (`proposed`)

---

## Lock Statement

This validation contract is **LOCKED at F-24 (/tasks)** per Article X. The REQUIRED set below is the pre-implementation contract for F-25. No REQUIRED item may be silently dropped (Article X rule; Sprint 7/8/9/10 no-silent-deferral rule inherited).

**Mixed-validation split (Q-I / Article XII).** This spec opts into the UI Lifecycle Variant (`ui-variant: true`). The split is binding:

- **Strict (Article X) -- cannot loosen post-lock:** R-3, R-4, R-5, R-6, R-7, R-9, R-10. These are schema/ledger correctness items; any change requires re-opening the spec under normal Article X, not a delta entry.
- **UI-Variant (Article XII) -- eligible for append-only deltas:** R-1, R-2, R-8. These are visual dashboard surfaces; post-lock refinement is recorded as append-only `## Delta Entries` (timestamp / author / rationale / item-type) during F-25, never by silently editing the locked item.

At F-24 there are **zero** delta entries.

---

## Required Items (all unchecked -- implementation is F-25)

### Strict (Article X)

- [x] **R-3 (`depends_on` schema).** `spec.md` accepts an optional inline-list `depends_on` of feature IDs; absent = empty list; the field is NOT in `REQUIRED_CONTRACT_FIELDS`. (AC-3, Q-E) -- Evidence: `parse_depends_on()` in `cli/schema_lint.py`; demonstrator `depends_on: [SDD-018]` on this spec.md; `REQUIRED_CONTRACT_FIELDS` unchanged; tests in `test_schema_lint.py`.
- [x] **R-4 (`schema_lint` when-present validation).** With `depends_on` present, lint flags bad list shape, bad ID shape, duplicates, and self-dependency at ERROR, and non-existent BACKLOG reference at WARNING; absent field yields zero findings. (AC-4, Q-F) -- Evidence: `check_depends_on()` wired into `_walk_artifacts` spec branch; `test_schema_lint.py` 43 passed covering all five cases + absent=0.
- [x] **R-5 (Dependency-lock behavior).** A move above an incomplete dependency is blocked with a human-readable reason; a cycle-creating move is blocked; a legal move succeeds; deps are feature IDs only. (AC-5, Q-D) -- Evidence: `dependency_violations()` (incomplete-dep-above + `_has_cycle_through`); reorder smoke blocked reason `SDD-103 cannot be ranked above SDD-101: ... not yet complete`; `test_backlog_reorder.py` legal/blocked/cycle cases.
- [x] **R-6 (Audit-trail append).** Each reorder appends exactly one JSON object to `ledger/reorder-audit.jsonl` with all nine locked fields; the file is append-only across multiple moves. (AC-6, Q-G) -- Evidence: `append_audit_row()` emits locked 9-tuple in order; reorder smoke allowed-move row had 9 fields; append-only test in `test_backlog_reorder.py`.
- [x] **R-7 (Force-override governance).** A dependency-violating move is rejected unless `--force` with a non-empty reason is given; forced moves record `force_override: true`; the tool never silently forces (`--force` without reason fails). (AC-7, Q-H) -- Evidence: `move()` raises `ReorderError` unforced; `--force` w/o reason -> exit 2 main() guard; `force_override:true` + `dependency_check:override` on forced; `test_backlog_reorder.py` 14 passed.
- [x] **R-9 (Schema lint clean).** `python spec-driven-development/cli/schema_lint.py` exits 0 after all changes. (AC-9) -- Evidence: `Schema lint clean. Scanned: ...Evolving-Multi-Agent-Framework`, EXIT=0.
- [x] **R-10 (Test baseline preserved).** `python -m pytest spec-driven-development/ --tb=no -q` returns at least 349 passed with the known 2 platform-conditional skips, plus the new SDD-036 tests. (AC-10) -- Evidence: `python -m pytest cli/ -q` -> **399 passed, 2 skipped** (baseline 349+2; +50 new SDD-036 tests; S1 footprint lock guard passes).

### UI-Variant (Article XII -- delta-eligible)

- [x] **R-1 (Lifecycle pipeline render).** Each feature card and sprint card renders the 9-state pipeline with current-state emphasis, derived from existing `detect_stage()` / sprint status; no new registry. (AC-1, Q-A) -- Evidence: `render_lifecycle_pipeline()` (9 `STAGES` nodes, `pipe-current`/`pipe-complete`/`pipe-later`); regenerated `exec/state.html` smoke `lifecycle-card:32`, `pipe-current:33` (32 cards + 1 CSS rule); `TestLifecyclePipeline` + `TestInjectLifecycleHtml` (incl. sprint card). Satisfied as-locked; no refinement -> no delta entry.
- [x] **R-2 (Four-card docs row).** Each feature card renders Constitution / Spec / Sprint / ADRs deep-linking to existing artifacts; an unresolved target renders a disabled "missing" card; no SDD-037 cards. (AC-2, Q-B) -- Evidence: `resolve_docs_cards()` + `render_docs_row()`; smoke `docs-row:32`, `docs-card-missing:13`; `TestDocsRow`. Satisfied as-locked; no delta entry.
- [x] **R-8 (Reorder control on dashboard).** The dashboard exposes a keyboard-accessible, no-JS-framework move control that invokes the reorder operation and reflects the display-order overlay. (AC-8, Q-C) -- Evidence: `render_reorder_control()` native `<button>` up/down with `aria-label`, disabled at ends, `data-cmd` invoking `cli/backlog_reorder.py move`; smoke `reorder-control:32`, `script tags:0` (no JS framework); `TestReorderControl`. Satisfied as-locked; no delta entry.

---

## Optional / Best-Effort Items

- [ ] **O-1.** Pipeline node tooltips naming the artifact that advanced each state.
- [ ] **O-2.** Reorder control shows the blocking-dependency reason inline before a move is attempted.
- [ ] **O-3.** `reorder-audit.jsonl` pretty-printed companion view on the dashboard (visible-on-demand). (Note: full ledger-visibility cards are SDD-037, out of scope here.)

---

## Specific Test Coverage Required

- `check_depends_on`: valid list; bad ID shape (ERROR); duplicate (ERROR); self-dependency (ERROR); non-existent reference (WARNING); absent field (zero findings).
- `backlog_reorder`: legal move reorders overlay + exit 0 + one audit row; blocked move (exit 1) + reason + no order change; cycle-creating move blocked; `--force` + reason lands + `force_override:true`; `--force` without reason -> exit 2; append-only across two moves; bad args -> exit 2.
- `state_builder` render: 9 pipeline nodes + current-state emphasis for one active feature, one done feature, and one sprint card; four docs cards including one disabled/missing; reorder control present; overlay order respected.
- Full suite: >= 349 passed + 2 skips + new tests.

## Manual Checks (F-26 close evidence, not F-25)

- [x] **M-1.** Dashboard smoke: pipeline + 4-card docs row render for one active/done feature and one sprint card. -- Evidence (F-26, 2026-06-24): regenerated `exec/state.html` markers present: `zone-lifecycle`, `lifecycle-card`, `pipe-current`, `docs-row`, `reorder-control`; `<script` tag count = 0 (no JS framework).
- [x] **M-2.** Reorder smoke: a dependency-blocked move is blocked with a reason; a legal move records an audit row. -- Evidence (F-26, 2026-06-24): isolated temp-tree real-CLI run -- blocked move exit 1, reason `SDD-103 cannot be ranked above SDD-101: SDD-103 depends on SDD-101 and SDD-101 is not yet complete`; legal move exit 0 `Moved SDD-102 from rank 2 to 0 (dependency_check=pass, force_override=False)`; one append-only audit row with all 9 locked fields `[actor, dependency_check, event_type, force_override, from_rank, item_id, reason, timestamp, to_rank]`.
- [x] **M-3.** `exec/state.md` does not say `Active focus: azure-decommission` after regeneration. -- Evidence (F-26, 2026-06-24): regenerated `exec/state.md` active-focus substring `azure-decommission` count = 0.

## Tone / UX Check (UI-Variant)

- [x] **U-1.** Reorder is friction-free for legal moves (no modal ceremony) -- honors the owner correction. -- Evidence (F-26): legal move executed in one CLI invocation, exit 0, no confirmation prompt; dashboard control is a native `<button>` up/down with no modal.
- [x] **U-2.** Blocked-move reasons are plain language, naming the specific dependency. -- Evidence (F-26): blocked reason names SDD-103 and SDD-101 explicitly and states the dependency is not yet complete; no error codes or stack traces.
- [x] **U-3.** Missing docs cards read as an intentional signal, not an error/crash. -- Evidence (F-26): `docs-card-missing:13` rendered as disabled cards; regeneration completed without exception (exit 0).

## Definition of Done (F-25 + F-26)

- All Strict REQUIRED items (R-3..R-7, R-9, R-10) checked with evidence (F-25).
- All UI-Variant REQUIRED items (R-1, R-2, R-8) checked with evidence; any post-lock refinement recorded as append-only deltas (F-25).
- Manual checks M-1..M-3 satisfied at Sprint 11 close (F-26).
- `schema_lint` exit 0; test baseline preserved; executive surfaces regenerated.
- Owner pre-push approval recorded (F-26 gate).

---

## Delta Entries

None at F-24 lock. UI-Variant REQUIRED items (R-1, R-2, R-8) refined during F-25 are appended here as `### Delta DE-NN -- <title>` blocks, each with mandatory `timestamp`, `author`, `rationale`, and `item-type` (one of add / wontfix / re-check / retroactive-demo). Strict items are NOT delta-eligible.
