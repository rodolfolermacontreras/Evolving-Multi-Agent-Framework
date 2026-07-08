---
id: SDD-051-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Implementation Plan: SDD-051

## Approach

TDD, guard-first. Build and prove the stale-doc guard (SDD-051B) against a
fixture BEFORE refreshing the docs, so the deliberate-red test lands first and
the refresh is validated by a green guard. Serial single-session execution (no
fleet dispatch): shared surfaces (`bootstrap.py`, the four docs, the guard
module) force serialization per the sprint sequence.

## Phases

### Phase 1 -- SDD-051B guard (TDD)

1. Write `cli/test_staledoc_lint.py` first (RED): plants a stale article count
   and a stale `Current PI: PI-N` in a temp doc; asserts findings. Asserts a
   clean doc and a marked line produce no findings.
2. Implement `cli/staledoc_lint.py`: stdlib-only; `SESSION_START_DOCS` tuple;
   `live_article_count(root)` (reuse `governance_check.count_articles`);
   `live_current_pi(root)` (mirror `bootstrap.current_pi_name`); `scan(root)`
   returning findings; `main(argv)` printing findings and returning 0/1.
3. Marker: inline `<!-- staledoc-ok -->` on a line exempts that line.

### Phase 2 -- doctor wiring

4. Add a `(label, ok, detail)` check tuple to `run_doctor` in
   `cli/bootstrap.py` that calls `staledoc_lint.scan(root)` (framework checkout
   only), mirroring the origin-lint wiring. Add guard tests in
   `cli/test_bootstrap.py` or `cli/test_staledoc_lint.py` for the wiring.

### Phase 3 -- SDD-051A doc refresh

5. Refresh the four docs (see per-doc edit list in tasks.md) to the verified
   live counts. Drop moving counts (test totals) and point at the live source;
   mark legitimate historical counts with `<!-- staledoc-ok -->`.
6. Verify `docs/RULES.md` and root `README.md` are untouched.

### Phase 4 -- validation + close

7. Run the guard on the refreshed tree (GREEN); run full suite, schema lint,
   origin lint, doctor, lock guard. Check off validation-051A / validation-051B.
   Log dispatches in the ledger (B-1 dogfood). Append the sprint-close block.

## File plan (no two tasks share a file)

| File | Task | Kind |
|------|------|------|
| `cli/test_staledoc_lint.py` | T-01 (test-first) | new |
| `cli/staledoc_lint.py` | T-02 | new |
| `cli/bootstrap.py` | T-03 (doctor wiring) | edit (additive) |
| `docs/HIGH_LEVEL_DEV_TRACKER.md` | T-04 | edit |
| `INSTRUCTIONS.md` | T-05 | edit |
| `docs/ONBOARDING_KICK_OFF.md` | T-06 | edit |
| `CONTEXT.md` | T-07 | edit |

## Constraints

- Stdlib-only (Article V): argparse, pathlib, re, sys.
- Article X locked functions untouched; `TestS1FootprintLockGuard` stays GREEN.
- No `constitution/**` edits (guard reads principles.md, never writes).
- Explicit-path git staging only; owner pre-push approval required.
