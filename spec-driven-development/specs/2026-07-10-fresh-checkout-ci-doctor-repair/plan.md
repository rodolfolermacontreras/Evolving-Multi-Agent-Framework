---
id: SDD-20260710CIDOCTOR-plan
type: plan
status: active
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-fresh-checkout-ci-doctor-repair
---

# PLAN: SDD-055 -- Fresh-checkout CI doctor repair

- Feature ID: SDD-055
- Spec: [spec.md](spec.md) | Validation: [validation.md](validation.md)
- ADR: [ADR-025](../../docs/ADR/025-local-and-ci-doctor-profiles.md)
- Execution owner: Principal Software Developer

---

## Approach

Keep one doctor implementation with two explicit profiles rather than two
independent validators:

1. Extend the existing `doctor` parser with an explicit CI-mode option. Preserve
   local as the default; do not inspect ambient CI variables.
2. In `run_doctor`, always run the tracked-database guard. In local mode, retain
   ledger existence/query and current-PI row checks unchanged. In CI mode, mark
   only those two clone-local operational checks inapplicable and continue.
3. Keep schema/orphan lint, governance, origin lint, stale-doc lint, tests, TDD,
   and DONE checks on the shared path for both modes.
4. Change the GitHub workflow command to select CI mode explicitly.
5. Prove the matrix with isolated temporary-root tests before implementation is
   accepted. Do not use the real ledger as test setup or success evidence.

This is profile separation inside the existing stdlib doctor, not a second CI
validator and not an environment-sensitive branch.

## Options considered

### Option A -- Explicit local/CI profiles in one doctor (selected)

- Pros: honest state boundary; shared source checks; local B-1 remains strict;
  deterministic and testable; smallest coherent repair.
- Cons: local and CI are no longer byte-identical invocations; output must make
  the two intentionally omitted checks clear.

### Option B -- Create/populate a temporary operational ledger in CI

- Pros: current doctor could remain nominally unchanged.
- Cons: fabricates operational evidence, cannot honestly reproduce clone-local
  history, and risks making a synthetic row satisfy B-1. Rejected.

### Option C -- Waive or soft-fail doctor in CI

- Pros: fastest path to a green badge.
- Cons: defeats the required gate and violates the owner-selected
  repair-over-waiver decision. Rejected.

## Implementation phases

### Phase 1 -- Red tests (isolated)

- Add focused tests under `spec-driven-development/cli/` using temporary roots,
  scratch git repositories, and scratch SQLite only where local B-1 needs it.
- Patch checker boundaries or inject controlled results so the test matrix proves
  which checks run without consulting the real checkout.
- Clear/control environment state and prove explicit mode wins over `CI` and
  `GITHUB_ACTIONS`.
- Required red cases: local missing ledger; local zero PI rows; CI tracked DB.
- Required green cases: CI missing ignored ledger; local PI row present.

### Phase 2 -- Minimal doctor repair

- Add explicit CI-mode argument handling in `bootstrap.py`.
- Refactor only enough to separate clone-local operational checks from common
  source checks.
- Preserve existing local invocation and strict B-1 behavior.
- Represent CI-only omissions as `SKIP`/`N/A` or equivalent truthful output; do
  not label unperformed local checks `PASS`.

### Phase 3 -- Workflow contract

- Update `.github/workflows/doctor.yml` to invoke the explicit CI mode.
- Preserve read-only validation posture and all existing workflow triggers/setup.

### Phase 4 -- Verification and close

- Run focused SDD-055 tests, full pytest, schema/origin/staledoc lints, Article X
  lock tests, and local doctor.
- Confirm explicit-path diff contains no Sprint 23 or constitution change.
- Commit with conventional message and Copilot co-author trailer.
- Push under the recorded owner authorization, inspect the public workflow result,
  record the green run in `validation.md`, then return control to Sprint EM.

## File budget

Implementation SHOULD touch only:

- `spec-driven-development/cli/bootstrap.py`
- one existing or focused doctor test module under `spec-driven-development/cli/`
- `.github/workflows/doctor.yml`
- this feature's validation/close artifacts

Any additional production surface requires Architect review before edit. No
constitution or Sprint 23 file is permitted.

## Risk and rollback

- **Risk:** CI mode accidentally skips a source-controlled check. Mitigation:
  isolated spy/mocked invocation test covering the full R-5 list.
- **Risk:** local B-1 is weakened by shared branching. Mitigation: preserve and
  test missing-ledger and zero-row failures in default mode.
- **Risk:** ambient `CI` changes local behavior. Mitigation: explicit CLI-only
  selection plus contradictory-environment tests.
- **Rollback:** revert the repair commit. No schema/data migration or dependency
  makes rollback costly. A rollback makes required CI red again and therefore
  must not be represented as a successful waiver.

## Handoff gate

Design is ready for the Principal Software Developer. Before implementation, the
Software Developer must derive atomic TDD tasks from R-1..R-10 and V-1..V-11,
without changing the locked validation contract. Sprint 23 remains untouched.
