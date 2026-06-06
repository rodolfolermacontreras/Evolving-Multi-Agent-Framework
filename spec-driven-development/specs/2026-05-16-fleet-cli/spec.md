---
id: SDD-20260516FLEE-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-16-fleet-cli
---

# Feature Spec: fleet.py

- Date: 2026-05-16
- Author: Principal Software Developer
- Status: Done
- Priority: P2
- Sprint: PI-2 Sprint A
- Spec ID: 2026-05-16-fleet-cli

---

## Problem Statement

The framework has a fleet ledger (fleet.db) and a low-level CLI for recording dispatches (ledger_cli.py), but no orchestration tool that reads task lists, generates dispatch packets, assigns agents, and writes ledger rows in a single command. Today, dispatching a task to a worker requires the human to manually compose the agent brief, manually call ledger_cli.py to record the dispatch, and mentally track which tasks have been assigned. This is error-prone and un-traceable at scale.

## Proposed Solution

Implement `cli/fleet.py` as a stdlib-only Python CLI that:

1. **Parses tasks.md** from a feature directory to extract task metadata (ID, description, file scope, acceptance test, effort, deps, fleet-dispatch eligibility).
2. **Generates dispatch packets**: a Markdown agent brief per task (matching `templates/agent-brief.md` structure) printed to stdout or saved to an output directory.
3. **Writes dispatch rows** to `fleet.db` via the existing `ledger_cli.py` functions (reuse `record_dispatch`).
4. **Supports batch dispatch**: multiple tasks in one command (`--tasks T-001,T-002,T-003`), each getting its own brief and ledger row.
5. **Supports outcome marking**: `fleet.py mark --dispatch-id <id> --outcome success|failed|blocked` wrapping `ledger_cli.py mark-outcome`.
6. **Lists active dispatches**: `fleet.py status --feature <dir>` showing in-flight and completed tasks.

Human launches agents manually after reviewing the generated briefs. No programmatic agent invocation in v1.

## Acceptance Criteria

1. Given a feature directory with a `tasks.md` containing parseable task rows, when `fleet.py dispatch --feature <dir> --tasks T-001 --agent developer-general --pi PI-2` runs, then a Markdown agent brief is printed to stdout containing the task ID, description, file scope, acceptance test, and agent role.
2. Given the same command, when the dispatch runs, then a row is written to `fleet.db` dispatches table with matching pi, feature_dir, task_id, task_title, agent_id, agent_role, and dispatched_at fields.
3. Given `--tasks T-001,T-002,T-003`, when batch dispatch runs, then one brief is printed per task and one ledger row is written per task, with sequential dispatch IDs returned.
4. Given `--output-dir <path>`, when dispatch runs, then each brief is saved as `<path>/dispatch-<id>-<task_id>.md` instead of printing to stdout.
5. Given a dispatch ID, when `fleet.py mark --dispatch-id <id> --outcome success` runs, then `dispatches.outcome` and `dispatches.outcome_at` are updated in fleet.db.
6. Given a feature directory, when `fleet.py status --feature <dir>` runs, then all dispatches for that feature are listed in a readable table with dispatch ID, task, agent, outcome, and timestamps.
7. Given a `tasks.md` with a task marked `Fleet Dispatch Eligible = No`, when that task ID is included in `--tasks`, then the dispatch is rejected with a clear error message and no ledger row is written for that task.
8. Given `tasks.md` does not exist in the feature directory, when dispatch is attempted, then the command exits with a clear error message explaining that tasks.md is required.
9. Given the runtime implementation files, when imports are inspected, then they use only Python stdlib modules at runtime (plus the existing `ledger/` modules via relative import or sys.path).
10. Given `fleet.py --help`, `fleet.py dispatch --help`, `fleet.py mark --help`, and `fleet.py status --help`, when run, then help text is shown with all supported arguments.

## Affected Modules

- Files:
  - `spec-driven-development/cli/fleet.py` (replace scaffold)
  - `spec-driven-development/cli/test_fleet.py` (new)
  - `spec-driven-development/ledger/fleet.db` (dispatch rows written at runtime)
  - `spec-driven-development/specs/2026-05-16-fleet-cli/spec.md`
  - `spec-driven-development/specs/2026-05-16-fleet-cli/clarification-log.md`
  - `spec-driven-development/specs/2026-05-16-fleet-cli/plan.md`
  - `spec-driven-development/specs/2026-05-16-fleet-cli/tasks.md`
  - `spec-driven-development/specs/2026-05-16-fleet-cli/validation.md`
- Directories:
  - `spec-driven-development/cli/`
  - `spec-driven-development/specs/2026-05-16-fleet-cli/`

## Data Model Changes

None. Uses the existing `dispatches` and `decisions` tables in `fleet.db`.

## API Changes

No service API. Local CLI with three subcommands:

- `fleet.py dispatch --feature <dir> --tasks T-001[,T-002,...] --agent <agent-id> --pi <PI> [--sprint <sprint>] [--output-dir <path>] [--notes <text>]`
- `fleet.py mark --dispatch-id <id> --outcome success|failed|blocked [--notes <text>]`
- `fleet.py status --feature <dir> [--pi <PI>]`

## Test Strategy

- Unit: Direct tests for task-list parser (parse_tasks_md), brief generator (render_brief), dispatch-to-ledger writer, and eligibility checker.
- Integration: Full dispatch command against a tmp_path with a seeded tasks.md and temporary fleet.db; assert ledger rows and brief content.
- End-to-end/manual: Run `--help` for all subcommands; run a dispatch against a real feature directory in `--dry-run` or `--output-dir` mode.
- Regression: Batch dispatch of 3 tasks produces 3 briefs and 3 ledger rows with correct metadata.

## Validation Contract

The binding validation contract for this feature lives in the sibling file `validation.md` in this feature directory.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| AC1: Brief output | `test_dispatch_prints_brief_to_stdout` | `fleet.py` |
| AC2: Ledger row written | `test_dispatch_writes_ledger_row` | `fleet.py` |
| AC3: Batch dispatch | `test_batch_dispatch_multiple_tasks` | `fleet.py` |
| AC4: Output dir saves files | `test_dispatch_saves_briefs_to_output_dir` | `fleet.py` |
| AC5: Mark outcome | `test_mark_outcome_updates_dispatch` | `fleet.py` |
| AC6: Status listing | `test_status_lists_feature_dispatches` | `fleet.py` |
| AC7: Eligibility check | `test_ineligible_task_rejected` | `fleet.py` |
| AC8: Missing tasks.md error | `test_missing_tasks_md_error` | `fleet.py` |
| AC9: Stdlib-only runtime | `test_runtime_imports_are_stdlib_only` | `fleet.py` |
| AC10: Help text | Manual check | `fleet.py` |

## Open Questions

None. All resolved in `clarification-log.md`.

## Out of Scope

- Programmatic agent invocation (launching VS Code Copilot Chat agents from CLI)
- Conflict detection between parallel dispatches (Sprint C scope)
- Worker specialization tracking
- Auto-assignment of agents based on task metadata
- Web UI or dashboard for dispatch management
