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

## v0.2 additions (2026-05-16, post user UX feedback)

- [x] Live server mode: `python state_builder.py serve` starts a local ThreadingHTTPServer on port 8765
- [x] Each GET / triggers a fresh rebuild from artifacts (no stale HTML)
- [x] `/healthz` endpoint returns 200 ok for monitoring
- [x] Browser auto-opens unless `--no-open` is passed
- [x] Page auto-refreshes every 20 seconds via `<meta http-equiv="refresh">`
- [x] Multi-segment PI progress bar shows feature distribution by stage with color legend
- [x] All kanban cards have stage-colored left borders (not just IMPLEMENT)
- [x] Card text contrast bumped: name uses `--ink-paper`, meta uses `--ink-paper-dim`
- [x] Column headers show count badges (e.g., `CLARIFY (1)`)
- [x] Empty kanban columns get dashed border + reduced visual weight
- [x] Recommended next action box has clickable CTA link to the relevant feature dir or roadmap
- [x] Recent commits get color-coded type tags (feat/docs/chore/design/plan/fix)
- [x] Header has `[refresh]` button (live mode: hits `/`; static mode: reloads file)
- [x] Dispatch empty state is a bordered card with hint about how to record one
- [x] Live-server smoke test: `test_serve_responds_to_requests` passes (port bind, healthz, /, content checks)

## Notes

- Auto-detection of current PI works via `(current)` marker in roadmap.md `## PI-N:` headers.
- Stage detection uses validation.md checkbox ratio: 0-79% = IMPLEMENT, 80-99% = REVIEW, 100% + RETRO = DONE.
- `state.md` is now machine-generated; human-curated color (Active focus, etc.) moves to the EM's chat response, not the file.
