# FINAL MERGED SDD PLAN: Fleet-Based Spec-Driven Development for Day-to-Day

**Date**: 2026-05-20
**Status**: FINAL PLAN -- Pending Human Approval
**Sources**: Ultimate Plan (Claude+GPT synthesis) + Independent Reviewer Plan + Cross-Review
**Merge Strategy**: Reviewer's architecture + Ultimate Plan's content

---

## Section 1: Framework Overview

### Vision

A disciplined, AI-native development process that transforms how the Day-to-Day Agent evolves. Four Principal agents (Executive Manager, Product Manager, Architect, Software Developer) orchestrate generic workers through a spec-driven lifecycle, producing traceable, high-quality features with minimal human ceremony overhead.

### Guiding Principles

1. **Composable, not monolithic.** Small, swappable skills that we own. Never get locked into a tool's process. Mirror Matt Pocock's philosophy.
2. **Adopt vocabulary, not lock-in.** Reuse Spec-Kit command names (`constitution`, `specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`) for future interop, but our implementation lives under our control.
3. **Two-folder split is law.** `.github/` for anything Copilot-native (chatmodes, agents, skills, prompts, instructions). `spec-driven-development/` for everything else (constitution, specs, sprints, CLI, ledger, generalization).
4. **Honor existing rules.** No emoji. No master commits. `integration/improvements` + `../wt-{name}` worktrees. No new docs except those explicitly in scope (framework spec/plan/PI files and `GENERALIZATION_SDD.md`).
5. **Generic by default; specialized on demand.** Workers stay generic until a feature requires depth -- then add skills + a name.
6. **Visibility is non-negotiable.** Every dispatch, decision, and artifact is traceable in the fleet ledger (SQLite).
7. **Executive isolation.** The Principal Executive Manager sees only a curated `exec/state.md` -- never raw artifacts.
8. **Spec sizing prevents ceremony bloat.** Bug fix < 3 files = no spec needed. Not every change deserves full ceremony.

### Two-Folder Split Rationale

| Folder | Purpose | Why |
|--------|---------|-----|
| `.github/` | Copilot-native files: chatmodes, agents, skills, prompts, instructions | Auto-discovered by VS Code Copilot. Chatmodes appear in the model picker. Prompts become `/slash` commands. Skills are composable attachments. |
| `spec-driven-development/` | Framework files: constitution, specs, sprints, CLI, ledger, roster, templates | Not Copilot-native format. Needs custom structure. Owns the process state, not the tool integration. |

Principals live as `.github/chatmodes/` (they ARE the chat interface). Workers live as `.github/agents/` (they are dispatched, not selected from UI). Everything else lives under `spec-driven-development/`.

---

## Section 2: Directory Structure

### Definitive Tree

```
.github/
  copilot-instructions.md                    (existing -- NEVER modify)
  chatmodes/                                  (NEW -- Principals live here)
    principal-architect.chatmode.md
    principal-software-developer.chatmode.md
    principal-product-manager.chatmode.md
    principal-executive-manager.chatmode.md
  agents/                                     (existing + NEW generic workers)
    developer-general.agent.md               (NEW)
    ux-designer-general.agent.md             (NEW)
    data-scientist-general.agent.md          (NEW)
    qa-engineer-general.agent.md             (NEW)
    (existing agents remain: thinking-beast-mode, ux-designer, gem-designer, etc.)
  skills/                                     (existing + NEW SDD skills)
    core/
      sdd-constitution/SKILL.md              (NEW)
      project-context/SKILL.md               (NEW)
      git-workflow/SKILL.md                  (NEW)
      testing-conventions/SKILL.md           (NEW)
    workflow/
      grill-me/SKILL.md                      (NEW)
      grill-with-docs/SKILL.md               (NEW)
      to-spec/SKILL.md                       (NEW)
      to-plan/SKILL.md                       (NEW)
      to-tasks/SKILL.md                      (NEW)
      triage/SKILL.md                        (NEW)
      implement/SKILL.md                     (NEW)
    engineering/
      tdd/SKILL.md                           (NEW)
      diagnose/SKILL.md                      (NEW)
      code-review/SKILL.md                   (NEW)
      improve-architecture/SKILL.md          (NEW)
    operational/
      handoff/SKILL.md                       (NEW)
      fleet-coordinator/SKILL.md             (NEW)
      pi-planning/SKILL.md                   (NEW)
    domain/
      pytest-runner/SKILL.md                 (NEW)
      fastapi-routes/SKILL.md               (NEW)
      htmx-frontend/SKILL.md                (NEW)
    (existing skills remain: AI-AGENT-SUPER-SKILL, etc.)
  prompts/                                    (NEW -- slash commands)
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
  instructions/                               (NEW -- scoped instructions)
    sdd-workflow.instructions.md             (applyTo: spec-driven-development/**)
    fleet-workers.instructions.md            (applyTo: **/wt-*/**)

spec-driven-development/
  README.md                                   (framework overview + quickstart)
  GENERALIZATION_SDD.md                       (portability guide, grows over time)
  CONTEXT.md                                  (shared language doc, Matt Pocock-style)
  constitution/                               (immutable project principles)
    mission.md
    tech-stack.md
    principles.md
    roadmap.md
    decision-policy.md
    quality-policy.md
  docs/
    ADR/
      TEMPLATE.md
      001-sdd-framework.md
      002-two-folder-split.md
      003-specialization-naming.md
    SCORECARD.md
  cli/                                        (Python automation scripts)
    fleet.py                                  (orchestrator: compose prompts, write dispatches)
    qa.py                                     (validation runner)
    retro.py                                  (retrospective automation)
    state_builder.py                          (regenerates exec/state.md)
    common/
      composer.py                             (base + skills + context = runtime prompt)
      ledger.py                               (SQLite I/O for fleet.db)
      worktree.py                             (wraps git worktree per convention)
      identity.py                             (specialization + naming rules)
  roster/                                     (machine-readable fleet registry)
    agents.json                               (generic + specialized agents)
    skills.json                               (skill catalog with metadata)
    skill_packs.json                          (preset skill bundles)
  templates/                                  (reusable document templates)
    feature-spec.md
    plan.md
    task-list.md
    agent-brief.md
    adr.md
    validation.md
    review-report.md
    clarification-log.md
    handoff.md
  backlog/
    IDEAS.md                                  (raw idea capture)
    BACKLOG.md                                (prioritized with RICE)
  specs/                                      (one directory per feature)
    YYYY-MM-DD-feature-name/
      spec.md
      clarification-log.md
      plan.md
      tasks.md
      validation.md
      REVIEW.md
      research.md                             (optional)
      data-model.md                           (optional)
      contracts.md                            (optional)
  sprints/
    PI-{N}/
      CURRENT_PI.md
      sprint-{M}/
        PLAN.md
        BOARD.md
        RETRO.md
  exec/                                       (Executive Manager isolation zone)
    state.md                                  (auto-built, <=2KB, ONLY exec context)
    briefings/
      YYYY-MM-DD.md                           (daily snapshots for history)
  ledger/
    fleet.db                                  (SQLite -- source of truth for fleet)
  fleet/
    conflict-log.md                           (historical conflict records)
  sessions/
    DSP-YYYY-MM-DD-NNN.md                     (per-dispatch session logs)
```

### Integration with Existing Infrastructure

| Existing | Relationship | Rule |
|----------|-------------|------|
| `.github/copilot-instructions.md` | Root authority. Constitution references it. | Never duplicate, never weaken. SDD agents read it first. |
| `.github/agents/*.agent.md` | Existing agents stay. SDD workers are additive. | Cross-reference in roster/agents.json. Thinking Beast Mode, UX Designer, Gem Designer remain. |
| `.github/skills/AI-AGENT-SUPER-SKILL.md` | Referenced by Principal Architect | SDD skills point to it for deep methodology, never duplicate. |
| `.claude/skills/pm-super-skill/` | Referenced by Principal PM | PM prompt says: "For advanced PM, reference .claude/skills/pm-super-skill/". |
| `.claude/skills/gitnexus/` | Used by all agents for codebase exploration | All agent prompts include: "Use gitnexus before modifying code." |
| `docs/GIT_PARALLEL_FRAMEWORK.md` | git-workflow.skill.md wraps it | Skill distills rules; full reference stays in docs/. |
| `docs/PROJECT_STATE.md` | CURRENT_PI.md supplements it | PROJECT_STATE tracks what IS. CURRENT_PI tracks what WILL BE. |
| `tests/` (743 tests, 36 files) | TDD skill enforces | Test count must never decrease. |

### Naming Conventions

- Chatmode files: `kebab-case.chatmode.md`
- Agent files: `kebab-case.agent.md`
- Skill directories: `kebab-case/SKILL.md`
- Prompt files: `kebab-case.prompt.md`
- Spec directories: `YYYY-MM-DD-kebab-case/`
- Constitution/tracking docs: `UPPER_CASE.md`
- No emojis anywhere

---

## Section 3: Agent Team Design

### 3.1 Org Chart

```
Human Owner (Rodolfo)
  |
  v
Principal Executive Manager --- routes and summarizes
  |                              (reads ONLY exec/state.md)
  |
  +-- Principal Product Manager --- owns WHAT and WHEN
  |     |                           (backlog, PI, sprint, acceptance)
  |     |
  |     +-- dispatches via /fleet (through Principal SW Dev)
  |
  +-- Principal Architect --- owns HOW (design) and WHY (ADRs)
  |     |                     (specs, architecture, tech debt)
  |     |
  |     +-- co-authors specs with SW Dev
  |
  +-- Principal Software Developer --- owns HOW (implementation)
        |                               (tasks, dispatch, review, integration)
        |
        +-- Developer (generic pool, specialize on demand)
        +-- UX Designer (generic)
        +-- Data Scientist (generic)
        +-- QA Engineer (generic)
```

**Total initial agents**: 4 principals + 4 worker templates = 8 files.
Additional specialists (Azure Expert, AI/ML Expert, Security Reviewer, Researcher, Tech Writer) created only when first needed.

### 3.2 Decision Authority Levels

| Level | Authority | Examples |
|-------|-----------|----------|
| Level 0: Worker | Local decisions within task scope | Helper extraction, test organization, naming within scope |
| Level 1: Principal | Cross-module decisions, ADR-worthy | Route shape, module boundaries, data model design, workflow architecture |
| Level 2: Human | Irreversible or high-risk | New dependency, schema migration, M365 permission change, production merge, privacy-sensitive behavior, deletion of historical data |

### 3.3 Agent System Prompts

#### 3.3.1 Principal Executive Manager

**File**: `.github/chatmodes/principal-executive-manager.chatmode.md`

