---
name: handoff
description: "Use before ending any session with incomplete work. Updates CONTEXT.md, BOARD.md, rebuilds exec/state.md, writes handoff note with what was done, what's next, and blockers."
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
---

# Handoff

Session handoff protocol: update CONTEXT.md, update BOARD.md, rebuild exec/state.md, write handoff note. Ensures continuity when work is incomplete.

## When to Use

Load this skill when:
- Ending session with incomplete work
- Switching between features mid-sprint
- Handing off to another agent or human
- At end of day with work in progress

Do NOT load when:
- Feature completely done and merged
- Quick fix committed and verified

## Process

### 1. Answer Five Questions

```markdown
## Handoff: {Feature Name} - {Date}

### 1. What was the GOAL?
{Original task or feature objective}

### 2. What was COMPLETED?
- [x] Task 1.1: {description}
- [x] Task 1.2: {description}
- [ ] Task 1.3: {IN PROGRESS - 60% done}

### 3. What is REMAINING?
- [ ] Task 1.3: Finish {specific next step}
- [ ] Task 2.1: {description}
- [ ] Code review (Stage 1)

### 4. What is the NEXT ACTION?
**Exact command or file to open**:
```powershell
cd ..\wt-calendar-sync
# Open: agent/routes/calendar.py line 45
# Implement: Error handling for API timeout
# Test: test_calendar.py::test_api_timeout_handling
```

### 5. Any CONTEXT that would be lost?
- Design decision: Chose one-way sync over two-way (see clarification-log.md Q3)
- Blocker: Google API rate limit hit during testing (need production quota)
- Known issue: Events with null start_time crash parser (needs edge case handling)
- Tech debt: Hardcoded 7-day lookahead (should be configurable)
```

### 2. Update CONTEXT.md

Add dated section with key decisions:

```markdown
## 2026-05-22: Calendar Sync Development

**Decision**: One-way sync only (read calendar, don't write back)
**Reason**: Simpler, lower risk, faster to ship
**Impact**: Defers two-way sync to v2

**Decision**: 7-day lookahead window
**Reason**: Balance between usefulness and API quota
**Impact**: Historical events not synced

**Tech Debt**: Hardcoded lookahead should be user-configurable
```

### 3. Update BOARD.md

Update sprint board with current state:

```markdown
# Sprint Board - PI-1 / Sprint-1

## In Progress
- **Calendar Sync** (60% - agent/routes/calendar.py)
  - Blocked: Google API quota (production key needed)
  - Next: Error handling for timeouts

## Completed This Session
- [x] CalendarEvent model created
- [x] GoogleCalendarClient implemented
- [x] /calendar/sync endpoint (90% done)

## Blocked
- Calendar Sync: Need production Google API key (L1 approval)
```

### 4. Rebuild exec/state.md

Run state builder CLI:

```powershell
python spec-driven-development\cli\state_builder.py

# Outputs:
# - Updated: spec-driven-development/exec/state.md
# - Archived: spec-driven-development/exec/briefings/2026-05-22.md
```

Verify state.md reflects:
- Active sprint progress
- Blocked items
- Recent completions

### 5. Commit Handoff Note

```powershell
git add spec-driven-development/CONTEXT.md
git add spec-driven-development/sprints/PI-1/sprint-1/BOARD.md
git commit -m "docs: session handoff for calendar-sync (60% complete)"
```

## Examples

### Example 1: Feature In Progress

```markdown
## Handoff: Calendar Sync - 2026-05-22 17:30

### 1. GOAL
Implement calendar sync integration (specs/2026-05-21-calendar-sync/)
Enable users to view Google Calendar events in dashboard timeline

### 2. COMPLETED
- [x] Task 1.1: CalendarEvent model (committed SHA: a3f2b1)
- [x] Task 1.2: GoogleCalendarClient OAuth flow (committed SHA: b4c5d6)
- [x] Task 2.1: /calendar/sync endpoint (90% - needs error handling)

### 3. REMAINING
- [ ] Task 2.1: Finish error handling (API timeout, network failure)
- [ ] Task 2.2: Add calendar data to world_state.py
- [ ] Task 3.1: Timeline widget UI
- [ ] Code review (both stages)
- [ ] Integration test

### 4. NEXT ACTION
```powershell
cd ..\wt-calendar-sync
# Open: agent/routes/calendar.py line 58
# Add try/except around client.fetch_events()
# Test case: test_calendar.py::test_sync_handles_api_timeout (already written, fails)
# Expected: 2h to complete
```

### 5. CONTEXT
**Blocker**: Hit Google API rate limit during dev testing. Need production quota.
  - Action required: Request L1 approval for production API key
  - Impact: Can't test end-to-end without prod credentials

**Design decision**: One-way sync confirmed (see clarification-log.md Q1)

**Known edge case**: Events with null start_time crash parser
  - Workaround: Skip events with null time
  - Proper fix: Validate in GoogleCalendarClient.parse_event()

**Tech debt**: 7-day lookahead hardcoded
  - Should be user preference in settings
  - Deferred to v2
```

### Example 2: Blocked on Dependency

```markdown
## Handoff: Task Filters - 2026-05-22 14:00

### 1. GOAL
Add filter UI to task board (priority, status, project)

### 2. COMPLETED
- [x] Task 1.1: Filter API endpoints (committed SHA: e7f8g9)
- [ ] Task 2.1: Filter UI dropdowns (BLOCKED)

### 3. REMAINING
- [ ] Task 2.1: Filter UI (blocked on design approval)
- [ ] Task 2.2: Wire filters to API
- [ ] Manual testing

### 4. NEXT ACTION
WAITING FOR: UX Designer to finalize filter placement mockup
Expected: Tomorrow AM

Once unblocked:
```powershell
cd ..\wt-task-filters
# Open: templates/pages/board.html line 23
# Add filter dropdown HTML per approved mockup
```

### 5. CONTEXT
**Blocker**: UX Designer reviewing filter placement
  - Two options: (A) sidebar, (B) top bar
  - Waiting for design decision before implementing UI

**Completed while waiting**: Implemented API logic so UI can be quick drop-in
```

## Common Mistakes

- Not answering all 5 questions - incomplete handoff
- Vague "next action" - should be exact command/file
- Forgetting to update CONTEXT.md - loses decisions
- Not rebuilding exec/state.md - Executive sees stale state
- Committing without handoff note - team doesn't know status
- Not documenting blockers - next session wastes time rediscovering
- Writing essay instead of bullet points - too verbose
