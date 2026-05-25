---
sprint: PI-3 / S3
title: PI-2 Lessons Curation via /evolve
status: Proposed
owner: principal-product-manager (lead), principal-architect (constitution impact review)
worktree: wt-pi3-s3-lessons
deps: Parallel-safe with S1, S2, S4 (writes land in sprints/PI-2/lessons.md and possibly .github/skills/)
created: 2026-05-25
canonical_spec_dir: spec-driven-development/specs/2026-05-25-pi2-lessons-curation/ (to be created)
backlog_ids: SDD-012 (to be assigned)
adr: TBD per-lesson if framework changes are SHIPPED
---

# Sprint 3 -- PI-2 Lessons Curation via /evolve

## Required Reading

1. [`ONBOARDING_KICK_OFF.md`](../ONBOARDING_KICK_OFF.md)
2. [`RULES.md`](../RULES.md)
3. [`HIGH_LEVEL_DEV_TRACKER.md`](../HIGH_LEVEL_DEV_TRACKER.md)
4. This file
5. [`sprints/PI-2/lessons.md`](../../sprints/PI-2/lessons.md) -- the 5 OPEN lessons + 1 carry-over from PI-1
6. [`.github/prompts/evolve.prompt.md`](../../../.github/prompts/evolve.prompt.md) -- the /evolve command spec
7. [`.github/skills/operational/lesson-capture/SKILL.md`](../../../.github/skills/operational/lesson-capture/SKILL.md)

## 1. Sprint Goal (one sentence)

Run the `/evolve` ceremony against the 5 OPEN PI-2 lessons (plus the
carry-over LESSON-004 from PI-1, which shipped its mitigation but was never
formally closed), producing a SHIP / DEFER / DISCARD decision per lesson and
landing any SHIP changes as small, conventional commits.

## 2. Why this matters

The framework's "Evolving" claim depends on the closed loop: project work
captures lessons -> /evolve curates -> framework changes ship -> next project
inherits improvements. If lessons accumulate without curation, the loop is
broken and "Evolving" is aspirational. PI-2 left 5 lessons OPEN. This sprint
closes them.

## 3. Lessons in scope

