---
id: SDD-20260626MAINT-validation-d2
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# VALIDATION: SDD-048 / D-2 -- lightweight-spec path for small features

- Per-item ID: D-2 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN D-2 Acceptance
- Lock statement: LOCKED at F-44. F-45 may CHECK with real-run evidence; may not weaken a REQUIRED item. Deltas are numbered DE-xx and must SHARPEN.

## Required Items (Strict)

> Evidence backfill -- F-54b / SDD-052 item 052C (owner-approved 2026-07-08). All 4 REQUIRED items below were validated at the **Sprint 17 close (commit `71bba51`)**, whose close record in `exec/sprint-progress.md` states "SDD-048 per-item ... D-2 4/4 REQUIRED checked with real-run evidence". This corrective pass ticks the boxes to match the authoritative close record; it CHECKS with real-run evidence only -- no REQUIRED item is added, removed, or weakened (Lock Statement honored).

- [x] **R-1 (combined-doc template exists).** A single combined-artifact template (story + requirements + validation contract in one file, with cross-links) exists for <5-file features. Evidence: the template file is present under `templates/` with the sections defined in [`plan.md`](plan.md).
- [x] **R-2 (Article X preserved).** The combined artifact authors a checkable validation contract (Required Items strict + Manual Checks + Definition of Done) BEFORE implementation. The lock is NOT weakened -- duplication is collapsed, not the validation rigor. Evidence: the template's validation section mirrors the strict-items pattern; schema_lint accepts it.
- [x] **R-3 (proven on a real <5-file feature).** One real <5-file feature completes the full lifecycle using the single combined artifact and still satisfies Article X (its lock holder validates). Evidence: a real spec dir uses the combined doc; its fleet/lock check passes.
- [x] **R-4 (eligibility documented).** The "<5-file feature" eligibility rule (when the lightweight path is allowed vs when the four-doc path is required) is documented alongside the template. Evidence: eligibility note present; references Article VI.

## Manual Checks

- [ ] **M-1.** Reviewer confirms the lightweight path does NOT bypass the validation contract -- it merges the four files, it does not drop the lock.
- [ ] **M-2.** Reviewer confirms `schema_lint` recognizes the combined artifact's frontmatter `type` and does not regress on the four-doc path.

## Definition of Done

R-1..R-4 checked with real-run evidence; the combined-doc template exists and is
schema_lint-clean; one real <5-file feature proves the path end-to-end with the
Article X lock intact; M-1..M-2 confirmed.
