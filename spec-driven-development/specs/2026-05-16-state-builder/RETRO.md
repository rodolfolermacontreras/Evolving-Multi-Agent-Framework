# Retrospective: state_builder.py (SDD-002)

- Date: 2026-05-16
- PI/Sprint: PI-2 / Sprint A
- Status: DONE
- Test count: 9 of 10 ACs covered by automated tests (AC9 is manual `--help`, verified)

---

## What worked

- **TDD scaffolding via tmp_path:** The `make_minimal_sdd_root` helper seeds a complete miniature SDD root in a temp dir (constitution, specs, backlog, roster, ledger.db). All 9 SDD-002 ACs run against that synthetic root in under 3 seconds. Tests do not touch the real repo state.
- **Convergent implementation:** SDD-002 (the canonical state.md spec) and the parallel state-dashboard work (live HTML + Bridge UX) shipped from a single CLI. Shared data loaders, two renderers (markdown + html), one CLI entry.
- **Deterministic mode unlocked clean tests:** Adding `fixed_date` parameter to `build()` made AC7 (byte-identical output) trivially testable.

## What did not work

- **State-builder spec was authored in parallel to state-dashboard.** Two specs for the same implementation file (`cli/state_builder.py`) landed in the same session. Reconciled by treating SDD-002 as the canonical `state.md` contract and state-dashboard as the additive HTML/live-server feature. They share the file but cover disjoint scopes.

## Lesson candidate (for /evolve)

- **LESSON-008:** When two parallel specs target the same implementation file, declare one as canonical for the file's primary contract and treat the other as additive scope. Cross-reference both validation contracts from the implementation file's header docstring.

## Validation

All 9 automated AC tests in `cli/test_state_builder.py` green. Manual `--help` verified.
