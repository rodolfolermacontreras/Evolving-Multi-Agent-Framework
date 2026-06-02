# Feature Spec: Day-to-Day Brownfield Bootstrap

- Date: 2026-06-01
- Author: principal-architect
- Status: Done
- Priority: P1
- Sprint: PI-3/S2
- Spec ID: SDD-S2-001

---

## Problem Statement

The Evolving Multi-Agent Framework (SDD) was extracted from the Day-to-Day Agent
project but has never been bootstrapped back onto it as a standalone host project.
Until SDD is successfully adopted by a second project, the portability claims in
GENERALIZATION_SDD.md remain unvalidated. The Day-to-Day Agent is the ideal first
pilot: it is a real brownfield project with 743+ tests, a mature FastAPI/HTMX
stack, and the human owner knows both codebases intimately.

This sprint has two deliverables:

1. **Bootstrap**: Install the SDD framework file structure, adapted constitution,
   and agent definitions onto the Day-to-Day repo at `C:\Training\Microsoft\Day_to_Day`
   (GitHub: `rodolfolermacontreras/day-to-day-microsoft`), branch
   `integration/improvements`.

2. **Dogfood**: Implement one small feature -- "Export weekly status report as
   Markdown download" (`GET /api/reports/{date}/export.md`) -- through the full
   SDD lifecycle inside the Day-to-Day repo, proving the bootstrap works.

## Proposed Solution

### Part 1: Brownfield Bootstrap

Use the existing `bootstrap.py brownfield` CLI (with `--draft-only` followed by
human-reviewed `--apply`) to perform the archaeology pass and stage a constitution
proposal. Then manually refine the staged proposal with Day-to-Day-specific
content drawn from `.github/copilot-instructions.md` and the existing codebase.

The bootstrap creates two directory trees in the Day-to-Day repo:

- `.github/` -- adapted Principal agents, worker agents, skills, prompts, and
  instructions (merging with the existing `.github/` which already has
  `copilot-instructions.md` and `workflows/`)
- `spec-driven-development/` -- constitution, templates, backlog, roster, ledger,
  exec, docs (entirely new)

The existing `.github/copilot-instructions.md` in the Day-to-Day repo is
preserved as the root authority. The SDD agents and skills are additive.

#### Constitution Adaptation

Each of the 6 constitution files MUST be adapted for the Day-to-Day project:

| File | Tag | Adaptation |
|------|-----|------------|
| `mission.md` | [PROJECT-SPECIFIC] | Rewrite from scratch. Extract mission from Day-to-Day README and `copilot-instructions.md`. Owner: Rodolfo Lerma. Vision: single-pane-of-glass AI work management. |
| `tech-stack.md` | [PROJECT-SPECIFIC] | Rewrite from scratch. Document: Python 3.12+, FastAPI, HTMX/Jinja2, SQLite/SQLModel, MSAL, OpenAI-compatible LLM (GitHub Models + Copilot fallback), Docker, pytest (743+ baseline). |
| `principles.md` | [CONFIGURABLE] | Inherit the 10 framework articles (I-X) verbatim. Add host articles H1-H9 codifying existing Day-to-Day patterns: Engine singleton, APIRouter discipline, Pydantic schemas, safe_path/esc, file_lock, world_state aggregation, settings object, CSS utility classes, record_llm_call. |
| `roadmap.md` | [PROJECT-SPECIFIC] | Write fresh. PI-1 = "SDD Bootstrap Validation" with the Markdown export feature as the pilot. |
| `decision-policy.md` | [PORTABLE] | Copy verbatim from the framework. |
| `quality-policy.md` | [CONFIGURABLE] | Copy structure. Extend the "Validation by Change Type" table with Day-to-Day rows: backend route (Pydantic + APIRouter + test), HTMX template (esc + macro), LLM workflow (MockLLMClient + record_llm_call). Set test baseline to 743. |

#### Directory Structure Created

