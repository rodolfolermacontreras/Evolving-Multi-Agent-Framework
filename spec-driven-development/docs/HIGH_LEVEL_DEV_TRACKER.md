---
version: '1.2.0'
last_updated: 2026-07-08
owner: principal-executive-manager
co_owner: principal-product-manager
discipline: abstraction-not-detail
purpose: birds-eye operational view of all active sprints across the current PI
---

# High-Level Dev Tracker

The bird's-eye view of every sprint, every PI, every blocker. This file is
**abstraction, not detail** -- each PI links to its
[`Management/PI-N/INDEX.md`](Management/) and each sprint to its
[`Management/PI-N/Sprint-N-{title}/SPEC.md`](Management/) deep spec. Never
reproduce sprint detail here.

Read [`ONBOARDING_KICK_OFF.md`](ONBOARDING_KICK_OFF.md) first if you are new.
Read [`RULES.md`](RULES.md) for the binding rules.

---

## Snapshot

> **Live operational view.** The dashboard [`exec/state.html`](../exec/state.html)
> and the append-only ledger [`exec/sprint-progress.md`](../exec/sprint-progress.md)
> are the source of truth for "what is happening right now." This tracker points
> at those live surfaces instead of freezing counts that rot (the root
> `README.md` no-hardcoded-count pattern). The PI-3 sprint board further down is
> preserved as the PI-3 historical snapshot, not current state.

| Field | Value |
|-------|-------|
| **Current PI** | PI-9 (Experience Polish) -- 8 PIs closed (PI-1..PI-8), PI-9 active |
| **Current sprint** | See [`exec/sprint-progress.md`](../exec/sprint-progress.md) (read bottom-up) |
| **Cadence** | Symbolic; ~1 day per sprint, ~5 sprints per PI (ADR-0003) |
| **Tests passing** | See the live count in [`exec/state.md`](../exec/state.md) and the ledger (schema_lint clean) |
| **Branch state** | See `git status` and the dashboard freshness line |
| **PI history** | PI-1..PI-7 closed; PI-8 active -- see [`constitution/roadmap.md`](../constitution/roadmap.md) |

---

## Top 3 Next Moves (PI-3 historical snapshot -- see the live ledger for current moves)

1. **S2 (Day-to-Day Brownfield Bootstrap) -- human picks dogfood feature.** T-001
   needs the human to pick which Day-to-Day feature to walk through the lifecycle.
   Then `bootstrap.py brownfield --draft-only` can run.
2. **Human runs the 9 HITL Azure provisioning steps for Sprint 1.** Listed in
   [Sprint-1 SPEC](Management/PI-3/Sprint-1-dashboard-freshness-unblock/SPEC.md)
   Section 8. ~5 min once `az login` is done.
3. **Push to origin.** 60+ commits ahead. `git push origin master` when ready.

---

## PI-3 Sprint Board (historical snapshot -- PI-3)

| # | Title | Status | Owner | Worktree | Deps | Detail Doc |
|---|-------|--------|-------|----------|------|------------|
| **S1** | Dashboard About + Freshness Unblock | **BLOCKED on HITL** | SW Dev | `wt-pi3-s1-freshness-*` | None (Sprint 0 already shipped spec/plan/tasks/validation) | [SPEC](Management/PI-3/Sprint-1-dashboard-freshness-unblock/SPEC.md) |
| **S2** | Day-to-Day Brownfield Bootstrap | **Proposed** | PM + Architect (spec), SW Dev (dispatch) | `wt-pi3-s2-brownfield` | Parallel-safe with S1, S3, S4, S5; artifacts in SEPARATE repo | [SPEC](Management/PI-3/Sprint-2-day-to-day-brownfield-bootstrap/SPEC.md) |
| **S3** | PI-2 Lessons Curation via /evolve | **DONE** | PM (lead), Architect (constitution impact) | -- | 4 skills amended (v1.0->1.1), 1 lesson deferred, 1 closed retro, tech debt spec filed | [SPEC](Management/PI-3/Sprint-3-pi2-lessons-curation/SPEC.md) |
| **S4** | Live UI v2 Spec (Principal UI Designer kickoff) | **DONE** | UI Designer (lead, ADR-0010 approved), Architect (review) | -- | Parallel-safe for the SPEC phase; implementation deferred to PI-4 | [SPEC](Management/PI-3/Sprint-4-live-ui-v2-spec/SPEC.md) |
| **S5** | Navigation Layer Migration -- Management/ Structure | **DONE** | EM (lead), SW Dev (build-index), PM (Rule 13) | -- | Landed first; S2/S3/S4 adopt new structure from day one | [SPEC](Management/PI-3/Sprint-5-management-navigation-layer/SPEC.md) |

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
        +---------+----------+--------------+--------------+--------------+
        v                    v              v              v              v
    +-------+            +-------+      +-------+      +-------+      +-------+
    |  S1   |            |  S2   |      |  S3   |      |  S4   |      |  S5   |
    | Fresh |            |Brown- |      |Lesson |      |UI v2  |      | Nav   |
    | -ness |            | field |      |Curate |      | Spec  |      | Layer |
    +---+---+            +---+---+      +---+---+      +---+---+      +---+---+
        |                    ^              ^              ^              |
        |  (S2 demo benefits |              |              |              |
        |   from S1 deploy)  |              |              |              |
        |                    |              |              |              |
        |                    +--------------+--------------+--------------+
        |                                                                 |
        |                  S5 SHOULD land first so S2/S3/S4 adopt the new
        |                  Management/ structure from day one
        |                  (soft preference; technically parallel-safe)
        |
        +----- S1 must merge to master before any cross-sprint visual
               changes from S4 can land (PI-4 work; out of scope here)
