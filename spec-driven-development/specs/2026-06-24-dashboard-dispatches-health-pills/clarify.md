---
id: SDD-20260624DASHHEALTH-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-24
feature: 2026-06-24-dashboard-dispatches-health-pills
---

# CLARIFY: SDD-037 -- Dispatches card + dashboard health-pills strip

- Date: 2026-06-24
- Authors: Principal Product Manager + Principal Architect (jointly, with Software Developer task input), at F-27
- Status: **DONE** -- Q-A through Q-F answered; validation contract locked in [`validation.md`](./validation.md)
- Spec ID: SDD-037
- Sprint: PI-6 / Sprint 3 (= overall Sprint 12), feature slot F-27 (CLARIFY + SPEC + PLAN + TASKS; IMPLEMENT is F-28; close is F-29)
- Decision source: SDD-037 design surfaces resolved at F-27 against the locked owner direction recorded in [`SPRINT-12-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-12-KICKOFF.prompt.md) section 3 (Q-A..Q-F default recommendations).

---

## Ground Rules

- This file is the source of truth for SDD-037 design decisions.
- Default recommendations are taken from [`SPRINT-12-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-12-KICKOFF.prompt.md) section 3. Each question records the question, the options, the recommendation, and the **locked decision + rationale**.
- Article V (stdlib-only CLI), Article VII (context isolation / every artifact is a file), Article VIII (constitution immutability -- the health checks READ but never WRITE `constitution/**`), Article X (validation pre-implementation contract + S1 footprint lock), and Article XII (UI Lifecycle Variant) all remain binding.
- F-27 is design-only. **No implementation, no production code, no `.py` edit, no commit, no push** is authorized by this file. Implementation is F-28.
- The three Level-2 triggers the kickoff named -- a new ledger read API, a new ledger schema/table, and turning any health pill into a blocking gate -- are **deliberately avoided** by the decisions below, keeping the entire feature at Level-1.

---

## Decision Summary (Q-A..Q-F)

| Q | Topic | Locked Decision | Level |
|---|-------|-----------------|-------|
| Q-A | Dispatches card content + source | Render agent / role / task / status / when, grouped by feature then sprint, from `ledger/fleet.db` via the **existing `load_ledger()`** loader; empty -> empty card; unreachable -> disabled card with plain reason; never crash | Level-1 |
| Q-B | Ledger read caching | Read the ledger **once per `build()` refresh tick** through the existing single `load_ledger()` call; both the card and the ledger pill consume that one in-memory `LedgerView`; no per-panel re-query; no second `sqlite3.connect`; file-mtime caching rejected | Level-1 |
| Q-C | Health-pill set + "stale" definition | Four pills -- constitution semver, skill frontmatter validity (reuse `check_skill`), ledger reachability, stale-tracker; "stale" = tracker latest-date age **> 7 days** (green <=7, yellow 8-14, red >14, yellow if undatable) | Level-1 |
| Q-D | Pill click-through | Non-green pill anchors (`#health-detail-<check>`) to a **server-rendered** in-page detail section listing concrete failures; green pills render no link; **no JavaScript** (preserves `script tags:0`) | Level-1 |
| Q-E | Refresh-model integration | Reuse the existing additive `inject_*` post-processor pattern (SDD-036) + the per-tick `build()` refresh model; two new injectors wired after `inject_lifecycle_html`; no new refresh mechanism, route, or JS | Level-1 |
| Q-F | Pills are indicators, not gates | Sprint 12 health checks are **read-only indicators**; they never raise, never alter exit codes, never become CI/lint/pytest gates; internal errors degrade to red/yellow with a reason | Level-1 |

---

## Scope

### Q-A: Dispatches card content and source of truth

**Context.** SDD-037 surfaces the fleet ledger on the framework dashboard. `state_builder.py` already reads `ledger/fleet.db` read-only via `load_ledger()` (returns a `LedgerView` with `recent`, `recent_success`, `blockers`, and an `available` flag), degrading to `available=False` when the file is missing or a `sqlite3.Error` occurs. The `dispatches` table columns are: `dispatched_at`, `pi`, `sprint`, `feature_dir`, `task_id`, `task_title`, `agent_id`, `agent_role`, `outcome`, `outcome_at`, `notes`.

**Options.**

