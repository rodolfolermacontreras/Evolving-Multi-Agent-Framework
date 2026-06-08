---
id: SDD-20260608ADOGHBRIDGE-spec
type: spec
status: active
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Feature Spec: ADO / GitHub Issues Sync Bridge (SDD-022)

- Date: 2026-06-08
- Authors: Principal Product Manager + Principal Architect
- Status: APPROVED for PLAN/TASKS/IMPLEMENT
- Priority: P2
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Spec ID: SDD-022
- Parent objective: PI-5 Objective 4 -- ADO/GitHub Bridge + Model Upgrade Discipline
- Lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
- CLARIFY: Closed 2026-06-08 in `clarify.md`; owner approved Q-A through Q-I defaults.

---

## Problem Statement

The framework currently produces implementation work as committed repo artifacts: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, sprint boards, and ledger rows. That works for a single developer inside VS Code, but it does not meet the adoption pattern Scott Epperly surfaced: external teams live in issue trackers and need SDD work to appear in their operational tracker.

The adoption gap is specific and practical:

1. **External teams need tracker-native visibility.** A teammate should be able to see SDD tasks as GitHub Issues or ADO Work Items without learning the whole spec directory structure first.
2. **The framework must not abandon file-backed traceability.** The reviewed source of truth still lives in repo files. An issue bridge must not silently overwrite specs, tasks, validation contracts, or sprint state.
3. **The bridge must stay portable.** The framework is meant to be adopted by arbitrary host projects. The sync mechanism cannot depend on host-specific files, cloud services, or third-party Python packages.
4. **GitHub must prove the model before ADO hardens.** Sprint 8 is GitHub-first with ADO fast-follow: live GitHub Issues round-trip is the v1 close criterion; ADO must be represented by the same provider boundary and dry-run/test fixture, not by live ADO API execution.

---

## Goals

SDD-022 delivers a `/taskstoissues` bridge that mirrors SDD task lists into external issue trackers while preserving the repo artifact contract.

The v1 goals are:

1. Parse an SDD `tasks.md` file into deterministic task records that can be rendered as tracker issues.
2. Create or update GitHub Issues from those records through explicit on-demand invocation.
3. Keep `tasks.md` authoritative and report remote conflicts without silently mutating local artifacts.
4. Persist task-to-issue identity in a deterministic per-spec-dir `issue-map.json` file.
5. Use environment-variable token auth, dry-run default, and redacted output so credentials are never committed or logged.
6. Keep HTTP implementation stdlib-only through `urllib.request`, `urllib.parse`, `urllib.error`, and `json`.
7. Preserve an ADO-compatible provider boundary and test fixture so ADO can fast-follow without redesigning the bridge.

---

## Non-Goals

- No background daemon, webhook listener, commit hook, or state-dashboard-triggered write behavior.
- No automatic mutation of `tasks.md` from issue tracker state.
- No live ADO API execution as a v1 close criterion.
- No third-party SDK wrappers for GitHub or ADO.
- No GitHub App installation flow.
- No ADO service connection setup.
- No assignee, milestone, dependency graph, estimate, or sprint-capacity synchronization.
- No ledger schema migration.
- No edits under `constitution/**`.
- No writes into an adopted host project's application files.
- No F-13 model-upgrade discipline work.

---

## Requirements

| ID | Requirement | Decision Source |
|----|-------------|-----------------|
| R1 | `tasks.md` is the authoritative local source. Issue trackers mirror task state in v1. | Q-A |
| R2 | GitHub Issues is the live v1 provider. ADO support is an adapter contract plus dry-run/test fixture fast-follow. | Q-B |
| R3 | Sync is explicit and on demand through `/taskstoissues`; no implicit hook, dashboard, or webhook writes. | Q-C, Q-E |
| R4 | Status and destructive conflicts are reported and block mutation; no last-writer-wins. | Q-D |
| R5 | Task-to-issue identity persists in per-spec-dir `issue-map.json`; no ledger schema migration. | Q-F |
| R6 | Auth uses env vars only; dry-run is default; no committed credentials or secret logging. | Q-G |
| R7 | Synced fields are title, generated body, labels, status, source links, and task ID. Assignee, milestone, and dependencies are excluded. | Q-H |
| R8 | HTTP and serialization use stdlib only: `urllib.request`, `urllib.parse`, `urllib.error`, and `json`. | Q-I |
| R9 | Implementation writes framework-owned artifacts only and never writes into host application files. | Sprint 8 hard constraint |
| R10 | CLI follows `docs/CLI-PATTERN.md`: `main(argv)`, argparse, pathlib, deterministic exit codes, stderr for expected errors. | Local convention |
| R11 | A slash prompt wrapper exists for `/taskstoissues` and documents dry-run-first usage. | Q-C, Q-E |
| R12 | F-14 validates with targeted tests, full pytest, schema_lint, and import scans proving no third-party tracker/HTTP dependency. | Sprint 8 quality gate |

