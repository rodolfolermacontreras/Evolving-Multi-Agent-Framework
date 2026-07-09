---
id: SDD-20260708DECREQ-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-decision-request-format
---

# SPEC: SDD-053 -- Decision-request format for human-facing agents

- Feature ID: SDD-053
- Sprint: PI-8 / Sprint 4 (Sprint 21); design slot F-56; implementation F-57
- Status: **active** (design locked; skill + charter edits and structural test pending in F-57)
- CLARIFY: [`clarify.md`](clarify.md)
- Validation contract: [`validation.md`](validation.md)
- Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- ADR: none (skill + charter behavioral amendment; no constitution edit, no authority change -- Q-A)

---

## Problem Statement

The Sprint Executive Manager and other human-facing agents send long status updates with the decision buried in the prose. The owner cannot quickly see what is being asked, what the options are, or the impact of each. SDD-044 (PI-7) broadened the `em-communication-discipline` skill so human-facing language is short and plain, but it did not fix HOW a decision is surfaced in a message. SDD-053 adds a mandatory DECISION-REQUEST FORMAT: a short status above, and a clearly-marked decision block at the very end that names the ask, the options with their impact, and one recommendation.

## Goal

Design (not implement) the amendment that adds a mandatory DECISION-REQUEST FORMAT to the `em-communication-discipline` skill (single source of truth) and binds both EM charters to it, plus a cheap stdlib-only structural test, so F-57 can execute with no design ambiguity. The format is the container for the recommendation the skill already mandates -- it does not reintroduce menuing.

## Non-Goals

- Editing the skill, either charter, or any code (all F-57).
- Rewording the skill's existing brevity / "recommend, do not menu" rules (SDD-044 owns those).
- A prose-quality linter that scores live owner-facing messages (rejected in Q-C).
- Any `constitution/**` edit, ADR, version bump, or new dependency (Q-A).
- Duplicating the full format spec into the charters (Q-B: charters reference the skill by name).

## Acceptance Criteria

- **AC-1 (skill carries the format).** F-57 edits `em-communication-discipline` so the skill contains a DECISION-REQUEST FORMAT section with, at minimum: the `DECISION NEEDED:` line; a numbered `Options:` list where each option has a one-line `impact:`; a `Recommendation:` line; the rule "one decision block per message"; the rule that the block sits "at the very end" with nothing after it; and the rule that "no decision" means no block.
- **AC-2 (both charters bind to the skill as SSOT).** Both `.github/agents/sprint-executive-manager.agent.md` and `.github/agents/principal-executive-manager.agent.md` require the format for owner decisions and reference `em-communication-discipline` by name as the single source of truth. Neither charter restates the full block (no drift-prone duplication).
- **AC-3 (structural test).** F-57 adds `spec-driven-development/cli/test_sdd053.py` (stdlib-only) that asserts the skill's required format tokens/rules (AC-1) and that BOTH charters reference the skill by name for the decision-request format (AC-2). The test passes.
- **AC-4 (lints clean).** `schema_lint.py` exits 0; `origin_lint.py` is clean; `staledoc_lint.py` is green after the F-57 edits.
- **AC-5 (no regression).** Full `spec-driven-development/` pytest stays at >= 590 passed / 2 skipped (the count grows when `test_sdd053.py` is added; it must not regress).
- **AC-6 (Article X intact).** Article X FootprintLockGuard stays PASS; no locked render/load function is touched.
- **AC-7 (no Level-2 trigger).** No `constitution/**` edit, no ADR, no `metadata.version` bump, no third-party dependency (stdlib-only, Article V).
- **AC-8 (owner approval).** Owner pre-push approval is recorded before any push of the F-57 implementation (house discipline).

## Affected Modules

| Module / file | Change | When |
|---------------|--------|------|
| `.github/skills/operational/em-communication-discipline/SKILL.md` | Add the DECISION-REQUEST FORMAT section (single source of truth). Keep `name`/directory match and quoted `metadata.version` unchanged. | F-57 |
| `.github/agents/sprint-executive-manager.agent.md` | Add a one-line binding: for any owner decision, use the DECISION-REQUEST FORMAT defined in `em-communication-discipline` (SSOT). No duplicated block. | F-57 |
| `.github/agents/principal-executive-manager.agent.md` | Same one-line binding to the skill's format. No duplicated block. | F-57 |
| `spec-driven-development/cli/test_sdd053.py` | New stdlib-only structural test (skill tokens + both charter references). | F-57 |

## Data Model Changes

None. Skill/charter Markdown plus one stdlib test module. No schema, ledger, SQLite, or CLI-behavior change.

## API Changes

None.

## Test Strategy

- SDD-053 adds a deterministic, stdlib-only STRUCTURAL test (`test_sdd053.py`) following the `test_sdd045.py` convention (`unittest`, `pathlib`, framework-root resolution, stdlib-only import audit).
- The test asserts PRESENCE only: the skill's format tokens/rules (AC-1) and both charters' references to the skill for the format (AC-2). It does NOT attempt to grade live prose quality (Q-C Option B rejected).
- F-57 MUST keep the full suite at >= 590 passed / 2 skipped (grows with the new test) and keep `schema_lint.py` / `origin_lint.py` / `staledoc_lint.py` green.

## Validation Contract Pointer

The authoritative pass/fail contract for SDD-053 is [`validation.md`](validation.md). It is LOCKED at F-56 and checked off in F-57.

## Traceability Matrix

| Requirement | Source | Acceptance | Validation |
|-------------|--------|------------|------------|
| Skill carries the DECISION-REQUEST FORMAT (all tokens + rules) | Q-B | AC-1 | R-1 |
| Both EM charters bind to the skill as single source of truth | Q-B | AC-2 | R-2 |
| Stdlib-only structural test (skill tokens + both charter refs), passes | Q-C | AC-3 | R-3 |
| schema_lint / origin_lint / staledoc_lint clean | quality-policy | AC-4 | R-4 |
| No pytest regression (>= 590 passed / 2 skipped, grows) | quality-policy | AC-5 | R-5 |
| Article X FootprintLockGuard PASS; no locked function touched | Article X | AC-6 | R-6 |
| No constitution edit / ADR / version bump / dependency | Q-A, Article V | AC-7 | R-7 |
| Owner pre-push approval recorded | house discipline | AC-8 | M-3 |

## Open Questions

- None blocking. Q-A, Q-B, Q-C answered. No ADR required (Q-A: Level-1, no authority/gate/constitution change).

## Out of Scope

- The skill edit, the two charter bindings, and the structural test (all F-57).
- Any constitution edit, new skill, dependency, schema migration, version bump, or Article X locked-function change.
- A prose-quality linter (Q-C Option B, rejected).
- SDD-044's existing brevity rules (unchanged by SDD-053).
