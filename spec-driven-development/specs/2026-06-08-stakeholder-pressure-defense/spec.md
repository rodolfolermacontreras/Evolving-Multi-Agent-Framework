---
id: SDD-20260608PRESSUREDEFENSE-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-stakeholder-pressure-defense
---

# Feature Spec: Stakeholder-Pressure Defense Pattern (SDD-025)

- Date: 2026-06-08
- Author: Principal Architect + Principal Product Manager
- Status: APPROVED FOR PLAN/TASKS
- Priority: P3
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Spec ID: SDD-025

---

## Problem Statement

Stakeholders, owners, or agents can create pressure to move faster than the framework's gates allow. The pressure may be well-intentioned: ship sooner, use the latest model, reduce ceremony, avoid a long explanation, or accept a stakeholder claim at face value. The risk is that agents respond by weakening validation, skipping owner approval, reducing scope without traceability, pushing before approval, or accepting unverified external claims.

SDD-014 already created the Friction Analysis brief for Level-2 decisions, and SDD-023 now defines first-class user gates. The missing piece is an operational playbook that helps the Executive Manager and Principals respond to pressure in a consistent, calm, evidence-based way. The response should defend quality without sounding obstructive and should route high-risk shortcuts through the existing Friction Analysis template instead of inventing exceptions in chat.

## Proposed Solution

Add a stakeholder-pressure defense workflow that agents can invoke when a request pressures validation, approval, traceability, evidence, or irreversible-change rules. The workflow has three outputs:

1. **Classification**: identify the pressure trigger, the gate or requirement affected, the missing evidence, and the correct Principal route.
2. **Response**: produce an executive-register answer that acknowledges urgency, states the blocked transition or evidence gap, gives options, and recommends the fastest compliant path.
3. **Escalation**: for Level-2 pressure or irreversible shortcuts, instantiate the existing SDD-014 Friction Analysis brief at `spec-driven-development/templates/level-2-decision.md`; for repeated pressure lessons, route them through SDD-021 self-review promotion.

The v1 implementation should be skill/template-first. It should not add code, dependencies, or schema unless F-19 explicitly determines automation is necessary and passes the approval gates.

## Pressure Trigger Taxonomy

| Trigger | Definition | Default Route | Required Defense |
|---------|------------|---------------|------------------|
| `speed-over-validation` | Request to mark DONE, merge, close, or hand off without required lint/tests or checked validation evidence. | SW Dev + QA, EM synthesis | Run or record required validation; if exception is requested, use SDD-023 `required-validation-exception`. |
| `skip-owner-approval` | Request to proceed without owner approval for Level-2, push, sprint/PI close, constitution edit, model upgrade, external write, or validation exception. | EM + owner; Architect if Level-2 | Keep gate pending/blocked until evidence exists. |
| `scope-reduction-without-traceability` | Request to drop committed requirement, AC, task, or validation item without artifact update. | PM + Architect | Update spec/plan/tasks/validation through approved path before implementation changes. |
| `push-before-approval` | Request to push or close while `push-approval`, `sprint-close`, or `pi-close` lacks evidence. | EM + owner + SW Dev | Block the downstream transition and request approval evidence. |
| `unverified-external-claim` | Request to use numbers, system state, stakeholder claims, or production impact without durable evidence. | EM + PM or Architect | Ask for evidence, run the authoritative pipeline/source, or mark claim unverified. |
| `novelty-or-prestige-pressure` | Request to adopt a model, tool, cloud path, framework, or agent pattern because it is new or visible rather than proven beneficial. | Architect + EM; owner if Level-2 | Run SDD-014 Friction Analysis and recommend based on measurable benefit. |
| `external-write-pressure` | Request to write to GitHub, ADO, M365, cloud resources, or another external system without dry-run, token, owner, or evidence path. | SW Dev + EM + owner if required | Preserve dry-run/apply rules and keep `external-write` gate pending until evidence exists. |
| `silent-exception-pressure` | Request to treat a failing REQUIRED item as optional, done, or not applicable without approval evidence. | EM + owner; Architect for governance | Use SDD-023 `required-validation-exception` gate; no silent deferral. |

## Gate Vocabulary Reuse

SDD-025 does not define a second approval model. When a pressure case involves approval, evidence, or blocked transition state, it MUST cite the SDD-023 fields:

- `gate_id`
- `gate_type`
- `blocking_scope`
- `approver`
- `evidence_type`
- `evidence_ref`
- `status`
- `next_action`

The workflow MUST use the SDD-023 gate types and evidence taxonomy. Green tests, elapsed time, generated dashboards, agent confidence, or stakeholder silence are not approval evidence.

## Friction Analysis Reuse

Level-2 pressure or irreversible shortcut pressure MUST invoke the SDD-014 Friction Analysis brief at `spec-driven-development/templates/level-2-decision.md`. The response may cite the worked example at `spec-driven-development/templates/level-2-decision-EXAMPLE.md` when explaining how cost, complexity, maintenance, benefit, and alternatives are evaluated.

