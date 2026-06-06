---
id: SDD-20260516DASH-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-16-dashboard-about-and-freshness
---

# Feature Spec: Dashboard About Section and Data Freshness

- Date: 2026-05-16
- Author: Principal Architect (co-author: Principal Software Developer)
- Status: Done
- Priority: P2
- Sprint: PI-3 Sprint A (proposed)
- Spec ID: 2026-05-16-dashboard-about-and-freshness
- Backlog items: SDD-009 (data-freshness, RICE 4.0), SDD-010 (About section, RICE 3.0)
- Depends on: SDD-007 (cloud-dashboard, DEPLOYED v1), REC-3 (OIDC workflow draft in cloud-dashboard SECURITY-REVIEW)
- Clarification record: `clarification.md` in this directory

---

## Problem Statement

**SDD-009 -- Data freshness.** The live dashboard at
`https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`
is currently served from a container image built at the time of the last
manual deployment. Any commit to master (new ledger entries, new
`exec/state.md`, new spec status) is invisible to the dashboard until a human
runs the deploy runbook. This breaks the implicit contract that the cloud
dashboard reflects the current state of the project, and silently erodes trust
in the dashboard as a source of truth.

**SDD-010 -- About / Where we are.** A newcomer landing on the cloud
dashboard sees fleet metrics and spec pipeline tables with no framing. There
is no statement of what this project is, no acknowledgement of the meta angle
(the dashboard is built by the framework whose progress it tracks), and no
quick orientation of where the project sits today (which PI, which sprint,
what's in flight). The result is a high-context artifact presented to readers
with zero context.

The two items are bundled because they share a single surface
(`cli/state_builder.py` HTTP handler + its HTML template) and because the
About section's "where we are" line is only honest if SDD-009 is solved -- a
stale dashboard claiming to show the current sprint would be worse than no
About section at all.

## Proposed Solution

1. **Auto-redeploy via OIDC (SDD-009).** Commit the REC-3 GitHub Actions
   workflow file (drafted in `2026-05-16-cloud-dashboard/DESIGN.md` Section 6)
   with both `workflow_dispatch` and `push` (master, image-relevant paths)
   triggers. Create the federated credential per the cloud-dashboard runbook
   step 5. On push to master, the workflow authenticates to Azure via OIDC
   (no stored secrets), builds the container image, and updates the ACA
   revision. The existing Easy Auth gate and single-replica-min posture are
   preserved.

2. **Hybrid About block (SDD-010).** Add an "About / Where we are" section to
   the dashboard HTML template rendered by `cli/state_builder.py`. The section
   contains:
   - A static purpose paragraph (project identity + meta caveat).
   - A dynamic one-line "Current PI / sprint / focus" pulled from
     `spec-driven-development/exec/state.md` (which `state_builder.py`
     already parses).
   No new data source is introduced; the dynamic line reuses fields already
   present in `state.md` header (`Current PI`, `Active sprint`, `Active focus`).

## Acceptance Criteria

Each criterion is phrased as a testable assertion.

1. **(Headline -- latency SLO)** Given a commit pushed to master that changes
   `spec-driven-development/exec/state.md`, when 5 minutes have elapsed since
   the push, then the change MUST be visible at
   `https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`.
2. Given any push to master, when the GitHub Actions deploy workflow runs,
   then it MUST authenticate to Azure via OIDC federated credentials only
   (no client secret, no PAT, no service principal password in repo or in
   workflow secrets).
3. Given a workflow run failure, when the failure occurs, then a GitHub
   Actions failure notification MUST be emitted to the repository owner
   (default GitHub notification settings are sufficient; no custom alerting
   stack required).
4. Given a newcomer loads the dashboard root URL, when the page renders, then
   an "About / Where we are" section MUST appear above the fold containing
   (a) a static paragraph naming the project and stating the meta caveat,
   and (b) a dynamic line displaying the current PI, active sprint, and
   active focus.
5. Given `exec/state.md` header values change, when the dashboard is
   redeployed (per AC #1), then the dynamic About line MUST reflect the new
   values without any template edit.
6. Given the workflow file is committed, when `gh workflow list` is run
   against the repo, then the deploy workflow MUST appear and be enabled.
7. Given the federated credential is created, when `az ad app
   federated-credential list` is run for the deploy app registration, then a
   credential bound to
   `repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master`
   MUST be present.
8. Given no commit to master in the preceding 24 hours, when the dashboard
   is loaded, then it MUST still serve correctly (ACA min-replicas posture
   from SDD-007 is preserved; freshness mechanism MUST NOT introduce a
   cold-start regression beyond what SDD-007 already accepted).

## Affected Modules

- Files:
  - `cli/state_builder.py` (HTML template block addition only -- About section)
  - `.github/workflows/deploy-dashboard.yml` (new -- materializes REC-3 draft)
  - `spec-driven-development/specs/2026-05-16-cloud-dashboard/SECURITY-REVIEW.md` (status update: REC-3 from DEFERRED to LANDED, in cloud-dashboard's own follow-up; out of scope for this feature's PR)
- Directories:
  - `cli/`
  - `.github/workflows/`
  - `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/`

Out-of-bounds for this spec (do not touch in implementation PR):
`Dockerfile`, any other cloud spec file, `agent/` (this is an SDD-tooling
feature, not an app-agent feature).

## Data Model Changes

None. The dynamic About line reads existing `Current PI`, `Active sprint`,
and `Active focus` fields from `exec/state.md`. No schema additions.

## API Changes

None. The dashboard HTTP handler exposes the same routes; only the HTML
payload of `/` gains an About block.

## Constraints (inherited from cloud-dashboard spec, SDD-007)

- Easy Auth gate remains in front of all dashboard routes.
- Single-user tenant (Microsoft tenant, repository owner only).
- Stdlib-only Python in `cli/state_builder.py` (no new pip dependencies).
- No new pip dependencies anywhere in this feature.
- ACA `max-replicas = 2` (cost ceiling; do not raise).
- Immutable container image (no writable volumes, no runtime `git pull`).
- OIDC federation only -- no service principal client secret stored.

## Test Strategy

- **Unit:** Add tests for the About-block template rendering in
  `state_builder.py`: given a mocked `exec/state.md` content with known
  `Current PI` / `Active sprint` / `Active focus` lines, the rendered HTML
  contains the dynamic line with those values, and contains the static
  purpose paragraph verbatim. Stdlib-only; no network.
- **Integration:** Add a workflow-syntax check via `actionlint` (already in
  the SDD lint envelope if present; otherwise a `yaml.safe_load` smoke test
  in CLI tests is acceptable as a fallback consistent with the stdlib-only
  constraint). Validate that the workflow declares `permissions: id-token:
  write` and does not declare any `client_secret`-style input.
- **End-to-end / manual:** After merge, push a no-op commit to master that
  edits `exec/state.md` (e.g. regenerate via `state_builder.py`), record the
  push timestamp, then poll the live URL until the change is visible. Record
  the elapsed seconds. AC #1 PASSES iff elapsed <= 300s.
- **Regression:** Existing `state_builder.py` test suite MUST remain green.
  Existing cloud-dashboard `PROVISIONED.md` SLOs (cold-start, scale behavior)
  MUST remain met -- verify by one cold-start probe after first auto-deploy.

## Validation Contract

The binding validation contract for this feature lives in the sibling file
`validation.md` in this feature directory. It is written during `/spec`,
locked at `/tasks`, and must have zero unchecked required items before
implementation can be considered complete. (SW Dev to author at `/plan` time
per Article X.)

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| SDD-009 freshness <= 5 min | AC #1 (manual timed push), AC #6 (workflow registered) | `.github/workflows/deploy-dashboard.yml` |
| SDD-009 OIDC-only auth | AC #2 (workflow inspection), AC #7 (federated credential present) | `.github/workflows/deploy-dashboard.yml`, Azure app registration |
| SDD-009 failure visibility | AC #3 (workflow notification) | GitHub Actions default notifications |
| SDD-010 newcomer orientation | AC #4 (section present + content), AC #5 (dynamic line tracks state.md) | `cli/state_builder.py` template |
| Inherited SDD-007 posture | AC #8 (no cold-start regression) | ACA revision config (unchanged) |

## Risks

- **CI failure leaves dashboard stale longer than 5 min.** Mitigation: AC #3
  requires that workflow failures surface via default GitHub notifications to
  the repo owner; owner is on the hook to re-run or fix. No bespoke alerting
  stack added (would violate stdlib-only / no-new-deps posture).
- **OIDC trust misconfiguration could broaden blast radius.** Mitigation:
  federated credential is scoped to a single branch (`refs/heads/master`) per
  cloud-dashboard DESIGN.md Section 6; workflow file changes require a
  commit to master, which itself is owner-gated.
- **`state.md` header format drift.** If a future change to
  `state_builder.py` renames `Current PI` / `Active sprint` / `Active focus`
  header keys, the dynamic About line silently shows nothing. Mitigation:
  unit test (see Test Strategy) asserts the dynamic line is non-empty for a
  canonical `state.md` fixture.
- **First push after merge tests the latency SLO live.** Mitigation: the
  E2E test in Test Strategy is the validation; if it fails, revert is
  cheap (workflow file deletion + ACA pin to last good revision).

## Implementation Decomposition (advisory -- SW Dev refines at /tasks)

Likely 3-4 tasks across these surfaces:
1. Author `.github/workflows/deploy-dashboard.yml` from REC-3 draft (workflow file + permissions block).
2. Create federated credential in the deploy app registration (Azure CLI runbook step; one-shot, human-executed, recorded in `PROVISIONED.md` follow-up).
3. Add static + dynamic About block to `cli/state_builder.py` HTML template, plus unit tests.
4. Live latency probe after first auto-deploy; record elapsed seconds in this feature's `validation.md`.

## Open Questions

- None. All three clarification questions were resolved on 2026-05-16 (see `clarification.md`).

## Out of Scope

- Multi-user landing pages or per-viewer personalization.
- Role-based or audience-segmented About content.
- Build-cache optimization beyond what Azure Container Apps and the default
  `docker build` layer cache already provide.
- Alerting stack beyond default GitHub Actions failure notifications.
- Auto-rollback on deploy failure (manual revert is acceptable at this scale).
- Migrating `state_builder.py` away from stdlib-only.
- Changes to Easy Auth, scale rules, or ACA `max-replicas` cap from SDD-007.
- Backfilling auto-deploy onto non-master branches.
