---
feature: live-ui-v2
status: approved
sprint: PI-4
created: 2026-05-31
author: principal-software-developer
plan: plan.md
spec: spec.md
total_tasks: 14
parallel_batches: 5
---

# Live UI v2 -- Task List

## Batch 1: Data Layer Tests (Phase 1, parallelizable)

All four tasks modify different test sections and the same source file, but the test
functions are independent. The source-file functions are added in separate blocks.
Mark [P] for parallel dispatch with one constraint: each worker appends to
`test_state_builder.py` and adds a function to `state_builder.py`. To avoid merge
conflicts, dispatch as 2 pairs: (T-001 + T-002) then (T-003 + T-004).

---

### Task T-001: Test and implement `load_sprint_table()`

**Story:** US-PI4-01: As a dashboard user, I see the sprint table for each PI.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** NONE

#### Description

Write tests for a new `load_sprint_table(sdd_root, pi_name)` function, then implement it.
The function reuses `_discover_sprints(pi_dir)` and `_query_ledger_for_pi(sdd_root, pi)`
from the existing build-index machinery (lines 1369-1455). It merges the results: each
sprint dict gains `dispatch_count` (int) and `last_outcome` (str) keys from the ledger data.

Returns `[]` if the PI directory does not exist or contains no sprint directories.

The PI directory path is: `sdd_root / "docs" / "Management" / pi_name`.

#### Acceptance Criteria

- [ ] Test: returns empty list when PI directory does not exist
- [ ] Test: returns sprint dicts with `dispatch_count` and `last_outcome` when sprints and ledger data exist
- [ ] Test: returns sprints with `dispatch_count=0` and `last_outcome="--"` when no ledger data for a sprint
- [ ] Test: sprints are sorted by `num` ascending
- [ ] Implementation: function exists and is importable
- [ ] All existing tests still pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "sprint_table" -v --tb=short
```

---

### Task T-002: Test and implement `load_sprint_goal()`

**Story:** US-PI4-02: As a dashboard user, I see the current sprint's goal text.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** NONE

#### Description

Write tests for a new `load_sprint_goal(sdd_root, pi_name, sprint_num)` function, then
implement it. The function reads `docs/Management/PI-{N}/Sprint-{M}-{title}/SPEC.md` and
extracts text under the first `## 1. Sprint Goal` heading (or the first `##` heading if
that exact heading is not found). Returns the first non-empty paragraph after the heading.

Returns `"No sprint goal defined"` if the file does not exist or no heading is found.

The sprint directory is discovered by scanning `docs/Management/{pi_name}/` for directories
matching `_SPRINT_DIR_RE` (existing regex, line 1364) where the sprint number matches
`sprint_num`.

#### Acceptance Criteria

- [ ] Test: returns fallback string when SPEC.md does not exist
- [ ] Test: returns goal text from `## 1. Sprint Goal` heading
- [ ] Test: returns first paragraph after the first `##` heading if `## 1. Sprint Goal` not found
- [ ] Test: returns fallback when SPEC.md exists but has no headings
- [ ] Implementation: function exists and is importable
- [ ] All existing tests still pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "sprint_goal" -v --tb=short
```

---

### Task T-003: Test and implement `detect_current_sprint()`

**Story:** US-PI4-03: As a dashboard user, the current sprint is auto-detected.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** NONE

#### Description

Write tests for a new `detect_current_sprint(sprints)` function, then implement it.
Takes a list of sprint dicts (as returned by `load_sprint_table()`). Returns the first
sprint whose `status` is NOT `"DONE"` and NOT `"Proposed"`. Falls back to the first sprint
if all are DONE or Proposed. Returns `None` if the list is empty.

#### Acceptance Criteria

- [ ] Test: returns `None` for empty list
- [ ] Test: returns first non-DONE, non-Proposed sprint
- [ ] Test: returns first sprint when all are DONE
- [ ] Test: returns first sprint when all are Proposed
- [ ] Test: skips DONE sprints and returns first In-Flight sprint
- [ ] Implementation: function exists and is importable
- [ ] All existing tests still pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "current_sprint" -v --tb=short
```

---

### Task T-004: Test and implement `load_decisions()`

**Story:** US-PI4-04: As a dashboard user, I see decision events in the activity feed.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** NONE

#### Description

Write tests for a new `load_decisions(sdd_root, limit=50)` function, then implement it.
Queries the `decisions` table in `ledger/fleet.db`. Returns rows as dicts with keys:
`timestamp`, `decider`, `level`, `description`. Ordered by timestamp descending, capped
at `limit`.

