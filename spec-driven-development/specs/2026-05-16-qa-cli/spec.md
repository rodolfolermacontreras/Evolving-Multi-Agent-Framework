# Feature Spec: qa.py

- Date: 2026-05-16
- Author: Principal Software Developer
- Status: Done
- Priority: P2
- Sprint: PI-2 Sprint B
- Spec ID: 2026-05-16-qa-cli

---

## Problem Statement

The framework requires two-stage review (Article III) but has no automation to assist reviewers. Today, spec-compliance review is entirely manual: a reviewer opens validation.md, spec.md, and the implementation files side by side, and mentally cross-references them. This is slow and error-prone, especially for features with 10+ acceptance criteria.

## Proposed Solution

Implement `cli/qa.py` as a stdlib-only Python CLI that automates the mechanical parts of both review stages:

**Stage 1 -- Spec Compliance:**
1. Parse `validation.md` checkboxes -- report checked vs unchecked count.
2. Cross-reference AC identifiers in `spec.md` against test function names in the test file -- detect MISSING (AC has no test) and EXTRA (test has no AC).
3. Check that all tasks in `tasks.md` are marked `done`.

**Stage 2 -- Code Quality (mechanical checks only):**
4. Scan implementation files for bare `except:` statements.
5. Scan for `print()` calls that look like debug statements (not stderr).
6. Scan for stdlib-only runtime imports (reuse the pattern from other CLIs).

Output: a structured Markdown report with PASS/FAIL per check, suitable for the reviewer to annotate with human findings.

## Acceptance Criteria

1. Given a feature directory with `validation.md`, when `qa.py check --feature <dir>` runs, then a report is printed showing checked/unchecked validation counts and listing any unchecked items.
2. Given `spec.md` with AC identifiers (AC1, AC2, etc.) and a test file, when the cross-reference runs, then MISSING ACs (no matching test) and EXTRA tests (no matching AC) are listed.
3. Given `tasks.md` with task rows, when the task-status check runs, then any task not marked `done` is flagged.
4. Given implementation Python files, when the bare-except scan runs, then lines with bare `except:` are flagged as CRITICAL.
5. Given implementation Python files, when the debug-print scan runs, then `print(` calls not writing to `sys.stderr` are flagged as WARNING.
6. Given `--feature <dir>`, when qa.py runs, then the report has two sections: "Stage 1: Spec Compliance" and "Stage 2: Code Quality."
7. Given all checks pass, when qa.py runs, then it exits with code 0 and prints "COMPLIANT" at the end.
8. Given any Stage 1 check fails, when qa.py runs, then it exits with code 1 and prints "NOT COMPLIANT" with the specific failures.
9. Given the runtime files, when imports are inspected, then they use only Python stdlib modules.
10. Given `qa.py --help` and `qa.py check --help`, when run, then help text is shown.

## Affected Modules

- Files:
  - `spec-driven-development/cli/qa.py` (replace scaffold)
  - `spec-driven-development/cli/test_qa.py` (new)
- Directories:
  - `spec-driven-development/cli/`
  - `spec-driven-development/specs/2026-05-16-qa-cli/`

## Data Model Changes

None. Read-only scan of Markdown and Python files.

## API Changes

Local CLI:

- `qa.py check --feature <dir> [--impl <file-or-dir>] [--test <file>]`
- `qa.py --help`

## Test Strategy

- Unit: Tests for validation parser, AC cross-referencer, task status checker, bare-except scanner, debug-print scanner.
- Integration: Full qa run against a tmp_path with seeded feature dir and implementation files.
- Edge cases: perfect feature (all pass), missing validation.md, missing test file.

## Validation Contract

Lives in sibling `validation.md`.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| AC1: Validation checkbox count | `test_validation_checkbox_report` | `qa.py` |
| AC2: AC cross-reference | `test_ac_crossref_missing_and_extra` | `qa.py` |
| AC3: Task status check | `test_task_status_check` | `qa.py` |
| AC4: Bare except scan | `test_bare_except_scan` | `qa.py` |
| AC5: Debug print scan | `test_debug_print_scan` | `qa.py` |
| AC6: Two-section report | `test_report_has_two_stages` | `qa.py` |
| AC7: Compliant exit 0 | `test_compliant_exit_zero` | `qa.py` |
| AC8: Not compliant exit 1 | `test_not_compliant_exit_one` | `qa.py` |
| AC9: Stdlib-only | `test_runtime_imports_are_stdlib_only` | `qa.py` |
| AC10: Help text | Manual check | `qa.py` |

## Out of Scope

- Human-judgment code quality review (naming, design, architecture)
- Security-specific scanning (OWASP checks)
- Automated fix suggestions
- Integration with CI/CD pipelines
