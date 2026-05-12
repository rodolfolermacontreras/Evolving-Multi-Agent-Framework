# Spec-Driven Development Framework

A disciplined, AI-native development process for any project. Four Principal agents
orchestrate a fleet of generic workers through a spec-driven lifecycle, producing
traceable, high-quality features with minimal human ceremony overhead.

The framework is project-agnostic. It can be bootstrapped onto any codebase by copying
`.github/` and `spec-driven-development/` into the host project root and authoring the
host's own constitution. See `GENERALIZATION_SDD.md` for the bootstrap procedure.

Full details: `spec-driven-development/docs/FINAL_MERGED_PLAN.md`

---

## What SDD Is

SDD is a structured process that connects an idea to a merged feature through a sequence
of formal artifacts: backlog item -> clarification log -> spec -> plan -> tasks -> dispatch ->
two-stage review -> done.

Each artifact is a file. Each phase has a gate. Gates have defined approvers. Nothing
proceeds to implementation without an approved spec.

The framework does not replace the existing project conventions -- it wraps them. The rules
in `.github/copilot-instructions.md` remain the root authority. SDD adds ceremony only where
the cost is worth the quality gain.

---

## Two-Folder Split

| Folder | Contents | Why |
|--------|----------|-----|
| `.github/` | Agents (Principals + workers), skills, prompts, instructions | Copilot-native `.agent.md` format, auto-discovered by VS Code |
| `spec-driven-development/` | Constitution, specs, sprints, CLI, ledger, templates | Framework process state, not Copilot-native |

All agents (Principals and workers) live as `.github/agents/*.agent.md` -- auto-discovered by VS Code Copilot.
Principals appear in the Copilot Chat picker and include `handoffs` for agent-to-agent workflow transitions.
Everything else lives under `spec-driven-development/`.

---

## How to Get Started

The Principal Executive Manager is your single human-facing entry point. Talk to
the Executive Manager first; it will answer directly when it can, otherwise route
to the right Principal, get the answer, and synthesize it back at executive
register. You are also welcome to attend ceremonies (sprint planning, PI planning,
retros) directly -- the Executive Manager is the *default* entry point, not a wall.

### Starting a new feature

1. Open the **Principal Executive Manager** agent in VS Code Copilot Chat.
2. Tell it the idea in plain language. The Executive Manager captures it in
   `backlog/IDEAS.md` and hands off to the Principal Product Manager.
3. The PM runs `/triage` -- grills the idea, RICE-scores it, assigns priority.
4. The PM (or Architect, depending on what `/triage` surfaces) runs `/clarify` to
   resolve ambiguities one question at a time.
5. The PM runs `/spec` to generate the feature spec. **Human approves before next
   step.**
6. Open the **Principal Architect** agent and run `/plan`.
7. Open the **Principal Software Developer** agent and run `/tasks`.
8. Run `/implement` for sequential tasks or `/fleet` for parallel batches.
9. Two-stage review: spec compliance first, then code quality.
10. Merge to your integration branch.

### Asking ad-hoc questions

Use `/ask` against the Executive Manager (or just ask in plain language). It
will:

1. Try to answer from `exec/state.md` and big-picture awareness.
2. If not, classify the question, route to the right Principal, wait, and
   synthesize the answer back to you with TL;DR, detail, implication, and a
   recommended next action.

### Attending a sprint ceremony

- Sprint planning: the PM has the draft ready. The Executive Manager will tell
  you when it is. Walk through it with the PM directly.
- PI planning: PM + Architect + SW Dev + you. Executive Manager coordinates and
  briefs you beforehand.
- Sprint retro: the PM runs `/retro`; the Executive Manager summarizes outcomes
  and ensures lessons are captured.

### Checking project state (any time)

Ask the Executive Manager: "what's the status?" or run `/state` to refresh the
underlying `exec/state.md` snapshot.

---

## Chatmode Quick Reference

| Chatmode | When to Use |
|----------|-------------|
| Principal Executive Manager | **Default entry point.** Any question, new idea, status check, or ad-hoc routing. Owns kickoff and answer synthesis. |
| Principal Product Manager | Backlog, PI planning, sprint planning, acceptance review, triage, clarify, spec authoring (with Architect) |
| Principal Architect | Specs, plans, ADRs, tech debt, architecture review |
| Principal Software Developer | Tasks, dispatch, code review, integration, fleet coordination |

---

## Slash Command Quick Reference

| Command | Phase | What It Does |
|---------|-------|-------------|
| `/ask` | Any | Ask the Executive Manager any project question. It answers directly or routes, synthesizes, and returns at executive register. |
| `/triage` | Backlog | Grill idea, RICE score, assign P1-P4 |
| `/clarify` | Pre-spec | Structured Q&A, one question at a time with recommendation |
| `/spec` | Specify | Generate feature spec from clarified requirements |
| `/plan` | Plan | Generate implementation plan from approved spec |
| `/tasks` | Tasks | Decompose plan into tagged, batched tasks |
| `/analyze` | Spec-Plan | Cross-artifact consistency check |
| `/fleet` | Implement | Parallel dispatch of [P][AFK] tasks |
| `/implement` | Implement | Execute single task (TDD workflow) |
| `/qa` | Review | Validate implementation against spec |
| `/retro` | Ceremony | Sprint retrospective, max 3 action items |
| `/replan` | Ceremony | Review constitution/roadmap/skills/lessons after every feature DONE |
| `/state` | Any | Refresh and present exec/state.md |

---

## Constitution Files

The constitution is the immutable core of the framework. All agents read it before acting.

| File | Contents |
|------|----------|
| `constitution/mission.md` | Project identity, owner, vision, values, non-negotiables |
| `constitution/tech-stack.md` | Approved technologies, key modules, approval-required changes |
| `constitution/principles.md` | Nine binding architectural articles |
| `constitution/roadmap.md` | What is done, what is next, tech debt backlog |
| `constitution/decision-policy.md` | Level 0/1/2 decision authority and escalation path |
| `constitution/quality-policy.md` | Test baseline, two-stage review, security conventions, DoD |

---

## Key Files and Directories

| Path | Purpose |
|------|---------|
| `CONTEXT.md` | Shared vocabulary for all agents (read this first after the constitution) |
| `backlog/IDEAS.md` | Raw idea capture |
| `backlog/BACKLOG.md` | Prioritized backlog with RICE scores |
| `specs/` | One directory per feature: spec, plan, tasks, clarification log, review |
| `sprints/PI-{N}/` | Sprint artifacts (PLAN.md, BOARD.md, RETRO.md) |
| `exec/state.md` | Auto-built executive summary (<= 2KB) |
| `ledger/fleet.db` | SQLite source of truth for fleet dispatches and agent records |
| `templates/` | Reusable document templates (spec, plan, tasks, agent brief, ADR) |
| `docs/ADR/` | Architecture Decision Records |
| `docs/SCORECARD.md` | Sprint-level process metrics |

---

## Spec Sizing Rule

Not every change needs full ceremony.

| Change Size | Process |
|-------------|---------|
| Bug fix, < 3 files | No spec. Task + test + review. |
| Feature, < 5 files | Lightweight spec: user story + requirements + success criteria only |
| Feature, >= 5 files | Full spec with all sections |
| Cross-cutting or schema change | Full spec + ADR + human approval |

---

## Non-Negotiables (from root authority)

Source of truth: `.github/copilot-instructions.md`

- Never touch master branch
- Never commit directly to integration/improvements
- No new pip dependencies without human approval
- Always use .venv
- No emojis
- 743+ tests must pass (count must never decrease)
- Small, frequent commits -- format: `type: short description`
