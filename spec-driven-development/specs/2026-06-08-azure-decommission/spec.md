---
id: SDD-20260608AZUREDECOM-spec
type: spec
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# Feature Spec: SDD-035 -- Decommission Azure dashboard; concentrate UI investment locally

- Date: 2026-06-08
- Author: Principal Cloud Security Architect (EM dispatch, Phase A.3)
- Status: ACTIVE (scaffolded; pending Level-2 owner approval before T-035-05 teardown)
- Priority: P1
- Sprint: Out-of-band (this week, 2026-06-08..2026-06-13); NOT folded into Sprint 8
- Spec ID: SDD-035

---

> ## LEVEL-2 DECISION CANDIDATE
>
> **This spec REVERSES the 2026-05-16 cloud-deploy commitment** that
> shipped SDD-007 (Azure Container Apps + Entra ID + scale-to-zero +
> OIDC CI/CD; live per
> `specs/2026-05-16-cloud-dashboard/PROVISIONED.md`).
>
> A reversal of a shipped, owner-ratified architectural commitment is a
> Level-2 decision per `constitution/decision-policy.md`. **No Azure
> resource may be torn down before T-035-02 (ADR-015) is owner-approved
> in writing.** The ADR is the gate; the teardown is the consequence.
>
> **CLARIFY not required.** The decision is owner-driven and operational,
> not technical-discovery. All design questions are resolved by the
> dispatch direction itself: "Azure not sustainable, especially if we
> want to share this tool to others. Concentrate all efforts on local
> dashboard (UI)" (owner via EM, 2026-06-08).

---

## Problem Statement

The Azure-hosted Bridge Dashboard (SDD-007, live since 2026-05-16) has
created three concrete problems that the dispatch direction
2026-06-08 makes the framework explicit about resolving.

**Cost burn and governance ambiguity.** The cloud deployment runs on
MSDN credit with `min=0, max=2` replicas and was expected to cost $0
per month under the free tier. In practice it remains a non-zero
*governance* cost: every architecture conversation now has to answer
"cloud vs local -- which is the source of truth?" before it can answer
the question the conversation was actually about. Every doc that
mentions the dashboard has to choose between the Azure URL and the
local `state_builder.py serve` URL. The framework spends owner
attention on a forked surface that nobody actually uses as their
primary workflow.

**Portability blocker for team share.** Owner direction 2026-06-08
identified the strategic blocker: "if we want to share this tool to
others." The Azure deployment is bound to a single tenant
(`c6d3fc52-...`), a single app registration
(`625bdb84-d2e6-4853-96a9-f601571e3a0f`), a single allowed user
(`rodolfolermacontreras@gmail.com`), and a single resource group
(`rg-bridge-dashboard`). Handing the framework to another team
requires re-provisioning every Azure resource, re-issuing OIDC trust,
re-registering the Entra app -- in effect re-doing SDD-007 from
scratch with no portable artifact. The local dashboard has none of
those bindings: `python spec-driven-development/cli/state_builder.py
serve` works in any clone on any laptop.

**Functional equivalence already exists.** The Azure deployment is
*not* a separate render path. SDD-007 wrapped the same
`state_builder.py serve` HTTP handler in a Container Apps image with
Entra ID ingress and OIDC CI/CD. The local dashboard renders the
same HTML from the same code path. There is no feature in the cloud
dashboard that does not exist locally. Decommissioning the cloud
surface loses zero functional capability and removes the forked
governance surface.

Owner direction (2026-06-08, via Executive Manager): "We are
decommissioning the Azure website... not sustainable, especially if
we want to share this tool to others. We will concentrate all our
efforts to improve the local dashboard (UI)." The follow-on UI
investment is filed as SDD-036 / SDD-037 / SDD-038 (PI-6 dashboard
reinvestment bundle) and is **out of scope for this spec**. SDD-035
is the operational teardown only.

## Proposed Solution

Execute a clean, traceable Azure decommission with three serialized
phases and one Level-2 owner approval gate:

1. **Audit and inventory.** Enumerate every Azure resource in
   `rg-bridge-dashboard` plus the Entra app registration, the OIDC
   federated credential, and any external dependencies (GitHub Actions
   workflows, repo-wide grep for the live URL). Export the full
   resource configuration to JSON (committed under this spec dir as
   `azure-resource-inventory.json`) so the decision is reversible from
   the audit alone if a future team needs to resurrect cloud hosting.
