---
id: SDD-20260608AZUREDECOM-plan
type: plan
status: active
owner: principal-cloud-security-architect
updated: 2026-06-08
feature: 2026-06-08-azure-decommission
---

# Implementation Plan: SDD-035 -- Azure Dashboard Decommission

- Spec Reference: `spec.md` (SDD-035)
- Sprint: OUT-OF-BAND (2026-06-08..2026-06-13); NOT folded into Sprint 8
- Author: Principal Cloud Security Architect (EM dispatch, Phase A.3)
- Date: 2026-06-08

---

## Approach Summary

Operational decommission with three serialized phases and one
Level-2 owner approval gate. No new architecture, no new code,
additive removal only.

**Phase 1 -- Audit and decide.** Inventory every Azure resource and
every in-repo Azure reference (T-035-01); draft ADR-015 with
cost-savings analysis and present for owner approval (T-035-02). No
destructive action in this phase. **R10 (ADR-015 owner approval) is
the gate; nothing destructive proceeds until it is checked.**

**Phase 2 -- Repair upstream and tear down.** Scan and repair every
GitHub Actions workflow that consumes the OIDC trust or references
Azure (T-035-03, T-035-04); then execute Azure resource teardown in
inventory order (T-035-05). T-035-05 splits into AFK steps (Azure
CLI `az group delete`) and one HITL step (GitHub repo settings OIDC
removal, requires owner browser).

**Phase 3 -- Purge docs, verify local, close.** Review
`cli/state_builder.py` for cloud-aware code paths and remove them
additively (T-035-06); purge README + roadmap + BACKLOG; retire
PROVISIONED.md to archive (T-035-07); verify local dashboard
end-to-end (T-035-08); close-out with owner ratification (T-035-09).

The plan reuses the existing decommission runbook embedded in
`specs/2026-05-16-cloud-dashboard/PROVISIONED.md` "Operational
commands" table (`az group delete -n rg-bridge-dashboard --yes
--no-wait && az ad app delete --id ...`). No new tooling required.

### Design Choices (no new ADRs beyond ADR-015)

1. **Inventory format.** `azure-resource-inventory.json` =
   `az group export --resource-group rg-bridge-dashboard` output +
   `az ad app show --id 625bdb84-d2e6-4853-96a9-f601571e3a0f` output
   + `az ad sp show --id 8b2fc156-312a-4f58-9f60-ac9dd69a0aa1`
   output, concatenated under three top-level keys (`resource_group`,
   `entra_app`, `service_principal`). Plus a fourth key
   (`oidc_federated_credentials`) populated from `az ad app
   federated-credential list --id 625bdb84-...` if any exist.
   Stdlib JSON. No new tooling.

2. **Repo grep manifest.** `repo-references.md` = output of
   `git grep -n -i "azurecontainerapps\|politehill-ac7984d9\|
   state-dashboard\|rg-bridge-dashboard\|625bdb84\|cae-bridge-
   dashboard\|ca24921a026cacr"` (or the equivalent multi-pattern
   `git grep -f patterns.txt`), formatted as a Markdown table with
   columns: path, line, snippet. Becomes the authoritative
   reference list for T-035-07 docs purge.

3. **ADR-015 number.** Confirmed free at scaffold (013, 014 taken;
   `ls docs/ADR/` returns 001..014 plus TEMPLATE.md). T-035-02
   creates `docs/ADR/015-azure-dashboard-decommission.md` from
   `docs/ADR/TEMPLATE.md`.

4. **Teardown order (T-035-05 sub-steps).** Strict dependency order
   to avoid orphaned references:
   1. (AFK) `az containerapp ingress disable` (kill switch first --
      stops accepting traffic immediately, lets in-flight requests
      drain).
   2. (HITL) Owner removes GitHub repo settings Federated credentials
      entry (cannot be automated; requires owner browser sign-in).
   3. (AFK) `az ad app federated-credential delete` (cleans up the
      Azure side of the federation).
   4. (AFK) `az group delete -n rg-bridge-dashboard --yes --no-wait`
      (deletes container app, environment, registry, log analytics
      workspace, any storage account, any key vault).
   5. (AFK) `az ad app delete --id 625bdb84-...` (deletes Entra app
      + service principal; SP is auto-deleted with the app).
   6. (AFK) Verification commands; output committed to spec dir.

