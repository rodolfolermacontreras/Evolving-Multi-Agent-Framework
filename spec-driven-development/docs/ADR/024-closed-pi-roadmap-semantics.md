# ADR-024: Closed-PI roadmap semantics and marker convention

- Date: 2026-07-08
- Status: accepted (drafted by principal-architect at Sprint 20 F-53 design; ratified by owner at F-54 on 2026-07-08)

## Owner ratification

Ratified by the project owner on 2026-07-08 (verbatim): "ADR-024 is accepted,
`constitution/roadmap.md` bumps 1.1.0 -> 1.2.0, and you are greenlit to make
local edits." Local edits authorized; push remains a separate gate at Sprint
close (F-55).

## Context

The PI-8 "Truth in the Window" audit
(`docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`, Section 5) found three defects in
`constitution/roadmap.md` that make the dashboard untruthful:

- The roadmap has no PI-6 section -- headers jump PI-5 -> PI-7, so the dashboard
  cannot render PI-6.
- The PI-7 header reads `(current, closed 2026-07-07)` -- a PI cannot be both
  current and closed.
- Closed PIs carry unchecked carry-forward checkboxes, and the dashboard reader
  reads those as a partial "% complete."

The dashboard reader `cli/state_builder_data.py::load_pis` (shipped by SDD-050,
Sprint 18) already parses PI lifecycle from the header text:

- `is_closed = "closed" in low`
- `is_current = ("(current" in low) and not is_closed`
- percent returns 100 when `is_closed`.

The reader is defensive and correct, but the roadmap format it consumes is not
written down anywhere, so the constitution format and the reader can silently
drift. This is the same class of durable, cross-surface data contract that
ADR-012 (filesystem-frontmatter-data-contract) governs. `roadmap.md` is a
`constitution/**` file; per Article VIII and ADR-006, changing its format and
backfilling sections is a Level-2 change that warrants an ADR + recorded owner
approval + a version bump.

## Decision

1. **Marker convention.** Each PI section header carries exactly one lifecycle
   marker:
   - Exactly one PI header carries `(current)` -- the single active PI.
   - Every completed PI header carries `(closed YYYY-MM-DD)`.
   - The two markers are never combined as `(current, closed ...)`.
   This matches the existing PI-4 `(closed 2026-06-06)` and PI-5 `(closed
   2026-06-09)` headers.

2. **Closed-PI semantics.** A PI whose header contains the substring `closed`
   renders done / 100% on the dashboard regardless of unchecked checkboxes.
   Unchecked boxes under a closed PI header denote CARRYOVER (items re-homed into
   a later PI), not incomplete work.

3. **Reader contract unchanged.** This convention is exactly what
   `cli/state_builder_data.py::load_pis` already parses. No reader change is
   made. No Article X locked function (`render_html`, `render_markdown`,
   `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
   `load_decisions`) is touched, and `TestS1FootprintLockGuard` stays GREEN.

4. **Roadmap completeness.** Every PI, including PI-6 and the current PI-8, MUST
   have its own section. No PI number may be skipped.

5. **Versioning.** Backfilling PI-6/PI-8 and adding the convention note are
   additive, backward-compatible changes to `constitution/roadmap.md`. Per
   ADR-006 semantic versioning this is a MINOR bump: `1.1.0 -> 1.2.0`, applied
   at F-54.

## Consequences

- Positive: the dashboard closed-PI percentage is correct; the roadmap has no PI
  gaps; the closed-PI convention is written down and provably aligned with the
  reader; the PI-7 contradiction is resolved by a clean closed marker.
- Negative: editing `roadmap.md` requires owner ratification + a version bump
  (Level-2 ceremony), so the fix cannot land silently.
- Neutral: no code changes; no new dependency (stdlib-only preserved); the
  reader and all Article X locked functions are untouched.

## Alternatives Considered

- Record the convention in `plan.md` only, no ADR. Rejected: a durable
  cross-surface data contract binding constitution format to the reader warrants
  an ADR (consistent with ADR-012), and the audit acceptance explicitly requires
  the roadmap edit to be "under an ADR + version bump."
- Change the reader to compute closed-state differently. Rejected: the reader is
  already defensive and correct; altering it risks Article X-adjacent surfaces
  for no benefit.
- Tick the carry-forward checkboxes on closed PIs to force 100%. Rejected:
  dishonest -- the boxes are genuine carryover and must stay unchecked while the
  convention explains them.

## Compliance

- [x] No new dependencies (stdlib-only preserved).
- [x] Backward compatible (additive PI-6/PI-8 sections + convention note; MINOR
      bump 1.1.0 -> 1.2.0).
- [x] No Article X locked function touched; `TestS1FootprintLockGuard` GREEN.
- [x] Recorded owner approval before any push (Article VIII); ratification quoted
      above (2026-07-08). Local edits authorized; push is the separate F-55 gate.
