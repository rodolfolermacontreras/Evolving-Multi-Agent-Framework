# RETRO: fleet.py (SDD-003)

- Date: 2026-05-16
- PI/Sprint: PI-2 / Sprint A
- Status: DONE (10/10 automated tests passing, manual checks confirmed, first real dispatch recorded as dispatch #1 in fleet.db)

---

## What worked

- **Reused ledger_cli.py wholesale.** All ledger I/O was already in ledger_cli (record_dispatch, mark_outcome, fetch_dispatches, print_dispatch_table). fleet.py is a thin orchestration layer with packet rendering. No duplication.
- **Best-effort tasks.md scraping.** Regex pulls Description / File Scope / Acceptance from the task row, but everything is overridable via flags. Means a packet is always emit-able even when tasks.md is incomplete.
- **First real dispatch through the system.** Created dispatch #1, packet at `dispatches/PI-2/000001.md`, then marked success. The next dashboard regeneration will show it in "Recently Completed".

## What did not work

- **Windows SQLite + tempdir teardown race.** Tests initially failed because `sqlite3.Connection` keeps the file open until GC, and `TemporaryDirectory.cleanup()` on Windows refuses to delete locked files. Fixed by `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` + `gc.collect()` in tearDown. This is a Python stdlib behavior, not a bug in our code.

## Lesson candidate

- **LESSON-009:** Windows tests that use sqlite3 + TemporaryDirectory must pass `ignore_cleanup_errors=True` and call `gc.collect()` in tearDown, otherwise tests pass logically but fail on tempdir cleanup. Add to `testing-conventions` skill.

## Validation

All 10 automated AC tests green:
```
$ python -m unittest spec-driven-development.cli.test_fleet
..........
Ran 10 tests in ~1.8s
OK
```

Manual checks confirmed via real dispatch round-trip (`dispatch` -> `list` -> `mark-outcome` -> `list` showing outcome=success).