---

## Acceptance Criteria

- **AC-1**: Given an SDD spec directory with a valid `tasks.md`, the bridge parses task IDs, titles, status, description, file scope, acceptance criteria references, and verification references into structured records. (R1, R7)
- **AC-2**: A dry-run invocation renders deterministic GitHub issue payloads without network writes and exits 0 when required local artifacts are valid. (R2, R3, R6)
- **AC-3**: A write invocation creates or updates GitHub Issues using `GITHUB_TOKEN` or `GH_TOKEN`; missing tokens fail before any write attempt with a redacted error. (R2, R6)
- **AC-4**: The command creates or updates a per-spec-dir `issue-map.json` that maps each local task ID to provider, remote ID, URL, last synced timestamp, generated body hash or equivalent sync fingerprint, and last seen remote status. (R5)
- **AC-5**: Re-running the command against an existing `issue-map.json` is idempotent: unchanged tasks do not produce duplicate issues, and changed generated sections update only the generated body region. (R5, R7)
- **AC-6**: If remote status conflicts with `tasks.md`, the command writes a conflict report, exits non-zero, and does not mutate `tasks.md`. (R1, R4)
- **AC-7**: `/taskstoissues` is the only documented trigger; no commit hook, dashboard refresh, webhook, or background worker writes externally. (R3)
- **AC-8**: Generated issue fields are limited to title, body, labels, status, source links, and task ID; assignee, milestone, and dependency graph are absent. (R7)
- **AC-9**: The provider boundary includes a GitHub provider and an ADO-compatible provider contract/test double; live ADO execution is not required for v1. (R2)
- **AC-10**: Implementation imports no third-party HTTP, GitHub, or ADO libraries and uses `urllib.request`, `urllib.parse`, `urllib.error`, and `json` for HTTP + serialization. (R8)
- **AC-11**: Implementation does not write into host project application files; generated sync state stays in the target spec directory. (R9)
- **AC-12**: F-14 closes with `python spec-driven-development/cli/schema_lint.py` exit 0 and full pytest exit 0 with test count at or above the Sprint 8 baseline plus new tests. (R12)

---

## Affected Modules

Approved implementation surfaces for F-14:

- `spec-driven-development/cli/taskstoissues.py` -- new stdlib CLI and provider boundary.
- `spec-driven-development/cli/test_taskstoissues.py` -- new tests for parsing, rendering, auth, dry-run, mapping, conflict detection, and provider behavior.
- `.github/prompts/taskstoissues.prompt.md` -- new slash prompt wrapper.
- `spec-driven-development/specs/*/issue-map.json` -- generated per-spec-dir mapping files when sync is invoked.
- `spec-driven-development/specs/*/issue-conflicts.md` -- generated per-spec-dir conflict report when conflicts are detected.

Blocked surfaces unless separately approved:

- `constitution/**`
- `spec-driven-development/ledger/schema.sql`
- `spec-driven-development/ledger/**` migration files
- Host project application files outside this framework repo
- Any package/dependency manifest adding a third-party HTTP or issue-tracker library

---

## Data Model

### `issue-map.json`

Each synced spec directory may contain one committed mapping file:

```json
{
  "schema_version": 1,
  "spec_id": "SDD-022",
  "provider": "github",
  "repository": "owner/name",
  "tasks": {
    "T-022-01": {
      "provider": "github",
      "remote_id": "123",
      "url": "https://github.com/owner/name/issues/123",
      "last_synced_at": "2026-06-08T00:00:00Z",
      "last_seen_remote_status": "open",
      "sync_fingerprint": "sha256:..."
    }
  }
}
```

Rules:

- The file is deterministic JSON with stable key ordering.
- It stores identity and sync metadata only; it does not store tokens.
- It lives beside the target `tasks.md`.
- It is the replayable source for future ADO migration or ledger promotion.

### Conflict Report

When conflicts are detected, the command writes `issue-conflicts.md` beside `tasks.md`. The report includes task ID, local status, remote status, remote URL, conflict type, and recommended owner action. It does not mutate `tasks.md`.

