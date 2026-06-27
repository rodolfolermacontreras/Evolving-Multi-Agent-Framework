---
id: SDD-20260626MAINT-validation-c2
type: validation
status: active
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# VALIDATION: SDD-048 / C-2 -- right-size the stdlib-only rule (render wall)

- Per-item ID: C-2 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN C-2 Acceptance
- Lock statement: LOCKED at F-44. F-45 may CHECK with real-run evidence; may not weaken a REQUIRED item. Deltas are numbered DE-xx and must SHARPEN.

## Required Items (Strict)

- [ ] **R-1 (stdlib-only preserved).** No `cli/**` module imports any third-party package. Article V holds. Evidence: import scan over `cli/**` shows only stdlib modules; `schema_lint.py` exit 0.
- [ ] **R-2 (non-locked wall factored).** `render_markdown` (762 lines, non-locked) plus the non-locked html injectors are factored into `string.Template`-based stdlib helpers so the non-locked render surface is no longer a single monolithic f-string wall. Evidence: `string.Template` (or equivalent stdlib factoring) used; no single non-locked render function remains a 700-line wall (see C-1 R-2).
- [ ] **R-3 (render_html exempt + documented).** `render_html` (658 lines, LOCKED) is NOT factored and is explicitly recorded as the Article X exception. Evidence: `render_html` byte-identical (C-1 R-4); the ADR names it as the documented exception.
- [ ] **R-4 (ADR recorded).** `docs/ADR/023-dashboard-render-stdlib-only.md` exists and records: (a) the stdlib-only decision, (b) the `string.Template` factoring choice, (c) the `render_html`-locked trade-off, and (d) options considered. Evidence: ADR file present; Status: Proposed at F-44.

## Manual Checks

- [ ] **M-1.** Reviewer confirms the ADR honestly states that the "no 700-line wall" outcome applies to the NON-locked surface only, because `render_html` is locked.
- [ ] **M-2.** Owner ratifies ADR-023 to Accepted at close (F-46). Until then it stays Proposed. Evidence: ADR Status flip + owner approval recorded at close.

## Definition of Done

R-1..R-4 checked with real-run evidence; ADR-023 present and Proposed at F-44,
Accepted at close under owner approval; M-1 confirmed; no third-party dependency
introduced or proposed.
