# Validation Contract: qa.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-qa-cli/spec.md`
- Contract Date: 2026-05-16
- Author: Principal Software Developer
- Lock Point: `/tasks`

---

## Automated Tests

> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

- [ ] `test_validation_checkbox_report`: proves AC1.
- [ ] `test_ac_crossref_missing_and_extra`: proves AC2.
- [ ] `test_task_status_check`: proves AC3.
- [ ] `test_bare_except_scan`: proves AC4.
- [ ] `test_debug_print_scan`: proves AC5.
- [ ] `test_report_has_two_stages`: proves AC6.
- [ ] `test_compliant_exit_zero`: proves AC7.
- [ ] `test_not_compliant_exit_one`: proves AC8.
- [ ] `test_runtime_imports_are_stdlib_only`: proves AC9.

## Specific Test Coverage Required

- [ ] Unit coverage for each scanner function.
- [ ] Integration coverage for full qa run against seeded tmp_path.
- [ ] Edge cases: perfect feature, missing validation.md, missing test file.

## Manual Checks

- [ ] `python spec-driven-development/cli/qa.py --help` shows subcommand `check`.
- [ ] `python spec-driven-development/cli/qa.py check --help` shows --feature, --impl, --test.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] Local developer CLI.

## Definition of Done

All automated tests pass, all manual checks confirmed, zero unchecked items.
