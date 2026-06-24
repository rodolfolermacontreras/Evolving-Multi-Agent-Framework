# SPRINT 12 KICKOFF -- PI-6 Sprint 3 / Dispatches card + dashboard health pills

You are leading **Sprint 12**, which is **PI-6 Sprint 3**. Your job is to ship
**SDD-037** only: surface the fleet ledger and runtime health on the framework
dashboard:

1. A **Dispatches card** that renders fleet ledger rows (agent, role, task,
   status, when) per feature/sprint -- the ledger is currently locked inside
   SQLite and never opened without a manual query.
2. A **health-pills strip** in the dashboard header: constitution semver
   consistency, skill frontmatter validity, ledger reachability, and a
   stale-tracker pill, each green/yellow/red with click-through to failure
   detail.

Do not absorb **SDD-038** or the carryovers (SDD-034 dedup, SDD-039 Article VII
wording, PI-4 housekeeping) -- those are Sprint 13 contingency. Do not touch
Azure decommission work (SDD-035). Sprint 12 is intentionally scoped to SDD-037
alone, which is cheap relative to SDD-036 because it adds rendering, not schema.

You are the **Principal Executive Manager** for this kickoff. PM + Architect own
SDD-037 CLARIFY/SPEC/PLAN/TASKS. The Principal Software Developer owns
implementation, QA, sprint close, and Sprint 13 kickoff authoring if Sprint 12
closes cleanly and the owner approves the Sprint 13 contingency pull-in.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 12 must not start until all checks are true:

1. **Sprint 11 is closed and pushed.** Confirm
   [`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md) marks
   PI-6 Sprint 2 / Sprint 11 **CLOSED** on 2026-06-24, still marks PI-6
   **ACTIVE**, and names Sprint 12 / SDD-037 as the next planned sprint.
2. **Sprint 11 close is recorded.** Confirm
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) contains a
   `### Sprint 11 -- CLOSED` block with owner ratification
   `APPROVED FOR COMMIT + PUSH` and a commit SHA.
3. **Tests are green at the Sprint 11 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   412 passed with the known 2 platform-conditional skips. Run from the repo
   root, not from inside `spec-driven-development/`.
4. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
5. **SDD-036 is DONE in BACKLOG** with evidence (412 passed / 2 skipped, schema
   lint clean, 10/10 REQUIRED, ADR-017, dashboard + reorder smoke). Confirm the
   SDD-036 row in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) reads
   **DONE** 2026-06-24 and the spec dir
   `specs/2026-06-24-dashboard-lifecycle-reorder/` exists.
6. **SDD-037 remains open and allocated as Sprint 12.** Confirm the SDD-037 row
   in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is still open and not
   marked DONE.
7. **SDD-038 and the carryovers remain open for Sprint 13 contingency.** Confirm
   SDD-038, SDD-034, SDD-039, and PI-4 housekeeping are not pulled into
   Sprint 12.
8. **The dashboard surface SDD-037 builds on exists.** After
   `python spec-driven-development/cli/state_builder.py`,
   [`../exec/state.html`](../exec/state.html) must render the SDD-036 lifecycle
   pipeline and 4-card docs row, and must not say
   `Active focus: azure-decommission`.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 12 on a
red test baseline, an unpushed Sprint 11, a backlog that accidentally closed or
absorbed SDD-038/carryovers, or a dashboard that lost the SDD-036 surface.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 12 in isolated feature sessions or EM-routed subagent
   dispatches that preserve Article VII context isolation. Do not ask the owner
   to open another session when subagent dispatch gives equivalent isolation and
   the owner has approved that execution shape.
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 12 ships **one feature** (SDD-037): make the fleet ledger and runtime
health legible on the dashboard so the executive surface answers "what was
dispatched?" and "is the framework healthy?" without opening SQLite or running
CLIs by hand.

### Scope

