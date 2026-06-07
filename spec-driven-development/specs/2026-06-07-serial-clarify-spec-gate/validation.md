---
id: SDD-20260607SERIAL-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Validation Contract: Serial Gate on CLARIFY/SPEC (SDD-019)

- Spec ID: SDD-019
- Status: SKELETON -- contract NOT locked. Locks at /tasks.
- Rule (when locked): zero unchecked REQUIRED items before implementation is
  considered complete.

> **DO NOT IMPLEMENT until this contract is locked.** All REQUIRED items
> below are TODO placeholders pending CLARIFY answers. Each placeholder
> names the CLARIFY question(s) it traces to so /spec finalization can
> resolve them in one pass.

---

## Required Items (TODO -- locked at /tasks)

- [ ] R1. TODO -- enforcement mechanism behaves per CLARIFY Q3 (advisory
  vs hard refusal vs hybrid). Test: dispatching a second CLARIFY while
  another holds the lock produces the agreed-upon behavior.
- [ ] R2. TODO -- gate granularity per CLARIFY Q1 (per-phase vs per-repo).
  Test: two features in different phases either may or may not coexist
  per the CLARIFY decision.
- [ ] R3. TODO -- lock-state source-of-truth per CLARIFY Q2. Test: lock
  state can be derived deterministically from artifact frontmatter (or
  the ledger, per CLARIFY).
- [ ] R4. TODO -- override path per CLARIFY Q4. Test: force-release
  subcommand (or chosen alternative) writes the agreed audit record and
  allows subsequent dispatch.
- [ ] R5. TODO -- constitutional amendment shipped per CLARIFY Q5
  (Article VII extension / new Article VIII / decision-policy amendment).
  Test: schema_lint accepts the amended constitution; version bump
  recorded.
- [ ] R6. TODO -- multi-worker batch semantics per CLARIFY Q6. Test:
  intra-feature parallel workers proceed; inter-feature parallel workers
  in the same phase are refused.
- [ ] R7. TODO -- queue ordering per CLARIFY Q7. Test: simulated queue of
  3+ features releases in the agreed order.
- [ ] R8. TODO -- backwards compatibility per CLARIFY Q8. Test: spec dirs
  already open at enforcement-turn-on behave per the migration rule.
- [ ] R9. TODO -- out-of-scope phases per CLARIFY Q9 stay parallelizable.
  Test: /plan, /tasks, /implement, /qa, /retro dispatch is not gated.
- [ ] R10. TODO -- full existing test suite passes (no regression).
  Sprint 5 baseline: 213 tests.
- [ ] R11. TODO -- schema_lint stays clean.

## Optional / Best-Effort Items (TODO)

- [ ] O1. TODO -- dashboard widget surfaces current lock holder + queue.
- [ ] O2. TODO -- ledger contains `lock_acquired` / `lock_released` event
  rows for every transition.

## Notes

- Contract is SKELETON. Required-item count and exact wording will change
  at /spec finalization once CLARIFY answers land.
- ADR (separate file) must accompany this validation contract before any
  `constitution/` edit. ADR drafting is BLOCKED until CLARIFY closes.
- Lock the contract at /tasks; do not loosen REQUIRED items after lock
  without an explicit decision recorded here.
