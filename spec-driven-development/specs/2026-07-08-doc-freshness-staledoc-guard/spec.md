---
id: SDD-051-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Feature Spec: Doc-Freshness Sweep + Automated Stale-Doc Guard (SDD-051)

## Context

PI-8 ("Truth in the Window") makes the human-facing surfaces as trustworthy as
the engine. Sprint 18 (SDD-050) fixed the dashboard. Sprint 19 (SDD-051) fixes
the session-start docs a teammate reads first and adds an automated guard so the
rot cannot return silently.

Spec source: `docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 4
("Doc staleness"). Each requirement's acceptance is carried into the per-item
`validation-*.md` files.

## Per-item SDD-IDs

CLARIFY split SDD-051 into two distinct surfaces, each with its own validation:

- **SDD-051A** -- Doc-freshness sweep: refresh the four stale session-start docs.
- **SDD-051B** -- Stale-doc guard: a new `cli/staledoc_lint.py` wired into
  `doctor`, plus a deliberate-red test.

## Goals

- Bring the four session-start docs into agreement with the live repo.
- Add a mechanical guard that goes RED when a session-start doc carries a stale
  hardcoded count, proven by a deliberate red.
- Prefer the durable fix (drop a count that rots, point at the live source) over
  a hardcoded number wherever the number adds no onboarding value.

## Non-goals

- No dashboard/detector work (SDD-050, done).
- No roadmap repair, PI-6 backfill, spec-dir status backfill, or PI-7 4-feature
  checklist backfill (SDD-052, Sprint 20).
- No `constitution/**` edits. The guard READS the article count from
  `principles.md` but never modifies it.
- No Article X locked-function edits (`render_html`, `render_markdown`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
  `load_decisions`).
- `docs/RULES.md` and root `README.md` are verified-clean and left byte-unchanged.

## Requirements

### SDD-051A -- Doc-freshness sweep

- **R-A1**: `docs/HIGH_LEVEL_DEV_TRACKER.md` no longer reads "Current PI: PI-3"
  or "60 tests / 60 of 60" as current state. It reflects 7 PIs closed / PI-8
  active. Moving counts (test totals) point at the live dashboard / `exec/state.md`
  rather than a hardcoded number (durable fix, Q-D).
- **R-A2**: `INSTRUCTIONS.md` (root) reads "12 binding articles" (I-XII), not
  "10 binding articles".
- **R-A3**: `docs/ONBOARDING_KICK_OFF.md` reads 12 articles (I-XII) everywhere it
  cited 10; its header no longer frames the doc as "PI-3 kickoff" current state;
  stale current-state test totals ("70 passing") point at the live source.
  Legitimate historical / cross-project counts (the Day-to-Day origin story
  "743+ tests", the specialist-promotion "70 tests") are preserved as history and
  carry an inline `<!-- staledoc-ok -->` marker where the guard would otherwise
  read them.
- **R-A4**: `CONTEXT.md` reflects five roles (four Principals + the Sprint
  Executive Manager added by the two-tier EM, ADR-020), not four Principal agents.
- **R-A5**: The ADR count, where a doc cites one, is the verified live count
  (23 numbered ADRs, `001`-`023`) or points at the ADR directory. No doc plants
  "24".

### SDD-051B -- Stale-doc guard

- **R-B1**: A new stdlib-only `cli/staledoc_lint.py` exposes `main(argv)` and,
  given the framework root, scans the four session-start docs for stale counts.
- **R-B2 (verify-against-source, article count)**: the guard reads the live
  article count from `constitution/principles.md` (reusing
  `governance_check.count_articles`) and fails when a session-start doc's
  hardcoded article count (decimal `N articles` or roman range `(I-ROMAN)`)
  disagrees, unless the line carries the `<!-- staledoc-ok -->` marker.
- **R-B3 (verify-against-source, current PI)**: the guard reads the live active
  PI from `sprints/PI-*/CURRENT_PI.md` and fails when a session-start doc's
  hardcoded `Current PI: PI-N` disagrees, unless the line carries the marker.
- **R-B4 (false-positive safety, Q-C)**: the guard scopes to the four
  session-start docs only, and honors the inline `<!-- staledoc-ok -->` marker so
  a legitimate historical count does not trip it. The guard deliberately does NOT
  regex every `N tests` occurrence -- test totals move every sprint and per-file
  code-map counts are granular, so flagging them would false-positive on the
  origin-story and code-map lines; stale test totals are handled by R-A1/R-A3
  (durable fix) instead. This is the Q-A per-claim decision: verify-against-source
  where cheap and exact (article, current PI); drop-and-point-at-live where the
  count rots (test totals).
- **R-B5 (doctor wiring)**: `doctor` (`cli/bootstrap.py run_doctor`) calls the
  guard as a new lettered check tuple `(label, ok, detail)` so CI enforces it via
  the doctor set (the single source of truth for CI).
- **R-B6 (deliberate red)**: a test plants a stale count in a fixture / temp doc
  and asserts the guard goes RED; the guard is GREEN on the refreshed live tree.

## Acceptance criteria

- The four docs match the live repo (PI count, article count, role count); ADR
  count is 23 or a pointer, never 24.
- `cli/staledoc_lint.py` exists, is stdlib-only, exposes `main(argv)`, and is
  wired into the doctor set.
- The guard goes RED on a deliberate planted stale article-count or current-PI
  claim, and GREEN on the refreshed tree.
- `docs/RULES.md` (Articles I-XII) and root `README.md` (count-free) are
  byte-unchanged.
- Suite grows with the guard test; `python -m pytest spec-driven-development/`
  returns >= 576 passed, 2 skipped; schema lint and origin lint clean; doctor
  green; `TestS1FootprintLockGuard` PASS.

## Traceability

| Req | Validation item | Audit Section 4 acceptance |
|-----|-----------------|----------------------------|
| R-A1..R-A5 | validation-051A.md | "the four docs match the live repo" |
| R-B1..R-B6 | validation-051B.md | "a new stale-doc doctor/lint check exists, is wired, goes RED (deliberate red)" |
