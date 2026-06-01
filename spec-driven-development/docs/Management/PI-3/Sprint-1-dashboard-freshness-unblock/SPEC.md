---
sprint: PI-3 / S1
title: Dashboard About + Freshness Unblock
status: BLOCKED on HITL Azure provisioning
owner: principal-software-developer
worktree: wt-pi3-s1-freshness-workflow (T-003), wt-pi3-s1-freshness-about (T-004)
deps: none (hard); all upstream lifecycle artifacts already approved
created: 2026-05-16 (spec/plan/tasks/validation); revived 2026-05-25 for PI-3
canonical_spec_dir: spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/
backlog_ids: SDD-009, SDD-010
adr: ADR-0009 (CI/CD OIDC deploys to production)
---

# Sprint 1 -- Dashboard About + Freshness Unblock

## Required Reading (before starting any task)

1. [`ONBOARDING_KICK_OFF.md`](../ONBOARDING_KICK_OFF.md) -- project framing
2. [`RULES.md`](../RULES.md) -- 12 binding rules + HITL gates
3. [`HIGH_LEVEL_DEV_TRACKER.md`](../HIGH_LEVEL_DEV_TRACKER.md) -- PI-3 board
4. This file
5. The canonical lifecycle artifacts (already exist, do not re-author):
   - [`specs/2026-05-16-dashboard-about-and-freshness/clarification.md`](../../specs/2026-05-16-dashboard-about-and-freshness/clarification.md)
   - [`specs/2026-05-16-dashboard-about-and-freshness/spec.md`](../../specs/2026-05-16-dashboard-about-and-freshness/spec.md)
   - [`specs/2026-05-16-dashboard-about-and-freshness/plan.md`](../../specs/2026-05-16-dashboard-about-and-freshness/plan.md)
   - [`specs/2026-05-16-dashboard-about-and-freshness/tasks.md`](../../specs/2026-05-16-dashboard-about-and-freshness/tasks.md)
   - [`specs/2026-05-16-dashboard-about-and-freshness/validation.md`](../../specs/2026-05-16-dashboard-about-and-freshness/validation.md) (LOCKED 2026-05-16)
   - [`docs/ADR/009-ci-oidc-deploys-to-production.md`](../ADR/009-ci-oidc-deploys-to-production.md)
