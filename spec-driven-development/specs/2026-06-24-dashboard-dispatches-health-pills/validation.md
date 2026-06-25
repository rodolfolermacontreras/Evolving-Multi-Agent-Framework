---
id: SDD-20260624DASHHEALTH-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-24
feature: 2026-06-24-dashboard-dispatches-health-pills
---

# VALIDATION: SDD-037 -- Dispatches card + dashboard health-pills strip

- Feature ID: SDD-037
- Spec: [`spec.md`](./spec.md) | Plan: [`plan.md`](./plan.md) | Tasks: [`tasks.md`](./tasks.md) | CLARIFY: [`clarify.md`](./clarify.md)
- Sprint: PI-6 / Sprint 3 (overall Sprint 12)

---

## Lock Statement

This validation contract is **LOCKED at F-27 (the /tasks gate)** per Article X. The REQUIRED item set below is frozen before implementation. After F-27, REQUIRED items may only be **added** (never removed or loosened) via an explicit `### Delta` entry with timestamp, author, rationale, and item-type. UI-Variant items are delta-eligible for visual refinement per Article XII but their associated correctness assertions (Strict) are not.

All REQUIRED items are **UNCHECKED** at F-27. They are verified and checked during **F-28 implementation** (task T-037-07). This is a design artifact; no item is satisfied yet.

## Mixed-Validation Split (Strict vs UI-Variant)

SDD-037 is a UI-variant feature (`ui-variant: true`). Validation is split:

- **Strict (Article X)** -- correctness and invariants that MUST NOT be loosened: ledger-read correctness + single-connection, the four health-check correctness behaviors, indicators-not-gates, the S1 footprint lock, the no-JS invariant, `schema_lint` exit 0, and the test baseline.
- **UI-Variant (Article XII)** -- visual rendering surfaces that are delta-eligible for iteration: the Dispatches card layout/grouping presentation, the four-pill strip visual rendering, and the click-through detail-section presentation.

---

## REQUIRED Items

> **F-28 verification status: ALL REQUIRED items satisfied.** Evidence drawn from the real end-to-end run: full `cli/` suite **437 passed, 2 skipped** (pre-F-28 399/2, +38 SDD-037 tests); `schema_lint` exit **0**; `TestS1FootprintLockGuard` **3 passed**; and a smoke grep of the regenerated `exec/state.html` (zone-dispatches:1, zone-health:1, `pill pill-`:4 all green, `<script>`:0, dispatches-heading:1, health-heading:1, 11 dispatch rows across 3 feature groups).

### Strict (Article X) -- correctness, may not be loosened