Returns `[]` if the database file does not exist, the `decisions` table does not exist
(catch `sqlite3.OperationalError`), or the table is empty.

#### Acceptance Criteria

- [ ] Test: returns empty list when fleet.db does not exist
- [ ] Test: returns empty list when `decisions` table does not exist
- [ ] Test: returns decision dicts ordered by timestamp descending
- [ ] Test: respects `limit` parameter
- [ ] Test: default limit is 50
- [ ] Implementation: function exists and is importable
- [ ] All existing tests still pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "decisions" -v --tb=short
```

---

**CHECKPOINT 1:** Run full test suite. Verify test count increased by at least 16.
All existing tests pass. Four new functions are importable.

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
```

---

## Batch 2: CSS Rewrite (Phase 2, sequential)

### Task T-005: Replace `HTML_CSS` constant with v2 design-token CSS

**Story:** US-PI4-05: The dashboard uses the approved design token system.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** M
**Files:** `cli/state_builder.py`
**Depends on:** NONE (CSS constant is independent of data layer)

#### Description

Replace the entire `HTML_CSS` string constant in `state_builder.py` (lines 561-873) with
v2 CSS derived from DESIGN_TOKENS.md. The new CSS must include:

1. `:root` block with all design tokens (palette, type scale, spacing, motion)
2. CSS Grid layout using named areas: topbar, sprint, next, wip, pi, agents, feed, footer
3. Desktop grid: `grid-template-columns: 1fr 1fr` (next + wip side-by-side)
4. Tablet media query at `max-width: 1279px`: single-column stack
5. `<details>`/`<summary>` styles: hide disclosure marker, custom `::before` caret
6. Fade-in on `<main>`: `opacity 0->1, 300ms ease`
7. Hover transitions: `background-color 150ms ease` on table rows and feed items
8. `prefers-reduced-motion: reduce` gate: `transition-duration: 0s`
9. Focus indicators: `outline: 2px solid var(--ink-paper); outline-offset: 2px`
10. Skip-to-main link: visually hidden, visible on focus
11. Activity feed: `max-height: 480px; overflow-y: auto`
12. System monospace font stack (no external fonts)
13. Footer: 32px height

No changes to `render_html()` in this task. The CSS is a self-contained string constant.

#### Acceptance Criteria

- [ ] `HTML_CSS` contains all 11 palette tokens from DESIGN_TOKENS.md
- [ ] CSS Grid uses named areas matching spec Section 4.1
- [ ] Media query breakpoint at 1279px with single-column fallback
- [ ] `<details>`/`<summary>` styles present
- [ ] `prefers-reduced-motion` media query present
- [ ] Focus indicator styles present (no `outline: none` anywhere)
- [ ] No external font references (no `@import`, no CDN URLs)
- [ ] All existing tests still pass (CSS change does not break HTML structure tests)

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
```

---

**CHECKPOINT 2:** Run full test suite. Verify no regressions from CSS replacement.

---

## Batch 3: HTML Renderer Rewrite (Phase 2, sequential)

### Task T-006: Rewrite `render_html()` -- Top Bar and Current Sprint sections

**Story:** US-PI4-06: The dashboard opens with sprint-first information architecture.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** M
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** T-001, T-002, T-003, T-005

#### Description

Begin the `render_html()` rewrite. Update the function signature to accept new kwargs
(`sprint_table`, `current_sprint`, `sprint_goal`, `decisions`), all defaulting to `None`.

Implement the HTML generation for:

1. **Document shell:** `<!doctype html>`, `<html lang="en">`, `<head>` with meta tags,
   CSP headers in meta, `<style>` block (from `HTML_CSS`), `<title>`.
2. **Skip-to-main link:** Hidden `<a href="#main">` before `<header>`.
3. **Top bar (`<header role="banner">`):** BRIDGE title, PI pills (current highlighted
   with `--accent-oxblood`), live pulse indicator, freshness timestamp with `aria-live="polite"`.
4. **`<main id="main" role="main">`** container with CSS Grid class.
5. **Section 1 -- Current Sprint:** Sprint name (`<h2>`), sprint goal (`<p>`), task status
   counters as `<dl>` (done/in-progress/blocked/pending with signal colors), segmented
   progress bar, blocker list (top 3, amber left border). Uses `current_sprint` and
   `sprint_goal` data. Empty-state: "No active sprint found".

Remove the old Zone A and Zone B HTML generation code.

#### Acceptance Criteria

- [ ] Test: `render_html()` accepts new kwargs without error
- [ ] Test: output contains `<header role="banner">`
- [ ] Test: output contains `<a` skip-to-main link
- [ ] Test: output contains `<main id="main"` with `role="main"`
- [ ] Test: output contains sprint heading section with `aria-labelledby`
- [ ] Test: empty-state message when `current_sprint` is None
- [ ] Test: sprint goal text appears when provided
- [ ] Test: PI pills render with active class on current PI
- [ ] All existing tests pass (update old assertions that check Zone A/B structure)

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "render_html" -v --tb=short
```

