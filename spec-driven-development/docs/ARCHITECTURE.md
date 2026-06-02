# Architecture -- Evolving Multi-Agent Framework

**Last updated**: 2026-06-02
**Status**: Alpha (PI-4 complete)

---

## 1. System Overview

The Evolving Multi-Agent Framework is a portable development harness where **one human developer orchestrates a fleet of AI agents** through a structured lifecycle with quality gates, traceability, and separation of concerns.

```
                     +-------------------------+
                     |     Human Developer     |
                     |   (project owner)       |
                     +-----------+-------------+
                                 |
                         asks / approves
                                 |
                     +-----------v-------------+
                     |   Executive Manager     |  <-- single entry point
                     |   (routes, synthesizes) |
                     +----+--------+-------+---+
                          |        |       |
               routes     |        |       |     routes
            +-------------+   +----+----+  +-------------+
            |                 |         |                 |
   +--------v------+  +------v---+  +--v-----------+    |
   | Product       |  | Architect|  | Software     |    |
   | Manager       |  |          |  | Developer    |    |
   | (backlog,     |  | (specs,  |  | (tasks,      |    |
   |  priorities,  |  |  ADRs,   |  |  dispatch,   |    |
   |  acceptance)  |  |  quality) |  |  review,     |    |
   +---------------+  +----------+  |  integration) |    |
                                    +------+--------+    |
                                           |             |
                                    dispatches           |
                                           |             |
                         +-----------------+---------+   |
                         |        |        |         |   |
                    +----v--+ +--v---+ +--v----+ +--v---+
                    | Dev   | | Dev  | | QA    | | UX   |
                    | Worker| | CLI  | | Eng.  | | Des. |
                    |       | | Spec.| |       | |      |
                    +-------+ +------+ +-------+ +------+
```

**Key principle**: Specialization over generalism. Each agent has a constrained scope and defined handoff protocols.

---

## 2. Lifecycle

Every feature traverses a 9-stage pipeline with explicit gates:

```
IDEA --> BACKLOG --> CLARIFY --> SPEC --> PLAN --> TASKS --> IMPLEMENT --> REVIEW --> DONE
 |         |          |          |        |        |           |            |
 |      /triage    /grill     /spec    /plan   /tasks    /implement      /qa
 |         |          |          |        |        |           |            |
 v         v          v          v        v        v           v            v
IDEAS.md  BACKLOG.md  (verbal)  spec.md  plan.md  tasks.md  code+tests  two-stage
                                                                         review
```

| Gate | Approver | What passes |
|------|----------|-------------|
| BACKLOG entry | PM | RICE-scored, P1-P4 assigned |
| SPEC approved | Human + Architect | Acceptance criteria, data model, traceability matrix |
| PLAN approved | Architect + SW Dev | Phases, dependencies, effort estimates |
| TASKS approved | SW Dev | Atomic tasks with AFK/HITL classification |
| REVIEW passed | Two-stage: spec compliance, then code quality |
| DONE | Human sign-off | All gates passed, pushed to master |

---

## 3. Repository Structure

