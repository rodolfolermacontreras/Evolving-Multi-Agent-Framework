---
id: SDD-20260526DAYT-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-26-day-to-day-brownfield-bootstrap
---

# Task List: Day-to-Day Brownfield Bootstrap

- Spec Reference: SDD-S2-001 (`spec.md`)
- Plan Reference: `plan.md` (this directory)
- Task ID Format: `T-NNN` (local short IDs; directory carries date namespace)
- Owner: principal-software-developer

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Repo Legend

- **FW** = Framework repo (`C:\Training\Projects\Evolving-Multi-Agent-Framework`)
- **D2D** = Day-to-Day repo (`C:\Training\Microsoft\Day_to_Day`)

---

## Part 1: Bootstrap

### Phase 1A -- Constitution Authoring (Parallel-safe batch)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | Create `mission.md` with Day-to-Day identity: owner (Rodolfo Lerma), org (WWIC Central Analytics), vision (single-pane-of-glass AI work management). Adapt from `.sdd-proposal/constitution/mission.md` and `README.md`. | D2D | `spec-driven-development/constitution/mission.md` | File exists, references "Day-to-Day Agent", "Rodolfo Lerma", "single-pane-of-glass". No `TODO(human)`. Proves VAL-1, VAL-2, VAL-3. | S | NONE | AFK | Yes | pending |
| T-002 | Create `tech-stack.md` documenting: Python 3.12+, FastAPI, HTMX/Jinja2, SQLite/SQLModel, MSAL, OpenAI-compatible LLM, Docker, pytest (743+ baseline). | D2D | `spec-driven-development/constitution/tech-stack.md` | File exists, contains all stack items listed. No `TODO(human)`. Proves VAL-1, VAL-2, VAL-4. | S | NONE | AFK | Yes | pending |
| T-003 | Create `principles.md` with 10 framework articles (I-X) verbatim from framework constitution, plus host articles H1-H9: Engine singleton, APIRouter discipline, Pydantic schemas, safe_path/esc, file_lock, world_state, settings, CSS utility classes, record_llm_call. | D2D | `spec-driven-development/constitution/principles.md` | File exists, contains articles I through X, contains H1 through H9 referencing Engine, APIRouter, safe_path, esc, file_lock, world_state, settings, record_llm_call. No `TODO(human)`. Proves VAL-1, VAL-2, VAL-5. | M | NONE | AFK | Yes | pending |
| T-004 | Create `roadmap.md` for Day-to-Day. PI-1 = "SDD Bootstrap Validation" with Markdown export as pilot feature. | D2D | `spec-driven-development/constitution/roadmap.md` | File exists, references PI-1 and Markdown export. No `TODO(human)`. Proves VAL-1, VAL-2. | S | NONE | AFK | Yes | pending |
| T-005 | Copy `decision-policy.md` verbatim from framework constitution. | D2D | `spec-driven-development/constitution/decision-policy.md` | File exists, content matches framework version. No `TODO(human)`. Proves VAL-1, VAL-2. | S | NONE | AFK | Yes | pending |
| T-006 | Create `quality-policy.md` by copying framework structure and extending with Day-to-Day validation rows: backend route (Pydantic + APIRouter + test), HTMX template (esc + macro), LLM workflow (MockLLMClient + record_llm_call). Set test baseline to 743. | D2D | `spec-driven-development/constitution/quality-policy.md` | File exists, contains Day-to-Day-specific validation rows and baseline 743. No `TODO(human)`. Proves VAL-1, VAL-2. | S | NONE | AFK | Yes | pending |

