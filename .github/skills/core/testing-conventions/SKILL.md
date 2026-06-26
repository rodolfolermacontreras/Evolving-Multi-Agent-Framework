---
name: testing-conventions
description: "Use when writing tests, debugging test failures, or setting up test isolation. Enforces pytest patterns: tmp_path, patched_settings, MockLLMClient, factory helpers, and the recorded test baseline."
license: MIT
metadata:
  author: emf-framework
  version: '1.1'
---

# Testing Conventions

Enforces pytest patterns for the host project: tmp_path isolation, patched_settings fixture, MockLLMClient, factory helpers, and the recorded test baseline that must never decrease.

## When to Use

Load this skill when:
- Writing new tests
- Debugging test failures
- Refactoring test utilities
- Setting up test isolation for a new module
- Test count drops below baseline

Do NOT load when:
- Writing production code (unless TDD loop)
- Running tests as verification only

## Process

### Test Isolation Pattern

All tests use `tmp_path`-based isolation. The `patched_settings` fixture monkeypatches `settings.paths` to a temp directory tree so nothing touches real files.

```python
def test_my_feature(tmp_path, patched_settings):
    # patched_settings already set up temp dirs
    # Work in isolated environment
    result = my_function()
    assert result == expected
```

### LLM-Dependent Tests

Use `MockLLMClient` from `conftest.py`. Set `mock_llm.default_content` to control responses. Check `mock_llm.call_log` for assertions.

```python
def test_workflow_with_llm(mock_llm):
    mock_llm.default_content = "Generated plan content"
    
    result = generate_plan(query="test")
    
    assert result == "Generated plan content"
    assert len(mock_llm.call_log) == 1
    assert "test" in mock_llm.call_log[0]["messages"][0]["content"]
```

### Factory Helpers

Use factories from `conftest.py`:
- `make_idea()` - Create test ideas
- `write_ideas_file(tmp_path, ideas)` - Write IDEAS.json
- `write_project_status(tmp_path, content)` - Write PROJECT_STATUS.md

```python
def test_triage(tmp_path, patched_settings):
    idea = make_idea(title="Test Feature", priority="P1")
    write_ideas_file(tmp_path, [idea])
    
    result = triage_ideas()
    assert len(result) == 1
```

### Patching

Patch at the **source module**, not the import site.

```python
# GOOD
@patch("agent.accountability.load_entries")
def test_quick_log(mock_load):
    ...

# BAD - patches the wrong reference
@patch("agent.api.load_entries")
def test_quick_log(mock_load):
    ...
```

### Test Count Baseline

Current baseline: the test count recorded at sprint start. This number must NEVER decrease.

```powershell
# Run full suite - must all pass
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# Check count
.venv\Scripts\python.exe -m pytest tests/ --collect-only -q | findstr "test session"
```

## Examples

### Example 1: Test with File Isolation

```python
def test_process_transcript(tmp_path, patched_settings):
    # Setup in isolated temp dir
    transcript_path = tmp_path / "inbox" / "transcript.txt"
    transcript_path.parent.mkdir(parents=True)
    transcript_path.write_text("Meeting notes here")
    
    # Run function
    result = process_transcript(transcript_path)
    
    # Assert results
    assert result["type"] == "transcript"
    assert (tmp_path / "knowledge" / "meetings").exists()
```

### Example 2: Test LLM Integration

```python
def test_generate_status_report(mock_llm, tmp_path, patched_settings):
    # Configure mock LLM response
    mock_llm.default_content = "# Status Report\n\nAll on track."
    
    # Write test data
    write_project_status(tmp_path, "- Feature X: Complete\n- Feature Y: In progress")
    
    # Run workflow
    report = generate_status_report()
    
    # Verify
    assert "All on track" in report
    assert len(mock_llm.call_log) == 1
    assert "Feature X" in str(mock_llm.call_log[0])
```

### Example 3: Factory Usage

```python
def test_prioritization(tmp_path, patched_settings):
    ideas = [
        make_idea(title="High", priority="P1"),
        make_idea(title="Low", priority="P3"),
    ]
    write_ideas_file(tmp_path, ideas)
    
    sorted_ideas = load_and_sort_ideas()
    
    assert sorted_ideas[0]["title"] == "High"
    assert sorted_ideas[1]["title"] == "Low"
```

## Windows Test Fixtures (LESSON-009)

When tests open SQLite databases inside `tempfile.TemporaryDirectory()`, Windows
will refuse to clean up the temp directory because `sqlite3.Connection` holds the
file handle until garbage collection runs.

### Required pattern for SQLite tests

```python
import gc
import tempfile
import unittest

class TestWithSQLite(unittest.TestCase):
    def setUp(self):
        # ignore_cleanup_errors=True prevents WindowsError on teardown
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp_path = pathlib.Path(self._tmp.name)
        self.db_path = self.tmp_path / "test.db"

    def tearDown(self):
        # Close any open connections first
        if hasattr(self, 'conn'):
            self.conn.close()
        # Force GC to release SQLite file handles before cleanup
        gc.collect()
        self._tmp.cleanup()
```

### Key points

- Always pass `ignore_cleanup_errors=True` to `TemporaryDirectory()`.
- Always call `gc.collect()` in `tearDown` **before** `cleanup()`.
- Close SQLite connections explicitly in `tearDown` -- do not rely on `__del__`.
- This is a Python stdlib behavior on Windows, not a project bug.
- pytest's `tmp_path` fixture handles this automatically; this pattern is for
  `unittest.TestCase` with manual temp dirs.

## Common Mistakes

- Not using `tmp_path` - tests pollute real filesystem
- Forgetting `patched_settings` - tests read/write to actual project dirs
- Patching at import site instead of source - patch doesn't work
- Hardcoding paths - use `tmp_path` or `patched_settings.paths.*`
- Not checking MockLLMClient.call_log - misses verification of what was sent to LLM
- Decreasing test count - adds to technical debt, violates baseline rule
- Not running full suite before commit - breaks integration/improvements build
- Not using `ignore_cleanup_errors=True` on Windows -- tearDown fails with PermissionError (LESSON-009)
