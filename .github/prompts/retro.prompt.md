---
name: retro
description: Generate a sprint retrospective with evidence, themes, and action items.
---

You are running the **Retro** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 9 - Sprint Review and Retro**
- Use after a sprint, batch, or feature slice completes.

## Goal
Produce a focused retrospective that captures what happened, what mattered, and what should change next.

## Retro Rules
- Prefer evidence over vague sentiment.
- Keep action items to a maximum of three.
- Separate delivery review from process improvement.
- Note carryover work and systemic blockers.

## Areas to Cover
1. What was planned
2. What was delivered
3. What went well
4. What did not go well
5. Risks or blockers that repeated
6. Process changes worth trying next

## Output Format
```markdown
# Sprint Retrospective
- Sprint:
- Goal:
- Outcome:

## Delivered
- ...

## Went Well
- ...

## Did Not Go Well
- ...

## Signals and Evidence
- Velocity:
- Test or quality signals:
- Blockers:

## Action Items
1.
2.
3.
```

## Guardrails
- Avoid blame language.
- Keep the action items specific, owned, and testable.
- If not enough evidence exists, say what data is missing.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
