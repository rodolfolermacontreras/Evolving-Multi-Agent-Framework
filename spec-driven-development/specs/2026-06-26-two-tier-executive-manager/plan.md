---
id: SDD-20260626TWOTIEREM-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-two-tier-executive-manager
---

# PLAN: SDD-043 -- Two-tier Executive Manager (Sprint EM agent)

- Feature ID: SDD-043
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Validation: [`validation.md`](validation.md)
- ADR: [`../../docs/ADR/020-two-tier-executive-manager.md`](../../docs/ADR/020-two-tier-executive-manager.md)
- Implementation slot: **F-36** (this PLAN is authored in F-34, design-only)

---

## Approach

SDD-043 is a governance/identity change with no code. The implementation (F-36) is three text edits and an ADR acceptance:

1. **Author the Sprint EM agent file** by mirroring `principal-executive-manager.agent.md` and overriding the scope/authority sections to encode the sprint-scoped constraints (Q-A, AC-1..AC-6, AC-8).
2. **Add a forward-only activation block** to `_SHARED_ONBOARDING.md` so future sprints run under the Sprint EM (Q-C, AC-7).
3. **Accept ADR-020** at the Sprint 14 close gate with recorded owner ratification (normal Level-1 ADR lifecycle; not a Level-2 constitution edit).

No constitution edit (Q-B finding: NO). No CLI/schema/ledger change. No Article X locked-function edit.

## Source identity to mirror

The new file copies the section skeleton of `.github/agents/principal-executive-manager.agent.md`:

- YAML frontmatter: `description` (required by schema-lint) + `handoffs` to PM / Architect / SW Dev.
- Identity (Role / Scope = one sprint / Authority = Level 0 / Communication style).
- Default Context Source (the active sprint's spec dir + `exec/sprint-progress.md` tail, scoped to the sprint; NOT the project-wide `exec/state.md` as primary).
- Responsibilities: sprint kickoff intake, route feature work to PM/Architect/SW Dev, sprint status within scope, sprint-close summary + report-up, escalation to the project EM.
- Communication style: Do / Do not / Tone (loads `em-communication-discipline`, always active).
- "What you do NOT do": the exhaustive negative list, including the no-sprint/PI-creation + suggest-only + not-the-human-entry-point clauses.
- Skills loaded; Decision authority (Level 0); Session start protocol; Error handling.

## Phasing

- **Phase 1 (F-34, here):** CLARIFY + ADR-020 + SPEC + PLAN + TASKS + validation contract. No code, no agent file, no kickoff edit, no commit, no push.
- **Phase 2 (F-36):** create the agent file; edit `_SHARED_ONBOARDING.md`; (optional) one-line cross-reference in the project EM file; run schema-lint + full pytest; accept ADR-020 with owner ratification at close.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Shared "Executive Manager" name reads as conflicting with Article II | Agent file + ADR-020 state explicitly that the project EM is the single human entry point; Sprint EM is delegated/sprint-scoped (Q-B finding). |
| Activation block accidentally retrofits shipped kickoffs | Edit only `_SHARED_ONBOARDING.md`; forward-only; do not touch existing `SPRINT-##-KICKOFF.prompt.md` files (AC-7). |
| New agent file fails schema-lint | Agent frontmatter must include `description`; verify with `schema_lint.py` in F-36 (AC-9). |
| Scope creep into SDD-044 | SDD-044 is a separate spec dir; SDD-043 only *loads* the comms skill (AC-8), it does not edit the skill body. |

## Dependencies

- **ADR-020** must be Proposed (done in F-34) and Accepted at the Sprint 14 close gate before SDD-043 is marked DONE in BACKLOG.
- **depends_on: SDD-039** -- the Article VII context-isolation wording (ADR-018) is the precedent for how the Sprint EM runs in an isolated sprint session and for the `_SHARED_ONBOARDING.md` shared-template pattern this PLAN reuses.
- No external/library dependency. stdlib-only constraint is trivially satisfied (no code).

## Definition of Done (design, F-34)

- ADR-020 authored (Proposed); CLARIFY done; SPEC/PLAN/TASKS/validation authored and `status: active`.
- `schema_lint.py` exit 0; pytest unchanged at 481 passed / 2 skipped (docs-only).
- F-36 implementation tasks enumerated in [`tasks.md`](tasks.md).
