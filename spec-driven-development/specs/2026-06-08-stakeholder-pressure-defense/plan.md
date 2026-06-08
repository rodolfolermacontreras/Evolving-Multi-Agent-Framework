---
id: SDD-20260608PRESSUREDEFENSE-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-stakeholder-pressure-defense
---

# Implementation Plan: Stakeholder-Pressure Defense Pattern (SDD-025)

- Feature: SDD-025
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Plan Authors: Principal Architect + Principal Software Developer input
- Date: 2026-06-08
- Baseline: 331 passed, 2 skipped before Sprint 9

---

## Implementation Approach

Implement SDD-025 as a skill-first pressure-defense workflow with a lightweight response template. The first version should be portable, evidence-driven, and governance-preserving:

1. Add a `stakeholder-pressure-defense` operational skill that detects pressure triggers, classifies the pressured gate or decision surface, routes to the right Principal, and produces an executive-register response.
2. Add `spec-driven-development/templates/stakeholder-pressure-response.md` as a communication wrapper for non-Level-2 or pre-Level-2 responses.
3. Require Level-2 or irreversible shortcut cases to instantiate the existing SDD-014 Friction Analysis brief at `spec-driven-development/templates/level-2-decision.md`.
4. Reference SDD-021 for repeated pressure lessons and SDD-023 for all user-gate fields and approval evidence rules.
5. Close validation through schema lint and link/path sanity. Run full pytest only if F-19 touches executable code.

The implementation MUST preserve these architectural constraints:

- SDD-023 remains the source of gate vocabulary and approval evidence taxonomy.
- SDD-014 remains the source of Level-2 Friction Analysis.
- The new response template is not a Level-2 approval artifact.
- No direct self-modification of agents, skills, prompts, templates, or constitution files as a side effect of pressure defense.
- No new third-party dependencies.
- No ledger schema migration, constitution edit, M365 permission change, production-branch change, push behavior change, or external-write behavior change without owner approval.

### Key Design Decisions

1. **Skill-first, not CLI-first**: Pressure defense is judgment and routing. A skill is the lowest-risk v1 surface.
2. **Both templates, separate authority**: Use the existing `level-2-decision.md` for Level-2 Friction Analysis and a new response template for stakeholder communication.
3. **Executive tone as product requirement**: The playbook must make quality defense sound like delivery risk management, not process obstruction.
4. **Gates as evidence language**: Pressure against approval or validation uses SDD-023 fields instead of free-form gate prose.
5. **Self-review as learning path**: Repeated pressure lessons go through SDD-021 promotion targets, not ad hoc agent edits.

---

## File Scope For F-19

| File | Change Type | Owner | Notes |
|------|-------------|-------|-------|
| `.github/skills/operational/stakeholder-pressure-defense/SKILL.md` | Add | Developer | Primary SDD-025 implementation artifact. |
| `spec-driven-development/templates/stakeholder-pressure-response.md` | Add | Developer | Communication wrapper; must not replace Level-2 brief. |
| `.github/skills/operational/session-self-review/SKILL.md` | Optional extend | Developer | Only if SDD-021 implementation exists first and a small cross-reference is needed. |
| `.github/prompts/evolve.prompt.md` | Optional extend | Developer | Only if `/evolve` needs explicit pressure-defense lesson wording. |
| `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md` | Update | SW Dev | Check REQUIRED items only after evidence exists. |
| `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/tasks.md` | Update | SW Dev | Mark implementation tasks done during F-19. |

### Files Not Approved In F-18

