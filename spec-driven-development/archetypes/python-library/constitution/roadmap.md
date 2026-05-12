---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Roadmap

## PI-1: Foundation

Objective: establish the minimum useful Python library foundation for {{PROJECT_NAME}}.

Suggested first feature:

- Define the smallest public API that demonstrates the library's core value, with pytest coverage, type hints, and README usage examples.

Candidate PI-1 outcomes:

1. `pyproject.toml` defines package metadata, build backend, dependency groups, and tool configuration.
2. `src/` package layout imports cleanly from a fresh virtual environment.
3. `tests/` contains unit tests for the first public behavior and one edge case.
4. Ruff, mypy, and pytest run locally through documented commands.
5. README includes installation, quickstart, and development instructions.
6. Release checklist exists before the first tagged version.

## PI-2: API Hardening

Objective: improve reliability, error handling, and compatibility after early user feedback.

Potential outcomes:

- Stabilize public names and deprecation policy
- Add property tests for boundary-heavy logic
- Expand examples for common integration scenarios
- Document supported Python versions and dependency ranges

## PI-3: Distribution and Adoption

Objective: make the package easy to evaluate and adopt outside the original repository.

Potential outcomes:

- Publish signed or verified release artifacts where appropriate
- Add changelog discipline
- Add API reference documentation
- Validate installation in a clean downstream sample project

## Parking Lot

Capture future ideas in `backlog/IDEAS.md`; do not expand this roadmap until the Product Manager triages them.
