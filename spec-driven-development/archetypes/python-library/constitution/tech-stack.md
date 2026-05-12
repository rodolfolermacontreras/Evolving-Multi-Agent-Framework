---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Tech Stack

## Runtime

- Language: Python 3.10+ unless the project deliberately raises the floor
- Package metadata: `pyproject.toml`
- Source layout: `src/{{PROJECT_NAME}}/` or a normalized import package name chosen during PI-1
- Supported platforms: Windows, Linux, and macOS

## Packaging

- Build backend: hatchling by default, or another PEP 517 backend documented in `pyproject.toml`
- Environment manager: uv preferred for local development; pip remains supported for consumers
- Distribution targets: wheel and source distribution
- Versioning: semantic versioning once the public API stabilizes

## Testing

- Test runner: pytest
- Test layout: `tests/` mirrors public behavior and bug regressions
- Optional property tests: Hypothesis for parser, validator, serializer, and boundary-heavy logic
- Coverage target: establish a baseline in PI-1 and raise it deliberately

## Quality Tools

- Formatter and linter: ruff
- Type checker: mypy
- Import safety: package import must not perform expensive work or hidden side effects
- Documentation: README first, then API examples and docstrings for public symbols

## CI/CD

- CI should run pytest, ruff, and mypy on every pull request
- Release automation should build artifacts from a clean checkout
- Publishing credentials must live in the host platform's secret store, never in source

## Dependency Policy

Runtime dependencies are minimized. A dependency is acceptable when it reduces risk more than it increases install size, maintenance burden, and compatibility surface.
