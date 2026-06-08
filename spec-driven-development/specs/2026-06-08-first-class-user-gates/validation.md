---
id: SDD-20260608USERGATES-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-first-class-user-gates
---

# Validation Contract: First-Class User Gates (SDD-023)

- Spec ID: SDD-023
- Spec reference: `./spec.md`
- Contract date: 2026-06-08
- Status: **LOCKED at F-16 / TASKS 2026-06-08**
- Rule: zero unchecked REQUIRED items before SDD-023 implementation is considered complete. REQUIRED items cannot be loosened, converted to optional, or silently deferred after lock without an explicit decision recorded here.

---

## Required User Gates Declared By This Spec

These are the default user-gate types F-19 must support. They are not separate implementation tasks; they are the gate inventory the implementation must make representable and visible.

| gate_id | gate_type | blocking_scope | approver | evidence_type | evidence_ref | status | next_action |
|---------|-----------|----------------|----------|---------------|--------------|--------|-------------|
| GATE-001 | `clarify-owner-answer` | `clarify-close` | owner or EM with citation | `owner-quote`, `em-synthesis` |  | pending | Record owner answer evidence before CLARIFY close. |
| GATE-002 | `adr-acceptance` | `adr-dependent-edit` | owner for Level-2, Architect for Level-1 | `accepted-adr`, `owner-quote` |  | pending | Record accepted ADR or owner evidence before ADR-dependent edits. |
| GATE-003 | `constitution-edit` | `constitution-edit` | owner | `accepted-adr`, `owner-quote` |  | pending | Record ADR plus owner evidence before constitution edits. |
| GATE-004 | `level-2-decision` | `feature-close` | owner | `owner-quote`, `accepted-adr`, `commit-stamp` |  | pending | Record Level-2 approval evidence before the affected feature close. |
| GATE-005 | `external-write` | `external-write` | owner or delegated operator | `owner-quote`, `issue-comment`, `cli-record` |  | pending | Record approval evidence before external writes. |
| GATE-006 | `model-upgrade` | `model-upgrade` | owner | `owner-quote`, `accepted-adr`, `cli-record` |  | pending | Record model-upgrade approval before model assignment changes. |
| GATE-007 | `required-validation-exception` | `feature-close` | owner | `owner-quote`, `commit-stamp` |  | pending | Keep REQUIRED items unchecked unless owner-approved exception evidence exists. |
| GATE-008 | `sprint-close` | `sprint-close` | owner or delegated EM | `owner-quote`, `em-synthesis`, `commit-stamp` |  | pending | Record sprint close approval before claiming sprint CLOSED. |
| GATE-009 | `push-approval` | `push` | owner | `owner-quote`, `commit-stamp` |  | pending | Record explicit owner approval before push. |
| GATE-010 | `pi-close` | `pi-close` | owner | `owner-quote` |  | pending | Record owner approval before PI close. |

F-19 may mark a gate `not-triggered` only when the feature has no matching approval surface. It must not mark a triggered gate approved without evidence.

---

## Required Items (locked for F-19)

- [x] V-1. The implementation supports every default gate type listed in `Required User Gates Declared By This Spec`. Covers R1 / AC-1.
- [x] V-2. The implementation defines and validates all required gate fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`. Covers R2 / AC-2.
- [x] V-3. The implementation rejects or flags any gate with an evidence type outside `owner-quote`, `em-synthesis`, `accepted-adr`, `commit-stamp`, `issue-comment`, or `cli-record`. Covers R3 / AC-3.
- [x] V-4. The implementation rejects or flags any gate marked `approved` without a non-empty `evidence_ref`. Covers R3 / AC-3 / AC-6.
- [x] V-5. Per-feature gate declarations are read from `validation.md` as the authoritative source; summary/frontmatter, ledger, and dashboard state do not override it. Covers R4 / AC-4.
- [x] V-6. No standalone `gates.md` is required for SDD-023 v1. Covers R5 / AC-4.
- [x] V-7. `exec/state.md`, `exec/state.html`, and `exec/work-index.md` generated output surfaces pending or blocked gates with feature, gate ID, blocking scope, evidence need, and next action. Covers R6 / AC-5.
- [x] V-8. Missing `push-approval`, `sprint-close`, `pi-close`, `constitution-edit`, or `adr-acceptance` evidence blocks the correct downstream transition in implementation or close reporting. Covers R7 / AC-7 / AC-8.
- [x] V-9. REQUIRED validation items that depend on user approval remain unchecked until evidence exists; implementation must not convert them to optional or mark them deferred without explicit recorded approval. Covers R8 / AC-7 / AC-8.
- [x] V-10. Approval evidence is recorded durably through an existing ledger/event path or implementation stops for ADR + owner approval before any ledger schema migration. Covers R9 / AC-9.
- [x] V-11. SDD-021 artifacts can cite this gate vocabulary without redefining incompatible fields. Covers R10 / AC-10.
- [x] V-12. SDD-025 artifacts can cite gate type, blocking scope, missing evidence, and Friction Analysis routing from this model. Covers R11 / AC-10.
- [x] V-13. `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation and includes gate validation coverage or an explicitly documented equivalent validation path. Covers R12 / AC-11.
- [x] V-14. Full pytest suite exits 0 after implementation with test count at or above the Sprint 9 baseline. Covers R13 / AC-12.

---

## Manual / HITL Checks

- [x] M-1. Owner approval is recorded before any constitution wording change implied by SDD-023 implementation.
- [x] M-2. Owner approval is recorded before any ledger schema migration implied by SDD-023 implementation.
- [x] M-3. Owner approval is recorded before any external write, push-behavior, production-branch, M365 permission, or dependency change implied by SDD-023 implementation.

## F-19 Validation Evidence

- Gate parser and lint enforcement landed in `spec-driven-development/cli/schema_lint.py` with targeted tests in `spec-driven-development/cli/test_schema_lint.py`.
- Generated visibility landed in `spec-driven-development/cli/state_builder.py` with targeted tests in `spec-driven-development/cli/test_state_builder.py`.
- Existing ledger evidence path used: `spec-driven-development/ledger/ledger_cli.py record-decision` wrote decision row 2 to `spec-driven-development/ledger/fleet.db`; no schema migration was introduced.
- Manual gates M-1 through M-3 are not-triggered by the final diff: no constitution edit, ledger schema migration, dependency, external-write behavior change, push-behavior change, production-branch change, or M365 permission change landed.
- Verification commands: targeted gate tests passed; final schema lint and full pytest evidence recorded in F-19 closeout.

Manual checks are triggering-condition checks. If the trigger never occurs, F-19 records `not-triggered` with evidence from the final diff. If the trigger occurs and approval is missing, F-19 stops as OWNER-ATTENTION.

---

## Optional / Best-Effort Items

- [ ] O-1. Add a short worked example in a template or docs page showing a `push-approval` gate moving from pending to approved.
- [ ] O-2. Add a compact dashboard badge for "pending user gates" in `state.html` if it fits the existing dashboard layout without visual churn.
- [ ] O-3. Add an informational lint warning for deprecated ad hoc approval wording outside the new gate table format.

---

## Lock Notes

- CLARIFY closed 2026-06-08 after Q-A through Q-E were resolved by PM + Architect defaults.
- F-16 does not check V-1 through V-14 because implementation has not run yet.
- F-19 must not mark SDD-023 DONE unless all REQUIRED V-items are checked or an explicit owner-approved scope change is recorded.
- Generated executive surfaces are not approval evidence.
