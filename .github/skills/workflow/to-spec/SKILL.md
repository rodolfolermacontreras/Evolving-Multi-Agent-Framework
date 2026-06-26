---
name: to-spec
description: "Use when transforming a raw feature idea into a structured specification. Produces a complete spec.md with problem statement, acceptance criteria, affected modules, data model changes, and traceability matrix."
argument-hint: "What raw feature idea should I turn into a spec?"
license: MIT
metadata:
  author: emf-framework
  version: '1.1'
---

# To Spec

Transforms a feature idea into a structured specification using the `templates/feature-spec.md` template. Includes problem statement, acceptance criteria, affected modules, data model changes, test strategy, and traceability matrix.

## When to Use

Load this skill when:
- Feature idea has passed triage (P1/P2 priority assigned)
- Scope is clear enough to specify (after grill-me if needed)
- Ready to move from IDEAS.md to specs/YYYY-MM-DD-feature-name/

Do NOT load when:
- Idea still in triage (use triage skill first)
- Scope is too ambiguous (run grill-me first)
- Bug fix < 3 files (skip spec, go straight to fix)

## Process

1. **Create spec directory**: `spec-driven-development/specs/YYYY-MM-DD-feature-name/`

2. **Copy template**: From `spec-driven-development/templates/feature-spec.md`

3. **Fill sections**:

   **Problem Statement**:
   - What problem does this solve?
   - Who experiences this problem?
   - What's the impact if we don't solve it?

   **Acceptance Criteria** (format: FR-NNN):
   ```markdown
   - FR-001 (MUST): System SHALL do X
   - FR-002 (MUST): When Y happens, system SHALL respond with Z
   - FR-003 (SHOULD): User CAN perform action A
   - FR-004 (MAY): Optional enhancement B
   ```

   **Affected Modules**:
   - List all files/modules that will change
   - Mark as NEW, MODIFY, or DELETE
   - Estimate LoC change (+50, +200, etc.)

   **Data Model Changes**:
   - New tables/columns in SQLite
   - Changes to JSON schemas
   - Migration strategy if breaking change

   **Test Strategy**:
   - What gets unit tested?
   - What needs integration testing?
   - What requires manual verification?

   **Traceability Matrix**:
   ```markdown
   | Requirement | Affected Module | Test Coverage |
   |-------------|-----------------|---------------|
   | FR-001 | agent/api.py | test_api.py::test_fr001 |
   | FR-002 | agent/routes/calendar.py | test_calendar.py::test_sync |
   ```

   **Out of Scope**:
   - Explicitly list what this spec does NOT include
   - Prevents scope creep during implementation

4. **Review against constitution**:
   - Load sdd-constitution skill
   - Verify alignment with mission, tech stack, principles

5. **Commit spec**:
   ```
   spec: add {feature-name} specification
   ```

6. **Update BACKLOG.md**:
   - Move idea from TRIAGED to SPECCED
   - Link to spec directory

## Examples

### Example 1: Calendar Sync Feature Spec

```markdown
# Calendar Sync Feature Specification

**Date**: 2026-05-21
**Priority**: P1
**Effort**: Medium (3-5 days)

## Problem Statement
Users manually copy calendar events into tasks. Time-consuming, error-prone, leads to missed deadlines.

## Acceptance Criteria

- FR-001 (MUST): System SHALL fetch user's Google Calendar events for next 7 days
- FR-002 (MUST): System SHALL display calendar events on dashboard timeline
- FR-003 (MUST): When calendar event overlaps work hours, system SHALL mark time as unavailable
- FR-004 (SHOULD): User CAN manually create task from calendar event with one click
- FR-005 (MAY): System MAY suggest optimal task scheduling around calendar blocks

## Affected Modules

- NEW: agent/routes/calendar.py (+150 LoC)
- NEW: agent/calendar_client.py (+200 LoC)
- MODIFY: agent/models.py (+30 LoC - CalendarEvent model)
- MODIFY: templates/pages/dashboard.html (+50 LoC - timeline widget)
- MODIFY: agent/database.py (+10 LoC - table creation)

## Data Model Changes

New table: `calendar_events`
```sql
CREATE TABLE calendar_events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    attendees TEXT,
    last_synced TIMESTAMP,
    source TEXT DEFAULT 'google'
);
```

No breaking changes. Additive only.

## Test Strategy

- Unit: calendar_client.py OAuth flow, event parsing
- Unit: routes/calendar.py endpoint logic
- Integration: Full sync workflow with mocked Google API
- Manual: OAuth consent flow, UI timeline rendering

## Traceability Matrix

| Requirement | Module | Test |
|-------------|--------|------|
| FR-001 | calendar_client.py | test_calendar_client.py::test_fetch_events |
| FR-002 | templates/pages/dashboard.html | Manual verification |
| FR-003 | agent/scheduler.py | test_scheduler.py::test_unavailable_blocks |
| FR-004 | agent/routes/calendar.py | test_calendar.py::test_create_task_from_event |

## Out of Scope

- Two-way sync (write back to calendar) - deferred to v2
- Support for Outlook/other calendars - Google only for now
- Historical event sync (>7 days past) - future only
```

## Canonical File Declaration (LESSON-008)

When creating a new spec, check whether any **open** spec already targets the same implementation file(s).

### Detection

Before filling the "Affected Modules" section, run:
```
grep -rl "<target-filename>" spec-driven-development/specs/*/spec.md
```

If matches are found in open (non-DONE) spec directories:

### Resolution

1. **Declare one spec as canonical** for the shared file's primary contract.
2. **Declare the other spec as additive** -- it extends or modifies behavior but does not own the file's core contract.
3. Document this in both specs' "Affected Modules" sections:
   ```markdown
   - MODIFY: cli/state_builder.py (+80 LoC)
     - **Canonical spec:** specs/2026-05-16-state-dashboard/
     - **This spec adds:** build-index subcommand (additive scope)
   ```
4. Cross-reference both specs' validation contracts from the implementation file's header docstring.

### Why this matters

Without a canonical declaration, two parallel specs may write conflicting acceptance criteria for the same file, leading to validation deadlocks at review time.

## Common Mistakes

- Vague acceptance criteria - use FR-NNN format with MUST/SHOULD/MAY
- Missing traceability matrix - every FR-NNN needs a test plan
- Not listing affected modules - causes surprise during implementation
- Ignoring data model changes - leads to migration issues
- Skipping "Out of Scope" section - invites scope creep
- Not reviewing against constitution - violates principles mid-implementation
- Not checking for parallel open specs on the same file - leads to conflicting ACs (LESSON-008)