---

### Task T-007: Rewrite `render_html()` -- What Comes Next and WIP Summary sections

**Story:** US-PI4-07: The dashboard shows next action and WIP swim lanes.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** M
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** T-006

#### Description

Continue the `render_html()` rewrite. Add HTML generation for:

1. **Section 2 -- What Comes Next:** Next action card (title, reasoning, link) from
   `derive_next_action()`. Next gate: first feature in IMPLEMENT or REVIEW stage.
   Next sprint: from `sprint_table`, first sprint after current that is not DONE.
   Empty-state: "No recommended action available".

2. **Section 3 -- WIP Summary:** Feature swim lanes with 9-stage lifecycle bars.
   Overall completion percentage. Feature count by stage summary text.
   Uses `STAGE_TONE` and `STAGE_WEIGHT` mappings (existing). Swim lane bars use
   `aria-label` with text equivalent. Feature names truncated to 28 chars.
   Empty-state: "No features registered yet".

These two sections are side-by-side on desktop (next=left column, wip=right column).

Remove the old Zone C HTML generation code.

#### Acceptance Criteria

- [ ] Test: output contains "What Comes Next" section with `aria-labelledby`
- [ ] Test: next action card renders title and reasoning
- [ ] Test: empty-state for What Comes Next when no features
- [ ] Test: WIP section renders feature swim lanes
- [ ] Test: swim lanes have `aria-label` attributes
- [ ] Test: overall completion percentage rendered
- [ ] Test: empty-state for WIP when no features
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "render_html" -v --tb=short
```

---

### Task T-008: Rewrite `render_html()` -- PI Context and Agent Activity sections

**Story:** US-PI4-08: The dashboard shows PI navigation and fleet placeholder.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** M
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** T-007

#### Description

Continue the `render_html()` rewrite. Add HTML generation for:

1. **Section 4 -- PI Context:** One `<details>`/`<summary>` per PI. Current PI: `open`
   attribute (expanded by default). Past PIs: collapsed. Each PI section contains a sprint
   table with columns: Sprint, Title, Status, Dispatches, Last Outcome. Sprint rows link
   to `docs/Management/PI-{N}/Sprint-{M}-{title}/`. PI pills show completion percentage.
   Uses `all_pis` and `sprint_table` data.
   Empty-state: "No Program Increments found in roadmap".

2. **Section 5 -- Agent Activity (placeholder):** Fleet summary stats (principal/generic/
   specialist/total counts from `load_roster()`). Placeholder notice: "Per-agent real-time
   visibility planned for PI-5." Data contract reference link.
   Uses `roster` data.

Remove the old Zone B agent chips HTML generation code.

#### Acceptance Criteria

- [ ] Test: PI Context section uses `<details>` elements
- [ ] Test: current PI `<details>` has `open` attribute
- [ ] Test: past PI `<details>` do NOT have `open` attribute
- [ ] Test: sprint table rows render within PI sections
- [ ] Test: empty-state for PI Context when no PIs
- [ ] Test: Agent Activity placeholder renders with "PI-5" notice
- [ ] Test: fleet summary stats (principals, generic, specialist) render
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "render_html" -v --tb=short
```

---

### Task T-009: Rewrite `render_html()` -- Activity Feed, Footer, and `build()` integration

**Story:** US-PI4-09: The dashboard shows unified activity feed and correct footer.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** M
**Files:** `cli/state_builder.py`, `cli/test_state_builder.py`
**Depends on:** T-008

#### Description

Complete the `render_html()` rewrite. Add HTML generation for:

1. **Section 6 -- Activity Feed:** Unified feed merging dispatches, decisions, and commits.
   Reverse chronological order. Capped at 50 events (architect note, Appendix B.3).
   Each event has: timestamp, actor, event type badge (DISPATCH/DECISION/COMMIT), description.
   Container: `role="log"`, `aria-live="off"`, `tabindex="0"` for keyboard scrolling.
   Max height 480px with `overflow-y: auto`. Footer note: "Showing most recent 50 events.
   Full history in ledger/fleet.db."
   Empty-state: "No activity recorded yet."

