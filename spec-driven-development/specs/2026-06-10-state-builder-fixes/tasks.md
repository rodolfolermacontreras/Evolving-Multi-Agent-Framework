---
id: SDD-20260610STATEBUILDERFIX-tasks
type: tasks
status: active
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Task List: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Plan Reference: [`plan.md`](./plan.md)
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slot F-21 (CLARIFY/SPEC/PLAN/TASKS) + F-22 (IMPLEMENT)
- Author: Principal Architect (EM-routed Sprint 10 prep)
- Date: 2026-06-10
- Test baseline: 337 (PI-5 close, commit `8417818`)

---

> **SKELETON TASKS -- 2026-06-10.** Task IDs and one-line
> descriptions are final at scaffold. Full task content (concrete
> file scope lines, exact test names, verification commands) is
> authored at F-21 by the Principal Architect after CLARIFY closes
> and the validation contract LOCKS.
>
> **Task ID convention:** Local short IDs `T-040-NN` used within
> this date-prefixed feature directory.
>
> **No silent REQUIRED deferral.** Sprint 10 inherits the Sprint
> 7/8/9 owner direction: if a REQUIRED item in
> [`validation.md`](./validation.md) cannot close at F-22, the
> feature does not close and Sprint 10 does not close.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown (SKELETON)

| Task ID | Description (SKELETON) | File Scope (TBD at F-21) | Acceptance Test (TBD at F-21) | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|------------------------|--------------------------|-------------------------------|----------------|------|-----------------|-------------------------|--------|
| T-040-01 | Read existing `cli/state_builder.py` active-focus path (`derive_next_action` line 562) and existing serve subcommand (`DashboardHandler.do_GET` line 2358; `serve` line 2385); document the current heuristic and current refresh behavior in this `tasks.md` as the baseline against which T-040-02 and T-040-03 measure delta. | (read-only): `cli/state_builder.py`; (write): this `tasks.md` (baseline block appended) | proves baseline captured; gates F-22 implementation start | S | none | AFK | No (documentation; not parallelizable with implementation) | pending |
| T-040-02 | Implement new active-focus heuristic per CLARIFY Q-A. Add an additive helper (signal-source TBD at F-21) prepended to `derive_next_action`; preserve existing fallback chain. Add new test class `TestActiveFocusHeuristic` (exact name TBD) in `cli/test_state_builder.py`. | `cli/state_builder.py` (additive helper + prepend call); `cli/test_state_builder.py` (new test class) | proves AC-1; closes R1; closes R7 (half); new tests pass | S | T-040-01 | AFK | No (serial with T-040-03/04 on `state_builder.py`) | pending |
| T-040-03 | Implement auto-refresh handler in serve subcommand per CLARIFY Q-B. Mechanism (handler-side meta-refresh, polling, mtime sweep on background thread, or SSE) bound at F-21. Preserve existing `DashboardHandler.do_GET` body; layer additively. Add new test class `TestAutoRefreshHandler` (exact name TBD) in `cli/test_state_builder.py`. | `cli/state_builder.py` (additive handler logic); `cli/test_state_builder.py` (new test class) | proves AC-2 (mechanism half); closes R3; closes R7 (half); new tests pass | M | T-040-01 (read-only baseline) | AFK | No (serial with T-040-02/04 on `state_builder.py`) | pending |
| T-040-04 | Wire CLI flag for refresh cadence per CLARIFY Q-C. New argparse argument on `sub_serve` (near line 2784); default cadence TBD at F-21. Add new test `TestRefreshCadenceFlag` (exact name TBD) in `cli/test_state_builder.py`. | `cli/state_builder.py` (argparse addition); `cli/test_state_builder.py` (new test) | proves AC-2 (cadence half); closes R5; new tests pass | S | T-040-03 (cadence is meaningful only with auto-refresh present) | AFK | No (serial with T-040-02/03 on `state_builder.py`) | pending |
| T-040-05 | Regression sweep: verify non-serve invocation produces byte-identical static `state.md` and `state.html` against the pre-SDD-040 baseline (commit `8417818`). Verify all existing tests in `cli/test_state_builder.py` stay green. Run import audit to confirm no new third-party dependency. | (verification only): `exec/state.md`, `exec/state.html` diff vs baseline; `cli/test_state_builder.py` existing tests; import audit on `cli/state_builder.py` diff | proves AC-3 (stdlib) + AC-4 (backwards compat); closes R2, R4, R6 | S | T-040-02, T-040-03, T-040-04 | AFK | No (verification step; depends on all implementation tasks) | pending |
| T-040-06 | Sprint 10 F-22 close verification: (a) full pytest run (>= 337 + new tests); (b) `python spec-driven-development/cli/schema_lint.py` exit 0; (c) regenerate `exec/state.md` + `exec/state.html` + `exec/work-index.md` with the new builder; (d) **smoke test M1**: confirm regenerated `state.md` does NOT say "Active focus: azure-decommission"; (e) **manual M2**: serve-mode auto-refresh verification (start `serve`, edit a `specs/**` file, confirm refresh without manual re-run); (f) audit all REQUIRED items in [`validation.md`](./validation.md) -- 100% checked, no DEFERRED markers; (g) commit chain documented; (h) **owner pre-push approval recorded (M3)** before push. | (verification only): pytest; schema_lint; state_builder regen; smoke + manual checks; validation.md audit; close commit `close(sprint-10-f-22): SDD-040 state_builder fixes DONE` referencing R1-R9 and CLARIFY Q-A..Q-E answers | proves AC-5; closes R7 (verification half), R8, R9; M1, M2, M3 all recorded; **no DEFERRED markers permitted per Sprint 7/8/9 carry-over rule** | S | T-040-01, T-040-02, T-040-03, T-040-04, T-040-05 | HITL (owner reviews smoke test result + serve-mode manual verification before push) | No (verification + close commit + owner-gated push) | pending |

