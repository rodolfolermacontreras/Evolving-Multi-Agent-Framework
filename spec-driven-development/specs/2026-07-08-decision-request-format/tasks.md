---
id: SDD-20260708DECREQ-tasks
type: tasks
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-decision-request-format
---

# TASKS: SDD-053 -- Decision-request format for human-facing agents

- Feature ID: SDD-053
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Validation: [`validation.md`](validation.md)
- Implementation slot: **F-57**. These tasks are DESIGNED in F-56 and EXECUTED in F-57. Do not execute here.

---

## No Silent Deferral Rule

Every REQUIRED item in [`validation.md`](validation.md) (R-1..R-7) maps to a task below. No REQUIRED item may be silently dropped, loosened, or marked done without evidence. If a task cannot be completed, F-57 must record the reason in the validation contract and surface it to the owner via the DECISION-REQUEST FORMAT this feature defines.

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete with evidence
- `blocked` -- cannot proceed; reason recorded

## Baseline Block (record in F-57 before any edit)

- Full suite baseline to preserve: **590 passed, 2 skipped** (grows with `test_sdd053.py`; must not regress).
- Schema lint baseline: **exit 0**; `origin_lint.py` clean; `staledoc_lint.py` green.
- Article X FootprintLockGuard: **PASS** (3 tests). No locked render/load function may be touched.
- Skill `name` must keep matching its directory (`em-communication-discipline`); `metadata.version` must stay quoted and UNCHANGED (ADR-0006; no version bump -- Q-A).

## Task Breakdown

| Task ID | Description | allowed_files | blocked_files | Required Tests | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|---------------|---------------|----------------|--------|------|------|-------------------------|--------|
| T-053-01 | Add the DECISION-REQUEST FORMAT section to the skill (single source of truth) with the locked wording from CLARIFY Q-B: short status above; block at the very end (`DECISION NEEDED:` / numbered `Options:` each with `-- impact:` / `Recommendation:`); one block per message; no decision -> no block. Keep `name`/directory match and quoted `metadata.version` unchanged. | `.github/skills/operational/em-communication-discipline/SKILL.md` | `constitution/**`; any `.agent.md`; any locked render/load function | schema-lint (skill frontmatter valid) | S | none | serial | no (single skill file) | todo |
| T-053-02 | Bind the Sprint EM charter to the skill's format: add a one-line instruction that for any owner decision the agent uses the DECISION-REQUEST FORMAT defined in `em-communication-discipline` (SSOT). Do NOT restate the block. | `.github/agents/sprint-executive-manager.agent.md` | the skill file; `constitution/**`; the other charter | manual review (AC-2 / R-2) | S | T-053-01 | serial | no | todo |
| T-053-03 | Bind the project EM charter to the skill's format with the same one-line instruction naming `em-communication-discipline` and its `decision-request format`. Do NOT restate the block. | `.github/agents/principal-executive-manager.agent.md` | the skill file; `constitution/**`; the other charter | manual review (AC-2 / R-2) | S | T-053-01 | serial | no | todo |
| T-053-04 | Add the stdlib-only structural test `test_sdd053.py` (unittest, following `test_sdd045.py`): assert the skill's required tokens/rules (R-1) and that BOTH charters reference `em-communication-discipline` + `decision-request format` (R-2); include a stdlib-only import audit of the new module. | `spec-driven-development/cli/test_sdd053.py` | any file under `.github/`; `constitution/**` | the new test passes | M | T-053-01, T-053-02, T-053-03 | serial | no (new test file) | todo |
| T-053-05 | Run `schema_lint.py` (exit 0), `origin_lint.py`, `staledoc_lint.py`, and full pytest (>= 590 passed / 2 skipped, grows); confirm Article X FootprintLockGuard PASS; record evidence in [`validation.md`](validation.md). | (verification only) | all source files (read-only run) | schema/origin/staledoc lints + full pytest + Article X | S | T-053-01..04 | serial | no | todo |

## Dependency Graph

```
T-053-01 (add format section to skill)
   |-> T-053-02 (Sprint EM charter binding)
   |-> T-053-03 (project EM charter binding)
        |-> T-053-04 (structural test: skill tokens + both charter refs)
             |
             v
        T-053-05 (lints + pytest + Article X, record evidence)
```

## Batch Plan (F-57)

- Batch 1: T-053-01 (skill section edit, one file).
- Batch 2: T-053-02 + T-053-03 (the two charter bindings).
- Batch 3: T-053-04 (structural test).
- Batch 4: T-053-05 (verify + record evidence; log ledger rows via `fleet.py dispatch`, mark success -- B-1 dogfood).

## Traceability (task -> AC -> validation)

| Task | Acceptance | Validation |
|------|------------|------------|
| T-053-01 | AC-1 | R-1, M-1, U-1 |
| T-053-02 | AC-2 | R-2, M-2 |
| T-053-03 | AC-2 | R-2, M-2 |
| T-053-04 | AC-3 | R-3 |
| T-053-05 | AC-4, AC-5, AC-6, AC-7 | R-4, R-5, R-6, R-7 |
| (F-57 close, pre-push) | AC-8 | M-3 |

## Constraints

- Add the DECISION-REQUEST FORMAT to the EXISTING skill; do NOT create a new skill and do NOT rename the skill or its directory.
- Keep `metadata.version` quoted and UNCHANGED; keep `name` matching the directory (schema-lint / ADR-0006). No version bump (Q-A).
- Charters reference the skill by name only; no duplicated format block (Q-B / M-2).
- Structural test asserts PRESENCE of tokens/rules and charter references only; no live-prose linting (Q-C).
- No `constitution/**` edit; no ADR; no third-party dependency (stdlib-only, Article V).
- No Article X locked render/load-function edit; no CLI/schema/ledger behavior change.
- Explicit-path git staging only; no `git add -A` / `git add .`; no push without recorded owner approval (M-3).
- Human-facing outputs stay plain (SDD-044); the new format is the container for the recommendation, not a menu (U-1).
