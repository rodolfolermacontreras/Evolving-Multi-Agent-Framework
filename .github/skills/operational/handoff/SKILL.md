---
name: handoff
description: "Use when ending a session that another session (or agent) will pick up. Compacts the current conversation into a short handoff document referencing artifacts by path. Critical between SDD lifecycle phases (e.g. /grill -> /spec, /spec -> /plan)."
argument-hint: "What will the next session be used for?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Handoff

Compact the current conversation into a short handoff document so a fresh agent can continue without replaying the whole session.
## Canonical Instruction
Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to a path produced by `mktemp -t handoff-XXXXXX.md` (or on Windows, `New-TemporaryFile`).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.
## When to Use
- Ending a session another session or agent will pick up.
- Pausing mid-feature, mid-review, or mid-fleet integration.
- Crossing SDD phases such as `/grill` -> `/spec`, `/spec` -> `/plan`, `/plan` -> `/tasks`, or `/implement` -> `/qa`.
## SDD Additions
For lifecycle handoffs, include:
- Feature directory: `specs/YYYY-MM-DD-feature-name/`
- Key artifacts by path: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, `clarification-log.md`, optional `research.md`
- Next agent role and recommended skills
- First concrete next action

## Process
1. Identify the next session purpose.
2. Reference durable artifacts by path or URL; do not paste their content.
3. Capture only decisions, blockers, assumptions, and unresolved questions not already stored elsewhere.
4. Name the next role and suggested skills.
5. Write a one-page handoff and report the file path.

## Example
```markdown
# Handoff: 2026-05-12 payment-retry spec

## Next Session Purpose
Move from `/grill` to `/spec` for payment retry.

## Current State
- Feature directory: `specs/2026-05-12-payment-retry/`
- Clarification log: `specs/2026-05-12-payment-retry/clarification-log.md`
- Raw idea: `spec-driven-development/backlog/IDEAS.md#payment-retry`
- No `spec.md` exists yet.

## Context Not Captured Elsewhere
- Human rejected charging cards more than once per order.
- Retry limit and alerting owner remain unresolved.

## Next Agent and Skills
- Role: Principal Architect
- Skills: `sdd-constitution`, `project-context`, `to-spec`

## First Action
Draft `spec.md` and mark retry limit as a required assumption if still unanswered.
```

## Guardrails
- Keep it short; one page is the default.
- Do not invent decisions or mark unresolved questions as resolved.
- Do not update constitution, roadmap, or ADRs unless explicitly asked.
- For fleet handoffs, include branch/worktree and commit SHAs if available.
