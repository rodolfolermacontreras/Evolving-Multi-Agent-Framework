---
id: SDD-051-clarification
type: clarification
status: done
owner: principal-architect
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Clarification Log: SDD-051

Owner unavailable at CLARIFY (2026-07-08); Sprint EM proceeded on the kickoff's
default recommendations with two live-source findings surfaced for review at
close. All decisions defensible under "work autonomously and make good
decisions."

## Q-A -- stale-doc check mechanism

- **Decision**: MIXED per count kind. Verify-against-source for the two cheap,
  exact counts that caused the audit defects: **article count** (from
  `principles.md`) and **current PI** (from the active `CURRENT_PI.md`).
  Test totals are handled by the durable fix (drop, point at live), NOT by a
  regex flag, to avoid Q-C false positives on the origin-story and code-map
  test-count lines.
- **Rationale**: the kickoff itself notes verify-against-source where cheap
  (article count) and avoid flagging a moving test count. Article + current PI
  are exact and directly catch the "10 articles" and "PI-3" defects.

## Q-B -- where the check lives

- **Decision**: new stdlib `cli/staledoc_lint.py` with `main(argv)`, called by
  `doctor` (`run_doctor`), mirroring the `origin_lint` / `governance_check`
  pattern. Wired into the doctor set so CI enforces it automatically.

## Q-C -- avoiding false positives

- **Decision**: scope to the four session-start docs only; honor an inline
  `<!-- staledoc-ok -->` marker to exempt legitimate historical count lines
  (e.g. the Day-to-Day origin story "743+ tests"). The guard does not scan every
  `N tests` occurrence (see Q-A).

## Q-D -- stop hardcoding vs keep-count-plus-guard

- **Decision**: drop moving counts (test totals, ADR count) and point at the
  live source (root `README.md` good pattern); keep the stable structural counts
  (12 articles, five roles, current PI) as concrete numbers backed by the guard.

## Q-E -- the live counts to write (verified against source 2026-07-08)

- Articles: **12** (principles.md Article I..XII) -- verified.
- ADRs: **23** numbered (`001`-`023`), NOT 24 as the kickoff literal said.
  **FINDING surfaced**: write 23 or point at the ADR dir; do not plant 24.
- PIs: **7 closed (PI-1..7), PI-8 active** -- verified from CURRENT_PI.md.
- Roles: **five** (four Principals + Sprint Executive Manager, ADR-020).
- Tests: 576 (2 skipped) at kickoff; a moving count -> dropped from docs,
  pointed at live source per Q-D (grows with the guard test this sprint).

## Findings surfaced for owner review at close

1. **ADR count is 23, not 24** (kickoff literal was stale). Docs write 23 or a
   pointer.
2. **CONTEXT.md has no literal "four Principal agents" string** -- it enumerates
   exactly four Principals in the `Principal` definition and the roles table with
   no Sprint EM row. The refresh adds the Sprint EM as the fifth role in both
   places.
