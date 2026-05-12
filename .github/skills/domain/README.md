# Domain Skills

Domain skills capture **project-specific** knowledge: the conventions, helpers, file
layouts, and tooling quirks of a particular host project. They are the most volatile
category of skill in the framework -- they exist to be replaced by every host project
that adopts SDD.

---

## What lives here

Three example skills ship with the framework, all extracted from the original Day-to-Day
Agent host project (a Python/FastAPI/HTMX dashboard):

- `pytest-runner/` -- pytest command patterns, fixtures, mocks, baseline enforcement
- `fastapi-routes/` -- FastAPI APIRouter conventions, Pydantic schemas, safety helpers
- `htmx-frontend/` -- HTMX + Jinja2 + Alpine.js template conventions

Each example carries a `status: example` and `origin: day-to-day-agent` marker in its
YAML frontmatter and a banner at the top of its body. They are reference implementations,
not framework defaults.

## What a host project should do

When a host project bootstraps the framework, it should:

1. **Delete** any example skill that does not apply to the host's tech stack.
2. **Replace** with host-specific equivalents tuned to the host's actual conventions
   (e.g. `vitest-runner`, `nestjs-routes`, `react-frontend`, `dotnet-tests`).
3. **Update** `spec-driven-development/roster/skills.json` to reflect the active set.

Domain skills should always be small and concrete. If a domain skill grows past a page,
it is probably trying to be two skills.

## Naming convention

`{technology-or-area}-{specific-aspect}` -- e.g. `pytest-runner`, `react-components`,
`postgres-migrations`, `terraform-modules`. Keep it lowercase + hyphens.

## What does NOT belong here

- General engineering knowledge (goes under `.github/skills/engineering/`)
- Workflow / lifecycle skills (`.github/skills/workflow/`)
- Framework-core skills (`.github/skills/core/`)
- Operational / fleet-coordination skills (`.github/skills/operational/`)

If a skill is reusable across host projects with the same tech stack, it can stay
under `domain/`. If it is reusable across **all** host projects regardless of tech, it
belongs in one of the other categories.
