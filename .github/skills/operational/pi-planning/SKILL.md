---
name: pi-planning
description: "Use for PI planning ceremony: review backlog, define 3-5 PI objectives, allocate features to sprints, identify risks (ROAM), set capacity, produce CURRENT_PI.md."
argument-hint: "What backlog, objective, or PI planning input should I use?"
license: MIT
metadata:
  author: emf-framework
  version: '1.1'
---

# PI Planning

PI (Program Increment) planning ceremony: review backlog, define 3-5 objectives, allocate features to sprints, identify risks (ROAM), set capacity, produce CURRENT_PI.md.

## When to Use

Load this skill when:
- Starting a new PI (10-week symbolic cadence; wall-clock compressed by AI fleet)
- Quarterly planning session
- Need to align roadmap with sprint capacity

Do NOT load when:
- Sprint planning (smaller scope)
- Mid-PI adjustments (use sprint retro instead)

## Process

### 1. Review Backlog

Read `spec-driven-development/backlog/BACKLOG.md`:

```markdown
# Review Questions
- What P1/P2 items are ready (SPECCED or PLANNED)?
- What P3 items should be promoted?
- What blockers remain from last PI?
- What new requests arrived?
```

**Filter criteria**:
- **Must have spec** (at least SPECCED state)
- **High RICE score** (P1/P2)
- **No blockers** (or blocker resolution plan exists)

### 2. Define PI Objectives (3-5 max)

Each objective should be:
- **Outcome-focused** (not task list)
- **User-valuable** (not purely technical)
- **Measurable** (clear success criteria)
- **Achievable** (within 3 sprints)

**Format**:
```markdown
## PI Objective 1: {User-Facing Outcome}
**Why**: {Business value}
**Success Criteria**: {How we know it's done}
**Features**: {High-level features included}
```

### 3. Allocate Features to Sprints

**Capacity rules**:
- **5 sprints per PI** (2 weeks each = 10 weeks symbolic)
- **Reserve 20% for tech debt** (1 sprint = 0.8 sprint of features)
- **Dependencies first** (features with blockers in early sprints)

**Allocation template**:
```markdown
### Sprint 1 (Weeks 1-2)
- Feature A (5 story points)
- Feature B (3 story points)
- Tech debt: X, Y
Total: 8 SP + 20% buffer = 10 SP capacity

### Sprint 2 (Weeks 3-4)
- Feature C (8 story points)
- Feature D (2 story points)
Total: 10 SP

### Sprint 3 (Weeks 5-6)
- Feature E (5 story points)
- Feature F (3 story points)
- Buffer for slippage
Total: 8 SP
```

### 4. Identify Risks (ROAM)

**ROAM framework**:
- **Resolved**: Risk mitigated (no action needed)
- **Owned**: Risk assigned to owner with mitigation plan
- **Accepted**: Risk acknowledged, no mitigation (monitor only)
- **Mitigated**: Risk reduced through action

**Risk register**:
```markdown
| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| Google API quota limits | High | Medium | Owned | Rodolfo | Request production quota in Sprint 1 |
| Calendar event schema changes | Medium | Low | Accepted | - | Monitor Google API changelog |
| UX review delays | Low | High | Mitigated | PM | Pre-approve designs before Sprint 2 |
```

### 5. Set Capacity

**Factors**:
- **Team size**: 1 developer (example)
- **Availability**: Holidays, PTO, meetings
- **Velocity**: Historical average (from past sprints)

**Calculation**:
```
Total capacity = (# developers) × (days per sprint) × (velocity factor)
                = 1 × 10 days × 0.8 (reserve for meetings/admin)
                = 8 ideal days per sprint
                = 24 ideal days per PI
```

### 6. Create PI Directory and Artifacts (Atomic Commit)

All PI artifacts must be created in a **single commit** to prevent partial state.
Create both the sprint-ceremony directory and the Management navigation entry together.

**PI kickoff checklist** (all items in one commit):

- [ ] `spec-driven-development/sprints/PI-{N}/CURRENT_PI.md` -- ceremony artifact (template below)
- [ ] `spec-driven-development/sprints/PI-{N}/lessons.md` -- copy from `lessons-template.md`, replace PI-{N}
- [ ] `spec-driven-development/docs/Management/PI-{N}/INDEX.md` -- navigation entry with sprint table

Do NOT create one without the others. The `sprints/` directory holds ceremony
artifacts (CURRENT_PI, lessons, retros). The `docs/Management/` directory holds
the navigation index. Both are required for a PI to be fully tracked.

**Commit message**: `docs: kick off PI-{N} -- {theme}`

Write `CURRENT_PI.md` to `spec-driven-development/sprints/PI-{N}/CURRENT_PI.md`:

