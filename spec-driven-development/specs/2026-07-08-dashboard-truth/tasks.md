---
id: SDD-20260708DASHBOARDTRUTH-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: 2026-07-08-dashboard-truth
depends_on: [SDD-046]
---

# TASKS: SDD-050 -- "Dashboard truth"

- Feature ID: SDD-050. Sprint: PI-8 Sprint 18.
- Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Validation: [validation.md](validation.md).

---

## No Silent Deferral Rule

Every task below is either DONE this feature or explicitly marked `blocked` / `deferred` with a reason in Notes. A task may not vanish.

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete, tests pass, reviewed
- `blocked` -- cannot proceed (reason in Notes)

## Baseline Block

- Test baseline at design time: 558 passed / 2 skipped (Sprint 17 close).
- Baseline only grows. F must end at >= 576 passed / 2 skipped.
- `python spec-driven-development/cli/schema_lint.py` must exit 0.
- `TestS1FootprintLockGuard` must stay PASS (no locked-function edit).

---

## Task Breakdown

| Task ID | Description | File Scope | Required Tests | Effort | Deps | Mode | Fleet-Eligible | Status |
|---------|-------------|-----------|----------------|--------|------|------|----------------|--------|
| T-050-01 | Rewrite `detect_stage` evidence-first: validation-complete -> DONE (no RETRO gate); REQUIRED-only ratio -> REVIEW>=80% else IMPLEMENT (never DONE); artifact + normalized-status fallback | `cli/state_builder_data.py` | `TestSdd050DetectStage`: DONE on all-checked+status:active+no-retro; IMPLEMENT on 0/N; REVIEW at >=80%; artifact fallbacks | M | none | serial (state_builder_data.py) | No | done |
| T-050-02 | Widen `done_check.py` validation reader to glob `validation*.md`; expose `required_checked`/`required_unchecked`/`validation_complete`/`validation_files` for shared import | `cli/done_check.py` | split-validation counted across all files; DONE gate unchanged (RETRO/artifact still enforced) | M | none | parallel | Yes | done |
| T-050-03 | Add `PIBlock.is_closed` (after `checkboxes`); `pct`=100 when closed; `load_pis` sets `is_closed="closed" in title`, `is_current` requires `not is_closed` | `cli/state_builder_data.py` | `TestSdd050PiClosed`: closed marked; closed+current -> closed wins; closed pct=100 with unchecked | M | T-050-01 | serial (state_builder_data.py) | No | done |
| T-050-04 | Add `_pi_number` helper; `current_pi` unchecked-fallback skips closed; final fallback = newest open PI by number (never `pis[0]`) | `cli/state_builder_data.py` | `TestSdd050PiClosed`: all-closed -> newest; unchecked-fallback skips closed | S | T-050-03 | serial (state_builder_data.py) | No | done |

- Fleet-eligible count: 1 (T-050-02). T-050-01/03/04 share `state_builder_data.py` -> serial by file-conflict rule.

---

## Notes

- T-050-01, T-050-03, T-050-04 all edit `cli/state_builder_data.py`; per the file-conflict rule they are serial and were implemented in one context, not fleet-dispatched in parallel.
- T-050-02 edits a different file (`done_check.py`) and is Fleet-eligible; it is the task logged to the ledger for the PI-8 dogfood row.
- No task deferred. All four tasks `done`.
