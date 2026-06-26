---
id: SDD-20260626DEAUTHOR-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# TASKS: SDD-047 -- De-author the framework

- Plan: [`plan.md`](plan.md) | Spec: [`spec.md`](spec.md)
- Serial execution (shared surfaces). Each task names allowed_files.

| Task ID | Item | Description | File Scope | Verify |
|---------|------|-------------|------------|--------|
| T-047-01 | A-2 | Create `project.config.json` (owner/team/repo_url) + stdlib reader helper | `project.config.json`, `cli/bootstrap.py` (reader) | reader returns owner; unit test |
| T-047-02 | A-2 | De-author `INSTRUCTIONS.md` line 5 + README-as-instruction owner line | `INSTRUCTIONS.md` | grep name -> 0 |
| T-047-03 | A-2 | Neutralize PM agent owner/single-user lines -> "the host project's owner" | `.github/agents/principal-product-manager.agent.md` | grep name -> 0; PM traces to config |
| T-047-04 | A-2 | De-author remaining agent files (personal name) | `.github/agents/*.agent.md` (excl. historical) | grep name -> 0 |
| T-047-05 | A-2 | Set all skill `author:` frontmatter -> `emf-framework` | `.github/skills/**/SKILL.md` | grep author rodolfo -> 0; schema_lint clean |
| T-047-06 | A-2 | A-6 lint reads config-derived personal-name denylist (TDD first) | `cli/origin_lint.py`, `cli/test_*` | re-added name fails lint test |
| T-047-07 | A-3 | Replace origin examples with stack-neutral; relocate engine.py table to archetype | flagged agents/skills, `archetypes/**` | A-6 0 hits in generic files |
| T-047-08 | A-3 | Wrap origin story in labeled history block (`copilot-instructions.md`, README) | `.github/copilot-instructions.md`, `README.md` | A-6 exempts labeled block |
| T-047-09 | D-1 | Wire `tdd-gate` into SW Dev review flow | SW Dev agent + relevant prompt | grep reference >=1 |
| T-047-10 | D-1 | Wire-or-delete remaining 9 dead skills per validation-D1 | skills + `roster/skills.json` | each referenced or removed |
| T-047-11 | D-1 | schema_lint rule: orphan skill fails (TDD first) | `cli/schema_lint.py`, `cli/test_schema_lint.py` | orphan test fails, referenced passes |
| T-047-12 | D-3 | Rename over-claim in `GENERALIZATION_SDD.md`; file SDD-049 backlog item | `GENERALIZATION_SDD.md`, `backlog/BACKLOG.md` | no over-claim text remains |
| T-047-13 | A-2/A-3/D-3 | **LEVEL-2 (owner-gated)** constitution de-author under ADR-022 | `constitution/mission.md`, `constitution/decision-policy.md`, `constitution/roadmap.md` | ADR accepted + owner approval + version bump |
| T-047-14 | close | QA: pytest/schema_lint/doctor/Article X; log ledger; owner pre-push | exec/ledger/sprint-progress | gates green; rows logged |

## Notes

- T-047-13 is BLOCKED on owner approval (Level-2). All other tasks proceed.
- TDD gate (B-2) applies to T-047-06 and T-047-11 (code changes need test-first).
- Backfill/ledger (B-1) logged at T-047-14 close.