---

## API / CLI Contract

F-14 should implement a CLI compatible with this shape:

```powershell
python spec-driven-development/cli/taskstoissues.py push --spec-dir spec-driven-development/specs/2026-06-08-ado-github-bridge --provider github --repo owner/name --dry-run
python spec-driven-development/cli/taskstoissues.py push --spec-dir spec-driven-development/specs/2026-06-08-ado-github-bridge --provider github --repo owner/name --apply
python spec-driven-development/cli/taskstoissues.py conflicts --spec-dir spec-driven-development/specs/2026-06-08-ado-github-bridge --provider github --repo owner/name
```

Required semantics:

- Dry-run is default; `--apply` is required for network writes.
- Write mode requires `GITHUB_TOKEN` or `GH_TOKEN` for GitHub.
- Future ADO mode reserves `ADO_PAT`, `ADO_ORG_URL`, and `ADO_PROJECT` but does not require live ADO in v1.
- Exit code 0 = no blocking conflict; 1 = local validation/auth/network expected failure; 2 = remote conflict detected.

---

## Test Strategy

- Unit tests for task parsing, issue body rendering, label rendering, source-link rendering, and deterministic mapping serialization.
- Unit tests for env-var auth resolution and redaction of missing/invalid token errors.
- Unit tests for GitHub provider request construction using stdlib `urllib.*` with mocked opener/transport.
- Unit tests for conflict detection and conflict report generation.
- Unit tests or fixtures proving ADO provider contract shape without live ADO network calls.
- Import scan or test assertion proving no `requests`, `httpx`, `PyGithub`, `github`, `azure-devops`, or ADO SDK imports.
- Regression: `python spec-driven-development/cli/schema_lint.py` exit 0.
- Regression: full pytest suite exit 0 after F-14 code changes.

---

## Validation Contract

The binding validation contract lives in sibling file `validation.md` and is locked at F-12 pass 2. F-14 implementation must check every REQUIRED item before SDD-022 can be marked DONE.

---

## Traceability Matrix

| Requirement | Acceptance Criteria | Validation Items | Implementation Surface |
|-------------|---------------------|------------------|------------------------|
| R1 | AC-1, AC-6 | V-1, V-6 | `cli/taskstoissues.py` |
| R2 | AC-2, AC-3, AC-9 | V-2, V-3, V-9 | `cli/taskstoissues.py`, tests |
| R3 | AC-2, AC-7 | V-2, V-7, V-11 | CLI + slash prompt |
| R4 | AC-6 | V-6 | conflict detector/report |
| R5 | AC-4, AC-5 | V-4, V-5 | `issue-map.json` writer |
| R6 | AC-2, AC-3 | V-3, V-8 | auth helpers |
| R7 | AC-1, AC-8 | V-1, V-10 | renderer |
| R8 | AC-10 | V-12 | import scan/tests |
| R9 | AC-11 | V-13 | path guards/tests |
| R10 | AC-2, AC-3 | V-14 | CLI entry point |
| R11 | AC-7 | V-11 | `.github/prompts/taskstoissues.prompt.md` |
| R12 | AC-12 | V-15, V-16 | test suite + schema_lint |

---

## Open Questions

None. CLARIFY closed 2026-06-08.

---

## F-14 Caveats

- Live GitHub write validation requires the owner or operator to provide a safe `GITHUB_TOKEN` or `GH_TOKEN`. Automated tests must not require live network or committed credentials.
- ADO must remain structurally possible through the provider boundary, but live ADO API execution is not required for Sprint 8 close.
- Any pressure to add `requests`, `httpx`, `PyGithub`, `azure-devops`, or another third-party dependency is a new Level-2 decision and stops SDD-022 implementation until routed.---
id: SDD-20260608ADOGHBRIDGE-spec
type: spec
status: blocked
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---
# Feature Spec: ADO / GitHub Issues Sync Bridge (SDD-022)

> **Status note**: this spec is blocked on CLARIFY answers in
> [`clarify.md`](./clarify.md). SDD-FDC-001 has no `clarify` status,
> so `status: blocked` is the valid carrier for this phase. Do not
> implement against this file until CLARIFY closes and this spec is

- Date: 2026-06-08
- Authors: Principal Product Manager + Principal Architect
- Status: BLOCKED (F-12 pass 1; owner decisions pending)
- Priority: P2
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Spec ID: SDD-022
- Parent objective: PI-5 Objective 4 -- ADO/GitHub Bridge + Model
  Upgrade Discipline
