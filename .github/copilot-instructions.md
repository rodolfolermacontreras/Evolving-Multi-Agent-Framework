# Copilot Instructions -- Evolving Multi-Agent Framework

Read this file first on every session start. This is the authoritative context for understanding the project, its history, its architecture, and what work remains.

---

## Project Identity

- **Name**: Evolving Multi-Agent Framework (working title: Spec-Driven Development / SDD)
- **Owner**: Rodolfo Lerma, Senior Data Scientist (L63), Microsoft WWIC Central Analytics
- **Type**: Standalone framework -- NOT tied to any specific application
- **Goal**: A portable, replicable multi-agent development system that can be carried to ANY project. One human developer orchestrates a team of AI agents through a structured spec-driven lifecycle with quality gates, traceability, and separation of concerns.
- **Status**: Framework scaffolded (v0.1). Core assets created. No pilot run yet. Ready for generalization and first real-world test.

---

## Origin Story

This framework was born inside the [Day-to-Day Agent](https://github.com/rodolfolermacontreras/day-to-day-microsoft) project -- a personal AI-powered work management dashboard (Python/FastAPI/HTMX). As that project grew to 743+ tests and 20+ feature branches, the ad-hoc "chat with AI and paste code" approach hit scaling limits:

- Context overload across architecture, implementation, and testing
- Inconsistent patterns across AI sessions
- No traceability for WHY features were built a certain way
- No quality gates between idea and production

The solution was to formalize the development process itself: a **team of specialized AI agents** with defined roles, constrained scopes, and explicit handoff protocols. The framework was developed inside the Day-to-Day repo during May 2026, then extracted on 2026-05-12 to become a standalone initiative.

---

## Inspirations and References

The framework draws from four key sources:

1. **Spec-Kit** (by GitHub) -- https://github.com/github/spec-kit -- Command naming convention (`constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`). We adopted the vocabulary for future interop but own our implementation.
2. **Matt Pocock's Skills Pattern** -- https://github.com/mattpocock/skills -- Composable, single-purpose skill files that agents load on demand. Small, swappable, human-readable. The `SKILL.md` format with YAML frontmatter follows this philosophy. The *core* `grill-me` concept (interview the user one question at a time until shared understanding) also comes from here; our SDD-lifecycle framing and structure are our own extensions.
3. **DeepLearning.AI "Spec-Driven Development with Coding Agents" course** by Paul Everitt (JetBrains) -- https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/ -- Conceptual foundation for the 3-file constitution model (mission + tech-stack + roadmap), the feature loop, the brownfield-via-archaeology approach, and treating specs as versioned first-class artifacts. Companion code repo: https://github.com/rodolfolermacontreras/sc-spec-driven-development-files.
4. **SAFe (Scaled Agile Framework)** -- Adapted for a single developer + AI fleet. Program Increments (10-week), Sprints (2-week), but treated as **symbolic cadence** -- AI fleet compresses wall-clock time dramatically.

---

## Architecture

### The Single Developer + AI Fleet Paradigm

```
Human Developer (1 person -- Rodolfo)
  |
  v
Four Principal Agents (strategic roles, run as VS Code Copilot agents)
  |-- Executive Manager:  SINGLE HUMAN ENTRY POINT. Owns kickoff, ad-hoc Q&A routing with answer synthesis, status, escalation, big-picture awareness. (See ADR-0004.)
  |-- Product Manager:    Backlog ownership, RICE scoring, acceptance criteria
  |-- Architect:          Specs, ADRs, architectural quality, pattern enforcement
  |-- Software Developer: Task decomposition, fleet dispatch, code review, integration
      |
      v
  N Worker Agents (tactical roles, dispatched per task)
      |-- Developers (generic, specialize on demand via skills)
      |-- UX Designers
      |-- QA Engineers
      |-- Data Scientists
      |-- (new roles created when first needed)
```

### Key Design Decisions

1. **Specialization over generalism**: A code reviewer that ONLY reviews code catches more than a general assistant. Workers are constrained to 1-3 files per task.
2. **Two-stage review**: Spec compliance FIRST (does it match the spec?), code quality SECOND (is it well-written?). Different reviewers for each stage.
3. **Generic by default, specialized on demand**: Workers start generic. If a worker excels at a domain, it earns a permanent identity and specialized skill pack.
4. **Two-folder split**: `.github/` for Copilot-native files (auto-discovered by VS Code). `spec-driven-development/` for process state.
5. **Spec sizing prevents ceremony bloat**: Bug fix <3 files = no spec. Not every change deserves full ceremony.
6. **Executive entry point**: The Principal Executive Manager is the single human-facing entry point. The human talks to the Executive Manager first; it answers directly or routes to the right Principal, gets the answer, and synthesizes it back at executive register. Reads `exec/state.md` by default; may read raw artifacts to answer routed questions; never modifies any artifact except (optionally) `state.md`. (See ADR-0004.)
7. **Fleet ledger**: Every dispatch, decision, and artifact is traceable in SQLite (`ledger/fleet.db`).

### Lifecycle

```
IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
```

Each phase has a gate. Gates have defined approvers. Nothing proceeds to implementation without an approved spec (except bugs <3 files).

---

## Repository Structure

```
.github/
  copilot-instructions.md           <- YOU ARE HERE
  agents/                            (8 agent definitions)
    principal-architect.agent.md
    principal-executive-manager.agent.md
    principal-product-manager.agent.md
    principal-software-developer.agent.md
    developer-general.agent.md
    data-scientist-general.agent.md
    qa-engineer-general.agent.md
    ux-designer-general.agent.md
  skills/                            (25 skill files across 5 categories)
    AI-AGENT-SUPER-SKILL.md
    core/                            (sdd-constitution, project-context, git-workflow, testing-conventions)
    workflow/                        (triage, grill-me, grill-with-docs, to-spec, to-plan, to-tasks, implement)
    engineering/                     (tdd, diagnose, code-review, improve-architecture)
    operational/                     (handoff, fleet-coordinator, pi-planning)
    domain/                          (pytest-runner, fastapi-routes, htmx-frontend)
  prompts/                           (16 slash commands)
    triage, clarify, spec, plan, tasks, analyze, fleet, implement, qa, retro, state
  instructions/                      (2 scoped instruction files)
    sdd-workflow.instructions.md     (applies to spec-driven-development/**)
    fleet-workers.instructions.md    (applies to worktree patterns)

spec-driven-development/
  CONTEXT.md                         (shared vocabulary -- read after this file)
  GENERALIZATION_SDD.md              (62KB portability guide -- the blueprint for making this work on ANY project)
  README.md                          (framework overview + quickstart)
  constitution/                      (immutable core -- 6 files)
    mission.md, tech-stack.md, principles.md, roadmap.md, decision-policy.md, quality-policy.md
  docs/
    FINAL_MERGED_PLAN.md             (85KB definitive plan -- 15 sections, covers everything)
    SCORECARD.md
    ADR/                             (3 architecture decision records)
  cli/                               (Python automation scaffolds -- not yet operational)
    fleet.py, qa.py, retro.py, state_builder.py
    common/ (composer.py, ledger.py, worktree.py, identity.py)
  roster/                            (machine-readable registry)
    agents.json, skills.json, skill_packs.json
  templates/                         (8 reusable document templates)
    feature-spec.md, plan.md, task-list.md, agent-brief.md, etc.
  backlog/                           (IDEAS.md + BACKLOG.md)
  specs/                             (empty -- no features have been spec'd yet)
  sprints/                           (empty -- no sprints have been run yet)
  exec/                              (state.md -- executive briefing, auto-generated)
  fleet/                             (conflict-log.md)
  ledger/                            (fleet.db location -- not yet created)
  sessions/                          (session artifacts)
```

---

## What Has Been Done

### Phase 1: Dual-LLM Planning (completed 2026-05-07)

The framework plan was created using a dual-LLM approach:
- **Claude Opus 4.7** generated one comprehensive plan
- **GPT 5.5** generated an independent plan
- Both plans were cross-reviewed and merged into `FINAL_MERGED_PLAN.md` (85KB, 15 sections)
- An independent reviewer provided feedback that was incorporated (symbolic cadence, pilot decisions, wall-clock vs symbolic time)

### Phase 2: Asset Creation (completed 2026-05-07)

81 files, 12,663 lines created in a single commit:
- 4 Principal agent definitions (`.agent.md` format for VS Code auto-discovery)
- 4 Generic worker agent definitions
- 12 slash command prompts (`/triage`, `/grill`, `/spec`, `/plan`, `/tasks`, etc.)
- 25 composable skills across 5 categories
- 6 constitution files (mission, principles, tech-stack, roadmap, decision-policy, quality-policy)
- 8 document templates (spec, plan, tasks, review, etc.)
- 3 ADRs, 8 CLI scaffolds, 3 roster JSONs
- GENERALIZATION_SDD.md (62KB portability guide)
- CONTEXT.md (shared vocabulary)

### Phase 3: Format Conversion (completed 2026-05-10)

- Converted 4 Principal agents from `.chatmode.md` to `.agent.md` format (VS Code auto-discovery)
- Updated all cross-references in SDD docs

### Phase 4: Extraction (completed 2026-05-12)

- Migrated all 82 SDD files from the Day-to-Day repo to this standalone repository
- Day-to-Day repo cleaned of all SDD references
- This repo initialized with its own git history

---

## What Has NOT Been Done Yet

### Critical: No Pilot Run

The framework has never been used to deliver a real feature. All assets are scaffolded but untested in practice. The originally planned pilot was "docs drift cleanup" in the Day-to-Day project. Now that this is standalone, the pilot needs to be redefined -- ideally a feature within this framework itself (dogfooding).

### Specific Gaps

1. **Constitution files reference Day-to-Day project specifics** -- `mission.md`, `tech-stack.md`, `CONTEXT.md`, and `roadmap.md` all contain Day-to-Day-specific content (FastAPI, HTMX, Engine singleton, etc.). These need to be **generalized** to describe the framework itself, not the original host project.

2. **FINAL_MERGED_PLAN.md references Day-to-Day** -- The 85KB plan was written for implementing SDD inside the Day-to-Day project. Section references to `agent/`, `templates/`, specific test files, etc. are Day-to-Day-specific.

3. **Domain skills are Day-to-Day-specific** -- `fastapi-routes`, `htmx-frontend`, `pytest-runner` skills under `.github/skills/domain/` are specific to the Day-to-Day tech stack. They serve as examples of how domain skills work, but should be either removed or clearly marked as examples.

4. **CLI scripts are scaffolds only** -- `cli/fleet.py`, `cli/qa.py`, `cli/retro.py`, `cli/state_builder.py` and `cli/common/*.py` are empty scaffolds. They need implementation.

5. **Fleet ledger database does not exist** -- `ledger/fleet.db` has not been created. The schema is defined in `FINAL_MERGED_PLAN.md` Section 5 but never instantiated.

6. **No sprint has been run** -- `sprints/` is empty. No PI or sprint artifacts exist.

7. **No spec has been written** -- `specs/` is empty. The framework has not produced its first feature spec.

8. **GENERALIZATION_SDD.md is v0.1** -- The portability guide needs to be tested against a real second-project bootstrap.

9. **No README.md at the repo root** -- The `spec-driven-development/README.md` exists but the top-level repo needs its own README.

---

## Next Steps (Priority Order)

### Immediate: Generalize the Framework

1. **Decouple from Day-to-Day** -- Update `constitution/mission.md`, `constitution/tech-stack.md`, `CONTEXT.md`, and `constitution/roadmap.md` to describe the framework itself (not a FastAPI dashboard). Keep the Day-to-Day references as an "origin story" appendix or example.

2. **Create a root README.md** -- Explain what this framework is, who it is for, how to bootstrap it on a new project.

3. **Mark domain skills as examples** -- The `domain/` skills (fastapi-routes, htmx-frontend, pytest-runner) should be clearly labeled as reference implementations, not framework essentials.

### Short-Term: Dogfood the Framework

4. **Run the first pilot** -- Use the SDD lifecycle to deliver a feature within this repo. Candidates:
   - Implement the fleet ledger database schema (`fleet.db`)
   - Implement the CLI `state_builder.py` to auto-generate `exec/state.md`
   - Build the bootstrap automation (the "3-hour bootstrap" described in GENERALIZATION_SDD.md Section 3)

5. **Validate the lifecycle end-to-end** -- IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE. Document what works and what needs adjustment.

### Medium-Term: Portability

6. **Test on a second project** -- Bootstrap SDD on a completely different tech stack to validate GENERALIZATION_SDD.md claims.

7. **Publish GENERALIZATION_SDD.md v1.0** -- After the second-project test.

8. **Package as distributable** -- Consider making this a GitHub template repo, a Copilot skill pack, or a CLI tool that scaffolds SDD onto any project.

---

## Conventions

- **No emojis** in code, docs, or commits
- **Commit format**: `type: short description` (e.g., `feat: implement fleet ledger schema`, `docs: generalize mission.md`)
- **Dates**: always `YYYY-MM-DD`
- **Markdown**: `-` bullets (not `*`), 4-space indent nesting, `---` between sections
- **Files**: lowercase + hyphens for directories, snake_case for Python files
- **Uppercase exceptions**: `README.md`, `CONTEXT.md`, `GENERALIZATION_SDD.md`, constitution files

---

## Key Documents to Read

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | This file | Project context, history, what is next |
| 2 | `spec-driven-development/CONTEXT.md` | Shared vocabulary for all agents |
| 3 | `spec-driven-development/GENERALIZATION_SDD.md` | Portability guide -- the vision for how this works on any project |
| 4 | `spec-driven-development/README.md` | Framework overview + quickstart |
| 5 | `spec-driven-development/docs/FINAL_MERGED_PLAN.md` | The definitive 85KB plan (15 sections) |
| 6 | `spec-driven-development/constitution/` | Immutable principles (6 files) |

---

## Session Recovery

On every new session:

1. Read this file
2. Run `git log --oneline -10` to see recent work
3. Read `spec-driven-development/CONTEXT.md` for shared vocabulary
4. Check `spec-driven-development/constitution/roadmap.md` for what is done vs remaining
5. If working on generalization, read `spec-driven-development/GENERALIZATION_SDD.md`
