# Retro: Retro CLI (SDD-005)

- Date: 2026-05-16
- Feature: `spec-driven-development/specs/2026-05-16-retro-cli/`
- Facilitator: Developer (dispatch retro-closure T-003)

---

## What worked

1. **Querying fleet.db for dispatch metrics was straightforward.** Total dispatches, success/fail/blocked counts, and unique agent/feature counts came from simple SQL aggregations. The ledger schema was well-suited for retrospective queries without any schema changes.
2. **Scanning specs/ for DONE features reused the validation.md checkbox logic.** The same completion-detection approach from qa.py applied here, reinforcing the convention that validation.md checkboxes are the source of truth for feature status.
3. **lessons.md parser extracts lesson entries and statuses reliably.** The Markdown format is simple enough that regex-based parsing works without a full Markdown AST.
4. **stdout-by-default with --output flag is the right UX.** Developers can pipe output or redirect without learning a new flag, and --output serves automated workflows that need a file artifact.

## What did not work as smoothly

1. **The retro report is plain text only.** No structured output format (JSON, YAML) is available for downstream tools that might want to aggregate retro data across sprints or PIs. Adding --format json would make retro data composable.
2. **lessons.md parsing assumes a single file per sprint.** If lessons are split across multiple files or nested directories, the scanner misses them. The convention works today but may not scale.
3. **No date filtering on ledger queries.** The retro covers all dispatches in the database rather than scoping to a specific sprint or date range. A --since / --sprint filter would make the report more useful for targeted retrospectives.

## Framework change candidates filed

- LESSON candidate: Add --format json to retro.py so retro metrics can feed dashboards or trend analysis tools.
- LESSON candidate: Add --since or --sprint filters to scope retro queries to a specific time window or sprint boundary.
- LESSON candidate: Clarify the convention for lessons.md location and format -- single file per sprint vs. per-PI vs. global -- before the second PI creates ambiguity.

## Honest assessment

Retro CLI closes the lifecycle loop: dispatches go out through fleet.py, quality is checked by qa.py, and retro.py summarizes what happened. The tool works well for its initial scope -- generating a human-readable retrospective from ledger data and artifact scans. The main gap is composability: the output is prose, not data, so automated trend tracking will require either a structured output mode or a separate analytics tool. For a first implementation, prose is the right default because retros are read by humans. The structured mode should come when there is a real consumer for it.