```
Evolving-Multi-Agent-Framework/
|
+-- .github/                          # Copilot-native (VS Code auto-discovers)
|   +-- agents/                       # 12 agent definitions (.agent.md)
|   |   +-- principal-*.agent.md      # 5 Principals (EM, PM, Arch, SW Dev, UI Des)
|   |   +-- developer-*.agent.md      # 2 Developer workers (generic + CLI specialist)
|   |   +-- qa-engineer-*.agent.md    # 1 QA worker
|   |   +-- ux-designer-*.agent.md    # 1 UX worker
|   |   +-- data-scientist-*.agent.md # 1 Data Science worker
|   |   +-- _TEMPLATE-worker.agent.md # Template for new workers
|   |
|   +-- skills/                       # 28+ composable skills (SKILL.md)
|   |   +-- core/                     # sdd-constitution, project-context, git-workflow,
|   |   |                             # testing-conventions, constitution-sync
|   |   +-- workflow/                 # triage, grill-me, to-spec, to-plan, to-tasks,
|   |   |                             # implement, archetype-recommender, grill-with-docs
|   |   +-- engineering/              # tdd, tdd-gate, code-review, diagnose,
|   |   |                             # improve-architecture
|   |   +-- operational/              # fleet-coordinator, handoff, lesson-capture,
|   |   |                             # role-creation, pi-planning, em-communication-
|   |   |                             # discipline, design-tokens, azure-deployment-
|   |   |                             # architecture, weekly-status-report, respect-existing
|   |   +-- domain/                   # EXAMPLES ONLY: fastapi-routes, htmx-frontend,
|   |                                 # pytest-runner (from Day-to-Day host project)
|   |
|   +-- prompts/                      # 17 slash commands (/triage, /spec, /plan, etc.)
|   +-- instructions/                 # 2 scoped instruction files
|   +-- workflows/                    # CI/CD (deploy-dashboard.yml)
|
+-- spec-driven-development/          # Process state (portable across projects)
|   +-- constitution/                 # 6 immutable files (mission, principles,
|   |                                 # tech-stack, roadmap, decision-policy, quality-policy)
|   +-- cli/                          # 6 Python CLI tools + tests (stdlib only)
|   |   +-- common/                   # 4 shared library modules
|   +-- ledger/                       # Fleet SQLite database + CLI
|   +-- specs/                        # Feature specifications (by date)
|   +-- sprints/                      # PI ceremony artifacts (CURRENT_PI.md, lessons)
|   +-- backlog/                      # IDEAS.md + BACKLOG.md
|   +-- exec/                         # Auto-generated: state.md, state.html
|   +-- docs/                         # ADRs, plans, architecture, management indexes
|   +-- roster/                       # agents.json, skills.json, skill_packs.json
|   +-- templates/                    # Reusable document templates
|   +-- archetypes/                   # 5 project archetypes with constitution presets
|   +-- sessions/                     # SESSION-MEMORY.md (cross-session state)
|   +-- CONTEXT.md                    # Shared vocabulary
|   +-- GENERALIZATION_SDD.md         # 62KB portability guide
```

---

## 4. Code Architecture

All CLI tools follow a strict pattern: **stdlib-only Python**, `main(argv)` entry point, `argparse` for arguments, testable functions. No third-party runtime dependencies (LESSON-001).

### 4.1 Dependency Graph

```
                  +-------------------+
                  |  state_builder.py |  2086 lines
                  |  (dashboard +     |  Reads: specs/, sprints/, ledger/,
                  |   state.md gen)   |  backlog/, roster/, git log
                  +---------+---------+
                            |
                            | reads fleet.db (read-only)
                            v
+------------------+    +-------------------+    +------------------+
|   fleet.py       |--->|  ledger_cli.py    |<---|   retro.py       |
|   (dispatch,     |    |  (CRUD for        |    |   (retrospective |
|    mark, status) |    |   fleet.db)       |    |    generator)    |
+------------------+    +---------+---------+    +------------------+
                                  |
                                  | schema
                                  v
                        +-------------------+
                        |  init_ledger.py   |
                        |  (schema.sql -->  |
                        |   fleet.db)       |
                        +-------------------+

+------------------+    +-------------------+
|  bootstrap.py    |    |  schema_lint.py   |
|  (project        |    |  (frontmatter     |
|   scaffolding)   |    |   validation)     |
+------------------+    +-------------------+
       |                         |
   (standalone)             (standalone)

Shared library (cli/common/):
  composer.py  -- prompt composition helpers
  identity.py  -- agent naming (role-firstname-domain-NNN)
  ledger.py    -- alternate SQLite schema scaffold
  worktree.py  -- git worktree path conventions
```

### 4.2 CLI Tool Catalog

