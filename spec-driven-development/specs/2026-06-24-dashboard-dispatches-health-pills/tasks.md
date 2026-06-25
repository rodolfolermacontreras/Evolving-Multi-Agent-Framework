---
id: SDD-20260624DASHHEALTH-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-24
feature: 2026-06-24-dashboard-dispatches-health-pills
---

# TASKS: SDD-037 -- Dispatches card + dashboard health-pills strip

- Feature ID: SDD-037
- Spec: [`spec.md`](./spec.md) | Plan: [`plan.md`](./plan.md) | Validation: [`validation.md`](./validation.md)
- Sprint: PI-6 / Sprint 3 (overall Sprint 12). These tasks are executed at **F-28** (implementation). Authored at F-27 (design-only); all statuses are `TODO`.

---

## No Silent Deferral Rule

If any task cannot be completed as written, the implementer MUST stop and record the blocker in this file (a `### Delta` note) and in [`validation.md`](./validation.md). No requirement may be dropped silently. A REQUIRED validation item may only move to deferred via an explicit Delta entry with rationale and owner sign-off.

## Status Legend

- `TODO` -- not started
- `WIP` -- in progress
- `DONE` -- complete and its required verification passed
- `BLOCKED` -- cannot proceed; blocker recorded

## Baseline Block (capture at start of F-28, T-037-01)

- Pre-F-28 `python -m pytest spec-driven-development/cli/ -q` passed/skipped counts: 399 passed, 2 skipped (the two known skips remain).
- Pre-F-28 `python spec-driven-development/cli/schema_lint.py` exit code: 0.
- `TestS1FootprintLockGuard` status pre-F-28: pass (3 tests).
- Post-F-28 (final): 437 passed, 2 skipped (+38 SDD-037 tests); `schema_lint` exit 0; `TestS1FootprintLockGuard` pass.

## Task Breakdown

| Task ID | Description | File Scope | Required Tests / Verification | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|-----------|-------------------------------|--------|------|------|--------------------------|--------|
| T-037-01 | Capture baseline: pytest passed/skipped counts, `schema_lint` exit, `TestS1FootprintLockGuard` pass; record in Baseline Block. | (read-only) | Commands run; counts recorded in this file | XS | -- | HITL | No (serialized) | DONE |
| T-037-02 | Widen the single ledger read: add an additive grouped/all-rows field to `LedgerView` and populate it inside `load_ledger`'s **existing single `sqlite3.connect`** (leave `recent`/`recent_success`/`blockers`/`available` unchanged); pass it through `build()`. | allowed: `cli/state_builder.py`, `cli/test_state_builder.py` | New tests: grouping by feature->sprint correct; `available` true/false paths; **exactly one** `sqlite3.connect` per build tick (monkeypatch/count); existing `len(ledger.recent)` report unchanged | S | T-037-01 | AFK | No (shared file) | DONE |
| T-037-03 | Add `inject_dispatches_html(html_doc, *, ledger, sdd_root)` + `_DISPATCHES_STYLE`; render grouped card (agent/role/task/status/when); empty-state note when reachable+no rows; disabled-state with reason when `available is False`; wire in `build()` after `inject_lifecycle_html`. Never raise. | allowed: `cli/state_builder.py`, `cli/test_state_builder.py` | New tests: card markers + grouping present (AC-1); empty state (AC-2); disabled state + no raise (AC-3); injected after lifecycle marker | M | T-037-02 | AFK | No (shared file) | DONE |
| T-037-04 | Add four read-only health-check helpers, each returning (status, reason, detail) and never raising: `constitution_semver_status` (read-only `parse_frontmatter` over `constitution/*.md`), `skill_validity_status` (**reuse `schema_lint.check_skill`**), `ledger_reachability_status(ledger)` (from `LedgerView.available`), `stale_tracker_status(..., stale_days=7)` (latest ISO date in `exec/sprint-progress.md`; green<=7/yellow 8-14/red>14/yellow if undatable). | allowed: `cli/state_builder.py`, `cli/test_state_builder.py` | New tests: semver green/yellow/red + no constitution write (AC-6); skill green/red via `check_skill` reuse (AC-7); ledger green/red (AC-8); stale N=7 boundaries + unknown (AC-9); each helper degrade-safe on forced internal error (AC-11) | M | T-037-02 | AFK | No (shared file) | DONE |
| T-037-05 | Add `inject_health_pills_html(html_doc, *, sdd_root, ledger, now=None)` + `_HEALTH_PILLS_STYLE`; render exactly four pills (green/yellow/red); non-green pills anchor to server-rendered `#health-detail-<check>` sections; green pills no link; no JavaScript; wire in `build()` after the Dispatches injector. | allowed: `cli/state_builder.py`, `cli/test_state_builder.py` | New tests: four pills present + colors (AC-5); anchors + detail sections for non-green, none for green (AC-10); document `<script>` count == 0 (AC-5, AC-10) | M | T-037-04, T-037-03 | AFK | No (shared file) | DONE |
| T-037-06 | Invariant guards: assert health checks are indicators only (no raise out of build; `build()` exit unchanged; not wired into any gate); confirm `TestS1FootprintLockGuard` passes; confirm `<script>` count == 0 post-injection. | allowed: `cli/test_state_builder.py` | New tests: indicators-not-gates (AC-11); S1 lock pass (AC-12); no-JS invariant (AC-5) | S | T-037-05 | AFK | No (shared file) | DONE |
| T-037-07 | Regenerate `exec/state.html` via `state_builder`; run `python spec-driven-development/cli/schema_lint.py` (exit 0); run full `cli/` pytest (>= baseline passed + new tests; two known skips unchanged). Update [`validation.md`](./validation.md) REQUIRED items with evidence. | allowed: `exec/state.html` (generated), `cli/test_state_builder.py`; update `validation.md` | `schema_lint` exit 0 (AC-13); full suite green at >= baseline + new (AC-13); validation evidence recorded | S | T-037-06 | HITL | No (serialized) | DONE |

