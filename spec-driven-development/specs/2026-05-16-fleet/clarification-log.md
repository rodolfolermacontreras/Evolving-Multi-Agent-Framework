# Clarification Log: fleet.py

- Date: 2026-05-16
- Status: ready for spec (EM-discipline: recommended answers, no menu)

---

## Q1: Should fleet.py launch workers or just emit packets?

- Recommended: emit packets only; operator launches workers manually.
- Why: launching workers requires process management, secrets, and per-vendor APIs. Out of scope for v0.1.
- Answer: yes, packets-only.

## Q2: Where do packets live on disk?

- Recommended: `spec-driven-development/dispatches/<pi>/<dispatch-id>.md`
- Why: keeps the audit trail next to the rest of the SDD root; PI grouping mirrors sprint folders.
- Answer: yes, that path.

## Q3: Should mark-outcome and list be in fleet.py or stay in ledger_cli.py?

- Recommended: thin wrappers in fleet.py that delegate to ledger_cli.py functions.
- Why: avoids duplication; gives one fleet ergonomic entry point while keeping ledger_cli as the low-level layer.
- Answer: thin wrappers, delegate to ledger_cli.

## Summary

3 of 3 resolved. Proceed to /spec.
