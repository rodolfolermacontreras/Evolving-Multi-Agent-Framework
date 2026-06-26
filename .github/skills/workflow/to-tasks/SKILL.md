---
name: to-tasks
description: "Use when breaking a plan into atomic, executable tasks. Produces task-list.md with file scope, acceptance tests, effort tags, dependencies, and AFK/HITL classification."
argument-hint: "Which implementation plan should I break into tasks?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# To Tasks

Breaks an implementation plan into atomic tasks using `templates/task-list.md`. Each task gets file scope, acceptance test, effort tag, dependency tag, and AFK/HITL classification.

## When to Use

Load this skill when:
- Plan is complete and reviewed
- Ready to create dispatch packets for workers
- Need atomic units for fleet coordination

Do NOT load when:
- Plan is still incomplete
- Bug fix (goes straight to implement)

## Process

1. **Read the plan** in `specs/YYYY-MM-DD-feature-name/plan.md`

2. **Copy template**: From `spec-driven-development/templates/task-list.md`

3. **For each task in the plan, create task entry**:
   ```markdown
   ## Task {N}: {Title}
   
   **Phase**: {phase number}
   **Effort**: S | M | L
   **Files**: {explicit list}
   **Dependencies**: {task IDs or "None"}
   **Parallel-safe**: Yes | No
   **Classification**: AFK | HITL
   
   ### Description
   {What to build, clear and complete}
   
   ### Acceptance Test
   {Exact test to write and pass}
   
   ### Success Criteria
   - [ ] Test passes
   - [ ] No lint errors
   - [ ] Committed with message: {format}
   ```

4. **Classify each task**:
   - **AFK (Away From Keyboard)**: Can run unattended. Clear spec, no ambiguity, automated verification.
   - **HITL (Human In The Loop)**: Needs human judgment. UX decisions, security review, visual verification.

5. **Verify atomicity**:
   - Task touches ≤ 3 files
   - Effort ≤ 4h (if larger, split it)
   - Single acceptance test
   - Clear definition of done

6. **Check dependencies**:
   - If Task B needs Task A's output: mark "Dependencies: Task A"
   - If tasks touch same files: NOT parallel-safe
   - If tasks are independent: parallel-safe = Yes

7. **Commit task list**:
   ```
   tasks: create task breakdown for {feature-name}
   ```

## Examples

### Example 1: Atomic Task

```markdown
## Task 1: Create CalendarEvent Model

**Phase**: 1
**Effort**: S (< 2h)
**Files**: agent/models.py, agent/database.py
**Dependencies**: None
**Parallel-safe**: Yes
**Classification**: AFK

### Description
Add CalendarEvent SQLModel table with fields: id (TEXT PRIMARY KEY), title, start_time, end_time, attendees, last_synced, source. Add table creation to database.py::create_db_and_tables().

### Acceptance Test
```python
def test_calendar_event_creation(session):
    event = CalendarEvent(
        id="evt_123",
        title="Team Sync",
        start_time=datetime(2026, 5, 21, 10, 0),
        end_time=datetime(2026, 5, 21, 11, 0),
        source="google"
    )
    session.add(event)
    session.commit()
    
    retrieved = session.get(CalendarEvent, "evt_123")
    assert retrieved.title == "Team Sync"
    assert retrieved.source == "google"
```

### Success Criteria
- [ ] test_models.py::test_calendar_event_creation passes
- [ ] No lint errors in agent/models.py
- [ ] Committed: "feat: add CalendarEvent model"
```

### Example 2: HITL Task

```markdown
## Task 7: Design Timeline Widget UI

**Phase**: 3
**Effort**: M (2-4h)
**Files**: templates/pages/dashboard.html, static/css/main.css
**Dependencies**: Task 5 (needs /calendar/sync endpoint)
**Parallel-safe**: Yes (different files from other Phase 3 tasks)
**Classification**: HITL

### Description
Add horizontal timeline widget to dashboard showing calendar events for next 7 days. Events render as colored blocks (green=available, red=busy). Click event to expand details.

### Acceptance Test
Manual verification:
1. Navigate to /dashboard
2. Timeline widget visible below project board
3. Calendar events render as blocks
4. Clicking event shows title, time, attendees
5. Responsive on mobile (timeline scrolls horizontally)

### Success Criteria
- [ ] Visual verification passed
- [ ] No layout regressions on existing dashboard
- [ ] CSS follows main.css conventions (no inline styles)
- [ ] Committed: "feat: add calendar timeline widget to dashboard"
```

### Example 3: Dependent Task

```markdown
## Task 4: Create /calendar/sync Endpoint

**Phase**: 2
**Effort**: M (2-4h)
**Files**: agent/routes/calendar.py, agent/api.py
**Dependencies**: Task 3 (needs GoogleCalendarClient)
**Parallel-safe**: No (depends on Task 3)
**Classification**: AFK

### Description
Create a web-framework POST endpoint /calendar/sync that calls GoogleCalendarClient.fetch_events(), stores results in calendar_events table, and returns count of events synced.

### Acceptance Test
```python
def test_calendar_sync_endpoint(client, mock_google_api):
    mock_google_api.list_events.return_value = [
        {"id": "1", "summary": "Event 1", "start": "2026-05-21T10:00:00"},
        {"id": "2", "summary": "Event 2", "start": "2026-05-21T14:00:00"},
    ]
    
    response = client.post("/calendar/sync")
    
    assert response.status_code == 200
    assert response.json()["synced"] == 2
    
    # Verify stored in DB
    events = session.query(CalendarEvent).all()
    assert len(events) == 2
```

### Success Criteria
- [ ] test_calendar.py::test_calendar_sync_endpoint passes
- [ ] Endpoint registered in agent/api.py
- [ ] Returns proper error codes (401 if not authed, 500 if API fails)
- [ ] Committed: "feat: add /calendar/sync endpoint"
```

## Common Mistakes

- Tasks too large (> 4h) - split them
- Touching > 3 files per task - too much scope
- Missing acceptance test - how do you know it's done?
- Not marking dependencies - leads to blocked workers
- Marking HITL as AFK - visual/UX tasks need human judgment
- Vague descriptions - worker won't know what to build
- Forgetting success criteria - incomplete definition of done
