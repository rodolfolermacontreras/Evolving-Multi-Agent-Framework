# Implementation Plan: Fleet Ledger v0.1

- Spec Reference: `spec-driven-development/specs/2026-05-12-fleet-ledger/spec.md`
- Author: Agent INDIA
- Status: Done
- Last Updated: 2026-05-12

---

## Approach Summary

Use the framework lifecycle on itself: define a full spec, lock a validation contract before implementation, write tests first, implement the minimal stdlib-only SQLite ledger, run automated/manual checks, then capture retro lessons for `/evolve` curation.

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Schema + init script | Spec and validation contract locked | `schema.sql`, `init_ledger.py`, schema/idempotency tests |
| 2 | CLI subcommands | Phase 1 database initialization | `ledger_cli.py`, dispatch/decision/outcome/list/summary tests |
| 3 | Tests, initialized DB, lifecycle closure | Phases 1-2 | Passing pytest suite, committed `fleet.db`, completed `validation.md`, `clarification-log.md`, `RETRO.md`, `sprints/PI-1/lessons.md` |

## Parallel-Safe Tasks

- Draft lifecycle prose artifacts once spec decisions are stable -- Files: `spec-driven-development/specs/2026-05-12-fleet-ledger/*.md`
- Implement tests and code in serialized TDD order -- Files: `spec-driven-development/ledger/*`

## Sequential Tasks

1. Write `spec.md` and `validation.md` before implementation.
2. Write `test_ledger.py` first and confirm the initial red state.
3. Implement `schema.sql` and `init_ledger.py` until schema tests pass.
4. Implement `ledger_cli.py` until CLI behavior tests pass.
5. Initialize `fleet.db`, run manual checks, and update validation checkboxes.
6. Write `clarification-log.md`, `RETRO.md`, and seed `sprints/PI-1/lessons.md`.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Binary `fleet.db` committed with stray test data | Low | Medium | Initialize from schema only after tests; inspect counts before commit. |
| CLI path handling differs across OSes | Medium | Medium | Use `pathlib.Path`; tests use pytest `tmp_path`. |
| Runtime dependency creep | Low | Medium | Keep implementation stdlib-only and add an import scanner test. |
| Lifecycle artifacts become ceremony without feedback | Medium | Medium | Capture concrete retro lessons and seed `lessons.md`. |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | S | Two tables, three indexes, one initializer. |
| 2 | M | Six CLI subcommands with readable output. |
| 3 | M | ~12 tests plus manual checks and retro capture. |

## Validation Criteria

- [x] Automated tests in `spec-driven-development/ledger/test_ledger.py` pass.
- [x] Manual `--help` checks pass for both scripts.
- [x] Default `init_ledger.py` creates and preserves `spec-driven-development/ledger/fleet.db`.
- [x] All required checkboxes in `validation.md` are checked before DONE.
