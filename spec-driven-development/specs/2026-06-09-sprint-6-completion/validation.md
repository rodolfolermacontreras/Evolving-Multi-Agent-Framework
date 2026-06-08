---
id: SDD-20260609S6COMPLETE-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-09
feature: 2026-06-09-sprint-6-completion
---

# Validation Contract: Sprint 6 Completion Bundle (SDD-032)

- Spec Reference: `spec.md` (SDD-032)
- Contract Date: 2026-06-09
- Author: Principal Architect (EM prep session)
- Lock Point: **AT SCAFFOLD (2026-06-09)** -- no CLARIFY round needed

---

> **CONTRACT LOCKED 2026-06-09 at scaffold** (no CLARIFY round needed;
> reuses parent-spec answers from
> `specs/2026-06-07-serial-clarify-spec-gate/clarify.md` Q1-Q9 and
> `specs/2026-06-07-cross-feature-dedup/clarify.md` Q1-Q7).
>
> **No REQUIRED item may be deferred from Sprint 7 F-09 close per owner
> direction 2026-06-08 (Option 3 hybrid).** Any attempt to mark a
> REQUIRED item DEFERRED at close requires an explicit decision recorded
> below with owner signature and a new carry-over spec ID; otherwise the
> sprint does not close.
>
> Rule (Article X): zero unchecked REQUIRED items before implementation
> is considered complete. REQUIRED items cannot be loosened after lock
> without an explicit decision recorded here.

---

## Required Items (LOCKED at scaffold 2026-06-09)

- [x] **R1 -- SDD-019.R7 closed: priority-weighted FIFO queue ordering.** (commit `557b672`)
  When two or more features are queued for the same phase lock and the
  holder releases, the next acquirer is the queued feature with the
  highest BACKLOG priority (P1 > P2 > P3); equal-priority entries break
  ties by submission timestamp (FIFO). Empty-queue case yields no
  acquirer. Closes parent SDD-019.R7. Task: T-032-01. Tests:
  `TestQueueOrdering.test_priority_wins`,
  `TestQueueOrdering.test_fifo_tiebreak`,
  `TestQueueOrdering.test_empty_queue`.
- [x] **R2 -- SDD-019.R8 closed: cutover-commit grandfather migration.** (commit `557b672`)
  Any spec dir whose CLARIFY or SPEC frontmatter `updated` date is
  strictly earlier than `2026-06-08` (Article XI ratification cutover)
  is treated as a grandfathered lock holder by the scanner. The
  grandfathered feature is not retroactively blocked. On its first
  post-cutover edit, it claims the lock if free, or queues if held.
  New features (any spec dir created on or after `2026-06-08`) are
  subject to normal lock rules. Closes parent SDD-019.R8. Task:
  T-032-02. Tests: `TestGrandfather.test_pre_cutover_not_blocked`,
  `TestGrandfather.test_post_cutover_blocked`,
  `TestGrandfather.test_mixed_pre_and_post`.
- [x] **R3 -- SDD-020.R6 closed: triple-destination log writers.** (commit `8025a50`)
  Every invocation of `cli/dedup.py scan` (clean, HARD, SOFT, or
  ADVISORY) produces all three log artifacts: (a) a `dedup_scan_run`
  row plus one `dedup_overlap_flagged` row per overlap in
  `ledger/fleet.db`; (b) a `dedup-scan.md` file in each spec dir that
  was a candidate in a spec-bound overlap (skipped for pure-backlog
  scans); (c) a one-line append to `backlog/DEDUP-LOG.md`. The flag
  `--no-emit-logs` suppresses all three writes (for test isolation).
  Closes parent SDD-020.R6. Task: T-032-03. Tests:
  `TestDedupLogWriters.test_ledger_rows_written`,
  `TestDedupLogWriters.test_per_spec_file_written`,
  `TestDedupLogWriters.test_rolling_log_appended`,
  `TestDedupLogWriters.test_no_emit_logs_flag`.
- [x] **R4 -- SDD-020.R8 closed: dedup invoked from /triage and /clarify.** (commit `a6a25e4`)
  The files `.github/prompts/triage.prompt.md` and
  `.github/prompts/clarify.prompt.md` each contain a literal
  instruction line that invokes `cli/dedup.py scan --scope all` as a
  pre-step and documents the tiered-action response (HARD = stop and
  surface, SOFT = surface to owner, ADVISORY = note and continue).
  Closes parent SDD-020.R8. Tasks: T-032-04 (triage half) and
  T-032-05 (clarify half). Tests:
  `TestPromptHooks.test_triage_invokes_dedup`,
  `TestPromptHooks.test_clarify_invokes_dedup`,
  `TestPromptHooks.test_tier_action_guidance_present`.
- [x] **R5 -- No regression in existing test count.** (verified at T-032-06)
  Full test suite passes with test count >= 259 (Sprint 6 baseline) +
  new tests added in T-032-01..T-032-03. `schema_lint` exits 0. No
  new warnings or deprecations introduced. Task: T-032-06.
  Result: 259 -> 273 passed (+14 new tests), 2 skipped, 0 failed.
