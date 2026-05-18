# Implementation Plan: Dashboard About Section and Data Freshness

- Spec Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/spec.md`
- Author: Principal Software Developer
- Status: Draft -- pending human approval of plan + locked validation
- Last Updated: 2026-05-16
- Binding ADR: `spec-driven-development/docs/ADR/009-ci-oidc-deploys-to-production.md`

---

## Approach Summary

Two surfaces, one feature branch. The OIDC auto-deploy workflow (SDD-009) is
the load-bearing change: until it lands and the federated credential exists in
Entra, the 5-minute freshness SLO cannot be verified. The About block
(SDD-010) is a localized template change in `state_builder.py` with no runtime
dependency on the workflow, but its dynamic line is only meaningful once the
workflow is live, so we land the template first (cheap, reviewable, tested)
and use it as the payload that proves the latency SLO end-to-end.

Sequence is therefore: human one-shot to provision the federated credential
-> workflow file + about-block template land together on the feature branch
-> merge to master -> first push triggers auto-deploy -> live latency probe
records the elapsed seconds in `validation.md`.

## Surfaces Touched

| Surface | Change | Owner |
|---------|--------|-------|
| `.github/workflows/deploy-dashboard.yml` (new) | Materialize REC-3 draft from `specs/2026-05-16-cloud-dashboard/DESIGN.md` §6: `workflow_dispatch` + `push: master` triggers (paths filter on image-relevant files), `permissions: id-token: write`, Azure login via OIDC, build + push image, `az containerapp update` revision | developer-general |
| `spec-driven-development/cli/state_builder.py` | Add About-block template fragment between top bar and `layout-4zone` main; static purpose paragraph + dynamic `Current PI / Active sprint / Active focus` line sourced from values already parsed in `build(...)` | developer-general |
| `spec-driven-development/cli/test_state_builder.py` | Unit tests for the About block (presence, dynamic values, fallback) | qa-engineer-general |
| `Dockerfile` | No change expected -- confirmed: the dashboard image build does not require Dockerfile edits for either SDD-009 or SDD-010 | -- |
| Azure app registration (deploy SP) | One-shot CLI: create federated credential bound to `repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master` | human (pre-dispatch) |
| `spec-driven-development/specs/2026-05-16-cloud-dashboard/PROVISIONED.md` | Out of scope for this feature's PR (recorded as follow-up per spec) | -- |

Note: the spec text references `cli/state_builder.py`; the actual repository
path is `spec-driven-development/cli/state_builder.py`. Tasks use the actual
path; no code move.

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Pre-implementation provisioning | Human Azure CLI access; deploy app registration object-id | Federated credential present in Entra (verified via `az ad app federated-credential list`); `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID` confirmed as repo Actions variables (not secrets) |
| 2 | Land code changes on feature branch | Phase 1 complete | `.github/workflows/deploy-dashboard.yml` committed; About block + tests in `state_builder.py` committed; full `python -m unittest` suite green |
| 3 | Merge + live verification | Phase 2 merged to master | First auto-deploy executes; latency probe records elapsed seconds in `validation.md`; AC #1 marked PASS or FAIL |

## Branch Strategy

- Single feature branch off master: `feature/2026-05-16-dashboard-about-and-freshness`
- Worktree per `.github/instructions/fleet-workers.instructions.md`:
  `../wt-dashboard-about-and-freshness`
- T-003 (workflow file) and T-004 (About block + tests) touch disjoint files
  and MAY be dispatched in parallel from sibling worktrees if desired, but
  serial execution in a single worktree is the recommended default given the
  small task count and the merge-back simplicity.
- T-005 (live latency probe) is HITL and runs only after merge to master.

## Pre-Implementation Dependencies

1. Federated credential MUST exist in the deploy app registration before T-003
   merges to master, otherwise the first auto-deploy fails the OIDC handshake
   and AC #1 cannot be measured. Human one-shot, ~2 minutes:

   ```
   az ad app federated-credential create \
     --id <DEPLOY_APP_OBJECT_ID> \
     --parameters '{
       "name": "gha-master",
       "issuer": "https://token.actions.githubusercontent.com",
       "subject": "repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master",
       "audiences": ["api://AzureADTokenExchange"]
     }'
   ```

   Verification: `az ad app federated-credential list --id <DEPLOY_APP_OBJECT_ID>`
   returns one entry whose `subject` matches the above (proves AC #7).

2. Repository Actions variables (not secrets) `AZURE_CLIENT_ID`,
   `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` populated (per ADR-009: these
   are public identifiers). If already populated from SDD-007 provisioning,
   confirm-only.

3. Deploy SP role assignment MUST be minimum-scope per ADR-009 (ACA revision
   update on the single Container App `state-dashboard` in resource group
   `rg-bridge-dashboard`). If broader, narrow before T-003 merges.

## Rollback Strategy

If the first auto-deploy ships a broken revision:

```
az containerapp revision list \
  --name state-dashboard --resource-group rg-bridge-dashboard \
  -o table

