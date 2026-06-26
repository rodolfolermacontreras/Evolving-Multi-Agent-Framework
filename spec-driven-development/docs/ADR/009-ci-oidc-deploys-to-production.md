# ADR-009: CI auto-deploys to production via OIDC federation

- Date: 2026-05-16
- Status: superseded by ADR-021

## Context

The cloud-deployed Bridge dashboard (SDD-007) currently reaches production
via a human running the documented deploy runbook. The REC-3 hardening item
in `spec-driven-development/specs/2026-05-16-cloud-dashboard/SECURITY-REVIEW.md`
drafted -- but deferred -- a GitHub Actions workflow that would let CI deploy
to Azure Container Apps automatically using OIDC federated credentials (no
stored client secret).

Feature `2026-05-16-dashboard-about-and-freshness` (SDD-009) commits to a
5-minute freshness SLO for the live dashboard after a push to master. That
SLO is not achievable with a human-in-the-loop deploy. This is the first
time the project will let an automated pipeline mutate a production
workload, so the pattern deserves a recorded decision rather than living
only inside one feature spec.

## Decision

Adopt **GitHub Actions OIDC federation** as the canonical pattern for any
CI-driven deploy to a production workload owned by this project.

Concretely:
- The workflow declares `permissions: id-token: write` and uses Azure login
  via OIDC. No client secret, no PAT, no service principal password is
  stored in repo, in workflow secrets, or in any other persistent store.
- The federated credential in Entra is scoped to a single repository and a
  single ref (e.g. `repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master`).
- The deploy target (Azure role assignment) is the smallest scope that
  permits the operation (e.g. ACA revision update on one Container App,
  not subscription contributor).
- Workflow file changes are themselves owner-gated by the normal commit
  path to master.

This pattern is the default for future CI deploys (other Container Apps,
Functions, Static Web Apps, etc.). Deviations require a superseding ADR.

## Consequences

Positive:
- Bounded production freshness (enables SDD-009's 5-minute SLO).
- No long-lived deploy secret to rotate, leak, or revoke.
- Federated credential is observable and revocable from one Entra blade.
- Reuses an Entra pattern already approved for SDD-007.

Negative:
- A compromised commit to master is a compromised production deploy. The
  blast radius now includes "automated push to ACA revision." Mitigation:
  branch is owner-gated, role assignment is minimum-scope, ACA revision
  history allows fast rollback.
- A failed deploy leaves the live workload stale until the workflow is fixed
  or a manual deploy runs. Mitigation: default GitHub Actions failure
  notifications go to the repository owner.
- Workflow file becomes part of the security perimeter -- any change to
  permissions, triggers, or target resource is effectively a privilege
  change and should be reviewed accordingly.

Neutral:
- Adds one workflow file to `.github/workflows/` per deploy target.
- Adds one federated credential per (app registration, ref) pair in Entra,
  recorded in the relevant `PROVISIONED.md`.

## Alternatives Considered

- **Stored service principal client secret in GitHub Actions secrets.**
  Rejected: introduces a long-lived high-privilege secret with rotation
  burden and leak risk; explicitly the posture REC-3 was designed to avoid.
- **Manual deploys only (status quo from SDD-007 v1).** Rejected: cannot
  meet the SDD-009 5-minute freshness SLO; couples freshness to operator
  availability.
- **Runtime repo sync inside the container (volume mount or startup `git
  pull`).** Rejected in clarification Q1: violates the immutable-image
  posture, adds repo credentials to the runtime, and couples cold-start
  time to network I/O.
- **Self-hosted runner with managed identity.** Rejected: adds an
  always-on runner host (cost + patching) for a workload whose whole point
  is scale-to-low; OIDC from GitHub-hosted runners gives the same identity
  guarantees without the runner footprint.

## Superseded by ADR-021

This ADR is superseded by
[ADR-021: CI runs the doctor validation gate](021-ci-doctor-validation.md).

ADR-009 described an OIDC deploy-to-production workflow that was never
implemented -- no `deploy.yml` exists and the live dashboard is no longer the
project's CI concern. SDD-046 ("Make promises true") instead adds a CI workflow
that runs `make doctor` (validation only: tests, schema lint, governance, origin
tokens, ledger truth, TDD gate, DONE completeness) with no Azure login, no
secret, and no production mutation. ADR-021 records that decision and is the
canonical CI pattern going forward. If a CI deploy is ever needed again, a new
ADR must supersede ADR-021 and may re-adopt the OIDC pattern recorded here.
