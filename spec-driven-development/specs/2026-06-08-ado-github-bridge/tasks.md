---
id: SDD-20260608ADOGHBRIDGE-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Task List: ADO / GitHub Issues Sync Bridge (SDD-022)

- Spec Reference: `./spec.md`
- Plan Reference: `./plan.md`
- Validation Reference: `./validation.md`
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Owner: Principal Software Developer
- Test baseline: >= 305
- Lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

---

## Batch Overview

| Batch | Tasks | Mode | Notes |
|-------|-------|------|-------|
| B1 | T-022-01 -> T-022-04 | Sequential | Shared `cli/taskstoissues.py`; establish parser, renderer, mapping |
| B2 | T-022-05 -> T-022-07 | Mostly sequential | Provider/auth/conflict behavior shares CLI surface |
| B3 | T-022-08, T-022-09 | Parallel after T-022-06 | Prompt wrapper and import/path guard tests can split if interfaces are stable |
| B4 | T-022-10 | Sequential close-out | Validation, schema_lint, full pytest, checkboxes |

---

## Task T-022-01: Implement tasks.md parser

**Story**: [R1, R7] Parse the authoritative local task contract
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: `constitution/**`, `spec-driven-development/ledger/**`, `spec-driven-development/cli/fleet.py`, `spec-driven-development/cli/state_builder.py`
**Depends on**: NONE

### Description

Create `cli/taskstoissues.py` with a parser that reads a spec directory's `tasks.md` and extracts task ID, title, status, requirement/story traceability, file scope, blocked files, description, acceptance criteria, and verification commands. Expected parse failures should raise a custom CLI error and return a non-zero exit through `main(argv)`.

### Acceptance Criteria

