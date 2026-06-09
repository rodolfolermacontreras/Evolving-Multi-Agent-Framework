---
id: SDD-20260608SELFREVIEW-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-end-of-session-self-review
---

# Validation Contract: End-of-Session Self-Review Loop (SDD-021)

- Spec ID: SDD-021
- Spec reference: `./spec.md`
- Contract date: 2026-06-08
- Status: **LOCKED at F-17 / TASKS 2026-06-08**
- Rule: zero unchecked REQUIRED items before SDD-021 implementation is considered complete. REQUIRED items cannot be loosened, converted to optional, or silently deferred after lock without an explicit decision recorded here.

---

## Required User Gates Declared By This Spec

SDD-021 uses the SDD-023 gate vocabulary. These gates are implementation-close checks for F-19, not separate F-17 implementation tasks.

| gate_id | gate_type | blocking_scope | approver | evidence_type | evidence_ref | status | next_action |
|---------|-----------|----------------|----------|---------------|--------------|--------|-------------|
| GATE-021-001 | `level-2-decision` | `feature-close` | owner | `owner-quote` | `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md#f-19-validation-evidence` | not-triggered | F-19 implementation introduced no constitution edit, schema migration, dependency, M365 permission change, production-branch impact, or external-write behavior change. |
| GATE-021-002 | `required-validation-exception` | `feature-close` | owner | `owner-quote` | `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md#f-19-validation-evidence` | not-triggered | F-19 closes all REQUIRED SDD-021 items without an exception. |

---

## Required Items (locked for F-19)

- [x] V-1. The implementation defines the required triggers: feature handoff, feature DONE, feature BLOCKED, OWNER-ATTENTION, sprint close, friction-detected, and manual request. Covers R1 / AC-1.
- [x] V-2. The implementation defines or emits every required self-review record field: `source_feature`, `trigger`, `evidence_used`, `friction_observed`, `gate_findings`, `promotion_target`, `recommended_owner`, and `next_action`. Covers R2 / AC-2.
- [x] V-3. The implementation can run without raw transcript access by using committed artifacts, validation results, git metadata, and sanitized summaries. Covers R3 / AC-3.
- [x] V-4. The implementation explicitly forbids requiring private transcript export, M365/WorkIQ access, or external system reads as mandatory evidence. Covers R4 / AC-4.
- [x] V-5. Proposed durable changes to agents, skills, prompts, templates, docs, or constitution files route through `lesson-capture`, `/evolve`, PM triage, `/constitution`, or approved implementation tasks. Covers R5 / AC-5.
- [x] V-6. Gate-related self-review findings use SDD-023 fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`. Covers R6 / AC-6.
- [x] V-7. The implementation distinguishes `no-op`, `session-note`, `lesson-candidate`, `backlog-candidate`, `gate-friction`, and `agent-skill-delta` outcomes. Covers R7 / AC-7.
- [x] V-8. Sprint close or retro guidance includes a self-review summary location, or requires an explicit `none` when no findings exist. Covers R8 / AC-8.
- [x] V-9. SDD-021 validation items remain unchecked until implementation evidence exists; no REQUIRED item is silently deferred or downgraded. Covers R9 / AC-9.
- [x] V-10. `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation. Covers R9 / AC-10.
- [x] V-11. Full pytest exits 0 with test count at or above the Sprint 9 baseline if F-19 touches executable code; if docs/skill-only, F-19 records why full pytest was not required. Covers R9 / AC-11.
- [x] V-12. F-19 records `GATE-021-001` and `GATE-021-002` as approved or not-triggered with evidence before marking SDD-021 DONE. Covers R10 / AC-5.

---

## Manual / HITL Checks

- [x] M-1. Owner approval is recorded before any constitution wording change implied by SDD-021 implementation.
- [x] M-2. Owner approval is recorded before any ledger schema migration implied by SDD-021 implementation.
- [x] M-3. Owner approval is recorded before any external write, push-behavior, production-branch, M365 permission, dependency, or direct agent/skill mutation behavior change implied by SDD-021 implementation.

## F-19 Validation Evidence

- Primary implementation artifact: `.github/skills/operational/session-self-review/SKILL.md`.
- Sprint-close destination: `spec-driven-development/sprints/README.md` self-review summary guidance.
- The skill defines all required triggers, record fields, transcript-independent evidence, privacy boundaries, SDD-023 gate fields, promotion targets, and governance routing.
- Gates `GATE-021-001` and `GATE-021-002` are not-triggered: F-19 added an advisory skill and sprint guidance only; it introduced no constitution edit, ledger schema migration, dependency, M365 permission change, production/push/external-write behavior change, direct mutation behavior, or validation exception.
- Verification commands: final schema lint and full pytest evidence recorded in F-19 closeout.

Manual checks are triggering-condition checks. If the trigger never occurs, F-19 records `not-triggered` with evidence from the final diff. If the trigger occurs and approval is missing, F-19 stops as OWNER-ATTENTION.

---

## Optional / Best-Effort Items

- [ ] O-1. Add a copy-ready sample self-review output to the new skill.
- [ ] O-2. Add a short cross-reference from `sprints/README.md` to the self-review loop.
- [ ] O-3. Add `/evolve` wording that names self-review outputs as a first-class curation input.

---

## Lock Notes

- CLARIFY closed 2026-06-08 after Q-F through Q-I were resolved by PM + Architect defaults.
- F-17 does not check V-1 through V-12 because implementation has not run yet.
- F-19 must not mark SDD-021 DONE unless all REQUIRED V-items are checked or an explicit owner-approved scope change is recorded.
- Generated executive surfaces and green tests are not approval evidence for SDD-023-style gates.