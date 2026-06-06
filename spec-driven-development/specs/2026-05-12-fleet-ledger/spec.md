---
id: SDD-20260512FLEE-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-12-fleet-ledger
---

# Feature Spec: Fleet Ledger v0.1

- Date: 2026-05-12
- Author: Agent INDIA
- Status: Done
- Priority: P2
- Sprint: PI-1
- Spec ID: 2026-05-12-fleet-ledger

---

## Problem Statement

Article VII says every dispatch is logged; the database does not exist. The framework references `spec-driven-development/ledger/fleet.db` as the source of truth for fleet dispatches, but there is no schema, initializer, query tool, or test suite. This makes the framework auditable in theory but not in practice.

## Proposed Solution

Deliver Fleet Ledger v0.1: a minimal stdlib-only SQLite ledger with:

- A `dispatches` table for fleet work assignment and outcomes.
- A `decisions` table for Level 0/1/2 decision capture.
- An idempotent initializer that creates `fleet.db` from `schema.sql`.
- A small CLI that can record dispatches, record decisions, mark outcomes, list dispatches by PI or feature, and summarize by outcome, role, and PI.
- A pytest suite that validates the schema and CLI behavior using temporary databases.

## Acceptance Criteria

Each criterion MUST be phrased as a testable assertion that an automated or manual check can prove true or false.

1. Given an empty database path, when `python spec-driven-development/ledger/init_ledger.py --db <path>` runs, then the database exists with `dispatches` and `decisions` tables plus `idx_dispatches_pi`, `idx_dispatches_feature`, and `idx_dispatches_agent` indexes.
2. Given an existing initialized ledger containing rows, when `init_ledger.py` is re-run against the same path, then existing rows remain and no duplicate schema objects are created.
3. Given valid dispatch metadata, when `ledger_cli.py record-dispatch ...` writes a row, then `ledger_cli.py list-pi <PI>` prints that dispatch back in a readable table.
4. Given an existing dispatch row, when `ledger_cli.py mark-outcome <id> --outcome success` runs, then `dispatches.outcome` and `dispatches.outcome_at` are updated for that row.
5. Given the repository test runner on Windows, Linux, or macOS, when `python -m pytest spec-driven-development/ledger/test_ledger.py -v` runs, then all Fleet Ledger tests pass in the runner default environment.
6. Given the runtime implementation files, when imports are inspected, then they use only Python stdlib modules at runtime (`argparse`, `datetime`, `pathlib`, `sqlite3`, `sys`, and typing helpers as needed).
7. Given the CLI entry points, when `python spec-driven-development/ledger/init_ledger.py --help` and `python spec-driven-development/ledger/ledger_cli.py --help` run, then help text is shown and all supported subcommands are discoverable.

## Affected Modules

- Files:
  - `spec-driven-development/ledger/__init__.py`
  - `spec-driven-development/ledger/schema.sql`
  - `spec-driven-development/ledger/init_ledger.py`
  - `spec-driven-development/ledger/ledger_cli.py`
  - `spec-driven-development/ledger/test_ledger.py`
  - `spec-driven-development/ledger/fleet.db`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/spec.md`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/plan.md`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/tasks.md`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/validation.md`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/clarification-log.md`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/RETRO.md`
  - `spec-driven-development/sprints/PI-1/lessons.md`
- Directories:
  - `spec-driven-development/ledger/`
  - `spec-driven-development/specs/2026-05-12-fleet-ledger/`
  - `spec-driven-development/sprints/PI-1/`

## Data Model Changes

Create the first Fleet Ledger SQLite schema:

- `dispatches`: one row per agent dispatch, with PI/sprint/feature/task/agent metadata and nullable outcome fields for in-flight work.
- `decisions`: one row per decision, with `level` constrained by framework policy to 0, 1, or 2.
- Indexes: `pi`, `feature_dir`, and `agent_id` on `dispatches`.

This is a new schema, so no migration of existing data is required.

## API Changes

No service API. This feature adds a local command-line interface:

- `record-dispatch`
- `record-decision`
- `mark-outcome`
- `list-pi`
- `list-feature`
- `summary`

## Test Strategy

- Unit: Direct tests for `init_ledger.init_ledger`, schema object creation, idempotency, and CLI command functions through `ledger_cli.main`.
- Integration: CLI commands write to and read from a real SQLite database created under pytest `tmp_path`.
- End-to-end/manual: Run `--help` for both scripts, run default `init_ledger.py` twice, and inspect `git status --short` for scoped paths only.
- Regression: Tests ensure dispatch rows survive repeated initialization and summary/list outputs remain readable.

Acceptance Criteria for Tests: pytest is required as a development dependency for this repository test suite. It is not a Fleet Ledger runtime dependency and must not be added to runtime requirements.

## Validation Contract

The binding validation contract for this feature lives in the sibling file `validation.md` in this feature directory. It is written during `/spec`, locked at `/tasks`, and must have zero unchecked required items before implementation can be considered complete.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| Initialize schema | `test_init_creates_schema_objects` | `init_ledger.py`, `schema.sql` |
| Idempotent initialization | `test_init_is_idempotent_and_preserves_rows` | `init_ledger.py` |
| Dispatch round trip | `test_record_dispatch_then_list_pi_round_trip` | `ledger_cli.py` |
| Outcome update | `test_mark_outcome_updates_existing_dispatch` | `ledger_cli.py` |
| Feature filtering | `test_list_feature_filters_by_feature_dir` | `ledger_cli.py` |
| Summary counts | `test_summary_counts_by_outcome_role_and_pi` | `ledger_cli.py` |
| Runtime dependency boundary | `test_runtime_imports_are_stdlib_only` | `init_ledger.py`, `ledger_cli.py` |

## Open Questions

- Should the ledger track worker specialization packs in v0.1? Answered in `clarification-log.md`: no, defer.
- Should the initializer support migrations now? Answered in `clarification-log.md`: no, v0.1 only.

## Out of Scope

- Web UI
- REST API
- Cross-PI analytics beyond simple summary counts
- Agent-specialization or worker-pack tracking
- Schema migrations beyond v0.1
- Non-SQLite database backends
