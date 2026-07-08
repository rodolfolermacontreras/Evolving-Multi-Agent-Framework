# SPRINT 18 KICKOFF -- PI-8 Sprint 1 / Dashboard truth (fix stale detectors)

You are leading **Sprint 18**, which is **PI-8 Sprint 1** -- the first sprint of
**PI-8 ("Truth in the Window")**. PI-7 hardened the engine: the ledger is real,
the rules that matter block, CI fires for everyone, identity is config, and the
3082-line god-module is split (558 tests, `doctor` green). But the human-facing
surfaces still lie about that healthy engine -- a closed, DONE feature renders as
REVIEW or IMPLEMENT on the dashboard, and every closed PI shows a partial
percentage. Sprint 18 fixes the loudest lie: the dashboard's stage and
percentage detectors. Your job is to ship one anchor feature (SDD-050) and leave
PI-8 ready to continue to Sprint 19:

1. **SDD-050** -- Dashboard truth (audit spec source
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   Section 3): fix **Defect 1** (DONE features render as REVIEW/IMPLEMENT/TASKS --
   `detect_stage()` demands a per-spec-dir `RETRO.md` this framework keeps at
   PI/sprint level; the validation reader only reads a literal `validation.md` and
   is blind to split `validation-*.md` files; 5 of 6 PI-7 spec dirs still say
   `status: active`) and **Defect 2** (closed PIs show a partial percentage --
   `pct = done/total` has no "closed" concept, `is_current` matches
   `"(current, closed ...)"`, and PI-6 is missing from the roadmap). CLARIFY
   assigns per-item SDD-IDs as needed, each with its own `validation.md` from the
   audit Acceptance blocks.

**Closing Sprint 18 does NOT close PI-8.** Sprint 18's close produces a
sprint-close summary and continues PI-8 to Sprint 19; the PI-8 CLOSE is a
separate, owner-approved decision taken after the final PI-8 sprint.

Do NOT pull in any other PI-8 work: **SDD-051** (doc-freshness sweep, Sprint 19)
and **SDD-052** (roadmap repair + status backfill, Sprint 20) are NOT in
Sprint 18. The Sprint 21 owner-pick slice (**SDD-049** file-overlap detector or
**SDD-041 Option B** reorder re-optimization) is NOT in Sprint 18. **SDD-035**
(Azure decommission) remains out-of-band.

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

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-050 (including the
Defect-1 backfill placement and the Defect-2 dependency on the SDD-052 roadmap
backfill). The Principal Software Developer owns implementation, QA, and the
Sprint 18 close (reporting up to the project EM through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 18 must not start until all checks are true:

1. **PI-7 is CLOSED and pushed.** Confirm PI-7 (Hardening + Orchestration
   Maturity) CLOSED 2026-07-07 / DONE-WITH-CARRYOVER at commit `7088f35`, that
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) exists and
   marks PI-8 **DRAFTED / QUEUED** (`status: draft`) naming Sprint 18 as the
   first sprint, and that SDD-048 (with its
   C-1/C-2/C-3/D-2 per-item IDs) is marked DONE in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md). PI-8 is intentionally NOT
   yet `active`: activating it (flip to `status: active` + first ledger
   dispatch) is Sprint 18's first act (see §0), which keeps the post-PI-7-close
   interim invariant (no active PI, doctor green) true until Sprint 18 starts.
2. **Tests are green at the PI-7 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **558 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint and origin lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0 and
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files.
4. **`doctor` is green and CI is green.** The health set passes: `doctor` reports
   green, and the GitHub Actions CI workflow (B-4) is green on the `7088f35`
   head. The Article X lock guard (`TestS1FootprintLockGuard`) is PASS at this
   baseline.
5. **SDD-050 is filed and allocated to Sprint 18.** Confirm the SDD-050 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-8 Sprint 18.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   exists; SDD-050's per-item `validation.md` files are built from its Section 3
   "Acceptance" blocks (Defect 1 + Defect 2).
7. **The live PI-7 gates apply to Sprint 18.** The mandatory-ledger close gate
   (B-1) is LIVE -- Sprint 18's own dispatch outcomes must be logged in the
   ledger before Sprint 18 can be stamped DONE. The blocking checks (B-2: TDD
   gate + DONE-completeness) and CI (B-4) are LIVE -- Sprint 18 must pass them.
