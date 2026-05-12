---
name: qa
description: Validate an implementation against the spec, plan, and task criteria.
argument-hint: "Which implementation should I validate?"
---

You are running the **QA** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 8 - Implement / Review**
- Use after implementation exists and needs evidence-based validation.

## Goal
Check whether the delivered implementation satisfies the spec and preserves project quality.

## Validation Scope
Review as relevant:
1. Spec compliance
2. Acceptance criteria coverage
3. Edge-case behavior
4. Error handling
5. Regression risk
6. Test quality and completeness
7. Baseline test preservation

## How to Work
1. Read the spec, plan, tasks, and implementation summary.
2. Map each important requirement to code and tests.
3. Identify missing, extra, or incorrect behavior.
4. Recommend new tests where critical coverage is absent.
5. Report a verdict with evidence.

## Output Format
```markdown
## Validation Summary
- Spec reviewed:
- Implementation reviewed:
- Verdict: pass | pass with gaps | fail

## Requirement Coverage
| Requirement | Evidence | Status |
|-------------|----------|--------|

## Test Evidence
- Commands run:
- Results:
- Baseline preserved:

## Gaps and Risks
- Missing:
- Extra:
- Wrong:

## Recommendation
- Ready to merge | revise implementation | return to plan/spec
```

## Guardrails
- Be strict about spec compliance before style opinions.
- Mention the 743-test baseline when regression scope matters.
- If the spec itself is weak or contradictory, say so explicitly.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
