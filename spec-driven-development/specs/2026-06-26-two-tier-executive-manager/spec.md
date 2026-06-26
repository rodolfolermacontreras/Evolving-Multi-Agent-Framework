---
id: SDD-20260626TWOTIEREM-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-two-tier-executive-manager
depends_on: [SDD-039]
---

# SPEC: SDD-043 -- Two-tier Executive Manager (Sprint EM agent)

- Feature ID: SDD-043
- Sprint: PI-7 / Sprint 1 (Sprint 14), design slot F-34; implementation F-36
- Status: **active** (design locked; implementation pending in F-36)
- CLARIFY: [`clarify.md`](clarify.md)
- ADR: [`../../docs/ADR/020-two-tier-executive-manager.md`](../../docs/ADR/020-two-tier-executive-manager.md) (Proposed)
- Validation contract: [`validation.md`](validation.md)
- Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)

---

## Problem Statement

A single-sprint working session currently reuses the project Executive Manager identity (`.github/agents/principal-executive-manager.agent.md`), which is built for project-wide awareness across all PIs and sprints. Driving one sprint with a project-wide identity causes (1) scope drift beyond the sprint's own features, (2) authority creep -- nothing stops a single-sprint session from inventing the next sprint/PI or authoring a future kickoff (the Sprint 12 close had to be hand-corrected with "you are not the Highest Executive"), and (3) reliance on per-sprint kickoff prose rather than a durable identity-level constraint. SDD-043 makes the two-tier model first-class by designing a sprint-scoped "Sprint Executive Manager" whose limits live in an agent identity file.

## Goal

Design (not build) a new sprint-scoped **Sprint Executive Manager** agent that:

- Runs exactly ONE sprint and is scoped strictly to that sprint's features.
- Routes feature work to the four Principals (PM, Architect, SW Dev) -- and to workers via SW Dev.
- Reports UP to the project EM at sprint close.
- CANNOT create sprints or PIs and CANNOT author the next kickoff; it may only SUGGEST the next sprint/PI upward.
- Is NOT a human entry point; defers project-wide human Q&A to the project EM (Article II preserved).
- Operates at Level 0 only (routes, summarizes, surfaces; makes no Level 1/2 decisions).

This SPEC fixes the agent's required behavior and content so F-36 can create the file with no further design ambiguity.

## Non-Goals

- Creating the Sprint EM agent file (F-36).
- Editing the kickoff template `_SHARED_ONBOARDING.md` (F-36).
- Any `constitution/**` edit (Q-B finding: not required).
- Changing the project EM identity (`principal-executive-manager.agent.md`) beyond, at most, a one-line cross-reference noting the Sprint EM as a delegated tier (optional, F-36 owner discretion -- see AC-7).
- SDD-044 plain-language comms discipline (paired, separate spec dir).
- Any CLI / code / schema / ledger change.

## Acceptance Criteria

- **AC-1 (agent file exists, identity shape).** F-36 creates exactly one new file under `.github/agents/` for the Sprint Executive Manager, mirroring the structure of `principal-executive-manager.agent.md`: YAML frontmatter with a `description` (required by schema-lint) plus `handoffs` to PM / Architect / SW Dev; then Identity, Default Context Source, Responsibilities, Communication style, "What you do NOT do", Skills loaded, Decision authority, Session start protocol, Error handling.
- **AC-2 (scope lock).** The agent file states, at identity level, that the Sprint EM operates ONLY within its named sprint's features and does not comment on, re-prioritize, or start work outside the sprint.
- **AC-3 (no sprint/PI creation; suggest-only).** The "What you do NOT do" section states the Sprint EM CANNOT create a sprint or PI, CANNOT author the next sprint's kickoff, and CANNOT make PI-level commitments; it may only SUGGEST the next sprint/PI to the project EM as a recommendation.
- **AC-4 (report up at close).** The Responsibilities section states the Sprint EM produces a sprint-close summary and hands UP to the project EM at sprint close; the project EM (with the owner) owns what happens next.
- **AC-5 (not the human entry point; Article II preserved).** The agent file states explicitly that the project EM remains the single human entry point per Article II and that the Sprint EM defers project-wide human Q&A to the project EM.
- **AC-6 (Level 0 authority).** The Decision authority section pins the Sprint EM to Level 0 (route / summarize / surface); it makes no Level 1 or Level 2 decisions and escalates per `decision-policy.md`.
- **AC-7 (forward-only activation).** F-36 adds a Sprint-EM activation block to `_SHARED_ONBOARDING.md` so future sprints run under the Sprint EM; already-shipped `SPRINT-##-KICKOFF.prompt.md` files are NOT retrofitted.
- **AC-8 (plain-language comms loaded).** The agent file loads the `em-communication-discipline` skill as "always active" (it is a human-facing EM); this dovetails with SDD-044, which extends that skill's applicability to all human-facing principals.
- **AC-9 (schema-lint clean).** All SDD-043 design artifacts (this spec dir) and, in F-36, the new agent file pass `python spec-driven-development/cli/schema_lint.py` with exit 0 (agent files require a `description`; skill/agent frontmatter rules unchanged).
- **AC-10 (no regression).** F-36 does not reduce the test count (baseline 481 passed / 2 skipped) and introduces no constitution edit, dependency, schema change, or Article X locked-function edit.

