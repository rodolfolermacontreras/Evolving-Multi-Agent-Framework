# SPRINT 23 KICKOFF -- PI-9 Sprint 2 / Experience Polish: dashboard truth + color tokens

You are leading **Sprint 23**, the **second sprint of PI-9 ("Experience Polish")**.
Sprint 22 opened PI-9 and shipped SDD-049 (fleet file-overlap detector) and SDD-054
(backlog reorder -> backend re-optimization). Sprint 23 clears the visible
dashboard rot and finishes the surface polish: the PI pill-nav still shows
PI-1..PI-5 with PI-5 marked current (wrong -- we are on PI-9), the "Current Sprint"
widget reads a deprecated path and shows "No active sprint found," lifecycle states
have no consistent color language, and a little stale "fresh session" wording
lingers. After Sprint 23 the dashboard tells the truth at a glance: the pill-nav
shows the real current PI, the current-sprint widget shows the active sprint,
lifecycle states carry consistent colors, and the wording is clean.

**Every fix in this sprint is Article-X-lock-safe** -- the pill-nav and the
current-sprint widget live inside locked functions (`render_html`,
`load_sprint_table`), so they are fixed by **additive `inject_*` / additive
loaders**, never by editing a locked function. `TestS1FootprintLockGuard` stays
GREEN throughout.

Deliverables:

1. **SDD-038** (filed, allocated) -- dashboard color tokens: one color per
   lifecycle state, used consistently across the dashboard + rendered views. Land
   via additive CSS tokens / injector, not by editing `render_html`.
2. **Pill-nav fix** (IDEAS.md 2026-06-25, not yet filed) -- the `state.html` PI
   pill-nav renders PI-1..PI-5 with PI-5 `current`. Fix via an additive `inject_*`
   post-processor that rewrites the pill-nav after render to reflect the real
   current PI (PI-9) without touching locked `render_html`. **PM files an SDD-ID at
   CLARIFY.**
3. **Current-Sprint widget fix** (IDEAS.md 2026-06-26, not yet filed) -- the
   dashboard "Current Sprint" section shows "No active sprint found" because
   `load_sprint_table` reads a deprecated `docs/Management/PI-N/Sprint-N-*/SPEC.md`
   path; real sprint state lives in `sprints/PI-N/CURRENT_PI.md`. Fix via an
   ADDITIVE loader that derives the current sprint from the newest ACTIVE
   `CURRENT_PI.md` and feeds `detect_current_sprint`, wired into `build()` WITHOUT
   editing the locked `load_sprint_table` / `detect_current_sprint`. **PM files an
   SDD-ID at CLARIFY.**
4. **Wording cleanup** (IDEAS.md, tiny) -- the leftover "fresh session" phrasing
   from the SDD-039 area (SPRINT-05 L35 / SPRINT-06 L202 incidental note). **PM
   files an SDD-ID (or folds it into one of the above) at CLARIFY.**

Do NOT pull in other work: SDD-034 (dedup heuristic) is P3 non-UX and stays out;
PI-4 housekeeping (domain-skill annotations, GH Actions Node bump) stays out;
**SDD-035** (Azure decommission) remains out-of-band.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent (sprint-scoped EM;
SDD-043 / ADR-020), NOT the project Executive Manager.

- In the fresh session, **activate the `sprint-executive-manager` agent**
  ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md)).
- It **routes** feature work to the Principal Product Manager, Principal Architect,
  and Principal Software Developer, synthesizes, and surfaces escalations. Level 0 --
  makes no product/technical/implementation decisions itself.
- It **cannot create sprints or PIs** -- it may only SUGGEST to the project EM, and
  reports UP at close.
- Human-facing output is **short and plain** (SDD-044); every owner decision uses
  the **DECISION-REQUEST FORMAT** (SDD-053). Dogfood both.

**The PM owns triage here.** Three of the four items are IDEAS.md notes, not filed
backlog rows -- the PM files them as fresh SDD-IDs (next free after SDD-054, e.g.
SDD-055/056/057) at CLARIFY, or folds the tiny wording item into another. Only
SDD-038 is pre-filed and allocated.

---

## HARD PREREQUISITE -- STOP IF NOT MET

1. **Sprint 22 is CLOSED and pushed.** Confirm Sprint 22 (PI-9 Sprint 1) at push
   head `6883a83` with SDD-049 + SDD-054 DONE in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md), and
   [`../sprints/PI-9/CURRENT_PI.md`](../sprints/PI-9/CURRENT_PI.md) marking PI-9
   **ACTIVE**, PI-9 the sole `(current)` PI in `constitution/roadmap.md`.