```
Day_to_Day/
  .github/                            (EXISTING -- merge, do not replace)
    copilot-instructions.md           (EXISTING -- preserve, do not modify)
    workflows/                        (EXISTING -- preserve)
    agents/                           (NEW)
      principal-executive-manager.agent.md
      principal-product-manager.agent.md
      principal-architect.agent.md
      principal-software-developer.agent.md
      developer-general.agent.md
      ux-designer-general.agent.md
      qa-engineer-general.agent.md
    skills/                           (NEW)
      core/
        sdd-constitution/SKILL.md
        project-context/SKILL.md
        git-workflow/SKILL.md
        testing-conventions/SKILL.md
      workflow/                       (PORTABLE -- copy as-is)
        grill-me/SKILL.md
        to-spec/SKILL.md
        to-plan/SKILL.md
        to-tasks/SKILL.md
        triage/SKILL.md
        implement/SKILL.md
      engineering/                    (PORTABLE -- copy as-is)
        tdd/SKILL.md
        code-review/SKILL.md
        improve-architecture/SKILL.md
        diagnose/SKILL.md
      operational/                    (PORTABLE/CONFIGURABLE)
        handoff/SKILL.md
        fleet-coordinator/SKILL.md
        respect-existing/SKILL.md
      domain/                         (PROJECT-SPECIFIC -- adapt from framework examples)
        fastapi-routes/SKILL.md
        htmx-frontend/SKILL.md
        pytest-runner/SKILL.md
    prompts/                          (PORTABLE -- copy as-is)
      triage.prompt.md
      grill.prompt.md
      spec.prompt.md
      plan.prompt.md
      tasks.prompt.md
      implement.prompt.md
      qa.prompt.md
      retro.prompt.md
      state.prompt.md
    instructions/
      sdd-workflow.instructions.md
  spec-driven-development/            (ENTIRELY NEW)
    README.md
    CONTEXT.md
    constitution/
      mission.md
      tech-stack.md
      principles.md
      roadmap.md
      decision-policy.md
      quality-policy.md
    docs/
      ADR/
        TEMPLATE.md
        001-sdd-adoption.md
      SCORECARD.md
    templates/                        (PORTABLE -- copy as-is from framework)
      feature-spec.md
      plan.md
      task-list.md
      agent-brief.md
      adr.md
      validation.md
      review-report.md
      clarification-log.md
      handoff.md
    roster/
      agents.json
      skills.json
      skill_packs.json
    ledger/
      fleet.db
    fleet/
      conflict-log.md
    backlog/
      IDEAS.md
      BACKLOG.md
    specs/
    sprints/
    exec/
      state.md
    sessions/
```

#### Respect-Existing Constraints

The following Day-to-Day conventions MUST be preserved during bootstrap and
during the dogfood feature:

1. **Branch model**: `master` (read-only) -> `integration/improvements` (trunk) ->
   feature branches. Worktrees at `../wt-{shortname}`.
2. **Virtual environment**: `.venv\Scripts\python.exe` for all commands.
3. **Test command**: `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short`.
4. **Route pattern**: `APIRouter` with prefix in `agent/routes/*.py`. Shared
   helpers (`get_engine`, `esc`, `safe_path`) from `agent/routes/__init__.py`.
5. **Schema pattern**: Pydantic models in `agent/schemas.py` for all POST
   endpoints (GET endpoints use path/query params directly).
6. **Engine pattern**: Lazy singleton in `agent/engine.py`. Access via
   `from agent.engine import engine`.
7. **Config pattern**: Frozen dataclass `settings` in `agent/config.py`.
8. **LLM pattern**: `agent/llm.py` with `record_llm_call` for observability.
9. **Test pattern**: `tmp_path` isolation, `patched_settings` fixture,
   `MockLLMClient` for LLM tests, factory helpers, patch at source module.
