---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Roadmap

## PI-1: Foundation

Objective: establish the minimum useful foundation for {{PROJECT_NAME}}.

Suggested first feature:

- Implement a `--version` flag with a packaged entry point and smoke test.

Candidate PI-1 outcomes:

1. Project metadata and dependency groups are documented.
2. The first feature has a spec, task plan, and validation contract.
3. Tests or validation checks cover happy path and one failure path.
4. Ruff, mypy where applicable, and pytest or equivalent commands are documented.
5. README includes setup, quickstart, and development instructions.
6. Release or milestone readiness criteria are explicit.

## PI-2: Hardening

Objective: improve reliability after early feedback.

Potential outcomes:

- Expand edge-case validation
- Add regression checks for confirmed bugs
- Document compatibility and operational assumptions
- Tighten dependency and release policy

## PI-3: Adoption

Objective: make the project easy for others to evaluate and extend.

Potential outcomes:

- Add richer examples and runbooks
- Add changelog discipline
- Validate setup from a clean checkout
- Capture future ideas in `backlog/IDEAS.md` after Product Manager triage
