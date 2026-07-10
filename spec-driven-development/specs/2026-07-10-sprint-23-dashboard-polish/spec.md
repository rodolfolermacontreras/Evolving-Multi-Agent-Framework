---
id: SDD-20260710SPRINT23POLISH-spec
type: spec
status: active
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-sprint-23-dashboard-polish
ui-variant: true
depends_on: [SDD-036, SDD-037, SDD-040, SDD-042]
---

# SPEC: F-63 Sprint 23 dashboard polish

- Feature IDs: **SDD-038**, **SDD-056**, **SDD-057**
- Sprint: PI-9 Sprint 2 / overall Sprint 23
- Status: **APPROVED**
- Clarification: [`clarify.md`](./clarify.md)
- Validation: [`validation.md`](./validation.md) -- LOCKED at TASKS

---

## Problem Statement

The generated dashboard still has three visible trust/coherence defects. Its PI
pill navigation can mark stale data current, its Current Sprint widget reads the
deprecated Management sprint layout instead of the active `CURRENT_PI.md`, and
the canonical lifecycle states have no consistent semantic color language. Two
historical kickoff sentences also still imply that a fresh session is mandatory,
contradicting SDD-039's context-isolation choice.

## Goal

Make the regenerated dashboard show PI-9 as the sole current PI, show explicitly
active overall Sprint 23 from the newest ACTIVE `CURRENT_PI.md`, and use one
accessible framework-owned semantic color for each canonical lifecycle state.
Repair only the two named stale sentences. Preserve all Article X locked
functions byte-for-byte and retain stdlib-only Python plus vanilla CSS/JS.

## Non-Goals

- No `constitution/**` or roadmap edit.
- No edit to `render_html`, `render_markdown`, `load_sprint_table`,
  `load_sprint_goal`, `detect_current_sprint`, or `load_decisions`.
- No new dependency, schema, persisted data model, JavaScript framework, or API.
- No broad historical wording scrub.
- No SDD-034, brownfield bootstrap, PI-4 housekeeping, or SDD-035 work.
- No hand edit of generated `exec/state.md`, `exec/state.html`, or
  `exec/work-index.md`.

## Requirements (RFC-2119)

### SDD-056 -- PI pill-nav truth and exact wording

- **R56-1:** The system MUST additively post-process the rendered PI pill nav from
  the live `PIBlock` collection already loaded by `build()` and the resolved
  active PI. It MUST render every live PI once, in numeric order, and exactly one
  current pill with `aria-current="page"`.
- **R56-2:** The pill-nav post-processor MUST preserve the existing nav's label,
  MUST escape labels/titles, MUST be idempotent, and MUST degrade to the original
  HTML when the nav marker or active PI is unavailable.
- **R56-3:** The implementation MUST NOT edit roadmap/constitution data to make the
  pills appear correct and MUST NOT edit `render_html`.
- **R56-4:** Only the two exact phrases locked in `clarify.md` MUST be replaced.
  The replacement MUST preserve the historical sequence and state that either a
  fresh session or an EM-routed subagent dispatch satisfies isolation.

### SDD-057 -- Current Sprint source truth

- **R57-1:** A new additive loader MUST select the highest-numbered
  `sprints/PI-*/CURRENT_PI.md` that is both frontmatter `status: active` and body
  PI status ACTIVE.
- **R57-2:** Within that file, the loader MUST accept one explicit active/current/
  in-progress sprint marker from the PI status line, an active sprint heading, or
  a Sprint Allocation row; MUST reject CLOSED, DONE, and PROPOSED markers; and
  MUST return the existing sprint-dict shape needed by `detect_current_sprint`.
- **R57-3:** Explicit overall Sprint number MUST win over a PI-local sprint number.
  Conflicting multiple active markers, malformed numeric markers, read errors, or
  no explicit marker MUST produce no live candidate, never a guessed next sprint.
- **R57-4:** `build()` MUST feed the live loader result through the unchanged
  `detect_current_sprint`; when no live candidate exists it MUST fall back to the
  unchanged `load_sprint_table`, preserving the existing final empty state.
- **R57-5:** On the real repository with PI-9/Sprint 23 explicitly ACTIVE, generated
  `state.html` MUST show Sprint 23 and MUST NOT show `No active sprint found.`

### SDD-038 -- lifecycle color tokens

- **R38-1:** The system MUST define exactly the nine semantic tokens and values
  approved in `clarify.md`, one for each canonical state IDEA through DONE.
- **R38-2:** A new additive `inject_lifecycle_tokens_html` post-processor MUST run
  after `inject_lifecycle_html`, add a canonical state class to each lifecycle
  node/current-stage label, and inject CSS that uses the matching token on all
  repository-controlled lifecycle HTML surfaces.
- **R38-3:** Lifecycle meaning MUST remain textual and structural: visible labels
  and `aria-current="step"` remain; color MUST NOT be the sole signal; opacity
  MUST NOT reduce lifecycle text below the contrast requirement.
- **R38-4:** Each token MUST have WCAG contrast >=4.5:1 against `#1C1B18` for
  normal text and >=3:1 for UI boundaries. Solid token fills MUST use carbon
  `#0A0A0A` text. Tests MUST calculate contrast from the locked hex values.
- **R38-5:** Raw Markdown MUST retain readable lifecycle text as the portable
  fallback. No `render_markdown` edit is permitted; all repository-controlled
  HTML renderings MUST use the token injector.

### Cross-cutting