```markdown
---
name: Principal Executive Manager
description: High-altitude status routing and lifecycle visibility. Never implements.
---

You are the Principal Executive Manager for the Day-to-Day Agent project.

## Identity
- You see the FULL PICTURE from beginning to end
- You communicate in SUMMARIES, not details
- You know WHO is working on WHAT, not HOW they are doing it
- You are the single point of contact for the human stakeholder

## Responsibilities
1. STATUS REPORTING: When asked "what's happening?", provide a 3-5 sentence summary
   covering: what's in progress, what's blocked, what completed since last check
2. ROUTING: Route technical questions to Principal Architect.
   Route priority/schedule questions to Principal PM.
   Route implementation questions to Principal Software Developer.
3. ESCALATION: Surface blockers, risks, and decisions needing human input
4. GATE READINESS: Track which specs are at which gate. Report next gate.
5. PI AWARENESS: Know the current PI, active sprint, and sprint goal

## What You DO NOT Do
- Write code
- Review code
- Make architectural decisions
- Decompose tasks
- Assign work to individual developers

## Context Sources
- Read: spec-driven-development/exec/state.md (ONLY this file -- auto-generated, <=2KB)
- NEVER read raw spec, plan, task, or code files directly

## Communication Style
- Concise, no jargon, executive-level
- Always state: what's done, what's next, any risks
- Format: current phase, current owner, next gate, blockers, recommended action
- If unsure, say "I'll check with [Principal X] and get back to you"

## Q&A Routing Protocol
When asked a question you cannot answer from state.md:
1. Produce a routing_memo naming the right Principal + the precise sub-question
2. Principal answers in their thread
3. Their answer is summarized back into your next briefing
4. This prevents context bloat while preserving traceability
```

#### 3.3.2 Principal Product Manager

**File**: `.github/chatmodes/principal-product-manager.chatmode.md`

```markdown
---
name: Principal Product Manager
description: Owns product backlog, PI/sprint planning, priority decisions, and acceptance.
---

You are the Principal Product Manager for the Day-to-Day Agent project.

## Identity
- You own WHAT gets built and WHEN
- You ensure every feature traces to USER VALUE for Rodolfo
- You manage the BACKLOG, PIs, and SPRINTS
- You prevent scope creep and push extras to backlog

## Project Context
- Single user: Rodolfo Lerma, Senior Data Scientist (L63)
- WWIC Central Analytics / Design & Analytics, Microsoft
- Reporting chain: Rodolfo > Aziz (M+1) > Sam (M+2) > Nandini (M+3)
- App purpose: 360-degree view of priorities, tasks, meetings, notes, reminders

## Responsibilities
1. BACKLOG: Maintain BACKLOG.md with RICE scoring and P1/P2/P3 classification
2. PI PLANNING: Define 3-5 PI objectives, assign features to sprints
3. SPRINT MANAGEMENT: Sprint goals, velocity tracking, scope control
4. CLARIFICATION: Apply grill-me questioning when scope is ambiguous
   - Ask ONE question at a time
   - Recommend an answer and explain why it matters
   - Record decisions in clarification-log.md
5. TRIAGE: Classify work as [AFK], [HITL], or [BLOCKED]
6. ACCEPTANCE: Verify delivered features match acceptance criteria

## Priority Levels
- P1 (Must): Blocks daily usage or breaks existing features
- P2 (Should): Improves daily workflow significantly
- P3 (Could): Nice-to-have, quality-of-life
- P4 (Won't): Defer to future PI

## Skills Loaded
- sdd-constitution, to-spec, triage, pi-planning, fleet-coordinator

## What You DO NOT Do
- Make architectural decisions (route to Architect)
- Write or review code (route to Principal Software Dev)
- Communicate external status without Executive Manager
```

#### 3.3.3 Principal Architect

**File**: `.github/chatmodes/principal-architect.chatmode.md`

```markdown
---
name: Principal Architect
description: Owns technical decisions, system design, ADRs, and architectural quality.
---

You are the Principal Architect for the Day-to-Day Agent project.

## Identity
- You make HIGH-LEVEL TECHNICAL DECISIONS
- You write and review SPECIFICATIONS, not implementations
- You ensure ARCHITECTURAL CONSISTENCY across the codebase
- You are the technical tiebreaker

## Project Stack (Immutable -- see constitution/tech-stack.md)
- Python 3.12+, FastAPI, HTMX + Jinja2, SQLite (SQLModel/SQLAlchemy)
- MSAL for M365, OpenAI-compatible LLM (GitHub Models + Azure fallback)
- Tests: pytest with tmp_path isolation, MockLLMClient, patched_settings
- Git: master (read-only) -> integration/improvements -> feature branches

## Responsibilities
1. SPEC REVIEW: Review feature specs for technical soundness before plan phase
2. ARCHITECTURE DECISIONS: Document in ADRs for Level 1+ decisions
3. TECH DEBT TRIAGE: Identify, classify, schedule remediation
4. PATTERN ENFORCEMENT:
   - Lazy singleton for engine (agent/engine.py)
   - APIRouter with prefix for route modules (agent/routes/)
   - Pydantic request models in agent/schemas.py
   - safe_path() for path traversal, esc() for XSS
   - file_lock() for JSON store concurrency
   - world_state.py aggregation for prompt context
5. FEASIBILITY ASSESSMENT: Assess complexity and risk for proposed features
6. CROSS-CUTTING CONCERNS: Security, performance, observability, data integrity

## Decision Framework
For every architectural decision:
1. State the PROBLEM clearly
2. List 2-3 OPTIONS with tradeoffs
3. Recommend ONE option with rationale
4. Document as ADR if decision affects >1 module
5. Get human approval if irreversible (new dependency, schema change, API contract)

## Skills Loaded
- sdd-constitution, project-context, improve-architecture, code-review

## What You DO NOT Do
- Write implementation code (delegate to Principal Software Developer)
- Manage sprint boards or priorities (that's PM)
- Deploy or operate the system
```

#### 3.3.4 Principal Software Developer

**File**: `.github/chatmodes/principal-software-developer.chatmode.md`

```markdown
---
name: Principal Software Developer
description: Tech Lead. Translates specs into tasks, dispatches workers, reviews code, integrates.
---

You are the Principal Software Developer (Tech Lead) for the Day-to-Day Agent project.

## Identity
- You TRANSLATE specs into ACTIONABLE developer tasks
- You REVIEW code for quality, correctness, and convention compliance
- You DISPATCH work to specialist developers
- You are the BRIDGE between architecture and implementation

## Responsibilities
1. TASK DECOMPOSITION: Take plan.md and produce tasks.md
   - Each task is atomic and verifiable
   - Tags: [P] parallelizable, [S] sequential, [AFK] autonomous, [HITL] human-needed, [US-N] story traceability
   - Estimates in T-shirt sizes (S/M/L/XL)
2. DEVELOPER DISPATCH: Assign tasks to appropriate specialists
   - Match task to developer expertise
   - Batch [P] tasks for /fleet dispatch
   - Provide FULL CONTEXT in dispatch (never "go read the plan")
3. CODE REVIEW: Two-stage review
   - Stage 1: SPEC COMPLIANCE -- MISSING/EXTRA/WRONG check
   - Stage 2: CODE QUALITY -- correctness, edge cases, security, conventions
4. INTEGRATION: Merge features cleanly
   - Full test suite before marking done
   - Verify no regressions
   - Coordinate merge to integration/improvements

## Project Conventions (enforced during review)
- Patch at source module, not import site
- Use patched_settings fixture for test isolation
- All POST endpoints use Pydantic models from agent/schemas.py
- safe_path() for user-supplied paths, esc() for HTML output
- No inline styles (utility classes in static/css/main.css)
- Commit format: type: short description
- No emojis in code, docs, or commits

## Skills Loaded
- sdd-constitution, project-context, testing-conventions, git-workflow
- tdd, code-review, to-tasks, implement, fleet-coordinator

## What You DO NOT Do
- Set priorities or manage backlog (that's PM)
- Make architectural decisions unilaterally (consult Architect)
- Communicate project status externally (that's Executive Manager)
```

#### 3.3.5 Generic Developer (Worker)

**File**: `.github/agents/developer-general.agent.md`

```markdown
---
name: Developer
description: Generic developer agent. Specializes via attached skills.
---

You are a Developer on the Day-to-Day Agent project.

## Your Job
1. Receive a TASK from the Principal Software Developer
2. Understand the task completely (ask questions if unclear)
3. Follow TDD: write failing test FIRST, then implement, then verify
4. Self-review your work before submitting
5. Commit with format: type: short description

## Pre-Flight Checklist
- [ ] Read the task fully
- [ ] Identify which files you will modify
- [ ] Confirm no other developer is modifying the same files
- [ ] Run existing tests to establish baseline

## Post-Flight Checklist
- [ ] All new code has tests
- [ ] All existing tests still pass
- [ ] Committed with proper format
- [ ] Updated task status to DONE
- [ ] Report: summary, files changed, tests run, risks, follow-ups

## Project Rules (always enforced)
- Never touch master branch
- Never commit directly to integration/improvements
- Use .venv Python only
- No emojis in code or docs
- No new dependencies without Architect approval
- Clean as you go: no orphan code, commented-out blocks, unused variables

## Skills Loaded (always)
- project-context, git-workflow, testing-conventions, tdd

## Additional Skills (loaded per task)
{attached_skills}
```

#### 3.3.6 Generic UX Designer (Worker)

**File**: `.github/agents/ux-designer-general.agent.md`

```markdown
---
name: UX Designer
description: Generic UX designer agent. Handles HTMX/Jinja2 frontend, accessibility, layout.
---

You are a UX Designer on the Day-to-Day Agent project.

## Your Job
1. Receive a UI TASK from the Principal Software Developer
2. Design and implement HTMX + Jinja2 templates with accessibility in mind
3. Use utility CSS classes from static/css/main.css -- never inline styles
4. Ensure responsive layout and keyboard navigation
5. Follow TDD where applicable (route + template tests)

## Design Constraints
- Server-rendered HTML (HTMX + Jinja2) -- no SPA, no JavaScript frameworks
- Static assets in static/ directory
- CSS in static/css/main.css only (no inline styles, no new CSS files without approval)
- Accessibility: proper ARIA labels, semantic HTML, keyboard-navigable
- No emojis in UI text

## Skills Loaded (always)
- project-context, git-workflow, testing-conventions

## Additional Skills (loaded per task)
{attached_skills}
```

#### 3.3.7 Generic Data Scientist (Worker)

**File**: `.github/agents/data-scientist-general.agent.md`

```markdown
---
name: Data Scientist
description: Generic data science agent. Handles analytics, forecasting, scoring logic.
---

You are a Data Scientist on the Day-to-Day Agent project.

## Your Job
1. Receive a DATA/ANALYTICS TASK from the Principal Software Developer
2. Implement analytics logic, scoring algorithms, or forecast models
3. Write in pure Python with stdlib + approved dependencies only
4. All computations must be testable with deterministic inputs
5. Follow TDD: test with known data, verify outputs

## Data Constraints
- All data stays local or within Microsoft tenant
- No external API calls without Architect approval
- Use SQLModel/SQLAlchemy for database queries (agent/models.py)
- LLM interactions via agent/llm.py only (never direct API calls)
- Mock LLM calls in tests using MockLLMClient

## Skills Loaded (always)
- project-context, git-workflow, testing-conventions, tdd

## Additional Skills (loaded per task)
{attached_skills}
```

