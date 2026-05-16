# Validation Contract: state_builder.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-state-builder/spec.md`
- Contract Date: 2026-05-16
- Author: Principal Software Developer
- Lock Point: `/tasks`

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Automated Tests

> **Cross-reference rule:** Each test name below maps to one or more AC
> identifiers from `spec.md`. Use the format `proves AC1` to link the
> test to its requirement. The spec is the single source of truth for
> acceptance criteria wording.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

- [x] `test_full_build_produces_all_sections`: proves AC1 -- output contains all 7 section headers and a correct date.
- [x] `test_recently_completed_from_dispatches`: proves AC2 -- successful dispatches appear in Recently Completed.
- [x] `test_blockers_from_stale_dispatches`: proves AC3 -- dispatches with NULL outcome older than 24h appear in Blockers.
- [x] `test_pipeline_from_spec_dirs`: proves AC4 -- spec dirs with Status lines produce pipeline table rows.
- [x] `test_sprint_plan_from_backlog`: proves AC5 -- backlog sprint assignments produce grouped sprint plan.
- [x] `test_fleet_counts_from_roster`: proves AC6 -- roster JSON files produce correct principal/worker/skill counts.
- [x] `test_deterministic_output`: proves AC7 -- two runs with same data produce byte-identical output.
- [x] `test_runtime_imports_are_stdlib_only`: proves AC8 -- no third-party runtime imports.
- [x] `test_dry_run_prints_to_stdout`: proves AC10 -- dry-run mode writes to stdout, not to file.

## Specific Test Coverage Required

- [x] Unit coverage for each section-builder function (pipeline, backlog, ledger queries, roster, blockers, milestones).
- [x] Integration coverage for full builder run against a seeded tmp_path environment.
- [x] Regression coverage for deterministic output across repeated runs.
- [x] Error/edge cases: missing fleet.db returns graceful message; empty specs/ produces empty pipeline; empty backlog produces "no items" note.

## Manual Checks

- [x] `python spec-driven-development/cli/state_builder.py --help` shows usage with `--sdd-root`, `--dry-run`, and `--pi` arguments.
- [x] `python spec-driven-development/cli/state_builder.py --sdd-root spec-driven-development --dry-run` produces readable state output to stdout.
- [x] Running the builder against the real repo produces output structurally consistent with the current hand-written `state.md`.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] This is a local developer CLI that generates a Markdown file. No end-user visual UI is introduced.

## Definition of Done

Implementation is merge-ready only when all automated tests listed above pass,
all required manual checks are confirmed, the branch is rebased cleanly, no debug
prints or throwaway instrumentation remain, and this validation contract has zero
unchecked required items. Any skipped item must include a written justification
accepted by the spec-compliance reviewer. Production-code changes without a
corresponding test require a task-level `[NO-TEST-NEEDED]` tag and accepted
justification before the IMPLEMENT gate can pass.
