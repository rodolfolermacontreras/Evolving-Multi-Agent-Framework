# Evolving Multi-Agent Framework

A portable, replicable multi-agent development system for spec-driven software delivery.

---

## What is this

The Evolving Multi-Agent Framework is a structured development system where one human developer orchestrates a team of AI agents through a complete software lifecycle -- from IDEA to DONE -- with quality gates, full traceability, and separation of concerns at every phase. It is not a runtime or library you import; it is a set of Markdown files, YAML schemas, agent definitions, composable skills, and conventions that operate inside VS Code with GitHub Copilot.

The framework defines four Principal agents (Executive Manager, Product Manager, Architect, Software Developer) who handle strategy, and N Worker agents (Developer, UX Designer, QA Engineer, Data Scientist, and any role created on demand via `/hire`) who handle tactics. Workers are constrained to 1-3 files per task. Every implementation goes through a two-stage review: spec compliance first, then code quality. Fleet dispatch enables parallel execution of up to 4 independent tasks with automatic conflict detection.

Skills are composable, single-purpose Markdown files with YAML frontmatter that any agent can load on demand. The framework ships with 28+ skills across five categories (core, workflow, engineering, operational, domain) and is designed so that host projects add their own domain skills without modifying the framework itself.

## Quick start

Clone, run one setup command, then talk to the Executive Manager:

```bash
# 1. Clone
git clone <this-repo-url> && cd Evolving-Multi-Agent-Framework

# 2. Set up (creates a fresh local ledger, runs health checks)
make setup
#   or, without make:
#   python spec-driven-development/cli/bootstrap.py setup --owner "Your Name"

# 3. Verify the install is healthy at any time
make doctor
```

Then open the **Principal Executive Manager** agent in VS Code Copilot Chat and
describe what you want to do. The EM is your single entry point -- it routes work,
reports status, and surfaces decisions.

`make setup` is idempotent (safe to re-run) and gives every clone its own empty
`fleet.db` ledger; the personal ledger is never shared through git. `make doctor`
exits non-zero and names the failed check if anything is wrong.

### Adopt SDD on another project

To bootstrap the framework onto a different codebase, use the archetype helper.
The `archetype-recommender` skill (open the EM and describe your project) walks you
through 5-6 questions to recommend a best-fit archetype, or see
`spec-driven-development/GENERALIZATION_SDD.md` Section 3 for the full procedure.

```bash
# Greenfield (new project)
python spec-driven-development/cli/bootstrap.py greenfield python-library \
  --project-name MyLib --owner "Your Name" --target ../MyLib

# Brownfield (existing project)
python spec-driven-development/cli/bootstrap.py brownfield ../my-host-project --draft-only
```

## Repository structure

```
.github/                          -- Copilot-native (auto-discovered by VS Code)
  agents/                         -- 4 Principal + N Worker agent definitions
  skills/                         -- 28+ composable skills (core, workflow, engineering, operational, domain)
  prompts/                        -- 17 slash commands (/triage, /spec, /plan, /tasks, /implement, /fleet, etc.)
  instructions/                   -- scoped guidance documents

spec-driven-development/          -- process state (the "SDD folder")
  constitution/                   -- mission, tech-stack, principles, roadmap, decision-policy, quality-policy
  specs/                          -- one directory per feature (spec, plan, tasks, validation)
  sprints/                        -- PI-{N}/ artifacts (CURRENT_PI, lessons)
  ledger/                         -- fleet.db (SQLite dispatch ledger)
  cli/                            -- Python automation (state_builder, fleet, qa, retro, schema_lint, bootstrap)
  docs/                           -- ADRs, FINAL_MERGED_PLAN, Management/ navigation layer
  exec/                           -- state.md + state.html (auto-generated executive summary and dashboard)
  templates/                      -- reusable document templates
  roster/                         -- machine-readable agent + skill registries
  sessions/                       -- SESSION-MEMORY.md and session artifacts
```

## Key concepts

- **Constitution** -- six immutable files (mission, tech-stack, principles, roadmap, decision-policy, quality-policy) that define the project's identity and rules. Changes require human approval.
- **Principals** -- four strategic agents (Executive Manager, Product Manager, Architect, Software Developer) who decide WHAT to build, HOW to design it, and HOW to implement it. They dispatch workers but never write production code directly.
- **Workers** -- tactical agents (Developer, UX Designer, QA Engineer, Data Scientist, and custom roles) dispatched per task, constrained to 1-3 files. Generic by default; they earn permanent specialist identity through demonstrated competence.
- **Skills** -- composable, single-purpose Markdown files with YAML frontmatter that agents load on demand. Skills encode domain knowledge, workflow procedures, or engineering patterns.
- **Fleet Dispatch** -- parallel execution of up to 4 independent tasks. The Software Developer builds a file dependency graph, confirms no two tasks modify the same file, and dispatches workers concurrently. Every dispatch is logged in the SQLite ledger.
- **Two-Stage Review** -- every implementation goes through Stage 1 (spec compliance: MISSING / EXTRA / WRONG) before Stage 2 (code quality: CRITICAL / IMPORTANT / SUGGESTION). Stage 2 never runs before Stage 1 passes.
- **Lifecycle Gates** -- the pipeline IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE has explicit gates between phases. Ceremony scales with risk: bug fixes skip specs, small features get lightweight specs, cross-cutting changes require full specs + ADRs.

## Live dashboard

The Bridge dashboard (`cli/state_builder.py`) generates `exec/state.md` (Markdown executive summary) and `exec/state.html` (self-contained HTML dashboard) from live framework artifacts. The v3.0 sprint-first layout shows active sprint status, PI progress, fleet dispatch history, and agent roster at a glance. The entire CLI is stdlib-only Python (no external dependencies).

**Live site**: [https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io](https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io)

The dashboard is deployed to Azure Container Apps via GitHub Actions (OIDC authentication, no stored secrets). Every push to `master` that touches `state_builder.py`, `state.md`, the workflow file, or the `Dockerfile` triggers an automatic build and deploy.

## Origin story

This framework was born inside the [Day-to-Day Agent](https://github.com/rodolfolermacontreras/day-to-day-microsoft) project -- an AI-powered personal work management system built with Python, FastAPI, HTMX, and SQLite. As the agent team and process matured, the framework outgrew its host. On 2026-05-12, all 82 SDD files were extracted into this standalone repository. The framework has since been validated back on Day-to-Day as a brownfield bootstrap (PI-3), proving portability across tech stacks.

## Inspirations

- **Spec-Kit (GitHub)** -- the command vocabulary (`constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`) and the spec-quality-checklist concept.
- **Matt Pocock's Skills Pattern** -- the composable single-purpose `SKILL.md` format with YAML frontmatter and the core `grill-me` concept (interview the user one question at a time until shared understanding is reached).
- **DeepLearning.AI "Spec-Driven Development with Coding Agents"** course by Paul Everitt (JetBrains) -- the 3-file constitution model, the feature-loop, the brownfield-via-archaeology approach, and the validation-scorecard concept.
- **SAFe (Scaled Agile Framework)** -- adapted for a single developer + AI fleet, with PI/Sprint cadence treated as symbolic rhythm, not wall-clock duration.

## License

Internal use -- not yet published as open source.
