---
name: plan
description: Generate an implementation plan from an approved feature spec.
argument-hint: "Which approved feature spec should I plan?"
---

You are running the **Plan** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 6 - Plan**
- This phase begins after a spec is approved or judged clear enough for planning.

## Goal
Turn a spec into an implementation approach that is detailed enough for task decomposition and review.

## Required Plan Content
Include:
1. Proposed implementation approach
2. Affected files with risk level
3. Files to create
4. Data model or storage changes
5. API or interface contracts
6. Test strategy
7. Migration or rollout steps
8. Risk assessment
9. Estimated effort
10. Open questions or approval gates

## How to Work
1. Read the spec and extract the core user stories and requirements.
2. Identify touched modules, routes, templates, stores, or workflows.
3. Separate low-risk edits from cross-cutting work.
4. Call out any new patterns, schema changes, or dependency proposals.
5. Define how the work will be verified.
6. Keep the plan implementation-focused but not yet task-level.

## Output Format
```markdown
# Implementation Plan
- Proposed path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/plan.md`
- Status: draft for architect and software-dev review

## Summary
...

## Approach
...

## Affected Files
| File | Change Type | Risk | Notes |
|------|-------------|------|-------|

## Files To Create
- ...

## Data Model and Contracts
- ...

## Test Strategy
- Unit:
- Integration:
- Regression:

## Migration or Rollout Steps
1.
2.

## Risks and Mitigations
- ...

## Effort Estimate
- Overall:
- Suggested sequencing:

## Approval Flags
- ...
```

## Guardrails
- Do not decompose into worker tasks yet.
- Plans touching more than 5 files, new patterns, schema changes, or permissions should clearly call for higher scrutiny.
- If the spec is weak, recommend returning to `/clarify` or `/spec` instead of forcing a plan.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
