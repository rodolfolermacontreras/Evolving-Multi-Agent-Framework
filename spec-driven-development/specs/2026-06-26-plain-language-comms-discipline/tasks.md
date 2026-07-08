---
id: SDD-20260626PLAINLANG-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-plain-language-comms-discipline
---

# TASKS: SDD-044 -- Plain-language human-facing communication discipline

- Feature ID: SDD-044
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)
- Implementation slot: **F-36**. These tasks are DESIGNED in F-34 and EXECUTED in F-36. Do not execute here.

---

## No Silent Deferral Rule

Every REQUIRED item in [`validation.md`](validation.md) maps to a task below. No REQUIRED item may be silently dropped, loosened, or marked done without evidence. If a task cannot be completed, F-36 must record the reason in the validation contract and surface it to the owner.

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete with evidence
- `blocked` -- cannot proceed; reason recorded

## Baseline Block (record in F-36 before any edit)

- Full suite baseline to preserve: **481 passed, 2 skipped**.
- Schema lint baseline: **exit 0**.
- Skill `name` must keep matching its directory (`em-communication-discipline`); `metadata.version` must stay quoted (ADR-0006).

## Task Breakdown

| Task ID | Description | File Scope | Required Tests | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|----------------|--------|------|------|-------------------------|--------|
| T-044-01 | Broaden the skill applicability/scope wording so the discipline binds ALL human-facing principals/EMs, not EM only; update `description` accordingly. Keep `name`/`license`/`metadata.author`/quoted `metadata.version` unchanged. | `.github/skills/operational/em-communication-discipline/SKILL.md` | schema-lint (skill frontmatter valid) | S | none | serial | no (single skill file) | todo |
| T-044-02 | State the rule explicitly: human-facing output (status, progress, owner questions, recommendations) is short, plain, lead-with-answer, recommend-not-menu, no long engineering detail unless asked. | same file as T-044-01 | manual review (AC-2) | S | T-044-01 | serial | no | todo |
| T-044-03 | Add the agent-to-agent carve-out: dispatch briefs, tasks/validation tables, ADR bodies retain full detail and are not constrained by the short/plain rule. | same file as T-044-01 | manual review (AC-3) | S | T-044-01 | serial | no | todo |
| T-044-04 | Confirm the project EM already loads the skill as always-active; ensure the new Sprint EM (SDD-043) loads it (via SDD-043 T-043-04). | `.github/agents/principal-executive-manager.agent.md`; Sprint EM file | manual review (AC-5) | S | T-044-01 | serial | no | todo |
| T-044-05 | (Where applicable) Add the always-active skill reference to other human-facing principal agent files (PM / Architect / SW Dev) that speak to the owner. | relevant `.github/agents/*.agent.md` | manual review (AC-5) | S | T-044-01 | serial | no | todo |
| T-044-06 | Run `schema_lint.py` (exit 0) and full pytest (>= 481 passed / 2 skipped); record evidence in validation.md. | (verification only) | schema-lint + pytest | S | T-044-01..05 | serial | no | todo |

## Dependency Graph

```
T-044-01 (broaden skill scope + description)
   |-> T-044-02 (rule content)
   |-> T-044-03 (agent-to-agent carve-out)
   |-> T-044-04 (EM + Sprint EM load it)
   |-> T-044-05 (other human-facing principals, where applicable)
        |
        v
   T-044-06 (schema-lint + pytest)
```

## Batch Plan (F-36)

- Batch 1: T-044-01 .. T-044-03 (the skill file edit, in one file).
- Batch 2: T-044-04 + T-044-05 (loader references).
- Batch 3: T-044-06 (verify).

## Constraints

- Amend the EXISTING skill; do NOT create a new skill and do NOT rename the skill or its directory.
- Keep `metadata.version` quoted; keep `name` matching the directory (schema-lint / ADR-0006).
- No `constitution/**` edit; no ADR (skill amendment, no authority/gate change).
- No Article X locked render-function edit; no CLI/schema/ledger change.
- Explicit-path git staging only; no `git add -A` / `git add .`; no push without recorded owner approval.
- Plain-language human-facing outputs (this feature defines that discipline).
