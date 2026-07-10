---
id: SDD-20260710SPRINT23POLISH-validation
type: validation
status: active
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-sprint-23-dashboard-polish
---

# VALIDATION: F-63 Sprint 23 dashboard polish

- IDs: SDD-038, SDD-056, SDD-057
- Spec: [`spec.md`](./spec.md)
- Lock point: **TASKS, 2026-07-10**

---

## Lock Statement

This contract is **LOCKED** before implementation under Article X. Every REQUIRED
item is unchecked. No REQUIRED item may be removed, weakened, or silently
deferred. SDD-038 visual refinements may use Article XII append-only deltas, but
contrast, state coverage, labels, Article X byte identity, and generated-output
truth are Strict and cannot be loosened.

## REQUIRED -- SDD-056

- [x] **V56-1:** Unit tests prove PI-1..PI-9 render once in numeric order from live
  PI data, PI-9 alone carries current class and `aria-current="page"`, values are
  escaped, and no constitution/roadmap write occurs. Proves AC56-1.
- [x] **V56-2:** Unit tests prove missing-marker/no-active fallback and injector
  idempotence. Proves AC56-2.
- [x] **V56-3:** Exact-wording test proves only Sprint 5's
  `Each F-## runs in its own fresh session.` and Sprint 6's
  `Do NOT start Sprint 7 in this session. It runs in its own fresh session`
  are absent, their approved context-isolation replacements are present, and the
  files' remaining text differs only in those two replacements. Proves AC56-3.
- [x] **V56-4:** Real generated `exec/state.html` has PI-9 as the sole current
  pill and no stale PI current. Proves AC56-1/AC57-3.

## REQUIRED -- SDD-057

- [x] **V57-1:** Loader unit tests cover: highest-numbered ACTIVE PI wins; inactive
  frontmatter/body rejected; explicit status-line, heading, and allocation-row
  markers accepted; overall Sprint number beats PI-local number. Proves AC57-1.
- [x] **V57-2:** Boundary tests reject CLOSED/DONE/PROPOSED, malformed, absent,
  duplicate-conflicting, and unreadable markers without guessing. Proves AC57-1.
- [x] **V57-3:** Build integration test spies on the unchanged
  `detect_current_sprint`: live list is supplied when valid; unchanged legacy
  `load_sprint_table` is used only when live list is empty; both-empty preserves
  the existing empty state. Proves AC57-2.
- [x] **V57-4:** With PI-9 `CURRENT_PI.md` explicitly marking overall Sprint 23
  ACTIVE, a real build writes `state.html` containing active Sprint 23 and not
  `No active sprint found.` Proves AC57-3.

## REQUIRED -- SDD-038

- [x] **V38-1:** Token test locks exactly nine names/hex values and one canonical
  state-to-token mapping for IDEA, BACKLOG, CLARIFY, SPEC, PLAN, TASKS, IMPLEMENT,
  REVIEW, DONE. Proves AC38-1.
- [x] **V38-2:** Injector tests prove all lifecycle nodes/current-stage labels gain
  the matching state class, CSS variables are injected once, and a second pass is
  byte-idempotent. Proves AC38-1.
- [x] **V38-3:** WCAG sRGB calculation in tests proves every locked token is >=4.5:1
  against `#1C1B18` and >=3:1 for boundaries; solid fills specify `#0A0A0A` text.
  Record the nine measured ratios in close evidence. Proves AC38-2.
- [x] **V38-4:** Accessibility test/manual evidence proves visible state labels and
  `aria-current="step"` remain, color is not sole meaning, and lifecycle state
  text is not dimmed by opacity. Raw Markdown remains readable and
  `render_markdown` is byte-unchanged. Proves AC38-2.

## REQUIRED -- cross-cutting and close

- [x] **VX-1:** TDD evidence records RED before production behavior and GREEN after
  for each state-builder behavior group and the wording guard. Proves RX-1.
- [x] **VX-2:** `TestS1FootprintLockGuard` passes unchanged; independent
  `inspect.getsource` SHA-256 values for all five locked functions equal the
  existing `GOLDEN_S1_HASHES`; no locked function body changed. Proves ACX-2.
- [x] **VX-3:** Full `python -m pytest spec-driven-development/ --tb=no -q` is
  >=623 passed / 2 skipped plus new tests; schema lint, origin lint, and stale-doc
  lint all exit 0. Proves ACX-1.
- [ ] **VX-4:** Strict local doctor is green; fresh CI-profile doctor is green in a
  clean checkout; public GitHub Actions CI is green at close. B-1 contains real
  Sprint 23 outcome rows, B-2 is green, and B-4 is green. Proves ACX-1.
- [ ] **VX-5:** `git diff` proves no `constitution/**` edit; generated executive
  files were produced only by `state_builder.py build`; no dependency/schema/API
  addition; no REQUIRED deferral. Proves RX-1..RX-4.