| ID | One-liner | Current candidate change | Recommended verdict |
|----|-----------|--------------------------|---------------------|
| LESSON-004 (PI-1) | Ledger migration policy | ALREADY SHIPPED via `ledger/MIGRATION-POLICY.md` (PI-2 Sprint A) | **CLOSE** (mark shipped retrospectively) |
| LESSON-006 | Closure ceremonies must touch ALL "current" markers | Add "closure checklist" to `pi-planning` skill OR extend `constitution-sync` to flag stale `(current)` markers | **SHIP** (extend constitution-sync; smaller blast radius than amending pi-planning) |
| LESSON-007 | Pre-spec design exploration produces reusable tokens at near-zero cost | Document the pattern in `gem-designer` skill OR new `design-tokens` skill | **DEFER** to S4 (Live UI v2 Spec) where new UI Designer can write this skill in context |
| LESSON-008 | Two parallel specs for same file: declare one canonical | Add a guard to `/spec` skill: when a new spec targets a file already covered by another open spec, prompt for canonical declaration | **SHIP** (small amendment to `to-spec` skill) |
| LESSON-009 | Windows SQLite + tempdir tests need `ignore_cleanup_errors=True` + `gc.collect()` | Add "Windows test fixtures" section to `testing-conventions` skill | **SHIP** (single-skill edit; high payoff for any future SQLite-touching CLI) |
| LESSON-010 | ACA Easy Auth needs `enableIdTokenIssuance=true` on companion app reg | Add to `azure-deployment-architecture` skill (cloud-security architect's domain) | **SHIP** (cloud-security architect already wrote that skill; one-line amendment) |

## 4. Acceptance Criteria

| # | AC | Verification |
|---|----|--------------|
| AC1 | Each of the 6 lessons in scope has a documented verdict (SHIP / DEFER / DISCARD / CLOSE) with one-sentence rationale | Read `sprints/PI-2/lessons.md` after edits |
| AC2 | Every SHIP verdict produces a corresponding commit that implements the change | `git log --grep="LESSON-"` shows N commits matching SHIP count |
| AC3 | Every SHIP commit references the lesson ID in the body | `git log --grep="LESSON-006"` etc. |
| AC4 | DEFER verdicts get a target sprint / PI noted (e.g. "DEFER to S4 / PI-3" or "DEFER to PI-4") | Verdict line includes target |
| AC5 | If any SHIP changes a constitution file or amends an ADR, semver is bumped per ADR-0006 | `constitution-sync` script reports clean |
| AC6 | Tech debt TD-01 (Day-to-Day-Agent residual in Principal agent files) is opportunistically checked during the skill/agent hygiene pass; if found, file a fix spec for PI-4 (do NOT fix in-flight) | `grep -r "Day-to-Day Agent" .github/agents/` |
| AC7 | `sprints/PI-2/lessons.md` ends with a curation timestamp line: `Curated 2026-05-XX via /evolve in PI-3/S3` | grep that line |
| AC8 | `HIGH_LEVEL_DEV_TRACKER.md` "Open Lessons" table updated -- no more OPEN PI-2 lessons (all CLOSED or DEFERRED with target PI noted) | Diff the tracker |

## 5. Task Decomposition

| ID | Description | Owner | Tag | Status | File scope |
|----|-------------|-------|-----|--------|------------|
| T-001 | CLOSE LESSON-004: mark retrospectively shipped in `sprints/PI-1/lessons.md` + `sprints/PI-2/lessons.md` | PM | [S][AFK] | Proposed | 2 files |
| T-002 | SHIP LESSON-006: extend `.github/skills/core/constitution-sync/SKILL.md` with stale-`(current)`-marker check; if scripted, add to `cli/schema_lint.py` | developer-cli-specialist-1 | [P][AFK] | Proposed | 1-2 files |
| T-003 | DEFER LESSON-007: note in lessons.md "DEFER to PI-3/S4 -- UI Designer authors `design-tokens` skill in spec phase" | PM | [S][AFK] | Proposed | 1 file |
| T-004 | SHIP LESSON-008: amend `.github/skills/workflow/to-spec/SKILL.md` with canonical-declaration prompt; bump version | developer-general | [P][AFK] | Proposed | 1 file |
| T-005 | SHIP LESSON-009: amend `.github/skills/core/testing-conventions/SKILL.md` with "Windows test fixtures" section | developer-general | [P][AFK] | Proposed | 1 file |
| T-006 | SHIP LESSON-010: amend `.github/skills/operational/azure-deployment-architecture/SKILL.md` with `enableIdTokenIssuance` note | principal-cloud-security-architect | [P][AFK] | Proposed | 1 file |
| T-007 | Tech debt sweep: grep for "Day-to-Day Agent" in `.github/agents/`; if hits, file `specs/2026-05-25-principal-agent-hygiene/` spec for PI-4 | qa-engineer-general | [S][AFK] | Proposed | report only |
| T-008 | Update `HIGH_LEVEL_DEV_TRACKER.md` "Open Lessons" table + commit | PM | [S][AFK] | Proposed | 1 file |
| T-009 | Run `cli/schema_lint.py` to verify no frontmatter regressions from skill edits | developer-cli-specialist-1 | [S][AFK] | Proposed | n/a |

T-002, T-004, T-005, T-006 are all parallel-safe (different skill files,
different worktrees). Recommend 4-worker batch dispatch.

## 6. Worktree Plan

```powershell
git worktree add ../wt-pi3-s3-lessons-constitution-sync -b pi3/s3/lesson-006 master
git worktree add ../wt-pi3-s3-lessons-to-spec          -b pi3/s3/lesson-008 master
git worktree add ../wt-pi3-s3-lessons-test-conventions -b pi3/s3/lesson-009 master
git worktree add ../wt-pi3-s3-lessons-azure-deploy     -b pi3/s3/lesson-010 master
```

Single worktree `wt-pi3-s3-lessons` (no sub-suffix) for T-001, T-003, T-007,
T-008 which are sequential PM/QA tasks.

## 7. Dispatch Tracker

| Dispatch ID | Task | Worker | Sent | Marked | Outcome |
|-------------|------|--------|------|--------|---------|
| (pending) | T-002 | developer-cli-specialist-1 | -- | -- | -- |
| (pending) | T-004 | developer-general | -- | -- | -- |
| (pending) | T-005 | developer-general | -- | -- | -- |
| (pending) | T-006 | principal-cloud-security-architect | -- | -- | -- |

## 8. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A SHIP change to a skill might trigger constitution semver bump unexpectedly | Run `constitution-sync` before commit per AC5 |
| R2 | Parallel skill edits collide if a future skill-registry file is touched by multiple workers | All 4 SHIP tasks touch DIFFERENT skill files; verified at task decomposition time |
| R3 | LESSON-010 amendment requires the principal-cloud-security-architect to be available | They are an active Principal; can also be done by developer-general following the cloud-sec skill verbatim |

## 9. HITL Gates Specific to this Sprint

- Per RULES.md HITL #8: any new ADR with `status: binding` requires human approval. None expected, but if T-006 escalates the ACA Easy Auth note to a binding ADR, pause.
- Per RULES.md HITL #1: no new Azure provisioning. T-006 is a doc-only amendment to the existing skill.

## 10. Scope guards (what is NOT in this sprint)

- New skills (deferred to S4)
- Constitution amendments beyond stale-marker check
- Re-running PI-2's tests against the SHIP changes (covered by AC9 schema_lint only; full regression is overkill here)
- Fixing TD-01 in-flight (only file the fix spec)

## 11. Definition of DONE for this sprint

- [ ] AC1-AC8 verified
- [ ] All 6 lessons have a recorded verdict
- [ ] All SHIP verdicts produce green commits with LESSON-ID in body
- [ ] `schema_lint.py` exit 0 after edits
- [ ] Tracker "Open Lessons" updated
- [ ] This file moved to `sprints/PI-3/SPRINT_3_PI2_LESSONS_CURATION.md`
- [ ] All worktrees torn down

## 12. Status Log

| Date | Event |
|------|-------|
| 2026-05-25 | Sprint proposed at PI-3 kickoff; awaiting PM sign-off |
