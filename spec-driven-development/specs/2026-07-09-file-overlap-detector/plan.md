---
id: SDD-20260709FOVL-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-07-09
feature: 2026-07-09-file-overlap-detector
---

# PLAN: SDD-049 -- File-overlap conflict detector

- Feature ID: SDD-049
- Spec: [`spec.md`](spec.md) | Tasks: [`tasks.md`](tasks.md)

---

## Approach

Add three small pure helpers to `cli/fleet.py` next to `is_eligible`, then wire a
single guard block into `cmd_dispatch`:

1. `parse_file_scope(cell) -> set[str]` -- normalize a `File Scope` cell (mirrors
   `render_brief` parsing; drops placeholder/"none" tokens).
2. `detect_file_overlaps(batch) -> list[dict]` -- pairwise intersection over the
   batch, stable order, one record per overlapping pair.
3. `format_overlap_report(conflicts) -> str` -- human-readable indented list.
4. Guard in `cmd_dispatch`: after `resolved` is built and BEFORE the ledger loop,
   compute overlaps; block (raise `FleetError`) by default or warn under
   `--allow-overlap`.
5. Add the `--allow-overlap` store-true flag to the `dispatch` subparser.

## TDD sequence

- Write failing tests first in `cli/test_fleet.py`:
  - `TestFileScopeParsing` (AC1)
  - `TestDetectFileOverlaps` (AC2)
  - `TestDispatchOverlapGate` (AC3/AC4/AC5), using an `OVERLAP_TASKS_MD` fixture with
    two tasks sharing `cli/shared.py` and one disjoint task.
- Implement helpers + guard until green.

## Risk / rollback

- Pure, additive functions + one guard block; no existing behavior changed for
  disjoint or single-task dispatch. Rollback = remove the guard block + flag + helpers.

## Lock safety

`cmd_dispatch` and the helpers are leaf CLI code. No Article X locked function is
touched; `TestS1FootprintLockGuard` stays GREEN.