10. **Commit format**: `type: short description` (e.g., `feat:`, `fix:`,
    `refactor:`, `test:`). No emojis.

### Part 2: Dogfood Feature -- Markdown Export

#### Endpoint Specification

```
GET /api/reports/{date}/export.md
```

- **Path parameter**: `date` -- ISO 8601 date string (`YYYY-MM-DD`) identifying
  the weekly status report's end date.
- **Response (200)**:
  - `Content-Type: text/markdown; charset=utf-8`
  - `Content-Disposition: attachment; filename="weekly_status_{date}.md"`
  - Body: the weekly status report rendered as Markdown text
- **Response (404)**: returned when no report exists for the given date
  (no HTML file found at `export/weekly_status_{date}.html`)
- **Response (422)**: returned when `date` is not a valid ISO date string

#### Markdown Rendering Logic

The endpoint reads the existing generated `StatusReportData` (or the saved HTML
report) for the given date and produces a Markdown representation. Two
implementation approaches exist:

- **Option A (recommended)**: Add a `render_status_report_markdown(data: StatusReportData) -> str`
  function in a new file `agent/status_report_markdown.py`. The endpoint loads
  the report data (either by re-collecting or by reading the persisted HTML and
  extracting structured data), then calls the renderer. This follows the existing
  pattern where `status_report_renderer.py` renders HTML and
  `status_report_email.py` renders email HTML.

- **Option B**: Parse the saved HTML file and convert to Markdown. Simpler but
  fragile and couples to the HTML renderer's structure.

The Architect recommends Option A. It follows the existing renderer separation
pattern and produces clean, predictable Markdown.

The Markdown output MUST include:
- Report title with date range
- Executive summary section
- Per-project sections (status, completed items, open items, blockers)
- Meetings section (if any)
- Next actions section
- Scorecard table (if any)

The Markdown output MUST NOT include:
- Interactive HTML elements
- CSS/JavaScript
- Raw HTML tags

#### File Changes in Day-to-Day Repo

| File | Action | Description |
|------|--------|-------------|
| `agent/status_report_markdown.py` | CREATE | Markdown renderer: `render_status_report_markdown(data) -> str` |
| `agent/api.py` or `agent/routes/generation.py` | MODIFY | Add the `GET /api/reports/{date}/export.md` route |
| `tests/test_status_report.py` | MODIFY | Add tests for the new endpoint and renderer |

No new dependencies. The Markdown renderer uses only Python stdlib (`textwrap`,
string formatting). No `markdown` or `mdutils` library.

#### SDD Lifecycle Exercise

The dogfood feature MUST pass through every SDD lifecycle phase inside the
Day-to-Day repo:

| Phase | Artifact | Location in Day-to-Day |
|-------|----------|------------------------|
| IDEA | Entry in IDEAS.md | `spec-driven-development/backlog/IDEAS.md` |
| TRIAGE | RICE score in BACKLOG.md | `spec-driven-development/backlog/BACKLOG.md` |
| CLARIFY | Clarification log | `spec-driven-development/specs/YYYY-MM-DD-markdown-export/clarification.md` |
| SPEC | Feature spec | `spec-driven-development/specs/YYYY-MM-DD-markdown-export/spec.md` |
| PLAN | Implementation plan | `spec-driven-development/specs/YYYY-MM-DD-markdown-export/plan.md` |
| TASKS | Task list | `spec-driven-development/specs/YYYY-MM-DD-markdown-export/tasks.md` |
| IMPLEMENT | Code + tests | `agent/status_report_markdown.py`, route file, test file |
| REVIEW | Two-stage review | Stage 1 (spec compliance) + Stage 2 (code quality) |
| DONE | Merged to `integration/improvements` | PR or direct merge after review |

---

## Acceptance Criteria

### Part 1: Bootstrap

1. Given the Day-to-Day repo at `C:\Training\Microsoft\Day_to_Day` on branch
   `integration/improvements`, when the bootstrap is complete, then
   `spec-driven-development/constitution/` contains all 6 constitution files
   with Day-to-Day-specific content (no `TODO(human)` markers remain).

