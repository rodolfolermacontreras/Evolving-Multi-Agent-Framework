# PI-4: Alpha Release

- Status: **Active**
- Theme: Ship the Live UI v2 dashboard, update roadmap, create root README, release alpha-quality framework
- Started: 2026-06-02
- Owner: principal-executive-manager

---

## Goal

Deliver the alpha-quality framework package: a sprint-first dashboard (Live UI v2), an accurate roadmap, a root README entry point, and all housekeeping needed so a teammate can clone this repo and bootstrap SDD onto their own project.

---

## PI Objectives

### 1. Ship the Sprint-First Dashboard (Live UI v2)
**Why**: The current dashboard (v2.1) is functional but basic. The v2 redesign gives any team member a single page to understand project state without reading files. This is the "front door" for adoption.
**Success Criteria**: `state_builder.py build` produces an HTML dashboard matching the mockup at 1280px and 768px widths, with all 15 IAC criteria and 21 VAL criteria passing.
**Features**: 7-section sprint-first layout, design-token-driven CSS, responsive grid, accessibility (AA), activity feed, PI context drill-down, empty-state fallbacks.

### 2. Release-Ready Housekeeping
**Why**: The framework has no root README and the roadmap is stale. A teammate cloning this repo sees no entry point and outdated status. These are blockers for sharing.
**Success Criteria**: Root `README.md` exists with quickstart and bootstrap pointer. `constitution/roadmap.md` reflects PI-1 through PI-3 as complete and PI-4 as current. Domain skills marked as examples. Node.js deprecation warnings resolved in CI.
**Features**: Root README, roadmap update, domain skill annotations, CI maintenance.

---

## Sprint Allocation

### Sprint 1: Live UI v2 Implementation
**Goal**: Implement the sprint-first dashboard redesign
**Tasks**: 14 tasks from `specs/2026-05-26-live-ui-v2/tasks.md` (LOCKED)
**Phases**:
- [ ] Phase 1: Data layer -- 4 new functions (T-001 through T-004, parallelizable as 2 pairs)
- [ ] Phase 2: HTML renderer rewrite (T-005 through T-009, sequential)
- [ ] Phase 3: CSS / responsive polish (T-010, T-011)
- [ ] Phase 4: Accessibility and final polish (T-012 through T-014)
**Capacity**: 14 tasks, effort M overall
**Validation**: 15 IAC + 21 VAL criteria (LOCKED contract)

### Sprint 2: Alpha Release Housekeeping
**Goal**: Make the framework shareable with the team
**Tasks**:
- [ ] Create root `README.md` with quickstart, bootstrap pointer, and project identity
- [ ] Update `constitution/roadmap.md` -- PI-1/PI-2/PI-3 as complete, PI-4 as current
- [ ] Mark domain skills (fastapi-routes, htmx-frontend, pytest-runner) as reference examples
- [ ] Bump GitHub Actions versions (actions/checkout, azure/login) to resolve Node.js 20 deprecation
- [ ] Update SESSION-MEMORY.md and exec/state.md for alpha release
- [ ] Final test suite pass on master after all merges
**Capacity**: 6 tasks, effort S overall

### Sprint 3: Scott Feedback Hybrid Absorption (added 2026-06-03)
**Goal**: Absorb the two lowest-cost / highest-leverage items from the Scott Feedback Bundle without disrupting Sprints 1 and 2.
**Rationale**: Human approved option (c) from EM scope-conflict escalation (2026-06-03). The other 4 P1 Scott items (SDD-015, 016+017, 018) are deferred to PI-5. Foundry/model-pressure framing for SDD-015 was specific to another project, so SDD-015 loses its urgency here and waits for PI-5 cleanly.
**Tasks**:
- [ ] **SDD-013** -- "One feature, one session" rule -- one-line binding rule added to `constitution/principles.md` and operational guidance added to `.github/copilot-instructions.md`. **Skip-to-implement per spec-sizing rule** (less than 3 files, no spec needed). Owner: Architect.
- [ ] **SDD-014** -- Friction Analysis section in Level-2 decision template -- locate or create the Level-2 decision template, add required section covering money cost, complexity cost, maintenance burden, expected benefit, alternatives considered. One-page max. Owner: Architect (SPEC -> IMPLEMENT).
**Capacity**: 2 items, effort XS+S overall (total < 1 sprint of typical work)
**Validation**: SDD-013 -- single-line edit verifiable by `grep` for the rule phrase in both files. SDD-014 -- template file exists with the 5 required headings; reference link from `constitution/decision-policy.md` added.

---

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| render_html() rewrite breaks existing build/serve callers | High | Medium | Mitigated | SW Dev | Keep backward-compatible kwargs with None defaults; TDD ensures regression coverage |
| CSS rewrite introduces visual regressions | Medium | Medium | Owned | SW Dev | Test captures v1 structure assertions; mockup comparison at both breakpoints |
| Test count regression during rewrite | Medium | Medium | Mitigated | SW Dev | Track baseline before/after; TDD adds tests before removing old ones |
| Node.js 20 deprecation deadline (June 16) | Low | High | Owned | SW Dev | Bump action versions in S2 housekeeping sprint |
| decisions table may not exist in older fleet.db | Low | High | Mitigated | SW Dev | load_decisions() wraps in try/except; returns [] |

---

## Dependencies

**Internal**:
- Live UI v2 spec, plan, tasks, validation: ALL LOCKED (completed in PI-3 S4)
- DESIGN_TOKENS.md: 59 CSS custom properties defined (completed in PI-3 S4)
- mockup.html: static prototype for visual fidelity comparison (completed in PI-3 S4)

**External**:
- None. All work is self-contained within this repo.

---

## Success Metrics

- All 15 IAC criteria pass (automated tests)
- All 21 VAL criteria pass (20 automated + 1 HITL screen reader)
- Test count >= baseline + 30 new tests
- Root README exists and points to GENERALIZATION_SDD.md
- Roadmap accurately reflects PI-1 through PI-4
- A teammate can clone, read README, and begin bootstrap within 30 minutes

---

## Cross-References

- Live UI v2 spec: `specs/2026-05-26-live-ui-v2/spec.md`
- Live UI v2 tasks: `specs/2026-05-26-live-ui-v2/tasks.md`
- Live UI v2 validation: `specs/2026-05-26-live-ui-v2/validation.md`
- Design tokens: `specs/2026-05-26-live-ui-v2/DESIGN_TOKENS.md`
- Mockup: `specs/2026-05-26-live-ui-v2/mockup.html`
- Management index: `docs/Management/PI-4/INDEX.md`
