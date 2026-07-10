---
id: SDD-20260709REOPT-validation
type: validation
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-reorder-backend-reoptimization
---

# VALIDATION: SDD-054 -- Backlog reorder -> backend re-optimization (SDD-041 Option B)

- Feature ID: SDD-054
- Sprint: PI-9 / Sprint 1 (Sprint 22); design + implementation F-61
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)

---

## Lock Statement

Contract LOCKED at F-61 design. Implementation MUST satisfy every REQUIRED item
(R-1..R-7) with evidence and MUST NOT loosen, drop, or silently defer any REQUIRED
item. If a REQUIRED item cannot be met, implementation stops and surfaces it to the
owner via the DECISION-REQUEST FORMAT.

---

## Required Items (Strict)

- [x] **R-1 (RICE parse).** `load_backlog_entries` parses each row's RICE priority
  (P1-P4, cell 2) and done state, defaulting to P3. (AC1) -- EVIDENCE:
  `test_backlog_entries_parse_rice_priority` PASS.
- [x] **R-2 (scored, RICE-annotated ranking).** `compute_effective_priority` returns
  per-item `{id, manual_rank, effective_rank, rice_priority, priority_weight,
  priority_score}` with descending `priority_score` and the manual order as primary
  signal. (AC2) -- EVIDENCE: `test_compute_blends_manual_and_rice_into_scored_ranking`
  PASS.
- [x] **R-3 (dependency-legal re-optimization).** An item ranked above an incomplete
  dependency is demoted below it in the effective order (reuses the Option A
  dependency check). (AC2) -- EVIDENCE:
  `test_dependency_correction_demotes_below_incomplete_dep` PASS.
- [x] **R-4 (move feeds the backend, one audit row).** A legal `move` writes
  `backlog/effective-priority.json` AND still appends exactly one audit row (no
  double-logging). (AC3) -- EVIDENCE: `test_move_writes_effective_priority_artifact`
  + `test_move_still_appends_exactly_one_audit_row` PASS.
- [x] **R-5 (backend consumer API).** `effective_priority_order` returns the persisted
  effective priority order after a move. (AC4) -- EVIDENCE:
  `test_effective_priority_order_reads_persisted_ranking` PASS.
- [x] **R-6 (on-demand subcommand).** `reoptimize` CLI subcommand exits 0 and writes
  the artifact. (AC5) -- EVIDENCE:
  `test_reoptimize_subcommand_exits_zero_and_writes_artifact` PASS.
- [x] **R-7 (ADR-017 held + Article X + Level-1).** `BACKLOG.md` is byte-identical
  after move+reoptimize (RICE source not mutated); no locked function touched
  (`TestS1FootprintLockGuard` PASS); stdlib-only; no `constitution/**` edit, no ADR,
  no version bump. (AC6 / constraints) -- EVIDENCE:
  `test_backlog_md_not_mutated_by_reoptimization` PASS; `-k FootprintLockGuard` PASS;
  only `cli/backlog_reorder.py` + `cli/test_backlog_reorder.py` + this spec dir edited.

---

## Manual Checks (at close)

- [x] **M-1 (full suite).** `pytest spec-driven-development/` >= 596 passed / 2
  skipped, growing by the 8 new SDD-054 cases -- 616 passed / 2 skipped locally
  at F-62 close.
- [x] **M-2 (lints).** schema + origin + staledoc lint clean locally at F-62 close.
- [x] **M-3 (doctor + CI).** Local doctor green at F-62 close (616 passed / 2
  skipped; all checks PASS). CI is pending the owner-approved push and is not
  claimed pre-push.
