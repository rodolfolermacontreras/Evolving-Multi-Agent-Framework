---
id: SDD-20260626MAINT-validation-c3
type: validation
status: active
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# VALIDATION: SDD-048 / C-3 -- replace the hardcoded grandfather date

- Per-item ID: C-3 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN C-3 Acceptance
- Lock statement: LOCKED at F-44. F-45 may CHECK with real-run evidence; may not weaken a REQUIRED item. Deltas are numbered DE-xx and must SHARPEN.

## Required Items (Strict)

- [ ] **R-1 (config-sourced cutover).** `ARTICLE_XI_CUTOVER` is read from `project.config.json` (stdlib `json`), not defined as a bare literal in CLI control flow. Evidence: `fleet.py` resolves the cutover from config; `json.load(open('project.config.json'))` contains the cutover field.
- [ ] **R-2 (fallback + comment retained).** `fleet.py` keeps a fallback constant for when the config field is absent, and retains a comment explaining WHY the cutover exists (SDD-019.R8 Article XI grandfather migration). Evidence: comment present; fallback path covered.
- [ ] **R-3 (no hardcoded date in CLI logic).** No hardcoded calendar date remains in CLI control flow without a config source and explanatory comment. Evidence: grep for `"20\d\d-\d\d-\d\d"` literals in `cli/**` shows none in control flow without a config-backed source + comment.
- [ ] **R-4 (behavior unchanged).** `_is_grandfathered` returns the same verdict for existing spec dirs as before the change. Evidence: existing fleet tests pass; a unit test asserts config-sourced and fallback paths agree for the `2026-06-08` value.

## Manual Checks

- [ ] **M-1.** Reviewer confirms the cutover field name and location in `project.config.json` are documented (so a host-project owner can find/override it).
- [ ] **M-2.** Reviewer confirms stdlib-only: only `json` (or equivalent stdlib) is used to read the config.

## Definition of Done

R-1..R-4 checked with real-run evidence; fleet tests green; config field
documented; stdlib-only; full suite 540/2 and schema_lint exit 0.
