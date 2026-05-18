# Session Checkpoint — Dashboard About + Freshness Feature

**Date:** 2026-05-16 (paused 2026-05-18)
**Owner:** Rodolfo Lerma
**Feature in flight:** SDD-009 + SDD-010 bundled as `2026-05-16-dashboard-about-and-freshness`
**Lifecycle position:** TASKS done; blocked on HITL Azure provisioning before IMPLEMENT can dispatch

---

## How to resume

1. Read `.github/copilot-instructions.md`
2. Read this file
3. Greet the human with: "Welcome back. Last we left off, the dashboard about+freshness feature is waiting on your HITL Azure provisioning (9 numbered steps). Have you run them yet, or do you need me to re-surface the commands?"
4. If human says "done" → dispatch T-003 (workflow YAML) + T-004 (About-section template) to developer-general fleet in parallel worktrees.
5. If human says "not yet" → re-present the 9 steps (they are below in this file).

---

## State at pause

### Process gates (all cleared)
- Spec approved by human (Architect-authored)
- Plan + locked validation.md approved by human (SW Dev-authored)
- AC sign-off APPROVED by PM (all 8 ACs map cleanly to V-N entries)

### What's blocking
The human needs to provision an Azure deploy app registration + federated credential + role + GitHub Actions variables. This is the T-001 + T-002 HITL phase. Without it, no auto-deploy can run.

### Artifacts on disk (uncommitted, working tree)
- `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/clarification.md` (3.4 KB)
- `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/spec.md` (11.5 KB)
- `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/plan.md` (10.8 KB)
- `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/tasks.md` (8.2 KB)
- `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/validation.md` (10.7 KB, **LOCKED 2026-05-16**)
- `spec-driven-development/docs/ADR/009-ci-oidc-deploys-to-production.md` (binding ADR)
- `spec-driven-development/backlog/BACKLOG.md` (SDD-009, SDD-010 added under P2)
- `spec-driven-development/backlog/IDEAS.md` (both 2026-05-16 entries marked routed)

### Repo state at pause
- HEAD: `33b355f` retro: PI-2 retrospective
- origin/master is **29 commits behind local** (local is ahead, not yet pushed)
- Uncommitted: BACKLOG.md, IDEAS.md, state.html (cosmetic regen), plus the new feature dir and ADR

---

## Feature summary (one paragraph)

Add a newcomer-facing "About / Where we are" section to the live Bridge dashboard (static purpose paragraph + dynamic PI/sprint line from `exec/state.md`) and close the data-freshness gap so that `git push` to master is visible on the live URL within 5 minutes via GitHub Actions OIDC auto-redeploy. Two backlog items (SDD-009 freshness + SDD-010 about), one feature dir, one shared spec, no menus.

---

## Human's binding decisions (from clarification.md)

- **Q1 — Freshness mechanism:** (b) GH Actions OIDC auto-redeploy on push to master
- **Q2 — About-section content:** (c) hybrid (static purpose + dynamic PI/sprint line)
- **Q3 — Acceptance latency:** N = 5 minutes from push to visible on live URL

---

## Task list (from tasks.md)

| ID | Description | Owner | Status |
|----|-------------|-------|--------|
| T-001 | Provision deploy app reg + federated credential (HITL one-shot) | Human | **PENDING** |
| T-002 | Verify preconditions (federated cred, Actions vars, SP role, GH notifications) | Human | **PENDING** |
| T-003 | Author `.github/workflows/deploy-dashboard.yml` TDD-first | developer-general | Blocked on T-002 |
| T-004 | About-section template block + unit tests in `state_builder.py` | developer-general | Blocked on T-002 (can parallel with T-003) |
| T-005 | Live latency probe after first auto-deploy on master (HITL) | Human | Blocked on T-003/T-004 merge |

---

## The 9 HITL steps the human needs to run (when ready)

```powershell
# Step 1 — Log in
az login
az account set --subscription <YOUR_SUBSCRIPTION_NAME_OR_ID>

# Step 2 — Create deploy app registration
az ad app create --display-name "Bridge Dashboard Deploy" --sign-in-audience AzureADMyOrg
#  Copy from output:  appId  → DEPLOY_CLIENT_ID
#                     id     → DEPLOY_OBJECT_ID

# Step 3 — Create the SP for it
az ad sp create --id <DEPLOY_CLIENT_ID>

# Step 4 — Assign minimum-scope role on the Container App only
$SUB = az account show --query id -o tsv
$SCOPE = "/subscriptions/$SUB/resourceGroups/rg-bridge-dashboard/providers/Microsoft.App/containerApps/state-dashboard"
az role assignment create --assignee <DEPLOY_CLIENT_ID> --role "Contributor" --scope $SCOPE

# Step 5 — Federated credential bound to master
az ad app federated-credential create --id <DEPLOY_OBJECT_ID> --parameters '{
  \"name\": \"gha-master\",
  \"issuer\": \"https://token.actions.githubusercontent.com\",
  \"subject\": \"repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master\",
  \"audiences\": [\"api://AzureADTokenExchange\"]
}'

# Step 6 — Get the tenant id
az account show --query tenantId -o tsv
#  Call this TENANT_ID

# Step 7 — Set the three GitHub repo Actions variables
gh variable set AZURE_CLIENT_ID --body "<DEPLOY_CLIENT_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
gh variable set AZURE_TENANT_ID --body "<TENANT_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
gh variable set AZURE_SUBSCRIPTION_ID --body "<YOUR_SUBSCRIPTION_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework

# Step 8 — Verify
az ad app federated-credential list --id <DEPLOY_OBJECT_ID>
gh variable list --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
az role assignment list --assignee <DEPLOY_CLIENT_ID> --all -o table

# Step 9 — Tell the EM "done" and dispatch begins.
```

---

## Risks parked

- **Image registry mismatch (GHCR vs ACR).** REC-3 draft assumes GHCR; the live `state-dashboard` ACA may pull from ACR. T-003 brief instructs a pre-flight `az containerapp show ... --query properties.template.containers[0].image` check; if ACR, swap GHCR steps for ACR build/push and escalate role-scope changes to the Architect.
- **First push is the only true latency test** for AC #1; documented re-probe procedure in validation.md V-11.

---

## What is NOT in this scope

- Bespoke workflow-failure alerting (deferred — default GH notifications satisfy AC #3)
- Build-cache optimization beyond ACA defaults
- Multi-user landing or role-based content
- Anything cloud-infra-only from cloud-dashboard SECURITY-REVIEW (REC-4, REC-5)

---

## EM standing recommendation when human returns

> "Run the 9 HITL steps above (~5 min total once `az login` is done), tell me 'done', and I'll dispatch T-003 + T-004 in parallel to the developer fleet. Evidence capture into validation.md V-9/V-14 can be offloaded to the worker too."
