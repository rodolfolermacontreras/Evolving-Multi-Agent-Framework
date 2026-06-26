---
name: pytest-runner
description: "EXAMPLE (Day-to-Day Agent host project). Use when running tests in a host project that uses pytest with the patched_settings + MockLLMClient pattern. NOT a framework default -- treat as a reference implementation showing what a domain skill looks like."
argument-hint: "Which pytest target or failure should I run or diagnose?"
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
> tooling knowledge) but its contents -- the 743-test baseline, `patched_settings`
> fixture, `MockLLMClient`, factory helpers -- are specific to that host project.
>
> Host projects that adopt the framework should either delete this skill or replace
> it with their own `pytest-runner` (or `vitest-runner`, `go-test-runner`, etc.)
> tuned to their actual test setup. See `.github/skills/domain/README.md`.

# Pytest Runner (example)

Day-to-Day Agent pytest knowledge: command patterns, fixtures, mocks, factories, and test file organization. Enforces 743+ test baseline.

## When to Use

Load this skill when:
- Running tests (full suite, single file, or single test)
- Verifying test baseline count
- Working from a worktree (needs special command)
- Debugging test failures

Do NOT load when:
- Just understanding testing conventions (use testing-conventions skill)
- Writing new tests (use tdd skill)

## Test Command Patterns

### Full Suite

```powershell
# Run all tests with verbose output
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# Quick run (just pass/fail counts)
.venv\Scripts\python.exe -m pytest tests/ -q

# With coverage report
.venv\Scripts\python.exe -m pytest tests/ --cov=agent --cov-report=html
```

### Single File

```powershell
# Run one test file
.venv\Scripts\python.exe -m pytest tests/test_accountability.py -v --tb=short

# Run with print output visible
.venv\Scripts\python.exe -m pytest tests/test_accountability.py -v --tb=short -s
```

### Single Test

```powershell
# Run specific test function
.venv\Scripts\python.exe -m pytest tests/test_accountability.py::test_quick_log_creates_entry -v --tb=short

# Run with debug logging
.venv\Scripts\python.exe -m pytest tests/test_accountability.py::test_quick_log_creates_entry -v --tb=short --log-cli-level=DEBUG
```

### Keyword Filter

```powershell
# Run tests matching keyword
.venv\Scripts\python.exe -m pytest tests/ -k "conflict" -v --tb=short

# Run tests NOT matching keyword
.venv\Scripts\python.exe -m pytest tests/ -k "not slow" -v --tb=short
```

### From Worktree

```powershell
# Worktrees don't have .venv - use main repo's Python
cd ..\wt-calendar-sync
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=. -v --tb=short

# If tests need project root context
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=..\Day_to_Day -v --tb=short
```

## Test File Organization

```
tests/
├── conftest.py                 # Fixtures: patched_settings, mock_llm, factories
├── test_accountability.py      # Accountability log tests
├── test_api.py                 # FastAPI endpoint tests
├── test_board.py               # Project board logic tests
├── test_calendar.py            # Calendar sync tests
├── test_database.py            # SQLite/SQLModel tests
├── test_graph_client.py        # Graph API (M365) tests
├── test_ideas.py               # Idea management tests
├── test_llm.py                 # LLM client tests
├── test_models.py              # SQLModel tests
├── test_reminders.py           # Reminder tests
├── test_routes_*.py            # Route module tests
├── test_status_report.py       # Status report workflow tests
├── test_world_state.py         # World state aggregation tests
└── test_workflows.py           # Workflow tests
```

## Key Fixtures (from conftest.py)

### patched_settings

Isolates tests to tmp_path:

```python
def test_my_feature(tmp_path, patched_settings):
    # All paths now point to tmp_path
    # settings.paths.projects -> tmp_path / "projects"
    # settings.paths.inbox -> tmp_path / "inbox"
    # ... etc
    
    # Work in isolation
    result = my_function()
    assert result == expected
```

### mock_llm

Mocks LLM calls:

```python
def test_workflow_with_llm(mock_llm):
    # Set mock response
    mock_llm.default_content = "Generated output"
    
    # Run code that calls LLM
    result = generate_plan("test query")
    
    # Verify
    assert result == "Generated output"
    assert len(mock_llm.call_log) == 1
    assert "test query" in str(mock_llm.call_log[0])
```

### Factory Helpers

Create test data:

```python
def test_with_ideas(tmp_path, patched_settings):
    # Create test ideas
    idea1 = make_idea(title="Test Feature", priority="P1")
    idea2 = make_idea(title="Another", priority="P3")
    
    # Write to file
    write_ideas_file(tmp_path, [idea1, idea2])
    
    # Test code that reads ideas
    ideas = load_ideas()
    assert len(ideas) == 2
```

## Test Baseline

**Current baseline**: 743 tests across 36 files

```powershell
# Check test count
.venv\Scripts\python.exe -m pytest tests/ --collect-only -q | findstr "test session"
# Expected: "743 tests collected"

# Verify baseline never decreases
# Before commit:
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
# All 743 must pass
```

## Common Test Patterns

### Testing API Endpoints

```python
def test_endpoint(client):
    """client fixture provides TestClient for FastAPI app"""
    response = client.post("/api/calendar/sync")
    
    assert response.status_code == 200
    assert response.json()["synced"] >= 0
```

### Testing with Database

```python
def test_with_db(session):
    """session fixture provides SQLAlchemy session"""
    event = CalendarEvent(id="1", title="Test")
    session.add(event)
    session.commit()
    
    retrieved = session.get(CalendarEvent, "1")
    assert retrieved.title == "Test"
```

### Testing File Processing

```python
def test_file_processing(tmp_path, patched_settings):
    # Create test file
    inbox_file = tmp_path / "inbox" / "test.txt"
    inbox_file.parent.mkdir(parents=True)
    inbox_file.write_text("Test content")
    
    # Process
    result = process_file(inbox_file)
    
    # Verify output
    assert (tmp_path / "knowledge" / "processed.md").exists()
```

## Examples

### Example 1: Run Full Suite Before Merge

```powershell
# Verify all tests pass
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# Expected output:
# ==================== test session starts ====================
# ... (test output) ...
# ==================== 743 passed in 45.23s ====================

# If any fail, fix before merging
```

### Example 2: Debug Single Failing Test

```powershell
# Run with full traceback
.venv\Scripts\python.exe -m pytest tests/test_calendar.py::test_sync_endpoint -v --tb=long

# Run with print statements visible
.venv\Scripts\python.exe -m pytest tests/test_calendar.py::test_sync_endpoint -v -s

# Run with debug logging
.venv\Scripts\python.exe -m pytest tests/test_calendar.py::test_sync_endpoint -v --log-cli-level=DEBUG
```

### Example 3: Test from Worktree

```powershell
# Working in feature worktree
cd ..\wt-calendar-sync

# Add new test
# (edit tests/test_calendar.py)

# Run tests using main repo's venv
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=. -v --tb=short

# If passes, commit
git add tests/test_calendar.py agent/routes/calendar.py
git commit -m "feat: add calendar sync endpoint"

# Verify baseline still passes in main repo
cd ..\Day_to_Day
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
# Should now be 744 passed (added 1 test)
```

## Common Mistakes

- Running pytest without `-m` flag - may use wrong Python version
- Not using --tb=short - traceback too verbose
- Forgetting --rootdir when in worktree - imports fail
- Not running full suite before merge - breaks integration
- Adding test but not verifying baseline increases - test may not be discovered
- Using relative paths in tests - breaks when run from different directories
- Not using patched_settings - tests pollute real filesystem
