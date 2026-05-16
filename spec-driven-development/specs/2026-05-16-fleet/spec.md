---
feature: fleet
status: implementing
created: 2026-05-16
pi: PI-2
sprint: A
priority: P2
spec_id: SDD-003
---

# Feature Spec: cli/fleet.py (SDD-003)

- Date: 2026-05-16
- Author: Principal Software Developer (routed by Executive Manager)

---

## Problem Statement

The framework's task dispatch workflow today is fully manual: a human (or the Software Developer in chat) hand-writes a dispatch brief, sends it to a worker, and remembers to record the dispatch in fleet.db afterwards. This is error-prone (dispatches forgotten, packets inconsistent) and breaks the dashboard's "Recently Completed" + "Blockers" sections (state_builder reads from fleet.db, which stays empty).

## Proposed Solution

Implement `cli/fleet.py` as a stdlib-only Python CLI that composes dispatch packets from feature artifacts and atomically inserts a ledger row. Reuses existing helpers in `ledger/ledger_cli.py` (no duplication).

Subcommands:

- `dispatch` -- emit a markdown dispatch packet AND record the dispatch in fleet.db in one call.
- `mark-outcome` -- close a dispatch by id with outcome success | failed | blocked.
- `status` -- list dispatches with no outcome (i.e. in-flight + blocked candidates).
- `list` -- list dispatches scoped by PI and/or feature, reusing ledger_cli queries.

Dispatch packets are written to `spec-driven-development/dispatches/<pi>/<dispatch-id>.md` using `templates/agent-brief.md` as the template (variable substitution).

## Acceptance Criteria

1. `python fleet.py dispatch --task T-001 --agent developer-general --feature specs/<dir>/ --pi PI-2 --sprint A --title "..."` exits 0 and:
   - inserts one new row in `fleet.db` dispatches table with all required columns populated;
   - writes a packet markdown file at `dispatches/<pi>/<dispatch-id>.md`;
   - prints the new dispatch id and the packet path to stdout.
2. `python fleet.py mark-outcome <id> --outcome success` exits 0 and updates the dispatch row's outcome and outcome_at columns; updating an unknown id exits non-zero with a clear error message.
3. `python fleet.py status` prints a table of dispatches where outcome IS NULL, ordered oldest first; with no in-flight dispatches it prints "no in-flight dispatches" and exits 0.
4. `python fleet.py list --pi PI-2` prints all dispatches for the named PI (reuses ledger_cli.fetch_dispatches); accepts `--feature` to filter by feature_dir.
5. `python fleet.py dispatch` requires a known agent id present in `roster/agents.json`; unknown agent ids fail loudly with the list of valid ids.
6. The generated packet markdown contains: the task id and title, the feature dir, the resolved agent role, the allowed-files scope (derived from the tasks.md File Scope cell when available), the acceptance reference, and the verification command.
7. `python fleet.py --help` shows all four subcommands.
8. Implementation imports only Python stdlib + the local `ledger_cli` module (no third-party deps).
9. All automated tests in `cli/test_fleet.py` pass against a tmp_path seeded fixture.

## Affected Modules

- Files:
  - `spec-driven-development/cli/fleet.py` (replace scaffold)
  - `spec-driven-development/cli/test_fleet.py` (new)
  - `spec-driven-development/dispatches/` (new directory; .gitkeep)
- Reuses:
  - `spec-driven-development/ledger/ledger_cli.py` (record_dispatch, mark_outcome, fetch_dispatches)
  - `spec-driven-development/ledger/init_ledger.py`

## Data Model Changes

None. Uses the existing `dispatches` table schema.

## Out of Scope

- Auto-launching worker processes (this is Phase 2, future PI).
- Parallel dispatch coordination / conflict detection (this stays in `/fleet` slash command for now).
- Modifying the ledger schema.
- Worker-side packet consumption (the worker reads the markdown and acts on it).

## Validation Contract

See sibling `validation.md`.
