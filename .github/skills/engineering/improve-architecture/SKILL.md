---
name: improve-architecture
description: "Use when identifying pattern violations, technical debt, or architecture improvements. Workflow: identify violation, propose fix with ADR, get approval for Level 1+ changes, implement with tests."
argument-hint: "What architecture issue or area should I improve?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Improve Architecture

Architecture improvement workflow: identify pattern violation → propose fix with ADR → get human approval for Level 1+ changes → implement with tests.

## When to Use

Load this skill when:
- Architecture review triggered (end of PI, tech debt > 10 items, or core module change)
- Pattern violation discovered during implementation
- Performance bottleneck identified
- Deep module dependency detected
- Vocabulary drift found

Do NOT load when:
- Simple bug fix (no architecture change)
- Feature implementation within existing patterns

## Process

### 1. Identify Violation

Check implementation against `spec-driven-development/constitution/principles.md`:

**Common violations**:
- **Article 1**: Global mutable state (use Engine singleton instead)
- **Article 2**: Circular dependencies (refactor to dependency injection)
- **Article 3**: God class (> 300 LoC, > 10 methods)
- **Article 4**: Deep module (hidden complexity, unclear interface)
- **Article 5**: Leaky abstraction (implementation details exposed)

**Investigation**:
```powershell
# Use gitnexus to analyze dependencies
gitnexus analyze --module agent/board.py

# Check for circular dependencies
gitnexus deps --circular

# Find god classes
gitnexus metrics --loc --methods
```

### 2. Propose Fix with ADR

Create Architecture Decision Record in `spec-driven-development/docs/ADR/`:

```markdown
# ADR {number}: {Decision Title}

**Date**: YYYY-MM-DD
**Status**: PROPOSED | ACCEPTED | REJECTED | SUPERSEDED
**Decision Level**: 0 (trivial) | 1 (module) | 2 (system) | 3 (foundational)

## Context
{What led to this? What problem exists?}

## Decision
{What are we changing?}

## Consequences
**Enables**:
- {positive outcome 1}
- {positive outcome 2}

**Constrains**:
- {limitation 1}
- {trade-off 2}

## Alternatives Considered
1. **{Alternative A}**: Rejected because {reason}
2. **{Alternative B}**: Rejected because {reason}

## Implementation Plan
1. {Step 1}
2. {Step 2}
3. {Verification}

## Affected Modules
- {module 1}
- {module 2}
```

### 3. Get Approval

**Decision levels** (from decision-policy.md):
- **Level 0 (Trivial)**: Rename variable, extract helper. Proceed without approval.
- **Level 1 (Module)**: Refactor single module, change API. Get Principal Architect approval.
- **Level 2 (System)**: Change a core abstraction module (the orchestrator, the LLM client). Get Principal Architect + PM approval.
- **Level 3 (Foundational)**: Change tech stack or principles. Get human approval + team review.

**Approval process**:
1. Commit ADR with status: PROPOSED
2. If Level 0: Proceed to implementation
3. If Level 1+: Tag Principal Architect for review
4. Wait for approval before implementing
5. Update ADR status to ACCEPTED or REJECTED

### 4. Implement with Tests

Follow TDD discipline:
```
1. Write failing test that demonstrates the problem
2. Implement fix following ADR plan
3. Refactor to clean patterns
4. Update affected tests
5. Run full suite (recorded baseline)
6. Commit with reference to ADR
```

### 5. Update Documentation

- Update CONTEXT.md if new patterns/terms introduced
- Update principles.md if new article added
- Mark old ADRs as SUPERSEDED if applicable

## Examples

### Example 1: God Class Violation

