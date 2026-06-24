---
id: SDD-PI-6-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-06-10
sprint: PI-6
---

# PI-6: Dashboard Reinvestment + Carryover Cleanup

- Status: **ACTIVE** (Sprint 1 / Sprint 10 CLOSED locally on 2026-06-10; Sprint 11 / SDD-036 is next planned; no commit or push performed by F-23 close prep)
- Theme: Ship dashboard patterns that make the framework's state visible and useful at a glance, then clear the carryover backlog accumulated across PI-3..PI-5.
- Started: 2026-06-10
- Owner: principal-executive-manager
- Predecessor: PI-5 (Brownfield Adoption + Anti-Conflict + Stakeholder Discipline) CLOSED 2026-06-09 as DONE-WITH-CARRYOVER at commit `8417818`.
- Authorization: Owner approval 2026-06-10 via Executive Manager. Owner direction (verbatim): "Still says Active focus: azure-decommission (stale -- that wrapped up). Static -- refreshes only when you re-run state_builder.py." This complaint anchors PI-6 on the dashboard parser fix (SDD-040) and confirms the broader dashboard reinvestment bundle as the PI-6 commitment.

---

## Goal

Make the framework's live dashboard a trustworthy executive surface again --
the parser stops lying about active focus, the page refreshes on its own, the
lifecycle pipeline becomes visible, and the ledger contents become readable
without opening SQLite. Once the dashboard story lands, clear the carryover
items (SDD-034 dedup heuristic upgrade, SDD-039 Article VII wording, PI-4
housekeeping) that PI-5 closed DONE-WITH-CARRYOVER.

---

## PI Objectives

### 1. Dashboard Parser Fix + Auto-Refresh (SDD-040)
**Why**: The owner observed 2026-06-10 that `state.html` still showed
`Active focus: azure-decommission` after PI-5 closed (commit `8417818`),
because (a) the active-focus heuristic relies on frontmatter alone, not on
commit recency or validation state, and (b) the page is static -- it only
updates when `state_builder.py` is invoked by hand. This is the smallest,
highest-trust-payoff dashboard fix in the bundle and it must ship before any
of the larger dashboard patterns build on top of it.

**Success Criteria**: Active-focus picks the most-recently-shipped or
in-validation feature (not stale frontmatter); serve-mode auto-refreshes via
stdlib-only file-watch or polling (no `watchdog`, no `flask`); non-serve
invocation still produces static `state.md` + `state.html` for git/diff use.

**Feature**: SDD-040 (state_builder.py parser fix + auto-refresh).

---

### 2. Lifecycle Pipeline + Drag-to-Reorder with Safeguards (SDD-036)
**Why**: SDD-036 imports the three highest-value patterns from Scott's
WWIC Analyst Backlog UI: lifecycle status pipeline on every feature/sprint
card, 4-card documentation row (Constitution / Spec / Sprint / ADRs), and
drag-to-reorder backlog with audit-trail + dependency-lock safeguards.
This is the largest CLARIFY surface in PI-6 because the safeguards
introduce a new `depends_on` frontmatter field and a new audit-trail
ledger row schema. SDD-018 (UI Lifecycle Variant) is the prerequisite
and shipped in PI-5 Sprint 3.

**Success Criteria**: Feature/sprint cards render the lifecycle pipeline
horizontally; the 4-card docs row replaces scattered per-feature links;
drag-to-reorder writes an audit-trail ledger row per drag and respects
`depends_on` cycle constraints; force-override requires Level-2 escalation.

**Feature**: SDD-036.

---

### 3. Dispatches Card + Health Pills (SDD-037)
**Why**: SDD-037 surfaces fleet ledger contents per feature/sprint
(currently locked in SQLite and never opened) and adds a health-pills
strip to the dashboard header (constitution semver consistency, skill
frontmatter validity, ledger reachability, stale-tracker pills with
click-through). Cheap to build, large reliability payoff. Depends on
SDD-036 lifecycle pipeline existing on the same dashboard surface.

**Success Criteria**: A Dispatches card renders ledger rows (agent, role,
task, status, when) for each feature/sprint; the header strip shows
green/yellow/red pills with click-through to failure detail; both surfaces
respect the same refresh model SDD-040 ships.

**Feature**: SDD-037.

---

### 4. Aesthetic Tokens + Carryover Cleanup (SDD-038 + carryovers)
**Why**: SDD-038 defines our own lifecycle-state color tokens (consistent
across dashboard + rendered Markdown views + agent UIs) so the visual
language matches the conceptual one Article XII established. The carryover
bundle finally closes SDD-034 (content-shingle dedup upgrade), SDD-039
(Article VII wording clarification; requires ADR), and the PI-4
housekeeping (domain-skill annotations + GH Actions Node.js bump) that
PI-5 closed DONE-WITH-CARRYOVER.

**Success Criteria**: Lifecycle-state token palette defined and applied
to at least one dashboard surface + one rendered Markdown view; SDD-034
content-shingle upgrade lands in `cli/dedup.py`; SDD-039 Article VII
wording amended via ADR; PI-4 housekeeping committed.

