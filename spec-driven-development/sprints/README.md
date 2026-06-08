---
id: SDD-SPRINTS-README-index
type: index
status: active
owner: principal-product-manager
updated: 2026-06-06
---

# Sprints

Per-PI artifacts:

- `sprints/PI-{N}/lessons.md` -- framework-evolution candidates (see `lessons-template.md`)
- `sprints/PI-{N}/sprint-{M}/PLAN.md`, `BOARD.md`, `RETRO.md` -- sprint artifacts
- `sprints/PI-{N}/CURRENT_PI.md` -- optional PI-level context once sprints begin
- Other sprint-local evidence, validation notes, demos, or handoffs as needed

## Lessons loop

The `lessons.md` file is the project-to-framework feedback rail. `/retro` and `/replan` update it after delivery moments, and any agent can use the `lesson-capture` skill during normal work when a framework improvement becomes visible.

Use `lessons-template.md` when starting a new PI:

1. Create `sprints/PI-{N}/lessons.md`.
2. Copy the template content.
3. Replace `PI-{N}` with the PI identifier.
4. Append new lessons as tagged candidates, most-recent first.

Run `/evolve` to curate open candidates into SHIP, DEFER, or DISCARD decisions. `/evolve` drafts framework changes with provenance; it does not auto-commit them.

## Self-review summary

Sprint close and retro artifacts should include a compact self-review summary or explicitly record `none`. Use the `session-self-review` skill at feature handoff, feature DONE, feature BLOCKED, OWNER-ATTENTION, sprint close, or friction-detected moments. Promote reusable findings through `lesson-capture` and `/evolve`; do not silently mutate agents, skills, prompts, templates, or constitution files from a self-review.