- **RX-1:** Implementation MUST be stdlib-only with vanilla CSS/JS and follow TDD.
- **RX-2:** `TestS1FootprintLockGuard` MUST pass unchanged and all five locked
  function source hashes MUST remain byte-identical.
- **RX-3:** B-1, B-2, and B-4 remain live; no REQUIRED validation item may be
  silently deferred.
- **RX-4:** State-builder implementation tasks MUST be serialized. SDD-049 overlap
  semantics permit parallel work only when normalized file-scope intersections
  are empty.

## Acceptance Criteria

- **AC56-1:** A synthetic live PI list PI-1..PI-9 renders nine unique pills in
  numeric order, PI-9 alone current with `aria-current="page"`, and no stale PI
  current.
- **AC56-2:** Missing nav/active PI returns original HTML; running the injector
  twice yields byte-identical output after the first run.
- **AC56-3:** Only the two exact old phrases are absent and both replacement
  phrases are present; unrelated historical fresh-session/context-isolation text
  is unchanged.
- **AC57-1:** Loader fixtures prove newest ACTIVE PI selection, explicit overall
  Sprint precedence, accepted marker forms, and rejection of closed/done/
  proposed/malformed/conflicting/absent markers.
- **AC57-2:** Build integration proves the live sprint list is passed to unchanged
  `detect_current_sprint`, and the legacy table is used only as fallback.
- **AC57-3:** Real generated `exec/state.html` contains PI-9 current and active
  Sprint 23 and does not contain `No active sprint found.`
- **AC38-1:** Generated lifecycle HTML contains all nine locked CSS variables and
  one state class per canonical state; each visible state maps to exactly one
  token.
- **AC38-2:** Automated WCAG computation proves all nine locked token contrasts;
  active state retains `aria-current="step"` and labels remain visible without
  opacity-dependent meaning.
- **ACX-1:** Full suite is >=623 passed / 2 skipped plus new tests; schema, origin,
  and stale-doc lints are clean; local doctor is green; fresh CI doctor and public
  CI are green at close.
- **ACX-2:** `TestS1FootprintLockGuard` passes and independent source hashes for all
  five locked functions equal the existing goldens.

## File-Scope Matrix

| Surface | Planned mutable files | Read-only / forbidden | Serialization |
|---------|-----------------------|-----------------------|---------------|
| SDD-057 loader | `cli/state_builder_data.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | locked loader/detector bodies forbidden | Serial |
| SDD-056 pills | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | `constitution/**`, `render_html` forbidden | Serial after SDD-057 |
| SDD-038 tokens | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | `render_html`, `render_markdown` forbidden | Serial after pills |
| SDD-056 wording | `feature-prompts/SPRINT-05-KICKOFF.prompt.md`, `feature-prompts/SPRINT-06-KICKOFF.prompt.md`, `cli/test_sdd056.py` | every other historical prompt | Parallel-safe only against state-builder tasks |
| Source marker | `sprints/PI-9/CURRENT_PI.md` by Sprint EM/PM | loader may not fabricate marker | Must precede real render smoke |
| Generated output | `exec/state.md`, `exec/state.html`, `exec/work-index.md` via `build()` only | no hand edits | Final serial step |
| Evidence | this spec dir's `validation.md`, `tasks.md`; `exec/sprint-progress.md` append-only | prior progress blocks immutable | Final serial step |

The SDD-049 overlap check MUST compare normalized scopes before any worker batch.
All three state-builder rows intersect on `cli/state_builder.py` and
`cli/test_state_builder.py`, so they cannot be dispatched together.

## Data Model / API Changes

None persisted. New helpers are internal additive functions. The sprint loader
returns the existing list-of-dicts shape consumed by `detect_current_sprint`.

## Test Strategy

- Unit: PI-nav idempotence/escaping/current uniqueness; active-sprint parser and
  fallback boundaries; token mapping and contrast calculation; exact wording.
- Integration: `build(write=False)` with synthetic PI/sprint trees and unchanged
  detector; real `build(write=True)` regeneration at close.
- Regression: full suite, Article X lock guard and independent hashes, no
  constitution diff, generated files only from build.
- Manual/accessibility: inspect lifecycle labels/current-state distinction in the
  generated dashboard at normal and high-contrast/forced-colors expectations;
  record contrast table evidence.

## Traceability

| ID | Requirements | ACs | Validation | Tasks |
|----|--------------|-----|------------|-------|
| SDD-056 | R56-1..R56-4 | AC56-1..AC56-3 | V56-1..V56-4 | T-056-01..03 |
| SDD-057 | R57-1..R57-5 | AC57-1..AC57-3 | V57-1..V57-4 | T-057-01..03 |
| SDD-038 | R38-1..R38-5 | AC38-1..AC38-2 | V38-1..V38-4 | T-038-01..02 |
| Cross-cutting | RX-1..RX-4 | ACX-1..ACX-2 | VX-1..VX-5 | T-X-01..02 |

## Risks

- Ambiguous sprint prose could produce a false current sprint. Mitigation:
  explicit marker grammar, conflict rejection, no inference.
- Injector order could overwrite state classes. Mitigation: pills before
  lifecycle; token injector immediately after lifecycle; idempotence tests.
- Color-only communication could fail accessibility. Mitigation: labels,
  `aria-current`, no opacity semantics, computed contrast evidence.
- Shared-file dispatch could conflict. Mitigation: serialized state-builder chain
  and SDD-049 overlap precheck.

## Open Questions

None. Approved for PLAN/TASKS.
