---
name: tasks
description: Break an implementation plan into atomic, assignable tasks.
argument-hint: "Which implementation plan should I break into tasks?"
---

You are running the **Tasks** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 7 - Tasks**
- Input should be a concrete implementation plan, not a vague feature description.

## Goal
Convert a plan into small, verifiable tasks that can be assigned to workers or fleet batches.

## Task Rules
- Each task should modify roughly 1-3 files when possible.
- Each task must be atomic and verifiable.
- Use tags:
  - `[P]` parallelizable
  - `[S]` sequential
  - `[AFK]` autonomous
  - `[HITL]` human-needed
  - `[US-N]` user-story traceability
- Shared-file conflicts should force sequential ordering.
- Default batch size should not exceed 4 tasks.

## How to Work
1. Read the plan and list all implementation chunks.
2. Group by dependency, file ownership, and verification scope.
3. Split overly broad work until each task can be owned by one worker.
4. Mark parallel work only when file conflicts are unlikely.
5. Add verification criteria and recommended worker type.
6. Suggest fleet batches where safe.

## Output Format
```markdown
# Task List
- Proposed path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/tasks.md`
- Status: ready for software-dev dispatch

## Batch Overview
| Batch | Tasks | Mode | Notes |
|-------|------|------|-------|

## Tasks
### T1
- Title:
- Tags:
- Recommended worker:
- Files in scope:
- Depends on:
- Description:
- Verification:

### T2
...

## Conflict Notes
- Shared files:
- Sequential requirements:
- Candidate fleet batch:
```

## Guardrails
- Do not assign tasks that are still architecturally ambiguous.
- Do not mark a task `[P]` if it clearly shares core files with another task.
- If the plan is too vague for atomic tasks, send it back to `/plan`.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
