# F-03 -- PI-5 kickoff -- allocate Scott bundle, write `CURRENT_PI.md`

| Field | Value |
|---|---|
| Backlog IDs | (planning -- no new IDs; touches SDD-015..SDD-026 sprint assignments) |
| Priority | P1 (gates all PI-5 work) |
| Size | M |
| Sprint | PI-5 / Sprint 1 (= Sprint 5 overall) |
| Phase | PI PLANNING |
| Owner | Principal Product Manager |
| Prerequisite | Sprint 4 DONE; PI-4 closed or explicitly status-marked |
| Blocks | F-04, F-05; any PI-5 sprint that follows |

---

## 0. How to use this prompt

Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) first. Then take the
deferred Scott Feedback Bundle, propose PI-5 sprint allocation, present to
owner, capture approval, write `sprints/PI-5/CURRENT_PI.md`, update
`BACKLOG.md` sprint column entries, scaffold `docs/Management/PI-5/INDEX.md`.

This is a **PM-only planning session**. No code, no specs, no implementation.

---

## 1. Project goal (short)

Convert the 11 deferred Scott items (and SDD-025, now unblocked by SDD-014)
into a real PI-5 plan with sprint allocation, so the owner can paste sprint
kickoff prompts in order. Without this file, PI-5 is just a backlog of
intentions; with it, the framework knows what is committed when.

---

## 2. The rules

See [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md). Load-bearing:

- **PM authority (Level 1)**: you decide priority, scope, sprint allocation,
  RICE adjustments. You may NOT decide architecture (Architect domain) or task
  decomposition (SW Dev domain).
- **Decision policy**: a PI plan is Level-1. Sprint allocations within a PI
  are Level-1. Hiring a new worker (SDD-017) is Level-1 if it doesn't change
  the constitution; Level-2 if it does. Defer Level-2 calls to the owner with
  a Friction Analysis using `templates/level-2-decision.md`.
- **One feature, one session** (Article VII): finish this in one session.

---

## 3. Onboarding on this task

### Input -- the deferred Scott bundle

From [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) and the EM rollup
(2026-06-05):

| ID | Title | Status going in | Notes |
|----|-------|-----------------|-------|
| SDD-015 | Model upgrades as Level-2 (regression branch + A/B + cost) | DEFERRED -> PI-5 | Was urgent on another project, not here -- still worth doing |
| SDD-016 | `.github/` symlink portability trick | DEFERRED -> PI-5 | CLARIFY first; co-spec with SDD-017 |
| SDD-017 | Hire `dev-env-manager` worker | DEFERRED -> PI-5 | SPEC; co-spec with SDD-016 |
| SDD-018 | UI lifecycle variant (relaxed Article X for live dashboard) | DEFERRED -> PI-5 | PM-overridden P2 -> P1 |
| SDD-019 | Serial gate on CLARIFY/SPEC repo-wide | PROPOSED -> PI-5 | Bundle with SDD-020 |
| SDD-020 | Cross-feature dedup at /triage and /clarify | PROPOSED -> PI-5 | Bundle with SDD-019 |
| SDD-021 | End-of-session self-review loop | PROPOSED -> PI-5 | Blocked on Architect transcript-accessibility audit |
| SDD-022 | ADO / GitHub Issues sync bridge | PROPOSED -> PI-5 | Gap Scott named as blocking his adoption |
| SDD-023 | First-class user gates uniform construct | PROPOSED -> PI-5 | Synergistic with SDD-019 |
| SDD-025 | Stakeholder-pressure defense pattern | PROPOSED -> PI-5 | **Now unblocked** by SDD-014 |
| SDD-026 | Trim agent traceability scope | DEFERRED INDEFINITELY | P4; re-evaluate at PI-5 retro |
| SDD-024 | Microsoft self-improving skills paper memo | UNSCHEDULED | P3 single-task; not PI-bound |

### EM recommendation (received from prior PM agent on 2026-06-05)

Bundle ordering:

1. **PI-5 Sprint 1** -- SDD-016 + SDD-017 (brownfield-portability finisher).
   This is the sprint that contains the F-04 + F-05 prompts already authored.
2. **PI-5 Sprint 2** -- SDD-019 + SDD-020 (anti-conflict gates).
3. **PI-5 Sprint 3** -- SDD-018 (UI lifecycle variant -- relieves live
   dashboard pain).
4. **PI-5 Sprint 4 or later** -- SDD-022 (ADO/GitHub Issues bridge -- the gap
   Scott named).
5. **PI-5 Sprint 4 or later** -- SDD-015 (model-upgrades discipline).
6. **PI-5 Sprint 4 or later** -- SDD-021 (self-review loop, after Architect
   transcript audit).
7. **PI-5 Sprint 4 or later** -- SDD-023 (uniform user gates, after SDD-019).
8. **PI-5 Sprint 4 or later** -- SDD-025 (stakeholder defense playbook, small).
9. **Unscheduled** -- SDD-024 single-task; SDD-026 P4 deferred indefinitely.

You (PM) are free to revise this ordering with rationale. Present the
revision to the owner and get explicit approval before writing
`CURRENT_PI.md`.

### What you produce

