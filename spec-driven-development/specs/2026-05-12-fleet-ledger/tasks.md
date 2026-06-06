---
id: SDD-20260512FLEE-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-12-fleet-ledger
---

# Task List: Fleet Ledger v0.1

- Spec Reference: `spec-driven-development/specs/2026-05-12-fleet-ledger/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-05-12-fleet-ledger/plan.md`
- Task ID Format: `T-001` through `T-008`
- Owner: Agent INDIA

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Tag | Description | File Scope | Acceptance Test / Validation Link | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-----|-------------|------------|-----------------------------------|----------------|------|-----------------|-------------------------|--------|
| T-001 | [S] | Write schema and CLI pytest tests first (red). | `ledger/test_ledger.py` | Automated Tests checkboxes 1-6 | M | None | AFK | No | done |
| T-002 | [S] | Implement SQLite schema with idempotent DDL. | `ledger/schema.sql` | `test_init_creates_schema_objects` | S | T-001 | AFK | No | done |
| T-003 | [S] | Implement idempotent initializer with `--db PATH`. | `ledger/init_ledger.py`, `ledger/__init__.py` | `test_init_is_idempotent_and_preserves_rows`; Manual init help check | S | T-002 | AFK | No | done |
| T-004 | [S] | Implement record/list dispatch CLI behavior. | `ledger/ledger_cli.py` | `test_record_dispatch_then_list_pi_round_trip`; Manual CLI help check | M | T-003 | AFK | No | done |
| T-005 | [S] | Implement decision, outcome, feature, and summary CLI behavior. | `ledger/ledger_cli.py` | `test_mark_outcome_updates_existing_dispatch`; `test_summary_counts_by_outcome_role_and_pi` | M | T-004 | AFK | No | done |
| T-006 | [S] | Run automated tests, initialize empty `fleet.db`, and complete manual smoke checks. | `ledger/fleet.db`, `validation.md` | All Validation Contract checkboxes | S | T-005 | AFK | No | done |
| T-007 | [P] | Capture clarification log and feature retro. | `clarification-log.md`, `RETRO.md` | Lifecycle artifact existence check | S | T-006 | AFK | Yes | done |
| T-008 | [P] | Seed PI-1 lessons from the pilot retro. | `sprints/PI-1/lessons.md` | Lessons content included in final report | S | T-007 | AFK | Yes | done |

## Notes

- T-001 intentionally precedes production code to satisfy Article X and the TDD rule.
- All ledger implementation work is serialized because the files are tightly coupled.
- No task requires HITL inside this pilot because the user pre-approved the v0.1 scope and no external side effects occur.
