---
id: SDD-20260609S6COMPLETE-tasks
type: tasks
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-sprint-6-completion
---

# Task List: Sprint 6 Completion Bundle (SDD-032)

- Spec Reference: `spec.md` (SDD-032)
- Plan Reference: `plan.md`
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7), feature slot F-09
- Author: Principal Architect (EM prep session)
- Date: 2026-06-09
- Test baseline: 259 (Sprint 6 close)

---

> **Task ID convention:** Local short IDs `T-032-NN` used within this
> date-prefixed feature directory.
>
> **Owner direction 2026-06-08 (Option 3 hybrid):** No REQUIRED item
> may be deferred at Sprint 7 F-09 close. Tasks 01-05 ship implementation;
> Task 06 is the no-deferral close verification.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-032-01 | Implement priority-weighted FIFO queue ordering (SDD-019.R7) | `cli/fleet.py` (additive helpers `_lookup_backlog_priority`, `_compute_queue_order`); `cli/test_fleet.py` (new `TestQueueOrdering` class) | proves AC-1; closes R1; tests `TestQueueOrdering.test_priority_wins`, `TestQueueOrdering.test_fifo_tiebreak`, `TestQueueOrdering.test_empty_queue` all pass | M | none | AFK | Yes | done |
| T-032-02 | Implement cutover-commit grandfather migration (SDD-019.R8) | `cli/fleet.py` (additive helper `_is_grandfathered` + constant `ARTICLE_XI_CUTOVER`); `cli/test_fleet.py` (new `TestGrandfather` class) | proves AC-2; closes R2; tests `TestGrandfather.test_pre_cutover_not_blocked`, `TestGrandfather.test_post_cutover_blocked`, `TestGrandfather.test_mixed_pre_and_post` all pass | M | T-032-01 (same file serialization) | AFK | No (shares `cli/fleet.py` with T-032-01) | done |
| T-032-03 | Implement dedup triple-destination log writers (SDD-020.R6) | `cli/dedup.py` (additive functions `_write_ledger_rows`, `_write_per_spec_dedup_scan`, `_append_rolling_log` + `--emit-logs` / `--no-emit-logs` argparse flag + 3 call sites at end of `cmd_scan`); `cli/test_dedup.py` (new `TestDedupLogWriters` class); `backlog/DEDUP-LOG.md` (new file: header + first-run placeholder) | proves AC-3; closes R3; tests `TestDedupLogWriters.test_ledger_rows_written`, `TestDedupLogWriters.test_per_spec_file_written`, `TestDedupLogWriters.test_rolling_log_appended`, `TestDedupLogWriters.test_no_emit_logs_flag` all pass | M | none (parallel-safe with T-032-01 and T-032-02; different file) | AFK | Yes | done |
| T-032-04 | Wire dedup invocation into `/triage` prompt (SDD-020.R8 half) | `.github/prompts/triage.prompt.md` (minimal edit: one new numbered list item invoking `cli/dedup.py scan --scope all` with HARD/SOFT/ADVISORY tier-action guidance); `cli/test_dedup.py` (new `TestPromptHooks.test_triage_invokes_dedup` + shared `test_tier_action_guidance_present`) | proves AC-4a; partial-closes R4; tests pass | S | T-032-03 (depends on log writers being callable) | AFK | Yes (different file from T-032-05) | done |
| T-032-05 | Wire dedup invocation into `/clarify` prompt (SDD-020.R8 other half) | `.github/prompts/clarify.prompt.md` (minimal edit: same content as T-032-04); `cli/test_dedup.py` (new `TestPromptHooks.test_clarify_invokes_dedup`) | proves AC-4b; partial-closes R4; tests pass | S | T-032-03 (depends on log writers being callable); parallel-safe with T-032-04 (different prompt file) | AFK | Yes | done |
| T-032-06 | Sprint 7 F-09 close verification: full pytest, schema_lint, regenerate `exec/state.md`, check all R-items in `validation.md`, verify lock-surface preserved by `git diff --stat` on `cli/fleet.py` and `cli/dedup.py` against commits `524872b` and `8eb564d` | (verification only): full pytest run; `python spec-driven-development/cli/schema_lint.py`; `python spec-driven-development/cli/state_builder.py` regen; `validation.md` checkbox audit; `git diff --stat 524872b -- spec-driven-development/cli/fleet.py`; `git diff --stat 8eb564d -- spec-driven-development/cli/dedup.py`; final close commit `close(sprint-7-f-09): SDD-032 Sprint 6 completion bundle DONE` referencing all four parent R-items (SDD-019.R7, SDD-019.R8, SDD-020.R6, SDD-020.R8) | proves AC-5; closes R5, R6, R7; all REQUIRED items checked in `validation.md`; **no DEFERRED markers permitted per owner direction 2026-06-08** | S | T-032-01, T-032-02, T-032-03, T-032-04, T-032-05 | HITL (owner reviews manual-check items before close) | No (verification + close commit) | done |

