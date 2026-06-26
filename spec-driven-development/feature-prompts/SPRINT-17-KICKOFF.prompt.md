# SPRINT 17 KICKOFF -- PI-7 Sprint 4 / Maintainability + right-sizing (final PI-7 sprint)

You are leading **Sprint 17**, which is **PI-7 Sprint 4** -- the **FINAL sprint of
PI-7** ("Hardening + Orchestration Maturity"). Sprint 14 made the framework
clone-and-run portable. Sprint 15 made its promises true (the ledger is real, the
rules that matter block, CI fires for everyone). Sprint 16 de-authored the content
(identity is config, origin fingerprints are gone, every skill is wired, the
over-claim is renamed). Sprint 17 is the maintainability sprint: the 3082-line
`state_builder.py` god-module gets broken up behind its existing tests, the
stdlib-vs-templating question for the dashboard renderer gets an honest ADR, the
hardcoded grandfather date stops coupling the CLI to a calendar, and small
features stop drowning in four near-duplicate documents. Your job is to ship one
epic feature (SDD-048) and leave PI-7 ready to CLOSE:

1. **SDD-048** -- Maintainability + right-sizing (audit epic, spec source
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   Part C + D-2): **C-1** (split the `state_builder.py` god-module into modules,
   behavior identical, the existing test suite is the net), **C-2** (record the
   stdlib-vs-templating decision for the dashboard rendering layer as an ADR --
   **OWNER FORK**), **C-3** (replace the hardcoded grandfather date
   `ARTICLE_XI_CUTOVER = "2026-06-08"` with a config or derived value), **D-2**
   (add the lightweight-spec path Article VI promises -- one combined doc for
   <5-file features instead of four near-duplicate files). CLARIFY assigns
   per-item SDD-IDs, each with its own `validation.md` from the audit Acceptance
   blocks.

**This is the LAST PI-7 sprint -- but closing Sprint 17 does NOT close PI-7.**
The PI-7 CLOSE is a **separate, owner-approved decision** taken AFTER Sprint 17
closes. Sprint 17's close produces a **PI-7 close-readiness report** for the owner
(see Close criteria), but does not itself close the PI. Do NOT mark PI-7 CLOSED.

Do NOT pull in any deferred or carry-forward work: the PI-6 carryovers
(SDD-038 color tokens, SDD-034 dedup heuristic, PI-4 housekeeping, SDD-042
pill-nav follow-up, SDD-039 wording cleanup) and SDD-041 Option B (reorder ->
backend re-optimization) are NOT in Sprint 17 unless the owner explicitly
replans. **SDD-049** (true file-overlap detector, filed in Sprint 16 as a P3
placeholder) is NOT in Sprint 17. **SDD-035** (Azure decommission) remains
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
  project EM. At sprint close it produces a sprint-close summary **and a PI-7
  close-readiness report**, and **reports both UP to the project Executive
  Manager**, who folds them into project-wide state and owns the owner
  conversation about closing PI-7.
- Human-facing output from the Sprint EM is **short and plain** (SDD-044). Save
  the detail for agent-to-agent handoffs.

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-048 (including the C-1
lock approach and the C-2 owner fork). The Principal Software Developer owns
implementation, QA, and the Sprint 17 close (reporting up to the project EM
through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 17 must not start until all checks are true:

1. **Sprint 16 is CLOSED and pushed.** Confirm Sprint 16 (PI-7 Sprint 3 --
   De-author) closed at commit `e93862d`, that
   [`../sprints/PI-7/CURRENT_PI.md`](../sprints/PI-7/CURRENT_PI.md) marks PI-7
   **ACTIVE** and names Sprint 17 as the next (and final) sprint, and that
   SDD-047 (with its per-item A-2/A-3/D-1/D-3 IDs) is marked DONE in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md).
2. **Tests are green at the Sprint 16 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **540 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint and origin lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0 and
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files.
4. **`doctor` is green and CI is green.** The Sprint 14/15/16 health set passes:
   `doctor` reports green (7/7), and the GitHub Actions CI workflow (B-4) is
   green on the `e93862d` head. The Article X lock guard
   (`TestS1FootprintLockGuard`) is PASS at this baseline.
