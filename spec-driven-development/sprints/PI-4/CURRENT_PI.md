---
id: SDD-PI-4-CURRENT_PI-sprint
type: sprint
status: done
owner: principal-product-manager
updated: 2026-07-07
sprint: PI-4
---

# PI-4: Alpha Release

- Status: **Closed** (Sprints 1-4 DONE, 2 PI-4 commitments deferred to PI-5; PI-4 close = DONE-WITH-DEFERRED, ratified by owner 2026-06-06; status frontmatter finalized to `done` on 2026-07-07 during PI-7 close)
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
- [x] **SDD-013** -- "One feature, one session" rule -- one-line binding rule added to `constitution/principles.md` and operational guidance added to `.github/copilot-instructions.md`. **Skip-to-implement per spec-sizing rule** (less than 3 files, no spec needed). Owner: Architect. **DONE** commit `5992ec8`.
- [x] **SDD-014** -- Friction Analysis section in Level-2 decision template -- locate or create the Level-2 decision template, add required section covering money cost, complexity cost, maintenance burden, expected benefit, alternatives considered. One-page max. Owner: Architect (SPEC -> IMPLEMENT). **DONE** commit `85b39be`.
**Capacity**: 2 items, effort XS+S overall (total < 1 sprint of typical work). **STATUS: COMPLETE 2026-06-03.**
**Validation**: SDD-013 -- single-line edit verifiable by `grep` for the rule phrase in both files. SDD-014 -- template file exists with the 5 required headings; reference link from `constitution/decision-policy.md` added.

### Sprint 4: Filesystem Data Contracts (added 2026-06-04)
**Goal**: Establish machine-readable filesystem data contracts so dashboard doc metrics are reproducible and lintable.
**Spec**: `specs/2026-06-04-filesystem-data-contracts/` -- SDD-FDC-001. P2 / HITL.
**Deliverables**: (1) YAML frontmatter schema for `specs/**` + `sprints/**`; (2) schema-lint extension; (3) doc-count rollup; (4) new `count` subcommand on `state_builder.py`; (5) opt-in commit-msg convention.
**Hard constraint**: b7ce642 S1 footprint locked -- `render_html()` + data-layer T-001..T-004 immutable (additive code only).
**Status (2026-06-05)**: Clarify CLOSED (D1-D5). Spec APPROVED WITH CONDITIONS (Architect). Plan + ADR-012 DONE. Conditions closed. **Next: /tasks (Software Developer).**
**Validation**: `specs/2026-06-04-filesystem-data-contracts/validation.md` -- R1-R7 required (R5 = automated b7ce642 lock guard), O1-O2 optional.

### Sprint 4: Filesystem Data Contracts -- CLOSED 2026-06-06
**Status**: **DONE** (ratified by owner 2026-06-06, Level-2 via Executive Manager)
**Closed**: 2026-06-06
**Spec**: `specs/2026-06-04-filesystem-data-contracts/` -- SDD-FDC-001. P2 / HITL.
**Sprint 4 commits (in order)**:
- `2335a2a` spec(fdc): amend R5/AC-5 anchor b7ce642 -> 257b081 (Article X)
- `e96f849` docs(fdc): log Q5 amendment of R5 anchor in clarification-log
- `c2e5871` test(fdc): T-FDC-02 add S1 footprint lock guard against 257b081
- `405c332` docs(fdc): T-FDC-01 + T-FDC-06 frontmatter schema and commit convention
- `62006f4` feat(fdc): T-FDC-03 extend schema_lint with artifact contract validator
- `99499ac` feat(fdc): T-FDC-07 add opt-in commit-msg hook + tests
- `47b1568` feat(fdc): T-FDC-04 + T-FDC-05 add count subcommand (rollup + handler)
- `b2586dc` docs(fdc): T-FDC-08 backfill frontmatter across specs/** and sprints/**
- `20c16dc` spec(fdc): T-FDC-09 close validation -- R1..R7 + O1/O2 all checked
**Tests**: 152 -> 200 (+48 net; +47 new tests across all five deliverables, +1 from previously-skipped real-repo lint test that now passes because the in-scope tree lints clean)
**Validation**: 7/7 REQUIRED, 2/2 OPTIONAL all checked. R5 lock guard PASS against 257b081 (re-anchored from b7ce642 via Article X amendment 2026-06-06; see clarification-log Q5). R6 `python schema_lint.py specs/ sprints/` exits 0.
**Lock evidence (current HEAD)**: sha256 of `inspect.getsource(state_builder.<fn>)` for the five locked symbols:
- `render_html`             5b41283be94e5db1adfb99692b457d370b84fe100eeda7734c95cafe823a705b
- `load_sprint_table`       35ab5ad467970ec88709ef923ac608511d49408d31a7787cf2146fccb0e7248f
- `load_sprint_goal`        a50e52427f26b489b98f1030cb99f004127fc177d37dedc8de9c5f3e7de00716
- `detect_current_sprint`   81af06480d402b032665be3d6a2a34c343be0a7005704dc096d52a7280263311
- `load_decisions`          98ba432c79d2a3c6e3c9eb84a69b07ea8af6d7deb7a5cf8fa3245692cd712eaf
**Retro (one paragraph)**: Sprint 4 closed cleanly after a Day-1 anchor drift was caught by the lock guard and resolved via Article X amendment rather than relaxation -- proving the locked-validation discipline works even when the literal anchor is itself wrong. The TDD discipline of landing T-FDC-02 (tripwire) FIRST paid off twice: it gated subsequent state_builder.py edits, and it produced the goldens that the amendment then ratified. The 77-file frontmatter backfill (T-FDC-08) was the largest single touch but went smoothly because the schema lint was written before the backfill ran -- every prepended block was verified by the lint that would later police it. The five-line legacy-frontmatter patch (DESIGN.md, live-ui-v2 family) surfaced naturally during R6 verification and was fixed in-line without scope creep. Net: 9 commits, 152 -> 200 tests, zero contract loosening.

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
- Filesystem Data Contracts spec: `specs/2026-06-04-filesystem-data-contracts/spec.md`
- Filesystem Data Contracts plan: `specs/2026-06-04-filesystem-data-contracts/plan.md`
- ADR-012 (frontmatter data contract): `docs/ADR/012-filesystem-frontmatter-data-contract.md`
