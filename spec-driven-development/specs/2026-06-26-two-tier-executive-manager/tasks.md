---
id: SDD-20260626TWOTIEREM-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-two-tier-executive-manager
---

# TASKS: SDD-043 -- Two-tier Executive Manager (Sprint EM agent)

- Feature ID: SDD-043
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)
- ADR: [`../../docs/ADR/020-two-tier-executive-manager.md`](../../docs/ADR/020-two-tier-executive-manager.md)
- Implementation slot: **F-36**. These tasks are DESIGNED in F-34 and EXECUTED in F-36. Do not execute here.

---

## No Silent Deferral Rule

Every REQUIRED item in [`validation.md`](validation.md) maps to a task below. No REQUIRED item may be silently dropped, loosened, or marked done without evidence. If a task cannot be completed, F-36 must record the reason in the validation contract and surface it to the owner -- not skip it.

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete with evidence
- `blocked` -- cannot proceed; reason recorded

## Baseline Block (record in F-36 before any edit)

- Full suite baseline to preserve: **481 passed, 2 skipped** (`python -m pytest spec-driven-development/ --tb=no -q`).
- Schema lint baseline: **exit 0** (`python spec-driven-development/cli/schema_lint.py`).
- Article X locked render functions: must remain byte-identical (no SDD-043 edit touches CLI).

## Task Breakdown

| Task ID | Description | File Scope | Required Tests | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|----------------|--------|------|------|-------------------------|--------|
| T-043-01 | Author the Sprint Executive Manager agent file mirroring the project EM structure; encode scope lock, route-to-Principals, report-up, Level 0, defers human Q&A. | `.github/agents/<sprint-executive-manager>.agent.md` (NEW) | schema-lint (agent `description` present) | M | ADR-020 Proposed | serial | no (single new identity file) | todo |
| T-043-02 | In the agent "What you do NOT do" section, encode: cannot create sprint/PI, cannot author next kickoff, cannot make PI-level commitments; may only SUGGEST upward. | same file as T-043-01 | manual review (AC-3) | S | T-043-01 | serial | no | todo |
| T-043-03 | In the agent file, state explicitly that the project EM is the single human entry point per Article II and the Sprint EM defers project-wide human Q&A to it. | same file as T-043-01 | manual review (AC-5) | S | T-043-01 | serial | no | todo |
| T-043-04 | Load `em-communication-discipline` as always-active in the agent's Skills section (human-facing EM; dovetails SDD-044). | same file as T-043-01 | manual review (AC-8) | S | T-043-01 | serial | no | todo |
| T-043-05 | Add a forward-only Sprint-EM activation block to the shared kickoff template; do NOT retrofit shipped kickoff prompts. | `spec-driven-development/feature-prompts/_SHARED_ONBOARDING.md` | manual review (AC-7) | S | T-043-01 | serial | no | todo |
| T-043-06 | (Optional, owner discretion) Add a one-line cross-reference in the project EM file noting the Sprint EM delegated tier. | `.github/agents/principal-executive-manager.agent.md` | manual review | S | T-043-01 | serial | no | todo |
| T-043-07 | Run `schema_lint.py` (exit 0) and full pytest (>= 481 passed / 2 skipped); record evidence in validation.md. | (verification only) | schema-lint + pytest | S | T-043-01..05 | serial | no | todo |
| T-043-08 | Accept ADR-020 (Proposed -> Accepted) at the Sprint 14 close gate with recorded owner ratification. | `spec-driven-development/docs/ADR/020-two-tier-executive-manager.md` | manual (owner approval recorded) | S | T-043-07 | serial | no | todo |

## Dependency Graph

```
ADR-020 (Proposed, F-34)
   |
   v
T-043-01 (agent file)
   |-> T-043-02 (no-create clause)
   |-> T-043-03 (Article II preserved)
   |-> T-043-04 (comms skill loaded)
   |-> T-043-05 (kickoff activation)
   |-> T-043-06 (optional cross-ref)
        |
        v
   T-043-07 (schema-lint + pytest) --> T-043-08 (ADR-020 Accepted at close)
```

## Batch Plan (F-36)

- Batch 1: T-043-01 .. T-043-04 (the agent file, in one file).
- Batch 2: T-043-05 (kickoff template) + T-043-06 (optional cross-ref).
- Batch 3: T-043-07 (verify) then T-043-08 (ADR acceptance at close).

## Constraints

- stdlib-only is trivially met (no code). No new dependency.
- No `constitution/**` edit (Q-B finding: NO).
- No Article X locked render-function edit; no CLI/schema/ledger change.
- Forward-only kickoff activation; do not rewrite shipped `SPRINT-##-KICKOFF.prompt.md` files.
- Explicit-path git staging only; no `git add -A` / `git add .`; no push without recorded owner approval.
- Plain-language human-facing outputs (SDD-044 discipline applies to this EM).