5. **Cloud-aware code review scope (T-035-06).** Search keywords in
   `cli/state_builder.py`:
   - `MS-CLIENT-PRINCIPAL` / `MS_CLIENT_PRINCIPAL` (Easy Auth header)
   - `X-MS-CLIENT-PRINCIPAL-ID` / `X-MS-CLIENT-PRINCIPAL-NAME`
   - `CONTAINER_APP_NAME` / `CONTAINER_APP_REVISION`
   - `WEBSITES_PORT` / `WEBSITE_HOSTNAME`
   - `azurecontainerapps` / `politehill-ac7984d9`
   - Any hard-coded Azure URL
   If grep returns ZERO matches, R9 is satisfied by a note in the
   close-commit body. If grep returns matches, the matching code is
   reviewed; pure environment-variable reads that are no-ops on
   localhost are LEFT IN PLACE (no functional harm); only code that
   *requires* the Azure environment to operate is removed (additive
   deletion, lock surfaces preserved).

6. **Docs-purge plan (T-035-07 sub-steps).** Strict ordering to
   preserve referential integrity:
   1. Copy `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` to
      `docs/archive/PROVISIONED.md` with retirement note prepended.
   2. Delete `specs/2026-05-16-cloud-dashboard/PROVISIONED.md`.
   3. Edit `constitution/roadmap.md` PI-3 SDD-007 entry.
   4. Edit `backlog/BACKLOG.md` SDD-007 row.
   5. Edit `README.md` (repo root) and
      `spec-driven-development/README.md` per the R1 grep manifest.
   6. Edit any other doc the grep manifest flags (case-by-case;
      historical-record sections preserved with documentation).

---

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Audit + decide (no destructive action) | None | Inventory JSON + repo-references.md + ADR-015 (drafted, owner-approved) |
| 2 | Repair upstream + Azure teardown | Phase 1 complete (R10 checked) | Workflow scan report + repaired workflows + Azure resources deleted + verification artifacts |
| 3 | Docs purge + local verification + close | Phase 2 complete | state_builder.py review note + retired PROVISIONED.md + edited README/roadmap/BACKLOG + local dashboard verification + close commit |

---

## File Scope (additive removal + doc-only, NO new functional code)

| File / Resource | Change Type | R-Items | Task |
|-----------------|-------------|---------|------|
| `specs/2026-06-08-azure-decommission/spec.md` | **NEW** (this spec) | (scaffold) | -- |
| `specs/2026-06-08-azure-decommission/validation.md` | **NEW** (this spec) | (scaffold) | -- |
| `specs/2026-06-08-azure-decommission/plan.md` | **NEW** (this file) | (scaffold) | -- |
| `specs/2026-06-08-azure-decommission/tasks.md` | **NEW** (this spec) | (scaffold) | -- |
| `specs/2026-06-08-azure-decommission/azure-resource-inventory.json` | **NEW**: JSON dump of Azure config | R1 | T-035-01 |
| `specs/2026-06-08-azure-decommission/repo-references.md` | **NEW**: grep manifest | R1 | T-035-01 |
| `specs/2026-06-08-azure-decommission/workflow-scan-report.md` | **NEW**: workflow enumeration + repair plan | R4 | T-035-03 |
| `specs/2026-06-08-azure-decommission/verification-azure-delete.txt` | **NEW**: CLI output / screenshot of Azure deletion | R2, R3 | T-035-05 |
| `specs/2026-06-08-azure-decommission/verification-local-dashboard.txt` | **NEW**: local route smoke test output | R12 | T-035-08 |
| `docs/ADR/015-azure-dashboard-decommission.md` | **NEW**: ADR (Level-2 gate) | R10 | T-035-02 |
| `docs/archive/PROVISIONED.md` | **NEW**: archived copy with retirement note | R5 | T-035-07 |
| `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` | **DELETE** (after archive copy) | R5 | T-035-07 |
| `README.md` (repo root) | **EDIT**: purge Azure refs | R7 | T-035-07 |
| `spec-driven-development/README.md` | **EDIT**: purge Azure refs (if any) | R7 | T-035-07 |
| `constitution/roadmap.md` | **EDIT**: PI-3 SDD-007 status -> DECOMMISSIONED | R6 | T-035-07 |
| `backlog/BACKLOG.md` | **EDIT**: SDD-007 row status -> DECOMMISSIONED | R8 | T-035-07 |
| `cli/state_builder.py` | **ADDITIVE REMOVAL ONLY** (if any cloud-aware paths exist; else no change with written note) | R9 | T-035-06 |
| `.github/workflows/*.yml` (each) | **REPAIR or REMOVE** per T-035-03 plan | R4 | T-035-04 |
| Any other doc flagged by R1 grep | **EDIT** case-by-case | R7 | T-035-07 |
| `exec/state.md`, `exec/state.html`, `exec/work-index.md`, `exec/sprint-progress.md` | **REGENERATE** by `state_builder.py` at close | R11 | T-035-09 |