2. **Tests green at the Sprint 22 baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **616 passed**, 2 skipped (from the repo root).
3. **Schema lint, origin lint, stale-doc lint clean.**
4. **`doctor` green and CI green** on `6883a83`; `TestS1FootprintLockGuard` PASS.
5. **SDD-038 is OPEN and allocated to PI-9 Sprint 23** in the backlog; the three
   IDEAS.md items are present for the PM to file.
6. **Live gates apply**: B-1 (ledger before close), B-2 (TDD + DONE-completeness),
   B-4 (CI) are LIVE.
7. **Owner approved the Sprint 23 start** (via the Executive Manager) with the full
   experience-polish set.

If any fails, STOP as OWNER-ATTENTION.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md).
2. Verify the HARD PREREQUISITE.
3. **Activate the Sprint Executive Manager agent.**
4. Execute in isolated feature sessions or Sprint-EM-routed subagent dispatches
   (Article VII).
5. Append feature blocks + the close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Ledger append-only;
   dogfood B-1.

---

## 1. Sprint goal

After Sprint 23 the dashboard is honest and coherent at a glance: the PI pill-nav
shows PI-9 as current (not PI-5), the "Current Sprint" widget shows the active
sprint (not "No active sprint found"), lifecycle states carry one consistent color
each, and the stale wording is gone -- all achieved without touching a single
Article X locked function.

### Scope

- **SDD-038 -- color tokens**: define OUR OWN lifecycle-state color tokens (one
  color per state) applied consistently across the dashboard + rendered Markdown
  views via an additive injector / CSS tokens. Do NOT photocopy any external
  palette. Lock-safe (no `render_html` edit).
- **Pill-nav fix (PM-filed ID)**: additive `inject_*` post-processor rewrites the
  `state.html` pill-nav to the real current PI after render.
- **Current-Sprint widget fix (PM-filed ID)**: additive loader derives the current
  sprint from the newest ACTIVE `CURRENT_PI.md`, feeding `detect_current_sprint`
  via `build()` without editing the locked loader.
- **Wording cleanup (PM-filed / folded)**: remove the leftover "fresh session"
  phrasing.
- **Dogfood B-1**: log Sprint 23's own dispatch outcomes before close.

### Article X is the central constraint -- READ THIS

The pill-nav lives inside `render_html`; the current-sprint widget inside
`load_sprint_table` / `detect_current_sprint`. These are **byte-frozen locked
functions**. Every Sprint 23 fix is **additive** -- a post-render `inject_*` or a
new additive loader wired into `build()` -- and NEVER edits a locked function.
`TestS1FootprintLockGuard` PASS is a close criterion. Touching a locked function is
an Article X re-baseline (ADR + owner approval, Level-2) and is NOT in scope.

### Explicit exclusions

- SDD-034 (dedup), PI-4 housekeeping, and any non-UX carryover -- OUT.
- Azure decommission (SDD-035) -- out-of-band.
- No `constitution/**` edit expected. If a fix seems to need a roadmap/principles
  change, STOP and surface it (the pill-nav fix must be data-driven from the live
  current PI, not a roadmap edit).
- Do NOT scrub history.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-63: CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect | PM files the three IDEAS.md items as fresh SDD-IDs (pill-nav, current-sprint widget, wording), confirms SDD-038 scope, and the Architect confirms every fix is additive/lock-safe (no locked-fn edit) and no `constitution/**` change. Builds each `validation.md`. |
| 2 | F-64: IMPLEMENT + QA -- dashboard-truth pair (pill-nav + current-sprint widget) | SW Dev + workers | The two visible "lies" first. Additive injector + additive loader; TDD; `TestS1FootprintLockGuard` stays GREEN. |
| 3 | F-65: IMPLEMENT + QA -- SDD-038 color tokens + wording cleanup | SW Dev + workers | Aesthetic + wording after the truth fixes. Additive tokens; TDD. |
| 4 | F-66: Sprint 23 close | Sprint EM + SW Dev | Regenerate state, run the dashboard smoke test (pill-nav shows PI-9, widget shows active sprint, states colored, wording clean), owner pre-push approval, mark items DONE, report up. |

Default sequential. Fleet dispatch only after CLARIFY proves no two workers touch
the same file -- and note SDD-049 (shipped Sprint 22) now automates that check.
Shared surfaces (`state_builder*` modules, generated exec surfaces) force
serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- file the three IDEAS.md items (PM)
Assign fresh SDD-IDs (next free after SDD-054) to the pill-nav fix and the
current-sprint widget fix; file or fold the tiny wording cleanup. Default: file
pill-nav + current-sprint widget as their own IDs; fold the wording fix into the
closest one. Surface the IDs.

