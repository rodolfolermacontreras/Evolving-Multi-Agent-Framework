# SPRINT 22 KICKOFF -- PI-9 Sprint 1 / Close PI-8, open PI-9, ship the experience pair

You are leading **Sprint 22**, the **first sprint of PI-9**. It does three things
in order: (1) **closes PI-8** ("Truth in the Window") -- owner-approved, all four
truth anchors DONE (dashboard truth SDD-050, doc freshness SDD-051, roadmap repair
SDD-052, comms truth SDD-053); (2) **opens PI-9** so exactly one PI carries the
`(current)` marker; and (3) ships the **two experience-and-safety items** the owner
prioritized next -- **SDD-049** (a real file-overlap conflict detector for fleet
dispatch) and **SDD-041 Option B** (backlog reorder that actually re-optimizes on
the backend, not just persists the visual order). After Sprint 22, PI-8 renders
closed / 100% with its carryovers tracked, PI-9 is the current PI, and both
experience items are live.

Deliverables, in order:

1. **PI-8 CLOSE** (owner-approved 2026-07-09) -- flip the `constitution/roadmap.md`
   PI-8 header from `(current)` to `(closed 2026-07-09)`, add the PI-8 close
   summary + carryover note (SDD-049 and SDD-041 Option B move to PI-9; any other
   open PI-8 candidates tracked as carryover), and flip
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) `status:
   active -> closed`. This applies the **existing** closed-PI convention (ADR-024,
   roadmap 1.2.0) -- it is documentation-consistency, **no new ADR expected** --
   but `roadmap.md` is `constitution/**`, so recorded owner approval before push
   is mandatory. The Architect confirms the no-ADR call at CLARIFY.
2. **PI-9 OPEN** -- add a `## PI-9: <theme> (current)` section to `roadmap.md`
   (exactly one `(current)` marker at a time -- PI-8 loses it, PI-9 gains it),
   create [`../sprints/PI-9/CURRENT_PI.md`](../sprints/PI-9/CURRENT_PI.md)
   (`status: active`) in the PI-8 shape, and log the first PI-9 ledger dispatch row
   so `doctor`'s current-PI dispatch-rows check (B-1) is satisfied for PI-9.
3. **SDD-049** -- true pre-dispatch file-overlap conflict detector (fleet safety).
4. **SDD-041 Option B** -- backlog reorder -> backend re-optimization (backlog UX);
   the PM assigns Option B a fresh SDD-ID at CLARIFY.

**Note on the pair:** SDD-041 Option B is user-facing backlog UX; SDD-049 is
fleet-dispatch safety (developer experience). Both were grouped by the owner as
high-value quality-of-life work -- PI-9's theme covers both honestly.

Do NOT pull in any other work: PI-6/PI-7/PI-8 carryovers (SDD-038 color tokens,
SDD-034 dedup, SDD-042 pill-nav, SDD-039 wording, etc.) stay tracked as carryover
and are NOT in Sprint 22. **SDD-035** (Azure decommission) remains out-of-band.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent -- the sprint-scoped
EM shipped in Sprint 14 (SDD-043 / ADR-020). It is NOT the project Executive
Manager.

- In the fresh session, **activate the `sprint-executive-manager` agent**
  ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md)),
  not `principal-executive-manager`.
- The Sprint EM coordinates exactly this one sprint. It **routes** feature work
  to the Principal Product Manager, Principal Architect, and Principal Software
  Developer, synthesizes their answers, and surfaces escalations. It makes NO
  product, technical, or implementation decisions itself (Level 0).
- The Sprint EM **cannot create sprints or PIs on its own authority** -- opening
  PI-9 here is the execution of an **owner-approved** decision carried in this
  kickoff, not a Sprint-EM-originated PI creation. At sprint close it produces a
  sprint-close summary and **reports UP to the project Executive Manager**.
- Human-facing output is **short and plain** (SDD-044) and every owner decision
  uses the **DECISION-REQUEST FORMAT** shipped in SDD-053 (dogfood it).

PM + Architect own CLARIFY / SPEC / PLAN / TASKS (including the PI-9 theme/name,
the no-ADR confirmation on the PI-8 close, and the Option B ID assignment). The
Principal Software Developer owns implementation, QA, and the Sprint 22 close.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 22 must not start until all checks are true:

1. **Sprint 21 is CLOSED and pushed.** Confirm Sprint 21 (PI-8 Sprint 4,
   decision-request format) CLOSED at commit `07a2296` (push head `37fbdd4` or
   later) with SDD-053 marked DONE in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md),
   and that [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) still
   marks PI-8 **ACTIVE** (Sprint 22 is what closes it).
