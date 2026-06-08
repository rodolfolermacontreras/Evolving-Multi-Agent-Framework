# F-10 -- SDD-018 UI Lifecycle Variant (CLARIFY + SPEC + PLAN + TASKS)

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Product Manager + Principal Architect** (jointly).
- Prerequisite: F-09 DONE -- all 7 REQUIRED items in the SDD-032
  validation contract checked, lock surface preserved, no REQUIRED-item
  deferrals.
- SDD-018 has **no spec dir yet**. F-10 scaffolds it from scratch under
  `specs/YYYY-MM-DD-ui-lifecycle-variant/` (date = F-10 session date).
- Run a full CLARIFY interview with the human owner: one question at a
  time, recommendation first, wait for the answer (grill-me protocol).
  Expect a heavy CLARIFY load -- the "relaxed Article X" surface needs
  explicit owner guidance:
  - Which Article X rules relax? (validation lock? the
    pre-implementation contract? the no-loosening-after-lock clause?)
  - What replaces them? (a new `delta` field in `validation.md`? a
    separate `/spec-ui` slash command? an opt-in marker on the spec dir?)
  - How do delta entries flow through `schema_lint`?
  - Is the variant opt-in per spec (via marker) or global for any UI
    work? (PI-5 risk register flags the leak risk as "Mitigated --
    opt-in via a marker on the spec dir.")
  - One retroactive validation on a PI-3 dashboard change is the
    success criterion per `CURRENT_PI.md` -- which change?
- Finalize `spec.md` (Acceptance Criteria, Out-of-Scope, Traceability
  Matrix).
- Lock `validation.md` (Article X discipline -- REQUIRED items locked at
  spec close; no loosening after).
- Write `plan.md` and `tasks.md`.

## Article XI live contention test

When this F-10 session scaffolds the SDD-018 spec dir and the dir
enters CLARIFY status, the new Article XI gate (now fully wired by
SDD-032 R7 queue + R8 grandfather, both closed in F-09) should observe
it. **This is the first real-world test of Article XI under live
contention.** Verify the gate fires correctly when SDD-018 enters
CLARIFY, and log the observed behavior (queue state, grandfather
classification, any unexpected blocks) in the F-10 session report.

## Constitutional / Article-X risk flags

- **SDD-018 may require a constitutional amendment** -- either an
  Article X amendment (to permit delta entries / lifecycle variants) or
  a new Article XII (UI Lifecycle Variant) sitting beside Article XI.
  CLARIFY decides which path. **If an amendment is required, DO NOT
  edit `constitution/**` in this session.** Document the amendment
  requirement in `spec.md`, draft the ADR under `docs/ADR/`, and route
  to the owner as a Level-2 decision via the EM. The constitution edit
  itself never happens in F-10 -- it waits for explicit owner approval
  after reading the ADR (analogous to how ADR-013 + Article XI rolled
  out in Sprint 6).

---

> **FULL CONTENT AUTHORED AT F-10 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full CLARIFY interview script, per-question PM/Architect
> recommendations, spec-dir scaffolding template, Article XI live-
> contention verification checklist, ADR-drafting branch, plan/tasks
> template, and commit instructions are authored by the PM/Architect at
> the start of the F-10 session, after F-09 closes.
