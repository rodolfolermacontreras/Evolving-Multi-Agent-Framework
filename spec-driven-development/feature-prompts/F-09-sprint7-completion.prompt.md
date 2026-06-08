# F-09 -- SDD-032 Sprint 6 completion bundle (IMPLEMENT)

Worker session prompt. Load [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md)
first.

---

## Scope (brief)

- Owner: **Principal Software Developer + Developer worker**.
- **Implementation only.** The SDD-032 spec dir is fully LOCKED at
  scaffold (commit `b005e66`, 2026-06-09):
  - [`../specs/2026-06-09-sprint-6-completion/spec.md`](../specs/2026-06-09-sprint-6-completion/spec.md)
  - [`../specs/2026-06-09-sprint-6-completion/validation.md`](../specs/2026-06-09-sprint-6-completion/validation.md) (7 REQUIRED + 2 OPTIONAL, LOCKED)
  - [`../specs/2026-06-09-sprint-6-completion/plan.md`](../specs/2026-06-09-sprint-6-completion/plan.md)
  - [`../specs/2026-06-09-sprint-6-completion/tasks.md`](../specs/2026-06-09-sprint-6-completion/tasks.md) (T-032-01..06)
- Execute T-032-01 through T-032-06 in order, honoring the same-file
  serialization constraint between T-032-01 and T-032-02 (both edit
  `cli/fleet.py`).
- Close all 4 deferred LOCKED REQUIRED items from Sprint 6: SDD-019.R7
  (queue), SDD-019.R8 (grandfather), SDD-020.R6 (log writers),
  SDD-020.R8 (prompt hooks).
- **All 7 REQUIRED items must close** (`R1..R7`). **No deferral
  permitted** per owner direction 2026-06-08 (Option 3 hybrid). If a
  REQUIRED item cannot close, F-09 does not close -- escalate to the
  owner via the EM.
- Final close commit references all four parent R-items
  (SDD-019.R7, SDD-019.R8, SDD-020.R6, SDD-020.R8) and verifies the
  Sprint 6 lock surface is preserved (commits `524872b` and `8eb564d`
  not modified beyond additive integration points).

## Optional pull-in

- SDD-033 (HOST-INTEGRATION.md docs refresh, P3) may be pulled into the
  F-09 close-out if capacity permits. Doc-only; no code touched.
  Decision is F-09's; document it in the close commit body.

---

> **FULL CONTENT AUTHORED AT F-09 SESSION START** -- this is a stub
> placeholder so the file exists and the kickoff prompt can reference it.
> The full task-by-task execution plan, fleet-vs-serial dispatch decision
> for T-032-03 vs T-032-04/05, QA checklist, BACKLOG-update script,
> state-regen step, and close-commit template are authored by the SW Dev
> at the start of the F-09 session, after re-reading the four LOCKED
> spec-dir artifacts.