| CLI | Lines | Purpose | Spec ID | Key Commands |
|-----|-------|---------|---------|--------------|
| `state_builder.py` | 2086 | Executive dashboard + state.md generation + live HTTP server | SDD-002 | `--sdd-root`, `--dry-run`, `serve` |
| `bootstrap.py` | 576 | Scaffold SDD onto greenfield/brownfield projects | -- | `greenfield`, `brownfield` |
| `fleet.py` | 339 | Dispatch workers, mark outcomes, query status | SDD-003 | `dispatch`, `mark`, `status` |
| `qa.py` | 373 | Two-stage spec-compliance and code-quality checks | SDD-004 | `check` |
| `retro.py` | 299 | Generate sprint retrospectives from ledger + lessons | SDD-005 | `--pi`, `--sprint` |
| `schema_lint.py` | 282 | Validate YAML frontmatter in agents/skills/prompts | SDD-006 | `--repo-root`, `--json` |

**Test coverage**: 2727 lines of tests across 6 test files (90+ tests for state_builder alone).

### 4.3 State Builder (state_builder.py) -- Deep Dive

This is the largest and most complex CLI. It serves two contracts:

1. **SDD-002**: Generate `exec/state.md` -- a <2KB executive summary
2. **SDD state-dashboard**: Generate `exec/state.html` -- the Bridge visual dashboard

```
state_builder.py internal architecture:

+-------------------------------------------------------------------+
|                        build() orchestrator                        |
|  Calls all data loaders, passes results to both renderers          |
+--------+-------------------+-------------------+------------------+
         |                   |                   |
   +-----v------+    +------v------+    +-------v-------+
   | Data Layer  |    | MD Renderer |    | HTML Renderer |
   | (loaders)   |    | render_     |    | render_html() |
   |             |    | markdown()  |    | + HTML_CSS    |
   +-----+------+    +-------------+    +-------+-------+
         |                                       |
   +-----v------+                         +------v------+
   | File System |                         | 7-Section   |
   | + SQLite    |                         | Grid Layout |
   | + Git       |                         | (v3.0)      |
   +-------------+                         +-------------+
```

**Data Layer Functions** (added in PI-4 S1):

| Function | Source | Returns |
|----------|--------|---------|
| `load_features()` | `specs/*/spec.md` | Feature stage, name, dates |
| `load_pis()` | `docs/Management/PI-*` | PI blocks with sprint counts |
| `load_backlog()` | `backlog/BACKLOG.md` | Backlog items by priority |
| `load_roster()` | `roster/agents.json` | Agent registry |
| `load_ledger()` | `ledger/fleet.db` | Dispatch/decision summaries |
| `load_recent_commits()` | `git log` | Last N commit subjects |
| `load_sprint_table()` | `docs/Management/PI-*/S*` | Sprint status, dispatch counts |
| `load_sprint_goal()` | `docs/Management/PI-*/S*/SPEC.md` | Current sprint's goal text |
| `detect_current_sprint()` | sprint list | Active or latest sprint |
| `load_decisions()` | `ledger/fleet.db` | Recent decision records |
| `derive_next_action()` | features + PI state | Recommended next step |

**HTML Dashboard (v3.0 Bridge Layout)**:

```
+-----------------------------------------------+
|  TOPBAR: "BRIDGE" title + PI/sprint badge     |
+-----------------------------------------------+
|  SPRINT FOCUS         |  NEXT ACTION          |
|  Current sprint goal  |  AI-derived           |
|  + sprint table       |  recommendation       |
|                       +-----------------------+
|                       |  WIP KANBAN           |
|                       |  9-stage pipeline     |
|                       |  with feature cards   |
+-----------------------+-----------------------+
|  PI PROGRESS                                  |
|  Progress bar + PI mission + stats            |
+-----------------------------------------------+
|  AGENT ROSTER         |  ACTIVITY FEED        |
|  Fleet members with   |  Recent commits +     |
|  specialization       |  decision log         |
+-----------------------+-----------------------+
|  FOOTER: about text + generation timestamp    |
+-----------------------------------------------+
```

