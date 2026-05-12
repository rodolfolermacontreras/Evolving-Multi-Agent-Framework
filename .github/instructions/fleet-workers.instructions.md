---
applyTo: "**/wt-*/**"
---

When working inside a worktree branch, assume you are executing isolated feature work for the Day-to-Day Agent.

## Worktree Discipline
- A worktree maps to exactly one feature branch and one primary task stream.
- Never treat a worktree as a scratch area for unrelated changes.
- Keep edits scoped to the assigned brief and branch purpose.

## Branch Safety
- Never touch `master`.
- Never commit directly to `integration/improvements`.
- Merge direction is feature branch -> `integration/improvements`.
- If you discover you are on the wrong branch or wrong worktree, stop immediately.

## Worker Behavior
- Read the assigned brief before editing.
- Confirm files in scope and watch for overlap with other workers.
- Prefer TDD: failing test first, minimal implementation, refactor, verify.
- Record blockers early instead of improvising around missing context.

## Conflict Management
- Shared-file conflict means the work is sequential until resolved.
- Do not overwrite or absorb another worker's parallel changes casually.
- Use explicit file boundaries in worker briefs when possible.
- If conflict risk is unclear, escalate rather than assuming safety.

## Validation
- Establish a local baseline before changes when practical.
- Run the smallest relevant test scope during implementation.
- Run the broader required regression scope before handoff.
- Preserve the repository's test baseline expectations.

## Commit and Handoff Rules
- Commit messages must follow `type: short description`.
- Handoffs should include summary, tests run, concerns, and commit SHA when available.
- Leave the worktree clean enough for integration review.

## Project Rules
- Use `.venv\Scripts\python.exe` for Python commands.
- No emojis.
- No new dependencies, schema migrations, or permission changes without approval.
- Clean as you go: remove dead code, stale comments, and accidental debug output.
