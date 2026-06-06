---
id: SDD-20260526DAYT-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-26-day-to-day-brownfield-bootstrap
---

# Validation Contract: Day-to-Day Brownfield Bootstrap

- Spec: SDD-S2-001
- Date: 2026-06-01
- Status: OPEN (locked at /tasks)

---

## Part 1: Bootstrap (Required)

- [ ] **VAL-1**: `spec-driven-development/constitution/` contains 6 files: mission.md, tech-stack.md, principles.md, roadmap.md, decision-policy.md, quality-policy.md
- [ ] **VAL-2**: No `TODO(human)` markers remain in any constitution file
- [ ] **VAL-3**: `mission.md` references Day-to-Day Agent, Rodolfo Lerma, and the single-pane-of-glass vision
- [ ] **VAL-4**: `tech-stack.md` documents Python 3.12+, FastAPI, HTMX/Jinja2, SQLite/SQLModel, pytest
- [ ] **VAL-5**: `principles.md` contains 10 framework articles (I-X) plus host articles (H1+) codifying Engine singleton, APIRouter, safe_path, esc, file_lock, world_state, settings, record_llm_call
- [ ] **VAL-6**: `.github/agents/` contains >= 7 agent definition files (4 principals + 3 workers)
- [ ] **VAL-7**: `.github/skills/domain/` contains >= 3 domain skill directories (fastapi-routes, htmx-frontend, pytest-runner)
- [ ] **VAL-8**: `.github/copilot-instructions.md` is byte-identical to pre-bootstrap version (SHA comparison)
- [ ] **VAL-9**: `spec-driven-development/backlog/IDEAS.md` contains the Markdown export feature idea
- [ ] **VAL-10**: Full test suite passes: `.venv\Scripts\python.exe -m pytest tests/ -v --tb=short` exits 0 with >= 743 tests
- [ ] **VAL-11**: `spec-driven-development/docs/ADR/001-sdd-adoption.md` exists with Status, Context, Decision, and Consequences sections
- [ ] **VAL-12**: `spec-driven-development/CONTEXT.md` exists with >= 10 vocabulary terms

## Part 2: Dogfood Feature (Required)

- [ ] **VAL-13**: `GET /api/reports/2026-05-30/export.md` returns 200 when report exists
- [ ] **VAL-14**: Response has `Content-Type: text/markdown; charset=utf-8`
- [ ] **VAL-15**: Response has `Content-Disposition: attachment; filename="weekly_status_2026-05-30.md"`
- [ ] **VAL-16**: Response body starts with a Markdown heading (`# `)
- [ ] **VAL-17**: Response body contains no `<` characters (no raw HTML)
- [ ] **VAL-18**: `GET /api/reports/{date}/export.md` returns 404 when no report exists for date
- [ ] **VAL-19**: `GET /api/reports/not-a-date/export.md` returns 422 or 400
- [ ] **VAL-20**: `render_status_report_markdown` function exists in `agent/status_report_markdown.py`
- [ ] **VAL-21**: Test count after implementation >= 745
- [ ] **VAL-22**: SDD spec directory exists in Day-to-Day: `spec-driven-development/specs/*/spec.md`
- [ ] **VAL-23**: Two-stage review report filed with zero CRITICAL issues

## Part 2: Dogfood Feature (Stretch -- not required for Done)

- [ ] **VAL-S1**: Download button added to the weekly status report template page
- [ ] **VAL-S2**: `plan.md` and `tasks.md` co-located with the feature spec in the Day-to-Day repo

---

## Definition of Done

All **Required** items (VAL-1 through VAL-23) must be checked.
Stretch items (VAL-S1, VAL-S2) are not required.
