# Technology Stack

This file describes the technologies the **framework itself** is built on. Host projects
that adopt SDD will have their own tech stack documented in their own constitution; the
framework imposes nothing on the host beyond the two-folder split and the file formats
described here.

---

## Framework Core (no runtime dependency required)

The framework is fundamentally a **set of Markdown files, YAML schemas, and conventions**.
A host project can use SDD with nothing more than a text editor and VS Code with the
GitHub Copilot extension.

- Markdown for all artifacts (specs, plans, tasks, ADRs, retros)
- YAML frontmatter on agents, skills, and prompts
- JSON for machine-readable registries (`roster/agents.json`, `roster/skills.json`, `roster/skill_packs.json`)
- SQLite for the fleet ledger (`ledger/fleet.db`)

## Agent Runtime

- VS Code with the GitHub Copilot extension (Chat + Agents)
- `.github/agents/*.agent.md` format -- auto-discovered by VS Code Copilot Chat
- `.github/skills/**/*.md` -- composable skill files loaded on demand by agents
- `.github/prompts/*.prompt.md` -- slash commands surfaced in Copilot Chat
- `.github/instructions/*.instructions.md` -- scoped guidance applied by file glob

## CLI Automation (optional, currently scaffolded)

- Python 3.12+ for the CLI tooling under `spec-driven-development/cli/`
- Standard library preferred (`sqlite3`, `json`, `pathlib`, `argparse`)
- Approved third-party libraries when needed: `gitpython` (worktree management), `jinja2` (template rendering)
- Virtual environment: `.venv` (mandatory when CLI is used)
- The CLI is a convenience layer -- the framework remains usable without it

## Storage

- SQLite (`ledger/fleet.db`) -- single source of truth for fleet dispatches, agent records, skill assignments, and decisions
- Plain Markdown files for all narrative artifacts (specs, plans, tasks, retros, ADRs)
- Plain JSON for registry data (rosters)
- No database server, no message broker, no external state store required

## Version Control

- Git, with worktree-based parallelism (`../wt-{shortname}`)
- Branch convention: feature branches off the host project's integration trunk
- The framework does not mandate a specific branching model. Host projects document
  their branching conventions in their own host-level articles, not in framework
  `principles.md`.

## Testing

- The framework has no runtime tests of its own at v0.1 -- it is a process and document set
- Future: schema validation tests for agent/skill/prompt frontmatter
- Future: lint rules enforcing the two-folder split and naming conventions
- Host project test conventions are documented in the host's own `tech-stack.md`

## Documentation

- All framework documentation in Markdown
- Diagrams in ASCII art (no binary diagram files committed)
- ADRs in `spec-driven-development/docs/ADR/` numbered sequentially
- The portability guide `spec-driven-development/GENERALIZATION_SDD.md` is the source of
  truth for adopting SDD on a new project

---

## Key Files and Directories

| Path | Responsibility |
|------|----------------|
| `.github/copilot-instructions.md` | Root authority -- read on every session start |
| `.github/agents/*.agent.md` | Agent definitions (4 Principals + N generic workers) |
| `.github/skills/**/*.md` | Composable skills, organized by category (core, workflow, engineering, operational, domain) |
| `.github/prompts/*.prompt.md` | Slash commands (`/triage`, `/spec`, `/plan`, `/tasks`, `/fleet`, `/implement`, etc.) |
| `.github/instructions/*.instructions.md` | Scoped guidance applied by file glob |
| `spec-driven-development/CONTEXT.md` | Shared vocabulary for all agents |
| `spec-driven-development/GENERALIZATION_SDD.md` | Portability guide for adopting SDD on a new project |
| `spec-driven-development/constitution/` | Mission, tech stack, principles, roadmap, decision policy, quality policy |
| `spec-driven-development/docs/FINAL_MERGED_PLAN.md` | Definitive 15-section framework plan |
| `spec-driven-development/docs/ADR/` | Architecture Decision Records |
| `spec-driven-development/cli/` | Python automation scaffolds (fleet, qa, retro, state_builder) |
| `spec-driven-development/roster/` | Machine-readable agent and skill registries |
| `spec-driven-development/templates/` | Reusable document templates (spec, plan, tasks, agent brief, ADR, retro) |
| `spec-driven-development/specs/` | One directory per feature (spec, plan, tasks, clarification log, review) |
| `spec-driven-development/sprints/` | Sprint artifacts under `PI-{N}/sprint-{M}/` |
| `spec-driven-development/backlog/` | `IDEAS.md` (raw) and `BACKLOG.md` (RICE-scored) |
| `spec-driven-development/exec/state.md` | Auto-built executive summary (<= 2KB) |
| `spec-driven-development/ledger/fleet.db` | SQLite source of truth for all dispatches |

---

## Approval-Required Changes (framework repo)

The following require human approval (Level 2 decision) and an ADR before implementation:

- Adding a new principal agent role
- Changing the lifecycle phase order or gate definitions
- Modifying the agent or skill frontmatter schema
- Adding a new top-level directory under `spec-driven-development/`
- Adding a runtime dependency to the CLI beyond the approved list
- Changing the ledger schema once it is operational

## ADR Location

`spec-driven-development/docs/ADR/`

---

## Host Project Tech Stack

When SDD is bootstrapped onto a host project, the host's own technology stack is
documented separately under that project's constitution. The framework does not impose
languages, frameworks, or libraries on the host project. See
`spec-driven-development/GENERALIZATION_SDD.md` for the bootstrap procedure.