- [x] **R6 -- Lock surface preserved.** (verified at T-032-06)
  Sprint 6 commits `524872b` (lock scanner / pre-dispatch gate /
  existing lock subcommands in `cli/fleet.py`) and `8eb564d`
  (`load_corpus`, `find_overlaps`, `handle_overlaps`, existing
  `cmd_scan` body in `cli/dedup.py`) are NOT modified beyond
  additive integration points called out in `plan.md`. Verified by
  `git diff --stat` review at T-032-06.
  Result: fleet.py +175 / -0 (pure-additive); dedup.py +243 / -1
  (the 1 deletion is the documented `return handle_overlaps(...)` ->
  `exit_code = handle_overlaps(...); ...; return exit_code` integration
  point at the end of `cmd_scan` per plan.md "Lock-Surface Protections").
- [x] **R7 -- `exec/state.md` regenerates cleanly.** (verified at T-032-06)
  After all R1-R6 close, `python spec-driven-development/cli/state_builder.py`
  runs to completion, produces a fresh `spec-driven-development/exec/state.md`,
  and the resulting file passes `schema_lint`. Task: T-032-06.
  Result: state.md / state.html / work-index.md regenerated; schema_lint exit 0.

## Optional / Best-Effort Items

- [x] **O1 -- Dedup log JSON schema documented.** (commit `8025a50`)
  The shape of `dedup_scan_run` and `dedup_overlap_flagged` ledger
  rows, plus the `dedup-scan.md` frontmatter, plus the rolling-log
  line format, is documented in a short comment block at the top of
  the log-writer section of `cli/dedup.py`. Allows downstream
  dashboard consumers to read the log without re-reading the writer
  source.
- [x] **O2 -- Queue ordering visible in `fleet.py lock status` output.** (commit `557b672`)
  The CLI surface `python cli/fleet.py lock status` prints a "Queue"
  section after the "Lock holders" section, listing each queued
  feature with its priority and submission timestamp in the order the
  acquirer-selection rule would release them. (Optional because R1's
  internal correctness can be verified by unit tests; CLI surface is a
  usability bonus.)

## Specific Test Coverage Required

- [x] **Unit (R1)**: queue ordering with mixed priorities, FIFO tiebreak,
  empty-queue case. Files: `cli/test_fleet.py`.
- [x] **Unit (R2)**: grandfather pre-cutover, post-cutover, mixed.
  Files: `cli/test_fleet.py`.
- [x] **Unit (R3)**: each log writer in isolation + integration through
  `cmd_scan`; `--no-emit-logs` regression. Files: `cli/test_dedup.py`.
- [x] **Markdown lint (R4)**: prompt files contain expected literal
  substring + tier-action guidance. Files: `cli/test_dedup.py` (new
  `TestPromptHooks` class) OR a dedicated `cli/test_prompts.py` (plan
  decides).
- [x] **Regression (R5, R6)**: full suite green; `schema_lint` clean;
  no edits to the protected commit-`524872b` / commit-`8eb564d` line
  ranges.

## Manual Checks

- [x] Owner reviews the new lines added to `.github/prompts/triage.prompt.md`
  and `.github/prompts/clarify.prompt.md` and confirms they match the
  intended hook invocation. (R4 is a behavior change in agent
  prompts, not in code; a one-eye human review at close prevents
  silent prompt drift.) **Reviewed and approved by Rodolfo Lerma 2026-06-08 via EM ("wording is fine"). Pre-push gate.**
- [ ] Owner reviews `backlog/DEDUP-LOG.md` after the first real `/triage`
  invocation post-merge to confirm the rolling-log entry is
  readable and useful. (Surface check, not blocking.)

## Tone / UX Check

[NO-UX-CHECK-NEEDED] -- this is a CLI + prompt-file completion bundle.
No user-facing UI surfaces are introduced. Existing CLI output is
preserved (additive only).

## Definition of Done

Implementation is merge-ready only when:

1. All seven REQUIRED items above (R1-R7) are checked.
2. All "Specific Test Coverage Required" boxes are checked.
3. The two "Manual Checks" boxes are confirmed.
4. The full test suite passes (>= 259 + new tests; no regression).
5. `schema_lint` exits 0.
6. `exec/state.md` regenerates cleanly and is committed.
7. The completion commit references all four closed parent R-items
   (SDD-019.R7, SDD-019.R8, SDD-020.R6, SDD-020.R8) in its body.
8. **No REQUIRED item is marked DEFERRED.** Per owner direction
   2026-06-08 (Option 3 hybrid), Sprint 7 F-09 ships clean or does
   not ship.

Any skipped REQUIRED item requires an explicit Level-2 decision
recorded here with owner signature and a new carry-over spec ID --
not a re-write of this contract.
