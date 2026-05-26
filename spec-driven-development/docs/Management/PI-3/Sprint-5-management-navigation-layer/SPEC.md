---
sprint: PI-3 / S5
title: Navigation Layer Migration -- Management/ Structure
status: In-Flight (ADR-0011 approved, Rule 13 landed; T-002 unblocked for dispatch)
owner: principal-executive-manager (lead, owns tracker + INDEXes), principal-software-developer (ledger -> INDEX automation), principal-product-manager (rule + ceremony binding)
worktree: wt-pi3-s5-management-layer
deps: Soft preference -- LAND BEFORE S2/S3/S4 dispatch begins so those sprints adopt the new structure from day one. Parallel-safe with S1 (S1 is HITL-blocked, no file collision).
created: 2026-05-25
canonical_spec_dir: spec-driven-development/specs/2026-05-25-navigation-layer/ (to be created in CLARIFY)
backlog_ids: SDD-015 (Management nav layer), SDD-016 (state_builder INDEX auto-gen) -- to be assigned by PM
adr: ADR-0011 (Three-Tier Navigation Layer) to be authored as part of T-001
scope: Manual migration in Phase 1; state_builder.py auto-gen of mechanical INDEX parts in Phase 2 (in-scope this sprint, low ambition); full automation deferred to PI-4
trigger: External feedback received 2026-05-25 from parallel team adopting framework -- visibility/transparency gap blocking adoption
---

# Sprint 5 -- Navigation Layer Migration (Management/ Structure)

## Required Reading

1. [`ONBOARDING_KICK_OFF.md`](../ONBOARDING_KICK_OFF.md)
2. [`RULES.md`](../RULES.md)
3. [`HIGH_LEVEL_DEV_TRACKER.md`](../HIGH_LEVEL_DEV_TRACKER.md)
4. This file
5. The feedback document (paste-only, verbatim in Section 1 below)
6. Current artifacts being migrated:
   - `docs/Temp/SPRINT_1_DETAILED_*.md` through `SPRINT_4_DETAILED_*.md`
   - `sprints/PI-1/lessons.md`
   - `sprints/PI-2/lessons.md` + `sprints/PI-2-retro.md`
   - `specs/YYYY-MM-DD-*/` (13 feature dirs to be linked from PI INDEXes)
7. [`cli/state_builder.py`](../../cli/state_builder.py) -- the CLI that Phase 2 will extend

## 1. The Feedback (verbatim, preserved as binding context)

> The framework already records everything it does -- the SQLite ledger is a
> complete, machine-queryable audit trail, and the Azure dashboard gives a live
> runtime view. Both are working as intended. But there is a gap, and it is a
> real one: at any given moment it is hard for a human to open the repo and see
> where we are -- which PI is active, which sprint is in flight, what document
> governs it, what was decided, and who did the work. The ledger answers this
> only if you query it; the dashboard answers it only while it's up and you're
> looking at it.
>
> A previous project we ran had weaker tooling but much stronger navigability:
> you could open one tracker, follow it down, and always know the state of the
> whole effort at a glance. We want to bring that property into this framework
> without removing anything that exists. This is purely additive -- a durable,
> version-controlled, Markdown navigation layer that sits alongside the ledger
> and dashboard, not in place of them.

Three complementary views of the same truth:

- **Ledger (SQLite)** -- complete audit trail. Authoritative, machine-readable, not glanceable.
- **Dashboard (Azure)** -- live runtime view. Real-time, external, ephemeral.
- **Tracker + INDEX (Markdown, in-repo)** -- durable human map. Glanceable, diffable, travels with the repo. **This is what we are adding.**

## 2. Sprint Goal (one sentence)

Replace the flat `docs/Temp/` sprint-detail layer with a three-tier
human-readable navigation pyramid (`HIGH_LEVEL_DEV_TRACKER.md` -> `Management/PI-N/INDEX.md` -> `Management/PI-N/Sprint-N-{title}/SPEC.md` + `AGENT_NOTES.md`),
backfill PI-1 and PI-2 INDEXes from existing artifacts, and bind the update
discipline to existing ceremonies so the navigation layer cannot rot.

## 3. Why this matters (business case)