2. **Decision document and gate.** Draft ADR-015 documenting the
   reversal, the rationale, and the cost-savings analysis. Owner must
   approve ADR-015 in writing before any teardown begins (T-035-02
   gate).
3. **Teardown and purge.** Delete Azure resources in inventory order
   (`az group delete --no-wait` for the resource group; explicit
   commands for the Entra app + federated credential, which live
   outside the resource group). Repair or remove any GitHub Actions
   workflow that depended on the OIDC trust. Purge all docs that
   reference the cloud dashboard (PROVISIONED.md retired to
   `docs/archive/`; README + roadmap + BACKLOG updated). Verify the
   local dashboard end-to-end. Close-commit with owner ratification.

Constraints baked into the solution:

- **Additive removal only.** `cli/state_builder.py` is reviewed for
  cloud-aware code paths (Entra ID auth, OIDC-related, container-
  specific). Any such paths are removed; no functional code is added.
  PI-4 frontmatter lock and PI-5 Sprint 7 UI lifecycle variant lock
  surfaces are NOT touched.
- **Reversibility from inventory.** The exported JSON is sufficient to
  re-provision the deployment if a future decision reverses this one.
  No proprietary state lives only in Azure.
- **Explicit owner gates.** Three Level-2 ratification points: (1)
  ADR-015 approval before any teardown (T-035-02 gate); (2) GitHub
  OIDC trust removal requires owner sign-in (T-035-05 owner-action
  step); (3) close-commit owner ratification before push.
- **No Sprint 8 scope creep.** This spec is OUT-OF-BAND, scheduled
  this week. Sprint 8 already carries 14 Level-1 surfaces across
  SDD-022 + SDD-015 (per F-11 close report); folding SDD-035 into
  Sprint 8 would breach scope.

## Goal

Achieve a clean, fully-traceable decommission of the Azure-hosted
Bridge Dashboard with the local dashboard verified functional and
all documentation purged of Azure references, in time for the PI-6
dashboard reinvestment bundle (SDD-036/037/038) to land on an
unambiguous foundation.

Concretely, after this spec is DONE:

- `rg-bridge-dashboard` and all its child resources are deleted.
- Entra app `Bridge Dashboard Auth` (client id
  `625bdb84-d2e6-4853-96a9-f601571e3a0f`) is deleted.
- GitHub OIDC federated credential is removed.
- No GitHub Actions workflow references Azure (or any broken
  workflow is removed).
- `cli/state_builder.py serve` continues to render the dashboard
  locally.
- README, roadmap, BACKLOG, and any other top-level docs are purged
  of Azure dashboard references; `PROVISIONED.md` is moved to
  `docs/archive/` with a retirement note.
- ADR-015 is accepted and committed under `docs/ADR/`.
- BACKLOG SDD-007 status is flipped to `DECOMMISSIONED` with date
  and the SDD-035 close-commit SHA.
- 305-test baseline preserved; `schema_lint` exits 0.

## Acceptance Criteria

Each criterion below is a one-line success definition that traces to
a completion task ID (`T-035-NN`) and to a `validation.md` R-item.
Detailed test names live in `validation.md`.

1. **AC-1 (audit and reversibility).** Given the live Azure deployment
   in `rg-bridge-dashboard`, when T-035-01 runs the inventory step,
   then a complete configuration JSON is exported and committed under
   this spec dir, and a repo-wide grep for the live URL has documented
   every reference. Task: T-035-01. Validation: R1.
2. **AC-2 (decision document and Level-2 gate).** Given the
   intent to reverse the 2026-05-16 cloud-deploy commitment, when
   T-035-02 drafts ADR-015 and presents it for owner review, then
   the ADR is accepted in writing before any teardown begins. Task:
   T-035-02. Validation: R10. **Level-2 gate.**
3. **AC-3 (workflow scan and repair).** Given the GitHub Actions
   workflows in the repository, when T-035-03 enumerates every
   workflow that consumes the OIDC trust or references the Azure
   deployment, then a repair plan is produced and (T-035-04) executed.
   Tasks: T-035-03, T-035-04. Validation: R4.
