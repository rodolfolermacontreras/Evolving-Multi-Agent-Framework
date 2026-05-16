---
feature: cloud-dashboard
status: pre-spec design exploration
created: 2026-05-16
designer: principal-cloud-security-architect (draft Principal)
priority: P3 (backlog SDD-007)
spec_status: not yet written -- this is design, not approved scope
subscription_target: 05e7b074-305c-48d8-9bd0-ce5305cd027c (Visual Studio Enterprise, MSDN)
tenant: rodolfolermacontrerasgmail.onmicrosoft.com
cost_ceiling: $10/month
---

# Cloud Dashboard -- Design Spec (SDD-007)

> Deploy the live Bridge dashboard (`exec/state.html` served by
> `cli/state_builder.py serve`) to Microsoft Azure so the single human owner can
> view current project state from any device. Single-user, Entra-authenticated,
> scale-to-zero, near-zero cost.

This is design exploration. No provisioning. The next step is approval and a
formal `/spec` cycle (SDD-007).

---

## 1. Recommendation (one sentence)

**Run the dashboard as one container on Azure Container Apps (Consumption plan),
with public HTTPS ingress, Microsoft Entra ID built-in auth restricted to the
owner's account, scale-to-zero, image built and pushed by GitHub Actions via
OIDC federated credentials.**

## 2. Architecture

```
+---------------------------------------------------------------+
|                                                               |
|   Browser  -- https --> *.azurecontainerapps.io               |
|                              |                                |
|                              v                                |
|                  +-----------------------+                    |
|                  |  ACA built-in Easy    |                    |
|                  |  Auth (Entra ID)      |  <- enforces auth  |
|                  +-----------+-----------+                    |
|                              |                                |
|                              v                                |
|                  +-----------------------+                    |
|                  |  Container App        |                    |
|                  |  state-dashboard:N    |                    |
|                  |  minReplicas=0        |                    |
|                  |  maxReplicas=2        |                    |
|                  |  HTTP :8080           |                    |
|                  +-----------------------+                    |
|                              |  managed identity              |
|                              v                                |
|                  +-----------------------+                    |
|                  |  Log Analytics WS     |  <- container logs |
|                  +-----------------------+                    |
|                                                               |
+---------------------------------------------------------------+

CI/CD:

  GitHub repo --push main--> GitHub Actions
       |                        |
       | OIDC federation        |
       v                        v
  Entra app registration --> azure/login@v2
       |                        |
       |                        v
       |                  docker build + push to ghcr.io
       |                        |
       +----- minimum role -----+--> az containerapp update --image ghcr.io/.../state-dashboard:<sha>
              (Microsoft.App/containerApps/revisions/write
               + Microsoft.App/containerApps/read on this RG only)
```

## 3. Threat model

| Threat | Control | Residual risk |
|--------|---------|---------------|
| Anyone on the public internet hits the URL | ACA Easy Auth: `unauthenticatedClientAction = RedirectToLoginPage`, allowed audience = owner's Entra tenant, allowed users = explicit single-email allow-list | Other users in the same Entra tenant could log in but are blocked by allowed-users filter. Tenant is single-user (personal), so residual risk is near zero. |
| Compromised container image | Pinned base image SHA; built only by GitHub Actions; image scanned by GHCR; non-root container user | If the GitHub account is compromised, attacker can push a poisoned image. Mitigation: branch protection + required reviews on main. |
| Leaked secrets | No secrets in the image (this dashboard reads no secrets at runtime); ACA env config has no credentials; Log Analytics workspace key never exposed (handled by Azure) | None at this scope. If we later add features that need secrets, store as ACA secret refs. |
| Billing / DoS attack | Free tier covers expected usage; maxReplicas=2 caps blast radius; cost alert at $5/mo | A determined attacker forcing many auth flows could chew into the free tier. Mitigation: cost alert + ability to disable ingress with one `az` command. |
| Stale data | GitHub Actions runs on every push to main; ACA performs a rolling revision; eventual consistency on the order of 1-2 minutes | Acceptable for a status dashboard. |
| Network exfiltration from container | No outbound calls in the codebase; default ACA egress allows all outbound, which is acceptable for a tool that pulls no external data | If we later add MCP / LLM calls, revisit and consider Container Apps Environment with VNet egress restrictions. |
| OIDC trust misconfiguration | Federated credential restricted to a specific repo + branch (`repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/main`) | A repo admin could create a workflow on main that abuses the trust. Mitigation: required reviews on workflow file changes. |

## 4. Cost estimate

Expected monthly usage (single user, ~10-50 page loads per day, ~3 sec to rebuild):

