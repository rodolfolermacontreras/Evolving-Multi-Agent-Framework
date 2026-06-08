---
id: SDD-20260608USERGATES-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-first-class-user-gates
---

# Feature Spec: First-Class User Gates (SDD-023)

- Date: 2026-06-08
- Author: Principal Architect + Principal Product Manager
- Status: APPROVED FOR PLAN/TASKS
- Priority: P1
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Spec ID: SDD-023

---

## Problem Statement

The framework has several human approval gates, but they are expressed in different places and with different strength. Sprint 7 and Sprint 8 exposed the risk:

1. Owner ratification, ADR acceptance, and pre-push approval were real blockers, but agents had to infer them from prose in sprint prompts, validation notes, and progress blocks.
2. Missing approvals could be mistaken for routine follow-up because no uniform gate object declared what was blocked, who could approve it, and what evidence counted.
3. Executive surfaces could show a sprint as operationally ready while a human gate still blocked push, constitution edits, or close.

SDD-023 makes user gates a first-class framework construct with uniform vocabulary, artifact placement, validation rules, dashboard visibility, and failure semantics. It does not implement code in F-16; it locks the model for F-19.

## Proposed Solution

Define a **User Gate** as a required human approval checkpoint with a stable ID, gate type, blocking scope, accepted evidence type, approver, status, evidence reference, and next action.

The v1 model uses a layered contract:

- `validation.md` is authoritative for per-feature required gates.
- `spec.md` frontmatter gains a compact implementation-time summary for machine discovery.
- The fleet ledger records gate events and approval evidence after F-19 implements event recording.
- `exec/state.md`, `exec/state.html`, and `exec/work-index.md` surface pending and blocked gates as generated read-only state.
- No standalone `gates.md` is introduced in v1.

The model is intentionally reusable by:

- **SDD-021**: end-of-session self-review can emit candidate gate failures or gate-friction lessons using the same gate fields.
- **SDD-025**: stakeholder-pressure defense can say which gate is being pressured, what evidence is missing, and which Friction Analysis or owner decision is required.

## Gate Vocabulary

| Field | Required | Definition |
|-------|----------|------------|
| `gate_id` | Yes | Stable ID using `GATE-###` within a feature, or a framework-level ID for recurring gates. |
| `gate_type` | Yes | Controlled value describing the approval surface. |
| `blocking_scope` | Yes | The downstream transition blocked when the gate is pending. |
| `approver` | Yes | `owner`, `principal-executive-manager`, or named Principal when delegated. Level-2 gates require owner. |
| `evidence_type` | Yes | Controlled value from the accepted evidence taxonomy. |
| `evidence_ref` | Required to close | Path, commit SHA, ADR, issue/PR URL, or ledger event ID proving approval. |
| `status` | Yes | `pending`, `approved`, `blocked`, `not-triggered`, or `superseded`. |
| `next_action` | Required while pending/blocked | Plain operational action needed to close or unblock the gate. |

### Gate Types

| Gate Type | Default Blocking Scope | Default Approver |
|-----------|------------------------|------------------|
| `clarify-owner-answer` | `clarify-close` | owner or EM with cited owner evidence |
| `adr-acceptance` | `adr-dependent-edit` | owner for Level-2, Architect for Level-1 |
| `constitution-edit` | `constitution-edit` | owner |
| `level-2-decision` | `feature-close` or narrower Level-2 action | owner |
| `external-write` | `external-write` | owner or explicitly delegated operator |
| `model-upgrade` | `model-upgrade` | owner |
| `required-validation-exception` | `feature-close` | owner |
| `sprint-close` | `sprint-close` | owner or EM if explicitly delegated |
| `push-approval` | `push` | owner |
| `pi-close` | `pi-close` | owner |

### Evidence Types

Accepted evidence types are:

- `owner-quote`: verbatim owner quote in committed artifact.
- `em-synthesis`: Executive Manager summary that cites the original owner quote, issue comment, or commit evidence.
- `accepted-adr`: ADR status accepted with date and approval evidence.
- `commit-stamp`: committed progress/spec artifact naming approval evidence.
- `issue-comment`: GitHub or ADO issue/PR comment with stable reference.
- `cli-record`: framework CLI gate record with event ID, once F-19 implements it.

