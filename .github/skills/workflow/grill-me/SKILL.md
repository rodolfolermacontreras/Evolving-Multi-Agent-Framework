---
name: grill-me
description: "Use when scope is ambiguous, acceptance criteria are weak, user impact is unclear, architecture tradeoffs need judgment, or UX behavior is unclear. Socratic questioning with ONE question at a time."
argument-hint: "What plan or feature do you want me to grill you on?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Grill Me

Socratic questioning skill (Matt Pocock-inspired). Ask ONE question at a time, recommend an answer, explain why it matters. Wait for response. Record in clarification-log.md. Stop when 3 consecutive "confirmed" answers.

## When to Use

Load this skill when:
- Feature spec lacks clear acceptance criteria
- Scope boundaries are ambiguous
- User impact or priority is unclear
- Multiple implementation approaches exist with tradeoffs
- UX behavior needs definition
- Edge cases not addressed

Do NOT load when:
- Spec is already clear and complete
- Simple bug fix with obvious solution
- Implementation details (not design questions)

## Process

1. **Ask ONE question** - never batch multiple questions
2. **Recommend an answer**: "I'd suggest: {recommendation}. Does that work?"
3. **Explain why it matters**: Brief context on impact
4. **Wait for human response**
5. **Record the answer** in `clarification-log.md`
6. **Ask next question** based on previous answer
7. **Stop after 3 consecutive confirmations** or max 7 questions (diminishing returns)

### Question Categories (Priority Order)

1. **SCOPE**: What's in/out? Where are the boundaries?
2. **USERS**: Who is this for? What's their goal?
3. **CONSTRAINTS**: What must we preserve? What can't we change?
4. **EDGE CASES**: What happens when {unusual condition}?
5. **PRIORITY**: What matters most if we have to cut scope?

### Clarification Log Format

```markdown
# Clarification Log - {Feature Name}
Date: YYYY-MM-DD

## Q1: {Category} - {Question}
**Asked**: {exact question}
**Recommended**: {your suggestion}
**Answer**: {human response}
**Impact**: {what this unlocks or constrains}

## Q2: ...
```

## Examples

### Example 1: Ambiguous Scope

```markdown
Q: "Should the calendar sync be one-way (read-only) or two-way (write-back)?"

Recommendation: "I'd suggest one-way for now. Read calendar events to auto-schedule tasks, but don't write back to calendar. Simpler, lower risk, faster to ship. Does that work?"

Why it matters: Two-way sync requires conflict resolution, error recovery, and user trust. One-way gets 80% of value with 20% of complexity.

[Wait for answer]

Answer: "Confirmed. One-way is fine."

Recorded to clarification-log.md:
## Q1: SCOPE - Sync Direction
**Asked**: Should calendar sync be one-way or two-way?
**Recommended**: One-way (read-only)
**Answer**: Confirmed. One-way is fine.
**Impact**: Eliminates need for conflict resolution. Reduces scope by ~40%.
```

### Example 2: Unclear Edge Case

```markdown
Q: "What happens if a user has overlapping calendar events during the same time slot?"

Recommendation: "I'd suggest we stack them visually in the UI and let the user manually pick which one blocks their availability. Alternatively, we could auto-merge them into one 'busy' block. Which feels better?"

Why it matters: Affects both data model (do we keep all events or merge?) and UX (how does user see/interact?).

[Wait for answer]

Answer: "Stack them. Keep all events visible."

Recorded to clarification-log.md:
## Q2: EDGE CASES - Overlapping Events
**Asked**: How to handle overlapping calendar events?
**Recommended**: Stack visually, let user pick
**Answer**: Confirmed. Stack and keep all visible.
**Impact**: Requires array field in data model. UI needs vertical stacking layout.
```

## Common Mistakes

- Asking multiple questions at once - violates "one at a time" rule
- Not recommending an answer - makes human do all the thinking
- Forgetting to explain why it matters - loses learning opportunity
- Not recording in clarification-log.md - loses traceability
- Continuing past 7 questions - diminishing returns, ceremony bloat
- Asking implementation questions - this is for design clarity, not code details
