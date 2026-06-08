---
id: SDD-20260608SELFREVIEW-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-end-of-session-self-review
---

# Implementation Plan: End-of-Session Self-Review Loop (SDD-021)

- Feature: SDD-021
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Plan Authors: Principal Architect + Principal Software Developer input
- Date: 2026-06-08
- Baseline: 331 passed, 2 skipped before Sprint 9

---

## Implementation Approach

Implement SDD-021 as a skill-first workflow with explicit promotion boundaries. The first version should be small, portable, and artifact-driven:

1. Add a `session-self-review` operational skill that defines triggers, evidence sources, output record shape, promotion targets, and SDD-023 gate-friction handling.
2. Wire the output to existing lesson and evolution rails by referencing `lesson-capture` and `/evolve`, not by writing agent or skill deltas directly.
3. Add lightweight sprint-close guidance only where the repo already has a stable sprint or review surface.
4. Close validation through schema lint and link/path sanity. Run full pytest only if F-19 touches executable code.

The implementation MUST preserve these architectural constraints:

- No direct self-modification of `.github/agents/**`, `.github/skills/**`, prompts, templates, or constitution files as a side effect of self-review.
- No raw transcript dependency.
- No new third-party dependencies.
- No ledger schema migration without ADR + owner approval.
- SDD-023 remains the source of gate vocabulary.

### Key Design Decisions

1. **Skill-first, not CLI-first**: A skill is the lowest-risk v1 surface because the loop is mostly judgment and routing. CLI automation can come later if repeated use proves a need.
2. **Artifact evidence baseline**: The skill must work from committed artifacts and validation results because raw transcripts may be unavailable or privacy-sensitive.
3. **Proposal-only self-improvement**: Self-review can propose changes, but `/evolve` curates and owners approve governance-impacting changes.
4. **Gate findings use SDD-023**: Approval friction is represented with gate fields rather than free-form prose.

---

## File Scope For F-19

| File | Change Type | Owner | Notes |
|------|-------------|-------|-------|
| `.github/skills/operational/session-self-review/SKILL.md` | Add | Developer | Primary SDD-021 implementation artifact. |
| `.github/skills/operational/lesson-capture/SKILL.md` | Optional extend | Developer | Only if cross-reference wording is needed. |
| `.github/prompts/evolve.prompt.md` | Optional extend | Developer | Only if `/evolve` needs explicit self-review input wording. |
| `spec-driven-development/templates/review.md` or nearest existing review template | Optional extend | Developer | Add self-review summary section only if pattern is stable. |
| `spec-driven-development/sprints/README.md` | Optional extend | Developer | Document sprint-close summary destination if needed. |
| `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md` | Update | SW Dev | Check REQUIRED items only after evidence exists. |
| `spec-driven-development/specs/2026-06-08-end-of-session-self-review/tasks.md` | Update | SW Dev | Mark implementation tasks done during F-19. |

### Files Not Approved In F-17

- `spec-driven-development/constitution/**` -- requires ADR + owner approval if implementation determines wording changes are necessary.
- `spec-driven-development/ledger/**` schema files -- requires ADR + owner approval for migration or incompatible table changes.
- Dependency manifests -- no new dependencies approved.
- External service configuration -- no external write behavior changes approved.
- Generated executive files -- no regeneration required for F-17; F-19 may regenerate only if implementation convention requires it.

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| SDD-023 first-class user gates | Complete F-16, commit `6345366` | Provides gate vocabulary and approval evidence taxonomy. |
| `lesson-capture` skill | Existing | Provides the durable lesson-candidate append path. |
| `/evolve` prompt | Existing | Curates lessons into shipped/deferred/discarded framework changes. |
| Sprint 9 F-18 / SDD-025 | Future | May consume self-review gate-friction outputs for pressure-defense examples. |

---

## Implementation Order

1. **T-021-01**: Create the `session-self-review` skill with valid frontmatter and trigger model.
2. **T-021-02**: Define the self-review record shape, promotion targets, and SDD-023 gate-findings format.
3. **T-021-03**: Document transcript-independent evidence and privacy boundaries.
4. **T-021-04**: Connect durable learning to `lesson-capture`, `/evolve`, and PM triage without direct edits.
5. **T-021-05**: Add sprint-close or retro summary guidance if a stable target file exists.
6. **T-021-06**: Review for approval-required triggers and stop if implementation requires Level-2 approval.
7. **T-021-07**: Run schema lint, optional targeted checks, optional full pytest, and close validation without silent deferral.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Self-review becomes noisy ceremony | Medium | Agents ignore it | Keep the record short; require it only at handoff/close and sprint close. |
| Skill silently edits framework files | Medium | Governance bypass | Explicitly route deltas through lessons, `/evolve`, PM triage, or `/constitution`. |
| Raw transcript access is unavailable | High | Loop cannot run | Make artifact-based evidence mandatory and transcript use optional. |
| Gate friction is described inconsistently | Medium | SDD-023 model fragments | Require gate findings to use SDD-023 fields and evidence taxonomy. |
| Sprint-close guidance duplicates retros | Low | Artifact clutter | Add only a compact summary field or `none`; avoid creating a new retro format. |

---

## Test Strategy

- **Schema lint**: validate new skill frontmatter and modified SDD artifacts.
- **Link/path checks**: verify references to `lesson-capture`, `/evolve`, SDD-023, and sprint lessons are accurate.
- **Sample output review**: confirm the skill includes every required self-review record field.
- **Governance review**: verify no direct durable modifications are made by the self-review loop.
- **Regression tests**: run full pytest if F-19 changes executable code; otherwise record docs/skill-only rationale.

---

## Dispatch Plan For F-19

SDD-021 is small and mostly sequential. Do not split parallel edits across `.github/skills/operational/**` and prompt/template files until the primary skill is drafted.

- Track A: primary `session-self-review` skill.
- Track B: optional `/evolve` or lesson-capture wording after Track A stabilizes.
- Track C: validation closeout and lint.

No fleet dispatch is required unless F-19 combines SDD-021 with SDD-023 and SDD-025 implementation and assigns disjoint file sets.

---

## Approval Gates

- Constitution edit: BLOCKED unless ADR + owner approval exists.
- Ledger schema migration: BLOCKED unless ADR + owner approval exists.
- New dependency: BLOCKED unless Level-2 Friction Analysis + owner approval exists.
- External write behavior change: BLOCKED unless owner approval exists.
- Direct self-review mutation of agent or skill files: BLOCKED; redesign as lesson candidate or `/evolve` curation.
- Push/PI close behavior change: BLOCKED unless owner approval exists.