2. **Tests are green at the Sprint 21 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **596 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint, origin lint, and stale-doc lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0,
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files, and `python spec-driven-development/cli/staledoc_lint.py`
   is green on the current tree.
4. **`doctor` is green and CI is green.** The health set passes and the GitHub
   Actions CI workflow (B-4) is green on the `37fbdd4` head. The Article X lock
   guard (`TestS1FootprintLockGuard`) is PASS at this baseline.
5. **The two features are filed and allocated to Sprint 22.** Confirm the SDD-049
   row in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN and allocated to
   PI-9 Sprint 22, and that SDD-041 Option B is co-allocated (the PM assigns Option
   B a fresh SDD-ID at CLARIFY).
6. **The live gates apply to Sprint 22.** The mandatory-ledger close gate (B-1)
   is LIVE -- Sprint 22's own dispatch outcomes (and the first PI-9 row) must be
   logged in the ledger before Sprint 22 can be stamped DONE. The blocking checks
   (B-2: TDD gate + DONE-completeness) and CI (B-4) are LIVE.
7. **Owner has approved the Sprint 22 start** (via the Executive Manager), which
   includes the PI-8 close and the PI-9 open.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start on a red test
baseline (< 596), an unpushed/mismatched Sprint 21, a red `doctor` / origin lint /
staledoc lint / CI, a broken Article X lock, or without recorded owner approval.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 22 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation.
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

---

## 1. Sprint goal

Sprint 22 closes PI-8 cleanly, opens PI-9, and ships two quality-of-life features:
the fleet finally has an automated file-overlap check before parallel dispatch
(no more relying on manual per-worker file scopes), and dragging a backlog item to
a new position actually re-optimizes the priority order on the backend instead of
only saving the visual arrangement. After Sprint 22 the dashboard shows PI-8 closed
/ 100%, PI-9 as the current PI, and both features live and tested.

### Scope

- **PI-8 close** (`constitution/roadmap.md` + `sprints/PI-8/CURRENT_PI.md`):
  header `(current)` -> `(closed 2026-07-09)`, PI-8 close summary + carryover note,
  `CURRENT_PI.md` `status: closed`. Applies ADR-024 closed-PI semantics; no new
  ADR; owner-approved constitution edit (gated).
- **PI-9 open** (`constitution/roadmap.md` + new `sprints/PI-9/CURRENT_PI.md`):
  `## PI-9: <theme> (current)` section; `CURRENT_PI.md` `status: active`; first
  PI-9 ledger dispatch row for the B-1 current-PI check. PM names the PI-9 theme
  at CLARIFY (candidate: "Experience Polish" -- backlog UX + dispatch safety).
- **SDD-049 -- file-overlap conflict detector**: build a real pre-dispatch check
  that reads each worker brief's declared IN-scope file set and blocks (or warns)
  when two briefs in the same batch intersect. Lives in the fleet dispatch path
  (`cli/fleet.py`, a leaf CLI -- NOT an Article X locked function). Stdlib-only,
  TDD (failing test first). Replaces the manual per-worker file-scope discipline
  with an automated gate.
- **SDD-041 Option B -- reorder backend re-optimization**: when a backlog item is
  dragged to a new position, feed the new order into the prioritization/
  optimization logic on the backend, not only the display-order overlay. Build on
  the existing safeguarded `move()` + `reorder-audit.jsonl` + dependency-lock
  machinery (ADR-017) from Option A -- same audit trail, same governance. CLARIFY
  pins the exact backend surface and confirms it does NOT touch any Article X
  locked render/load function (`TestS1FootprintLockGuard` stays GREEN).
- **Dogfood B-1**: Sprint 22's own dispatch outcomes plus the first PI-9 row must
  be in the ledger before close.

### The PI-8-close / PI-9-open roadmap edit is constitution-gated -- READ THIS

`constitution/roadmap.md` is a `constitution/**` file (Article VIII). The close
marker + PI-9 section apply the **existing** ADR-024 closed-PI convention (roadmap
1.2.0), so on precedent this is **documentation-consistency -- no new ADR and no
version bump expected**. The Architect confirms the no-ADR call at CLARIFY.
Recorded owner approval before push is mandatory regardless, and no worker edits
`roadmap.md` silently.

### Explicit exclusions