59 CSS custom properties from DESIGN_TOKENS.md. Carbon background, paper-cream text, oxblood/amber/jade signal colors. Monospace typography. Responsive (tablet at 1279px breakpoint). `prefers-reduced-motion` respected. CSP meta tag blocks all scripts.

**Live Server Mode**: `state_builder.py serve` starts a `ThreadingHTTPServer` on port 8765, regenerating the dashboard on each request.

### 4.4 Fleet Ledger (ledger/)

The fleet ledger is a SQLite database (`fleet.db`) that tracks every dispatch, decision, and outcome.

**Schema** (6 tables):

```sql
agents          -- id, role, name, specialized, skills_json, born_at, last_used
skills          -- id, name, version, summary, applies_to, requires
dispatches      -- id, feature_id, worker_id, skills_json, prompt_hash,
                -- worktree, branch, status, started_at, finished_at
artifacts       -- id, dispatch_id, path, kind, sha
blockers        -- id, dispatch_id, severity, summary, raised_at, resolved_at/by
retro_lessons   -- id, pi_id, sprint_id, lesson, applied_to_skill_id
```

Plus an operational schema used by `ledger_cli.py`:

```sql
dispatches      -- id, dispatched_at, pi, sprint, feature_dir, task_id,
                -- task_title, agent_id, agent_role, outcome, outcome_at, notes
decisions       -- id, decided_at, decider, level, description
```

**Access pattern**: `fleet.py` and `retro.py` write through `ledger_cli.py`. `state_builder.py` reads directly (read-only).

### 4.5 Bootstrap System (bootstrap.py)

Scaffolds SDD onto new projects:

```
bootstrap.py greenfield <archetype> --project-name X --owner Y --target ../X

What it does:
1. Validates target is empty (or --force)
2. Copies framework Markdown/YAML assets from archetypes/<name>/
3. Replaces placeholders: {{PROJECT_NAME}}, {{OWNER}}, {{DATE}}
4. Normalizes YAML frontmatter dates
5. Writes constitution files (6 files)
6. Initializes backlog (IDEAS.md + BACKLOG.md)
7. Initializes ledger directory
8. Copies archetype-specific skills
9. Runs git init + first commit

bootstrap.py brownfield --target ../existing-project

What it does:
1. Validates target has .git/
2. Runs "archaeology": detects languages, package managers, test frameworks,
   CI systems, convention files, branching strategy
3. Generates a constitution proposal from detected patterns
4. Writes proposal for human review (does NOT auto-apply)
```

**5 Archetypes available**: `cli-tool`, `data-pipeline`, `python-library`, `python-web-service`, `research-repo`. Each has a constitution preset and 1-2 domain-specific skills.

### 4.6 QA Runner (qa.py)

Automates two-stage review:

```
Stage 1: Spec Compliance
  - Parse validation.md checkboxes (checked vs unchecked)
  - Cross-reference acceptance criteria between spec.md and validation.md
  - Check task completion status from tasks.md

Stage 2: Code Quality
  - Scan implementation files for bare except clauses
  - Scan for debug print statements
  - (Extensible: add more linters here)

Output: Structured report with PASS/FAIL per check
```

### 4.7 Schema Lint (schema_lint.py)

Validates YAML frontmatter across all agent, skill, and prompt files:

- **Agents**: checks `name`, `description`, `tools` fields
- **Skills**: checks `name`, `description`, `license`, `metadata.author`, `metadata.version`
- **Prompts**: checks `name`, `description`, `mode`

Outputs human-readable or JSON findings.

### 4.8 Common Library (cli/common/)

