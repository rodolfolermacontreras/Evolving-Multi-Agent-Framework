# Onboarding & Kick-Off Guide -- Evolving Multi-Agent Framework

**Date:** 2026-05-25, maintained current through PI-8 (originally 2026-05-21; renamed from `kick_off.md` and amended for its onboarding role at the PI-3 kickoff)
**Owner:** Rodolfo Lerma, Senior Data Scientist (L63), Microsoft WWIC Central Analytics
**Repo:** [rodolfolermacontreras/Evolving-Multi-Agent-Framework](https://github.com/rodolfolermacontreras/Evolving-Multi-Agent-Framework)
**License:** MIT

---

## How to Use This Document

This is the single entry point for any agent or human joining the project from
zero. If you read only this document plus the four pointers in Section 0 below,
you will be fully up to speed to start your first sprint.

Read order:

1. Sections 0-8 of this file (project framing, architecture, lifecycle, structure)
2. [`RULES.md`](RULES.md) -- the 13 binding rules + HITL gates
3. [`HIGH_LEVEL_DEV_TRACKER.md`](HIGH_LEVEL_DEV_TRACKER.md) -- current PI/sprint state
4. Active PI's [`Management/PI-N/INDEX.md`](Management/) -- PI-level navigation
5. Your sprint's [`Management/PI-N/Sprint-N-{title}/SPEC.md`](Management/) -- deep spec
6. Sections 13-16 of this file (codebase reading guide, getting started, what's next)

---

## Table of Contents

0. [Required Reading (4-pointer onboarding)](#0-required-reading-4-pointer-onboarding)
1. [What This Project Is](#1-what-this-project-is)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [Origin Story](#3-origin-story)
4. [Inspirations and What We Borrowed](#4-inspirations-and-what-we-borrowed)
5. [Architecture at a Glance](#5-architecture-at-a-glance)
6. [The Lifecycle](#6-the-lifecycle)
7. [The Constitution](#7-the-constitution)
8. [Repository Structure](#8-repository-structure)
9. [What Has Been Built](#9-what-has-been-built)
10. [Current State and Metrics](#10-current-state-and-metrics)
11. [Key Architecture Decisions](#11-key-architecture-decisions)
12. [Where to Read More (full document directory)](#12-where-to-read-more-full-document-directory)
13. [Agent Dispatch Flow](#13-agent-dispatch-flow)
14. [Codebase Reading Guide for Brownfield Agents](#14-codebase-reading-guide-for-brownfield-agents)
15. [Getting Started](#15-getting-started)
16. [What Is Next](#16-what-is-next)

---

## 0. Required Reading (5-pointer onboarding)

Any agent picking up work in this project must read these five documents
before touching code. In order:

| # | Path | Why |
|---|------|-----|
| 1 | [`ONBOARDING_KICK_OFF.md`](ONBOARDING_KICK_OFF.md) (this file) | Project framing, architecture, lifecycle |
| 2 | [`RULES.md`](RULES.md) | 13 binding rules + 11 HITL gates |
| 3 | [`HIGH_LEVEL_DEV_TRACKER.md`](HIGH_LEVEL_DEV_TRACKER.md) | Current PI/sprint state + dependency graph |
| 4 | Active PI's [`Management/PI-N/INDEX.md`](Management/) | PI-level decisions, sprint list, what-was-done |
| 5 | Your sprint's [`Management/PI-N/Sprint-N-{title}/SPEC.md`](Management/) | Sprint spec, tasks, validation contract |

If you are a Principal, also read:
- `constitution/principles.md` -- the 12 binding articles
- `constitution/decision-policy.md` -- Level 0/1/2 authority
- `INSTRUCTIONS.md` at repo root and `.github/copilot-instructions.md`

If you are a Worker, also read:
- The skill files your sprint doc cites under `Skills:` in its frontmatter
- `docs/CLI-PATTERN.md` if you are touching any `cli/*.py` file

---

## 1. What This Project Is

The Evolving Multi-Agent Framework is a **portable, replicable system for orchestrating a fleet of AI agents** through a structured, spec-driven, test-driven development lifecycle. It is designed so that **one human developer** can ship production-quality software at the pace of a small team by treating AI agents as first-class team members with defined roles, scoped responsibilities, and explicit handoff protocols.

**It is:**

- A **process** -- a defined lifecycle from idea to merged code with quality gates between phases
- A **team structure** -- four Principal agents plus a sprint-scoped Sprint Executive Manager (five roles; ADR-020, the two-tier EM) (strategic) plus a fleet of generic Worker agents (tactical) that specialize on demand
- A **file convention** -- Markdown files, YAML schemas, SQLite ledger, and conventions that operate inside VS Code with GitHub Copilot
- A **traceable system** -- every dispatch, decision, and handoff is recorded in a SQLite ledger

**It is NOT:**

- A runtime, library, or framework you import into your code
- Opinionated about the host project's tech stack (Python, TypeScript, Go -- anything works)
- A finished product -- it is actively evolving through its own lifecycle

---

## 2. The Problem It Solves

When a solo developer uses AI assistants (Copilot, Claude, Cursor) to build software, they typically "chat with AI and paste code." This works at small scale but hits scaling limits as the project grows:

- **Context overload** -- one conversation cannot hold architecture, implementation, and testing context simultaneously
- **Inconsistent patterns** -- different AI sessions produce different approaches to the same problem
- **No traceability** -- there is no record of WHY a feature was built a certain way
- **No quality gates** -- nothing separates the idea phase from the implementation phase; code arrives at review without acceptance criteria
- **No separation of concerns** -- the same AI session is asked to be product manager, architect, and developer at once

The framework solves these by assigning **specialized roles** to AI agents, defining **explicit handoff protocols** between them, enforcing **quality gates** between lifecycle phases, and recording **everything in files and a ledger** for auditability.

---

## 3. Origin Story

The framework was born inside the [Day-to-Day Agent](https://github.com/rodolfolermacontreras/day-to-day-microsoft) project -- a personal AI-powered work management dashboard built with Python/FastAPI/HTMX. As that project grew to 743+ tests and 20+ feature branches, the ad-hoc AI development approach broke down.

The solution was to formalize the development process itself: a team of specialized AI agents with defined roles, constrained scopes, and explicit handoff protocols.

**Timeline:**

| Date | Milestone |
|------|-----------|
| 2026-05-07 | **Dual-LLM Planning** -- Claude Opus 4.7 and GPT 5.5 independently generated comprehensive plans, cross-reviewed and merged into a single 85KB, 15-section definitive plan (`FINAL_MERGED_PLAN.md`) |
| 2026-05-07 | **Asset Creation** -- 81 files, 12,663 lines created in a single commit: agents, skills, prompts, constitution, templates, CLI scaffolds |
| 2026-05-10 | **Format Conversion** -- Principal agents converted from `.chatmode.md` to `.agent.md` for VS Code auto-discovery |
| 2026-05-12 | **Extraction** -- All SDD files migrated from Day-to-Day repo to this standalone repository |
| 2026-05-12--13 | **PI-1: Generalization and First Pilot** -- Constitution generalized, first feature (fleet ledger) shipped through full SDD lifecycle, bootstrap CLI created, 7 ADRs, 10 binding articles, lessons captured | <!-- staledoc-ok: PI-1 historical milestone (10 articles was the count at PI-1; XI/XII added later) -->
| 2026-05-16 | **PI-2: Fleet Maturity and CLI** -- 5 CLI tools shipped (`state_builder.py`, `fleet.py`, `qa.py`, `retro.py`, `schema_lint.py`), live Azure Bridge dashboard deployed, first specialist promoted (`developer-cli-specialist-1`), PI-2 retrospective with 6 lessons |
| 2026-05-16 | **PI-3 approved** -- Day-to-Day brownfield bootstrap selected as portability validation target |

---

## 4. Inspirations and What We Borrowed

The framework draws from four sources. Research was conducted by dispatching four parallel subagents to inspect the actual repositories. Full findings are in `sessions/inspiration-repos-research-findings.md`.

### 4.1 Spec-Kit (GitHub)

**Repo:** https://github.com/github/spec-kit

What we adopted:
- The slash-command vocabulary (`/constitution`, `/clarify`, `/plan`, `/tasks`, `/analyze`, `/implement`)
- The constitution propagation check concept (semver + sync impact report, our ADR-0006)
- The spec quality gate concept

What we deliberately did NOT adopt:
- Their single-agent model (would erase our multi-agent handoff chain)
- Python CLI as primary distribution (we are Markdown-first for portability)
- `.specify/extensions.yml` hook system (adds coordination overhead in multi-agent orchestration)

### 4.2 DeepLearning.AI "Spec-Driven Development with Coding Agents" Course

**Course:** https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/
**Instructor:** Paul Everitt (JetBrains)
**Companion code:** https://github.com/rodolfolermacontreras/sc-spec-driven-development-files

What we adopted:
- The 3-file constitution model (`mission.md` + `tech-stack.md` + `roadmap.md`)
- The feature loop pattern (idea to merged code with defined phases)
- The brownfield-via-archaeology approach (inspect existing code before imposing process)
- The validation scorecard as a pre-implementation contract (our Article X, ADR-0005)
- The `/replan` ceremony (pause after every DONE to update constitution/roadmap/skills)
- Date-prefix feature directories (`specs/YYYY-MM-DD-feature-name/`)

### 4.3 Matt Pocock's Skills Pattern

**Repo:** https://github.com/mattpocock/skills

What we adopted:
- Composable, single-purpose `SKILL.md` files with YAML frontmatter
- The `argument-hint` frontmatter field on all skills and prompts
- The `handoff` skill concept (compact one session into a handoff doc for the next)
- The core `grill-me` concept (interview the user one question at a time until shared understanding); our SDD-lifecycle framing and completion signals are our own extensions

### 4.4 SAFe (Scaled Agile Framework)

Adapted for a single developer + AI fleet:
- Program Increments (PI) and Sprints as planning horizons
- Treated as **symbolic cadence** -- AI fleet compresses wall-clock time dramatically; PIs and sprints provide ceremony rhythm (planning, retro, demo), not calendar gates (ADR-0003)

### Key Convergent Finding

All three code-based inspirations independently agree: **validation criteria belong BEFORE implementation, not after**. This became Article X (the strongest binding article) and ADR-0005. The validation contract is committed alongside the spec, locked at `/tasks`, and verified at `/qa`.

---

## 5. Architecture at a Glance

### The Single Developer + AI Fleet Paradigm

```
Human (1 person -- Rodolfo)
  |
  v
Executive Manager  <-- SINGLE HUMAN ENTRY POINT
  |                    Owns: kickoff, Q&A routing + synthesis, status, escalation
  |
  +---> Product Manager      --+
  +---> Architect             --+--> STRATEGY layer (decide WHAT and HOW)
  +---> Software Developer    --+
  |     Cloud Security Arch.  --+
  |
  v
Worker Agents (the actual hands) --> TACTICS layer (DO the work)
  +-- Developer (generic)
  +-- UX Designer (generic)
  +-- QA Engineer (generic)
  +-- Data Scientist (generic)
  +-- developer-cli-specialist-1 (earned)
  +-- <any role created on demand via /hire>
```

**Vendor analogy:** The human is the client. The Executive Manager is the engagement manager -- your single phone number. Principals are partner-level consultants who decide strategy. Workers are the actual hands doing the work, dispatched per task, constrained to 1-3 files.

### Key Design Principles

| # | Principle | Article |
|---|-----------|---------|
| 1 | Two-folder split (`.github/` for Copilot-native, `spec-driven-development/` for process state) | I |
| 2 | Single human entry point (Executive Manager) | II |
| 3 | Two-stage review (spec compliance first, code quality second, different reviewers) | III |
| 4 | Specialization over generalism (workers constrained to 1-3 files per task) | IV |
| 5 | Generic by default, specialized on demand (workers earn permanent identity through demonstrated competence) | V |
| 6 | Ceremony proportional to risk (bug fix <3 files = no spec) | VI |
| 7 | Every artifact is a file; every dispatch is logged (SQLite ledger) | VII |
| 8 | Constitution is immutable without an ADR | VIII |
| 9 | Human holds final approval on Level 2 decisions (irreversible, high-risk) | IX |
| 10 | Validation is a pre-implementation contract (tests before code) | X |
| 11 | Cross-feature serial gate at CLARIFY and SPEC (no two features share a file mid-flight) | XI |
| 12 | UI lifecycle variant of the validation contract | XII |

Full text: `spec-driven-development/constitution/principles.md`

### Decision Authority Tiers

| Level | Authority | Examples |
|-------|-----------|----------|
| **Level 0** (Worker) | Any worker, autonomously | Rename variable, add docstring, extract helper within task scope |
| **Level 1** (Principal) | Relevant Principal must agree + ADR | Change route signature, create new module, choose architectural pattern |
| **Level 2** (Human) | Explicit human approval required | New dependency, schema migration, production merge, credential changes |

Full text: `spec-driven-development/constitution/decision-policy.md`

---

## 6. The Lifecycle

```
IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE -> /replan
```

Each phase has a gate. Gates have defined approvers. Nothing proceeds to implementation without an approved spec (except bug fixes <3 files).

| Phase | Command | Owner | Output |
|-------|---------|-------|--------|
| Capture | `/ask` or plain language | Executive Manager | `backlog/IDEAS.md` entry |
| Triage | `/triage` | Product Manager | RICE score, priority assignment in `BACKLOG.md` |
| Clarify | `/clarify` | PM or Architect | One Q&A at a time in `clarification-log.md` |
| Specify | `/spec` | PM + Architect | `spec.md` + `validation.md` (pre-implementation contract) |
| Plan | `/plan` | Architect + SW Dev | `plan.md` with phased implementation steps |
| Tasks | `/tasks` | SW Dev | `tasks.md` with tagged tasks: [P]/[S], [AFK]/[HITL] |
| Analyze | `/analyze` | Architect (read-only) | Cross-artifact consistency check |
| Implement | `/implement` or `/fleet` | SW Dev dispatches Workers | Code + tests committed |
| Review | `/qa` | Two-stage: spec compliance, then code quality | COMPLIANT/NOT COMPLIANT, then APPROVED/CHANGES REQUIRED |
| Ceremony | `/retro` | PM | Sprint retrospective, max 3 action items |
| Evolve | `/replan` + `/evolve` | All Principals | Update constitution, roadmap, skills, lessons |

### Spec Sizing Rule (prevents ceremony bloat)

| Change Size | Process |
|-------------|---------|
| Bug fix, <3 files | No spec. Task + test + review. |
| Feature, <5 files | Lightweight spec (user story + requirements + success criteria) |
| Feature, >=5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

### Task Tags

| Tag | Meaning |
|-----|---------|
| `[P]` | Parallelizable -- safe for fleet dispatch alongside other [P] tasks |
| `[S]` | Sequential -- must be executed alone or in order |
| `[AFK]` | Away From Keyboard -- safe for fully autonomous agent execution |
| `[HITL]` | Human In The Loop -- requires a human decision before completion |

---

## 7. The Constitution

Six immutable files in `spec-driven-development/constitution/` define the project's identity and rules. All carry YAML frontmatter with semantic versioning (`version`, `ratified`, `last_amended`). Amendments use the `/constitution` command which semver-bumps and runs a propagation scan.

| File | Contents |
|------|----------|
| `mission.md` | Project identity, owner, vision, core values, non-negotiables |
| `tech-stack.md` | Approved technologies (Markdown, YAML, SQLite, Python stdlib for CLI) |
| `principles.md` | Twelve binding architectural articles (I-XII) |
| `roadmap.md` | Completed phases, current PI, tech debt backlog |
| `decision-policy.md` | Level 0/1/2 decision authority and escalation path |
| `quality-policy.md` | Test baseline, two-stage review, security conventions, Definition of Done |

---

## 8. Repository Structure

```
Evolving-Multi-Agent-Framework/
|
+-- INSTRUCTIONS.md                       <-- Entry point for any AI agent
+-- README.md                             <-- Project overview + quickstart
+-- Dockerfile                            <-- Bridge dashboard container
|
+-- .github/                              <-- Copilot-native (auto-discovered by VS Code)
|   +-- copilot-instructions.md           <-- Session-start authority (read on every session)
|   +-- agents/                           <-- 5 Principals + 4 generic workers + 1 specialist + template
|   |   +-- principal-executive-manager.agent.md
|   |   +-- principal-product-manager.agent.md
|   |   +-- principal-architect.agent.md
|   |   +-- principal-software-developer.agent.md
|   |   +-- principal-cloud-security-architect.agent.md
|   |   +-- developer-general.agent.md
|   |   +-- developer-cli-specialist-1.agent.md    <-- Earned via /hire (ADR-0007)
|   |   +-- ux-designer-general.agent.md
|   |   +-- qa-engineer-general.agent.md
|   |   +-- data-scientist-general.agent.md
|   |   +-- _TEMPLATE-worker.agent.md              <-- Used by /hire to create new roles
|   +-- skills/                           <-- 29 composable skills across 5 categories
|   |   +-- core/                         <-- sdd-constitution, project-context, git-workflow,
|   |   |                                     testing-conventions, constitution-sync
|   |   +-- workflow/                     <-- grill-me, grill-with-docs, to-spec, to-plan,
|   |   |                                     to-tasks, triage, implement, archetype-recommender
|   |   +-- engineering/                  <-- tdd, tdd-gate, diagnose, code-review,
|   |   |                                     improve-architecture
|   |   +-- operational/                  <-- handoff, fleet-coordinator, pi-planning,
|   |   |                                     lesson-capture, role-creation, respect-existing,
|   |   |                                     em-communication-discipline
|   |   +-- domain/                       <-- pytest-runner, fastapi-routes, htmx-frontend
|   |   |                                     (marked as EXAMPLES from Day-to-Day project)
|   |   +-- AI-AGENT-SUPER-SKILL.md
|   +-- prompts/                          <-- 17 slash commands
|   |   +-- triage, clarify, spec, plan, tasks, analyze, fleet,
|   |       implement, qa, retro, state, ask, grill, hire,
|   |       replan, evolve, constitution
|   +-- instructions/                     <-- Scoped guidance by file glob
|       +-- sdd-workflow.instructions.md  <-- Applies to spec-driven-development/**
|       +-- fleet-workers.instructions.md <-- Applies to wt-* worktree patterns
|
+-- spec-driven-development/              <-- Process state (not Copilot-native)
    +-- CONTEXT.md                        <-- Shared vocabulary for all agents
    +-- GENERALIZATION_SDD.md             <-- 62KB portability guide
    +-- README.md                         <-- Framework overview + slash command reference
    +-- constitution/                     <-- 6 immutable files with semver frontmatter
    +-- docs/
    |   +-- FINAL_MERGED_PLAN.md          <-- 85KB definitive plan (15 sections)
    |   +-- CHEAT-SHEET.html              <-- Visual SVG workflow diagram
    |   +-- CLI-PATTERN.md                <-- Canonical Python stdlib CLI pattern
    |   +-- SCORECARD.md                  <-- Sprint-level process metrics
|   |   +-- ADR/                          <-- Architecture Decision Records (see docs/ADR/) + template
    +-- cli/                              <-- Python automation (stdlib-only, all operational)
    |   +-- state_builder.py              <-- Generates exec/state.md + state.html dashboard
    |   +-- fleet.py                      <-- Dispatch, mark, status commands
    |   +-- qa.py                         <-- Two-stage review automation
    |   +-- retro.py                      <-- Sprint retro generator
    |   +-- schema_lint.py                <-- YAML frontmatter validation
    |   +-- bootstrap.py                  <-- Greenfield + brownfield project bootstrap
    |   +-- test_*.py                     <-- Test suites for each CLI tool
    |   +-- common/                       <-- Shared modules (composer, ledger, worktree, identity)
    +-- archetypes/                       <-- 5 starter constitutions for new projects
    |   +-- python-library/
    |   +-- python-web-service/
    |   +-- data-pipeline/
    |   +-- cli-tool/
    |   +-- research-repo/
    +-- roster/                           <-- Machine-readable registries
    |   +-- agents.json                   <-- 10 agent entries
    |   +-- skills.json                   <-- 29 skill entries
    |   +-- skill_packs.json              <-- Specialist skill bundles
    +-- templates/                        <-- 8 reusable document templates
    +-- backlog/                          <-- IDEAS.md (raw) + BACKLOG.md (RICE-scored)
    +-- specs/                            <-- 13 feature directories (one per feature)
    +-- sprints/                          <-- PI-1/, PI-2/ artifacts + lessons
    +-- exec/                             <-- state.md + state.html (Bridge dashboard)
    +-- fleet/                            <-- conflict-log.md
    +-- ledger/                           <-- fleet.db (SQLite) + schema + CLI + tests
    +-- sessions/                         <-- Session checkpoints + research findings
```

---

## 9. What Has Been Built

### PI-1: Generalization and First Pilot (closed 2026-05-13)

The framework was generalized from Day-to-Day-specific to project-agnostic, and the first feature was shipped through the full SDD lifecycle as a dogfood pilot.

**Deliverables:**
- Constitution generalized (mission, tech-stack, principles, CONTEXT decoupled from Day-to-Day)
- 10 binding architectural articles (I-X) with semver frontmatter <!-- staledoc-ok: PI-1 historical deliverable (articles XI/XII added in later PIs) -->
- 7 ADRs documenting key decisions
- Bootstrap CLI (`bootstrap.py greenfield` + `bootstrap.py brownfield`)
- 5 starter archetypes (python-library, python-web-service, data-pipeline, cli-tool, research-repo)
- Fleet ledger v0.1 (`ledger/fleet.db`) -- first feature shipped end-to-end through the SDD lifecycle
  - See `specs/2026-05-12-fleet-ledger/` for all 6 lifecycle artifacts
- `/evolve`, `/replan`, `/hire`, `/ask`, `/constitution` slash commands
- `CHEAT-SHEET.html` visual SVG workflow diagram
- Archetype recommender skill
- 4 lessons captured for `/evolve` curation

### PI-2: Fleet Maturity and CLI (closed 2026-05-16)

Five CLI tools shipped, live dashboard deployed, specialization mechanic exercised.

**Deliverables:**

| Tool | Tests | What It Does |
|------|-------|-------------|
| `state_builder.py` | 21 | Generates `exec/state.md` + `state.html` Bridge dashboard from ledger and artifacts |
| `fleet.py` | 9 | Fleet dispatch packets, ledger writes, mark outcomes, status queries |
| `qa.py` | 9 | Two-stage review automation (spec compliance + code quality) |
| `retro.py` | 8 | Sprint retrospective generator from ledger data |
| `schema_lint.py` | 10 | YAML frontmatter validation for all agents, skills, prompts |

Additional PI-2 deliverables:
- **Live Azure Bridge dashboard** (SDD-007) -- deployed on Azure Container Apps with Entra ID auth, scale-to-zero
- **First specialist promoted** -- `developer-general` earned permanent identity as `developer-cli-specialist-1` via `/hire specialist` (ADR-0007), citing 5 CLI implementations, 70 tests, consistent CLI-PATTERN.md adherence
- **Sprint C batch dispatch** -- 3 workers dispatched in parallel, 3 retros captured, 100% success rate
- **EM communication discipline** skill (LESSON-005) -- "recommend, do not menu"
- **PI-2 retrospective** -- 5 features delivered, 100% dispatch success, 6 lessons captured

### Feature Specs Completed (13 total)

Each lives in its own directory under `specs/YYYY-MM-DD-feature-name/` with co-located lifecycle artifacts (spec.md, plan.md, tasks.md, validation.md, clarification-log.md, RETRO.md).

| Feature | Status |
|---------|--------|
| fleet-ledger | DONE |
| fleet-bridge-dashboard | CLARIFY (design exploration) |
| cloud-dashboard | CLARIFY (design exploration) |
| dashboard-about-and-freshness | SPEC (blocked on HITL Azure provisioning) |
| fleet | DONE |
| fleet-cli | DONE |
| qa-cli | DONE |
| retro-cli | DONE |
| retro-closure | TASKS |
| schema-lint | DONE |
| sprint-c-validation | BACKLOG |
| state-builder | DONE |
| state-dashboard | DONE |

---

## 10. Current State and Metrics

**As of 2026-05-21 (historical snapshot -- see the live dashboard [`exec/state.html`](../exec/state.html) and the ledger [`exec/sprint-progress.md`](../exec/sprint-progress.md) for current metrics):**

| Metric | Value |
|--------|-------|
| Total commits | 40+ on master |
| Test count | See the live count in [`exec/state.md`](../exec/state.md) and the ledger |
| Agent definitions | 10 (5 Principals + 4 generic workers + 1 specialist) |
| Skills | 29 across 5 categories |
| Slash commands | 17 |
| ADRs | 23 (`001`-`023`; see [`docs/ADR/`](ADR/)) |
| Features delivered through SDD lifecycle | 8 DONE, 5 in various stages |
| Fleet dispatch success rate | 100% |
| Constitution articles | 12 binding (I-XII) |
| CLI tools operational | 6 (`state_builder`, `fleet`, `qa`, `retro`, `schema_lint`, `bootstrap`) |
| Archetypes | 5 starter constitutions |
| Lessons captured | 10 (4 from PI-1, 6 from PI-2) |

### Current PI: PI-9 (Experience Polish)

**For current state, read the live source.** The current PI, sprint, in-flight
feature, and test count live in the dashboard [`exec/state.html`](../exec/state.html),
the ledger [`exec/sprint-progress.md`](../exec/sprint-progress.md), and the roadmap
[`../constitution/roadmap.md`](../constitution/roadmap.md). PI-1..PI-8 are closed;
PI-9 ("Experience Polish") is active -- shipping two quality-of-life features: an
automated pre-dispatch file-overlap check and a backlog reorder that re-optimizes
on the backend.

---

## 11. Key Architecture Decisions

Nine ADRs document the major decisions. Each follows the format: context, decision, rationale, consequences, status.

| ADR | Title | Key Point |
|-----|-------|-----------|
| 001 | SDD Framework | Establishing the multi-agent spec-driven development system |
| 002 | Two-Folder Split | `.github/` for Copilot-native, `spec-driven-development/` for process state |
| 003 | Specialization Naming | Generic by default, specialized on demand; naming convention: `role-name-domain-N` |
| 004 | Executive Manager as Orchestrator | Single human entry point; routes questions, synthesizes answers, holds big picture (not a passive reporter) |
| 005 | Validation as Pre-Implementation Contract | Validation criteria written DURING `/spec`, locked at `/tasks`, verified at `/qa` |
| 006 | Constitution Semantic Versioning | YAML frontmatter with semver; `/constitution` command runs propagation scan |
| 007 | /hire Command and Role Lifecycle | Two modes: generic (create new role) and specialist (promote with evidence) |
| 008 | Hire Cloud Security Architect | Added cloud security principal for Azure deployment decisions |
| 009 | CI/CD OIDC Deploys to Production | GitHub Actions OIDC federated credential for auto-deploy on push |

Full text: `spec-driven-development/docs/ADR/`

---

## 12. Where to Read More (full document directory)

These documents are ordered by priority for someone getting up to speed. Section
0 above is the minimum 4-pointer onboarding; this section is the full directory.

### Tier 1: Start Here (required reading)

| Document | Purpose | Size |
|----------|---------|------|
| `docs/RULES.md` | 12 binding rules + HITL gates -- agent-facing rulebook | 6 KB |
| `docs/HIGH_LEVEL_DEV_TRACKER.md` | Current PI/sprint state, dependency graph, top 3 next moves | live |
| `docs/Temp/SPRINT_#_DETAILED_*.md` | Your sprint's deep spec (one file per active sprint) | varies |
| `INSTRUCTIONS.md` (root) | Entry point for any AI agent -- points to everything else | 2 KB |
| `.github/copilot-instructions.md` | Full project context, history, conventions, session recovery protocol | 12 KB |
| `spec-driven-development/CONTEXT.md` | Shared vocabulary for all agents -- terms, lifecycle, roles | 5 KB |
| `spec-driven-development/sessions/SESSION-MEMORY.md` | Most recent session checkpoint -- what shipped, what is open, next moves | 15 KB |
| `spec-driven-development/constitution/roadmap.md` | What is done, what is next, tech debt backlog | 4 KB |

### Tier 2: Understand the Design (recommended)

| Document | Purpose | Size |
|----------|---------|------|
| `spec-driven-development/constitution/principles.md` | 12 binding articles that govern the framework | 6 KB |
| `spec-driven-development/constitution/mission.md` | Vision, core values, non-negotiables | 3 KB |
| `spec-driven-development/constitution/decision-policy.md` | Level 0/1/2 decision authority | 3 KB |
| `spec-driven-development/constitution/quality-policy.md` | Test baseline, two-stage review, DoD | 3 KB |
| `spec-driven-development/docs/CLI-PATTERN.md` | Canonical Python stdlib CLI pattern used by all CLIs | 2 KB |
| `spec-driven-development/README.md` | Slash command reference + lifecycle quickstart | 6 KB |

### Tier 3: Deep Dives (reference material)

| Document | Purpose | Size |
|----------|---------|------|
| `spec-driven-development/GENERALIZATION_SDD.md` | 62KB portability guide -- how to bootstrap SDD on any project | 62 KB |
| `spec-driven-development/docs/FINAL_MERGED_PLAN.md` | Definitive 15-section framework plan (historical) | 85 KB |
| `spec-driven-development/sessions/framework-foundations-strategy.md` | Strategy memo: evolution loops, greenfield/brownfield convergence | 8 KB |
| `spec-driven-development/sessions/inspiration-repos-research-findings.md` | Research synthesis on all 3 inspiration sources | 6 KB |
| `spec-driven-development/sprints/PI-2/lessons.md` | Lessons from PI-2 (EM communication, closure ceremonies, Windows SQLite) | 4 KB |

### Tier 4: See It in Action (examples)

| Document | Purpose |
|----------|---------|
| `spec-driven-development/specs/2026-05-12-fleet-ledger/` | The dogfood pilot -- all 6 lifecycle artifacts (spec, plan, tasks, validation, clarification-log, RETRO) |
| `spec-driven-development/specs/2026-05-16-state-builder/` | Full lifecycle for the state_builder CLI tool |
| `spec-driven-development/cli/state_builder.py` | ~430 lines of stdlib Python that generates the Bridge dashboard |
| `spec-driven-development/ledger/schema.sql` | Fleet ledger SQLite schema (dispatches + decisions) |
| `spec-driven-development/docs/CHEAT-SHEET.html` | Visual SVG workflow diagram (open in browser) |

### Key Code to Review

| Path | What It Is | Tests |
|------|-----------|-------|
| `spec-driven-development/cli/state_builder.py` | Bridge dashboard generator | `test_state_builder.py` (21 tests) |
| `spec-driven-development/cli/fleet.py` | Fleet dispatch CLI | `test_fleet.py` (9 tests) |
| `spec-driven-development/cli/qa.py` | Two-stage review CLI | `test_qa.py` (9 tests) |
| `spec-driven-development/cli/retro.py` | Sprint retro generator | `test_retro.py` (8 tests) |
| `spec-driven-development/cli/schema_lint.py` | YAML frontmatter linter | `test_schema_lint.py` (10 tests) |
| `spec-driven-development/cli/bootstrap.py` | Project bootstrap (greenfield + brownfield) | -- |
| `spec-driven-development/ledger/ledger_cli.py` | Fleet ledger CRUD CLI | `test_ledger.py` (13 tests) |

All CLI tools follow the canonical pattern in `docs/CLI-PATTERN.md`: stdlib-only, testable `main(argv)` signature, `argparse` with subcommands, `pathlib.Path` for files, UTC timestamps, custom exception classes.

---

## 13. Agent Dispatch Flow

How work flows from human intent to merged code.

```
Human (executive sponsor + sole HITL gate)
  |
  v
Principal Executive Manager  <-- the single phone number
  |  Captures idea, routes to right Principal(s), synthesizes answers back
  |
  +--> Principal Product Manager      (backlog, RICE scoring, sprint/PI planning)
  +--> Principal Architect            (spec.md, ADRs, pattern enforcement)
  +--> Principal Software Developer   (plan.md, tasks.md, worker dispatch, two-stage review)
  +--> Principal UI Designer          (UI specs, design tokens, visual layer) [ADR-0010]
  +--> Principal Cloud Security Arch. (Azure, identity, secrets, threat modeling)
         |
         | Each Principal hires the workers it needs PER TASK:
         v
      Worker Agents (1-3 files each, disposable per task)
         +-- developer-general
         +-- ux-designer-general
         +-- qa-engineer-general
         +-- data-scientist-general
         +-- developer-cli-specialist-1   (earned via ADR-0007)
         +-- <hired on demand via /hire>
```

### Dispatch protocol (per task)

1. **PM** triages the idea in `backlog/BACKLOG.md` (RICE-scored).
2. **Architect** writes `specs/YYYY-MM-DD-{slug}/spec.md` + `validation.md`
   (validation locked BEFORE implementation per Article X).
3. **SW Dev** writes `plan.md` and decomposes into `tasks.md`. Tasks are tagged
   `[P]` (parallel) or `[S]` (sequential), `[AFK]` (autonomous) or `[HITL]`
   (human gate). Tasks are 1-3 files in scope (Rule 8 / Article IV).
4. **SW Dev** creates a worktree `wt-pi{N}-s{M}-{slug}` (Rule 7) and dispatches
   the worker via `cli/fleet.py dispatch` -- this writes a packet to
   `dispatches/PI-N/<id>.md` and a row to `ledger/fleet.db`.
5. **Worker** receives the dispatch packet (contains: task description, embedded
   spec, file scope, validation criteria, the four required-reading pointers).
   Worker executes TDD against the validation contract.
6. **QA Engineer** (different worker) runs spec-compliance review FIRST. If
   COMPLIANT, a second reviewer runs code-quality review. Rule 10.
7. **SW Dev** merges the worktree into `master` (human-approved if cross-cutting
   per HITL #4) and tears down the worktree.
8. **PM** marks the feature DONE in `BACKLOG.md` and `HIGH_LEVEL_DEV_TRACKER.md`.
9. **EM** updates `exec/state.md` (via `cli/state_builder.py`) and routes the
   close-of-loop back to the human.

### How the Executive Manager talks to the human

- **Default mode:** "I recommend X because Y. OK?" -- single recommendation
  with one-line reasoning. (Per LESSON-005, `em-communication-discipline`.)
- **Menu mode** (max 3 options): only when the choice is irreversible,
  expensive, or genuinely ambiguous.
- **Routing mode:** "Routing this to Principal X. Will report back with the
  synthesized answer."
- **Status mode:** "Here is the tracker state. Top 3 next moves: ..."

The EM never absorbs deep sprint context -- it points to detail docs and lets
the Principals own the depth.

---

## 14. Codebase Reading Guide for Brownfield Agents

This project is brownfield as of 2026-05-25: PI-1 and PI-2 are closed, 70 tests
pass, the Bridge dashboard is live on Azure. Before you write your first line
of code, read the existing implementations in this order so your additions
match the established patterns.

### Reading order (brownfield)

| # | Path | What you learn | Reading time |
|---|------|----------------|--------------|
| 1 | [`docs/CLI-PATTERN.md`](CLI-PATTERN.md) | Canonical Python stdlib CLI pattern: `main(argv)`, argparse subcommands, custom exceptions, pathlib | 5 min |
| 2 | [`ledger/schema.sql`](../ledger/schema.sql) | SQLite schema -- `dispatches` and `decisions` tables. Source of truth for traceability. | 3 min |
| 3 | [`ledger/ledger_cli.py`](../ledger/ledger_cli.py) | First production CLI in the project; the canonical CRUD pattern. 13 tests. | 15 min |
| 4 | [`cli/state_builder.py`](../cli/state_builder.py) | The largest CLI (~1,273 lines). Generates `exec/state.md` AND serves the live HTML dashboard. Read the docstring header first -- it cross-references two specs. 21 tests. | 30 min |
| 5 | [`cli/fleet.py`](../cli/fleet.py) | Fleet dispatch CLI. Writes packets, calls ledger. The pattern for any new CLI that interacts with the ledger. 9 tests. | 15 min |
| 6 | [`cli/qa.py`](../cli/qa.py) | Two-stage review automation. Pattern for any review/validation tool. 9 tests. | 10 min |
| 7 | [`cli/retro.py`](../cli/retro.py) | Sprint retro generator from ledger data. Pattern for any reporting tool. 8 tests. | 10 min |
| 8 | [`cli/schema_lint.py`](../cli/schema_lint.py) | YAML frontmatter validator. Pattern for any lint/validation tool. 10 tests. | 10 min |
| 9 | [`cli/bootstrap.py`](../cli/bootstrap.py) | Greenfield + brownfield project scaffolding. Read if you are touching anything portability-related. | 20 min |
| 10 | Any `cli/test_*.py` file | The test pattern: unittest, `TemporaryDirectory(ignore_cleanup_errors=True)` on Windows (LESSON-009), `gc.collect()` in `tearDown` for SQLite-touching tests. | 10 min |

Total: about 2 hours of reading before any new CLI work.

### Code that is NOT canonical (skip unless directly needed)

- `cli/common/*.py` -- scaffolds, not all implemented. Refer to actual CLIs above.
- `.github/skills/domain/*` -- marked as EXAMPLES from the Day-to-Day Agent
  project. Not framework canon.
- `docs/FINAL_MERGED_PLAN.md` -- 85 KB historical planning doc. Skim only if
  you need to understand a decision; current state lives in roadmap +
  HIGH_LEVEL_DEV_TRACKER.

### What to read by role

**Worker -- Developer:** rows 1, 3, 5, 6, 10 (~50 min), plus the CLI most
adjacent to your task.

**Worker -- QA Engineer:** rows 1, 6, 7, 10 (~35 min), plus the spec + tests
for the feature under review.

**Worker -- UX Designer:** row 4 (state_builder.py serves the dashboard), plus
`exec/state.html` and the `state-builder` and `state-dashboard` spec dirs.

**Principal -- Architect:** rows 1, 2, 4 (~40 min), plus ALL files in
`docs/ADR/`, plus `constitution/`.

**Principal -- SW Developer:** rows 1, 3, 4, 5, 10 (~80 min). You will dispatch
workers and need to know the established patterns to review their PRs.

**Principal -- PM:** `backlog/BACKLOG.md`, `constitution/roadmap.md`,
`sprints/PI-1/lessons.md`, `sprints/PI-2/lessons.md`, and the
`HIGH_LEVEL_DEV_TRACKER.md`. Skip CLI internals.

**Principal -- UI Designer:** row 4 (the dashboard server), plus
`specs/2026-05-16-state-dashboard/`, `specs/2026-05-16-cloud-dashboard/DESIGN.md`,
and the live dashboard at https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/.

### Critical patterns to honor (from the reading)

- **Stdlib only.** No `requests`, no `pydantic`, no `flask`. `urllib`, `http.server`,
  `sqlite3`, `argparse`, `pathlib`, `dataclasses`. This is the portability claim.
- **`main(argv)` signature.** Every CLI's entry point takes `argv` for testability.
- **Custom exception classes.** Don't raise bare `Exception`. See `cli/state_builder.py`
  for `StateBuilderError` pattern.
- **UTC timestamps.** `datetime.now(timezone.utc)`, ISO 8601 format.
- **No emojis.** Plain ASCII (Rule 1).
- **TDD.** Test file goes in before implementation (Rule 2 / Article X).
- **Worktrees.** Never work on `master` directly (Rule 7).

---

## 15. Getting Started

### If You Want to Understand the Framework

1. Read this document
2. Open `spec-driven-development/docs/CHEAT-SHEET.html` in a browser for the visual workflow
3. Read `spec-driven-development/CONTEXT.md` for the shared vocabulary
4. Browse `spec-driven-development/specs/2026-05-12-fleet-ledger/` to see a complete feature lifecycle

### If You Want to Run the Tests

```powershell
cd C:\Training\Projects\Evolving-Multi-Agent-Framework
python -m pytest spec-driven-development/ -v --tb=short
# Expected: 70 passed
```

### If You Want to See the Dashboard

```powershell
python spec-driven-development/cli/state_builder.py serve
# Opens Bridge dashboard at http://localhost:8000
```

### If You Want to Bootstrap SDD on a New Project

```bash
# Greenfield (new project)
python spec-driven-development/cli/bootstrap.py greenfield python-library \
  --project-name MyLib --owner "Your Name" --target ../MyLib

# Brownfield (existing project)
python spec-driven-development/cli/bootstrap.py brownfield ../my-existing-project --draft-only
```

### If You Want to Use the Agent Team

1. Open the repo in VS Code with the GitHub Copilot extension
2. Open the **Principal Executive Manager** agent in Copilot Chat (it appears in the agent picker)
3. Tell it your idea in plain language
4. Follow its guidance through the lifecycle

---

## 16. What Is Next

### Immediate (in-flight)

- **Unblock SDD-009/010** (Dashboard About + Freshness) -- the human needs to run 9 Azure HITL provisioning steps for OIDC federated credential, then dispatch T-003 + T-004 to workers
- **Curate PI-2 lessons** (LESSON-006 through LESSON-010 are still OPEN) via `/evolve`

### PI-3: Portability Validation

- **Bootstrap SDD onto the Day-to-Day Agent project** (brownfield) -- the portability test
- Validate that `bootstrap.py brownfield` works on a real established codebase
- Run one feature through the full SDD lifecycle in the host project
- Publish `GENERALIZATION_SDD.md` v1.0 after second-project test
- Establish SDD process metrics baseline (cycle time, defect escape rate, fleet utilization)

### Future PIs

- GitHub template repo packaging for easy distribution
- GitHub Issues integration (`/taskstoissues`)
- Bridge dashboard v3 (D3 force-directed graph, WebSocket live push)
- Fleet ledger schema migration scripts
- Domain skill library expansion

### Open Design Questions

1. **Framework versioning model** -- semver on the framework as a whole? Pin per-host?
2. **Distribution model** -- GitHub template repo? Scaffolding CLI? npm/pip package?
3. **Host-vs-framework skill ownership** -- when a host modifies a framework skill, does it diverge or fork?

---

## Quick Verification Commands

```powershell
# Check current state
cd C:\Training\Projects\Evolving-Multi-Agent-Framework
git log --oneline -10

# Run all tests
python -m pytest spec-driven-development/ -v --tb=short

# Lint all agent/skill/prompt frontmatter
python spec-driven-development/cli/schema_lint.py

# Generate fresh state dashboard
python spec-driven-development/cli/state_builder.py

# View the visual cheat sheet
start spec-driven-development\docs\CHEAT-SHEET.html

# Try the bootstrap CLI
python spec-driven-development/cli/bootstrap.py --help
```

---

*This document was authored on 2026-05-21. For the latest session state, always check `spec-driven-development/sessions/SESSION-MEMORY.md`.*
