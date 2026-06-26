---
name: tdd
description: "Use when implementing new features or fixing bugs. Enforces test-driven development: write failing test, implement minimal code, pass test, refactor. Never skip the red phase."
argument-hint: "What feature or bug should I implement with TDD?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# TDD

Test-Driven Development loop enforcement: write failing test → implement minimum code → pass → refactor → repeat. Never skip the "failing test first" step.

## When to Use

Load this skill when:
- Implementing new features
- Fixing bugs (write regression test first)
- Refactoring existing code
- Adding new API endpoints or workflows

Do NOT load when:
- Template-only changes (visual verification sufficient)
- Trivial glue code (imports, __init__.py)
- Documentation updates

## Process

### Vertical TDD Loop

```
1. Pick ONE behavior from the task
2. Write ONE failing test
3. Run: ..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_{module}.py -v --tb=short
4. Confirm FAIL (RED phase - test must fail first)
5. Write MINIMAL code to pass
6. Run again, confirm PASS (GREEN phase)
7. Refactor if needed (maintain passing tests)
8. Commit: "test: add {behavior} test" then "feat: implement {behavior}"
9. Repeat for next behavior
```

### Rules

- **Never write more than ONE test before implementing**
- **Never write implementation code without a failing test first**
- **Exceptions**: 
  - Trivial glue code (imports, __init__.py)
  - Template changes verified visually + existing tests passing
  - Model definitions (but write test for create/read/update immediately after)

### Test Structure

```python
def test_{behavior}_when_{condition}_then_{expected}(fixtures):
    """Clear docstring explaining what this tests"""
    # ARRANGE - set up test data
    input_data = make_test_object()
    
    # ACT - execute the behavior
    result = function_under_test(input_data)
    
    # ASSERT - verify expected outcome
    assert result.status == "expected"
    assert result.data == expected_data
```

## Examples

### Example 1: Feature Implementation TDD

```python
# BEHAVIOR: Calendar sync endpoint returns count of synced events

# Step 1: Write failing test
def test_calendar_sync_returns_event_count(client, mock_google_api):
    """Sync endpoint should return count of events synced from Google Calendar"""
    # Arrange
    mock_google_api.list_events.return_value = [
        {"id": "1", "summary": "Event 1"},
        {"id": "2", "summary": "Event 2"},
    ]
    
    # Act
    response = client.post("/calendar/sync")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["synced"] == 2

# Step 2: Run test (expect FAIL)
# ..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_calendar.py::test_calendar_sync_returns_event_count -v --tb=short
# Result: FAILED (endpoint doesn't exist yet)

# Step 3: Write minimal implementation
# agent/routes/calendar.py:
@router.post("/sync")
def sync_calendar():
    client = GoogleCalendarClient()
    events = client.fetch_events()
    for event in events:
        store_event(event)
    return {"synced": len(events)}

# Step 4: Run test again (expect PASS)
# Result: PASSED

# Step 5: Refactor if needed (tests still pass)

# Step 6: Commit
# git commit -m "test: add calendar sync endpoint test"
# git commit -m "feat: implement calendar sync endpoint"
```

### Example 2: Bug Fix TDD

```python
# BUG: Dashboard crashes when project status file is empty

# Step 1: Write regression test (should fail with current code)
def test_board_handles_empty_project_status(tmp_path, patched_settings):
    """Board should gracefully handle empty PROJECT_STATUS.md"""
    # Arrange
    status_file = tmp_path / "projects" / "PROJECT_STATUS.md"
    status_file.parent.mkdir(parents=True)
    status_file.write_text("")  # Empty file
    
    # Act
    board_data = get_board_data()
    
    # Assert
    assert board_data["projects"] == []
    assert board_data["error"] is None  # No crash

# Step 2: Run test (expect FAIL - code crashes on empty file)
# Result: FAILED (AttributeError when parsing empty file)

# Step 3: Fix the bug
# agent/board.py:
def get_board_data():
    content = read_project_status()
    if not content.strip():  # Handle empty file
        return {"projects": [], "error": None}
    # ... rest of parsing ...

# Step 4: Run test again (expect PASS)
# Result: PASSED

# Step 5: Commit
# git commit -m "test: add regression test for empty PROJECT_STATUS.md"
# git commit -m "fix: handle empty PROJECT_STATUS.md gracefully"
```

### Example 3: Refactoring with Test Coverage

```python
# REFACTOR: Extract duplicate error handling into helper function

# Step 1: Ensure existing tests pass
# ..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ -v --tb=short
# Result: baseline tests passed

# Step 2: Write test for new helper (if complex logic)
def test_safe_api_call_handles_timeout():
    """safe_api_call should catch timeout and return error dict"""
    def timeout_func():
        raise requests.Timeout("API timeout")
    
    result = safe_api_call(timeout_func)
    
    assert result["status"] == "error"
    assert "timeout" in result["message"].lower()

# Step 3: Implement helper
# agent/utils.py:
def safe_api_call(func):
    try:
        return func()
    except requests.Timeout:
        return {"status": "error", "message": "API request timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Step 4: Refactor existing code to use helper (tests still pass)

# Step 5: Run ALL tests (must maintain the recorded baseline)
# Result: 744 passed (added 1 test)

# Step 6: Commit
# git commit -m "test: add safe_api_call helper test"
# git commit -m "refactor: extract error handling to safe_api_call"
```

## Common Mistakes

- Writing implementation before test - violates TDD principle
- Writing 5 tests then implementing all at once - lose RED-GREEN feedback
- Skipping RED phase (test passes immediately) - test might not be testing anything
- Not running tests after each change - miss regressions
- Batch committing ("test + feat" in one commit) - lose atomic history
- Testing implementation details instead of behavior - brittle tests
- Not refactoring when tests are green - accumulates tech debt
- Letting test count decrease - violates the baseline rule