- **Primary scope**: SDD-037 only.
- **Dashboard surfaces in scope**: generated `exec/state.html` and the data
  structures in `cli/state_builder.py` that feed it -- specifically a new
  Dispatches card and a header health-pills strip, both wired as
  `inject_*` post-processors alongside the existing SDD-036
  `inject_lifecycle_html()`.
- **Ledger surfaces in scope**: read-only access to `ledger/fleet.db` to render
  dispatch rows. No new ledger tables or schema unless CLARIFY explicitly locks
  one with Architect review.
- **Health-check surfaces in scope**: constitution semver consistency, skill
  frontmatter validity (reuse `schema_lint.py` logic, do not fork it), ledger
  reachability, and stale-tracker detection -- surfaced as pills, not new gates.
- **Prompts/docs in scope**: SDD-037 spec dir artifacts, Sprint 12 close block,
  and the Sprint 13 kickoff prompt only if Sprint 12 closes and the owner
  approves the Sprint 13 contingency.

### Explicit exclusions

- **SDD-038**: aesthetic lifecycle color-token system is Sprint 13 contingency.
  Reuse the minimal existing SDD-036 styles for pill readability; do not define
  or apply a new token palette.
- **Carryovers**: SDD-034 (content-shingle dedup), SDD-039 (Article VII
  wording; ADR), and PI-4 housekeeping (domain-skill annotations, GH Actions
  Node.js bump) remain outside Sprint 12 unless the owner replans PI-6.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 12 scope.
- **New gates**: health pills are read-only indicators. Do not turn a pill into
  a blocking validation gate without a separate Level-2 decision.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-27: SDD-037 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect, with SW Dev task input | SDD-037 has real design surfaces: ledger read caching, health-check definitions and thresholds, pill click-through targets, and the refresh-cycle integration. Lock the contract first. |
| 2 | F-28: IMPLEMENT + QA for SDD-037 | SW Dev + workers | Implementation only after the rendering model, ledger-read caching, and health-check definitions are locked. Use the UI Lifecycle Variant if CLARIFY confirms iterative UI validation. |
| 3 | F-29: Sprint 12 close + Sprint 13 decision | SW Dev + EM | Close Sprint 12, regenerate state, request owner approval before any push, and either author `SPRINT-13-KICKOFF.prompt.md` (if the owner approves the contingency pull-in) or record Sprint 13 as not-pulled-in with carry-forward. |

The default is sequential. Fleet dispatch is allowed only after F-27 produces a
file dependency graph that proves no two workers modify the same file. Shared
`cli/state_builder.py`, generated exec surfaces, or SDD-037 artifacts force
serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- Dispatches card content and grouping

Decide which ledger columns render and how rows group. Default recommendation:
render agent, role, task, status, and timestamp grouped by feature/sprint, read
from `ledger/fleet.db`. If the ledger is empty or unreachable, render a
disabled/empty Dispatches card with a plain-language reason rather than crashing.

### Q-B -- Ledger read caching (performance)

Lock how the dashboard reads the ledger. Per the PI-6 ROAM register, the
fleet.db query at page render is a known performance risk. Default
recommendation: cache the ledger read inside the same refresh cycle SDD-040
ships; do not re-query SQLite on every panel render. Decide cache invalidation
(per refresh tick vs file-mtime).

### Q-C -- Health-pill set and thresholds

Lock the exact pills and their pass/warn/fail thresholds. Default
recommendation: constitution semver consistency, skill frontmatter validity,
ledger reachability, and a stale-tracker pill. Reuse `schema_lint.py` validation
logic for frontmatter; do not fork or duplicate it. Decide what "stale" means
(e.g. tracker last-updated older than N days).

### Q-D -- Pill click-through targets

Decide where a red/yellow pill links. Default recommendation: click-through
resolves to the failing local artifact (the inconsistent constitution file, the
invalid skill, the unreachable ledger path) or to an inline failure-detail
panel. Avoid introducing JavaScript routing; prefer anchor links or a
server-rendered detail section.

