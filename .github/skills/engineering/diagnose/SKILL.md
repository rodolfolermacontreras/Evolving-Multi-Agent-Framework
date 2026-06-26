---
name: diagnose
description: "Use when debugging failures or unexpected behavior. Workflow: reproduce → isolate → root cause → fix → regression test. Uses gitnexus for codebase exploration and world_state.py for data flow issues."
argument-hint: "What failure, error, or unexpected behavior should I diagnose?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Diagnose

Bug diagnosis workflow: reproduce → isolate → root cause → fix → regression test. Leverages gitnexus for code exploration and world_state.py for data flow issues.

## When to Use

Load this skill when:
- Test failures
- Unexpected behavior or errors
- Performance degradation
- Data inconsistencies
- User-reported bugs

Do NOT load when:
- Feature request (not a bug)
- Expected behavior clarification needed (use grill-me)

## Process

### 1. Reproduce

```powershell
# Get exact steps to trigger bug
# Run failing test or manual workflow

# Example: Failing test
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_calendar.py::test_sync_endpoint -v --tb=short

# Example: Manual repro
1. Navigate to /dashboard
2. Click "Sync Calendar"
3. Error: 500 Internal Server Error
```

### 2. Isolate

Narrow down the problem:

**Code-level isolation:**
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoints or print statements
def sync_calendar():
    print(f"DEBUG: Fetching events...")
    events = client.fetch_events()
    print(f"DEBUG: Got {len(events)} events")
    # ...
```

**Module-level isolation:**
```powershell
# Use gitnexus to trace code flow
gitnexus trace sync_calendar --depth 3

# Find which module fails
# - Does API client fail?
# - Does database write fail?
# - Does response serialization fail?
```

**Data-level isolation:**
```python
# Check world_state.py for data flow issues
from agent.world_state import get_world_state

state = get_world_state()
print(state.keys())  # Are all expected sources present?

# Check intermediate data
events = client.fetch_events()
print(events)  # Is data shaped as expected?
```

### 3. Root Cause

Ask: WHY did it fail?

**Common root causes:**
- **Null/empty data**: Missing validation
- **Type mismatch**: Expected dict, got list
- **API change**: External dependency changed response format
- **State corruption**: Database or file system out of sync
- **Race condition**: Async operations not synchronized
- **Config missing**: ENV var or setting not set

**Investigation tools:**
```powershell
# Check logs
cat logs\agent.log | findstr ERROR

# Check database state
sqlite3 agent\daytoday.db "SELECT * FROM calendar_events LIMIT 5"

# Check file state
cat projects\PROJECT_STATUS.md

# Check gitnexus for recent changes
gitnexus history sync_calendar --since 7d
```

### 4. Fix

Write fix **with regression test first** (TDD for bugs):

```python
# 1. Write test that fails with current code
def test_sync_handles_empty_response():
    """Sync should handle empty event list without crashing"""
    mock_api.list_events.return_value = []  # Empty list
    
    response = client.post("/calendar/sync")
    
    assert response.status_code == 200
    assert response.json()["synced"] == 0

# 2. Run test (expect FAIL)

# 3. Fix the bug
def sync_calendar():
    events = client.fetch_events()
    if not events:  # Handle empty case
        return {"synced": 0}
    # ... rest of logic ...

# 4. Run test (expect PASS)
```

### 5. Regression Test

```powershell
# Run full test suite to ensure fix doesn't break anything
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ -v --tb=short

# Baseline must not decrease
```

## Examples

### Example 1: Null Pointer Bug

```python
# BUG: Dashboard crashes when PROJECT_STATUS.md doesn't exist

# 1. Reproduce
# Navigate to /dashboard -> 500 error

# 2. Isolate
# Logs show: FileNotFoundError in board.py::get_board_data()
# Line 42: content = status_file.read_text()

# 3. Root Cause
# PROJECT_STATUS.md expected but doesn't exist (new install)

# 4. Fix (test-first)
def test_board_handles_missing_status_file(tmp_path, patched_settings):
    # Arrange: no PROJECT_STATUS.md
    # Act
    board = get_board_data()
    # Assert
    assert board["projects"] == []
    assert "error" not in board

# Fix in agent/board.py:
def get_board_data():
    status_file = settings.paths.projects / "PROJECT_STATUS.md"
    if not status_file.exists():
        return {"projects": [], "last_update": None}
    content = status_file.read_text()
    # ...

# 5. Regression test
# All tests pass (744 now)
```

### Example 2: Data Flow Issue

```python
# BUG: Calendar events not appearing in world_state

# 1. Reproduce
from agent.world_state import get_world_state
state = get_world_state()
print("calendar" in state)  # False (should be True)

# 2. Isolate
# Check: are events in database?
# Yes, calendar_events table has 5 rows

# Check: is world_state reading them?
# Look at agent/world_state.py line 82
# BUG FOUND: calendar events collector is commented out!

# 3. Root Cause
# Previous refactor commented out calendar data source by mistake

# 4. Fix
def get_world_state():
    state = {
        "projects": get_projects(),
        "meetings": get_meetings(),
        # "calendar": get_calendar_events(),  # BUG: commented out
    }
    
# Fix:
def get_world_state():
    state = {
        "projects": get_projects(),
        "meetings": get_meetings(),
        "calendar": get_calendar_events(),  # Uncomment
    }

# 5. Test
def test_world_state_includes_calendar(session):
    # Add calendar event to DB
    event = CalendarEvent(id="1", title="Test", ...)
    session.add(event)
    session.commit()
    
    state = get_world_state()
    
    assert "calendar" in state
    assert len(state["calendar"]) == 1
```

### Example 3: Performance Issue

```python
# BUG: /dashboard loads slowly (5+ seconds)

# 1. Reproduce
# Measure: curl http://localhost:8000/dashboard -w "%{time_total}\n"
# Result: 5.2 seconds

# 2. Isolate
# Add timing logs:
import time

@app.get("/dashboard")
def dashboard():
    start = time.time()
    
    board = get_board_data()
    print(f"Board: {time.time() - start:.2f}s")
    
    meetings = get_meetings()
    print(f"Meetings: {time.time() - start:.2f}s")
    
    ideas = get_ideas()
    print(f"Ideas: {time.time() - start:.2f}s")  # 4.8s! Problem here.

# 3. Root Cause
# get_ideas() calls LLM to classify each idea (10 ideas = 10 LLM calls)

# 4. Fix
# Cache classifications or batch them
def get_ideas():
    ideas = load_ideas()
    if not needs_classification(ideas):
        return ideas  # Use cached
    # ... classify ...

# 5. Measure again
# Result: 0.3 seconds (16x faster)
```

## Common Mistakes

- Not reproducing first - can't fix what you can't see
- Guessing root cause instead of investigating - leads to wrong fix
- Fixing without regression test - bug comes back later
- Not checking full test suite after fix - breaks something else
- Fixing symptoms instead of root cause - problem reappears differently
- Not using gitnexus for code exploration - wastes time manual searching
- Ignoring world_state.py for data flow bugs - misses obvious issues
