---
id: SDD-20260608ADOGHBRIDGE-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Validation Contract: ADO / GitHub Issues Sync Bridge (SDD-022)

- Spec ID: SDD-022
- Spec reference: [`./spec.md`](./spec.md)
- Status: **DRAFT -- NOT LOCKED**
- Lock Point: F-12 pass 2, after Q-A through Q-H are answered and
  `spec.md` is finalized.

---

> **F-12 pass 1 boundary**: this file is intentionally a scaffold.
> REQUIRED items are not enumerated in pass 1 because the owner has not
> resolved the authority, provider, cadence, conflict, mapping, auth,
> and field-scope decisions in [`clarify.md`](./clarify.md). Locking a
> validation contract now would invent the owner's decisions.

---

## Required Items

**TBD pending owner answers.** Expected item areas, not commitments:

- R-area for Q-A authority model and mutation boundary.
- R-area for Q-B v1 provider scope (GitHub live vs ADO live).
- R-area for Q-C/Q-E explicit sync cadence and trigger.
- R-area for Q-D conflict report semantics.
- R-area for Q-F task-to-issue identity mapping.
- R-area for Q-G auth model and no-secret logging.
- R-area for Q-H synced field set and generated body shape.
- R-area for Q-I stdlib-only `urllib.*` implementation and import scan.
- R-area for no host-project writes.
- R-area for `.github/prompts/taskstoissues.prompt.md`, if confirmed.
- R-area for schema_lint clean exit.
- R-area for full test suite after F-14 code changes.

## Optional / Best-Effort Items

**TBD pending owner answers.** Candidate optional areas:

- ADO dry-run provider fixture if live ADO is not v1-required.
- Human-readable sync report in Markdown.
- Optional live GitHub smoke test, only if owner supplies a safe token
  and confirms external write validation.

## Notes

- This contract must be locked before F-14 implementation starts.
- No REQUIRED item may be silently deferred from Sprint 8 close.
- If the owner changes Q-I and requests a third-party dependency, F-12
  must stop and route a Level-2 dependency brief before this contract
  can be locked.
