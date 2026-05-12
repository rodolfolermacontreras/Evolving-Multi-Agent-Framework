# Evolving Multi-Agent Framework

A portable, replicable system for orchestrating a fleet of AI agents through a
structured, spec-driven, test-driven development lifecycle. One human developer
plus a team of specialized AI agents, with explicit roles, scoped responsibilities,
defined handoffs, and full traceability.

**Status: v0.1 -- scaffolded, not yet piloted.** The framework's assets are in
place; the first end-to-end pilot run is the next milestone.

---

## What this is

- **A process**: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT
  -> REVIEW -> DONE, with quality gates between phases.
- **A team of agent roles**: four Principal agents (Executive Manager, Product
  Manager, Architect, Software Developer) plus a fleet of generic worker agents
  (Developer, UX Designer, QA Engineer, Data Scientist) that specialize on demand.
- **A two-folder convention**: `.github/` for Copilot-native files (agents, skills,
  prompts, instructions); `spec-driven-development/` for process state (constitution,
  specs, sprints, ledger, templates).
- **A constitution**: six immutable files that define the project's mission,
  technology stack, principles, roadmap, decision policy, and quality policy.
- **A traceable ledger**: every dispatch, decision, and handoff recorded in SQLite.

## What this is not

- Not a runtime, library, or framework you import. It is a set of Markdown files,
  YAML schemas, and conventions that operate inside VS Code with GitHub Copilot.
- Not opinionated about your host project's tech stack. The framework imposes a
  process, not a language or a web framework.
- Not yet validated on a second project. Portability is the explicit goal of PI-3.

---

## Who this is for

- Solo developers and small teams who want to multiply their throughput by
  delegating tactical work to AI agents while keeping strategic decisions human.
- Anyone tired of "chat with AI and paste code" hitting scaling limits as a
  project grows past a few hundred files or a few hundred tests.
- Teams that want spec-driven development with explicit acceptance criteria *and*
  test-driven development with mechanical enforcement, not cultural enforcement.

---

## Quickstart

### Greenfield (new project)

For a brand-new repository:

1. Copy `.github/` and `spec-driven-development/` into the new repo's root.
2. Open `spec-driven-development/constitution/` and rewrite each file for your
   project. Start with `mission.md` (who, what, why) and `tech-stack.md` (your
   actual stack). Use the existing files as a structural template.
3. Open VS Code with the GitHub Copilot extension. Confirm the four Principal
   agents appear in the Copilot Chat agent picker.
4. Open the **Principal Executive Manager** agent. This is your single human-facing
   entry point: tell it your first idea in plain language. It will capture it in
   `backlog/IDEAS.md` and hand off to the Principal Product Manager for `/triage`.
5. From there, walk the lifecycle: `/clarify` -> `/spec` -> `/plan` -> `/tasks`
   -> `/implement` -> `/qa`. Use `/ask` against the Executive Manager any time
   you have a question about who is doing what or why.

A `cli/bootstrap.py greenfield` automation that scaffolds steps 1-3 from a few
prompts is on the PI-1 roadmap (item `s3-greenfield-bootstrap`).

### Brownfield (existing project)

For a repository with established code, tests, and conventions:

1. Read `spec-driven-development/GENERALIZATION_SDD.md` for the full adoption
   playbook.
2. Run an **archaeology pass** before writing the constitution: inventory the
   host's languages, test frameworks, branching model, deploy pipeline, existing
   convention files. The constitution must reflect what is, not what should be.
3. Copy `.github/` and `spec-driven-development/` into the host repo.
4. Author the constitution with your team's input -- this is a one-time
   investment of an afternoon, not a perpetual exercise.
5. Pick one small feature or refactor as the **adoption pilot**. Walk it through
   the lifecycle. Measure friction. Update skills. Don't try to convert the
   whole project at once.
6. Define explicit **coexistence rules**: what SDD owns, what stays under the
   existing process. Emergency hotfixes typically bypass SDD.

A `cli/bootstrap.py brownfield <path>` that automates the archaeology pass and
proposes a constitution draft is on the PI-2 roadmap (item `s4-brownfield-bootstrap`).

---

## How it works (one screen)

```
Human (1 person)
  |
  v
Four Principal agents (strategic, in VS Code Copilot Chat)
  |- Executive Manager:  SINGLE HUMAN ENTRY POINT -- kickoff, Q&A routing with answer synthesis, status, escalation, big-picture awareness
  |- Product Manager:    backlog, RICE scoring, acceptance criteria
  |- Architect:          specs, ADRs, architectural quality, pattern enforcement
  |- Software Developer: task decomposition, fleet dispatch, code review
       |
       v
  N Worker agents (tactical, dispatched per task, generic by default)
       |- Developer | UX Designer | QA Engineer | Data Scientist | ...
```

