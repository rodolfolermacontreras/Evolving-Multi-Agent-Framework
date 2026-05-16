# Implementation Plan: fleet.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-fleet-cli/spec.md`
- Author: Principal Software Developer
- Status: Draft
- Last Updated: 2026-05-16

---

## Approach Summary

Follow CLI-PATTERN.md conventions (LESSON-001). Write tests first (Article X). Reuse `ledger_cli.py` functions for ledger writes and outcome marking -- do not duplicate SQL. Parse tasks.md with regex matching the pipe-delimited table format from the task-list template.

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Tests + tasks.md parser | Spec locked | `test_fleet.py` (red), `parse_tasks_md()` |
| 2 | Dispatch subcommand (brief gen + ledger write) | Phase 1 parser | `dispatch` subcommand, brief renderer |
| 3 | Mark + status subcommands + CLI wiring | Phase 2 | `mark`, `status` subcommands, manual checks |

## Sequential Tasks

1. Write `test_fleet.py` with all 9 test functions from the validation contract.
2. Implement `parse_tasks_md()` -- parse pipe-delimited task table from tasks.md.
3. Implement `render_brief()` -- generate Markdown agent brief from task metadata.
4. Implement `dispatch` subcommand -- parse tasks, check eligibility, render briefs, write ledger rows.
5. Implement `mark` subcommand -- wrap existing ledger mark-outcome.
6. Implement `status` subcommand -- query ledger by feature_dir, format as readable table.
7. Run tests, manual checks, update validation.md checkboxes.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| tasks.md table format varies across features | Medium | Medium | Flexible regex; test with both pilot and template formats |
| Import path to ledger modules from cli/ | Medium | Low | Use sys.path insert or relative path; test import scanner still passes |
| Batch dispatch partial failure (1 of 3 tasks invalid) | Low | Medium | Dispatch all valid tasks, report failures, non-zero exit if any fail |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | S | Parser is regex on known table format |
| 2 | M | Brief rendering + ledger integration |
| 3 | S | Thin wrappers on existing ledger_cli functions |

> **Cross-reference rule:** Use the AC identifiers from `spec.md` (e.g., AC1,
> AC2) instead of restating acceptance criteria prose. Each checkbox below
> should reference the spec AC it validates.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

## Validation Criteria

- [ ] Automated tests in `test_fleet.py` pass (proves AC1-AC9).
- [ ] Manual `--help` checks pass for all subcommands (proves AC10).
- [ ] All required checkboxes in `validation.md` are checked before DONE.
