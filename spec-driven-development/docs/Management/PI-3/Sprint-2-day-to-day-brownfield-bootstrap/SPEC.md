---
sprint: PI-3 / S2
title: Day-to-Day Brownfield Bootstrap (Portability Validation)
status: Proposed (awaiting Principal sign-off)
owner: principal-product-manager (clarify), principal-architect (spec), principal-software-developer (dispatch)
worktree: wt-pi3-s2-brownfield (in THIS repo for notes; actual changes land in the Day-to-Day Agent repo)
deps: Parallel-safe with S1, S3, S4 (writes land in separate Day-to-Day repo, zero collision with this repo's master)
created: 2026-05-25
canonical_spec_dir: spec-driven-development/specs/2026-05-25-day-to-day-brownfield-bootstrap/ (to be created in CLARIFY phase)
backlog_ids: SDD-011 (to be assigned by PM)
adr: TBD if `bootstrap.py brownfield` requires a Level-1 change
---

# Sprint 2 -- Day-to-Day Brownfield Bootstrap (Portability Validation)

## Required Reading

1. [`ONBOARDING_KICK_OFF.md`](../ONBOARDING_KICK_OFF.md)
2. [`RULES.md`](../RULES.md)
3. [`HIGH_LEVEL_DEV_TRACKER.md`](../HIGH_LEVEL_DEV_TRACKER.md)
4. This file
5. The portability guide: [`GENERALIZATION_SDD.md`](../../GENERALIZATION_SDD.md) -- ~62KB, focus on Sections 3 (3-hour bootstrap), 4 (archetype selection), 6 (coexistence rules)
6. [`cli/bootstrap.py`](../../cli/bootstrap.py) -- the script being validated
7. [`archetypes/`](../../archetypes/) -- 5 starter constitutions; pick the closest to Day-to-Day
8. The host project: https://github.com/rodolfolermacontreras/day-to-day-microsoft (~743 tests, FastAPI/HTMX, Python 3.12+)

## 1. Sprint Goal (one sentence)

Prove the framework's portability claim by bootstrapping SDD onto the existing
Day-to-Day Agent project (brownfield) using `bootstrap.py brownfield --draft-only`,
reviewing the proposal as the human, then taking ONE small feature through the
full SDD lifecycle in the host project's repo.

## 2. Why this matters

The framework's core marketing claim is: "Bootstrap onto ANY project, greenfield
or brownfield." The dogfood pilot (PI-1 fleet-ledger) proved it works on its
OWN project. PI-2 proved the CLIs and dispatch work at scale. **PI-3/S2 is the
first time the framework will be applied to a project it did not originate in.**
If `bootstrap.py brownfield` cannot produce a sensible draft against a real
established codebase, the portability claim is empty.

## 3. Acceptance Criteria

| # | AC | Verification |
|---|----|--------------|
| AC1 | `bootstrap.py brownfield <day-to-day-path> --draft-only` runs without error against the actual Day-to-Day repo | Stdout + exit 0 |
| AC2 | Produces a draft proposal at `<day-to-day>/.sdd-proposal/` containing: adapted constitution (6 files), suggested archetype, archaeology report | `ls .sdd-proposal/` -- all 7 artifacts present |
| AC3 | Archaeology report correctly identifies: Python 3.12+, FastAPI, HTMX, pytest, the 743-test suite, the Engine singleton pattern | Manual diff vs Day-to-Day's actual structure |
| AC4 | Proposed constitution's `tech-stack.md` reflects the host's stack, not this framework's stdlib-only stance | Read & confirm |
| AC5 | Proposed constitution's `principles.md` inherits the 10 framework articles AND adds at least 1 Day-to-Day-specific article (e.g. "FastAPI route conventions") | Read & confirm |
| AC6 | Human reviews the draft, accepts or amends, then runs `bootstrap.py brownfield --apply` to land SDD into the Day-to-Day repo | HITL gate |
| AC7 | ONE small feature picked from Day-to-Day's backlog and walked through the lifecycle: IDEA -> SPEC -> TASKS -> IMPLEMENT -> REVIEW -> DONE | All 6 lifecycle artifacts exist in `day-to-day/spec-driven-development/specs/YYYY-MM-DD-{slug}/` |
| AC8 | Friction log captured in `sessions/2026-05-XX-brownfield-bootstrap-lessons.md` -- specifically what `bootstrap.py brownfield` got right, got wrong, and what is missing | File exists, >= 5 lesson entries |
| AC9 | If lessons reveal a bug or gap in `bootstrap.py brownfield`, file a feature spec in THIS repo (not the host) for the fix; do NOT fix in-flight | New spec dir in THIS repo's `specs/` for PI-4 work |
| AC10 | `GENERALIZATION_SDD.md` updated with corrections from real-world test; bump to v1.0 (out of v0.1) | semver bump in file frontmatter |

## 4. Task Decomposition (proposed; PM to confirm in CLARIFY)

| ID | Description | Owner | Tag | Status |
|----|-------------|-------|-----|--------|
| T-001 | CLARIFY: which feature in Day-to-Day to dogfood as the lifecycle test? Get human pick. | PM | [HITL] | Proposed |
| T-002 | SPEC: write `specs/2026-05-25-day-to-day-brownfield-bootstrap/spec.md` based on AC above | Architect | [S] | Proposed |
| T-003 | Run `bootstrap.py brownfield ../day-to-day-microsoft --draft-only` and capture stdout + `.sdd-proposal/` contents | developer-general | [P][AFK] | Blocked on T-002 |
| T-004 | Review the draft against AC3, AC4, AC5; annotate gaps in `validation.md` | qa-engineer-general | [P][AFK] | Blocked on T-003 |
| T-005 | Human approves the draft (or amends) | Human | [HITL] | Blocked on T-004 |
| T-006 | Run `bootstrap.py brownfield --apply` -- SDD files land in Day-to-Day repo | developer-general | [HITL] (writes to external repo) | Blocked on T-005 |
| T-007 | Walk the chosen feature through the lifecycle in the Day-to-Day repo (separate session/worktree under the day-to-day project) | developer-general + qa-engineer-general | [HITL] | Blocked on T-006 |
| T-008 | Capture friction log + lessons; update `GENERALIZATION_SDD.md` | qa-engineer-general | [S] | Blocked on T-007 |

## 5. Worktree Plan

This sprint is unusual: the **actual file changes land in a different repo**
(Day-to-Day Agent). In THIS repo, only notes, the spec dir, and possibly a
`bootstrap.py` bugfix branch are touched.

```powershell
# In THIS repo (Evolving-Multi-Agent-Framework):
git worktree add ../wt-pi3-s2-brownfield -b pi3/s2/brownfield-notes master

# In the OTHER repo (Day-to-Day Agent), the bootstrap CLI will write directly:
# - .sdd-proposal/ (draft)
# - spec-driven-development/ (after --apply)
# - specs/2026-05-XX-{slug}/ (lifecycle artifacts for the dogfood feature)
```

- **THIS repo modifies:** `specs/2026-05-25-day-to-day-brownfield-bootstrap/{spec,plan,tasks,validation,clarification,RETRO}.md`, possibly `GENERALIZATION_SDD.md` (frontmatter bump + amendments).
- **DAY-TO-DAY repo modifies:** all of the above as a brownfield import.

## 6. Dispatch Tracker

| Dispatch ID | Task | Worker | Sent | Marked | Outcome |
|-------------|------|--------|------|--------|---------|
| (pending T-003) | T-003 | developer-general | -- | -- | -- |
| (pending T-004) | T-004 | qa-engineer-general | -- | -- | -- |

## 7. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | `bootstrap.py brownfield` may fail on Day-to-Day's complexity (743 tests, 20+ branches, mature conventions) | If it fails, the failure IS the lesson. File a spec for the gap and proceed manually for the lifecycle test. |
| R2 | Day-to-Day's existing conventions may conflict with framework conventions (e.g. emoji usage if any) | Coexistence rules in `GENERALIZATION_SDD.md` Section 6: SDD owns what it owns; the host's existing process owns the rest. Emergency hotfixes bypass SDD. |
| R3 | Dogfood feature (T-007) may take longer than expected | This is fine. Sprint can extend; PI-3 cadence is symbolic. The portability validation is the deliverable, not speed. |
| R4 | We are the only authorized contributor to Day-to-Day repo today | This sprint is single-developer-safe by design. |

## 8. HITL Gates Specific to this Sprint

- T-001: human picks the dogfood feature in Day-to-Day
- T-005: human approves the brownfield draft before `--apply`
- T-006: `--apply` writes to a different repo (irreversible without `git restore`) -- explicit approval
- T-007: any merge to Day-to-Day's `dev` or `master` requires Day-to-Day's existing review process

## 9. Scope guards (what is NOT in this sprint)

- Rewriting Day-to-Day's existing tests or conventions
- Migrating Day-to-Day's backlog into SDD format
- Cloud deployment of any Day-to-Day artifact (no Azure work)
- Changes to the framework's own CLI/skills/agents beyond the `GENERALIZATION_SDD.md` doc update
- Performance benchmarking of Day-to-Day under SDD

## 10. Definition of DONE for this sprint

- [ ] AC1-AC10 all verified
- [ ] Friction log filed at `sessions/2026-05-XX-brownfield-bootstrap-lessons.md`
- [ ] `GENERALIZATION_SDD.md` bumped to v1.0 with real-world corrections
- [ ] If `bootstrap.py` needed changes, those are filed as a PI-4 spec (not done in-flight)
- [ ] `HIGH_LEVEL_DEV_TRACKER.md` updated: S2 -> DONE
- [ ] This file moved to `sprints/PI-3/SPRINT_2_DAY_TO_DAY_BROWNFIELD_BOOTSTRAP.md`
- [ ] Worktree `wt-pi3-s2-brownfield` torn down

## 11. Status Log

| Date | Event |
|------|-------|
| 2026-05-25 | Sprint proposed at PI-3 kickoff; awaiting Principal sign-off |
