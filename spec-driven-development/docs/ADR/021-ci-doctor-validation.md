# ADR-021: CI runs the doctor validation gate

- Date: 2026-06-26
- Status: accepted
- Supersedes: ADR-009

## Context

ADR-009 (proposed 2026-05-16) recorded an OIDC pattern for letting GitHub
Actions deploy the cloud dashboard to Azure Container Apps automatically. That
workflow was never implemented: no `deploy.yml` exists, the live dashboard is no
longer the project's active concern, and the framework's CI need shifted from
"ship a workload" to "prove the framework keeps its own promises."

SDD-046 ("Make promises true") closes the gap between what the framework asserts
and what it mechanically enforces. It adds two blocking checks -- a TDD gate
(`tdd_gate_check.py`) and DONE completeness (`done_check.py`) -- and a current-PI
ledger-truth check, all wired into `run_doctor`. Locally, `make doctor` is the
single source of truth for whether the repository is in a valid state. Nothing
ran that gate on push or pull request, so a contributor (human or agent) could
regress the framework and only find out by remembering to run the gate by hand.

## Decision

Adopt a single **validation-only** GitHub Actions workflow,
`.github/workflows/doctor.yml`, as the canonical CI for this framework.

Concretely:
- Triggers on `push` and `pull_request`.
- One job: `actions/checkout` -> `actions/setup-python` (3.12) -> `make doctor`.
- `permissions: contents: read` only. No `id-token`, no Azure login, no
  `secrets.*` reference, no deploy step, no production mutation.
- `make doctor` runs `bootstrap.py doctor`, which is the same gate developers run
  locally: tests, schema lint, governance coherence, origin-token absence, ledger
  reachability, current-PI dispatch rows, the TDD gate, and DONE completeness.
- Because the workflow is pure stdlib Python validation, no dependency install
  step is required beyond `setup-python` (Article V: stdlib only).

CI and local validation are therefore identical -- the doctor is run the same way
in both places, so "green locally" and "green in CI" cannot diverge.

## Consequences

Positive:
- Every push and PR is checked against the framework's own rules automatically.
- CI has no production blast radius: it cannot deploy, cannot log into Azure, and
  holds no secret. A compromised commit cannot mutate a live workload through
  this workflow.
- Local and CI validation share one code path (`run_doctor`), eliminating the
  "passes on my machine" class of CI drift.
- The TDD gate and DONE completeness become enforced, not merely documented --
  this is the "make promises true" goal realized at the CI boundary.

Negative:
- CI is now a gate that can fail and block; a flaky or slow check would surface
  on every push. Mitigation: doctor is deterministic and stdlib-only; the test
  suite is the slowest step and already runs in seconds.
- Running the full suite on every push has a small compute cost. Accepted as the
  price of continuous validation.

Neutral:
- Adds one workflow file to `.github/workflows/`. No Entra credential, no role
  assignment, no `PROVISIONED.md` entry (unlike the superseded ADR-009 pattern).

## Alternatives Considered

- **Keep CI deploy-focused (ADR-009 as written).** Rejected: the deploy workflow
  was never built and the deploy need lapsed; the live concern is framework
  validity, not workload freshness.
- **No CI; rely on developers running `make doctor` by hand.** Rejected: that is
  exactly the unenforced-promise problem SDD-046 exists to close.
- **A CI workflow that re-implements the checks inline (bash/yaml).** Rejected:
  it would duplicate `run_doctor` and let CI and local validation drift. Calling
  `make doctor` keeps one source of truth.

If a CI-driven production deploy is ever required again, a new ADR must supersede
ADR-021 and may re-adopt the OIDC federation pattern recorded in ADR-009.