- Option A: Render a Dispatches card from the existing `LedgerView`, showing per row the **agent** (`agent_id`), **role** (`agent_role`), **task** (`task_id` + `task_title`), **status** (`outcome`, or "pending" when null), and **when** (`outcome_at` if present else `dispatched_at`), **grouped by `feature_dir` then `sprint`**. Empty ledger -> empty card with "No dispatches recorded yet."; unreachable ledger (`available=False`) -> disabled card with a plain-language reason. Never crash.
- Option B: Add a new public ledger read API in `ledger/__init__.py` (currently empty) that other modules call. (**Level-2** -- a new cross-module API surface; rejected.)
- Option C: Open a second `sqlite3.connect` inside the new injector to query the full table. (Rejected -- violates the single-read-per-tick decision in Q-B and duplicates the existing loader.)

**PM recommendation:** Option A. Reuse what already reads the ledger; render the five fields the kickoff named.

**Architect recommendation:** Option A. The existing `load_ledger()` is the in-module read pattern this feature extends. F-28 MAY *additively widen* the `LedgerView` returned by that single call (e.g. add a grouped/all-rows accessor populated **inside the same single connection**, leaving `recent` untouched so `build()`'s existing `len(ledger.recent)` report is unchanged). This is NOT a new ledger read API and NOT a new schema -- it is the same class of read the file already performs over the existing `dispatches` table, so it stays Level-1.

**SW Dev input:** Grouping is a pure rendering concern over already-loaded rows; the new injector is a stdlib post-processor like `inject_lifecycle_html`. No new file is required.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Render a **Dispatches card** grouped by `feature_dir` then `sprint`, each row showing agent / role / task / status / when, sourced from the existing single `load_ledger()` read. Empty -> empty card with a friendly note; unreachable -> disabled card with a plain reason; **never crash**. No new ledger package API; no new schema; no second DB read.
**Rationale:** Reuses the existing read path and graceful-degradation contract, keeps the change to additive rendering plus an additive `LedgerView` field, and avoids every Level-2 trigger.

---

### Q-B: Ledger read caching and invalidation

**Context.** The kickoff requires the ledger be read once per refresh tick and reused, not re-queried per panel. `state_builder.build()` already calls `load_ledger(sdd_root)` exactly once per invocation, and `DashboardHandler.do_GET` calls `build()` once per HTTP request (one refresh tick = one `build()`).

**Options.**

- Option A: **Per-tick single read.** Read the ledger once per `build()` call via the existing `load_ledger()`; pass the resulting `LedgerView` into both the Dispatches injector and the ledger-reachability pill. No additional `sqlite3.connect` anywhere in the new code.
- Option B: File-mtime cache keyed on `fleet.db` mtime, persisted across ticks. (Rejected -- premature optimization; adds cross-tick state for a handful of rows; the per-tick single read already bounds I/O to one open per render.)

**PM recommendation:** Option A.

**Architect recommendation:** Option A, with an explicit invalidation statement: **the cache lifetime is exactly one `build()` tick.** Each tick re-reads from disk (so the dashboard always reflects the current ledger), and within a tick every consumer reuses the same in-memory `LedgerView`. F-28 must add **zero** new `sqlite3.connect` calls; any widening of the read happens inside `load_ledger`'s existing single connection.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** **One ledger read per `build()` refresh tick**, reused in-memory by the Dispatches card and the ledger pill. Invalidation is per tick (each render re-reads). **No second `sqlite3.connect`; file-mtime caching is rejected.**
**Rationale:** Matches the existing architecture exactly, satisfies the kickoff constraint literally, and avoids cross-tick cache state that would add complexity for no measurable benefit at this scale.

---

### Q-C: Health-pill set and the concrete "stale" definition

**Context.** The dashboard header gains a health-pills strip. The kickoff names four checks; each pill is green/yellow/red. "Stale" must be defined concretely, and the skill-validity check must reuse `schema_lint`.

**The four pills (locked).**

1. **Constitution semver.** Reads `constitution/*.md` frontmatter `version:` (each file already carries a quoted `version: 'X.Y.Z'`; `principles.md` documents per-file semantic versioning). Reuses `parse_frontmatter`. **Read-only over `constitution/**` -- Article VIII forbids writing.**
   - green: every constitution file has a present, quoted, valid-semver `X.Y.Z` version.
   - yellow: a version is present and parseable but unquoted (ADR-0006 soft issue).
   - red: any constitution file is missing a version or carries an unparseable version.
2. **Skill frontmatter validity.** **Reuses `schema_lint.check_skill`** over `.github/skills/**/SKILL.md`. green: zero findings across all skills. red: any finding. (Binary -- schema_lint findings are pass/fail; no yellow.)
3. **Ledger reachability.** Reads `LedgerView.available` from the single per-tick read (Q-B). green: available. red: unreachable (missing `fleet.db` or `sqlite3.Error`), surfacing the reason.
4. **Stale-tracker.** Targets [`exec/sprint-progress.md`](../../exec/sprint-progress.md), the operational progress heartbeat. Staleness = (build date - the **latest ISO-8601 date token** found in the tracker) measured in whole days.
   - **N = 7 days.** green: age <= 7. yellow: 8 <= age <= 14. red: age > 14. yellow ("freshness unknown"): no parseable date.

**Why N = 7 (justification, not an arbitrary number).** The framework's human operating cadence is weekly: weekly status reports, the 1:1 cadence, and `exec/sprint-progress.md` is appended each feature slot (multiple times per active week). A tracker untouched for **more than 7 days** is the earliest honest "is this sprint still moving?" signal -- one missed weekly cycle. **14 days** is one full symbolic sprint with no progress entry, which is a hard red. Tying N to the actual weekly cadence (rather than a round number) makes the pill meaningful rather than decorative.

**Robustness.** Every check is wrapped so any internal exception degrades the pill to red (or yellow for the stale "unknown" case) with a plain reason -- never propagates (see Q-F).

**Status:** ANSWERED.
**Decision:** The four pills above, with constitution-semver read-only, skill-validity via `check_skill` reuse, ledger reachability from the single `LedgerView`, and a stale-tracker pill with **N = 7** (green <=7 / yellow 8-14 / red >14 / yellow if undatable) against `exec/sprint-progress.md`.
**Rationale:** Each pill reuses an existing signal or loader; the concrete N is anchored to the team's weekly cadence; read-only constitution access honors Article VIII.

---

### Q-D: Pill click-through to failure detail

**Context.** A non-green pill must let the human reach the failure detail. The dashboard has a hard **no-JavaScript** invariant (SDD-036 verified `script tags:0`); there is no client-side router.

**Options.**

- Option A: **Server-rendered in-page detail + same-page anchors.** Each non-green pill is an `<a href="#health-detail-<check>">`; the same injector also renders a `<section id="health-detail-<check>">` listing the concrete failures (the `check_skill` findings, the offending constitution file + bad/missing version, the ledger unreachable reason, the tracker latest-date + age). Green pills render no link and no detail section.
- Option B: Client-side JS routing / a fetch to a new endpoint. (Rejected -- introduces JavaScript and a new route; violates the no-JS invariant and Article V intent.)
- Option C: Link to the raw local artifact file on disk via `file://`. (Rejected -- brittle across hosts; the failure *reason* is what the human needs, not the raw file.)

**PM recommendation:** Option A.

**Architect recommendation:** Option A. Server-rendered detail keeps the dashboard a static, stdlib-generated surface, preserves `script tags:0`, and gives the human the actionable reason inline. Anchors are plain HTML.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Non-green pills anchor to **server-rendered** in-page detail sections; green pills have no link; **no JavaScript** is introduced.
**Rationale:** Honors the no-JS invariant and Article V, and surfaces the concrete failure reason where the human is already looking.

---

### Q-E: Refresh-model integration

**Context.** SDD-040 established the refresh model and SDD-036 established the additive surface-injection pattern (`inject_user_gates_html`, `inject_lifecycle_html` wired in `build()`; `DashboardHandler` regenerates per request; `served_html_with_refresh` adds the meta-refresh).

**Decision.** SDD-037 adds **two new additive injectors** -- `inject_dispatches_html` and `inject_health_pills_html` -- wired in `build()` **immediately after `inject_lifecycle_html`**, mirroring the existing chain. No new refresh mechanism, no new server route, no JavaScript, no change to the locked S1 functions. The pills strip injects into the dashboard header region; the Dispatches card injects into the main grid like the lifecycle section.

**Status:** ANSWERED.
**Decision:** Reuse the existing additive `inject_*` pattern + per-tick `build()` refresh; two new post-processors wired after `inject_lifecycle_html`.
**Rationale:** Consistency with SDD-036/SDD-040, additive-only, and keeps the S1 footprint lock intact.

---

### Q-F: Health checks are indicators, not gates

**Context.** A health check that can block a build or fail CI would change behavior and risk halting the dashboard. The kickoff is explicit that Sprint 12 pills are indicators only.

**Decision.**

1. **Read-only indicators.** Each check computes a status (green/yellow/red) + a reason; it performs no writes (constitution access is read-only).
2. **Never raises.** Any internal exception is caught and degraded to red (or yellow for the stale "unknown" case) with a plain reason. A health-check failure NEVER aborts `build()` or the HTTP handler.
3. **Never a gate.** The checks are NOT wired into `schema_lint`'s exit code, NOT into pytest gates, NOT into any CI gate. `build()`'s exit behavior is unchanged.
4. **Sprint-12 scope only.** Promoting any pill to a gate is a future, separately-governed decision -- out of scope here.

**Status:** ANSWERED.
**Decision:** Health checks are read-only indicators that never raise and never gate; internal errors degrade gracefully with a reason.
**Rationale:** Preserves dashboard reliability, keeps the feature additive, and avoids the Level-2 "blocking gate" trigger entirely.

---

## OWNER-ATTENTION Items (F-27 close)

- **No Level-2 surface is introduced.** The three triggers the kickoff named are all avoided:
  - *New ledger read API* -- AVOIDED. SDD-037 reuses the existing in-module `load_ledger()` and, at most, additively widens its `LedgerView` inside the same single connection. `ledger/__init__.py` stays empty; no new public ledger package API is created.
  - *New ledger schema/table* -- AVOIDED. Read-only over the existing `dispatches` table; no new table or column.
  - *Blocking gate* -- AVOIDED. Pills are read-only indicators (Q-F).
- **Single confirmation point for the owner (not a blocker):** if the owner regards *any* widening of `load_ledger`'s return shape as a "new ledger read API," that is the **only** point that could escalate to Level-2. The design treats it as in-scope Level-1 per the kickoff's own Q-A ("read from `ledger/fleet.db`") and hard constraint ("read-only access to `ledger/fleet.db` to render dispatch rows"). Flagging for explicit confirmation; **not designing a Level-2 in.**
- **No force, migration, or constitution edit is involved.** F-27 and F-28 perform no Level-2 action.
- **Pre-push approval remains mandatory at Sprint 12 close (F-29),** per standing owner direction. That gate is owned by F-29, not F-27.

## ADR Decision

- **ADR required: NO.** Unlike SDD-036 -- which introduced a new optional frontmatter field (`depends_on`), a new persisted append-only audit artifact, a new lint validator, and a dependency-lock/force-override governance regime (a new pattern across >1 module, hence ADR-017) -- SDD-037 introduces **no new persisted artifact, no new frontmatter field, no new governance regime, no new schema, and no new module**. It is additive, read-only rendering over existing loaders and existing checkers (`load_ledger`, `check_skill`, `parse_frontmatter`). This stays below the ADR threshold ("decision affects >1 module / new architectural pattern"). No ADR is authored at F-27. If the owner escalates the single confirmation point above, ADR-018 would be authored then to record a ledger-read-API decision -- it is NOT authored now.

## F-27 Close Checklist

1. Q-A through Q-F answered with locked decisions and rationale; zero open NEEDS-CLARIFICATION items.
2. This file frontmatter set to `status: done`, `updated: 2026-06-24`.
3. [`spec.md`](./spec.md) authored with goals, non-goals, requirements, acceptance criteria, file scope, traceability, `ui-variant: true`, and `depends_on: [SDD-036, SDD-018]`.
4. [`plan.md`](./plan.md) authored with the F-28 file dependency graph and serialization analysis.
5. [`tasks.md`](./tasks.md) authored with atomic, verification-driven F-28 tasks honoring CLI-PATTERN and full per-task file scoping.
6. [`validation.md`](./validation.md) authored, LOCKED at F-27, with the explicit Strict-vs-UI-Variant split; all REQUIRED items unchecked (implementation is F-28).
7. No ADR authored (no Level-2 surface); single confirmation point flagged for the owner.
8. `python spec-driven-development/cli/schema_lint.py` exits 0.
9. No implementation, commit, or push performed in F-27.
