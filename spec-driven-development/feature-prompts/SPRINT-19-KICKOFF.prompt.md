# SPRINT 19 KICKOFF -- PI-8 Sprint 2 / Doc-freshness sweep + stale-doc guard

You are leading **Sprint 19**, which is **PI-8 Sprint 2** -- the second sprint of
**PI-8 ("Truth in the Window")**. Sprint 18 fixed the loudest lie: the dashboard
now tells the truth (closed features render DONE, closed PIs render 100%, PI-7 is
no longer flagged current). But the docs a teammate reads at session start still
disagree with the repo -- the tracker is frozen at "PI-3 / 60 tests," INSTRUCTIONS
and ONBOARDING say "10 articles" (it is 12), and CONTEXT.md says "four Principal
agents" (it is five roles since the two-tier EM). Sprint 19 refreshes those four
docs to match reality **and** adds an automated check so the rot cannot return
silently. Your job is to ship one anchor feature (SDD-051) and leave PI-8 ready to
continue to Sprint 20:

1. **SDD-051** -- Doc-freshness sweep + automated stale-doc guard (audit spec
   source
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   Section 4): **(1)** refresh the four stale session-start docs
   (`docs/HIGH_LEVEL_DEV_TRACKER.md`, `INSTRUCTIONS.md`,
   `docs/ONBOARDING_KICK_OFF.md`, `CONTEXT.md`) so their PI / test / article /
   role counts match the live repo (PI-7 closed / PI-8 active, 576 tests, 12
   articles, two-tier EM = five roles, 24 ADRs); **(2)** add an automated
   stale-doc check to `doctor` / lint that flags a session-start doc carrying a
   stale hardcoded PI / test / article count, so drift is caught mechanically
   going forward. CLARIFY assigns per-item SDD-IDs as needed, each with its own
   `validation.md` from the audit Section 4 Acceptance block.

**Closing Sprint 19 does NOT close PI-8.** Sprint 19's close produces a
sprint-close summary and continues PI-8 to Sprint 20; the PI-8 CLOSE is a
separate, owner-approved decision taken after the final PI-8 sprint.

Do NOT pull in any other PI-8 work: **SDD-052** (roadmap repair + status backfill
+ the PI-7 4-feature checklist backfill, Sprint 20) and the Sprint 21 owner-pick
slice (**SDD-049** file-overlap detector or **SDD-041 Option B** reorder
re-optimization) are NOT in Sprint 19. **SDD-035** (Azure decommission) remains
out-of-band.

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
- The Sprint EM **cannot create sprints or PIs** -- it may only SUGGEST to the
  project EM. At sprint close it produces a sprint-close summary and **reports UP
  to the project Executive Manager**, who folds it into project-wide state and
  owns the owner conversation.
