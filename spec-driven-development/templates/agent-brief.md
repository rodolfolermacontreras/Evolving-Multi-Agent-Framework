# Agent Brief: {TASK_ID}

- Task Reference: {TASK_REFERENCE}
- Worker Role: {WORKER_ROLE}
- Dispatch ID: {DISPATCH_ID}

---

## Spec Excerpt

{RELEVANT_SPEC_EXCERPT_ONLY}

## File Scope

- Allowed files:
  - {ALLOWED_FILE_001}
  - {ALLOWED_FILE_002}
- Blocked files:
  - {BLOCKED_FILE_001}
  - {BLOCKED_FILE_002}

## Acceptance Criteria

1. {AC_001}
2. {AC_002}
3. {AC_003}

## Constraints

- {CONSTRAINT_001}
- {CONSTRAINT_002}
- Do not modify files outside the allowed scope.
- Do not add new dependencies.

## Expected Output Format

```text
Summary:
- {WHAT_CHANGED}

Files Changed:
- {FILE_001}

Validation:
- Command: {COMMAND}
- Result: {PASS_FAIL}

Open Issues:
- {NONE_OR_ISSUE}
```