External feedback from the parallel team using the framework today:
**visibility and transparency are the items blocking adoption.** The ledger
+ dashboard solve "what is recorded?" but not "where are we right now?"
A new agent or human cannot open the repo and answer "what's the current PI,
current sprint, who is doing what, why?" in under 60 seconds without
running CLI tools or visiting an external URL. The proposed structure
restores that property -- which the team's previous framework had even with
weaker underlying tooling.

This is **purely additive**. Nothing existing is removed. Ledger and
dashboard remain authoritative for their respective dimensions.

## 4. Acceptance Criteria

| # | AC | Verification |
|---|----|--------------|
| AC1 | `Management/` folder exists at `spec-driven-development/docs/Management/` with subfolders `PI-1/`, `PI-2/`, `PI-3/` | `ls Management/` |
| AC2 | Each PI has an `INDEX.md` with: goal/theme, sprint list (status), what-was-done feature-by-feature (linked to ADRs/specs), key decisions (linked to ADRs), where full specs live (linked to Sprint folders), on-the-ground notes/lessons | Read & verify each INDEX |
| AC3 | Every sprint in each PI has a folder `Sprint-N-<kebab-title>/` containing `SPEC.md` (the coordination doc) and `AGENT_NOTES.md` (initially empty template for active sprints; backfilled with what we can reconstruct for closed sprints) | `find Management -name SPEC.md`, `find Management -name AGENT_NOTES.md` |
| AC4 | `docs/Temp/` is empty (all SPRINT_*.md files moved to `Management/PI-3/Sprint-N-{title}/SPEC.md`) | `ls Temp/` returns empty or contains only a `README.md` explaining the directory is deprecated |
| AC5 | `HIGH_LEVEL_DEV_TRACKER.md` updated: PI rows link to `Management/PI-N/INDEX.md` instead of (or in addition to) `Temp/`; "Sprint Board" rows link to `Management/PI-3/Sprint-N-{title}/SPEC.md` | Click every link in the tracker; all resolve |
| AC6 | `ONBOARDING_KICK_OFF.md` Section 0 (4-pointer read) extended to a **5-pointer read** that adds `Management/PI-{current}/INDEX.md` between the tracker and the sprint detail | Diff the file |
| AC7 | `RULES.md` adds **Rule 13: No untracked sprint work** -- "No work on a sprint may begin without a corresponding `Management/PI-#/Sprint-#-{title}/` folder + tracker entry" | Diff the file |
| AC8 | Ceremony binding documented: `SPEC.md` updated each dispatch/REVIEW; PI `INDEX.md` updated at DONE + /replan; tracker updated every session. This is captured in `RULES.md` Section 4 (Definition of DONE) plus relevant skill files | Diff RULES + relevant skills |
| AC9 | `cli/state_builder.py` extended with `build-index` subcommand: emits the mechanical parts of a PI INDEX (sprint list with status, dispatch count per sprint, last-marked outcome) by querying `ledger/fleet.db`. Human/agent prose sections are preserved across regenerations via a marker block | Run `python cli/state_builder.py build-index --pi PI-3`; output appears at `Management/PI-3/INDEX.md` with mechanical sections refreshed |
| AC10 | New tests cover `build-index`: at minimum, 3 tests (empty PI, populated PI, marker-block preservation) | `python -m pytest cli/test_state_builder.py -k "build_index" -v` >= 3 passed |
| AC11 | ADR-0011 (Three-Tier Navigation Layer) authored and approved -- captures the decision, alternatives considered (single tracker only, dashboard-only, Wiki external), and the rationale for adopting the borrowed pattern | File exists in `docs/ADR/` |
| AC12 | First closure dry-run: when S5 itself closes, its INDEX entry and ground notes are populated through the new ceremony -- proving the discipline works on its first eligible event | `Management/PI-3/INDEX.md` reflects S5 DONE with rationale |
| AC13 | Onboarding smoke test: a fresh agent (or human) starting from `HIGH_LEVEL_DEV_TRACKER.md` can navigate to the active sprint's `SPEC.md` in under 60 seconds using only the links in the three-tier hierarchy. Validates glanceability, not just file existence. | Timed walkthrough by a fresh agent or manual test |

## 5. Task Decomposition

