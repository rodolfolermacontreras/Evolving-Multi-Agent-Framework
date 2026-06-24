---
id: SDD-20260611DASHREORDER-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-11
feature: 2026-06-24-dashboard-lifecycle-reorder
---

# TASKS: SDD-036 -- Lifecycle pipeline + 4-card docs row + drag-to-reorder safeguards

- Feature ID: SDD-036
- Spec: [`spec.md`](./spec.md) | Plan: [`plan.md`](./plan.md) | Validation: [`validation.md`](./validation.md)
- Status: **active** -- this is the F-25 task contract; F-24 does not execute these tasks.
- Maximum task count budget: 9. This breakdown uses 8.

---

## No Silent Deferral Rule

If a REQUIRED validation item cannot be satisfied by its mapped task, the feature does NOT close. No REQUIRED item may be quietly dropped. UI-Variant REQUIRED items (R-1, R-2, R-8) may be refined via append-only `## Delta Entries` in [`validation.md`](./validation.md) during F-25, but may not be deleted.

## Status Legend

- `[ ]` not started
- `[~]` in progress
- `[x]` complete with evidence
- `[!]` blocked (record reason)

## Baseline Block (capture before T-036-02)

- `python -m pytest spec-driven-development/ --tb=no -q` -> expect `>= 349 passed, 2 skipped`.
- `python spec-driven-development/cli/schema_lint.py` -> expect exit 0.
- Record both as the F-25 starting baseline.

## Task Breakdown

| Task ID | Description | File Scope | Required Tests / Verification | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-------------------------------|--------|------|------|-------------------------|--------|
| T-036-01 | Capture baseline (tests + schema lint) and confirm Sprint 10 close state. | (read-only) | `pytest` >= 349/2; `schema_lint` exit 0 | S | -- | AFK | No (serialized) | [ ] |
| T-036-02 | Add optional `depends_on` inline-list field support: parse the raw `[...]` string from frontmatter into a clean ID list helper (shared convention). Add the demonstrator `depends_on` to ONE existing `spec.md`. | `cli/schema_lint.py` (helper only), one `spec.md` | Unit: `[SDD-018]` -> `["SDD-018"]`; absent -> `[]`; `[A, B]` -> `["A","B"]` | S | T-036-01 | AFK | No (shared file) | [ ] |
| T-036-03 | Implement `check_depends_on` validator (when-present only): list shape, ID shape, duplicates, self-dependency (ERROR); BACKLOG existence (WARNING). Wire into the `spec.md` lint path; do NOT touch `REQUIRED_CONTRACT_FIELDS`. | `cli/schema_lint.py`, `cli/test_schema_lint.py` | Tests: valid; bad-ID ERROR; duplicate ERROR; self-dep ERROR; missing-ref WARNING; absent-field zero findings (AC-4) | M | T-036-02 | AFK | No (shared file) | [ ] |
| T-036-04 | Create `cli/backlog_reorder.py` (CLI-PATTERN): read/write `backlog/display-order.json`; `move` subcommand with `--item`, `--to-rank`; exit 0/1/2. Reads BACKLOG IDs; overlay absent -> BACKLOG natural order. | `cli/backlog_reorder.py`, `cli/test_backlog_reorder.py` | Tests: legal move reorders overlay + exit 0; unknown item -> exit 1 w/ stderr reason; bad args -> exit 2 (AC-8 plumbing) | M | T-036-03 | AFK | No (new file, serialized behind parse convention) | [ ] |
| T-036-05 | Add dependency-lock + audit append to `backlog_reorder.py`: block move above incomplete `depends_on` target (human-readable reason); block cycle-creating move; append one row to `ledger/reorder-audit.jsonl` with locked shape on every move. | `cli/backlog_reorder.py`, `cli/test_backlog_reorder.py`, `ledger/reorder-audit.jsonl` (created) | Tests: blocked move -> exit 1 + reason + NO order change; legal move -> one appended JSON row w/ all 9 fields; append-only across two moves (AC-5, AC-6) | M | T-036-04 | AFK | No | [ ] |
| T-036-06 | Add force-override governance to `backlog_reorder.py`: `--force` lands an otherwise-blocked move, records `force_override: true` + non-empty `reason`; tool NEVER silently forces (empty reason under `--force` -> exit 2). | `cli/backlog_reorder.py`, `cli/test_backlog_reorder.py` | Tests: `--force` + reason -> move lands, audit `force_override:true`; `--force` w/o reason -> exit 2; no `--force` on violation -> blocked (AC-7) | S | T-036-05 | HITL | No | [ ] |
| T-036-07 | Render lifecycle pipeline (AC-1), four-card docs row with missing-state (AC-2), and keyboard-accessible reorder control reflecting the overlay (AC-8) in `state_builder.py`. Read `depends_on` + overlay; do not regress the locked render surface. | `cli/state_builder.py`, `cli/test_state_builder.py` | Tests: 9 pipeline nodes + current-state emphasis for one active + one done feature + one sprint; 4 docs cards incl. one disabled/missing; reorder control present; overlay order respected (AC-1, AC-2, AC-8) | L | T-036-05 | HITL | No (shared file) | [ ] |
| T-036-08 | Regenerate executive surfaces and verify: run `state_builder.py`; `schema_lint` exit 0; full suite >= 349+new; record evidence. (Sprint-close smoke is F-26.) | (read-only + generated `exec/*`) | `state_builder.py` runs clean; `schema_lint` exit 0 (AC-9); `pytest` >= 349 + new (AC-10) | S | T-036-07 | AFK | No | [ ] |

## Dependency Graph

```
T-036-01 -> T-036-02 -> T-036-03 -> T-036-04 -> T-036-05 -> T-036-06
                                                     \-> T-036-07 -> T-036-08
```

All tasks are serial. T-036-07 (render) depends on T-036-05 (overlay + audit exist) and T-036-02 (`depends_on` parsing). T-036-08 closes after both T-036-06 and T-036-07.

## Batch Plan

- Batch 1: T-036-01, T-036-02, T-036-03 (schema layer).
- Batch 2: T-036-04, T-036-05, T-036-06 (reorder layer).
- Batch 3: T-036-07 (render layer), T-036-08 (verify).
- Checkpoint for owner feedback after each batch.

## Constraints

- Stdlib only (Article V): `argparse`, `json`, `pathlib`, `re`, `datetime`, `sys`, `subprocess`, `typing`. No PyYAML, no JS framework.
- CLI-PATTERN for `backlog_reorder.py`: `main(argv: list[str] | None = None) -> int`, explicit `parse_args(argv)`, `if __name__ == "__main__": sys.exit(main())`, exit codes 0/1/2, custom exception class, errors to stderr, UTC ISO-8601 `Z` timestamps, default paths relative to `__file__`.
- One test per acceptance criterion; tests in `cli/test_<module>.py`.
- Do NOT extend `REQUIRED_CONTRACT_FIELDS`; do NOT add a SQLite table; do NOT mutate `BACKLOG.md` ordering; do NOT hand-edit generated `exec/*`; do NOT silently force a dependency-violating move.

## Notes

- `[NO-TEST-NEEDED]` is not used here; every REQUIRED maps to a test.
- F-26 (separate dispatch) owns: marking SDD-036 DONE in BACKLOG, sprint close, dashboard + dependency-lock smoke evidence, and the pre-push owner-approval gate.
