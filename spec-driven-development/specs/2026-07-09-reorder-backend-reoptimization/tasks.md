---
id: SDD-20260709REOPT-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-07-09
feature: 2026-07-09-reorder-backend-reoptimization
---

# TASKS: SDD-054 -- Backlog reorder -> backend re-optimization

- Feature ID: SDD-054
- Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)

---

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------------------------|--------|
| T-054-01 | [S] | Write failing tests: RICE parse, scored ranking, dependency demotion, move writes artifact + one audit row, consumer order, reoptimize subcommand, BACKLOG untouched | `cli/test_backlog_reorder.py` | AC1-AC6 red before impl | S | None | AFK | No | done |
| T-054-02 | [S] | Implement priority parse + compute_effective_priority + _dependency_correct_order + write/load + reoptimize + effective_priority_order; wire reoptimize into move(); add reoptimize subcommand | `cli/backlog_reorder.py` | AC1-AC6 green | S | T-054-01 | AFK | No | done |
| T-054-03 | [S] | QA closeout: full suite + lints + doctor + Article X lock; check validation REQUIRED items | `specs/2026-07-09-reorder-backend-reoptimization/validation.md` | validation.md all REQUIRED checked | S | T-054-02 | AFK | No | done |

Note: all three tasks are serial (`Fleet Dispatch Eligible: No`) -- they share
`cli/backlog_reorder.py` / `cli/test_backlog_reorder.py`.
