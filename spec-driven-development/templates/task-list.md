# Task List: {TITLE}

- Spec Reference: {SPEC_REFERENCE}
- Plan Reference: {PLAN_REFERENCE}
- Task ID Format: `T-{spec-date}-{NNN}`
- Owner: {OWNER}

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-{SPEC_DATE}-001 | {TASK_001_DESCRIPTION} | {TASK_001_FILE_SCOPE} | {TASK_001_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |
| T-{SPEC_DATE}-002 | {TASK_002_DESCRIPTION} | {TASK_002_FILE_SCOPE} | {TASK_002_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |
| T-{SPEC_DATE}-003 | {TASK_003_DESCRIPTION} | {TASK_003_FILE_SCOPE} | {TASK_003_ACCEPTANCE_TEST} | {S_M_L} | {NONE_OR_TASK_IDS} | {AFK_OR_HITL} | {YES_OR_NO} | pending |

## Notes

- Use `Fleet Dispatch Eligible = No` when a task touches shared files, shared templates, shared CSS, or other serialized resources.
- Record blockers inline in the table status column and summarize them during handoff.
