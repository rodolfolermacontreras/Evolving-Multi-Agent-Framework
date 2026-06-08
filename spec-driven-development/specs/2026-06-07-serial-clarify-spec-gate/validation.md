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

- [ ] R1. `fleet.py` dispatching a second CLARIFY while another feature holds the lock exits non-zero naming the lock holder (Q1, Q3). Test: mock two features, dispatch second, assert exit 1 + message naming holder.
- [ ] R2. Two independent per-phase locks (one CLARIFY, one SPEC) allow features in different phases to coexist (Q1). Test: Feature A in CLARIFY + Feature B in SPEC both proceed without conflict.
- [ ] R3. Lock state derived from frontmatter -- clarification status != done = CLARIFY lock held, spec.md status == draft = SPEC lock held (Q2). Test: create fixture spec dirs with various frontmatter states, assert lock detection matches expected state.
- [ ] R4. `fleet.py lock force-release <feature> --reason "..."` writes ledger row with mandatory --reason (Q4). Test: force-release + verify ledger row content (event_type, feature, reason, timestamp).
- [ ] R5. Article XI added to `constitution/principles.md`; version 1.2.0; `schema_lint` accepts (Q5). Test: schema_lint clean after amendment.
- [ ] R6. Intra-feature parallel workers proceed; inter-feature same-phase workers blocked (Q6). Test: dispatch N workers for lock-holding feature succeeds; dispatch 1 worker for non-holding feature in same phase refused.
- [ ] R7. Queue releases in priority-weighted FIFO order (Q7). Test: 3 features queue for CLARIFY lock; highest-priority released first; same-priority breaks by FIFO timestamp.
- [ ] R8. Existing open features at enforcement turn-on are grandfathered (Q8). Test: fixture with pre-existing open spec dirs; gate does not retroactively block them.
- [ ] R9. `/plan`, `/tasks`, `/implement`, `/qa`, `/retro` dispatch is NOT gated (Q9). Test: dispatch for post-SPEC phases proceeds regardless of lock state.
- [ ] R10. Full test suite passes (>= 213 baseline, no regression).
- [ ] R11. `schema_lint` stays clean.

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