8. **Owner has approved the Sprint 18 start** (PI-8 launch, owner direction
   2026-07-08 via the Executive Manager: "yes, this is critical").

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 18 on a
red test baseline (< 558), an unpushed/mismatched PI-7 (not closed at `7088f35`),
a red `doctor` / origin lint / CI, a broken Article X lock, a backlog that
accidentally closed SDD-050, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. **Activate PI-8 (first act of Sprint 18).** Flip
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) from
   `status: draft` to `status: active` (and its body status line to ACTIVE),
   then log Sprint 18's first ledger dispatch. This is what makes `doctor`'s
   current-PI dispatch-rows check (B-1) green for PI-8 -- do it before running
   `doctor` in-sprint. Until this step PI-8 stays drafted by design.
5. Execute Sprint 18 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
6. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

---

## 1. Sprint goal

Sprint 18 ships **one anchor feature** (SDD-050) that makes the dashboard tell the
truth. A closed, DONE feature renders as DONE -- not REVIEW, IMPLEMENT, or TASKS.
A closed PI renders done / 100% -- not a partial percentage -- and the just-closed
PI-7 is not flagged as the current PI. The fix lives entirely in
`cli/state_builder_data.py`, the leaf data-assembly module split out of
`state_builder.py` in PI-7 (SDD-048). That module holds **no Article X locked
functions**, so the fix is lock-safe: `render_html` and `render_markdown` are not
touched and `TestS1FootprintLockGuard` stays GREEN. At close, the regenerated
dashboard renders SDD-043..048 as DONE (the smoke test), every closed PI reads
done / 100%, and the dashboard's definition of "done" agrees with
`cli/done_check.py` through a single source of truth.

### Scope

- **SDD-050 -- Defect 1 (DONE features render at an earlier stage)**: fix
  `detect_stage()` in `cli/state_builder_data.py` so it (a) treats a spec dir with
  frontmatter `status: done` and satisfied validation as DONE **without** demanding
  a per-spec-dir `RETRO.md` (retros live at PI/sprint level here); (b) globs
  `validation*.md` so split per-item validation files (`validation-A2.md`, etc.)
  count toward completeness. Backfilling the 5 stale `status: active` PI-7 spec-dir
  lines is in scope OR handed to SDD-052 -- decided at CLARIFY, done in ONE place.
- **SDD-050 -- Defect 2 (closed PIs show partial %)**: fix the PI percentage +
  current-PI logic in `cli/state_builder_data.py` so it (a) reads the
  `(closed YYYY-MM-DD)` marker on a PI header and renders that PI as done / 100%
  regardless of unchecked deferred/carryover boxes; (b) hardens `is_current` so
  `"(current, closed ...)"` does NOT count as current (the closed marker wins).
  PI-6 rendering depends on SDD-052's roadmap backfill -- resolve the dependency
  at CLARIFY (pull the roadmap-marker part earlier OR read closed-state
  defensively).
- **SDD-050 -- single source of truth for "done"**: reconcile `detect_stage()`
  with `cli/done_check.py` so the dashboard and `doctor` agree on what "done"
  means -- one shared definition read by both. If reconciling changes
  `done_check.py` behavior (it feeds the live B-2 gate), surface it at CLARIFY; it
  cannot regress silently.
- **Per-item SDD-IDs**: CLARIFY assigns a per-item SDD-ID to each distinct fix
  surface as needed, each with its own `validation.md` built from the audit
  Section 3 "Acceptance" blocks.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1) applies
  to **this sprint's own dispatches**. Sprint 18's own dispatch outcomes must be
  in the ledger before Sprint 18 can be stamped DONE.

### The lock-safety fact -- why Sprint 18 is safe (READ THIS)

C-1 (PI-7) split `state_builder.py` into sibling modules. The five Article X
LOCKED functions -- `render_html`, `load_sprint_table`, `load_sprint_goal`,
`detect_current_sprint`, `load_decisions` -- guarded by `TestS1FootprintLockGuard`
with golden SHA-256 hashes, live in the render / locked modules. **SDD-050's fix
is in `cli/state_builder_data.py`, a leaf module that contains NONE of the five
locked functions.** So Sprint 18 does its work without going anywhere near the
lock:

- **Do NOT touch** `render_html`, `render_markdown`, or any of the five locked
  functions. The stage/percentage detectors being fixed are in the data-assembly
  module, not the render wall.
- `TestS1FootprintLockGuard` must stay **GREEN** at close. If a fix appears to
  require touching a locked function, STOP and surface it via the Sprint EM -- do
  not silently edit, move, or rewrite a locked function. Touching one is an
  Article X re-baseline (ADR + owner approval, Level-2) and is NOT expected for
  Sprint 18.

**A worker must NEVER silently edit, move, or rewrite a locked function.**

### The SDD-052 dependency -- #1 sequencing risk (READ THIS)

