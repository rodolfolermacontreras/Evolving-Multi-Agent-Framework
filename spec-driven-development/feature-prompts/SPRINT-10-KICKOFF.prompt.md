# SPRINT 10 KICKOFF -- PI-6 Sprint 1 / Dashboard parser fix + auto-refresh

You are leading **Sprint 10**, which is **PI-6 Sprint 1**. This is the launch
sprint of PI-6 (Dashboard Reinvestment + Carryover Cleanup). Your job is to
ship **SDD-040** -- the `state_builder.py` parser fix (stale active-focus
heuristic) and serve-mode auto-refresh (static-page defect). Do not absorb
SDD-036, SDD-037, or SDD-038 -- those are Sprints 11, 12, and 13.

You are the **Principal Executive Manager** for this kickoff. PM + Architect
own SDD-040 CLARIFY/SPEC/PLAN/TASKS (F-21). The Principal Software Developer
owns implementation, QA, sprint close, and the Sprint 11 kickoff authoring
(F-22 and F-23).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 10 must not start until all seven checks are true:

1. **PI-5 closed at `8417818`.** Verify
   [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md) shows
   `CLOSED / DONE-WITH-CARRYOVER` 2026-06-09 and
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) contains a
   `### PI-5 -- CLOSED / DONE-WITH-CARRYOVER` block dated 2026-06-09. The PI-5
   close commit on `origin/master` must be `8417818`; confirm with
   `git log --oneline origin/master -5`.
