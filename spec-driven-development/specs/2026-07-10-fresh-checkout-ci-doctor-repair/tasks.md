---
id: SDD-20260710CIDOCTOR-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-07-10
feature: 2026-07-10-fresh-checkout-ci-doctor-repair
---

# TASKS: SDD-055 -- Fresh-checkout CI doctor repair

## Task T-055-01: Lock the explicit doctor-profile contract

**Story**: [US-1] CI validates source-controlled health while local doctor remains strict.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: `spec-driven-development/cli/test_sdd055.py`
**Depends on**: NONE

### Description

Write isolated tests first for explicit local/CI selection, ambient independence,
local missing-ledger and current-PI strictness, CI omissions, universal tracked-DB
rejection, and shared source-check invocation. Use temporary roots, scratch git and
SQLite state, and mocks at checker boundaries; never consult the real ledger.

### Acceptance Criteria

- [ ] Tests fail before production changes for the missing CI profile.
- [ ] Tests cover V-1 through V-7 without mutating checkout-local state.

### Verification

Run `python -m pytest spec-driven-development/cli/test_sdd055.py -q`; confirm the
new profile-contract tests are red before T-055-02 and green afterward.

## Task T-055-02: Implement the minimal doctor profile split

**Story**: [US-1] CI validates source-controlled health while local doctor remains strict.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: `spec-driven-development/cli/bootstrap.py`, `spec-driven-development/cli/test_sdd055.py`
**Depends on**: T-055-01

### Description

Add an explicit `--mode local|ci` option with local as default. Keep the tracked-DB
guard and all source-controlled checks shared. In CI mode only, report ignored-ledger
reachability and current-PI rows as inapplicable; retain strict local behavior.

### Acceptance Criteria

- [ ] Explicit profiles satisfy V-1 through V-7.
- [ ] CI omissions are shown as N/A, never PASS.
- [ ] No ambient CI variable influences profile selection.

### Verification

Run the focused test module and the existing bootstrap tests; both pass.

## Task T-055-03: Wire and prove fresh-checkout CI

**Story**: [US-1] The required public doctor gate succeeds honestly from a fresh checkout.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: `.github/workflows/doctor.yml`, `spec-driven-development/specs/2026-07-10-fresh-checkout-ci-doctor-repair/validation.md`, `spec-driven-development/exec/sprint-progress.md`
**Depends on**: T-055-02

### Description

Make the workflow invoke explicit CI mode, run all locked validation including a
disposable fresh clone, record exact evidence, push the owner-authorized repair, and
verify the public workflow. Append only an out-of-sprint repair block; do not alter
Sprint 23 scope or status.

### Acceptance Criteria

- [ ] V-8 through V-11 and M-3 have real evidence.
- [ ] Public CI URL and status are recorded only after observed completion.
- [ ] Worktree is clean and `HEAD == origin/master` at handoff.

### Verification

Run full pytest, three lints, Article X guard, strict local doctor, local B-1 query,
and explicit CI doctor in a disposable fresh clone; then inspect the public run.

## Batch checkpoint

All tasks are sequential because T-055-01 and T-055-02 share the focused test file,
and close evidence depends on the implementation commit. After T-055-03, review the
explicit-path diff for forbidden constitution, Sprint 23, dependency, database, locked
function, dashboard, and waiver changes.