- vCPU-seconds: ~5,000 / month (free tier: 180,000) -> **$0**
- GiB-seconds: ~5,000 / month (free tier: 360,000) -> **$0**
- Requests: ~1,500 / month (free tier: 2,000,000) -> **$0**
- Log Analytics: ~50 MB ingest / month (free tier: 5 GB) -> **$0**
- Container registry: GHCR (free for private) -> **$0**

**Estimated total: $0 / month.** Cost ceiling: $10/month. Cost alert: $5/month.

Worst case (sustained ~100k requests via auth replay attack before manual shutoff):
~$2-3 burst, well under ceiling.

## 5. The Dockerfile (ready to commit)

Path: `Dockerfile` at repo root.

```dockerfile
# syntax=docker/dockerfile:1.7
# Pinned to a digest in production. The :3.13-slim tag is shown for clarity.
FROM python:3.13-slim AS base

# Non-root user
RUN groupadd -r app && useradd -r -g app -u 10001 -m -d /home/app app

WORKDIR /repo

# We ship the WHOLE checked-out repo into the image (artifacts + ledger + cli).
# state_builder.py reads from the repo at runtime; no separate data volume.
# .dockerignore excludes the .git dir, virtualenvs, pycache, node_modules, etc.
COPY --chown=app:app . /repo

# No third-party deps -- stdlib only (LESSON-001).
USER app
EXPOSE 8080
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "spec-driven-development/cli/state_builder.py", "serve", \
     "--host", "0.0.0.0", "--port", "8080", "--no-open"]
```

Path: `.dockerignore` at repo root.

```
.git
.gitignore
.github
__pycache__
*.pyc
*.pyo
.venv
.vscode
.idea
.copilot
.DS_Store
*.swp
*.swo
node_modules
```

Note: `cli/state_builder.py serve` currently binds 127.0.0.1. We will need a
small change to accept `--host 0.0.0.0` for the container case. Tracked as the
v0.2.1 follow-up below.

## 6. GitHub Actions workflow (ready to commit, disabled by default)

Path: `.github/workflows/deploy-cloud-dashboard.yml`

```yaml
name: deploy-cloud-dashboard

# Disabled by default; flip workflow_dispatch -> push when the user is ready.
on:
  workflow_dispatch:

permissions:
  id-token: write   # OIDC federation
  contents: read
  packages: write   # push to ghcr.io

env:
  IMAGE: ghcr.io/${{ github.repository }}/state-dashboard

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.IMAGE }}:latest
          provenance: true
          sbom: true

      - name: Azure login (OIDC, no secrets stored)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Update Container App revision
        run: |
          az containerapp update \
            --name state-dashboard \
            --resource-group rg-bridge-dashboard \
            --image ${{ env.IMAGE }}:${{ github.sha }}
```

The three `secrets.AZURE_*` values are NOT credentials; they are public identifiers.
OIDC federation means no client secret is stored anywhere -- GitHub presents a
short-lived token that Entra trusts because of the federated credential bound
to this specific repo + branch.

## 7. Deployment runbook (you execute when ready)

Prerequisites:
- `az` CLI 2.60+ installed
- `az login` succeeds against your tenant
- You have Owner on the subscription (you do per the screenshot)

### Step 1. Set defaults

```bash
SUB=05e7b074-305c-48d8-9bd0-ce5305cd027c
RG=rg-bridge-dashboard
LOC=westus2
ENV=cae-bridge-dashboard
APP=state-dashboard
GHREPO=rodolfolermacontreras/Evolving-Multi-Agent-Framework

az account set --subscription $SUB
```

### Step 2. Resource group + Log Analytics + Container Apps Environment

```bash
az group create -n $RG -l $LOC

LAW=law-bridge-dashboard
az monitor log-analytics workspace create \
    -g $RG -n $LAW -l $LOC --retention-time 30

LAW_ID=$(az monitor log-analytics workspace show -g $RG -n $LAW --query customerId -o tsv)
LAW_KEY=$(az monitor log-analytics workspace get-shared-keys -g $RG -n $LAW --query primarySharedKey -o tsv)

az containerapp env create \
    -g $RG -n $ENV -l $LOC \
    --logs-workspace-id $LAW_ID \
    --logs-workspace-key $LAW_KEY
```

### Step 3. Initial container app (placeholder image, will be replaced by CI)

```bash
az containerapp create \
    -g $RG -n $APP \
    --environment $ENV \
    --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
    --target-port 8080 \
    --ingress external \
    --transport auto \
    --min-replicas 0 \
    --max-replicas 2 \
    --cpu 0.25 --memory 0.5Gi \
    --system-assigned
```

### Step 4. Enable Microsoft Entra ID auth, owner-only