1. **PI-5 plan document**: `sprints/PI-5/CURRENT_PI.md` -- match the structure
   of [`../sprints/PI-4/CURRENT_PI.md`](../sprints/PI-4/CURRENT_PI.md). Must
   include: PI status, theme, started date, owner, PI goal, PI objectives
   (one per logical bundle), sprint allocation, risks (ROAM), dependencies,
   success metrics, cross-references.
2. **BACKLOG updates**: `backlog/BACKLOG.md` -- update the `Sprint` column for
   SDD-015..SDD-026 to reflect the approved allocation (e.g. `PI-5 Sprint 1`,
   `PI-5 Sprint 2`, etc.). Do NOT change priorities or RICE without owner
   approval. Do NOT add new SDD-IDs.
3. **PI-5 management folder**: `docs/Management/PI-5/INDEX.md` -- scaffold
   the index file (match `docs/Management/PI-4/INDEX.md`). Sprint sub-folders
   are created as sprints start; not in this session.
4. **Sprint 5 follow-up prompt**: identify the second PI-5 sprint by name
   (e.g. "PI-5 Sprint 2 = SDD-019 + SDD-020 anti-conflict gates") and add a
   one-line note to `exec/sprint-progress.md` under F-03's result block:
   "Next sprint to plan: ... -- EM to author SPRINT-06-KICKOFF prompt when
   PI-5 Sprint 1 (current Sprint 5) closes."

### Owner gate

Before writing any of the four artifacts above:

1. Present the proposed sprint allocation as a one-page summary in chat.
2. Ask the owner: "Approved as-is / revise / defer some items further?"
3. Wait for explicit answer.
4. Only then write the files.

---

## 4. Acceptance criteria (testable)

| AC | Statement | Verification |
|----|-----------|--------------|
| AC-1 | `sprints/PI-5/CURRENT_PI.md` exists, valid YAML frontmatter (id, type, status, owner, updated) | Read file |
| AC-2 | Plan has theme, goal, PI objectives, sprint allocation, risks, dependencies, success metrics, cross-refs | Manual review |
| AC-3 | Every deferred Scott item (SDD-015..SDD-026, excluding SDD-024 single-task and SDD-026 deferred-indefinitely) is assigned a PI-5 sprint OR explicitly noted as deferred with rationale | Read CURRENT_PI.md + BACKLOG |
| AC-4 | `BACKLOG.md` sprint column updated for affected rows; no priority/RICE silently changed | Diff BACKLOG.md |
| AC-5 | `docs/Management/PI-5/INDEX.md` exists with sprint table scaffold | Read file |
| AC-6 | Owner has approved the allocation in chat before files were written | Conversation transcript |
| AC-7 | Full test suite passes (no regression -- this should be doc-only) | `pytest -q` |
| AC-8 | F-03 result block appended to `sprint-progress.md` | Read file |

---

## 5. SDD workflow

- This is `/triage` + light PI planning. No new spec dir.
- Branch: `master`.
- Slash command: `/triage` (at [`../../.github/prompts/triage.prompt.md`](../../.github/prompts/triage.prompt.md))
  if you want the formal triage flow; otherwise PM judgment per the
  pre-existing 2026-06-03 triage report at
  [`../sprints/PI-4/triage-scott-feedback-2026-06-03.md`](../sprints/PI-4/triage-scott-feedback-2026-06-03.md).

---

## 6. Definition of done + report

Sections 7-10 of [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) apply. Append to
[`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### F-03 -- pi5-kickoff -- DONE

- Date: YYYY-MM-DD
- Owner: Principal Product Manager
- Commits: <sha-1>, <sha-2>
- Files changed: 3
  - spec-driven-development/sprints/PI-5/CURRENT_PI.md (new)
  - spec-driven-development/backlog/BACKLOG.md (sprint column updates)
  - spec-driven-development/docs/Management/PI-5/INDEX.md (new)
- Tests: <N> -> <N> (no code changes)
- Owner approval: <date/timestamp captured in chat>
- PI-5 sprint allocation:
  - Sprint 1 (= overall Sprint 5): SDD-016 + SDD-017 -- brownfield portability
  - Sprint 2 (= overall Sprint 6): <items>
  - Sprint 3 (= overall Sprint 7): <items>
  - Sprint 4 (= overall Sprint 8): <items>
  - Unscheduled: SDD-024 (single-task), SDD-026 (P4 deferred indefinitely)
- Notes: <one paragraph>
- Next: F-04 ready -- paste F-04-symlink-portability-clarify-spec.prompt.md
  in a fresh session
```

Commit:
`plan(pi-5): launch PI-5 -- sprint allocation for deferred Scott bundle`

Then tell the owner: "PI-5 launched. SHA `<sha>`. Paste
`spec-driven-development/feature-prompts/F-04-symlink-portability-clarify-spec.prompt.md`
in a fresh session to start the SDD-016+SDD-017 bundle."

---

## 7. Do NOT do

- Do NOT change priorities or RICE scores without owner approval.
- Do NOT add new SDD-IDs. All bundle items already have IDs.
- Do NOT write any specs, plans, tasks, or implementation in this session.
- Do NOT start F-04 in this session.
- Do NOT modify `constitution/**`.
- Do NOT touch `cli/state_builder.py` or any other locked file.