4. **AC-4 (Azure teardown, every named resource).** Given the
   inventory from T-035-01, when T-035-05 executes resource deletion
   in inventory order, then each of the following is verifiably
   deleted: Container App (`state-dashboard`), Container Apps
   Environment (`cae-bridge-dashboard`), Container Registry
   (`ca24921a026cacr.azurecr.io`), Log Analytics workspace,
   Resource Group (`rg-bridge-dashboard`), Entra app registration
   (`Bridge Dashboard Auth`), Enterprise app / service principal,
   GitHub OIDC federated credential, any Key Vault, any Storage
   Account. Task: T-035-05. Validation: R2, R3.
5. **AC-5 (cloud-aware code-path review).** Given `cli/state_builder.py`,
   when T-035-06 reviews the file for cloud-aware code paths (Entra
   ID auth, OIDC-related, container-specific), then any such paths
   are removed via additive deletion, with the PI-4 frontmatter lock
   surface and PI-5 Sprint 7 UI lifecycle variant surface preserved
   byte-identical. Task: T-035-06. Validation: R9.
6. **AC-6 (docs purge).** Given the docs tree, when T-035-07 executes
   the purge, then: README has no Azure dashboard references;
   `constitution/roadmap.md` PI-3 SDD-007 entry status is
   `DECOMMISSIONED` with date and SDD-035 close-commit SHA;
   `backlog/BACKLOG.md` SDD-007 row status is `DECOMMISSIONED`;
   `docs/PROVISIONED.md` (the one under `specs/2026-05-16-cloud-
   dashboard/`) is moved to `docs/archive/` with a retirement note
   prepended. Task: T-035-07. Validation: R5, R6, R7, R8.
8. **AC-7 (local-dashboard functional verification).** Given the
   completion of T-035-04..07, when T-035-08 runs
   `python spec-driven-development/cli/state_builder.py serve` and
   loads every documented route, then all routes return 200 and the
   rendered HTML contains zero references to any Azure URL or Azure
   resource name. Task: T-035-08. Validation: R12.
9. **AC-8 (close verification).** Full test suite passes (>= 305
   baseline); `schema_lint` exits 0; close-commit references all
   R-items and is owner-ratified before push. Task: T-035-09.
   Validation: R11.

## Affected Modules

| Module / File | Change Type | R-Item |
|---------------|-------------|--------|
| `specs/2026-06-08-azure-decommission/azure-resource-inventory.json` | **NEW**: complete JSON dump of Azure resource configuration | R1 |
| `docs/ADR/015-azure-dashboard-decommission.md` | **NEW**: ADR documenting the reversal, cost-savings analysis, owner approval | R10 |
| `docs/archive/PROVISIONED.md` | **NEW**: retired copy of `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` with retirement note | R5 |
| `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` | **MOVED** (deleted from source after archive copy) | R5 |
| `README.md` (repo root + `spec-driven-development/README.md` if it carries Azure refs) | **EDIT**: purge Azure dashboard references | R7 |
| `constitution/roadmap.md` | **EDIT**: PI-3 SDD-007 entry status -> DECOMMISSIONED + date + commit SHA | R6 |
| `backlog/BACKLOG.md` | **EDIT**: SDD-007 row status -> DECOMMISSIONED | R8 |
| `cli/state_builder.py` | **ADDITIVE REMOVAL ONLY**: if cloud-aware code paths exist, remove them; lock surfaces (PI-4 frontmatter, PI-5 UI lifecycle variant) untouched | R9 |
| Any GitHub Actions workflow file under `.github/workflows/` that consumes the OIDC trust or references Azure | **REPAIR or REMOVE** per T-035-03 plan | R4 |
| Any other doc the T-035-01 grep flags | **EDIT**: purge Azure dashboard references | R7 |

## Data Model Changes

None. This spec is operational decommission. No new code, no new
schema, no new frontmatter field.

The `azure-resource-inventory.json` artifact is a *snapshot*, not a
schema. Its shape is whatever `az group export --resource-group
rg-bridge-dashboard` plus the Entra app `show` output produce.

## API Changes

