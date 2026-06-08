---
id: SDD-20260609UIVARIANT-spec
type: spec
status: blocked
owner: principal-product-manager
updated: 2026-06-09
feature: 2026-06-09-ui-lifecycle-variant
---

# Feature Spec: UI Lifecycle Variant (SDD-018)

> **Status note for the linter and the owner**: this spec is in the
> CLARIFY phase (see [`clarify.md`](./clarify.md), status `active`).
> SDD-FDC-001's closed status enum (`{draft, active, blocked, done,
> superseded, archived}`) does NOT contain a `clarify` value. The F-10
> prompt requested `status: clarify`; the closest valid mapping is
> `status: blocked` ("blocked on CLARIFY answers"). This is flagged as
> an OWNER-ATTENTION item in the F-10 pass 1 final report -- the
> framework may want to add `clarify` to the enum OR keep `blocked` as
> the official "blocked on CLARIFY" carrier. Either way, this spec
> stays `blocked` until CLARIFY closes, at which point it transitions
> directly to `active` (and then `done` at F-11 close).

- Date: 2026-06-09
- Authors: Principal Product Manager + Principal Architect
- Status: DRAFT (CLARIFY in progress -- pass 1 of 2 in F-10)
- Priority: P1
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7)
- Spec ID: SDD-018
- Parent objective: PI-5 Objective 3 -- UI Lifecycle Variant
  (`sprints/PI-5/CURRENT_PI.md`)
- Backlog row: BACKLOG.md / SDD-018 (P1, M effort, CLARIFY-gated)

> **F-10 pass 1 boundary**: only the sections marked "AUTHORED IN PASS 1"
> below are filled in. Sections marked "TBD pending CLARIFY answers" are
> deliberately left empty -- they will be populated in F-10 pass 2 after
> the owner answers the questions in [`clarify.md`](./clarify.md).
> Do not implement against any TBD section.

---

## Problem Statement (AUTHORED IN PASS 1)

Article X of `constitution/principles.md` ("Validation Is a Pre-Implementation
Contract", version 1.0.0) locks `validation.md` at `/tasks` time and forbids
loosening REQUIRED items after lock. The rule is sound for back-end and CLI
work where requirements can be enumerated up front and remain stable through
implementation. It is **too rigid for iterative visual / UI work**, where the
following are normal and expected:

1. **The contract surfaces during implementation, not before.** A
   dashboard panel's REQUIRED behavior (e.g. "the kanban column must
   highlight stale items older than N hours") is often only discoverable
   once the panel is rendered against real data. Pre-locking the contract
   either over-specifies (forcing guesses) or under-specifies (forcing
   re-locks via override ceremony).
2. **Visual decisions cascade.** Choosing a palette, type scale, or
   spacing token in week 1 changes the REQUIRED items in week 2 for every
   downstream panel. Article X's "no loosening" clause turns each cascade
   into an override.
3. **The PI-3/PI-4 Live UI v2 dashboard work proved the friction
   empirically.** The
   [`specs/2026-05-26-live-ui-v2/`](../2026-05-26-live-ui-v2/) and
   [`specs/2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
   spec dirs both show validation contracts that had to be edited after
   lock to absorb visual decisions made during implementation -- each
   edit a constitutional-grey-zone event, none currently auditable as
   a sanctioned variant.

Article XI ("Cross-Feature Serial Gate at CLARIFY and SPEC", version
1.2.0) was ratified 2026-06-08 and now actively gates this very spec dir
(see [`clarify.md`](./clarify.md) and the Article XI live contention
test results in the F-10 pass 1 final report). Article XI hardens the
upstream gates; SDD-018 must NOT undo that hardening for UI work. The
variant introduced here is narrow, opt-in, and additive to Article X --
not a global loosening.

PI-5 risk register entry for SDD-018 (`sprints/PI-5/CURRENT_PI.md`,
Risks section, row 5):

> "SDD-018 UI lifecycle relaxation leaks into non-UI features --
> Mitigated -- the variant is opt-in via a marker on the spec dir, not
> a global Article X amendment."

That mitigation is a CLARIFY input, not a CLARIFY answer. Pass 2 of
F-10 must record whether the owner confirms or amends it.

---

## Goal (AUTHORED IN PASS 1)

