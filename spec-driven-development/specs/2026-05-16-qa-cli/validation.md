---
id: SDD-20260516QACL-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-16-qa-cli
---

# Validation Contract: qa.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-qa-cli/spec.md`
- Contract Date: 2026-05-16
- Author: Principal Software Developer
- Lock Point: `/tasks`

---

## Automated Tests

> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

- [x] `test_validation_checkbox_report`: proves AC1.
- [x] `test_ac_crossref_missing_and_extra`: proves AC2.
- [x] `test_task_status_check`: proves AC3.
- [x] `test_bare_except_scan`: proves AC4.
- [x] `test_debug_print_scan`: proves AC5.
- [x] `test_report_has_two_stages`: proves AC6.
- [x] `test_compliant_exit_zero`: proves AC7.
- [x] `test_not_compliant_exit_one`: proves AC8.
- [x] `test_runtime_imports_are_stdlib_only`: proves AC9.

## Specific Test Coverage Required

- [x] Unit coverage for each scanner function.
- [x] Integration coverage for full qa run against seeded tmp_path.
- [x] Edge cases: perfect feature, missing validation.md, missing test file.

## Manual Checks

- [x] `python spec-driven-development/cli/qa.py --help` shows subcommand `check`.
- [x] `python spec-driven-development/cli/qa.py check --help` shows --feature, --impl, --test.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] Local developer CLI.

## Definition of Done

All automated tests pass, all manual checks confirmed, zero unchecked items.