| Module | Lines | Purpose |
|--------|-------|---------|
| `composer.py` | 40 | Combine role prompt + skills + context + task brief into a runtime prompt |
| `identity.py` | 42 | Agent naming: `{role}-{firstname}-{domain}-{NNN}` per ADR-003. Fixed name pool. |
| `worktree.py` | 33 | Git worktree paths: `../wt-{shortname}`, branch `feature/{shortname}` |
| `ledger.py` | 166 | Alternate SQLite schema scaffold (agents, skills, dispatches, artifacts, blockers, retro_lessons) |

---

## 5. Agent Architecture

### 5.1 Role Hierarchy

```
Level 2 (Human)         -- irreversible decisions, scope changes, approvals
  |
Level 1 (Principals)    -- cross-module, ADRs, product/technical choices
  |
Level 0 (Workers)       -- single-task execution within constrained scope
```

### 5.2 Principal Agents

| Agent | Scope | Owns | Does NOT Do |
|-------|-------|------|-------------|
| Executive Manager | Project-wide | Routing, status synthesis, escalation, kickoff | Code, specs, decisions |
| Product Manager | Backlog, sprints | RICE scoring, acceptance criteria, PI planning | Architecture, code |
| Architect | Technical design | Specs, ADRs, pattern enforcement, quality gates | Task decomposition, dispatch |
| Software Developer | Implementation | Task breakdown, fleet dispatch, code review, TDD | Priority decisions, specs |
| UI Designer | Visual layer | Design tokens, accessibility, information architecture | HTML/CSS implementation |

### 5.3 Worker Agents

| Agent | Type | Specialization |
|-------|------|----------------|
| Developer (generic) | Tactical | Any implementation task |
| Developer CLI Specialist | Promoted | Earned via 5 CLI implementations, 70 tests. Stdlib Python, argparse, sqlite3. |
| QA Engineer | Tactical | Validation, test writing, spec-compliance checks |
| UX Designer | Tactical | HTMX, Jinja2, CSS, accessibility |
| Data Scientist | Tactical | Analytics, ML, data processing |

Workers start generic. If a worker excels at a domain, it earns a permanent identity and specialized skill pack (see CLI Specialist as the first example).

### 5.4 Skill System

Skills are composable, single-purpose Markdown files (Matt Pocock pattern). YAML frontmatter defines when they load.

**Skill loading**: Agents declare which skills they load in their `.agent.md` file. Skills are loaded on demand based on the task context. The VS Code Copilot agent system auto-discovers skills from `.github/skills/`.

**Skill categories**:
- **Core** (5): Framework fundamentals loaded by all agents
- **Workflow** (8): Lifecycle phase skills (/triage through /implement)
- **Engineering** (5): TDD, code review, diagnosis, architecture improvement
- **Operational** (10): Fleet coordination, handoff, planning ceremonies, communication discipline
- **Domain** (3): Project-specific reference implementations (marked as EXAMPLES)

---

## 6. Data Flow

### 6.1 Feature Lifecycle Data Flow

```
Human idea
  |
  v
IDEAS.md  -->  BACKLOG.md  -->  specs/{date}-{name}/
  (raw)        (RICE scored)     |-- spec.md
                                 |-- plan.md
                                 |-- tasks.md
                                 |-- validation.md
                                 |-- DESIGN_TOKENS.md (if UI)
                                 |
                                 v
                          fleet.db (dispatch records)
                                 |
                                 v
                          code + tests (on master)
                                 |
                                 v
                          exec/state.md + state.html
                          (auto-generated dashboard)
```

### 6.2 Dashboard Data Flow

