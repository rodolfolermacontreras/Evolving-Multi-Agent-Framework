---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Mission

## Project

{{PROJECT_NAME}} is a Python library: a small, reusable package with a clear public API, predictable behavior, and documentation suitable for downstream developers.

## Owner

{{OWNER}}

## Vision

Make {{PROJECT_NAME}} easy to install, understand, test, and extend. The library should solve a focused problem well rather than grow into an application framework.

## Users

Primary users are Python developers who need the capability exposed by this package in their own scripts, services, notebooks, or automation workflows.

Secondary users are maintainers and AI agents contributing to the library through the SDD lifecycle.

## Success Criteria

The project succeeds when:

- The public API is documented and stable enough for another project to depend on it
- Installation works from a standard Python package manager
- Core behaviors are covered by pytest tests, including edge cases and errors
- Type hints make the API understandable without reading implementation details
- Releases are repeatable from `pyproject.toml` metadata and tagged commits
- Contributions trace from idea -> triage -> spec -> plan -> tasks -> implementation -> QA

## Core Values

1. SMALL SURFACE AREA: Prefer a narrow, coherent API over many loosely related helpers.
2. TESTABLE BY DEFAULT: Every public behavior has a fast pytest test.
3. TYPED INTERFACES: Public functions and classes carry useful type hints.
4. CLEAR ERRORS: User-facing failures explain what happened and how to fix it.
5. BACKWARD COMPATIBILITY: Breaking changes require explicit planning and release notes.
6. PORTABLE TOOLING: Development commands work on Windows, Linux, and macOS.
7. HUMAN OWNERSHIP: {{OWNER}} approves Level 1 and Level 2 product and architecture decisions.

## Non-Negotiables

- No new public API without tests and documentation notes
- No dependency added without a short rationale in the relevant spec or plan
- No release without passing pytest, ruff, and mypy gates
- No hidden network, filesystem, or environment side effects in library import paths
- Dates use `YYYY-MM-DD`