**Features**: SDD-038, SDD-034, SDD-039, PI-4-carry-over (domain-skill
annotations, GH Actions Node.js bump). Pulled in only if Sprint 13 has
capacity; Sprint 13 is a contingency sprint, not a guarantee.

---

## Sprint Allocation

| Sprint | Overall | Title | Items | Size | Why this order |
|--------|---------|-------|-------|------|----------------|
| **PI-6 Sprint 1** | Sprint 10 | Dashboard Parser Fix + Auto-Refresh | SDD-040 | S | **CLOSED locally 2026-06-10.** Highest-trust-payoff fix shipped in local working tree; active focus no longer points at stale azure-decommission work and serve-mode refresh is verified. Commit pending; no push performed. |
| **PI-6 Sprint 2** | Sprint 11 | Lifecycle Pipeline + Drag-to-Reorder (with Safeguards) | SDD-036 | L | **NEXT PLANNED.** Heaviest CLARIFY load in PI-6; introduces new `depends_on` frontmatter field and audit-trail ledger schema; sequencing precondition SDD-018 (UI Lifecycle Variant) is satisfied. Must land before SDD-037 because SDD-037's Dispatches card sits on the same dashboard surface as the SDD-036 lifecycle pipeline. |
| **PI-6 Sprint 3** | Sprint 12 | Dispatches Card + Health Pills | SDD-037 | M | Builds on SDD-036's dashboard surface; surfaces ledger contents and runtime health pills; cheap relative to SDD-036 because no new schema, just new rendering. |
| **PI-6 Sprint 4** | Sprint 13 | Aesthetic Tokens + Carryover Cleanup | SDD-038 + carryovers (SDD-034 dedup, SDD-039 Article VII wording, PI-4 housekeeping) | M | Contingency sprint. Pulled in only if Sprints 10-12 hold velocity. Aesthetic tokens are P3 polish; the carryover items are the long tail of PI-5 DONE-WITH-CARRYOVER and should not block PI-7 planning. |

**Unscheduled** (out of PI-6 scope):

- **SDD-035** -- Decommission Azure dashboard remains tracked as
  out-of-band 2026-06 work (Phase A.3 scaffold pending); PM and Architect
  will decide separately whether to fold any remaining decommission work
  into PI-6 or carry to PI-7.
- **SDD-024** -- Microsoft self-improving skills paper memo (P3,
  single-task; not PI-bound).
- **SDD-026** -- Trim agent traceability scope (P4, deferred indefinitely
  per PM override).

---

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| Stdlib-only constraint (Article V) makes auto-refresh awkward; polling wastes CPU and file-watch needs `watchdog` | Medium | Medium | Owned | SW Dev + Architect | CLARIFY in Sprint 10 must explicitly choose polling cadence vs stdlib file-mtime sweep; document the trade-off in the spec; HTTP handler can also refresh on each request as a fallback. |
| SDD-036's new `depends_on` frontmatter field forces schema_lint extension + retroactive backfill | High | Medium | Owned | Architect + SW Dev | CLARIFY in Sprint 11 must decide whether `depends_on` is optional (no backfill) or required (backfill all existing spec dirs). Default to optional to avoid a flag day. |
| SDD-036 drag-to-reorder produces audit-trail spam if users drag frequently in leadership demos | Medium | Medium | Mitigated | PM | Owner correction 2026-06-08 already acknowledged: "drag-to-reorder must be possible without ceremony -- the framework value-add is the audit trail, not blocking the human." Treat audit-trail as append-only and visible-on-demand, not modal. |
| SDD-037 fleet.db query at page render slows the dashboard | Medium | Low | Mitigated | SW Dev | Cache the ledger read inside the same refresh cycle SDD-040 ships; do not re-query SQLite on every panel render. |
| Sprint 13 contingency sprint pulls in too much and slips the carryover items past PI-6 close | Medium | Medium | Mitigated | EM | Sprint 13 is explicitly contingent. Carryover items remain visible in BACKLOG as carry-forward; PI-6 close can stamp DONE-WITH-CARRYOVER if Sprint 13 cannot land within wall-clock budget. |
| Dashboard reinvestment competes with team-share readiness (SDD-035 Azure decommission docs purge) | Low | Low | Accepted | EM | Owner direction 2026-06-08 already declared local-dashboard the strategic investment. Azure decommission docs purge runs out-of-band as Phase A.3 scaffold work; PI-6 owns only the in-repo dashboard surface. |

---

## Dependencies

**Internal**:
- PI-5 close commit `8417818` is the PI-6 base. Tests at 337 passed + 2
  skipped is the floor; PI-6 must hold or improve this baseline.
- SDD-FDC-001 frontmatter contract (LOCKED 2026-06-06): new artifacts in
  PI-6 must carry valid frontmatter; schema_lint guards this.
- ADR-014 (Article XII / UI Lifecycle Variant): SDD-036 is a UI-lifecycle
  feature and can use the relaxed-validation pattern with `validation.md`
  delta entries.
- `cli/state_builder.py`: SDD-040 modifies this CLI; SDD-036 + SDD-037
  consume its output surface.
