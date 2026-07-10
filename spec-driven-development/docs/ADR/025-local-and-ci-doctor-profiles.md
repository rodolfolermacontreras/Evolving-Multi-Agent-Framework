# ADR-025: Separate source-controlled CI health from clone-local operational health

- Date: 2026-07-10
- Status: accepted
- Supersedes: ADR-021

## Owner authorization

The owner selected repair over waiver and authorized the pre-sprint repair path:

> "Owner approved Option 1 on 2026-07-10: authorize the pre-Sprint-23 CI repair, push it, verify public CI green, then return control to Sprint EM."

This is an out-of-sprint precondition before Sprint 23. It does not start, alter,
or consume Sprint 23.

## Context

ADR-021 correctly replaced deployment CI with a read-only doctor gate, but it
made an over-broad equivalence claim: local and CI validation were declared
identical, including clone-local operational ledger checks. The fleet ledger is
intentionally ignored and is initialized by local setup. A fresh GitHub checkout
therefore has no `ledger/fleet.db` and cannot carry the current PI's local
dispatch history. GitHub doctor runs #21 through #23 fail for this structural
reason even though the local baseline at `28f1262` is green (616 passed / 2
skipped, clean lints, Article X 3/3, local doctor green).

Two health domains were conflated:

- **Source-controlled health:** tracked-DB safety, schemas, governance, origin
  cleanliness, live-doc freshness, tests, TDD pairing, and DONE completeness.
- **Clone-local operational health:** ignored ledger reachability/queryability and
  current-PI dispatch rows required by strict B-1 dogfooding.

The required CI gate must be repaired, not waived. At the same time, CI must not
fabricate an operational ledger or weaken the local B-1 contract.

## Decision

Adopt two explicit profiles in the existing doctor:

1. **Local profile (default).** Runs every source-controlled check and also
   requires the ignored `fleet.db` to exist and be queryable plus at least one
   current-PI dispatch row when a PI is active. This preserves strict B-1.
2. **CI profile (explicit CLI selection).** Runs every source-controlled check.
   It omits only ignored-ledger existence/queryability and current-PI row
   requirements because those are clone-local operational state unavailable in a
   fresh checkout by design.
3. **Tracked DB guard is universal.** Both profiles inspect git-tracked database
   files and fail if any are tracked. Missing ignored `fleet.db` is acceptable in
   CI; a tracked database is never acceptable.
4. **No ambient inference.** The workflow explicitly selects CI profile at the
   command line. The doctor does not infer profile from `CI`, `GITHUB_ACTIONS`, or
   any other environment variable.
5. **Truthful reporting.** CI-only operational omissions are reported as
   inapplicable/omitted, not as passing evidence.
6. **Validation-only workflow retained.** Push and pull-request triggers,
   contents-read permission, Python 3.12, no secrets, and no deploy/production
   mutation remain unchanged.
7. **Isolated verification.** Profile tests use temporary roots and scratch
   git/database fixtures, explicitly select mode, and control ambient environment.
   They do not depend on or mutate the real checkout's ledger or PI rows.

ADR-021 is superseded because its central claim that local and CI run an
identical validation contract is false for an intentionally ignored operational
store. Its validation-only, least-privilege CI posture remains adopted here.

## Options considered

### Option A: Explicit profiles in one doctor (selected)

- Pros: preserves one source-check implementation; keeps local B-1 strict;
  models the state boundary honestly; deterministic and stdlib-only.
- Cons: local and CI invocations differ by an explicit flag; output needs an
  N/A/omitted state for two checks.

### Option B: Initialize and seed a synthetic CI ledger

- Pros: permits the old invocation to proceed.
- Cons: manufactures operational evidence, cannot represent real local dispatch
  history, and can falsely satisfy B-1. Rejected.

### Option C: Waive, soft-fail, or remove doctor CI

- Pros: immediately green status.
- Cons: abandons the enforcement promise and contradicts the fixed owner decision
  to repair rather than waive. Rejected.

## Consequences

- Positive: fresh-checkout CI can become green for the right reason while still
  running every source-controlled check.
- Positive: local doctor remains the strict validator of operational ledger
  health and current-PI dogfooding.
- Positive: tracked databases remain blocked everywhere.
- Positive: explicit mode selection and isolated tests prevent machine-specific
  ambient behavior.
- Negative: "run the same doctor" now means one implementation with explicit
  profiles, not byte-identical check sets.
- Neutral: no constitution edit, dependency, ledger schema change, deployment,
  or Sprint 23 change.

## Compliance

- [x] Owner authorization recorded verbatim.
- [x] Repair-over-waiver selected.
- [x] Stdlib-only architecture; no new dependency.
- [x] Local B-1 remains strict.
- [x] CI retains tracked-DB rejection and all source-controlled checks.
- [x] No constitution edit.
- [x] Out-of-sprint/pre-Sprint-23 classification recorded; Sprint 23 untouched.
