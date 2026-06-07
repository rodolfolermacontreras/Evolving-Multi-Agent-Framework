---
id: SDD-20260607PREP-sprint
type: sprint
status: draft
owner: principal-architect
updated: 2026-06-07
feature: PI-5-sprint-2
---

# Sprint 6 (PI-5 / Sprint 2) -- Prep Notes

> Scaffolded by the Principal Architect on 2026-06-07 inside the Executive
> Manager session. **CLARIFY answers, final spec authoring, and validation
> contract locking happen in the fresh Sprint 6 implementation session per
> Article VII (One Feature, One Session).** Do NOT finalize specs in this
> EM session.

---

## Sprint identity

- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Theme: Anti-Conflict Gates + Carry-Over
- Goal: land the serial CLARIFY/SPEC gate (SDD-019), the cross-feature
  dedup pass (SDD-020), and the host `.gitignore` protection layer
  (SDD-027). P2 housekeeping items (SDD-028, SDD-029) and PI-4 carry-over
  (domain-skill annotations, GH Actions Node.js bump) pulled in only if
  capacity permits.
- Baseline preserved at scaffold time: Sprint 5 close commit `3cb7dea`,
  213 tests, schema_lint clean, master clean.

## Spec directories scaffolded

| Spec ID  | Path                                                                 | CLARIFY Qs | Article-amendment flag                                                                                  |
|----------|----------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------|
| SDD-019  | `specs/2026-06-07-serial-clarify-spec-gate/`                         | **9**      | **CONSTITUTIONAL AMENDMENT CANDIDATE.** ADR required before any `constitution/` edit; ADR drafting BLOCKED until CLARIFY closes. |
| SDD-020  | `specs/2026-06-07-cross-feature-dedup/`                              | **7**      | None.                                                                                                   |
| SDD-027  | `specs/2026-06-07-host-gitignore-protection/`                        | **7**      | **Article X amendment CANDIDATE per owner direction 2026-06-07.** Normal spec first; only escalate if the spec proves the article must change. Friction Analysis NOT required up front. |

Each spec dir contains exactly three files:
- `spec.md` -- Header + Problem Statement + Proposed Solution fully drafted;
  Acceptance Criteria + Out-of-Scope + Traceability Matrix are TODO blocks
  pointing at the relevant CLARIFY questions.
- `clarify.md` -- numbered CLARIFY questions grouped by category (Scope,
  Constraints, Behavior, Edge Cases, Out of Scope) with Architect
  recommended answers but no owner answers.
- `validation.md` -- skeleton with R1..Rn placeholders, all unchecked,
  each tracing to the CLARIFY question(s) that gate it. Contract is NOT
  locked.

## Cross-dependencies

- **SDD-019 <-> SDD-020.** Synergistic. CLARIFY Q5 of SDD-020 explicitly
  forces the integration ordering decision (dedup-first / gate-first /
  independent). This question SHOULD be answered jointly with the
  SDD-019 CLARIFY session to avoid divergent decisions.
- **SDD-019 <-> constitution.** SDD-019 CLARIFY Q5 decides which Article
  is amended (extend Article VII, new Article VIII, or amend
  decision-policy). No `constitution/` edit may happen until an ADR is
  drafted, and ADR drafting is blocked until CLARIFY closes.
- **SDD-027 <-> Article X.** SDD-027 CLARIFY Q1 decides whether Article X
  needs an amendment. Owner direction is "normal spec first; only
  escalate if the spec proves the article must change." Friction
  Analysis NOT required up front.
- **SDD-027 <-> SDD-028 / SDD-029.** SDD-028 and SDD-029 (P2 housekeeping)
  touch the same `bootstrap.py host_link()` code path. Sequencing is the
  PM's call at /plan time; the spec scaffolds do not pre-commit.

## Total CLARIFY load

- 9 + 7 + 7 = **23 CLARIFY questions** to answer in the fresh Sprint 6
  implementation session.
- CURRENT_PI.md flags Sprint 6 as "the highest-CLARIFY-load sprint in
  PI-5"; budget the session accordingly.

## What was NOT done in this EM prep session

- No CLARIFY questions answered.
- No validation contract locked.
- No `constitution/` edit.
- No ADR drafted.
- No `BACKLOG.md` or `CURRENT_PI.md` modification.
- No existing spec dir touched.
- No `cli/` or implementation file modified.

## What MUST happen in the fresh Sprint 6 implementation session

1. Open a NEW Copilot Chat session (Article VII).
2. Re-read this prep note + the three spec dirs.
3. Answer SDD-019 CLARIFY (9 Qs) and SDD-020 CLARIFY (7 Qs) -- joint
   handling recommended for SDD-019 Q5 / SDD-020 Q5 (integration order).
4. Answer SDD-027 CLARIFY (7 Qs) -- Q1 (Article X fit) decides whether
   the spec branches into amendment ceremony.
5. Finalize each spec (Acceptance Criteria + Out-of-Scope + Traceability).
6. Draft ADR(s) for SDD-019 (if amendment confirmed) and SDD-027 (only if
   Q1 confirms amendment is needed).
7. Lock each validation contract at /tasks.
8. Dispatch implementation under Sprint 6.

## Sprint exit conditions (carried from CURRENT_PI.md)

- All P1 items shipped (SDD-019, SDD-020, SDD-027).
- Test suite green; schema_lint clean.
- Constitutional amendments (if any) recorded as ADRs with explicit
  version bumps.
- P2 housekeeping pulled in or explicitly deferred to a later sprint.

---

## Provenance

- Scaffolded: 2026-06-07
- Scaffolder: Principal Architect (in EM session)
- Source signals:
  - Backlog SDD-019, SDD-020, SDD-027 entries (commit `17e7cc0`)
  - Sprint 5 close commit `3cb7dea`
  - Sprint 5 Architect audit 2026-06-07 (YELLOW verdict; SDD-027 follow-up)
  - `sprints/PI-5/CURRENT_PI.md` Sprint 2 section
  - Owner direction 2026-06-07 (via EM) on SDD-027 amendment posture
