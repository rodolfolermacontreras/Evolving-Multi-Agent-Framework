---
name: fleet-coordinator
description: "Use when dispatching parallel workers. Checks conflict matrix (6 levels), determines batch size (start 2, max 4), generates dispatch packets, tracks in ledger, post-dispatch integration."
argument-hint: "What work should I coordinate across parallel agents?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Fleet Coordinator

Fleet dispatch coordination: conflict matrix checks, batch sizing, dispatch packet generation, ledger tracking, and post-dispatch integration.

## When to Use

Load this skill when:
- Sprint has 3+ parallel-safe tasks ready
- Need to coordinate multiple workers on same feature
- Planning batch dispatch for efficiency

Do NOT load when:
- Single task (no coordination needed)
- All tasks have dependencies (not parallel-safe)

## Process

### 1. Check Conflict Matrix (6 Levels)

Before dispatching, verify no conflicts:

```markdown
| Level | Conflict Type | Example | Action |
|-------|--------------|---------|--------|
| 0 | Independent files | routes/a.py vs routes/b.py | Safe - dispatch |
| 1 | Same file, different functions | board.py::fn1 vs board.py::fn2 | Caution - review diffs before merge |
| 2 | Same function | board.py::get_data() | UNSAFE - serialize |
| 3 | Shared global state | Both modify the core orchestrator module | UNSAFE - serialize |
| 4 | Database schema changes | Both alter same table | UNSAFE - coordinate |
| 5 | Breaking API changes | Both change same endpoint signature | UNSAFE - coordinate |
```

**Conflict check**:
```python
# Read task-list.md
tasks = parse_task_list("specs/feature/tasks.md")

conflicts = []
for i, task_a in enumerate(tasks):
    for task_b in tasks[i+1:]:
        level = check_conflict(task_a.files, task_b.files)
        if level >= 2:
            conflicts.append((task_a, task_b, level))

if conflicts:
    print(f"CONFLICT: Tasks cannot run in parallel - Level {level}")
    # Serialize or coordinate
```

### 2. Determine Batch Size

**Rules**:
- **Start with 2** workers (learn conflict patterns)
- **Max 4** workers (diminishing returns + integration overhead)
- **Scale up** only if batch 1 had zero conflicts

**Batch sizing**:
```python
if first_batch:
    batch_size = 2  # Conservative start
elif prev_batch_conflicts == 0:
    batch_size = min(prev_batch_size + 1, 4)  # Scale up
else:
    batch_size = prev_batch_size  # Keep same size
```

### 3. Generate Dispatch Packets

For each task in batch, create session file:

**File**: `spec-driven-development/sessions/DSP-YYYY-MM-DD-NNN.md`

```markdown
# Dispatch Packet: {Task Title}

**Session ID**: DSP-2026-05-22-001
**Task**: {Task ID from task-list.md}
**Worker**: developer-general
**Worktree**: ../wt-{feature-name}-task{N}

## Task Brief
{Copy full task description from task-list.md}

## Context
**Spec**: specs/YYYY-MM-DD-feature/spec.md
**Plan**: specs/YYYY-MM-DD-feature/plan.md
**Dependencies**: {Task IDs this depends on}
**Parallel with**: {Other task IDs in this batch}

## Skill Attachments
- sdd-constitution
- project-context
- git-workflow
- testing-conventions
- tdd
- implement

## Success Criteria
- [ ] Acceptance test passes
- [ ] No lint errors
- [ ] Committed with format: {commit message template}
- [ ] Posted completion to ledger

## Worktree Setup
```powershell
git checkout integration/improvements
git branch feature/f{N}.{M}-{name}-task{T}
git worktree add ..\wt-{name}-task{T} feature/f{N}.{M}-{name}-task{T}
cd ..\wt-{name}-task{T}
```

## Stop Conditions
{Copy from implement skill}
```

### 4. Track in Ledger

