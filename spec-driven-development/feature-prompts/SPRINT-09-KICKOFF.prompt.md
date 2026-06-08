# SPRINT 9 KICKOFF -- PI-5 Sprint 5 / Self-Review + Uniform Gates + Stakeholder Defense

You are leading **Sprint 9**, which is **PI-5 Sprint 5**. This is the final
planned sprint of PI-5. Your job is to ship **SDD-021** (end-of-session
self-review loop), **SDD-023** (first-class user gates as a uniform construct),
and **SDD-025** (stakeholder-pressure defense pattern invoking the Friction
Analysis template). Do not close PI-5 until all Sprint 9 close criteria pass and
the owner explicitly approves the PI close.

You are the **Principal Executive Manager** for this kickoff. PM + Architect own
CLARIFY/SPEC/PLAN for SDD-021, SDD-023, and SDD-025. The Principal Software
Developer owns task decomposition, implementation dispatch, QA, sprint close,
and PI-5 close readiness reporting.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 9 must not start until all seven checks are true:

1. **Sprint 8 is locally closed** in
   [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md) as
   `CLOSED 2026-06-08`, and PI-5 remains ACTIVE with one sprint remaining.
2. **Sprint 8 close block is present** in
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) with SDD-022
   16/16 REQUIRED, SDD-015 12/12 REQUIRED, and owner approval status recorded
   as REQUIRED BEFORE PUSH / pending unless already ratified.
3. **Sprint 8 close commit exists locally** and includes only explicit F-15
   close paths. Confirm unrelated SDD-035/Azure/workflow dirty work was not
   staged into the Sprint 8 close.
4. **Owner has explicitly approved any push of Sprint 8 close commits** before
   anyone pushes to `origin/master`. If approval is still pending, Sprint 9 can
   be designed locally only if the owner explicitly permits that sequencing;
   otherwise STOP and request the pre-push approval first.
5. **Tests are green at the Sprint 8 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   331 passed with the known 2 platform-conditional skips.
6. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
7. **BACKLOG entries are present and correct**: SDD-021 and SDD-023 allocated to
   PI-5 Sprint 5, SDD-025 allocated to PI-5 Sprint 5, SDD-034 carried forward,
   and PI-4 carry-over housekeeping remains explicitly carried forward unless it
   was actually completed.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 9 on an
unapproved Sprint 8 push, a red test baseline, or a false Sprint 8 close.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 9 in isolated feature sessions or subagent dispatches that
   preserve Article VII's context-isolation property. Do not ask the owner to
   manually open new sessions when EM-routed subagent dispatch gives equivalent
   isolation and the owner has approved that execution shape.
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 9 closes the remaining PI-5 process discipline bundle:

1. **Ship SDD-021: end-of-session self-review loop.** Sessions should produce a
   lightweight self-review output that identifies process inefficiencies,
   suggests agent/skill deltas, and routes durable changes through `/evolve`
   instead of burying lessons in chat history.
2. **Ship SDD-023: first-class user gates.** User approvals should be declared
   consistently by phase, surfaced in artifacts and dashboards, and recorded in
   the ledger or equivalent framework-owned state. This generalizes the Sprint 7
   and Sprint 8 approval lessons: Article XII ratification, ADR-016 acceptance,
   and pre-push approval gates must be visible before work proceeds.
3. **Ship SDD-025: stakeholder-pressure defense.** Create a playbook/skill that
   helps the EM and Principals respond to pressure by invoking SDD-014 Friction
   Analysis instead of accepting scope, quality, or governance shortcuts.

### Scope

- **Primary scope**: SDD-021, SDD-023, SDD-025.
- **Housekeeping shoulder if capacity permits**: SDD-039 Article VII wording
  clarification (fresh session OR subagent dispatch satisfies context
  isolation). Pull only if it fits without endangering the primary three items.
- **Carry-forward visibility**: SDD-034 and the PI-4 housekeeping items remain
  visible. Do not mark them DONE unless this sprint actually completes them.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-16: SDD-023 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect, with SW Dev task input | Uniform gates are the foundation for SDD-021 self-review outputs and SDD-025 pressure-defense approvals. Define the gate model first. |
| 2 | F-17: SDD-021 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect | Self-review needs to reference the user-gate construct and decide what evidence is durable versus session-local. |
| 3 | F-18: SDD-025 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect | Stakeholder-pressure defense should reuse the SDD-023 gate vocabulary and SDD-014 Friction Analysis path. |
| 4 | F-19: IMPLEMENT + QA for SDD-023, SDD-021, SDD-025 | SW Dev + workers | Implement only after all three validation contracts are locked; use fleet dispatch only for disjoint file sets. |
| 5 | F-20: Sprint 9 close + PI-5 close-readiness report | SW Dev + EM | Close Sprint 9, regenerate state, request owner approval before push, and produce a PI-5 close recommendation. |

The EM may split or combine CLARIFY sessions if the owner approves a specific
execution shape. The default is sequential, because SDD-023 defines vocabulary
that the other two specs should consume.

---

## 3. Likely CLARIFY surfaces

### SDD-023 -- First-Class User Gates

- **Q-A: Gate inventory.** Which phases require explicit user gates by default:
  CLARIFY answers, ADR acceptance, constitution edits, external writes, model
  upgrades, sprint close, push approval, PI close?