2. **Footer:** `<footer role="contentinfo">`. Generation timestamp. Version: "v3.0
   (sprint-first)" (architect note S-2). Stdlib compliance badge: "stdlib only".
   Height: 32px.

3. **`build()` function update:** Add calls to `load_sprint_table()`,
   `detect_current_sprint()`, `load_sprint_goal()`, and `load_decisions()`. Pass results
   as new kwargs to `render_html()`.

Remove the old Zone D HTML generation code and old footer code.

#### Acceptance Criteria

- [ ] Test: activity feed section has `role="log"`
- [ ] Test: feed includes dispatch events
- [ ] Test: feed includes decision events when decisions are provided
- [ ] Test: feed includes commit events
- [ ] Test: feed is capped at 50 events
- [ ] Test: empty-state for activity feed when no events
- [ ] Test: footer contains "v3.0 (sprint-first)"
- [ ] Test: footer contains "stdlib only"
- [ ] Test: `build()` calls new data-layer functions and passes to `render_html()`
- [ ] Test: no `<script` tags in output
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
```

---

**CHECKPOINT 3:** Run full test suite. Verify renderer rewrite is complete.
Verify `build()` and `serve` still work. Generate state.html and visually inspect.

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
.venv\Scripts\python.exe cli/state_builder.py --sdd-root spec-driven-development --dry-run
```

---

## Batch 4: Responsive and Visual Verification (Phase 3, sequential)

### Task T-010: CSS responsive breakpoint tests

**Story:** US-PI4-10: The dashboard is usable on tablet (768px+).
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/test_state_builder.py`
**Depends on:** T-009

#### Description

Add tests that verify the CSS in the generated HTML contains the correct responsive
breakpoints and layout rules. These are string-based assertions on the `HTML_CSS` content:

1. Verify `@media (max-width: 1279px)` is present
2. Verify `grid-template-columns: 1fr` appears in the media query
3. Verify grid-template-areas in desktop layout contain "next" and "wip" on the same row
4. Verify grid-template-areas in tablet layout have each area on its own row
5. Verify `max-height: 480px` for the feed scroll container
6. Verify `prefers-reduced-motion` media query is present

#### Acceptance Criteria

- [ ] Test: desktop grid has two-column layout (next + wip on same row)
- [ ] Test: tablet grid has single-column layout
- [ ] Test: feed scroll container has max-height constraint
- [ ] Test: reduced-motion media query present
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "responsive or breakpoint or motion" -v --tb=short
```

---

### Task T-011: Empty-state fallback tests

**Story:** US-PI4-11: Every section gracefully degrades when data is missing.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/test_state_builder.py`
**Depends on:** T-009

#### Description

Add a comprehensive test that calls `render_html()` with minimal/empty data and verifies
every section produces its defined empty-state message:

1. No current sprint -> "No active sprint found"
2. No features -> "No features registered yet"
3. No PIs -> "No Program Increments found in roadmap"
4. No dispatches -> "No dispatch activity recorded" (or similar)
5. No decisions -> feed still renders (just no DECISION badges)
6. No commits -> feed still renders (just no COMMIT badges)
7. All empty -> all fallback messages present, no crashes

#### Acceptance Criteria

- [ ] Test: empty-state messages for each section verified
- [ ] Test: `render_html()` does not crash with all-empty inputs
- [ ] Test: page structure is valid even with no data
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "empty_state" -v --tb=short
```

---

**CHECKPOINT 4:** Run full test suite. Verify all responsive and empty-state tests pass.

---

## Batch 5: Accessibility and Final Validation (Phase 4, sequential)

### Task T-012: Accessibility audit tests

**Story:** US-PI4-12: The dashboard meets WCAG 2.1 AA accessibility targets.
**Type:** [S] sequential
**Execution:** [HITL] human-needed (manual screen reader verification)
**Size:** S
**Files:** `cli/test_state_builder.py`
**Depends on:** T-009

#### Description

Add tests verifying the semantic HTML structure and accessibility attributes in the
generated HTML output:

1. `<header role="banner">` present
2. `<main id="main" role="main">` present
3. `<footer role="contentinfo">` present
4. Every `<section>` has `aria-labelledby` attribute
5. Heading hierarchy: exactly one `<h1>`, multiple `<h2>`, no skipped levels
6. Activity feed container has `role="log"`
7. Skip-to-main link present (href="#main")
8. No `outline: none` in CSS
9. `aria-label` on swim lane progress bars
10. `aria-live="polite"` on freshness timestamp