### Phase 1B -- Agent and Skill Definitions (Parallel-safe batch)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-007 | Create 4 principal agent definitions adapted for Day-to-Day: `principal-executive-manager.agent.md`, `principal-product-manager.agent.md`, `principal-architect.agent.md`, `principal-software-developer.agent.md`. Each references Day-to-Day stack, conventions, and repo paths. | D2D | `.github/agents/principal-*.agent.md` (4 files) | 4 files exist in `.github/agents/`, each references "Day-to-Day", Python/FastAPI stack. Proves VAL-6. | M | NONE | AFK | Yes | pending |
| T-008 | Create 3 generic worker agent definitions: `developer-general.agent.md`, `ux-designer-general.agent.md`, `qa-engineer-general.agent.md`. Each references Day-to-Day conventions. | D2D | `.github/agents/{developer,ux-designer,qa-engineer}-general.agent.md` (3 files) | 3 files exist in `.github/agents/`. Total agent count >= 7. Proves VAL-6. | S | NONE | AFK | Yes | pending |
| T-009 | Create 3 domain skill directories with SKILL.md files: `fastapi-routes/SKILL.md` (documenting APIRouter, safe_path, esc, Pydantic patterns), `htmx-frontend/SKILL.md` (documenting Jinja2 macros, esc, CSS utility classes), `pytest-runner/SKILL.md` (documenting patched_settings, MockLLMClient, factory helpers, patch-at-source). Content must describe EXISTING Day-to-Day patterns, not aspirational ones. | D2D | `.github/skills/domain/{fastapi-routes,htmx-frontend,pytest-runner}/SKILL.md` (3 files) | 3 directories exist with SKILL.md files. Each references actual Day-to-Day code patterns. Proves VAL-7. | M | NONE | AFK | Yes | pending |
| T-010 | Copy portable skills from framework: core skills (sdd-constitution, project-context, git-workflow, testing-conventions), workflow skills (grill-me, to-spec, to-plan, to-tasks, triage, implement), engineering skills (tdd, code-review, improve-architecture, diagnose), operational skills (handoff, fleet-coordinator, respect-existing). Copy prompts and instructions directories. | D2D | `.github/skills/{core,workflow,engineering,operational}/**/*.md`, `.github/prompts/*.prompt.md`, `.github/instructions/*.md` | Directories exist with SKILL.md files. Prompts directory has >= 6 prompt files. Proves VAL-6 (skills support). | M | NONE | AFK | Yes | pending |

### Phase 1C -- SDD Scaffold, ADR, Backlog (Parallel-safe batch)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-011 | Create SDD scaffold directories and copy portable templates from framework: `spec-driven-development/{README.md,templates/,roster/,ledger/,fleet/,specs/,sprints/,exec/,sessions/}`. Copy template files (feature-spec.md, plan.md, task-list.md, agent-brief.md, adr.md, validation.md, review-report.md, clarification-log.md, handoff.md). Create roster JSON stubs. Create ledger `fleet.db`. Create `fleet/conflict-log.md`. | D2D | `spec-driven-development/{README.md,templates/*.md,roster/*.json,ledger/fleet.db,fleet/conflict-log.md}` | Directories exist. Templates match framework versions. Proves VAL-1 (directory structure). | M | NONE | AFK | Yes | pending |
| T-012 | Create `spec-driven-development/CONTEXT.md` with >= 10 vocabulary terms for the Day-to-Day project: Engine, world_state, StatusReportData, safe_path, esc, patched_settings, MockLLMClient, record_llm_call, file_lock, APIRouter prefix, settings, ideas file. | D2D | `spec-driven-development/CONTEXT.md` | File exists, contains >= 10 defined terms. Proves VAL-12. | S | NONE | AFK | Yes | pending |
| T-013 | Create `spec-driven-development/docs/ADR/001-sdd-adoption.md` documenting the decision to adopt SDD on Day-to-Day. Must include Status, Context, Decision, and Consequences sections. Also create `docs/ADR/TEMPLATE.md` (copy from framework) and `docs/SCORECARD.md` stub. | D2D | `spec-driven-development/docs/ADR/001-sdd-adoption.md`, `spec-driven-development/docs/ADR/TEMPLATE.md`, `spec-driven-development/docs/SCORECARD.md` | ADR-001 exists with all 4 required sections. TEMPLATE.md exists. Proves VAL-11. | S | NONE | AFK | Yes | pending |
| T-014 | Create `spec-driven-development/backlog/IDEAS.md` with the Markdown export feature seeded as an idea entry. Create `spec-driven-development/backlog/BACKLOG.md` stub. | D2D | `spec-driven-development/backlog/IDEAS.md`, `spec-driven-development/backlog/BACKLOG.md` | IDEAS.md exists and contains "Markdown export" or "export report as Markdown". BACKLOG.md exists. Proves VAL-9. | S | NONE | AFK | Yes | pending |