2. Given the bootstrap is complete, when `.github/agents/` is inspected, then it
   contains at least 4 Principal agent definitions and at least 3 generic worker
   agents, each referencing Day-to-Day stack and conventions.

3. Given the bootstrap is complete, when `.github/skills/domain/` is inspected,
   then it contains at least `fastapi-routes/SKILL.md`,
   `htmx-frontend/SKILL.md`, and `pytest-runner/SKILL.md`, each documenting
   existing Day-to-Day patterns (not aspirational patterns).

4. Given the bootstrap is complete, when `.github/copilot-instructions.md` is
   inspected, then it is byte-identical to the pre-bootstrap version (the root
   authority file is never modified by bootstrap).

5. Given the bootstrap is complete, when `spec-driven-development/backlog/IDEAS.md`
   is inspected, then it contains at least the Markdown export feature as a
   seeded idea.

6. Given the bootstrap is complete, when
   `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short` is run, then all
   743+ existing tests pass (bootstrap introduces zero regressions).

7. Given the bootstrap is complete, when `spec-driven-development/docs/ADR/001-sdd-adoption.md`
   is inspected, then it documents the decision to adopt SDD on the Day-to-Day
   project with context, rationale, and consequences.

### Part 2: Dogfood Feature

8. Given the Markdown export endpoint is implemented, when
   `GET /api/reports/2026-05-30/export.md` is called and a report for that date
   exists, then the response has status 200, `Content-Type: text/markdown; charset=utf-8`,
   and `Content-Disposition: attachment; filename="weekly_status_2026-05-30.md"`.

9. Given the Markdown export endpoint is implemented, when
   `GET /api/reports/2026-05-30/export.md` is called and NO report exists for
   that date, then the response has status 404.

10. Given the Markdown export endpoint is implemented, when
    `GET /api/reports/not-a-date/export.md` is called, then the response has
    status 422 (or 400).

11. Given the Markdown export endpoint is implemented, when the response body is
    inspected for a valid report, then it contains valid Markdown with: a title
    heading, an executive summary section, at least one project section, and no
    raw HTML tags.

12. Given the dogfood feature is complete, when the SDD spec directory
    `spec-driven-development/specs/` in the Day-to-Day repo is inspected, then it
    contains a feature directory with at least `spec.md`, `plan.md`, and
    `tasks.md` for the Markdown export feature.

13. Given the dogfood feature is complete, when the test suite is run, then the
    test count is >= 745 (743 baseline + at least 2 new tests for the export
    endpoint).

14. Given the dogfood feature is complete, when the implementation is reviewed,
    then it passes both Stage 1 (spec compliance) and Stage 2 (code quality)
    review with zero CRITICAL issues.

---

## Affected Modules

### Framework Repo (Evolving-Multi-Agent-Framework)

- Files:
  - `spec-driven-development/specs/2026-05-26-day-to-day-brownfield-bootstrap/spec.md` (this file)
  - `spec-driven-development/cli/bootstrap.py` (may need minor fixes if brownfield apply fails)
- Directories:
  - `spec-driven-development/specs/2026-05-26-day-to-day-brownfield-bootstrap/`

### Day-to-Day Repo (day-to-day-microsoft)

- Files (bootstrap -- all NEW):
  - `.github/agents/*.agent.md` (7 files)
  - `.github/skills/**/*.md` (~25 files)
  - `.github/prompts/*.prompt.md` (~9 files)
  - `.github/instructions/sdd-workflow.instructions.md`
  - `spec-driven-development/constitution/*.md` (6 files)
  - `spec-driven-development/CONTEXT.md`
  - `spec-driven-development/README.md`
  - `spec-driven-development/docs/ADR/001-sdd-adoption.md`
  - `spec-driven-development/docs/ADR/TEMPLATE.md`
  - `spec-driven-development/docs/SCORECARD.md`
  - `spec-driven-development/templates/*.md` (9 files)
  - `spec-driven-development/roster/*.json` (3 files)
  - `spec-driven-development/backlog/IDEAS.md`
  - `spec-driven-development/backlog/BACKLOG.md`