Define and ship a **controlled, opt-in, auditable variant of Article X
for UI work** that:

1. Permits `validation.md` to evolve during implementation through a
   structured `delta` mechanism (post-lock additions/changes recorded
   with timestamp + rationale + author), instead of forcing an override
   or a friction-analysis re-lock.
2. Is **opt-in per spec dir** via an explicit marker so the variant
   cannot leak into back-end, CLI, schema, or constitution work.
3. Stays **machine-checkable** through `cli/schema_lint.py` -- the
   variant introduces a new schema, not a relaxation of the existing
   one.
4. Demonstrates the variant by **retroactively validating one PI-3 / PI-4
   dashboard change** (specific spec dir TBD pending CLARIFY Q-E), so
   the rule is proven against real prior art before any new UI feature
   adopts it.
5. Resolves the **constitutional path** (Article X amendment vs new
   Article XII vs process-only) before any `constitution/` edit lands
   (CLARIFY Q-F).

---

## Out-of-Scope (AUTHORED IN PASS 1)

- **Loosening Article X for non-UI features.** Back-end, CLI, schema,
  and constitution work continue to lock validation at `/tasks` with no
  delta mechanism. The variant is opt-in only.
- **Loosening Article XI.** The serial CLARIFY/SPEC gate stays as
  ratified 2026-06-08. SDD-018 is itself subject to Article XI (see the
  live contention test in the F-10 final report).
- **Loosening Article VII** (One Feature, One Session). Pass 2 of F-10
  must run in its own session; F-11 (implementation) must run in another
  session.
- **A redesign of `validation.md`'s base schema.** The variant adds a
  `delta` section, not a rewrite. Existing locked items continue to
  parse and check identically.
- **New UI features in PI-5.** PI-5 ships no UI features after SDD-018;
  the first real UI feature exercising this variant ships in PI-6
  (target TBD pending CLARIFY Q-G).
- **Tooling for retroactive validation of more than one prior spec dir.**
  Exactly one PI-3 / PI-4 dashboard change is retro-validated as the
  proof; broader backfill is a future P3/P4 backlog item.
- **A new slash command for UI specs IF the variant ships as opt-in
  marker only** (CLARIFY Q-B will decide between marker, command, or
  hybrid).
- **Drafting ADR-014 (if needed).** CLARIFY Q-F decides the
  constitutional path; the ADR (if confirmed) is drafted in F-10 pass 2,
  not pass 1.

---

## Cross-Feature Notes (AUTHORED IN PASS 1)

Dedup scan run as part of the Article XI live contention test (F-10
pass 1) classified the following prior-art relationships. Final
disposition recorded in `backlog/DEDUP-LOG.md`; summary captured in the
F-10 pass 1 final report.

