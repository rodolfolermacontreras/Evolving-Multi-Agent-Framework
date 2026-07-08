---
id: SDD-20260626TWOTIEREM-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-two-tier-executive-manager
---

# VALIDATION: SDD-043 -- Two-tier Executive Manager (Sprint EM agent)

- Feature ID: SDD-043
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- ADR: [`../../docs/ADR/020-two-tier-executive-manager.md`](../../docs/ADR/020-two-tier-executive-manager.md)
- Checked off in: **F-36**

---

## Lock Statement

This contract is LOCKED at F-34. F-36 may CHECK items with evidence; it may NOT add, remove, or weaken REQUIRED items. Any delta must be recorded as a numbered DE-xx entry with rationale and must SHARPEN, never loosen, an item. SDD-043 is a governance/identity design feature; acceptance is verified by schema-lint plus manual review of the F-36 agent file and kickoff-template edit.

## Required Items (Strict)

- [ ] **R-1 (agent file created, correct shape).** Exactly one new `.github/agents/` file for the Sprint Executive Manager exists, mirroring the project EM section skeleton (frontmatter `description` + handoffs; Identity; Default Context Source; Responsibilities; Communication style; "What you do NOT do"; Skills; Decision authority; Session start; Error handling). (AC-1)
- [ ] **R-2 (scope lock).** The agent file states the Sprint EM operates only within its sprint's features and does not comment on, re-prioritize, or start work outside the sprint. (AC-2)
- [ ] **R-3 (no sprint/PI creation; suggest-only).** The "What you do NOT do" section states the Sprint EM cannot create a sprint/PI, cannot author the next kickoff, cannot make PI-level commitments, and may only SUGGEST upward. (AC-3)
- [ ] **R-4 (report up at close).** The Responsibilities section states the Sprint EM produces a sprint-close summary and reports up to the project EM at sprint close. (AC-4)
- [ ] **R-5 (Article II preserved; not human entry point).** The agent file states the project EM remains the single human entry point per Article II and the Sprint EM defers project-wide human Q&A to it. (AC-5)
- [ ] **R-6 (Level 0 authority).** The Decision authority section pins the Sprint EM to Level 0 (route / summarize / surface), no Level 1/2 decisions, escalation per `decision-policy.md`. (AC-6)
- [ ] **R-7 (forward-only kickoff activation).** `_SHARED_ONBOARDING.md` contains a Sprint-EM activation block; no already-shipped `SPRINT-##-KICKOFF.prompt.md` is retrofitted. (AC-7)
- [ ] **R-8 (comms skill loaded).** The agent file loads `em-communication-discipline` as always-active. (AC-8)
- [ ] **R-9 (schema-lint clean).** `python spec-driven-development/cli/schema_lint.py` -> exit 0 with the new agent file present. (AC-9)
- [ ] **R-10 (no regression / no Level-2 trigger).** Full pytest >= 481 passed / 2 skipped; no constitution edit, no dependency, no schema change, no Article X locked-function edit. (AC-10)
- [ ] **R-11 (ADR-020 accepted at close).** ADR-020 transitions Proposed -> Accepted at the Sprint 14 close gate with recorded owner ratification.

## Optional Items

- [ ] **O-1.** Optional one-line cross-reference in the project EM file noting the Sprint EM delegated tier (owner discretion). (T-043-06)
- [ ] **O-2.** Optional additive presence test asserting the agent file exists and contains the no-create clause (must not weaken existing assertions).

## Specific Test Coverage

- schema-lint must validate the new agent file (`description` present; agent rules pass).
- Full `spec-driven-development/` pytest suite must stay at >= 481 passed / 2 skipped (docs/agent text only).

## Manual Checks

- [ ] **M-1.** Reviewer confirms R-2..R-8 wording is actually present in the F-36 agent file (not just claimed).
- [ ] **M-2.** Reviewer confirms `_SHARED_ONBOARDING.md` activation block is forward-only and no shipped kickoff prompt was edited.
- [ ] **M-3.** Owner pre-push approval recorded before any push of the F-36 implementation and before ADR-020 acceptance.

## Tone / UX Check

- [ ] **U-1.** The agent file's human-facing communication guidance is short and plain (SDD-044 discipline), while agent-to-agent routing detail stays allowed.

## Definition of Done

SDD-043 is DONE when R-1..R-11 are checked with evidence, M-1..M-3 are confirmed, U-1 holds, ADR-020 is Accepted with recorded owner approval, and the full suite + schema-lint are green. Optional O-1/O-2 are nice-to-have and do not block.
