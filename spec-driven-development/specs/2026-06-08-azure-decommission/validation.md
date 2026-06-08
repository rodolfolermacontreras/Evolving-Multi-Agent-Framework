---
id: SDD-20260608AZUREDECOM-validation
type: validation
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# Validation Contract: SDD-035 -- Azure Dashboard Decommission

- Spec Reference: `spec.md` (SDD-035)
- Contract Date: 2026-06-08
- Author: Principal Cloud Security Architect (EM dispatch, Phase A.3)
- Lock Point: **AT SCAFFOLD (2026-06-08)** -- no CLARIFY round needed

---

> **CONTRACT LOCKED 2026-06-08 at scaffold** per owner direction
> 2026-06-08 (Option 3 hybrid no-silent-slip precedent applies). No
> REQUIRED item may be deferred from this spec's close.
>
> CLARIFY is not required: the decision is owner-driven and
> operational, not technical-discovery. All design questions are
> resolved by the dispatch direction itself ("Azure not sustainable,
> especially if we want to share this tool to others. Concentrate all
> efforts on local dashboard (UI)").
>
> **Level-2 gate inside this contract: R10 (ADR-015) MUST be checked
> before any of R2 / R3 / R4 (Azure teardown / OIDC removal /
> workflow repair) may begin.** This ordering is enforced by the task
> dependency graph in `tasks.md`.
>
> Rule (Article X): zero unchecked REQUIRED items before
> implementation is considered complete. REQUIRED items cannot be
> loosened after lock without an explicit Level-2 decision recorded
> here with owner signature and a new carry-over spec ID.

---

## Required Items (LOCKED at scaffold 2026-06-08)

- [ ] **R1 -- Azure resource inventory + repo grep manifest committed.**
  Before any teardown, T-035-01 produces
  `specs/2026-06-08-azure-decommission/azure-resource-inventory.json`
  containing the complete configuration of every Azure resource under
  `rg-bridge-dashboard` plus the Entra app registration + service
  principal + OIDC federated credential. A repo-wide grep manifest
  (`specs/2026-06-08-azure-decommission/repo-references.md`) lists
  every in-repo reference to the live Azure URL
  (`state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io`)
  and every reference to an Azure resource name from the inventory.
  Both files are committed before T-035-02 ADR drafting begins.
  Task: T-035-01.

- [ ] **R2 -- All Azure resources deleted (verifiable).**
  After T-035-05 completes, the following are verifiably absent:
  Container App `state-dashboard`, Container Apps Environment
  `cae-bridge-dashboard`, Container Registry
  `ca24921a026cacr.azurecr.io`, Log Analytics workspace (auto-created
  with the environment), Resource Group `rg-bridge-dashboard`. Any
  Key Vault or Storage Account discovered in R1 inventory is also
  deleted. Verification: `az group show -n rg-bridge-dashboard`
  returns `ResourceGroupNotFound`; screenshot or CLI output committed
  to spec dir as `verification-azure-delete.txt`. Task: T-035-05.
  **Gated on R10.**

- [ ] **R3 -- OIDC trust removed from GitHub Actions repo settings.**
  After T-035-05 completes, GitHub repo Settings -> Secrets and
  variables -> Actions -> Federated credentials shows zero entries
  for the decommissioned Entra app
  (`625bdb84-d2e6-4853-96a9-f601571e3a0f`). The Entra app itself is
  deleted: `az ad app show --id 625bdb84-d2e6-4853-96a9-f601571e3a0f`
  returns not-found. Verification screenshot committed.
  Task: T-035-05 (sub-step HITL). **Gated on R10 and R4.**

- [ ] **R4 -- GitHub Actions workflows scanned and repaired.**
  T-035-03 enumerates every workflow file under `.github/workflows/`
  that consumes the OIDC trust or references the Azure deployment
  (search for keywords `azure/login`, `azure-credentials`,
  `containerapp`, `client-id: ${{ secrets.AZURE_CLIENT_ID`, plus the
  live Azure URL). The enumeration is committed as
  `specs/2026-06-08-azure-decommission/workflow-scan-report.md`.
  T-035-04 either repairs each workflow (removing Azure dependency)
  or removes the workflow entirely with rationale recorded in the
  scan report. After T-035-04, no workflow under `.github/workflows/`
  contains Azure-deployment dependencies. Tasks: T-035-03, T-035-04.
  **Must complete before R3 (so OIDC removal does not silently break
  active pipelines).**

- [ ] **R5 -- PROVISIONED.md retired to docs/archive/.**
  `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` is copied to
  `spec-driven-development/docs/archive/PROVISIONED.md` with a
  retirement note prepended:
  > # RETIRED 2026-06-08 (SDD-035)
  > This document recorded the live Azure deployment of the Bridge
  > Dashboard (2026-05-16..2026-06-08). The deployment was
  > decommissioned per SDD-035 / ADR-015. This copy is preserved as
  > historical record only; the cloud URL it references no longer
  > resolves.
  The original at `specs/2026-05-16-cloud-dashboard/PROVISIONED.md`
  is then deleted. Both moves committed in T-035-07. Task: T-035-07.

- [ ] **R6 -- roadmap.md PI-3 SDD-007 entry flipped to DECOMMISSIONED.**
  `spec-driven-development/constitution/roadmap.md` PI-3 SDD-007 entry
  (currently `Shipped 2026-05-16`) is updated to `DECOMMISSIONED
  2026-06-DD per SDD-035 ADR-015 commit <CLOSE_SHA>`. The original
  shipping note is preserved as historical context (e.g. as a
  parenthetical or a struck-through note); the status field is the
  one that flips. Task: T-035-07.

- [ ] **R7 -- README and top-level docs purged of Azure dashboard
  references.** `README.md` (repo root) and
  `spec-driven-development/README.md` are scanned and edited so that
  no live Azure URL and no reference to the Azure-hosted dashboard
  remain. Any reference is either removed or replaced with the local
  invocation (`python spec-driven-development/cli/state_builder.py
  serve`). Verification: `git grep -i
  "azurecontainerapps\|state-dashboard\.politehill"` returns zero
  matches under `README.md` and `spec-driven-development/README.md`
  (matches in `specs/2026-05-16-cloud-dashboard/` and
  `docs/archive/` are expected; matches in this spec dir are also
  expected). Task: T-035-07.

- [ ] **R8 -- BACKLOG.md SDD-007 status flipped to DECOMMISSIONED.**
  `spec-driven-development/backlog/BACKLOG.md` SDD-007 row (currently
  `Shipped 2026-05-16 | DEPLOYED (v1 live, see PROVISIONED.md)`) is
  updated to `DECOMMISSIONED 2026-06-DD | Closed per SDD-035 /
  ADR-015 commit <CLOSE_SHA>`. The SDD-007 row is otherwise preserved
  (priority, RICE, original title) to retain historical record.
  Task: T-035-07.

- [ ] **R9 -- state_builder.py cloud-aware code-path review (additive
  removal only).** `cli/state_builder.py` is reviewed for cloud-aware
  code paths (Entra ID auth headers / cookies, OIDC-specific URL
  handling, container-specific environment variables like
  `PORT`, `WEBSITES_PORT`, `CONTAINER_APP_*`). Any such code is
  removed with explicit commit-message marker
  `removed per SDD-035 ADR-015`. **PI-4 frontmatter lock surface
  (commits `4f81df6`, `0913583`) and PI-5 Sprint 7 UI lifecycle
  variant lock surface MUST be preserved byte-identical.**
  Verification: `git diff --stat <PRE_COMMIT> -- cli/state_builder.py`
  shows only deletions (no functional additions); lock-surface line
  ranges show zero changes. If NO cloud-aware code paths exist, R9
  is satisfied by a written note in the close-commit body stating
  "R9: no cloud-aware code paths found in state_builder.py; no
  changes needed." Task: T-035-06.

- [ ] **R10 -- ADR-015 drafted, owner-approved, committed.**
  `spec-driven-development/docs/ADR/015-azure-dashboard-decommission.md`
  is drafted in T-035-02 per the ADR template at
  `docs/ADR/TEMPLATE.md`. The ADR documents: (a) the decision (reverse
  the 2026-05-16 SDD-007 cloud-deploy commitment), (b) the context
  (cost burn + governance ambiguity + portability blocker), (c) the
  alternatives considered and rejected (keep-as-is; keep-as-staging;
  migrate-to-different-cloud), (d) the consequences (URL stops
  resolving; resurrection cost ~2 hours via inventory replay), (e)
  the cost-savings analysis. **The ADR is owner-approved in writing
  before T-035-05 (Azure teardown) begins.** Owner approval is
  recorded inline in the ADR (e.g. "Approved by Rodolfo Lerma
  2026-06-DD via <channel>") and is the gate that unlocks R2 / R3 /
  R4. Task: T-035-02. **This is the Level-2 gate.**

- [ ] **R11 -- Test suite preserves 305 baseline; schema_lint clean.**
  After all R1..R10 close, `python -m pytest spec-driven-development/
  --tb=no -q` reports passed >= 305 (Sprint 7 baseline) with 2
  skipped. `python spec-driven-development/cli/schema_lint.py` exits
  0. `exec/state.md` regenerates cleanly via
  `python spec-driven-development/cli/state_builder.py`.
  Task: T-035-09.

- [ ] **R12 -- Local dashboard end-to-end functional verification.**
  After T-035-05..07 complete, T-035-08 runs `python
  spec-driven-development/cli/state_builder.py serve` and:
  (a) the server boots without error;
  (b) every documented route (`/`, plus any `/state*`, `/work-index`,
  any other route exposed by the serve handler) returns HTTP 200;
  (c) `curl -s` of each route returns HTML containing zero matches
  for `azurecontainerapps`, `politehill-ac7984d9`, `state-dashboard`
  (as a deployment name; `state-dashboard.*.html` filenames inside
  the docs tree are not part of the rendered HTML output), or any
  Azure resource name from the R1 inventory.
  Verification commands + outputs committed to spec dir as
  `verification-local-dashboard.txt`. Task: T-035-08.

## Optional / Best-Effort Items

- [ ] **O1 -- Cost-savings calculation documented in spec or ADR.**
  Per-month estimate (governance attention + dollar floor + any
  ancillary savings) multiplied by time-to-payback for the
  engineering effort spent on SDD-035 execution. Lives in either
  `spec.md` (under "Cost-Savings Note") or `ADR-015` (preferred).
  Floor is given in spec.md: $0/month dollar cost; ~100 minutes/month
  governance attention. O1 is checked if ADR-015 includes a more
  rigorous estimate.
- [ ] **O2 -- PI-5 retro note added (or queued for PI-5 close retro).**
  A one-paragraph lesson is added to a future PI-5 retro section (or
  queued as a tracked note for the PI-5 close retro) titled
  "What we learned about cloud dashboard ROI", capturing: the
  original cloud-deploy reasoning, the actual usage pattern, the
  decommission rationale, and the durable lesson for future
  cloud-deploy decisions. Filed under
  `spec-driven-development/sprints/PI-5/lessons.md` or equivalent
  per current PI-5 retro location. O2 is OPTIONAL because the lesson
  is durably recorded in ADR-015 either way; the retro note is a
  visibility enhancement.

## Specific Test Coverage Required

- [ ] **Regression (R11)**: full pytest run >= 305 passed + 2
  skipped; `schema_lint` exits 0. No new tests added by this spec
  (operational decommission only).
- [ ] **Lock-surface preservation (R9)**: `git diff --stat <BASE> --
  cli/state_builder.py` reviewed by hand; PI-4 frontmatter lock
  surface and PI-5 UI lifecycle variant lock surface lines confirmed
  unchanged.
- [ ] **Azure-deletion verification (R2, R3)**: CLI output / screenshot
  for `az group show` (not-found), `az ad app show` (not-found),
  GitHub repo Federated credentials view (empty), committed to spec
  dir.
- [ ] **Workflow-scan verification (R4)**: scan report committed; post-
  repair `git grep` for Azure workflow keywords returns zero matches
  under `.github/workflows/`.
- [ ] **Docs-purge verification (R7, R6, R8)**: `git grep` for live
  URL + Azure resource names under `README.md`, `roadmap.md`,
  `BACKLOG.md` returns zero matches (or only matches in archive /
  historical record sections that are documented as intentional).
- [ ] **Local-dashboard verification (R12)**: route smoke test output
  committed to spec dir.

## Manual Checks

- [ ] Owner reviews ADR-015 at T-035-02 and either approves in
  writing or returns it with revisions. **Approval is the Level-2
  gate; no Azure teardown proceeds without it.**
- [ ] Owner performs the GitHub repo settings Federated credentials
  removal at T-035-05 (this step requires owner browser sign-in;
  cannot be automated by Cloud Security Architect).
- [ ] Owner ratifies the close commit before push (per Sprint 7
  Option 3 hybrid precedent). Ratification recorded in the close-
  commit body or in the EM session log.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] -- this is an operational decommission with no
user-facing UI changes. The local dashboard (which is user-facing)
must remain functional (R12) but is not redesigned as part of this
spec.

## Definition of Done

Implementation is merge-ready only when:

1. All twelve REQUIRED items above (R1..R12) are checked.
2. All "Specific Test Coverage Required" boxes are checked.
3. All three "Manual Checks" boxes are confirmed.
4. R10 (ADR-015) was checked BEFORE R2 / R3 / R4 (Azure teardown /
   OIDC removal / workflow repair). The dependency ordering is
   verifiable from the close-commit chain (ADR commit precedes
   teardown commits).
5. The full test suite passes (>= 305 baseline + 2 skipped, zero
   new failures).
6. `schema_lint` exits 0.
7. `exec/state.md` regenerates cleanly and is committed.
8. The close-commit references R1..R12 in its body and is
   owner-ratified before push.
9. **No REQUIRED item is marked DEFERRED.** Per owner direction
   2026-06-08 (Option 3 hybrid), SDD-035 ships clean or does not
   ship.

Any skipped REQUIRED item requires an explicit Level-2 decision
recorded here with owner signature and a new carry-over spec ID --
not a rewrite of this contract.
