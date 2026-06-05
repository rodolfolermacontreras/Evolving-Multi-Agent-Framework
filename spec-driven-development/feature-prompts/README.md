---
id: feature-prompts-index
type: index
status: active
owner: principal-executive-manager
updated: 2026-06-05
---

# Feature Prompts -- Index

Each file in this folder is a self-contained prompt designed to be **copy-pasted
into a fresh VS Code Copilot Chat session**. One file = one worker session. Pasting
the right prompt into a fresh session is how we keep context clean and avoid
poisoning one feature with another feature's history (Article VII: "one feature,
one session").

The Principal Executive Manager owns this folder. Workers and Principals do not
edit prompts; they execute them.

---

## How to use this folder

1. Open a fresh Copilot Chat session in VS Code (new window, or `Clear` the
   current one).
2. Copy the entire contents of the prompt file into the chat.
3. The session reads the referenced docs, runs the feature, and appends a result
   block to `spec-driven-development/exec/sprint-progress.md`.
4. When the feature is DONE, the next feature in the sprint can start (in a new
   session, again).

The **sprint kickoff prompt** (`SPRINT-##-KICKOFF.prompt.md`) is the lead
session: it loads project state, orders the sprint's features, and either
executes them inline or hands each `F-##` prompt to its own worker session.

---

## Active sprints

### Sprint 4 -- PI-4 / Filesystem Data Contracts (FDC) finish

| Order | File | Owner | Status |
|-------|------|-------|--------|
| 0 | [SPRINT-04-KICKOFF.prompt.md](SPRINT-04-KICKOFF.prompt.md) | Principal Software Developer (lead) | READY |
| 1 | [F-01-fdc-tasks.prompt.md](F-01-fdc-tasks.prompt.md) | Principal Software Developer | READY |
| 2 | [F-02-fdc-implement.prompt.md](F-02-fdc-implement.prompt.md) | Principal Software Developer + workers | READY |

Prerequisite: HEAD at or descended from `ae603c4`, FDC plan + ADR-012 committed,
review conditions closed.

### Sprint 5 -- PI-5 kickoff + Brownfield-portability bundle (SDD-016 + SDD-017)

| Order | File | Owner | Status |
|-------|------|-------|--------|
| 0 | [SPRINT-05-KICKOFF.prompt.md](SPRINT-05-KICKOFF.prompt.md) | Principal Executive Manager (lead) | READY (gated on Sprint 4) |
| 1 | [F-03-pi5-kickoff.prompt.md](F-03-pi5-kickoff.prompt.md) | Principal Product Manager | READY (gated on Sprint 4) |
| 2 | [F-04-symlink-portability-clarify-spec.prompt.md](F-04-symlink-portability-clarify-spec.prompt.md) | Principal Product Manager + Principal Architect | READY (gated on F-03) |
| 3 | [F-05-symlink-portability-implement.prompt.md](F-05-symlink-portability-implement.prompt.md) | Principal Software Developer + workers | READY (gated on F-04) |

Prerequisite: **Sprint 4 must close DONE** before any Sprint 5 feature starts.
Full test suite must be green and FDC must be merged to `master`.

---

## Shared onboarding

Every prompt in this folder begins by pointing the session at
[_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md). That file holds the load-bearing
rules (Articles, test discipline, git workflow, definition of done) so individual
prompts stay short and focused on the feature.

---

## Ledger

Progress is reported, append-only, at
[../exec/sprint-progress.md](../exec/sprint-progress.md). Every completed feature
adds a block: feature ID, owner, date, files changed, test count, notes.

---

## Naming convention

- `SPRINT-##-KICKOFF.prompt.md` -- sprint lead's prompt; numbered by sprint
  sequence across the whole project (Sprint 4 = PI-4 S4, Sprint 5 = PI-5 S1).
- `F-##-{slug}.prompt.md` -- one feature, one session. Numbered sequentially
  across the project (F-01 was the first PI-4 S4 feature). Slugs are
  kebab-case.
- All prompts are markdown with no YAML frontmatter (they are runnable prompts,
  not data-contract artifacts).

---

## Authority

This folder and its file-naming convention were authorized by the project owner
on 2026-06-05, adopting the prompt-per-session pattern from the Day-to-Day Agent
project. New prompt files are authored only by the Executive Manager (or the PM
when decomposing a PI-5 sprint inside F-03). Workers never edit prompts.
