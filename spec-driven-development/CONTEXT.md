# CONTEXT -- Shared Language for the Evolving Multi-Agent Framework

This file captures the shared vocabulary, assumptions, and conventions that all agents
must understand before working on this framework. It follows the Matt Pocock pattern: a
single document that grounds all participants in the same mental model.

Updated by `grill-with-docs` sessions and ADRs. Acts as a living glossary.

---

## Project Identity

- The Evolving Multi-Agent Framework (working title: Spec-Driven Development / SDD) is a portable, replicable system for orchestrating a fleet of AI agents through a structured development lifecycle
- It is project-agnostic -- intended to be bootstrapped onto any codebase (web app, library, data pipeline, CLI, research repo)
- It does not impose runtime technologies on the host project; it imposes a process, a file layout, and a set of agent definitions
- The framework was extracted from the Day-to-Day Agent project on 2026-05-12 and now stands alone

---

## SDD Framework Terms

| Term | Definition |
|------|------------|
| **Framework** | This repository -- the agent definitions, skills, prompts, templates, constitution, and process docs that constitute SDD |
| **Host Project** | Any project that adopts SDD by copying `.github/` and `spec-driven-development/` into its own root |
| **Orchestrator / Entry Point** | The Principal Executive Manager in its expanded role: the single human-facing entry point that captures kickoffs, routes ad-hoc questions, synthesizes answers, surfaces escalations, and holds the big picture on the human's behalf. See ADR-0004. |
| **Routing Memo** | The internal handoff format the Executive Manager uses to dispatch a question to the right Principal: original question, relevant state.md context, urgency, and the explicit ask "answer at engineering depth; I will translate to executive register." |
| **Executive Register** | The communication style the Executive Manager uses when speaking to the human: TL;DR + detail in plain language + implication for timeline/scope/risk + recommended next action. No jargon. |
| **PI** | Program Increment -- a planning horizon containing 5 sprints (symbolic; AI fleet compresses wall-clock time) |
| **Sprint** | A development cycle within a PI (symbolic cadence -- not a fixed calendar duration) |
| **Spec** | A formal feature specification document in `specs/YYYY-MM-DD-feature-name/spec.md` |
| **Plan** | Implementation plan co-authored by Architect and SW Dev, lives next to the spec |
| **Task** | An atomic unit of work (1-3 files max) derived from a plan, tagged with [P]/[S]/[AFK]/[HITL] |
| **Gate** | A formal checkpoint between lifecycle phases requiring approval before proceeding |
| **AFK** | Away From Keyboard -- a task safe for fully autonomous agent execution |
| **HITL** | Human In The Loop -- a task that requires a human decision before completion |
| **[P]** | Parallelizable task tag -- safe for fleet dispatch alongside other [P] tasks |
| **[S]** | Sequential task tag -- must be executed alone or in order |
| **Fleet** | The pool of generic worker agents available for parallel dispatch |
| **Dispatch** | A single assignment of one task to one worker agent, recorded in the ledger |
| **Worker** | A generic agent (Developer, UX Designer, Data Scientist, QA Engineer) |
| **Principal** | A senior agent role with decision authority (Executive Manager, Product Manager, Architect, Software Developer) |
| **Skill** | A composable, single-purpose `SKILL.md` file under `.github/skills/` that an agent loads on demand |
| **Skill Pack** | A bundle of skills granted to a worker that earns specialization in a domain |
| **Specialization** | The mechanic by which a generic worker earns a permanent identity through demonstrated competence |
| **Two-Stage Review** | The mandatory review order: spec compliance FIRST, code quality SECOND, by different reviewers |
| **Two-Folder Split** | The architectural rule that `.github/` holds Copilot-native files (agents, skills, prompts, instructions) and `spec-driven-development/` holds everything else |
| **Constitution** | The six immutable files in `spec-driven-development/constitution/` that define mission, principles, tech stack, roadmap, decision policy, quality policy |
| **Ledger** | `spec-driven-development/ledger/fleet.db` -- the SQLite source of truth for all fleet dispatches, agent records, decisions, and skill assignments |
| **Worktree** | A git worktree at `../wt-{shortname}` providing parallel branch isolation for fleet workers |
| **Curated Briefing** | The < 2KB executive summary in `exec/state.md` -- the only artifact the Executive Manager reads |
| **RICE** | Reach, Impact, Confidence, Effort -- the scoring rubric used in `/triage` and the backlog |

