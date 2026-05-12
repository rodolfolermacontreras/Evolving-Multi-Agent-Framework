# Mission

## Project

Evolving Multi-Agent Framework (working title: Spec-Driven Development / SDD) -- a portable,
replicable system for orchestrating a fleet of AI agents through a structured development
lifecycle.

## Owner

Rodolfo Lerma, Senior Data Scientist (L63)
WWIC Central Analytics / Design & Analytics, Microsoft

## Vision

A framework that lets one human developer ship production-quality software at the pace of a
small team, by treating AI agents as first-class team members with defined roles, scoped
responsibilities, and explicit handoff protocols.

The framework is project-agnostic. It can be bootstrapped onto any codebase -- web app,
data pipeline, library, CLI, research repo -- without rewriting its core. The host project
contributes its own constitution (mission, tech stack, principles); the framework contributes
the process (lifecycle, agents, skills, gates, ledger).

## Users

Primary users: solo developers and small teams who want to multiply their output by
delegating tactical work to AI agents while keeping strategic decisions human-controlled.

Indirect users: any downstream project that adopts SDD as its development methodology.

## Success Criteria

The framework succeeds when:

- A new project can bootstrap SDD in under a day, following GENERALIZATION_SDD.md
- Every shipped feature traces back through tasks -> plan -> spec -> clarified idea
- The two-stage review (spec compliance + code quality) catches defects before merge
- The fleet ledger captures every dispatch, decision, and handoff for full auditability
- Generic worker agents become specialists by demonstrated competence, not configuration
- The Principal Executive Manager can summarize project state from `exec/state.md` alone
- A second project can adopt SDD without modifying the framework core

## Core Values

1. SEPARATION OF CONCERNS: Strategy (Principals) and tactics (workers) are different roles with different agents.
2. TRACEABILITY: Every artifact is a file. Every dispatch is logged. Every decision has an owner.
3. SPECIALIZATION OVER GENERALISM: A reviewer that only reviews catches more than a general assistant. Workers stay constrained to 1-3 files per task.
4. GENERIC BY DEFAULT, SPECIALIZED ON DEMAND: Workers start generic. They earn permanent identity through demonstrated competence in a domain.
5. CEREMONY PROPORTIONAL TO RISK: Bug fixes < 3 files skip the spec. Schema changes require ADRs. Sizing prevents process bloat.
6. PORTABILITY: The framework owns the process. The host project owns its mission, stack, and principles. Neither overrides the other.
7. HUMAN IN COMMAND: The human always holds the final approval. Agents propose; humans dispose on Level 1 and Level 2 decisions.

## Non-Negotiables

These rules apply to the framework repository itself. Host projects that adopt SDD layer
their own non-negotiables on top via their own `.github/copilot-instructions.md`.

- Two-folder split is invariant: `.github/` for Copilot-native files, `spec-driven-development/` for process state
- Principal agents live as `.github/agents/*.agent.md` for VS Code auto-discovery
- Constitution files are immutable without an ADR
- No feature merges without an approved spec (except bug fixes < 3 files)
- Two-stage review order is fixed: spec compliance first, code quality second
- Fleet ledger is the source of truth for all dispatches
- Executive Manager is the single human-facing entry point: owns kickoff, ad-hoc Q&A routing with answer synthesis, status, escalation. Reads `exec/state.md` by default; may read raw artifacts to answer routed questions but never modifies any artifact except (optionally) `state.md`. Output to the human is always at executive register. (See ADR-0004.)
- Completed roadmap items are never deleted -- mark done with date
- Small, frequent commits -- format: `type: short description`
- No emojis in code, docs, or commits
- Dates always `YYYY-MM-DD`

## Origin

The framework was extracted from the Day-to-Day Agent project (a personal AI work
management dashboard built with FastAPI/HTMX) on 2026-05-12 after proving its value
inside that codebase. It is now a standalone initiative. Day-to-Day Agent remains a
useful reference implementation and example host project but is no longer the framework's
target.
