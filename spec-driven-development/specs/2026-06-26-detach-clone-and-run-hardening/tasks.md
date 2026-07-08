---
id: SDD-20260626DETACHHARDENING-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-detach-clone-and-run-hardening
---

# TASKS: SDD-045 -- Detach + clone-and-run hardening

- Feature ID: SDD-045
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)
- Implementation slot: **F-36** (these tasks are authored in F-35; NONE executed here)

---

## No Silent Deferral Rule

Every task below MUST end F-36 in state `done` or `blocked` with a written reason. A task may NOT be silently dropped or silently kept if stale. If a task becomes unnecessary, record a DE-xx entry in [`validation.md`](validation.md) explaining why and how the contract still holds (sharpen, never loosen).

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete with evidence
- `blocked` -- cannot proceed (reason required)

## Baseline Block (capture at F-36 start, before any change)

- Tests: **481 passed, 2 skipped** (`python -m pytest spec-driven-development/ --tb=no -q`)
- Schema-lint: **exit 0** (`python spec-driven-development/cli/schema_lint.py`)
- Article X: `TestS1FootprintLockGuard` **PASS** (locked render functions byte-identical)
- Ledger: `git ls-files` currently **lists** `spec-driven-development/ledger/fleet.db` (to be detached)

## Task Breakdown

| Task ID | Description | File Scope | Required Tests | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|----------------|--------|------|------|-------------------------|--------|
| T-045-01 | Replace `initialize_ledger()` empty `touch()` with init from `ledger/schema.sql` (creates correct, 0-row DB; idempotent if DB exists non-empty) | `cli/bootstrap.py` | new test: fresh DB matches schema, 0 dispatch rows (R-3) | S | none | sync | yes | todo |
| T-045-02 | `git rm --cached spec-driven-development/ledger/fleet.db` (stop-tracking; preserve local file) -- **owner-visible, gate at commit** | git index (no file body) | R-1 capture (`git ls-files` empty for fleet.db) | S | T-045-01 | sync | no (owner-visible) | todo |
| T-045-03 | Add `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, `*.db-shm` to `.gitignore` | `.gitignore` | R-2 (.gitignore diff) | S | T-045-02 | sync | yes | todo |
| T-045-04 | Add tracked-`fleet.db` guard (in `origin_lint.py` or `schema_lint.py` outside locked fns; surfaced by doctor) | `cli/origin_lint.py` or `cli/schema_lint.py` | new test: guard fails when fleet.db re-indexed (R-4) | S | T-045-08 | sync | yes | todo |
| T-045-05 | Add `setup` subcommand (py>=3.12 check, venv create, ledger init, hook install, owner config, run lint+tests, green message; idempotent) | `cli/bootstrap.py` | new tests: happy path + idempotency (R-5, R-6) | M | T-045-01, T-045-09 | sync | yes | todo |
| T-045-06 | Add `make setup` Makefile target wrapping `bootstrap.py setup` | `Makefile` | covered by R-5 run | S | T-045-05 | sync | yes | todo |
| T-045-07 | Reduce README quickstart to clone -> setup -> talk-to-EM | `README.md` | R-7 (README diff) | S | T-045-05 | sync | yes | todo |
| T-045-08 | Author `cli/origin_lint.py` (stdlib-only; denylist of personal/origin/`engine.py`/host-path tokens; scans `.github/**`+`constitution/**`; `<!-- example: ... -->` escape; `main(argv)`/`sys.exit`) | `cli/origin_lint.py` | new tests: leak fails (R-10), escape passes (R-11) | M | none | sync | yes | todo |
| T-045-09 | Add `doctor` subcommand aggregating ledger-untracked + schema_lint + governance check + origin_lint + tests into one report; non-zero on any fail | `cli/bootstrap.py` | new tests: green exit 0 + broken exit non-zero (R-8); CI-parity note (R-9) | M | T-045-04, T-045-08, T-045-10 | sync | yes | todo |
| T-045-10 | Author governance-consistency check (RULES.md article range == principles.md article count; version/`last_amended` coherence across 6 constitution files + RULES.md) | `cli/bootstrap.py` (or `cli/governance_check.py`) | new tests: pass + fail-on-13th-article (R-13) | M | none | sync | yes | todo |
| T-045-11 | Apply owner-gated RULES.md fix: "Articles I-X" -> "Articles I-XII" at lines 18 + 202 (optionally bump version 1.1.0->1.2.0); **requires recorded owner approval first** (`amendable_by: human-only`) | `docs/RULES.md` | R-12 (`Select-String "Articles I-X"` empty) | S | T-045-10 | sync | no (owner-gated) | todo |
| T-045-12 | Final verification: full pytest >= 481 passed/2 skipped (grown), schema-lint exit 0, footprint guard PASS, stdlib-only import audit, no constitution edit; record owner approvals (M-2 A-1, M-3 B-3) + pre-push (M-4) | (verification only) | R-15, R-16, R-17 + M-1..M-4 | S | all above | sync | no | todo |

## Notes

- All code tasks are stdlib-only (Article V): `argparse`, `sqlite3`, `pathlib`, `json`, `sys`, `os`, `subprocess`, `re`.
- T-045-02 (detach) and T-045-11 (RULES.md edit) are the two gated tasks: T-045-02 owner-visible, T-045-11 owner-gated. Both stop at owner approval before commit.
- Article X locked render functions and any `constitution/**` file are OUT OF SCOPE for every task.
- A-1 is forward-only stop-tracking; NO history rewrite (BFG/filter-repo) in any task.