Task budget: 7 tasks (<= 9). All tasks except T-037-04 depend linearly; T-037-03 and T-037-04 both depend on T-037-02 but share the same file, so they run sequentially within the single F-28 session (not in parallel).

## Dependency Graph

```
T-037-01 (baseline)
    |
    v
T-037-02 (ledger widening, single connection)
    |
    +--> T-037-03 (Dispatches card)            shared file -> serialized
    |
    +--> T-037-04 (4 health helpers)           shared file -> serialized
              |
              v
         T-037-05 (health-pills strip)  <- also needs T-037-03 (build wiring order)
              |
              v
         T-037-06 (invariant guards: indicators/S1-lock/no-JS)
              |
              v
         T-037-07 (regenerate + schema_lint 0 + full suite + validation evidence)
```

## Batch Plan

- Single serialized batch (one F-28 session): T-037-01 -> T-037-02 -> T-037-03 -> T-037-04 -> T-037-05 -> T-037-06 -> T-037-07.
- Checkpoint after T-037-05 (both surfaces rendering) before the invariant/regenerate tasks.

## Fleet Dispatch / Serialization Note

**F-28 is NOT fleet-dispatch eligible.** Every task writes to one of two shared files (`cli/state_builder.py`, `cli/test_state_builder.py`), and the two surfaces are interdependent via the shared widened `LedgerView` and the shared `build()` wiring. Concurrent workers would conflict in `cli/state_builder.py`. Execute as a single ordered session. This mirrors the SDD-036 precedent.

## Constraints

- stdlib-only (Article V): argparse, sqlite3, pathlib, json, re, datetime, sys, subprocess, typing, hashlib, html. No third-party imports.
- Do NOT edit the five Article X locked S1 functions; `TestS1FootprintLockGuard` must pass.
- Exactly one `sqlite3.connect` to `fleet.db` per build tick (no second read).
- Read-only over `constitution/**` (Article VIII), `ledger/**`, `exec/sprint-progress.md`.
- No JavaScript; `<script>` count stays 0.
- Health checks never raise out of the build and never become gates.
- `ledger/__init__.py` stays empty; no new ledger schema/table.

## Notes

- All statuses are `TODO`; nothing is implemented at F-27.
- Per-task `allowed:` lists are the only files a task may modify; any other path is blocked.
- Evidence for REQUIRED validation items is recorded in [`validation.md`](./validation.md) at T-037-07.
