---
id: SDD-PI-6-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-06-26
sprint: PI-6
---

# PI-6: Dashboard Reinvestment + Carryover Cleanup

- Status: **ACTIVE -> READY TO CLOSE** (Sprint 1 / Sprint 10 CLOSED locally 2026-06-10; Sprint 2 / Sprint 11 CLOSED 2026-06-24 with owner-approved commit + push; Sprint 3 / Sprint 12 / SDD-037 CLOSED 2026-06-25 with owner-approved commit + push; Sprint 4 / Sprint 13 CLOSED 2026-06-26 with scope SDD-042 + SDD-041 + SDD-039 and owner-approved commit + push -- SDD-038/034/PI-4 housekeeping deferred to PI-7. The PI-6 CLOSE itself remains a separate owner-approved decision and is NOT stamped here.)
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

### 4. Final PI-6 Value Sprint -- Dashboard + Governance (SDD-042 + SDD-041 + SDD-039)
**Why**: Sprint 13 was pulled in under owner delegation 2026-06-26 and
delivered the three highest-value remaining items, NOT the originally-framed
SDD-038 aesthetic-tokens contingency. SDD-042 fixes the stale dashboard
PI-label parser; SDD-041 ships a working OPEN-only Backlog drag-to-reorder
(Option A); SDD-039 rewords the Article VII context-isolation corollary and
bumps `principles.md` 1.3.0 -> 1.4.0 via ADR-018. The aesthetic-tokens +
dedup + PI-4 housekeeping bundle (SDD-038, SDD-034, PI-4 housekeeping) was
NOT pulled in and is deferred to PI-7.

**Success Criteria**: Dashboard header + HTML title surface the newest
ACTIVE PI (SDD-042, DONE); a dedicated OPEN-only "Backlog -- drag to
reprioritize" section keyed by SDD-xxx round-trips drag + up/down through
the safeguarded `move()` with DONE rows hidden and cross-project IAI
contamination removed (SDD-041, DONE); Article VII corollary reworded with
`principles.md` 1.3.0 -> 1.4.0 via ADR-018 (SDD-039, DONE).

**Features**: SDD-042, SDD-041, SDD-039. **CLOSED 2026-06-26.** Deferred to
PI-7: SDD-038 (aesthetic tokens), SDD-034 (content-shingle dedup), PI-4
housekeeping (domain-skill annotations, GH Actions Node.js bump), plus the
SDD-041 Option B reorder re-optimization.

---

## Sprint Allocation

| Sprint | Overall | Title | Items | Size | Why this order |
|--------|---------|-------|-------|------|----------------|
| **PI-6 Sprint 1** | Sprint 10 | Dashboard Parser Fix + Auto-Refresh | SDD-040 | S | **CLOSED locally 2026-06-10.** Highest-trust-payoff fix shipped in local working tree; active focus no longer points at stale azure-decommission work and serve-mode refresh is verified. Commit pending; no push performed. |
| **PI-6 Sprint 2** | Sprint 11 | Lifecycle Pipeline + Drag-to-Reorder (with Safeguards) | SDD-036 | L | **CLOSED 2026-06-24.** Shipped SDD-036 (lifecycle pipeline + 4-card docs row + reorder safeguards); tests 349 -> 412; schema lint clean; 10/10 REQUIRED + ADR-017 (proposed); owner-approved commit + push. Unblocks SDD-037, whose Dispatches card sits on the same dashboard surface as the SDD-036 lifecycle pipeline. |
| **PI-6 Sprint 3** | Sprint 12 | Dispatches Card + Health Pills | SDD-037 | M | **CLOSED 2026-06-25.** Shipped SDD-037 (Dispatches card + 4 header health pills) as additive `inject_*` post-processors on the SDD-036 surface; tests 412 -> 450; schema lint clean; 13/13 REQUIRED; Article X lock held; owner-approved commit + push. Sprint 13 (SDD-038 + carryovers) pull-in is a Highest-Executive decision, not authored at this close. |
| **PI-6 Sprint 4** | Sprint 13 | Final PI-6 Value Sprint (Dashboard + Governance) | SDD-042 (dashboard PI-label fix) + SDD-041 (OPEN-only Backlog reorder, Option A) + SDD-039 (Article VII wording + version bump) | M | **CLOSED 2026-06-26.** Pulled in under owner delegation; delivered the three highest-value items. SDD-038 aesthetic tokens + SDD-034 dedup + PI-4 housekeeping deferred to PI-7. |

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

