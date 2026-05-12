---
version: '1.0.0'
ratified: 2026-05-12
last_amended: 2026-05-12
---

# Quality Policy

## Test Baseline

The test suite must never regress. Current baseline: **743 tests, 36 files**.

- Every code change ships with tests
- Test count at merge must be >= test count at branch creation
- Failing tests block merge -- no exceptions
- Run the full suite: `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short`

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
- Security: `safe_path()` for file paths, `esc()` for HTML output
- Concurrency: `file_lock()` for JSON store access
- Pydantic models for all POST endpoints (`agent/schemas.py`)
- No new dependencies introduced without Level 2 approval
- No emojis anywhere

## Validation by Change Type

| Change Type | Required Validation |
|-------------|---------------------|
| Backend route | Targeted pytest, Pydantic validation, safe_path/esc review |
| DB/model change | CRUD tests, migration compatibility, tmp_path isolation |
| HTMX/UI | Route + template test, accessibility review |
| LLM workflow | MockLLMClient test, prompt grounding, observability check |
| Status report | Renderer sanity test, sidecar override test |
| M365/MSAL | Mocked Graph flow, no token logging |
| Docs/spec only | Link/path sanity and constitution consistency |

## Security Conventions

These are not optional:

- File path from user input -> `safe_path(base, *parts)` from `agent/routes/__init__.py`
- User content in HTML template -> `esc(text)` from `agent/routes/__init__.py`
- API mutation endpoint -> Pydantic model in `agent/schemas.py`, returns 422 on failure
- JSON store read/write -> `file_lock()` from `agent/utils.py` (thread RLock + OS lock)
- Credentials/tokens -> environment variables only, never in code or logs

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
- [ ] Merged to `integration/improvements` via feature branch
- [ ] `BOARD.md` updated in the current sprint
