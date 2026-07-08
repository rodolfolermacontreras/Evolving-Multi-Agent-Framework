---
id: SDD-20260708RMREPAIR-tasks
type: tasks
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-roadmap-repair-status-backfill
depends_on: [SDD-050]
---

# TASKS: SDD-052 -- Roadmap repair + status backfill

Atomic, verification-driven tasks for F-54. Shared surfaces
(`constitution/roadmap.md`, `docs/ADR/024-...`) force SERIALIZATION -- one writer
at a time; no parallel dispatch on those files. Status-flip tasks touch disjoint
files and may run in parallel.

Legend: `[G]` = blocked on an owner gate (see `plan.md`). `[L1]` = Level-1, no
gate.

---

## SDD-052B -- Status backfill (Level-1)

### T-B1 [L1] Flip SDD-043 artifacts to done
- allowed_files: `specs/2026-06-26-two-tier-executive-manager/{spec,plan,tasks,validation}.md`
- blocked_files: `constitution/**`, `cli/**`, everything else
- Change: `status: active` -> `status: done` (4 lines). Leave `clarify.md`
  (already done).
- Verify: `grep -n "^status:" specs/2026-06-26-two-tier-executive-manager/*.md`
  shows all `done`.

### T-B2 [L1] Flip SDD-044 artifacts to done
- allowed_files: `specs/2026-06-26-plain-language-comms-discipline/{spec,plan,tasks,validation}.md`
- Change: 4 lines active -> done. Leave `clarify.md`.
- Verify: grep all `done`.

### T-B3 [L1] Flip SDD-045 artifacts to done
- allowed_files: `specs/2026-06-26-detach-clone-and-run-hardening/{spec,plan,tasks,validation}.md`
- Change: 4 lines active -> done. Leave `clarify.md`.
- Verify: grep all `done`.

### T-B4 [L1] Flip SDD-046 artifacts to done
- allowed_files: `specs/2026-06-26-make-promises-true/{spec,plan,tasks,validation}.md`
- Change: 4 lines active -> done. Leave `clarify.md`.
- Verify: grep all `done`.

### T-B5 [L1] Flip SDD-048 artifacts to done
- allowed_files: `specs/2026-06-26-sdd-048-maintainability/{clarify,spec,plan,tasks,validation-C1,validation-C2,validation-C3,validation-D2}.md`
- Change: 8 lines active -> done.
- Verify: grep all `done`.

### T-B6 [L1] Confirm SDD-047 no-op + schema-lint
- allowed_files: none (read-only)
- Verify: `grep -rn "^status: active" specs/2026-06-26-sdd-047-de-author/`
  returns 0; then `python spec-driven-development/cli/schema_lint.py` exits 0.

---

## SDD-052A + SDD-052C -- Roadmap edit (Level-2, SERIALIZED)

### T-A1 [G] Backfill PI-6 section
- gate: G-1 (ADR-024 accepted) + G-2 (owner roadmap approval)
- allowed_files: `constitution/roadmap.md`
- blocked_files: `cli/state_builder_data.py`, all Article X locked functions
- Change: insert `## PI-6: <title> (closed YYYY-MM-DD)` between PI-5 and PI-7,
  matching PI-5 section shape.
- Verify: `grep -n "^## PI-6" constitution/roadmap.md` present + `(closed`.

### T-A2 [G] Fix PI-7 header
- allowed_files: `constitution/roadmap.md`
- Change: `(current, closed 2026-07-07)` -> `(closed 2026-07-07)`.
- Verify: PI-7 header has no `current`.

### T-A3 [G] Add PI-8 section
- allowed_files: `constitution/roadmap.md`
- Change: append `## PI-8: <title> (current)` with sprint checklist including an
  SDD-052 row.
- Verify: `grep -n "^## PI-8" ...` present; exactly one `(current` across all PI
  headers.

### T-C1 [G] Write closed-PI convention note
- allowed_files: `constitution/roadmap.md`
- Change: add a "PI status conventions" note (marker rules + carry-forward
  semantics per spec C-1). Cross-reference `state_builder_data.py::load_pis`.
- Verify: note present; wording requires literal `closed` substring and forbids
  `(current, closed`.

### T-A4 [G] Bump roadmap version
- allowed_files: `constitution/roadmap.md`
- Change: frontmatter `version: '1.1.0'` -> `version: '1.2.0'`.
- Verify: grep frontmatter version.

---

## SDD-052D -- ADR-count verify (Level-1)

### T-D1 [L1] Verify live docs cite 23 ADRs
- allowed_files: none (read-only unless a live assertion is found)
- Verify: `grep -rn "24 ADR" spec-driven-development/` -> only frozen historical
  prompts; no live forward-looking assertion. Record in validation D-1. No edit
  expected (SDD-051 already fixed).

---

## ADR + close

### T-ADR [F-53] Draft ADR-024
- allowed_files: `docs/ADR/024-closed-pi-roadmap-semantics.md`
- Change: draft plain-markdown ADR, status `proposed`. **This is the one edit
  performed at F-53** (audit acceptance permits the draft ADR).
- Verify: file exists; ADR-023 format; no YAML frontmatter.

### T-RATIFY [G] Owner ratifies ADR-024 (F-54)
- gate: G-1
- Change: owner flips ADR-024 `proposed` -> `accepted` with ratification note.

### T-CLOSE [G] Close SDD-052 (F-54)
- Change: flip this feature's spec/plan/tasks/validation to `done`; tick the
  PI-8 SDD-052 checklist row; record close commit SHA in
  `exec/sprint-progress.md`.
- Verify: AC-1..AC-7 all proven in `validation.md`; schema-lint exit 0; pytest
  count not decreased; `TestS1FootprintLockGuard` GREEN.
