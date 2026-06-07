# F-08 -- IMPLEMENT + QA + RETRO + sprint close

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Software Developer + dispatched workers**.
- Prerequisite: F-07 DONE -- `plan.md` and `tasks.md` exist for SDD-019,
  SDD-020, SDD-027 (and SDD-028 / SDD-029 if pulled in); any ADR drafted
  in F-07 is committed.
- Implement the three primary specs in the order F-07 decided. Honor the
  same-file sequencing constraints (SDD-019 / SDD-020 schema_lint
  touchpoints; SDD-027 / SDD-028 / SDD-029 bootstrap.py host_link()
  touchpoints).
- Stdlib only (Article V). No `constitution/**` edit unless an ADR
  approved in F-07 explicitly authorizes one.
- Run QA after implementation: full test suite green, schema_lint clean,
  validation contracts at 100% REQUIRED for each spec.
- Write a one-paragraph retro into
  [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
  Sprint 2 section.
- Update [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) entries
  SDD-019, SDD-020, SDD-027 (and 028 / 029 if pulled) to DONE with
  commit SHAs.
- Regenerate `exec/state.md` via
  `python spec-driven-development/cli/state_builder.py`.
- Append a sprint-close block to
  [`../exec/sprint-progress.md`](../exec/sprint-progress.md) per the
  SPRINT-06-KICKOFF reporting template.
- **Author `SPRINT-07-KICKOFF.prompt.md`** if PI-5 Sprint 3 (SDD-018, UI
  Lifecycle Variant) is ready. Otherwise, note the deferral in the close
  block.

## Important sprint-boundary note

This sprint close closes **PI-5 Sprint 2** -- **not PI-5 itself**. PI-5
has three more sprints after this one (Sprint 3 = UI Lifecycle Variant,
Sprint 4 = ADO/GitHub Bridge + Model Upgrade Discipline, Sprint 5 =
Self-Review + Stakeholder Defense + Uniform Gates). Do not mark PI-5
DONE; only mark Sprint 2 DONE.

---

> **FULL CONTENT AUTHORED AT F-08 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full implementation dispatch plan, per-spec acceptance walk, QA
> checklist, retro template, BACKLOG-update script, state-regen step,
> sprint-close block, and SPRINT-07 authoring branch are authored by the
> SW Dev at the start of the F-08 session, after F-07 closes and the
> plans + tasks are committed.
