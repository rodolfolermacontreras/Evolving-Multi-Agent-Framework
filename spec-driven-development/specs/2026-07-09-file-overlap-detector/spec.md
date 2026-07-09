---
id: SDD-20260709FOVL-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-file-overlap-detector
---

# SPEC: SDD-049 -- File-overlap conflict detector for fleet dispatch

- Feature ID: SDD-049
- Sprint: PI-9 / Sprint 1 (Sprint 22)
- CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md) | Validation: [`validation.md`](validation.md)

---

## Goal

Replace the manual per-worker file-scope discipline with an automated pre-dispatch
check. When `fleet.py dispatch` receives a batch of tasks (`--tasks T-A,T-B,...`),
detect when two tasks in that batch declare the same IN-scope file and block the
dispatch before any brief or ledger row is written, unless the operator passes an
explicit override.

## Non-goals

- No cross-batch or cross-feature detection (a single `dispatch` invocation only).
- No filesystem inspection of what a worker *actually* touches -- the detector reads
  *declared* scope from `tasks.md`, the same source `render_brief` already trusts.
- No change to the serial CLARIFY/SPEC lock gate (`_scan_lock_state`, SDD-019).
- No new gate wired into `doctor`/CI (this is a dispatch-time guard, not a health check).

## Requirements

- R1: A `parse_file_scope(cell)` helper normalizes a `File Scope` cell into a set of
  file paths (split on `,`/`;`, strip whitespace + backticks, drop empty and
  placeholder/"none" tokens).
- R2: A pure `detect_file_overlaps(batch)` returns one conflict record per
  overlapping unordered task pair, each with the sorted shared file list, in stable
  order. Single-task and empty/placeholder scopes never conflict.
- R3: `cmd_dispatch` runs the detector AFTER eligibility validation and BEFORE any
  `record_dispatch` / brief write. On overlap with no override it raises `FleetError`
  (non-zero exit) naming the conflicting task pairs and shared files; no ledger row
  or brief is written.
- R4: A `--allow-overlap` flag downgrades a detected overlap to a stderr WARNING and
  proceeds with the dispatch.
- R5: Non-overlapping batches and single-task dispatches are unaffected (no regression
  to existing dispatch behavior).

## Acceptance criteria

- AC1 (R1): `parse_file_scope` strips backticks, splits on both separators, and maps
  placeholder/"none"/empty to the empty set.
- AC2 (R2): `detect_file_overlaps` returns `[]` for disjoint scopes and one record per
  overlapping pair (three identical scopes -> 3 pairs).
- AC3 (R3): an overlapping batch exits non-zero, prints "overlap" + the shared file,
  and writes zero ledger rows.
- AC4 (R4): the same batch with `--allow-overlap` exits 0, warns on stderr, and writes
  one row per task.
- AC5 (R5): a disjoint batch and a single-task dispatch exit 0 and write the expected
  row count.

## Constraints

- Stdlib-only (Article V): `re`, `argparse`, `sqlite3`, `pathlib`, `sys` only.
- Article X: no locked render/load function touched; `TestS1FootprintLockGuard` GREEN.
- Level-1: no `constitution/**` edit, no ADR, no version bump.
