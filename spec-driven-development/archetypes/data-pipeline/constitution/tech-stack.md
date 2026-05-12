---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Tech Stack

## Runtime

- Language: Python 3.11+
- Dataframes: pandas or polars
- Orchestration: Prefect by default for solo development; Airflow or Dagster when their ecosystem is justified
- Staging: DuckDB by default; Postgres when concurrent consumers or service integration require it
- Supported platforms: Windows, Linux, and macOS for development; Linux containers for scheduled runs

## Data Processing

- Source adapters isolate file, database, API, or warehouse access from transformation logic
- Transformations accept explicit inputs and return explicit outputs
- Configuration is file- or environment-driven and documented
- No web framework is part of this archetype by default

## Testing

- Test runner: pytest
- Unit tests cover transformations with small fixtures
- Integration tests cover one load -> validate -> transform -> publish path when practical
- Validation uses Great Expectations, pandera, pydantic-as-validator, or a documented lightweight equivalent

## Quality Tools

- Formatter and linter: ruff
- Type checker: mypy
- Containerization: docker
- Observability: structured logs plus counts, durations, errors, and output manifests

## CI/CD

- CI should run pytest, ruff, mypy, and fixture validation checks
- Scheduled runs fail closed when validation fails
- Credentials live in the host platform's secret store, never in source