## Dependency Graph (SKELETON)

```
T-040-01 (baseline doc) -> T-040-02 (parser fix) -+
                        -> T-040-03 (auto-refresh) -> T-040-04 (cadence flag) -+
                                                                               |
                                                                               +-> T-040-05 (regression) -> T-040-06 (close)
```

All tasks serialize within the same file (`cli/state_builder.py`)
and within the same session (single F-22 implementation session per
[`plan.md`](./plan.md) Approach Summary).

## Batch Plan (SKELETON)

- **Batch 0 (F-21):** CLARIFY round answers Q-A..Q-E; PM + Architect
  finalize spec.md / validation.md / plan.md / tasks.md; validation
  contract LOCKS.
- **Batch 1 (F-22):** T-040-01 -> T-040-02 -> T-040-03 -> T-040-04
  -> T-040-05 -> T-040-06 (sequential, single session).
- **Batch 2 (F-23):** Sprint 10 close + SPRINT-11-KICKOFF.prompt.md
  authoring (owned by Principal SW Dev + EM, not in this tasks.md).

## Constraints (carry-over from plan.md "Lock-Surface Protections")

Implementers MUST NOT modify the existing bodies of:

- `render_markdown` (line 528 in `cli/state_builder.py`) -- SDD-002
  canonical 7-section format.
- `derive_next_action` (line 562) -- existing fallback chain
  (IMPLEMENT > REVIEW > PI > backlog) preserved; new helper prepended
  only.
- `DashboardHandler._send` (line 2342) -- security headers (REC-2)
  preserved.
- `DashboardHandler.do_GET` (line 2358) -- existing body preserved;
  auto-refresh layered additively.
- `serve` (line 2385) -- existing body preserved; cadence flag
  plumbed through existing argparse surface.
- Any existing test class or test name in
  `cli/test_state_builder.py`.
- `constitution/` (no constitution edit expected; route via ADR if
  CLARIFY surfaces one, per `SPRINT-10-KICKOFF.prompt.md` Hard
  Constraints item 4).
- `cli/state_builder.py` outside the four additive sites enumerated
  in [`plan.md`](./plan.md) File Scope.

## Notes

- Maximum task count budget: 9 (per EM prep guidance). Actual: **6**.
- Owner review (HITL) required at T-040-06 for the two manual-check
  items in [`validation.md`](./validation.md) M1 + M2 and the
  pre-push approval gate M3.
- **Carry-over policy:** if any task surfaces a CLARIFY answer that
  needs revision (e.g. Q-B mechanism doesn't work on a particular OS
  test target), mark "OWNER GUIDANCE REQUIRED" in
  [`spec.md`](./spec.md) Open Questions and STOP that task. Do not
  invent an answer. Do not silently widen scope.
- **Fleet dispatch decision:** SDD-040 is single-file, small-diff,
  one-session work; fleet dispatch is NOT justified per Article VII
  and per [`plan.md`](./plan.md) Approach Summary. All tasks run
  AFK (or HITL for T-040-06) in the same F-22 session.
