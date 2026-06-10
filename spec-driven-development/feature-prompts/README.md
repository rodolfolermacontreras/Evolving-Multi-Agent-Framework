---
id: feature-prompts-index
type: index
status: active
owner: principal-executive-manager
updated: 2026-06-10
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

### Sprint 6 -- PI-5 Sprint 2 / Anti-Conflict Gates + Carry-Over (SDD-019 + SDD-020 + SDD-027)

| Order | File | Owner | Status |
|-------|------|-------|--------|
| 0 | [SPRINT-06-KICKOFF.prompt.md](SPRINT-06-KICKOFF.prompt.md) | Principal Executive Manager (lead) | READY (gated on Sprint 5 close + audit backlog + spec scaffolds) |
| 1 | [F-06-sprint6-clarify.prompt.md](F-06-sprint6-clarify.prompt.md) | Principal Product Manager + Principal Architect | READY (gated on SPRINT-06 kickoff prereqs) |
| 2 | [F-07-sprint6-plan-tasks.prompt.md](F-07-sprint6-plan-tasks.prompt.md) | Principal Architect + Principal Software Developer | READY (gated on F-06) |
| 3 | [F-08-sprint6-implement.prompt.md](F-08-sprint6-implement.prompt.md) | Principal Software Developer + workers | READY (gated on F-07) |

Prerequisite: **Sprint 5 must close DONE** (commit `3cb7dea`), the BACKLOG
audit follow-ups SDD-027..031 must be filed (commit `17e7cc0`), and the three
Sprint 6 spec dirs must be scaffolded with CLARIFY questions (commit
`d08cd73`). F-06, F-07, F-08 run sequentially in three fresh sessions. SDD-019
is a constitutional-amendment candidate; SDD-027 is an Article X amendment
candidate (handled as a normal spec first per owner direction 2026-06-07).

### Sprint 7 -- PI-5 Sprint 3 / Sprint 6 Completion + UI Lifecycle Variant (SDD-032 + SDD-018)

| Order | File | Owner | Status |
|-------|------|-------|--------|
| 0 | [SPRINT-07-KICKOFF.prompt.md](SPRINT-07-KICKOFF.prompt.md) | Principal Executive Manager (lead) | READY (gated on Sprint 6 close + ratification + SDD-032 scaffold) |
| 1 | [F-09-sprint7-completion.prompt.md](F-09-sprint7-completion.prompt.md) | Principal Software Developer + Developer worker | READY (gated on SPRINT-07 kickoff prereqs) |
| 2 | [F-10-sprint7-sdd018-design.prompt.md](F-10-sprint7-sdd018-design.prompt.md) | Principal Product Manager + Principal Architect | READY (gated on F-09 close) |
| 3 | [F-11-sprint7-sdd018-implement.prompt.md](F-11-sprint7-sdd018-implement.prompt.md) | Principal Software Developer + workers | READY (gated on F-10 close) |

Prerequisite: **Sprint 6 must close DONE** (close commit `4a6941c` plus
owner ratification commit `6c70e30`, both 2026-06-08), the BACKLOG entries
SDD-019/020/027 must read DONE-WITH-DEFERRED and SDD-032 (P1, F-09) +
SDD-033 (P3, unscheduled) must be filed at commit `6c70e30`, and the
SDD-032 spec dir at `specs/2026-06-09-sprint-6-completion/` must be
scaffolded with all four artifacts LOCKED at scaffold (commit `b005e66`).
F-09, F-10, F-11 run sequentially in three fresh sessions. F-09 is
implementation-only (no CLARIFY -- spec already locked). F-10 scaffolds
the SDD-018 spec dir from scratch and runs a heavy CLARIFY round; SDD-018
may require an Article X amendment or a new Article XII (handled via F-10
ADR drafting if confirmed). Per owner direction 2026-06-08 (Option 3
hybrid), **no REQUIRED-item deferral is permitted from Sprint 7 close**,
and Sprint 7 close requires **explicit owner approval before any close
commit is pushed**.

### Sprint 10 -- PI-6 Sprint 1 / Dashboard parser fix + auto-refresh (SDD-040)

| Order | File | Owner | Status |
|-------|------|-------|--------|
| 0 | [SPRINT-10-KICKOFF.prompt.md](SPRINT-10-KICKOFF.prompt.md) | Principal Executive Manager (lead) | READY (gated on Sprint 10 HARD PREREQUISITE) |

Prerequisite: **PI-5 must be closed at commit `8417818`** (PI-5 CLOSED /
DONE-WITH-CARRYOVER 2026-06-09), **PI-6 must be launched** via
[`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md), tests at
or above 337, schema lint clean, **SDD-040 filed in BACKLOG under "PI-6
Dashboard Bundle (filed 2026-06-10)"** as P1 allocated to PI-6 Sprint 10,
SDD-036/037/038 still present in BACKLOG as PI-6 candidates, and **owner
approval recorded** for Sprint 10 start. F-21 (CLARIFY/SPEC/PLAN/TASKS),
F-22 (IMPLEMENT + QA), and F-23 (sprint close + SPRINT-11 kickoff
authoring) run sequentially. SDD-040 has a stdlib-only constraint
(Article V): no `watchdog`, no `flask` -- auto-refresh must use polling,
on-request refresh, stdlib file-mtime sweep, or Server-Sent Events.

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