## Manual / UX evidence

- [ ] **M-1:** Open real generated dashboard: PI-9 is sole current pill; Current
  Sprint says Sprint 23; all nine lifecycle states show their approved semantic
  colors and retain labels/current emphasis.
- [ ] **M-2:** Record computed contrast table and inspect keyboard/focus,
  forced-colors/high-contrast behavior, and narrow viewport wrapping. No state is
  communicated by color alone.
- [ ] **M-3:** Confirm the two repaired historical instructions still communicate
  their original sequencing prohibition while allowing either isolation method.

## Definition of Done

All 17 REQUIRED rows and 3 manual rows are checked with real evidence; no REQUIRED
deferral; state surfaces regenerated; B-1/B-2/B-4 green; public CI green; owner
pre-push authorization honored.

## Delta Entries

None at lock.

## F-64 Evidence -- 2026-07-10

- V56-1/V56-2: focused F-64 plus lock run passed 36 tests; PI-nav tests cover
  PI-1..PI-9 ordering, escaping, sole current + ARIA, fallback, idempotence, and
  no roadmap write.
- V56-4/V57-4: regenerated by `state_builder.py`; `state.html` contains Sprint
  23, one PI-9 `aria-current="page"`, no stale PI-5 current, and no
  `No active sprint found.`
- V57-1/V57-2: fixtures cover all three marker sources, highest ACTIVE PI,
  overall-number precedence, frontmatter/body rejection, read errors, conflicts,
  terminal/negated states, and malformed decimal/alphanumeric/hyphenated tokens.
- V57-3: integration spies prove live-first, legacy-only fallback, and preserved
  both-empty behavior through unchanged `detect_current_sprint`.
- VX-1: initial helper imports failed RED; review-found decimal/status boundary
  fixtures each failed RED before their production fixes; focused GREEN was
  36 passed.
- VX-2: lock guard 3 passed; independent SHA-256 checks matched all five golden
  hashes for `render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, and `load_decisions`.
- VX-3: full suite 657 passed / 2 skipped / 2 subtests; schema, origin, and
  stale-doc lints all clean.
- Still open by scope: V56-3, all V38 rows, VX-4/VX-5, and M-1..M-3 belong to
  F-65 and/or F-66 close. No checkbox for those rows was changed by F-64.

## F-65 Evidence -- 2026-07-10

- V56-3: `test_sdd056.py` failed RED before the prompt edits, then passed with
  3 tests / 4 subtests. Whole-file before/after SHA-256 and reverse replacement
  prove that only the two approved byte sequences changed.
- V38-1/V38-2: token tests failed RED on the missing export, then passed GREEN.
  Exact nine-token equality, canonical class mapping, every lifecycle node,
  current-stage labels, one style marker, byte-idempotence, and immediate build
  ordering are covered.
- V38-3: independent WCAG sRGB ratios against `#1C1B18` are IDEA 7.186,
  BACKLOG 6.845, CLARIFY 7.297, SPEC 7.250, PLAN 7.425, TASKS 6.245,
  IMPLEMENT 5.239, REVIEW 5.852, and DONE 5.901. Carbon `#0A0A0A` fill-text
  ratios range 6.022..8.535. Every text ratio is >=4.5:1 and every token/surface
  boundary is >=3:1.
- V38-4: tests and independent UX review prove labels and
  `aria-current="step"` remain, lifecycle node/label opacity is 1, current state
  retains weight plus a >=3:1 token outline, and exact focus-visible,
  forced-colors, and <=640px wrapping rules exist. `render_markdown` remains
  byte-unchanged. Stage 2 initially found an insufficient `currentColor` outline
  and weak CSS assertions; both were fixed and two independent re-reviews
  APPROVED.
- Focused final: 13 passed / 4 subtests. Full suite: 668 passed / 2 skipped /
  6 subtests. Schema, origin, and stale-doc lints are clean. Strict local doctor
  and explicit CI-profile doctor are green.
- Article X: unchanged guard 3/3 passed. Independent SHA-256 values matched all
  five goldens for `render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, and `load_decisions`.
- Generated smoke after builder-only regeneration: Sprint 23 present; empty
  sprint text absent; PI-9 is the sole current pill; one token style marker; all
  nine exact variables and all nine state classes present. F-64 truth remains.
- Ledger: real PI-9 dispatch/review rows 35-38 all record success. SDD-049
  normalized overlap assessment found zero intersections between the state-builder
  and wording packets; shared state-builder work remained serialized.
- Intentionally open for F-66: VX-4, VX-5, M-1, M-2, M-3, T-X-02, public CI,
  owner pre-push approval, and sprint close. No checkbox for those rows changed.