```bash
TENANT_ID=$(az account show --query tenantId -o tsv)

# Create an Entra app registration for the dashboard
APP_ID=$(az ad app create --display-name "Bridge Dashboard Auth" --query appId -o tsv)

# Configure ACA Easy Auth
az containerapp auth microsoft update \
    -g $RG -n $APP \
    --client-id $APP_ID \
    --tenant-id $TENANT_ID \
    --yes

az containerapp auth update \
    -g $RG -n $APP \
    --enabled true \
    --action RedirectToLoginPage \
    --redirect-provider azureactivedirectory \
    --require-https true

# Restrict to your single account (replace with your real UPN)
OWNER_UPN=rodolfolermacontreras@gmail.com   # adjust if Entra UPN differs
echo "Configure allowed users in the Azure Portal:"
echo "Container App -> Authentication -> Identity provider -> Microsoft -> Edit"
echo "  -> Issuer URL: https://sts.windows.net/$TENANT_ID/"
echo "  -> Allowed token audiences: api://$APP_ID"
echo "Then under Container App -> Access Control (IAM), add a custom claims rule"
echo "  or use the App Registration's 'Assignment required' + Enterprise App users."
```

### Step 5. Federated credential for GitHub Actions OIDC

```bash
az ad app federated-credential create \
    --id $APP_ID \
    --parameters "{
        \"name\": \"github-main-deploy\",
        \"issuer\": \"https://token.actions.githubusercontent.com\",
        \"subject\": \"repo:$GHREPO:ref:refs/heads/main\",
        \"audiences\": [\"api://AzureADTokenExchange\"]
    }"

SP_ID=$(az ad sp create --id $APP_ID --query id -o tsv)

# Grant minimum role on the RG only
az role assignment create \
    --assignee $SP_ID \
    --role "Contributor" \
    --scope "/subscriptions/$SUB/resourceGroups/$RG"

echo "Add these as GitHub repo secrets:"
echo "  AZURE_CLIENT_ID       = $APP_ID"
echo "  AZURE_TENANT_ID       = $TENANT_ID"
echo "  AZURE_SUBSCRIPTION_ID = $SUB"
```

### Step 6. Cost alert at $5

```bash
az consumption budget create \
    --amount 5 --budget-name bridge-dashboard-cap --category cost \
    --time-grain monthly --start-date $(date -u +%Y-%m-01) \
    --end-date $(date -u -d "+1 year" +%Y-%m-01) \
    --resource-group $RG
```

### Step 7. First deploy

In the GitHub Actions tab, run "deploy-cloud-dashboard" via workflow_dispatch.
After it completes, browse to:

```bash
az containerapp show -g $RG -n $APP --query properties.configuration.ingress.fqdn -o tsv
```

You should see a Microsoft login page; sign in as the owner; see the dashboard.

### Step 8. Teardown (if you ever want to remove everything)

```bash
az group delete -n $RG --yes --no-wait
az ad app delete --id $APP_ID
```

One command removes all resources. The Entra app reg removal is separate.

## 8. What this design does NOT yet do

- No custom domain (uses `*.azurecontainerapps.io`).
- No CDN, no caching layer (single-user; not needed).
- No VNet integration / private endpoints (single user; public ingress + auth is sufficient).
- No structured logging / metrics dashboards beyond Log Analytics defaults.
- No staging slot or blue/green (single-revision rolling updates only).
- No automated security scanning beyond what GHCR provides by default.

All deferred until justified by an actual need.

## 9. Required code change (small, blocking on first deploy)

`cli/state_builder.py` currently binds `127.0.0.1` only. Container needs
`0.0.0.0`. The `serve` subcommand already accepts `--host`, so the Dockerfile
CMD passes it. No code change required -- this was a self-resolving concern.

## 10. Open questions for the human (intentional)

These are Level-2 decisions the Cloud Security Architect cannot make alone:

1. Confirm the Entra UPN to allow-list (the screenshot shows `rodolfolermacontreras@gmail.com`).
2. Confirm region preference (default: `westus2`).
3. Confirm cost ceiling (default: $10/mo, alert at $5).
4. Confirm "you will execute the runbook yourself" vs "delegate to Software Developer".

None of these block the design. They are decisions to make at /spec time.

---

## Status

Design exploration complete. Backlog item: **SDD-007 (P3)**. Next action after
human approval: run `/spec` to convert this design into an approved feature
spec, then `/plan` -> `/tasks` -> `/implement`.

Required pre-approvals before implementation:
- Approve ADR-0008 (hire principal-cloud-security-architect)
- Approve cost ceiling
- Approve OIDC federation pattern (vs storing service principal secrets)
