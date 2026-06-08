# F-11 -- SDD-018 IMPLEMENT + QA + RETRO + sprint close

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Software Developer + dispatched workers**.
- Prerequisite: F-10 DONE -- SDD-018 spec finalized, `validation.md`
  contract LOCKED, `plan.md` + `tasks.md` committed, and any ADR drafted
  in F-10 either approved by the owner and the constitution edit landed,
  or formally deferred with the SDD-018 implementation working around the
  unamended constitution.
- Implement SDD-018 per F-10's locked validation contract and `tasks.md`.
- Stdlib only (Article V). No `constitution/**` edit unless an ADR
  approved in F-10 explicitly authorizes one (and that edit landed
  before F-11 started).
- Run QA after implementation: full test suite green (>= 259 baseline +
  new tests from F-09 and F-11), `schema_lint` clean, SDD-018
  validation contract at 100% REQUIRED items checked.
- Write a one-paragraph retro into
  [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
  Sprint 3 section.
- Update [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) entries
  SDD-032 and SDD-018 to **DONE** with commit SHAs. SDD-033 either
  marked DONE (if pulled into F-09 close-out) or carried forward with
  a note.
- Regenerate `exec/state.md` via
  `python spec-driven-development/cli/state_builder.py`.
- Append a sprint-close block to
  [`../exec/sprint-progress.md`](../exec/sprint-progress.md) per the
  SPRINT-07-KICKOFF reporting template.
- **Author `SPRINT-08-KICKOFF.prompt.md`** if PI-5 Sprint 4
  (SDD-015 + SDD-022 -- ADO/GitHub Issues bridge + model-upgrade
  discipline) is ready to start. Otherwise, note the deferral in the
  close block.

## Owner approval is REQUIRED BEFORE push

**Sprint close criterion #8 in `SPRINT-07-KICKOFF.prompt.md` requires
explicit owner approval before any close commit is pushed to
`origin/master`.** This is NOT inferred from a green test suite, a clean
`schema_lint`, or a 100% validation contract. The F-11 session must:

1. Stage the close commit locally.
2. Request approval from the owner via the EM (a single message
   summarizing what is about to close, the commit SHA chain, the test
   delta, validation status, and any ADR rollout).
3. Wait for an **explicit ratification** ("approved" / "ratified" /
   "ship it") from the owner.
4. Only then push the close commit chain.

This is the no-silent-slip floor established by the Option 3 hybrid
ratification on 2026-06-08 (Sprint 6 close at `4a6941c` plus owner
ratification stamp at `6c70e30`). For Sprint 7, the ratification step
moves to **before the push**, not after.

## Important sprint-boundary note

This sprint close closes **PI-5 Sprint 3** -- **not PI-5 itself**.
PI-5 has two more sprints after this one (Sprint 4 = SDD-022 + SDD-015;
Sprint 5 = SDD-021 + SDD-023 + SDD-025). Do not mark PI-5 DONE; only
mark Sprint 3 DONE.

---

> **FULL CONTENT AUTHORED AT F-11 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full implementation dispatch plan, per-task acceptance walk, QA
> checklist, retro template, BACKLOG-update script, state-regen step,
> sprint-close block, owner-approval request template, SPRINT-08
> authoring branch, and final close-commit instructions are authored by
> the SW Dev at the start of the F-11 session, after F-10 closes.
