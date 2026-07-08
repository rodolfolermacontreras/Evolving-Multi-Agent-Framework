---
id: SDD-20260708RMREPAIR-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-roadmap-repair-status-backfill
depends_on: [SDD-050]
---

# SPEC: SDD-052 -- Roadmap repair + status backfill

- Feature ID: SDD-052
- Sprint: PI-8 / Sprint 3 (Sprint 20, "Truth in the Window"); design slot F-53, implementation F-54
- Status: **active** (design locked at F-53; implementation pending in F-54)
- CLARIFY: [`clarify.md`](clarify.md)
- ADR: [`../../docs/ADR/024-closed-pi-roadmap-semantics.md`](../../docs/ADR/024-closed-pi-roadmap-semantics.md) (draft; owner ratification at F-54)
- Validation contract: [`validation.md`](validation.md)
- Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Source of truth: [`../../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md) Section 5 (Roadmap defects) + Section 3 Defect 1(c) + Section 7 sequencing

---

## Problem Statement

The PI-8 "Truth in the Window" audit found the roadmap and the spec-dir status
data are not trustworthy:

1. `constitution/roadmap.md` is missing an entire PI section: headers jump
   PI-5 -> PI-7 with no PI-6. The dashboard therefore cannot render PI-6.
2. The PI-7 header is self-contradictory: it reads
   `Hardening + Orchestration Maturity (current, closed 2026-07-07)` -- a PI
   cannot be both current and closed.
3. There is no PI-8 section on the roadmap, so PI-8 repeats the PI-6 gap.
4. Closed PIs carry unchecked carry-forward checkboxes, and the dashboard reader
   (`cli/state_builder_data.py::load_pis`, shipped by SDD-050) reads a partial
   percentage unless the header is marked closed. The "closed-PI" convention is
   nowhere written down, so the roadmap format and the reader can drift.
5. Five PI-7 spec directories still carry `status: active` frontmatter on
   already-DONE features, so the dashboard renders finished work as in-flight.

`roadmap.md` is a `constitution/**` file. Editing it is a Level-2 change per
Article VIII, requiring an ADR + recorded owner approval + version bump. This
spec designs that repair; it does not perform it. Implementation is F-54, gated
on owner approval (see `plan.md`).

## Goal

Repair the roadmap to structural and semantic truth, and backfill stale spec-dir
status, without changing any reader code or any Article X locked function:

- Backfill the missing PI-6 section with a `(closed YYYY-MM-DD)` marker.
- Fix the PI-7 header to a clean closed marker (drop "current").
- Add a PI-8 section carrying `(current)`.
- Write down the closed-PI marker convention and carry-forward semantics, and
  confirm they match what SDD-050 already reads (no reader change).
- Flip the stale `status: active` artifact lines in the closed PI-7 spec dirs to
  `done`.
- Ratify the convention and the constitution edit via ADR-024 + owner approval +
  a MINOR version bump (1.1.0 -> 1.2.0).

## Work items

| Item | Scope | Change class | Gate |
|------|-------|--------------|------|
| SDD-052A | Roadmap structural repair: add PI-6 section, fix PI-7 header, add PI-8 section, bump version 1.1.0 -> 1.2.0 | constitution edit (Level-2) | owner approval + ADR-024 |
| SDD-052B | Spec-dir status backfill: 24 `status: active` -> `done` artifact lines across 5 closed PI-7 dirs | data hygiene (Level-1) | none (rides F-54 batch) |
| SDD-052C | Closed-PI carry-forward semantics: write the convention note in the roadmap; confirm it matches `state_builder_data.py::load_pis` (no reader change) | constitution edit (Level-2) | rides SDD-052A / ADR-024 |
| SDD-052D | ADR-count correction: verify live planning/onboarding docs cite 23 ADRs (not 24); SDD-051 already fixed this -- verify/no-op | data hygiene (Level-1) | none |

## Requirements (RFC-2119)

### SDD-052A -- Roadmap structural repair
- **A-1 (MUST):** `roadmap.md` MUST contain a PI-6 section whose header carries a
  `(closed YYYY-MM-DD)` marker, placed between PI-5 and PI-7, matching the shape
  of the PI-5 / PI-7 sections. Headers MUST NOT jump PI-5 -> PI-7.
- **A-2 (MUST):** The PI-7 header MUST read as a clean closed PI (e.g.
  `Hardening + Orchestration Maturity (closed 2026-07-07)`) with no "current"
  token.
- **A-3 (MUST):** `roadmap.md` MUST contain a PI-8 section whose header carries
  the single `(current)` marker.
- **A-4 (MUST):** Exactly one PI header in `roadmap.md` MUST carry `(current)`
  after the edit (the PI-8 header). No header may combine `(current, closed ...)`.
- **A-5 (MUST):** The `roadmap.md` frontmatter `version` MUST be bumped from
  `'1.1.0'` to `'1.2.0'` (MINOR, additive per ADR-006).
- **A-6 (MUST):** The `roadmap.md` edit MUST be performed under ADR-024 with
  recorded owner approval before any push (Article VIII).

### SDD-052B -- Spec-dir status backfill
- **B-1 (MUST):** Every `status: active` artifact frontmatter line in the five
  closed PI-7 spec dirs MUST be flipped to `status: done`. The exact surface is
  24 artifact lines across five dirs (enumerated in `tasks.md`):
  - `2026-06-26-two-tier-executive-manager` (SDD-043): spec, plan, tasks, validation (4)
  - `2026-06-26-plain-language-comms-discipline` (SDD-044): spec, plan, tasks, validation (4)
  - `2026-06-26-detach-clone-and-run-hardening` (SDD-045): spec, plan, tasks, validation (4)
  - `2026-06-26-make-promises-true` (SDD-046): spec, plan, tasks, validation (4)
  - `2026-06-26-sdd-048-maintainability` (SDD-048): clarify, spec, plan, tasks, validation-C1, validation-C2, validation-C3, validation-D2 (8)
- **B-2 (MUST):** `2026-06-26-sdd-047-de-author` (SDD-047) MUST be left unchanged
  (all 8 artifacts already `done`; this is a no-op confirmation).
- **B-3 (MUST):** `python spec-driven-development/cli/schema_lint.py` MUST exit 0
  after the flips (`done` is a valid `status` enum value; no new enum needed).

### SDD-052C -- Closed-PI carry-forward semantics
- **C-1 (MUST):** `roadmap.md` MUST contain a written convention (a short "PI
  status conventions" note) stating: (a) each PI header carries exactly one
  lifecycle marker; (b) `(current)` marks the single active PI; (c)
  `(closed YYYY-MM-DD)` marks a completed PI; (d) a closed PI renders done /
  100% on the dashboard regardless of unchecked boxes; (e) unchecked boxes under
  a closed PI header denote carry-forward (re-homed to a later PI), not
  incomplete work.
- **C-2 (MUST):** The convention MUST match what SDD-050's reader parses. The
  reader (`cli/state_builder_data.py::load_pis`) uses `is_closed = "closed" in
  low`, returns pct 100 when closed, and guards `is_current` with
  `not is_closed`. The convention MUST therefore require the literal substring
  `closed` in closed headers and forbid combining `current` with `closed`.
- **C-3 (MUST NOT):** No change may be made to `cli/state_builder_data.py`, to
  any Article X locked reader function (`render_html`, `render_markdown`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
  `load_decisions`), or to `TestS1FootprintLockGuard`.

### SDD-052D -- ADR-count correction
- **D-1 (MUST):** Live planning/onboarding docs MUST cite the correct ADR count
  (23; next ADR is 024). This was already corrected by SDD-051 (Sprint 19);
  D-1 is a verification that no live text still asserts "24 ADRs".
- **D-2 (MUST NOT):** Frozen historical artifacts (kickoff prompts, closed
  retros, shipped ADRs/specs) MUST NOT be rewritten to change a historical "24"
  reference; only live, forward-looking text is in scope.

## Acceptance criteria

Traces 1:1 to the audit Section 5 "Acceptance (Roadmap)" plus the two
CLARIFY-surfaced items. Full evidence lives in `validation.md`.

- **AC-1 (A-1):** `roadmap.md` has a PI-6 section with a closed marker; headers no
  longer jump PI-5 -> PI-7. Evidence: grep `^## PI-6` + `(closed`.
- **AC-2 (A-2, A-4):** The PI-7 header carries a clean closed marker (no
  "current"); exactly one header (`## PI-8 ... (current)`) is current. Evidence:
  grep PI-7 header + count of `(current`.
- **AC-3 (A-3):** `roadmap.md` has a PI-8 section. Evidence: grep `^## PI-8`.
- **AC-4 (C-1, C-2):** A written closed-PI convention exists and matches what
  SDD-050 reads. Evidence: convention note text + cross-reference to
  `load_pis` parsing (`"closed" in low`; one `(current)`).
- **AC-5 (B-1, B-2, B-3):** All 24 stale spec-dir `status:` lines are `done`;
  SDD-047 unchanged; schema-lint exit 0. Evidence: grep `^status:\s*active`
  returns 0 in the five dirs; schema-lint run.
- **AC-6 (A-5, A-6):** The `roadmap.md` edit is under ADR-024 + recorded owner
  approval + version bump `1.1.0 -> 1.2.0`. Evidence: ADR-024 Accepted; owner
  approval quote; frontmatter version.
- **AC-7 (D-1):** No live text asserts "24 ADRs"; live docs cite 23. Evidence:
  grep of live docs; SDD-051 validation-051A reference.

## Non-goals (out of scope)

- No change to any reader code (`state_builder_data.py`) or any Article X locked
  function. SDD-050 already reads closed-state defensively; the roadmap markers
  it consumes are the only new inputs.
- No dashboard Defect 1/2 reader fix (that is SDD-050, Sprint 18) and no
  doc-staleness refresh (that is SDD-051, Sprint 19).
- No ticking of the carry-forward checkboxes on any closed PI; boxes are honest
  carryover and stay unchecked while the convention explains them.
- No rewrite of frozen historical artifacts.
- No new pip dependency; stdlib-only (Article V).

## Sequencing note (audit Section 7)

SDD-052's roadmap PI-6 backfill + closed markers are a data-prerequisite for
SDD-050's closed-PI percentage fix. SDD-050 shipped a defensive reader (Sprint
18) that does not block on S20, so the ordering is safe: SDD-052 supplies the
marker data; the reader already knows how to consume it. Hence `depends_on:
[SDD-050]` -- the reader must exist for the `(closed)` markers to render 100%.

## Traceability matrix

| Requirement | Acceptance | Audit anchor |
|-------------|-----------|--------------|
| A-1 | AC-1 | Sec 5 Defect "PI-6 MISSING"; Acceptance bullet 1 |
| A-2 | AC-2 | Sec 5 Defect "PI-7 self-contradiction"; Acceptance bullet 2 |
| A-3 | AC-3 | Sec 5 Fix "Add PI-8 entry"; Acceptance bullet 5 |
| A-4 | AC-2 | Sec 5 (one current PI) |
| A-5 | AC-6 | Sec 5 Acceptance bullet 6 (version bump) |
| A-6 | AC-6 | Sec 5 Note (Level-2 ADR + owner approval) |
| B-1 | AC-5 | Sec 3 Defect 1(c); Sec 5 Acceptance bullet 4 |
| B-2 | AC-5 | Sec 5 "6th surfaced at CLARIFY" (already done) |
| B-3 | AC-5 | schema-lint gate |
| C-1 | AC-4 | Sec 5 "Define closed-PI semantics"; Acceptance bullet 3 |
| C-2 | AC-4 | Sec 5 "matches what SDD-050 reads" |
| C-3 | -- | Article X immutability (non-goal) |
| D-1 | AC-7 | Sec 4 doc staleness (ADR count); SDD-051 already fixed |
| D-2 | AC-7 | frozen-artifact exclusion |
