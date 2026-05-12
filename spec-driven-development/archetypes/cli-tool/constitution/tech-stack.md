---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Tech Stack

## Runtime

- Language: Python 3.11+
- CLI framework: Typer by default
- Alternatives: Click for lower-level control; argparse for stdlib-only projects
- Cross-platform rule: use pathlib everywhere and avoid POSIX-only assumptions
- Supported platforms: Windows, Linux, and macOS

## Packaging and Distribution

- Package metadata: pyproject.toml
- Build backend: hatchling or setuptools
- Distribution target: PyPI-compatible wheel and source distribution
- Build command: `uv build` or documented equivalent
- Console script entry point is declared in project metadata

## Testing

- Test runner: pytest
- CLI tests: Typer or Click `CliRunner`, plus subprocess smoke tests for packaged entry points when needed
- Contract coverage: `--help`, `--version`, happy path, validation error, and non-zero exit behavior
- Tests normalize paths and line endings

## Quality Tools

- Formatter and linter: ruff
- Type checker: mypy
- User-facing errors avoid stack traces unless verbose/debug mode is requested

## CI/CD

- CI should run pytest, ruff, mypy, package build, and CLI smoke tests
- Publishing credentials live in the host platform's secret store, never in source
