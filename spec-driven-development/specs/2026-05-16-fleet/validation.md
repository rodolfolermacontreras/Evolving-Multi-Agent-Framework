# Validation Contract: fleet.py

- Date: 2026-05-16
- Spec: `spec-driven-development/specs/2026-05-16-fleet/spec.md`

## Automated tests

- [x] `test_dispatch_inserts_row_and_writes_packet` -- proves AC1
- [x] `test_mark_outcome_updates_row` -- proves AC2
- [x] `test_mark_outcome_unknown_id_fails_cleanly` -- proves AC2 (edge)
- [x] `test_status_lists_in_flight_only` -- proves AC3
- [x] `test_status_empty_message` -- proves AC3 (edge)
- [x] `test_list_by_pi_and_feature` -- proves AC4
- [x] `test_dispatch_unknown_agent_fails` -- proves AC5
- [x] `test_packet_contains_required_fields` -- proves AC6
- [x] `test_help_shows_all_subcommands` -- proves AC7
- [x] `test_runtime_imports_are_stdlib_plus_local_only` -- proves AC8

## Manual checks

- [x] `python spec-driven-development/cli/fleet.py --help` exits 0 with all 4 subcommands listed.
- [x] `python spec-driven-development/cli/fleet.py status` against the real `fleet.db` works (initially "no in-flight", then populated, then closed via mark-outcome).

## Definition of done

Implementation merge-ready when all automated tests pass, all manual checks confirmed, no debug prints remain, and this contract has zero unchecked items.