### Files NOT in scope

- `constitution/principles.md` -- no constitutional change. Article
  XII (UI Lifecycle Variant) is final at version 1.3.0 (ratified
  Sprint 7 close `4f81df6` + `22b6d22`). Decommission is operational,
  not principled.
- Any spec dir under `specs/2026-05-16-cloud-dashboard/` other than
  `PROVISIONED.md` -- the original SDD-007 spec / plan / tasks
  files are preserved as historical record.
- `sprints/PI-5/*` -- this spec is OUT-OF-BAND; not bound to any
  sprint artifact.
- `cli/fleet.py`, `cli/dedup.py`, `cli/schema_lint.py`,
  `cli/qa.py`, `cli/retro.py`, `cli/bootstrap.py` -- no Azure
  dependency.
- `feature-prompts/*` -- no edits.

---

## Lock-Surface Protections (DO NOT EDIT)

The following code surfaces are **LOCKED** by prior sprint commits
and **MUST NOT** be modified by any T-035-NN task. Implementers
verify by `git diff --stat` and by reviewing diff hunks before
commit.

### From Sprint 6 commit `524872b` (`cli/fleet.py` -- SDD-019)

- `_scan_lock_state`, `cmd_lock_*` subcommand handlers, pre-dispatch
  gate refusal in `cmd_dispatch`. **Not edited by SDD-035** (no
  fleet.py changes in scope).

### From Sprint 6 commit `8eb564d` (`cli/dedup.py` -- SDD-020)

- `load_corpus`, `_parse_*`, `_tokenize`, `_jaccard`,
  `find_overlaps`, `_format_overlap`, `handle_overlaps`. **Not
  edited by SDD-035** (no dedup.py changes in scope).

### From Sprint 6 / Sprint 7 commit `4a6941c` + `557b672` + `8025a50` + `a6a25e4` (SDD-032 completion bundle)

- `cli/fleet.py` queue ordering + grandfather helpers.
- `cli/dedup.py` log writers + `--emit-logs` flag.
- `.github/prompts/triage.prompt.md` + `clarify.prompt.md` hook
  lines.
- **Not edited by SDD-035.**

### From PI-4 frontmatter-data-contract work (`cli/schema_lint.py`)

- SDD-FDC-001 artifact contract walk in `_walk_artifacts`,
  `check_artifact`, `REQUIRED_CONTRACT_FIELDS`,
  `ARTIFACT_TYPE_ENUM`, `ARTIFACT_STATUS_ENUM`. **Not edited by
  SDD-035** (no schema_lint changes in scope).

### From PI-5 Sprint 7 UI Lifecycle Variant (commits `4f81df6`, `22b6d22`, `0913583`; SDD-018)

- `cli/state_builder.py` rendering of `## Delta Entries` sections
  in spec validation files; SDD-018 demo-route handling;
  ui-variant marker detection.
