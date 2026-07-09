---
id: SDD-20260709REOPT-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-reorder-backend-reoptimization
---

# SPEC: SDD-054 -- Backlog reorder -> backend re-optimization (SDD-041 Option B)

- Feature ID: SDD-054
- Sprint: PI-9 / Sprint 1 (Sprint 22)
- CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md) | Validation: [`validation.md`](validation.md)

---

## Goal

Make a backlog reorder feed the backend prioritization logic, not only the display
overlay. When an item is dragged (via the existing safeguarded `move()`), the new
order is turned into a persisted, dependency-corrected, RICE-annotated, scored
**effective-priority ranking** the backend consumes.

## Non-goals

- Do NOT mutate `BACKLOG.md` RICE scores (ADR-017: BACKLOG.md stays PM-authoritative).
- Do NOT change Option A's display overlay contract (`display-order.json`) or its
  audit-row shape.
- Do NOT touch any Article X locked render/load function.
- No new dependency-lock rule -- reuse the Option A dependency check verbatim.

## Requirements

- R1: `load_backlog_entries` also parses each row's RICE priority (P1-P4, cell 2),
  defaulting to P3 when absent/unparseable.
- R2: `compute_effective_priority(order, entries, depends_map)` returns one record
  per item in effective-rank order: `{id, manual_rank, effective_rank,
  rice_priority, priority_weight, priority_score}`, with the manual order as the
  primary signal, made dependency-legal (incomplete-dependency demotion), and a
  descending-integer `priority_score`.
- R3: `reoptimize(sdd_root)` recomputes from the current display order + BACKLOG
  state, persists `backlog/effective-priority.json`, and returns the ranking.
- R4: `move()` calls `reoptimize()` after writing the overlay + the single audit
  row (no extra audit row; same dependency-lock governance).
- R5: `effective_priority_order(sdd_root)` returns the backend priority order
  (feature IDs), reading the persisted artifact or recomputing when absent -- the
  function a prioritization consumer calls.
- R6: A `reoptimize` CLI subcommand recomputes + persists on demand (text/json).

## Acceptance criteria

- AC1 (R1): entries carry `priority`; done + priority parsed correctly.
- AC2 (R2): scored ranking with descending `priority_score` and RICE annotation;
  an item above an incomplete dependency is demoted below it.
- AC3 (R3/R4): a legal `move` writes `effective-priority.json` and still appends
  exactly one audit row.
- AC4 (R5): `effective_priority_order` reflects the persisted ranking after a move.
- AC5 (R6): `reoptimize` subcommand exits 0 and writes the artifact.
- AC6 (non-goal): `BACKLOG.md` is byte-identical after a move+reoptimize.

## Constraints

- Stdlib-only (Article V): `json`, `re`, `argparse`, `pathlib`, `datetime`, `sys`.
- Article X: no locked function touched; `TestS1FootprintLockGuard` GREEN.
- Level-1: no `constitution/**` edit, no ADR, no version bump.
