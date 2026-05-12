---
name: triage
description: Classify incoming work by priority, autonomy, and next SDD phase.
argument-hint: "What idea or backlog item should I triage?"
---

You are running the **Triage** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 1 - Backlog Grooming**
- Supports the flow: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE

## Goal
Take a new request, bug, idea, or improvement and classify it so the Product Manager can decide what happens next.

## Required Outputs
1. Priority: `P1`, `P2`, `P3`, or `P4`
2. Execution flag: `AFK`, `HITL`, or `BLOCKED`
3. Suggested next phase in the SDD workflow
4. Short rationale with explicit assumptions

## Priority Rules
- `P1`: Breaks daily use, blocks critical workflow, or creates meaningful risk.
- `P2`: Important quality or productivity improvement with clear near-term value.
- `P3`: Useful but not urgent quality-of-life or optimization work.
- `P4`: Defer, reject, or park for later.

## Execution Flag Rules
- `AFK`: Can proceed autonomously with enough context.
- `HITL`: Human input is needed for a decision, approval, or ambiguity.
- `BLOCKED`: Cannot proceed because a dependency, gate, or artifact is missing.

## How to Work
1. Restate the incoming request in one sentence.
2. Identify the problem type: feature, bug, tech debt, process change, or research.
3. Note missing information that affects scoping or priority.
4. Assign a priority using the rules above.
5. Assign `AFK`, `HITL`, or `BLOCKED`.
6. Recommend the next SDD phase:
   - Clarify if key decisions are missing.
   - Spec if the request is already clear enough.
   - Plan only if an approved spec already exists.
   - Tasks or Implement only if upstream artifacts exist.
7. If useful, provide 3-5 short grill questions for follow-up.

## Use This Structure
```markdown
## Intake Summary
- Request:
- Category:
- Assumptions:

## Classification
- Priority: P?
- Execution Flag: AFK | HITL | BLOCKED
- Recommended Next Phase:

## Rationale
- Value:
- Risk:
- Urgency:
- Missing context:

## Recommended Follow-Up
1.
2.
3.
```

## Decision Notes
- If the change is a bug fix affecting fewer than 3 files, say that it may bypass a full spec.
- If the request implies a schema change, new dependency, or M365 permission change, mark `HITL` or `BLOCKED`.
- If the request is vague, route to `/grill` or `/clarify`.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
