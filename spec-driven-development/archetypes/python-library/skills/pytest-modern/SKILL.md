---
name: pytest-modern
description: "Use when designing, writing, or debugging pytest suites for a modern Python library. Covers fixtures, parametrization, property tests with Hypothesis, and command patterns for src-layout packages."
argument-hint: "What Python library behavior or pytest failure should I work on?"
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
  archetype: python-library
---

# Pytest Modern

Pytest patterns for small reusable Python libraries with `pyproject.toml`, `src/` layout, ruff, mypy, and optional Hypothesis property tests.

## When to Use

Load this skill when:

- Writing tests for a new public function, class, module, or exception
- Converting ad-hoc checks into repeatable pytest coverage
- Debugging pytest failures in a library package
- Designing fixtures, parametrized cases, or property tests

Do not load when:

- The task is only packaging metadata or README prose
- The project uses a non-pytest test runner by explicit constitution amendment

## Command Patterns

```bash
# Full suite
python -m pytest

# Quiet summary for fast verification
python -m pytest -q

# One file
python -m pytest tests/test_public_api.py -v --tb=short

# One behavior
python -m pytest tests/test_public_api.py::test_parse_rejects_empty_input -v --tb=short

# Keyword selection
python -m pytest -k "parse and not slow" -v --tb=short
```

If the project uses uv, prefix commands with `uv run`.

## Test Organization

```text
tests/
├── conftest.py
├── test_public_api.py
├── test_errors.py
└── test_regressions.py
```

Mirror user-visible behavior, not private module layout. A private helper usually earns direct tests only when it carries complex logic that is hard to observe through the public API.

## Fixture Guidance

Use fixtures for reusable setup with clear ownership:

```python
import pytest

@pytest.fixture
def sample_config() -> dict[str, str]:
    return {"mode": "strict", "encoding": "utf-8"}


def test_loads_strict_config(sample_config):
    result = load_config(sample_config)
    assert result.mode == "strict"
```

Keep fixtures small. Prefer local arrange code when only one test needs the object.

## Parametrization

Use `pytest.mark.parametrize` for boundary tables:

```python
import pytest

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("alpha", "alpha"),
        (" alpha ", "alpha"),
        ("ALPHA", "alpha"),
    ],
)
def test_normalize_name_accepts_common_forms(raw, expected):
    assert normalize_name(raw) == expected
```

Name cases with `ids=` when failures would otherwise be ambiguous.

## Hypothesis Property Tests

Use Hypothesis when many generated examples clarify invariants:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_normalize_name_is_idempotent(value):
    normalized = normalize_name(value)
    assert normalize_name(normalized) == normalized
```

Do not add Hypothesis casually. It belongs where invariants are stable and generated cases are more valuable than a small hand-written table.

## Assertions and Errors

Assert observable outcomes and helpful error messages:

```python
import pytest


def test_parse_rejects_empty_input():
    with pytest.raises(ValueError, match="input must not be empty"):
        parse_value("")
```

Avoid asserting exact private call chains, local variable names, or implementation-only types.

## Regression Tests

For every confirmed bug:

1. Write a failing test that reproduces the bug.
2. Confirm it fails for the expected reason.
3. Implement the smallest fix.
4. Keep the test permanently as a regression guard.