| ID | Description | Owner | Tag | Status | File scope |
|----|-------------|-------|-----|--------|------------|
| T-001 | Author ADR-0011 (Three-Tier Navigation Layer): context, decision, alternatives, scope, reversibility. Cite the verbatim feedback as provenance. | EM (drafts), Architect (reviews) | [S][HITL] (Level-1 + ADR binding requires human sign-off per RULES HITL #8) | DONE (022a9c7) | 1 file |
| T-002 | Create skeleton: `Management/PI-1/INDEX.md`, `Management/PI-2/INDEX.md`, `Management/PI-3/INDEX.md`. Empty/templated for PI-1 and PI-2 until T-004/T-005 backfill them. | developer-general | [P][AFK] | Unblocked (T-001 DONE) | 3 files |
| T-003 | Migrate `docs/Temp/SPRINT_1_DETAILED_*.md` through `SPRINT_4_DETAILED_*.md` to `Management/PI-3/Sprint-N-{title}/SPEC.md`. Create empty `AGENT_NOTES.md` per sprint as templates. Move (`git mv`) not copy to preserve history. | developer-general | [P][AFK] | Blocked on T-002 | 4 moves + 4 new template files |
| T-004 | Backfill `Management/PI-1/INDEX.md` from `sprints/PI-1/lessons.md`, `specs/2026-05-12-fleet-ledger/`, ledger rows for PI-1 dispatches (if any), and `roadmap.md` PI-1 section. Include: theme, sprint list, what-was-done, ADRs 001-007, lessons, links. **PI-1 sprint SPEC.md files are summaries only** (what happened, key commits, outcome) -- not full coordination specs, since PI-1 never produced formal sprints. | qa-engineer-general (research + draft), EM (review) | [S] | Blocked on T-002 | 1 file + new `Management/PI-1/Sprint-N-{title}/SPEC.md` summary per PI-1 sprint (sprints aren't formally numbered in PI-1; use logical groupings from commit log) |
| T-005 | Backfill `Management/PI-2/INDEX.md` from `sprints/PI-2/lessons.md`, `sprints/PI-2-retro.md`, the 5 PI-2 spec dirs, ADRs 008-009, ledger rows for PI-2. Include Sprint-A, Sprint-B, Sprint-C as the three same-day sprints documented in retro. | qa-engineer-general (research + draft), EM (review) | [S] | Blocked on T-002 (can run parallel to T-004) | 1 INDEX + 3 sprint folders |
| T-006 | Populate `Management/PI-3/INDEX.md` for the IN-FLIGHT PI: theme (portability validation + live UI v2), 5 sprints with current status (S1 BLOCKED, S2-S4 Proposed, S5 in-flight executing this very sprint), key decisions (ADR-0010, ADR-0011), in-flight feature SDD-009/010, open lessons table | EM | [S] | Blocked on T-003, T-004, T-005 | 1 file |
| T-007 | Update `HIGH_LEVEL_DEV_TRACKER.md`: PI rows now link to `Management/PI-N/INDEX.md`. Sprint board rows link to `Management/PI-3/Sprint-N-{title}/SPEC.md`. Add a "Navigation Layer" line to the Snapshot table. Refresh dep graph. | EM | [S] | Blocked on T-006 | 1 file |
| T-008 | Extend `ONBOARDING_KICK_OFF.md` Section 0 to **5-pointer read** (insert PI INDEX between tracker and sprint detail). Update Section 13 (Agent Dispatch Flow) to mention AGENT_NOTES.md as the per-sprint ground-truth artifact. | EM | [S][P with T-009] | Blocked on T-006 | 1 file |
| T-009 | Add **Rule 13: No untracked sprint work** to `RULES.md`. Update Section 4 (DONE) with the new ceremony bindings (SPEC updated each REVIEW, INDEX updated at DONE + /replan, tracker every session). Bump RULES version (MINOR: added rule). | PM (drafts), Architect (reviews per Article VIII), Human (approves per HITL #8 if binding) | [S][HITL] | DONE (022a9c7) | 1 file |
| T-010 | Implement `cli/state_builder.py build-index --pi PI-N` subcommand. Reads ledger; emits mechanical INDEX sections (sprint list, dispatch counts, last-marked outcomes) inside `<!-- BEGIN/END auto-generated -->` marker blocks that preserve human prose outside the markers. | developer-cli-specialist-1 | [S] | Blocked on T-002 (needs INDEX template format finalized) | 1 file (state_builder.py) |
| T-011 | Write 3+ tests for `build-index`: empty PI, populated PI from ledger fixture, marker-block preservation across re-runs. Follow LESSON-009 Windows SQLite cleanup pattern. | developer-cli-specialist-1 | [S] | Blocked on T-010 | 1 file (test_state_builder.py) |
| T-012 | Update `INSTRUCTIONS.md` (repo root) to mention the new navigation layer as the first stop after CONTEXT.md. | EM | [S][AFK] | Blocked on T-008 | 1 file |
| T-013 | Deprecate `docs/Temp/` formally: leave a `Temp/README.md` redirect note explaining the move; remove empty Temp folder OR keep as a "scratch" zone with a strict no-sprint-detail rule. PM decides which. | PM | [S][AFK] | Blocked on T-003 | 1 file |
| T-014 | First closure dry-run: when S5 itself closes, its row in `Management/PI-3/INDEX.md` + `Sprint-5-management-navigation-layer/AGENT_NOTES.md` are populated through the new ceremony. Captures the discipline working end-to-end on its first eligible event. | EM + closing worker | [S] | At end of sprint | -- |

### Parallelization plan

After T-001 (ADR) and T-002 (skeleton), the following sets are parallel-safe:

- Set A: T-004 (PI-1 backfill) + T-005 (PI-2 backfill) + T-010 (build-index impl)
- Set B (after Set A): T-006 (PI-3 INDEX), then T-007/T-008/T-009/T-012 in parallel (different files), then T-011 (tests for T-010)

### Coordination directive: `cli/state_builder.py`

Both S5/T-010 and S1/T-004 modify `cli/state_builder.py` (different subcommands:
`build-index` vs. About-section template). **Single rule: S5/T-010 merges to
master before S1/T-004 dispatches.** No worktree-sharing alternative. S1's HITL
block on 9 Azure provisioning steps makes this sequencing natural -- S1 cannot
dispatch until those steps are completed by the human.

Estimated wall-clock with parallel dispatch: 1-2 sessions.

## 6. Worktree Plan

```powershell
git worktree add ../wt-pi3-s5-management-layer -b pi3/s5/management-layer master
```

Single worktree -- all changes are in this repo, no cross-repo work like S2.

Tear down after merge:

```powershell
git worktree remove ../wt-pi3-s5-management-layer
git branch -d pi3/s5/management-layer
```

## 7. Dispatch Tracker

| Dispatch ID | Task | Worker | Sent | Marked | Outcome |
|-------------|------|--------|------|--------|---------|
| (pending) | T-002 | developer-general | -- | -- | -- |
| (pending) | T-003 | developer-general | -- | -- | -- |
| (pending) | T-004 | qa-engineer-general | -- | -- | -- |
| (pending) | T-005 | qa-engineer-general | -- | -- | -- |
| (pending) | T-010 | developer-cli-specialist-1 | -- | -- | -- |
| (pending) | T-011 | developer-cli-specialist-1 | -- | -- | -- |

## 8. Validation / Test Results

Empty until T-010/T-011 land. Evidence will be captured in `validation.md`
in `specs/2026-05-25-navigation-layer/` once that dir is created in CLARIFY.

## 9. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Hand-maintained Markdown rots the moment updating becomes optional (the explicit warning from feedback) | Bind updates to existing ceremonies via Rule 13 + DONE definition (T-009). Phase 2 auto-gen (T-010/T-011) takes the highest-rot-risk sections (sprint list, dispatch counts) off human hands entirely. |
| R2 | Backfill of PI-1 (T-004) is archaeology -- some sprint-level grouping may be subjective since PI-1 wasn't formally sprint-divided | Document the subjective groupings in the INDEX itself; mark sections as "reconstructed from commit log" so future readers understand provenance. |
| R3 | Migration (T-003) collides with the in-flight S1 sprint detail doc | S1 is BLOCKED on HITL with zero file activity. Coordinate timing: do T-003 between S1's HITL wait and the dispatch. If S1 dispatches first, T-003 just operates on a couple-of-commits-old file. |
| R4 | Renaming `Temp/SPRINT_*.md` -> `Management/PI-3/Sprint-N-{title}/SPEC.md` breaks links in HIGH_LEVEL_DEV_TRACKER (which currently points to `Temp/`) | T-007 updates the tracker as part of the same sprint. Order tasks: T-003 (migration) -> T-007 (tracker links updated) in same commit if possible. |
| R5 | Rule 13 ("no untracked sprint work") is a behavior change for any in-flight work | Apply Rule 13 prospectively. Currently in-flight S1 is grandfathered via the migration in T-003. |
| R6 | Auto-gen marker-block parsing could clobber human prose if marker is malformed | T-011 marker-block preservation test catches this. Also: do not blanket-overwrite; INDEX file must already exist before `build-index` will run. |

## 10. HITL Gates Specific to this Sprint

- T-001 (ADR-0011): per RULES HITL #8 (new ADR with status binding requires human approval)
- T-009 (Rule 13 addition + DONE redefinition): RULES.md is amendable only by human per its own frontmatter
- General: per Rule 12, no provisioning/credentials/Azure work in this sprint (zero exposure)

## 11. Scope guards (what is NOT in this sprint)

- Building a GUI to view the navigation layer (dashboard is the live view; this layer is in-repo Markdown)
- Generating the entire INDEX programmatically (Phase 2 generates only mechanical sections; rationale + lessons stay human-authored)
- Renaming `specs/YYYY-MM-DD-{slug}/` feature dirs (those remain the feature lifecycle layer; sprint folders link to them)
- Modifying the SQLite schema (ledger stays authoritative; `build-index` only reads)
- Bulk-rewriting ADRs to add navigation-layer cross-references (let those amend organically)
- Migrating `INSTRUCTIONS.md` content into the new structure (T-012 only adds a pointer)

## 12. Definition of DONE for this sprint

Per [`RULES.md`](../RULES.md) Section 4, AND:

- [ ] AC1-AC13 verified
- [ ] ADR-0011 approved and landed
- [ ] Rule 13 added to RULES.md (semver bump: 1.0.0 -> 1.1.0); RULES.md version-history block updated
- [ ] All four PI-3 sprint detail docs migrated; `docs/Temp/` is empty (or contains only deprecation README)
- [ ] PI-1, PI-2, PI-3 INDEXes populated and link to their respective sprint folders
- [ ] `build-index` subcommand operational with 3+ passing tests
- [ ] Existing 70 tests still pass (no regressions); new tests bring total to >= 73
- [ ] `HIGH_LEVEL_DEV_TRACKER.md` and `ONBOARDING_KICK_OFF.md` and `INSTRUCTIONS.md` all updated
- [ ] First closure dry-run completed: S5 itself populates the new structure on close
- [ ] This file moved to `Management/PI-3/Sprint-5-management-navigation-layer/SPEC.md`
- [ ] Worktree `wt-pi3-s5-management-layer` torn down
- [ ] Lesson candidate captured: did the new structure deliver the glanceability claim? Did the binding-to-ceremonies prevent rot?

## 13. Status Log

| Date | Event |
|------|-------|
| 2026-05-25 | External feedback from parallel team received; visibility/transparency identified as adoption blocker |
| 2026-05-25 | EM authored this S5 plan; open question on file naming resolved (Option B with refinements: folder carries title, SPEC.md + AGENT_NOTES.md inside) |
| _next_ | Human approves: (a) execute S5 immediately to give parallel team early benefit, OR (b) approve plan and queue for after S1 unblocks |
| 2026-05-25 | Parallel EM review completed; three amendments accepted: AC13 (onboarding smoke test), A2 (single coordination directive for state_builder.py), A3 (PI-1 backfill scope constrained to summaries) |
| 2026-05-25 | ADR-0011 approved (HITL #8), committed at `022a9c7`. Rule 13 + DONE ceremony bindings landed in RULES.md v1.1.0. T-001 and T-009 marked DONE. |

---

## Appendix A: Target file tree (after migration)

```
spec-driven-development/docs/
  HIGH_LEVEL_DEV_TRACKER.md          <- top of pyramid, spans all PIs
  RULES.md
  ONBOARDING_KICK_OFF.md
  CHEAT-SHEET.html
  CLI-PATTERN.md
  FINAL_MERGED_PLAN.md
  SCORECARD.md
  1_1_STATUS_REPORT_SDD.md
  ADR/
    001-sdd-framework.md
    ...
    010-hire-principal-ui-designer.md
    011-three-tier-navigation-layer.md  <-- NEW
  Management/                            <-- NEW
    PI-1/
      INDEX.md
      Sprint-1-extraction-and-generalization/
        SPEC.md
        AGENT_NOTES.md
      Sprint-2-fleet-ledger-pilot/
        SPEC.md
        AGENT_NOTES.md
    PI-2/
      INDEX.md
      Sprint-A-state-builder-fleet-bridge/
        SPEC.md
        AGENT_NOTES.md
      Sprint-B-qa-retro-schema-lint/
        SPEC.md
        AGENT_NOTES.md
      Sprint-C-batch-dispatch-specialist-hire/
        SPEC.md
        AGENT_NOTES.md
    PI-3/
      INDEX.md
      Sprint-1-dashboard-freshness-unblock/
        SPEC.md                          <-- migrated from Temp/SPRINT_1_DETAILED_*.md
        AGENT_NOTES.md
      Sprint-2-day-to-day-brownfield-bootstrap/
        SPEC.md                          <-- migrated from Temp/SPRINT_2_DETAILED_*.md
        AGENT_NOTES.md
      Sprint-3-pi2-lessons-curation/
        SPEC.md                          <-- migrated from Temp/SPRINT_3_DETAILED_*.md
        AGENT_NOTES.md
      Sprint-4-live-ui-v2-spec/
        SPEC.md                          <-- migrated from Temp/SPRINT_4_DETAILED_*.md
        AGENT_NOTES.md
      Sprint-5-management-navigation-layer/
        SPEC.md                          <-- migrated from THIS FILE
        AGENT_NOTES.md
  Temp/
    README.md                            <-- deprecation notice + redirect
```

## Appendix B: Skeleton for `Management/PI-N/INDEX.md`

```markdown
---
pi: PI-N
status: Active | Closed | Proposed
theme: <one-line>
started: YYYY-MM-DD
closed: YYYY-MM-DD or "in flight"
owner: principal-executive-manager
last_updated: YYYY-MM-DD
---

# PI-N -- <Theme>

## Goal
<one paragraph -- what this PI is trying to prove or ship>

## Sprint List

<!-- BEGIN auto-generated:sprints (refreshed by `cli/state_builder.py build-index`) -->
| Sprint | Title | Status | Dispatches | Last Outcome | Detail |
|--------|-------|--------|------------|--------------|--------|
| 1 | <title> | DONE | 3 | success | [Sprint-1-...](Sprint-1-...) |
| 2 | <title> | Active | 1 | -- | [Sprint-2-...](Sprint-2-...) |
<!-- END auto-generated:sprints -->

## What Was Done (feature-by-feature)
- **SDD-XXX**: <one-line>. See [spec](../../specs/YYYY-MM-DD-slug/) | [ADR](../../docs/ADR/NNN-*.md)
- ...

## Key Decisions
- **ADR-NNN**: <one-line> ([link](../../docs/ADR/NNN-*.md))
- ...

## Lessons Captured
- **LESSON-NNN**: <one-line>. Status: SHIP/DEFER/DISCARD/OPEN ([source](../../sprints/PI-N/lessons.md))
- ...

## On-the-Ground Notes (synthesized)
<one paragraph distilling AGENT_NOTES.md highlights across the PI's sprints -- the *why* the ledger can't capture>

## Links
- Tracker: [HIGH_LEVEL_DEV_TRACKER.md](../../HIGH_LEVEL_DEV_TRACKER.md)
- Retro: [sprints/PI-N/RETRO.md or sprints/PI-N-retro.md](../../../sprints/...)
- Roadmap section: [constitution/roadmap.md#PI-N](../../../constitution/roadmap.md)
```

## Appendix C: Skeleton for `Management/PI-N/Sprint-N-{title}/AGENT_NOTES.md`

```markdown
---
sprint: PI-N / S-N
title: <kebab-title>
owner: <agent or role>
last_updated: YYYY-MM-DD
---

# Agent Notes -- PI-N / Sprint-N

Ground-truth notes from agents who actually did the work. The *why*, *what
surprised us*, *what worked*, *what didn't*, and *what is worth remembering*.
Not a status report; a working journal.

## Session log
- **YYYY-MM-DD** by `<agent-id>` (task T-NNN): <2-3 sentences on what happened
  on the ground -- a non-obvious decision, a surprise, a workaround, a tool
  behavior to remember>

## Surprises
- ...

## What worked
- ...

## What didn't
- ...

## To remember
- <one-liners that should likely become lessons; reviewed at sprint close for promotion to `sprints/PI-N/lessons.md`>
```