### Phase 1D -- Bootstrap Verification (Sequential gate)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-015 | Verify `.github/copilot-instructions.md` is byte-identical to pre-bootstrap version. Compute SHA before and after. | D2D | `.github/copilot-instructions.md` (READ ONLY) | SHA comparison matches. File was not modified. Proves VAL-8. | S | T-007, T-008, T-009, T-010 | HITL | No | pending |
| T-016 | Run full test suite: `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short`. Assert all tests pass and count >= 743. | D2D | `tests/` (READ ONLY) | Exit code 0, test count >= 743. Proves VAL-10. | S | T-001 through T-014 | HITL | No | pending |
| T-017 | Spot-check all VAL-1 through VAL-12 items from `validation.md`. Mark each as checked. This is the Part 1 gate -- Part 2 cannot begin until this passes. | D2D | All bootstrap files (READ ONLY) | All 12 VAL items verified. Proves Part 1 gate. | S | T-015, T-016 | HITL | No | pending |

---

## CHECKPOINT 1: Part 1 Complete

Run full test suite. Verify all VAL-1 through VAL-12. If any fail, fix before proceeding.

---

## Part 2: Dogfood Feature

### Phase 2A -- SDD Lifecycle Artifacts (Sequential)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-018 | Create SDD spec directory for the dogfood feature: `spec-driven-development/specs/2026-06-01-markdown-export/`. Write lightweight `spec.md` (problem, AC, affected files), `plan.md` (single phase), and `tasks.md` (3-4 tasks). Seed the idea in IDEAS.md and add RICE score in BACKLOG.md. | D2D | `spec-driven-development/specs/2026-06-01-markdown-export/{spec.md,plan.md,tasks.md}`, `spec-driven-development/backlog/{IDEAS.md,BACKLOG.md}` | Spec directory exists with all 3 files. Each is non-empty and follows template format. Proves VAL-22, VAL-S2. | S | T-017 | AFK | No | pending |

### Phase 2B -- TDD Implementation (Sequential)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-019 | RED: Write failing tests in `tests/test_status_report.py`. Add 4 test functions: `test_export_markdown_happy_path` (200, correct headers, Markdown body), `test_export_markdown_not_found` (404), `test_export_markdown_invalid_date` (422), `test_render_markdown_sections` (unit test for renderer function). Use `patched_settings`, `tmp_path`, factory data. Tests must FAIL (no implementation yet). | D2D | `tests/test_status_report.py` | 4 new test functions exist. Running them produces 4 FAILURES (expected -- RED phase). Proves VAL-21 (test count after GREEN). | S | T-018 | AFK | No | pending |
| T-020 | GREEN: Create `agent/status_report_markdown.py` with `render_status_report_markdown(data: StatusReportData) -> str`. Uses only stdlib (textwrap, string formatting). Output includes: title with date range, executive summary, per-project sections, meetings, next actions, scorecard table. No HTML tags in output. | D2D | `agent/status_report_markdown.py` | File exists. Function signature matches. Calling with synthetic StatusReportData returns string starting with `# `, containing section headers, no `<` chars. Proves VAL-16, VAL-17, VAL-20. | S | T-019 | AFK | No | pending |
| T-021 | GREEN: Add `GET /api/reports/{date}/export.md` route to `agent/routes/generation.py`. Validate date format (return 422 for invalid). Look up report file at `export/weekly_status_{date}.html`. Return 404 if not found. Load StatusReportData, call `render_status_report_markdown`, return `Response` with `text/markdown; charset=utf-8` Content-Type and `attachment; filename="weekly_status_{date}.md"` Content-Disposition. | D2D | `agent/routes/generation.py` | All 4 tests from T-019 pass (GREEN). Route returns correct status codes and headers. Proves VAL-13, VAL-14, VAL-15, VAL-18, VAL-19. | S | T-020 | AFK | No | pending |
| T-022 | Run full test suite. Assert exit code 0 and test count >= 745 (743 baseline + at least 2 new). | D2D | `tests/` (READ ONLY) | `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short` exits 0. Count >= 745. Proves VAL-10, VAL-21. | S | T-021 | HITL | No | pending |

