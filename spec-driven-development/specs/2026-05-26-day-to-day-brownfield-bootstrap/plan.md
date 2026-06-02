# Implementation Plan: Day-to-Day Brownfield Bootstrap

- Spec Reference: SDD-S2-001 (`spec.md` in this directory)
- Author: principal-software-developer
- Status: APPROVED
- Last Updated: 2026-06-01

---

## Spec Compliance Review (Stage 1 -- inline)

Reviewed `spec.md` against `clarification.md` and `validation.md`.

| Check | Verdict | Notes |
|-------|---------|-------|
| Q1 answer (export endpoint) reflected in spec | COMPLIANT | Spec Part 2 matches: `GET /api/reports/{date}/export.md`, no new deps, 2-3 files |
| Q2 answer (repo path) reflected in spec | COMPLIANT | Spec uses `C:\Training\Microsoft\Day_to_Day` and `integration/improvements` throughout |
| VAL-1 through VAL-12 (bootstrap) covered by AC | COMPLIANT | AC 1-7 cover all bootstrap validations. VAL-5 host articles (H1+) match principles.md spec. VAL-8 (byte-identical copilot-instructions.md) matches AC-4. VAL-11 (ADR) matches AC-7. VAL-12 (CONTEXT.md) covered by directory structure. |
| VAL-13 through VAL-23 (dogfood) covered by AC | COMPLIANT | AC 8-14 cover all dogfood validations. VAL-20 (render function in specific file) matches spec Option A. VAL-21 (745 tests) matches AC-13. VAL-22 (SDD spec dir) matches AC-12. VAL-23 (two-stage review) matches AC-14. |
| Existing Day-to-Day patterns respected | COMPLIANT | Spec section "Respect-Existing Constraints" lists all 10 patterns. Route goes in `agent/routes/generation.py` (existing generation router). |
| Scope guards reasonable | COMPLIANT | No scope creep. Stretch items (VAL-S1, VAL-S2) clearly marked optional. |
| MISSING items | NONE | -- |
| EXTRA items | NONE | -- |
| WRONG items | NONE | -- |

**Verdict: PASS -- spec is compliant with clarification answers and validation contract. No CRITICAL issues. Proceeding to plan.**

One SUGGESTION (non-blocking): The spec says `agent/api.py` or `agent/routes/generation.py` for the route. The Day-to-Day repo has already been refactored to use `agent/routes/generation.py` (the monolithic `api.py` still exists but routes are split). Plan will target `agent/routes/generation.py` exclusively.

---

## Approach Summary

Two-part sequential delivery. Part 1 (Bootstrap) creates the SDD framework
structure in the Day-to-Day repo by adapting the archaeology proposal, writing
constitution files, copying portable artifacts, and creating agent/skill
definitions. Part 2 (Dogfood) exercises the bootstrapped SDD by implementing
the Markdown export feature through the full lifecycle. All work targets the
Day-to-Day repo at `C:\Training\Microsoft\Day_to_Day` on branch
`integration/improvements`, except for this spec/plan/tasks which live in the
framework repo.

**Key constraint**: Part 1 must be fully complete (all VAL-1 through VAL-12
passing) before Part 2 begins, because Part 2 creates SDD artifacts inside
the directory tree that Part 1 creates.

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1A | Constitution authoring | None | 6 constitution files in `spec-driven-development/constitution/` |
| 1B | Agent and skill definitions | None (parallel with 1A) | 7 agent files, 3+ domain skills, core/workflow/engineering/operational skills |
| 1C | SDD scaffold and backlog | None (parallel with 1A, 1B) | Templates, roster, ledger, ADR-001, CONTEXT.md, IDEAS.md, BACKLOG.md |
| 1D | Bootstrap verification | 1A, 1B, 1C | Full test suite passes, copilot-instructions.md unchanged, all VAL-1 to VAL-12 checked |
| 2A | Dogfood SDD artifacts | 1D | spec.md, plan.md, tasks.md for Markdown export in Day-to-Day SDD |
| 2B | Dogfood implementation (TDD) | 2A | `agent/status_report_markdown.py`, route in `generation.py`, tests |
| 2C | Dogfood review and integration | 2B | Two-stage review report, merge to `integration/improvements` |

## Parallel-Safe Tasks

Within Part 1, three workstreams can proceed in parallel because they touch
completely disjoint file sets:

