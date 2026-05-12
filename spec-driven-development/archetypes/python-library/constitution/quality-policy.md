---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Quality Policy

## Required Gates

Before merge or release, {{PROJECT_NAME}} should pass these gates unless {{OWNER}} explicitly approves an exception:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

If the project uses uv, equivalent commands may be:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Testing Standards

- New public behavior starts with a failing pytest test when practical.
- Parametrize boundary cases instead of copying similar test bodies.
- Use fixtures for repeated setup, but keep fixture behavior obvious.
- Add regression tests for every confirmed bug before fixing it.
- Avoid tests that only assert implementation details.

## Type and Lint Standards

- Public functions and classes include type hints.
- Internal helpers are typed when they carry non-trivial data structures.
- Ruff formatting is the source of truth for style.
- Mypy errors are fixed rather than suppressed unless the suppression is explained.

## Documentation Standards

- README examples must be runnable or clearly marked as illustrative.
- Public errors should include remediation guidance.
- Release notes call out breaking changes, deprecations, and migration steps.

## Release Readiness

A release is ready only when tests, linting, type checking, README quickstart, and package build all succeed from a clean checkout.
