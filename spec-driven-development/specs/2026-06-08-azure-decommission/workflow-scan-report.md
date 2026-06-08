---
id: SDD-20260608AZUREDECOM-workflow-scan
type: index
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# Workflow Scan Report: SDD-035 Azure Decommission

- Task: T-035-03
- Date: 2026-06-08
- Gate state: G1 open via accepted ADR-015; G2 not started
- Scope: `.github/workflows/*.yml`

---

## Scan Command

```powershell
git grep -n -i -E "azure/login|azure-credentials|containerapp|AZURE_CLIENT_ID|azurecontainerapps|state-dashboard|rg-bridge-dashboard|ca24921a026cacr" -- .github/workflows
```

## Findings

| Workflow | Azure dependency matches | Decision | Rationale |
|----------|--------------------------|----------|-----------|
| `.github/workflows/deploy-dashboard.yml` | `ACR_NAME: ca24921a026cacr`; `IMAGE_NAME: state-dashboard`; `CONTAINER_APP: state-dashboard`; `RESOURCE_GROUP: rg-bridge-dashboard`; `azure/login@v2`; `client-id: ${{ vars.AZURE_CLIENT_ID }}`; `az containerapp update` | Remove entire workflow | The workflow has no non-Azure behavior. Its sole purpose is OIDC login, ACR build, and Azure Container Apps deploy for the dashboard being decommissioned. Editing out Azure steps would leave an empty workflow. |

No other workflow files exist in `.github/workflows/` at scan time.

## Repair Plan

1. Delete `.github/workflows/deploy-dashboard.yml`.
2. Repurpose `spec-driven-development/cli/test_deploy_workflow.py` from validating the obsolete deploy workflow to enforcing that the Azure dashboard deploy workflow remains retired.
3. Verify post-repair grep under `.github/workflows/` returns no Azure deployment keyword matches.

## Post-Repair Expected State

- `.github/workflows/` contains no Azure deployment workflow.
- No workflow consumes `azure/login` or Azure OIDC variables.
- No workflow references `rg-bridge-dashboard`, `state-dashboard`, `ca24921a026cacr`, or Azure Container Apps deployment commands.