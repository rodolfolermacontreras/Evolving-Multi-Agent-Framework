# Technology Stack

## Runtime

- Python 3.12+ (required)
- Virtual environment: `.venv` (mandatory -- never use global Python)
- Primary OS: Windows (development), Linux (Docker container)

## Web Framework

- FastAPI (ASGI, async support)
- HTMX + Jinja2 for frontend (server-rendered, no SPA framework)
- Alpine.js for lightweight client-side interactivity
- Static assets in `static/` -- all styles in `static/css/main.css`
- Templates in `templates/` -- `base.html` is the shell, pages in `templates/pages/`
- Dark theme uses `--accent-*` CSS variables (not `--success`/`--error`/`--warning`)

## Database

- SQLite with WAL mode (`agent/daytoday.db`)
- SQLModel (SQLAlchemy wrapper) for ORM -- tables defined in `agent/models.py`
- `get_session()` is the FastAPI dependency for DB access
- Legacy: JSON dotfiles in `agent/` -- migration to SQLite is ongoing (tech debt D1)

## Authentication

- MSAL (Microsoft Authentication Library) for M365 integration
- Single-user passthrough auth (`agent/auth.py`) -- no multi-tenant

## LLM Integration

- OpenAI-compatible API (`agent/llm.py`) -- all LLM calls go through this layer
- Primary endpoint: `models.inference.ai.azure.com` (GitHub Models: GPT-4o, DeepSeek, etc.)
- Fallback endpoint: `api.githubcopilot.com` (Claude, Gemini, GPT-5.x via Copilot Chat)
- Token resolved from `GITHUB_TOKEN` env var or `gh auth token` CLI
- Reasoning models (o3/o4-mini) auto-switch to `max_completion_tokens`, strip system messages
- Retry with exponential backoff; per-call observability via `record_llm_call`

## Scheduling

- APScheduler for in-process scheduling
- Windows Task Scheduler for system-level jobs (`--install-scheduler`)

## Testing

- pytest with `tmp_path`-based isolation
- `patched_settings` fixture (in `conftest.py`) monkeypatches `settings.paths` to temp dir
- `MockLLMClient` for LLM-dependent tests (set `default_content`, assert on `call_log`)
- Factory helpers: `make_idea()`, `write_ideas_file()`, `write_project_status()`
- Patch at the source module, not the import site
- Current baseline: 743 tests, 36 files, ~75s runtime -- count must never decrease

## Deployment

- Docker (Dockerfile + `docker-compose.yml`)
- `DATA_ROOT=/data` redirects user data to mounted volume, app code stays at `/app`
- Port 8000 (dashboard)

## Key Module Map

| Module | Responsibility |
|--------|---------------|
| `agent/engine.py` | Lazy singleton orchestrator -- watcher, scheduler, WebSocket broadcast |
| `agent/api.py` + `agent/routes/` | FastAPI app + 5 router modules (reminders, ideas, accountability, generation, graph) |
| `agent/llm.py` | Dual-endpoint LLM client with observability |
| `agent/config.py` | Frozen dataclasses composed into `settings` object |
| `agent/world_state.py` | Aggregates all data sources for LLM context |
| `agent/board.py` | Project board aggregation -- `MAIN_PROJECTS` controls visibility |
| `agent/status_report.py` + `agent/status_report_renderer.py` | Bi-weekly HTML report pipeline |
| `agent/workflows/` | Self-contained workflow modules (weekly_plan, transcript, digest, etc.) |
| `agent/prompts/templates.py` | All LLM prompt templates |
| `agent/schemas.py` | Pydantic request models for all POST endpoints |

## Approval-Required Changes

The following require human approval (Level 2 decision) before implementation begins:

- New pip dependency
- Schema migration
- M365 permission scope change
- New external API integration
- Any change to `agent/models.py` table structure

## ADR Location

`spec-driven-development/docs/ADR/`
