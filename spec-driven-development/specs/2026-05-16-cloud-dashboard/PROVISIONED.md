# Cloud Dashboard -- Provisioned State (v1.0 LIVE)

- **Status:** DEPLOYED AND LIVE
- **Date deployed:** 2026-05-16
- **Deployed by:** Executive Manager autopilot session, against authenticated `az` session

---

## Live URL

```
https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/
```

Access requires Microsoft Entra ID sign-in as `rodolfolermacontreras@gmail.com` (the only allowed user).

## Provisioned Azure resources

| Resource | Name | Notes |
|----------|------|-------|
| Subscription | Visual Studio Enterprise Subscription | id: 05e7b074-305c-48d8-9bd0-ce5305cd027c |
| Resource group | rg-bridge-dashboard | West US 2 |
| Container Apps Environment | cae-bridge-dashboard | Auto-created by `az containerapp up` |
| Container App | state-dashboard | min=0, max=2 replicas, 0.25 vCPU / 0.5 GiB |
| Container Registry (auto) | ca24921a026cacr.azurecr.io | Basic, auto-created by `az containerapp up` |
| Log Analytics workspace (auto) | workspace-... | Auto-created, default retention |
| Entra app registration | Bridge Dashboard Auth | client id: 625bdb84-d2e6-4853-96a9-f601571e3a0f |
| Enterprise app (service principal) | Bridge Dashboard Auth | object id: 8b2fc156-312a-4f58-9f60-ac9dd69a0aa1; appRoleAssignmentRequired=true |
| User assigned | Rodolfo Lerma (766b4806-d349-4c31-a281-5268ebd1b045) | Default access role |

## Security posture (as deployed)

| Control | State | Verified |
|---------|-------|----------|
| HTTPS-only (TLS 1.2+) | Enforced by ACA ingress | Yes -- ingress.transport=Auto, requireHttps=true |
| Auth required | Enforced | Yes -- `/` returns 302 -> login.microsoftonline.com |
| Auth on health check too | Enforced | Yes -- `/healthz` also 302 (no info disclosure) |
| Single-tenant audience | Yes | sign-in-audience=AzureADMyOrg, tenant c6d3fc52-... |
| Assignment required | Yes | appRoleAssignmentRequired=true on the SP |
| Only one user assigned | Yes | Only rodolfolermacontreras@gmail.com |
| Container runs as non-root | Yes | UID 10001 |
| No secrets baked in image | Yes | Image only contains the repo; state_builder reads no secrets |
| Scale-to-zero | Yes | minReplicas=0, no cost when idle |
| Max replica cap | Yes | maxReplicas=2 (blast radius cap on auth-replay attack) |

## Cost posture

Expected: **$0/month** under MSDN Visual Studio Enterprise credit (free tier covers
single-user usage: 180k vCPU-seconds + 360k GiB-seconds + 2M requests per month).

**Cost alert at $5/month** -- Azure CLI `az consumption budget` failed due to a known
preview-API parsing issue (start/end date colons in ISO format break the shorthand
syntax). Set this up manually in Azure Portal:

> Portal > Subscriptions > Visual Studio Enterprise Subscription > Cost Management >
> Budgets > Add > Scope: rg-bridge-dashboard > Amount: $5 monthly > Alerts: 50% / 80% /
> 100% to rodolfolermacontreras@gmail.com.

Effort: 30 seconds. Tracked as v1.1 follow-up (see below).

## What was NOT done (deferred to v1.1+)

1. **Cost budget alert** -- portal-only step pending (CLI API issue, see above).
2. **GitHub Actions OIDC CI/CD** -- v1 deployed manually via `az containerapp up --source .`
   which used ACR Build. To enable push-to-deploy: create federated credential, add
   GitHub repo secrets, enable the workflow file (currently in DESIGN.md §6 but not
   committed).
3. **Custom domain** -- using default `*.azurecontainerapps.io` URL.
4. **VNet integration / private endpoint** -- public ingress with Entra auth is
   sufficient for single-user.
5. **Image hardening** -- base image is `python:3.13-slim` by tag, not pinned to a
   specific digest yet.

## Operational commands

| Action | Command |
|--------|---------|
| View logs | `az containerapp logs show -g rg-bridge-dashboard -n state-dashboard --follow` |
| Redeploy after a `git push` (manual) | `cd <repo> && az containerapp up -n state-dashboard -g rg-bridge-dashboard --source .` |
| Show current revision | `az containerapp revision list -g rg-bridge-dashboard -n state-dashboard -o table` |
| Stop accepting traffic (kill switch) | `az containerapp ingress disable -g rg-bridge-dashboard -n state-dashboard` |
| Resume traffic | `az containerapp ingress enable -g rg-bridge-dashboard -n state-dashboard --type external --target-port 8080 --transport auto` |
| **Tear everything down** | `az group delete -n rg-bridge-dashboard --yes --no-wait && az ad app delete --id 625bdb84-d2e6-4853-96a9-f601571e3a0f` |

## Verification trace (recorded 2026-05-16)

```
1. az account show -- subscription 05e7b074-... user rodolfolermacontreras@gmail.com OK
2. Providers registered: Microsoft.App, Microsoft.OperationalInsights, Microsoft.ContainerRegistry OK
3. az group create rg-bridge-dashboard westus2 -- Succeeded
4. az containerapp up --source . -- ACR Build OK, image pushed, app created, deployed
5. az containerapp update --min-replicas 0 --max-replicas 2 --cpu 0.25 --memory 0.5Gi -- Succeeded
6. /healthz returned 200 "ok" (pre-auth)
7. Entra app created: client id 625bdb84-d2e6-4853-96a9-f601571e3a0f, SP 8b2fc156-...
8. az containerapp auth microsoft update + auth update enable -- Succeeded
9. Unauthenticated GET / -> 302 to login.microsoftonline.com OK
10. SP set appRoleAssignmentRequired=true OK
11. User Rodolfo Lerma assigned to app role OK
12. Final: /healthz also 302 (auth-gated, no info leak) OK
```

## Closes

- SDD-007 (cloud-dashboard) -- design exploration + v1 implementation
- F2-cloud (live cloud deployment of state dashboard)
- Original user request 2026-05-16: "we will develop this to be useful to me only,
  so I will share resources in Azure so we can run it live, but it has to be secure"