- [ ] Parses current SDD-022 `tasks.md` into structured task records.
- [ ] Parses at least one prior completed `tasks.md` fixture without false task boundaries.
- [ ] Reports missing `tasks.md`, duplicate task IDs, or malformed task headings clearly.
- [ ] Does not infer authority from issue tracker state.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "parser or task_records" -v --tb=short
```

---

## Task T-022-02: Render deterministic issue payloads

**Story**: [R3, R7] Render tracker fields without network writes
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: `constitution/**`, `spec-driven-development/ledger/**`, host project application files
**Depends on**: T-022-01

### Description

Render deterministic GitHub issue payloads from parsed task records. Payload includes title, generated body, labels, status intent, source links, and task ID. Body must include generated-region markers so future updates avoid clobbering human tracker discussion.

### Acceptance Criteria

- [ ] Title rendering is stable and includes task ID.
- [ ] Body rendering includes description, source links, acceptance criteria references, file scope, and validation references.
- [ ] Labels include `sdd`, spec ID, provider/lifecycle/status labels as defined in tests.
- [ ] Payload excludes assignee, milestone, and dependency graph fields.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "render or payload or labels" -v --tb=short
```

---

## Task T-022-03: Add CLI entry point and dry-run behavior

**Story**: [R3, R10] Explicit on-demand `/taskstoissues` command shape
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: `constitution/**`, `.github/prompts/taskstoissues.prompt.md`
**Depends on**: T-022-02

### Description

Add argparse CLI with `main(argv)` and subcommands for push/dry-run and conflict checking. Dry-run must be default. `--apply` is required for network writes. Exit codes: 0 for success/no blocking conflict, 1 for local/auth/network expected failure, 2 for remote conflict.

### Acceptance Criteria

- [ ] `main(argv)` is testable without subprocess.
- [ ] Dry-run default renders planned changes and performs no network write.
- [ ] `--apply` is required before provider write functions are invoked.
- [ ] `--help` output is clean.
- [ ] Expected errors print to stderr and return non-zero.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "cli or dry_run or argparse" -v --tb=short
```

---

## Task T-022-04: Implement issue-map.json serialization and idempotency

**Story**: [R5] Persist task-to-issue identity beside tasks.md
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: `spec-driven-development/ledger/schema.sql`, `spec-driven-development/ledger/**`
**Depends on**: T-022-03

### Description

Implement deterministic `issue-map.json` load/write behavior with schema version, spec ID, provider, repository, per-task provider, remote ID, URL, `last_synced_at`, `last_seen_remote_status`, and sync fingerprint. Re-running sync must choose update over duplicate create when mapping exists.

### Acceptance Criteria

- [ ] Mapping JSON is stable and sorted.
- [ ] Mapping stores no tokens or secrets.
- [ ] Existing task mapping prevents duplicate issue creation.
- [ ] Changed generated body fingerprints trigger update path.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "mapping or idempotent or fingerprint" -v --tb=short
```

---

## Task T-022-05: Implement GitHub provider with env-var auth

**Story**: [R2, R6, R8] GitHub live provider through stdlib HTTP
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: dependency manifests, `constitution/**`
**Depends on**: T-022-04

### Description

Implement GitHub provider request construction and response handling using `urllib.request`, `urllib.parse`, `urllib.error`, and `json`. Resolve auth from `GITHUB_TOKEN` first, then `GH_TOKEN`. Missing token in apply mode fails before write. Tests must mock transport and avoid live network.

### Acceptance Criteria

- [ ] GitHub create/update/get status requests are constructed correctly.
- [ ] Missing token fails before provider write.
- [ ] Command output and errors redact secrets.
- [ ] Tests do not require live network or committed credentials.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "github or auth or urllib" -v --tb=short
```

---

## Task T-022-06: Add provider boundary and ADO-compatible test double

**Story**: [R2] Keep ADO fast-follow structurally possible
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: `spec-driven-development/ledger/**`, dependency manifests
**Depends on**: T-022-05

### Description

Extract provider operations around create/update/read remote status. Add an ADO-compatible provider contract or dry-run/test double that proves equivalent payload shape and reserved env-var names (`ADO_PAT`, `ADO_ORG_URL`, `ADO_PROJECT`) without live ADO API calls.

### Acceptance Criteria

- [ ] GitHub provider uses the shared provider boundary.
- [ ] ADO test double exercises the same create/update/status contract.
- [ ] No live ADO network call is required.
- [ ] Provider-specific behavior is isolated from parser/renderer logic.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "provider or ado" -v --tb=short
```

---

## Task T-022-07: Implement conflict detection and report writing

**Story**: [R1, R4] `tasks.md` wins; conflicts report, not mutate
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/taskstoissues.py`, `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: target `tasks.md` mutation, `constitution/**`
**Depends on**: T-022-06

### Description

Compare local task status against mapped remote issue status. If remote state conflicts with `tasks.md`, write `issue-conflicts.md`, exit with code 2, and do not mutate `tasks.md`. Conflict report includes task ID, local status, remote status, remote URL, conflict type, and recommended owner action.

### Acceptance Criteria

- [ ] Closed remote vs pending local produces conflict report.
- [ ] Open/reopened remote vs done local produces conflict report.
- [ ] Conflict path leaves `tasks.md` byte-unchanged.
- [ ] Conflict command exits 2.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "conflict" -v --tb=short
```

---

## Task T-022-08: Create /taskstoissues slash prompt wrapper

**Story**: [R3, R11] Expose explicit lifecycle trigger
**Type**: [P] parallelizable after provider CLI contract stabilizes
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `.github/prompts/taskstoissues.prompt.md`
**Files Blocked**: `spec-driven-development/cli/taskstoissues.py`, `constitution/**`
**Depends on**: T-022-03

### Description

Create `.github/prompts/taskstoissues.prompt.md` with frontmatter and operating instructions. The prompt should instruct agents to run dry-run first, require explicit apply confirmation for writes, explain env vars, explain conflict semantics, and state that no commit hook/dashboard/webhook triggers exist in v1.

### Acceptance Criteria

- [ ] Prompt file exists with valid frontmatter.
- [ ] Prompt documents dry-run default and `--apply` write requirement.
- [ ] Prompt documents `GITHUB_TOKEN` / `GH_TOKEN` and future ADO env vars.
- [ ] Prompt states `tasks.md` is authoritative and conflicts do not mutate local artifacts.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
```

---

## Task T-022-09: Add dependency and path guard tests

**Story**: [R8, R9, R12] Protect Article V and host-project boundaries
**Type**: [P] parallelizable after T-022-05
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/cli/test_taskstoissues.py`
**Files Blocked**: dependency manifests, host project application files
**Depends on**: T-022-05

### Description

Add tests that inspect imports and path behavior. Import tests must fail if third-party HTTP/tracker libraries appear. Path tests must prove generated state writes are constrained to the target framework spec directory.

### Acceptance Criteria

- [ ] Import scan rejects `requests`, `httpx`, `PyGithub`, `github`, `azure-devops`, and ADO SDK imports.
- [ ] Generated mapping/conflict paths resolve under the target spec directory.
- [ ] Host application paths are not accepted as generated sync state destinations.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_taskstoissues.py -k "import or path_guard or host" -v --tb=short
```

---

## Task T-022-10: Close SDD-022 validation

**Story**: [R12] Prove no regression and mark validation complete
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-ado-github-bridge/validation.md`, `spec-driven-development/specs/2026-06-08-ado-github-bridge/spec.md`, `spec-driven-development/specs/2026-06-08-ado-github-bridge/tasks.md`
**Files Blocked**: F-13 SDD-015 artifacts unless F-14 explicitly owns joint close-out
**Depends on**: T-022-07, T-022-08, T-022-09

### Description

Run targeted tests, schema_lint, and full pytest. Check V-1 through V-16 in `validation.md` only after evidence exists. Mark task statuses done and update spec status only at implementation close.

### Acceptance Criteria

- [ ] `python spec-driven-development/cli/schema_lint.py` exits 0.
- [ ] Full pytest exits 0 with test count >= Sprint 8 baseline + new tests.
- [ ] All REQUIRED validation items V-1..V-16 are checked with evidence.
- [ ] Optional live GitHub smoke is either completed with owner-provided safe target or explicitly noted as skipped.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```

---

## Conflict Notes

- `cli/taskstoissues.py` is a shared implementation file across most tasks; run T-022-01 through T-022-07 sequentially unless the Software Developer creates explicit edit ownership boundaries.
- `.github/prompts/taskstoissues.prompt.md` can be worked independently after the CLI contract exists.
- No task may add a third-party dependency.
- No task may write into `constitution/**`.
- No task may start F-13 or modify SDD-015 artifacts.

---

## Traceability

| Task | Requirements | Validation |
|------|--------------|------------|
| T-022-01 | R1, R7 | V-1 |
| T-022-02 | R3, R7 | V-2, V-10 |
| T-022-03 | R3, R10 | V-2, V-7, V-14 |
| T-022-04 | R5 | V-4, V-5 |
| T-022-05 | R2, R6, R8 | V-3, V-8, V-12 |
| T-022-06 | R2 | V-9 |
| T-022-07 | R1, R4 | V-6 |
| T-022-08 | R3, R11 | V-11 |
| T-022-09 | R8, R9, R12 | V-12, V-13 |
| T-022-10 | R12 | V-15, V-16 |---
id: SDD-20260608ADOGHBRIDGE-tasks
type: tasks
status: draft
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Task List: ADO / GitHub Issues Sync Bridge (SDD-022)

- Spec Reference: [`./spec.md`](./spec.md)
- Plan Reference: [`./plan.md`](./plan.md)
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Owner: Principal Software Developer (deferred until CLARIFY closes)

---

> **NOT READY FOR IMPLEMENTATION.**
>
> F-12 pass 1 does not decompose implementation tasks because the owner
> decisions in [`clarify.md`](./clarify.md) are still open. This file is
> a placeholder so the spec directory is complete and schema-lintable.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

**TBD pending CLARIFY close.**

Expected task areas after owner answers:

- Parse `tasks.md` and render deterministic issue payloads.
- Implement confirmed provider(s) with stdlib `urllib.*`.
- Implement confirmed mapping mechanism.
- Implement conflict detection/reporting.
- Implement confirmed auth/env-var validation and secret redaction.
- Add slash prompt wrapper if confirmed.
- Add tests and validation close-out.

## Notes

- No task may add a third-party dependency.
- No task may write into host project application files.
- No task may auto-sync on commit hook, dashboard refresh, or webhook
  unless the owner explicitly rejects the F-12 recommendation.
