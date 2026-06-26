---
name: fastapi-routes
description: "EXAMPLE (Day-to-Day Agent host project). Use when creating FastAPI routes in a host project that follows the Day-to-Day Agent conventions (APIRouter prefix, Pydantic in schemas.py, safe_path(), esc(), agent/routes/). NOT a framework default -- treat as a reference implementation showing what a domain skill looks like."
argument-hint: "What FastAPI route or endpoint should I work on?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
  status: example
  origin: day-to-day-agent
---

> **STATUS: EXAMPLE SKILL.** This skill was extracted from the Day-to-Day Agent host
> project and ships with the framework as a reference implementation, not as a
> framework default. It demonstrates the shape of a `domain/` skill (project-specific
> framework knowledge) but its contents -- FastAPI, the `safe_path()` and `esc()`
> helpers, the `agent/routes/` layout -- are specific to that host project.
>
> Host projects that adopt the framework should either delete this skill or replace
> it with one tuned to their own web framework. See
> `.github/skills/domain/README.md`.

# FastAPI Routes (example)

Day-to-Day Agent FastAPI conventions: APIRouter with prefix, Pydantic request models, safe_path(), esc() for XSS, route organization.

## When to Use

Load this skill when:
- Creating new API endpoints
- Modifying existing routes
- Understanding route organization
- Adding request validation

Do NOT load when:
- Testing routes (use pytest-runner skill)
- General FastAPI learning (not project-specific)

## Route Organization

```
agent/
├── api.py                      # Main app + legacy routes (dashboard, board, chat, websocket)
├── routes/
│   ├── __init__.py            # Shared helpers: get_engine(), esc(), safe_path()
│   ├── reminders.py           # Reminder CRUD (prefix: /reminders)
│   ├── ideas.py               # Idea management (prefix: /ideas)
│   ├── accountability.py      # Quick-log endpoints (prefix: /accountability)
│   ├── generation.py          # LLM generation (prefix: /generation)
│   └── graph.py               # M365 Graph API (prefix: /graph)
└── schemas.py                  # Pydantic request/response models
```

## Creating a New Route Module

### 1. Define Router

```python
# agent/routes/calendar.py
from fastapi import APIRouter, HTTPException
from agent.routes import get_engine, esc, safe_path
from agent.schemas import CalendarSyncRequest, CalendarSyncResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.post("/sync", response_model=CalendarSyncResponse)
def sync_calendar(request: CalendarSyncRequest):
    """Sync Google Calendar events to local database"""
    engine = get_engine()
    
    try:
        events = engine.calendar_client.fetch_events(days=request.days)
        count = len(events)
        return CalendarSyncResponse(synced=count, events=events)
    except Exception as e:
        logger.error(f"Calendar sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Define Request/Response Models

```python
# agent/schemas.py
from pydantic import BaseModel, Field

class CalendarSyncRequest(BaseModel):
    days: int = Field(default=7, ge=1, le=30, description="Days to sync (1-30)")
    force: bool = Field(default=False, description="Force re-sync even if cached")

class CalendarSyncResponse(BaseModel):
    synced: int = Field(..., description="Number of events synced")
    events: list[dict] = Field(default_factory=list, description="Event summaries")
```

### 3. Register Router

```python
# agent/api.py
from agent.routes import calendar

app = FastAPI(title="Day-to-Day Agent")

# Register routers
app.include_router(calendar.router)
app.include_router(reminders.router)
# ... etc
```

## Shared Helpers (agent/routes/__init__.py)

### get_engine()

Get Engine singleton:

```python
from agent.routes import get_engine

@router.get("/status")
def get_status():
    engine = get_engine()
    return {
        "watcher_running": engine.watcher_running,
        "scheduler_running": engine.scheduler_running,
    }
```

### esc(text)

HTML-escape for XSS prevention:

```python
from agent.routes import esc

@router.post("/note")
def create_note(content: str):
    # ALWAYS escape user content before rendering in templates
    safe_content = esc(content)
    
    return {"message": "Note created", "content": safe_content}
```

### safe_path(base, *parts)

Path traversal protection:

```python
from agent.routes import safe_path
from agent.config import settings