5. **SDD-048 is filed and allocated to Sprint 17.** Confirm the SDD-048 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-7 Sprint 17.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   exists; SDD-048's per-item `validation.md` files are built from its Part C
   (C-1 / C-2 / C-3) and D-2 "Acceptance" blocks.
7. **The live PI-7 gates apply to Sprint 17.** The mandatory-ledger close gate
   (B-1) is LIVE -- Sprint 17's own dispatch outcomes must be logged in the
   ledger before Sprint 17 can be stamped DONE. The blocking checks (B-2: TDD
   gate + DONE-completeness) and CI (B-4) are LIVE -- Sprint 17 must pass them.
8. **Owner has approved the Sprint 17 start** (the final PI-7 hardening sprint).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 17 on a
red test baseline (< 540), an unpushed/mismatched Sprint 16 (not closed at
`e93862d`), a red `doctor` / origin lint / CI, a broken Article X lock, a backlog
that accidentally closed SDD-048, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 17 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

---

## 1. Sprint goal

Sprint 17 ships **one epic feature** (SDD-048) that makes the codebase
maintainable and right-sizes the ceremony. The 3082-line `state_builder.py`
god-module is decomposed into focused modules -- data assembly, markdown render,
html render, http server, doc-count, work-index -- with the 762-line
`render_markdown` and 658-line `render_html` broken into per-section functions,
**behavior identical and the existing test suite the only proof needed** (C-1).
The dashboard's stdlib-vs-templating question gets an honest ADR with the
trade-off recorded either way (C-2). The hardcoded grandfather date stops
coupling the CLI to a calendar (C-3). And a small (<5-file) feature can complete
the lifecycle with one combined artifact instead of four near-duplicate files,
without weakening the Article X validation lock (D-2). At close, no function
exceeds ~120 lines, the C-2 decision is an ADR, no calendar date is hardcoded in
CLI logic, the lightweight-spec path works on a real <5-file feature, and PI-7 is
ready for the owner to CLOSE.

### Scope

- **SDD-048 -- C-1 (split the `state_builder.py` god-module)**: split the 3082-line
  file into focused modules (data assembly / markdown render / html render / http
  server / doc-count / work-index) and decompose the two giant render functions
  into per-section helpers. **Behavior is identical -- the 135+ existing
  `test_state_builder` tests pass with NO assertion changes.** Refactor one
  section at a time, **one extraction per commit**. Target: no function exceeds
  ~120 lines. See the Article X / C-1 tension section below -- this is the #1
  design risk.
- **SDD-048 -- C-2 (stdlib-vs-templating ADR -- OWNER FORK)**: decide whether the
  dashboard rendering layer stays **stdlib-only** (factor the render wall into
  `string.Template`-based helpers -- still stdlib) OR takes **one templating
  dependency**. This is an **ADR-level, Level-2 owner decision** surfaced at
  CLARIFY. **Default lean: stay stdlib-only** (Article V is the framework's
  portability guarantee; breaking it for the dashboard is a real trade-off).
  Record the decision and its trade-off in an ADR either way; C-2 folds into C-1.
- **SDD-048 -- C-3 (replace the hardcoded grandfather date)**: move
  `fleet.py` `ARTICLE_XI_CUTOVER = "2026-06-08"` to a config source or derive it,
  and document why the cutover exists. At close, no hardcoded calendar date lives
  in CLI logic without a config source and a comment.
- **SDD-048 -- D-2 (lightweight-spec path for small features)**: implement the
  lightweight path Article VI already authorizes -- **one combined doc** (story +
  requirements + validation contract) for <5-file features, with cross-links
  instead of four near-duplicate files. **Do NOT weaken the validation lock**:
  the combined artifact must still satisfy Article X (validation before
  implementation). Prove it on a real <5-file feature.
- **Per-item SDD-IDs**: CLARIFY assigns a per-item SDD-ID to C-1, C-2, C-3, and
  D-2, each with its own `validation.md` built from the audit "Acceptance" block.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1, live
  from Sprint 15) applies to **this sprint's own dispatches**. Sprint 17's own
  dispatch outcomes must be in the ledger before Sprint 17 can be stamped DONE.

