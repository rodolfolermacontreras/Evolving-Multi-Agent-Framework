---
id: SDD-20260709FOVL-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-07-09
feature: 2026-07-09-file-overlap-detector
---

# TASKS: SDD-049 -- File-overlap conflict detector

- Feature ID: SDD-049
- Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)

---

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------------------------|--------|
| T-049-01 | [S] | Write failing tests for parse_file_scope + detect_file_overlaps + dispatch overlap gate | `cli/test_fleet.py` | AC1-AC5 red before impl | S | None | AFK | No | done |
| T-049-02 | [S] | Implement parse_file_scope, detect_file_overlaps, format_overlap_report; wire the pre-dispatch guard + --allow-overlap flag into cmd_dispatch | `cli/fleet.py` | AC1-AC5 green | S | T-049-01 | AFK | No | done |
| T-049-03 | [S] | QA closeout: full suite + lints + doctor + Article X lock; check validation REQUIRED items | `specs/2026-07-09-file-overlap-detector/validation.md` | validation.md all REQUIRED checked | S | T-049-02 | AFK | No | done |

Note: all three tasks are serial (`Fleet Dispatch Eligible: No`) -- they share
`cli/fleet.py` / `cli/test_fleet.py`, exactly the kind of overlap SDD-049 detects.
