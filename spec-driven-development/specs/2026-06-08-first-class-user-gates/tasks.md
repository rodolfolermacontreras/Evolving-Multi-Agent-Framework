---
id: SDD-20260608USERGATES-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-first-class-user-gates
---

# Task List: First-Class User Gates (SDD-023)

- Spec Reference: `./spec.md`
- Plan Reference: `./plan.md`
- Validation Reference: `./validation.md`
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Owner: Principal Software Developer
- Test baseline: >= 331 passed, 2 skipped
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
| B1 | T-023-01 | Sequential | Lock vocabulary before parser work. |
| B2 | T-023-02 -> T-023-04 | Sequential | Parser and lint share `schema_lint.py`. |
| B3 | T-023-05 | Sequential after B2 | State surfaces depend on parsed gate state. |
| B4 | T-023-06 | HITL-sensitive | Ledger reuse or ADR stop. |
| B5 | T-023-07 -> T-023-08 | Sequential close-out | Validation, tests, cross-feature handoff. |

---

## Task T-023-01: Finalize gate vocabulary reference

**Story**: [R1, R2, R10, R11] Stable vocabulary for Sprint 9 downstream specs
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-first-class-user-gates/spec.md`, `spec-driven-development/specs/2026-06-08-first-class-user-gates/validation.md`
**Files Blocked**: `spec-driven-development/constitution/**`, `spec-driven-development/ledger/**`
**Depends on**: NONE

### Description

Confirm the Gate Vocabulary, Gate Types, Evidence Types, and Required User Gates sections remain internally consistent before implementation edits begin. If F-17 or F-18 needs a field not covered here, route the addition back through Architect before changing implementation.

### Acceptance Criteria

- [ ] Gate Vocabulary table contains all required fields from R2.
- [ ] Required User Gates table contains all default gate types from R1.
- [ ] SDD-021 and SDD-025 handoff note is present in spec and validation.
- [ ] No `gates.md` is introduced.

### Verification

```powershell
Select-String -Path spec-driven-development/specs/2026-06-08-first-class-user-gates/spec.md -Pattern 'Gate Vocabulary|SDD-021|SDD-025'
```

---

## Task T-023-02: Add gate declaration reader

**Story**: [R2, R4, R5] Parse required gates from validation.md
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/schema_lint.py`, `spec-driven-development/cli/test_schema_lint.py`
**Files Blocked**: `spec-driven-development/cli/state_builder.py`, `spec-driven-development/ledger/**`, `spec-driven-development/constitution/**`
**Depends on**: T-023-01

### Description

Add a small parser for the `## Required User Gates Declared By This Spec` table in `validation.md`. The parser should return structured gate rows with fields needed by lint and state generation. Historical specs without the section must remain valid.

### Acceptance Criteria

- [ ] Valid gate table parses into rows with gate ID, type, blocking scope, evidence need, approver, and status.
- [ ] Historical validation files without gate tables still pass schema lint.
- [ ] Parser does not require or create `gates.md`.
- [ ] Tests use temp fixture files and no network.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_schema_lint.py -k "gate" -v --tb=short
```

---

## Task T-023-03: Enforce gate schema and evidence rules

**Story**: [R2, R3, R7, R8, R12] Prevent malformed or falsely approved gates
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Status**: done
**Files**: `spec-driven-development/cli/schema_lint.py`, `spec-driven-development/cli/test_schema_lint.py`
**Files Blocked**: `spec-driven-development/cli/state_builder.py`, `spec-driven-development/constitution/**`
**Depends on**: T-023-02

### Description

Extend linting to validate required fields, allowed gate types, allowed blocking scopes, allowed evidence types, allowed statuses, and the rule that an approved gate requires evidence reference. If the first implementation uses table columns from `validation.md`, document the expected column names in tests.

### Acceptance Criteria

- [ ] Invalid status fails lint.
- [ ] Invalid evidence type fails lint.
- [ ] Approved gate without evidence reference fails lint.
- [ ] Pending or blocked gate with next action appears as valid.
- [ ] Generated dashboard state is not accepted as evidence.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_schema_lint.py -k "gate" -v --tb=short
python spec-driven-development/cli/schema_lint.py
```

---

## Task T-023-04: Preserve validation.md authority and no-gates.md rule

**Story**: [R4, R5] Keep one authoritative per-feature contract
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/cli/test_schema_lint.py`
**Files Blocked**: `spec-driven-development/specs/**/gates.md`
**Depends on**: T-023-03

### Description

Add regression tests or explicit validation checks proving that SDD-023 v1 does not require a standalone `gates.md` and does not allow a generated or summary surface to override the locked `validation.md` gate contract.

### Acceptance Criteria

- [ ] Valid spec dir with only `validation.md` gate section passes.
- [ ] Missing `gates.md` never fails lint.
- [ ] Test names or assertions state that `validation.md` is authoritative.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_schema_lint.py -k "gate" -v --tb=short
```

---

## Task T-023-05: Surface pending gates in generated executive state