- `spec-driven-development/templates/level-2-decision.md` -- reference only unless owner-approved scope explicitly calls for edit.
- `spec-driven-development/constitution/**` -- requires ADR + owner approval if implementation determines wording changes are necessary.
- `spec-driven-development/ledger/**` schema files -- requires ADR + owner approval for migration or incompatible table changes.
- Dependency manifests -- no new dependencies approved.
- External service configuration -- no external write behavior changes approved.
- Generated executive files -- no regeneration required for F-18; F-19 may regenerate only if implementation convention requires it.

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| SDD-014 Friction Analysis | Shipped PI-4 Sprint 3, commit `85b39be` | Provides mandatory `level-2-decision.md` brief for Level-2 pressure. |
| SDD-023 first-class user gates | Complete F-16, commit `6345366` | Provides gate vocabulary, blocking scopes, status values, evidence taxonomy, and no-silent-approval semantics. |
| SDD-021 self-review loop | Complete F-17, commit `82689d3` | Provides promotion path for repeated pressure lessons and gate-friction findings. |
| SDD-015 model-upgrade discipline | Shipped Sprint 8 | Model/tool novelty pressure must not bypass model-upgrade Friction Analysis and A/B evidence. |
| SDD-022 external issue bridge | Shipped Sprint 8 | External-write pressure must preserve dry-run/apply and token/approval behavior. |

---

## Implementation Order

1. **T-025-01**: Create the `stakeholder-pressure-defense` skill with valid frontmatter and trigger taxonomy.
2. **T-025-02**: Add SDD-023 gate-pressure classification and evidence rejection rules.
3. **T-025-03**: Add SDD-014 Friction Analysis routing for Level-2 and irreversible shortcut pressure.
4. **T-025-04**: Add Principal routing matrix for EM, PM, Architect, SW Dev, and owner.
5. **T-025-05**: Add executive-register response pattern and examples.
6. **T-025-06**: Add SDD-021 self-review promotion guidance for repeated pressure lessons.
7. **T-025-07**: Create the stakeholder-pressure response template and verify it does not replace `level-2-decision.md`.
8. **T-025-08**: Review approval-required triggers, run schema lint, run tests if needed, and close validation without silent deferral.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Response sounds obstructive | Medium | Stakeholders bypass the framework | Require executive-register response pattern with options and recommended next action. |
| New template competes with Level-2 brief | Medium | Governance fragmentation | State that response template is communication-only; Level-2 uses `level-2-decision.md`. |
| Trigger taxonomy grows too broad | Medium | Skill becomes noisy | Anchor triggers to validation, approval, traceability, evidence, and irreversible-change pressure only. |
| Agents infer approval from green tests or silence | Medium | False close/push readiness | Reuse SDD-023 evidence taxonomy and explicitly reject invalid evidence. |
| Repeated pressure lessons stay in chat | Medium | Framework does not improve | Route lessons through SDD-021 self-review promotion targets. |
| Implementation drifts into constitution edits | Low | Level-2 bypass | Block constitution edits unless ADR + owner approval exist. |

---

## Test Strategy

- **Schema lint**: validate new skill frontmatter and modified SDD artifacts.
- **Link/path checks**: verify references to SDD-014 `level-2-decision.md`, SDD-014 example, SDD-023, and SDD-021 are accurate.
- **Content checks**: confirm trigger taxonomy, routing matrix, evidence rejection, Friction Analysis routing, response pattern, and self-review promotion guidance appear in implementation artifacts.
- **Governance review**: verify no Level-2 changes land without owner evidence and no SDD-014 template edit occurs unless explicitly approved.
- **Regression tests**: run full pytest if F-19 changes executable code; otherwise record docs/skill/template-only rationale.

---

## Dispatch Plan For F-19

SDD-025 can be implemented after SDD-023 and SDD-021 implementation surfaces exist or in the same F-19 batch after their primary artifacts are stable. Prefer sequential execution because the skill references both:

- Track A: SDD-023 gate enforcement and SDD-021 self-review skill land first.
- Track B: SDD-025 pressure-defense skill and response template.
- Track C: validation closeout, lint, and optional tests.

Do not dispatch parallel edits to the same skill/template files. Do not edit SDD-014 `level-2-decision.md` without owner-approved scope.

---

## Approval Gates

- Constitution edit: BLOCKED unless ADR + owner approval exists.
- Ledger schema migration: BLOCKED unless ADR + owner approval exists.
- New dependency: BLOCKED unless Level-2 Friction Analysis + owner approval exists.
- External write behavior change: BLOCKED unless owner approval exists.
- Push/PI close behavior change: BLOCKED unless owner approval exists.
- Required validation exception: BLOCKED unless SDD-023 `required-validation-exception` evidence exists.
- SDD-014 template edit: BLOCKED unless explicitly approved; F-19 should reference it, not modify it.