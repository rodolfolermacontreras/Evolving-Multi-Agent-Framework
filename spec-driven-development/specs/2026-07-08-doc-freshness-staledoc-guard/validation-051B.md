---
id: SDD-051B-validation
type: validation
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Validation Contract: SDD-051B (Stale-Doc Guard)

Built from `docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 4 Acceptance
("a new stale-doc doctor/lint check exists, is wired into the doctor set, and
goes RED ... proven by a deliberate red").

## REQUIRED

- [x] **V-B1**: `cli/staledoc_lint.py` exists, is stdlib-only (argparse,
  dataclasses, pathlib, re, sys + sibling `governance_check`), and exposes
  `main(argv)`. (test_sdd045 `test_staledoc_lint_stdlib_only` PASS.)
- [x] **V-B2**: the guard verifies a session-start doc's article count against
  the live count from `principles.md` and fails on an unmarked mismatch.
  (`TestArticleCount` PASS; live deliberate-red flagged INSTRUCTIONS "10".)
- [x] **V-B3**: the guard verifies a session-start doc's `Current PI: PI-N`
  against the live active PI and fails on an unmarked mismatch. (`TestCurrentPi`
  PASS; live deliberate-red flagged tracker "PI-3".)
- [x] **V-B4**: the guard scopes to the four session-start docs and honors the
  inline `<!-- staledoc-ok -->` marker. (`TestScope` + marker tests PASS.)
- [x] **V-B5**: `doctor` (`run_doctor`) includes the guard as a check tuple;
  the doctor set (and CI) enforces it. (doctor "session-start docs fresh: ok".)
- [x] **V-B6**: a test plants a deliberate stale count and asserts the guard
  goes RED; the guard is GREEN on the refreshed tree. (`test_main_nonzero_on_stale`
  + live: 9 findings pre-refresh -> 0 post-refresh.)

## MANUAL (checked at close)

- [x] **V-B7**: `TestS1FootprintLockGuard` PASS (3 passed); no locked function
  touched.
- [x] **V-B8**: full suite 590 passed / 2 skipped (up from 576); schema lint +
  origin lint clean (exit 0); doctor green.
