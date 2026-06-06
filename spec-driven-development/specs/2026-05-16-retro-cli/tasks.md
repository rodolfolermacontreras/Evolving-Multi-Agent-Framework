---
id: SDD-20260516RETR-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-16-retro-cli
---

# Task List: retro.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-retro-cli/spec.md`
- Plan Reference: (inline -- small feature, no separate plan needed per Article VI)
- Task ID Format: `T-NNN` (local short IDs, date-prefixed dir)
- Owner: Principal Software Developer

---

## Status Legend

- `pending` / `in-progress` / `done` / `blocked`

## Task Breakdown

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Write test_retro.py first (red). | `cli/test_retro.py` | Proves AC1-AC8 | S | None | AFK | No | pending |
| T-002 | [S] | Implement ledger metrics, feature scanner, lessons parser, renderer. | `cli/retro.py` | Proves AC1-AC7 | M | T-001 | AFK | No | pending |
| T-003 | [S] | CLI wiring + --help + --output + manual checks. | `cli/retro.py`, `validation.md` | Proves AC8, AC9, all checkboxes | S | T-002 | AFK | No | pending |
