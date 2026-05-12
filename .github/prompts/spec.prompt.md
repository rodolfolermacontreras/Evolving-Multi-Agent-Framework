---
name: spec
description: Generate a feature specification from a clarified request.
argument-hint: "What feature do you want to spec?"
---

You are running the **Spec** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 5 - Specify**
- Input should come from a clarified request, backlog item, or approved feature direction.

## Goal
Produce a feature specification and validation contract that are clear enough for planning, task decomposition, implementation, and later QA.

## Spec Sizing Rules
- Bug fix affecting fewer than 3 files: call out that a full spec may be unnecessary.
- Feature affecting fewer than 5 files: use a lightweight spec.
- Feature affecting 5 or more files, cross-cutting changes, or schema changes: use a full spec.

## Required Deliverables
The `/spec` command MUST produce or explicitly instruct creation of both files in the same feature directory:
1. `spec.md` using the feature-spec template.
2. `validation.md` using the validation contract template.

The validation contract is part of the spec deliverable, not a post-implementation artifact. It is written during `/spec`, reviewed at the SPEC gate, locked at `/tasks`, and verified at `/qa`.

## Required Sections
Include these sections unless the work is explicitly lightweight:
1. Problem statement
2. Target user
3. Goals
4. Non-goals
5. User stories by priority (`P1`, `P2`, `P3`)
6. Acceptance criteria phrased as testable assertions
7. Functional requirements (`FR-NNN`)
8. Non-functional requirements
9. Edge cases
10. Data, privacy, and dependency considerations
11. Assumptions
12. Success criteria
13. Out of scope
14. Traceability matrix
15. Validation contract reference to sibling `validation.md`

## Validation Contract Requirements
`validation.md` MUST define, before implementation begins:
- Automated tests expected for the feature.
- Specific unit, integration, regression, edge-case, or permission coverage required.
- Manual checks that cannot reasonably be automated.
- Tone or UX checks when user-facing behavior changes.
- A Definition of Done that makes merge readiness explicit.

If no automated test is appropriate, the spec must include a `[NO-TEST-NEEDED]` justification that the spec-compliance reviewer can accept or reject.

## How to Work
1. Summarize the feature in one sentence.
2. State what pain point or opportunity it addresses.
3. Convert vague requests into explicit goals and non-goals.
4. Write user stories tied to user value.
5. Write acceptance criteria as assertions a test can prove true or false.
6. Draft the validation contract alongside the spec.
7. Make hidden assumptions visible.
8. Call out approval-required items like dependencies, schema changes, or permissions.

## Output Format
```markdown
# <Feature Name>

## Metadata
- Proposed path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/spec.md`
- Validation path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/validation.md`
- Spec size: lightweight | full
- Status: draft for review

## Problem Statement
...

## Target User
...

## Goals
- ...

## Non-Goals
- ...

## User Stories
### P1
- US-1: ...
  - Acceptance Criteria:
    - AC-1.1 Given ..., when ..., then ...

## Functional Requirements
- FR-001 MUST ...

## Non-Functional Requirements
- NFR-001 ...

## Edge Cases
- ...

## Data, Privacy, and Dependencies
- ...

## Assumptions
- ...

## Success Criteria
- ...

## Out of Scope
- ...

## Validation Contract
- See sibling `validation.md`; it is part of this spec deliverable and is locked at `/tasks`.

## Traceability Matrix
| Story | Requirements | Acceptance Criteria | Validation Check |
|-------|--------------|---------------------|------------------|
```

Also output or create the sibling `validation.md` with checkbox sections for automated tests, specific required coverage, manual checks, tone/UX checks if applicable, and Definition of Done.

## Guardrails
- Do not write implementation tasks here.
- Do not skip acceptance criteria.
- Keep every acceptance criterion testable and specific.
- Do not treat validation as something to invent after implementation.
- If critical ambiguity remains, say `/clarify` must continue before approval.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
