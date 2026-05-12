---
name: state
description: Rebuild and summarize the executive state view for the current SDD workflow.
---

You are running the **State** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Can be used at **any phase**.
- This command supports the executive isolation model by producing a concise state summary.

## Goal
Rebuild the equivalent of `spec-driven-development/exec/state.md` as a compact executive snapshot.

## Audience
- Primary audience: Principal Executive Manager and human stakeholders.
- Assume the reader should not need raw artifact details unless they are blockers.

## What to Summarize
1. Current initiative or sprint focus
2. Stage in the SDD workflow
3. Top active work items
4. Material blockers or approval needs
5. Recent progress
6. Next decision or milestone

## Output Format
```markdown
# Executive State
- Date:
- Current phase:
- Overall status: on-track | at-risk | blocked

## Active Focus
- ...

## Progress Since Last Update
- ...

## Blockers and Decisions Needed
- ...

## Next Milestones
- ...

## Notes
- ...
```

## Guardrails
- Keep the summary concise and executive-friendly.
- Do not dump raw task detail unless it is necessary to explain risk.
- Highlight only the most important blockers and approvals.
- If the current state is uncertain, say what artifact is missing.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
