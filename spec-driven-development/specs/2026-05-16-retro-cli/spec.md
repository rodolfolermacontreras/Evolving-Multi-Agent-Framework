# Feature Spec: retro.py

- Date: 2026-05-16
- Author: Principal Software Developer
- Status: Draft
- Priority: P2
- Sprint: PI-2 Sprint B
- Spec ID: 2026-05-16-retro-cli

---

## Problem Statement

The `/retro` slash command runs in Copilot Chat and requires the human to manually gather sprint context. There is no CLI tool that can automatically collect dispatch metrics from the ledger, scan completed feature artifacts, and generate a structured retrospective document. This makes retros dependent on agent availability and chat context rather than repeatable automation.

## Proposed Solution

Implement `cli/retro.py` as a stdlib-only Python CLI that:

1. **Queries fleet.db** for dispatches in the target PI/sprint: total dispatches, success/failed/blocked counts, unique agents, unique features.
2. **Scans spec directories** for features that reached DONE in the target period (have RETRO.md or status=Done in spec.md).
3. **Reads lessons.md** for the target PI to list open and shipped lessons.
4. **Generates a structured Markdown retro** matching the `/retro` prompt output format: sprint goal, delivered items, went well, signals/evidence, and a lessons summary.
5. **Prints to stdout by default**, with `--output <path>` to write to a file.

The retro document is a *draft* -- the human and PM review it, add "went well" / "did not go well" commentary, and finalize action items.

## Acceptance Criteria

1. Given a valid `--sdd-root` and `--pi PI-2`, when `retro.py --sdd-root <path> --pi PI-2` runs, then a Markdown document is printed to stdout with sections: header, Delivered, Signals and Evidence, Lessons Summary.
2. Given fleet.db with dispatches for PI-2, when the retro runs, then the Signals section shows dispatch counts (total, success, failed, blocked), unique agent count, and unique feature count.
3. Given `specs/` containing a feature directory with `Status: Done` in spec.md, when the retro runs, then that feature appears in the Delivered section with its name and completion evidence.
4. Given `sprints/PI-1/lessons.md` with lesson entries, when `--pi PI-1` is passed, then the Lessons Summary section lists lessons with their status (shipped/open/deferred).
5. Given `--output sprints/PI-2/retro-sprint-b.md`, when the retro runs, then the document is written to that path instead of stdout.
6. Given `--sprint "Sprint A"`, when passed, then the header and dispatch queries filter to that sprint value.
7. Given no dispatches in fleet.db for the target PI, when the retro runs, then the Signals section shows zero counts with a note "no dispatches recorded."
8. Given the runtime implementation files, when imports are inspected, then they use only Python stdlib modules at runtime (plus framework-internal ledger modules).
9. Given `retro.py --help`, when run, then help text is shown with all supported arguments.

## Affected Modules

- Files:
  - `spec-driven-development/cli/retro.py` (replace scaffold)
  - `spec-driven-development/cli/test_retro.py` (new)
- Directories:
  - `spec-driven-development/cli/`
  - `spec-driven-development/specs/2026-05-16-retro-cli/`

## Data Model Changes

None. Read-only access to fleet.db and Markdown artifacts.

## API Changes

No service API. Local CLI:

- `retro.py --sdd-root <path> --pi <PI> [--sprint <sprint>] [--output <path>]`
- `retro.py --help`

## Test Strategy

- Unit: Tests for dispatch metric aggregation, feature scanner, lessons parser.
- Integration: Full retro run against a tmp_path with seeded fleet.db, specs/, and lessons.md.
- Edge cases: empty ledger, no specs, missing lessons.md.

## Validation Contract

The binding validation contract lives in the sibling `validation.md`.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| AC1: Full retro output | `test_full_retro_produces_all_sections` | `retro.py` |
| AC2: Dispatch metrics | `test_dispatch_metrics_from_ledger` | `retro.py` |
| AC3: Delivered features | `test_delivered_features_from_specs` | `retro.py` |
| AC4: Lessons summary | `test_lessons_summary_from_file` | `retro.py` |
| AC5: Output to file | `test_output_writes_to_file` | `retro.py` |
| AC6: Sprint filter | `test_sprint_filter` | `retro.py` |
| AC7: Empty ledger graceful | `test_empty_ledger_graceful` | `retro.py` |
| AC8: Stdlib-only | `test_runtime_imports_are_stdlib_only` | `retro.py` |
| AC9: Help text | Manual check | `retro.py` |

## Out of Scope

- "Went well" / "did not go well" commentary (human-authored)
- Action items (human-authored during review)
- Historical retro comparison across PIs
- Web UI