## Affected Modules

| Module / file | Change | When |
|---------------|--------|------|
| `.github/agents/<sprint-executive-manager>.agent.md` | NEW agent identity file (Sprint EM) | F-36 |
| `spec-driven-development/feature-prompts/_SHARED_ONBOARDING.md` | Add forward-only Sprint-EM activation block | F-36 |
| `.github/agents/principal-executive-manager.agent.md` | Optional one-line cross-reference noting the Sprint EM delegated tier | F-36 (owner discretion) |
| `spec-driven-development/docs/ADR/020-two-tier-executive-manager.md` | NEW ADR (Proposed -> Accepted at Sprint 14 close) | F-34 (here) / accept at close |
| `spec-driven-development/specs/2026-06-26-two-tier-executive-manager/*` | Design artifacts | F-34 (here) |

## Data Model Changes

None. No schema, no ledger, no SQLite, no `display-order.json`/audit changes. SDD-043 is governance/identity design and Markdown/agent-file authoring.

## API Changes

None. No CLI surface, no HTTP endpoint, no public function signature changes.

## Test Strategy

- SDD-043 ships agent/governance text, not code; its acceptance is verified by **schema-lint** (the new agent file must carry a valid `description` and pass frontmatter checks) plus **manual review** that AC-2..AC-8 wording is present in the F-36 file.
- No new pytest is required by SDD-043 itself. F-36 MUST keep the full suite at >= 481 passed / 2 skipped and `schema_lint.py` exit 0.
- If F-36 chooses to add a presence test (e.g. a lint assertion that the Sprint EM agent file exists and contains the no-sprint/PI-creation clause), that test is optional and additive; it must not weaken any existing assertion.

## Validation Contract Pointer

The authoritative pass/fail contract for SDD-043 is [`validation.md`](validation.md). It is LOCKED at F-34 and checked off in F-36.

## Traceability Matrix

| Requirement | Source | Acceptance | Validation |
|-------------|--------|------------|------------|
| Sprint-scoped EM under project EM | Q-A, ADR-020 | AC-1, AC-2 | R-1, R-2 |
| No sprint/PI creation; suggest-only | BACKLOG SDD-043, ADR-020 | AC-3 | R-3 |
| Report up at sprint close | Q-A, ADR-020 | AC-4 | R-4 |
| Article II preserved; not human entry point | Q-B finding, ADR-020 | AC-5 | R-5 |
| Level 0 authority | decision-policy.md | AC-6 | R-6 |
| Forward-only kickoff activation | Q-C, ADR-020 | AC-7 | R-7 |
| Plain-language comms skill loaded | SDD-044 link | AC-8 | R-8 |
| Schema-lint clean | Article V / schema_lint | AC-9 | R-9 |
| No regression / no Level-2 trigger | quality-policy, Article X | AC-10 | R-10 |

## Open Questions

- None blocking. Q-A..Q-C answered; Q-B finding = NO constitution edit. ADR-020 Proposed and accepted at the Sprint 14 close gate.

## Out of Scope

- Implementation of the agent file and kickoff-template edit (F-36).
- SDD-044 (separate spec dir) and SDD-045 (F-35).
- Any constitution edit, dependency, schema migration, or Article X locked-function change.