### The Article X / C-1 tension -- #1 design risk (READ THIS)

C-1 splits the god-module. But five `state_builder.py` functions are **Article X
LOCKED** to commit `257b081` with golden SHA-256 hashes guarded by
`TestS1FootprintLockGuard` (`cli/test_state_builder.py`):

```
render_html, load_sprint_table, load_sprint_goal, detect_current_sprint, load_decisions
```

`render_html` (658 lines) is exactly the kind of giant function C-1 wants to
break up, and the locked load_* functions are the data-assembly layer C-1 wants to
move into a module. **Splitting the god-module will collide with the lock.** The
lock test takes `inspect.getsource(...)` of each function by name and compares its
sha256 to the golden -- so even *moving* a locked function to another module, or
changing its body, will fail the guard.

The kickoff resolves this at CLARIFY with a default and a gated escape hatch:

- **Default approach (a) -- refactor AROUND the locked functions.** Extract
  everything that is NOT one of the five locked functions: the markdown render,
  the HTTP server (`DashboardHandler`, `serve`), the doc-counter, the work-index
  builder, and the non-locked render helpers. Leave the five locked functions in
  place (the lock test imports them from `cli.state_builder` by name, so they can
  stay there even as other code moves out). C-1's "no function exceeds ~120 lines"
  target then applies to the **non-locked** surface; the five locked functions
  are a documented, owner-ratified exception that an Article X amendment would be
  required to touch. This keeps the lock GREEN with zero owner gating.
- **Option (b) -- re-baseline the lock under an ADR + owner approval.** If, and
  only if, the owner decides the split MUST move or rewrite a locked function
  (e.g. break `render_html` into per-section helpers), that is an **Article X
  amendment**: a new ADR + recorded owner ratification + a re-computed
  `GOLDEN_S1_HASHES` set (or a redefinition of `LOCKED_S1_FUNCTIONS`). This is a
  **Level-2 decision**. Do NOT proceed with it without the ADR and owner sign-off.

**A worker must NEVER silently edit, move, or rewrite a locked function.** If C-1
implementation finds it cannot hit the ~120-line target without touching a locked
function, it STOPS and surfaces the choice (refactor-around vs re-baseline) to the
owner via the Sprint EM. The default is (a); (b) only with ADR + approval.

### Explicit exclusions

- **PI-6 carryovers** -- SDD-038 (color tokens), SDD-034 (dedup heuristic), PI-4
  housekeeping (domain-skill annotations + GH Actions Node.js bump), SDD-042
  (pill-nav follow-up), SDD-039 (wording cleanup) -- are NOT in Sprint 17 unless
  the owner explicitly replans them in.
- **SDD-041 Option B** (reorder triggers backend re-optimization) is NOT the
  Sprint 17 anchor; it folds in ONLY if the owner explicitly adds it after
  SDD-048 lands and capacity allows. Default: out of scope.
- **SDD-049** (true file-overlap detector, the honest backlog item filed in
  Sprint 16) is a P3 placeholder and is NOT in Sprint 17.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 17 scope.
- **PI-7 close**: closing PI-7 is a separate owner-approved decision AFTER the
  Sprint 17 close. Sprint 17 produces a PI-7 close-readiness report; it does not
  close PI-7.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-44: SDD-048 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs (C-1/C-2/C-3/D-2), builds each `validation.md` from the audit Acceptance blocks, **decides the C-1 lock approach** (default (a) refactor-around vs (b) re-baseline-under-ADR), and **surfaces the C-2 stdlib-vs-templating owner fork** (default: stay stdlib-only). The C-1 extraction plan (one module per commit) and the C-3 cutover destination are designed here. Any Article X amendment (option (b)) is an ADR drafted here with owner approval. |
