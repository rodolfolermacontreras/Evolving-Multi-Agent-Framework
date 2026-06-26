# GENERALIZATION_SDD.md -- Portability Guide for Spec-Driven Development

- Version: v0.1
- Date: 2026-05-07
- Status: Living document -- grows with each project adoption
- Origin: Day-to-Day Agent project (Python/FastAPI/HTMX)
- Sources: Dual-LLM planning (Claude Opus 4.7 + GPT 5.5) + independent reviewer cross-review
- Inspiration: Spec-Kit, Matt Pocock skills, DeepLearning.AI SDD course, SAFe (adapted)

---

## Table of Contents

1. [What is SDD?](#1-what-is-sdd)
2. [Three-Tier Tagging System](#2-three-tier-tagging-system)
3. [Bootstrap Process (~3 Hours)](#3-bootstrap-process-3-hours)
4. [Greenfield vs Brownfield](#4-greenfield-vs-brownfield)
5. [Team Size Adaptation](#5-team-size-adaptation)
6. [Multi-Stack Examples](#6-multi-stack-examples)
7. [Anti-Patterns](#7-anti-patterns)
8. [Evolution Path](#8-evolution-path)
9. [Carrying This to a New Project](#9-carrying-this-to-a-new-project)
10. [Version History](#10-version-history)

---

## 1. What is SDD?

### 1.1 Definition

Spec-Driven Development (SDD) is a structured methodology for AI-augmented software development. It transforms ad-hoc "chat with an AI and paste the result" coding into a disciplined, multi-agent development process with traceability, quality gates, and separation of concerns.

At its core, SDD treats AI coding assistants not as a single general-purpose helper, but as a **team of specialized agents** -- each with a defined role, constrained scope, and explicit responsibilities. A single human developer orchestrates this team through specifications, plans, and task decomposition, producing software with the quality and traceability of a well-run engineering team.

### 1.2 Why SDD Exists

The "single developer with AI" paradigm has a scaling problem. As projects grow beyond trivial size, several failure modes emerge:

1. **Context overload**: A single AI assistant accumulates too much context across architecture, implementation, testing, and product decisions. Quality degrades as conversations grow.
2. **Inconsistency**: Without explicit standards, the same AI produces code that contradicts itself across sessions -- different naming conventions, conflicting architectural patterns, incompatible error handling.
3. **No traceability**: There is no record of WHY a feature was built a certain way, WHAT the requirements were, or HOW decisions were made.
4. **No quality gates**: Code goes from idea to production with no structured review, no spec compliance check, and no architectural validation.
5. **Ceremony avoidance**: Solo developers skip planning because it "feels like overhead" -- until the project becomes unmaintainable.

SDD solves these problems by borrowing from established team methodologies (SAFe, Scrum, Spec-Kit) and adapting them for a single developer commanding a fleet of AI agents.

### 1.3 The Single Developer with AI Fleet Paradigm

SDD assumes the following operating model:

```
Human Developer (1 person)
  |
  v
Four Principal Agents (strategic roles, run as chatmodes)
  |-- Executive Manager:  Status, routing, escalation
  |-- Product Manager:    Backlog, priorities, acceptance
  |-- Architect:          Specs, ADRs, architectural quality
  |-- Software Developer: Tasks, dispatch, code review, integration
      |
      v
  N Worker Agents (tactical roles, dispatched per task)
      |-- Developers (generic, specialize on demand)
      |-- UX Designers
      |-- QA Engineers
      |-- Data Scientists
      |-- (others created when first needed)
```

The human interacts with ONE Principal at a time through chatmodes. Principals never implement code. Workers never make architectural decisions. This separation is the foundation of quality.

### 1.4 Key Insight: Specialization and Constraint

AI agents produce better work when they are:

- **Specialized**: A code reviewer that ONLY reviews code catches more issues than a general assistant asked to "also review this."
- **Constrained**: A worker limited to modifying 1-3 specific files cannot introduce sprawling, unreviewed changes.
- **Context-loaded**: An agent given a focused skill pack (testing conventions, git workflow, domain patterns) produces more consistent work than one given the entire codebase history.
- **Ordered**: Two-stage review (spec compliance THEN code quality) catches different classes of defects than a single-pass "looks good."

The framework provides the structure to achieve all four properties systematically.

---

## 2. Three-Tier Tagging System

Every file in the SDD framework receives exactly one portability tag. These tags determine what happens when you adopt SDD for a new project.

### 2.1 Tag Definitions

| Tag | Meaning | Action When Adopting |
|-----|---------|---------------------|
| **[PORTABLE]** | Works in any project with zero edits. Copy directly. | `cp` as-is to new project |
| **[CONFIGURABLE]** | Structure is universal; values need substitution. | Find-and-replace project name, tech stack, branch names, test commands |
| **[PROJECT-SPECIFIC]** | Must be rewritten from scratch per project. | Use as a reference for structure, then write new content |

### 2.2 What Makes Something Portable

A file is `[PORTABLE]` when it describes a **process, pattern, or workflow** that does not reference:
- A specific programming language or framework
- A specific project name, team, or domain
- Specific file paths, module names, or architectural decisions
- Specific tools (beyond generic categories like "test runner" or "linter")

### 2.3 What Makes Something Configurable

A file is `[CONFIGURABLE]` when it has a **universal structure** but contains **substitutable values**:
- Branch naming conventions (swap `integration/improvements` for `develop` or `main`)
- Test commands (swap `pytest` for `vitest` or `go test`)
- Commit formats (swap `type: description` for `feat(scope): description`)
- Project names and team references
- File path patterns

### 2.4 What Makes Something Project-Specific

A file is `[PROJECT-SPECIFIC]` when its **content is unique** to one project:
- Constitution mission statement (describes THIS project's purpose)
- Domain skills (teach agents THIS project's patterns)
- CONTEXT.md vocabulary (defines terms specific to THIS codebase)
- Specific ADRs (record decisions made for THIS project)
- Active backlog and sprint data

### 2.5 Complete File-by-File Tagging Table

#### spec-driven-development/ (Framework Root)

| File / Directory | Tag | Rationale |
|-----------------|-----|-----------|
| `README.md` | [CONFIGURABLE] | Structure is standard; project name, links, and quickstart commands need substitution |
| `GENERALIZATION_SDD.md` | [PORTABLE] | This file. Describes the framework itself, not any project |
| `CONTEXT.md` | [PROJECT-SPECIFIC] | Vocabulary, assumptions, and conventions are unique per project |

#### spec-driven-development/constitution/

| File | Tag | Rationale |
|------|-----|-----------|
| `mission.md` | [PROJECT-SPECIFIC] | Project identity, owner, vision, values are unique |
| `tech-stack.md` | [PROJECT-SPECIFIC] | Language, framework, database, deployment are unique |
| `principles.md` | [CONFIGURABLE] | Article structure is universal; content references specific patterns (e.g., "world_state", "safe_path") that change per project |
| `roadmap.md` | [PROJECT-SPECIFIC] | PI objectives and milestones are unique |
| `decision-policy.md` | [PORTABLE] | Three-level decision authority (Worker / Principal / Human) applies universally |
| `quality-policy.md` | [CONFIGURABLE] | Table structure is universal; change types and validation steps reference project-specific tools |

#### spec-driven-development/docs/

| File | Tag | Rationale |
|------|-----|-----------|
| `SCORECARD.md` | [PORTABLE] | The 9 metrics (idea disposition, spec clarity, TDD rate, traceability, fleet conflicts, test pass, defect escape, cycle time) apply to any SDD project |
| `ADR/TEMPLATE.md` | [PORTABLE] | ADR format (Context, Decision, Consequences) is universal |
| `ADR/001-sdd-framework.md` | [PROJECT-SPECIFIC] | Records why THIS project adopted SDD |
| `ADR/002-two-folder-split.md` | [PORTABLE] | The two-folder split rationale applies to any VS Code Copilot project |
| `ADR/003-specialization-naming.md` | [PORTABLE] | Naming convention (`role-firstname-domain-NNN`) is framework-level |

#### spec-driven-development/templates/

| File | Tag | Rationale |
|------|-----|-----------|
| `feature-spec.md` | [PORTABLE] | Spec structure (problem, goals, user stories, FR/NFR, edge cases, traceability) is universal |
| `plan.md` | [PORTABLE] | Plan structure (approach, files, data model, API, test strategy, risk) is universal |
| `task-list.md` | [PORTABLE] | Task structure (batches, tags, checkpoints, dependency graph) is universal |
| `agent-brief.md` | [PORTABLE] | Brief structure (objective, scope, context, steps, constraints, validation) is universal |
| `adr.md` | [PORTABLE] | Same as ADR/TEMPLATE.md -- universal format |
| `validation.md` | [PORTABLE] | Validation checklist structure is universal |
| `review-report.md` | [PORTABLE] | Two-stage review report structure is universal |
| `clarification-log.md` | [PORTABLE] | Grill question format (question, recommendation, answer, status) is universal |
| `handoff.md` | [PORTABLE] | Handoff structure (goal, completed, remaining, next action, lost context) is universal |

#### spec-driven-development/roster/

| File | Tag | Rationale |
|------|-----|-----------|
| `agents.json` | [CONFIGURABLE] | JSON structure (id, role, skills, specialized, etc.) is universal; agent descriptions reference project-specific stack and patterns |
| `skills.json` | [CONFIGURABLE] | JSON structure is universal; skill catalog content references project-specific domain skills |
| `skill_packs.json` | [CONFIGURABLE] | JSON structure is universal; pack contents change with available skills |

#### spec-driven-development/cli/

| File | Tag | Rationale |
|------|-----|-----------|
| `fleet.py` | [CONFIGURABLE] | Dispatch logic is universal; worktree path pattern and branch naming need substitution |
| `qa.py` | [CONFIGURABLE] | Validation runner structure is universal; test commands need substitution |
| `retro.py` | [PORTABLE] | Retrospective data collection and template generation is universal |
| `state_builder.py` | [PORTABLE] | Executive state generation from ledger data is universal |
| `common/composer.py` | [PORTABLE] | Prompt composition algorithm (base + skills + context + brief) is universal |
| `common/ledger.py` | [PORTABLE] | SQLite I/O for fleet.db is universal (schema is framework-level) |
| `common/worktree.py` | [CONFIGURABLE] | Git worktree wrapper is universal; path patterns (`../wt-{name}`) may change |
| `common/identity.py` | [PORTABLE] | Auto-promotion, naming rules, and skill matching are universal |

#### spec-driven-development/ledger/

| File | Tag | Rationale |
|------|-----|-----------|
| `fleet.db` | [PORTABLE] | Schema (6 tables: agents, skills, dispatches, artifacts, blockers, retro_lessons) is universal. Data is project-specific but auto-generated. |

#### spec-driven-development/fleet/

| File | Tag | Rationale |
|------|-----|-----------|
| `conflict-log.md` | [PORTABLE] | Conflict logging format is universal. Content is project-specific but auto-generated. |

#### spec-driven-development/exec/

| File | Tag | Rationale |
|------|-----|-----------|
| `state.md` | [PORTABLE] | Shape (<=2KB, PI/Sprint/Priorities/Blockers/Fleet/Deliveries/Milestones) is universal. Content is auto-generated. |
| `briefings/` | [PORTABLE] | Daily snapshot directory. Content is auto-generated. |

#### spec-driven-development/backlog/

| File | Tag | Rationale |
|------|-----|-----------|
| `IDEAS.md` | [PROJECT-SPECIFIC] | Ideas are unique to each project |
| `BACKLOG.md` | [PROJECT-SPECIFIC] | Prioritized items are unique to each project |

#### spec-driven-development/specs/

| Directory | Tag | Rationale |
|-----------|-----|-----------|
| `YYYY-MM-DD-feature-name/` | [PROJECT-SPECIFIC] | All spec content (spec.md, plan.md, tasks.md, etc.) is unique per feature per project |

Use `specs/YYYY-MM-DD-feature-name/` as the canonical feature directory convention so date metadata travels with the spec, plan, tasks, validation, clarification log, and optional research artifacts.

#### spec-driven-development/sprints/

| Directory | Tag | Rationale |
|-----------|-----|-----------|
| `PI-{N}/CURRENT_PI.md` | [PROJECT-SPECIFIC] | PI objectives are project-specific |
| `PI-{N}/sprint-{M}/` | [PROJECT-SPECIFIC] | Sprint plans, boards, and retros are project-specific |

#### spec-driven-development/sessions/

| File | Tag | Rationale |
|------|-----|-----------|
| `DSP-YYYY-MM-DD-NNN.md` | [PROJECT-SPECIFIC] | Per-dispatch session logs are project-specific. Auto-generated. |

#### .github/ (Copilot-Native Files)

| File | Tag | Rationale |
|------|-----|-----------|
| `chatmodes/principal-executive-manager.chatmode.md` | [CONFIGURABLE] | Role structure is universal; project references (state.md path, team context) need substitution |
| `chatmodes/principal-product-manager.chatmode.md` | [CONFIGURABLE] | Role structure is universal; project identity, user persona, and skill references need substitution |
| `chatmodes/principal-architect.chatmode.md` | [CONFIGURABLE] | Role structure is universal; tech stack, pattern enforcement list, and skill references need substitution |
| `chatmodes/principal-software-developer.chatmode.md` | [CONFIGURABLE] | Role structure is universal; conventions list, test commands, and skill references need substitution |
| `agents/developer-general.agent.md` | [CONFIGURABLE] | Role and checklist are universal; project rules and skill references need substitution |
| `agents/ux-designer-general.agent.md` | [CONFIGURABLE] | Role is universal; design constraints (HTMX/Jinja2 vs React vs Blazor) need substitution |
| `agents/data-scientist-general.agent.md` | [CONFIGURABLE] | Role is universal; data constraints and tool references need substitution |
| `agents/qa-engineer-general.agent.md` | [CONFIGURABLE] | Role is universal; testing standards and baseline metrics need substitution |
| `prompts/triage.prompt.md` | [PORTABLE] | Triage workflow (grill, RICE, classify) is universal |
| `prompts/grill.prompt.md` | [PORTABLE] | Grill-me questioning protocol is universal |
| `prompts/spec.prompt.md` | [PORTABLE] | Spec generation workflow is universal |
| `prompts/clarify.prompt.md` | [PORTABLE] | Clarification session protocol is universal |
| `prompts/plan.prompt.md` | [PORTABLE] | Plan generation workflow is universal |
| `prompts/tasks.prompt.md` | [PORTABLE] | Task decomposition workflow is universal |
| `prompts/analyze.prompt.md` | [PORTABLE] | Cross-artifact consistency check is universal |
| `prompts/fleet.prompt.md` | [CONFIGURABLE] | Fleet dispatch structure is universal; worktree convention and conflict rules need substitution |
| `prompts/implement.prompt.md` | [CONFIGURABLE] | Implementation workflow is universal; test commands need substitution |
| `prompts/qa.prompt.md` | [CONFIGURABLE] | QA validation is universal; test commands and baseline metrics need substitution |
| `prompts/retro.prompt.md` | [PORTABLE] | Retrospective protocol is universal |
| `prompts/state.prompt.md` | [PORTABLE] | State refresh protocol is universal |
| `instructions/sdd-workflow.instructions.md` | [CONFIGURABLE] | Scoped instructions structure is universal; `applyTo` paths may change |
| `skills/core/sdd-constitution/SKILL.md` | [CONFIGURABLE] | Constitution loading skill is universal; references to constitution file paths need substitution |
| `skills/core/project-context/SKILL.md` | [CONFIGURABLE] | Context loading skill is universal; CONTEXT.md path reference is stable but content changes |
| `skills/core/git-workflow/SKILL.md` | [CONFIGURABLE] | Git workflow skill structure is universal; branch naming, worktree patterns, and merge rules need substitution |
| `skills/core/testing-conventions/SKILL.md` | [CONFIGURABLE] | Testing skill structure is universal; test runner, fixtures, and commands need substitution |
| `skills/workflow/grill-me/SKILL.md` | [PORTABLE] | Questioning protocol (one at a time, recommend answer, record) is universal |
| `skills/workflow/grill-with-docs/SKILL.md` | [PORTABLE] | Grill + document update protocol is universal |
| `skills/workflow/to-spec/SKILL.md` | [PORTABLE] | Spec authoring protocol is universal |
| `skills/workflow/to-plan/SKILL.md` | [PORTABLE] | Plan authoring protocol is universal |
| `skills/workflow/to-tasks/SKILL.md` | [PORTABLE] | Task decomposition protocol is universal |
| `skills/workflow/triage/SKILL.md` | [PORTABLE] | Triage and RICE scoring protocol is universal |
| `skills/workflow/implement/SKILL.md` | [CONFIGURABLE] | Implementation protocol is universal; TDD commands need substitution |
| `skills/engineering/tdd/SKILL.md` | [CONFIGURABLE] | TDD loop is universal; test runner command needs substitution |
| `skills/engineering/diagnose/SKILL.md` | [PORTABLE] | Diagnostic methodology is universal |
| `skills/engineering/code-review/SKILL.md` | [PORTABLE] | Two-stage review protocol (MISSING/EXTRA/WRONG then CRITICAL/IMPORTANT/SUGGESTION) is universal |
| `skills/engineering/improve-architecture/SKILL.md` | [PORTABLE] | Architecture improvement methodology is universal |
| `skills/operational/handoff/SKILL.md` | [PORTABLE] | Session handoff protocol is universal |
| `skills/operational/fleet-coordinator/SKILL.md` | [CONFIGURABLE] | Coordination logic is universal; conflict rules reference project-specific files |
| `skills/operational/pi-planning/SKILL.md` | [PORTABLE] | PI planning ceremony structure is universal |
| `skills/domain/pytest-runner/SKILL.md` | [PROJECT-SPECIFIC] | Python/pytest-specific patterns and fixtures |
| `skills/domain/fastapi-routes/SKILL.md` | [PROJECT-SPECIFIC] | FastAPI-specific route, schema, and middleware patterns |
| `skills/domain/htmx-frontend/SKILL.md` | [PROJECT-SPECIFIC] | HTMX/Jinja2-specific template and partial patterns |

### 2.6 Tag Distribution Summary

| Tag | Count | Percentage |
|-----|-------|-----------|
| [PORTABLE] | ~38 files | ~50% |
| [CONFIGURABLE] | ~25 files | ~33% |
| [PROJECT-SPECIFIC] | ~13 files | ~17% |

This distribution means roughly half the framework works out of the box for any project, a third needs value substitution, and less than a fifth needs to be written from scratch.

---

## 3. Bootstrap Process (~3 Hours)

This section provides a step-by-step guide to adopting SDD for a new project. The process is divided into three one-hour blocks. Each step references the tagging system from Section 2.

### Prerequisites

- A project repository (new or existing)
- VS Code with GitHub Copilot extension
- Familiarity with the project's tech stack
- A mental model of what the project does and who it serves

### Hour 1: Foundation (Directory Structure + Constitution)

**Goal**: Establish the two-folder split and core identity documents.

| Step | Action | Time | Details |
|------|--------|------|---------|
| 1.1 | Copy all [PORTABLE] files from a reference SDD project | 5 min | This gives you templates, scorecard, ADR template, portable prompts, portable skills, fleet schema, and this file |
| 1.2 | Create the full directory structure | 5 min | See Section 3.1 below for the canonical tree |
| 1.3 | Write `constitution/mission.md` | 10 min | Answer: What is this project? Who is it for? What are its values? What is non-negotiable? |
| 1.4 | Write `constitution/tech-stack.md` | 10 min | Document: language, framework, database, test runner, deployment model, LLM integration (if any) |
| 1.5 | Adapt `constitution/principles.md` | 10 min | Start with the 9-article structure. Replace project-specific references (e.g., swap "world_state" for your equivalent). Keep universal articles as-is. |
| 1.6 | Write `CONTEXT.md` with initial vocabulary | 10 min | Define 10-20 key terms that an agent must know to work in this codebase. Include architectural patterns, naming conventions, and domain terms. |
| 1.7 | Copy `constitution/decision-policy.md` as-is | 1 min | [PORTABLE] -- three-level authority works everywhere |
| 1.8 | Adapt `constitution/quality-policy.md` | 5 min | Keep the table structure. Replace change types and validation steps with your stack's equivalents. |
| 1.9 | Write `constitution/roadmap.md` | 5 min | Sketch 2-3 PIs. The first PI is always "Foundation + SDD Bootstrap." |

**Checkpoint**: You should now have a complete `constitution/` directory and a `CONTEXT.md` that captures your project's shared language.

#### 3.1 Canonical Directory Structure

```
.github/
  chatmodes/                         (4 Principal chatmodes)
    principal-executive-manager.chatmode.md
    principal-product-manager.chatmode.md
    principal-architect.chatmode.md
    principal-software-developer.chatmode.md
  agents/                            (generic worker agents)
    developer-general.agent.md
    ux-designer-general.agent.md
    data-scientist-general.agent.md
    qa-engineer-general.agent.md
  skills/
    core/                            (loaded by all agents)
      sdd-constitution/SKILL.md
      project-context/SKILL.md
      git-workflow/SKILL.md
      testing-conventions/SKILL.md
    workflow/                        (SDD lifecycle skills)
      grill-me/SKILL.md
      grill-with-docs/SKILL.md
      to-spec/SKILL.md
      to-plan/SKILL.md
      to-tasks/SKILL.md
      triage/SKILL.md
      implement/SKILL.md
    engineering/                     (code quality skills)
      tdd/SKILL.md
      diagnose/SKILL.md
      code-review/SKILL.md
      improve-architecture/SKILL.md
    operational/                     (process skills)
      handoff/SKILL.md
      fleet-coordinator/SKILL.md
      pi-planning/SKILL.md
    domain/                          (project-specific skills)
      {your-stack-skill-1}/SKILL.md
      {your-stack-skill-2}/SKILL.md
      {your-stack-skill-3}/SKILL.md
  prompts/                           (slash commands)
    triage.prompt.md
    grill.prompt.md
    spec.prompt.md
    clarify.prompt.md
    plan.prompt.md
    tasks.prompt.md
    analyze.prompt.md
    fleet.prompt.md
    implement.prompt.md
    qa.prompt.md
    retro.prompt.md
    state.prompt.md
  instructions/
    sdd-workflow.instructions.md

spec-driven-development/
  README.md
  GENERALIZATION_SDD.md
  CONTEXT.md
  constitution/
    mission.md
    tech-stack.md
    principles.md
    roadmap.md
    decision-policy.md
    quality-policy.md
  docs/
    ADR/
      TEMPLATE.md
    SCORECARD.md
  templates/
    feature-spec.md
    plan.md
    task-list.md
    agent-brief.md
    adr.md
    validation.md
    review-report.md
    clarification-log.md
    handoff.md
  roster/
    agents.json
    skills.json
    skill_packs.json
  cli/
    fleet.py
    qa.py
    retro.py
    state_builder.py
    common/
      composer.py
      ledger.py
      worktree.py
      identity.py
  ledger/
    fleet.db
  fleet/
    conflict-log.md
  backlog/
    IDEAS.md
    BACKLOG.md
  specs/
  sprints/
  exec/
    state.md
    briefings/
  sessions/
```

### Hour 2: Team Setup (Agents + Skills + Roster)

**Goal**: Configure the agent team and their knowledge packs.

| Step | Action | Time | Details |
|------|--------|------|---------|
| 2.1 | Adapt 4 Principal chatmodes | 20 min | For each: keep role structure, replace project references (name, stack, conventions, file paths). The Executive Manager prompt changes least; the Architect and SW Dev prompts change most. |
| 2.2 | Adapt 4 generic worker agents | 10 min | Keep checklists and rules. Replace project-specific rules (branch naming, test commands, dependency policy). |
| 2.3 | Create 2-3 domain skills | 15 min | These are `[PROJECT-SPECIFIC]`. Each skill teaches agents your stack's patterns. Start with: (1) test runner skill, (2) framework routing/API skill, (3) frontend/UI skill. |
| 2.4 | Adapt core skills | 10 min | `git-workflow`: swap branch names, worktree paths. `testing-conventions`: swap test runner, fixtures, commands. `sdd-constitution` and `project-context`: swap file path references. |
| 2.5 | Populate `roster/agents.json` | 5 min | Register all 4 principals + 4 workers with their initial skill assignments. Use the same JSON schema; change the content. |
| 2.6 | Run a first `/grill` session | Remainder | Pick a concept you want agents to understand. Run the grill-me protocol. Record answers in CONTEXT.md. This validates that the questioning flow works and starts building shared vocabulary. |

**Checkpoint**: You should be able to switch between all 4 Principal chatmodes in VS Code and have them respond with project-aware context.

### Hour 3: First Spec (Validate the Pipeline)

**Goal**: Run one small feature through the complete SDD lifecycle to validate the setup.

| Step | Action | Time | Details |
|------|--------|------|---------|
| 3.1 | Seed `backlog/IDEAS.md` with 3-5 ideas | 5 min | Use real ideas from your project, not hypothetical ones |
| 3.2 | Run `/triage` on one idea | 5 min | PM chatmode grills the idea, applies RICE score, assigns priority |
| 3.3 | Run `/clarify` on the selected feature | 5 min | Record 3-5 clarification Q&As |
| 3.4 | Run `/spec` to generate a feature spec | 10 min | Architect + SW Dev chatmode co-author the spec using the template |
| 3.5 | Run `/plan` to generate an implementation plan | 5 min | Plan should reference specific files in your codebase |
| 3.6 | Run `/tasks` to decompose into tagged tasks | 5 min | Tag with [P]/[S], [AFK]/[HITL], [US-N] |
| 3.7 | Implement one task with TDD | 15 min | Use a single worker. Follow TDD loop. Verify that all skills load correctly. |
| 3.8 | Run two-stage review | 5 min | Stage 1: spec compliance (MISSING/EXTRA/WRONG). Stage 2: code quality. |
| 3.9 | Run `/retro` | 5 min | Capture 2-3 learnings from the pilot. What worked? What needs adjustment? |

**Checkpoint**: You have completed one feature through the full SDD lifecycle. Your retro should produce actionable improvements to the framework configuration for this project.

---

## 4. Greenfield vs Brownfield

### 4.1 Greenfield (New Project)

Starting a new project with SDD is simpler because there are no existing conventions to discover or codify.

| Aspect | Approach |
|--------|----------|
| **Mission** | Written fresh. Answer: What problem does this solve? For whom? |
| **Tech stack** | Chosen deliberately. Document in `tech-stack.md` before writing code. |
| **Constitution** | Aspirational. Principles describe the codebase you WANT, not the codebase you have. |
| **CONTEXT.md** | Starts nearly empty. Grows organically through grill sessions as decisions are made. |
| **Domain skills** | Written as you build. First skill is usually the test runner; second is the web framework. |
| **First PI** | Always "Foundation": core architecture, data models, first routes, CI/CD pipeline. |
| **Patterns** | Established by the Architect in the first spec. Become precedent for all future work. |

**Greenfield Bootstrap Additions:**

Use the stdlib-only bootstrap helper to copy the framework into an empty host repo, apply the first archetype, personalize constitution placeholders, and initialize the starter backlog and ledger placeholder. The helper preserves the Markdown-as-distribution model; it is not a Python wheel or `uvx` distribution path.

```bash
python spec-driven-development/cli/bootstrap.py greenfield python-library --project-name MyLib --owner "Your Name" --target ../MyLib
```

After bootstrapping, open the Principal Executive Manager, capture the first idea, run `/triage`, create initial ADR-001 for the stack choice, and scaffold the minimal project structure before writing features.

### 4.2 Brownfield (Existing Project)

Adopting SDD on an existing codebase requires reverse-engineering what the project already does and codifying it.

| Aspect | Approach |
|--------|----------|
| **Mission** | Extracted from README, existing docs, or developer knowledge. Describes what the project IS, not what you wish it were. |
| **Tech stack** | Discovered from package files (`requirements.txt`, `package.json`, `go.mod`), CI config, and existing code. |
| **Constitution** | Descriptive. Principles codify existing patterns. If the codebase already uses a singleton engine pattern, Article I says so. |
| **CONTEXT.md** | Reverse-engineered. Run `grill-with-docs` sessions where an agent reads key files and you confirm/correct its understanding. |
| **Domain skills** | Teach agents the existing patterns. "In this project, routes are defined in `agent/routes/`, use `APIRouter`, and share helpers from `__init__.py`." |
| **First PI** | Never "rewrite everything." Pick 1-2 small features and run them through SDD to validate the framework configuration. |
| **Patterns** | Already exist. The Architect's job is to document them, not invent new ones. |

**Brownfield Bootstrap Additions:**

Use the brownfield CLI to run archaeology before any framework files are adopted. The safe default is to stage only the report and constitution proposal, then review it with the human owner before applying SDD to the host repository.

```bash
python spec-driven-development/cli/bootstrap.py brownfield ../my-host-project --draft-only
# Review ../my-host-project/.sdd-archaeology.json and ../my-host-project/.sdd-proposal/
python spec-driven-development/cli/bootstrap.py brownfield ../my-host-project --apply
```

The archaeology pass inventories languages, package managers, test frameworks, CI systems, convention files, docs, git history, and the inferred branching model. It drafts `mission.md`, `tech-stack.md`, `principles.md`, `roadmap.md`, `decision-policy.md`, and `quality-policy.md` under `.sdd-proposal/constitution/` with evidence-derived content and `TODO(human)` markers where observation is not enough.

When dispatching workers in a brownfield host, load the `respect-existing` operational skill. Workers must mimic existing patterns and avoid rewriting code outside their explicit task scope; if a pattern blocks the task, they route to the Architect instead of silently expanding scope.

After review and apply, pilot one small feature through the full lifecycle before committing to SDD for all work.

### 4.3 Key Difference Summary

| Factor | Greenfield | Brownfield |
|--------|-----------|------------|
| Constitution source | Aspirational (what we want) | Descriptive (what we have) |
| CONTEXT.md | Grows forward from zero | Reverse-engineered from codebase |
| Domain skills | Written as patterns emerge | Written to teach existing patterns |
| First PI scope | Foundation (architecture, models, first routes) | Validation (1-2 small features through SDD) |
| Risk | Over-engineering the architecture up front | Codifying bad patterns and calling them "principles" |
| Principle updates | Rare (you chose them deliberately) | Frequent (you discover gaps in codification) |

---

## 5. Team Size Adaptation

SDD was designed for a solo developer with an AI fleet, but the framework scales to small teams. Beyond ~15 people, traditional agile methods are more appropriate -- SDD's value proposition is AI-augmented development, which has diminishing returns as human-to-human coordination overhead grows.

### 5.1 Sizing Matrix

| Team Size | Principals | Workers | PI Cadence | Sprint Length | Notes |
|-----------|-----------|---------|------------|---------------|-------|
| **Solo (1 person)** | 4 (all chatmodes, 1 human) | 2-4 generic | 10-week PI | 2-week sprint (symbolic) | The reference model. Human IS the executive in practice. All 4 principals run as chatmodes. Workers dispatched per task. AI fleet compresses a full PI to ~1 wall-clock week. |
| **Pair (2 people)** | 4 (shared across both devs) | 4-6 generic | 10-week PI | 2-week sprint (symbolic) | Each person can dispatch workers independently. Coordinate via BOARD.md. One person "owns" PM, the other "owns" Architect. |
| **Small team (3-5)** | 4 (dedicated owner per principal) | 4-8 specialized | 10-week PI | 2-week sprint | Assign one person as PM liaison, one as Architect liaison. Workers can be shared or per-person. Fleet becomes the primary dispatch mechanism. |
| **Medium team (6-15)** | 4 (full-time roles or rotated) | 10-20 | 10-week PI | 2-week sprint | Principals become team lead responsibilities. Sub-principals for large domains. Workers organized into squads. Ledger becomes essential for coordination. |
| **Large team (15+)** | Not recommended | N/A | N/A | N/A | Coordination overhead exceeds AI-augmentation benefit. Use traditional agile (SAFe, Scrum, Kanban) with SDD-inspired spec quality practices. |

### 5.2 Solo Developer Notes

In the solo model:
- The Executive Manager chatmode is optional. The human already knows the status.
- PM + Architect roles can be mentally merged for very small projects (<5 features/quarter). Separate them when scope grows.
- Fleet mode is rarely needed -- sequential dispatch with a single worker is usually sufficient.
- Sprint retros feel silly alone, but they are critical. The retro forces you to improve the process, not just the code.

### 5.3 Small Team Notes

When 2-5 people share the framework:
- **Backlog ownership**: One person owns BACKLOG.md. Others contribute to IDEAS.md.
- **Spec reviews**: Cross-review between team members BEFORE AI-driven code review.
- **Fleet coordination**: The ledger (fleet.db) records every dispatch, and the serial CLARIFY/SPEC gate (`fleet.py` `_scan_lock_state`) enforces one feature at a time through the clarify and spec phases. Avoiding same-file dispatch within a batch is still a manual discipline (assign explicit per-worker file scopes) -- there is no automated file-overlap detector (see SDD-049).
- **CONTEXT.md**: Becomes a team alignment tool. Review it at the start of each PI.
- **Chatmode sharing**: Any team member can use any chatmode. The chatmodes are roles, not people.

### 5.4 Scaling Indicators

Signs you need to scale up from solo to team:
1. Sprint carryover exceeds 30% for 3+ consecutive sprints
2. Fleet batches regularly hit 4 (max) and you need more parallelism
3. Domain skills exceed 10 (indicating broad codebase)
4. Grill sessions consistently surface questions you cannot answer

Signs you need to scale DOWN (simplify):
1. Ceremony time exceeds implementation time in a sprint
2. You skip retros because "nothing changed"
3. Spec-to-merged cycle time exceeds 2 sprints for medium features
4. Workers are idle because dependencies are sequential

---

## 6. Multi-Stack Examples

The SDD framework is language-agnostic. This section shows how the `[CONFIGURABLE]` files change across four common stacks. The `[PORTABLE]` files remain identical in all cases.

### 6.1 Python / FastAPI (Reference Implementation)

This is the stack used in the Day-to-Day Agent project where SDD was first developed.

**constitution/tech-stack.md (excerpt):**
```markdown
## Runtime
- Python 3.12+
- Virtual environment: .venv (mandatory)

## Web Framework
- FastAPI (ASGI, async)
- HTMX + Jinja2 (server-rendered, no SPA)

## Database
- SQLite with WAL mode
- SQLModel (SQLAlchemy wrapper)

## Testing
- pytest with tmp_path isolation
- Custom fixtures: patched_settings, MockLLMClient
- Baseline: 743 tests, 36 files
```

**Domain skills created:** `pytest-runner`, `fastapi-routes`, `htmx-frontend`

**Key configurable values:**
| Value | Setting |
|-------|---------|
| Test command | `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short` |
| Lint command | `ruff check agent/ tests/` |
| Branch model | `master` (read-only) -> `integration/improvements` -> `feature/f{N}.{M}-slug` |
| Worktree path | `../wt-{shortname}` |
| Commit format | `type: short description` |
| Package file | `agent/requirements.txt` |

### 6.2 TypeScript / Next.js

**constitution/tech-stack.md (excerpt):**
```markdown
## Runtime
- Node.js 20 LTS
- Package manager: pnpm (mandatory)

## Web Framework
- Next.js 14+ (App Router)
- React Server Components preferred
- Tailwind CSS for styling

## Database
- PostgreSQL 16
- Prisma ORM

## Testing
- Vitest for unit/integration
- Playwright for E2E
- Custom fixtures: createTestDb, mockNextAuth
- Baseline: TBD
```

**Domain skills to create:** `vitest-runner`, `nextjs-routes`, `react-components`

**Key configurable values:**
| Value | Setting |
|-------|---------|
| Test command | `pnpm test` |
| Lint command | `pnpm lint` |
| Branch model | `main` -> `develop` -> `feature/PROJ-NNN-slug` |
| Worktree path | `../wt-{shortname}` |
| Commit format | `feat(scope): description` (Conventional Commits) |
| Package file | `package.json` |

**Files that change vs Python/FastAPI:**

| File | What Changes |
|------|-------------|
| `constitution/tech-stack.md` | Entirely rewritten |
| `constitution/principles.md` | Articles reference React patterns, Prisma conventions, Tailwind classes instead of FastAPI/Jinja2/SQLModel |
| `constitution/quality-policy.md` | Validation steps reference vitest, eslint, Playwright |
| Core skills (`testing-conventions`, `git-workflow`) | Test commands, fixture names, branch model |
| Domain skills | All 3 are new: vitest-runner, nextjs-routes, react-components |
| Worker agents | Design constraints reference React/Tailwind instead of HTMX/Jinja2 |
| CLI scripts (`qa.py`, `fleet.py`) | Test commands and worktree path patterns |

**Files that stay the same:**

All templates, all workflow skills (grill-me, to-spec, to-plan, to-tasks, triage), code-review skill, handoff skill, pi-planning skill, scorecard, ADR template, fleet ledger schema, executive isolation contract, retro protocol.

### 6.3 Go / gRPC

**constitution/tech-stack.md (excerpt):**
```markdown
## Runtime
- Go 1.22+
- Module path: github.com/org/project

## Framework
- gRPC with protobuf
- Connect-Go for HTTP gateway
- Chi router for REST endpoints

## Database
- PostgreSQL 16
- sqlc for type-safe queries

## Testing
- go test with testify assertions
- Test isolation via t.TempDir()
- Custom helpers: setupTestDB, mockGRPCClient
- Baseline: TBD
```

**Domain skills to create:** `go-testing`, `grpc-services`, `protobuf-contracts`

**Key configurable values:**
| Value | Setting |
|-------|---------|
| Test command | `go test ./... -v -count=1` |
| Lint command | `golangci-lint run` |
| Branch model | `main` -> `feature/PROJ-NNN-slug` |
| Worktree path | `../wt-{shortname}` |
| Commit format | `feat(scope): description` |
| Package file | `go.mod` |

### 6.4 C# / .NET

**constitution/tech-stack.md (excerpt):**
```markdown
## Runtime
- .NET 8 (LTS)
- C# 12

## Web Framework
- ASP.NET Core Minimal APIs or Controllers
- Blazor Server for interactive UI (or Razor Pages for SSR)

## Database
- SQL Server (or PostgreSQL via Npgsql)
- Entity Framework Core

## Testing
- xUnit with FluentAssertions
- Test isolation via in-memory SQLite provider
- Custom fixtures: WebApplicationFactory<Program>, MockHttpClient
- Baseline: TBD
```

**Domain skills to create:** `xunit-runner`, `aspnet-controllers`, `blazor-components`

**Key configurable values:**
| Value | Setting |
|-------|---------|
| Test command | `dotnet test --verbosity normal` |
| Lint command | `dotnet format --verify-no-changes` |
| Branch model | `main` -> `develop` -> `feature/PROJ-NNN-slug` |
| Worktree path | `../wt-{shortname}` |
| Commit format | `feat(scope): description` |
| Package file | `*.csproj` |

### 6.5 Cross-Stack Comparison Matrix

| Aspect | Python/FastAPI | TypeScript/Next.js | Go/gRPC | C#/.NET |
|--------|---------------|-------------------|---------|---------|
| **Files that change** | 0 (reference) | ~12 | ~12 | ~12 |
| **Files unchanged** | All portable (~38) | All portable (~38) | All portable (~38) | All portable (~38) |
| **Domain skills** | 3 | 3 | 3 | 3 |
| **Constitution rewrite** | 0% | ~60% | ~60% | ~60% |
| **Time to adapt** | 0 (already done) | ~45 min | ~45 min | ~45 min |
| **Framework overhead** | Same | Same | Same | Same |

The key takeaway: regardless of stack, you write 3 domain skills, adapt ~12 configurable files, and leave ~38 files untouched. The SDD process, templates, review protocol, and coordination patterns are entirely stack-independent.

---

## 7. Anti-Patterns

These are failure modes observed or anticipated during SDD development. Each anti-pattern includes what goes wrong and how to fix it.

### 7.1 Giving Workers Full Codebase Access

**What happens**: A worker agent given free reign modifies files outside its assigned scope. It "helpfully" refactors a shared utility while implementing a feature, breaking another worker's concurrent changes.

**Why it breaks SDD**: The fleet coordination model depends on workers staying within their assigned file scope. Conflict avoidance is a manual discipline (explicit per-worker file scopes), not an automated detector -- full access removes the only safeguard.

**Fix**: Every agent brief must include an explicit `Files IN scope` and `Files OUT of scope` list. Workers must be instructed: "If you need to modify a file outside your scope, STOP and report to Principal SW Dev."

### 7.2 Skipping the Grill Phase

**What happens**: "We already know what we want" leads to specs built on assumptions. The Architect designs for misunderstood requirements. Workers implement the wrong thing. Review catches the misalignment late, forcing a rework cycle.

**Why it breaks SDD**: The grill phase is where ambiguity is surfaced and resolved CHEAPLY (in conversation, not in code). Skipping it pushes ambiguity resolution to the implementation phase where it costs 10x more.

**Fix**: Make the grill gate mandatory for any feature that touches >3 files or introduces a new pattern. Allow bypass only for bug fixes <3 files.

### 7.3 Specializing Agents Too Early

**What happens**: Before completing a single PI, you create 12 specialized agents with elaborate skill packs. Most are never dispatched. The roster becomes cluttered. Skill maintenance becomes a burden.

**Why it breaks SDD**: Specialization should emerge from repeated dispatch patterns, not from prediction. The auto-promotion mechanic (>=2 dispatches with the same skill set = earn a name) ensures specialists are created from evidence.

**Fix**: Start with 4 generic workers. Add a specialist only when the same generic worker has been dispatched with the same skill combination 2+ times.

### 7.4 Making the Executive Manager Read Raw Artifacts

**What happens**: The Executive Manager chatmode is given access to spec files, task lists, and code diffs. It loses its "big picture" perspective and starts making tactical recommendations.

**Why it breaks SDD**: Executive isolation exists to prevent context overload. The Executive should see a <=2KB state summary, not a 50-page spec. When it reads raw artifacts, its status reports become noisy, unfocused, and filled with implementation details.

**Fix**: Executive Manager reads ONLY `exec/state.md`. State builder regenerates this file from the ledger. No exceptions.

### 7.5 Running Fleet Before Single-Agent Workflow Works

**What happens**: Parallel dispatch is attempted before the serial workflow (triage -> spec -> plan -> tasks -> implement -> review) has been validated. Agents produce incompatible outputs. Integration fails. Nobody knows if the problem is the dispatch or the workflow.

**Why it breaks SDD**: Fleet mode adds coordination complexity on top of the base workflow. If the base workflow has problems, fleet amplifies them.

**Fix**: Complete at least one feature through the full lifecycle with a single worker before attempting fleet dispatch. Phase 3 (Pilot Spec) must succeed before Phase 4 (Fleet Pilot).

### 7.6 Writing Specs for Trivial Changes (Ceremony Bloat)

**What happens**: A 2-file bug fix gets a full spec with 15 sections, a plan with risk assessment, and a task list with dependency graph. The ceremony takes longer than the fix.

**Why it breaks SDD**: SDD includes a spec sizing rule specifically to prevent this. Over-ceremonializing small changes creates resentment toward the framework and incentivizes bypassing it entirely.

**Fix**: Apply the spec sizing rule:

| Change Size | Required Process |
|-------------|-----------------|
| Bug fix < 3 files | Task + test + review. No spec. |
| Feature < 5 files | Lightweight spec (user story + requirements + success criteria only) |
| Feature >= 5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

### 7.7 Letting Workers Make Architectural Decisions

**What happens**: A worker encounters an ambiguous requirement and makes an architectural choice (e.g., "I'll add a new middleware layer" or "I'll create a shared utility module"). The choice is locally reasonable but globally inconsistent.

**Why it breaks SDD**: Architectural decisions (Level 1) belong to the Principal Architect. Workers making them bypasses the ADR process, skips the consistency check, and creates undocumented precedent.

**Fix**: Workers are instructed: "If implementation requires a choice that affects >1 module, STOP and escalate to Principal SW Dev, who will consult Principal Architect." Include this as a stop condition in every agent brief.

### 7.8 Skipping Two-Stage Review

**What happens**: Code review is done as a single pass, mixing spec compliance and code quality concerns. The reviewer says "the code looks good" but misses that a required feature from the spec was not implemented.

**Why it breaks SDD**: The two stages catch different classes of defects. Stage 1 (spec compliance: MISSING/EXTRA/WRONG) verifies correctness against requirements. Stage 2 (code quality: edge cases, security, naming) verifies craftsmanship. Combining them causes one class to dominate and the other to be overlooked.

**Fix**: Always run Stage 1 first. If Stage 1 fails (NOT COMPLIANT), fix and re-review Stage 1 before starting Stage 2. Never jump to code quality review on spec-non-compliant code.

### 7.9 Not Updating CONTEXT.md

**What happens**: After 2 PIs, the project has evolved significantly. New modules exist, patterns have changed, terminology has shifted. But CONTEXT.md still reflects the original project. Agents use outdated vocabulary and patterns.

**Why it breaks SDD**: CONTEXT.md is the shared language that keeps all agents aligned. When it drifts from reality, agents produce increasingly incoherent work -- using old module names, referencing deprecated patterns, misunderstanding current architecture.

**Fix**: Update CONTEXT.md in every `grill-with-docs` session. Add it to the sprint retro checklist: "Is CONTEXT.md still accurate?" Schedule a full CONTEXT.md review at every PI boundary.

### 7.10 Treating SDD as a Rigid Process

**What happens**: A team follows every step mechanically, even when the step adds no value. Retros surface complaints but nobody acts on them because "the process says to do it this way."

**Why it breaks SDD**: SDD is a framework, not a religion. The retro exists specifically to identify and remove process friction. If a gate adds no value, the retro should recommend removing it. If a ceremony is too heavy, the retro should recommend lightening it.

**Fix**: Every retro must include the question: "Which parts of SDD helped this sprint? Which parts hindered it?" Act on the answers. Document adaptations in CONTEXT.md or a process-focused ADR.

---

## 8. Evolution Path

SDD is designed to grow incrementally. Do not attempt to implement everything at once. The phases below represent maturity stages, not a waterfall plan.

### 8.1 Phase 1: Manual Dispatch (Start Here)

**What you have**: Constitution, templates, chatmodes, skills, prompts, and a CLI that generates dispatch packets but does NOT spawn processes.

**How it works**: You run `/fleet` in the SW Dev chatmode. The CLI emits a launch table telling you which VS Code windows to open and which dispatch files to use. You manually launch each worker.

**Value delivered**: Full traceability (ledger), conflict prevention (pre-dispatch checks), consistent prompts (composer), quality gates (two-stage review). All of this works without any automation.

**Duration**: Use this until you have completed 2-3 features through the full lifecycle and the manual process feels routine.

### 8.2 Phase 2: CLI Automation

**What changes**: The `fleet.py` script gains a `--auto` flag that spawns worker processes via a headless CLI runtime (recommended: `gh copilot` CLI). Workers post status back to the ledger via `common/ledger.py`.

**Prerequisite**: Manual dispatch has been validated. You know which conflict rules work and which need adjustment. The ledger schema is stable.

**Value added**: Reduced manual overhead. Workers can be dispatched and monitored from a single terminal. Batch completion triggers automatic review prompts.

### 8.3 Phase 3: Metrics and Dashboard

**What changes**: After 3+ PIs of data in the ledger, you have enough signal to build meaningful metrics. Optionally, add a dashboard page to your application or a standalone report generator.

**Metrics to track**:
- Cycle time: idea-to-spec, spec-to-merged
- Velocity: tasks completed per sprint (rolling average)
- Quality: defects escaping review, test coverage trends
- Fleet: conflicts per batch, batch success rate
- Process: ceremony time vs implementation time ratio

**Prerequisite**: At least 3 PIs of ledger data. The scorecard from `SCORECARD.md` should have baseline values established.

### 8.4 Phase 4: MCP Server Wrapping

**What changes**: If you need to share SDD across an organization, wrap the CLI layer as an MCP server. This allows other tools (VS Code extensions, CI/CD pipelines, custom UIs) to interact with the SDD process programmatically.

**When to consider**: When 3+ projects use SDD and you want centralized tooling.

**What the MCP server exposes**:
- `sdd_dispatch_batch`: Create dispatch packets for a sprint batch
- `sdd_check_lock_state`: Report the serial CLARIFY/SPEC gate state before dispatch (`fleet.py` `_scan_lock_state`)
- `sdd_query_ledger`: Query fleet.db for status, metrics, history
- `sdd_compose_prompt`: Build a runtime agent prompt from base + skills + context
- `sdd_update_state`: Regenerate `exec/state.md`

### 8.5 Symbolic vs Wall-Clock Time [PORTABLE]

SDD ceremonies use traditional cadences (10-week PI, 2-week sprints) regardless of executor speed. An AI fleet may compress a PI into days; a human team may take the full quarter. The cadence is a planning lattice, not a deadline.

Tooling that displays "sprint progress" should show both the symbolic position (Sprint 2 of 5) and elapsed wall-clock time, never collapse the two.

This distinction is critical for portability: if the framework used "1-week sprints because agents are fast," it would not transfer to human teams without rewriting all artifacts and ceremonies.

### 8.6 Phase 5: Cross-Organization Sharing

**What changes**: GENERALIZATION_SDD.md (this file) becomes the onboarding guide for new projects. Each new project adoption produces feedback that refines the tagging table, bootstrap process, and anti-patterns.

**Growth mechanism**: Every new project that adopts SDD should:
1. Follow the bootstrap process (Section 3)
2. Record deviations and reasons
3. Run a "framework retro" after the first PI
4. Contribute learnings back to GENERALIZATION_SDD.md

---

## 9. Carrying This to a New Project

This section provides concrete, numbered steps for a developer who wants to adopt SDD for a project that is not the Day-to-Day Agent.

### 9.1 Before You Start

Verify:
- [ ] You have a project repository (new or existing)
- [ ] You have VS Code with GitHub Copilot Chat extension
- [ ] You understand the project's tech stack
- [ ] You have read Sections 1-2 of this document (What is SDD + Tagging System)
- [ ] You have ~3 hours of uninterrupted time

### 9.2 Step-by-Step

**Step 1: Fork or Copy (5 minutes)**

Copy the entire `spec-driven-development/` directory from the reference project to your new project.

```
cp -r reference/spec-driven-development/ ./spec-driven-development/
```

**Step 2: Delete Project-Specific Content (5 minutes)**

Remove all `[PROJECT-SPECIFIC]` data files (keep the directories):

```
# Delete content, keep structure
rm spec-driven-development/backlog/IDEAS.md
rm spec-driven-development/backlog/BACKLOG.md
rm -rf spec-driven-development/specs/*
rm -rf spec-driven-development/sprints/*
rm -rf spec-driven-development/sessions/*
rm -rf spec-driven-development/exec/briefings/*
rm spec-driven-development/docs/ADR/001-*.md   # Keep TEMPLATE.md
```

Create empty placeholder files where needed:

```
touch spec-driven-development/backlog/IDEAS.md
touch spec-driven-development/backlog/BACKLOG.md
```

**Step 3: Fill Configurable Files (45 minutes)**

For each `[CONFIGURABLE]` file, perform value substitution:

| File | What to Change |
|------|---------------|
| `README.md` | Project name, quickstart commands, link targets |
| `constitution/principles.md` | Replace project-specific pattern references with your equivalents |
| `constitution/quality-policy.md` | Replace change types and validation steps |
| `roster/agents.json` | Replace project descriptions, skill references |
| `roster/skills.json` | Replace domain skill entries |
| `roster/skill_packs.json` | Update pack contents to match your skill catalog |
| `cli/fleet.py` | Worktree path pattern, branch naming convention |
| `cli/qa.py` | Test runner commands |
| `cli/common/worktree.py` | Worktree path pattern |

**Step 4: Write Project-Specific Content (30 minutes)**

Create from scratch:

| File | Content |
|------|---------|
| `constitution/mission.md` | Project identity, owner, vision, values, non-negotiables |
| `constitution/tech-stack.md` | Complete tech stack documentation |
| `constitution/roadmap.md` | PI objectives (PI-1 is always "Foundation + SDD Bootstrap") |
| `CONTEXT.md` | Initial vocabulary (10-20 terms), key assumptions, conventions |

**Step 5: Copy Copilot-Native Files to .github/ (20 minutes)**

```
# Portable files (copy as-is)
cp -r reference/.github/prompts/ .github/prompts/
cp -r reference/.github/skills/workflow/ .github/skills/workflow/
cp -r reference/.github/skills/engineering/ .github/skills/engineering/
cp -r reference/.github/skills/operational/ .github/skills/operational/

# Configurable files (copy then adapt)
cp -r reference/.github/chatmodes/ .github/chatmodes/
cp -r reference/.github/agents/ .github/agents/
cp -r reference/.github/skills/core/ .github/skills/core/
cp -r reference/.github/instructions/ .github/instructions/

# Project-specific (create new)
mkdir -p .github/skills/domain/
# Create 2-3 domain skills for your stack
```

**Step 6: Adapt Chatmodes and Agents (20 minutes)**

For each of the 4 chatmodes and 4 agent files:
1. Keep the role structure (responsibilities, what you do/don't do, communication style)
2. Replace project references (name, stack, conventions, file paths)
3. Update skills loaded list to match your skill catalog
4. Update specific rules to match your project's conventions

**Step 7: Create Domain Skills (15 minutes)**

Write 2-3 skills for your tech stack. Each should be <100 lines and teach agents:
- How to run tests in this project
- How to create new routes/endpoints/components
- How to follow the project's UI conventions

**Step 8: Initialize the Fleet Ledger (2 minutes)**

```sql
-- Run the schema creation script against a new fleet.db
sqlite3 spec-driven-development/ledger/fleet.db < schema.sql
```

**Step 9: Run the 3-Hour Bootstrap (Section 3)**

Execute the Hour 1 / Hour 2 / Hour 3 process from Section 3 of this document.

**Step 10: First PI (ongoing)**

Begin PI-1: "Foundation + SDD Bootstrap." Use the full SDD lifecycle for your first 1-2 features. Run a retro after each sprint. Update framework files based on learnings.

### 9.3 Validation Checklist

After bootstrap, verify:

- [ ] All 4 Principal chatmodes appear in VS Code Copilot model picker
- [ ] Slash commands (`/triage`, `/spec`, `/plan`, etc.) are invocable
- [ ] Domain skills load correctly when attached to a chat session
- [ ] `constitution/` files are internally consistent (no contradictions)
- [ ] `CONTEXT.md` defines at least 10 project-specific terms
- [ ] One feature has been run through the full lifecycle (triage -> spec -> plan -> tasks -> implement -> review)
- [ ] `fleet.db` ledger is initialized and writable
- [ ] Test baseline is established and documented in `tech-stack.md`
- [ ] Retro from pilot feature produced at least 1 actionable improvement
- [ ] No references to the original project remain in any adapted file

---

## 10. Version History

### v0.1 (2026-05-07)

Initial framework extraction from the Day-to-Day Agent project.

**Scope**:
- Complete three-tier tagging system with file-by-file table
- Bootstrap process (3-hour guide)
- Greenfield vs brownfield adoption paths
- Team size adaptation matrix (solo through medium teams)
- Four multi-stack examples (Python, TypeScript, Go, C#)
- Ten anti-patterns with fixes
- Five-phase evolution path
- Step-by-step adoption guide for new projects

**Sources**:
- Dual-LLM planning: Claude Opus 4.7 + GPT 5.5 (synthesis of complementary strengths)
- Independent reviewer cross-review (adversarial validation of plan coherence)
- Spec-Kit (vocabulary alignment: `constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`)
- Matt Pocock skills philosophy (composable, small, owned by the developer)
- DeepLearning.AI SDD course (spec-driven lifecycle patterns)
- SAFe (adapted for solo/small team: PI planning, sprint cadence, ROAM risk classification)

**Known gaps for v1.0**:
- Multi-stack examples are structural only; they need validation by running bootstrap on actual TypeScript, Go, and C# projects
- Fleet coordination rules are theoretical until Phase 4 (Fleet Pilot) is completed
- Brownfield onboarding script is not yet automated
- Greenfield constitution wizard is not yet automated
- Team size adaptation beyond solo has not been tested
- No metrics from actual SDD usage yet (need 3+ PIs of ledger data)

**Planned for v1.0** (after Phase 3-4 completion):
- Validated multi-stack bootstrap (at least one non-Python project)
- Fleet coordination rules refined from actual dispatch data
- Metrics baseline from first PI
- Brownfield/greenfield onboarding scripts (CLI)
- Process friction points identified and addressed from retro data

---

## Appendix A: Portable Patterns Reference

These patterns are the intellectual core of SDD. They are fully `[PORTABLE]` and apply to any project regardless of stack.

### A.1 Four-Principal Pattern

Four strategic roles that never implement code:

| Role | Owns | Key Question |
|------|------|-------------|
| Executive Manager | Status and routing | "What's the current state?" |
| Product Manager | What and when | "What should we build next?" |
| Architect | How (design) and why (decisions) | "How should we build it?" |
| Software Developer | How (implementation) and integration | "How do we break this into tasks?" |

### A.2 Generic-Then-Specialize Roster

Start with 4 generic worker roles: Developer, UX Designer, Data Scientist, QA Engineer. Specialists are promoted from generics after >=2 dispatches with the same skill combination. Named using `{role}-{firstname}-{domain}-{NNN}` convention.

### A.3 Skill Composition Algorithm

Runtime prompt = Base role prompt + Skill 1 + ... + Skill N + CONTEXT.md + Task brief. The composer assembles this at dispatch time. Skills are <100 lines each, composable, and independently versionable.

### A.4 Two-Folder Split

`.github/` for Copilot-native files (auto-discovered by VS Code). `spec-driven-development/` for framework files (process state, not tool integration). Principals live as chatmodes in `.github/chatmodes/`. Workers live as agents in `.github/agents/`.

### A.5 Executive Isolation Contract

Executive Manager reads ONLY `exec/state.md` (<=2KB, auto-generated). Never reads raw specs, plans, tasks, or code. Questions outside state.md scope are routed to the appropriate Principal via a routing memo.

### A.6 Two-Stage Code Review

Stage 1 (Spec Compliance): MISSING features, EXTRA features, WRONG implementations. Must pass before Stage 2.
Stage 2 (Code Quality): Edge cases, security, naming, conventions. CRITICAL / IMPORTANT / SUGGESTION classifications.

### A.7 Spec Sizing Rule

Bug fix <3 files = no spec. Feature <5 files = lightweight spec. Feature >=5 files = full spec. Cross-cutting = full spec + ADR.

### A.8 Grill Protocol

One question at a time. Agent recommends an answer. Human confirms, modifies, or rejects. Maximum 7 questions per session. Answers recorded in clarification-log.md.

### A.9 Three Decision Levels

Level 0 (Worker): Local, within task scope. No approval needed.
Level 1 (Principal): Cross-module. ADR required. Principal approves.
Level 2 (Human): Irreversible. Human approval required before implementation begins.

### A.10 Eight Stop Conditions

Stop implementation if: (1) on master branch, (2) no linked spec for non-trivial change, (3) critical clarification remains, (4) test baseline not established, (5) shared-file conflict in fleet batch, (6) security reviewer finds critical issue, (7) architecture reviewer rejects plan, (8) gate fails twice consecutively.

---

## Appendix B: Configurable Values Reference

When adapting SDD for a new project, these are the values you need to substitute in `[CONFIGURABLE]` files.

| Value | Where Used | Example (Python) | Example (TypeScript) |
|-------|-----------|-------------------|---------------------|
| Project name | Constitution, chatmodes, README | Day-to-Day Agent | MyApp |
| Owner / team | mission.md, chatmodes | Rodolfo Lerma | Team Name |
| Primary branch | git-workflow skill, fleet.py | `master` | `main` |
| Development branch | git-workflow skill, fleet.py | `integration/improvements` | `develop` |
| Feature branch pattern | git-workflow skill | `feature/f{N}.{M}-slug` | `feature/PROJ-NNN-slug` |
| Worktree path pattern | worktree.py, fleet.py | `../wt-{shortname}` | `../wt-{shortname}` |
| Test command | testing-conventions, qa.py, agents | `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short` | `pnpm test` |
| Lint command | quality-policy, qa.py | `ruff check agent/ tests/` | `pnpm lint` |
| Commit format | git-workflow skill, agents | `type: short description` | `feat(scope): description` |
| Package file | tech-stack.md | `requirements.txt` | `package.json` |
| Test baseline count | tech-stack.md, qa-engineer agent | 743 tests | TBD |
| Test isolation fixture | testing-conventions | `patched_settings` + `tmp_path` | `createTestDb` |
| Mock pattern | testing-conventions | `MockLLMClient` | `vi.mock()` |
| Source directory | agents, fleet-coordinator | `agent/` | `src/` |
| Test directory | agents, fleet-coordinator | `tests/` | `__tests__/` or `tests/` |

---

## Appendix C: Quick-Reference Decision Guide

Use this when you are unsure which part of SDD applies to your current situation.

| Situation | Action | Reference |
|-----------|--------|-----------|
| "I have a new idea" | Seed in IDEAS.md, run `/triage` | Section 3 (Hour 3, Step 3.2) |
| "I want to start a new project with SDD" | Run the 3-hour bootstrap | Section 3 |
| "I want to add SDD to an existing project" | Follow brownfield onboarding | Section 4.2 |
| "I need to adapt SDD for TypeScript" | Swap configurable values per Section 6 | Section 6.2 |
| "My team has 5 people" | Use small team configuration | Section 5.1 |
| "Workers are modifying files outside their scope" | Fix: explicit file scoping in agent briefs | Anti-Pattern 7.1 |
| "Specs take too long for small changes" | Apply spec sizing rule | Anti-Pattern 7.6 |
| "I want to run parallel agents" | Validate single-agent first, then fleet | Anti-Pattern 7.5, Section 8.1 |
| "I want to share SDD across my org" | Consider MCP server wrapping at Phase 4 | Section 8.4 |
| "Something about SDD is not working" | Run retro, identify friction, adapt | Anti-Pattern 7.10 |
