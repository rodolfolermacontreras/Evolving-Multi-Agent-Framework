---
id: SDD-20260608SELFREVIEW-validation
type: validation
status: active
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
| GATE-021-001 | `level-2-decision` | `feature-close` | owner | `owner-quote` |  | pending | F-19 must record `not-triggered` or approved evidence before close if implementation introduces constitution edits, schema migration, new dependencies, M365 permission changes, production-branch impact, or external write behavior changes. |
| GATE-021-002 | `required-validation-exception` | `feature-close` | owner | `owner-quote` |  | pending | F-19 must not close SDD-021 with unchecked REQUIRED items unless owner-approved exception evidence is recorded. |

---

## Required Items (locked for F-19)

- [ ] V-1. The implementation defines the required triggers: feature handoff, feature DONE, feature BLOCKED, OWNER-ATTENTION, sprint close, friction-detected, and manual request. Covers R1 / AC-1.
- [ ] V-2. The implementation defines or emits every required self-review record field: `source_feature`, `trigger`, `evidence_used`, `friction_observed`, `gate_findings`, `promotion_target`, `recommended_owner`, and `next_action`. Covers R2 / AC-2.
- [ ] V-3. The implementation can run without raw transcript access by using committed artifacts, validation results, git metadata, and sanitized summaries. Covers R3 / AC-3.
- [ ] V-4. The implementation explicitly forbids requiring private transcript export, M365/WorkIQ access, or external system reads as mandatory evidence. Covers R4 / AC-4.
- [ ] V-5. Proposed durable changes to agents, skills, prompts, templates, docs, or constitution files route through `lesson-capture`, `/evolve`, PM triage, `/constitution`, or approved implementation tasks. Covers R5 / AC-5.
- [ ] V-6. Gate-related self-review findings use SDD-023 fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`. Covers R6 / AC-6.
- [ ] V-7. The implementation distinguishes `no-op`, `session-note`, `lesson-candidate`, `backlog-candidate`, `gate-friction`, and `agent-skill-delta` outcomes. Covers R7 / AC-7.
- [ ] V-8. Sprint close or retro guidance includes a self-review summary location, or requires an explicit `none` when no findings exist. Covers R8 / AC-8.
- [ ] V-9. SDD-021 validation items remain unchecked until implementation evidence exists; no REQUIRED item is silently deferred or downgraded. Covers R9 / AC-9.
- [ ] V-10. `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation. Covers R9 / AC-10.
- [ ] V-11. Full pytest exits 0 with test count at or above the Sprint 9 baseline if F-19 touches executable code; if docs/skill-only, F-19 records why full pytest was not required. Covers R9 / AC-11.
- [ ] V-12. F-19 records `GATE-021-001` and `GATE-021-002` as approved or not-triggered with evidence before marking SDD-021 DONE. Covers R10 / AC-5.

---

## Manual / HITL Checks

- [ ] M-1. Owner approval is recorded before any constitution wording change implied by SDD-021 implementation.
- [ ] M-2. Owner approval is recorded before any ledger schema migration implied by SDD-021 implementation.
- [ ] M-3. Owner approval is recorded before any external write, push-behavior, production-branch, M365 permission, dependency, or direct agent/skill mutation behavior change implied by SDD-021 implementation.

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