- **PI-6/PI-7/PI-8 carryovers** (SDD-038, SDD-034, SDD-042, SDD-039, etc.) stay
  tracked as carryover; they are NOT implemented in Sprint 22.
- **Azure decommission**: SDD-035 remains out-of-band.
- **Article X locked render functions** are out of scope. Neither feature touches
  `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, or `load_decisions`. `TestS1FootprintLockGuard` stays
  GREEN.
- **Do NOT scrub history.** Sprint 22 closes PI-8 forward-looking and adds PI-9; it
  does not rewrite historical `specs/`, `sprints/`, retros, ADRs, or frozen
  kickoff prompts.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-59: PI-8 close + PI-9 open | Sprint EM + Architect + SW Dev | Governance first. Apply the roadmap close marker + PI-9 section (Architect confirms no-ADR), flip CURRENT_PI, create PI-9 CURRENT_PI, log first PI-9 ledger row, regenerate the dashboard, run the close smoke test, and get owner pre-push approval on the constitution edit. |
| 2 | F-60: SDD-049 CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT + QA | PM + Architect design; SW Dev + workers | File-overlap detector in `cli/fleet.py`. TDD, stdlib-only, leaf CLI (no locked fn). |
| 3 | F-61: SDD-041 Option B CLARIFY -> ... -> IMPLEMENT + QA | PM + Architect design; SW Dev + workers | Reorder -> backend re-optimization on the existing safeguarded `move()`/audit machinery. CLARIFY pins the backend surface and confirms no locked-fn touch. PM assigns the Option B SDD-ID. |
| 4 | F-62: Sprint 22 close | Sprint EM + SW Dev | Close Sprint 22, regenerate state, verify PI-8 renders closed/100% and PI-9 is current, both features tested, get owner pre-push approval, mark the items DONE, produce the sprint-close summary, report up to the project EM. |

Default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph proving no two workers modify the same file -- and note the
irony that SDD-049 is the tool that will automate exactly this check. Shared
surfaces (`roadmap.md`, `CURRENT_PI.md`, the reorder backend, generated exec
surfaces) force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- PI-8 close is no-ADR documentation-consistency (Architect confirms)
The close marker + PI-9 section apply ADR-024's existing closed-PI convention.
Default recommendation: documentation-consistency, no new ADR, no version bump;
owner approval before push still mandatory. If CLARIFY finds a genuine new-rule
impact, STOP and escalate as Level-2. Surface the call.

### Q-B -- PI-9 theme / name
Name PI-9. Default recommendation: "Experience Polish" (covers user-facing backlog
UX + fleet-dispatch safety). Surface the name to the owner.

### Q-C -- SDD-049 block vs warn
Decide whether an overlap hard-blocks dispatch or warns. Default recommendation:
block by default with an explicit override flag (consistent with the force-as-
Level-2 governance in ADR-017), so the safe path is automatic and the override is
deliberate. Surface the choice.

### Q-D -- SDD-041 Option B backend surface + ID
Pin the exact backend re-optimization surface and confirm it stays off the Article
X locked functions. Default recommendation: extend the existing `move()`/audit
path; PM assigns Option B a fresh SDD-ID (next free, e.g. SDD-054). Surface the ID
and surface list.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** argparse, sqlite3, pathlib, json, sys, os, re only;
  vanilla JS for any browser code (no framework). No third-party Python dependency.
- **Article X locked render functions are immutable.** Neither feature nor the PI
  close touches a locked function. `TestS1FootprintLockGuard` stays GREEN.
- **`roadmap.md` is `constitution/**` -- gated.** No-ADR call is Architect-confirmed
  at CLARIFY; recorded owner approval before push is mandatory. No silent edits.
- **Exactly one `(current)` PI marker.** PI-8 loses it, PI-9 gains it, in the same
  edit. Marker text is load-bearing (`load_pis` reads "closed" vs "(current").
- **Do not regress the `doctor`/CI set.** Health set stays green after the close.
- **Live B-1 / B-2 / B-4 gates apply.** Log Sprint 22's dispatches + the first
  PI-9 row; pass the TDD gate + DONE-completeness; keep CI green.
- **No new gates / no silent REQUIRED deferral.** Surface any REQUIRED slip.
- **Dogfood SDD-044 + SDD-053.** Short, plain human-facing output; every owner
  decision uses the DECISION-REQUEST FORMAT.
- **Append-only ledger.** Report in `exec/sprint-progress.md` append-only.
- **Do NOT scrub history.**
- **Git discipline.** Explicit path staging only; never `git add -A` / `git add .`.
  Pre-push owner approval mandatory (doubly for the `roadmap.md` edit).

---

## 5. Close criteria (Definition of Done)

Sprint 22 closes only when all are true:

1. **PI-8 renders closed / 100%.** `roadmap.md` PI-8 header reads
   `(closed 2026-07-09)` with a close summary + carryover note; `CURRENT_PI.md`
   `status: closed`; the dashboard shows PI-8 done / 100% and NOT current.
2. **PI-9 is the current PI.** `roadmap.md` has a `## PI-9: <theme> (current)`
   section (exactly one `(current)` marker total); `sprints/PI-9/CURRENT_PI.md`
   exists (`status: active`); the first PI-9 ledger row is logged (B-1 satisfied
   for PI-9).
3. **SDD-049 shipped.** A real pre-dispatch file-overlap detector reads worker
   brief IN-scope file sets and blocks/warns on intersection, with tests.
4. **SDD-041 Option B shipped.** A backlog reorder re-optimizes on the backend via
   the safeguarded `move()`/audit path, with tests; PM-assigned SDD-ID marked DONE.
5. All per-item REQUIRED validation items checked with real evidence (100%
   REQUIRED); manual checks checked at close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 596
   passed, 2 skipped (grows with the new feature tests; must not regress).
7. Schema lint clean, origin lint clean (0 hits in generic files), stale-doc lint
   green.
8. **Article X lock held**: `TestS1FootprintLockGuard` PASS; locked render/load
   functions byte-identical.
9. **`doctor` green and CI green** on the Sprint 22 head; B-2 blocking checks pass.
10. **Ledger shows real Sprint 22 rows** plus the first PI-9 row; B-1 satisfied.
11. SDD-049 and SDD-041 Option B (PM ID) marked DONE in BACKLOG with evidence.
12. **Owner pre-push approval recorded before any push** -- explicitly covering the
    `constitution/roadmap.md` PI-8-close / PI-9-open edit.
13. **Reported up to the project Executive Manager**, who confirms PI-9 is the
    current PI and folds Sprint 22 into project-wide state.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 22 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-59, F-60, F-61, F-62
- Commits: <commit SHAs>
- Tests: 596 -> <N> (>= 596 required; must not regress)
- Schema lint: clean; origin lint: 0 hits in generic files; stale-doc lint: green
- PI-8 close: roadmap header (closed 2026-07-09) + close summary + carryover; CURRENT_PI status: closed; dashboard PI-8 100% / not current -- <PASS | FAIL>
- PI-9 open: roadmap PI-9 (current) section; sprints/PI-9/CURRENT_PI.md active; first PI-9 ledger row -- <PASS | FAIL>
- Roadmap edit gating: no-ADR documentation-consistency (Architect-confirmed); owner approval recorded before push -- <YES>
- SDD-049 file-overlap detector: <PASS | FAIL> (block/warn: <choice>)
- SDD-041 Option B (SDD-0NN) reorder -> backend re-optimization: <PASS | FAIL>
- Validation: <r>/<r> REQUIRED per item + manual checks
- Live gates satisfied: B-1 ledger (<N> Sprint 22 rows + PI-9 row), B-2, B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS)
- History preserved: YES
- Deferred / out of scope: PI-6/7/8 carryovers, SDD-035 out-of-band
- PI-9 status: ACTIVE -- current PI; PI-8 CLOSED
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 22 lessons>
- Next: PI-9 Sprint 2 (owner-directed) or PI-9 close decision
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close or open a PI on Sprint-EM authority alone -- the PI-8 close and PI-9
  open here execute an owner-approved decision carried in this kickoff.
- Do NOT edit `constitution/roadmap.md` silently. It is `constitution/**`: the
  no-ADR call is Architect-confirmed at CLARIFY, and recorded owner approval before
  push is mandatory.
- Do NOT leave zero or two `(current)` PI markers. PI-8 loses it and PI-9 gains it
  in the same edit.
- Do NOT pull in PI-6/7/8 carryovers or any work beyond SDD-049 + SDD-041 Option B.
- Do NOT edit, move, or rewrite the Article X locked functions. `TestS1FootprintLockGuard`
  stays GREEN.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates.
- Do NOT scrub or rewrite history.
- Do NOT push without recorded owner approval (doubly for the `roadmap.md` edit).
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the feature spec dirs here -- F-60/F-61 do that in-session.
- Do NOT have the Sprint EM author the next kickoff -- it may only SUGGEST to the
  project EM and reports up at close.