Decision sections are authored in this pass. Acceptance Criteria,
Traceability Matrix, Plan, and Tasks are intentionally left as pending.
Reason: Q-A through Q-H in [`clarify.md`](./clarify.md) are owner-level
surfaces for an external issue-tracker bridge. Locking a spec before
those decisions are answered would invent owner decisions and violate
Article IX. Locking validation before the spec is complete would violate
Article X.

---

## Problem Statement

The framework currently produces implementation work as committed repo
artifacts: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, sprint
boards, and ledger rows. That works for a single developer inside VS
Code, but it does not meet the adoption pattern Scott Epperly surfaced
appear in their operational tracker.

The adoption gap is specific and practical:

1. **External teams need tracker-native visibility.** A teammate should
   be able to see SDD tasks as GitHub Issues or ADO Work Items without
   learning the whole spec directory structure first.
2. **The framework must not abandon file-backed traceability.** The
   reviewed source of truth still lives in repo files. An issue bridge
   must not silently overwrite specs, tasks, validation contracts, or
   sprint state.
3. **The bridge must stay portable.** The framework is meant to be
   adopted by arbitrary host projects. The sync mechanism cannot depend
   on host-specific files, cloud services, or third-party Python
   packages.
   Sprint 8 kickoff says GitHub-first with ADO fast-follow; the owner
   must confirm whether live ADO is v1-required or a provider contract
   after GitHub is proven.

---

## Goal

Define a `/taskstoissues` bridge that can turn SDD `tasks.md` rows into
external tracker issues while preserving the framework's file-backed
contract and Article V stdlib-only discipline.

locked validation contract for F-14 that specifies:

- Which artifact is authoritative (`tasks.md`, tracker, or
- Which tracker provider is live in v1.
- How sync is invoked.
- Which auth model is used without committing secrets.
- That HTTP access uses Python stdlib `urllib.*` only.
---
## Constraints

  only. No `requests`, `httpx`, `PyGithub`, `azure-devops`, or other
  third-party package.
- **No constitution edits** in F-12.
  spec directory or framework CLI surfaces, not in host project files.
- **No F-13 work**: model-upgrade discipline remains a separate Sprint 8
---
## Out-of-Scope for SDD-022 v1 Unless Owner Upgrades Scope

- Background daemon, webhook listener, or state-dashboard-triggered
  write behavior.
- Automatic mutation of `tasks.md` from issue tracker state.
- Third-party SDK wrappers for GitHub or ADO.
- GitHub App installation flow.
- ADO service connection setup.
- Assignee, milestone, dependency graph, estimate, or sprint-capacity
  synchronization.
- Any edits under `constitution/**`.
- Any writes into an adopted host project's application files.

---

## Open Decisions Blocking SPEC Finalization


| ID | Decision | Status |
|----|----------|--------|
| Q-A | Direction of authority | OPEN |
| Q-B | Canonical issue system for v1 | OPEN |
| Q-C | Sync cadence | OPEN |
| Q-D | Conflict resolution semantics | OPEN |


Expected AC areas, not yet locked:

- AC area for authority model and mutation boundaries.
- AC area for GitHub provider behavior and ADO fast-follow boundary.
- AC area for synced field rendering.
- AC area for schema_lint, full tests, and no host-project writes.

---


**TBD pending CLARIFY close.** Candidate surfaces only:

- `spec-driven-development/cli/taskstoissues.py` (new, candidate)
- `spec-driven-development/cli/test_taskstoissues.py` (new, candidate)
- `spec-driven-development/templates/task-list.md` (possible doc-only
  guidance if mapping file is confirmed)
  per-spec-dir state if Q-F recommendation is accepted)
No candidate surface is approved until CLARIFY closes.


**TBD pending CLARIFY close.** Expected strategy:

- Unit tests for task parsing, body rendering, mapping serialization,
  conflict detection, auth/env-var validation, and stdlib HTTP request
  construction.
  doubles; no live network in automated tests.
- Manual check only for optional live GitHub token smoke, if owner
  approves live write validation.
- `python spec-driven-development/cli/schema_lint.py` clean.
- Full suite only in F-14 if code is touched.

---

## Validation Contract

The sibling [`validation.md`](./validation.md) is a draft scaffold only.
It must be populated and locked after owner decisions are recorded.

---

## Traceability Matrix

**TBD pending CLARIFY close.**