```
state_builder.py build()
  |
  +-- load_features()       <-- specs/*/spec.md (filesystem scan)
  +-- load_pis()            <-- docs/Management/PI-* (filesystem scan)
  +-- load_backlog()        <-- backlog/BACKLOG.md (file parse)
  +-- load_roster()         <-- roster/agents.json (JSON parse)
  +-- load_ledger()         <-- ledger/fleet.db (SQLite query)
  +-- load_recent_commits() <-- git log (subprocess)
  +-- load_sprint_table()   <-- docs/Management/PI-*/S* (filesystem scan)
  +-- load_sprint_goal()    <-- docs/Management/PI-*/S*/SPEC.md (file parse)
  +-- detect_current_sprint()
  +-- load_decisions()      <-- ledger/fleet.db (SQLite query)
  +-- derive_next_action()  <-- computed from features + PI state
  |
  v
  render_markdown() --> exec/state.md  (7-section executive summary)
  render_html()     --> exec/state.html (7-section visual dashboard)
```

---

## 7. CI/CD

### 7.1 Dashboard Deployment (deploy-dashboard.yml)

**Live site**: [https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io](https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io)

```
Trigger: push to master (when state_builder.py, state.md, Dockerfile, or workflow changes)
         OR manual workflow_dispatch

Steps:
  1. actions/checkout@v4
  2. azure/login@v2 (OIDC federation -- no stored secrets)
  3. az acr build (build container image in Azure Container Registry)
  4. az containerapp update (deploy to Azure Container Apps)

Infrastructure:
  - Azure Container Registry: ca24921a026cacr.azurecr.io
  - Azure Container App: state-dashboard (resource group: rg-bridge-dashboard)
  - Region: West US 2
  - Authentication: GitHub OIDC -> Entra ID federated credential (no stored secrets)
  - Auto-deploy: every qualifying push to master triggers build + deploy
```

---

## 8. Design Decisions (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-0001 | Two-folder split (.github/ + spec-driven-development/) | Copilot auto-discovery for agents/skills; portable process state in sdd/ |
| ADR-0003 | Agent identity naming: `role-firstname-domain-NNN` | Memorable identifiers for promoted specialists |
| ADR-0004 | Executive Manager as single human entry point | Reduces cognitive load; one agent to talk to |
| ADR-0005 | CLI specialist promotion (earned, not assigned) | Demonstrated competence model for worker specialization |
| ADR-0006 | LESSON-001: stdlib-only CLIs | No pip install on CI, no version conflicts, runs everywhere |
| ADR-0007 | Domain skills marked as examples, not framework defaults | Framework must be tech-stack agnostic |
| ADR-0010 | Principal UI Designer role (hired 2026-05-25) | Design token ownership needs dedicated principal |

---

## 9. Portability Model

The framework is designed to be carried to ANY project:

```
bootstrap.py greenfield <archetype> --project-name X --target ../X

Available archetypes:
  cli-tool            -- argparse CLIs, cross-platform testing
  data-pipeline       -- ETL/ML pipelines, validation, observability
  python-library      -- pytest, typing, packaging
  python-web-service  -- FastAPI, API contracts, deployment
  research-repo       -- notebooks, reproducibility, experiment tracking
```

Each archetype provides:
- Pre-configured constitution files (mission, tech-stack, principles)
- Domain-specific skills (1-2 per archetype)
- Appropriate quality policies

The brownfield path runs "archaeology" to detect existing patterns and proposes (not applies) a constitution.

---

## 10. Test Architecture

All tests follow pytest conventions with `tmp_path` fixtures for isolation.

| Test File | Tests | Covers |
|-----------|-------|--------|
| `test_state_builder.py` | 90 | Data layer, CSS, HTML layout, accessibility, security, integration |
| `test_fleet.py` | ~30 | Task parsing, dispatch, mark, status |
| `test_qa.py` | ~35 | Validation checks, cross-references, code scans |
| `test_retro.py` | ~30 | Metrics queries, feature scanning, lesson parsing |
| `test_schema_lint.py` | ~25 | Frontmatter validation for all artifact types |
| `test_ledger.py` | ~30 | Schema init, CRUD, dispatch recording |
| `test_deploy_workflow.py` | ~10 | Workflow YAML structure validation |

**Total**: 240+ tests across the framework.

**Constraint**: No third-party test dependencies beyond pytest itself (LESSON-001 stdlib spirit).