- Files (dogfood -- MODIFY or CREATE):
  - `agent/status_report_markdown.py` (CREATE)
  - `agent/api.py` or `agent/routes/generation.py` (MODIFY -- add route)
  - `tests/test_status_report.py` (MODIFY -- add tests)

- Directories (bootstrap -- all NEW):
  - `spec-driven-development/` (entire tree)

---

## Data Model Changes

None. The dogfood feature reads existing `StatusReportData` and renders it as
Markdown. No database schema changes. No new SQLModel tables. No migrations.

---

## API Changes

One new GET endpoint added to the Day-to-Day API:

```
GET /api/reports/{date}/export.md

Path Parameters:
  date: str  -- ISO 8601 date (YYYY-MM-DD)

Response 200:
  Content-Type: text/markdown; charset=utf-8
  Content-Disposition: attachment; filename="weekly_status_{date}.md"
  Body: Markdown text

Response 404:
  {"detail": "Report not found"}

Response 422:
  {"detail": "Invalid date format. Use YYYY-MM-DD."}
```

This endpoint is read-only and stateless. It does not trigger report generation;
it exports an already-generated report. If the user needs a report generated
first, they use the existing `POST /api/reports/weekly-status` endpoint.

---

## Test Strategy

- **Unit tests** (in `tests/test_status_report.py`):
  - `test_export_markdown_happy_path`: Create a mock report HTML file at the
    expected path, call `GET /api/reports/{date}/export.md`, assert 200,
    correct headers, body contains expected Markdown sections.
  - `test_export_markdown_not_found`: Call with a date for which no report
    exists. Assert 404.
  - `test_export_markdown_invalid_date`: Call with `not-a-date`. Assert 422.
  - `test_render_markdown_sections`: Unit-test the
    `render_status_report_markdown` function directly with a synthetic
    `StatusReportData` object. Assert output contains title, executive summary,
    project sections, and no HTML tags.

- **Integration**: The happy-path test acts as an integration test (FastAPI
  TestClient -> route -> renderer -> response).

- **Regression**: Run the full test suite after implementation. Assert count >= 745.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Bootstrap overwrites `.github/copilot-instructions.md` | Low | High | AC-4 explicitly guards this. Bootstrap script copies to `.github/agents/` and `.github/skills/` only. Manual verification step. |
| Existing tests break after bootstrap | Low | High | Bootstrap adds only Markdown/JSON/YAML files. No Python code modified. AC-6 requires full test pass. |
| `bootstrap.py brownfield --apply` fails on Day-to-Day repo structure | Medium | Medium | Run `--draft-only` first. If `--apply` fails, perform manual file copy guided by the archaeology JSON. |
| Markdown renderer couples to HTML renderer internals | Medium | Medium | Use Option A (render from `StatusReportData`, not HTML parsing). Decouples completely. |
| Date path parameter conflicts with existing routes | Low | Low | New route `/api/reports/{date}/export.md` uses a distinct path pattern. No overlap with existing `/api/reports/weekly-status/*` routes. |

---

## Scope Guards (Out of Scope)

- **Generating reports on demand**: The export endpoint reads existing reports
  only. It does not trigger `generate_status_report`. Adding on-demand generation
  is a separate backlog item.
- **PDF export**: Only Markdown export is in scope. PDF is a future feature.
- **UI download button in the template**: MAY be added as a stretch goal but is
  NOT required for AC. The API endpoint is sufficient.
- **Modifying existing Day-to-Day tests**: Only additive test changes (new test
  functions). No refactoring of existing tests.
