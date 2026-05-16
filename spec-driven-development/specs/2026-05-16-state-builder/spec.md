# Feature Spec: state_builder.py

- Date: 2026-05-16
- Author: Principal Software Developer (routed by Executive Manager)
- Status: Draft
- Priority: P2
- Sprint: PI-2 Sprint A
- Spec ID: 2026-05-16-state-builder

---

## Problem Statement

The Executive Manager reads `exec/state.md` as its default context source. Today that file is authored manually, which means it drifts from reality between sessions. The framework has no automated way to regenerate `state.md` from the fleet ledger and artifact directories. This creates a silent-drift risk: the Executive Manager briefs the human from stale data.

## Proposed Solution

Implement `cli/state_builder.py` as a stdlib-only Python CLI that reads from two source categories:

1. **Fleet Ledger** (`ledger/fleet.db`): dispatches table for recent activity, outcomes, and blockers; decisions table for recent Level 1/2 decisions.
2. **Markdown/JSON artifacts on disk**: `specs/*/spec.md` for the pipeline table, `backlog/BACKLOG.md` for sprint assignments and pending items, `roster/agents.json` and `roster/skills.json` for fleet counts.

The output is a complete `exec/state.md` in the 7-section format the Executive Manager consumes: header, spec pipeline, sprint plan (derived from backlog sprint assignments), fleet summary, recently completed, blockers, and next milestones.

## Acceptance Criteria

1. Given a valid `--sdd-root` path, when `python state_builder.py --sdd-root <path>` runs, then `exec/state.md` is written with all 7 sections and a `Generated date:` matching today's date.
2. Given an initialized `fleet.db` with at least one dispatch row with `outcome='success'`, when the builder runs, then the Recently Completed section lists that dispatch's `task_title` and `feature_dir`.
3. Given an initialized `fleet.db` with a dispatch row where `outcome IS NULL` and `dispatched_at` is older than 24 hours, when the builder runs, then the Blockers section lists that dispatch as a potential stuck task.
4. Given `specs/` containing directories with `spec.md` files that have a `Status:` line, when the builder runs, then the Spec Pipeline table includes one row per feature directory with the correct gate status.
5. Given `backlog/BACKLOG.md` containing rows with Sprint column values, when the builder runs, then the Sprint Plan section groups features by sprint assignment.
6. Given `roster/agents.json` and `roster/skills.json`, when the builder runs, then the Fleet section shows correct counts for principals, generic workers, specialists, and skills.
7. Given the builder runs twice with no underlying data changes, when the two outputs are compared, then they are byte-identical (deterministic output).
8. Given the runtime implementation files, when imports are inspected, then they use only Python stdlib modules at runtime.
9. Given `python state_builder.py --help`, when run, then help text is shown with all supported arguments.
10. Given `python state_builder.py --sdd-root <path> --dry-run`, when run, then the output is printed to stdout instead of writing to `exec/state.md`.

## Affected Modules

- Files:
  - `spec-driven-development/cli/state_builder.py` (replace scaffold)
  - `spec-driven-development/exec/state.md` (output target)
  - `spec-driven-development/specs/2026-05-16-state-builder/spec.md`
  - `spec-driven-development/specs/2026-05-16-state-builder/clarification-log.md`
  - `spec-driven-development/specs/2026-05-16-state-builder/plan.md`
  - `spec-driven-development/specs/2026-05-16-state-builder/tasks.md`
  - `spec-driven-development/specs/2026-05-16-state-builder/validation.md`
- Directories:
  - `spec-driven-development/cli/`
  - `spec-driven-development/specs/2026-05-16-state-builder/`

## Data Model Changes

None. Reads from the existing fleet ledger schema and Markdown artifacts. No new tables or columns.

## API Changes

No service API. Local CLI:

- `state_builder.py --sdd-root <path>` -- generate state.md (writes to `exec/state.md`)
- `state_builder.py --sdd-root <path> --dry-run` -- print to stdout instead of writing
- `state_builder.py --sdd-root <path> --pi <PI-N>` -- override the current PI label
- `state_builder.py --help` -- show usage

## Test Strategy

- Unit: Direct tests for each section-builder function (pipeline parser, backlog parser, ledger queries, roster counter, blocker detector).
- Integration: Full builder run against a tmp_path with seeded `fleet.db`, `specs/`, `backlog/`, and `roster/` directories; assert the output matches expected Markdown.
- End-to-end/manual: Run `--help`, run `--dry-run` against the real repo, diff output against the current hand-written `state.md`.
- Regression: Determinism test -- run twice, assert byte-identical output.

## Validation Contract

The binding validation contract for this feature lives in the sibling file `validation.md` in this feature directory. It is written during `/spec`, locked at `/tasks`, and must have zero unchecked required items before implementation can be considered complete.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| AC1: Full 7-section output | `test_full_build_produces_all_sections` | `state_builder.py` |
| AC2: Recently Completed from ledger | `test_recently_completed_from_dispatches` | `state_builder.py` |
| AC3: Blockers from stale dispatches | `test_blockers_from_stale_dispatches` | `state_builder.py` |
| AC4: Spec Pipeline from specs/ dirs | `test_pipeline_from_spec_dirs` | `state_builder.py` |
| AC5: Sprint Plan from backlog | `test_sprint_plan_from_backlog` | `state_builder.py` |
| AC6: Fleet counts from roster JSONs | `test_fleet_counts_from_roster` | `state_builder.py` |
| AC7: Deterministic output | `test_deterministic_output` | `state_builder.py` |
| AC8: Stdlib-only runtime | `test_runtime_imports_are_stdlib_only` | `state_builder.py` |
| AC9: Help text | Manual `--help` check | `state_builder.py` |
| AC10: Dry-run mode | `test_dry_run_prints_to_stdout` | `state_builder.py` |

## Open Questions

None. All resolved in `clarification-log.md`.

## Out of Scope

- Writing to any file other than `exec/state.md`
- Reading from or writing to the fleet ledger (read-only)
- Historical state snapshots or diffing
- Web API or dashboard rendering
- Automatic scheduling or cron-like execution