### Q-B -- confirm lock-safe approach for each (Architect)
Confirm pill-nav = additive `inject_*` post-processor; current-sprint = additive
loader feeding `detect_current_sprint` via `build()`; color tokens = additive CSS/
injector. None edits a locked function. Surface the confirmation.

### Q-C -- color token set (SDD-038)
Define the lifecycle-state color set (one per state) as OUR tokens, not a copied
palette. Default: a small, accessible, IDE-native set applied via tokens. Surface
the set.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** argparse, sqlite3, pathlib, json, sys, os, re;
  vanilla JS / CSS for browser (no framework, no dep).
- **Article X locked functions immutable.** Every fix additive; no edit to
  `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`. `TestS1FootprintLockGuard` PASS.
- **No `constitution/**` edit expected.** Pill-nav is fixed data-driven, not by a
  roadmap edit. If a change seems to need one, STOP and surface.
- **Do not regress `doctor`/CI.** Health set stays green.
- **Live B-1 / B-2 / B-4 gates apply.**
- **No silent REQUIRED deferral.**
- **Dogfood SDD-044 + SDD-053.**
- **Append-only ledger. Do NOT scrub history.**
- **Git discipline.** Explicit path staging only; never `git add -A` / `git add .`.
  Pre-push owner approval mandatory.

---

## 5. Close criteria (Definition of Done)

1. **Pill-nav shows the real current PI** (PI-9), not PI-5, on the regenerated
   `state.html`.
2. **Current-Sprint widget shows the active sprint**, not "No active sprint found."
3. **Lifecycle states carry consistent colors** (SDD-038 tokens) across dashboard
   + rendered views.
4. **Wording cleanup done** -- no leftover stale "fresh session" phrasing.
5. All per-item REQUIRED validation checked with real evidence; manual checks at
   close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` >= 616 passed, 2
   skipped (grows with new tests; must not regress).
7. Schema lint clean, origin lint clean, stale-doc lint green.
8. **Article X lock held**: `TestS1FootprintLockGuard` PASS; locked functions
   byte-identical (every fix additive).
9. **`doctor` green and CI green**; B-2 blocking checks pass.
10. **Ledger shows real Sprint 23 rows**; B-1 satisfied.
11. SDD-038 + the PM-filed IDs marked DONE in BACKLOG with evidence; the IDEAS.md
    items are marked filed/closed.
12. **Owner pre-push approval recorded before any push.**
13. **Reported up to the project Executive Manager**; PI-9 continues or its close is
    surfaced as the next owner decision.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 23 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect design; SW Dev + workers implementation/close
- Features completed: F-63, F-64, F-65, F-66
- Commits: <commit SHAs>
- Tests: 616 -> <N> (>= 616; must not regress)
- Schema lint: clean; origin lint: 0 hits; stale-doc lint: green
- Pill-nav fix (SDD-0NN): shows PI-9 current -- <PASS | FAIL> (additive inject_*, no locked-fn edit)
- Current-Sprint widget fix (SDD-0NN): shows active sprint -- <PASS | FAIL> (additive loader)
- SDD-038 color tokens: consistent lifecycle-state colors -- <PASS | FAIL>
- Wording cleanup (SDD-0NN / folded): <PASS | FAIL>
- IDs filed by PM at CLARIFY: <list>
- Validation: <r>/<r> REQUIRED per item + manual checks
- Live gates: B-1 ledger (<N> rows), B-2, B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS); all fixes additive
- History preserved: YES
- Deferred / out of scope: SDD-034, PI-4 housekeeping, SDD-035 out-of-band
- PI-9 status: ACTIVE -- Sprint 23 CLOSED; next: PI-9 Sprint 3 or PI-9 close decision
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph lessons>
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT edit any Article X locked function. Every fix is additive.
  `TestS1FootprintLockGuard` stays GREEN.
- Do NOT edit `constitution/roadmap.md` to fix the pill-nav -- fix it data-driven
  from the live current PI. If a constitution change seems needed, STOP and surface.
- Do NOT fabricate the color set from a copied external palette -- define our own.
- Do NOT pull in SDD-034, PI-4 housekeeping, or any non-UX carryover.
- Do NOT touch Azure decommission (SDD-035).
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates.
- Do NOT scrub or rewrite history.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the spec dirs here -- F-63 does that in-session.
- Do NOT have the Sprint EM create a sprint/PI or author the next kickoff -- it
  SUGGESTS to the project EM and reports up at close.