```markdown
# PI-{N}: {Theme}

**Duration**: YYYY-MM-DD to YYYY-MM-DD (6 weeks)
**Team**: {owner from project.config.json}

## PI Objectives

### 1. {Objective Title}
**Why**: {Business value}
**Success Criteria**: {Measurable outcome}
**Features**:
- Calendar sync integration
- Task filters

### 2. {Objective Title}
...

## Sprint Allocation

### Sprint 1 (Weeks 1-2)
**Goal**: {Sprint theme}
**Features**:
- [ ] Calendar sync (8 SP)
- [ ] Tech debt: Migrate JSON to SQLite (2 SP)
**Capacity**: 10 SP

### Sprint 2 (Weeks 3-4)
**Goal**: {Sprint theme}
**Features**:
- [ ] Task filters (5 SP)
- [ ] Status report automation (5 SP)
**Capacity**: 10 SP

### Sprint 3 (Weeks 5-6)
**Goal**: {Sprint theme}
**Features**:
- [ ] Email notifications (4 SP)
- [ ] Buffer for slippage (4 SP)
**Capacity**: 8 SP

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| ... | ... | ... | ... | ... | ... |

## Dependencies

- Google API production quota (external)
- UX review for filters (internal)

## Success Metrics

- All PI objectives met (3/3)
- Velocity: 24-28 SP delivered
- Tech debt: < 10 items remaining
- Test coverage: the recorded test baseline passing

## Notes

{Any context, decisions, or constraints}
```

## Examples

### Example 1: PI-1 Planning

```markdown
# PI-1: Automation & Integration

**Duration**: 2026-05-22 to 2026-07-03 (6 weeks)
**Team**: {owner}

## PI Objectives

### 1. Reduce Manual Work via Calendar Integration
**Why**: Save 30min/day per user by auto-importing calendar events
**Success Criteria**: Users can see next 7 days of calendar events in dashboard timeline
**Features**:
- Calendar sync (Google Calendar OAuth)
- Dashboard timeline widget

### 2. Improve Task Discoverability
**Why**: Users report "lost tasks" - need better filtering
**Success Criteria**: Users can filter tasks by priority, status, and project
**Features**:
- Task filter UI
- Filter persistence (remember user preferences)

### 3. Automate Status Reporting
**Why**: Status reports take 1h to compile manually
**Success Criteria**: Generate HTML status report with one click
**Features**:
- Status report generator
- Email export

## Sprint Allocation

### Sprint 1 (May 22 - Jun 5)
**Goal**: Calendar foundation
- [ ] Calendar sync backend (8 SP)
  - OAuth flow
  - Event fetch/store
  - API endpoints
- [ ] Tech debt: JSON → SQLite migration (2 SP)
**Capacity**: 10 SP

### Sprint 2 (Jun 6 - Jun 19)
**Goal**: UI polish
- [ ] Calendar timeline widget (5 SP)
- [ ] Task filters (5 SP)
**Capacity**: 10 SP

### Sprint 3 (Jun 20 - Jul 3)
**Goal**: Reporting automation
- [ ] Status report generator (5 SP)
- [ ] Email export (3 SP)
**Capacity**: 8 SP

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| Google API quota limits | High | Medium | Owned | Rodolfo | Request prod quota Week 1 |
| Calendar schema changes | Medium | Low | Accepted | - | Monitor changelog |
| JSON migration complexity | Medium | High | Mitigated | Rodolfo | Allocate 2 SP buffer |

## Dependencies

**External**:
- Google API production quota approval (needed by Sprint 1 end)

**Internal**:
- UX Designer review for timeline widget (needed by Sprint 2 start)

## Success Metrics

- All 3 PI objectives met
- Velocity: 24-28 SP delivered
- Zero P1 bugs carried over
- Test baseline: the recorded test baseline passing

## Notes

- This PI focuses on user-visible automation (not architecture refactors)
- Tech debt capped at 20% (only critical items)
- Reserve Sprint 3 capacity for slippage buffer
```

## Common Mistakes

- Too many objectives (> 5) - dilutes focus
- Objectives are tasks, not outcomes - "Implement calendar API" vs "Reduce manual work"
- Not reserving capacity buffer - assumes 100% velocity
- Ignoring dependencies - features block each other
- No ROAM risk assessment - surprises cascade
- Sprint overload (> 10 SP per sprint) - burnout risk
- Forgetting to commit CURRENT_PI.md - team misaligned
- Creating `sprints/PI-N/` without `docs/Management/PI-N/INDEX.md` (or vice versa) - navigation gap, stale references. LESSON-013 from PI-3: always create both in one commit.
