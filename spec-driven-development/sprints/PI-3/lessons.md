# Lessons: PI-3

Living document. Updated by /retro and /replan after each feature DONE.
Each lesson is a *candidate* for framework evolution. Curation happens
via /evolve, which decides which candidates ship as PRs back to the
framework, which defer to a future PI, and which discard.

## Lesson Format

Each lesson is one entry:

```markdown
### LESSON-{NN}: {short title}

- Date: YYYY-MM-DD
- Source feature: {feature dir or "general"}
- Tag: {skill-update | new-skill | agent-update | constitution-amendment | template-update | prompt-update | docs-update}
- Proposal: {one paragraph -- what should change in the framework}
- Evidence: {what happened in the project that suggests this change}
- Affects: {explicit file paths -- skills, prompts, agents, templates, constitution articles}
- Estimated effort: S | M | L
- Status: open | curated-ship | curated-defer | curated-discard | shipped
- Curator decision: {filled in by /evolve}
- PR / commit: {filled in when shipped}
```

---

## Lessons

(Append new lessons below this line. Most-recent first.)

### LESSON-011: Brownfield bootstrap produces 77+ files -- batch verification is essential

- Date: 2026-06-02
- Source feature: `specs/2026-05-26-day-to-day-brownfield-bootstrap/`
- Tag: skill-update
- Proposal: The bootstrap process creates a large number of files (77 in Part 1 alone). The 12-item VAL checklist (including SHA verification of copilot-instructions.md, full test suite run, TODO(human) scan) proved essential for catching issues at scale. Future bootstraps should include a machine-checkable validation script rather than relying on manual spot-checks.
- Evidence: S2 Part 1 dispatched 4 parallel workers creating files across disjoint paths. All 12 VAL items passed on first attempt, but without the checklist the SHA-match check (VAL-8) would likely have been skipped.
- Affects: `.github/skills/workflow/implement/SKILL.md`, `spec-driven-development/GENERALIZATION_SDD.md`
- Estimated effort: M
- Status: open
- Curator decision:
- PR / commit:

### LESSON-012: async def with blocking I/O is the #1 FastAPI pattern mistake

- Date: 2026-06-02
- Source feature: `specs/2026-06-01-markdown-export/` (Day-to-Day dogfood)
- Tag: skill-update
- Proposal: The two-stage code review caught an `async def` route handler calling synchronous `StatusReportCollector.collect()`. This stalls the event loop. All 60+ existing handlers in Day-to-Day use sync `def` (FastAPI threadpools them automatically). Add this as an explicit check item in the `fastapi-routes` domain skill and the `code-review` engineering skill.
- Evidence: Stage 2 review flagged this as the only finding. The fix was a one-word change (`async def` -> `def`), but the impact under concurrent load would have been significant.
- Affects: `.github/skills/domain/fastapi-routes/SKILL.md`, `.github/skills/engineering/code-review/SKILL.md`
- Estimated effort: S
- Status: open
- Curator decision:
- PR / commit:

### LESSON-013: Sprint artifacts must land in sprints/PI-N/ alongside Management/ index

- Date: 2026-06-02
- Source feature: general (PI-3 closeout)
- Tag: skill-update
- Proposal: PI-3 work was tracked in `docs/Management/PI-3/` (INDEX, SPECs, AGENT_NOTES) but the canonical `sprints/PI-3/` directory was never created. This violates the README convention that sprints/ holds per-PI ceremony artifacts (CURRENT_PI.md, lessons.md). Future PI kickoffs should create both locations in the same commit.
- Evidence: Human noticed the gap during PI-3 closeout. PI-1 and PI-2 both had `sprints/PI-N/lessons.md` but PI-3 did not.
- Affects: `.github/skills/operational/pi-planning/SKILL.md`, `spec-driven-development/sprints/README.md`
- Estimated effort: S
- Status: open
- Curator decision:
- PR / commit:
