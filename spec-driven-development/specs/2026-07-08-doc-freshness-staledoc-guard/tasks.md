---
id: SDD-051-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: doc-freshness-staledoc-guard
sprint: PI-8 / Sprint 19
---

# Task List: SDD-051

Sequential [S] (shared surfaces force serialization). TDD: T-01 before T-02.

| Task | Tag | Files | Req | Verify |
|------|-----|-------|-----|--------|
| T-01 write failing guard tests | [S] | `cli/test_staledoc_lint.py` (new) | R-B1,R-B2,R-B3,R-B4,R-B6 | tests fail RED before T-02 |
| T-02 implement staledoc_lint | [S] | `cli/staledoc_lint.py` (new) | R-B1,R-B2,R-B3,R-B4 | T-01 tests pass GREEN |
| T-03 wire guard into doctor | [S] | `cli/bootstrap.py` (additive) | R-B5 | doctor shows the check; wiring test passes |
| T-04 refresh tracker | [S] | `docs/HIGH_LEVEL_DEV_TRACKER.md` | R-A1,R-A5 | no "PI-3" current / "60 tests"; guard GREEN |
| T-05 refresh INSTRUCTIONS | [S] | `INSTRUCTIONS.md` | R-A2 | "12 binding articles"; guard GREEN |
| T-06 refresh ONBOARDING | [S] | `docs/ONBOARDING_KICK_OFF.md` | R-A3,R-A5 | 12 articles; header reframed; guard GREEN |
| T-07 refresh CONTEXT | [S] | `CONTEXT.md` | R-A4 | five roles incl Sprint EM; guard GREEN |
| T-08 validation + close | [S] | validation-051A/B, exec/sprint-progress.md, ledger | all | suite >=576; doctor green; lock PASS |

## Traceability

- R-A1,R-A5 -> T-04; R-A2 -> T-05; R-A3,R-A5 -> T-06; R-A4 -> T-07
- R-B1..R-B4 -> T-01,T-02; R-B5 -> T-03; R-B6 -> T-01,T-08

## Notes

- Guard-first (T-01/T-02/T-03) so the deliberate-red proof exists before the
  refresh; then the refresh (T-04..T-07) is validated by a green guard.
- Do NOT touch `docs/RULES.md` or root `README.md`.