- Human-facing output from the Sprint EM is **short and plain** (SDD-044). Save
  the detail for agent-to-agent handoffs.

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-051 (including the
stale-doc check mechanism and where it lives). The Principal Software Developer
owns implementation, QA, and the Sprint 19 close (reporting up to the project EM
through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 19 must not start until all checks are true:

1. **Sprint 18 is CLOSED and pushed.** Confirm Sprint 18 (PI-8 Sprint 1,
   Dashboard truth) CLOSED at commit `2cafe8b` with SDD-050 (and any per-item
   IDs) marked DONE in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md), and that
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) marks PI-8
   **ACTIVE** (`status: active`, flipped from `draft` as Sprint 18's first act).
   On the regenerated dashboard, every closed PI reads done / 100%, closed DONE
   features render DONE, and PI-7 is not flagged current.
2. **Tests are green at the Sprint 18 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **576 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint and origin lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0 and
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files.
4. **`doctor` is green and CI is green.** The health set passes: `doctor` reports
   green, and the GitHub Actions CI workflow (B-4) is green on the `2cafe8b`
   head. The Article X lock guard (`TestS1FootprintLockGuard`) is PASS at this
   baseline.
5. **SDD-051 is filed and allocated to Sprint 19.** Confirm the SDD-051 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-8 Sprint 19.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   exists; SDD-051's per-item `validation.md` files are built from its Section 4
   "Acceptance (Doc staleness)" block.
7. **The live PI-7/PI-8 gates apply to Sprint 19.** The mandatory-ledger close
   gate (B-1) is LIVE -- Sprint 19's own dispatch outcomes must be logged in the
   ledger before Sprint 19 can be stamped DONE. The blocking checks (B-2: TDD
   gate + DONE-completeness) and CI (B-4) are LIVE -- Sprint 19 must pass them.
8. **Owner has approved the Sprint 19 start** (via the Executive Manager).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 19 on a
red test baseline (< 576), an unpushed/mismatched Sprint 18 (not closed at
`2cafe8b`), a red `doctor` / origin lint / CI, a broken Article X lock, a backlog
that accidentally closed SDD-051, PI-8 not marked ACTIVE, or without recorded
owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 19 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

PI-8 is already ACTIVE (Sprint 18 flipped it). There is no PI-activation step in
Sprint 19; the current-PI dispatch-rows check (B-1) is satisfied by logging
Sprint 19's own dispatches into the ledger.

---

## 1. Sprint goal

Sprint 19 ships **one anchor feature** (SDD-051) that makes the session-start docs
tell the truth **and keeps them honest mechanically.** After Sprint 19 a teammate
who reads the onboarding docs sees the live counts (PI-7 closed / PI-8 active,
576 tests, 12 articles, five roles, 24 ADRs) -- not "PI-3 / 60 tests / 10
articles / four Principals." And a teammate who plants a stale count on purpose in
a session-start doc watches the new `doctor` check go red. The design principle
from the audit is the durable fix: **docs that avoid hardcoded counts do not rot**
-- root `README.md` is the good pattern. Where practical, the refreshed docs
should stop hardcoding counts and point at the live dashboard / state; the
stale-doc check backstops the ones that still carry a count.

### Scope

- **SDD-051 -- refresh the four stale docs**: bring
  `docs/HIGH_LEVEL_DEV_TRACKER.md`, `INSTRUCTIONS.md`,
  `docs/ONBOARDING_KICK_OFF.md`, and `CONTEXT.md` into agreement with the live
  repo:
  - `docs/HIGH_LEVEL_DEV_TRACKER.md` (worst offender, onboarding read #3): frozen
    at "PI-3" and "60 tests" -> reflect 7 PIs closed / PI-8 active and the live
    576-test baseline.
  - `INSTRUCTIONS.md` (root): "10 binding articles" -> 12 articles.
  - `docs/ONBOARDING_KICK_OFF.md`: "10 articles" (appears twice) -> 12; the header
    still frames itself as "PI-3 kickoff" -> reframe to the current PI-8 reality.
  - `CONTEXT.md`: "four Principal agents" -> five roles (the two-tier EM added the
    Sprint EM).
- **SDD-051 -- add the automated stale-doc guard**: add a check to the `doctor`
  set (and/or a lint) that flags a session-start doc carrying a stale hardcoded
  PI / test / article count, so drift is caught mechanically. Two mechanisms are
  in play (CLARIFY decides which, per-claim):
  - **(a) verify-against-source** -- the check reads the live count (article
    count from `principles.md`, test count from the suite / a recorded baseline,
    PI/role count from the live source) and fails if a session-start doc's
    hardcoded count disagrees. Recommended where the live source is cheap to read.
  - **(b) flag-and-require-a-marker** -- the check flags any hardcoded
    PI/test/article count in a session-start doc unless the line carries an
    explicit "intentional/historical" marker. Recommended where verify-against-
    source is expensive or where the count is a legitimate historical reference.
- **SDD-051 -- prove the guard catches a real stale claim**: a test plants a
  deliberate stale count in a session-start doc (or a fixture) and asserts the
  check goes RED, per the audit Acceptance "proven by a deliberate red."
- **Per-item SDD-IDs**: CLARIFY assigns a per-item SDD-ID to each distinct surface
  as needed (e.g., doc-refresh vs. the guard), each with its own `validation.md`
  built from the audit Section 4 "Acceptance (Doc staleness)" block.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1) applies
  to **this sprint's own dispatches**. Sprint 19's own dispatch outcomes must be
  in the ledger before Sprint 19 can be stamped DONE.

### The clean docs -- verify only, do NOT touch

The audit marks two docs CLEAN. **Verify** they are still clean, then leave them:

- `docs/RULES.md` -- already lists articles I-XII (the B-3 fix landed). Do not
  edit; just confirm it still reads I-XII.
- root `README.md` -- carries no hardcoded counts (the good "no hardcoded count"
  pattern the refreshed docs should emulate). Do not edit.

If a "clean" doc turns out to carry a stale count on inspection, file a
clarification and surface it -- do not silently expand scope.

### The stale-doc check placement -- CLARIFY decides (READ THIS)

The audit says "add a `doctor` / lint check." Where the check physically lives is
a CLARIFY decision with three shapes:

- **In `doctor`** (`cli/bootstrap.py run_doctor`) as a new lettered check tuple
  `(label, ok, detail)` alongside the existing ledger / schema_lint / governance /
  origin-token / tests / TDD-gate / DONE-completeness checks. This wires it into
  CI automatically (the `doctor` set is the single source of truth for CI).
- **In `schema_lint.py`** if the check is better modeled as a lint pass.
- **In a new `origin_lint`-style stdlib CLI** (e.g. `cli/staledoc_lint.py` with a
  `main(argv)` signature) that `doctor` then calls, mirroring how `origin_lint`
  and `governance_check` plug in.

Default recommendation: implement the logic in a small dedicated module and **wire
it into the `doctor` set** so CI enforces it without a separate step. CLARIFY
settles the exact home and the module boundary.

### Explicit exclusions

- **SDD-052** (roadmap repair + PI-6 backfill + PI-8 roadmap entry + the PI-7
  4-feature checklist backfill + the six spec-dir `status:` lines) is Sprint 20
  and is NOT in Sprint 19. That includes the known carry from Sprint 18: 4 of the
  6 PI-7 features (SDD-043/044/045/048) are genuinely DONE but their per-folder
  checklists were never ticked -- backfilling those checklists is **SDD-052**, not
  Sprint 19's job.
- **SDD-049** (true file-overlap detector) and **SDD-041 Option B** (reorder ->
  backend re-optimization) are Sprint 21 owner-pick candidates and are NOT in
  Sprint 19.
- **PI-6 carryovers** (SDD-038 / SDD-034 / SDD-042 / SDD-039, PI-4 housekeeping)
  are NOT in Sprint 19.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 19 scope.
- **Article X locked render functions** are out of scope. SDD-051 touches docs and
  a check module; it does NOT touch `render_html`, `render_markdown`, or any
  locked function. `TestS1FootprintLockGuard` stays GREEN.
- **PI-8 close**: closing PI-8 is a separate owner-approved decision AFTER the
  final PI-8 sprint. Sprint 19 continues PI-8 to Sprint 20; it does not close
  PI-8.

### Constitution note -- the target docs are NOT gated

The four docs Sprint 19 refreshes -- `docs/HIGH_LEVEL_DEV_TRACKER.md`,
`INSTRUCTIONS.md`, `docs/ONBOARDING_KICK_OFF.md`, `CONTEXT.md` -- are **NOT**
`constitution/**` files, so **no ADR / version bump is required** to refresh them
(they are docs, not the constitution). If CLARIFY finds that a needed refresh
actually lands inside `constitution/**` (e.g. a count baked into
`principles.md`), that edit becomes a Level-2 gated change (ADR + recorded owner
approval + version bump) -- surface it; do not edit `constitution/**` silently.
The stale-doc check reads counts from `constitution/**` (e.g. the article count in
`principles.md`) but must NOT modify it.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-50: SDD-051 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs, builds each `validation.md` from the audit Section 4 Acceptance block, **decides the stale-doc check mechanism** (verify-against-source (a) vs flag-and-require-a-marker (b), per-claim), **decides where the check lives** (doctor vs schema_lint vs new `origin_lint`-style CLI), settles **how to avoid false positives** on legitimate historical count references, and settles **whether the refreshed docs stop hardcoding counts** (the durable fix -- point at the live dashboard/state) or keep a count backed by the guard. If any refresh turns out to land in `constitution/**`, that fork is surfaced here (gated). |
| 2 | F-51: SDD-051 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. Refresh the four stale docs to reality (PI-7 closed / PI-8 active, 576 tests, 12 articles, five roles, 24 ADRs); add the stale-doc check module and wire it into the `doctor` set (and CI); add the test that plants a deliberate stale count and asserts the check goes RED. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. `TestS1FootprintLockGuard` stays GREEN; no locked function touched. |
| 3 | F-52: Sprint 19 close | Sprint EM + SW Dev | Close Sprint 19, regenerate state, run the doc-freshness smoke test (the four docs read live counts; the new check goes RED on a planted stale claim and GREEN on the refreshed tree), request owner pre-push approval, mark SDD-051 (and the per-item IDs) DONE, and produce the sprint-close summary. The Sprint EM reports UP to the project Executive Manager and confirms PI-8 continues to Sprint 20. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph that proves no two workers modify the same file. Shared
surfaces -- the stale-doc check module, `cli/bootstrap.py`, `cli/schema_lint.py`,
any refreshed doc, generated exec surfaces, or shared spec artifacts -- force
serialization. (Note: the only conflict mechanism is the serial CLARIFY/SPEC gate;
there is no file-overlap detector -- SDD-049 remains a Sprint 21 candidate.)

---

## 3. Likely CLARIFY surfaces

### Q-A -- stale-doc check mechanism (verify-against-source vs flag-a-marker)

Decide, per count kind, whether the check **verifies against the live source**
(reads the article count from `principles.md`, the test count from the suite / a
recorded baseline, the PI/role count from the live source, and fails on a
mismatch) or **flags any hardcoded count unless marked** (fails on any hardcoded
PI/test/article count in a session-start doc unless the line carries an explicit
intentional/historical marker). Default recommendation: **verify-against-source
where the live source is cheap to read** (article count from `principles.md` is
cheap and exact); **flag-and-require-a-marker where verify-against-source is
expensive or brittle** (e.g. a moving test count). Surface the per-claim choice to
the owner.

### Q-B -- where the check lives

Decide the check's home. Default recommendation: implement the logic in a small
dedicated stdlib module and **wire it into the `doctor` set** (a new lettered
check tuple in `run_doctor`) so CI enforces it automatically -- the `doctor` set
is the single source of truth for CI. Alternatives: a `schema_lint` pass, or a new
`origin_lint`-style `cli/staledoc_lint.py` with a `main(argv)` signature that
`doctor` calls. Surface the module boundary and the wiring to the owner.

### Q-C -- avoiding false positives on legitimate historical counts

Confirm how the check avoids flagging legitimate historical count references
(e.g. "PI-3 shipped 60 tests" as a factual history line, or a count inside a
quoted retro). Default recommendation: scope the check to the **session-start doc
set** named in the audit (the docs a teammate reads first), and honor an explicit
inline marker for intentional/historical counts so a true history line does not
trip the guard. Surface the doc set and the marker convention to the owner.

### Q-D -- stop hardcoding counts (the durable fix) vs keep-count-plus-guard

Decide whether the refreshed docs should **stop hardcoding counts entirely** and
point at the live dashboard / `exec/state.md` (the root `README.md` good pattern,
which cannot rot), or **keep a count backed by the guard**. Default
recommendation: **stop hardcoding where the count adds no onboarding value** and
point at the live source; keep a count only where a concrete number genuinely
helps a first read, and back it with the guard. Surface which docs go count-free
vs count-plus-guard to the owner.

### Q-E -- the live counts to write

Lock the exact live counts the refreshed docs must carry so the sweep is
consistent: **7 PIs closed / PI-8 active**, **576 tests** (2 skipped), **12
articles**, **five roles** (four Principals + the Sprint EM), **24 ADRs**. Default
recommendation: verify each number against the live source at IMPLEMENT time (the
count may have moved since kickoff) rather than trusting the kickoff literal.
Surface the verified count set to the owner before writing.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` and the stale-doc check use argparse,
  sqlite3, pathlib, json, sys, os, re only. Sprint 19 adds NO third-party Python
  dependency.
- **Article X locked render functions are immutable.** Sprint 19 does NOT touch
  `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, or `load_decisions`. `TestS1FootprintLockGuard` stays
  GREEN. Touching a locked function is an Article X re-baseline (ADR + owner
  approval, Level-2) and is NOT expected for Sprint 19.
- **The stale-doc guard is behavior-additive, tested.** The new check is covered
  by a test that plants a deliberate stale count and asserts a RED; the existing
  suites keep passing. New behavior without a test is a Level-1 review fail.
- **Do not regress the `doctor`/CI set.** Wiring the new check into `doctor` must
  keep the health set green on the refreshed tree; the new check goes RED only on
  a genuine stale claim, not on the clean refreshed docs.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 19's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 19 must pass the TDD
  gate and DONE-completeness checks and keep CI green; a change that breaks an
  enforced rule must fail loudly.
- **Constitution edits are gated.** No `constitution/**` change without an ADR +
  recorded owner approval + a version bump. The four target docs are NOT
  constitution files (no ADR needed); if CLARIFY finds a refresh lands inside
  `constitution/**`, surface it -- do not edit silently. The stale-doc check
  reads counts from `constitution/**` but must not modify it.
- **Do NOT touch the clean docs.** `docs/RULES.md` and root `README.md` are
  verified-only; leave them unchanged.
- **Spec source is authoritative but stale-checked.** Build SDD-051's per-item
  `validation.md` from the audit Section 4 "Acceptance (Doc staleness)" block, but
  verify each stale claim against the live doc before acting (a count may have
  been fixed already). If an item is wrong on inspection, file a clarification and
  surface it -- do not silently drop it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044).** All human-facing output in this
  sprint (status, progress, questions to the owner) is short and plain;
  agent-to-agent detail may stay detailed. The Sprint EM holds this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Do NOT scrub history.** Sprint 19 refreshes forward-looking session-start
  docs; it does not rewrite historical `specs/`, `sprints/`, retros, or ADRs. A
  count inside a historical record stays as written.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 19 closes only when all are true:

