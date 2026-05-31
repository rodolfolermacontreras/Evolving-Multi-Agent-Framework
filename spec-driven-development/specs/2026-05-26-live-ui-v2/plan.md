---
feature: live-ui-v2
status: approved
sprint: PI-4
created: 2026-05-31
author: principal-software-developer
spec: spec.md (approved 2026-05-31, architect review T-007)
design_tokens: DESIGN_TOKENS.md (LOCKED 2026-05-31)
implementation_target: cli/state_builder.py
test_target: cli/test_state_builder.py
---

# Live UI v2 -- Implementation Plan

## 1. Summary

Rewrite the HTML renderer in `cli/state_builder.py` to implement the sprint-first
information architecture defined in the Live UI v2 spec. The v1 "4-zone" layout
(zones A/B/C/D) is replaced with a 7-section priority-ordered layout: Current Sprint,
What Comes Next, WIP Summary, PI Context, Agent Activity (placeholder), Activity Feed,
and Footer. Four new data-layer functions are added. The CSS block is replaced with
design-token-driven styles including responsive breakpoints (1280px desktop, 768px tablet).

The existing `render_markdown()`, `build()`, `serve()`, and `build-index` machinery
are unchanged. All changes are confined to the HTML rendering pipeline.

## 2. Implementation Phases

### Phase 1: Data Layer (new functions)

**Effort:** S (small)
**Scope:** Add four new functions to `state_builder.py` that extract data needed by
the v2 renderer but not currently available.

Functions to add:

1. `load_sprint_table(sdd_root, pi_name) -> list[dict]`
   - Reuses `_discover_sprints(pi_dir)` + `_query_ledger_for_pi(sdd_root, pi)` from the
     existing `build-index` machinery (lines 1369-1455).
   - Returns a merged list: each sprint dict gains `dispatch_count` and `last_outcome` keys.
   - Empty-state: returns `[]` if PI directory or sprints not found.

2. `load_sprint_goal(sdd_root, pi_name, sprint_num) -> str`
   - Reads `docs/Management/PI-{N}/Sprint-{M}-{title}/SPEC.md`.
   - Extracts text under the first `## 1. Sprint Goal` heading (or first `##` heading).
   - Returns the first non-empty paragraph after the heading.
   - Empty-state: returns `"No sprint goal defined"`.

3. `detect_current_sprint(sprints: list[dict]) -> dict | None`
   - Takes the output of `load_sprint_table()`.
   - Returns the first sprint whose status is NOT "DONE" and NOT "Proposed".
   - Falls back to the first sprint if all are DONE or Proposed.
   - Returns `None` if the list is empty.

4. `load_decisions(sdd_root, limit=50) -> list[dict]`
   - Queries the `decisions` table in `ledger/fleet.db`.
   - Returns rows as dicts: `{timestamp, decider, level, description}`.
   - Ordered by timestamp descending, capped at `limit`.
   - Returns `[]` if table does not exist or DB is missing.

**Dependencies:** None. These functions are independent of each other and of the renderer.

**Files modified:**
- `cli/state_builder.py` (add functions after the existing `load_recent_commits()`)
- `cli/test_state_builder.py` (add tests for all four functions)

---

### Phase 2: HTML Renderer Rewrite

**Effort:** M (medium) -- per architect note I-2, this is a full rewrite (~260 lines)
**Scope:** Replace `render_html()` and `HTML_CSS` with the v2 implementation.

Changes:

1. **`HTML_CSS` constant:** Replace entirely with design-token-driven CSS from
   DESIGN_TOKENS.md. Includes:
   - CSS custom properties (`:root` block) -- 11 palette tokens, type scale, spacing scale
   - CSS Grid layout with named areas (topbar/sprint/next/wip/pi/agents/feed/footer)
   - Responsive breakpoint at 1279px (collapse to single column)
   - `<details>`/`<summary>` styles for PI sections (hide disclosure triangle, custom caret)
   - Fade-in animation on `<main>` (300ms)
   - Hover transitions on table rows and feed items (150ms)
   - `prefers-reduced-motion: reduce` gate (all transitions to 0s)
   - Focus indicators: `outline: 2px solid var(--ink-paper); outline-offset: 2px`
   - System monospace font stack (no external fonts)