SDD-050's closed-PI fix reads the `(closed)` marker on roadmap PI headers, and
PI-6 rendering needs PI-6 to exist in `constitution/roadmap.md`. But the roadmap
PI-6 backfill + closed markers are **SDD-052 (Sprint 20)**. Sprint 18 must not
hard-block on Sprint 20. CLARIFY resolves this with two options:

- **Option (a) -- read closed-state defensively (default).** SDD-050 reads the
  `(closed)` marker where present and tolerates a roadmap that has not yet been
  backfilled, so it ships in Sprint 18 without waiting on SDD-052. PI-6 renders
  correctly once SDD-052 backfills it in Sprint 20.
- **Option (b) -- pull the roadmap-marker part of SDD-052 earlier.** If the owner
  and Architect prefer, the minimal roadmap `(closed)`-marker + PI-6 stub part of
  SDD-052 is pulled into Sprint 18 as a small, gated `constitution/**` edit (ADR +
  owner approval + version bump). Default is (a); (b) only with the gating.

**The Architect resolves this at Sprint 18 CLARIFY.** Default (a).

### Explicit exclusions

- **SDD-051** (doc-freshness sweep + stale-doc `doctor` check) is Sprint 19 and is
  NOT in Sprint 18.
- **SDD-052** (roadmap repair + status backfill + PI-8 roadmap entry) is Sprint 20
  and is NOT in Sprint 18 -- EXCEPT the optional minimal roadmap-marker pull-in
  under CLARIFY option (b), gated by ADR + owner approval.
- **SDD-049** (true file-overlap detector) and **SDD-041 Option B** (reorder ->
  backend re-optimization) are Sprint 21 owner-pick candidates and are NOT in
  Sprint 18.
- **PI-6 carryovers** (SDD-038 / SDD-034 / SDD-042 / SDD-039, PI-4 housekeeping)
  are NOT in Sprint 18.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 18 scope.
- **PI-8 close**: closing PI-8 is a separate owner-approved decision AFTER the
  final PI-8 sprint. Sprint 18 continues PI-8 to Sprint 19; it does not close
  PI-8.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-47: SDD-050 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs, builds each `validation.md` from the audit Section 3 Acceptance blocks, **decides the Defect-1 backfill placement** (Sprint 18 vs SDD-052 -- one place), **resolves the Defect-2 dependency on the SDD-052 roadmap backfill** (default (a) read closed-state defensively vs (b) pull the roadmap-marker part earlier), and settles the **single-source-of-truth reconciliation** between `detect_stage()` and `done_check.py` (surface any `done_check.py` behavior change -- it feeds B-2). Any roadmap pull-in (option (b)) is a gated `constitution/**` edit drafted here with owner approval. |
| 2 | F-48: SDD-050 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. The fix lands in `cli/state_builder_data.py` (leaf module -- NO Article X locked functions); the stage detector drops the per-dir RETRO requirement and globs `validation*.md`; the percentage/current-PI logic reads the `(closed)` marker and hardens `is_current`; the "done" definition is reconciled with `done_check.py`. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. `TestS1FootprintLockGuard` stays GREEN; `render_html` / `render_markdown` untouched. |
| 3 | F-49: Sprint 18 close | Sprint EM + SW Dev | Close Sprint 18, regenerate state, run the DONE-features smoke test (SDD-043..048 render DONE; closed PIs render 100%), request owner pre-push approval, mark SDD-050 (and the per-item IDs) DONE, and produce the sprint-close summary. The Sprint EM reports UP to the project Executive Manager and confirms PI-8 continues to Sprint 19. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `cli/state_builder_data.py`, `cli/done_check.py`, `cli/schema_lint.py`,
`constitution/**`, the spec template surfaces, generated exec surfaces, or shared
spec artifacts -- force serialization. (Note: the only conflict mechanism is the
serial CLARIFY/SPEC gate; there is no file-overlap detector -- SDD-049 remains a
Sprint 21 candidate.)

---

## 3. Likely CLARIFY surfaces

### Q-A -- Defect-1 stale `status:` backfill placement

Decide where the 5 (or 6) stale `status: active` -> `done` spec-dir frontmatter
lines get backfilled. Default recommendation: **do it in ONE place** -- either in
SDD-050 (Sprint 18) alongside the detector fix, or hand it to SDD-052 (Sprint 20)
with the rest of the status/roadmap backfill. Do NOT do it in both. If the
dashboard fix should demonstrate DONE rendering on real spec dirs at Sprint 18
close, backfill here; otherwise defer to SDD-052. Surface the choice to the owner.