1. **The four stale docs now match reality**: `docs/HIGH_LEVEL_DEV_TRACKER.md`
   (no "PI-3" / "60 tests"), `INSTRUCTIONS.md` (12 articles, not 10),
   `docs/ONBOARDING_KICK_OFF.md` (12 articles, not 10; header reframed off "PI-3
   kickoff"), and `CONTEXT.md` (five roles, not "four Principal agents") read the
   live counts (7 PIs closed / PI-8 active, 576 tests, 12 articles, five roles,
   24 ADRs).
2. **The automated stale-doc check exists and is wired**: a stale-doc check
   flags a session-start doc carrying a stale hardcoded PI / test / article count,
   and it is wired into the `doctor` set (and therefore CI) per the CLARIFY
   placement decision.
3. **A test proves the guard catches a real stale claim**: a test plants a
   deliberate stale count in a session-start doc (or fixture) and asserts the
   check goes RED (the audit "proven by a deliberate red"); the check is GREEN on
   the refreshed tree.
4. **The clean docs are unchanged**: `docs/RULES.md` (still I-XII) and root
   `README.md` (still count-free) are byte-unchanged.
5. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual checks checked at close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 576
   passed, 2 skipped, and grows with the new stale-doc guard test.
7. Schema lint clean (exit 0) and origin lint clean (0 hits in generic files).
8. **Article X lock held**: `TestS1FootprintLockGuard` PASS; `render_html` /
   `render_markdown` and the four locked load_* functions are byte-identical.
9. **`doctor` green and CI green**: the health set (now including the stale-doc
   check) and the GitHub Actions workflow pass on the Sprint 19 head; the B-2
   blocking checks pass.
10. **Ledger shows real Sprint 19 rows**: the dogfood holds -- Sprint 19's own
    dispatches are in the ledger and the B-1 close gate is satisfied.
11. SDD-051 (and any per-item SDD-IDs) marked DONE in BACKLOG with evidence.
12. Owner pre-push approval recorded before any push.
13. **PI-8 continues to Sprint 20.** Sprint 19 does not close PI-8; the Sprint EM
    reports up to the project Executive Manager and confirms Sprint 20 is next.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 19 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-50, F-51, F-52
- Commits: <commit SHAs>
- Tests: 576 -> <N> (>= 576 required; new stale-doc guard test added)
- Schema lint: clean; origin lint: 0 hits in generic files
- Validation: SDD-051 per-item <r>/<r> REQUIRED + manual checks
- Docs refreshed: HIGH_LEVEL_DEV_TRACKER (no PI-3 / 60 tests), INSTRUCTIONS (12 articles), ONBOARDING_KICK_OFF (12 articles + header reframed), CONTEXT (five roles)
- Stale-doc guard: mechanism <verify-against-source (a) | flag-a-marker (b) | mixed>; home <doctor | schema_lint | staledoc_lint.py>; wired into doctor/CI
- Deliberate-red proof: planted stale count -> check RED; refreshed tree -> check GREEN -- <PASS | FAIL>
- Clean docs untouched: RULES.md (I-XII) + root README.md (count-free) byte-unchanged -- <YES>
- Durable fix: docs that dropped hardcoded counts and point at live source: <list | none>
- Per-item SDD-IDs assigned for SDD-051: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 19 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS); render_html / render_markdown untouched
- History preserved: YES (no historical specs/sprints/retros/ADRs rewritten)
- SDD-051: DONE (four docs refreshed + automated stale-doc guard wired + deliberate-red test)
- Deferred / out of scope: SDD-052 (S20, incl the PI-7 4-feature checklist backfill), Sprint 21 owner-pick (SDD-049 or SDD-041 Option B), SDD-035 out-of-band
- PI-8 status: ACTIVE -- Sprint 19 CLOSED; continues to Sprint 20
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 19 lessons>
- Next: Sprint 20 (SDD-052 roadmap repair + status backfill + PI-7 4-feature checklist backfill)
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close PI-8. Sprint 19 is the second PI-8 sprint; it continues PI-8 to
  Sprint 20. PI-8 CLOSE is a separate owner-approved decision after the final PI-8
  sprint.