### Sprint 2 -- Lifecycle Pipeline + Drag-to-Reorder -- CLOSED
**Status**: **CLOSED** 2026-06-24 (owner-approved commit + push; PI-6 remains ACTIVE; Sprint 12 / SDD-037 next planned).
**Scope**: SDD-036 (lifecycle pipeline on feature/sprint cards + 4-card Constitution/Spec/Sprint/ADRs docs row + keyboard-accessible backlog reorder with dependency-lock, append-only audit trail, and force-as-Level-2 governance).
**Sprint kickoff**: [`../../feature-prompts/SPRINT-11-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-11-KICKOFF.prompt.md)
**Close evidence**:
1. Tests: 349 -> 412 passed, 2 skipped (full `spec-driven-development/` suite; >= 349 required).
2. Schema lint: clean (exit 0).
3. Validation: SDD-036 10/10 REQUIRED (R-1..R-10) + manual M-1..M-3 + tone U-1..U-3 checked; Optional O-1..O-3 not implemented.
4. ADR: ADR-017 (proposed) -- optional `depends_on` field, `check_depends_on` validator, append-only `ledger/reorder-audit.jsonl`, `display-order.json` overlay (BACKLOG stays PM-authoritative), dependency-lock, force-as-Level-2.
5. Dashboard smoke: lifecycle pipeline + 4-card docs row render on feature/sprint cards in regenerated `exec/state.html`; 0 `<script>` tags (no JS framework).
6. Reorder smoke (isolated temp tree, no real-tree mutation): dependency-blocked move rejected exit 1 with plain-language reason; legal move exit 0 + one 9-field append-only audit row.
7. Article X lock held: the five SHA-pinned render functions were not edited; SDD-036 surfaces are `inject_lifecycle_html()` post-processors.
8. Owner ratification: APPROVED FOR COMMIT + PUSH.

**Retro**: Sprint 11 landed the largest CLARIFY surface in PI-6 without scope leakage -- `depends_on` shipped optional (no flag-day backfill), reorder writes an append-only overlay + audit trail rather than mutating BACKLOG, and force-override is governed as a Level-2 runtime gate. The UI Lifecycle Variant (Article XII) split kept the schema/ledger items strict while letting the three visual surfaces (R-1/R-2/R-8) close as-locked with zero delta entries. DA-Evidence Discipline was honored: every close claim came from a real run, and the reorder smoke ran against an isolated temp tree so no real `display-order.json`/`reorder-audit.jsonl` was mutated. SDD-037 (Dispatches card + health pills) is unblocked on the same dashboard surface and is the Sprint 12 anchor.

### Sprint 3 -- Dispatches Card + Health Pills -- CLOSED
**Status**: **CLOSED** 2026-06-25 (owner-approved commit + push; SDD-037 DONE). See sprint-progress.md "Sprint 12 -- CLOSED".
**Scope**: SDD-037.
**Sprint kickoff**: [`../../feature-prompts/SPRINT-12-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-12-KICKOFF.prompt.md)

### Sprint 4 -- Final PI-6 Value Sprint (Dashboard + Governance) -- CLOSED
**Status**: **CLOSED** 2026-06-26 (pulled in under owner delegation; owner-approved commit + push). See sprint-progress.md "Sprint 13 -- CLOSED".
**Scope**: SDD-042 (dashboard PI-label fix; `ac1ccf0`) + SDD-041 (working OPEN-only Backlog reorder, Option A; `afbfe47`) + SDD-039 (Article VII wording + ADR-018 + `principles.md` 1.3.0 -> 1.4.0; `699d8bb`).
**Deferred to PI-7**: SDD-038 (aesthetic tokens), SDD-034 (content-shingle dedup), PI-4 housekeeping (domain-skill annotations, GH Actions Node.js bump), SDD-041 Option B reorder re-optimization.
**Sprint kickoff**: [`../../feature-prompts/SPRINT-13-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-13-KICKOFF.prompt.md)

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
