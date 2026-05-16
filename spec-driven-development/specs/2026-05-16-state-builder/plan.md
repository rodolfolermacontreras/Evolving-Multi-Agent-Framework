# Implementation Plan: state_builder.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-state-builder/spec.md`
- Author: Principal Software Developer
- Status: Draft
- Last Updated: 2026-05-16

---

## Approach Summary

Follow the CLI-PATTERN.md conventions (LESSON-001). Write tests first (Article X), then implement section-builder functions one at a time, wiring them into a main builder that writes the full state.md. Use the fleet ledger's existing `init_ledger` and `sqlite3` patterns for database reads.

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Tests + section parsers (pipeline, backlog, roster) | Spec locked, validation contract locked | `test_state_builder.py` (red), section-parser functions |
| 2 | Ledger queries + blocker detection | Phase 1 parsers | Ledger read functions, blocker logic |
| 3 | Main builder + CLI wiring + manual checks | Phases 1-2 | Full `state_builder.py`, passing tests, `--help` and `--dry-run` verified |

## Parallel-Safe Tasks

- Lifecycle artifacts (clarification-log, plan, tasks) can be drafted in parallel with test writing -- Files: `specs/2026-05-16-state-builder/*.md`

## Sequential Tasks

> **Cross-reference rule:** In the Acceptance Test column, reference the spec's
> AC identifiers (e.g., "proves AC1, AC3") and the validation contract checkbox
> names rather than restating criteria. This prevents prose duplication.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

1. Write `test_state_builder.py` first and confirm initial red state.
2. Implement section parsers: pipeline from specs/, sprint plan from backlog, fleet counts from roster.
3. Implement ledger readers: recently completed, blockers.
4. Implement main builder that composes all sections into the 7-section output.
5. Implement CLI wiring: `--sdd-root`, `--dry-run`, `--pi`, `--help`.
6. Run automated tests until green, then manual checks.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Spec frontmatter format varies across existing spec.md files | Medium | Low | Parse `Status:` line with regex; tolerate missing field gracefully |
| BACKLOG.md table parsing is fragile | Medium | Medium | Parse with simple line-by-line regex for pipe-delimited tables; test with real backlog content |
| fleet.db may not exist when builder runs | Low | Medium | Graceful fallback: empty Recently Completed and Blockers sections with a note |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | S | Markdown/JSON parsing is straightforward |
| 2 | S | Two simple SQL queries against known schema |
| 3 | M | CLI wiring, output formatting, manual verification |

> **Cross-reference rule:** Use the AC identifiers from `spec.md` (e.g., AC1,
> AC2) instead of restating acceptance criteria prose. Each checkbox below
> should reference the spec AC it validates.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

## Validation Criteria

- [ ] Automated tests in `test_state_builder.py` pass (proves AC1-AC8, AC10).
- [ ] Manual `--help` check passes (proves AC9).
- [ ] Manual `--dry-run` against real repo produces readable output (proves AC10).
- [ ] All required checkboxes in `validation.md` are checked before DONE.
