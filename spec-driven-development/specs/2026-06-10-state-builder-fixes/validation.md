---
id: SDD-20260610STATEBUILDERFIX-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Validation Contract: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Contract Date: 2026-06-10 (SKELETON); LOCKS at F-21 after CLARIFY closes
- Author: Principal Architect (EM-routed Sprint 10 prep)
- Lock Point: `/tasks` (= F-21 close, fresh Sprint 10 session)

---

> **CONTRACT IS A SKELETON -- NOT LOCKED 2026-06-10.**
>
> **DO NOT IMPLEMENT against any REQUIRED item below until this
> contract is LOCKED at F-21** after CLARIFY closes in a fresh
> Sprint 10 session (Article VII context isolation).
>
> Placeholders below trace to the five open CLARIFY questions in
> [`clarify.md`](./clarify.md). Each REQUIRED row will be re-written
> with concrete, testable wording (specific test names, file paths,
> measurable outcomes) at F-21 by the Principal Architect after the
> owner answers Q-A through Q-E.
>
> Rule (Article X): zero unchecked REQUIRED items before
> implementation is considered complete. REQUIRED items cannot be
> loosened after lock without an explicit decision recorded here.
>
> Sprint 10 inherits the Sprint 7/8/9 owner direction: **no silent
> REQUIRED deferral.** If a REQUIRED item cannot close at F-22, the
> feature does not close and Sprint 10 does not close.

---

## Required Items (SKELETON -- LOCK AT F-21)

- [ ] **R1 (TODO at F-21) -- Active-focus signal source.** Source of
  truth for the `Active focus:` line in `state.md` is documented in
  `cli/state_builder.py` (or a colocated docstring) and implemented
  per the answer to CLARIFY Q-A (commit-recency, validation-completeness,
  sprint-frontmatter, or a combination). Concrete test names bound at
  F-21. Closes spec AC-1. Task: T-040-02.
- [ ] **R2 (TODO at F-21) -- Existing static generation preserved.**
  Non-serve invocation `python state_builder.py` produces
  byte-identical static `state.md` and `state.html` to the pre-SDD-040
  baseline (commit `8417818` reference). Verified by `diff` of the
  written artifacts against a captured baseline. Closes spec AC-4
  (half). Task: T-040-05.
- [ ] **R3 (TODO at F-21) -- Auto-refresh implemented.** Serve-mode
  dashboard auto-refresh is implemented per the mechanism chosen in
  CLARIFY Q-B (handler-side rebuild, mtime sweep / polling,
  on-request rebuild, or SSE). Concrete test name bound at F-21.
  Closes spec AC-2 (half). Task: T-040-03.
- [ ] **R4 (TODO at F-21) -- Stdlib-only constraint (Article V).**
  No new third-party dependency is added. Implementation uses only
  stdlib modules. Verified by an import audit on the diff of
  `cli/state_builder.py` and any new file. Specifically rejects
  `watchdog`, `flask`, `fastapi`, `requests`. Closes spec AC-3.
  Tasks: T-040-02, T-040-03, T-040-04.
- [ ] **R5 (TODO at F-21) -- Refresh cadence configurable via CLI
  flag.** A CLI flag on the `serve` subcommand controls refresh
  cadence with default per CLARIFY Q-C. Verified by a unit test that
  exercises the argparse surface. Closes spec AC-2 (half). Task:
  T-040-04.
- [ ] **R6 (TODO at F-21) -- Backwards compat sweep.** Existing
  tests in `cli/test_state_builder.py` pass without modification.
  Specifically, any test that exercises non-serve invocation or
  static-file output stays green. Closes spec AC-4 (half). Task:
  T-040-05.
- [ ] **R7 (TODO at F-21) -- New tests cover both defects.**
  `cli/test_state_builder.py` gains new tests covering (a) the
  active-focus signal source from R1 and (b) the auto-refresh
  mechanism from R3. Test class names bound at F-21. Closes spec
  AC-5 (half). Tasks: T-040-02, T-040-03.
- [ ] **R8 (TODO at F-21) -- Full test suite at PI-5 close baseline.**
  `python -m pytest spec-driven-development/ --tb=no -q` returns at
  least 337 passed + new tests added in R7. 2 known platform-conditional
  skips permitted. 0 failures. Closes spec AC-5 (half). Task: T-040-06.
