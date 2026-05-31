---
sprint: PI-3 / S4
title: Live UI v2 Spec (Principal UI Designer kickoff)
status: DONE
owner: principal-ui-designer (lead), principal-architect (review)
worktree: n/a (spec-only sprint, worked on master)
deps: Soft dep on S1 (live dashboard must remain stable; S4 is SPEC ONLY, no impl in this PI)
created: 2026-05-25
canonical_spec_dir: spec-driven-development/specs/2026-05-26-live-ui-v2/
backlog_ids: SDD-013 (UI v2 Spec), SDD-014 (design-tokens skill) -- to be assigned
adr: ADR-0010 (hire principal-ui-designer) authored in parallel
scope: SPEC ONLY -- implementation deferred to PI-4
---

# Sprint 4 -- Live UI v2 Spec (Principal UI Designer Kickoff)

## Required Reading

1. [`ONBOARDING_KICK_OFF.md`](../ONBOARDING_KICK_OFF.md)
2. [`RULES.md`](../RULES.md)
3. [`HIGH_LEVEL_DEV_TRACKER.md`](../HIGH_LEVEL_DEV_TRACKER.md)
4. This file
5. [`ADR-0010 -- Hire principal-ui-designer`](../ADR/010-hire-principal-ui-designer.md) (authored alongside this sprint)
6. The existing live UI (v1):
   - [`cli/state_builder.py`](../../cli/state_builder.py) -- the server (rows 4 of the [Codebase Reading Guide](../ONBOARDING_KICK_OFF.md#14-codebase-reading-guide-for-brownfield-agents))
   - [`exec/state.html`](../../exec/state.html) -- current rendered output
   - Live URL: https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/
7. The existing design exploration:
   - [`specs/2026-05-16-cloud-dashboard/DESIGN.md`](../../specs/2026-05-16-cloud-dashboard/DESIGN.md)
   - [`specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md`](../../specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md)
8. Lessons that bear on UI work:
   - LESSON-005 (EM communication discipline)
   - LESSON-007 (Pre-spec design tokens are reusable; pulled in from S3 DEFER)

## 1. Sprint Goal (one sentence)

Produce a fully approved SPEC + PLAN + TASKS + locked VALIDATION for the Live
UI v2 -- a minimalist, aesthetically clean evolution of the existing Bridge
dashboard that visualizes per-agent activity, current sprint, work-in-progress
summary, current PI, and what comes next -- with implementation deferred to PI-4
so this sprint can focus on getting the design right.

## 2. Why this matters

The kickoff prompt frames the framework as one that "ships with a minimalist,
aesthetically clean user interface, one instance attached to one project at a
time." The existing dashboard (v2.1) is functional but evolved from a CLI's
side-output, not from a UI-first design. A Principal UI Designer (hired in
this sprint per ADR-0010) authors the v2 spec so the visual layer becomes a
first-class framework concern, not a CLI afterthought.

Implementation is **deferred to PI-4** so:
- The spec gets the attention it deserves (Article X: validation contract first)
- The S1 freshness work doesn't collide with visual rework
- The Day-to-Day brownfield bootstrap (S2) can demo the v1 UI without rebuild

## 3. Acceptance Criteria

| # | AC | Verification |
|---|----|--------------|
| AC1 | ADR-0010 (hire principal-ui-designer) is approved and the agent file lands in `.github/agents/principal-ui-designer.agent.md` | File exists; roster updated |
| AC2 | UI v2 spec is authored at `specs/2026-05-25-live-ui-v2/spec.md` with: visual layer goals, information architecture, what data is shown per agent / per sprint / per PI, accessibility targets (AA), responsive targets | File exists, PM-reviewed |
| AC3 | Design tokens captured in `specs/2026-05-25-live-ui-v2/DESIGN_TOKENS.md`: color palette, type scale, spacing scale, motion principles, layout grid | File exists; tokens follow LESSON-007 (transferable to any v0.1 impl) |
| AC4 | Stdlib + plain HTML/CSS constraint is honored (per `tech-stack.md` and user decision at PI-3 kickoff). No new dependencies proposed. | Spec section "Tech constraints" lists stdlib-only |
| AC5 | `validation.md` LOCKED with explicit ACs for the v2 implementation (will be verified in PI-4 impl sprint) | File exists, marked LOCKED with date |
| AC6 | Plan + tasks decomposed for the future PI-4 implementation sprint (proposed task list, not executed) | `plan.md` + `tasks.md` exist; tasks tagged [P]/[S]/[AFK]/[HITL] |
| AC7 | New `design-tokens` skill authored at `.github/skills/operational/design-tokens/SKILL.md` -- documents the LESSON-007 pattern (design exploration produces reusable tokens) | File exists, registered in `roster/skills.json` |
| AC8 | A small visual prototype (static HTML mockup) is produced at `specs/2026-05-25-live-ui-v2/mockup.html` so the human can preview before approving the spec | File exists, openable in browser, reflects design tokens |
| AC9 | No regressions to live v1 dashboard | https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/ still loads and renders state correctly |
| AC10 | UI v2 explicitly addresses the visualizations called out in the kickoff prompt: per-agent activity, current sprint, WIP summary, current PI, what comes next | Spec section maps each requirement to a UI region |

## 4. Task Decomposition

| ID | Description | Owner | Tag | Status | File scope |
|----|-------------|-------|-----|--------|------------|
| T-001 | (Parallel to this sprint) Author ADR-0010 + `principal-ui-designer.agent.md` + roster updates | Executive Manager | [HITL] | In progress (this kickoff) | 3 files |
| T-002 | Human approves ADR-0010 (HITL gate #9: any /hire requires approval) | Human | [HITL] | Pending | n/a |
| T-003 | CLARIFY: UI Designer interviews human on visual preferences (minimalist examples, color preferences, typography preferences, motion tolerance) | principal-ui-designer | [HITL] | Blocked on T-002 | `specs/2026-05-25-live-ui-v2/clarification.md` |
| T-004 | Author DESIGN_TOKENS.md (palette, type scale, spacing, motion) | principal-ui-designer | [S] | Blocked on T-003 | 1 file |
| T-005 | Author static HTML mockup using only stdlib-served HTML + CSS, no JS framework | ux-designer-general | [S] | Blocked on T-004 | 1 file (mockup.html) |
| T-006 | Author spec.md with information architecture mapping each kickoff requirement to a UI region | principal-ui-designer | [S] | Blocked on T-004 (parallel with T-005) | 1 file |
| T-007 | Architect reviews spec.md for technical feasibility under stdlib-only constraint | principal-architect | [S] | Blocked on T-006 | review only |
| T-008 | SW Dev authors plan.md decomposing the future PI-4 implementation | principal-software-developer | [S] | Blocked on T-007 | 1 file |
| T-009 | PM authors tasks.md with tagged tasks for PI-4 impl | principal-product-manager | [S] | Blocked on T-008 | 1 file |
| T-010 | Author validation.md and LOCK it (Article X: pre-implementation contract) | principal-ui-designer + principal-architect | [S] | Blocked on T-009 | 1 file |
| T-011 | Author `design-tokens` skill (closes LESSON-007 DEFER from S3) | principal-ui-designer | [S] | Blocked on T-010 | 1 file |
| T-012 | Human reviews mockup + spec; APPROVE or AMEND | Human | [HITL] | Blocked on T-011 | n/a |

## 5. Worktree Plan

```powershell
git worktree add ../wt-pi3-s4-ui-v2 -b pi3/s4/ui-v2-spec master
```

All work in this sprint is documentation. No implementation files modified
in this PI. Implementation worktrees come in PI-4.

## 6. Dispatch Tracker

| Dispatch ID | Task | Worker | Sent | Marked | Outcome |
|-------------|------|--------|------|--------|---------|
| S4-D001 | T-004 (DESIGN_TOKENS.md) | principal-ui-designer | 2026-05-31 | 2026-05-31 | SUCCESS |
| S4-D002 | T-005 (mockup.html) | ux-designer-general | 2026-05-31 | 2026-05-31 | SUCCESS |
| S4-D003 | T-006 (spec.md) | principal-ui-designer | 2026-05-31 | 2026-05-31 | SUCCESS |
| S4-D004 | T-007 (Architect review) | principal-architect | 2026-05-31 | 2026-05-31 | APPROVED WITH NOTES |
| S4-D005 | T-008/T-009/T-010 (plan/tasks/validation) | principal-software-developer | 2026-05-31 | 2026-05-31 | SUCCESS |
| S4-D006 | T-011 (design-tokens skill) | principal-ui-designer | 2026-05-31 | 2026-05-31 | SUCCESS |

Most tasks in this sprint are Principal-authored, not worker-dispatched.

## 7. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Human may want JS framework (HTMX, Alpine, React) -- conflicts with stdlib decision | T-003 CLARIFY surfaces this; if human changes mind, escalate to constitution amendment via `/constitution` |
| R2 | UI v2 may bloat into a redesign of state_builder.py | Scope guard: SPEC ONLY this PI; impl deferred to PI-4 |
| R3 | Principal UI Designer hire (ADR-0010) may not be approved | Then this sprint is owned by ux-designer-general worker with Architect oversight; quality will be lower but sprint still deliverable |
| R4 | Live v1 dashboard breakage during spec authoring | No code changes in this sprint = zero risk |

## 8. HITL Gates Specific to this Sprint

- T-002: Approve ADR-0010 (RULES HITL #9)
- T-003: Human interview for design preferences
- T-012: Human approves the spec + mockup before sprint can close

## 9. Scope guards (what is NOT in this sprint)

- **Implementation of UI v2** -- deferred to PI-4
- Adding any JS framework, CSS library, or runtime dependency
- Modifying `cli/state_builder.py` (zero edits to the v1 server)
- Modifying `exec/state.html` (current output stays as-is)
- Cloud redeployment (no Azure work)
- Custom domain or branding work
- Mobile-first redesign (responsive is in scope; mobile-first is not, unless human requests)

## 10. Definition of DONE for this sprint

- [ ] AC1-AC10 verified
- [ ] All 6 lifecycle artifacts exist in `specs/2026-05-25-live-ui-v2/`: clarification, spec, plan, tasks, validation (LOCKED), DESIGN_TOKENS, mockup.html
- [ ] ADR-0010 approved; principal-ui-designer agent file lands; roster updated
- [ ] `design-tokens` skill registered
- [ ] Human APPROVES the mockup + spec
- [ ] `HIGH_LEVEL_DEV_TRACKER.md` updated: S4 -> DONE; PI-4 backlog seeded with the UI v2 implementation sprint
- [ ] This file moved to `sprints/PI-3/SPRINT_4_LIVE_UI_V2_SPEC.md`
- [ ] Worktree torn down

## 11. Status Log

| Date | Event |
|------|-------|
| 2026-05-25 | Sprint proposed at PI-3 kickoff; depends on ADR-0010 approval to begin |
| 2026-05-26 | ADR-0010 approved; UI Designer active; CLARIFY doc created with 6 questions |
| 2026-05-31 | Human approves all 6 CLARIFY questions (EM recommendations accepted) |
| 2026-05-31 | T-004 DESIGN_TOKENS.md authored (59 CSS custom properties, 8 sections) |
| 2026-05-31 | T-006 spec.md authored (37KB, 12 sections + 3 appendices) |
| 2026-05-31 | T-005 mockup.html authored (34KB static prototype, all 6 sections) |
| 2026-05-31 | T-007 Architect review: APPROVED WITH NOTES (3 open questions resolved) |
| 2026-05-31 | T-008/T-009/T-010 plan, tasks, validation authored and LOCKED |
| 2026-05-31 | T-011 design-tokens skill v1.0 authored (closes LESSON-007) |
| 2026-05-31 | Sprint DONE -- all 12 tasks complete, 7 artifacts in spec dir |