The stakeholder-pressure response template is a communication wrapper only. It MUST NOT replace the SDD-014 brief for Level-2 decisions.

## Self-Review Reuse

Repeated pressure patterns, unclear routing, or pressure-defense misses SHOULD be captured through the SDD-021 self-review loop. The finding should use SDD-021 promotion targets:

- `gate-friction` for missing approvals, pressured gates, or ambiguous evidence.
- `lesson-candidate` for reusable process guidance.
- `backlog-candidate` for larger product/process work.
- `agent-skill-delta` for proposed changes to agent, skill, prompt, or template behavior, routed through `/evolve` rather than applied silently.

## Executive-Register Response Pattern

Every stakeholder-facing response produced by the workflow MUST use this shape:

1. Acknowledge the stakeholder goal or urgency.
2. Name the blocked transition or decision surface.
3. Name the missing evidence, approval, validation result, or traceability update.
4. Explain the delivery/business risk of proceeding without it.
5. Offer options: fastest compliant path, safer full path, or explicit owner decision path.
6. Recommend one option and state the next action.
7. If Level-2 pressure exists, route to `spec-driven-development/templates/level-2-decision.md` before implementation or irreversible action.

## Requirements

- **R1: Trigger taxonomy.** The workflow MUST identify pressure triggers for speed over validation, skipping owner approval, reducing scope without traceability, pushing before approval, accepting unverified external claims, novelty/prestige-driven change, external-write pressure, and silent REQUIRED exceptions.
- **R2: Gate vocabulary reuse.** Approval-related pressure MUST reuse SDD-023 gate fields, gate types, blocking scopes, evidence taxonomy, missing evidence language, and `next_action` semantics without redefining incompatible fields.
- **R3: Friction Analysis routing.** Level-2 pressure, model/tool/platform novelty pressure with irreversible impact, schema migration pressure, dependency pressure, production/push behavior pressure, M365 permission pressure, privacy-sensitive logging pressure, or external-write behavior pressure MUST route to `spec-driven-development/templates/level-2-decision.md` before implementation proceeds.
- **R4: Principal routing.** The workflow MUST route pressure cases to EM, PM, Architect, SW Dev, or owner based on the decision surface being pressured.
- **R5: Executive tone.** The workflow MUST produce executive-register responses that acknowledge urgency, state evidence gaps, provide options, recommend a path, and avoid obstructive or blame-oriented language.
- **R6: Evidence discipline.** The workflow MUST reject unverified external claims as final evidence until supported by authoritative artifacts, source-system output, owner quote, issue comment, commit stamp, accepted ADR, or another SDD-023 accepted evidence type.
- **R7: Traceable scope changes.** Requests to reduce scope, drop requirements, or bypass acceptance criteria MUST update the appropriate spec, plan, tasks, or validation artifact through the approved lifecycle before implementation claims the changed scope.
- **R8: No silent validation exceptions.** REQUIRED validation failures or missing approval gates MUST remain visible and unchecked until resolved or owner-approved through SDD-023 `required-validation-exception` evidence.
- **R9: Self-review promotion.** Repeated pressure patterns, routing confusion, and pressure-defense misses SHOULD be captured using SDD-021 self-review promotion targets and MUST NOT silently mutate agents, skills, prompts, templates, or constitution files.
- **R10: Implementation boundaries.** F-19 implementation MUST prefer docs/skill/template changes, no new dependencies, no schema migration, no constitution edits, no M365 permission changes, no production-branch impact, and no external write behavior changes unless the appropriate owner/Level-2 approval exists.
- **R11: Validation enforcement.** SDD-025 REQUIRED validation items MUST remain unchecked until implementation evidence exists; schema lint MUST pass after implementation.

## Acceptance Criteria