```markdown
# ADR 005: Extract Board Data Aggregation

**Date**: 2026-05-22
**Status**: PROPOSED
**Decision Level**: 1 (Module)

## Context
agent/board.py has grown to 450 LoC with 15 methods. It aggregates data from 5 sources (projects, tasks, meetings, ideas, accountability), renders board HTML, and calculates statistics. This violates Article 3 (god class pattern).

## Decision
Extract data aggregation into separate `BoardDataAggregator` class. Keep rendering logic in board.py. Move statistics to `BoardMetrics` class.

## Consequences
**Enables**:
- Single responsibility (board.py = rendering only)
- Easier testing (mock aggregator, test rendering)
- Clearer dependencies

**Constrains**:
- More files (3 instead of 1)
- Must maintain interface between aggregator and renderer

## Alternatives Considered
1. **Keep as-is**: Rejected - violates principles, hard to test
2. **Split into 5 mini-modules**: Rejected - overkill for current scale

## Implementation Plan
1. Create agent/board_aggregator.py with BoardDataAggregator class
2. Create agent/board_metrics.py with BoardMetrics class
3. Refactor board.py to use aggregator
4. Update tests to mock aggregator
5. Verify the recorded test baseline passes

## Affected Modules
- agent/board.py (refactor)
- tests/test_board.py (update mocks)
- NEW: agent/board_aggregator.py
- NEW: agent/board_metrics.py

**Approval needed**: Principal Architect (Level 1 decision)
```

### Example 2: Level 0 Refactor (No Approval)

```markdown
# ADR 006: Extract Duplicate Error Handling

**Date**: 2026-05-22
**Status**: ACCEPTED (Level 0 - proceeded)
**Decision Level**: 0 (Trivial)

## Context
Duplicate try/except blocks in 8 API endpoints. DRY violation.

## Decision
Extract to `safe_api_call()` helper in agent/utils.py.

## Implementation
```python
def safe_api_call(func):
    try:
        return func()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"status": "error", "message": str(e)}
```

## Affected Modules
- agent/utils.py (new helper)
- agent/routes/*.py (use helper)

**No approval needed** (Level 0 - trivial refactor)

Committed: "refactor(D0): extract safe_api_call helper"
```

### Example 3: Level 2 System Change

```markdown
# ADR 007: Replace JSON Files with SQLite

**Date**: 2026-05-22
**Status**: PROPOSED
**Decision Level**: 2 (System - changes core data layer)

## Context
Six .json files for persistence (ideas, meetings, accountability, etc.) cause:
- Concurrent access issues (file locking)
- No query capability (must load full file)
- No relational integrity
- Migration pain (manual JSON surgery)

Tech stack already approved SQLite. This consolidates.

## Decision
Migrate all .json stores to SQLite tables. Keep file-based config/templates.

## Consequences
**Enables**:
- Atomic transactions
- Efficient queries
- Foreign key constraints
- Schema migrations (Alembic)

**Constrains**:
- Migration effort (one-time cost)
- Backup strategy change (SQLite dump instead of JSON)

## Alternatives Considered
1. **Keep JSON, improve locking**: Rejected - doesn't solve query/integrity issues
2. **Move to PostgreSQL**: Rejected - overkill, violates tech stack (SQLite approved)

## Implementation Plan
1. Define SQLModel models for each JSON store
2. Write migration script (JSON → SQLite)
3. Update loaders to use session.query()
4. Deprecate old JSON files (keep backups)
5. Update tests to use session fixtures

Estimated: 5 days

## Affected Modules
ALL data access layers:
- agent/ideas.py
- agent/accountability.py
- agent/meeting_processor.py
- agent/models.py (new tables)
- agent/database.py (migrations)
- tests/* (session fixtures)

**Approval needed**: Principal Architect + Product Manager (Level 2 - system change)
```

## Common Mistakes

- Implementing Level 1+ changes without approval - violates decision policy
- Not writing ADR for architectural changes - loses rationale
- Fixing violations without tests - can't verify fix works
- Marking trivial refactors as Level 1+ - ceremony bloat
- Not checking principles.md before proposing - duplicates existing patterns
- Forgetting to update CONTEXT.md - vocabulary drift
- Not running full test suite after refactor - breaks baseline
