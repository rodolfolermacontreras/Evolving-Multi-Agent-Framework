---
name: grill-with-docs
description: "Same as grill-me but ALSO updates CONTEXT.md with new terms/decisions discovered during questioning. Use when decisions will affect vocabulary or architecture."
argument-hint: "What decision, feature, or vocabulary should I grill and document?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Grill With Docs

Enhanced grill-me that updates CONTEXT.md with new terms/decisions discovered during Socratic questioning. Use when clarifications will create new vocabulary or architectural decisions.

## When to Use

Load this skill when:
- Same triggers as grill-me (ambiguous scope, weak criteria, etc.)
- AND the feature introduces new concepts or terminology
- AND decisions may affect multiple modules or future features

Do NOT load when:
- Clarifications are purely implementation details
- Feature uses existing, well-defined vocabulary
- Simple bug fix

## Process

1. Follow full **grill-me** process (one question at a time, recommend, explain, wait)

2. After EACH confirmed answer, check:
   - Does this introduce a new term or concept?
   - Does this decision affect architecture (>1 module)?
   - Does this supersede a previous decision?

3. If YES to any:
   - **Update CONTEXT.md** with the new term/decision
   - If architectural: **Create ADR** in `spec-driven-development/docs/ADR/`
   - If supersedes old decision: **Mark old as SUPERSEDED** with date

4. Update format:
   ```markdown
   ## New Term
   **Definition**: One sentence
   **Context**: Why it exists, where used
   **Examples**: Concrete usage
   **Related**: Cross-references
   **Decided**: YYYY-MM-DD in {feature-name} grill session
   ```

5. If creating ADR:
   ```markdown
   # ADR {number}: {Decision Title}
   Date: YYYY-MM-DD
   Status: ACCEPTED
   
   ## Context
   {what led to this decision}
   
   ## Decision
   {what we decided}
   
   ## Consequences
   {what this enables, what it constrains}
   
   ## Alternatives Considered
   {what we rejected and why}
   ```

6. Commit after each doc update:
   ```
   docs: update CONTEXT.md - add {term} from {feature} grill
   ```

## Examples

### Example 1: New Term Emerges

```markdown
Grill session on calendar sync feature:

Q: "Should we store calendar events in our database or just reference the original?"

Answer: "Store a snapshot. Calendar API might be offline."

New term identified: "Event Snapshot"

Update CONTEXT.md:
## Event Snapshot
**Definition**: A cached copy of a calendar event stored in our SQLite database, including title, time, attendees, and last-synced timestamp.
**Context**: Enables offline access to calendar data and reduces API calls. Requires periodic re-sync to stay fresh.
**Examples**: `CalendarEvent` model in agent/models.py
**Related**: Calendar Sync, Sync Strategy
**Decided**: 2026-05-21 in calendar-sync grill session
```

### Example 2: Architectural Decision

```markdown
Grill session on task prioritization:

Q: "Should RICE scoring be calculated on-demand or pre-computed and cached?"

Answer: "Pre-compute and cache. Recalc only when user edits a task."

This affects multiple modules (board.py, api.py, models.py).

Create ADR 004:
# ADR 004: RICE Score Caching Strategy
Date: 2026-05-21
Status: ACCEPTED

## Context
RICE scores are used for task prioritization across the board UI, API endpoints, and reporting. Calculating on-demand for every request adds latency.

## Decision
Pre-compute RICE scores and store them in the Task model. Recalculate only when task properties (reach, impact, confidence, effort) change.

## Consequences
- Faster board rendering (no calculation overhead)
- Requires migration to add `rice_score` column to tasks table
- Adds cache invalidation logic to task update endpoints
- Simplifies reporting queries

## Alternatives Considered
- On-demand calculation: Rejected due to latency
- Background job recalculation: Overkill for current scale
```

### Example 3: Superseding Old Decision

```markdown
Grill session reveals:

Old decision: "All notifications go to console only"
New decision: "Notifications persist to SQLite for dashboard display"

Update CONTEXT.md:
## Notification Persistence (SUPERSEDED 2026-05-21)
**Old Definition**: Notifications logged to console only, not stored.
**Superseded by**: Notification Store
**Reason**: Dashboard needs to display past notifications.

## Notification Store
**Definition**: SQLite table storing user notifications (tasks, reminders, system alerts) with status (unread/read/dismissed) and timestamp.
**Context**: Enables persistent notification center in dashboard. Replaces console-only approach.
**Examples**: `Notification` model in agent/models.py
**Related**: Dashboard, Alerts
**Decided**: 2026-05-21 in dashboard-notifications grill session
**Supersedes**: Notification Persistence (console-only)
```

## Common Mistakes

- Forgetting to update CONTEXT.md - loses vocabulary traceability
- Updating docs AFTER all questions - do it incrementally per answer
- Not creating ADR for multi-module decisions - loses rationale
- Not marking superseded terms - creates confusion
- Adding every tiny detail to CONTEXT.md - only important, reusable concepts
- Skipping commit after doc update - docs must be version-controlled
