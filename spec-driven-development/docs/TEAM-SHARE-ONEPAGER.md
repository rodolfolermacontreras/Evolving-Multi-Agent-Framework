---
id: SDD-DOC-TEAM-SHARE-ONEPAGER
type: doc
status: draft
owner: principal-executive-manager
updated: 2026-06-08
audience: WWIC Central Analytics team (internal)
---

# Spec-Driven Development (SDD) — Team Share One-Pager

**For:** WWIC Central Analytics team
**From:** Rodolfo Lerma
**Date:** 2026-06-08
**Status:** Pre-release. Recommended to share after Sprint 8 close (see "When can you use it").

---

## What it is

A portable framework for doing **spec-driven development with a team of AI agents** instead of ad-hoc chat-and-paste prompting. One human developer orchestrates four principal AI agents (Executive Manager, Product Manager, Architect, Software Developer) and a fleet of worker agents through a structured lifecycle with quality gates, traceability, and separation of concerns.

It is **not a chatbot**. It is **not a code generator**. It is a discipline: an opinionated process that turns a one-line idea into a shipped, tested, traceable feature.

## What problem it solves

If you've ever:

- Lost track of what you asked the AI to build three sessions ago
- Hit context-overload when the same chat covers architecture, implementation, and tests
- Watched the AI silently change patterns between sessions
- Built a feature you can't explain six months later because the "why" lives in a deleted chat history
- Felt the friction of "do I write a spec, or just code this?" for every small change

…this framework is the answer. It enforces a vocabulary, a lifecycle, and a paper trail so that scaling AI-assisted development beyond a single session does not produce chaos.

## How it works (the lifecycle)

```
IDEA → BACKLOG → CLARIFY → SPEC → PLAN → TASKS → IMPLEMENT → REVIEW → DONE
```

Each phase has a gate. Each gate has an approver. Nothing reaches IMPLEMENT without an approved spec (except bug fixes <3 files). Every dispatch and decision is logged to a SQLite ledger.

## What's in the box

- **6 principal agents** (Executive Manager, Product Manager, Architect, Software Developer, UI Designer, Cloud Security Architect)
- **5 generic worker agents** + 1 specialist (CLI developer earned through demonstrated competence)
- **32 composable skills** across 5 categories (core, workflow, engineering, operational, domain examples)
- **17 slash commands** (`/triage`, `/clarify`, `/spec`, `/plan`, `/tasks`, `/analyze`, `/fleet`, `/implement`, `/qa`, `/retro`, `/state`, etc.)
- **5 working CLIs** (`state_builder`, `fleet`, `qa`, `retro`, `schema_lint`)
- **Live ops dashboard** (`python state_builder.py serve` opens a local HTTP UI showing PI/sprint/feature state)
- **11-article constitution** that the framework enforces on itself
- **Filesystem data contracts** — every artifact carries YAML frontmatter; `schema_lint` keeps them honest
- **Fleet ledger** — every agent dispatch is logged with full traceability
- **Brownfield bootstrap** — `bootstrap.py host-link` drops the framework into any existing repo via symlink/junction without polluting the host's `.github/` or `.gitignore`

## What it has shipped (numbers)

- **259 automated tests** passing as of 2026-06-08
- **18 features** through full lifecycle (CLARIFY → DONE)
- **13 architecture decision records** (ADRs)
- **2 constitutional articles** ratified by Level-2 owner decision (Article VII corollary "one feature, one session"; Article XI serial CLARIFY/SPEC gate)
- **5 product increments** (PI-1 through PI-5) — 3 closed, 2 in progress

## Why it's different from other AI tooling

- **Not a single agent that tries to do everything.** It's a constrained team with explicit roles. A code reviewer that only reviews code catches more than a general assistant.
- **Two-stage review.** Spec compliance first ("does it match the spec?"), code quality second ("is it well-written?"). Different reviewers.
- **Specs are versioned first-class artifacts.** Every feature has a spec dir on disk with `spec.md`, `plan.md`, `tasks.md`, `validation.md`, `clarify.md`. You can git-blame why a feature is built a certain way.
- **Spec sizing prevents ceremony bloat.** Bug fix under 3 files = no spec. Not every change deserves full ceremony.
- **The framework runs itself.** It uses its own lifecycle to ship its own features. If a process doesn't work, you find out fast.

