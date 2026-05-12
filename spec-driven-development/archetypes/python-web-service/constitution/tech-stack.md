---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Tech Stack

## Runtime

- Language: Python 3.11+
- Default web framework: FastAPI
- Alternatives: Flask for small synchronous services; Django when admin, ORM conventions, or batteries-included auth are required
- ASGI server: uvicorn
- Validation and settings: pydantic v2
- Supported platforms: Windows, Linux, and macOS for development; Linux containers for deployment

## Persistence

- ORM/data layer: SQLAlchemy 2.x or SQLModel
- Migrations: alembic for every schema-changing feature
- Default deployed store: PostgreSQL; SQLite is acceptable for local smoke tests when documented
- Route handlers delegate persistence work to service or repository modules

## Testing

- Test runner: pytest
- API tests: httpx with ASGI transport or a test server
- Contract coverage: success, validation failure, auth failure, and persistence edge cases for each endpoint
- Fixtures isolate database state and clean it deterministically

## Quality Tools

- Formatter and linter: ruff
- Type checker: mypy
- Containerization: docker
- OpenAPI or route docs are reviewed for every public endpoint

## CI/CD

- CI should run pytest, ruff, mypy, and migration checks on every pull request
- Container builds should run from a clean checkout
- Secrets live in the host platform's secret store, never in source

## Gaps

FastAPI is the default because it pairs well with pydantic v2, OpenAPI, and httpx tests. Flask and Django are valid alternatives only after an explicit Level 2 decision.