- **R9 (T-035-06) reviews state_builder.py for cloud-aware code
  paths ONLY.** UI lifecycle variant code paths in
  state_builder.py are NOT touched. Verification: `git diff --stat
  4f81df6 -- cli/state_builder.py` shows no changes to ui-variant
  line ranges.

### From PI-4 frontmatter lock surface

- Frontmatter parsing utilities in `cli/state_builder.py` (the
  module that reads spec dir frontmatter to render the dashboard).
  Pure additive removal only; parsing surface preserved
  byte-identical.

---

## Owner Sign-Off Gates

SDD-035 explicitly requires Level-2 owner ratification at three
points:

1. **Gate G1 -- ADR-015 owner approval (BEFORE Phase 2 begins).**
   At T-035-02 completion, Cloud Security Architect presents
   ADR-015 to owner via EM. Owner approves in writing (recorded
   inline in the ADR + in the EM session log). **No Azure teardown
   action proceeds until G1 is checked.** This is the Level-2
   reversal-of-2026-05-16 gate.

2. **Gate G2 -- GitHub OIDC trust removal (owner HITL action,
   inside T-035-05).** Cloud Security Architect cannot remove the
   GitHub repo Federated credentials entry; this is a repo-settings
   action requiring owner browser sign-in. T-035-05 sub-step 2
   queues this as a single owner-action item with explicit
   instructions ("Settings -> Secrets and variables -> Actions ->
   Federated credentials -> delete the entry for client id
   `625bdb84-d2e6-4853-96a9-f601571e3a0f`").

3. **Gate G3 -- Close-commit owner ratification (BEFORE push).**
   Per Sprint 7 Option 3 hybrid precedent, the close commit is
   prepared, tests run, validation contract checked, then
   ratification requested from owner BEFORE `git push origin
   master`. Owner ratification recorded in close-commit body or EM
   session log.

---

## Parallel-Safe Tasks

- **T-035-01 (inventory + grep)** -- self-contained; no
  dependencies; parallel-safe with nothing else (T-035-02 depends
  on it).
- **T-035-03 (workflow scan) vs T-035-06 (state_builder review)** --
  different files, both read-only. PARALLEL-SAFE after T-035-02.
  Both block T-035-05 (workflow scan must precede teardown so OIDC
  removal does not break active pipelines).
- **T-035-08 (local-dashboard verification)** -- depends on T-035-06
  completion (state_builder.py review done); otherwise self-
  contained.

## Sequential Tasks

1. T-035-01 -- Azure inventory + repo grep manifest (Cloud
   Security Architect, AFK).
2. T-035-02 -- Draft ADR-015 + present for owner approval
   (Cloud Security Architect; HITL gate G1). **STOPS HERE if
   owner does not approve.**
3. (After G1) T-035-03 -- Workflow scan + repair plan (SW
   Developer, AFK, parallel with T-035-06).
4. (After G1) T-035-06 -- state_builder.py cloud-aware review
   (SW Developer, AFK, parallel with T-035-03).
5. (After T-035-03) T-035-04 -- Execute workflow repairs
   (SW Developer or Developer worker, AFK).
6. (After T-035-04) T-035-05 -- Azure teardown sub-steps in
   order, including HITL gate G2 (Cloud Security Architect +
   owner browser).
7. (After T-035-05, T-035-06) T-035-07 -- Docs purge (PM;
   uses T-035-01 grep manifest as authoritative reference).
8. (After T-035-07) T-035-08 -- Local dashboard end-to-end
   verification (QA Engineer or SW Developer, AFK).
9. (After T-035-08) T-035-09 -- Close-out: full pytest +
   schema_lint + state regen + validation audit + owner
   ratification (gate G3) + close commit + push.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Owner does not approve ADR-015 at G1; decommission cannot proceed | Low | Low | This is the gate, not a risk. If owner reverses the decommission direction, SDD-035 is suspended; no harm done; existing Azure deployment continues. |
| OIDC removal breaks active CI/CD workflows | Medium | Medium | T-035-03 workflow scan precedes T-035-05 OIDC removal; T-035-04 repairs every dependent workflow first. Hard ordering enforced by task deps. |
| Cloud-aware code-path removal accidentally breaks local rendering | Low | High | T-035-06 is additive removal only with explicit grep-keyword list; T-035-08 end-to-end local smoke test verifies. PI-4 + PI-5 lock surfaces explicitly preserved. |
| Docs purge misses an Azure reference | Medium | Low | T-035-01 grep manifest is the authoritative reference list. Any later-found reference filed as P3 docs bug (SDD-040+), not a spec re-open. |
| `az group delete --no-wait` returns success but resources persist for hours | Medium | Low | T-035-05 sub-step 6 verification queries `az group show` after a brief wait; if not-yet-deleted, the close is HELD with a status note ("teardown initiated; resource group deletion in progress per Azure async semantics"). R2 check tolerates a brief async window. |
| Resurrection later needed and inventory JSON is insufficient | Low | Medium | `az group export` captures the ARM template; combined with the documented `az containerapp up --source .` command + the documented `az ad app update --enable-id-token-issuance true` fix from PROVISIONED.md, resurrection is ~2 hours of work. Acceptable risk. |
| Owner sign-in for G2 is unavailable for several days | Medium | Low | T-035-05 can stop at sub-step 1 (ingress disabled = effectively decommissioned from traffic perspective). Sub-steps 2..6 resume when owner is available. R2 / R3 / R12 unaffected. |
| schema_lint refuses new spec dir frontmatter | Low | High | Spec dir frontmatter uses verified schema-lint-compatible values (`type: spec/plan/tasks/validation`, `status: active`, valid `updated` ISO date). Scaffold verified by running schema_lint before commit. |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | S | Inventory is one CLI command + JSON capture; grep is one `git grep` invocation; ADR is one document. ~30 min Cloud Security Architect + ~15 min owner review. |
| 2 | M | Workflow scan + repair = 30-60 min depending on workflow count; Azure teardown = 10 min CLI + async wait; OIDC removal HITL = 2 min owner action. |
| 3 | S | state_builder review = 15 min (grep + read); docs purge = 30 min (small file count); local-dashboard verification = 10 min smoke test; close = 15 min. |

Total: **S to M** (one out-of-band session, ~2-3 hours active time
spread across 1-2 days depending on owner availability for G1 and
G2).

## Validation Criteria

> Cross-reference rule: each validation checkbox below references
> the spec AC and the validation.md R-item it covers.

- [ ] Validates AC-1 / R1 (inventory + grep manifest).
- [ ] Validates AC-2 / R10 (ADR-015 owner-approved, Level-2 gate).
- [ ] Validates AC-3 / R4 (workflow scan + repair).
- [ ] Validates AC-4 / R2 + R3 (Azure resources deleted + OIDC
  removed).
- [ ] Validates AC-5 / R9 (state_builder.py review, additive
  removal only).
- [ ] Validates AC-6 / R5 + R6 + R7 + R8 (docs purge: PROVISIONED
  retired, roadmap + README + BACKLOG updated).
- [ ] Validates AC-7 / R12 (local dashboard end-to-end functional).
- [ ] Validates AC-8 / R11 (test baseline preserved, schema_lint
  clean, close commit owner-ratified).

## Cross-Feature Notes

- **SDD-036 / SDD-037 / SDD-038 (PI-6 dashboard reinvestment)**
  open after SDD-035 closes, so they start on an unforked
  foundation (local dashboard as single source of truth).
- **SDD-022 (Sprint 8 ADO/GitHub Issues bridge)** runs in parallel;
  unrelated to the Azure dashboard surface.
- **Sprint 7 close** (commits `4f81df6` + `22b6d22` +
  `0913583`) is final at scaffold time; SDD-035 does NOT modify
  any Sprint 7 close artifact.
- **PI-5 Sprint 4 / Sprint 8** carries its own scope (SDD-022 +
  SDD-015 + 14 Level-1 surfaces per F-11 close report). SDD-035 is
  out-of-band and does NOT add to Sprint 8 scope.
