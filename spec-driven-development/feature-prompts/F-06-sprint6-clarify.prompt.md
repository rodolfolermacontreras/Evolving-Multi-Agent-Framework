# F-06 -- CLARIFY + SPEC finalization for SDD-019 + SDD-020 + SDD-027

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Product Manager + Principal Architect** (jointly).
- Read the three scaffolded spec dirs:
  - [`../specs/2026-06-07-serial-clarify-spec-gate/`](../specs/2026-06-07-serial-clarify-spec-gate/) -- SDD-019, 9 CLARIFY Qs
  - [`../specs/2026-06-07-cross-feature-dedup/`](../specs/2026-06-07-cross-feature-dedup/) -- SDD-020, 7 CLARIFY Qs
  - [`../specs/2026-06-07-host-gitignore-protection/`](../specs/2026-06-07-host-gitignore-protection/) -- SDD-027, 7 CLARIFY Qs
- Run a CLARIFY interview with the human owner: one question at a time,
  recommendation first, wait for the answer (grill-me protocol). Joint
  handling for SDD-019 Q5 and SDD-020 Q5 (integration order) per the
  Architect's prep note.
- Finalize the three `spec.md` files (fill in Acceptance Criteria,
  Out-of-Scope, Traceability Matrix).
- Lock the three `validation.md` contracts (Article X).
- Commit per spec dir, push to `origin/master`.

## Constitutional / Article-X risk flags

- **SDD-019 CLARIFY Q5** decides whether a constitutional amendment is
  required. If yes, **DO NOT** edit `constitution/**` in this session.
  Document the amendment requirement in `spec.md` and hand off to F-07
  for ADR drafting.
- **SDD-027 CLARIFY Q1** decides whether Article X needs an amendment.
  Same rule: do not edit `constitution/**` here. Hand off to F-07 if
  needed. Friction Analysis is NOT required up front per owner direction
  2026-06-07.

---

> **FULL CONTENT AUTHORED AT F-06 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full CLARIFY interview script, per-question Architect
> recommendations, joint-handling instructions for SDD-019 Q5 / SDD-020
> Q5, spec finalization checklist, and commit instructions are authored
> by the PM/Architect at the start of the F-06 session, after re-reading
> the three spec dirs and the prep note.
