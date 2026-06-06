---
id: SDD-20260512FLEE-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-12-fleet-ledger
---

# Validation Contract: Fleet Ledger v0.1

- Spec Reference: `spec-driven-development/specs/2026-05-12-fleet-ledger/spec.md`
- Contract Date: 2026-05-12
- Author: Agent INDIA
- Lock Point: `/tasks`

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Automated Tests

- [x] `test_init_creates_schema_objects`: proves AC1 schema creation.
- [x] `test_init_is_idempotent_and_preserves_rows`: proves AC2 idempotent initialization.
- [x] `test_record_dispatch_then_list_pi_round_trip`: proves AC3 dispatch write/list round trip.
- [x] `test_mark_outcome_updates_existing_dispatch`: proves AC4 outcome update.
- [x] `test_summary_counts_by_outcome_role_and_pi`: proves AC5 summary behavior.
- [x] `test_runtime_imports_are_stdlib_only`: proves AC6 no third-party runtime dependencies.

## Specific Test Coverage Required

- [x] Unit coverage for schema initialization, row insert helpers, outcome updates, and summary aggregation.
- [x] Integration coverage for CLI commands against a real SQLite file under pytest `tmp_path`.
- [x] Regression coverage for repeated initialization preserving existing dispatch rows.
- [x] Error, empty, boundary, or permission cases: missing PI list returns a no-dispatch message; invalid outcome exits with parser error; missing dispatch id returns non-zero.

## Manual Checks

- [x] `python spec-driven-development/ledger/init_ledger.py --help` shows usage.
- [x] `python spec-driven-development/ledger/ledger_cli.py --help` shows usage with `record-dispatch`, `record-decision`, `mark-outcome`, `list-pi`, `list-feature`, and `summary`.
- [x] `python spec-driven-development/ledger/init_ledger.py` can be run twice with no error and leaves `fleet.db` initialized.
- [x] `git status --short` shows only paths in the Agent INDIA file scope.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] This is a local developer CLI and schema feature; no end-user visual UI is introduced.

- [x] CLI output is readable in a terminal and command help text is clear enough for framework contributors.

## Definition of Done

Implementation is merge-ready only when all automated tests listed above pass,
all required manual checks are confirmed, the branch is rebased cleanly, no debug
prints or throwaway instrumentation remain, and this validation contract has zero
unchecked required items. Any skipped item must include a written justification
accepted by the spec-compliance reviewer. Production-code changes without a
corresponding test require a task-level `[NO-TEST-NEEDED]` tag and accepted
justification before the IMPLEMENT gate can pass.
