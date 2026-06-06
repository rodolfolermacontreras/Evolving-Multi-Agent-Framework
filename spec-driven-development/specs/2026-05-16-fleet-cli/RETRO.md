---
id: SDD-20260516FLEE-retro
type: retro
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-16-fleet-cli
---

# Retro: Fleet CLI (SDD-003)

- Date: 2026-05-16
- Feature: `spec-driven-development/specs/2026-05-16-fleet-cli/`
- Facilitator: Developer (dispatch retro-closure T-001)

---

## What worked

1. **Reusing ledger_cli.py eliminated SQL duplication.** `record_dispatch` and `mark_outcome` were called directly, so fleet.py never contained a single raw SQL string. This kept the data-access layer in one place and let fleet.py focus on CLI orchestration.
2. **Batch dispatch with pre-validation prevented partial writes.** Validating all task IDs and agent references before writing any ledger rows meant a single bad input did not leave the database in an inconsistent state.
3. **The brief renderer produced clean Markdown.** Generating agent-brief-style output from parsed task data gave dispatchers a readable artifact without manual formatting.
4. **Two table-format parser for tasks.md handled both pilot and template layouts.** This avoided a brittle assumption about which format a spec author would use.

## What did not work as smoothly

1. **Argparse subcommand wiring is repetitive.** dispatch, mark, and status each needed similar boilerplate. A small shared helper for common argument patterns (--db, --pi, --sprint) would reduce copy-paste across CLI modules.
2. **tasks.md parsing relies on Markdown table conventions that are not formally validated.** A malformed table silently produces empty results rather than a clear error. The framework should consider a schema-lint pass on lifecycle artifacts.
3. **No integration test exercises the full dispatch-then-mark-then-status pipeline.** Unit tests cover each subcommand in isolation, but the end-to-end flow is only tested manually.

## Framework change candidates filed

- LESSON candidate: Extract a shared argparse base for common CLI flags (--db, --output, --pi, --sprint) to reduce boilerplate across fleet, qa, retro, and future CLI tools.
- LESSON candidate: Add a lifecycle-artifact schema lint step that catches malformed tasks.md tables before dispatch tries to parse them.
- LESSON candidate: Define a convention for integration-level CLI tests that chain subcommands against a temporary ledger.

## Honest assessment

Fleet CLI delivered its three subcommands cleanly because it delegated data access to the ledger layer and kept each subcommand focused on a single responsibility. The main friction was boilerplate: argparse setup, path resolution, and output formatting followed the same shape in every subcommand. That repetition is tolerable at three CLI modules but will become a maintenance drag as more tools are added. The tasks.md parser works but needs defensive validation before it can be trusted with arbitrary spec-author input.
