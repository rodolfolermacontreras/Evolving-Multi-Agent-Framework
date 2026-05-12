# Roadmap

This file tracks the high-level product trajectory. Sprint-level details live in
`sprints/PI-{N}/CURRENT_PI.md`. Tech debt details live in backlog items.

---

## Completed (as of 2026-05-20)

### Core Infrastructure
- [x] FastAPI server with HTMX + Jinja2 frontend (server-rendered, no SPA)
- [x] Engine singleton with file watcher, scheduler, git auto-commit, WebSocket broadcast
- [x] Dual-endpoint LLM client (GitHub Models + Copilot Chat fallback)
- [x] Frozen config dataclasses with `settings` singleton
- [x] SQLite/SQLModel database (WAL mode) -- `agent/daytoday.db`
- [x] Docker deployment with volume-mounted user data

### Features
- [x] Project board with `MAIN_PROJECTS` aggregation
- [x] Accountability log with quick-entry and history view
- [x] Bi-weekly HTML status report pipeline (collector + narrator + renderer)
- [x] Interactive report with week navigation, tabs, animations
- [x] Outlook-safe email HTML companion report
- [x] Microsoft Graph / M365 integration (calendar, tasks) via MSAL
- [x] Inbox file watcher with SHA256 dedup and workflow dispatch
- [x] Reminders module (routes + UI)
- [x] Ideas capture and management (routes + UI)
- [x] Meeting transcript summarization workflow
- [x] Weekly plan generation workflow
- [x] Daily digest workflow
- [x] Monthly showcase workflow
- [x] Test suite: 743 tests, 36 files, ~75s runtime

---

## PI-1: Foundation + SDD Bootstrap (10-week symbolic cadence; wall-clock compressed by AI fleet)

- [ ] SDD framework scaffolded and validated with a pilot feature
- [ ] Constitution and core skills operational
- [ ] First feature through the full SDD lifecycle (idea -> spec -> plan -> tasks -> done)
- [ ] Fleet pilot with batch size of 2

---

## PI-2: Core Features + Fleet Maturity

- [ ] 3-5 features delivered through the SDD pipeline
- [ ] Fleet batch size increased to 3-4
- [ ] Specialization mechanic validated (generic worker earns permanent identity)
- [ ] GENERALIZATION_SDD.md v1.0 published

---

## PI-3: Polish + Generalization

- [ ] SDD process metrics baseline established
- [ ] CLI automation Phase 2 (fleet.py, qa.py, retro.py operational)
- [ ] Second-project bootstrap test (validate portability)
- [ ] Optional: SDD dashboard page in the app

---

## Tech Debt Backlog

These items are tracked and prioritized but not yet scheduled for a sprint.

| ID | Description | Effort | Priority |
|----|-------------|--------|----------|
| D1 | JSON-to-SQLite migration -- all dotfile stores to SQLModel tables | XL | P2 |
| D7 | Status report renderer split -- separate CSS from logic in `status_report_renderer.py` | M | P3 |
| D9 | Route consolidation -- `MAIN_PROJECTS` defined in both `board.py` and `api.py` | S | P3 |
| D10 | Pagination -- all list endpoints need cursor-based pagination | M | P2 |
| D4 | Exception tightening -- bare `except` blocks to typed exceptions | S | P3 |

Full backlog with RICE scores: `backlog/BACKLOG.md`
