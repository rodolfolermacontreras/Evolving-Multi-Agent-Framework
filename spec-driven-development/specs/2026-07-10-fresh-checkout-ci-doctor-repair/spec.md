---
id: SDD-20260710CIDOCTOR-spec
type: spec
status: active
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-fresh-checkout-ci-doctor-repair
---

# SPEC: SDD-055 -- Fresh-checkout CI doctor repair

- Feature ID: SDD-055
- Classification: P1 repair; out-of-sprint precondition before PI-9 Sprint 23
- Status: design complete; implementation pending
- CLARIFY: [clarify.md](clarify.md)
- Validation: [validation.md](validation.md)
- Plan: [plan.md](plan.md)
- ADR: [ADR-025](../../docs/ADR/025-local-and-ci-doctor-profiles.md)

---

## Problem statement

The required GitHub doctor workflow fails on a fresh checkout because
`spec-driven-development/ledger/fleet.db` is intentionally ignored and therefore
absent. The current doctor treats that expected absence, and the resulting lack
of current-PI operational rows, as repository-health failures. Local doctor is
correctly green at baseline because the clone-local ledger exists and carries
PI-9 rows. The defect is a conflation of source-controlled health with
clone-local operational health, not a reason to waive CI.

## Goal

Introduce an explicit CI doctor mode that proves every source-controlled health
contract from a fresh checkout while preserving strict local B-1 ledger truth.
Repair the required gate, push it under the recorded owner authorization, verify
public CI green, and return control to the Sprint Executive Manager without
starting or altering Sprint 23.

## Non-goals

- No waiver, soft-fail, or removal of the doctor workflow.
- No weakening of local B-1 ledger reachability or current-PI row checks.
- No permission to track or generate `fleet.db` in CI.
- No constitution edit, new dependency, ledger schema change, or migration.
- No Sprint 23 kickoff, scope, allocation, status, or artifact edit.
- No change to source-controlled check semantics beyond selecting the proper
  explicit mode.

## Requirements (RFC-2119)

- **R-1 (explicit modes):** The doctor MUST expose explicit `local` and `ci`
  behavior. Local MUST remain the default for existing `doctor` and
  `make doctor` invocations. CI mode MUST be selected by a command-line option;
  it MUST NOT be inferred from ambient environment variables.
- **R-2 (local B-1 strict):** Local mode MUST fail when the clone-local
  `ledger/fleet.db` is missing or unqueryable and MUST fail when an active PI has
  zero dispatch rows. Existing local behavior and labels SHOULD remain stable.
- **R-3 (tracked database safety):** Both modes MUST inspect git-tracked database
  files and fail when any tracked DB is found. CI MUST perform this check even
  when ignored `ledger/fleet.db` is absent.
- **R-4 (CI operational omissions):** CI mode MAY omit only (a) ignored
  `fleet.db` existence/reachability/query validation and (b) current-PI dispatch
  row validation. These omissions MUST be reported as mode-inapplicable, not as
  passing operational evidence.
- **R-5 (common source checks):** Both modes MUST run all applicable
  source-controlled checks: schema lint with orphan checking, governance
  coherence, origin-token absence, session-start document freshness, tests, TDD
  gate, and DONE completeness.
- **R-6 (workflow explicitness):** `.github/workflows/doctor.yml` MUST invoke
  doctor in explicit CI mode. The workflow MUST retain push and pull-request
  triggers, read-only contents permission, Python 3.12, and no secret, deploy,
  Azure-login, or production-mutation step.
- **R-7 (isolated tests):** SDD-055 tests MUST use temporary roots and scratch
  git/database state; MUST explicitly select the mode under test; MUST control or
  clear relevant environment variables; and MUST NOT depend on or mutate the
  real checkout's ignored ledger, current-PI rows, branch, or ambient CI state.
- **R-8 (fresh-checkout proof):** Tests MUST prove that CI mode passes its ledger
  boundary when ignored `fleet.db` is absent, fails when a DB is tracked, and
  still invokes every common source-controlled check. Tests MUST also prove
  local mode remains red for a missing ledger and for zero current-PI rows.
- **R-9 (repair over waiver):** The required public CI gate MUST be repaired and
  verified green after the owner-authorized push. No required check may be
  disabled, made non-blocking, or bypassed.
- **R-10 (bounded change):** Implementation MUST be stdlib-only and SHOULD be
  limited to `cli/bootstrap.py`, isolated doctor tests, and
  `.github/workflows/doctor.yml`. No `constitution/**` or Sprint 23 file may
  change.

## Acceptance criteria

- **AC-1:** `doctor` / `make doctor` without a CI option remains strict and fails
  against an isolated local fixture with no `fleet.db`.
- **AC-2:** Local mode fails against an isolated active-PI fixture whose valid
  scratch ledger has zero rows, and passes that B-1 check after a matching row is
  inserted.
- **AC-3:** CI mode does not fail merely because ignored `fleet.db` is absent and
  does not require a current-PI ledger row.
- **AC-4:** CI mode fails against an isolated git fixture containing a tracked
  `.db` file.
- **AC-5:** An isolated spy/mocked harness proves both modes invoke every common
  source-controlled check named in R-5.
- **AC-6:** The workflow command contains the explicit CI-mode option and retains
  the read-only validation-only shape.
- **AC-7:** New tests remain unchanged when ambient `CI` or `GITHUB_ACTIONS`
  values are set, absent, or contradictory to the explicit mode.
- **AC-8:** Full pytest is at least 616 passed / 2 skipped, schema/origin/staledoc
  lints are clean, Article X FootprintLockGuard is 3/3 PASS, and local doctor is
  green.
- **AC-9:** After push, the public GitHub doctor run for the repair commit is
  green; its URL or run identifier is recorded as close evidence.
- **AC-10:** Git diff shows no constitution or Sprint 23 change and no new
  third-party dependency.

## Affected surfaces

| Surface | Intended change |
|---------|-----------------|
| `spec-driven-development/cli/bootstrap.py` | Add explicit doctor-mode selection and separate operational-ledger checks from common source-controlled checks. |
| `spec-driven-development/cli/test_bootstrap.py` or one focused `test_sdd055.py` | Add isolated mode-contract tests; remove no existing strict B-1 coverage. |
| `.github/workflows/doctor.yml` | Invoke explicit CI mode and point to ADR-025. |
| `spec-driven-development/docs/ADR/021-ci-doctor-validation.md` | Mark superseded by ADR-025. |
| `spec-driven-development/docs/ADR/025-local-and-ci-doctor-profiles.md` | Record the corrected architectural contract. |

## Traceability

| Requirement | Acceptance |
|-------------|------------|
| R-1 | AC-1, AC-3, AC-7 |
| R-2 | AC-1, AC-2 |
| R-3 | AC-4 |
| R-4 | AC-3 |
| R-5 | AC-5, AC-8 |
| R-6 | AC-6 |
| R-7 | AC-2, AC-3, AC-4, AC-5, AC-7 |
| R-8 | AC-1..AC-5 |
| R-9 | AC-9 |
| R-10 | AC-8, AC-10 |