Rejected evidence types are: green tests, schema-lint success, elapsed time, agent confidence, silence, generated dashboard state, or task status without cited approval.

## Requirements

- **R1: Gate inventory.** The framework MUST define default required user gates for CLARIFY owner answers, ADR acceptance, constitution edits, Level-2 decisions, external writes, model upgrades, REQUIRED validation exceptions, sprint close, push approval, and PI close.
- **R2: Gate schema.** The framework MUST define the required gate fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`.
- **R3: Approval evidence.** The framework MUST accept only durable, attributable, reviewable evidence types and MUST reject inferred approvals from tests, silence, dashboard generation, or agent confidence.
- **R4: Artifact placement.** `validation.md` MUST be the authoritative per-feature gate contract; spec frontmatter, ledger rows, and executive surfaces MUST be derived or summary surfaces, not conflicting authorities.
- **R5: No v1 `gates.md`.** The framework MUST NOT require a standalone `gates.md` in v1 unless a later ADR or approved spec changes the artifact model.
- **R6: Dashboard surface.** Pending and blocked user gates MUST be surfaced in `exec/state.md`, `exec/state.html`, and `exec/work-index.md` with feature, gate ID, blocking scope, evidence need, and next action.
- **R7: Failure semantics.** A missing REQUIRED user gate MUST block the downstream transition named by its `blocking_scope` and MUST block any feature/sprint/PI close claim that depends on that transition.
- **R8: No silent REQUIRED deferral.** A REQUIRED validation item that depends on user approval MUST remain unchecked until approval evidence exists; it cannot be converted to optional or deferred silently.
- **R9: Ledger evidence path.** F-19 MUST either record approval events in the existing ledger without schema migration or stop for an ADR/owner approval before any ledger schema change.
- **R10: SDD-021 reuse.** SDD-021 self-review artifacts MUST be able to reference the SDD-023 gate vocabulary when reporting missing approvals, gate friction, or proposed process deltas.
- **R11: SDD-025 reuse.** SDD-025 stakeholder-pressure defense MUST be able to reference gate type, blocking scope, missing evidence, and Friction Analysis routing from this model.
- **R12: Validation enforcement.** Schema lint or an equivalent framework-owned validation path MUST detect malformed gate declarations and any REQUIRED gate marked approved without evidence reference.
- **R13: Approval-required changes.** Constitution edits, new dependencies, schema migrations, M365 permission changes, production-branch impact, or external write behavior changes implied by implementation MUST be called out as approval-required before implementation proceeds.

## Acceptance Criteria

- **AC-1:** `validation.md` contains a locked required-gates section with all default gate types from R1 and blocking scopes from R7.
- **AC-2:** F-19 implementation defines a parseable gate schema with every field from R2 and status values limited to `pending`, `approved`, `blocked`, `not-triggered`, and `superseded`.
- **AC-3:** F-19 validation rejects a gate marked `approved` when `evidence_ref` is empty or when `evidence_type` is outside the accepted taxonomy.
- **AC-4:** No SDD-023 implementation path requires `gates.md`; all required per-feature gate declarations remain in `validation.md` or generated/derived surfaces.
- **AC-5:** Generated executive surfaces show pending/blocked gates for active features and explicitly identify what action remains.
- **AC-6:** Generated executive surfaces do not treat dashboard generation as approval evidence.
- **AC-7:** Missing `push-approval` blocks push recommendation even when tests and schema lint are green.
- **AC-8:** Missing `constitution-edit` or `adr-acceptance` blocks the dependent edit and blocks feature DONE if the edit is required.
- **AC-9:** The implementation records or references approval evidence durably; if ledger schema change is required, work stops for ADR + owner approval before the change lands.
- **AC-10:** SDD-021 and SDD-025 specs can cite this spec's Gate Vocabulary section without redefining incompatible fields.
- **AC-11:** `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation.
- **AC-12:** Full pytest suite exits 0 after implementation with test count at or above the Sprint 9 baseline.

## Affected Modules For F-19