2. **`render_html()` function:** Complete rewrite. New signature adds parameters for
   sprint data:
   ```python
   def render_html(*, generated_at, pi, features, roster, ledger, commits,
                   next_action, live=False, port=None, all_pis=None,
                   sprint_table=None, current_sprint=None, sprint_goal=None,
                   decisions=None) -> str:
   ```
   Sections rendered (in order):
   - Top bar: `<header role="banner">` with BRIDGE title, PI pills, live pulse, freshness
   - Section 1 -- Current Sprint: sprint name, goal, task status counters (done/in-progress/
     blocked/pending from ledger), blocker list, segmented progress bar
   - Section 2 -- What Comes Next: next action card from `derive_next_action()`, next gate
     (first feature in IMPLEMENT/REVIEW), next sprint (from sprint table)
   - Section 3 -- WIP Summary: feature swim lanes with 9-stage lifecycle bars, overall
     completion %, feature count by stage
   - Section 4 -- PI Context: `<details>`/`<summary>` per PI, current PI expanded, past PIs
     collapsed; sprint table per PI with status, dispatch count, last outcome
   - Section 5 -- Agent Activity (placeholder): fleet summary stats from `load_roster()`,
     "Per-agent real-time visibility planned for PI-5" notice
   - Section 6 -- Activity Feed: merged dispatch + decision + commit feed, capped at 50
     events, 480px max-height scrollable, event type badges (DISPATCH/DECISION/COMMIT)
   - Footer: generation timestamp, "v3.0 (sprint-first)", stdlib badge

3. **Helper functions:** Keep existing helpers (`_pulse`, `_weighted_progress`, `h()`,
   `split_commit_type`, `_stage_short`, `_next_for`). Add:
   - `_render_sprint_status_counters(sdd_root, pi, sprint_num) -> dict` -- queries
     dispatches for done/in-progress/blocked/pending counts
   - `_render_blocker_list(ledger) -> list[dict]` -- extracts top 3 blockers

4. **`build()` function:** Update to call the four new data-layer functions and pass
   their outputs to `render_html()`. Changes are additive (new keyword arguments).

**Dependencies:** Phase 1 must be complete (data-layer functions used by renderer).

**Files modified:**
- `cli/state_builder.py` (rewrite `HTML_CSS`, `render_html()`, update `build()`)
- `cli/test_state_builder.py` (rewrite/extend HTML output tests)

---

### Phase 3: CSS / Responsive / Visual Polish

**Effort:** S (small)
**Scope:** Validate and refine the CSS after the renderer rewrite. This phase handles
the visual fidelity pass -- ensuring the generated HTML matches the mockup.

Work items:

1. Verify all design tokens from DESIGN_TOKENS.md are applied correctly in `HTML_CSS`
2. Test desktop layout (1280px+): two-column grid for next/wip, full-width for others
3. Test tablet layout (768-1279px): single-column stack, swim lane bars scale, PI tabs wrap
4. Verify swim lane stage colors match `STAGE_TONE` mapping to design tokens
5. Verify `<details>`/`<summary>` behavior: current PI expanded, past collapsed
6. Verify hover transitions (150ms on table rows, feed items)
7. Verify fade-in on `<main>` (300ms opacity transition)
8. Verify focus indicators (2px solid, 2px offset) on all interactive elements
9. Verify activity feed max-height 480px with `overflow-y: auto`
10. Verify skip-to-main link (hidden, visible on focus)

**Dependencies:** Phase 2 must be complete.

**Files modified:**
- `cli/state_builder.py` (CSS refinements in `HTML_CSS` only)
- `cli/test_state_builder.py` (add responsive/CSS assertion tests)

---

### Phase 4: Accessibility and Final Polish

**Effort:** S (small)
**Scope:** Accessibility audit, empty-state fallbacks, and final quality pass.

Work items:

