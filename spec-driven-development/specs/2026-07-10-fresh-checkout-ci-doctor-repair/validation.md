---
id: SDD-20260710CIDOCTOR-validation
type: validation
status: done
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-fresh-checkout-ci-doctor-repair
---

# VALIDATION: SDD-055 -- Fresh-checkout CI doctor repair

- Feature ID: SDD-055
- Classification: out-of-sprint pre-Sprint-23 repair
- Spec: [spec.md](spec.md) | Plan: [plan.md](plan.md)

---

## Lock statement

This contract is LOCKED before implementation. Every REQUIRED item must be
proven with real command output or an isolated automated test. No item may be
waived, weakened, or silently deferred to make CI green. Repair-over-waiver is
the owner-approved disposition.

## Required items

- [x] **V-1 (explicit profile contract).** Local is the default; CI is selected
  explicitly by CLI option; no ambient-environment inference exists. (R-1)
- [x] **V-2 (local missing-ledger strictness).** Isolated local fixture with no
  `fleet.db` fails the operational ledger check. (R-2, AC-1)
- [x] **V-3 (local current-PI strictness).** Isolated active-PI scratch ledger
  with zero matching rows fails; adding one row passes. (R-2, AC-2)
- [x] **V-4 (fresh CI boundary).** Isolated CI-mode fixture without ignored
  `fleet.db` does not fail for ledger reachability or current-PI row absence, and
  reports those local-operational checks as inapplicable/omitted. (R-4, AC-3)
- [x] **V-5 (tracked DB rejection).** An isolated scratch git repository with a
  tracked `.db` fails in BOTH local and CI modes. (R-3, AC-4)
- [x] **V-6 (all source checks retained).** An isolated spy/mocked harness proves
  both modes invoke schema-orphan lint, governance, origin lint, stale-doc lint,
  tests, TDD gate, and DONE completeness. (R-5, AC-5)
- [x] **V-7 (ambient independence).** Mode-contract tests pass with relevant
  environment variables cleared and prove contradictory `CI` /
  `GITHUB_ACTIONS` values do not alter explicitly selected behavior. Tests do
  not read or mutate the real checkout ledger or current-PI rows. (R-7, AC-7)
- [x] **V-8 (workflow uses CI mode).** `doctor.yml` explicitly selects CI mode;
  retains push/PR, contents-read, Python 3.12, and validation-only steps; contains
  no secret, Azure, deploy, or production mutation. (R-6, AC-6)
- [x] **V-9 (quality baseline).** Full pytest is >= 616 passed / 2 skipped;
  schema/origin/staledoc lints clean; Article X FootprintLockGuard 3/3 PASS;
  local doctor green. (R-10, AC-8)
- [ ] **V-10 (public CI proof).** The owner-authorized repair commit is pushed
  and its public GitHub doctor run is green; URL/run ID recorded. (R-9, AC-9)
- [x] **V-11 (scope integrity).** Diff contains no constitution edit, Sprint 23
  edit, dependency, DB schema change, tracked DB, or gate waiver. (R-9, R-10,
  AC-10)

## Manual evidence

- [x] **M-1 (owner authorization recorded).** Verbatim: "Owner approved Option 1
  on 2026-07-10: authorize the pre-Sprint-23 CI repair, push it, verify public CI
  green, then return control to Sprint EM."
- [x] **M-2 (classification recorded).** SDD-055 is an out-of-sprint P1
  precondition before Sprint 23; these design artifacts do not start or alter
  Sprint 23.
- [x] **M-3 (handoff complete).** Principal Software Developer receives the
  locked contract and performs implementation/review without scope expansion.

## Implementation evidence

- TDD RED: initial `test_sdd055.py` run failed because `--mode` and the `mode`
  parameter did not exist (4 failures plus profile subtest errors).
- Targeted GREEN: `pytest cli/test_sdd045.py cli/test_sdd055.py` -> **28 passed,
  2 subtests passed**. Tests use temporary roots, scratch git/SQLite, explicit
  profiles, controlled environment variables, and checker-boundary mocks.
- Full suite: **623 passed, 2 skipped, 2 subtests passed**.
- Lints: schema `--check-orphans`, origin, and staledoc all clean.
- Article X: `TestS1FootprintLockGuard` -> **3 passed, 245 deselected**.
- Strict local doctor: all checks passed; B-1 reported **PI-9: 3 row(s)**.
  Direct read-only SQLite query returned `PI-9, 3`; `git ls-files -- '*.db'`
  returned no tracked databases.
- Fresh clone: ignored `fleet.db` absent; explicit
  `python spec-driven-development/cli/bootstrap.py doctor --mode ci` passed all
  source checks, reported both operational checks `N/A`, and ran the same full
  suite (**623 passed, 2 skipped, 2 subtests passed**).
- Scope review: only doctor implementation/tests/workflow and SDD-055 lifecycle
  evidence changed. No constitution, Sprint 23, dependency, schema, database,
  dashboard, Article X locked function, or waiver change.
- Public CI: **PENDING PUSH/RUN OBSERVATION**. V-10 remains unchecked until the
  owner-authorized repair commit's public run is observed green and linked here.

## Close rule

SDD-055 may close only when V-1..V-11 and M-1..M-3 are checked with evidence.
Local green without public CI green is insufficient; public CI green obtained by
waiver or skipped checks is also insufficient.
