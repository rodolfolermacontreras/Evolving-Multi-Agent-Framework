---
name: implement
description: Start implementing a task using the SDD worker and TDD workflow.
---

You are running the **Implement** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 8 - Implement**
- Use for a single, scoped task that is ready for execution.

## Goal
Execute one task in a disciplined worker style, following TDD and project conventions.

## Preconditions
Before implementation, confirm:
- There is a task ID or clearly scoped brief.
- The relevant spec and plan are available when required.
- The assigned worktree or branch context is known.
- A test baseline can be established.

## Required Workflow
1. Restate the task and scope.
2. Identify files in scope and likely tests.
3. Write or update a failing test first.
4. Implement the minimum change to pass the test.
5. Refactor while keeping tests green.
6. Run the broader relevant validation scope.
7. Summarize changes, tests, concerns, and commit status.

## Output Format
```markdown
## Task Summary
- Task ID:
- Goal:
- Files in scope:

## TDD Plan
- Failing test to write:
- Expected failure:
- Implementation target:

## Verification Plan
- Targeted tests:
- Broader tests:
- Stop conditions:

## Final Handoff
- Summary:
- Test results:
- Concerns:
- Commit SHA:
```

## Guardrails
- Do not skip the failing test step.
- Do not expand scope beyond the assigned task.
- If the task is blocked by ambiguity or missing artifacts, say so immediately.
- If the change is trivial bug-fix work under the sizing threshold, say whether a full spec was intentionally skipped.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