## Dependency Graph

```
T-032-01 -> T-032-02 -+
                      |
                      +-> T-032-06 (close)
T-032-03 -> T-032-04 -+
         -> T-032-05 -+
```

Sequencing notes (per `plan.md` "Parallel-Safe Tasks"):

- T-032-01 and T-032-02 BOTH touch `cli/fleet.py` -> serial.
- T-032-03 touches `cli/dedup.py` -> parallel-safe with the
  fleet.py track.
- T-032-04 and T-032-05 touch different prompt files -> parallel-safe
  with each other; both depend on T-032-03 land (so the log writers
  the hooks rely on are callable).
- T-032-06 fan-in: requires T-032-01..05 done.

## Batch Plan

- **Batch 1** (F-09, parallel across two file tracks):
  - Track A (`cli/fleet.py`): T-032-01 -> T-032-02 (serial within file)
  - Track B (`cli/dedup.py`): T-032-03 (single task, independent file)
- **Batch 2** (F-09, parallel across two prompt files):
  - T-032-04 (`.github/prompts/triage.prompt.md`)
  - T-032-05 (`.github/prompts/clarify.prompt.md`)
- **Batch 3** (F-09, close):
  - T-032-06 -- full test run + schema_lint + state regen +
    validation.md audit + close commit.

## Constraints (carry-over from plan.md "Lock-Surface Protections")

Implementers MUST NOT modify:

- `_scan_lock_state` body in `cli/fleet.py` (commit `524872b`).
- Existing `cmd_lock_*` subcommand handlers in `cli/fleet.py` --
  output may be EXTENDED only with additive lines after existing
  prints; existing prints stay byte-identical.
- Pre-dispatch gate refusal in `cmd_dispatch` (commit `524872b`).
- `load_corpus`, `_parse_*`, `_tokenize`, `_jaccard`, `find_overlaps`,
  `_format_overlap`, `handle_overlaps` in `cli/dedup.py` (commit
  `8eb564d`).
- The existing body of `cmd_scan` -- new writer calls go at the END
  of the function, guarded by `if args.emit_logs:`. Existing logic
  stays byte-identical.
- Any existing test class or test name in `cli/test_fleet.py` or
  `cli/test_dedup.py`.
- Any parent-spec file under `specs/2026-06-07-*`. The parent
  `validation.md` files retain their DEFERRED markers as historical
  record; SDD-032's `validation.md` is the authoritative completion
  check.
- `constitution/principles.md` -- Article XI is final at version
  1.2.0.

## Notes

- Use `Fleet Dispatch Eligible = No` for T-032-02 (same file as T-032-01)
  and T-032-06 (verification + close commit).
- Owner review (HITL) required at T-032-06 for the two manual-check
  items in `validation.md` (prompt-line review + first-run dedup-log
  surface check).
- Maximum task count budget: 9 (per EM prep guidance). Actual: **6**.
- **Carry-over policy:** if any task surfaces a parent-CLARIFY
  ambiguity, mark "OWNER GUIDANCE REQUIRED" in `spec.md` and STOP
  that task. Do not invent an answer. Do not silently widen scope.