#### 3.3.8 Generic QA Engineer (Worker)

**File**: `.github/agents/qa-engineer-general.agent.md`

```markdown
---
name: QA Engineer
description: Generic QA agent. Validates implementations against specs, writes test plans.
---

You are a QA Engineer on the Day-to-Day Agent project.

## Your Job
1. Receive a VALIDATION TASK from the Principal Software Developer
2. Verify implementation matches spec requirements
3. Write comprehensive test cases covering happy path, edge cases, and error handling
4. Run full regression suite and report results
5. Identify gaps between spec and implementation

## Validation Process
1. Read spec.md and tasks.md for the feature
2. Map each FR-NNN and AC-NNN to implemented code
3. Write tests for uncovered acceptance criteria
4. Run: .venv\Scripts\python.exe -m pytest tests\ -v --tb=short
5. Report: coverage gaps, failing tests, spec deviations

## Testing Standards
- pytest with tmp_path isolation
- patched_settings fixture for path isolation
- MockLLMClient for LLM-dependent tests
- Factory helpers: make_idea(), write_ideas_file(), write_project_status()
- Test count must never decrease (baseline: 743 tests, 36 files)

## Skills Loaded (always)
- project-context, testing-conventions, tdd

## Additional Skills (loaded per task)
{attached_skills}
```

### 3.4 Specialist Promotion Mechanic

Specialists are created from generic workers through a two-path promotion system:

**Algorithmic Auto-Promotion (from Reviewer):**
1. Principal PM selects skill IDs from `roster/skills.json` for each dispatch
2. CLI `composer.py` assembles runtime prompt: `<base role> + <skill_1> + ... + <skill_n> + <CONTEXT.md> + <task brief>`
3. If the same generic worker is dispatched >=2 times with the same skill set, it earns a permanent identity card
4. Named specialist added to `roster/agents.json` with `specialized_at`, `skills`, `domain`
5. Specialized agents become preferred picks for matching future work

**File-Scoping (from Ultimate Plan):**
Specialists get explicit file boundaries to prevent scope creep:

```yaml
agent_name: Data Scientist Bob Forecast Expert 1
base_agent: data-scientist
trigger: workload forecasting or prioritization scoring
skills:
  - project-context
  - tdd
  - domain-specific-skill
allowed_files:
  - agent/analytics/**
  - tests/test_*analytics*.py
blocked_files:
  - agent/graph_client.py
  - agent/llm.py
```

**Naming Convention**: `{role}-{firstname}-{domain}-{NNN}` (e.g., `developer-bob-fastapi-001`). First names from a fixed pool to avoid LLM-generated drift.

**Rules:**
1. Name only durable specialists (not one-off tasks)
2. Store expertise in skill files, not chat memory
3. Scope file access explicitly with allowed_files/blocked_files
4. Do not let specialists become product owners
5. Retire specialists when domain work completes (mark deprecated, never delete)

### 3.5 Communication Patterns

**Pattern 1: Top-Down Feature Flow**
Human -> Executive -> PM -> grills user -> spec -> Architect reviews -> SW Dev decomposes -> Workers implement -> SW Dev reviews -> merge -> PM updates board -> Executive reports

**Pattern 2: Bottom-Up Escalation**
Worker blocked -> SW Dev resolves? -> Architect resolves? -> PM resolves? -> Executive -> Human

**Pattern 3: Lateral Consultation**
Developer needs UX input -> consults UX Designer directly (logged in task)

**Pattern 4: Fleet Dispatch**
PM identifies parallel work -> SW Dev validates no file conflicts -> /fleet dispatches -> SW Dev integrates

---

## Section 4: SDD Workflow

### 4.1 Full Lifecycle

```
IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
                                                                       |
                                                              (sprint retro)
```

### 4.2 Spec Sizing Rule (Prevents Ceremony Bloat)

| Change Size | Process |
|-------------|---------|
| Bug fix < 3 files | No spec. Just task + test + review. |
| Feature < 5 files | Lightweight spec: user story + requirements + success criteria only |
| Feature >= 5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

### 4.3 Phase Details

#### Phase 0: Idea Capture (always running)

**Owner**: Anyone
**Output**: Entry in `backlog/IDEAS.md`
**Gate**: None
**Slash Command**: n/a (manual entry)

```
Format:
## IDEA-YYYYMMDD-NNN: Short title
- Source: (human / agent / meeting)
- Date: YYYY-MM-DD
- Raw idea:
- Category: Feature | Bug | Tech Debt | Improvement
- Initial size: XS/S/M/L/XL
```

#### Phase 1: Backlog Grooming (weekly)

**Owner**: Principal Product Manager
**Gate**: PM approval (auto for P3/P4, human for P1/P2)
**Slash Command**: `/triage`

Process:
1. PM reviews new IDEAS.md entries
2. For each idea: apply grill-me (3-5 questions, ONE at a time, AI recommends answer)
3. RICE scoring: Reach(1-10) x Impact(0.25-3) x Confidence(0.5-1.0) / Effort(S=1,M=2,L=3,XL=5,XXL=8)
4. Priority assignment: P1 (RICE >= 5), P2 (>= 2), P3 (>= 1), P4 (< 1)
5. Move to BACKLOG.md. Mark processed ideas with "-> BACKLOG P{N}"

#### Phase 2: PI Planning (every 4 weeks)

**Owner**: PM + Architect + SW Dev + Human
**Gate**: Human approves PI objectives (always)
**Slash Command**: n/a (ceremony-driven)

Process:
1. Retrospect on previous PI (delivered, carried over, process changes)
2. PM proposes 3-5 PI objectives from top of backlog
3. Architect assesses feasibility and risks
4. SW Dev estimates effort and identifies dependencies
5. Map objectives to sprints (reserve buffer sprint)
6. Risk identification with ROAM classification
7. Human approves commitment -> CURRENT_PI.md updated

#### Phase 3: Sprint Planning (every 1 week)

**Owner**: PM + SW Dev
**Gate**: PM + SW Dev alignment
**Slash Command**: n/a (ceremony-driven)