| 2 | F-45: SDD-048 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. The god-module split lands **behind the existing test suite with no assertion changes**, one extraction per commit; the C-3 date moves to config/derived; the D-2 lightweight path ships and is proven on a real <5-file feature. The C-2 decision is recorded as an ADR. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. The Article X lock stays GREEN (approach (a)) OR is re-baselined under the owner-approved ADR (approach (b)). |
| 3 | F-46: Sprint 17 close + PI-7 close-readiness report | Sprint EM + SW Dev | Close Sprint 17, regenerate state, request owner pre-push approval, mark SDD-048 (and the per-item IDs) DONE, and **produce a PI-7 close-readiness report** with a PI-7 close recommendation. The Sprint EM produces the sprint-close summary, folds in the close-readiness report, and reports both UP to the project Executive Manager, who owns the owner conversation about closing PI-7. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `cli/state_builder.py` (and any modules split out of it),
`cli/fleet.py`, `cli/schema_lint.py`, `constitution/**`, the spec template
surfaces, generated exec surfaces, or shared spec artifacts -- force
serialization. (Note: the only conflict mechanism is the serial CLARIFY/SPEC gate
renamed in Sprint 16 -- there is no file-overlap detector; SDD-049 remains a P3
placeholder.)

---

## 3. Likely CLARIFY surfaces

### Q-A -- C-1 lock approach (refactor-around vs re-baseline)

Decide how C-1 interacts with the five Article X locked functions. Default
recommendation: **approach (a) -- refactor around the locked functions.** Extract
the markdown render, HTTP server, doc-counter, work-index, and non-locked
helpers; leave `render_html`, `load_sprint_table`, `load_sprint_goal`,
`detect_current_sprint`, and `load_decisions` in place so the lock test keeps
finding them by name. The ~120-line target applies to the non-locked surface; the
five locked functions are a documented exception. Approach (b) -- re-baselining
the lock to allow moving/rewriting a locked function -- is an Article X amendment
(ADR + owner approval + re-computed goldens) and is Level-2; recommend it ONLY if
the owner wants the locked functions split too. A worker never touches a locked
function silently.

### Q-B -- C-1 extraction plan (one module per commit)

Confirm the module decomposition and the commit-per-extraction discipline.
Default recommendation: split into `state_builder_data.py` (data assembly /
load_* assembly), markdown render, html render, `dashboard_server.py` (HTTP
server), doc-count, and work-index -- each extraction in its own commit so a
regression bisects cleanly, and the full `test_state_builder` suite runs green
after every extraction. The split is a **pure refactor**: no behavior change, no
assertion change. Surface the proposed module boundaries to the owner.

### Q-C -- C-2 stdlib-vs-templating (OWNER FORK -- Level-2)

Surface the dashboard rendering decision to the owner as an explicit fork.
Default recommendation: **stay stdlib-only** and factor the render wall into
`string.Template`-based helpers (still stdlib), preserving the Article V
portability guarantee. The alternative -- taking **one templating dependency** for
the dashboard only -- is a Level-2 new-dependency decision that erodes the
clone-and-run-anywhere promise. Record the decision and its trade-off in an ADR
either way (C-2 folds into C-1). Recommend stdlib-only unless the owner
explicitly accepts the dependency.

### Q-D -- C-3 where the cutover date moves

Decide where `ARTICLE_XI_CUTOVER = "2026-06-08"` goes. Default recommendation:
move it to a config source (e.g. a `project.config.json` field or a small
constants surface) OR derive it, with a comment explaining why the cutover exists.
At close, no hardcoded calendar date lives in CLI logic without a config source
and a comment. Keep the change stdlib-only.

### Q-E -- D-2 lightweight-spec shape

Lock the shape of the combined lightweight artifact. Default recommendation: one
combined doc (story + requirements + validation contract) for <5-file features,
with cross-links instead of four near-duplicate files, that **still satisfies
Article X (validation before implementation)** -- the validation lock is NOT
weakened, only the duplication is collapsed. Prove the path on a real <5-file
feature during F-45. Surface the template shape to the owner.

### Q-F -- max-function-length lint (optional)

Decide whether to add a simple max-function-length `schema_lint`/CLI rule to lock
in C-1's ~120-line target. Default recommendation: add it as an **optional**
lock-in if it is cheap and stdlib-only, scoped to exclude the five Article X
locked functions; do not block the sprint on it. Surface it to the owner as a
nice-to-have.

