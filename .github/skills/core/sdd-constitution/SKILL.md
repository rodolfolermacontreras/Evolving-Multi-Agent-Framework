---
name: sdd-constitution
description: "Use when starting any SDD workflow task, making architectural decisions, or validating that work aligns with project mission, principles, tech stack, and decision policies."
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
---

# SDD Constitution

Loads and enforces the project constitution to ensure all decisions align with mission, principles, tech stack, roadmap, and quality policies.

## When to Use

Load this skill when:
- Starting any SDD workflow (triage, spec, plan, implement)
- Making architectural decisions (Level 1+ changes)
- Validating feature specs or implementation plans
- Resolving conflicts between requirements and project principles
- Onboarding to the Day-to-Day Agent codebase

Do NOT load when:
- Working on non-SDD features (use standard git-workflow instead)
- Making trivial changes (typos, formatting)

## Process

1. Read all constitution files in order:
   - `spec-driven-development/constitution/mission.md` - Core purpose and vision
   - `spec-driven-development/constitution/tech-stack.md` - Approved technologies
   - `spec-driven-development/constitution/principles.md` - Design principles and articles
   - `spec-driven-development/constitution/roadmap.md` - Strategic direction
   - `spec-driven-development/constitution/decision-policy.md` - Decision levels and approval gates
   - `spec-driven-development/constitution/quality-policy.md` - Quality gates and standards

2. Cross-reference with `.github/copilot-instructions.md` (root authority)
   - Never duplicate or weaken existing rules
   - Constitution supplements, not replaces

3. Check proposed work against:
   - Does it align with mission?
   - Does it follow tech stack constraints?
   - Does it violate any principles?
   - What decision level is required?
   - What quality gates apply?

4. If conflicts found:
   - Document in clarification-log.md
   - Escalate to Principal PM or Architect
   - Do NOT proceed until resolved

## Examples

### Example 1: Validating a Feature Spec

```markdown
Spec proposes: "Add Redis for caching"

Constitution check:
- tech-stack.md: "SQLite for all persistence. No external services."
- Violation: YES - Redis not in approved stack
- Action: Flag for decision-policy review (Level 1 decision)
- Recommendation: Use SQLite caching table instead
```

### Example 2: Validating Implementation Approach

```markdown
Task: "Code quality reviewer is asked to review a PR before the spec compliance reviewer has signed off"

Constitution check:
- principles.md Article III: "Two-Stage Review Order Is Fixed -- spec compliance first, then code quality"
- Violation: YES
- Action: Block the quality review. Route the PR to the spec compliance reviewer first; quality review proceeds only after compliance passes.
```

## Common Mistakes

- Skipping constitution check for "small" changes - even small changes can violate principles
- Not reading ALL constitution files - each serves a distinct purpose
- Treating constitution as optional - it is mandatory for all SDD work
- Forgetting to cross-check with copilot-instructions.md
