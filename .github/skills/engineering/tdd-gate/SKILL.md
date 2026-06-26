---
name: tdd-gate
description: "Use during spec compliance review. Mechanically checks a diff for test-first compliance: production code added without corresponding test code is flagged unless the task is explicitly tagged [NO-TEST-NEEDED]."
argument-hint: "Which diff or commit range should I check?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# TDD Gate

Use this skill during spec-compliance review to mechanically check whether a
change respects Article X: production-code changes need corresponding test
changes unless the task is explicitly tagged `[NO-TEST-NEEDED]` with an accepted
written justification.

## Inputs

- A diff, commit SHA, branch comparison, or commit range.
- The task description or implementation handoff, so the reviewer can see whether
  `[NO-TEST-NEEDED]` was declared and justified.
- The feature directory, when available, so `validation.md` can be cross-checked.

## Mechanical Check

1. List files added or modified in the diff.
2. Classify production-code paths. Treat source, application, CLI, API, model,
   component, migration, and script paths as production unless the repository has
   a stronger convention.
3. Classify test paths. Common signals include `test`, `tests`, `spec`,
   `__tests__`, `.test.`, `.spec.`, `pytest`, `playwright`, or documented
   framework-specific test directories.
4. Ignore docs-only, template-only, ADR-only, prompt-only, and pure configuration
   changes unless they execute production behavior.
5. Return PASS when every production-code change has at least one corresponding
   test-file change or the task carries an accepted `[NO-TEST-NEEDED]`
   justification.
6. Return FAIL when production code changed and no matching test change or
   accepted escape hatch exists.

## Corresponding Test Heuristic

A test file corresponds when it covers the same feature, module, route, command,
component, public behavior, or validation-contract checkbox. Exact filename
matching is helpful but not required; reviewer judgment is allowed when the
relationship is clear.

## Escape Hatch

`[NO-TEST-NEEDED]` is not a loophole for convenience. It is valid only when the
task description includes a written reason, such as docs-only behavior, generated
metadata, impossible-to-automate manual verification, or a change explicitly
covered by existing tests. The spec-compliance reviewer must accept or reject the
justification in writing.

## Reviewer Output

Return one of:

- `PASS`: production-code changes have corresponding test changes.
- `PASS WITH NO-TEST JUSTIFICATION`: no test change exists, but the accepted
  `[NO-TEST-NEEDED]` justification is present.
- `FAIL`: production-code changes lack corresponding tests and lack an accepted
  escape hatch.

For failures, list each production-code file that triggered the gate and the
missing test or missing justification required to pass.

## Enforced by

This skill's mechanical check is automated by
`spec-driven-development/cli/tdd_gate_check.py`, which `make doctor` runs as the
`tdd gate` check on every push and pull request. The skill is the human-readable
rationale; the script is the blocking gate.