None to local CLI surfaces. `cli/state_builder.py serve` continues to
behave exactly as it does today; the only changes (if any) are
additive removal of code paths that were never exercised in local
mode anyway.

External / cloud:

- The Azure URL `https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`
  ceases to resolve after T-035-05 completes (resource group deletion).
- GitHub repo OIDC federated credential ceases to exist after T-035-05.
- Any GitHub Actions workflow referencing the Azure deployment will
  fail unless repaired or removed in T-035-04.

## Test Strategy

This spec is operational (not code-implementing); test strategy
focuses on regression preservation and decommission verification:

- **Regression**: full pytest run >= 305 (Sprint 7 baseline); test
  count must not drop. `schema_lint` exits 0.
- **Local dashboard verification (R12)**: manual smoke test --
  `state_builder.py serve` boots, every documented route returns 200,
  rendered HTML contains zero Azure URL or Azure resource references.
- **Azure-deletion verification (R2)**: `az group show -n
  rg-bridge-dashboard` returns `ResourceGroupNotFound`. `az ad app
  show --id 625bdb84-d2e6-4853-96a9-f601571e3a0f` returns not-found.
  Verification screenshots committed to spec dir.
- **OIDC removal verification (R3)**: GitHub repo settings ->
  Federated credentials shows zero Azure-related entries.
- **Workflow scan verification (R4)**: `git grep` for Azure-related
  workflow keywords (`azure/login`, `azure-credentials`, etc.)
  returns zero results, OR any remaining workflow is documented as
  intentionally unrelated.
- **Docs-purge verification (R5..R8)**: `git grep` for the live URL
  + Azure resource names returns zero results in README,
  roadmap, BACKLOG; only documented-archive copies remain.

## Validation Contract

The binding validation contract lives in the sibling file
`validation.md`. It is **LOCKED at scaffold time (2026-06-08)** per
owner direction (Option 3 hybrid no-silent-slip precedent). No
REQUIRED item may be deferred from this spec's close. CLARIFY is
not required (decision is owner-driven and operational).

## Traceability Matrix