- **Q-B: Gate schema.** Should gates live in spec frontmatter, `validation.md`,
  a new `gates.md`, the ledger, or all of the above?
- **Q-C: Approval evidence.** What counts as accepted evidence: verbatim owner
  quote, EM synthesized decision, commit stamp, issue comment, or CLI record?
- **Q-D: Dashboard/state surface.** How should pending gates appear in
  `exec/state.md`, `exec/state.html`, and `exec/work-index.md`?
- **Q-E: Failure semantics.** Does a missing required user gate block feature
  close, sprint close, push, or all three?

### SDD-021 -- End-of-Session Self-Review Loop

- **Q-F: Trigger.** End every feature session, every sprint close, only when a
  worker detects friction, or an explicit `/evolve` command?
- **Q-G: Output shape.** Skill output, `RETRO.md` section, session memory entry,
  ledger event, or backlog candidate?
- **Q-H: Transcript access.** What can the self-review use when raw transcripts
  are unavailable or privacy-sensitive?
- **Q-I: Promotion path.** Which findings become agent deltas, skill updates,
  backlog items, or no-op lessons?

### SDD-025 -- Stakeholder-Pressure Defense

- **Q-J: Trigger examples.** Which pressure patterns matter most: speed over
  validation, skipping owner approval, reducing scope without traceability,
  pushing before approval, or accepting unverified external claims?
- **Q-K: Friction Analysis integration.** Does the playbook instantiate
  `templates/level-2-decision.md`, add a new defense template, or both?
- **Q-L: Principal routing.** Which cases route to EM, PM, Architect, SW Dev,
  or owner?
- **Q-M: Tone and evidence.** What is the expected executive-register response
  when defending quality without sounding obstructive?

---

## 4. Hard constraints

- **No silent REQUIRED deferral.** Sprint 9 inherits the Sprint 7 and Sprint 8
  rule: if a REQUIRED item cannot close, the feature or sprint does not close.
- **Pre-push approval is mandatory.** Sprint 8 made this explicit. Record owner
  approval status before any push, and never infer approval from green tests.
- **No constitution edit without ADR and owner approval.** SDD-023 or SDD-039 may
  require Article VII / gate-policy wording. Draft the ADR first, then route.
- **Stdlib-only CLI remains binding.** If implementation touches `cli/**`, use
  only stdlib and follow `docs/CLI-PATTERN.md`.
- **Preserve unrelated dirty work.** Stage explicit Sprint 9 paths only.
- **Do not close PI-5 automatically.** F-20 may write a close-readiness report,
  but PI close requires explicit owner approval.

---

## 5. Sprint close criteria

Sprint 9 closes DONE when all of the following are true:

1. SDD-023 validation contract is 100% REQUIRED checked.
2. SDD-021 validation contract is 100% REQUIRED checked.
3. SDD-025 validation contract is 100% REQUIRED checked.
4. Full test suite passes at or above the Sprint 8 baseline: `python -m pytest
   spec-driven-development/ --tb=no -q`.
5. Schema lint exits 0: `python spec-driven-development/cli/schema_lint.py`.
6. BACKLOG marks SDD-021, SDD-023, and SDD-025 DONE with commit SHAs. Any
   SDD-039, SDD-034, or PI-4 carry-over movement is recorded truthfully.
7. `sprints/PI-5/CURRENT_PI.md` marks Sprint 5 CLOSED with date, commit chain,
   tests, validation, ADRs, and retro paragraph. PI-5 remains active until owner
   approves final PI closure.
8. `exec/state.md`, `exec/state.html`, and `exec/work-index.md` are regenerated
   with `python spec-driven-development/cli/state_builder.py`.
9. `exec/sprint-progress.md` has `### Sprint 9 -- CLOSED` appended.
10. Owner approval is requested and recorded before any push.

---

## 6. Reporting template

Append this at Sprint 9 close:

```markdown
### Sprint 9 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-16, F-17, F-18, F-19, F-20
- Commits: <list>
- Tests: 331 -> N
- Validation: SDD-023 N/N REQUIRED; SDD-021 N/N REQUIRED; SDD-025 N/N REQUIRED
- ADRs: <list or none>
- PI-5 status: ACTIVE pending owner PI-close approval OR CLOSED if owner explicitly ratifies PI close
- SDD-023: DONE (<one-sentence gate model>)
- SDD-021: DONE (<one-sentence self-review loop>)
- SDD-025: DONE (<one-sentence pressure-defense playbook>)
- Carry-forward: <SDD-034 / SDD-039 / PI-4 carry-over truthfully reported>
- Owner ratification: REQUIRED BEFORE PUSH; <pending or approved with evidence>
- Notes: <one paragraph with Sprint 9 lessons>
- Next: <PI-5 close approval path or PI-6 kickoff recommendation>
```

---

## 7. Do NOT do

- Do NOT start Sprint 9 until Sprint 8 close/push approval status is resolved per
  the HARD PREREQUISITE.
- Do NOT close PI-5 without explicit owner approval.
- Do NOT mark any REQUIRED item done without evidence.
- Do NOT push without owner approval.
- Do NOT absorb unrelated SDD-035/Azure/workflow changes into Sprint 9 commits.