| Prior-art spec dir | Relationship | Disposition |
|---|---|---|
| [`2026-05-26-live-ui-v2/`](../2026-05-26-live-ui-v2/) | Primary motivating prior art -- the implementation that exposed Article X's rigidity. | Candidate for the retroactive validation in CLARIFY Q-E. |
| [`2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/) | Earliest dashboard spec dir; first instance of "static -> live" pivot mid-implementation. | Alternative candidate for CLARIFY Q-E retroactive validation. |
| [`2026-05-16-dashboard-about-and-freshness/`](../2026-05-16-dashboard-about-and-freshness/) | SDD-009 + SDD-010 bundled dashboard mods; CLARIFY-gated on data-freshness option. | Alternative candidate for CLARIFY Q-E retroactive validation. |
| [`2026-05-13-fleet-bridge-dashboard/`](../2026-05-13-fleet-bridge-dashboard/) | Design exploration (DESIGN.md only, never a full spec); originator of the "Bridge" aesthetic. | NOT a candidate for retroactive validation (no `validation.md` to retro-validate). Context only. |
| [`2026-06-07-serial-clarify-spec-gate/`](../2026-06-07-serial-clarify-spec-gate/) (SDD-019) | Provides the lock substrate this spec is currently subject to. | Hard cross-dependency: SDD-018 lock holder behavior assumes SDD-019 active. |
| [`2026-06-07-cross-feature-dedup/`](../2026-06-07-cross-feature-dedup/) (SDD-020) | Source of the dedup scan that surfaced the rows above. | Hard cross-dependency: dedup hook fires at `/clarify` (this spec). |

**Article XI live contention test (F-10 pass 1) confirmed**: this spec
dir currently holds the CLARIFY-phase lock per the rules ratified
2026-06-08. Grandfather predicate `_is_grandfathered` returns `False` for
this spec dir (`updated: 2026-06-09` >= `ARTICLE_XI_CUTOVER: 2026-06-08`),
so the spec is **subject to normal Article XI rules** -- it is not
grandfathered. Full output captured in the F-10 pass 1 final report.

---

## Acceptance Criteria

**TBD pending CLARIFY answers.** Will be derived in F-10 pass 2 from the
answered questions in [`clarify.md`](./clarify.md). At minimum the
acceptance criteria must trace to:

- CLARIFY Q-A (which Article X rules relax)
- CLARIFY Q-B (replacement mechanism: delta field, separate command,
  opt-in marker, or hybrid)
- CLARIFY Q-C (opt-in granularity: per-dir vs global)
- CLARIFY Q-D (`schema_lint` integration)
- CLARIFY Q-E (retroactive validation target -- specific spec dir
  named)
- CLARIFY Q-F (constitutional path -- amendment, new article, or
  neither)
- CLARIFY Q-G (first UI feature after SDD-018 -- success bar)

DO NOT IMPLEMENT against this section in pass 1.

---

## Affected Modules

**TBD pending CLARIFY answers.** Likely-affected modules listed as a
heads-up for the SW Dev (NOT a commitment):

- `cli/schema_lint.py` (probable -- new variant schema or marker
  recognition)
- `templates/validation.md` (probable -- new optional `delta` section)
- `templates/spec.md` (possible -- new optional frontmatter marker
  field)
- `constitution/principles.md` (CONDITIONAL on CLARIFY Q-F)
- `docs/ADR/014-*.md` (CONDITIONAL on CLARIFY Q-F; ID is provisional)
- `.github/prompts/spec.prompt.md` and/or new
  `.github/prompts/spec-ui.prompt.md` (CONDITIONAL on CLARIFY Q-B)

DO NOT IMPLEMENT against this section in pass 1.

---

## API Changes

**TBD pending CLARIFY answers.** Likely surface (NOT a commitment):

- `schema_lint` exit-code behavior on a UI-variant spec dir (Q-D)
- `validation.md` frontmatter / section schema (Q-B)
- Possible new `cli/spec_ui.py` or `cli/spec.py` --variant flag
  (depending on Q-B answer)

DO NOT IMPLEMENT against this section in pass 1.

---

## Test Strategy

**TBD pending CLARIFY answers.** Scaffolding tracker captured in the
F-10 pass 1 final report (section "Test scaffolding tracker") for SW
Dev pre-planning of F-11. DO NOT WRITE TESTS against this section in
pass 1.

---

## Traceability Matrix

**TBD pending CLARIFY answers.** Will trace each acceptance criterion
to: (a) the CLARIFY question that produced it; (b) the `validation.md`
REQUIRED item that checks it; (c) the test that verifies it; (d) the
file that implements it. Authored in F-10 pass 2.

---

## CLARIFY State

CLARIFY questions live in [`clarify.md`](./clarify.md). Status: **OPEN**.

**Pass 2 trigger** (per F-10 prompt): owner answers all questions in
`clarify.md`; Executive Manager commits the answered file and
re-dispatches F-10 pass 2 to finalize this spec, lock `validation.md`,
and author `plan.md`.

---

## Cross-References

- PI plan: [`../../sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md)
  (PI Objective 3, Sprint 3 row)
- Sprint 3 prep notes: [`../../sprints/PI-5/SPRINT-3-PREP-NOTES.md`](../../sprints/PI-5/SPRINT-3-PREP-NOTES.md)
- Backlog row: [`../../backlog/BACKLOG.md`](../../backlog/BACKLOG.md) (SDD-018)
- F-10 kickoff prompt: [`../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md`](../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md)
- Article X (locked validation contract): `constitution/principles.md` Article X
- Article XI (serial CLARIFY/SPEC gate): `constitution/principles.md` Article XI; ADR-013
- Prior art (PI-3/PI-4 dashboards): see "Cross-Feature Notes" table above