| Acceptance Criterion | Task | Validation Row | Docs File(s) Touched |
|----------------------|------|----------------|----------------------|
| AC-1 (audit + reversibility) | T-035-01 | R1 | `azure-resource-inventory.json` (new) |
| AC-2 (ADR-015 Level-2 gate) | T-035-02 | R10 | `docs/ADR/015-azure-dashboard-decommission.md` (new) |
| AC-3 (workflow scan) | T-035-03 | R4 | `.github/workflows/*` scan report |
| AC-3 (workflow repair) | T-035-04 | R4 | `.github/workflows/*` (repair or remove) |
| AC-4 (Azure teardown) | T-035-05 | R2, R3 | (Azure resources deleted; verification screenshots committed) |
| AC-5 (code-path review) | T-035-06 | R9 | `cli/state_builder.py` |
| AC-6 (docs purge) | T-035-07 | R5, R6, R7, R8 | `docs/PROVISIONED.md`, `README.md`, `constitution/roadmap.md`, `backlog/BACKLOG.md` |
| AC-7 (local-dashboard verification) | T-035-08 | R12 | (verification only) |
| AC-8 (close verification) | T-035-09 | R11 | close commit |

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Other systems may be reading the Azure dashboard URL (external bookmarks, third-party docs, scripts) | Medium | Low (read-only consumers; URL just stops resolving) | T-035-01 repo-wide grep enumerates every in-repo reference. Owner asked to enumerate any external bookmarks at T-035-02 ADR review. Documented references purged at T-035-07. URL-not-resolving is acceptable post-decommission behavior. |
| OIDC trust removal breaks other GitHub Actions workflows (cross-deploy, dependent pipelines) | Medium | Medium | T-035-03 explicitly enumerates every workflow that consumes the OIDC trust BEFORE T-035-05 deletes it. T-035-04 repairs or removes the dependent workflows. T-035-05 OIDC removal is gated on T-035-04 completion. |
| Azure resource teardown is irreversible | High (it's the goal) | Medium (if a future decision reverses) | T-035-01 exports complete resource configuration to JSON, committed to repo. Future resurrection re-runs `az containerapp up` against the inventory. Resurrection cost = one provisioning session (~2 hours per PROVISIONED.md verification trace). |
| `cli/state_builder.py` cloud-aware code-path removal accidentally breaks local rendering | Low | High | T-035-06 is additive removal only; verified by T-035-08 end-to-end local smoke test. PI-4 frontmatter lock surface and PI-5 UI lifecycle variant lock surface explicitly listed as DO-NOT-EDIT in `plan.md`. |
| Owner sign-in required for OIDC trust removal blocks T-035-05 mid-execution | Medium | Low | T-035-05 explicitly factored into two sub-steps: (a) AFK Azure resource deletion (no owner needed); (b) HITL GitHub repo settings OIDC removal (requires owner browser session). Sub-step (b) is queued as a single owner-action item. |
| ADR-015 owner approval delays the whole decommission | Low | Low | This is the gate, not a risk. Decommission cannot ethically proceed without it. Schedule window: dispatch direction is "this week"; expected ADR turn-around < 1 day. |
| Docs purge misses a reference; reader later finds "but the README says it's at the Azure URL" | Medium | Low | T-035-07 uses the T-035-01 grep manifest as authoritative reference list. Any later-found reference filed as a P3 docs bug, not a spec re-open. |

## Cost-Savings Note (referenced by R10 / ADR-015 / O1)

Expected dollar-cost savings: **$0/month** under MSDN free tier (the
deployment was already nominal-cost). Real savings are in *governance
attention*: every architecture conversation no longer has to answer
"cloud or local?". Quantified as ~5 minutes of decision-friction per
architecture session, ~20 sessions per month under current cadence =
~100 minutes per month of owner attention reclaimed. ADR-015 may
include a more rigorous estimate at T-035-02; this number is the
floor.

## Open Questions

None at scaffold. Decision is owner-driven and operational; design
questions are resolved by dispatch direction.

> If any ambiguity surfaces during execution that this spec did not
> resolve, the implementer MUST mark it explicitly in this section as
> **OWNER GUIDANCE REQUIRED** with a one-paragraph problem statement,
> then STOP that line of inquiry. Do not invent an answer.

## Out of Scope

- **Local dashboard improvements.** SDD-036 (lifecycle pipeline +
  4-card docs + drag-to-reorder), SDD-037 (ledger visibility +
  health pills), SDD-038 (aesthetic tokens) carry the PI-6
  dashboard reinvestment work. SDD-035 is teardown only.
- **Decommissioning anything other than the dashboard's Azure
  resources.** Other Azure resources (if any exist under different
  resource groups for unrelated reasons) are out of scope.
- **Refactoring `cli/state_builder.py`.** Only additive removal of
  cloud-aware code paths (if any exist) is in scope. Architectural
  refactors are out of scope.
- **Re-deciding the cloud-deploy strategy.** ADR-015 documents the
  decision; this spec does not relitigate it. Future reversal (if
  ever) requires a new spec + a new ADR.
- **Modifying constitution articles.** No constitutional change is
  needed; the decommission is operational. ADR-015 documents the
  consequence, not a principle change.
- **Modifying sprint-progress.md or any active sprint artifact.**
  SDD-035 is OUT-OF-BAND and is not bound to Sprint 8 or any future
  sprint. The close-commit message flags it as a Level-2 reversal
  but does not absorb sprint planning.

## Cross-Feature Notes

- **SDD-036 / SDD-037 / SDD-038 (PI-6 dashboard reinvestment).**
  These ride on the local dashboard surface. SDD-035 makes the local
  surface the single source of truth; SDD-036/037/038 then improve
  it. SDD-035 SHOULD close before SDD-036 opens so the PI-6 bundle
  starts on an unforked foundation.
- **SDD-022 (ADO / GitHub Issues sync bridge, Sprint 8).** Unrelated
  to the Azure dashboard surface. Sprint 8 proceeds in parallel with
  SDD-035's out-of-band execution.
- **SDD-007 (cloud dashboard, shipped 2026-05-16).** This spec
  flips SDD-007 status to DECOMMISSIONED in BACKLOG and roadmap. The
  SDD-007 spec dir (`specs/2026-05-16-cloud-dashboard/`) is preserved
  as historical record; only `PROVISIONED.md` inside it is retired.