1. **Semantic HTML audit:**
   - Every `<section>` has `aria-labelledby` pointing to its `<h2>`
   - Heading hierarchy: single `<h1>` in `<header>`, `<h2>` per section
   - Landmark regions: `<header role="banner">`, `<main role="main">`, `<nav>`, `<footer role="contentinfo">`
   - Activity feed: `role="log"` with `aria-live="off"`
   - PI context: `role="tablist"` / `role="tab"` / `role="tabpanel"` pattern
   - Swim lanes: `aria-label` on each progress bar with text equivalent

2. **Empty-state fallbacks (architect note S-1):**
   - No sprints: "No sprints discovered for {PI}"
   - No sprint goal: "No SPEC.md found for sprint goal"
   - No features: "No features registered yet"
   - No dispatches: "No dispatch activity recorded"
   - No decisions: "No decisions recorded"
   - No commits: "No recent commits"
   - No PIs: "No Program Increments found in roadmap"

3. **`prefers-reduced-motion` verification:** All transitions set to 0s when enabled

4. **Contrast audit:** Verify all text/background combinations against Section 8.1 table

5. **Footer version:** Confirm footer reads "v3.0 (sprint-first)" (architect note S-2)

6. **No JavaScript audit:** `grep -c '<script' state.html` returns 0

7. **No external requests audit:** No CDN fonts, no external CSS, no analytics

**Dependencies:** Phase 3 must be complete.

**Files modified:**
- `cli/state_builder.py` (accessibility attributes, empty-state strings)
- `cli/test_state_builder.py` (accessibility and empty-state tests)

## 3. Dependency Graph

```
Phase 1 (Data Layer)
    |
    v
Phase 2 (HTML Renderer Rewrite)
    |
    v
Phase 3 (CSS / Responsive)
    |
    v
Phase 4 (Accessibility / Polish)
```

All four phases are strictly sequential: each phase depends on the prior phase.
Within Phase 1, the four data-layer functions are independent of each other and
can be implemented in parallel (4 tasks, no file conflicts on tests if split).

## 4. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| `render_html()` rewrite breaks existing `build()` / `serve()` callers | High | Medium | Keep function signature backward-compatible via default `None` for new kwargs; existing callers pass nothing, get v1 behavior until `build()` is updated |
| `decisions` table may not exist in older fleet.db instances | Medium | High | `load_decisions()` wraps in try/except sqlite3.OperationalError; returns `[]` |
| Sprint directory naming may vary across PIs | Medium | Low | Reuse `_SPRINT_DIR_RE` (already proven in build-index); log warnings for unmatched directories |
| CSS rewrite introduces visual regressions in existing zones | High | Medium | Test captures v1 HTML structure assertions; keep v1 rendering available behind a flag until v2 is validated |
| Responsive breakpoint at 1279px does not match all tablet widths | Low | Low | Spec decision (Q5); testing at 768px and 1280px boundaries covers the requirement |
| Test count regression during rewrite | Medium | Medium | Track test baseline before and after; TDD ensures new tests are added before removing old ones |

## 5. Effort Summary

| Phase | Effort | Tasks (est.) | Parallel? |
|-------|--------|-------------|-----------|
| Phase 1: Data Layer | S | 4-5 | Yes (4 functions are independent) |
| Phase 2: HTML Renderer Rewrite | M | 4-5 | No (sequential: CSS, then sections, then build()) |
| Phase 3: CSS / Responsive | S | 2-3 | No (depends on Phase 2) |
| Phase 4: Accessibility / Polish | S | 2-3 | No (depends on Phase 3) |
| **Total** | **M** | **12-16** | -- |

Estimated implementation sprint: 1 sprint (PI-4). The M-sized renderer rewrite is the
critical path. Data-layer work (Phase 1) is straightforward extraction from existing
patterns. CSS and accessibility phases are polish work on top of a working renderer.

## 6. Out of Scope

- Agent Activity full implementation (deferred to PI-5 per spec Section 5.6)
- `agents` table schema in fleet.db (PI-5)
- JavaScript interactivity (spec constraint: stdlib only, no JS)
- Below-768px responsive optimization (spec decision Q5)
- D3 force-directed graph (tracked as SDD-008, requires JS deps)
- Changes to `render_markdown()` or the SDD-002 state.md format