Write to `spec-driven-development/ledger/fleet.db`:

```sql
INSERT INTO dispatches (
    session_id, task_id, worker_type, worktree_path,
    status, created_at
) VALUES (
    'DSP-2026-05-22-001', 'Task-2.1', 'developer-general',
    '../wt-calendar-task2', 'DISPATCHED', CURRENT_TIMESTAMP
);
```

### 5. Post-Dispatch Integration

After all workers complete:

```powershell
# 1. Collect results from each worktree
cd ..\wt-calendar-task1
git log --oneline -5  # Verify commits

cd ..\wt-calendar-task2
git log --oneline -5

# 2. Merge into integration/improvements (one at a time)
cd ..\Day_to_Day
git checkout integration/improvements

git merge --no-ff feature/f2.1-calendar-task1
# Resolve conflicts if any
git merge --no-ff feature/f2.1-calendar-task2

# 3. Run full test suite
.venv\Scripts\python.exe -m pytest tests\ -v --tb=short

# 4. Update ledger
UPDATE dispatches SET status='INTEGRATED', completed_at=CURRENT_TIMESTAMP
WHERE session_id IN ('DSP-2026-05-22-001', 'DSP-2026-05-22-002');

# 5. Clean up worktrees
git worktree remove ..\wt-calendar-task1
git worktree remove ..\wt-calendar-task2
git branch -d feature/f2.1-calendar-task1
git branch -d feature/f2.1-calendar-task2
```

## Examples

### Example 1: Safe Parallel Batch

```markdown
# Batch 1: Calendar Sync Feature

**Tasks**:
- Task 2.1: Create /calendar/sync endpoint (agent/routes/calendar.py)
- Task 2.3: Add calendar to world_state (agent/world_state.py)

**Conflict Check**:
- Level 0 (Independent files): SAFE

**Batch Size**: 2 (first batch, start small)

**Dispatch**:
- DSP-2026-05-22-001: Task 2.1 -> ../wt-calendar-sync-api
- DSP-2026-05-22-002: Task 2.3 -> ../wt-calendar-worldstate

**Launch**:
Window 1: cd ../wt-calendar-sync-api && code .
Window 2: cd ../wt-calendar-worldstate && code .
```

### Example 2: Conflict Detected

```markdown
# Batch 1: Board Refactor

**Tasks**:
- Task 1.1: Extract BoardDataAggregator (agent/board.py)
- Task 1.2: Extract BoardMetrics (agent/board.py)

**Conflict Check**:
- Level 2 (Same file, overlapping edits): UNSAFE

**Action**: SERIALIZE
- Dispatch Task 1.1 first
- Wait for completion
- Then dispatch Task 1.2

Do NOT run in parallel.
```

### Example 3: Post-Integration Conflict

```markdown
# Batch 1 Integration - 2 tasks completed

Merging feature/f2.1-calendar-task1 -> integration/improvements
  OK: No conflicts

Merging feature/f2.1-calendar-task2 -> integration/improvements
  CONFLICT: agent/world_state.py

Conflict details:
  Task1 added: "calendar": get_calendar_events()
  Task2 added: "calendar_raw": fetch_calendar_raw()

Resolution:
  Keep both (different keys, no semantic conflict)
  
  Combined:
  "calendar": get_calendar_events(),
  "calendar_raw": fetch_calendar_raw(),

Manual merge:
  git add agent/world_state.py
  git commit -m "merge: integrate calendar tasks 1 & 2"

Lesson: Next batch, check for semantic conflicts (not just file-level)
```

## Common Mistakes

- Skipping conflict matrix check - leads to merge hell
- Starting with batch size > 2 - learn before scaling
- Not tracking in ledger - loses traceability
- Merging all at once instead of one-by-one - conflicts compound
- Not running tests after integration - breaks baseline
- Forgetting to clean up worktrees - orphan directories
- Dispatching dependent tasks in parallel - blockers cascade