The [HITL] tag is because full accessibility validation requires manual screen reader
testing, which cannot be automated. The automated tests verify structure only.

#### Acceptance Criteria

- [ ] Test: all ARIA roles present in output
- [ ] Test: heading hierarchy is correct
- [ ] Test: skip-to-main link present
- [ ] Test: no `outline: none` in CSS
- [ ] Test: swim lanes have `aria-label`
- [ ] Manual: screen reader announces all sections correctly (HITL)
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "accessibility or a11y" -v --tb=short
```

---

### Task T-013: No-JavaScript and no-external-request audit tests

**Story:** US-PI4-13: The dashboard has zero JS and zero external network requests.
**Type:** [P] parallelizable
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/test_state_builder.py`
**Depends on:** T-009

#### Description

Add tests that verify the generated HTML contains:

1. Zero `<script` tags
2. Zero `@import` CSS rules
3. Zero external URLs (no `http://` or `https://` in CSS or HTML, except in `<a>` links
   to local Management/ directories)
4. No `<link rel="stylesheet"` tags (all CSS is inline `<style>`)
5. Footer contains "stdlib only"

#### Acceptance Criteria

- [ ] Test: no `<script` tags in output
- [ ] Test: no `@import` in CSS
- [ ] Test: no external font or CDN references
- [ ] Test: no `<link rel="stylesheet"` tags
- [ ] Test: stdlib badge in footer
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -k "no_javascript or no_external or stdlib" -v --tb=short
```

---

### Task T-014: Final integration test and regression check

**Story:** US-PI4-14: The v2 dashboard generates correctly end-to-end with no regressions.
**Type:** [S] sequential
**Execution:** [AFK] autonomous
**Size:** S
**Files:** `cli/test_state_builder.py`
**Depends on:** T-012, T-013

#### Description

Add an end-to-end integration test that:

1. Seeds a full sdd-root with PI directories, sprint directories with SPEC.md files,
   fleet.db with dispatches and decisions, roster, features, and commits
2. Calls `build()` and verifies it succeeds
3. Verifies the output HTML contains all 7 sections (by checking for section headings)
4. Verifies `render_markdown()` output is unchanged (v1 format preserved)
5. Verifies test count has not decreased from baseline
6. Verifies `serve` mode still initializes (mock the HTTP server)

This is the final gate before the feature is marked complete.

#### Acceptance Criteria

- [ ] Test: `build()` succeeds with full data
- [ ] Test: HTML output contains all 7 section headings
- [ ] Test: markdown output format is unchanged
- [ ] Test: HTML output contains "v3.0 (sprint-first)" in footer
- [ ] Test: no `<script` tags
- [ ] Test count >= baseline + all new tests from this task list
- [ ] All existing tests pass

#### Verification

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
```

---

**CHECKPOINT 5 (Final):** Run full test suite. Generate state.html. Visual inspection
against mockup. If all pass, feature is ready for Stage 1 + Stage 2 code review.

```powershell
.venv\Scripts\python.exe -m pytest cli/test_state_builder.py -v --tb=short
.venv\Scripts\python.exe cli/state_builder.py --sdd-root spec-driven-development
```

---

## Parallelization Summary

| Batch | Tasks | Parallel? | Constraint |
|-------|-------|-----------|------------|
| 1a | T-001, T-002 | [P] yes | Append to different sections of same files; dispatch as pair |
| 1b | T-003, T-004 | [P] yes | Same constraint as 1a; dispatch after 1a merges |
| 2 | T-005 | [S] solo | CSS constant replacement |
| 3 | T-006, T-007, T-008, T-009 | [S] sequential | Each builds on prior section |
| 4 | T-010, T-011 | [P] yes | Both add tests only, no source file conflicts |
| 5 | T-012, T-013 | [P] yes | Both add tests only |
| 5 (gate) | T-014 | [S] solo | Final integration; depends on all prior |

Maximum concurrency: 2 workers per batch. Total sequential depth: 10 tasks on critical path.

## Task Dependency Graph

```
T-001 ──┐
T-002 ──┤
T-003 ──┼── T-005 ── T-006 ── T-007 ── T-008 ── T-009 ──┬── T-010 ──┐
T-004 ──┘                                                 ├── T-011 ──┤
                                                          ├── T-012 ──┼── T-014
                                                          └── T-013 ──┘
```
