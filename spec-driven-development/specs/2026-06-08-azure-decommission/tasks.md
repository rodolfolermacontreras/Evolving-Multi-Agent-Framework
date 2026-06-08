---
id: SDD-20260608AZUREDECOM-tasks
type: tasks
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# Task List: SDD-035 -- Azure Dashboard Decommission

- Spec Reference: `spec.md` (SDD-035)
- Plan Reference: `plan.md`
- Sprint: OUT-OF-BAND (2026-06-08..2026-06-13); NOT folded into Sprint 8
- Author: Principal Cloud Security Architect (EM dispatch, Phase A.3)
- Date: 2026-06-08
- Test baseline: 305 (Sprint 7 close)

---

> **Task ID convention:** Local short IDs `T-035-NN` used within
> this date-prefixed feature directory.
>
> **Owner direction 2026-06-08:** No REQUIRED item may be deferred
> at SDD-035 close. R10 (ADR-015 owner approval) is the Level-2
> reversal-of-2026-05-16 gate; nothing destructive proceeds until
> R10 is checked.
>
> **Out-of-band:** SDD-035 is scheduled this week and is NOT bound
> to Sprint 8. The close commit message MUST flag the Level-2
> reversal explicitly.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-035-01 | Azure resource inventory + repo grep manifest. Run `az group export`, `az ad app show`, `az ad sp show`, `az ad app federated-credential list` against the four Azure surfaces; concatenate into `azure-resource-inventory.json`. Run `git grep` for live URL + Azure resource names; render results as `repo-references.md` table. | `specs/2026-06-08-azure-decommission/azure-resource-inventory.json` (new); `specs/2026-06-08-azure-decommission/repo-references.md` (new) | proves AC-1; closes R1; inventory contains all 4 Azure surfaces; grep manifest enumerates every in-repo Azure reference | S | none | AFK (Cloud Security Architect with `az` session) | Yes | done |
| T-035-02 | Draft ADR-015 from `docs/ADR/TEMPLATE.md`. Sections required: context (cost burn + governance ambiguity + portability blocker), decision (reverse 2026-05-16 SDD-007 cloud-deploy commitment), alternatives (keep-as-is; keep-as-staging; migrate-to-different-cloud), consequences (URL stops resolving; resurrection cost ~2h via inventory replay), cost-savings analysis (per spec.md Cost-Savings Note + any rigorous extension). **Present ADR-015 to owner via EM; await written approval recorded inline in the ADR.** This is the Level-2 gate (G1). | `spec-driven-development/docs/ADR/015-azure-dashboard-decommission.md` (new) | proves AC-2; closes R10; ADR drafted, owner-approved in writing inline; gate G1 unlocked for T-035-03..T-035-09 | M | T-035-01 (depends on inventory for cost-savings + consequences sections) | HITL (owner approval required) | No (HITL gate) | done |
| T-035-03 | GitHub Actions workflow scan + repair plan. Enumerate every `.github/workflows/*.yml` that consumes the OIDC trust or references the Azure deployment (search keywords: `azure/login`, `azure-credentials`, `containerapp`, `client-id: ${{ secrets.AZURE_CLIENT_ID`, plus the live Azure URL). Produce repair plan: for each workflow, decide repair (remove Azure step) or remove (entire workflow obsolete). | `specs/2026-06-08-azure-decommission/workflow-scan-report.md` (new) | proves AC-3 part 1; partial-closes R4; every Azure-dependent workflow enumerated with repair decision | S | T-035-02 (gate G1 must be unlocked) | AFK (SW Developer) | Yes (different file from T-035-06) | pending |
| T-035-04 | Execute workflow repairs per T-035-03 plan. For each workflow flagged: (a) edit to remove Azure dependency, OR (b) delete the workflow file entirely with rationale in commit message. Commit message references T-035-03 scan report path. | `.github/workflows/*.yml` (per scan report); commit referencing `specs/2026-06-08-azure-decommission/workflow-scan-report.md` | proves AC-3 part 2; closes R4; post-repair `git grep` for Azure workflow keywords under `.github/workflows/` returns zero matches | S | T-035-03 | AFK (SW Developer or Developer worker) | Yes (single-file changes per workflow are parallel-safe) | pending |
| T-035-05 | Azure teardown in inventory order. Sub-steps: (1) AFK `az containerapp ingress disable -g rg-bridge-dashboard -n state-dashboard` (kill switch); (2) **HITL (gate G2)** owner removes GitHub repo settings Federated credentials entry for client id `625bdb84-d2e6-4853-96a9-f601571e3a0f`; (3) AFK `az ad app federated-credential delete --id 625bdb84-... --federated-credential-id <id>` (Azure-side cleanup); (4) AFK `az group delete -n rg-bridge-dashboard --yes --no-wait`; (5) AFK `az ad app delete --id 625bdb84-d2e6-4853-96a9-f601571e3a0f` (deletes app + SP); (6) AFK verification: `az group show -n rg-bridge-dashboard` (expect ResourceGroupNotFound), `az ad app show --id 625bdb84-...` (expect not-found), GitHub repo Federated credentials view (expect empty). Output committed to `verification-azure-delete.txt`. | (Azure resources deleted -- no repo file edits; `verification-azure-delete.txt` (new) under spec dir) | proves AC-4; closes R2, R3; resource group + Entra app + federated credential all verifiably absent | M | T-035-02 (gate G1), T-035-04 (workflows repaired before OIDC trust removed) | HITL (gate G2 owner browser sign-in for sub-step 2) | No (HITL + serial sub-steps) | pending |
| T-035-06 | `cli/state_builder.py` cloud-aware code-path review. Grep for keywords listed in `plan.md` design choice 5 (`MS-CLIENT-PRINCIPAL`, `CONTAINER_APP_NAME`, `WEBSITES_PORT`, `azurecontainerapps`, etc.). For each match: (a) if pure environment-variable read that is a no-op on localhost, LEAVE IN PLACE with a note in close-commit body; (b) if code that requires Azure environment to operate, REMOVE additively with commit-message marker "removed per SDD-035 ADR-015". **PI-4 frontmatter lock surface and PI-5 Sprint 7 UI lifecycle variant lock surface MUST be preserved byte-identical** (verify by `git diff --stat 4f81df6 -- cli/state_builder.py` and `git diff --stat <PI-4 base> -- cli/state_builder.py`). If NO matches found, R9 satisfied by close-commit body note. | `cli/state_builder.py` (additive removal only, if any) | proves AC-5; closes R9; either (a) zero matches with documented note, or (b) matches removed with lock surfaces preserved | S | T-035-02 (gate G1) | AFK (SW Developer); parallel-safe with T-035-03/T-035-04 | Yes (different file from workflows) | pending |
| T-035-07 | Docs purge per T-035-01 grep manifest. Sub-steps: (1) copy `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` to `docs/archive/PROVISIONED.md` with retirement note prepended; (2) delete original at `specs/2026-05-16-cloud-dashboard/PROVISIONED.md`; (3) edit `constitution/roadmap.md` PI-3 SDD-007 entry status to `DECOMMISSIONED 2026-06-DD per SDD-035 ADR-015 commit <CLOSE_SHA placeholder>`; (4) edit `backlog/BACKLOG.md` SDD-007 row status to `DECOMMISSIONED 2026-06-DD per SDD-035`; (5) edit `README.md` (repo root) and `spec-driven-development/README.md` to purge Azure dashboard references (replace with local invocation where appropriate); (6) edit any other doc flagged by grep manifest (case-by-case). | `docs/archive/PROVISIONED.md` (new); `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` (delete); `constitution/roadmap.md` (edit); `backlog/BACKLOG.md` (edit); `README.md`, `spec-driven-development/README.md` (edit); other docs per manifest | proves AC-6; closes R5, R6, R7, R8; `git grep` for live URL under `README.md`, `roadmap.md`, `BACKLOG.md` returns zero matches; archive copy present; SDD-007 row + roadmap entry both DECOMMISSIONED | M | T-035-05 (teardown done so docs don't reference live URL that just got deleted), T-035-06 (state_builder review done) | HITL (PM owns docs purge with grep manifest as truth source) | No (cross-cuts multiple shared docs) | pending |
| T-035-08 | Local dashboard end-to-end functional verification. Run `python spec-driven-development/cli/state_builder.py serve`; wait for boot; `curl -s` each documented route (`/`, plus any other route the serve handler exposes -- enumerate by reading the handler code); verify HTTP 200 for each; `grep -i "azurecontainerapps\|politehill-ac7984d9"` against each HTML response; expect zero matches. Commit commands + outputs to `verification-local-dashboard.txt`. | `specs/2026-06-08-azure-decommission/verification-local-dashboard.txt` (new) | proves AC-7; closes R12; all routes return 200; rendered HTML contains zero Azure refs | S | T-035-06 (state_builder review done), T-035-07 (docs purge done so rendered HTML reflects post-decommission state) | AFK (QA Engineer or SW Developer) | Yes | pending |
| T-035-09 | Close-out. Run full `python -m pytest spec-driven-development/ --tb=no -q` (expect >= 305 passed + 2 skipped); run `python spec-driven-development/cli/schema_lint.py` (expect exit 0); regenerate `exec/state.md` via `python spec-driven-development/cli/state_builder.py`; audit `validation.md` checkboxes (R1..R12 all checked; O1 + O2 best-effort); verify lock surfaces preserved (`git diff --stat 4f81df6 -- cli/state_builder.py`); prepare close-commit message referencing R1..R12 and flagging Level-2 reversal of 2026-05-16 SDD-007. **Request owner ratification (gate G3) BEFORE `git push origin master`.** | (verification + close commit only; commits the various edits from T-035-04, T-035-05 verification, T-035-06, T-035-07, T-035-08); regenerated `exec/state.md`, `exec/state.html`, `exec/work-index.md`, `exec/sprint-progress.md` | proves AC-8; closes R11; all REQUIRED items checked; **no DEFERRED markers permitted**; gate G3 owner-ratified; pushed to master | S | T-035-01..08 all done | HITL (gate G3 owner ratification before push) | No (close commit + push) | pending |

## Dependency Graph

```
T-035-01 -> T-035-02 (Gate G1) -+-> T-035-03 -> T-035-04 -+
                                |                          |
                                +-> T-035-06               +-> T-035-05 (Gate G2)
                                                                       |
                                                                       v
                                                                  T-035-07
                                                                       |
                                                                       v
                                                                  T-035-08
                                                                       |
                                                                       v
                                                                  T-035-09 (Gate G3)
```

Sequencing notes (per `plan.md` "Sequential Tasks"):

- T-035-01 is the precondition for T-035-02 (inventory needed for
  ADR cost-savings + consequences sections).
- **T-035-02 is Gate G1.** No destructive action proceeds until
  owner approves ADR-015 in writing.
- T-035-03 and T-035-06 are PARALLEL-SAFE after G1 (different
  files, both read-mostly).
- T-035-04 depends on T-035-03 (executes the repair plan).
- T-035-05 depends on T-035-02 (G1) AND T-035-04 (workflows must
  be repaired BEFORE OIDC trust is removed). **T-035-05 sub-step
  2 is Gate G2** (owner browser sign-in for GitHub Federated
  credentials removal).
- T-035-07 depends on T-035-05 (live URL no longer reachable;
  docs reflect post-decommission state) AND T-035-06 (state_builder
  review done; final state reflected in regenerated dashboards).
- T-035-08 depends on T-035-06 + T-035-07.
- T-035-09 fan-in: requires T-035-01..08 done. **Gate G3** owner
  ratification before `git push`.

## Batch Plan

- **Batch 1** (Phase 1: audit + decide, AFK):
  - T-035-01 -- inventory + grep manifest (single Cloud Security
    Architect session)
- **Batch 2** (Phase 1 close: HITL gate G1):
  - T-035-02 -- ADR-015 draft + owner approval
- **Batch 3** (Phase 2 prep, parallel after G1):
  - Track A: T-035-03 -- workflow scan
  - Track B: T-035-06 -- state_builder.py review
- **Batch 4** (Phase 2 close: serial, includes HITL gate G2):
  - T-035-04 -- workflow repairs
  - T-035-05 -- Azure teardown (sub-step 2 = G2)
- **Batch 5** (Phase 3 close):
  - T-035-07 -- docs purge
  - T-035-08 -- local-dashboard verification
- **Batch 6** (close, HITL gate G3):
  - T-035-09 -- pytest + schema_lint + state regen +
    validation audit + close commit + owner ratification + push

## Constraints (carry-over from plan.md "Lock-Surface Protections")

Implementers MUST NOT modify:

- `cli/fleet.py` (no Azure dependency; not in scope for SDD-035).
- `cli/dedup.py` (no Azure dependency; not in scope).
- `cli/schema_lint.py` (no Azure dependency; SDD-FDC-001 surface
  preserved).
- `cli/bootstrap.py` / `cli/qa.py` / `cli/retro.py` (no Azure
  dependency).
- `constitution/principles.md` (Article XII final at version
  1.3.0; decommission is operational, not principled).
- Any spec dir under `specs/2026-05-16-cloud-dashboard/` other
  than `PROVISIONED.md`.
- Any `sprints/PI-5/*` artifact (SDD-035 is out-of-band).
- Any `.github/prompts/*.prompt.md` (no prompt changes in scope).
- Any `feature-prompts/*.prompt.md` (no kickoff prompt changes).
- PI-4 frontmatter lock surface in `cli/state_builder.py` and the
  PI-5 Sprint 7 UI lifecycle variant lock surface in
  `cli/state_builder.py` (commits `4f81df6`, `22b6d22`,
  `0913583`). T-035-06 is additive removal only.

## Notes

- Use `Fleet Dispatch Eligible = No` for T-035-02 (HITL gate G1),
  T-035-05 (HITL gate G2 + serial sub-steps), T-035-07 (cross-cuts
  multiple shared docs), and T-035-09 (close commit + push).
- Owner review (HITL) required at T-035-02 (G1), T-035-05 sub-step
  2 (G2), and T-035-09 (G3).
- Maximum task count budget: 10 (per EM dispatch). Actual: **9**.
- **Out-of-band scheduling:** dispatch direction is "this week";
  expected execution window 2026-06-08..2026-06-13. No sprint
  artifact (no `sprint-progress.md` edit) is updated by SDD-035 --
  the close-commit body is the only sprint-adjacent surface and it
  explicitly flags the Level-2 reversal.
- **Carry-over policy:** if any task surfaces an ambiguity this
  spec did not resolve, mark "OWNER GUIDANCE REQUIRED" in `spec.md`
  Open Questions and STOP that task. Do not invent an answer. Do
  not silently widen scope.

## Close-Commit Template

```
close(sdd-035): Azure dashboard DECOMMISSIONED -- Level-2 reversal of 2026-05-16 SDD-007

Closes SDD-035 (out-of-band, 2026-06-DD). Reverses the 2026-05-16 cloud-deploy
commitment that shipped SDD-007 (Azure Container Apps + Entra ID + scale-to-zero +
OIDC CI/CD). Local dashboard (state_builder.py serve) remains as the single
source of truth.

All 12 REQUIRED validation items closed:
- R1 (inventory + grep manifest) -- commit <T-035-01 SHA>
- R10 (ADR-015 owner-approved Level-2 gate) -- commit <T-035-02 SHA>
- R4 (workflows scanned + repaired) -- commits <T-035-03/04 SHAs>
- R2, R3 (Azure resources + OIDC removed) -- commit <T-035-05 SHA>
- R9 (state_builder cloud-aware review) -- commit <T-035-06 SHA>
- R5, R6, R7, R8 (docs purge: PROVISIONED archived, roadmap + README + BACKLOG
  flipped) -- commit <T-035-07 SHA>
- R12 (local dashboard end-to-end verified) -- commit <T-035-08 SHA>
- R11 (305 baseline preserved; schema_lint clean; state.md regenerated) -- this commit

Optional: O1 (cost-savings calc in ADR-015) checked/deferred; O2 (PI-5 retro note)
checked/deferred.

Lock surfaces preserved byte-identical: PI-4 frontmatter contract surface in
cli/state_builder.py; PI-5 Sprint 7 UI lifecycle variant surface (commits 4f81df6,
22b6d22, 0913583).

OUT-OF-BAND: not folded into Sprint 8. Sprint 8 scope unchanged (SDD-022 + SDD-015).
SDD-036 / SDD-037 / SDD-038 (PI-6 dashboard reinvestment) now open on unforked
local-dashboard foundation.

Owner ratified before push (gate G3).

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```