---

## 4. Hard constraints

- **Stdlib-only (Article V) UNLESS C-2 owner-overrides.** `cli/**`, the split
  modules, and any config reader use argparse, sqlite3, pathlib, json, sys, os
  only. The maintainability work adds NO third-party Python dependency **unless
  the owner explicitly accepts a templating dependency at the C-2 fork** (a
  Level-2 ADR decision). Default: no new dependency.
- **Article X locked render functions are immutable UNLESS re-baselined.** Do NOT
  edit, move, or rewrite `render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, or `load_decisions`. The default C-1 approach (a)
  refactors AROUND them and keeps `TestS1FootprintLockGuard` GREEN. They may be
  touched ONLY under approach (b): an Article X amendment with an ADR + recorded
  owner ratification + re-computed `GOLDEN_S1_HASHES`. A worker never touches a
  locked function silently.
- **C-1 is a pure refactor behind the test net.** Behavior is identical; the
  existing `test_state_builder` suite passes with NO assertion changes. One
  extraction per commit so a regression bisects cleanly.
- **D-2 does NOT weaken the validation lock.** The combined lightweight artifact
  must still satisfy Article X (validation before implementation). Collapse
  duplication only.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 17's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 17 must pass the TDD
  gate and DONE-completeness checks and keep CI green; a change that breaks an
  enforced rule must fail loudly.
- **Constitution edits are gated.** No `constitution/**` change without an ADR +
  recorded owner approval + a version bump. A C-2 dependency acceptance or an
  Article X re-baseline (option (b)) is a Level-2 ADR decision -- surface it; do
  not edit silently.
- **Spec source is authoritative but stale-checked.** Build each SDD-048 per-item
  `validation.md` from the audit "Acceptance" block, but verify each "Evidence"
  line against the live repo before acting (line counts and function sizes may
  have shifted). If an item is wrong on inspection, file a clarification and
  surface it -- do not silently drop it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044).** All human-facing output in this
  sprint (status, progress, questions to the owner, the close-readiness report)
  is short and plain; agent-to-agent detail may stay detailed. The Sprint EM holds
  this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Do NOT scrub history.** Sprint 17 is a code/maintainability sprint; it does
  not rewrite historical `specs/`, `sprints/`, retros, or ADRs.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 17 closes only when all are true:

1. **SDD-048 C-1 implemented**: `state_builder.py` is decomposed into focused
   modules (data assembly / markdown render / html render / http server /
   doc-count / work-index); the giant render functions are broken into per-section
   helpers; **no function exceeds ~120 lines** (the five Article X locked
   functions are the documented exception under approach (a)); the split landed
   one extraction per commit.
2. **SDD-048 C-2 implemented**: an ADR records the stdlib-vs-templating decision
   and its trade-off; if stdlib-only was kept, the renderer is factored so it is
   no longer one 700-line f-string wall.
3. **SDD-048 C-3 implemented**: `ARTICLE_XI_CUTOVER` (and any other calendar date
   in CLI logic) is config-sourced or derived with a comment; no hardcoded
   calendar date remains in CLI logic without a config source.
4. **SDD-048 D-2 implemented**: a <5-file feature can complete the lifecycle with
   one combined artifact and still satisfy Article X; the path is proven on a real
   <5-file feature.
5. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual checks checked at close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 540
   passed, 2 skipped (the Sprint 16 close baseline), and grows with any new tests.
   **C-1 keeps all existing tests passing with no assertion changes.**
7. Schema lint clean (exit 0) and origin lint clean (0 hits in generic files).
8. **Article X lock held OR re-baselined**: `TestS1FootprintLockGuard` PASS under
   approach (a); OR, under approach (b), the lock is re-baselined via an ADR +
   recorded owner ratification + re-computed goldens.
9. **`doctor` green and CI green**: the Sprint 14/15/16 health set and the GitHub
   Actions workflow pass on the Sprint 17 head; the B-2 blocking checks pass.
10. **Ledger shows real Sprint 17 rows**: the dogfood holds -- Sprint 17's own
    dispatches are in the ledger and the B-1 close gate is satisfied.
11. SDD-048 (and the per-item C-1/C-2/C-3/D-2 SDD-IDs) marked DONE in BACKLOG with
    evidence.
12. Owner pre-push approval recorded before any push.
13. **A PI-7 close-readiness report is produced for the owner** with a PI-7 CLOSE
    recommendation, and reported UP to the project Executive Manager. The PI-7
    CLOSE itself is a SEPARATE owner-approved decision taken after Sprint 17;
    Sprint 17 does not close PI-7.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 17 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-44, F-45, F-46
- Commits: <commit SHAs>
- Tests: 540 -> <N> (>= 540 required; C-1 added no assertion changes)
- Schema lint: clean; origin lint: 0 hits in generic files
- Validation: SDD-048 per-item (C-1/C-2/C-3/D-2) <r>/<r> REQUIRED + manual checks
- C-1 split: state_builder.py decomposed into <module list>; no function > ~120 lines (5 Article X locked fns excepted); one extraction per commit
- C-1 lock approach: <(a) refactor-around -- lock held | (b) re-baselined under ADR-0NN + owner approval>
- C-2 decision: <stdlib-only (string.Template helpers) | one templating dependency>; ADR-0NN records trade-off
- C-3 cutover: ARTICLE_XI_CUTOVER moved to <config source | derived>; no hardcoded calendar date in CLI logic
- D-2 lightweight path: combined-artifact path shipped; proven on <feature>; Article X validation lock intact
- Per-item SDD-IDs assigned for SDD-048: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 17 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: <held (TestS1FootprintLockGuard PASS) | re-baselined under ADR-0NN + owner ratification>
- max-function-length lint: <added (optional) | not added>
- History preserved: YES (no historical specs/sprints/retros/ADRs rewritten)
- SDD-048: DONE (C-1 god-module split + C-2 ADR + C-3 date config + D-2 lightweight path)
- Deferred / out of scope: PI-6 carryovers, SDD-041 Option B (unless owner replanned), SDD-049 (P3), SDD-035 out-of-band
- PI-7 status: ACTIVE -- final sprint CLOSED; PI-7 CLOSE pending separate owner decision
- PI-7 close-readiness report: PRODUCED; PI-7 close recommendation: <READY TO CLOSE | NOT READY -- reason>
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 17 lessons>
- Next: PI-7 CLOSE decision (owner-approved, taken after this close) -- NOT auto-closed here
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close PI-7 automatically. This is the FINAL PI-7 sprint, but PI-7 CLOSE
  is a separate owner-approved decision taken after Sprint 17 closes. Sprint 17
  produces a PI-7 close-readiness report; it does not close PI-7.
- Do NOT edit, move, or rewrite the Article X locked render functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`) under approach (a). They may be
  touched ONLY under approach (b): an Article X amendment with an ADR + recorded
  owner ratification + re-computed `GOLDEN_S1_HASHES`. A worker never touches a
  locked function silently.
- Do NOT change behavior in C-1. It is a pure refactor behind the existing test
  suite -- no assertion changes; one extraction per commit.
- Do NOT add a templating (or any third-party) dependency unless the owner
  explicitly accepts it at the C-2 fork (a Level-2 ADR decision). Default:
  stay stdlib-only (Article V).
- Do NOT weaken the Article X validation lock in D-2; collapse duplication only.
- Do NOT edit `constitution/**` without an ADR + recorded owner approval +
  version bump. A C-2 dependency acceptance or an Article X re-baseline is
  Level-2 -- surface it.
- Do NOT pull in the PI-6 carryovers (SDD-038/034/042/039, PI-4 housekeeping) or
  SDD-041 Option B unless the owner explicitly replans them in.
- Do NOT pull in SDD-049 (true file-overlap detector -- a P3 placeholder).
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently drop a SDD-048 audit item; if an "Evidence" line no longer
  matches the repo, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 17's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT scrub or rewrite history.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-048 spec dir here -- F-44 does that inside the
  Sprint 17 working sessions.
- Do NOT have the Sprint EM create a sprint or PI (or author the next kickoff) --
  it may only SUGGEST to the project EM and reports up at close.
