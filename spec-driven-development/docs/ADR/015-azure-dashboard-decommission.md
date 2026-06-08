---
id: ADR-015
type: spec
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# ADR-015: Azure Dashboard Decommission

- Date: 2026-06-08
- Status: **accepted**
- Accepted: 2026-06-08 by Rodolfo Lerma via VS Code Copilot EM approval prompt.
- Authors: Principal Cloud Security Architect (EM dispatch, SDD-035 T-035-02)
- Related spec: `specs/2026-06-08-azure-decommission/`
- Gate: **G1 Level-2 owner approval required before any teardown, workflow repair, OIDC removal, or Azure mutation**

> **Frontmatter note:** `status: active` is the SDD-FDC-001 carrier
> used for an in-flight ADR artifact. The substantive ADR status above
> was accepted by Rodolfo on 2026-06-08 via VS Code Copilot EM
> approval prompt.

---

## Context

SDD-007 shipped a live Azure-hosted Bridge Dashboard on 2026-05-16:
Azure Container Apps, Container Apps Environment, Azure Container
Registry, Log Analytics, Entra ID Easy Auth, and a single-user access
model. The deployment was appropriate for the original request: a
secure, owner-only live dashboard in Azure.

Owner direction changed on 2026-06-08: Azure hosting is no longer the
right strategic surface because the framework should be easy to share
with other people and teams. The local dashboard has become the durable
workflow surface, and cloud hosting now creates a forked governance
question: every future UI investment has to decide whether it targets
the local dashboard, the Azure dashboard, or both.

T-035-01 inventory confirms the Azure deployment still exists in the
recorded Visual Studio Enterprise subscription:

- Subscription: `05e7b074-305c-48d8-9bd0-ce5305cd027c`
- Tenant: `c6d3fc52-e612-4f5e-947c-9f16c3e5ccbb`
- Resource group: `rg-bridge-dashboard`
- Resource count: 4 direct resources in `az resource list`
- Resources: Log Analytics workspace `workspace-rgbridgedashboardEkLi`,
  Container Apps Environment `cae-bridge-dashboard`, Container Registry
  `ca24921a026cacr`, Container App `state-dashboard`
- Entra app: `Bridge Dashboard Auth`, client id
  `625bdb84-d2e6-4853-96a9-f601571e3a0f`
- Service principal: `Bridge Dashboard Auth`, object id
  `8b2fc156-312a-4f58-9f60-ac9dd69a0aa1`
- Azure-side federated credentials: 0 currently listed
- Repo reference manifest: 232 grep rows for the live URL and resource
  names, including `.github/workflows/deploy-dashboard.yml`

The ARM export emitted one warning: Azure CLI could not export
`Microsoft.OperationalInsights/workspaces/dataSources`. The Log
Analytics workspace itself is still captured in the resource list and
ARM template export, so the decommission target set remains clear.

This ADR reverses the 2026-05-16 cloud-deploy commitment. Per
`constitution/decision-policy.md`, reversing a shipped architectural
commitment is a Level-2 decision and requires owner approval before the
teardown begins.

---

## Decision

Decommission the Azure-hosted Bridge Dashboard and concentrate all
future dashboard/UI investment on the local dashboard served by:

```powershell
python spec-driven-development/cli/state_builder.py serve
```

Approval of this ADR authorizes SDD-035 Phase 2 and Phase 3 to proceed
in the task order already locked in `tasks.md`:

1. Scan and repair or remove Azure-dependent GitHub Actions workflows.
2. Disable Container App ingress as a kill switch.
3. Remove any OIDC/federated credential trust surfaces.
4. Delete `rg-bridge-dashboard` and all child resources.
5. Delete the Entra app registration and service principal.
6. Retire `PROVISIONED.md` to `docs/archive/`.
7. Purge active docs of live Azure dashboard references.
8. Verify the local dashboard remains functional.

