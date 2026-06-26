---
name: to-plan
description: "Use when transforming a completed spec into an implementation plan. Decomposes into phases, identifies dependencies, estimates effort (S/M/L), and flags parallel-safe tasks."
argument-hint: "Which completed spec should I turn into a plan?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# To Plan

Transforms a completed specification into an implementation plan using `templates/plan.md`. Decomposes work into phases, identifies dependencies, estimates effort, and flags tasks that can run in parallel.

## When to Use

Load this skill when:
- Spec is complete and reviewed
- Ready to move from spec.md to plan.md
- Need to break down work for sprint planning

Do NOT load when:
- Spec is still incomplete (run grill-me or to-spec first)
- Bug fix (simple fixes don't need a plan)

## Process

1. **Read the spec** in `specs/YYYY-MM-DD-feature-name/spec.md`

2. **Copy template**: From `spec-driven-development/templates/plan.md`

3. **Decompose into phases**:
   - **Phase 1**: Foundation (data model, core logic)
   - **Phase 2**: Integration (API routes, LLM workflows)
   - **Phase 3**: UI/UX (templates, frontend)
   - **Phase 4**: Polish (error handling, edge cases, docs)

4. **For each phase, list tasks**:
   ```markdown
   ### Phase 1: Foundation
   
   - [ ] Task 1.1: Create CalendarEvent model in models.py
     - **Effort**: S (< 2h)
     - **Files**: agent/models.py, agent/database.py
     - **Dependencies**: None
     - **Parallel-safe**: Yes
     - **Test**: test_models.py::test_calendar_event_creation
   
   - [ ] Task 1.2: Implement Google Calendar API client
     - **Effort**: M (2-4h)
     - **Files**: agent/calendar_client.py
     - **Dependencies**: Task 1.1 (needs model)
     - **Parallel-safe**: No (depends on 1.1)
     - **Test**: test_calendar_client.py::test_fetch_events
   ```

5. **Identify dependencies**:
   - Tasks with no dependencies can start immediately
   - Dependent tasks must wait for prerequisite completion
   - Flag with "Dependencies: Task X.Y"

6. **Estimate effort**:
   - **S (Small)**: < 2h, 1-2 files, < 100 LoC
   - **M (Medium)**: 2-4h, 2-4 files, 100-300 LoC
   - **L (Large)**: > 4h, > 4 files, > 300 LoC (consider splitting)

7. **Flag parallel-safe tasks**:
   - **Yes**: No shared state, no dependencies, can run in separate worktrees
   - **No**: Depends on other tasks or modifies same files

8. **Add verification gates**:
   ```markdown
   ## Verification

   After Phase 1:
   - [ ] All models create/migrate successfully
   - [ ] Test suite passes (recorded baseline)
   - [ ] No new lint errors

   After Phase 2:
   - [ ] API endpoints return 200 with valid data
   - [ ] OAuth flow completes without errors
   - [ ] Integration tests pass

   After Phase 4:
   - [ ] Full feature workflow verified end-to-end
   - [ ] All FR-NNN requirements met
   - [ ] Code review passed
   ```

9. **Commit plan**:
   ```
   plan: add implementation plan for {feature-name}
   ```

## Examples

### Example 1: Calendar Sync Implementation Plan

```markdown
# Implementation Plan: Calendar Sync

**Spec**: specs/2026-05-21-calendar-sync/spec.md
**Est. Total**: 3-5 days (1 developer)

## Phase 1: Foundation (Day 1)

- [ ] 1.1: Create CalendarEvent model
  - Effort: S
  - Files: agent/models.py, agent/database.py
  - Dependencies: None
  - Parallel-safe: Yes
  - Test: test_models.py::test_calendar_event_model

- [ ] 1.2: Add calendar_events table migration
  - Effort: S
  - Files: agent/database.py
  - Dependencies: 1.1
  - Parallel-safe: No
  - Test: Manual (check DB schema)

## Phase 2: Integration (Day 2-3)

- [ ] 2.1: Implement GoogleCalendarClient
  - Effort: M
  - Files: agent/calendar_client.py
  - Dependencies: 1.1
  - Parallel-safe: Yes
  - Test: test_calendar_client.py::test_oauth_flow, test_fetch_events

- [ ] 2.2: Create /calendar/sync API endpoint
  - Effort: M
  - Files: agent/routes/calendar.py
  - Dependencies: 2.1
  - Parallel-safe: No
  - Test: test_calendar.py::test_sync_endpoint

- [ ] 2.3: Add calendar data to world_state
  - Effort: S
  - Files: agent/world_state.py
  - Dependencies: 2.2
  - Parallel-safe: Yes (different module)
  - Test: test_world_state.py::test_calendar_included

## Phase 3: UI/UX (Day 4)

- [ ] 3.1: Add timeline widget to dashboard
  - Effort: M
  - Files: templates/pages/dashboard.html, static/css/main.css
  - Dependencies: 2.2
  - Parallel-safe: Yes
  - Test: Manual (visual verification)

- [ ] 3.2: Add "Create Task" button to events
  - Effort: S
  - Files: templates/pages/dashboard.html
  - Dependencies: 3.1
  - Parallel-safe: No
  - Test: test_calendar.py::test_task_creation

## Phase 4: Polish (Day 5)

- [ ] 4.1: Error handling for API failures
  - Effort: S
  - Files: agent/calendar_client.py, agent/routes/calendar.py
  - Dependencies: 2.1, 2.2
  - Parallel-safe: No
  - Test: test_calendar_client.py::test_api_error_handling

- [ ] 4.2: Add loading states to UI
  - Effort: S
  - Files: templates/pages/dashboard.html
  - Dependencies: 3.1
  - Parallel-safe: Yes
  - Test: Manual

## Verification

After Phase 1:
- [ ] calendar_events table exists in DB
- [ ] Test suite passes (recorded baseline)

After Phase 2:
- [ ] /calendar/sync returns 200 with events
- [ ] OAuth consent flow completes
- [ ] Integration tests pass

After Phase 4:
- [ ] Full sync workflow verified
- [ ] All FR-001 through FR-004 met
- [ ] Code review passed
```

## Common Mistakes

- Not breaking down large tasks - keep tasks under 4h
- Missing dependencies - leads to blocked workers
- Not flagging parallel-safe tasks - misses parallelization opportunities
- Skipping effort estimates - can't plan sprint capacity
- No verification gates - can't tell when phase is done
- Forgetting test strategy per task - leads to untested code
