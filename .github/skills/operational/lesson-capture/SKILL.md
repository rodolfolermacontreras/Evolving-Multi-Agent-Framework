---
name: lesson-capture
description: "Use during any phase when something happens that suggests the framework itself should change (skill missing, agent role unclear, template gap, constitution ambiguity). Appends a tagged lesson candidate to the current PI's sprints/PI-{N}/lessons.md."
argument-hint: "What did you observe and what change does it suggest?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Lesson Capture

Capture a framework-evolution candidate immediately when project work reveals a missing skill, unclear role, weak prompt, template gap, documentation issue, or constitution ambiguity.

## When to Use

- During any SDD phase when the framework itself should change.
- When a repeated workaround suggests a reusable skill, prompt, template, or agent update.
- When a constitution rule is ambiguous or missing.
- When waiting for `/retro` would risk losing evidence.

Do not use this for normal feature bugs, product backlog items, or implementation TODOs that do not improve the framework.

## Lesson Tags

Use exactly one tag:

- `skill-update` -- improve an existing skill trigger, protocol, guardrail, or example.
- `new-skill` -- add a reusable skill for repeated behavior.
- `agent-update` -- clarify or change an agent role, responsibility, or handoff boundary.
- `constitution-amendment` -- propose a binding governance, quality, or policy change.
- `template-update` -- change a reusable document template.
- `prompt-update` -- change a slash command prompt or reusable prompt.
- `docs-update` -- clarify README, guide, context, or explanatory documentation.

## Protocol

1. Read `spec-driven-development/constitution/roadmap.md` and identify the current PI.
2. Open `spec-driven-development/sprints/PI-{N}/lessons.md`.
3. If it is missing, create it from `spec-driven-development/sprints/lessons-template.md` and replace `PI-{N}`.
4. Find the highest existing `LESSON-NN` number and increment it by one.
5. Add the new lesson directly under `## Lessons`, most-recent first.
6. Fill every required field. Use `Status: open`.
7. Keep Proposal and Evidence concrete; name affected files explicitly.
8. Save the file and report the lesson ID and path.

## Lesson Format

```markdown
### LESSON-{NN}: {short title}

- Date: YYYY-MM-DD
- Source feature: {feature dir or "general"}
- Tag: {skill-update | new-skill | agent-update | constitution-amendment | template-update | prompt-update | docs-update}
- Proposal: {one paragraph -- what should change in the framework}
- Evidence: {what happened in the project that suggests this change}
- Affects: {explicit file paths -- skills, prompts, agents, templates, constitution articles}
- Estimated effort: S | M | L
- Status: open
- Curator decision: {filled in by /evolve}
- PR / commit: {filled in when shipped}
```

## Example

```markdown
### LESSON-004: Add validation checklist to planning skill

- Date: 2026-05-12
- Source feature: specs/2026-05-12-fleet-ledger
- Tag: skill-update
- Proposal: Update `.github/skills/workflow/to-plan/SKILL.md` so planning agents must list validation commands before implementation tasks are generated.
- Evidence: The implementation plan omitted database migration verification until QA caught it, causing rework.
- Affects: `.github/skills/workflow/to-plan/SKILL.md`, `spec-driven-development/templates/plan-template.md`
- Estimated effort: S
- Status: open
- Curator decision: {filled in by /evolve}
- PR / commit: {filled in when shipped}
```

## Guardrails

- Capture candidates, not final decisions.
- Do not edit affected framework files while capturing the lesson.
- Constitution candidates must later route through `/constitution`; do not directly amend constitution files.
- Every candidate needs provenance: date, source feature, evidence, and affected paths.
