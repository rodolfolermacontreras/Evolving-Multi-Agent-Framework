---
name: code-review
description: "Use when reviewing implementation. Two-stage process: Stage 1 checks spec compliance (MISSING/EXTRA/WRONG), Stage 2 checks code quality (CRITICAL/IMPORTANT/SUGGESTION). Never do Stage 2 before Stage 1 passes."
argument-hint: "Which file, PR, or commit range should I review?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Code Review

Two-stage review process: Stage 1 (spec compliance) checks MISSING/EXTRA/WRONG. Stage 2 (code quality) checks CRITICAL/IMPORTANT/SUGGESTION. Never do Stage 2 before Stage 1 passes.

## When to Use

Load this skill when:
- Implementation claims to be complete
- Before merging feature branch
- After worker signals task done
- Part of implement skill workflow

Do NOT load when:
- Spec not yet complete
- Work-in-progress (not ready for review)

## Process

### Stage 1: Spec Compliance Review

**Reviewer**: Principal Software Developer (or peer)

**What to check**:
- [ ] Every FR-NNN with MUST priority is implemented
- [ ] No features exist that aren't in the spec (EXTRA check)
- [ ] Implementation matches spec intent
- [ ] Success criteria verifiable in implementation
- [ ] Out of Scope items genuinely excluded

**Finding categories**:
- **MISSING**: Requirements in spec not implemented
- **EXTRA**: Features implemented NOT in spec (scope creep)
- **WRONG**: Implementation contradicts spec

**Verdict**:
- **COMPLIANT**: All FR-NNN requirements met, no extras, matches spec
- **NOT COMPLIANT**: One or more MISSING/EXTRA/WRONG found

**If NOT COMPLIANT**:
1. Document findings
2. Implementer fixes
3. Re-review from Stage 1 (start over)

**DO NOT PROCEED TO STAGE 2 UNTIL STAGE 1 PASSES**

### Stage 2: Code Quality Review

**Reviewer**: Principal Software Developer, or Architect if cross-cutting

**What to check**:
- [ ] **Error handling**: Exceptions caught, logged, user-friendly messages
- [ ] **Edge cases**: Null, empty, boundary values handled
- [ ] **Security**: safe_path() for paths, esc() for HTML, Pydantic for input
- [ ] **Naming**: Clear, consistent with codebase vocabulary
- [ ] **Tests**: Adequate coverage, proper isolation (tmp_path, patched_settings)
- [ ] **Conventions**: Commit format, no emojis, no orphan code
- [ ] **Performance**: No O(n^2) where O(n) suffices
- [ ] **DRY**: No duplicate logic (extract to helpers)
- [ ] **Data flow**: world_state.py updated if new data source

**Finding severity**:
- **CRITICAL**: Must fix before merge (security, correctness, data loss)
- **IMPORTANT**: Should fix (maintainability, performance, tech debt)
- **SUGGESTION**: Nice to have (style, naming preferences)

**Verdict**:
- **APPROVED**: Ready to merge
- **CHANGES REQUIRED**: One or more CRITICAL or IMPORTANT findings

**If CHANGES REQUIRED**:
1. Document findings with severity
2. Implementer fixes
3. Re-review Stage 2 only (Stage 1 still passes)

## Examples

### Example 1: Stage 1 Failure (MISSING)

```markdown
# Stage 1 Review: Calendar Sync Feature

**Spec**: specs/2026-05-21-calendar-sync/spec.md

## Findings

MISSING:
- FR-003 (MUST): "When calendar event overlaps work hours, system SHALL mark time as unavailable"
  - Location: Scheduler logic missing
  - Impact: Core requirement not implemented

## Verdict: NOT COMPLIANT

## Required Actions
1. Implement FR-003 in agent/scheduler.py
2. Add test: test_scheduler.py::test_mark_unavailable_time
3. Re-submit for Stage 1 review

DO NOT PROCEED TO STAGE 2 UNTIL FR-003 IS IMPLEMENTED.
```

### Example 2: Stage 1 Failure (EXTRA)

```markdown
# Stage 1 Review: Calendar Sync Feature

**Spec**: specs/2026-05-21-calendar-sync/spec.md

## Findings

EXTRA:
- Implemented two-way sync (write back to calendar)
  - Location: agent/routes/calendar.py lines 45-67
  - Not in spec: Spec says "one-way sync only"
  - Impact: Scope creep, adds complexity not requested

## Verdict: NOT COMPLIANT

## Required Actions
1. Remove two-way sync code (lines 45-67)
2. Keep only read-from-calendar logic
3. If two-way sync is desired, create separate spec

Scope creep detected. Reverting to spec boundaries.
```

### Example 3: Stage 2 Review (CRITICAL)

```markdown
# Stage 2 Review: Calendar Sync Feature

**Stage 1**: COMPLIANT (all FR-NNN met)

## Findings

CRITICAL:
1. **Security**: User input not validated
   - Location: agent/routes/calendar.py line 23
   - Issue: `user_id` param passed directly to DB query without Pydantic validation
   - Risk: SQL injection, path traversal
   - Fix: Use Pydantic model for request validation

2. **Error handling**: API failure crashes endpoint
   - Location: agent/calendar_client.py line 56
   - Issue: `requests.get()` not wrapped in try/except
   - Risk: 500 error on network failure
   - Fix: Wrap in try/except, return user-friendly error

IMPORTANT:
3. **Performance**: N+1 query in event loop
   - Location: agent/routes/calendar.py line 34
   - Issue: DB query inside for-loop (10 events = 10 queries)
   - Fix: Batch query before loop

SUGGESTION:
4. **Naming**: Variable name `e` unclear
   - Location: agent/calendar_client.py line 42
   - Suggestion: Rename to `event` for clarity

## Verdict: CHANGES REQUIRED

## Required Actions
1. Fix CRITICAL issues 1 & 2 (blocking merge)
2. Fix IMPORTANT issue 3 (tech debt)
3. SUGGESTION 4 is optional (nice to have)

Re-submit for Stage 2 review after fixes.
```

### Example 4: Approved

```markdown
# Stage 2 Review: Calendar Sync Feature

**Stage 1**: COMPLIANT
**Stage 2**: Second review after fixes

## Previous Issues
- CRITICAL 1 (Security): Fixed - Pydantic validation added
- CRITICAL 2 (Error handling): Fixed - try/except added
- IMPORTANT 3 (Performance): Fixed - batch query implemented

## Current Findings
None. All critical/important issues resolved.

SUGGESTION:
- Consider adding rate limiting for API calls (future enhancement)

## Verdict: APPROVED

Ready to merge into integration/improvements.
```

## Common Mistakes

- Doing Stage 2 before Stage 1 passes - wastes review cycles
- Not documenting findings clearly - implementer doesn't know what to fix
- Marking style issues as CRITICAL - inflates severity
- Failing review for SUGGESTION items - blocks progress on nice-to-haves
- Re-reviewing Stage 1 after Stage 2 fixes - Stage 1 doesn't change
- Not checking test coverage - untested code slips through
- Ignoring security checks - XSS/injection vulnerabilities merge
- Not verifying world_state.py updates - new data sources missed
