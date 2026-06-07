# F-07 -- PLAN + TASKS for SDD-019 + SDD-020 + SDD-027

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Architect + Principal Software Developer** (jointly).
- Prerequisite: F-06 DONE -- all three `spec.md` files finalized and all
  three `validation.md` contracts locked.
- Read the three finalized specs in:
  - [`../specs/2026-06-07-serial-clarify-spec-gate/`](../specs/2026-06-07-serial-clarify-spec-gate/)
  - [`../specs/2026-06-07-cross-feature-dedup/`](../specs/2026-06-07-cross-feature-dedup/)
  - [`../specs/2026-06-07-host-gitignore-protection/`](../specs/2026-06-07-host-gitignore-protection/)
- Produce a `plan.md` and a `tasks.md` for each spec.
- Identify file-scope collisions across the three specs (SDD-019 and
  SDD-020 likely both touch `cli/schema_lint.py` or a new gate helper;
  SDD-027 + SDD-028 + SDD-029 all touch `cli/bootstrap.py host_link()`).
  Sequence tasks to avoid same-file parallel dispatches.
- Decide whether SDD-028 and SDD-029 housekeeping items pull into this
  sprint based on F-08 capacity. Document the call in the relevant
  `plan.md`.

## ADR-drafting trigger

- **If SDD-019 F-06 CLARIFY confirmed a constitutional amendment is
  required** (Article VII extension, new Article, or `decision-policy.md`
  amendment), this session drafts the ADR under `docs/ADR/` and lists the
  amendment as a Level-2 decision routed to the owner via the EM before
  any `constitution/**` edit. ADR drafting is the F-07 owner's
  responsibility; the constitution edit itself is NOT in this session.
- **If SDD-027 F-06 CLARIFY Q1 confirmed an Article X amendment is
  required**, draft that ADR here too. Same hand-off rule.
- If neither was confirmed, no ADR is needed and this session writes only
  plan + tasks.

---

> **FULL CONTENT AUTHORED AT F-07 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full plan/tasks template, file-scope collision analysis,
> ADR-drafting branch, capacity-allocation decision for SDD-028/029, and
> commit instructions are authored by the Architect/SW Dev at the start
> of the F-07 session, after F-06 closes and the validation contracts
> are locked.