This decision does **not** authorize starting Sprint 8 work, changing
`constitution/principles.md`, redesigning the dashboard UI, adding new
cloud providers, or deleting historical spec records beyond the single
`PROVISIONED.md` retirement explicitly listed in SDD-035.

---

## Consequences

Positive consequences:

- Removes the only tenant-bound live surface from the framework's core
  operating model.
- Makes the local dashboard the single UI source of truth for PI-6
  dashboard reinvestment.
- Reduces governance drag from maintaining an unused cloud fork.
- Eliminates future risk from an orphaned public ingress surface, even
  though it is currently protected by Entra ID.
- Simplifies sharing the framework with other users: no Azure resource
  provisioning, Entra app registration, OIDC setup, or tenant-specific
  documentation is needed for the default experience.

Negative consequences:

- The public Azure URL stops resolving after teardown.
- Any existing workflow or doc that assumes the Azure deployment exists
  must be repaired or retired.
- A future cloud resurrection will require re-provisioning rather than
  toggling an existing deployment back on.
- The owner loses browser access to the dashboard from machines where
  the repo is not cloned and the local server is not running.

Residual risks after decommission:

- Historical docs will still mention Azure as a past deployment unless
  intentionally archived or marked historical.
- The local dashboard still needs its own usability investment; SDD-035
  removes cloud ambiguity but does not improve UI by itself.
- If any Azure resource is outside `rg-bridge-dashboard` and not tied to
  the known Entra app, T-035-05 verification must catch it before close.

Reversibility:

- `azure-resource-inventory.json` preserves the ARM template export,
  resource list, Entra app metadata, service principal metadata, and
  federated credential state from T-035-01.
- Estimated resurrection effort is about 2 hours for an owner familiar
  with the original SDD-007 deployment, assuming Azure CLI access and no
  new tenant policy blockers.

---

## Cost-Savings Analysis

Dollar cost is expected to be near $0/month under the Visual Studio
Enterprise / MSDN credit profile because the Container App is configured
for scale-to-zero (`minReplicas = 0`, `maxReplicas = 2`). The material
savings are governance and attack-surface reduction rather than direct
Azure spend.

Estimated recurring savings:

- Cloud governance review: about 60 minutes/month avoided.
- Dashboard documentation drift checks: about 20 minutes/month avoided.
- CI/OIDC/Azure workflow maintenance checks: about 20 minutes/month
  avoided.
- Total owner/agent attention saved: about 100 minutes/month.

Estimated one-time cost to decommission:

- T-035-01 inventory: complete.
- T-035-02 ADR and approval: small.
- T-035-03..T-035-09 teardown, docs purge, verification, close: medium.
- Payback period on governance time: roughly 1 to 2 months.

---

## Alternatives Considered

- **Keep as-is.** Rejected. This preserves a low-dollar-cost resource,
  but keeps the framework tied to one tenant and keeps future dashboard
  work split across local vs cloud surfaces.

- **Keep Azure as a staging environment.** Rejected. The dashboard has
  no separate staging-only behavior; the cloud deployment wraps the same
  local `state_builder.py serve` path. Keeping it as staging adds a
  release surface without adding meaningful test coverage.

- **Migrate to a different cloud or static host.** Rejected. The owner
  direction is to concentrate UI effort locally, not to move hosting
  vendors. A different host would keep the same portability problem in a
  new shape.

- **Pause but do not delete resources.** Rejected. Disabling ingress
  alone leaves Entra app registrations, docs, workflow assumptions, and
  Azure governance surface in place. SDD-035's goal is clean
  decommission, not temporary suspension.

---

## Owner Approval

- [x] Approved by Rodolfo Lerma on 2026-06-08 via VS Code Copilot EM approval prompt.
- [ ] Rejected (reason): n/a
- [ ] Deferred (resubmit after): n/a

**G1 is OPEN as of 2026-06-08.** This approval unlocks the later
SDD-035 task sequence, but no Azure teardown, GitHub Actions workflow
repair/removal, OIDC trust removal, or Azure mutation has been started
by this T-035-02 session.