---
sprint: PI-3 / S-3
title: pi2-lessons-curation
owner: principal-executive-manager (dispatch), 7 parallel workers
last_updated: 2026-05-26
status: DONE
---

# Agent Notes -- PI-3 / Sprint-3

Ground-truth notes from agents who actually did the work. The *why*, *what
surprised us*, *what worked*, *what didn't*, and *what is worth remembering*.
Not a status report; a working journal.

## Session log
- 2026-05-26: All 7 parallel tasks dispatched simultaneously.
  - T-001: CLOSE LESSON-004 retrospectively (commit `3d19114`)
  - T-002: SHIP LESSON-006 -- constitution-sync v1.0->1.1, stale-marker detection (commit `f8f446e`)
  - T-003: DEFER LESSON-007 to S4 (commit `f8f446e`)
  - T-004: SHIP LESSON-008 -- to-spec v1.0->1.1, canonical-declaration prompt (commit `b33347b`)
  - T-005: SHIP LESSON-009 -- testing-conventions v1.0->1.1, Windows fixtures (commit `0c65468`)
  - T-006: SHIP LESSON-010 -- already present in azure-deployment-architecture skill, closed retrospectively (commit `54602f5`)
  - T-007: Tech debt sweep -- filed `specs/2026-05-26-principal-agent-hygiene/spec.md` for PI-4 (commit `0e1f7a5`)
- T-008: Closure -- tracker + INDEX updated, schema_lint clean, 60/60 tests passing.

## Surprises
- LESSON-010 fix was already in the azure-deployment-architecture skill (applied during PI-2 work). No edit needed, just retrospective closure.
- T-002 and T-003 landed in the same commit because they both edited lessons.md. Git merged them cleanly but the commit message only references T-003.

## What worked
- 7-way parallel dispatch with zero file conflicts. Each task targeted a different skill file.
- Status updates in lessons.md converged correctly despite multiple agents editing the same file sequentially.
- Schema lint verified no frontmatter regressions across all 28 skills.

## What didn't
- Some workers flagged "committing directly to master conflicts with standing rules" -- the dispatch should have explicitly noted this is EM-authorized direct-to-master work for docs-only changes.

## To remember
- When dispatching parallel workers that edit the same file (lessons.md), commits serialize automatically via git but commit messages may conflate changes. Consider separate files or explicit commit ordering for cleaner history.
