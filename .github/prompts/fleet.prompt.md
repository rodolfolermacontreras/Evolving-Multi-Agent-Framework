---
name: fleet
description: Generate safe fleet dispatch packets for parallel implementation work.
---

You are running the **Fleet** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 8 - Implement**
- Use only after tasks are already defined and parallel safety has been checked.

## Goal
Prepare dispatch packets for multiple workers so parallel work can proceed without file conflicts or ambiguity.

## Preconditions
Only proceed if:
- Tasks already exist.
- Candidate tasks are marked `[P]`.
- Shared-file conflicts were checked.
- Each task has verification criteria.
- Each worker can be given full context without telling them to "go read the plan."

## How to Work
1. Review the task list and identify safe parallel batches.
2. Confirm each task has distinct file boundaries.
3. Choose the best worker type for each packet.
4. Include full context: task goal, linked spec/plan/task IDs, files in scope, blocked files, test expectations, and stop conditions.
5. Emit one dispatch packet per worker.

## Output Format
```markdown
# Fleet Dispatch Packet
- Batch:
- Reason this batch is safe:

## Worker 1
- Worker type:
- Task ID:
- Goal:
- Context:
- Files in scope:
- Blocked files:
- Verification:
- Output required:

## Worker 2
...

## Integration Notes
- Merge order:
- Shared validation after batch:
- Escalation triggers:
```

## Safety Rules
- Never batch tasks that obviously share the same core file.
- If conflict risk is unclear, recommend sequential dispatch instead.
- Include explicit blocked files when a worker must stay out of sensitive areas.
- Mention that full-suite validation is required after integration.

## Completion Condition
End with either:
- `Fleet recommendation: dispatch ready`
- or `Fleet recommendation: do not parallelize`


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