**Story**: [R6, R7] Make gates visible before work proceeds
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Status**: done
**Files**: `spec-driven-development/cli/state_builder.py`, `spec-driven-development/cli/test_state_builder.py`, `spec-driven-development/exec/state.md`, `spec-driven-development/exec/state.html`, `spec-driven-development/exec/work-index.md`
**Files Blocked**: `spec-driven-development/constitution/**`
**Depends on**: T-023-04

### Description

Extend state generation so pending and blocked user gates appear in `exec/state.md`, `exec/state.html`, and `exec/work-index.md`. The generated surfaces must name the feature, gate ID, blocking scope, evidence need, and next action. Approved and not-triggered gates may remain in detail or be omitted from top-level blockers.

### Acceptance Criteria

- [ ] `state.md` includes a pending user-gates section when a fixture has pending gates.
- [ ] `state.html` includes pending/blocked gate information without treating it as approval evidence.
- [ ] `work-index.md` lists active feature gates for Principal pre-work checks.
- [ ] Regenerated exec files are committed only after tests and lint pass.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_state_builder.py -k "gate" -v --tb=short
python spec-driven-development/cli/state_builder.py
```

---

## Task T-023-06: Record approval evidence or stop for ledger ADR

**Story**: [R9, R13] Durable approval evidence without quiet schema changes
**Type**: [S] sequential, HITL-sensitive
**Execution**: [HITL] owner/Architect approval required if schema migration is needed
**Size**: M
**Status**: done
**Files**: `spec-driven-development/ledger/**` or existing ledger-event caller files, `spec-driven-development/docs/ADR/**` if needed
**Files Blocked**: `spec-driven-development/constitution/**`
**Depends on**: T-023-05

### Description

Attempt to record user-gate approval evidence through existing ledger/event mechanics. If existing structures can capture event type, feature, gate ID, evidence type, evidence ref, approver, timestamp, and outcome without migration, implement and test that path. If not, stop as OWNER-ATTENTION and draft an ADR for a ledger schema migration before changing schema files.

### Acceptance Criteria

- [ ] Existing ledger/event path records approval evidence, or implementation stops with ADR + owner approval requirement.
- [ ] No ledger schema migration lands without ADR + owner approval.
- [ ] Evidence records are durable and attributable.

### Verification

```powershell
python -m pytest spec-driven-development/ledger spec-driven-development/cli -k "gate" -v --tb=short
```

---

## Task T-023-07: Close validation and regression checks

**Story**: [R8, R12, R13] No silent deferral, no regressions
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-first-class-user-gates/validation.md`, `spec-driven-development/specs/2026-06-08-first-class-user-gates/tasks.md`
**Files Blocked**: NONE
**Depends on**: T-023-06

### Description

Run schema lint and the full pytest suite. Check V-1 through V-14 only when evidence exists. If any REQUIRED item cannot close, stop as OWNER-ATTENTION and leave it unchecked.

### Acceptance Criteria

- [ ] `python spec-driven-development/cli/schema_lint.py` exits 0.
- [ ] `python -m pytest spec-driven-development/ --tb=no -q` exits 0 with >= 331 passed, 2 skipped or better.
- [ ] Every REQUIRED V-item is checked with evidence, or the feature is not marked DONE.
- [ ] No REQUIRED item is silently deferred.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```

---

## Task T-023-08: Cross-feature handoff for SDD-021 and SDD-025

**Story**: [R10, R11] Make Sprint 9 specs reuse the same gate model
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-first-class-user-gates/tasks.md`, future SDD-021/SDD-025 artifacts when their sessions run
**Files Blocked**: NONE
**Depends on**: T-023-07

### Description

Record the handoff rule for F-17 and F-18: SDD-021 and SDD-025 must cite this spec's Gate Vocabulary instead of redefining their own gate fields. SDD-025 should also route Level-2 pressure through the existing Friction Analysis template.

### Acceptance Criteria

- [ ] F-16 final report recommends F-17 cite SDD-023 Gate Vocabulary.
- [ ] SDD-021 and SDD-025 future specs can reuse gate ID, type, blocking scope, evidence type/ref, approver, status, and next action.
- [ ] No incompatible gate vocabulary is introduced in this SDD-023 task list.

### Verification

```powershell
Select-String -Path spec-driven-development/specs/2026-06-08-first-class-user-gates/spec.md -Pattern 'SDD-021|SDD-025|Gate Vocabulary'
```

---

## Traceability Summary

| Task | Requirements | Validation |
|------|--------------|------------|
| T-023-01 | R1, R2, R10, R11 | V-1, V-2, V-11, V-12 |
| T-023-02 | R2, R4, R5 | V-2, V-5, V-6 |
| T-023-03 | R2, R3, R7, R8, R12 | V-2, V-3, V-4, V-8, V-9, V-13 |
| T-023-04 | R4, R5 | V-5, V-6 |
| T-023-05 | R6, R7 | V-7, V-8 |
| T-023-06 | R9, R13 | V-10, M-1, M-2, M-3 |
| T-023-07 | R8, R12, R13 | V-9, V-13, V-14 |
| T-023-08 | R10, R11 | V-11, V-12 |
