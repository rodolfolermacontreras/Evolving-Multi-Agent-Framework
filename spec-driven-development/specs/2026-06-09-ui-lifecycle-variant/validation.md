---
id: SDD-20260609UIVARIANT-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-09
feature: 2026-06-09-ui-lifecycle-variant
---

# Validation Contract: UI Lifecycle Variant (SDD-018)

- Spec ID: SDD-018
- Status: **DRAFT (CONTRACT LOCKS AT SPEC FINALIZATION -- pass 2 of F-10)**
- Rule (Article X, current): zero unchecked REQUIRED items before
  implementation is considered complete. REQUIRED items cannot be
  loosened after lock without an explicit decision recorded here.

> **F-10 pass 1 boundary**: this file is intentionally a scaffold.
> REQUIRED items are NOT enumerated in pass 1 because they derive from
> the answers to [`clarify.md`](./clarify.md), which the owner has not
> yet provided. Locking this contract before CLARIFY closes would
> invert the very rule this spec is debating. The contract is locked
> at the close of F-10 pass 2 (after CLARIFY answers are committed and
> the spec is finalized).

---

## Required Items

**TBD pending CLARIFY answers.** Will be populated in F-10 pass 2.
Expected item areas (heads-up for SW Dev pre-planning F-11; NOT a
commitment):

- R-areas traceable to CLARIFY Q-A (which Article X rules relax)
- R-areas traceable to CLARIFY Q-B (delta mechanism / opt-in marker /
  separate command)
- R-areas traceable to CLARIFY Q-C (opt-in granularity)
- R-areas traceable to CLARIFY Q-D (`schema_lint` integration)
- R-area for the retroactive validation demo (Q-E)
- R-area for the constitutional path artifact (Q-F: ADR vs constitution
  edit vs neither)
- R-area for the documentation surface (where the variant is described
  for future spec authors)
- R-area for the test suite floor (no regression; test count >= baseline
  at F-10 pass 2 commit)
- R-area for `schema_lint` clean exit at F-11 close

See "Test scaffolding tracker" in the F-10 pass 1 final report for the
SW Dev's pre-plan starting point.

## Optional / Best-Effort Items

**TBD pending CLARIFY answers.**

---

## Notes

- This contract MUST be locked at F-10 pass 2 close (not before, not
  after F-11 starts). Pass 2 ratification = lock event.
- The variant being designed here will introduce a `delta` mechanism (or
  equivalent) that allows post-lock additions for spec dirs marked as
  UI-variant. Until SDD-018 itself ships, that mechanism is unavailable
  -- so SDD-018's own validation contract follows the standard Article X
  rule (lock at /tasks, no loosening). This is intentional and
  recursion-safe: SDD-018 bootstraps the variant; SDD-018 itself does
  not consume the variant.
- Article XI live contention test (F-10 pass 1) confirmed this spec dir
  currently holds the CLARIFY-phase lock and is NOT grandfathered. Full
  output in the F-10 pass 1 final report.