- **AC-1:** The implemented playbook/skill lists every trigger from R1 and gives at least one concrete example for each.
- **AC-2:** Approval-pressure examples cite SDD-023 fields and do not introduce a conflicting gate schema.
- **AC-3:** Level-2 examples route to `spec-driven-development/templates/level-2-decision.md`; the stakeholder response template does not replace the Level-2 brief.
- **AC-4:** The routing matrix assigns each trigger to EM, PM, Architect, SW Dev, or owner with clear handoff criteria.
- **AC-5:** Copy-ready response guidance follows the Executive-Register Response Pattern and avoids blame, sarcasm, obstruction, or vague process appeals.
- **AC-6:** The workflow rejects tests, silence, dashboards, elapsed time, and agent confidence as approval evidence.
- **AC-7:** Scope-reduction cases require traceable artifact updates before implementation or close claims change.
- **AC-8:** Validation-exception cases preserve unchecked REQUIRED items until owner evidence exists.
- **AC-9:** Repeated pressure lessons route through SDD-021 self-review targets instead of direct self-modification.
- **AC-10:** Implementation adds no new third-party dependencies, schema migration, constitution edit, M365 permission change, production-branch behavior change, or external-write behavior change unless owner-approved evidence is recorded first.
- **AC-11:** `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation.
- **AC-12:** Full pytest suite exits 0 after implementation if executable code changes; docs/skill/template-only implementation may record why full pytest was not required.

## Affected Modules For F-19

| File | Expected Change | Notes |
|------|-----------------|-------|
| `.github/skills/operational/stakeholder-pressure-defense/SKILL.md` | New | Primary workflow surface. Must have valid SKILL.md frontmatter. |
| `spec-driven-development/templates/stakeholder-pressure-response.md` | New | Communication wrapper for non-Level-2 and pre-Level-2 responses. Does not replace `level-2-decision.md`. |
| `.github/skills/operational/session-self-review/SKILL.md` | Optional extend | Only if F-19 needs a short cross-reference from repeated pressure findings to SDD-021. |
| `.github/prompts/evolve.prompt.md` | Optional extend | Only if `/evolve` needs explicit pressure-defense lesson input wording. |
| `spec-driven-development/templates/level-2-decision.md` | Reference only | Do not edit unless owner-approved scope explicitly calls for it. |
| `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md` | Update | Check REQUIRED items only after evidence exists. |
| `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/tasks.md` | Update | Mark implementation tasks done during F-19. |

## Data Model Changes

No data model or ledger schema change is approved by F-18. If F-19 determines that pressure-defense events require new durable ledger fields or tables, implementation MUST stop for ADR + owner approval before changing schema files.

## API / CLI Changes

No CLI change is required by F-18. If F-19 chooses to add CLI support, it MUST be stdlib-only, follow `docs/CLI-PATTERN.md`, and include tests. A CLI addition is optional, not required for SDD-025 v1.

## Test Strategy

- Skill/frontmatter validation: schema lint clean for the new `stakeholder-pressure-defense` skill.
- Template sanity: response template references SDD-023, SDD-014, and SDD-021 accurately.
- Link/path sanity: references to `level-2-decision.md`, `level-2-decision-EXAMPLE.md`, SDD-023, and SDD-021 resolve.
- Contract review: trigger taxonomy, routing matrix, evidence taxonomy, and response pattern appear in the implementation artifact.
- Governance review: no Level-2 changes land without owner evidence.
- Regression: full pytest if executable code or CLI behavior changes; docs/skill/template-only implementation may rely on schema lint plus targeted link/path checks unless F-19 touches code.

## Validation Contract

The binding validation contract lives in `validation.md`. It is locked by this F-18 `/tasks` pass for F-19 implementation. No REQUIRED item may be loosened or silently deferred during implementation.

## Traceability Matrix

| Requirement | Acceptance Criteria | Validation Items | Implementation Tasks |
|-------------|---------------------|------------------|----------------------|
| R1 | AC-1 | V-1 | T-025-01, T-025-02 |
| R2 | AC-2, AC-6 | V-2, V-6 | T-025-02, T-025-03 |
| R3 | AC-3, AC-10 | V-3, V-10 | T-025-03, T-025-07 |
| R4 | AC-4 | V-4 | T-025-04 |
| R5 | AC-5 | V-5 | T-025-05 |
| R6 | AC-6 | V-6 | T-025-03, T-025-05 |
| R7 | AC-7 | V-7 | T-025-02, T-025-04 |
| R8 | AC-8 | V-8 | T-025-03, T-025-07 |
| R9 | AC-9 | V-9 | T-025-06 |
| R10 | AC-10, AC-12 | V-10, V-12 | T-025-07, T-025-08 |
| R11 | AC-11, AC-12 | V-11, V-12 | T-025-08 |

## Open Questions

None for F-18. CLARIFY closed Q-J through Q-M in `clarification-log.md`.

## Out of Scope

- Implementing the pressure-defense skill or template during F-18.
- Editing `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, templates, or CLI files during F-18.
- Editing `constitution/**` during F-18.
- Adding new dependencies.
- Adding a ledger schema migration.
- Changing M365 permissions, production-branch behavior, push behavior, or external-write behavior.
- Replacing or editing the SDD-014 Friction Analysis template.
- Closing Sprint 9 or PI-5.

## Approval-Required Items Before Or During F-19

- Constitution wording changes require ADR + owner approval.
- Ledger schema migration requires ADR + owner approval.
- New dependencies require Level-2 Friction Analysis + owner approval.
- M365 permission changes require owner approval.
- Production-branch or push behavior changes require owner approval.
- External write behavior changes require owner approval.
- Any pressure-defense path that authorizes bypassing REQUIRED validation or user gates requires owner approval through SDD-023 evidence.