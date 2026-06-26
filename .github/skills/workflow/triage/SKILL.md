---
name: triage
description: "Use when processing new feature ideas from backlog. Applies RICE scoring, assigns P1-P4 priority, and moves through state machine: NEW -> TRIAGED -> SPECCED -> PLANNED -> TASKED -> IMPLEMENTING -> REVIEWING -> DONE."
argument-hint: "What feature idea or backlog item should I triage?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Triage

State machine for incoming work. Applies RICE scoring (Reach, Impact, Confidence, Effort), assigns P1-P4 priority, and transitions ideas through lifecycle states.

## When to Use

Load this skill when:
- New ideas added to IDEAS.md or BACKLOG.md
- Need to prioritize feature requests
- Sprint planning (selecting P1/P2 items)
- Quarterly planning (reviewing P3/P4 items)

Do NOT load when:
- Idea already triaged (has priority assigned)
- Urgent bug fix (skip triage, fix immediately)

## Process

### State Machine

```
NEW -> TRIAGED -> SPECCED -> PLANNED -> TASKED -> IMPLEMENTING -> REVIEWING -> DONE
```

### Triage Steps

1. **Read idea** from `spec-driven-development/backlog/IDEAS.md`

2. **Apply RICE scoring**:
   - **Reach**: How many users affected? (1-10)
   - **Impact**: How much does it help? (0.25=minimal, 0.5=low, 1=medium, 2=high, 3=massive)
   - **Confidence**: How sure are we? (0.5=low, 0.8=medium, 1.0=high)
   - **Effort**: Person-weeks to ship (1=week, 2=2 weeks, etc.)
   - **RICE Score** = (Reach × Impact × Confidence) / Effort

3. **Assign priority**:
   - **P1 (Critical)**: RICE > 30, or blocks other work, or executive priority
   - **P2 (High)**: RICE 15-30, important but not blocking
   - **P3 (Medium)**: RICE 5-15, nice to have
   - **P4 (Low)**: RICE < 5, or deferred/archived

4. **Update state**:
   - Move idea from IDEAS.md to BACKLOG.md under appropriate priority section
   - Add RICE score and justification
   - Transition state: NEW → TRIAGED

5. **Flag for next step**:
   - P1/P2: Flag for spec creation (use to-spec skill)
   - P3: Add to "Next Quarter" section
   - P4: Move to "Archived Ideas" with rationale

## Examples

### Example 1: High-Priority Idea

```markdown
Idea: "Calendar sync integration"

RICE scoring:
- Reach: 10 (all users)
- Impact: 2 (high - saves 30min/day)
- Confidence: 0.8 (medium - depends on Google API stability)
- Effort: 1.5 (1.5 weeks)

RICE = (10 × 2 × 0.8) / 1.5 = 10.67

Priority: P2 (High)
Rationale: High value, moderate effort. Not blocking, but strong ROI.

Action: Move to BACKLOG.md under "P2 - High Priority"
State: NEW → TRIAGED
Next: Flag for spec creation
```

### Example 2: Low-Priority Idea

```markdown
Idea: "Dark mode toggle animation"

RICE scoring:
- Reach: 3 (only users who toggle theme)
- Impact: 0.25 (minimal - aesthetic only)
- Confidence: 1.0 (high - simple CSS)
- Effort: 0.5 (half week)

RICE = (3 × 0.25 × 1.0) / 0.5 = 1.5

Priority: P4 (Low)
Rationale: Low impact, cosmetic feature. Not worth effort now.

Action: Move to "Archived Ideas" in BACKLOG.md
State: NEW → ARCHIVED (skips TRIAGED)
Next: None
```

### Example 3: Blocking Issue

```markdown
Idea: "Fix critical security flaw in auth flow"

RICE scoring:
- N/A (security issue trumps RICE)

Priority: P1 (Critical)
Rationale: Security vulnerability. Blocks production deployment.

Action: Move to BACKLOG.md under "P1 - Critical"
State: NEW → TRIAGED → SPECCED (skip spec for urgent fix)
Next: Implement immediately
```

## BACKLOG.md Format

```markdown
# Backlog

## P1 - Critical
- [TRIAGED] Calendar sync (RICE: 10.67) - saves 30min/day per user
- [SPECCED] Auth security fix - blocks prod deploy

## P2 - High Priority
- [TRIAGED] Task filters (RICE: 8.5) - requested by 5 users
- [PLANNED] Status report automation (RICE: 7.2)

## P3 - Medium Priority
- [TRIAGED] Email notifications (RICE: 6.0)

## P4 - Low Priority / Archived
- [ARCHIVED] Dark mode animation (RICE: 1.5) - cosmetic, low value
```

## Common Mistakes

- Skipping RICE calculation - leads to subjective prioritization
- Inflating Impact scores - be honest about real value
- Forgetting Effort estimate - can't calculate RICE without it
- Not updating state transition - loses traceability
- Moving P3/P4 items to spec phase - ceremony bloat for low-value work
- Treating all P1 as urgent - P1 means important, not always urgent
- Not documenting priority rationale - team doesn't understand decisions
