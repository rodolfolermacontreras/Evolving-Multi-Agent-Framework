# Sprint Progress Ledger

Append-only. Each completed feature appends a result block (format defined in
[../feature-prompts/_SHARED_ONBOARDING.md](../feature-prompts/_SHARED_ONBOARDING.md)
section 8).

The latest test baseline lives in the most recent block. **Read from the bottom
up to find current state.**

Maintained by feature workers themselves. The Executive Manager and the
`state_builder.py` CLI consume this file; they do not edit prior entries.

---

## Baseline (2026-06-05, HEAD `ae603c4`)

- Tests passing: **152**
- Current PI: PI-4 (Alpha Release)
- Active sprint: Sprint 4 (Filesystem Data Contracts) -- at `/tasks` gate
- Worktrees: 0
- Origin sync: up to date

---

## Sprint 4 -- PI-4 / Filesystem Data Contracts (FDC) finish

- Sprint kickoff: [../feature-prompts/SPRINT-04-KICKOFF.prompt.md](../feature-prompts/SPRINT-04-KICKOFF.prompt.md)
- Prerequisite: HEAD at or descended from `ae603c4`; FDC plan + ADR-012 committed.
- Sequence: F-01 -> F-02
- Owner: Principal Software Developer (lead)

### F-01 -- fdc-tasks -- DONE

- Date: 2026-06-05
- Owner: Principal Software Developer
- Commits: <pending-sha>
- Files changed: 2
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/tasks.md (new)
  - spec-driven-development/exec/sprint-progress.md (this block)
- Tests: 152 -> 152 (docs-only; no code changes in F-01)
- Validation: tasks.md frontmatter present (id/type/status/owner/updated);
  traceability matrix complete (9 tasks -> R1..R7 + O1..O2 mapped, zero
  orphans); per-task allowed_files/blocked_files scoping recorded (AC-3); no
  locked-function modification implied (AC-4); no third-party dep references
  (AC-5).
- Notes: Decomposed FDC plan into 9 tasks across 5 phases. Sequence:
  T-FDC-01 (schema doc) -> T-FDC-02 (S1 lock guard test, pulled forward as
  tripwire) -> T-FDC-03 (lint extension) -> T-FDC-04 (rollup helpers) ->
  T-FDC-05 (cmd_count handler) -> T-FDC-06 (COMMIT-CONVENTION) -> T-FDC-07
  (opt-in hook) -> T-FDC-08 (backfill) -> T-FDC-09 (validation closeout).
  Lock-guard task = T-FDC-02. Backfill task = T-FDC-08. One deviation
  documented in tasks.md "Frontmatter contract note": AC-1 mandates literal
  `status: locked` in tasks.md frontmatter but the FDC status enum does not
  include `locked` -- T-FDC-08 reconciles during backfill (either change to
  `active` or extend enum). No spec/plan/ADR/validation edits made.
- Next: F-02 ready -- paste F-02-fdc-implement.prompt.md in a fresh session

### F-02 -- fdc-implement -- NOT STARTED

(append block here on completion)

---

## Sprint 5 -- PI-5 kickoff + Brownfield-portability bundle (SDD-016 + SDD-017)

- Sprint kickoff: [../feature-prompts/SPRINT-05-KICKOFF.prompt.md](../feature-prompts/SPRINT-05-KICKOFF.prompt.md)
- Prerequisite: **Sprint 4 closed DONE.** Full suite green. FDC merged.
- Sequence: F-03 -> F-04 -> F-05
- Owner: Principal Executive Manager (lead); PM and Architect for planning;
  SW Dev + workers for implementation.

### F-03 -- pi5-kickoff -- NOT STARTED

(append block here on completion)

### F-04 -- symlink-portability-clarify-spec -- NOT STARTED

(append block here on completion)

### F-05 -- symlink-portability-implement -- NOT STARTED

(append block here on completion)