@router.get("/project/{name}")
def get_project(name: str):
    # Prevents path traversal attacks (e.g., name="../../etc/passwd")
    project_path = safe_path(settings.paths.projects, name, "status.md")
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    content = project_path.read_text()
    return {"name": name, "status": content}
```

## Request Validation Patterns

### Query Parameters

```python
from fastapi import Query

@router.get("/events")
def list_events(
    start_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    limit: int = Query(default=10, ge=1, le=100),
):
    """List calendar events in date range"""
    # Pydantic validates:
    # - start_date/end_date format (YYYY-MM-DD)
    # - limit range (1-100)
    ...
```

### Request Body

```python
from pydantic import BaseModel, validator

class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: str = Field(..., regex=r"^P[1-4]$")
    project: str | None = None
    
    @validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

@router.post("/tasks")
def create_task(request: CreateTaskRequest):
    # Pydantic validates all fields before function runs
    # Returns 422 if validation fails
    ...
```

## Error Handling

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.post("/sync")
def sync_data():
    try:
        result = risky_operation()
        return {"status": "success", "result": result}
    
    except ValueError as e:
        # Client error (bad input)
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileNotFoundError as e:
        # Resource not found
        raise HTTPException(status_code=404, detail=f"Resource not found: {e}")
    
    except Exception as e:
        # Server error (log it)
        logger.error(f"Sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## HTMX Response Patterns

```python
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@router.post("/tasks/{id}/toggle", response_class=HTMLResponse)
def toggle_task(id: str, request: Request):
    """HTMX endpoint - returns partial HTML"""
    task = get_task(id)
    task.completed = not task.completed
    save_task(task)
    
    # Return just the updated task row (HTMX swaps it in)
    return templates.TemplateResponse(
        "components/task_row.html",
        {"request": request, "task": task}
    )
```

## Examples

### Example 1: Complete CRUD Route Module

```python
# agent/routes/projects.py
from fastapi import APIRouter, HTTPException, Query
from agent.routes import get_engine, esc, safe_path
from agent.schemas import ProjectCreateRequest, ProjectResponse
from agent.config import settings

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=list[ProjectResponse])
def list_projects(status: str = Query(None, regex=r"^(active|archived|all)$")):
    """List all projects with optional status filter"""
    projects = get_all_projects()
    
    if status and status != "all":
        projects = [p for p in projects if p["status"] == status]
    
    return projects

@router.get("/{name}", response_model=ProjectResponse)
def get_project(name: str):
    """Get single project by name"""
    project_path = safe_path(settings.paths.projects, name, "status.md")
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    
    content = project_path.read_text()
    return ProjectResponse(name=name, status=content)

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(request: ProjectCreateRequest):
    """Create new project"""
    # Validate project doesn't exist
    project_path = safe_path(settings.paths.projects, request.name)
    if project_path.exists():
        raise HTTPException(status_code=409, detail="Project already exists")
    
    # Create directory and status file
    project_path.mkdir(parents=True)
    status_file = project_path / "status.md"
    status_file.write_text(f"# {esc(request.name)}\n\nStatus: Active\n")
    
    return ProjectResponse(name=request.name, status="Active")
```

### Example 2: Request Model with Validation

```python
# agent/schemas.py
from pydantic import BaseModel, Field, validator

class QuickLogRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=500)
    category: str = Field(default="work", regex=r"^(work|learning|blocked|meeting)$")
    
    @validator("text")
    def text_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()
    
    @validator("category")
    def category_lowercase(cls, v):
        return v.lower()

# Route usage
@router.post("/accountability/quick-log")
def quick_log(request: QuickLogRequest):
    # Request is already validated
    # text is trimmed, category is lowercase
    log_entry(request.text, request.category)
    return {"status": "logged"}
```

## Common Mistakes

- Not using APIRouter (defining routes in api.py instead) - loses organization
- Skipping Pydantic models (accepting raw dict) - no validation, 422 errors manual
- Not using safe_path() for user paths - path traversal vulnerability
- Not using esc() for user content - XSS vulnerability
- Returning 500 for client errors - should be 400/404/422
- Not logging server errors - hard to debug production issues
- Forgetting to register router in api.py - route not accessible
- Using synchronous blocking I/O without async - blocks event loop