6. For workers, additionally read the [Codebase Reading Guide rows for your role](../ONBOARDING_KICK_OFF.md#14-codebase-reading-guide-for-brownfield-agents).

This sprint **does not re-author** any of the artifacts above. They are
locked and PM-approved. This sprint EXECUTES the tasks.md against them.

---

## 1. Human's stated requirements (verbatim)

From clarification.md (PM-approved 2026-05-16):

- **Freshness mechanism (Q1):** "(b) GH Actions OIDC auto-redeploy on push to master"
- **About-section content (Q2):** "(c) hybrid (static purpose + dynamic PI/sprint line)"
- **Acceptance latency (Q3):** "N = 5 minutes from push to visible on live URL"

## 2. Sprint Goal (one sentence)

Close the gap between local commits and the live Bridge dashboard so that any
push to `master` is visible to a newcomer (with a clear "About / Where we are"
section) within 5 minutes, via GitHub Actions OIDC auto-redeploy.

## 3. Acceptance Criteria (from validation.md, summarized)

| # | AC | Verification |
|---|----|--------------|
| AC1 | Push to `master` triggers GH Actions workflow that redeploys ACA app | V-1, V-2: workflow run visible in Actions tab within 30s of push |
| AC2 | Live dashboard reflects the new commit within 5 min of push | V-9 latency probe |
| AC3 | Workflow failure produces visible signal (default GH notifications OK; bespoke alerting deferred) | V-3 |
| AC4 | New "About / Where we are" section is rendered at the top of the dashboard | V-4 visual check |
| AC5 | About section contains BOTH static purpose paragraph AND dynamic PI/sprint line from `exec/state.md` | V-5, V-6 |
| AC6 | About section is accessible (semantic HTML, AA contrast) | V-7 |
| AC7 | No regression: existing 21 state_builder tests still pass | V-8 |
| AC8 | Two new unit tests for About template added; pass on Windows + Linux | V-10 |

Full validation contract: see locked [`validation.md`](../../specs/2026-05-16-dashboard-about-and-freshness/validation.md).

## 4. Task Decomposition (from tasks.md)

| ID | Description | Owner | Tag | Status | Worktree |
|----|-------------|-------|-----|--------|----------|
| T-001 | Provision deploy app reg + federated credential (Azure) | Human | [HITL] | **DONE** | n/a |
| T-002 | Verify preconditions (cred, vars, role, GH notifications) | Human | [HITL] | **DONE** | n/a |
| T-003 | Author `.github/workflows/deploy-dashboard.yml` TDD-first | developer-general | [P][AFK] | **DONE** | `wt-pi3-s1-freshness-workflow` |
| T-004 | About-section template block + unit tests in `state_builder.py` | developer-general | [P][AFK] | **DONE** | `wt-pi3-s1-freshness-about` |
| T-005 | Live latency probe after first auto-deploy on master | Human | [HITL] | Blocked on T-003/T-004 merge | n/a |

Tags: `[P]` parallelizable, `[S]` sequential, `[AFK]` autonomous-safe, `[HITL]` human-in-the-loop.

## 5. Worktree Plan

Two parallel worktrees (T-003 and T-004 are parallel-safe per tasks.md):

```powershell
git worktree add ../wt-pi3-s1-freshness-workflow -b pi3/s1/freshness-workflow master
git worktree add ../wt-pi3-s1-freshness-about    -b pi3/s1/freshness-about    master
```

- **T-003 worktree** modifies: `.github/workflows/deploy-dashboard.yml` (NEW), `Dockerfile` (read only), `specs/2026-05-16-dashboard-about-and-freshness/validation.md` (V-1..V-3 evidence).
- **T-004 worktree** modifies: `spec-driven-development/cli/state_builder.py` (template block + 2 new tests), `spec-driven-development/cli/test_state_builder.py` (2 new tests).
- **File-overlap check:** zero overlap. Safe to merge in any order.

Tear down both worktrees after merge:

```powershell
git worktree remove ../wt-pi3-s1-freshness-workflow
git worktree remove ../wt-pi3-s1-freshness-about
git branch -d pi3/s1/freshness-workflow pi3/s1/freshness-about
```

## 6. Dispatch Tracker

| Dispatch ID | Task | Worker | Sent | Marked | Outcome |
|-------------|------|--------|------|--------|---------|
| (pending) | T-003 | developer-general | -- | -- | -- |
| (pending) | T-004 | developer-general | -- | -- | -- |

Dispatch via: `python cli/fleet.py dispatch --pi PI-3 --task T-003 --agent developer-general --brief Temp/SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md`

## 7. Validation / Test Results

Empty until T-003/T-004 land. Evidence will be captured into
`validation.md` V-1 through V-10 by the QA Engineer reviewer.

| AC | V-ref | Pass/Fail | Evidence path |
|----|-------|-----------|---------------|
| AC1 | V-1, V-2 | -- | -- |
| AC2 | V-9 | -- | -- |
| AC3 | V-3 | -- | -- |
| AC4 | V-4 | -- | -- |
| AC5 | V-5, V-6 | -- | -- |
| AC6 | V-7 | -- | -- |
| AC7 | V-8 | -- | -- |
| AC8 | V-10 | -- | -- |

## 8. HITL Blocker -- the 9 Azure Provisioning Steps

These are T-001 + T-002. The human runs them ONCE. Total time ~5 min after
`az login`.

```powershell
# Step 1 -- Log in
az login
az account set --subscription <YOUR_SUBSCRIPTION_NAME_OR_ID>

# Step 2 -- Create deploy app registration
az ad app create --display-name "Bridge Dashboard Deploy" --sign-in-audience AzureADMyOrg
#  Copy from output:  appId  -> DEPLOY_CLIENT_ID
#                     id     -> DEPLOY_OBJECT_ID

# Step 3 -- Create the SP for it
az ad sp create --id <DEPLOY_CLIENT_ID>

# Step 4 -- Assign minimum-scope role on the Container App only
$SUB = az account show --query id -o tsv
$SCOPE = "/subscriptions/$SUB/resourceGroups/rg-bridge-dashboard/providers/Microsoft.App/containerApps/state-dashboard"
az role assignment create --assignee <DEPLOY_CLIENT_ID> --role "Contributor" --scope $SCOPE

# Step 5 -- Federated credential bound to master
az ad app federated-credential create --id <DEPLOY_OBJECT_ID> --parameters '{
  \"name\": \"gha-master\",
  \"issuer\": \"https://token.actions.githubusercontent.com\",
  \"subject\": \"repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master\",
  \"audiences\": [\"api://AzureADTokenExchange\"]
}'

# Step 6 -- Get the tenant id
az account show --query tenantId -o tsv
#  Call this TENANT_ID

# Step 7 -- Set the three GitHub repo Actions variables
gh variable set AZURE_CLIENT_ID --body "<DEPLOY_CLIENT_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
gh variable set AZURE_TENANT_ID --body "<TENANT_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
gh variable set AZURE_SUBSCRIPTION_ID --body "<YOUR_SUBSCRIPTION_ID>" --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework

# Step 8 -- Verify
az ad app federated-credential list --id <DEPLOY_OBJECT_ID>
gh variable list --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework
az role assignment list --assignee <DEPLOY_CLIENT_ID> --all -o table

# Step 9 -- Tell the EM "done" and dispatch begins.
```

**Note for human:** The deploy currently uses ACR (auto-created when running
`az containerapp up --source .` per PROVISIONED.md). REC-3 of the draft assumes
GHCR. T-003 worker is briefed to do a pre-flight `az containerapp show
--query properties.template.containers[0].image` check; if ACR, swap GHCR
steps for ACR build/push and escalate role-scope change to the Architect.

## 9. Risks parked

- **Image registry mismatch (GHCR vs ACR).** T-003 brief instructs a pre-flight
  check. If ACR, escalate role-scope change to Architect.
- **First push is the only true latency test** for AC #1. Re-probe procedure
  documented in validation.md V-11.

## 10. Scope guards (what is NOT in this sprint)

- Bespoke workflow-failure alerting beyond default GH notifications
- Build-cache optimization beyond ACA defaults
- Multi-user landing or role-based dashboard content
- Anything from `specs/2026-05-16-cloud-dashboard/DESIGN.md` SECURITY-REVIEW REC-4 or REC-5
- Image digest pinning (parked to v1.1 per SESSION-MEMORY.md)

## 11. Definition of DONE for this sprint

Per [`RULES.md`](../RULES.md) Section 4, AND:

- [ ] Both worktrees merged to `master` (human-approved per HITL #4)
- [ ] First push to `master` triggers a green workflow run within 30s
- [ ] Latency probe (T-005) confirms <5 min push-to-live
- [ ] All 21 existing state_builder tests + 2 new About tests pass
- [ ] validation.md V-1..V-10 evidence cells populated
- [ ] `BACKLOG.md` updated: SDD-009 + SDD-010 marked DONE
- [ ] `HIGH_LEVEL_DEV_TRACKER.md` updated: S1 -> DONE
- [ ] This file moved to `sprints/PI-3/SPRINT_1_DASHBOARD_FRESHNESS_UNBLOCK.md`
- [ ] `RETRO.md` appended to the canonical spec dir
- [ ] Two worktrees torn down

## 12. Status Log

| Date | Event |
|------|-------|
| 2026-05-16 | Spec, plan, tasks, validation, clarification, ADR-009 all approved |
| 2026-05-18 | Checkpoint paused -- waiting on HITL Azure provisioning |
| 2026-05-25 | PI-3 kickoff -- revived as Sprint 1; this detail doc authored |
| 2026-06-01 | T-001/T-002 COMPLETE. Azure provisioning done: app reg, SP, federated cred, role, GH variables. Blocker cleared. |
| 2026-06-01 | T-003/T-004 COMPLETE. Both implemented, tested, merged to master. 68 tests passing. Worktrees torn down. AcrPush role granted on ACR. |
| _next_ | T-005: Human runs live latency probe after first push to origin triggers workflow |