```

- **S1 is the only HARD blocker** in this PI. S2/S3/S4/S5 are parallel-safe.
- **S5 -> S2/S3/S4** is a SOFT preference: if S5 lands first, the other sprints
  adopt `Management/PI-3/Sprint-N-{title}/SPEC.md` from inception and avoid a
  retroactive migration. If S5 lands later, T-003 in S5 picks up whatever
  is in `Temp/` at that time.
- **S1 -> any UI implementation** is a soft dependency (S4 here is SPEC only).
- **S2 has zero collision risk** with this repo's `master` because all its file
  writes land in the Day-to-Day Agent repo.
- **S3 touches** `sprints/PI-2/lessons.md` and may amend skill files; coordinate
  with S5 if S5 proposes new skills (S5 does not).
- **S5** touches `docs/Temp/` (migration), `docs/Management/` (new),
  `HIGH_LEVEL_DEV_TRACKER.md`, `ONBOARDING_KICK_OFF.md`, `RULES.md` (Rule 13
  add), `cli/state_builder.py` (build-index subcommand), `INSTRUCTIONS.md`.
  Coordinate with S3 on `RULES.md` if S3 amends rules too (S3 currently does
  not).

---

## Open Lessons (carry-over for /evolve curation in S3)

All PI-2 lessons curated in S3; LESSON-007 closed in S4 via design-tokens skill.
No open lessons remaining.

| ID | One-liner | Source | Status |
|----|-----------|--------|--------|
| LESSON-004 | Ledger migration policy | PI-1 | **CLOSED** (S3) |
| LESSON-006 | Closure ceremonies must touch ALL "current" markers | PI-2 | **SHIPPED** (S3, constitution-sync v1.1) |
| LESSON-007 | Pre-spec design exploration produces reusable tokens | PI-2 | **SHIPPED** (S4, design-tokens skill v1.0) |
| LESSON-008 | Two parallel specs for same file: declare one canonical | PI-2 | **SHIPPED** (S3, to-spec v1.1) |
| LESSON-009 | Windows SQLite + tempdir tests need cleanup fixes | PI-2 | **SHIPPED** (S3, testing-conventions v1.1) |
| LESSON-010 | ACA Easy Auth needs `enableIdTokenIssuance=true` | PI-2 | **SHIPPED** (S3, retrospectively) |

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
| **PI-1** | 2026-05-12 -> 2026-05-13 | Generalization + first pilot (fleet ledger) | 4 captured, 4 curated | [INDEX](Management/PI-1/INDEX.md) / `sprints/PI-1/lessons.md` |
| **PI-2** | 2026-05-16 (3 sprints same day) | 5 CLIs shipped, live Azure deploy, first specialist promoted | 6 captured, 1 shipped in-PI (LESSON-005), 5 open | [INDEX](Management/PI-2/INDEX.md) / `sprints/PI-2/lessons.md` |
| **PI-3** | 2026-05-25 -> 2026-05-26 | Portability validation + Live UI v2 spec + navigation layer | curated | [INDEX](Management/PI-3/INDEX.md) |
| **PI-4** | 2026-06 | Alpha release -- filesystem data contracts (SDD-FDC-001) | curated | [`constitution/roadmap.md`](../constitution/roadmap.md) |
| **PI-5** | 2026-06 | Closed -- see roadmap | curated | [`constitution/roadmap.md`](../constitution/roadmap.md) |
| **PI-6** | 2026-06 -> 2026-06-25 | Closed -- see roadmap | curated | [`constitution/roadmap.md`](../constitution/roadmap.md) |
| **PI-7** | -> 2026-07-07 | Hardening + orchestration maturity -- CLOSED (DONE-WITH-CARRYOVER at `7088f35`) | curated | [`constitution/roadmap.md`](../constitution/roadmap.md) |
| **PI-8** | 2026-07-08 -> active | Truth in the Window (dashboard + docs + roadmap truth) | _in flight_ | [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) |