### Phase 2C -- Review and Integration (Sequential)

| Task ID | Description | Repo | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-------------|------|------------|-----------------|--------|------|------|-------|--------|
| T-023 | Perform two-stage review. Stage 1: spec compliance (MISSING/EXTRA/WRONG). Stage 2: code quality (CRITICAL/IMPORTANT/SUGGESTION). File review report. Zero CRITICAL issues required. | D2D | Review report (inline or in spec directory) | Review report filed. Stage 1 PASS. Stage 2 verdict APPROVED with zero CRITICAL. Proves VAL-23. | S | T-022 | HITL | No | pending |
| T-024 | Commit all Part 2 changes to `integration/improvements`. Use commit format `feat: add markdown export endpoint for weekly status reports`. | D2D | All Part 2 files | Commit exists on `integration/improvements` with correct format. | S | T-023 | HITL | No | pending |

---

## CHECKPOINT 2: Part 2 Complete

Run full test suite. Verify all VAL-13 through VAL-23. Sprint S2 is DONE.

---

## Dependency Graph

```
Phase 1A: T-001, T-002, T-003, T-004, T-005, T-006  (parallel)
Phase 1B: T-007, T-008, T-009, T-010                 (parallel, parallel with 1A)
Phase 1C: T-011, T-012, T-013, T-014                 (parallel, parallel with 1A/1B)
Phase 1D: T-015 -> T-016 -> T-017                    (sequential, after 1A+1B+1C)
                                                       |
                                                       v
Phase 2A: T-018                                       (after T-017)
Phase 2B: T-019 -> T-020 -> T-021 -> T-022           (sequential TDD)
Phase 2C: T-023 -> T-024                              (sequential)
```

## Fleet Dispatch Plan

**Batch 1** (up to 4 parallel workers -- Phase 1A+1B+1C):
- Worker A: T-001, T-002, T-004, T-005, T-006 (constitution simple files)
- Worker B: T-003 (principles.md -- larger, needs framework articles + host articles)
- Worker C: T-007, T-008, T-009, T-010 (agents + skills)
- Worker D: T-011, T-012, T-013, T-014 (scaffold + ADR + backlog)

No file conflicts between workers. All touch disjoint paths.

**Batch 2** (sequential -- Phase 1D): T-015, T-016, T-017 (HITL verification)

**Batch 3** (sequential -- Phase 2): T-018 through T-024 (single worker + HITL gates)

## VAL Coverage Matrix

| VAL | Task(s) |
|-----|---------|
| VAL-1 | T-001 through T-006 |
| VAL-2 | T-001 through T-006 |
| VAL-3 | T-001 |
| VAL-4 | T-002 |
| VAL-5 | T-003 |
| VAL-6 | T-007, T-008 |
| VAL-7 | T-009 |
| VAL-8 | T-015 |
| VAL-9 | T-014 |
| VAL-10 | T-016, T-022 |
| VAL-11 | T-013 |
| VAL-12 | T-012 |
| VAL-13 | T-021 |
| VAL-14 | T-021 |
| VAL-15 | T-021 |
| VAL-16 | T-020 |
| VAL-17 | T-020 |
| VAL-18 | T-021 |
| VAL-19 | T-021 |
| VAL-20 | T-020 |
| VAL-21 | T-019, T-022 |
| VAL-22 | T-018 |
| VAL-23 | T-023 |
| VAL-S1 | (stretch -- no task assigned) |
| VAL-S2 | T-018 |

## Notes

- Use `Fleet Dispatch Eligible = No` when a task touches shared files, requires human judgment, or is sequential by nature.
- All D2D tasks operate on branch `integration/improvements`. No feature branch needed for bootstrap (additive files only). Feature branch optional for dogfood but not required given small scope.
- The `respect-existing` skill applies: no modifications to existing Day-to-Day code patterns, only additive changes.
- No new pip dependencies allowed in D2D. Markdown renderer uses only stdlib.
- Record blockers inline in the table status column and summarize them during handoff.