---

## Lifecycle Shorthand

```
IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
```

- `/triage` -- groom an idea, RICE score, assign priority
- `/clarify` -- structured clarification session (one question at a time, with recommendation)
- `/spec` -- generate a feature spec from clarified requirements
- `/plan` -- generate an implementation plan from an approved spec
- `/tasks` -- decompose a plan into tagged, batched tasks
- `/analyze` -- cross-artifact consistency check (spec vs plan vs tasks)
- `/fleet` -- parallel dispatch of [P][AFK] tasks to workers
- `/implement` -- execute a single task (TDD: test first, then implement)
- `/qa` -- validate implementation against spec
- `/retro` -- sprint retrospective
- `/state` -- refresh and present `exec/state.md`

Spec sizing rule (prevents ceremony bloat):

| Change Size | Process |
|-------------|---------|
| Bug fix, < 3 files | No spec. Task + test + review. |
| Feature, < 5 files | Lightweight spec: user story + requirements + success criteria only |
| Feature, >= 5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

---

## Agent Roles at a Glance

| Role | Type | Responsibility |
|------|------|----------------|
| **Principal Executive Manager** | Principal | **Single human-facing entry point.** Owns kickoff, ad-hoc Q&A routing with answer synthesis, status, escalation, big-picture awareness. Reads `exec/state.md` by default; may read raw artifacts to answer routed questions; never modifies any artifact except (optionally) `state.md`. Output to the human is always at executive register. |
| Principal Product Manager | Principal | Backlog ownership, RICE scoring, acceptance criteria, sprint and PI planning |
| Principal Architect | Principal | Specs, plans, ADRs, architectural quality, pattern enforcement |
| Principal Software Developer | Principal | Task decomposition, fleet dispatch, code review, integration |
| Developer (generic) | Worker | Implements tasks; specializes on demand via skill packs |
| UX Designer (generic) | Worker | Designs flows, wireframes, accessibility checks |
| QA Engineer (generic) | Worker | Writes and reviews tests, runs validation against specs |
| Data Scientist (generic) | Worker | Analysis, metrics, evaluation tasks |

New worker roles are created when first needed (not anticipated up front).

---

## Architecture Decisions

Populated by `grill-with-docs` sessions and ADRs in `spec-driven-development/docs/ADR/`.

Three ADRs exist at framework v0.1:
- ADR-0001 -- Two-folder split (`.github/` vs `spec-driven-development/`)
- ADR-0002 -- Two-stage review order (spec compliance before code quality)
- ADR-0003 -- Symbolic cadence (PI/Sprint as ceremony rhythm, not wall-clock duration)

---

## Assumptions

Populated during clarification phases. Each assumption is recorded with its source
(human answer, deferred, or unresolved) in `clarification-log.md` per feature.

Framework-level assumptions held at v0.1:

- The host project uses VS Code with the GitHub Copilot extension
- The host project uses git for version control
- The human developer holds final approval authority on all Level 1 and Level 2 decisions
- AI agents have access to a sufficiently capable LLM (frontier-class or comparable)
- The framework is read by agents via session-start instructions (`copilot-instructions.md`)

---

## Conventions Reference

- Architectural articles: `spec-driven-development/constitution/principles.md`
- Coding and session conventions: `.github/copilot-instructions.md`
- Decision authority: `spec-driven-development/constitution/decision-policy.md`
- Quality standards: `spec-driven-development/constitution/quality-policy.md`
- Portability and bootstrap: `spec-driven-development/GENERALIZATION_SDD.md`
- Definitive plan: `spec-driven-development/docs/FINAL_MERGED_PLAN.md`
