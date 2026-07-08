---
id: SDD-051A-validation
type: validation
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Validation Contract: SDD-051A (Doc-Freshness Sweep)

Built from `docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 4 Acceptance
("the four docs match the live repo"). REQUIRED items need real-run evidence.

## REQUIRED

- [x] **V-A1**: `docs/HIGH_LEVEL_DEV_TRACKER.md` no longer presents "Current PI:
  PI-3" or a "60/60 tests" total as current state; it reflects 7 PIs closed /
  PI-8 active and points test totals at the live source. (Snapshot rewritten;
  guard GREEN.)
- [x] **V-A2**: `INSTRUCTIONS.md` reads "12 binding articles" (not 10). (L78 edited.)
- [x] **V-A3**: `docs/ONBOARDING_KICK_OFF.md` reads 12 articles everywhere it
  cited 10; header no longer frames itself as current "PI-3 kickoff"; stale
  current-state test totals point at the live source; legitimate historical
  counts are preserved (marked where needed). (Articles table extended I-XII;
  Current PI subsection -> PI-8 pointer; PI-1 milestone lines marked.)
- [x] **V-A4**: `CONTEXT.md` reflects five roles (four Principals + Sprint
  Executive Manager) in the `Principal` definition and the roles table.
- [x] **V-A5**: no doc plants "24 ADRs"; ADR references are 23 or a pointer.
  (ONBOARDING metrics -> 23; structure diagram -> pointer.)
- [x] **V-A6**: the stale-doc guard is GREEN on the refreshed tree.
  (`staledoc_lint.py` exit 0; doctor "session-start docs fresh: ok".)
- [x] **V-A7**: `docs/RULES.md` and root `README.md` are byte-unchanged.
  (Not in `git status --short`.)

## MANUAL (checked at close)

- [x] **V-A8**: a teammate reading the four docs sees no contradiction with the
  live dashboard. (Docs point at `exec/state.html` / `exec/sprint-progress.md`
  for volatile counts.)
