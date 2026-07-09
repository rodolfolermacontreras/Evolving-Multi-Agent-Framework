---
id: SDD-20260709REOPT-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-07-09
feature: 2026-07-09-reorder-backend-reoptimization
---

# PLAN: SDD-054 -- Backlog reorder -> backend re-optimization

- Feature ID: SDD-054
- Spec: [`spec.md`](spec.md) | Tasks: [`tasks.md`](tasks.md)

---

## Approach

Extend `cli/backlog_reorder.py` additively (build on Option A's `move()`/audit):

1. Add `PRIORITY_WEIGHT = {P1:4,P2:3,P3:2,P4:1}`; extend `BacklogEntry` with
   `priority` and parse cell 2 in `load_backlog_entries` (default P3).
2. `_dependency_correct_order(order, depends_map, done_map)` -- stable pass that
   demotes any item ranked above an incomplete dependency to just after it.
3. `compute_effective_priority(order, entries, depends_map)` -- dependency-correct
   then annotate with manual_rank / effective_rank / rice_priority /
   priority_weight / descending priority_score.
4. `write_effective_priority` / `load_effective_priority` -> `backlog/effective-priority.json`.
5. `reoptimize(sdd_root)` -- recompute from current overlay + persist.
6. `effective_priority_order(sdd_root)` -- backend consumer API.
7. Call `reoptimize()` at the end of `move()` (after overlay + single audit row).
8. Add the `reoptimize` CLI subcommand (text/json).

## TDD sequence

Write failing tests first in `cli/test_backlog_reorder.py` (`EffectivePriority`
class: RICE parse, scored ranking, dependency demotion, move writes artifact,
one audit row, consumer order, subcommand, BACKLOG untouched), then implement.

## Risk / rollback

Additive; Option A's overlay + audit contract unchanged (move still appends exactly
one audit row; `reoptimize` writes a separate JSON artifact, no audit). Rollback =
remove the new functions + the one `move()` call + subcommand.

## Lock safety

Leaf module `backlog_reorder.py`; no Article X locked function touched;
`TestS1FootprintLockGuard` stays GREEN.
