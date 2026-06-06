---
id: SDD-20260526LIVE-retro
type: retro
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-26-live-ui-v2
---

# Retrospective: Live UI v2

**Feature**: Live UI v2 (sprint-first dashboard layout)
**PI**: PI-4, Sprint 1
**Shipped**: 2026-06-02

## What was delivered

- Complete rewrite of state_builder.py HTML renderer from v2 (4-zone) to v3.0 (7-section sprint-first grid)
- 4 new data-layer functions: load_sprint_table, load_sprint_goal, detect_current_sprint, load_decisions
- 59 CSS custom properties from DESIGN_TOKENS.md
- Accessibility: single h1, ARIA landmarks, skip-to-main, prefers-reduced-motion, CSP meta
- 90 tests (up from 29 baseline)

## What went well

- TDD approach: tests written before implementation for each phase
- Two-stage code review caught SQLite connection leak before merge
- Design tokens spec (DESIGN_TOKENS.md) prevented ad-hoc styling decisions

## What to improve

- RETRO.md should be created as part of the review gate, not retroactively
- Spec status lines should be updated to "done" at merge time
