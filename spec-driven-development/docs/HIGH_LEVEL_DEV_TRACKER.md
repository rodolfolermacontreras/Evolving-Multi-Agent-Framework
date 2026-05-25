---
version: '1.0.0'
last_updated: 2026-05-25
owner: principal-executive-manager
co_owner: principal-product-manager
discipline: abstraction-not-detail
purpose: birds-eye operational view of all active sprints across the current PI
---

# High-Level Dev Tracker

The bird's-eye view of every sprint, every PI, every blocker. This file is
**abstraction, not detail** -- each sprint entry links down to its
[`Temp/SPRINT_#_DETAILED_*.md`](Temp/) deep spec. Never reproduce sprint
detail here.

Read [`ONBOARDING_KICK_OFF.md`](ONBOARDING_KICK_OFF.md) first if you are new.
Read [`RULES.md`](RULES.md) for the binding rules.

---

## Snapshot

| Field | Value |
|-------|-------|
| **Current PI** | PI-3 (Portability Validation + Live UI v2) |
| **PI started** | 2026-05-25 (kickoff today; PI-2 closed 2026-05-16) |
| **Current sprint** | Sprint 1 of 4 (Dashboard Freshness Unblock) |
| **Cadence** | Symbolic; ~1 day per sprint, ~5 sprints per PI (ADR-0003) |
| **Active worktrees** | 0 (S1 awaiting HITL provisioning) |
| **Tests passing** | 70 across 5 CLI suites + ledger (last verified at HEAD `39d2266`) |
| **Branch state** | `master` at `39d2266`, **34 commits ahead of origin** (HITL gate #10) |
| **Open lessons** | 5 (LESSON-006, 007, 008, 009, 010 -- see Sprint 3) |
| **HITL pending** | 9 Azure provisioning steps for Sprint 1 |

---

## Top 3 Next Moves

1. **Human runs the 9 HITL Azure provisioning steps for Sprint 1.** Listed in
   [`Temp/SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md`](Temp/SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md) Section 8. ~5 min once `az login` is done. This unblocks the
   entire PI-3 dispatch chain.
2. **SW Dev dispatches T-003 + T-004 to `developer-general`** in parallel
   worktrees `wt-pi3-s1-freshness-workflow` and `wt-pi3-s1-freshness-about`
   the moment the human says "done".
3. **PM amends `BACKLOG.md`** to move SDD-009 + SDD-010 from "PI-3 Sprint A
   (proposed)" to "PI-3 Sprint 1 (active)" and add SDD-011..SDD-014 for
   sprints 2-4. (Single-paragraph backlog hygiene; can be done in parallel
   with #1.)

---

## PI-3 Sprint Board (4 sprints)

| # | Title | Status | Owner | Worktree | Deps | Detail Doc |
|---|-------|--------|-------|----------|------|------------|
| **S1** | Dashboard About + Freshness Unblock | **BLOCKED on HITL** | SW Dev | `wt-pi3-s1-freshness-*` | None (Sprint 0 already shipped spec/plan/tasks/validation) | [SPRINT_1_DETAILED](Temp/SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md) |
| **S2** | Day-to-Day Brownfield Bootstrap | **Proposed** | PM + Architect (spec), SW Dev (dispatch) | `wt-pi3-s2-brownfield` | Parallel-safe with S1; will create artifacts in a SEPARATE repo, no master collision | [SPRINT_2_DETAILED](Temp/SPRINT_2_DETAILED_DAY_TO_DAY_BROWNFIELD_BOOTSTRAP.md) |
| **S3** | PI-2 Lessons Curation via /evolve | **Proposed** | PM (lead), Architect (constitution impact) | `wt-pi3-s3-lessons` | Parallel-safe; touches only `sprints/PI-2/lessons.md` + possibly `.github/skills/` | [SPRINT_3_DETAILED](Temp/SPRINT_3_DETAILED_PI2_LESSONS_CURATION.md) |
| **S4** | Live UI v2 Spec (Principal UI Designer kickoff) | **Proposed** | UI Designer (lead, ADR-0010), Architect (review) | `wt-pi3-s4-ui-v2` | Parallel-safe for the SPEC phase; implementation deferred to PI-4 | [SPRINT_4_DETAILED](Temp/SPRINT_4_DETAILED_LIVE_UI_V2_SPEC.md) |

### Status legend
- **Proposed** -- sprint scope drafted, awaiting Principal sign-off + dispatch
- **Active** -- worktree exists, workers dispatched, in IMPLEMENT or REVIEW
- **BLOCKED** -- HITL gate or cross-sprint dependency in the way
- **DONE** -- merged to master, validation passed, worktree torn down
- **Archived** -- detail doc moved from `Temp/` to `sprints/PI-N/`

---

## Dependency Graph

```
            +-----------+
            |   PI-3    |
            |  Kickoff  |
            +-----+-----+
                  |
        +---------+----------+--------------+--------------+
        v                    v              v              v
    +-------+            +-------+      +-------+      +-------+
    |  S1   |            |  S2   |      |  S3   |      |  S4   |
    | Fresh |            |Brown- |      |Lesson |      |UI v2  |
    | -ness |            | field |      |Curate |      | Spec  |
    +---+---+            +-------+      +-------+      +---+---+
        |                                                  |
        | (S2 may want to demo live dashboard               |
        |  after S1 deploys; soft dep, not hard)            |
        |                                                  |
        | (S4 design tokens may inform a future PI-4        |
        |  UI v2 IMPLEMENTATION sprint; S4 here is          |
        |  SPEC ONLY)                                       |
        |                                                  |
        +----- S1 must merge to master before --------------+
               cross-sprint visual changes from S4 land
```

- **S1 is the only HARD blocker** in this PI. S2/S3/S4 are parallel-safe.
- **S1 -> any UI implementation** is a soft dependency (S4 here is SPEC only).
- **S2 has zero collision risk with master** because all its file writes land
  in the Day-to-Day Agent repo (separate workspace).
- **S3 touches** `sprints/PI-2/lessons.md` and may amend skill files; coordinate
  with S4 if S4 proposes new UI-related skills.

---

## Open Lessons (carry-over for /evolve curation in S3)

| ID | One-liner | Source |
|----|-----------|--------|
| LESSON-004 | Ledger migration policy (carry-over from PI-1; **SHIPPED in PI-2** via `ledger/MIGRATION-POLICY.md` -- close in /evolve) | PI-1 |
| LESSON-006 | Closure ceremonies must touch ALL "current" markers | PI-2 |
| LESSON-007 | Pre-spec design exploration produces reusable tokens at near-zero cost | PI-2 |
| LESSON-008 | Two parallel specs for same file: declare one canonical | PI-2 |
| LESSON-009 | Windows SQLite + tempdir tests need `ignore_cleanup_errors=True` + `gc.collect()` | PI-2 |
| LESSON-010 | ACA Easy Auth needs `enableIdTokenIssuance=true` on companion app reg | PI-2 |

Full text: [`sprints/PI-2/lessons.md`](../sprints/PI-2/lessons.md).

---

## Tech Debt Visible at the Tracker Level

Not blocking, but should be addressed in PI-3 or queued for PI-4. Detail in
backlog and the relevant sprint docs.

| ID | Issue | Severity | Picked up by |
|----|-------|----------|--------------|
| TD-01 | `.github/agents/principal-architect.agent.md` still says "Project: Day-to-Day Agent" (residual from extraction); other Principal agent files may have the same drift | Low | S3 lessons sweep (add to skill/agent hygiene check) |
| TD-02 | 34 unpushed local commits on `master` | Medium | HITL #10 -- human approves push timing |
| TD-03 | `cli/common/*.py` are scaffolds, not implemented; canonical CLIs (state_builder, fleet, qa, retro, schema_lint) bypass them | Low | Future PI; not impacting current work |
| TD-04 | `domain/` skills marked as examples but still in `.github/skills/`; consider moving to `archetypes/python-web-service/skills/` | Low | Future PI |

---

## How to Update This File

This file is updated at end of every session AND on every sprint state change:

1. Bump `last_updated:` in frontmatter.
2. Adjust the "Snapshot" table (current sprint, test count, branch state).
3. Move sprint rows between status columns; never delete a sprint row,
   only mark it Archived.
4. Refresh the "Top 3 Next Moves" -- ALWAYS exactly 3.
5. If a lesson closes, strike it through with a date and link to the
   /evolve ADR or commit.
6. Re-render the dependency graph if any dep changes.
7. Commit as `docs(tracker): <one-line change>`.

This file is the **single source of truth for "what is happening right now."**
The roadmap is strategic, the backlog is prioritized; the tracker is operational.

---

## PI History

| PI | Window | Outcome | Lessons | Retro doc |
|----|--------|---------|---------|-----------|
| **PI-1** | 2026-05-12 -> 2026-05-13 | Generalization + first pilot (fleet ledger) | 4 captured, 4 curated | `sprints/PI-1/lessons.md` |
| **PI-2** | 2026-05-16 (3 sprints same day) | 5 CLIs shipped, live Azure deploy, first specialist promoted | 6 captured, 1 shipped in-PI (LESSON-005), 5 open | `sprints/PI-2/lessons.md` + `sprints/PI-2-retro.md` |
| **PI-3** | 2026-05-25 -> active | _in flight_ | _open_ | _TBD_ |