### Q-B -- Defect-2 dependency on the SDD-052 roadmap backfill

Decide how SDD-050's closed-PI fix handles the missing PI-6 roadmap section
(backfilled in SDD-052 / Sprint 20). Default recommendation: **option (a) -- read
closed-state defensively.** SDD-050 reads the `(closed)` marker where present and
tolerates a not-yet-backfilled roadmap, so Sprint 18 ships without blocking on
Sprint 20; PI-6 renders once SDD-052 lands. Option (b) -- pull the minimal roadmap
`(closed)`-marker + PI-6 stub part of SDD-052 into Sprint 18 -- is a gated
`constitution/**` edit (ADR + owner approval + version bump) and is recommended
ONLY if the owner wants PI-6 rendering complete at Sprint 18 close. Default (a).

### Q-C -- single source of truth for "done"

Decide how `detect_stage()` and `cli/done_check.py` share one definition of
"done." Default recommendation: extract a single shared helper/definition that
both call, so the dashboard and `doctor` cannot disagree. If reconciling changes
`done_check.py` behavior (it feeds the live B-2 blocking check), surface the
change explicitly -- it must not regress the gate silently. Surface the shared-
definition shape to the owner.

### Q-D -- `RETRO.md` requirement removal scope

Confirm that dropping the per-spec-dir `RETRO.md` requirement for `status: done`
does not lose a signal the dashboard actually needs. Default recommendation: drop
it for the DONE determination (retros live at PI/sprint level here) but keep
rendering a per-dir retro link IF one exists -- remove the requirement, not the
capability. Surface the behavior to the owner.

### Q-E -- validation glob shape

