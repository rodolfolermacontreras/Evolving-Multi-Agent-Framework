# Python Library Archetype

Use this archetype for a small reusable Python package intended for internal reuse or publication to PyPI. It assumes a modern `pyproject.toml` project, pytest-based testing, type checking with mypy, linting and formatting with ruff, and packaging with hatch or uv.

The generated constitution is intentionally minimal. It gives the first SDD agents enough direction to plan a foundation PI without pretending the library's API, audience, or release policy are already settled.

After bootstrapping, review all six constitution files and replace remaining host-specific placeholders such as first package name, supported Python versions, and initial public API boundaries.
