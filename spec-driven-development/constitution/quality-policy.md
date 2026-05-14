---
version: '1.0.0'
ratified: 2026-05-12
last_amended: 2026-05-12
---

# Quality Policy

## Test Baseline

The test suite must never regress.

- Every code change ships with tests
- Test count at merge must be >= test count at branch creation
- Failing tests block merge -- no exceptions
- Run tests per the host project's test conventions (e.g., `python -m pytest <test-path> -v --tb=short`)
- The framework's own tests: `python -m pytest spec-driven-development/ledger/test_ledger.py -v`

## Two-Stage Code Review

All non-trivial implementations go through two review stages in order.
Do not proceed to Stage 2 until Stage 1 passes.

### Stage 1: Spec Compliance Review

Reviewer: Principal Software Developer (or PM for acceptance criteria)

Check for:
- MISSING: requirements in `spec.md` that are not implemented (FR-NNN, AC-NNN)
- EXTRA: features implemented that were not requested (scope creep)
- WRONG: behavior that contradicts the spec

Output: `COMPLIANT` or `NOT COMPLIANT` with specific FR/AC references.
Do NOT comment on code quality during Stage 1.

### Stage 2: Code Quality Review

Reviewer: Principal Software Developer (+ Architect for cross-cutting changes)
Only runs after Stage 1 passes.

Issue classification:
- CRITICAL: must fix before merge (security, correctness, data loss)
- IMPORTANT: should fix (maintainability, performance)
- SUGGESTION: nice to have (naming, style)

Check for:
- Error handling completeness (no bare `except:`)
- Edge cases (null, empty, boundary values)
- Security: input validation and path sanitization appropriate to the host stack
- No new dependencies introduced without Level 2 approval
- No emojis anywhere

## Validation by Change Type

| Change Type | Required Validation |
|-------------|---------------------|
| Schema / data model change | CRUD tests, migration compatibility, tmp_path isolation |
| CLI script | Targeted pytest, `--help` smoke check, stdlib-only import scan |
| Agent / skill / prompt | Link/path sanity and constitution consistency |
| Docs / spec only | Link/path sanity and constitution consistency |

Host projects should extend this table with stack-specific rows (e.g., backend
routes, UI templates, LLM workflows) in their own `quality-policy.md`.

## Security Conventions

These are not optional:

- Validate and sanitize all external input at system boundaries
- Never store credentials or tokens in code, logs, or committed files
- Use environment variables for secrets
- Host projects document their stack-specific security helpers (e.g., path
  sanitization, HTML escaping, CSRF protection) in their own `quality-policy.md`

## SDD Scorecard Metrics

Tracked per sprint in `spec-driven-development/docs/SCORECARD.md`:

| Metric | Definition | Target |
|--------|------------|--------|
| Spec compliance rate | Tasks with zero spec deviations / total tasks | >= 95% |
| Test delta | New tests added per feature | >= 1 per FR |
| Review rejection rate | Stage 1 rejections / total reviews | <= 20% |
| Cycle time | Idea to merged PR (days) | <= 14 |
| Fleet success rate | Parallel dispatches with zero conflicts / total fleet runs | >= 80% |
| Escalation rate | Level 2 stops per sprint | <= 2 |

## Definition of Done

A task is done when ALL of the following are true:

- [ ] Implementation matches the spec (Stage 1 passes)
- [ ] Code quality review passes (Stage 2 passes or SUGGESTION-only)
- [ ] Test count >= baseline
- [ ] All new tests pass
- [ ] Committed with `type: short description` format
- [ ] Merged to integration branch via feature branch
- [ ] Sprint board updated (if applicable)
