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
python -m pytest --nbval notebooks  # when notebooks are authoritative
```

If the project uses uv, prefix Python commands with `uv run`.

## Article X Validation Contract

Article X requires validation before implementation. For this archetype, a passing validation contract means:

- The intended behavior, input, output, failure modes, and acceptance checks are specified before code changes
- The idiomatic first test or validation check fails for the right reason before implementation when practical
- The happy path and at least one important failure or edge case are covered
- Dependency, data, persistence, packaging, or reproducibility impacts are documented when relevant
- The feature can be run locally from documented commands

## Testing Standards

- Add regression tests for every confirmed bug before fixing it.
- Prefer observable behavior over implementation details.
- Keep fixtures small, explicit, and portable.
- Do not rely on private credentials, machine-specific paths, or execution order.

## Release Readiness

A release or milestone is ready only when validation gates, README quickstart, and clean-checkout setup all succeed or have an approved exception.