### Q-E -- Refresh-model integration

Confirm the Dispatches card and pills respect the SDD-040 refresh model
(handler-side meta refresh + `--refresh-seconds`) and the SDD-036 surface
injection pattern. No new refresh mechanism.

### Q-F -- Health checks as indicators vs gates

Confirm health pills are read-only indicators in Sprint 12. Converting any pill
into a blocking validation gate (e.g. failing CI on a red pill) is a Level-2
decision and is out of Sprint 12 scope unless the owner approves it explicitly.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` uses argparse, sqlite3, pathlib, json,
  sys, os only. No third-party dependencies for ledger reads, health checks, or
  rendering.
- **Article X locked render functions are immutable.** Do NOT edit `render_html`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or
  `load_decisions`. Add the Dispatches card and health-pills strip as new
  `inject_*` post-processors wired in `build()`, exactly as SDD-036 added
  `inject_lifecycle_html()`. `TestS1FootprintLockGuard` golden SHA-256 hashes
  must still PASS.
- **Cache the ledger read in the refresh cycle.** Do not re-query SQLite on every
  panel render; read once per refresh tick and reuse.
- **Health checks reuse existing validators.** Reuse `schema_lint.py` logic for
  skill frontmatter validity; do not fork it.
- **No new gates.** Pills are indicators, not blocking gates, in Sprint 12.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Do not touch `constitution/**`.

---

## 5. Close criteria (Definition of Done)

Sprint 12 closes only when all are true:

1. SDD-037 implemented: Dispatches card renders ledger rows per feature/sprint;
   header health-pills strip renders with click-through.
2. All SDD-037 REQUIRED validation items checked with real-run evidence;
   manual/tone checks checked at close.
3. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 412
   passed, 2 skipped (the Sprint 11 baseline), and grows with SDD-037
   ledger-rendering and health-check tests.
4. Schema lint clean (exit 0).
5. Article X lock held (`TestS1FootprintLockGuard` PASS).
6. Dashboard smoke: regenerated `exec/state.html` shows the Dispatches card and
   pills; ledger-empty and unreachable states render gracefully; 0 unexpected
   `<script>` tags.
7. ADR authored if CLARIFY locks a Level-2 decision (e.g. a new ledger read API
   or any pill-as-gate proposal).
8. Owner pre-push approval recorded before any push.
9. SDD-037 marked DONE in BACKLOG; PI-6 remains ACTIVE; Sprint 13 either
   authored (owner-approved contingency) or recorded as not-pulled-in.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 12 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Principal Executive Manager (lead); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-27, F-28, F-29
- Commits: <commit SHA>
- Tests: 412 -> <N> (>= 412 required)
- Schema lint: clean
- Validation: SDD-037 <r>/<r> REQUIRED + manual checks
- ADRs: <ADR-018 if authored, else none>
- PI-6 status: ACTIVE; Sprint 13 (SDD-038 + carryovers) is contingency
- SDD-037: DONE (Dispatches card + dashboard health pills)
- Dashboard smoke: PASS
- Ledger-empty/unreachable smoke: PASS
- Carry-forward: SDD-038 + SDD-034 + SDD-039 + PI-4 housekeeping Sprint 13 contingency; SDD-035 out-of-band
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 12 lessons>
- Next: <SPRINT-13-KICKOFF.prompt.md authored at <path> | Sprint 13 not pulled in; carry-forward recorded>
```

---

## 7. Do NOT do

- Do NOT close PI-6. PI-6 remains ACTIVE after Sprint 12; Sprint 13 is a
  contingency, not a guarantee.
- Do NOT absorb SDD-038, SDD-034, SDD-039, or PI-4 housekeeping into Sprint 12.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT edit the Article X locked render functions or the `constitution/**`
  files.
- Do NOT add third-party dependencies.
- Do NOT turn a health pill into a blocking gate without a separate Level-2
  decision.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
