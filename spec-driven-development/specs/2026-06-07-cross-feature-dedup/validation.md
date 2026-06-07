---
id: SDD-20260607DEDUP-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Validation Contract: Cross-Feature Deduplication (SDD-020)

- Spec ID: SDD-020
- Status: SKELETON -- contract NOT locked. Locks at /tasks.
- Rule (when locked): zero unchecked REQUIRED items before implementation is
  considered complete.

> **DO NOT IMPLEMENT until this contract is locked.** All REQUIRED items
> below are TODO placeholders pending CLARIFY answers. Each placeholder
> names the CLARIFY question(s) it traces to.

---

## Required Items (TODO -- locked at /tasks)

- [ ] R1. TODO -- dedup scope per CLARIFY Q1 is honored. Test: scan
  reports the agreed corpus (e.g., backlog + open spec dirs); items
  outside scope are not reported.
- [ ] R2. TODO -- match heuristic per CLARIFY Q2 is implemented and
  layered correctly. Test: HARD / SOFT / ADVISORY tiers each fire on
  representative inputs and never on negative controls.
- [ ] R3. TODO -- tooling form per CLARIFY Q3. Test: CLI entry point is
  runnable standalone; skill (if chosen) invokes the CLI and surfaces
  output.
- [ ] R4. TODO -- action-on-overlap per CLARIFY Q4. Test: HARD blocks
  proceed, SOFT prompts, ADVISORY warns; behavior matches the chosen
  policy.
- [ ] R5. TODO -- SDD-019 integration per CLARIFY Q5. Test: composed
  behavior with the serial gate matches the agreed ordering.
- [ ] R6. TODO -- dedup log artifact per CLARIFY Q6 is written on every
  pass. Test: scan emits the expected log file(s) and / or ledger
  rows.
- [ ] R7. TODO -- empty-corpus behavior per CLARIFY Q7. Test: first
  triage round on a near-empty BACKLOG produces the agreed output (not
  a silent no-op).
- [ ] R8. TODO -- /triage and /clarify prompts invoke the dedup pass
  automatically. Test: dispatching either slash command produces a
  dedup report in the run record.
- [ ] R9. TODO -- full existing test suite passes (no regression).
  Sprint 5 baseline: 213 tests.
- [ ] R10. TODO -- schema_lint stays clean.

## Optional / Best-Effort Items (TODO)

- [ ] O1. TODO -- dashboard surface lists recent dedup decisions or
  pending overlap flags.
- [ ] O2. TODO -- CLI supports `--format json|table` mirroring
  SDD-FDC-001 `count` convention.

## Notes

- Contract is SKELETON. Required-item count and exact wording will change
  at /spec finalization once CLARIFY answers land.
- Q5 (SDD-019 integration) may shift R5 substantially depending on the
  chosen ordering. Re-review R5 immediately after CLARIFY closes.
- Lock the contract at /tasks; do not loosen REQUIRED items after lock
  without an explicit decision recorded here.
