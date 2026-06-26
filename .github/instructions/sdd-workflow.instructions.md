---
applyTo: "spec-driven-development/**"
---

When editing files under `spec-driven-development/`, treat this directory as the process and governance layer for the host project's spec-driven development framework.

## Core Purpose
- `spec-driven-development/` owns framework artifacts, not production application code.
- Favor traceability, stable naming, and predictable document structure.
- Keep terminology aligned with the SDD lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE.

## File and Artifact Conventions
- Use kebab-case for feature folders and prompt-facing artifact names.
- Spec folders should follow `YYYY-MM-DD-feature-name`.
- Keep constitution and tracking documents in the expected uppercase styles when already established.
- Do not introduce alternate folder layouts unless the plan explicitly calls for them.

## Workflow Expectations
- Clarification artifacts should capture questions, recommendations, answers, and status.
- Specs should separate goals, non-goals, requirements, acceptance criteria, and traceability.
- Plans should stay implementation-oriented but not task-granular.
- Tasks should be atomic, tagged, and verification-driven.
- Validation and review files should report evidence, not vague impressions.

## Writing Style
- Be precise and operational.
- Prefer checklists, tables, and stable headings when artifacts benefit from scanning.
- Avoid filler prose and avoid speculative implementation detail in upstream artifacts.
- No emojis.

## Governance Rules
- If a change implies a new dependency, schema migration, M365 permission change, or production-branch impact, call it out explicitly as approval-required.
- Preserve historical traceability; mark items complete rather than deleting them.
- Keep cross-references to `.github/copilot-instructions.md`, `docs/PROJECT_STATE.md`, and `docs/GIT_PARALLEL_FRAMEWORK.md` accurate when relevant.

## Quality Bar
- New artifacts should be internally consistent across spec, plan, tasks, and validation language.
- Requirement IDs, task IDs, and status markers should stay stable once introduced.
- If an artifact is too ambiguous to support the next phase, say so and route it back to the appropriate earlier phase.
