---
name: session-self-review
description: "Use when ending a feature session, closing a feature, hitting OWNER-ATTENTION, closing a sprint, detecting process friction, or manually reviewing a session for lessons, gate friction, backlog candidates, or agent/skill deltas. Produces an advisory self-review record and routes durable changes through lesson-capture, /evolve, PM triage, /constitution, or approved implementation tasks."
argument-hint: "Feature or sprint being reviewed, plus optional sanitized notes about friction or evidence."
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Session Self-Review

Run this workflow at the end of meaningful delivery moments so process lessons do not disappear into chat history.

## Triggers

Required triggers:

- `feature-handoff` -- a feature is being handed to another principal, worker, or session.
- `feature-done` -- a feature is ready to be reported DONE.
- `feature-blocked` -- a feature cannot close because a validation, test, gate, or implementation item is blocked.
- `owner-attention` -- the session must stop for human owner input.
- `sprint-close` -- a sprint close or retro is being prepared.

Optional triggers:

- `friction-detected` -- repeated tool failures, unclear instructions, ambiguous ownership, or gate friction appears during work.
- `manual-request` -- the human or a principal explicitly asks for a self-review.

The workflow is advisory. It does not directly modify agents, skills, prompts, templates, docs, constitution files, ledger schema, or external systems.

## Evidence Sources

Use transcript-independent evidence first:

- Committed artifacts: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, `RETRO.md`, sprint notes, and progress blocks.
- Validation results: schema lint, pytest output, targeted command results, and generated-state diffs.
- Git metadata: current branch, changed files, commit SHAs, and explicit diff scope.
- Sanitized session summary: short human-readable notes that omit private or sensitive content.

Raw transcript access is optional enrichment only. Do not require private transcript export, M365 access, WorkIQ access, or external system reads as mandatory evidence. If private context is necessary, summarize it at a safe level or route to the owner.

## Output Record

Produce exactly one compact record with these fields:

```markdown
### Session Self-Review -- {source_feature}

- source_feature: {feature dir, sprint close id, or manual scope}
- trigger: {feature-handoff | feature-done | feature-blocked | owner-attention | sprint-close | friction-detected | manual-request}
- evidence_used: {artifact paths, commands, validation results, git metadata, or sanitized summary}
- friction_observed: {concrete friction or none}
- gate_findings: {SDD-023 gate references or none}
- promotion_target: {no-op | session-note | lesson-candidate | backlog-candidate | gate-friction | agent-skill-delta}
- recommended_owner: {EM | PM | Architect | SW Dev | QA | owner | /evolve}
- next_action: {one concrete action or none}
```

## Gate Findings

When the finding involves missing approval, approval pressure, gate friction, or a blocked transition, cite SDD-023 fields exactly:

- `gate_id`
- `gate_type`
- `blocking_scope`
- `approver`
- `evidence_type`
- `evidence_ref`
- `status`
- `next_action`

Use SDD-023 accepted evidence types: `owner-quote`, `em-synthesis`, `accepted-adr`, `commit-stamp`, `issue-comment`, and `cli-record`.

Do not infer approval from green tests, schema lint, elapsed time, stakeholder silence, generated executive surfaces, task status, or agent confidence.

## Promotion Targets

Use exactly one target:

- `no-op` -- no reusable lesson or action.
- `session-note` -- useful context for handoff or `SESSION-MEMORY.md` only.
- `lesson-candidate` -- reusable framework improvement candidate; route through `lesson-capture`.
- `backlog-candidate` -- product/process work; route to PM triage.
- `gate-friction` -- missing, pressured, or ambiguous approval gate; route to EM and the relevant principal.
- `agent-skill-delta` -- proposed agent, skill, prompt, or template change; route through `/evolve` or an approved implementation task.

Self-review may propose durable changes, but those changes must move through `lesson-capture`, `/evolve`, PM triage, `/constitution`, or an approved implementation task. Do not silently mutate customization files as a side effect of the review.

## Sprint Close Summary

At sprint close, summarize promoted findings or record `none` in the sprint close block or retro. Keep the sprint summary short: source, trigger, promotion target, recommended owner, and next action are enough. Reusable framework changes still route through `lesson-capture` and `/evolve`.

## Example

```markdown
### Session Self-Review -- specs/2026-06-08-first-class-user-gates

- source_feature: specs/2026-06-08-first-class-user-gates
- trigger: feature-done
- evidence_used: validation.md V-1..V-14, schema_lint clean, pytest full suite, git diff --name-only
- friction_observed: gate evidence was scattered before SDD-023 parser support
- gate_findings: GATE-009 push-approval / push / owner / owner-quote / pending / request explicit owner approval before push
- promotion_target: gate-friction
- recommended_owner: EM
- next_action: surface push approval as pending in F-20 close readiness
```

## Guardrails

- Keep the record small enough to paste into a progress block.
- Use committed artifacts before memory or chat history.
- Preserve privacy boundaries; do not export private transcripts.
- Do not edit constitution files without `/constitution` and ADR approval.
- Do not add dependencies, ledger migrations, external writes, or direct self-modification behavior from this skill.