- [ ] **R9 (TODO at F-21) -- Schema lint clean.**
  `python spec-driven-development/cli/schema_lint.py` exits 0 after
  this spec dir is fully populated. Closes spec AC-5 (half). Task:
  T-040-06.

## Optional / Best-Effort Items (SKELETON)

- [ ] **O1 (TODO at F-21) -- File-watch fallback documented.** If
  the chosen Q-B mechanism uses any OS-specific path (e.g. inotify
  on Linux), document the Windows fallback (polling via `os.stat`)
  in a docstring at the top of the auto-refresh handler.
- [ ] **O2 (TODO at F-21) -- Manual refresh trigger.** Expose a
  manual refresh trigger over HTTP (e.g. `POST /refresh` or
  `GET /refresh`) so the owner can force a rebuild without waiting
  for the cadence interval. Only ship if Q-B/Q-C answers leave room
  for it without scope creep.

## Specific Test Coverage Required (SKELETON)

- [ ] **Unit (R1)**: active-focus signal source covering each input
  branch chosen in Q-A. Files: `cli/test_state_builder.py`.
- [ ] **Unit (R3)**: auto-refresh handler covering the mechanism
  chosen in Q-B. Files: `cli/test_state_builder.py`.
- [ ] **Unit (R5)**: CLI flag parsing for refresh cadence. Files:
  `cli/test_state_builder.py`.
- [ ] **Regression (R2, R6)**: non-serve invocation produces
  byte-identical static output; existing tests stay green. Files:
  `cli/test_state_builder.py` + diff harness.
- [ ] **Import audit (R4)**: no new third-party dependency in any
  modified or new file. Files: any file touched by SDD-040 tasks.

## Manual Checks (SKELETON)

- [ ] **M1 -- Smoke test (R1).** After SDD-040 lands, regenerate
  `exec/state.md` with `python spec-driven-development/cli/state_builder.py`
  and confirm the `Active focus:` line does NOT say
  "azure-decommission". This is the smoke test from
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  section 5 item 6.
- [ ] **M2 -- Serve-mode verification (R3).** Start
  `python spec-driven-development/cli/state_builder.py serve`, edit a
  file under `specs/`, confirm the dashboard refreshes without a
  manual CLI re-run. Record the verification in the Sprint 10 close
  block at `exec/sprint-progress.md`. This is item 9 from the same
  Sprint 10 close criteria.
- [ ] **M3 -- Owner pre-push approval.** Sprint 10 inherits the
  Sprint 7/8/9 owner direction: pre-push approval is mandatory.
  Record approval evidence (owner verbatim or EM-synthesized
  decision) in the Sprint 10 close block before any push.

## Tone / UX Check

The serve-mode dashboard is the only user-facing surface SDD-040
touches. The Active focus: line wording is owner-readable. No deeper
UX work (color, layout, typography) is in scope (SDD-038, PI-6 Sprint
13). If F-21 surfaces an in-page indicator for "last refreshed at",
that copy should be reviewed against the dashboard's existing voice.

- [ ] **U1 (only if R3 mechanism includes a visible refresh
  indicator).** Refresh-state copy (e.g. "Last updated: ...",
  "Refreshing now...") is consistent with existing dashboard voice.
  Marked `[NO-UX-CHECK-NEEDED]` if R3 mechanism is invisible to the
  user.

## Definition of Done

Implementation is merge-ready only when:

1. All REQUIRED items (R1-R9) above are checked, with concrete
   test-name evidence and commit SHAs.
2. The contract was locked at F-21 (timestamp recorded in the
   F-21 close report).
3. No REQUIRED item was loosened after lock without an explicit
   decision recorded here (Article X).
4. No REQUIRED item was silently deferred (Sprint 7/8/9 carry-over
   rule).
5. Full test suite passes at PI-5 close baseline + new tests; schema
   lint exits 0; smoke test passes (M1); serve-mode verified (M2);
   owner pre-push approval recorded (M3).

Production-code changes without a corresponding test require a
task-level `[NO-TEST-NEEDED]` tag and accepted justification before
the IMPLEMENT gate can pass.
