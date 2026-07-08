---
id: SDD-20260708DASHBOARDTRUTH-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: 2026-07-08-dashboard-truth
depends_on: [SDD-046]
---

# PLAN: SDD-050 -- "Dashboard truth"

- Feature ID: SDD-050. Sprint: PI-8 Sprint 18.
- Spec: [spec.md](spec.md). Tasks: [tasks.md](tasks.md). Validation: [validation.md](validation.md).

---

## Approach

Two defects, both isolated to leaf data functions. No render-path (Article X) function is touched, so the S1 footprint lock stays byte-identical. TDD throughout: failing test first, then the smallest evidence-first implementation.

### Defect 1 -- `detect_stage` evidence-first + shared validation reader

`cli/done_check.py` already parses REQUIRED/optional validation boxes for the DONE gate. Widen its reader to glob `validation*.md` (not just `validation.md`) and expose `required_checked`, `required_unchecked`, `validation_complete`, `validation_files` as importable helpers. Rewrite `detect_stage` in `cli/state_builder_data.py` to consume those helpers via ADR-012 dual-import:

1. If validation has REQUIRED items and all are checked -> DONE (no RETRO gate for the label).
1b. Else if an explicit normalized `spec.md` status is present -> use it.
2. Else if REQUIRED items exist -> REVIEW when checked ratio >= 80%, else IMPLEMENT (never DONE). Optional items excluded from the ratio.
3. Else artifact fallback: tasks -> TASKS, plan -> PLAN, spec -> SPEC, design/clarify -> CLARIFY, else BACKLOG.

### Defect 2 -- PI closed handling in `load_pis` / `current_pi`

Add `is_closed: bool = False` to `PIBlock` (after `checkboxes`, so existing positional/kwarg constructions keep working). `pct` returns 100 when closed. In `load_pis`, set `is_closed = "closed" in title.lower()` and `is_current = "(current" in title.lower() and not is_closed`. Add a `_pi_number` helper (trailing int of the PI name). In `current_pi`, add a `not p.is_closed` guard to the unchecked-fallback loop and replace the final `pis[0]` fallback with the newest PI by number (open PIs preferred).

---

## Affected Files

| File | Change | Locked? |
|------|--------|---------|
| `cli/state_builder_data.py` | `detect_stage` rewrite; `PIBlock.is_closed` + `pct`; `load_pis` closed detection; `_pi_number`; `current_pi` fallback | No (leaf data module) |
| `cli/done_check.py` | glob `validation*.md`; expose shared helpers | No |
| `cli/test_state_builder.py` | new `TestSdd050DetectStage`, `TestSdd050PiClosed` | test |
| `cli/test_done_check.py` (or equivalent) | split-validation counting tests | test |

Not touched: `state_builder.py` facade (re-exports only), `state_builder_html.py`, `state_builder_markdown.py`, `constitution/**`.

---

## Test Strategy

- TDD RED first for every requirement; confirm the failure mode (AttributeError / TypeError / wrong stage) before implementing.
- Full suite from repo root: `python -m pytest spec-driven-development/ --tb=short -q`.
- Lock guard: `python -m pytest spec-driven-development/ -k "Footprint or footprint or LockGuard"` -> 3 passed.
- Gates: `schema_lint.py` exit 0, `origin_lint.py` clean, `done_check.py` on the SDD-050 dir PASS.
- Smoke: regenerate the dashboard and confirm DONE set vs in-progress set, closed PIs at 100%, header = newest open PI.

## Baseline

- Design-time baseline: 558 passed / 2 skipped (Sprint 17 close).
- Baseline only grows: Defect 1 -> 571; Defect 2 -> 576. End >= 576 passed / 2 skipped.

## Risks

- Widening `done_check.py`'s reader could regress the DONE gate. Mitigation: keep RETRO/artifact gate rules; only the validation file glob changes.
- Evidence-first `detect_stage` could force a genuinely-incomplete feature to DONE. Mitigation: DONE requires all REQUIRED boxes checked (0/N stays IMPLEMENT). Verified against sdd-048 (0/19 REQUIRED) -> stays IMPLEMENT.
