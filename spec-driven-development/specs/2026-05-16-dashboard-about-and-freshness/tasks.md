---
id: SDD-20260516DASH-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-16-dashboard-about-and-freshness
---

# Task List: Dashboard About Section and Data Freshness

- Spec Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/plan.md`
- Validation Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/validation.md` (LOCKED 2026-05-16)
- Task ID Format: local short IDs `T-NNN` (feature directory is date-namespaced)
- Owner: Principal Software Developer
- Feature branch: `feature/2026-05-16-dashboard-about-and-freshness` off `master`
- Worktree: `../wt-dashboard-about-and-freshness`

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-001 | Create federated credential in deploy app registration (one-shot `az ad app federated-credential create`, subject pinned to `repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master`). Full command in plan.md "Pre-Implementation Dependencies" §1. Paste output into validation.md EVIDENCE V-9. | Azure app registration (no repo files) | proves AC #7; satisfies V-9 | S | NONE | HITL | No | pending |
| T-002 | Verify preconditions before any code merges to master: (a) run `az ad app federated-credential list --id <DEPLOY_APP_OBJECT_ID>` and confirm the T-001 entry is present; (b) confirm repository Actions variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` exist (these are public identifiers per ADR-009); (c) inspect the deploy SP's role assignments and confirm minimum scope per ADR-009 (ACA revision update on the single Container App `state-dashboard` in `rg-bridge-dashboard`, NOT subscription contributor); (d) confirm default GitHub Actions failure notifications are enabled for repo owner (Settings -> Notifications). Record all four in validation.md EVIDENCE V-9 and V-14. | None (Azure + GitHub admin surfaces) | proves AC #3, AC #7; satisfies V-9, V-14 | S | T-001 | HITL | No | pending |
| T-003 | Author `.github/workflows/deploy-dashboard.yml` materializing REC-3 from `spec-driven-development/specs/2026-05-16-cloud-dashboard/DESIGN.md` §6. Required: `name: deploy-dashboard`; `on: { workflow_dispatch: {}, push: { branches: [master], paths: [spec-driven-development/exec/state.md, spec-driven-development/cli/state_builder.py, .github/workflows/deploy-dashboard.yml, Dockerfile] } }`; `permissions: { id-token: write, contents: read, packages: write }`; checkout -> buildx -> registry login -> docker build/push -> `azure/login@v2` with `client-id`/`tenant-id`/`subscription-id` (NO `client-secret`) -> `az containerapp update --name state-dashboard --resource-group rg-bridge-dashboard --image <tag>`. Before authoring: run `az containerapp show --name state-dashboard --resource-group rg-bridge-dashboard --query properties.template.containers[0].image -o tsv` to confirm the currently-configured image registry (GHCR vs ACR); use whichever the ACA app is already pulling from; if ACR, swap GHCR steps for ACR build/push and STOP to escalate to Architect before granting any new role assignment beyond the ADR-009 minimum scope. Write TDD-first: V-6, V-7, V-8 in `spec-driven-development/cli/test_deploy_workflow.py` (stdlib-only YAML handling per validation.md V-6) BEFORE the workflow file. All three V-tests MUST PASS before commit. Also run `python -m unittest discover spec-driven-development/cli` and confirm V-13 (no regression). Commit with conventional message. | `.github/workflows/deploy-dashboard.yml` (new), `spec-driven-development/cli/test_deploy_workflow.py` (new) | proves AC #2; satisfies V-6, V-7, V-8, V-13 (regression) | M | T-002 | AFK | Yes | pending |
| T-004 | Add the About / Where we are block to the dashboard HTML rendered by `spec-driven-development/cli/state_builder.py`. Insert a `<section id="about">` (or equivalent stable selector) immediately BEFORE the `<main class="layout-4zone">` element in `render_html(...)` (current location around line 1214-1215 of `state_builder.py`). Block content: (1) a static `<p>` whose text is a project-identity sentence plus the meta caveat that the dashboard is built by the framework whose progress it tracks (exact wording is developer's choice; whatever text is shipped is pinned by V-1); (2) a single dynamic `<p class="about-where-we-are">` line containing the current `Current PI`, `Active sprint`, and `Active focus` values. Source those three values from data already available in `render_html(...)`'s scope (e.g., `pi.name`, `pi.title`, and existing parsed fields) -- do NOT re-parse `exec/state.md` from disk inside the renderer; if a needed value is not currently in scope, plumb it through `build(...)` -> `render_html(...)` as a keyword argument. Provide a module-level constant for the static paragraph string and a module-level constant for the fallback string used when any of the three dynamic values is missing or empty (the fallback path is exercised by V-4). All HTML user-content interpolation MUST go through the existing `h(...)` escape helper. Write TDD-first: V-1, V-2, V-3, V-4, V-5 in `spec-driven-development/cli/test_state_builder.py` BEFORE the template change. All five MUST PASS before commit; full `python -m unittest discover spec-driven-development/cli` must remain green (V-13). NO new pip dependencies. Stdlib only. | `spec-driven-development/cli/state_builder.py`, `spec-driven-development/cli/test_state_builder.py` | proves AC #4, AC #5; satisfies V-1, V-2, V-3, V-4, V-5, V-13 | M | T-002 | AFK | Yes | pending |
| T-005 | Live latency probe -- runs ONLY after T-003 and T-004 are merged to master AND the first auto-deploy has been observed in the Actions tab. Procedure verbatim from validation.md V-11: (1) confirm V-9 and V-10 PASS; (2) note the current `Generated date` shown at the live URL; (3) regenerate `spec-driven-development/exec/state.md` via the documented state-build command, commit, push to master, record `T0` (UTC, second precision); (4) poll the live URL every 15 seconds with `curl -fsSL <URL> | Select-String -SimpleMatch '<new Generated date>'`; (5) record `T1` on first match; (6) compute `elapsed = T1 - T0`; (7) paste `T0`, `T1`, `elapsed`, PASS/FAIL into validation.md EVIDENCE V-11. Then perform V-12 cold-start probe: wait >=10 minutes, issue `curl -w "%{time_total}\n" -o /dev/null -s <URL>`, paste `time_total` and PASS/FAIL into EVIDENCE V-12. Also confirm V-10 by running `gh workflow list` and pasting into EVIDENCE V-10. If V-11 FAILS, do NOT modify the validation contract; root-cause, fix, re-probe with a second `state.md` regen, and record both attempts. | `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/validation.md` (EVIDENCE section only) | proves AC #1, AC #6, AC #8; satisfies V-10, V-11, V-12 | S | T-003, T-004 (both merged to master) | HITL | No | pending |

## Notes

- Fleet dispatch eligibility: T-003 and T-004 touch disjoint files and may run in parallel from sibling worktrees per `.github/instructions/fleet-workers.instructions.md`. Serial execution in a single worktree is the recommended default for this small task count.
- T-001 and T-002 are gating: NO code task (T-003, T-004) may merge to master until T-002 EVIDENCE is recorded as PASS.
- T-005 is terminal and is the only mechanism by which AC #1 (the headline SLO) can be validated.
- All AFK tasks are TDD-mandated per Constitution Article X: tests in validation.md V-N MUST be authored and committed in the SAME commit as (or in a commit preceding) the corresponding implementation.
- No emojis in any code, commit message, or doc per repo conventions.
- Branch is owner-gated; the workflow file itself becomes part of the security perimeter per ADR-009. Any review of T-003 by code-review specialist MUST treat permissions, triggers, and target resource changes as privilege-equivalent changes.