- `cli/schema_lint.py`: SDD-036 likely extends this to validate the new
  `depends_on` field.
- `ledger/fleet.db`: SDD-036 audit-trail rows + SDD-037 Dispatches card
  both read/write here.

**External**:
- None. PI-6 is entirely in-repo and stdlib-only.

---

## Success Metrics

- All planned PI-6 sprints close DONE with full validation contracts
  checked (Sprint 13 may close DONE-WITH-CARRYOVER per its contingency
  posture).
- Test count holds at or above 337 (the PI-5 close baseline) and
  meaningfully grows in Sprints 11 and 12 (SDD-036 schema_lint extension,
  SDD-037 ledger-rendering tests).
- The owner-visible dashboard complaint that anchored PI-6 ("stale active
  focus + static page") is fully resolved by Sprint 10 close.
- One real-host bootstrap demo runs the new dashboard surface end-to-end
  (Day-to-Day Agent or equivalent) by Sprint 12 close.
- Sprint 13 either lands the carryover bundle or explicitly stamps the
  remaining items as carry-forward to PI-7 with owner approval.

---

## Cross-References

- Backlog: [`../../backlog/BACKLOG.md`](../../backlog/BACKLOG.md)
  - PI-6 anchor SDD-040 filed P1 under "PI-6 Dashboard Bundle (filed 2026-06-10)".
  - PI-6 candidates SDD-036 (P1) and SDD-037 (P2) filed under "Post-Sprint-7 Bundle".
  - PI-6 Sprint 13 carryovers SDD-038 (P3), SDD-034 (P3), SDD-039 (P2), PI-4 housekeeping.
- Predecessor PI: [`../PI-5/CURRENT_PI.md`](../PI-5/CURRENT_PI.md)
  - PI-5 close commit: `8417818` 2026-06-09 (DONE-WITH-CARRYOVER).
- Sprint 10 kickoff prompt: [`../../feature-prompts/SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
- Executive state surface: [`../../exec/state.md`](../../exec/state.md), [`../../exec/state.html`](../../exec/state.html) (SDD-040 modifies the generator that writes both)
- Owner direction record: 2026-06-10 owner verbatim ("Still says Active focus: azure-decommission (stale -- that wrapped up). Static -- refreshes only when you re-run state_builder.py") routed via Executive Manager.

---

## Sprints

### Sprint 1 -- Dashboard Parser Fix + Auto-Refresh -- CLOSED
**Status**: **CLOSED locally** 2026-06-10 (close prep approved by owner evidence `Approve close prep, no push`; no commit or push performed by F-23).
**Scope**: SDD-040 (state_builder.py parser fix + auto-refresh).
**Sprint kickoff**: [`../../feature-prompts/SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
**Close evidence**:
1. Tests: 337 -> 349 passed, 2 skipped.
2. Schema lint: clean.
3. Validation: SDD-040 9/9 REQUIRED + M1/M2/M3 checked.
4. Smoke: regenerated `state.md` no longer says `Active focus: azure-decommission`; current line reports SDD-040 close work.
5. Serve verification: handler-side meta refresh with configured cadence verified without manual CLI re-run.
6. Owner approval: EM prompt, 2026-06-10: `Approve close prep, no push`.
7. Commit chain: local close prep, commit pending.

### Sprint 2 -- Lifecycle Pipeline + Drag-to-Reorder -- NEXT PLANNED
**Status**: **NEXT PLANNED** (scope locked at SDD-036; kickoff prompt authored at Sprint 10 close)
**Planned scope**: SDD-036.
**Sprint kickoff**: [`../../feature-prompts/SPRINT-11-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-11-KICKOFF.prompt.md)

### Sprint 3 -- Dispatches Card + Health Pills -- PLANNED
**Status**: **PLANNED** (scope locked at SDD-037; kickoff prompt to be authored at Sprint 11 close)
**Planned scope**: SDD-037.

### Sprint 4 -- Aesthetic Tokens + Carryover Cleanup -- CONTINGENCY
**Status**: **CONTINGENCY** (pulled in only if Sprints 10-12 hold velocity; kickoff prompt to be authored at Sprint 12 close if pull-in is approved)
**Planned scope**: SDD-038 + carryovers (SDD-034 dedup, SDD-039 Article VII wording, PI-4 housekeeping).

---

## Notes for the next sprint lead

- Sprint 10 is the **smallest** sprint in PI-6 by design. Resist the urge
  to absorb SDD-036/037/038 -- they have their own sprints.
- SDD-040 has a stdlib-only constraint (Article V). Do not introduce
  `watchdog`, `flask`, or any non-stdlib dependency for auto-refresh.
  Polling, on-request refresh, or stdlib file-mtime sweep are the only
  acceptable mechanisms. Decide in CLARIFY.
- The non-serve invocation of `state_builder.py` must continue to write
  static `state.md` + `state.html` for git/diff use. Auto-refresh is a
  serve-mode-only behavior.
- Sprint 11 (SDD-036) is the largest CLARIFY surface in PI-6. Schedule
  the Architect early; the new `depends_on` frontmatter field needs an
  ADR.
