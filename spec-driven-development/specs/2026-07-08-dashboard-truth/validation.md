---
id: SDD-20260708DASHBOARDTRUTH-validation
type: validation
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: 2026-07-08-dashboard-truth
depends_on: [SDD-046]
---

# VALIDATION: SDD-050 -- "Dashboard truth"

- Feature ID: SDD-050. Sprint: PI-8 Sprint 18.
- Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Tasks: [tasks.md](tasks.md).

---

## Lock Statement

This contract is LOCKED at design time. Implementation may not add, remove, or weaken a REQUIRED item to make the feature pass.

DA-Evidence Discipline applies to every REQUIRED item: the box may be checked ONLY after a real command was run end-to-end and its artifact/output read. No item is satisfied by prediction, by "the code looks right", or by a harness that simulates the outcome. Each item names the command that proves it.

---

## Required Items

### Defect 1 -- Evidence-first stage detection

- [x] R-D1-1: A feature with all REQUIRED validation boxes checked renders DONE even with `status: active` and no `RETRO.md`. Proof: `detect_stage` unit test on a seeded feature dir. (AC-1, FR-D1-1)
    - PROVEN 2026-07-08: `TestSdd050DetectStage` GREEN in full-suite run (576 passed / 2 skipped). Evidence-first branch (validation-complete -> DONE) exercised.
- [x] R-D1-2: A feature with 0/N REQUIRED boxes checked renders IMPLEMENT, not DONE, even with a full artifact set. Proof: `detect_stage` unit test + real detect_stage run against sdd-048 (0/19 REQUIRED). (AC-2, FR-D1-2)
    - PROVEN 2026-07-08: real `detect_stage` run on sdd-048-maintainability -> ('IMPLEMENT','active','validation required 0% (0/19)'). Force-DONE prediction reversed. `TestSdd050DetectStage` IMPLEMENT case GREEN.
- [x] R-D1-3: REVIEW at >= 80% checked ratio, IMPLEMENT below, using REQUIRED-only counts (optional excluded). Proof: `detect_stage` ratio tests. (FR-D1-2)
    - PROVEN 2026-07-08: `TestSdd050DetectStage` REVIEW/IMPLEMENT ratio cases GREEN within full suite.
- [x] R-D1-4: `done_check.py` counts REQUIRED items across every `validation*.md`, not just `validation.md`. Proof: real detect_stage/done_check run against split-validation features. (AC-3, FR-D1-4)
    - PROVEN 2026-07-08: real run on sdd-047 (split validation files) -> ('DONE','done',...); sdd-048 four split files -> 0/19 aggregated. Both counted across files, confirming the glob reader.
- [x] R-D1-5: `detect_stage` and `done_check.py` share one validation-completeness reader (no divergence). Proof: `detect_stage` dual-imports `required_checked`/`required_unchecked`/`validation_complete`/`validation_files` from `done_check`; both agree on sdd-047 (DONE) and sdd-048 (IMPLEMENT). (FR-D1-5)
    - PROVEN 2026-07-08: shared helpers imported (ADR-012 dual-import); full suite 576 GREEN with both consumers on the same reader.

### Defect 2 -- PI closed handling

- [x] R-D2-1: `load_pis` marks a PI `is_closed` when its header title contains `closed`. Proof: `TestSdd050PiClosed::test_load_pis_marks_closed_pi`. (FR-D2-1)
    - PROVEN 2026-07-08: `TestSdd050PiClosed` 5/5 passed (sub-scope run + full suite).
- [x] R-D2-2: A closed PI is never `is_current`, even with `(current` in the header. Proof: `test_closed_and_current_title_closed_wins`. (FR-D2-2)
    - PROVEN 2026-07-08: `test_closed_and_current_title_closed_wins` GREEN (real PI-7 `(current, closed 2026-07-07)` -> is_current False).
- [x] R-D2-3: A closed PI's `pct` is 100 regardless of unchecked roadmap boxes. Proof: `test_closed_pi_pct_is_100_even_with_unchecked`. (FR-D2-3)
    - PROVEN 2026-07-08: `test_closed_pi_pct_is_100_even_with_unchecked` GREEN.
- [x] R-D2-4: `current_pi` unchecked-fallback skips closed PIs. Proof: `test_current_pi_unchecked_fallback_skips_closed`. (FR-D2-4)
    - PROVEN 2026-07-08: `test_current_pi_unchecked_fallback_skips_closed` GREEN.
- [x] R-D2-5: With all PIs closed, `current_pi` returns the newest PI by number, never `pis[0]`. Proof: `test_current_pi_fallback_returns_newest_when_all_closed`. (AC-6, FR-D2-5)
    - PROVEN 2026-07-08: `test_current_pi_fallback_returns_newest_when_all_closed` GREEN.

### Cross-cutting -- no regression, no lock break

- [x] R-X-1: `TestS1FootprintLockGuard` stays PASS (no Article X locked-function edit). Proof: lock-guard subset run. (AC-7)
    - PROVEN 2026-07-08: `pytest -k "Footprint or footprint or LockGuard"` -> 3 passed (golden SHA-256 intact). Changes confined to `state_builder_data.py` + `done_check.py`.
- [x] R-X-2: Full suite grows and stays green. Proof: repo-root full-suite run. (AC-7)
    - PROVEN 2026-07-08: `python -m pytest spec-driven-development/ -q` -> 576 passed / 2 skipped (73.02s). Arc 558 -> 571 (Defect 1) -> 576 (Defect 2).
- [x] R-X-3: `schema_lint.py` exit 0 and `origin_lint.py` clean. Proof: both run. (AC-7)
    - PROVEN 2026-07-08: `schema_lint.py` -> "Schema lint clean" exit 0; `origin_lint.py` -> "origin-lint: clean" exit 0.
- [x] R-X-4: Dashboard regeneration shows truth. Proof: `state_builder.py` (no `--pi`) run; done set / in-progress set / closed-PI 100% / header = newest open PI read from output. (AC-1..AC-6)
    - PROVEN 2026-07-08: see RETRO.md "Smoke Test" -- make-promises-true + sdd-047 render DONE; sdd-048 + azure-decommission + three 0%-carryover PI-7 features render in-progress; closed PIs at 100%; header resolves to newest open PI (PI-7; PI-6 is a roadmap gap), not PI-1.

---

## Optional Items

- [ ] O-1: Backfill stale `spec.md` status lines to match rendered stage. DEFERRED -- contrary to SDD-050 intent (surface truth, do not relabel inputs). Evidence-justified Q-A(5)->Q-A(0). Tracked in RETRO.md.
