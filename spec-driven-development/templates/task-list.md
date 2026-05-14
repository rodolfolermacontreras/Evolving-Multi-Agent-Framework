# Task List: {TITLE}

- Spec Reference: {SPEC_REFERENCE}
- Plan Reference: {PLAN_REFERENCE}
- Task ID Format: `T-{spec-date}-{NNN}` (global default)
- Owner: {OWNER}

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

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-{SPEC_DATE}-001 | {TASK_001_DESCRIPTION} | {TASK_001_FILE_SCOPE} | {TASK_001_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |
| T-{SPEC_DATE}-002 | {TASK_002_DESCRIPTION} | {TASK_002_FILE_SCOPE} | {TASK_002_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |
| T-{SPEC_DATE}-003 | {TASK_003_DESCRIPTION} | {TASK_003_FILE_SCOPE} | {TASK_003_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |

## Notes

- Use `Fleet Dispatch Eligible = No` when a task touches shared files, shared templates, shared CSS, or other serialized resources.
- Record blockers inline in the table status column and summarize them during handoff.
