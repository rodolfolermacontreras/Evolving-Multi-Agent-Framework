---
id: SDD-20260709FOVL-validation
type: validation
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-file-overlap-detector
---

# VALIDATION: SDD-049 -- File-overlap conflict detector for fleet dispatch

- Feature ID: SDD-049
- Sprint: PI-9 / Sprint 1 (Sprint 22); design + implementation F-60
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)

---

## Lock Statement

Contract LOCKED at F-60 design. Implementation MUST satisfy every REQUIRED item
(R-1..R-7) with evidence and MUST NOT loosen, drop, or silently defer any REQUIRED
item. If a REQUIRED item cannot be met, implementation stops and surfaces it to the
owner via the DECISION-REQUEST FORMAT.

---

## Required Items (Strict)

- [x] **R-1 (scope parser).** `fleet.parse_file_scope` splits a `File Scope` cell on
  `,`/`;`, strips whitespace + backticks, and maps empty and placeholder/"none"
  tokens to the empty set. (AC1) -- EVIDENCE: `test_fleet.py::TestFileScopeParsing`
  (3 cases) PASS.
- [x] **R-2 (overlap detector, pure).** `fleet.detect_file_overlaps` returns `[]` for
  disjoint or single-task batches and one record `{task_a, task_b, shared}` per
  overlapping unordered pair in stable order (three identical scopes -> 3 pairs).
  (AC2) -- EVIDENCE: `TestDetectFileOverlaps` (5 cases) PASS.
- [x] **R-3 (pre-dispatch block, no side effects).** `cmd_dispatch` runs the detector
  after eligibility and before any `record_dispatch`/brief write; an overlapping batch
  raises `FleetError` (non-zero exit), prints "overlap" + the shared file, and writes
  ZERO ledger rows. (AC3) -- EVIDENCE:
  `TestDispatchOverlapGate::test_overlapping_batch_is_blocked_with_no_side_effects`
  PASS (row count 0 after block).
- [x] **R-4 (deliberate override).** `--allow-overlap` downgrades a detected overlap to
  a stderr WARNING and proceeds. (AC4) -- EVIDENCE:
  `test_allow_overlap_flag_warns_and_proceeds` PASS (rc 0, "warning" on stderr, 2 rows).
- [x] **R-5 (no regression).** Disjoint batches and single-task dispatches are
  unaffected. (AC5) -- EVIDENCE: `test_non_overlapping_batch_dispatches` +
  `test_single_task_dispatch_unaffected` PASS; existing `TestFleetCLI` AC1-AC9 PASS.
- [x] **R-6 (Article X intact + stdlib-only).** No locked render/load function touched;
  `TestS1FootprintLockGuard` PASS; the detector uses only `re`/stdlib. (AC / constraint)
  -- EVIDENCE: `-k FootprintLockGuard` 3 passed; no new import added to `fleet.py`.
- [x] **R-7 (Level-1, no Level-2 trigger).** No `constitution/**` edit, no ADR, no
  version bump, no third-party dependency. -- EVIDENCE: only `cli/fleet.py` +
  `cli/test_fleet.py` + this spec dir edited.

---

## Manual Checks (at close)

- [x] **M-1 (full suite).** `pytest spec-driven-development/` >= 596 passed / 2 skipped,
  growing by the 12 new SDD-049 cases -- checked at F-62 close.
- [x] **M-2 (lints).** schema + origin + staledoc lint clean -- checked at F-62 close.
- [x] **M-3 (doctor + CI).** `doctor` green; CI green on the Sprint 22 head -- checked
  at F-62 close.
