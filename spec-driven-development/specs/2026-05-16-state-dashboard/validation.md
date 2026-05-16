# Validation Contract -- State Dashboard v0.1

Per Article X: validation criteria written DURING spec, locked at tasks, verified at REVIEW.

This file mirrors the validation contract from `spec.md` so the generator can detect REVIEW/DONE stage from a single file.

- [x] `python spec-driven-development/cli/state_builder.py` exits 0
- [x] Produces `spec-driven-development/exec/state.md`
- [x] Produces `spec-driven-development/exec/state.html`
- [x] HTML is self-contained (no external CSS/JS)
- [x] HTML contains "Recommended next action" section with ONE action + reasoning
- [x] HTML contains "Lifecycle Kanban" section showing all features grouped by stage
- [x] HTML contains "PI-2 Progress" bar with done/total counts
- [x] HTML contains "Fleet Roster" stats (principals, generic, specialist, total)
- [x] HTML contains "Recent Commits" feed (last 10 from git log)
- [x] HTML contains "Dispatch Stream" section (empty-state OK when ledger empty)
- [x] Generator uses pure Python stdlib only (LESSON-001 canonical pattern)
- [x] Smoke tests pass: `python -m unittest spec-driven-development.cli.test_state_builder`
- [x] All 4 smoke tests green
- [x] Tested on Windows PowerShell

## Notes

- Auto-detection of current PI works via `(current)` marker in roadmap.md `## PI-N:` headers.
- Stage detection uses validation.md checkbox ratio: 0-79% = IMPLEMENT, 80-99% = REVIEW, 100% + RETRO = DONE.
- `state.md` is now machine-generated; human-curated color (Active focus, etc.) moves to the EM's chat response, not the file.
