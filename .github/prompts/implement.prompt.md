---
name: implement
description: Start implementing a task using the SDD worker and TDD workflow.
argument-hint: "Which task should I implement?"
---

You are running the **Implement** command for the SDD workflow.

## Workflow Phase
- Primary phase: **Phase 8 - Implement**
- Use for a single, scoped task that is ready for execution.

## Goal
Execute one task in a disciplined worker style, following TDD, the pre-implementation validation contract, and project conventions.

## Preconditions
Before implementation, confirm:
- There is a task ID or clearly scoped brief.
- The relevant spec and plan are available when required.
- The assigned worktree or branch context is known.
- A test baseline can be established.
- The feature directory contains `validation.md`, unless this is intentionally spec-exempt work under the sizing rule.

## Pre-Execution Validation Gate
Before any implementation begins:
1. Locate the feature directory and verify `validation.md` exists.
2. Verify `validation.md` has at least one checkbox under `## Automated Tests`, or verify the task description is explicitly tagged `[NO-TEST-NEEDED]` with a written justification.
3. If neither condition is true, stop before editing code and report the missing validation contract or missing test justification.
4. Identify which validation checkboxes this task is responsible for satisfying.

## Required Workflow
1. Restate the task and scope.
2. Identify files in scope, likely tests, and relevant validation-contract items.
3. Write or update a failing test first, unless `[NO-TEST-NEEDED]` is justified.
4. Implement the minimum change to pass the test.
5. Refactor while keeping tests green.
6. Run the broader relevant validation scope.
7. Mark relevant validation checkboxes complete only after tests or manual checks pass.
8. Summarize changes, tests, concerns, and commit status.

## Post-Execution Validation Gate
Implementation is not done until one of these is true:
- The relevant validation-contract checkboxes are marked complete and backed by passing test output or confirmed manual checks.
- The task's `[NO-TEST-NEEDED]` justification is documented and accepted by the spec-compliance reviewer.

If production code changed without a corresponding test-file change and no accepted `[NO-TEST-NEEDED]` justification exists, stop and report that the IMPLEMENT gate fails. Apply the `tdd-gate` skill to mechanically check the diff for test-first compliance before declaring the gate passed.

## Output Format
```markdown
## Task Summary
- Task ID:
- Goal:
- Files in scope:

## Validation Contract Gate
- validation.md path:
- Automated test checkbox found: yes | no
- [NO-TEST-NEEDED] justification: n/a | documented | missing
- Validation items owned by this task:

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
- Validation checkboxes completed:
- Concerns:
- Commit SHA:
```

## Guardrails
- Do not skip the failing test step unless `[NO-TEST-NEEDED]` is explicitly justified.
- Do not begin implementation if `validation.md` is missing for spec-governed work.
- Do not expand scope beyond the assigned task.
- If the task is blocked by ambiguity or missing artifacts, say so immediately.
- If the change is trivial bug-fix work under the sizing threshold, say whether a full spec was intentionally skipped.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
