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
