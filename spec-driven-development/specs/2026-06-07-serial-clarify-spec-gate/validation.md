---
id: SDD-20260607SERIAL-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Validation Contract: Serial Gate on CLARIFY/SPEC (SDD-019)

- Spec ID: SDD-019
- Status: LOCKED at /tasks 2026-06-07
- Rule: zero unchecked REQUIRED items before implementation is
  considered complete. REQUIRED items cannot be loosened after lock
  without an explicit decision recorded here (Article X).

---

## Required Items (locked at /tasks)

- [x] R1. `fleet.py` dispatching a second CLARIFY while another feature holds the lock exits non-zero naming the lock holder (Q1, Q3). Test: TestSerialGateBlocks.test_gate_blocks_second_clarify.
- [x] R2. Two independent per-phase locks (one CLARIFY, one SPEC) allow features in different phases to coexist (Q1). Test: TestScanLockState.test_scan_lock_state_both.
- [x] R3. Lock state derived from frontmatter -- clarification status != done = CLARIFY lock held, spec.md status == draft = SPEC lock held (Q2). Test: TestScanLockState (4 tests).
- [x] R4. `fleet.py lock force-release <feature> --reason "..."` writes ledger row with mandatory --reason (Q4). Test: TestLockForceRelease.test_lock_force_release.
- [x] R5. Article XI added to `constitution/principles.md`; version 1.2.0; `schema_lint` accepts (Q5). Verified: version 1.2.0, schema_lint exit 0.
- [x] R6. Intra-feature parallel workers proceed; inter-feature same-phase workers blocked (Q6). Test: TestSerialGateBlocks.test_gate_allows_same_feature + test_gate_blocks_second_clarify.
- [ ] R7. Queue releases in priority-weighted FIFO order (Q7). DEFERRED: queue management requires backlog priority integration. V1 uses first-found semantics. Carry to Sprint 7.
- [ ] R8. Existing open features at enforcement turn-on are grandfathered (Q8). DEFERRED: grandfathering requires migration logic. V1 treats all open features uniformly. Carry to Sprint 7.
- [x] R9. `/plan`, `/tasks`, `/implement`, `/qa`, `/retro` dispatch is NOT gated (Q9). Test: TestSerialGateBlocks.test_gate_allows_post_spec.
- [x] R10. Full test suite passes (>= 213 baseline, no regression). 258 passed.
- [x] R11. `schema_lint` stays clean. Verified exit 0.

## Optional / Best-Effort Items

- [ ] O1. Dashboard widget surfaces current lock holder + queue.
- [ ] O2. Ledger contains `lock_acquired` / `lock_released` event rows for every transition.

## Notes

- Contract populated at /spec finalization 2026-06-07. All 9 CLARIFY
  answers recorded; required items trace to specific questions.
- ADR (separate file) must accompany this validation contract before any
  `constitution/` edit. ADR-013 committed in F-07.
- Contract LOCKED at /tasks 2026-06-07. Do not loosen REQUIRED items after
  lock without an explicit decision recorded here.