Lock the glob that picks up split validation files. Default recommendation:
`validation*.md` (matches `validation.md`, `validation-A2.md`, `validation-C1.md`)
scoped to the spec dir, with completeness computed across all matched files.
Surface the glob and the completeness rule to the owner.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` and the fix use argparse, sqlite3,
  pathlib, json, sys, os only. Sprint 18 adds NO third-party Python dependency.
- **Article X locked render functions are immutable.** Do NOT edit, move, or
  rewrite `render_html`, `render_markdown`, `load_sprint_table`,
  `load_sprint_goal`, `detect_current_sprint`, or `load_decisions`. The fix lives
  in `cli/state_builder_data.py` (leaf module, NO locked functions);
  `TestS1FootprintLockGuard` stays GREEN. A worker never touches a locked function
  silently; touching one is an Article X re-baseline (ADR + owner approval,
  Level-2) and is NOT expected for Sprint 18.
- **The dashboard fix is behavior-corrective, tested.** New/changed behavior is
  covered by tests (the DONE-features smoke + closed-PI percentage are the proof).
  The existing `test_state_builder` suite keeps passing.
- **Single source of truth must not regress B-2.** Reconciling `detect_stage()`
  with `done_check.py` must not silently change the DONE-completeness blocking
  check; surface any `done_check.py` behavior change at CLARIFY.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 18's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 18 must pass the TDD
  gate and DONE-completeness checks and keep CI green; a change that breaks an
  enforced rule must fail loudly.
- **Constitution edits are gated.** No `constitution/**` change without an ADR +
  recorded owner approval + a version bump. The CLARIFY option (b) roadmap pull-in
  is a Level-2 decision -- surface it; do not edit `roadmap.md` silently.
- **Spec source is authoritative but stale-checked.** Build SDD-050's per-item
  `validation.md` from the audit Section 3 "Acceptance" blocks, but verify each
  root-cause line against the live `cli/state_builder_data.py` before acting (line
  references may have shifted). If an item is wrong on inspection, file a
  clarification and surface it -- do not silently drop it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044).** All human-facing output in this
  sprint (status, progress, questions to the owner) is short and plain;
  agent-to-agent detail may stay detailed. The Sprint EM holds this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Do NOT scrub history.** Sprint 18 is a code/detector sprint; it does not
  rewrite historical `specs/`, `sprints/`, retros, or ADRs.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 18 closes only when all are true:

1. **SDD-050 Defect 1 implemented**: `detect_stage()` in
   `cli/state_builder_data.py` returns DONE for a spec dir with `status: done` and
   satisfied validation, with NO per-dir `RETRO.md` required; split
   `validation*.md` files count toward completeness.
2. **SDD-050 Defect 2 implemented**: the PI percentage/current-PI logic reads the
   `(closed)` marker and renders closed PIs as done / 100%; `is_current` no longer
   matches `"(current, closed ...)"`; PI-6 rendering handled per the CLARIFY
   dependency decision (defensive read or gated pull-in).
3. **Single source of truth**: `detect_stage()` and `cli/done_check.py` share one
   definition of "done"; a feature that is DONE in one is DONE in the other; no
   silent B-2 regression.
4. **DONE-features smoke test PASS**: the regenerated dashboard renders SDD-043,
   SDD-044, SDD-045, SDD-046, SDD-047, and SDD-048 as DONE, and every closed PI
   (PI-1..PI-7) renders done / 100% with PI-7 NOT flagged current.
5. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual checks checked at close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 558
   passed, 2 skipped, and grows with the new detector tests.
7. Schema lint clean (exit 0) and origin lint clean (0 hits in generic files).
8. **Article X lock held**: `TestS1FootprintLockGuard` PASS; `render_html` /
   `render_markdown` and the four locked load_* functions are byte-identical.
9. **`doctor` green and CI green**: the health set and the GitHub Actions workflow
   pass on the Sprint 18 head; the B-2 blocking checks pass.
10. **Ledger shows real Sprint 18 rows**: the dogfood holds -- Sprint 18's own
    dispatches are in the ledger and the B-1 close gate is satisfied.
11. SDD-050 (and any per-item SDD-IDs) marked DONE in BACKLOG with evidence.
12. Owner pre-push approval recorded before any push.
13. **PI-8 continues to Sprint 19.** Sprint 18 does not close PI-8; the Sprint EM
    reports up to the project Executive Manager and confirms Sprint 19 is next.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 18 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-47, F-48, F-49
- Commits: <commit SHAs>
- Tests: 558 -> <N> (>= 558 required; new detector tests added)
- Schema lint: clean; origin lint: 0 hits in generic files
- Validation: SDD-050 per-item <r>/<r> REQUIRED + manual checks
- Defect 1: detect_stage() drops per-dir RETRO for status:done; globs validation*.md; stale status backfill <here | deferred to SDD-052>
- Defect 2: closed-PI reads (closed) marker -> done/100%; is_current hardened; PI-6 dependency <defensive read (a) | roadmap pull-in (b) under ADR-0NN>
- Single source of truth: detect_stage() reconciled with done_check.py via <shared helper>; B-2 <unchanged | change surfaced>
- DONE-features smoke: SDD-043..048 render DONE; closed PIs PI-1..PI-7 render 100%; PI-7 NOT current -- <PASS | FAIL>
- Per-item SDD-IDs assigned for SDD-050: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 18 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS); render_html / render_markdown untouched
- History preserved: YES (no historical specs/sprints/retros/ADRs rewritten)
- SDD-050: DONE (Defect 1 stage detector + Defect 2 closed-PI percentage + single source of truth)
- Deferred / out of scope: SDD-051 (S19), SDD-052 (S20), Sprint 21 owner-pick (SDD-049 or SDD-041 Option B), SDD-035 out-of-band
- PI-8 status: ACTIVE -- Sprint 18 CLOSED; continues to Sprint 19
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 18 lessons>
- Next: Sprint 19 (SDD-051 doc-freshness sweep + stale-doc doctor check)
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close PI-8. Sprint 18 is the first PI-8 sprint; it continues PI-8 to
  Sprint 19. PI-8 CLOSE is a separate owner-approved decision after the final PI-8
  sprint.
- Do NOT edit, move, or rewrite the Article X locked functions (`render_html`,
  `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`). The fix lives in
  `cli/state_builder_data.py` (leaf module, NO locked functions);
  `TestS1FootprintLockGuard` stays GREEN. A worker never touches a locked function
  silently; touching one is an Article X re-baseline (ADR + owner approval,
  Level-2).
- Do NOT touch the render modules (`state_builder_html.py`,
  `state_builder_markdown.py`) -- the detectors being fixed are in the
  data-assembly module.
- Do NOT regress the B-2 DONE-completeness check when reconciling `detect_stage()`
  with `done_check.py`; surface any `done_check.py` behavior change.
- Do NOT pull in SDD-051 (Sprint 19) or SDD-052 (Sprint 20) -- EXCEPT the optional
  minimal roadmap-marker part of SDD-052 under CLARIFY option (b), and only with
  an ADR + recorded owner approval + version bump.
- Do NOT pull in SDD-049, SDD-041 Option B, or the PI-6 carryovers.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently drop a SDD-050 audit item; if a root-cause line no longer
  matches `state_builder_data.py`, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 18's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT scrub or rewrite history.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-050 spec dir here -- F-47 does that inside the Sprint 18
  working sessions.
- Do NOT have the Sprint EM create a sprint or PI (or author the next kickoff) --
  it may only SUGGEST to the project EM and reports up at close.
