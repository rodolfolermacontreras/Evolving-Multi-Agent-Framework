---
name: project-context
description: "Use when starting any session, encountering unfamiliar terminology, making naming decisions, or updating shared project vocabulary. Ensures consistent terminology across all agents and artifacts."
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Project Context

Loads and maintains the CONTEXT.md shared language document to ensure consistent terminology and vocabulary across all agents, specs, and code.

## When to Use

Load this skill when:
- Starting any session (always read CONTEXT.md first)
- Encountering unfamiliar terminology in specs or code
- Naming new modules, classes, or features
- Creating or updating documentation
- Running grill-with-docs workflow

Do NOT load when:
- Working on external documentation (README.md for general audience)
- Quick bug fixes with no new concepts

## Process

1. Read `spec-driven-development/CONTEXT.md` at session start
   - Absorb canonical terms and their definitions
   - Note any ambiguous or missing terms

2. When encountering new concepts during work:
   - Check if term exists in CONTEXT.md
   - If missing and important: flag for addition
   - If ambiguous: flag for clarification

3. Update CONTEXT.md when:
   - New architectural patterns emerge
   - New domain concepts are introduced
   - Existing terms are superseded
   - Ambiguities are resolved via grill-with-docs

4. Update format:
   ```markdown
   ## Term Name
   **Definition**: One sentence definition
   **Context**: Why it matters, where it's used
   **Examples**: Concrete usage
   **Related**: Cross-references to other terms
   **Supersedes**: (if applicable) Old term with date
   ```

5. After updates:
   - Commit: `docs: update CONTEXT.md - add {term}`
   - Inform team if term affects interfaces or naming

## Examples

### Example 1: Adding a New Term

```markdown
During implementation of fleet dispatch, discovered concept "dispatch packet":

Add to CONTEXT.md:

## Dispatch Packet
**Definition**: A complete set of instructions, context, and constraints for one worker agent to execute one task in isolation.
**Context**: Used by fleet-coordinator skill to prepare parallel agent dispatches. Includes agent brief, skill attachments, worktree path, and success criteria.
**Examples**: `sessions/DSP-2026-05-21-001.md` contains a dispatch packet for implementing the calendar route.
**Related**: Fleet Coordinator, Agent Brief, Worktree
```

### Example 2: Resolving Ambiguity

```markdown
Spec uses "task" in two ways: (1) implementation unit, (2) user-facing todo item.

Update CONTEXT.md:

## Implementation Task
**Definition**: An atomic unit of work in a sprint plan, typically scoped to 1-3 files, with clear acceptance criteria and 2-4h effort estimate.
**Context**: Internal SDD concept. Not exposed to end users.
**Supersedes**: "Task" (ambiguous as of 2026-05-20)

## User Task
**Definition**: A todo item created by the user in the host project's dashboard.
**Context**: Exposed via the web framework's /tasks endpoints and task board UI.
**Supersedes**: "Task" (ambiguous as of 2026-05-20)
```

## Common Mistakes

- Not reading CONTEXT.md at session start - leads to vocabulary drift
- Adding every tiny detail - CONTEXT.md is for important, reusable concepts only
- Failing to mark superseded terms - creates confusion
- Not committing changes - CONTEXT.md must stay version-controlled
- Duplicating content from constitution - CONTEXT.md is for vocabulary, constitution is for policy
