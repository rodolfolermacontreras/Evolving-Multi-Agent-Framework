---
id: SDD-20260626PLAINLANG-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-plain-language-comms-discipline
---

# SPEC: SDD-044 -- Plain-language human-facing communication discipline

- Feature ID: SDD-044
- Sprint: PI-7 / Sprint 1 (Sprint 14), design slot F-34 (paired with SDD-043); implementation F-36
- Status: **active** (design locked; skill body edit pending in F-36)
- CLARIFY: [`clarify.md`](clarify.md)
- Validation contract: [`validation.md`](validation.md)
- Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- ADR: none (skill applicability amendment; no constitution edit, no authority change)

---

## Problem Statement

The `em-communication-discipline` skill (`.github/skills/operational/em-communication-discipline/SKILL.md`, origin LESSON-005) currently scopes its short/plain "recommend, do not menu" rule to the Executive Manager only. In practice every human-facing principal/EM produces owner-facing text -- status, progress, recommendations, owner questions -- and those outputs sometimes carry long engineering detail the owner did not ask for. SDD-044 extends the existing discipline's applicability so every human-facing principal/EM keeps human-facing output short, plain, and to the point, while preserving full technical detail for agent-to-agent coordination.

## Goal

Design (not edit) the amendment that broadens the `em-communication-discipline` skill's applicability from EM-only to ALL human-facing principals/EMs, so F-36 can make the wording change with no further design ambiguity. The rule: human-facing output is short and plain; agent-to-agent / internal engineering detail stays allowed.

## Non-Goals

- Editing the skill body (F-36).
- Creating a new skill (Q-D: amend the existing one).
- Any `constitution/**` edit (skill amendment only).
- Changing the skill `name` or directory (must stay matched per schema-lint / ADR-0006).
- SDD-043 agent design (paired, separate spec dir) and SDD-045 (F-35).

## Acceptance Criteria

- **AC-1 (applicability broadened).** F-36 edits the `em-communication-discipline` skill so its stated applicability/scope binds ALL human-facing principals/EMs (Executive Manager, Sprint Executive Manager, Product Manager, Architect, Software Developer when speaking to the owner), not the EM alone.
- **AC-2 (rule content).** The amended skill states that every human-facing output -- status, progress, owner questions, recommendations -- MUST be short, plain, and to the point: lead with the answer, recommend (do not menu), no long engineering detail unless the owner asks.
- **AC-3 (agent-to-agent carve-out).** The amended skill states explicitly that agent-to-agent and internal engineering detail (dispatch briefs, tasks/validation tables, ADR bodies) remains allowed and is NOT constrained by the short/plain rule.
- **AC-4 (single skill, name preserved).** No new skill is created; the skill `name` stays `em-communication-discipline` and continues to match its directory name; required frontmatter (`name`, `description`, `license`, `metadata.author`, `metadata.version` quoted) stays valid.
- **AC-5 (loaded by human-facing agents).** The human-facing principals/EMs that should load this skill are identified so F-36 can ensure they reference it as always-active (at minimum: project EM, the new Sprint EM from SDD-043). Adding the reference for additional human-facing principals is in scope for F-36 where those agent files exist.
- **AC-6 (schema-lint clean).** The amended skill passes `python spec-driven-development/cli/schema_lint.py` exit 0 (skill frontmatter rules unchanged; version stays quoted; name matches dir).
- **AC-7 (no regression / no Level-2 trigger).** F-36 keeps the full suite at >= 481 passed / 2 skipped and introduces no constitution edit, no dependency, no schema change, and no Article X locked-function edit.

## Affected Modules

| Module / file | Change | When |
|---------------|--------|------|
| `.github/skills/operational/em-communication-discipline/SKILL.md` | Broaden applicability/scope wording (and `description`) to all human-facing principals/EMs | F-36 |
| `.github/agents/principal-executive-manager.agent.md` | Already loads the skill; confirm reference stays valid | F-36 (verify) |
| `.github/agents/<sprint-executive-manager>.agent.md` (SDD-043) | Loads the skill as always-active | F-36 (via SDD-043) |
| Other human-facing principal agent files (PM / Architect / SW Dev) | Optionally add the always-active reference where they speak to the owner | F-36 (where applicable) |

## Data Model Changes

None. Skill Markdown only. No schema, ledger, SQLite, or CLI change.

## API Changes

None.

## Test Strategy

- SDD-044 is a skill-text amendment; acceptance is verified by **schema-lint** (skill frontmatter still valid: name matches dir, version quoted) plus **manual review** that AC-1..AC-3 wording is present in the F-36 edit.
- No new pytest is required. F-36 MUST keep the suite at >= 481 passed / 2 skipped and `schema_lint.py` exit 0.
- An optional additive presence test (skill mentions "human-facing" applicability) is allowed but must not weaken existing assertions.

## Validation Contract Pointer

The authoritative pass/fail contract for SDD-044 is [`validation.md`](validation.md). It is LOCKED at F-34 and checked off in F-36.

## Traceability Matrix

| Requirement | Source | Acceptance | Validation |
|-------------|--------|------------|------------|
| Broaden applicability to all human-facing principals | Q-D | AC-1 | R-1 |
| Short/plain human-facing rule content | Q-E | AC-2 | R-2 |
| Agent-to-agent detail carve-out | Q-E | AC-3 | R-3 |
| Single skill; name preserved; frontmatter valid | Q-D, ADR-0006 | AC-4 | R-4 |
| Identify loaders (EM + Sprint EM, others optional) | SDD-043 link | AC-5 | R-5 |
| Schema-lint clean | Article V / schema_lint | AC-6 | R-6 |
| No regression / no Level-2 trigger | quality-policy, Article X | AC-7 | R-7 |

## Open Questions

- None blocking. Q-D, Q-E answered. No ADR required (skill amendment, no authority/gate/constitution change).

## Out of Scope

- The skill body edit itself (F-36).
- Any constitution edit, new skill, dependency, schema migration, or Article X locked-function change.
- SDD-043 (separate spec dir) and SDD-045 (F-35).