- **Phase 1A** (constitution files) -- Files: `spec-driven-development/constitution/*.md`
- **Phase 1B** (agents + skills) -- Files: `.github/agents/*.agent.md`, `.github/skills/**/*.md`, `.github/prompts/*.prompt.md`, `.github/instructions/*.md`
- **Phase 1C** (scaffold + backlog) -- Files: `spec-driven-development/{templates,roster,ledger,fleet,backlog,docs,exec,sessions,sprints}/**`

No file overlap between these three workstreams.

## Sequential Tasks

1. Phase 1D (verification) -- must wait for 1A + 1B + 1C
2. Phase 2A (dogfood SDD artifacts) -- must wait for 1D
3. Phase 2B (dogfood implementation) -- must wait for 2A
4. Phase 2C (dogfood review) -- must wait for 2B

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Archaeology proposal drafts are stale or incomplete | Medium | Low | Drafts in `.sdd-proposal/constitution/` exist but will be rewritten with spec guidance. They are a starting point, not a dependency. |
| Bootstrap file count is large (~50+ files) | Low | Medium | Most are portable copies from the framework. Only constitution and domain skills need authoring. Batch by category. |
| copilot-instructions.md accidentally modified | Low | High | SHA comparison before and after. VAL-8 explicitly tests this. |
| Day-to-Day tests fail before bootstrap | Low | High | Run full test suite BEFORE any changes. If baseline fails, stop and fix first. |
| StatusReportData structure has changed since spec was written | Low | Medium | Verify the dataclass fields before writing the renderer. Spec Option A (render from data) isolates from HTML changes. |
| Route path conflicts with existing generation routes | Low | Low | Verified: no existing routes match `/api/reports/{date}/export.md`. |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1A | M | 6 constitution files, each requires Day-to-Day-specific content. ~30 min per file. |
| 1B | M | 7 agent files (adapt from framework), 3 domain skills (write from Day-to-Day patterns), ~20 portable skill copies. |
| 1C | S | Mostly copy-paste from framework templates. ADR-001 and CONTEXT.md need authoring. |
| 1D | S | Run tests, verify checksums, spot-check files. |
| 2A | S | Write spec/plan/tasks for a small feature. Can be lightweight (< 5 files). |
| 2B | S | 1 new file (~100 lines), 1 route addition (~20 lines), 4 tests (~80 lines). |
| 2C | S | Two-stage review on small scope. |
| **Total** | **M** | Achievable in a single sprint. Part 1 is the bulk. |

## Repo Boundaries

| Phase | Repo | Branch |
|-------|------|--------|
| 1A-1D | Day-to-Day (`C:\Training\Microsoft\Day_to_Day`) | `integration/improvements` |
| 2A-2C | Day-to-Day (`C:\Training\Microsoft\Day_to_Day`) | `integration/improvements` (or feature branch) |
| This plan + spec + tasks | Framework (`C:\Training\Projects\Evolving-Multi-Agent-Framework`) | `master` (spec artifacts only) |

## Validation Criteria

> Cross-reference rule: references use VAL-N identifiers from `validation.md`.

**Part 1 Gate (must all pass before Part 2 starts):**
- [ ] VAL-1: Constitution directory has 6 files
- [ ] VAL-2: No `TODO(human)` markers in constitution
- [ ] VAL-3: mission.md references Day-to-Day, Rodolfo Lerma, single-pane-of-glass
- [ ] VAL-4: tech-stack.md documents full stack
- [ ] VAL-5: principles.md has framework articles I-X + host articles H1+
- [ ] VAL-6: 7+ agent definitions in `.github/agents/`
- [ ] VAL-7: 3+ domain skills in `.github/skills/domain/`
- [ ] VAL-8: copilot-instructions.md byte-identical
- [ ] VAL-9: IDEAS.md contains Markdown export idea
- [ ] VAL-10: Full test suite passes (743+ tests)
- [ ] VAL-11: ADR-001 exists with required sections
- [ ] VAL-12: CONTEXT.md exists with 10+ terms

**Part 2 Gate (Definition of Done):**
- [ ] VAL-13: Export endpoint returns 200 for existing report
- [ ] VAL-14: Correct Content-Type header
- [ ] VAL-15: Correct Content-Disposition header
- [ ] VAL-16: Body starts with Markdown heading
- [ ] VAL-17: No `<` characters in body
- [ ] VAL-18: 404 for missing report
- [ ] VAL-19: 422 for invalid date
- [ ] VAL-20: `render_status_report_markdown` in `agent/status_report_markdown.py`
- [ ] VAL-21: Test count >= 745
- [ ] VAL-22: SDD spec directory with spec.md exists in Day-to-Day
- [ ] VAL-23: Two-stage review with zero CRITICAL issues
