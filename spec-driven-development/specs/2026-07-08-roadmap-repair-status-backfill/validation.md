---
id: SDD-20260708RMREPAIR-validation
type: validation
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-roadmap-repair-status-backfill
depends_on: [SDD-050]
status_note: closed at F-54 2026-07-08; all REQUIRED items proven with real-run evidence
---

# VALIDATION: SDD-052 -- Roadmap repair + status backfill

Single combined validation contract (D-2 lightweight path; this is a docs/data
feature, no code). Grouped by SDD-052A/B/C/D. Every REQUIRED item is checkable
with real evidence; every commit SHA cited is real (DA-Evidence discipline).
Checkboxes are UNCHECKED here because this is the F-53 design contract -- F-54
ticks them with proof.

---

## SDD-052A -- Roadmap structural repair (REQUIRED)

- [x] **A-R1** `roadmap.md` has a `## PI-6` section with a `(closed YYYY-MM-DD)`
      marker; headers no longer jump PI-5 -> PI-7.
      Evidence: `grep -n "^## PI-6" constitution/roadmap.md` returns a header
      containing `(closed`.
- [x] **A-R2** PI-7 header reads `... (closed 2026-07-07)` with no `current`.
      Evidence: `grep -n "^## PI-7" constitution/roadmap.md` shows `(closed
      2026-07-07)` and no `current`.
- [x] **A-R3** `roadmap.md` has a `## PI-8` section.
      Evidence: `grep -n "^## PI-8" constitution/roadmap.md` present.
- [x] **A-R4** Exactly one PI header carries `(current)` (the PI-8 header); no
      header contains `(current, closed`.
      Evidence: `grep -c "(current" constitution/roadmap.md` on PI headers == 1;
      `grep -n "(current, closed" ...` returns 0.
- [x] **A-R5** Frontmatter version bumped `'1.1.0'` -> `'1.2.0'`.
      Evidence: `grep -n "^version:" constitution/roadmap.md` shows `'1.2.0'`.

## SDD-052B -- Spec-dir status backfill (REQUIRED)

- [x] **B-R1** All 24 stale `status: active` artifact lines flipped to `done`
      across the five closed PI-7 dirs (043/044/045/046/048).
      Evidence: `grep -rn "^status: active"` in those five dirs returns 0. Files:
      043 {spec,plan,tasks,validation}; 044 {spec,plan,tasks,validation}; 045
      {spec,plan,tasks,validation}; 046 {spec,plan,tasks,validation}; 048
      {clarify,spec,plan,tasks,validation-C1,validation-C2,validation-C3,validation-D2}.
- [x] **B-R2** SDD-047 dir unchanged (all 8 artifacts already `done`).
      Evidence: `git diff --name-only` shows no file under
      `specs/2026-06-26-sdd-047-de-author/`.
- [x] **B-R3** schema-lint clean after flips.
      Evidence: `python spec-driven-development/cli/schema_lint.py` exit 0.
- Supporting done-evidence (why these features are genuinely done, Q-C):
  Sprint 14 close `ecd13b3` (481->501, SDD-043 11/11 + SDD-044 7/7 + SDD-045
  17/17, ADR-020); Sprint 15 close `44d546d` (501->518, SDD-046 19/19, ADR-021);
  Sprint 16 close `e93862d` (518->540, SDD-047, ADR-022); Sprint 17 close
  `71bba51` (540->558, SDD-048 C-1 7/7 + C-2 4/4 + C-3 4/4 + D-2 4/4, ADR-023);
  PI-7 close push `7088f35`.

## SDD-052C -- Closed-PI carry-forward semantics (REQUIRED)

- [x] **C-R1** A written "PI status conventions" note exists in `roadmap.md`
      stating the marker rules and carry-forward semantics (spec C-1 a-e).
      Evidence: note text present in `constitution/roadmap.md`.
- [x] **C-R2** The convention matches SDD-050's reader.
      Evidence: convention requires literal `closed` substring and forbids
      `(current, closed`; cross-references `cli/state_builder_data.py::load_pis`
      (`is_closed = "closed" in low`; pct 100 when closed; `is_current` guarded
      by `not is_closed`). No reader diff.
- [x] **C-R3** No reader / Article X change.
      Evidence: `git diff --name-only` shows no `cli/state_builder_data.py`;
      `TestS1FootprintLockGuard` GREEN.

## SDD-052D -- ADR-count correction (REQUIRED)

- [x] **D-R1** No live forward-looking doc asserts "24 ADRs"; live docs cite 23
      (next 024). Already satisfied by SDD-051 (Sprint 19).
      Evidence: `grep -rn "24 ADR" spec-driven-development/` returns only frozen
      historical prompts (e.g. `SPRINT-19-KICKOFF.prompt.md`); SDD-051
      `validation-051A.md` line 30 asserts 23. No live edit required.

## Gate + ADR (REQUIRED at F-54)

- [x] **G-R1** ADR-024 status `accepted` with owner ratification note.
- [x] **G-R2** Recorded owner approval for the `roadmap.md` constitution edit,
      captured in `exec/sprint-progress.md` before push (Article VIII).

---

## Required User Gates Declared By This Spec

Per SDD-023 gate vocabulary. F-54 MUST NOT push the roadmap edit or ratify
ADR-024 until both gates are `approved`.

- gate_id: G-1
  gate_type: adr-acceptance
  blocking_scope: adr-dependent-edit
  approver: owner
  evidence_type: accepted-adr
  evidence_ref: `ADR-024`
  status: approved
  next_action: DONE at F-54 -- ADR-024 flipped proposed -> accepted with owner ratification note (2026-07-08). Push remains gated at F-55.

- gate_id: G-2
  gate_type: constitution-edit
  blocking_scope: constitution-edit
  approver: owner
  evidence_type: owner-quote
  evidence_ref: `owner-F54-roadmap-approval`
  status: approved
  next_action: DONE at F-54 -- owner verbatim approval quote (2026-07-08) recorded in exec/sprint-progress.md Sprint 20 / F-54 block. Push remains gated at F-55.

---

## Definition of Done (F-54)

- AC-1..AC-7 (spec) all proven with the evidence above.
- G-R1, G-R2 both satisfied (both gates `approved`).
- schema-lint exit 0; pytest count not decreased from F-54 baseline.
- `TestS1FootprintLockGuard` GREEN (no reader / Article X change).
- This feature's spec/plan/tasks/validation flipped to `done` at close;
  clarify already `done`.