| File | Expected Change | Notes |
|------|-----------------|-------|
| `spec-driven-development/cli/schema_lint.py` | Extend validation for gate declarations if implementation uses lint enforcement | Stdlib only; no third-party parser. |
| `spec-driven-development/cli/test_schema_lint.py` | Add malformed/valid gate declaration tests | One test per required validation behavior. |
| `spec-driven-development/cli/state_builder.py` | Surface pending gates in generated executive state | Only after schema is parseable. |
| `spec-driven-development/cli/test_state_builder.py` | Add pending-gate rendering tests | Must not require live external systems. |
| `spec-driven-development/docs/CLI-PATTERN.md` | No change expected | Read if CLI is touched. |
| `spec-driven-development/templates/feature-spec.md` | Optional template update to mention gate summary | Only if F-19 scope permits. |
| `spec-driven-development/templates/validation.md` | Optional template update to include required-gates section | Prefer if template exists and pattern is stable. |
| `spec-driven-development/exec/state.md` | Generated only | Do not hand-edit. |
| `spec-driven-development/exec/state.html` | Generated only | Do not hand-edit. |
| `spec-driven-development/exec/work-index.md` | Generated only | Do not hand-edit. |

## Data Model Changes

No schema migration is approved in F-16. F-19 should first attempt to represent gate events with existing ledger/event structures. If a new ledger table or incompatible schema change is required, F-19 MUST stop for an ADR and explicit owner approval before implementing that change.

## API / CLI Changes

No CLI behavior is implemented in F-16. F-19 may extend existing framework CLIs only with stdlib code and tests. Any new CLI command must follow `docs/CLI-PATTERN.md`.

## Test Strategy

- Unit: schema validation for gate status values, required fields, accepted evidence types, and missing evidence refs.
- Integration: generated state/work-index fixtures with pending, approved, blocked, and not-triggered gates.
- Regression: existing full suite remains green; schema lint remains clean.
- Governance: approval-required changes stop with OWNER-ATTENTION rather than landing quietly.

## Validation Contract

The binding validation contract lives in `validation.md`. It is locked by this F-16 `/tasks` pass for F-19 implementation. No REQUIRED item may be loosened or silently deferred during implementation.

## Traceability Matrix

| Requirement | Acceptance Criteria | Validation Items | Implementation Tasks |
|-------------|---------------------|------------------|----------------------|
| R1 | AC-1 | V-1 | T-023-01, T-023-02 |
| R2 | AC-2 | V-2 | T-023-02, T-023-03 |
| R3 | AC-3, AC-6 | V-3, V-4 | T-023-03 |
| R4 | AC-4 | V-5 | T-023-01, T-023-04 |
| R5 | AC-4 | V-6 | T-023-01, T-023-04 |
| R6 | AC-5 | V-7 | T-023-04, T-023-05 |
| R7 | AC-7, AC-8 | V-8 | T-023-02, T-023-03, T-023-05 |
| R8 | AC-7, AC-8 | V-9 | T-023-03, T-023-07 |
| R9 | AC-9 | V-10 | T-023-06 |
| R10 | AC-10 | V-11 | T-023-01, T-023-08 |
| R11 | AC-10 | V-12 | T-023-01, T-023-08 |
| R12 | AC-11 | V-13 | T-023-03, T-023-07 |
| R13 | AC-9 | V-14 | T-023-06, T-023-07 |

## Open Questions

None for F-16. CLARIFY closed Q-A through Q-E in `clarification-log.md`.

## Out of Scope

- Implementing gate behavior during F-16.
- Editing `constitution/**` during F-16.
- Adding new third-party dependencies.
- Creating `gates.md` in v1.
- Changing GitHub/ADO live-write behavior from SDD-022.
- Closing Sprint 9 or PI-5.
- Rewriting historical validation files to the new gate model; future features adopt it first, with optional backfill only after F-19 validates the shape.

## Approval-Required Items Before Or During F-19

- Constitution wording changes require ADR + owner approval.
- Ledger schema migration requires ADR + owner approval.
- New dependencies require Level-2 Friction Analysis + owner approval.
- M365 permission changes require owner approval.
- Production-branch or push behavior changes require owner approval.
- External write behavior changes require owner approval.