- Do NOT pull in SDD-052 (Sprint 20) -- including the roadmap PI-6 backfill, the
  PI-7 header fix, the PI-8 roadmap entry, the six spec-dir `status:` lines, and
  the **PI-7 4-feature checklist backfill** (SDD-043/044/045/048). That backfill
  is SDD-052's job, not Sprint 19's.
- Do NOT pull in SDD-049, SDD-041 Option B, or the PI-6 carryovers.
- Do NOT edit, move, or rewrite the Article X locked functions (`render_html`,
  `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`). `TestS1FootprintLockGuard` stays
  GREEN.
- Do NOT touch `docs/RULES.md` or root `README.md` (verified-only; already clean).
- Do NOT edit `constitution/**` (roadmap, principles) as part of the doc refresh;
  the four target docs are not constitution files. If a refresh lands inside
  `constitution/**`, surface it as a Level-2 gated change -- do not edit silently.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently drop a SDD-051 audit item; if a stale claim no longer matches
  the live doc, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 19's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT scrub or rewrite history; a count inside a historical record stays.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-051 spec dir here -- F-50 does that inside the Sprint 19
  working sessions.
- Do NOT refresh any doc in this kickoff -- the refresh is F-51 inside the Sprint
  19 working sessions.
- Do NOT have the Sprint EM create a sprint or PI (or author the next kickoff) --
  it may only SUGGEST to the project EM and reports up at close.
