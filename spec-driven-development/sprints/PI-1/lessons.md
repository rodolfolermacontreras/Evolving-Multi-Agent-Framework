# Lessons: PI-1

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

### LESSON-004: Define ledger migration policy before v0.2

- Date: 2026-05-12
- Source feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`
- Tag: docs-update
- Proposal: Add a short ledger migration policy before the next schema change, including version table expectations, migration file naming, rollback posture, and whether Level 2 approval is required for each migration.
- Evidence: Fleet Ledger v0.1 intentionally avoided migrations, but the first follow-up field addition will otherwise require ad hoc schema evolution decisions.
- Affects: `spec-driven-development/ledger/`, `spec-driven-development/constitution/principles.md`, future ledger docs or templates
- Estimated effort: S
- Status: curated-defer
- Curator decision: DEFER to PI-2. No schema change is imminent; define when cli/fleet.py drives the first real migration need.
- PR / commit: n/a (deferred)

### LESSON-003: Reduce validation prose duplication

- Date: 2026-05-12
- Source feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`
- Tag: template-update
- Proposal: Add a quick-fill guide or tighter cross-reference pattern so spec acceptance criteria, plan validation criteria, task acceptance tests, and validation contract checkboxes can reference the same canonical requirement ids without rewriting the same sentence four times.
- Evidence: The pilot benefited from validation-first work, but repeated the same AC/test mapping across `spec.md`, `plan.md`, `tasks.md`, and `validation.md`.
- Affects: `spec-driven-development/templates/feature-spec.md`, `spec-driven-development/templates/plan.md`, `spec-driven-development/templates/task-list.md`, `spec-driven-development/templates/validation.md`
- Estimated effort: M
- Status: curated-ship
- Curator decision: SHIP. Cross-reference blockquotes added to plan, task-list, and validation templates.
- PR / commit: bb5a762

### LESSON-002: Clarify task id convention inside feature directories

- Date: 2026-05-12
- Source feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`
- Tag: template-update
- Proposal: Clarify whether task ids should use global `T-{spec-date}-{NNN}` ids or local feature ids like `T-001` when the feature directory already carries the date-prefixed namespace.
- Evidence: The task template prescribes `T-{spec-date}-{NNN}`, while the pilot requested `T-001` through `T-00N`; both are understandable but inconsistent.
- Affects: `spec-driven-development/templates/task-list.md`, task-writing prompts
- Estimated effort: S
- Status: curated-ship
- Curator decision: SHIP. Task ID convention note added to task-list template; local short IDs allowed inside date-prefixed dirs.
- PR / commit: 2d5d729

### LESSON-001: Add a Python stdlib CLI utility pattern

- Date: 2026-05-12
- Source feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`
- Tag: docs-update
- Proposal: Document a small canonical pattern for framework Python utilities using `argparse`, `pathlib`, explicit `main(argv) -> int`, and testable functions, with optional SQLite helpers.
- Evidence: ECHO's `bootstrap.py` provided style hints, but the ledger CLI still had to derive its own conventions for subcommands, default paths, and import boundaries.
- Affects: `spec-driven-development/cli/`, future developer docs or templates
- Estimated effort: S
- Status: curated-ship
- Curator decision: SHIP. CLI-PATTERN.md created in docs/ with skeleton and 10 rules extracted from 3 proven scripts.
- PR / commit: 8ee6840
