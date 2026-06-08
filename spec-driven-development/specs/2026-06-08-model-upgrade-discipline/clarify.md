---
id: SDD-20260608MODELUPGRADE-clarify
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# CLARIFY: Model Upgrade Discipline (SDD-015)

- Date: 2026-06-08
- Owners: Principal Product Manager + Principal Architect
- Sprint: PI-5 Sprint 4 (= overall Sprint 8)
- Source item: SDD-015 -- Model upgrades as Level-2 decisions with regression-test branch + A/B + cost analysis
- Status: CLOSED for SPEC/PLAN/TASKS

---

## Context Verified

- SDD-014 is DONE and provides the Level-2 Friction Analysis template at `spec-driven-development/templates/level-2-decision.md`.
- `spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md` does not exist yet.
- `spec-driven-development/constitution/decision-policy.md` does not reference a model-upgrade protocol yet.
- Article VIII applies to `constitution/**`: F-13 does not edit constitution files. Any F-14 cross-reference edit to `decision-policy.md` requires an ADR or explicit owner waiver.
- Article V applies to any future CLI: stdlib only.

---

## Q-J: Scope -- What Counts As A Model Upgrade?

Question: Which model changes must trigger the Level-2 model-upgrade protocol?

Recommended answer: Treat a model upgrade as any major version bump, vendor swap, model-family swap, or role-critical model assignment change. Minor patch changes can be logged without the full protocol unless they materially change quality, cost, privacy, safety, or hosted capability behavior.

Why this matters: If every patch bump requires the full Level-2 path, routine maintenance becomes too heavy. If vendor and family swaps are not included, the framework has no guardrail against exactly the quality drift SDD-015 is meant to prevent.

Answer: Adopt the recommendation as the Sprint 8 default. A role-critical model is any model used by Principal agents, implementation workers, review workers, or commands/prompts that influence CLARIFY, SPEC, PLAN, TASKS, IMPLEMENT, REVIEW, or stakeholder-facing reports.

Status: CLOSED.

---

## Q-K: Regression Branch Shape And Representative Workload

Question: What branch shape and workload define the regression-test path?

Recommended answer: Use one ephemeral branch per upgrade named `model-upgrade/<old>-to-<new>`. Run the A/B comparison against a canonical fixture derived from recent sprint prompts and artifacts, not against live network calls or ad hoc chat transcripts.

Why this matters: A long-lived comparison branch accumulates stale state. A per-upgrade branch creates a clean audit trail and makes rejection cheap. The workload must be representative enough to catch prompt-sensitive regressions while remaining deterministic enough to test.

Answer: Adopt the recommendation. The canonical fixture should cover at least CLARIFY, SPEC, PLAN/TASKS, IMPLEMENT-report, and REVIEW-report scenarios using recent Sprint 7 and Sprint 8 artifacts as source material.

Status: CLOSED.

---

## Q-L: A/B Harness Implementation

Question: Should the A/B comparison be a new CLI harness, a manual checklist, or a test-only fixture?

Recommended answer: Implement a stdlib-only CLI at `spec-driven-development/cli/model_upgrade.py` with no-network fixture comparison. It should read committed fixture inputs, compare captured old/new outputs, calculate cost and quality deltas, and produce deterministic Markdown/JSON reports.

Why this matters: A manual-only checklist will drift. A live-network benchmark is hard to reproduce and unsafe for CI. A fixture-backed CLI gives F-14 a testable implementation surface that can evolve later into live capture only if the owner approves a new Level-2 path.

Answer: Adopt the recommendation. The CLI is required for F-14 unless the Principal Software Developer proves an equivalent stdlib-only implementation with the same validation coverage.

Status: CLOSED.

---

## Q-M: Cost-Delta Capture

Question: Where should pricing inputs live, and where should the resulting cost delta be recorded?

Recommended answer: Commit pricing inputs as explicit editable data in the protocol/template surface, and require the A/B output to populate the Money Cost section of the Level-2 Friction Analysis brief.

Why this matters: A cost claim without committed inputs is not reviewable. A cost delta outside the Level-2 brief will be missed by the human approval gate.

Answer: Adopt the recommendation. F-14 should create a committed pricing input file or table and ensure the generated report contains one-time, recurring, per-run, and per-token/per-unit assumptions that can be copied into `templates/level-2-decision.md`.

Status: CLOSED.

---

## Q-N: Quality-Delta Capture

Question: What counts as a measurable quality improvement or regression?

Recommended answer: Use a rubric with four measurable surfaces: validation/test pass, spec-quality checklist score, commit/report quality deltas, and manual owner approval for ambiguous quality wins.

Why this matters: "Better model" is otherwise subjective and easy to overclaim. The framework needs a record that distinguishes pass/fail regressions from qualitative improvements that still need owner judgment.

Answer: Adopt the recommendation. The protocol must make ambiguous quality wins owner-approved, not agent-approved.

Status: CLOSED.

---

## Q-O: Governance -- Decision Policy Cross-Reference

Question: Does adding a `decision-policy.md` cross-reference to `docs/MODEL-UPGRADE-PROTOCOL.md` require an ADR?

Recommended answer: Yes. Because the target file is under `constitution/**`, the safe Article VIII interpretation is that even a pure cross-reference addition should be accompanied by an ADR unless the owner explicitly waives that requirement.

Why this matters: Sprint 8 success criteria expects the protocol to be referenced from `decision-policy.md`, but F-13 must not normalize quiet constitution edits. The implementation task needs a clear gate so F-14 does not accidentally violate Article VIII.

Answer: Adopt the safe route. F-14 may draft ADR-016 for the cross-reference and may edit `decision-policy.md` only after the ADR is accepted or an explicit owner waiver is recorded. If neither happens, F-14 must stop as OWNER-ATTENTION instead of silently skipping the required cross-reference.

Status: CLOSED.

---

## CLARIFY Close

- No owner decision remains open for F-13 artifact finalization.
- F-14 has one explicit HITL caveat: the constitution cross-reference cannot be applied unless ADR-016 is accepted or the owner grants a waiver.
- No REQUIRED item may be deferred from Sprint 8 close.