Workers are constrained to 1-3 files per task. Reviews are two-stage: spec
compliance first (different reviewer), then code quality. Generic workers earn
permanent specialist identity by demonstrating competence in a domain.

The Executive Manager is the human's default entry point: it captures kickoffs,
routes ad-hoc questions to the right Principal, synthesizes answers back at
executive register, and surfaces escalations. It defaults to a curated
`exec/state.md` summary (under 2KB) but may read raw artifacts when needed to
answer a routed question. It never modifies any artifact except (optionally)
`state.md`. The human is welcome to attend ceremonies directly; the Executive
Manager is the *default* entry point, not a wall. See ADR-0004.

---

## Spec sizing rule (no ceremony for trivial changes)

| Change size | Process |
|-------------|---------|
| Bug fix, < 3 files | No spec. Task + test + review. |
| Feature, < 5 files | Lightweight spec: user story + requirements + success criteria |
| Feature, >= 5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

---

## Repository layout

```
.github/                                   <- Copilot-native (auto-discovered)
  copilot-instructions.md                  <- session-start authority
  agents/    (4 Principals + N workers)
  skills/    (22 composable skills across core, workflow, engineering, operational, domain)
  prompts/   (12 slash commands)
  instructions/                            (scoped guidance)

spec-driven-development/                   <- process state
  CONTEXT.md                               <- shared vocabulary
  GENERALIZATION_SDD.md                    <- portability guide (deep dive)
  README.md                                <- framework overview + slash command reference
  constitution/                            <- mission, tech-stack, principles, roadmap, decision-policy, quality-policy
  docs/
    FINAL_MERGED_PLAN.md                   <- definitive 15-section plan
    ADR/                                   <- Architecture Decision Records
  cli/                                     <- Python automation (currently scaffolded)
  roster/                                  <- machine-readable agent + skill registries
  templates/                               <- reusable document templates
  backlog/                                 <- IDEAS.md + BACKLOG.md
  specs/                                   <- one directory per feature
  sprints/                                 <- PI-{N}/sprint-{M}/ artifacts
  exec/                                    <- state.md (auto-built executive summary)
  fleet/                                   <- conflict log
  ledger/                                  <- fleet.db (SQLite source of truth for dispatches)
  sessions/                                <- session artifacts
```

---

## Key documents to read (in order)

| # | Document | Why |
|---|----------|-----|
| 1 | `.github/copilot-instructions.md` | Project context, history, what is next |
| 2 | `spec-driven-development/CONTEXT.md` | Shared vocabulary for all agents |
| 3 | `spec-driven-development/README.md` | Slash command reference + lifecycle quickstart |
| 4 | `spec-driven-development/constitution/mission.md` | Mission, vision, non-negotiables |
| 5 | `spec-driven-development/constitution/roadmap.md` | What is done, what is next |
| 6 | `spec-driven-development/GENERALIZATION_SDD.md` | Full portability and bootstrap guide |
| 7 | `spec-driven-development/docs/FINAL_MERGED_PLAN.md` | Definitive 15-section framework plan |

---

## Principles in one breath

Separation of strategy and tactics. Specialization over generalism. Generic by
default, specialized on demand. Two-stage review. Ceremony proportional to risk.
Every artifact is a file. Every dispatch is logged. The human always holds final
approval.

---

## Origin

Extracted from the [Day-to-Day Agent](https://github.com/rodolfolermacontreras/day-to-day-microsoft)
project on 2026-05-12 after proving its value inside that codebase. Day-to-Day Agent
remains the canonical reference host project; the framework now stands alone and
is intended for any project, in any tech stack.

## Inspirations

- **Spec-Kit (GitHub)** — https://github.com/github/spec-kit. The command vocabulary (`constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`) and the spec-quality-checklist concept come from here.
- **DeepLearning.AI "Spec-Driven Development with Coding Agents"** course by Paul Everitt (JetBrains) — https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/. The 3-file constitution model (`mission.md` + `tech-stack.md` + `roadmap.md`), the feature-loop, the brownfield-via-archaeology approach, and the validation-scorecard-as-pre-implementation-contract idea come from here. Companion code repo: [`sc-spec-driven-development-files`](https://github.com/rodolfolermacontreras/sc-spec-driven-development-files).
- **Matt Pocock's Skills Pattern** — https://github.com/mattpocock/skills. The composable single-purpose `SKILL.md` format with YAML frontmatter and the *core* `grill-me` concept (interview the user one question at a time until shared understanding is reached). Our SDD-lifecycle framing, question taxonomy, and completion signals are our own extensions on top of his ~60-word original.
- **SAFe (Scaled Agile Framework)** — adapted for a single developer + AI fleet, with PI/Sprint cadence treated as **symbolic** rhythm, not wall-clock duration.

## License

MIT.

## Contributing

The framework is currently a single-author initiative under active design. Once
the first pilot completes and `principles.md` is generalized, contribution
guidelines will be published. Issues and discussions are welcome in the meantime.
