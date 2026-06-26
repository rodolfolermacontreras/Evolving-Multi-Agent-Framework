---
id: SDD-20260626DEAUTHOR-validation-a3
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# VALIDATION: SDD-047 / A-3 -- scrub origin-project leakage

- Per-item ID: A-3 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN A-3 Acceptance
- Lock statement: LOCKED at F-41. F-42 may CHECK with evidence; may not weaken a REQUIRED item.

## Required Items (Strict)

- [x] **R-1 (no origin tokens in generic files).** The flagged generic files contain no origin tokens (`engine.py`, `FastAPI`, `HTMX`, `Day-to-Day`, `World State`, `Outlander`, `743`) outside a labeled `<!-- example: ... -->` or history block. Evidence: `origin_lint.py` clean (EXIT=0) + doctor `origin tokens absent: ok`.
- [x] **R-2 (architect examples stack-neutral).** `principal-architect.agent.md` design examples are stack-neutral; the `engine.py` lazy-singleton table is relocated to the host-project archetype, not deleted.
- [x] **R-3 (origin story = labeled history).** The `copilot-instructions.md` / README origin story is present and wrapped in clearly-labeled history/example blocks (`<!-- example: origin-history ... -->`), read as history not instruction.
- [x] **R-4 (replace, not delete).** Reviewer confirms each removed origin example was replaced with a stack-neutral equivalent or relocated -- no concept was lost (engine.py table -> host-project archetype; origin story -> labeled blocks).
- [x] **R-5 (Level-2, owner-gated).** The 3 origin-bearing `constitution/**` files (mission.md, decision-policy.md, roadmap.md) are de-authored under accepted ADR-022 with version bumps.

## Manual Checks

- [x] **M-1.** A teammate reading any agent or core skill cannot tell which project the framework came from (origin only in labeled history blocks).
- [x] **M-2.** A-6 lint with the tightened denylist returns 0 hits across `.github/**` and `constitution/**` (generic scope). Evidence: `origin_lint.py` EXIT=0.

## Definition of Done

R-1..R-4 checked with real-run evidence; R-5 landed under approved ADR-022;
M-1..M-2 confirmed; A-6 lint 0 hits in generic files.
