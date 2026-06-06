---
id: SDD-20260516STAT-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-16-state-builder
---

# Task List: state_builder.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-state-builder/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-05-16-state-builder/plan.md`
- Task ID Format: `T-{spec-date}-{NNN}` (global default)
- Owner: Principal Software Developer

---

> **Task ID convention:** Use the global format `T-{spec-date}-{NNN}` when tasks
> may be referenced across features or sprints. Inside a date-prefixed feature
> directory (`specs/YYYY-MM-DD-name/`), local short IDs `T-NNN` are acceptable
> because the directory already carries the date namespace.
> Provenance: LESSON-002, source feature `specs/2026-05-12-fleet-ledger/`.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

> **Cross-reference rule:** In the Acceptance Test column, reference the spec's
> AC identifiers (e.g., "proves AC1, AC3") and the validation contract checkbox
> names rather than restating criteria. This prevents prose duplication.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Write test_state_builder.py first (red). | `cli/test_state_builder.py` | Proves AC1-AC8, AC10 | M | None | AFK | No | done |
| T-002 | [S] | Implement spec pipeline parser (scan specs/ dirs for Status line). | `cli/state_builder.py` | Proves AC4 | S | T-001 | AFK | No | done |
| T-003 | [S] | Implement backlog parser (sprint assignments from BACKLOG.md table). | `cli/state_builder.py` | Proves AC5 | S | T-001 | AFK | No | done |
| T-004 | [S] | Implement roster counter (agents.json + skills.json). | `cli/state_builder.py` | Proves AC6 | S | T-001 | AFK | No | done |
| T-005 | [S] | Implement ledger readers (recently completed + blockers). | `cli/state_builder.py` | Proves AC2, AC3 | S | T-001 | AFK | No | done |
| T-006 | [S] | Implement main builder composing all sections + CLI wiring. | `cli/state_builder.py` | Proves AC1, AC7, AC8, AC9, AC10 | M | T-002, T-003, T-004, T-005 | AFK | No | done |
| T-007 | [S] | Run tests, manual checks, update validation.md checkboxes. | `validation.md`, `cli/state_builder.py` | All validation contract checkboxes | S | T-006 | AFK | No | done |

## Notes

- All tasks are serialized because they build on the same file (`state_builder.py`).
- T-001 intentionally precedes production code to satisfy Article X.
- No HITL needed -- scope was pre-approved during clarification.
