---
name: implement
description: "Use when executing a task from the task list. Follows TDD loop, self-review, and commit conventions. Includes stop conditions and escalation triggers."
argument-hint: "Which task from the task list should I implement?"
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
---

# Implement

Implementation workflow for executing atomic tasks. Includes agent brief reading, worktree setup, TDD loop, self-review, and commit. Defines stop conditions and escalation triggers.

## When to Use

Load this skill when:
- Assigned a task from task-list.md
- Ready to implement (spec/plan/tasks complete)
- Working in a feature branch worktree

Do NOT load when:
- Spec not complete (run to-spec first)
- Task too vague (needs clarification)
- Urgent hotfix (skip ceremony, fix and test)

## Process

### 1. Setup

```powershell
# Read agent brief
cat spec-driven-development/sessions/DSP-{date}-{id}.md

# Navigate to worktree
cd ..\wt-{feature-name}

# Verify clean state
git status  # Should be on feature/f{N}.{M}-{name}
```

### 2. TDD Loop

Follow test-first discipline (see tdd skill for details):

```
1. Read task acceptance test
2. Write failing test in tests/test_{module}.py
3. Run: ..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_{module}.py -v --tb=short
4. Confirm RED (test fails)
5. Write MINIMAL code to pass
6. Run again, confirm GREEN (test passes)
7. Refactor if needed (keep tests passing)
8. Repeat for next behavior
```

### 3. Self-Review Checklist

Before committing, check:

- [ ] All task acceptance criteria met
- [ ] All tests pass (including baseline 743)
- [ ] No lint errors
- [ ] Error handling complete (try/except, user-friendly messages)
- [ ] Edge cases handled (null, empty, boundary)
- [ ] Used `safe_path()` for paths, `esc()` for HTML
- [ ] No magic numbers/strings (extract to constants)
- [ ] Naming clear and consistent
- [ ] No orphan code (commented-out blocks, unused imports)
- [ ] Committed in small, logical chunks

### 4. Commit

```powershell
git add {files}
git commit -m "type: short description"

# Valid types: feat, fix, test, refactor, docs, chore
# Example: "feat: add calendar sync endpoint"
```

### 5. Signal Completion

Update task status:
```markdown
## Task {N}: {Title}
**Status**: COMPLETE
**Committed**: {commit SHA}
**Tests**: {test file}::{test function}
```

### Stop Conditions

STOP and escalate if:
- **Ambiguity discovered**: Task spec unclear or contradictory → Flag for grill-me
- **Architecture conflict**: Implementation violates principles.md → Flag for Architect review
- **Tech debt blocker**: Can't implement without refactoring large module → Flag for decision
- **Test failures cascade**: Fixing one test breaks 5 others → Flag for Architect
- **Effort exceeds estimate by 2x**: Task harder than expected → Flag for re-planning

### Escalation Protocol

```markdown
# Escalation: {Task N}

**Blocker**: {what stopped you}
**Attempted**: {what you tried}
**Impact**: {what's affected}
**Recommendation**: {suggested next step}
**Urgency**: IMMEDIATE | HIGH | MEDIUM
```

Post to clarification-log.md or session notes. Wait for resolution.

## Examples

### Example 1: Complete Implementation Flow

```powershell
# 1. Setup
cd ..\wt-calendar-sync
cat ..\Day_to_Day\spec-driven-development\sessions\DSP-2026-05-21-001.md

# 2. TDD - First test
# Write in tests/test_calendar.py:
def test_sync_endpoint_returns_event_count(client, mock_google_api):
    mock_google_api.list_events.return_value = [
        {"id": "1", "summary": "Event 1"},
        {"id": "2", "summary": "Event 2"},
    ]
    response = client.post("/calendar/sync")
    assert response.status_code == 200
    assert response.json()["synced"] == 2

# Run test (RED)
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_calendar.py::test_sync_endpoint_returns_event_count -v --tb=short

# 3. Implement minimal code
# agent/routes/calendar.py:
@router.post("/sync")
def sync_calendar():
    client = GoogleCalendarClient()
    events = client.fetch_events()
    # ... store events ...
    return {"synced": len(events)}

# Run test again (GREEN)
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\test_calendar.py::test_sync_endpoint_returns_event_count -v --tb=short

# 4. Self-review - all checks pass

# 5. Commit
git add agent/routes/calendar.py tests/test_calendar.py
git commit -m "feat: add /calendar/sync endpoint"

# 6. Signal completion
# Update task status in task-list.md
```

### Example 2: Escalation

```markdown
Working on Task 4: "Integrate calendar events into world_state"

Blocker discovered:
world_state.py aggregates from 5 sources. Adding calendar requires refactoring the entire aggregation pattern to support async data sources (Google API is async).

# Escalation: Task 4

**Blocker**: world_state.py is synchronous, calendar API is async
**Attempted**: Tried to wrap in asyncio.run(), but breaks existing callers
**Impact**: Can't add calendar to world_state without refactoring all 5 sources
**Recommendation**: 
1. Create separate async_world_state() function, OR
2. Make calendar sync a background job, store results in DB, read synchronously

**Urgency**: HIGH (blocks calendar feature)

Stopping work. Awaiting architectural decision.
```

## Common Mistakes

- Skipping test-first (writing code before test) - violates TDD
- Committing large chunks instead of small increments - hard to review
- Not self-reviewing before commit - catches issues late
- Ignoring stop conditions - pushes through blockers instead of escalating
- Not updating task status - team doesn't know it's done
- Continuing when stuck > 30min - ask for help sooner
- Forgetting to run baseline tests - breaks integration/improvements
