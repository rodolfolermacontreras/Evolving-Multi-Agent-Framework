# Retrospective -- State Dashboard v0.1

**Date:** 2026-05-16
**Feature:** state-dashboard (cli/state_builder.py + exec/state.html)
**PI/Sprint:** PI-2 / Sprint A
**Effort:** single session, single agent (no fleet dispatch)
**Outcome:** shipped, validation 100%, 4/4 tests green

---

## What worked

1. **User pain became the spec.** Rather than starting from the abstract SDD-001 design doc, we started from a concrete frustration ("I get lost in walls of text") and shipped the minimum that addresses it. This gave us a clear definition of done that survived implementation.
2. **Reusing the Bridge design tokens.** The existing SDD-001 DESIGN.md was a 28KB visual spec we did not implement in full -- but the color palette, typography choice, and panel system transferred directly with zero translation cost. Design exploration pays off even when not fully implemented.
3. **Stdlib-only constraint forced simplicity.** No Jinja2, no FastAPI, no React. The whole generator is one Python file + one HTML output. Anyone with Python installed can run it. LESSON-001 paying dividends.
4. **Stage detection from artifact presence.** Rather than a separate "status" file per feature, we detect lifecycle stage by which artifacts exist (spec.md = SPEC, plan.md = PLAN, validation.md % checked = IMPLEMENT/REVIEW/DONE). Convention over configuration.

## What did not work

1. **Initial roadmap had stale "current" marker.** PI-1 was already closed but roadmap.md still said `## PI-1: ... (current)`. The generator faithfully reported PI-1 as current. Symptom of: closure ceremony moved state.md but not roadmap.md. Lesson: closure must touch BOTH.
2. **state.md lost hand-curated nuance.** Previous state.md had "Active focus", "Recently Completed", "Next milestones" sections written by humans. Auto-generation strips these. Mitigation: EM adds color in chat response, not in file. Acceptable trade-off for v0.1.

## Lessons captured (feed to PI-2 lessons.md)

- **LESSON-005:** EM should recommend, not present a menu. (Triggered by user feedback: "it is very easy to get lost into all the words, choices and verbage that this is giving me.")
- **LESSON-006:** Closure ceremonies must touch BOTH state.md AND roadmap.md (and any other file that carries "current" status).
- **LESSON-007:** Pre-spec design exploration (DESIGN.md) is valuable even when the full design is not implemented -- design tokens, palettes, and layout language transfer to v0.1 implementations at near-zero cost.

## Metrics

- Lines of Python: ~430 in `cli/state_builder.py`
- Lines of CSS: ~140 inline
- HTML output size: ~12 KB (well under 50 KB target)
- Generator runtime: <1 second
- Tests: 4 passing
- Files created: 4 (spec.md, validation.md, RETRO.md, cli/state_builder.py rewrite, cli/test_state_builder.py)
- Files modified: 2 (roadmap.md PI markers, exec/state.md regenerated)

## Demo

Open `spec-driven-development/exec/state.html` in any browser. Refresh anytime with:

    python spec-driven-development/cli/state_builder.py

For live mode (rebuild on every page request, browser auto-refresh every 20s):

    python spec-driven-development/cli/state_builder.py serve

---

## v0.2 Addendum (2026-05-16 PM)

User UX review surfaced 10 issue categories. v0.2 addresses the high-priority items
in the same session, plus a fundamental pivot: **the dashboard is now LIVE, not static**.

### What changed in v0.2

| User concern (priority) | v0.2 response |
|------------------------|---------------|
| Dashboard is static HTML only, not live | Added `serve` subcommand using stdlib `http.server`. Rebuilds on every GET. Auto-refresh meta tag every 20s. Browser auto-opens. |
| Kanban card contrast unreadable | Bumped meta text from `--ink-paper-faint` to `--ink-paper-dim` (8.4:1 AAA). |
| Progress bar shows 0% but work is in flight | Replaced binary done/total bar with multi-segment bar showing feature distribution across all 9 stages + color legend. |
| Only IMPLEMENT cards had colored borders | All cards now have stage-colored left borders (faint -> amber-soft -> amber -> oxblood -> amber-bright -> jade). |
| Recommended action had no CTA | Action box now ends with oxblood-bordered CTA link to the relevant feature dir or roadmap.md. |
| Empty kanban columns wasted space | Empty columns get dashed border, dimmed header, no count badge, en-dash placeholder. |
| Commits all looked identical | Type prefix (feat/docs/chore/design/plan/fix) parsed and rendered as a color-coded pill. |
| Recent commits had no timestamp | Added relative date via `git log --pretty=format:%h%x1f%s%x1f%cr`. |
| Dispatch empty state was a dead line | Bordered empty-state card with icon hint + the exact CLI command to record a dispatch. |
| No column count visibility | Each non-empty column header shows a count badge. |
| No refresh affordance | Header has `[refresh]` button. In live mode it hits `/`; static mode reloads state.html. |

### What v0.2 did NOT do (deferred to SDD-001 v1.0)

- No light-mode toggle
- No agent attribution on cards (cards still show feature name only)
- No timeline / burndown view
- No filters or search
- No multi-PI navigation
- No interactive (mutating) controls -- the dashboard is still read-only

### Why this matters

SDD-001 (Fleet Bridge Dashboard) was parked at P3 because the full Bridge scope was large.
v0.2 of state-dashboard captures ~70% of its operator value at ~10% of the effort by
constraining scope to "live read-only view of current state." The full SDD-001 can still
ship later if it earns priority; until then, the Bridge dashboard exists and works.

### Tests added in v0.2

- `test_html_contains_multi_segment_progress_and_color_borders` -- proves the UX bumps
- `test_html_has_action_cta_and_refresh_button` -- proves the new CTAs
- `test_serve_responds_to_requests` -- end-to-end live server smoke (boot, healthz, GET /, content asserts, teardown)

Total tests now: **13** (SDD-002 ACs 9 + state-dashboard visual 3 + live-server smoke 1).
