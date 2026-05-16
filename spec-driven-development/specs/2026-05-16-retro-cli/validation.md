# Validation Contract: retro.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-retro-cli/spec.md`
- Contract Date: 2026-05-16
- Author: Principal Software Developer
- Lock Point: `/tasks`

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Automated Tests

> **Cross-reference rule:** Each test name maps to AC identifiers from `spec.md`.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

- [x] `test_full_retro_produces_all_sections`: proves AC1.
- [x] `test_dispatch_metrics_from_ledger`: proves AC2.
- [x] `test_delivered_features_from_specs`: proves AC3.
- [x] `test_lessons_summary_from_file`: proves AC4.
- [x] `test_output_writes_to_file`: proves AC5.
- [x] `test_sprint_filter`: proves AC6.
- [x] `test_empty_ledger_graceful`: proves AC7.
- [x] `test_runtime_imports_are_stdlib_only`: proves AC8.

## Specific Test Coverage Required

- [x] Unit coverage for metric aggregation, feature scanner, lessons parser.
- [x] Integration coverage for full retro run against seeded tmp_path.
- [x] Edge cases: empty ledger, no specs dir, missing lessons.md.

## Manual Checks

- [x] `python spec-driven-development/cli/retro.py --help` shows --sdd-root, --pi, --sprint, --output.
- [x] `python spec-driven-development/cli/retro.py --sdd-root spec-driven-development --pi PI-2` prints a readable retro to stdout.

## Tone / UX Check

[NO-UX-CHECK-NEEDED] Local developer CLI generating Markdown.

## Definition of Done

All automated tests pass, all manual checks confirmed, validation contract has zero unchecked required items.