- **Modifying `.github/copilot-instructions.md`** in the Day-to-Day repo:
  explicitly forbidden.
- **Upgrading Day-to-Day dependencies**: No new pip packages. No version bumps.
- **Full CLI automation of bootstrap**: If `bootstrap.py brownfield --apply`
  does not work cleanly, manual file copy is acceptable for this sprint.
  Fixing the CLI is a separate backlog item.
- **Adapting all 12 slash command prompts**: Only the subset needed for the
  dogfood lifecycle (`/triage`, `/spec`, `/plan`, `/tasks`, `/implement`,
  `/qa`) are required. Others MAY be deferred.
- **Fleet dispatch or parallel workers**: The dogfood feature is small enough
  for sequential single-worker implementation.
- **Modifying the framework repo's constitution or core files**: This sprint
  operates on the Day-to-Day repo. Framework-side changes are limited to this
  spec and any minor bootstrap.py fixes.

---

## Validation Contract

The binding validation contract for this feature lives in the sibling file
`validation.md` in this feature directory. It is written during `/spec`, locked
at `/tasks`, and must have zero unchecked required items before implementation
can be considered complete.

---

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| REQ-1: SDD directory structure created | AC-1: constitution files present, no TODO markers | `spec-driven-development/constitution/` |
| REQ-2: Agent definitions adapted | AC-2: 4 principals + 3 workers in `.github/agents/` | `.github/agents/` |
| REQ-3: Domain skills document existing patterns | AC-3: 3 domain skills in `.github/skills/domain/` | `.github/skills/domain/` |
| REQ-4: Root authority preserved | AC-4: `copilot-instructions.md` byte-identical | `.github/copilot-instructions.md` |
| REQ-5: Backlog seeded | AC-5: IDEAS.md contains Markdown export idea | `spec-driven-development/backlog/IDEAS.md` |
| REQ-6: Zero regression | AC-6: 743+ tests pass | `tests/` |
| REQ-7: Export endpoint returns Markdown | AC-8: 200 with correct Content-Type and Content-Disposition | `agent/api.py` or `agent/routes/generation.py` |
| REQ-8: Export endpoint 404 for missing report | AC-9: 404 response | Route handler |
| REQ-9: Export endpoint rejects invalid date | AC-10: 422 response | Route handler |
| REQ-10: Markdown body is valid | AC-11: Title, summary, projects, no HTML | `agent/status_report_markdown.py` |
| REQ-11: SDD lifecycle exercised | AC-12: spec directory has spec.md, plan.md, tasks.md | `spec-driven-development/specs/` |
| REQ-12: Test count increases | AC-13: >= 745 tests | `tests/test_status_report.py` |
| REQ-13: Two-stage review passes | AC-14: Stage 1 + Stage 2 with zero CRITICALs | Review report |
| REQ-14: ADR documents adoption | AC-7: ADR-001 present with context and rationale | `spec-driven-development/docs/ADR/001-sdd-adoption.md` |

---

## Open Questions

None. All blocking questions were answered in the clarification log
(`clarification.md`, 2026-06-01).

---

## Implementation Sequencing

The two parts MUST be sequenced:

1. **Part 1 (Bootstrap)** completes first. All AC 1-7 pass.
2. **Part 2 (Dogfood)** executes inside the bootstrapped SDD structure.
   AC 8-14 pass.

Part 2 cannot begin until Part 1 is complete because the dogfood feature's
SDD artifacts (spec, plan, tasks) must be created inside the
`spec-driven-development/` directory that Part 1 creates.

---

## Effort Estimate

- Part 1 (Bootstrap): **M** -- 2-3 hours of manual file adaptation, constitution
  authoring, and verification. Mostly document writing, not code.
- Part 2 (Dogfood): **S** -- 1-2 hours. One new file (~100 lines), one route
  addition (~20 lines), 4 new tests (~80 lines).
- Total: **M** -- achievable in a single sprint.
