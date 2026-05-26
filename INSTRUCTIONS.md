# INSTRUCTIONS — Read Me First

You are an AI agent (Copilot CLI, Claude Code, Cursor, or similar) starting a session in this repository. Read this file first, then follow the order below.

This repo is the **Evolving Multi-Agent Framework** — a portable spec-driven development system. Owner: Rodolfo Lerma. Repo: https://github.com/rodolfolermacontreras/Evolving-Multi-Agent-Framework

---

## Session-start read order

1. **This file** (`INSTRUCTIONS.md`) — entry point.
2. **`.github/copilot-instructions.md`** — full session-start authority: project identity, history, conventions, current state, what is next.
3. **`spec-driven-development/CONTEXT.md`** — shared vocabulary used across the framework.
4. **`spec-driven-development/docs/HIGH_LEVEL_DEV_TRACKER.md`** — bird's-eye operational view: which PI is active, which sprint is in flight, blockers.
5. **`spec-driven-development/docs/Management/PI-N/INDEX.md`** (active PI) — PI-level navigation: sprint list, decisions, what-was-done.
6. **`spec-driven-development/sessions/SESSION-MEMORY.md`** — checkpoint of the most recent working session. Always read the latest one for what shipped, what's open, and the recommended next moves.
7. **`spec-driven-development/constitution/roadmap.md`** — current PI status and tech-debt backlog.

If the user says "get up to speed" or "resume" or "continue", do exactly the above in order, then provide a 5-line status summary and the top 3 next moves drawn from the SESSION-MEMORY.md file.

---

## Where session memory lives

All session checkpoints, strategy memos, and research findings are committed to:

```
spec-driven-development/sessions/
```

Current contents:

| File | Purpose |
|---|---|
| `SESSION-MEMORY.md` | Latest checkpoint — full state, commit chain, what's done, what's next |
| `framework-foundations-strategy.md` | Strategic memo: evolution loops, greenfield/brownfield convergence, SDD+TDD integration |
| `inspiration-repos-research-findings.md` | Synthesis of research on Spec-Kit, Matt Pocock, DeepLearning.AI SDD course, sc-spec |

When ending a session that another session will pick up, **save a new or updated `SESSION-MEMORY.md` in this folder and commit it.** Use the `handoff` skill (`.github/skills/operational/handoff/SKILL.md`) for the format.

---

## Quick reference for new sessions

### Find current state
```powershell
cd C:\Training\Projects\Evolving-Multi-Agent-Framework
git pull
git log --oneline -10
```

### View the visual cheat sheet
```powershell
start spec-driven-development\docs\CHEAT-SHEET.html
```

### Confirm the dogfood pilot still works
```powershell
python -m pytest spec-driven-development\ledger\test_ledger.py -v
```

### Try the bootstrap CLI
```powershell
python spec-driven-development\cli\bootstrap.py --help
```

---

## Conventions (non-negotiable)

- No emojis anywhere — code, docs, commits.
- Dates always `YYYY-MM-DD`.
- Commits: `type: short description` (e.g. `feat:`, `docs:`, `chore:`, `fix:`).
- Co-author trailer on commits made by AI agents:
  ```
  Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
  ```
- The 10 binding articles in `spec-driven-development/constitution/principles.md` are immutable without an ADR + `/constitution` semver bump.

---

## The framework in 30 seconds

One human + 4 Principal AI agents (Executive Manager, Product Manager, Architect, Software Developer) + a fleet of generic worker agents (Developer, UX Designer, QA Engineer, Data Scientist, plus any role created on demand via `/hire`). The human talks to the **Executive Manager** first, always. It either answers or routes to the right Principal, gets the answer, and synthesizes back at executive register.

Lifecycle: `IDEA → BACKLOG → CLARIFY → SPEC → PLAN → TASKS → IMPLEMENT → REVIEW → DONE → /replan → (optional /evolve)`.

For the full picture see the visual workflow diagram in `spec-driven-development/docs/CHEAT-SHEET.html`.
