# Task List: fleet.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-fleet-cli/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-05-16-fleet-cli/plan.md`
- Task ID Format: `T-{spec-date}-{NNN}` (global default)
- Owner: Principal Software Developer

---

> **Task ID convention:** Inside a date-prefixed feature directory, local short
> IDs `T-NNN` are acceptable.
> Provenance: LESSON-002, source feature `specs/2026-05-12-fleet-ledger/`.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

> **Cross-reference rule:** In the Acceptance Test column, reference the spec's
> AC identifiers rather than restating criteria.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Write test_fleet.py first (red). | `cli/test_fleet.py` | Proves AC1-AC9 | M | None | AFK | No | pending |
| T-002 | [S] | Implement tasks.md parser (parse_tasks_md). | `cli/fleet.py` | Proves AC1, AC7, AC8 | S | T-001 | AFK | No | pending |
| T-003 | [S] | Implement brief renderer (render_brief). | `cli/fleet.py` | Proves AC1, AC4 | S | T-002 | AFK | No | pending |
| T-004 | [S] | Implement dispatch subcommand (eligibility check + ledger write + brief output). | `cli/fleet.py` | Proves AC1, AC2, AC3, AC4, AC7 | M | T-003 | AFK | No | pending |
| T-005 | [S] | Implement mark subcommand (wrap ledger mark-outcome). | `cli/fleet.py` | Proves AC5 | S | T-001 | AFK | No | pending |
| T-006 | [S] | Implement status subcommand (query + format table). | `cli/fleet.py` | Proves AC6 | S | T-001 | AFK | No | pending |
| T-007 | [S] | CLI wiring, --help verification, run all tests + manual checks. | `cli/fleet.py`, `validation.md` | Proves AC9, AC10, all validation checkboxes | S | T-004, T-005, T-006 | AFK | No | pending |

## Notes

- All tasks are serialized because they build on the same file (fleet.py).
- T-001 precedes production code per Article X.
- The dispatch subcommand reuses `ledger_cli.py` record_dispatch; it does NOT duplicate SQL.
- T-005 and T-006 can be done in parallel with T-003/T-004 but are serialized for simplicity in a single-file feature.
