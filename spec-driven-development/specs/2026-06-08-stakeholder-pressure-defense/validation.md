---
id: SDD-20260608PRESSUREDEFENSE-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-stakeholder-pressure-defense
---

# Validation Contract: Stakeholder-Pressure Defense Pattern (SDD-025)

- Spec ID: SDD-025
- Spec reference: `./spec.md`
- Contract date: 2026-06-08
- Status: **LOCKED at F-18 / TASKS 2026-06-08**
- Rule: zero unchecked REQUIRED items before SDD-025 implementation is considered complete. REQUIRED items cannot be loosened, converted to optional, or silently deferred after lock without an explicit decision recorded here.

---

## Required User Gates Declared By This Spec

SDD-025 uses the SDD-023 gate vocabulary. These gates are implementation-close checks for F-19, not separate F-18 implementation tasks.

| gate_id | gate_type | blocking_scope | approver | evidence_type | evidence_ref | status | next_action |
|---------|-----------|----------------|----------|---------------|--------------|--------|-------------|
| GATE-025-001 | `level-2-decision` | `feature-close` | owner | `owner-quote` | `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md#f-19-validation-evidence` | not-triggered | F-19 implementation introduced no constitution edit, schema migration, dependency, M365 permission change, production-branch impact, external-write behavior change, or irreversible shortcut. |
| GATE-025-002 | `required-validation-exception` | `feature-close` | owner | `owner-quote` | `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md#f-19-validation-evidence` | not-triggered | F-19 closes all REQUIRED SDD-025 items without an exception. |
| GATE-025-003 | `push-approval` | `push` | owner | `owner-quote` | `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md#f-19-validation-evidence` | not-triggered | F-19 does not push or recommend push; F-20 must request explicit owner approval before any push. |

---

## Required Items (locked for F-19)

- [x] V-1. The implementation lists pressure triggers for `speed-over-validation`, `skip-owner-approval`, `scope-reduction-without-traceability`, `push-before-approval`, `unverified-external-claim`, `novelty-or-prestige-pressure`, `external-write-pressure`, and `silent-exception-pressure`, with at least one concrete example for each. Covers R1 / AC-1.
- [x] V-2. Approval-pressure examples reuse SDD-023 fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`. Covers R2 / AC-2.
- [x] V-3. Level-2 or irreversible shortcut examples route to `spec-driven-development/templates/level-2-decision.md` and do not create a competing Level-2 approval template. Covers R3 / AC-3.
- [x] V-4. The implementation includes a routing matrix for EM, PM, Architect, SW Dev, and owner, with handoff criteria tied to the pressured decision surface. Covers R4 / AC-4.
- [x] V-5. The implementation includes copy-ready executive-register response guidance that acknowledges urgency, states the evidence or gate gap, offers options, recommends one path, and avoids obstructive or blame-oriented language. Covers R5 / AC-5.
- [x] V-6. The implementation explicitly rejects green tests, schema-lint success, elapsed time, generated executive surfaces, stakeholder silence, and agent confidence as approval evidence. Covers R2, R6 / AC-6.
- [x] V-7. Scope-reduction examples require traceable spec, plan, tasks, or validation updates before changed scope can be claimed. Covers R7 / AC-7.
- [x] V-8. Validation-exception examples keep REQUIRED items unchecked until owner evidence exists through SDD-023 `required-validation-exception`. Covers R8 / AC-8.
- [x] V-9. Repeated pressure patterns, routing confusion, or pressure-defense misses route through SDD-021 self-review promotion targets and do not silently mutate agents, skills, prompts, templates, or constitution files. Covers R9 / AC-9.
- [x] V-10. F-19 records `GATE-025-001` as approved or not-triggered with evidence before marking SDD-025 DONE. Covers R10 / AC-10.
- [x] V-11. `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation. Covers R11 / AC-11.
- [x] V-12. Full pytest exits 0 with test count at or above the Sprint 9 baseline if F-19 touches executable code; if docs/skill/template-only, F-19 records why full pytest was not required. Covers R10, R11 / AC-12.
- [x] V-13. F-19 records `GATE-025-002` and `GATE-025-003` as approved or not-triggered with evidence before SDD-025/Sprint 9 close or push recommendation claims. Covers R8, R10 / AC-8 / AC-10.

---

## Manual / HITL Checks

- [x] M-1. Owner approval is recorded before any constitution wording change implied by SDD-025 implementation.
- [x] M-2. Owner approval is recorded before any ledger schema migration implied by SDD-025 implementation.
- [x] M-3. Owner approval is recorded before any external write, push-behavior, production-branch, M365 permission, dependency, validation-exception, or irreversible pressure-defense behavior change implied by SDD-025 implementation.

## F-19 Validation Evidence

- Primary implementation artifact: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`.
- Communication wrapper: `spec-driven-development/templates/stakeholder-pressure-response.md`.
- The skill lists every pressure trigger, concrete examples, SDD-023 gate fields, invalid evidence sources, Principal routing, SDD-014 Friction Analysis routing, executive-register response pattern, and SDD-021 self-review promotion targets.
- Gates `GATE-025-001`, `GATE-025-002`, and `GATE-025-003` are not-triggered for F-19 close: F-19 added skill/template guidance only, introduced no Level-2 implementation change, closed all REQUIRED items without exception, did not push, and does not recommend push.
- Verification commands: final schema lint and full pytest evidence recorded in F-19 closeout.

Manual checks are triggering-condition checks. If the trigger never occurs, F-19 records `not-triggered` with evidence from the final diff. If the trigger occurs and approval is missing, F-19 stops as OWNER-ATTENTION.

---

## Optional / Best-Effort Items

- [ ] O-1. Add two worked examples: one validation-pressure response and one model/tool novelty pressure response.
- [ ] O-2. Add a short note to the self-review skill, if implemented in F-19, naming pressure-defense misses as `gate-friction` or `lesson-candidate` inputs.
- [ ] O-3. Add a compact response checklist to the new stakeholder-pressure response template.

---

## Lock Notes

- CLARIFY closed 2026-06-08 after Q-J through Q-M were resolved by PM + Architect defaults.
- F-18 does not check V-1 through V-13 because implementation has not run yet.
- F-19 must not mark SDD-025 DONE unless all REQUIRED V-items are checked or an explicit owner-approved scope change is recorded.
- Generated executive surfaces, green tests, and schema lint are not approval evidence for SDD-023-style gates.
- SDD-014 Friction Analysis remains the required path for Level-2 decisions via `spec-driven-development/templates/level-2-decision.md`.