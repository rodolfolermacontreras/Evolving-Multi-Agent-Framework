---
name: analyze
description: Analyze codebase impact, dependencies, and blast radius for a proposed change.
argument-hint: "What proposed change should I analyze?"
---

You are running the **Analyze** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Supports **Phases 5-7**: Spec, Plan, and Tasks.
- Use when a proposed change needs dependency tracing or consistency checks before implementation.

## Goal
Explain what parts of the codebase, workflow, data model, or UX are likely to be affected by the proposed change.

## Analysis Areas
Review as relevant:
1. Modules and files likely to change
2. Shared helpers and reused patterns
3. Routing and API impact
4. Template, HTMX, CSS, or frontend impact
5. Data storage or schema implications
6. Test surface and regression risk
7. Observability, privacy, or security implications

## How to Work
1. Restate the proposed change.
2. Identify primary modules in scope.
3. Trace secondary dependencies and consumers.
4. Call out hidden coupling or fragile areas.
5. Note what can remain untouched.
6. Recommend whether the change needs a lightweight spec, full spec, ADR, or human escalation.

## Output Format
```markdown
## Impact Summary
- Change:
- Likely size:
- Recommended phase action:

## Primary Areas
- ...

## Secondary Effects
- ...

## Risks
- ...

## Test and Validation Impact
- ...

## Recommendation
- Proceed to /spec | revise scope | escalate
```

## Guardrails
- Be specific; name likely files or modules when possible.
- Distinguish certain impacts from plausible risks.
- If the blast radius is broad or cross-cutting, say so plainly.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
