---
id: SDD-20260608USERGATES-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-first-class-user-gates
---

# Implementation Plan: First-Class User Gates (SDD-023)

- Feature: SDD-023
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Plan Authors: Principal Architect + Principal Software Developer input
- Date: 2026-06-08
- Baseline: 331 passed, 2 skipped before Sprint 9

---

## Implementation Approach

Implement user gates as a validation-first contract with generated visibility.
The safest sequence is to make the gate declaration parseable, then enforce
schema rules, then surface pending gates, then add evidence recording if the
existing ledger supports it without migration.

The implementation MUST preserve these architectural constraints:

- `validation.md` remains the per-feature authority for required gates.
- Generated executive files are derivative and must not be hand-edited.
- No `gates.md` is required in v1.
- No third-party dependencies are introduced.
- Any constitution edit or ledger schema migration stops for ADR + owner approval.

### Key Design Decisions

1. **Validation-first source of truth**: Gate declarations live in a stable section of `validation.md`. This aligns with Article X and avoids a competing artifact.
2. **Parseable Markdown before new state**: Implement a small parser for the gate table format before touching state generation. If parsing the Markdown table proves brittle, F-19 should stop and route a schema adjustment to Architect rather than inventing hidden state.
3. **Lint as enforcement boundary**: `schema_lint.py` or an equivalent framework-owned validation path checks required fields, status values, evidence taxonomy, and missing evidence references.
4. **Generated executive surfaces**: `state_builder.py` reads gate state and adds pending/blocked gate summaries to `state.md`, `state.html`, and `work-index.md`.
5. **Ledger evidence without migration first**: Reuse existing ledger event capacity if available. If a schema change is needed, stop for ADR + owner approval.

---

## File Scope For F-19

| File | Change Type | Owner | Notes |
|------|-------------|-------|-------|
| `spec-driven-development/cli/schema_lint.py` | Extend | Developer | Gate declaration linting. |
| `spec-driven-development/cli/test_schema_lint.py` | Extend | Developer / QA | Valid and invalid gate fixtures. |
| `spec-driven-development/cli/state_builder.py` | Extend | Developer | Pending gate extraction and rendering. |
| `spec-driven-development/cli/test_state_builder.py` | Extend | Developer / QA | Generated state/work-index tests. |
| `spec-driven-development/templates/feature-spec.md` | Optional extend | Developer | Only if template update is low-risk. |
| `spec-driven-development/templates/validation.md` | Optional extend | Developer | Add gate section only if template exists and pattern is stable. |
| `spec-driven-development/specs/2026-06-08-first-class-user-gates/validation.md` | Update | SW Dev | Check REQUIRED items after evidence exists. |
| `spec-driven-development/specs/2026-06-08-first-class-user-gates/tasks.md` | Update | SW Dev | Mark tasks done during implementation. |
| `spec-driven-development/exec/state.md` | Generated | SW Dev | Regenerate, do not hand-edit. |
| `spec-driven-development/exec/state.html` | Generated | SW Dev | Regenerate, do not hand-edit. |
| `spec-driven-development/exec/work-index.md` | Generated | SW Dev | Regenerate, do not hand-edit. |

### Files Not Approved In F-16

- `spec-driven-development/constitution/**` -- requires ADR + owner approval if implementation determines wording changes are necessary.
- `spec-driven-development/ledger/**` schema files -- requires ADR + owner approval for migration or incompatible table changes.
- Dependency manifests -- no new dependencies approved.
- External service configuration -- no external write behavior changes approved.

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| SDD-FDC-001 frontmatter/data contracts | Shipped | Reuse existing artifact lint discipline. |
| SDD-015 model-upgrade discipline | Shipped Sprint 8 | Gate type `model-upgrade` references its Level-2 route. |
| SDD-022 external issue bridge | Shipped Sprint 8 | Gate type `external-write` must not weaken dry-run/apply behavior. |
| SDD-021 | Future F-17 | Must reference SDD-023 vocabulary. |
| SDD-025 | Future F-18 | Must reference SDD-023 vocabulary and SDD-014 Friction Analysis. |

---

## Implementation Order

1. **T-023-01**: Document final gate vocabulary and examples in the SDD-023 artifacts.
2. **T-023-02**: Add parseable gate declaration reader for the locked `validation.md` table.
3. **T-023-03**: Add lint/validation checks for required fields, status enum, evidence taxonomy, and approved-without-evidence failures.
4. **T-023-04**: Add tests proving no `gates.md` is required and `validation.md` remains authoritative.
5. **T-023-05**: Surface pending/blocked gates in generated executive state and work index.
6. **T-023-06**: Add durable evidence recording through existing ledger/event mechanics, or stop for ADR + owner approval if migration is required.
7. **T-023-07**: Run schema lint, full pytest, and close SDD-023 validation items without silent deferral.
8. **T-023-08**: Provide cross-feature handoff notes for SDD-021 and SDD-025.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Markdown gate table parsing becomes brittle | Medium | False lint failures | Keep the table shape narrow; add fixture tests; route schema changes through Architect. |
| Ledger event recording requires schema migration | Medium | Level-2 stop | Try existing event structures first; stop for ADR + owner approval if incompatible. |
| Dashboard surface becomes noisy | Medium | EM misses critical gates | Show only pending/blocked gates in top summary; approved gates stay in validation/ledger detail. |
| SDD-021/SDD-025 redefine vocabulary | Low | Fragmented process language | Require both later specs to cite SDD-023 Gate Vocabulary. |
| Agents treat generated state as evidence | Medium | False approval | Lint/docs must state generated surfaces are not evidence; tests should cover this if practical. |

---

## Test Strategy

- **Schema tests**: valid required gate table, missing required field, invalid status, invalid evidence type, approved gate missing evidence ref.
- **State-builder tests**: active feature with pending gate appears in `state.md`, `state.html`, and `work-index.md`; approved or not-triggered gates do not create false blockers.
- **Regression tests**: existing schema/frontmatter lint still passes for historical specs that do not yet declare user gates.
- **Governance tests/manual checks**: approval-required implementation paths stop instead of landing constitution or ledger schema changes quietly.

---

## Dispatch Plan For F-19

SDD-023 is mostly sequential because `schema_lint.py` and `state_builder.py` are shared framework surfaces. The only safe parallel split is after the gate parser shape is stable:

- Track A: schema lint and parser tests.
- Track B: state-builder rendering tests using Track A fixtures.
- Track C: documentation/template updates after behavior is validated.

Do not dispatch parallel edits to the same CLI file.

---

## Approval Gates

- Constitution edit: BLOCKED unless ADR + owner approval exists.
- Ledger schema migration: BLOCKED unless ADR + owner approval exists.
- New dependency: BLOCKED unless Level-2 Friction Analysis + owner approval exists.
- External write behavior change: BLOCKED unless owner approval exists.
- Push/PI close behavior change: BLOCKED unless owner approval exists.