- [x] **R-2** (FR-5, AC-3): `TestInjectDispatchesHtml` unreachable path asserts the disabled note `"Fleet ledger unavailable (fleet.db missing or unreadable)."` and no raise on an `available=False` `LedgerView`; `TestSdd037IndicatorsNotGates` deletes `fleet.db` and confirms `build()` completes without raising.
- [x] **R-3** (FR-3, Q-B, AC-4): `TestSdd037NoNewConnections` patches `sqlite3.connect` and asserts the two new injectors open **zero** connections (both consume the passed-in `LedgerView`); `load_ledger` retains its single `with sqlite3.connect(...)` block; `build()` result `"dispatches" == len(ledger.recent)` is unchanged; no new public ledger API (`LedgerView` widened additively by one defaulted field `grouped`).
- [x] **R-5** (FR-7, AC-6): `TestHealthCheckHelpers` exercises `constitution_semver_status` green (quoted valid semver) / yellow (unquoted parseable) / red (missing/unparseable) on synthetic dirs and asserts the constitution files are **byte-unchanged** after the check. Real run: Constitution pill **green** ("all versions valid").
- [x] **R-6** (FR-8, AC-7): `skill_validity_status` reuses `schema_lint.check_skill` (imported, not reimplemented); tests assert green on zero findings and red on a seeded invalid SKILL.md. Real run: Skills pill **green** ("all skills valid").
- [x] **R-7** (FR-9, AC-8): `ledger_reachability_status` returns green for `available=True`, red with reason for `available=False`; covered by `TestHealthCheckHelpers`. Real run: Ledger pill **green** ("fleet ledger reachable").
- [x] **R-8** (FR-10, AC-9): `stale_tracker_status(stale_days=7)` boundary tests at 7 (green), 8/14 (yellow), 15 (red), and the undatable/missing-file case (yellow) against synthetic `sprint-progress.md`. Real run: Tracker pill **green** ("fresh (1d)").
- [x] **R-10** (FR-13, NG-5, AC-12): `TestS1FootprintLockGuard` **3 passed** -- the five locked S1 functions are byte-identical to their goldens (`render_html` 5b41283b, `load_sprint_table` 35ab5ad4, `load_sprint_goal` a50e5242, `detect_current_sprint` 81af0648, `load_decisions` 98ba432c). Both surfaces are additive injectors wired in `build()` AFTER `inject_lifecycle_html`.
- [x] **R-11** (FR-12, AC-5, AC-10): Health-pills and dispatches tests assert `<script>` count == 0 on the injected fragments; real regenerated `exec/state.html` smoke grep: **`<script>` count = 0**.
- [x] **R-12** (FR-14, Q-F, AC-11): Each health helper is try/except-wrapped to degrade to red/yellow with a reason; `TestSdd037IndicatorsNotGates` confirms forced-failure paths do not raise out of `build()`, do not change exit behavior, and are not wired into any gate (checks are render-time only).
- [x] **R-13** (FR-15, FR-16, AC-13): stdlib-only confirmed (imports limited to stdlib + in-repo `schema_lint`; verified by import scan); `python cli/schema_lint.py` exit **0**; full `cli/` suite **437 passed, 2 skipped** (>= 399 + 38 new; two known skips unchanged).

### UI-Variant (Article XII) -- visual surfaces, delta-eligible

- [x] **R-1** (FR-1, FR-2, FR-4, AC-1, AC-2): `TestInjectDispatchesHtml` asserts feature->sprint grouping and the five per-row fields (agent / role / task id+title / status / when), plus the reachable-empty note `"No dispatches recorded yet."`. Real run: 3 feature groups, 11 rows rendered, no fallback note.
- [x] **R-4** (FR-6, AC-5): `TestInjectHealthPillsHtml` asserts exactly four pills with color classes; real `exec/state.html` smoke grep: **4** `class="pill pill-"` (all green).
- [x] **R-9** (FR-11, AC-10): `TestInjectHealthPillsHtml` asserts non-green pills emit `href="#health-detail-<check>"` anchors with matching detail `<section>`s and green pills emit no link. (All four checks green in the current real run, so no detail sections render -- the anchor/detail behavior is unit-covered on forced non-green fixtures.)

## Optional / Best-Effort

- [x] **O-1**: Dispatch rows are ordered by `COALESCE(outcome_at, dispatched_at) DESC` within each feature/sprint group (most-recent-first).
- [x] **O-2**: Pill detail sections include the offending artifact (constitution filename via the semver detail list; skill path `parent.name` via the skill detail list).
- [ ] **O-3**: Per-group dispatch count (e.g. "feature X -- 4 dispatches") -- not implemented (deferred; not required).
- [x] **O-4**: The stale-tracker detail lists the parsed latest date and the computed age in days.

## Specific Test Coverage Required (F-28)

