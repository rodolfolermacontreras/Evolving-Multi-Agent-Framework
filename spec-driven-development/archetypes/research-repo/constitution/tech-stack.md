---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Tech Stack

## Runtime

- Language: Python 3.11+
- Notebook environment: Jupyter with a named, pinned kernel
- Parameterization: papermill
- Core libraries: pandas, numpy, matplotlib, and seaborn
- Optional modeling: scikit-learn or torch when justified by the research plan
- Optional rendering: quarto or pandoc for paper-style reports
- Supported platforms: Windows, Linux, and macOS

## Repository Shape

- Notebooks live in `notebooks/` with ordered names when sequence matters
- Reusable code belongs in `src/` or `analysis/`, not duplicated across notebooks
- Generated figures live in a documented output directory
- Data notes distinguish raw, interim, processed, and external sources where applicable

## Testing

- Test runner: pytest for utility modules and deterministic transformations
- Notebook checks: nbval, papermill smoke runs, or an equivalent command
- Tests are lighter-weight than application repos but protect reusable logic and published claims

## Quality Tools

- Formatter and linter: ruff
- Type checker: mypy for reusable modules when practical
- Notebook hygiene: output stripping for clean diffs unless outputs are intentional review artifacts
- Reproducibility: lockfile, seed pinning, data version notes, and environment capture

## CI/CD

- CI emphasis is lighter; reproducibility emphasis is stronger
- CI should run pytest and at least one notebook smoke test when practical
- Large data, private credentials, and long experiments are not required for every pull request
