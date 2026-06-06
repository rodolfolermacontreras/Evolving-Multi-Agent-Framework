---
id: SDD-20260516FLEE-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-16-fleet-cli
---

# Validation Contract: fleet.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-fleet-cli/spec.md`
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

- [x] `test_dispatch_prints_brief_to_stdout`: proves AC1 -- brief contains task ID, description, file scope, acceptance test, agent role.
- [x] `test_dispatch_writes_ledger_row`: proves AC2 -- dispatch row in fleet.db with correct fields.
- [x] `test_batch_dispatch_multiple_tasks`: proves AC3 -- 3 tasks = 3 briefs + 3 ledger rows.
- [x] `test_dispatch_saves_briefs_to_output_dir`: proves AC4 -- files saved as dispatch-ID-TASKID.md.
- [x] `test_mark_outcome_updates_dispatch`: proves AC5 -- outcome and outcome_at updated.
- [x] `test_status_lists_feature_dispatches`: proves AC6 -- readable table with dispatch ID, task, agent, outcome.
- [x] `test_ineligible_task_rejected`: proves AC7 -- task with Fleet Dispatch Eligible = No is rejected.
- [x] `test_missing_tasks_md_error`: proves AC8 -- clear error when tasks.md absent.
- [x] `test_runtime_imports_are_stdlib_only`: proves AC9 -- no third-party runtime imports.

## Specific Test Coverage Required

- [x] Unit coverage for task-list parser (parse_tasks_md), brief renderer, eligibility checker.
- [x] Integration coverage for full dispatch + mark + status cycle against a tmp_path fleet.db.
- [x] Regression coverage for batch dispatch producing correct sequential dispatch IDs.
- [x] Error/edge cases: missing tasks.md, invalid task ID, invalid outcome value, empty feature dir.

## Manual Checks

- [x] `python spec-driven-development/cli/fleet.py --help` shows subcommands: dispatch, mark, status.
- [x] `python spec-driven-development/cli/fleet.py dispatch --help` shows --feature, --tasks, --agent, --pi, --sprint, --output-dir, --notes.
- [x] `python spec-driven-development/cli/fleet.py mark --help` shows --dispatch-id, --outcome, --notes.
- [x] `python spec-driven-development/cli/fleet.py status --help` shows --feature, --pi.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] This is a local developer CLI. No end-user visual UI is introduced.

## Definition of Done

Implementation is merge-ready only when all automated tests listed above pass,
all required manual checks are confirmed, the branch is rebased cleanly, no debug
prints or throwaway instrumentation remain, and this validation contract has zero
unchecked required items. Any skipped item must include a written justification
accepted by the spec-compliance reviewer. Production-code changes without a
corresponding test require a task-level `[NO-TEST-NEEDED]` tag and accepted
justification before the IMPLEMENT gate can pass.
