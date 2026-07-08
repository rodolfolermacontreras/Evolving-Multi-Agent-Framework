---
id: SDD-20260708DASHBOARDTRUTH-spec
type: spec
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: 2026-07-08-dashboard-truth
depends_on: [SDD-046]
---

# SPEC: SDD-050 -- "Dashboard truth"

- Feature ID: SDD-050. Sprint: PI-8 Sprint 18.
- Status: done.
- Plan: [plan.md](plan.md). Tasks: [tasks.md](tasks.md). Validation: [validation.md](validation.md). Retro: [RETRO.md](RETRO.md).
- Depends on: SDD-046 (`done_check.py` REQUIRED-item enforcement; `fleet.py mark` ledger close).

---

## Problem Statement

The generated dashboard (`state.html` / `state.md`) contradicts the repository it describes. Two defects were observed against the real roadmap and feature tree:

- Defect 1 (feature stage is wrong): `detect_stage` used a status-line-first / artifact-first heuristic that disagreed with the actual validation evidence. A feature whose REQUIRED validation items are fully checked (proof of DONE) could render as IMPLEMENT or REVIEW because its `spec.md` status line still read `active`, or because a `RETRO.md` was demanded before DONE would show. Conversely, `done_check.py` only read a single `validation.md`, so features that split validation into `validation-*.md` files (SDD-047, SDD-048) were mis-counted. The dashboard reported stage from the weakest signal (prose status line) instead of the strongest (real checked REQUIRED boxes).
- Defect 2 (closed PIs render wrong and the header shows a stale PI): a Program Increment header that reads `(closed YYYY-MM-DD)` still computed percent-complete from stray unchecked roadmap boxes, so a fully-closed PI could show < 100%. A header that reads `(current, closed YYYY-MM-DD)` was treated as the live PI. And when every PI was closed, the header fell back to `pis[0]` (the OLDEST, PI-1) instead of the newest, so the dashboard could announce a long-finished PI as the active one.

Both defects are truth defects: the dashboard is the single at-a-glance status surface, and it was reporting states the underlying artifacts do not support.

---

## Goal

Make the dashboard report the truth of the artifacts, from the strongest available signal:

- Defect 1: `detect_stage` becomes evidence-first. Fully-checked REQUIRED validation items mean DONE, with no separate RETRO gate for the dashboard stage label; REQUIRED-only ratio (not optional items) drives IMPLEMENT/REVIEW; artifact presence is only a last-resort fallback. `done_check.py` reads every `validation*.md` file so split-validation features are counted correctly.
- Defect 2: a PI whose header contains `closed` renders at 100% and is never the current PI; when all PIs are closed the header falls back to the NEWEST PI by number, never PI-1.

The change is confined to the leaf data module `cli/state_builder_data.py` and the shared reader in `cli/done_check.py`. No Article X locked render function is touched.

---

## Requirements

### Defect 1 -- Evidence-first stage detection

- FR-D1-1: When a feature's validation (across all `validation*.md`) has REQUIRED items and every REQUIRED item is checked, `detect_stage` returns DONE regardless of the `spec.md` status line and regardless of whether a `RETRO.md` exists.
- FR-D1-2: When REQUIRED items exist but are not all checked, `detect_stage` returns REVIEW if the checked ratio is >= 80%, otherwise IMPLEMENT -- never DONE. Optional items do not count toward this ratio.
- FR-D1-3: When no validation evidence exists, `detect_stage` falls back to artifact presence (tasks -> TASKS, plan -> PLAN, spec -> SPEC, design/clarify -> CLARIFY, else BACKLOG) and to an explicit normalized `spec.md` status line where present.
- FR-D1-4: `done_check.py` aggregates REQUIRED/optional counts across every `validation*.md` in a feature dir, not just `validation.md`.
- FR-D1-5: `detect_stage` and `done_check.py` share one validation-completeness reader so the dashboard label and the DONE gate cannot disagree.

### Defect 2 -- PI closed handling

- FR-D2-1: `load_pis` marks a PI `is_closed` when its header title contains `closed` (case-insensitive).
- FR-D2-2: A closed PI is never `is_current`, even if its header also contains `(current`.
- FR-D2-3: A closed PI's `pct` is 100, regardless of any unchecked roadmap checkboxes in its body.
- FR-D2-4: `current_pi` skips closed PIs in the unchecked-fallback loop.
- FR-D2-5: When no PI is current and none has unchecked open items, `current_pi` returns the NEWEST PI by trailing number (open PIs preferred; otherwise newest overall), never `pis[0]`.

---

## Non-Goals

- No change to any Article X locked render function (`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`). `render_markdown` is not locked but is not modified either.
- No hand-editing of feature `spec.md` status lines to force a stage. The dashboard must surface truth, not be fed a relabeled input (see RETRO Q-A deviation).
- No change to `done_check.py`'s existing RETRO / artifact enforcement for the DONE *gate* (B-2 regression risk). Only its validation *reader* is widened to glob `validation*.md`. The RETRO requirement is dropped only from the dashboard *stage label*, not from the gate.
- No PI marker flip, no ledger PI activation, no push. Sprint EM owns activation and close.

---

## Acceptance Criteria

- AC-1: A feature with all REQUIRED validation boxes checked renders DONE on the dashboard even with `status: active` in `spec.md` and no `RETRO.md`.
- AC-2: A feature with 0/N REQUIRED boxes checked renders IMPLEMENT (not DONE), even if it has a full set of artifacts.
- AC-3: Split-validation features (`validation-C1.md`, `validation-D2.md`, ...) are counted across all files by both `detect_stage` and `done_check.py`.
- AC-4: A PI header `(closed 2026-07-07)` renders 100% and is not current.
- AC-5: A PI header `(current, closed 2026-07-07)` is not current; the header still resolves to the newest PI.
- AC-6: With every PI closed, `current_pi` returns the newest PI by number, not PI-1.
- AC-7: `TestS1FootprintLockGuard` stays green (no locked-function edit); full suite grows by the new tests.

---

## Traceability

| Requirement | Task | Validation |
|-------------|------|------------|
| FR-D1-1..FR-D1-3 | T-050-01 | R-D1-1, R-D1-2, R-D1-3 |
| FR-D1-4, FR-D1-5 | T-050-02 | R-D1-4, R-D1-5 |
| FR-D2-1..FR-D2-3 | T-050-03 | R-D2-1, R-D2-2, R-D2-3 |
| FR-D2-4, FR-D2-5 | T-050-04 | R-D2-4, R-D2-5 |

---

## Behavior Change Notes

- Shared-helper reconciliation: `detect_stage` now imports the same `required_checked`, `required_unchecked`, `validation_complete`, `validation_files` helpers used by `done_check.py`. One source of truth for "is this feature's validation complete".
- Dropped per-dir RETRO for the DONE dashboard label: a feature with complete REQUIRED validation renders DONE without waiting for a `RETRO.md`. The DONE *gate* (`done_check.py`) still enforces its own rules; only the dashboard stage label relaxed.
- REQUIRED-only unchecked counting: the IMPLEMENT/REVIEW ratio ignores Optional items, so a feature is not held at IMPLEMENT by parked/optional work.
- PI closed -> 100% and newest-PI header fallback: closed PIs are complete by definition and never the current PI; the header never regresses to PI-1.