2. **PI-6 launched.** Either
   [`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md) exists
   with `status: active` and an `ACTIVE` status line, OR this kickoff prompt
   carries an explicit "PI-6 launches with this sprint" note and the EM is
   prepared to create CURRENT_PI.md as part of the launch commit. The
   default at Sprint 10 kickoff time is that CURRENT_PI.md already exists
   (filed 2026-06-10).
3. **Tests are green at the PI-5 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   337 passed with the known 2 platform-conditional skips.
4. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
5. **SDD-040 is filed in BACKLOG** with PI-6 Sprint 10 allocation. Confirm
   the entry under "### PI-6 Dashboard Bundle (filed 2026-06-10)" in the P1
   section of [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md).
6. **SDD-036, SDD-037, SDD-038 are still present in BACKLOG** as PI-6
   candidates (SDD-036 + SDD-037 under "### Post-Sprint-7 Bundle" P1 + P2;
   SDD-038 under the same bundle in P3). They must NOT be marked DONE or
   pulled into Sprint 10.
7. **Owner approved Sprint 10 start.** Record the approval evidence (owner
   verbatim or EM-synthesized decision) in the Sprint 10 close block at
   `exec/sprint-progress.md` before any push.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 10 on a
red test baseline, a missing PI-6 launch, or a BACKLOG that does not show
SDD-040 allocated to PI-6 Sprint 10.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 10 in isolated feature sessions or subagent dispatches that
   preserve Article VII's context-isolation property. Do not ask the owner to
   manually open new sessions when EM-routed subagent dispatch gives
   equivalent isolation and the owner has approved that execution shape.
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the
   ledger append-only.

---

## 1. Sprint goal

Sprint 10 ships **one feature** (SDD-040) covering **two defects**:

1. **Stale active-focus heuristic.** Owner observed 2026-06-10 (verbatim via
   EM): "Still says Active focus: azure-decommission (stale -- that wrapped
   up)." The current `state_builder.py` active-focus heuristic picks
   features by frontmatter alone and does not reflect what shipped most
   recently. Flip the signal to one based on commit recency, validation
   state, or some combination -- to be decided in CLARIFY.
2. **Static dashboard page.** Owner observed in the same message: "Static
   -- refreshes only when you re-run state_builder.py." Today the page
   only updates when the CLI is invoked manually. Add a serve-mode
   auto-refresh mechanism. Stdlib-only (Article V): no `watchdog`, no
   `flask`. Acceptable mechanisms include polling, on-request refresh in
   the HTTP handler, stdlib file-mtime sweep, or Server-Sent Events --
   choice to be made in CLARIFY.

### Scope

- **Primary scope**: SDD-040 only.
- **Carry-forward visibility**: SDD-034 (content-shingle dedup upgrade),
  SDD-039 (Article VII wording clarification), and PI-4 housekeeping
  (domain-skill annotations + GH Actions Node.js deprecation bump) remain
  visible in BACKLOG. Do NOT pull any of them into Sprint 10.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-21: SDD-040 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect, with SW Dev task input | SDD-040 has two genuine design questions (active-focus signal and refresh mechanism) plus a stdlib-only constraint that needs explicit treatment. CLARIFY before any code. |
| 2 | F-22: IMPLEMENT + QA for SDD-040 | SW Dev + workers | Implementation only after the validation contract is locked. SDD-040 is small (one CLI + one HTTP handler + tests) -- single-session implementation, no fleet split needed. |
| 3 | F-23: Sprint 10 close + SPRINT-11 kickoff authoring | SW Dev + EM | Close Sprint 10, regenerate state with the new builder, request owner approval before push, and author `SPRINT-11-KICKOFF.prompt.md` for SDD-036. |

The EM may combine F-21 and F-22 into a single session if the owner approves
that execution shape (SDD-040 is small enough to be tractable end-to-end).
The default is sequential because CLARIFY needs to lock the refresh-mechanism
decision before implementation starts.

---

## 3. Likely CLARIFY surfaces

### SDD-040 -- state_builder.py parser fix + auto-refresh

- **Q-A: Active-focus signal source.** Should "active focus" be determined
  by (a) most recent commit touching `specs/<dir>/`, (b) validation
  incompleteness (any spec dir with REQUIRED items still unchecked), (c)
  sprint frontmatter (the currently-open sprint in `sprints/PI-N/`), or
  (d) some combination? Owner complaint shows that (c) alone is wrong --
  needs at least one runtime signal.
- **Q-B: Auto-refresh mechanism.** Stdlib-only (Article V) rules out
  `watchdog` and `flask`. Choose among: (a) polling refresh inside the
  HTTP handler (client polls, server re-renders), (b) periodic stdlib
  file-mtime sweep on a background thread (server re-renders when mtimes
  change), (c) server-side render-on-request (every request rebuilds
  state -- cheapest, may be slow on cold cache), or (d) Server-Sent
  Events (`text/event-stream` push from server). Polling and on-request
  refresh are the lowest-complexity options.
- **Q-C: Refresh cadence.** If polling is chosen, what is the cadence
  (every 1 second? 5 seconds? on-demand only via HTTP request)? Cadence
  must balance freshness with CPU cost on the developer's laptop.
- **Q-D: Stdlib constraint (Article V).** Confirm the implementation uses
  only `urllib`, `http.server`, `os.path`, `sqlite3`, and other stdlib
  modules already imported by `state_builder.py`. Reject any proposal
  that adds `watchdog`, `flask`, `fastapi`, or `requests`. If a stdlib
  watcher is needed, it must be a polling/mtime construct, not an OS-level
  inotify subscription.
- **Q-E: Backwards compatibility for non-serve invocation.** Confirm that
  `python state_builder.py` (without `serve`) still writes static
  `state.md` and `state.html` files to `exec/` for git/diff use. Auto-
  refresh must be a serve-mode-only behavior; the CLI form must not
  change.

CLARIFY must also explicitly decide whether SDD-040 needs an ADR. Default
answer: no -- the active-focus heuristic and refresh mechanism are
implementation choices inside an existing CLI surface, not new
constitutional or governance ground. Escalate to ADR only if CLARIFY
surfaces a constitutional question (e.g., a refresh mechanism that touches
Article V's stdlib-only rule).

---

## 4. Hard constraints

- **No silent REQUIRED deferral.** Sprint 10 inherits the Sprint 7, 8, 9
  rule: if a REQUIRED item cannot close, the feature or sprint does not
  close.
- **Pre-push approval is mandatory.** Sprint 8 made this explicit; Sprint 9
  reinforced it. Record owner approval status before any push, and never
  infer approval from green tests.
- **Stdlib-only CLI is binding (Article V).** Implementation MUST follow
  `docs/CLI-PATTERN.md` and use only stdlib modules. No `watchdog`,
  `flask`, `fastapi`, `requests`, or any other non-stdlib dependency for
  auto-refresh.
- **No constitution edit without ADR and owner approval.** SDD-040 should
  not require a constitution edit. If CLARIFY surfaces one, draft the ADR
  first, route to owner, and split the constitution work into its own
  feature.
- **Preserve unrelated dirty work.** Stage explicit Sprint 10 paths only.
  The owner has approved this discipline pattern across Sprints 7-9.
- **Do not absorb SDD-036, SDD-037, or SDD-038.** Those are Sprint 11,
  Sprint 12, and Sprint 13 (contingency) work. Sprint 10's scope is
  exactly SDD-040.
- **Do not close PI-6 automatically.** F-23 closes Sprint 10 only;
  PI-6 close happens after Sprint 12 (or Sprint 13 if pulled in) with
  explicit owner approval.

---

## 5. Sprint close criteria

Sprint 10 closes DONE when all of the following are true:

1. SDD-040 validation contract is 100% REQUIRED checked. No silent
   deferral.
2. Full test suite passes at or above the PI-5 close baseline:
   `python -m pytest spec-driven-development/ --tb=no -q` returns >= 337
   passed with the known 2 platform-conditional skips.
3. Schema lint exits 0:
   `python spec-driven-development/cli/schema_lint.py`.
4. BACKLOG marks SDD-040 DONE with the commit chain.
5. `sprints/PI-6/CURRENT_PI.md` marks Sprint 1 (Sprint 10) CLOSED with
   date, commit chain, tests, validation, ADRs (if any), and retro
   paragraph. PI-6 remains ACTIVE; Sprint 11 (SDD-036) is the next
   planned sprint.
6. `exec/state.md`, `exec/state.html`, and `exec/work-index.md` are
   regenerated with `python spec-driven-development/cli/state_builder.py`.
   **The regenerated state.md must NOT say "Active focus:
   azure-decommission" -- this is the smoke test for the parser fix.**
7. `exec/sprint-progress.md` has `### Sprint 10 -- CLOSED` appended.
8. `SPRINT-11-KICKOFF.prompt.md` is authored under
   `spec-driven-development/feature-prompts/` and the README index is
   updated to reference it.
9. Serve-mode auto-refresh behavior is manually verified (start
   `python state_builder.py serve`, edit a file under `specs/`,
   confirm the dashboard refreshes without a manual CLI re-run).
   Record the verification in the sprint close block.
10. Owner approval is requested and recorded before any push.

---

## 6. Reporting template

Append this at Sprint 10 close:

```markdown
### Sprint 10 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-21, F-22, F-23
- Commits: <list>
- Tests: 337 -> N (>= 337 required)
- Schema lint: clean
- Validation: SDD-040 N/N REQUIRED + N/N OPTIONAL + N/N manual
- ADRs: <list or none>
- PI-6 status: ACTIVE; Sprint 11 (SDD-036) is the next planned sprint
- SDD-040: DONE (<one-sentence summary of active-focus signal source + refresh mechanism>)
- Smoke test: regenerated state.md no longer says "Active focus: azure-decommission" -- now says <new active focus>
- Serve-mode auto-refresh verification: PASS (<short description of manual test>)
- Carry-forward: SDD-034, SDD-039, PI-4 housekeeping remain open; SDD-036 + SDD-037 + SDD-038 remain PI-6 candidates per CURRENT_PI.md
- Owner ratification: REQUIRED BEFORE PUSH; <pending or approved with evidence>
- Notes: <one paragraph with Sprint 10 lessons>
- Next: SPRINT-11-KICKOFF.prompt.md authored at <path>; SDD-036 (lifecycle pipeline + drag-to-reorder w/ safeguards) is the Sprint 11 anchor
```

---

## 7. Do NOT do

- Do NOT start Sprint 10 until the HARD PREREQUISITE passes (especially
  prereq 1: PI-5 close at `8417818`).
- Do NOT close PI-6 in Sprint 10. PI-6 close is a separate owner-approved
  decision after Sprint 12 (or Sprint 13 if pulled in).
- Do NOT mark any REQUIRED item done without evidence.
- Do NOT push without explicit owner approval.
- Do NOT absorb SDD-036, SDD-037, or SDD-038 into Sprint 10. Those are
  Sprints 11, 12, and 13.
- Do NOT introduce `watchdog`, `flask`, `fastapi`, `requests`, or any
  non-stdlib dependency for auto-refresh. Article V is binding.
- Do NOT change the behavior of `python state_builder.py` (non-serve
  invocation). It must continue to write static `state.md` + `state.html`
  for git/diff use.
- Do NOT absorb unrelated dirty work (SDD-035 Azure decommission docs,
  workflow files, etc.) into Sprint 10 commits.
