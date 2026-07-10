---
id: SDD-20260710CIDOCTOR-clarify
type: clarification
status: done
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-fresh-checkout-ci-doctor-repair
---

# CLARIFY: SDD-055 -- Fresh-checkout CI doctor repair

- Feature ID: SDD-055
- Classification: P1 repair; out-of-sprint precondition before PI-9 Sprint 23
- Status: closed by fixed owner decision

---

## Owner decision and evidence

The owner selected repair over waiver and authorized the pre-sprint repair path:

> "Owner approved Option 1 on 2026-07-10: authorize the pre-Sprint-23 CI repair, push it, verify public CI green, then return control to Sprint EM."

This approval authorizes the repair, its push, and public-CI verification. It does
not start, rescope, or otherwise alter Sprint 23.

## Resolved questions

### Q-1 -- What does each doctor invocation validate?

- **Decision:** `doctor` has two explicit modes. Local mode validates both
  source-controlled repository health and clone-local operational ledger health.
  CI mode validates source-controlled repository health from a fresh checkout.
- **Constraint:** local mode remains the default and preserves strict B-1 checks.
  CI mode may omit only the ignored `ledger/fleet.db` reachability/query check and
  current-PI ledger-row requirement.

### Q-2 -- May CI waive database safety because the operational ledger is ignored?

- **Decision:** No. CI MUST still reject every git-tracked database file. A
  missing ignored `fleet.db` is expected in a fresh checkout and is not itself a
  CI failure; a tracked database remains a failure in every mode.

### Q-3 -- How is CI mode selected?

- **Decision:** The workflow selects it explicitly at the command line. No
  inference from `CI`, `GITHUB_ACTIONS`, or any other ambient environment
  variable is allowed.

### Q-4 -- What checks remain common?

- **Decision:** Both modes run all source-controlled checks: schema lint with
  orphan checking, governance coherence, origin-token lint, stale-doc lint, the
  test suite, the TDD gate, and DONE completeness. CI is not a reduced quality
  gate; it differs only where clone-local operational state is unavailable by
  design.

### Q-5 -- How are tests isolated?

- **Decision:** New SDD-055 tests use temporary roots and scratch git/database
  fixtures, clear or control environment variables, and invoke mode explicitly.
  They MUST NOT depend on or mutate the real checkout's ignored `fleet.db`,
  current PI rows, branch, or ambient CI variables.

### Q-6 -- Is governance changed?

- **Decision:** ADR-025 supersedes ADR-021's claim that local and CI validation
  are identical. No constitution edit, dependency, schema migration, waiver, or
  Sprint 23 artifact change is authorized.