- [x] Ledger widening: grouping correctness; `available` true and false paths; **single-connection-per-tick** assertion; `len(ledger.recent)` unchanged. (`TestLedgerGrouping`, `TestSdd037NoNewConnections`)
- [x] Dispatches card: populated render (grouping + five fields), reachable-empty state, unreachable disabled state with reason and no raise, injected after the lifecycle marker. (`TestInjectDispatchesHtml`)
- [x] Constitution-semver: green / yellow / red cases on synthetic constitution dirs; assertion that no constitution file is modified. (`TestHealthCheckHelpers`)
- [x] Skill-validity: green (zero findings) and red (>=1 finding) via `check_skill` reuse on synthetic skill trees. (`TestHealthCheckHelpers`)
- [x] Ledger-reachability: green and red from a synthetic `LedgerView`. (`TestHealthCheckHelpers`)
- [x] Stale-tracker: boundary cases at 7, 8, 14, 15 days and the undatable case (N=7). (`TestHealthCheckHelpers`)
- [x] Health-pills strip: four pills present + colors; non-green anchors + detail sections; green has no link; `<script>` count == 0. (`TestInjectHealthPillsHtml`)
- [x] Indicators-not-gates: each check forced to fail internally degrades gracefully, does not raise, does not change `build()` exit. (`TestSdd037IndicatorsNotGates`)
- [x] S1 footprint lock: `TestS1FootprintLockGuard` passes. (3 passed)

## Manual Checks

- [x] **M-1**: Regenerated `exec/state.html` renders the Dispatches card (zone-dispatches:1, dispatches-heading:1) and the four-pill strip (zone-health:1, 4 green pills); page has no JavaScript (`<script>` count 0, so no console JS errors possible).
- [x] **M-2**: Anchor-to-detail behavior verified by `TestInjectHealthPillsHtml` on forced non-green fixtures (server-rendered same-page `#health-detail-<check>` anchors). All pills are green in the current real run, so no live non-green pill is present to click; behavior is unit-asserted.
- [x] **M-3** (F-close): `ledger/__init__.py` confirmed **0 bytes** (still empty); no new ledger table/column was added (only an additive in-memory `LedgerView.grouped` field; `dispatches` schema untouched).

## Tone / UX Check

- [x] **U-1**: Empty and disabled card states use plain language ("No dispatches recorded yet." / "Fleet ledger unavailable (fleet.db missing or unreadable).") -- no stack traces or jargon.
- [x] **U-2**: Pill colors use dark-theme-consistent backgrounds (green `#13351f`, yellow/red analogues) with legible labels, matching existing dashboard styling.

## Definition of Done (F-28)

- [x] All Strict REQUIRED items (R-2, R-3, R-5, R-6, R-7, R-8, R-10, R-11, R-12, R-13) checked with evidence.
- [x] All UI-Variant REQUIRED items (R-1, R-4, R-9) checked (visual delta DE-01 recorded below).
- [x] Specific Test Coverage list fully checked; full `cli/` suite green at 437 (>= baseline 399 + 38 new); `schema_lint` exit 0.
- [x] Manual checks M-1..M-3 and tone checks U-1..U-2 confirmed.
- [x] No `.py` outside the two allowed shared files modified; no constitution write; `<script>` count 0; `TestS1FootprintLockGuard` passing.

## Delta Entries

### Delta DE-01 (2026-06-24, principal-software-developer, test-assertion scoping, UI-Variant R-4)

- **Item type**: UI-Variant test assertion (no REQUIRED-item loosening).
- **Change**: In the full-build test `test_full_build_has_dispatches_card_and_pills`, the health-pill count assertion was scoped from `count('class="pill') == 4` to `count('class="pill pill-') == 4`.
- **Rationale**: The full dashboard already renders pre-existing PI top-bar pills using the plain class `class="pill"`. The four SDD-037 health pills uniquely use `class="pill pill-<color>"`. Scoping the assertion to the color-qualified class asserts the correct invariant (exactly four health pills) without coupling to the unrelated PI pill count. The isolated injector unit test (`test_exactly_four_pills`) still asserts `class="pill` on the health-only fragment, where no PI pills exist. This sharpens the test; it does not weaken R-4 (still "exactly four health pills").
