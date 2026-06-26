---
name: stakeholder-pressure-defense
description: "Use when a stakeholder, owner, or agent pressures validation, approval gates, traceability, evidence discipline, push timing, external writes, model/tool novelty, schema/dependency changes, or REQUIRED validation exceptions. Classifies the pressure, cites SDD-023 gate fields, routes Level-2 pressure through SDD-014 Friction Analysis, and drafts an executive-register response."
argument-hint: "Pressure request, affected feature/gate, missing evidence, and urgency."
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Stakeholder Pressure Defense

Use this workflow when a request would weaken validation, approval, traceability, evidence, or irreversible-change discipline. The goal is to preserve delivery speed by naming the fastest compliant path, not to sound obstructive.

## Trigger Taxonomy

| Trigger | Example | Default Route | Required Defense |
|---------|---------|---------------|------------------|
| `speed-over-validation` | "Mark it DONE; we can run tests later." | SW Dev + QA, EM synthesis | Run or record required validation. If an exception is requested, use SDD-023 `required-validation-exception`. |
| `skip-owner-approval` | "Proceed with the Level-2 change; owner approval is obvious." | EM + owner; Architect if Level-2 | Keep the gate pending or blocked until durable approval evidence exists. |
| `scope-reduction-without-traceability` | "Drop that requirement quietly so we can close." | PM + Architect | Update spec, plan, tasks, or validation through the approved lifecycle before claiming changed scope. |
| `push-before-approval` | "Tests passed, push now." | EM + owner + SW Dev | Keep `push-approval`, `sprint-close`, or `pi-close` pending until approval evidence exists. |
| `unverified-external-claim` | "Use this number from memory in the stakeholder response." | EM + PM or Architect | Ask for durable evidence, run the authoritative source, or label the claim unverified. |
| `novelty-or-prestige-pressure` | "Use the new model/tool because it is newer." | Architect + EM; owner if Level-2 | Run SDD-014 Friction Analysis and decide on measurable benefit. |
| `external-write-pressure` | "Write to GitHub/ADO/M365/cloud even though the dry run is missing." | SW Dev + EM + owner if required | Preserve dry-run/apply rules and keep `external-write` pending until evidence exists. |
| `silent-exception-pressure` | "Treat the failing REQUIRED item as not applicable." | EM + owner; Architect for governance | Use SDD-023 `required-validation-exception`; never silently defer or downgrade REQUIRED items. |

## Gate-Pressure Classification

For approval, evidence, or blocked-transition pressure, cite SDD-023 fields exactly:

- `gate_id`
- `gate_type`
- `blocking_scope`
- `approver`
- `evidence_type`
- `evidence_ref`
- `status`
- `next_action`

Use SDD-023 gate types and evidence taxonomy. Accepted evidence types are `owner-quote`, `em-synthesis`, `accepted-adr`, `commit-stamp`, `issue-comment`, and `cli-record`.

Reject green tests, schema-lint success, elapsed time, generated executive surfaces, stakeholder silence, task status, and agent confidence as approval evidence.

Scope-reduction pressure routes to PM + Architect and requires traceable updates to `spec.md`, `plan.md`, `tasks.md`, or `validation.md` before implementation or close claims use the reduced scope.

## Friction Analysis Routing

Level-2 pressure and irreversible shortcut pressure MUST instantiate `spec-driven-development/templates/level-2-decision.md` before implementation proceeds. This includes:

- schema migration pressure
- new dependency pressure
- model/tool/platform novelty with irreversible impact
- production or push behavior changes
- M365 permission changes
- privacy-sensitive logging changes
- external-write behavior changes
- constitution edits
- validation exceptions that require owner approval

The worked example at `spec-driven-development/templates/level-2-decision-EXAMPLE.md` may be cited as guidance. The stakeholder-pressure response template is a communication wrapper only; it does not replace Friction Analysis.

## Principal Routing Matrix

| Pressured Surface | Route | Handoff Criteria |
|-------------------|-------|------------------|
| Stakeholder synthesis, tone, owner approval request | Executive Manager | Human-facing response, escalation, or approval evidence needed. |
| Product scope, requirement removal, sprint commitment | Product Manager | Scope, priority, acceptance criteria, or backlog movement changes. |
| Architecture, constitution, schema, dependency, model/tool platform choice | Architect | Pattern, ADR, Level-2, or irreversible technical decision. |
| Implementation readiness, tests, lint, push readiness, external-write safety | Software Developer | Code, validation, explicit paths, test baseline, or apply/dry-run behavior. |
| Test evidence, validation adequacy, regression risk | QA | Evidence is incomplete or disputed. |
| Level-2 approval, push approval, sprint/PI close approval, validation exception | owner | Human approval is required by SDD-023 or the decision policy. |

Disputed cross-principal decisions and Level-2 decisions route to the owner.

## Executive-Register Response Pattern

Use this response shape:

1. Acknowledge the goal or urgency.
2. Name the blocked transition or decision surface.
3. Name the missing evidence, approval, validation result, or traceability update.
4. Explain the delivery or business risk of proceeding without it.
5. Offer options: fastest compliant path, safer full path, or explicit owner decision path.
6. Recommend one option and state the next action.
7. If Level-2 pressure exists, route to `spec-driven-development/templates/level-2-decision.md` before implementation or irreversible action.

## Copy-Ready Example

```markdown
I understand the urgency to close this today. The blocked surface is `push-approval`: tests and schema lint are green, but SDD-023 does not treat those as owner approval evidence. The risk of pushing now is that we would collapse a human gate into an inferred approval and lose traceability for why the external write was allowed.

Fastest compliant path: record an owner quote or commit-stamped approval for `GATE-009`, then push. Safer full path: complete the Sprint close block first, then request push approval with the final SHA list. I recommend the fastest compliant path if the owner is available now; next action is to request the explicit push approval quote.
```

## Self-Review Promotion

Repeated pressure patterns, routing confusion, or pressure-defense misses should be captured through SDD-021 self-review. Use these promotion targets:

- `gate-friction` for missing approvals, pressured gates, or ambiguous evidence.
- `lesson-candidate` for reusable process guidance.
- `backlog-candidate` for larger product/process work.
- `agent-skill-delta` for proposed agent, skill, prompt, or template updates routed through `/evolve`.

Do not silently mutate agents, skills, prompts, templates, docs, or constitution files from this workflow.

## Guardrails

- Defend quality by explaining delivery risk and options.
- Keep REQUIRED validation items unchecked until evidence exists or owner-approved exception evidence exists.
- Do not edit `spec-driven-development/templates/level-2-decision.md` unless a separate owner-approved task explicitly authorizes it.
- Do not add dependencies, ledger schema migrations, constitution edits, M365 permission changes, production behavior changes, push behavior changes, or external-write behavior changes from this workflow.
