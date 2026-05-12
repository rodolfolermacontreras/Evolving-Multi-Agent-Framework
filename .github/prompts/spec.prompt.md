---
name: spec
description: Generate a feature specification from a clarified request.
---

You are running the **Spec** command for the Day-to-Day Agent SDD workflow.

## Workflow Phase
- Primary phase: **Phase 5 - Specify**
- Input should come from a clarified request, backlog item, or approved feature direction.

## Goal
Produce a feature specification that is clear enough for planning, task decomposition, and later QA.

## Spec Sizing Rules
- Bug fix affecting fewer than 3 files: call out that a full spec may be unnecessary.
- Feature affecting fewer than 5 files: use a lightweight spec.
- Feature affecting 5 or more files, cross-cutting changes, or schema changes: use a full spec.

## Required Sections
Include these sections unless the work is explicitly lightweight:
1. Problem statement
2. Target user
3. Goals
4. Non-goals
5. User stories by priority (`P1`, `P2`, `P3`)
6. Acceptance criteria
7. Functional requirements (`FR-NNN`)
8. Non-functional requirements
9. Edge cases
10. Data, privacy, and dependency considerations
11. Assumptions
12. Success criteria
13. Out of scope
14. Traceability matrix

## How to Work
1. Summarize the feature in one sentence.
2. State what pain point or opportunity it addresses.
3. Convert vague requests into explicit goals and non-goals.
4. Write user stories tied to user value.
5. Write acceptance criteria that can be tested.
6. Make hidden assumptions visible.
7. Call out approval-required items like dependencies, schema changes, or permissions.

## Output Format
```markdown
# <Feature Name>

## Metadata
- Proposed path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/spec.md`
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
    - AC-1.1 ...

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

## Traceability Matrix
| Story | Requirements | Acceptance Criteria |
|-------|--------------|---------------------|
```

## Guardrails
- Do not write implementation tasks here.
- Do not skip acceptance criteria.
- Keep requirements testable and specific.
- If critical ambiguity remains, say `/clarify` must continue before approval.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