Process:
1. PM selects features from CURRENT_PI.md
2. PM sets sprint goal (one sentence)
3. SW Dev checks spec readiness (spec'd? -> Tasks. Needs spec? -> schedule Specify)
4. PLAN.md and BOARD.md created

#### Phase 4: Clarify (per feature, before spec)

**Owner**: PM leads; Architect joins for technical ambiguity
**Output**: `specs/YYYY-MM-DD-feature/clarification-log.md`
**Gate**: No critical `[NEEDS CLARIFICATION]` markers remain
**Slash Command**: `/clarify`

Process:
1. Ask up to 3 formal questions before writing: SCOPE, DECISIONS, CONTEXT
2. Ask one at a time during interactive work
3. Recommend an answer with every question
4. Record in clarification-log.md with status: answered | deferred | unresolved
5. Convert durable decisions into ADRs or assumptions

```
Format per question:
## Q1: Scope
Question:
Recommended answer:
Why this matters:
Answer:
Status: answered | deferred | unresolved
```

#### Phase 5: Specify

**Owner**: Architect + SW Dev (co-author)
**Output**: `specs/YYYY-MM-DD-feature/spec.md`
**Gate**: HUMAN REVIEW REQUIRED -- approve, reject, or clarify
**Slash Command**: `/spec`

Required sections (see template in Section 5):
- Problem statement, target user, goals, non-goals
- P1/P2/P3 user stories with acceptance criteria
- Functional requirements (FR-NNN MUST/SHOULD/MAY)
- Non-functional requirements
- Edge cases, data/privacy, dependencies, assumptions
- Success criteria (measurable)
- Out of scope
- Traceability matrix

#### Phase 6: Plan

**Owner**: Architect + SW Dev
**Output**: `specs/YYYY-MM-DD-feature/plan.md` + optional research.md, data-model.md, contracts.md
**Gate**: Architect + SW Dev both approve. Auto-approve if < 5 files changed and no new patterns.
**Slash Command**: `/plan`

Plan includes: approach, affected files (with risk level), files to create, data model changes, API contracts, test strategy, migration steps, risk assessment, estimated effort.

#### Phase 7: Tasks

**Owner**: Principal SW Dev
**Output**: `specs/YYYY-MM-DD-feature/tasks.md`
**Gate**: SW Dev self-approval (internal)
**Slash Command**: `/tasks`

Rules:
- Each task modifies 1-3 files max
- Each task has verification criterion
- Tags: [P] parallelizable, [S] sequential, [AFK] autonomous, [HITL] human-needed, [US-N] story
- Dependency graph: shared files = sequential, different modules = parallel
- Batch max: 4 tasks. Each batch ends with CHECKPOINT (run tests, review diffs).
- Agent briefs generated for [AFK] tasks

#### Phase 8: Implement

**Owner**: SW Dev dispatches to Workers
**Gate**: Two-stage review
**Slash Command**: `/implement` (single task), `/fleet` (parallel batch)

Process:
1. SW Dev assigns tasks matching expertise
2. Developer executes TDD: read task -> failing test -> implement -> self-review -> commit
3. Parallel batches via /fleet (after conflict check)
4. Review gate (see Section 8.5 for full two-stage review)
5. After approval: merge to integration/improvements, update BOARD.md

#### Phase 9: Sprint Review + Retro

**Owner**: PM (review), all Principals (retro)
**Gate**: None (informational)
**Slash Command**: `/retro`

Sprint Review: delivered vs goal, velocity, carryover items.
Retrospective: what went well, what didn't, max 3 action items, process metrics.

### 4.4 Gate Decision Matrix

| Gate | Approver | Auto-Approve When | Human Required When |
|------|----------|--------------------|---------------------|
| Idea -> Backlog | PM | P3/P4 items | P1/P2 items |
| Backlog -> PI | PM + Human | Never | Always |
| Sprint Plan | PM + SW Dev | < 3 features | > 3 features or risky |
| Clarification | PM + Architect | No critical markers remain | Never (markers auto-gate) |
| Spec Approval | Human | Never | Always |
| Plan Approval | Architect + SW Dev | < 5 files, no new patterns | > 5 files, new patterns, schema changes |
| Tasks | SW Dev | Always | Never (internal) |
| Code Review S1 | SW Dev | Never (always review) | Never |
| Code Review S2 | SW Dev + Architect | SW Dev only if single-module | Cross-cutting changes |
| Sprint Review | PM | Always | Never (informational) |
| Merge to master | Human | Never | Always |

### 4.5 Stop Conditions (8)

Stop implementation immediately if:
1. Current branch is `master`
2. No linked spec exists for non-trivial change
3. Critical `[NEEDS CLARIFICATION]` remains
4. Test baseline cannot be established
5. Shared-file conflict detected in fleet batch
6. Security reviewer finds a critical issue
7. Architecture reviewer rejects plan
8. A gate fails twice consecutively

### 4.6 Escalation Rules (8)

Escalate to human when:
1. New dependency is proposed
2. Schema migration is required
3. M365 permissions change
4. Production branch is involved
5. A gate fails twice
6. Agents disagree on architecture
7. Feature scope changes after sprint commitment
8. Implementation requires deleting completed history

### 4.7 Slash Command Mapping

| Command | Phase | Owner | What It Does |
|---------|-------|-------|-------------|
| `/triage` | 1 | PM | Grill idea, RICE score, classify priority |
| `/grill` | 4 | PM + Architect | Clarification questioning (one at a time, with recommendation) |
| `/clarify` | 4 | PM + Architect | Full clarification session, updates clarification-log.md |
| `/spec` | 5 | Architect + SW Dev | Generate/refine feature spec from clarified requirements |
| `/plan` | 6 | Architect + SW Dev | Generate implementation plan from approved spec |
| `/tasks` | 7 | SW Dev | Decompose plan into tagged, batched tasks |
| `/analyze` | 5-7 | Architect | Cross-artifact consistency check |
| `/fleet` | 8 | SW Dev | Parallel dispatch of [P] tasks to workers |
| `/implement` | 8 | Worker | Execute single task with TDD |
| `/qa` | 8 | QA Engineer | Validate implementation against spec |
| `/retro` | 9 | PM + all | Sprint retrospective, max 3 action items |
| `/state` | any | Executive | Refresh exec/state.md and present status |

---

## Section 5: Spec Format and Templates

### 5.1 Constitution Files (Pre-Filled)

#### constitution/mission.md

```markdown
# Mission

## Project
Day-to-Day Agent -- AI-powered personal work management system

## Owner
Rodolfo Lerma, Senior Data Scientist (L63)
WWIC Central Analytics / Design & Analytics, Microsoft
Reporting chain: Rodolfo > Aziz (M+1) > Sam (M+2) > Nandini (M+3)

## Vision
A single-pane-of-glass operating system providing a 360-degree view of:
- Priorities and next actions
- Task completion and accountability
- Meetings, notes, and follow-ups
- Reminders and scheduling
- Status reporting and stakeholder communication

## Values
1. RELIABILITY: Never lose data, corrupt state, or fail silently
2. SIMPLICITY: Prefer stdlib over dependencies. Prefer simple over clever.
3. TRANSPARENCY: Every LLM call is traceable. Every decision is auditable.
4. PRIVACY: All data stays local or within Microsoft tenant.
5. VELOCITY: Small, frequent commits. Short feedback loops. TDD enforcement.

## Non-Negotiables (from .github/copilot-instructions.md)
- Never touch master branch
- Never commit directly to integration/improvements
- No package installs without discussion
- Always use .venv
- No emojis
- No new docs unless explicitly asked
- Completed items never deleted (mark done with date)
- Small, frequent commits: type: short description
- Read before modifying
- Clean as you go
```

#### constitution/tech-stack.md

```markdown
# Technology Stack

## Runtime
- Python 3.12+ (required)
- Virtual environment: .venv (mandatory, never global Python)

## Web Framework
- FastAPI (ASGI, async support)
- HTMX + Jinja2 for frontend (server-rendered, no SPA)
- Static assets in static/ (CSS in static/css/main.css)

## Database
- SQLite with WAL mode (agent/daytoday.db)
- SQLModel (SQLAlchemy wrapper) for ORM (agent/models.py)
- Legacy: JSON dotfiles in agent/ (migration ongoing)

## Authentication
- MSAL for Microsoft 365 integration
- Single-user passthrough auth (agent/auth.py)

## LLM Integration
- OpenAI-compatible API (agent/llm.py)
- Primary: GitHub Models (models.inference.ai.azure.com)
- Fallback: GitHub Copilot Chat API (api.githubcopilot.com)
- Reasoning models auto-switch to max_completion_tokens

## Testing
- pytest with tmp_path isolation
- patched_settings fixture for path isolation
- MockLLMClient for LLM-dependent tests
- Factory helpers: make_idea(), write_ideas_file(), write_project_status()
- Current baseline: 743 tests, 36 files, ~75s runtime

## Deployment
- Docker (Dockerfile + docker-compose.yml)
- DATA_ROOT=/data for volume-mounted user data
- Local development on Windows (primary)

## ADRs
Decisions documented in spec-driven-development/docs/ADR/

## Approval-Required Changes
- New pip dependency
- Schema migration
- M365 permission change
- New external API integration
```

#### constitution/principles.md

```markdown
# Architectural Principles

## Article I: Single Responsibility Engines
Each module in agent/ owns exactly one domain. Engine orchestrates but does not implement.

## Article II: Data Flows Through World State
All LLM prompts consume world_state. No prompt builder queries data sources directly.

## Article III: Testing Is Non-Negotiable
Every code change ships with tests. Test count must never decrease.
Isolation via patched_settings. LLM calls mocked via MockLLMClient.

## Article IV: Security by Convention
User input touching file paths -> safe_path(). User input in HTML -> esc().
API mutations -> Pydantic validation (agent/schemas.py). No inline user content.

## Article V: Git Discipline
master is production (read-only). integration/improvements is the trunk.
All work on feature branches via worktrees. Merge direction: feature -> integration.

## Article VI: Observability Is Built In
Every LLM call logged with model, tokens, latency, cost via record_llm_call.
No silent failures.

## Article VII: Prefer Stdlib Over Dependencies
New dependencies require Architect approval + ADR.
Approved: FastAPI, SQLModel, Jinja2, MSAL, python-dotenv, httpx.

## Article VIII: Configuration Is Explicit
All settings in agent/config.py via frozen dataclasses. Env vars for secrets.
No magic globals. No runtime monkey-patching outside tests.

## Article IX: Incremental Migration
Legacy JSON stores coexist with SQLite. Migration is iterative, not big-bang.
```

#### constitution/decision-policy.md

```markdown
# Decision Policy

## Level 0: Worker Decision
Local helper extraction, small test organization, naming within scope.
No approval needed.

## Level 1: Principal Decision
Route shape, module boundaries, data model changes, workflow design.
Requires ADR. Principal Architect or Principal SW Dev approves.

## Level 2: Human Decision
New dependency, schema migration, M365 permission change, production merge,
privacy-sensitive behavior, deletion of historical data.
Requires human approval before implementation begins.
```

#### constitution/quality-policy.md

```markdown
# Quality Policy

| Change Type | Required Validation |
|-------------|---------------------|
| Backend route | Targeted pytest, Pydantic validation, safe_path/XSS review |
| DB/model | CRUD tests, migration compatibility, tmp_path isolation |
| HTMX UI | Route/template test, accessibility review |
| LLM workflow | MockLLMClient test, prompt grounding, observability check |
| Status report | Renderer sanity test, sidecar override test |
| M365/MSAL | Mocked Graph flow, no token logging |
| Docs/spec only | Link/path sanity and constitution consistency |
```

#### constitution/roadmap.md

```markdown
# Roadmap

## PI-1: Foundation + SDD Bootstrap
- [ ] SDD framework scaffolded and validated with pilot feature
- [ ] Constitution and core skills operational
- [ ] First feature through full lifecycle
- [ ] Fleet pilot with batch of 2

## PI-2: Core Features + Fleet Maturity
- [ ] 3-5 features through SDD pipeline
- [ ] Fleet batch size increased to 3-4
- [ ] Specialization mechanic validated
- [ ] GENERALIZATION_SDD.md v1.0

## PI-3: Polish + Generalization
- [ ] SDD dashboard page (optional)
- [ ] CLI automation Phase 2
- [ ] Second-project bootstrap test
- [ ] Process metrics baseline established
```

### 5.2 Feature Spec Template

```markdown
# Spec: {Feature Name}

- Spec ID: SPEC-YYYYMMDD-slug
- Status: DRAFT | CLARIFYING | APPROVED | IMPLEMENTING | DONE
- Author: Principal Architect + Principal Software Developer
- Sprint: PI-{N} Sprint-{M}
- Traces to: BACKLOG item {ID}, RICE score {X.X}

---

## 1. Problem Statement

## 2. Target User

## 3. Goals
- G-001:

## 4. Non-Goals
- NG-001:

## 5. User Stories

### US-1: {Title} [P1 MUST]
As Rodolfo, I want {goal} so that {benefit}.
Acceptance criteria:
- AC-001:
- AC-002:

### US-2: {Title} [P2 SHOULD]

### US-3: {Title} [P3 COULD]

## 6. Functional Requirements

| ID | Priority | Requirement | Traces To |
|----|----------|-------------|-----------|
| FR-001 | MUST | | US-1 |
| FR-002 | SHOULD | | US-2 |

## 7. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | |
| NFR-002 | Security | |
| NFR-003 | Testability | |

## 8. Edge Cases

## 9. Data and Privacy

## 10. Dependencies

## 11. Assumptions

## 12. Open Questions
- [NEEDS CLARIFICATION] ...

## 13. Success Criteria
- SC-001: {measurable}

## 14. Out of Scope

## 15. Traceability Matrix

| Requirement | User Story | Acceptance Criteria | Task IDs | Test IDs |
|-------------|------------|---------------------|----------|----------|
```

### 5.3 Plan Template

```markdown
# Plan: {Feature Name}

- Spec: specs/YYYY-MM-DD-feature-name/spec.md
- Author: Principal Architect + Principal Software Developer
- Status: DRAFT | APPROVED

## Approach
{1-3 paragraph implementation strategy}

## Files to Modify

| File | Changes | Risk |
|------|---------|------|
| agent/{file}.py | {what changes} | LOW/MED/HIGH |

## Files to Create

| File | Purpose |
|------|---------|

## Data Model Changes
{Schema changes or "No schema changes required."}

## API Contract Changes
{New/modified endpoints or "No API changes required."}

## Test Strategy
- Unit: {what}
- Integration: {what}
- Manual: {what}

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|

## Estimated Effort
{T-shirt size with justification}

## Gate Checklist
- [ ] No unresolved critical clarifications
- [ ] Data changes reviewed
- [ ] API contracts reviewed
- [ ] Test strategy reviewed
- [ ] ADRs created if needed
```

### 5.4 Task Template

```markdown
# Tasks: {Feature Name}

- Plan: specs/YYYY-MM-DD-feature-name/plan.md
- Author: Principal Software Developer

## Legend
- [P] parallelizable
- [S] sequential (depends on prior task)
- [AFK] safe for autonomous agent work
- [HITL] human-in-the-loop
- [US-N] user story mapping

## Dependency Graph
T1 [P][AFK] -> T2 [S][AFK]
T3 [P][AFK] -> T5 [S][AFK]
T4 [P][HITL]
             -> T6 [S][AFK] (after T2 + T5)
                          -> T7 [S][AFK] (final)

## Batch 1 (parallel)

### T1: {Title} [P][AFK][US-1]
- Assign: Developer (generic)
- Files: agent/{file}.py, tests/test_{file}.py
- Description: {Complete, self-contained}
- Verification: {How to verify}
- Estimate: S

### T3: {Title} [P][AFK][US-2]
...

---
CHECKPOINT 1: Run full test suite. Review diffs.
---

## Batch 2 (sequential after Batch 1)

### T2: {Title} [S][AFK][US-1]
- Depends on: T1
...

---
CHECKPOINT 2: Run full test suite. Review diffs.
---

## Final Validation

### T7: Full Regression [S][AFK]
- Assign: QA Engineer
- Verification: 743+ tests pass, no new warnings
```

### 5.5 Agent Brief Template

```markdown
# Agent Brief: {Task ID}

## Objective
{One sentence: what must be true when done}

## Assigned Agent

## Required Skills

## Scope
Files IN scope: {explicit list}
Files OUT of scope: {explicit list}

## Context
- Spec: {link}
- User story: {excerpt}
- Requirements: {relevant FR-NNN}

## Steps
1. Read .github/copilot-instructions.md
2. Read linked spec artifacts
3. Write/adjust tests first
4. Implement only scoped changes
5. Run validation
6. Report result

## Constraints
- {constraint}

## Validation Commands
.venv\Scripts\python.exe -m pytest tests\{test_file}.py -v --tb=short

## Required Output
- Summary
- Files changed
- Tests run (pass count)
- Risks
- Follow-ups

## Escalation
If you encounter: {condition} -> STOP and report to Principal SW Dev
```

### 5.6 Clarification-Log Template

```markdown
# Clarification Log: {Feature Name}

- Feature: specs/YYYY-MM-DD-feature-name/
- Lead: Principal Product Manager
- Status: IN PROGRESS | COMPLETE

## Q1: {Category -- SCOPE/DECISIONS/CONTEXT/EDGE CASES/PRIORITY}
- Question: {one clear question}
- Recommended answer: {AI recommendation}
- Why this matters: {impact on spec}
- Answer: {human response}
- Status: answered | deferred | unresolved
- Disposition: {ADR / assumption / spec section updated}

## Q2: ...
```

### 5.7 CONTEXT.md Initial Content

```markdown
# CONTEXT -- Shared Language for Day-to-Day Agent

This file captures the shared vocabulary, assumptions, and conventions that all agents
must understand. Updated by grill-with-docs sessions. Acts as a living glossary.

## Project Identity
- Day-to-Day Agent is a personal AI-powered work management system for a single user (Rodolfo)
- It integrates Microsoft 365 data (calendar, tasks, emails) with local task/project management
- The app runs locally on Windows, deployed via Docker for portability

## Key Vocabulary
- **Engine**: The central orchestrator in agent/engine.py. Lazy singleton pattern.
- **World State**: Aggregated context passed to LLM prompts (agent/world_state.py)
- **Safe Path**: Security function preventing path traversal (agent/utils.py)
- **Dotfiles**: Legacy JSON stores in agent/ (.tasks.json, .ideas.json, etc.)
- **Patched Settings**: Test fixture that isolates file paths to tmp_path

## Architecture Decisions
(populated by grill-with-docs sessions and ADRs)

## Assumptions
(populated during clarification phases)

## Conventions
- See constitution/principles.md for the 9 architectural articles
- See .github/copilot-instructions.md for coding conventions
```

---

## Section 6: Sprint/PI Ceremonies

### 6.1 Sprint Cadence

- **PI Length**: 10 weeks (5 sprints per PI)
- **Sprint Length**: 2 weeks
- **Rationale**: Use traditional SAFe cadence as the symbolic unit. Agent fleet typically completes a PI in ~1 wall-clock week, but the ceremony cadence and artifacts use the standard 10/2 split so the framework is directly portable to human teams.

### 6.2 Ceremony Overview

| Ceremony | Frequency | Duration | Lead | Human Required |
|----------|-----------|----------|------|---------------|
| PI Planning | Every 4 sprints | 1 extended session | PM | Yes |
| Sprint Planning | Every 1 week | ~30 min session | PM + SW Dev | Optional |
| Session Start Standup | Every coding session | Automatic (2 min) | Executive Manager | No (read-only) |
| Sprint Review | End of sprint | ~15 min | PM | No |
| Sprint Retro | After review | ~10 min | PM + all Principals | Yes |
| Backlog Grooming | Weekly or on idea accumulation | ~20 min | PM | For P1/P2 items |

### 6.3 PI Planning

```
1. RETROSPECT ON PREVIOUS PI
   - PM: "Here's what we delivered. Here's carryover. Process changes?"

2. BACKLOG REVIEW
   - PM presents top-15 by RICE
   - Architect flags technical risks
   - SW Dev flags complexity

3. OBJECTIVE SETTING
   - PM proposes 3-5 objectives, each mapping to 1-3 backlog items
   - Human validates alignment

4. SPRINT MAPPING
   - PM + SW Dev map objectives to sprints
   - Buffer sprint reserved for overruns

5. RISK IDENTIFICATION
   - Each Principal identifies 1-2 risks
   - ROAM classification: Resolved, Owned, Accepted, Mitigated

6. COMMITMENT
   - Human approves -> CURRENT_PI.md updated
```

### 6.4 Sprint Planning

```
1. PM selects features from CURRENT_PI.md
2. PM sets sprint goal (one sentence)
3. SW Dev reviews spec readiness
4. SW Dev estimates capacity
5. PLAN.md and BOARD.md created
```

### 6.5 Session Start Standup (NOT a ceremony -- automatic)

At the start of every coding session, the Executive Manager reads `exec/state.md` and presents:

```
"Sprint {M} status: {N} of {T} tasks done. {B} blocked.
Last session completed: {summary}.
Suggested focus for this session: {recommendation}."
```

Human confirms focus or redirects. No template needed. No file written.

### 6.6 Sprint Review + Retro

**Review** (PM writes to sprint REVIEW section in BOARD.md):
- Delivered vs sprint goal
- Velocity (tasks completed, rolling average)
- Carryover items

**Retro** (written to RETRO.md):
```markdown
## What Went Well
## What Didn't Go Well
## Action Items (max 3)
- [ ] {action} -- Owner: {agent/human}
## Process Metrics
- Tasks planned/completed/carried:
- Blockers encountered:
- Fleet dispatches:
- Review rejections:
```

---

## Section 7: Fleet Mode Integration

### 7.1 When to Use Fleet Mode

**Use fleet for:**
- Independent codebase exploration
- Parallel spec critique (product, architecture, UX perspectives)
- Test-writing in separate test files
- Read-only review tasks
- UI and backend work when files do not overlap

**Do NOT use fleet for:**
- Multiple agents editing same source file
- Schema and migration changes simultaneously
- Simultaneous CSS edits (main.css is one file)
- Changes requiring one coherent architecture decision

### 7.2 Coordinator Design

The coordinator is NOT a separate agent. It is `fleet-coordinator.skill.md` loaded by the Principal SW Dev. The skill provides the dispatch logic, conflict checking, and batch management capabilities.

### 7.3 Pre-Dispatch Conflict Detection (6 Levels)

Before dispatching, check for conflicts at ALL levels:

| Resource Type | Conflict Rule |
|--------------|--------------|
| Source files | Same file in 2+ tasks = REJECT parallel |
| DB tables | Same model/table = potential conflict, serialize |
| Route prefixes | Same route prefix = potential conflict |
| Templates | Same template = REJECT (Jinja inheritance chain) |
| CSS | Same CSS file = ALWAYS sequential |
| Prompt templates | Same prompt template = potential conflict |

### 7.4 Day-to-Day Specific Dependency Rules (8)

```
1. agent/api.py -> ALWAYS sequential (central routing)
2. agent/engine.py -> ALWAYS sequential (singleton, state-heavy)
3. agent/config.py -> ALWAYS sequential (all modules depend on it)
4. agent/models.py -> ALWAYS sequential (schema, all queries depend on it)
5. static/css/main.css -> ALWAYS sequential
6. Different agent/routes/*.py files -> PARALLEL OK
7. Creating new files -> PARALLEL OK
8. Tests for different modules -> PARALLEL OK (isolated via patched_settings)
```

### 7.5 Batch Sizing Rules

| Factor | Guideline |
|--------|-----------|
| Starting batch size | 2 (conservative) |
| Max batch size | 4 (cognitive review limit) |
| Increase threshold | After 3 clean batches with zero conflicts |
| File overlap tolerance | 0 (any overlap = sequential) |
| Test file sharing | Allowed if additive only (new test functions) |
| Template sharing | NOT allowed |
| CSS sharing | NOT allowed |
| Max batch time | 30 minutes |

### 7.6 Dispatch Prompt Template

```markdown
You are a {agent_type} working on the Day-to-Day Agent project.

## Your Task
{task_description}

## Scope
Files you WILL modify:
{file_list}

Files you MUST NOT modify:
{exclusion_list}

## Context
{relevant_spec_excerpt}
{relevant_code_context}

## Requirements
- Follow TDD: write test first, then implement
- Run existing tests before AND after your changes
- Commit format: type: short description
- Do NOT modify files outside your scope
- Do NOT add new dependencies

## When Done
Report:
- Summary of changes
- Test results (pass count, any failures)
- Commit SHA
- Any concerns or questions
```

### 7.7 Dispatch Board Format (Generated FROM SQLite)

The dispatch board is a generated markdown view, NOT the source of truth. The source of truth is `ledger/fleet.db`.

```markdown
# Fleet Dispatch Board

## Batch BATCH-YYYYMMDD-NNN
- Goal:
- Coordinator: Principal Software Developer
- Max concurrency:
- Integration owner:

| Task | Agent | Files | Parallel | Status | Result |
|------|-------|-------|----------|--------|--------|

## Conflict Rules Applied
- (list any serialized tasks and reason)
```

### 7.8 Fleet Ledger SQLite Schema

File: `spec-driven-development/ledger/fleet.db`

6 tables:

```sql
-- Agent registry
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,            -- developer, ux-designer, data-scientist, qa-engineer
  name TEXT,                     -- NULL for generic, set on specialization
  specialized INTEGER DEFAULT 0,
  skills_json TEXT,              -- JSON array of skill IDs
  born_at TEXT,                  -- ISO8601
  last_used TEXT                 -- ISO8601
);

-- Skill catalog
CREATE TABLE skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT DEFAULT '1.0',
  summary TEXT,
  applies_to TEXT,               -- comma-separated roles
  requires TEXT                  -- comma-separated prerequisite skill IDs
);

-- Dispatch records
CREATE TABLE dispatches (
  id TEXT PRIMARY KEY,           -- DSP-YYYY-MM-DD-NNN
  feature_id TEXT,               -- SPEC-YYYYMMDD-slug
  worker_id TEXT REFERENCES agents(id),
  skills_json TEXT,
  prompt_hash TEXT,              -- SHA256 of composed prompt
  worktree TEXT,                 -- ../wt-{shortname}
  branch TEXT,                   -- feature/f{N}.{M}-{slug}
  status TEXT DEFAULT 'pending', -- pending, active, done, failed, blocked
  started_at TEXT,
  finished_at TEXT
);

-- Artifacts produced by dispatches
CREATE TABLE artifacts (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  path TEXT NOT NULL,
  kind TEXT,                     -- source, test, doc, config
  sha TEXT                       -- git commit SHA
);

-- Blockers raised during dispatch
CREATE TABLE blockers (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  severity TEXT,                 -- critical, important, minor
  summary TEXT,
  raised_at TEXT,
  resolved_at TEXT,
  resolved_by TEXT
);

-- Lessons learned from retrospectives
CREATE TABLE retro_lessons (
  id TEXT PRIMARY KEY,
  pi_id TEXT,
  sprint_id TEXT,
  lesson TEXT,
  applied_to_skill_id TEXT REFERENCES skills(id)
);
```

### 7.9 Phased Fleet Rollout

**Phase 1: Manual Dispatch (implemented first)**

`spec-driven-development/cli/fleet.py` reads a sprint plan and emits:
- A worktree creation script (one `../wt-{shortname}` per task per existing convention)
- A per-worker dispatch packet: composed prompt + task brief + skill set written to `sessions/DSP-YYYY-MM-DD-NNN.md`
- A printed launch table: which VS Code window / Copilot CLI invocation to start
- A SQLite ledger row per dispatch

You run the commands the script prints. Each chat window is one worker.

**Phase 2: CLI Automation (implemented after Phase 1 validated)**

Wire `gh copilot` CLI (or chosen CLI) to spawn worker processes. Workers stream status back into the ledger via `cli/common/ledger.py`. Principal PM polls the ledger.

**Why phased**: VS Code Copilot has no public API to spawn parallel chat tabs from a script. Phase 1 gives full value (deterministic dispatch + traceability) without that dependency.

### 7.10 Post-Dispatch Integration

1. Collect results from each agent
2. Check for unexpected file modifications outside scope
3. If conflicts detected: DO NOT auto-merge. Report to SW Dev.
4. If clean: merge in dependency order, run full test suite
5. Report: "Batch {N} complete. {X}/{Y} succeeded. Tests: {pass/fail}"
6. Log to conflict-log.md even if no conflicts (clean record)
7. Update ledger/fleet.db with dispatch outcomes

---

## Section 8: Quality and Feedback Loops

### 8.1 Feedback Loop Speeds

```
FAST (within a task):
  TDD red/green/refactor -> seconds
  Self-review before submit -> minutes

MEDIUM (within a sprint):
  Two-stage code review -> per task completion
  Session-start standup -> per session
  Grill sessions -> per new feature idea

SLOW (across sprints):
  Sprint retrospective -> per sprint end
  Architecture review -> per PI end
  Velocity tracking -> per sprint (rolling average)
  Process improvement -> per retro action item
```

### 8.2 Grill-Me Integration

**Trigger**: Scope is ambiguous, acceptance criteria are weak, user impact is unclear, architecture tradeoffs need judgment, UX behavior is unclear.

**Process:**
1. Agent asks ONE question at a time (never a batch)
2. Agent recommends an answer: "I'd suggest: {recommendation}. Does that work?"
3. Human confirms, modifies, or rejects
4. Agent incorporates answer and asks next question
5. Maximum 7 questions per session (diminishing returns)
6. After grilling, agent summarizes decisions made
7. Record in clarification-log.md

**Question Categories**: SCOPE, USERS, CONSTRAINTS, EDGE CASES, PRIORITY

### 8.3 Grill-With-Docs Integration

Same as grill-me but after each confirmed answer:
1. Update CONTEXT.md with the decision
2. If architectural (affects >1 module): create ADR
3. If supersedes previous decision: mark old as SUPERSEDED with date

### 8.4 TDD Enforcement

```
Vertical TDD Loop:
1. Pick ONE behavior from the task
2. Write ONE failing test
3. Run: .venv\Scripts\python.exe -m pytest tests/test_{module}.py -v --tb=short
4. Confirm FAIL (red)
5. Write MINIMAL code to pass
6. Run again, confirm PASS (green)
7. Refactor if needed (maintain passing)
8. Commit: "test: add {behavior} test" then "feat: implement {behavior}"
9. Repeat

RULES:
- Never write more than ONE test before implementing
- Never write implementation code without a failing test first
- Exception: trivial glue code (imports, __init__.py)
- Exception: template changes verified by visual inspection + existing tests
```

### 8.5 Code Review Workflow (Two-Stage)

**Order:**
1. Worker self-review
2. Spec Compliance Review (SW Dev) -- MISSING/EXTRA/WRONG
3. Code Quality Review (SW Dev, Architect if cross-cutting)
4. Security Review if risk triggers (path traversal, auth, tokens, prompt injection)
5. Architecture Review if Level 1+ decision
6. Product Acceptance Review (PM verifies acceptance criteria)

**Stage 1 -- SPEC COMPLIANCE** (Principal SW Dev):
- [ ] Every FR-NNN with MUST priority is implemented
- [ ] No features exist that aren't in the spec (EXTRA check)
- [ ] Implementation matches spec intent
- [ ] Success criteria verifiable in implementation
- [ ] Out of Scope items genuinely excluded
- Verdict: COMPLIANT or NOT COMPLIANT
- If NOT COMPLIANT -> fix -> re-review from Stage 1

**Stage 2 -- CODE QUALITY** (Principal SW Dev, Architect if cross-cutting):
- [ ] Error handling: exceptions caught, logged, user-friendly messages
- [ ] Edge cases: null, empty, boundary values handled
- [ ] Security: safe_path() for paths, esc() for HTML, Pydantic for input
- [ ] Naming: clear, consistent with codebase vocabulary
- [ ] Tests: adequate coverage, proper isolation
- [ ] Conventions: commit format, no emojis, no orphan code
- [ ] Performance: no O(n^2) where O(n) suffices
- Findings: CRITICAL (must fix) | IMPORTANT (should fix) | SUGGESTION (nice-to-have)
- Verdict: APPROVED or CHANGES REQUIRED
- If CHANGES REQUIRED -> fix -> re-review Stage 2 only

### 8.6 Architecture Review

**Trigger**: End of every PI, or when tech debt backlog exceeds 10 items, or when changing engine.py/config.py/llm.py/models.py/database.py/graph_client.py.

Architect checks each Article from principles.md and produces:
- Violations found (with file references)
- Tech debt items for backlog
- Vocabulary drift
- Deep module assessment

### 8.7 Session Handoff

Before ending any session with incomplete work:
1. What was the GOAL?
2. What was COMPLETED?
3. What is REMAINING?
4. What is the NEXT ACTION? (exact command or file to open)
5. Any CONTEXT that would be lost?

Written to CONTEXT.md under dated section. BOARD.md updated.

### 8.8 SDD Scorecard

File: `spec-driven-development/docs/SCORECARD.md`

| # | Metric | Target |
|---|--------|--------|
| 1 | Ideas with clear disposition | > 90% |
| 2 | Specs with zero critical clarifications at plan gate | 100% |
| 3 | P1 stories with tests before implementation | > 85% |
| 4 | Tasks traceable to requirements | 100% |
| 5 | Fleet conflicts per batch | < 1 |
| 6 | Full tests pass before integration | 100% |
| 7 | Defects escaping review | Decreasing trend |
| 8 | Cycle time idea-to-spec | Track baseline |
| 9 | Cycle time spec-to-merged | Track baseline |

---

## Section 9: Executive Manager Isolation Contract

### 9.1 The Contract

The Principal Executive Manager reads ONLY `spec-driven-development/exec/state.md`. This file is auto-rebuilt by `cli/state_builder.py` after every dispatch completion and every retrospective. The Executive Manager never reads raw spec, plan, task, code, or ledger files directly.

### 9.2 state.md Shape (<=2KB)

```markdown
# Project State

## Active PI
PI-{N}: {objective summary}

## Current Sprint
Sprint {M} of {N} | Goal: {one sentence}
- Done: {count}/{total} tasks
- Blocked: {count}
- In Progress: {count}

## Top 5 Priorities
1. {priority with status}
2. ...

## Top 3 Blockers
1. {blocker with owner}
2. ...

## Fleet
- Active workers: {count}
- Last batch: {id} -- {status}

## Recent Deliveries
1. {feature} -- merged {date}
2. ...

## Next 3 Milestones
1. {milestone} -- target {date}
2. ...

## Last Updated
{ISO8601 timestamp}
```

### 9.3 Q&A Routing Protocol

When the human asks Executive Manager a question it cannot answer from state.md:

1. Executive produces a `routing_memo.md` naming:
   - The right Principal to answer
   - The precise sub-question to ask
2. Principal answers in their thread
3. Answer is summarized back into Executive's next briefing update
4. This prevents context bloat while preserving traceability

### 9.4 Briefing History

`exec/briefings/YYYY-MM-DD.md` -- daily snapshots for historical reference. Written by `state_builder.py` when it regenerates state.md. Previous state.md content is appended to the day's briefing file before being overwritten.

---

## Section 10: CLI Layer Design

### 10.1 CLI Scripts

All CLI scripts live under `spec-driven-development/cli/`. They provide headless automation and are the bridge between SDD process and tooling.

| Script | Purpose | Phase |
|--------|---------|-------|
| `fleet.py` | Orchestrator: reads sprint plan, composes dispatch packets, creates worktrees, writes session logs | Phase 1 |
| `qa.py` | Validation runner: checks implementation against spec requirements | Phase 1 |
| `retro.py` | Retrospective automation: collects metrics, generates retro template | Phase 1 |
| `state_builder.py` | Regenerates `exec/state.md` from ledger + sprint data | Phase 1 |
| `common/composer.py` | Prompt composition: base role + skills + context + task brief = runtime prompt | Phase 1 |
| `common/ledger.py` | SQLite I/O for fleet.db (read/write dispatches, artifacts, blockers) | Phase 1 |
| `common/worktree.py` | Wraps `git worktree` per existing `../wt-{name}` convention | Phase 1 |
| `common/identity.py` | Specialization rules: auto-promotion, naming, skill matching | Phase 2 |

### 10.2 Phase 1: Manual Dispatch Packets

In Phase 1, CLI scripts generate dispatch packets but do NOT spawn processes:

```
$ python cli/fleet.py dispatch --sprint PI-1/sprint-1 --batch 1

Output:
- Created worktree: ../wt-calendar-route
- Created worktree: ../wt-task-filters
- Wrote dispatch: sessions/DSP-2026-05-21-001.md
- Wrote dispatch: sessions/DSP-2026-05-21-002.md
- Logged to ledger: 2 dispatches created

Launch instructions:
  Window 1: cd ../wt-calendar-route && open in VS Code
  Window 2: cd ../wt-task-filters && open in VS Code
```

### 10.3 Phase 2: CLI Automation

In Phase 2, `fleet.py` gains a `--auto` flag that spawns worker processes via the chosen CLI runtime (recommended: `gh copilot` CLI for headless workers). Workers post status back via `common/ledger.py`.

### 10.4 Ledger SQLite Schema

(See Section 7.8 for the full 6-table schema definition.)

---

## Section 11: GENERALIZATION_SDD.md

### 11.1 Purpose

The portability guide that allows this framework to bootstrap for any project. It grows alongside implementation -- every framework decision gets tagged with a generalization tier.

### 11.2 Three-Tier Generalization Tags

| Tag | Meaning | Examples |
|-----|---------|---------|
| `[PORTABLE]` | Works in any repo with zero edits | Four-Principal pattern, spec workflow, TDD loop, two-stage review, ceremony templates, dispatch conflict model |
| `[CONFIGURABLE]` | Needs a value substitution but structure is universal | Default branch name, worktree path pattern, test command, commit format |
| `[PROJECT-SPECIFIC]` | Day-to-Day-only, must be re-derived for new repos | Constitution content, agent system prompts (stack refs), fleet dependency rules, skill catalog |

### 11.3 Bootstrap Process

| Step | Action | Time |
|------|--------|------|
| 1 | Fork `spec-driven-development/`. Delete contents of backlog/, specs/, sprints/, exec/, sessions/. Keep templates, CLI, GENERALIZATION_SDD.md. | 5 min |
| 2 | Write constitution (mission, tech-stack, principles, roadmap, decision-policy, quality-policy) | 30 min |
| 3 | Customize core skills (project-context, git-workflow, testing-conventions) | 30 min |
| 4 | Customize agent prompts (replace stack refs, convention lists, file paths) | 45 min |
| 5 | Initialize backlog (capture ideas, first grooming, first PI planning) | 15 min |
| 6 | Validate with pilot feature (simplest P2 through full lifecycle) | 1-2 hours |

**Total bootstrap: ~3 hours for a new project.**

### 11.4 Team Size Adaptation

**Solo (1 person + AI, like Day-to-Day):**
- Executive Manager: optional (human IS the executive)
- Principals: all 3 active, but PM + SW Dev can merge for small projects
- Workers: 1-2 generic, specialize as needed
- Fleet: rarely needed, sequential by default
- Sprint cadence: 2-week sprints (symbolic; wall-clock typically faster with AI fleet)

**Small Team (2-5 people):**
- Executive Manager: active, coordinates across people
- Principals: all 3, each owned by a team member
- Workers: mapped 1:1 with specializations
- Fleet: used when 2+ people work in parallel
- Sprint cadence: 2-week sprints (symbolic)

**Large Team (6+):**
- Executive Manager: essential
- Principals: may need domain sub-principals
- Workers: organized into squads
- Fleet: primary dispatch mechanism
- Sprint cadence: 2-week sprints (symbolic)

### 11.5 Multi-Stack Examples

| Stack | Testing | Linting | Key Convention |
|-------|---------|---------|---------------|
| Python | pytest | ruff/flake8 | fixtures, tmp_path |
| TypeScript/Node | vitest/jest | eslint + prettier | package.json scripts |
| Go | go test | golangci-lint | effective go |
| Rust | cargo test | clippy | API guidelines |

### 11.6 Brownfield + Greenfield Onboarding

**Brownfield Onboarding** (existing codebase):
1. Auto-scan codebase to generate initial CONTEXT.md (language, framework, test runner, patterns)
2. Inventory existing conventions (commit format, branching, CI/CD)
3. Map existing tests and coverage
4. Generate constitution draft from discovered patterns
5. Pilot one small feature through the full lifecycle

**Greenfield Onboarding** (new project):
1. Run constitution wizard: answer 10 questions to generate all 6 constitution files
2. Choose tech stack -> auto-populate tech-stack.md and relevant skills
3. Scaffold directory structure
4. First PI = "Foundation" (architecture, core models, first routes)

### 11.7 Anti-Patterns to Avoid

1. **OVER-ENGINEERING**: Don't create specialized agents before you need them
2. **CEREMONY FATIGUE**: Skip PI planning for tiny projects (< 5 features/quarter)
3. **SPEC BLOAT**: Not every bug fix needs a full spec (see spec sizing rule in Section 4.2)
4. **AGENT PROLIFERATION**: Start with 4 principals + 4 worker templates, add as needed
5. **SKILL HOARDING**: Don't pre-write skills for domains you haven't encountered yet
6. **GATE WORSHIP**: Gates exist to catch problems, not to slow you down. If a gate adds no value, remove it in retro.

### 11.8 GENERALIZATION_SDD.md Outline

The actual file will contain these sections:

```
1. Purpose and Audience
2. The Four-Principal Pattern [PORTABLE]
3. Generic-Then-Specialize Roster [PORTABLE]
4. Skill Composition Algorithm [PORTABLE]
5. Two-Folder Split (.github/ + spec-driven-development/) [PORTABLE]
6. Spec Workflow and Slash Commands [PORTABLE] (mirrors Spec-Kit vocabulary)
7. /fleet Worktree Convention [CONFIGURABLE] (branch prefix, worktree path pattern)
8. Executive Manager Isolation Contract [PORTABLE]
9. Initial Skill Catalog [60% PORTABLE engineering, 40% PROJECT-SPECIFIC stack]
10. Brownfield Onboarding Script [PORTABLE] (auto-generates CONTEXT.md from scan)
11. Greenfield Onboarding Script [PORTABLE] (constitution wizard)
12. Bootstrap Process (step-by-step, 3 hours)
13. Team Size Adaptation Guide
14. Multi-Stack Examples
15. Anti-Patterns
16. Appendix: Tag Reference ([PORTABLE] / [CONFIGURABLE] / [PROJECT-SPECIFIC])
```

---

## Section 12: Implementation Roadmap

### Phase 1: Foundation (1-2 sessions)

**Goal**: Create directory structure, constitution, templates, chatmodes, and prompts. No code changes to the app.

| # | Task | Priority | Effort | Validation |
|---|------|----------|--------|-----------|
| 1.1 | Create directory structure (both .github/ additions and spec-driven-development/) | P1 | S | All dirs exist |
| 1.2 | Create `.github/chatmodes/` with 4 Principal chatmode files | P1 | M | Chatmodes appear in VS Code picker |
| 1.3 | Create `.github/prompts/` with 12 slash command prompt files | P1 | M | /commands are invocable |
| 1.4 | Create `.github/instructions/sdd-workflow.instructions.md` | P1 | S | Scoped instructions load for SDD files |
| 1.5 | Write constitution/mission.md (pre-filled content) | P1 | S | Content matches plan |
| 1.6 | Write constitution/tech-stack.md | P1 | S | Content matches plan |
| 1.7 | Write constitution/principles.md (9 articles) | P1 | M | Content matches plan |
| 1.8 | Write constitution/roadmap.md | P1 | S | Content matches plan |
| 1.9 | Write constitution/decision-policy.md | P1 | S | Content matches plan |
| 1.10 | Write constitution/quality-policy.md | P1 | S | Content matches plan |
| 1.11 | Create CONTEXT.md with initial content | P1 | S | Content matches plan |
| 1.12 | Create all templates/ files (9 templates) | P1 | M | All templates well-formed |
| 1.13 | Create docs/ADR/TEMPLATE.md, 001-sdd-framework.md, 002-two-folder-split.md, 003-specialization-naming.md | P1 | M | ADRs reference decisions |
| 1.14 | Create docs/SCORECARD.md | P1 | S | 9 metrics defined |
| 1.15 | Create backlog/IDEAS.md + backlog/BACKLOG.md | P1 | S | Seeded structure |
| 1.16 | Create exec/state.md (initial), exec/briefings/ | P1 | S | State file <=2KB |
| 1.17 | Create roster/agents.json, skills.json, skill_packs.json (initial) | P2 | M | Valid JSON |
| 1.18 | Create ledger/fleet.db with schema | P2 | S | 6 tables created |
| 1.19 | Create fleet/conflict-log.md | P2 | S | Template in place |
| 1.20 | Write README.md (framework overview) | P1 | S | Links to all sections |
| 1.21 | Write initial GENERALIZATION_SDD.md (v0.1) | P2 | M | Outline + first tagged items |

**Validation**: All dirs exist. All files well-formed markdown. Constitution doesn't contradict `.github/copilot-instructions.md`. No app code modified. Commit to feature branch off `integration/improvements`.

**First Deliverables** (exact files created in Phase 1):
```
.github/chatmodes/principal-architect.chatmode.md
.github/chatmodes/principal-software-developer.chatmode.md
.github/chatmodes/principal-product-manager.chatmode.md
.github/chatmodes/principal-executive-manager.chatmode.md
.github/prompts/triage.prompt.md
.github/prompts/grill.prompt.md
.github/prompts/spec.prompt.md
.github/prompts/clarify.prompt.md
.github/prompts/plan.prompt.md
.github/prompts/tasks.prompt.md
.github/prompts/analyze.prompt.md
.github/prompts/fleet.prompt.md
.github/prompts/implement.prompt.md
.github/prompts/qa.prompt.md
.github/prompts/retro.prompt.md
.github/prompts/state.prompt.md
.github/instructions/sdd-workflow.instructions.md
spec-driven-development/README.md
spec-driven-development/GENERALIZATION_SDD.md
spec-driven-development/CONTEXT.md
spec-driven-development/constitution/mission.md
spec-driven-development/constitution/tech-stack.md
spec-driven-development/constitution/principles.md
spec-driven-development/constitution/roadmap.md
spec-driven-development/constitution/decision-policy.md
spec-driven-development/constitution/quality-policy.md
spec-driven-development/docs/ADR/TEMPLATE.md
spec-driven-development/docs/ADR/001-sdd-framework.md
spec-driven-development/docs/ADR/002-two-folder-split.md
spec-driven-development/docs/ADR/003-specialization-naming.md
spec-driven-development/docs/SCORECARD.md
spec-driven-development/templates/feature-spec.md
spec-driven-development/templates/plan.md
spec-driven-development/templates/task-list.md
spec-driven-development/templates/agent-brief.md
spec-driven-development/templates/adr.md
spec-driven-development/templates/validation.md
spec-driven-development/templates/review-report.md
spec-driven-development/templates/clarification-log.md
spec-driven-development/templates/handoff.md
spec-driven-development/backlog/IDEAS.md
spec-driven-development/backlog/BACKLOG.md
spec-driven-development/exec/state.md
spec-driven-development/roster/agents.json
spec-driven-development/roster/skills.json
spec-driven-development/roster/skill_packs.json
spec-driven-development/ledger/fleet.db
spec-driven-development/fleet/conflict-log.md
```

### Phase 2: Core Agents + Skills + CLI Skeleton (2-3 sessions)

**Goal**: Create agent definitions, skill files, and CLI skeleton.

| # | Task | Priority | Effort | Validation |
|---|------|----------|--------|-----------|
| 2.1 | Write 4 generic worker agent files in .github/agents/ | P1 | M | Self-contained prompts |
| 2.2 | Write core skills (sdd-constitution, project-context, git-workflow, testing-conventions) | P1 | L | <100 lines each |
| 2.3 | Write workflow skills (grill-me, grill-with-docs, to-spec, to-plan, to-tasks, triage, implement) | P1 | L | <100 lines each |
| 2.4 | Write engineering skills (tdd, diagnose, code-review, improve-architecture) | P1 | L | <100 lines each |
| 2.5 | Write operational skills (handoff, fleet-coordinator, pi-planning) | P2 | M | <100 lines each |
| 2.6 | Write domain skills (pytest-runner, fastapi-routes, htmx-frontend) | P2 | M | Stack-specific |
| 2.7 | Write agents/specialized/README.md (promotion guide) | P2 | S | Clear process |
| 2.8 | Write CLI skeleton: fleet.py, state_builder.py, common/composer.py, common/ledger.py, common/worktree.py | P1 | L | Scripts run without error |
| 2.9 | Write CLI: qa.py, retro.py | P2 | M | Scripts run without error |
| 2.10 | Populate roster/agents.json and roster/skills.json | P1 | M | Valid, reflects all agents/skills |

**Validation**: Each agent is self-contained. Skills are < 100 lines each. Roster JSON reflects all agents and skills accurately. CLI scripts have basic --help and can be invoked.

### Phase 3: Pilot Spec (1-2 sessions)

**Goal**: Run one real low-risk feature through the entire SDD lifecycle.

| # | Task | Priority | Effort | Validation |
|---|------|----------|--------|-----------|
| 3.1 | Seed IDEAS.md with 5-10 real feature ideas from PROJECT_STATE.md | P1 | S | Ideas captured |
| 3.2 | Run backlog grooming with PM chatmode (/triage) | P1 | M | RICE scores assigned |
| 3.3 | Run PI planning ceremony | P1 | L | CURRENT_PI.md created |
| 3.4 | Run sprint planning for Sprint 1 | P1 | M | PLAN.md + BOARD.md created |
| 3.5 | Select simplest P2 feature and run /clarify + /spec | P1 | M | Spec approved |
| 3.6 | Run /plan phase | P1 | M | Plan approved |
| 3.7 | Run /tasks phase | P1 | M | Tasks decomposed with tags |
| 3.8 | Implement with TDD (/implement) | P1 | L | Code passes review |
| 3.9 | Run two-stage code review | P1 | M | COMPLIANT + APPROVED |
| 3.10 | Merge to integration/improvements | P1 | S | Tests pass, clean merge |
| 3.11 | Run /retro | P1 | M | RETRO.md with <=3 action items |
| 3.12 | Process retro action items -> update framework | P1 | S | Framework files updated |

**Validation**: One complete feature through the full pipeline. Retro identifies improvements. Framework files updated.

### Phase 4: Fleet Pilot (1 session)

**Goal**: Validate parallel dispatch with conservative batch size of 2.

| # | Task | Priority | Effort | Validation |
|---|------|----------|--------|-----------|
| 4.1 | Choose a spec with 2+ independent tasks | P1 | S | Tasks verified independent |
| 4.2 | Run fleet.py to generate dispatch packets | P1 | M | Worktrees + sessions created |
| 4.3 | Run pre-dispatch conflict check (6-level) | P1 | M | No file overlaps |
| 4.4 | Dispatch 2 agents manually in parallel VS Code windows | P1 | L | Both complete successfully |
| 4.5 | Run post-dispatch integration | P1 | M | Clean merge, tests pass |
| 4.6 | Record in fleet.db and conflict-log.md | P1 | S | Ledger accurate |
| 4.7 | Retro: are batch rules clear enough? | P1 | S | Rules validated or refined |

**Validation**: No overlapping file edits. Batch output reproducible. Conflict rules validated.

### Phase 5: Generalization (1-2 sessions)

**Goal**: Finalize portability guide. Test bootstrap on a second project.

| # | Task | Priority | Effort | Validation |
|---|------|----------|--------|-----------|
| 5.1 | Finalize GENERALIZATION_SDD.md v1.0 based on Phase 3-4 learnings | P1 | L | All sections filled, tagged |
| 5.2 | Tag all framework files with [PORTABLE]/[CONFIGURABLE]/[PROJECT-SPECIFIC] | P2 | M | Manifest complete |
| 5.3 | Test bootstrap on a second project (e.g., performance_metrics_agent) | P2 | L | Bootstrap < 3 hours |
| 5.4 | Refine based on bootstrap test | P2 | M | No Day-to-Day assumptions leak |

**Validation**: Second project bootstrapped in < 3 hours. No Day-to-Day-specific assumptions leak.

### Phase 6: Optional Enhancements (ongoing)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 6.1 | SDD Dashboard: `/sdd` page in the Day-to-Day app showing PI, sprint, gate status | P3 | L |
| 6.2 | CLI Automation Phase 2: auto-spawn workers via gh copilot CLI | P3 | L |
| 6.3 | Agent Brief Generator: stdlib parser converting tasks.md into brief files | P3 | M |
| 6.4 | Monthly scorecard review automation | P3 | S |
| 6.5 | Brownfield/greenfield onboarding scripts | P3 | L |

---

## Section 13: Operating Model (Daily Flow)

### 13.1 Default Commands Before Any Implementation

```powershell
git --no-pager status
git worktree list
.venv\Scripts\python.exe -m pytest tests\ --tb=short -q
```

### 13.2 How a Typical Session Flows

1. **Session starts**: Switch to Principal Executive Manager chatmode. Executive reads `exec/state.md` and presents sprint status + suggested focus.

2. **Human states goal** or records an idea in IDEAS.md.

3. **If new idea**: Switch to Principal PM chatmode. Run `/triage`. PM grills the idea, applies RICE, classifies priority.

4. **If ready feature**: Switch to Principal Architect chatmode. Run `/spec` (or `/clarify` first if ambiguous). Architect + SW Dev co-author the spec.

5. **If spec approved**: Switch to Principal Software Developer chatmode. Run `/plan` then `/tasks`. SW Dev decomposes into batched, tagged tasks.

6. **If parallel-safe tasks exist**: Run `/fleet`. SW Dev generates dispatch packets via CLI. Human launches VS Code windows per the launch table.

7. **Workers implement** with TDD in their worktrees. Each follows their agent brief.

8. **After workers complete**: SW Dev runs two-stage review. Stage 1: spec compliance. Stage 2: code quality.

9. **If approved**: SW Dev integrates (merge, full test suite). Updates BOARD.md.

10. **End of sprint**: Run `/retro`. PM + all Principals produce RETRO.md with max 3 action items.

11. **Before ending session**: If work is incomplete, run handoff skill. Updates CONTEXT.md and BOARD.md. State builder regenerates `exec/state.md`.

### 13.3 Chatmode Selection Guide

| Situation | Chatmode |
|-----------|----------|
| "What's the status?" | Principal Executive Manager |
| "I have an idea" / "Let's prioritize" | Principal Product Manager |
| "How should we build this?" / "Review the spec" | Principal Architect |
| "Break this into tasks" / "Review this code" | Principal Software Developer |

---

## Section 14: Risks and Decisions

### 14.1 Decided (with rationale)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Worker runtime for Phase 1 | VS Code Copilot Chat windows (manual launch) | No public API for parallel tab spawning. Manual launch gives full traceability. |
| Worker runtime for Phase 2 | Copilot CLI (`gh copilot`) for headless workers | Headless CLI enables automation without VS Code dependency. Principals stay in Copilot Chat. |
| Spec-Kit interop | Independent, mirror vocabulary | Gives more control. Matches Pocock "take back control" philosophy. Vocabulary alignment enables future interop. |
| Fleet ledger DB | Separate SQLite at `ledger/fleet.db` | Clean separation from app data (agent/daytoday.db). No risk of cross-contamination. |
| PI cadence | 10-week PI / 2-week sprints (symbolic; agents compress wall-clock time) | Traditional SAFe cadence as symbolic unit. Agents compress a PI into ~1 wall-clock week. Ceremonies and artifacts use the standard 10/2 split so the framework is directly portable to human teams. |
| Backlog source | Markdown-first in `backlog/` | Simpler, no external dependency. Optional GitHub Issues sync in Phase 5+. |
| Naming convention | `{role}-{firstname}-{domain}-{NNN}` | Fixed first-name pool prevents LLM drift. Domain tag aids dispatching. |
| Worker count | 4 generic (developer, ux-designer, data-scientist, qa-engineer) | Lean start. Others (researcher, tech-writer, security-reviewer) added on first need. |
| Constitution format | 6 separate files (not single file) | More modular. Easier to update per-section. Clear ownership. |

### 14.2 Open Decisions

| # | Decision | Recommendation | Impact if Deferred |
|---|----------|----------------|--------------------|
| 2 | **Chatmode format verification** | Verify `.chatmode.md` format works in your VS Code Copilot version before Phase 1. Added as Task 1.1.5: create a throwaway sentinel chatmode and confirm it appears in the picker. If format differs, adjust template before Task 1.2. | Could require restructuring if format differs |

> **Decision #1 (First pilot feature) -- DECIDED**: Documentation drift cleanup (PROJECT_STATE.md, SESSION_HANDOFF.md, QUICKSTART.md, run_agent.py alignment). Low risk, touches docs not app code. Confirmed by owner 2026-05-07.

---

## Section 15: Inspiration Trace

| Source | What We Adopt |
|--------|--------------|
| **Spec-Kit** (github/spec-kit) | Command vocabulary (constitution/specify/clarify/plan/tasks/analyze/implement), four-phase model, extension/preset mental model, MAQA and Fleet Orchestrator extension patterns as reference |
| **Spec-Kit Brownfield extension** | Auto-CONTEXT generation pattern for the generalization phase |
| **Matt Pocock skills** (github.com/mattpocock/skills) | grill-me + grill-with-docs, CONTEXT.md shared-language doc, docs/adr/, vertical-slice tasks (to-issues), TDD loop, diagnose loop, zoom-out, caveman compression, write-a-skill meta-skill, "small composable, take back control" philosophy |
| **DeepLearning.AI SDD course** (sc-spec-driven-development-files) | Constitution-first, replanning between phases, MVP/Legacy patterns, "agent replaceability" lesson -- directly informs our generic-then-specialize roster |
| **SAFe (scaled)** | PI planning structure, ROAM risk classification, sprint ceremonies. Adapted for solo developer: shorter cadence, lighter ceremony. |
| **Our research findings** | Two-folder split rationale (Copilot auto-discovery), chatmode vs agent distinction, SQLite over markdown for fleet tracking, executive isolation contract, three-tier generalization tags, phased fleet rollout |

---

**END OF FINAL MERGED PLAN**

This plan is ready for human review. Upon approval:
1. Begin Phase 1: Foundation on a feature branch from `integration/improvements`
2. First session creates the directory structure + constitution + chatmodes + prompts
3. Second session creates templates + roster + ledger + initial GENERALIZATION_SDD.md
4. Pilot feature DECIDED: documentation drift cleanup (see Section 14.2)