## Where it came from

Born inside the **Day-to-Day Agent** project (a personal AI-powered work management dashboard, 1,065+ tests, FastAPI/HTMX) when ad-hoc AI prompting hit its scaling wall. Extracted to a standalone framework on 2026-05-12.

Draws from:
- **Spec-Kit** (GitHub) — command naming convention (`/specify`, `/clarify`, `/plan`, `/tasks`, etc.)
- **Matt Pocock's Skills pattern** — composable, single-purpose `SKILL.md` files agents load on demand
- **DeepLearning.AI "Spec-Driven Development with Coding Agents"** (Paul Everitt, JetBrains) — the 3-file constitution model (mission + tech-stack + roadmap), the feature loop, brownfield-via-archaeology
- **SAFe (Scaled Agile Framework)** — Program Increments + Sprints adapted for a single developer + AI fleet (symbolic cadence; AI compresses wall-clock time dramatically)

## When can you use it

**Two readiness gates:**

| Gate | Trigger | What it unlocks |
|---|---|---|
| **Gate 1 (minimum)** | Sprint 7 close (in flight 2026-06-08) | Anti-conflict gates fully wired; UI lifecycle variant defined. Usable by a team member who already knows SDD vocabulary. |
| **Gate 2 (recommended)** | Sprint 8 close | ADO/GitHub Issues bridge shipped (Scott named this as the gap blocking team adoption); model-upgrade discipline shipped. Pitchable to the team without the "I can't use this without ADO" objection. |

**Stretch (post-PI-5):** GENERALIZATION_SDD.md v1.0 (battle-tested on a second project) + GitHub template repo packaging. That's when it can be handed to a stranger without hand-holding.

## How you'll get it

When ready: clone the repo, run `python spec-driven-development/cli/bootstrap.py host-link --target <your-repo>`, follow the HOST-INTEGRATION.md walkthrough. The framework lives in its own folder; your host repo's `.github/` stays clean (a symlink does the magic).

## Questions that always come up

- **Q: Do I have to use all the agents?** No. Start with Executive Manager (the single human-facing entry point). Other principals come in as you need them.
- **Q: What if my project already has its own conventions?** The framework is opt-in. The `host-link` command never overwrites existing files; it refuses on conflict by default.
- **Q: What's the smallest thing I can ship through this?** A bug fix under 3 files needs no spec. That's the floor. Above that, the lifecycle scales with the size of the change.
- **Q: How much chat-history pollution does this prevent?** Article VII ("one feature, one session") is now binding. Each feature runs in its own fresh chat session; durable state lives in the spec dir, the ledger, and SESSION-MEMORY.md.
- **Q: What's the catch?** Up-front ceremony. The framework trades the "just code it" speed of single-session prompting for traceability and discipline. If you ship a feature a week, this is overkill. If you're trying to ship a *system* over months with AI help, this is what it costs to stay sane.

## What to read next

| If you have… | Read |
|---|---|
| 5 minutes | This file |
| 30 minutes | [README.md](../README.md) + [CONTEXT.md](../CONTEXT.md) |
| A weekend | [FINAL_MERGED_PLAN.md](FINAL_MERGED_PLAN.md) (85KB, 15 sections — the definitive plan) |
| A real second project | [GENERALIZATION_SDD.md](../GENERALIZATION_SDD.md) (portability guide, v0.1) |

## Contact

**Owner:** Rodolfo Lerma (Senior Data Scientist L63, WWIC Central Analytics).
**Status updates:** sprint close blocks in [`exec/sprint-progress.md`](../exec/sprint-progress.md).
**Live dashboard:** `python spec-driven-development/cli/state_builder.py serve` (local, no cloud needed).

---

*This is a working document. Re-share after Sprint 7 close (Gate 1) and again after Sprint 8 close (Gate 2). Each share should update the "When can you use it" section.*
