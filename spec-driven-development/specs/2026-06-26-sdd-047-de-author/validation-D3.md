---
id: SDD-20260626DEAUTHOR-validation-d3
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# VALIDATION: SDD-047 / D-3 -- rename "conflict detection" over-claim

- Per-item ID: D-3 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN D-3 Acceptance
- Lock statement: LOCKED at F-41. F-42 may CHECK with evidence; may not weaken a REQUIRED item.

## Required Items (Strict)

- [x] **R-1 (generic doc renamed).** `GENERALIZATION_SDD.md` no longer claims "conflict detection" the code does not perform; wording matches the serial CLARIFY/SPEC gate (`fleet.py` `_scan_lock_state`). Evidence: 3 reframes at SS5.3, SS7.1, SS8.4 (`sdd_check_lock_state`).
- [x] **R-2 (Level-2, owner-gated).** `constitution/roadmap.md` line 78 ("Conflict-detection workflow ... deferred") renamed under accepted ADR-022 (version 1.0.0->1.1.0).
- [x] **R-3 (honest backlog item).** A true file-overlap detector is filed as SDD-049 in `backlog/BACKLOG.md` (P3, honest, not papered over).

## Scope note

Historical specs (`specs/**`) and the audit/kickoff sources that contain
"conflict detection" are OUT of scope -- they are the record. Only the generic
guidance surfaces are renamed.

## Manual Checks

- [x] **M-1.** Reviewer confirms no generic doc claims a conflict detection the code does not perform.

## Definition of Done

R-1 + R-3 checked with real-run evidence; R-2 landed under approved ADR-022;
M-1 confirmed.