az containerapp revision activate \
  --name state-dashboard --resource-group rg-bridge-dashboard \
  --revision <last-known-good-revision-name>
```

Recovery time: under 60 seconds for revision activation; ACA min-replicas
posture from SDD-007 preserved (no cold start needed for an already-warm
prior revision). If the workflow itself is broken (not the image), revert
the workflow commit on master; auto-deploy disables itself on next push.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Federated credential missing at first auto-deploy -> first push fails OIDC handshake, AC #1 unprovable | Medium | High | Phase 1 gates Phase 2; T-001 verifies before T-003 dispatch; locked validation requires AC #7 proof before AC #1 attempt |
| Image registry mismatch: REC-3 draft uses GHCR but ACA may be configured for ACR pull | Medium | High | T-003 brief instructs developer to confirm the registry currently configured on the `state-dashboard` Container App (`az containerapp show ... --query properties.template.containers[0].image`) before authoring the workflow; if ACR, swap GHCR steps for ACR build/push and add ACR pull role to the deploy SP (escalate to Architect if role change crosses ADR-009 minimum-scope boundary) |
| CI failure leaves dashboard stale longer than 5 min | Medium | Medium | AC #3 satisfied by default GitHub notifications to repo owner; no bespoke alerting in scope (deferred with rationale: violates stdlib-only/no-new-deps; spec Out of Scope §) |
| `state.md` header drift renames `Current PI` / `Active sprint` / `Active focus` and silently breaks dynamic About line | Low | Medium | T-004 unit tests assert non-empty dynamic line for canonical fixture; About block uses the same values already returned by `build()` rather than re-parsing `state.md`, so any future rename surfaces as a test failure in `test_state_builder.py` rather than a silent regression on the live dashboard |
| Path-filter on `push:` trigger too narrow -> changes to `exec/state.md` alone don't trigger redeploy and AC #1 fails | Medium | High | T-003 brief mandates the `paths:` list include `spec-driven-development/exec/state.md`, `spec-driven-development/cli/state_builder.py`, `.github/workflows/deploy-dashboard.yml`, and `Dockerfile`; validation.md has a dedicated unit check on the workflow YAML |
| OIDC trust misconfiguration broadens blast radius | Low | High | Per ADR-009: federated credential scoped to single repo + single ref (`refs/heads/master`); role assignment minimum-scope; T-001 verification step inspects both |
| Live latency probe consumes the verification budget (only first push truly tests AC #1) | High | Low | Probe procedure documented in validation.md; if first probe fails, root-cause + fix + re-probe with a second no-op `state.md` regen |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | S | One Azure CLI command + one verification command, ~2 minutes human time |
| 2 | M | Workflow YAML authoring (~30 lines), About block template insertion (~20 lines), ~6 unit tests; full `python -m unittest` suite remains green |
| 3 | S | Single push + poll loop; mostly wait time bounded by the 5-minute SLO |

## Parallel-Safe Tasks

- T-003 (`.github/workflows/deploy-dashboard.yml` new file) -- Files: `.github/workflows/deploy-dashboard.yml`
- T-004 (`state_builder.py` About block + tests) -- Files: `spec-driven-development/cli/state_builder.py`, `spec-driven-development/cli/test_state_builder.py`

T-003 and T-004 share no files and can be dispatched concurrently to sibling
worktrees per `.github/instructions/fleet-workers.instructions.md`. Default
recommendation is serial in one worktree; parallel is permitted but not
required.

## Sequential Tasks

1. T-001 (human one-shot: federated credential provisioning) -- gates everything below.
2. T-002 (verify Phase 1 preconditions: `az ad app federated-credential list`, Actions variables present, deploy SP role-scope review) -- gates merge to master.
3. T-003 and T-004 (may run in parallel) -- both must be green before merge.
4. T-005 (live latency probe after merge) -- terminal; records the AC #1 result.

## Validation Criteria

> Cross-reference rule: AC identifiers below are from `spec.md`. Detailed test
> procedures are in `validation.md`.

- [ ] AC #1 (5-minute freshness SLO) -- validated by T-005 live probe
- [ ] AC #2 (OIDC-only auth, no client secret) -- validated by T-003 unit check
- [ ] AC #3 (workflow failure notification) -- validated by T-002 check (default GH notifications enabled for repo owner)
- [ ] AC #4 (About section present with static + dynamic content) -- validated by T-004 unit tests
- [ ] AC #5 (dynamic line tracks `state.md` header changes) -- validated by T-004 unit tests (fixture-driven)
- [ ] AC #6 (`gh workflow list` shows the workflow enabled) -- validated by T-005 pre-probe check
- [ ] AC #7 (federated credential present with the canonical subject) -- validated by T-002
- [ ] AC #8 (no cold-start regression vs. SDD-007 baseline) -- validated by T-005 post-deploy cold-start probe
