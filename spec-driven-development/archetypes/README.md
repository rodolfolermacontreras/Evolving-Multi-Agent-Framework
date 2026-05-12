# SDD Archetypes

Archetypes are lightweight starter profiles for greenfield host projects that adopt Spec-Driven Development. They keep the framework portable as Markdown and YAML while giving new projects a practical first constitution, backlog, and domain skill baseline.

Use an archetype with the bootstrap helper:

```bash
python spec-driven-development/cli/bootstrap.py greenfield python-library --project-name MyLib --owner "Your Name" --target ../MyLib
```

## Archetype Index

- `python-library`: reusable Python package with a stable public API, pytest coverage, ruff, mypy, and pyproject packaging. Choose this when the first useful slice is importable library behavior for downstream developers.
- `python-web-service`: FastAPI-first Python HTTP service with pydantic schemas, SQLAlchemy or SQLModel persistence, alembic migrations, and pytest/httpx API tests. Choose this when the first useful slice is an endpoint, route contract, or persistence-backed web workflow.
- `data-pipeline`: Python ETL or analytics pipeline using pandas or polars, Prefect by default, DuckDB or Postgres staging, validation contracts, and run observability. Choose this when the first useful slice is load -> validate -> transform -> publish data flow.
- `cli-tool`: installable command-line tool using Typer by default, Click or argparse alternatives, cross-platform path discipline, `CliRunner` tests, and PyPI-ready packaging. Choose this when the first useful slice is a command, flag, exit code, or shell workflow.
- `research-repo`: reproducible research workspace with Jupyter notebooks, papermill parameterization, scientific Python, optional modeling/rendering tools, nbval-style checks, and data/version notes. Choose this when the first useful slice is reproducing a figure, table, or analysis from documented data.

Each archetype may provide:

- `constitution/`: the six host constitution files with `{{PROJECT_NAME}}`, `{{OWNER}}`, and `{{DATE}}` placeholders
- `skills/`: domain skills copied into the host project's `.github/skills/domain/`
- `backlog/IDEAS.md` and `backlog/BACKLOG.md`: optional starter backlog templates

The archetype does not replace project judgment. Treat it as a starting point, then refine it through the Executive Manager, Product Manager, Architect, and Developer workflow.
