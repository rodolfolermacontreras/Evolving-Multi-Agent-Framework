---
id: SDD-20260708DECREQ-plan
type: plan
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-decision-request-format
---

# PLAN: SDD-053 -- Decision-request format for human-facing agents

- Feature ID: SDD-053
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Validation: [`validation.md`](validation.md) | Tasks: [`tasks.md`](tasks.md)
- Implementation slot: **F-57** (this PLAN is authored in F-56, design-only)

---

## Approach

SDD-053 is a one-section skill edit, two one-line charter bindings, and one stdlib structural test:

1. **Add the format to the skill (single source of truth).** In `.github/skills/operational/em-communication-discipline/SKILL.md`, add a DECISION-REQUEST FORMAT section with the locked wording from CLARIFY Q-B: short status above; a decision block at the very end (`DECISION NEEDED:` / numbered `Options:` each with `-- impact:` / `Recommendation:`); one block per message; no decision -> no block. Keep `name` matching the directory and `metadata.version` quoted so schema-lint stays green. No version bump (Q-A).
2. **Bind both EM charters to the skill.** In `.github/agents/sprint-executive-manager.agent.md` and `.github/agents/principal-executive-manager.agent.md`, add a one-line instruction: for any owner decision, use the DECISION-REQUEST FORMAT defined in `em-communication-discipline` (single source of truth). Do NOT copy the block into the charters (Q-B).
3. **Add the structural test.** Create `spec-driven-development/cli/test_sdd053.py` (stdlib-only, `unittest`, following `test_sdd045.py`) asserting the skill tokens/rules and both charter references, plus a stdlib-only import audit of the new module.
4. **Verify.** Run `schema_lint.py` (exit 0), `origin_lint.py`, `staledoc_lint.py`, and full pytest (>= 590 passed / 2 skipped, grows). Confirm Article X FootprintLockGuard PASS.

No new skill, no constitution edit, no ADR, no dependency, no CLI/schema/ledger behavior change.

## Phasing

- **Phase 1 (F-56, here):** CLARIFY + SPEC + PLAN + TASKS + validation contract. No skill/charter edit, no code, no commit, no push.
- **Phase 2 (F-57):** edit the skill; bind both charters; add `test_sdd053.py`; run lints + full pytest; log ledger rows via `fleet.py dispatch` (B-1 dogfood); record owner pre-push approval before any push.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Renaming the skill or its directory breaks schema-lint | Do NOT rename; only add a section. `name` must keep matching the directory (ADR-0006); `metadata.version` stays quoted. |
| Charters duplicate the format and drift | Charters reference the skill by name only (Q-B / R-2 / M-2); no restated block. |
| Structural test becomes a brittle prose linter | Assert PRESENCE of tokens/rules and charter references only (Q-C); never grade live prose. |
| Format reads as a return to menuing | `Recommendation:` stays mandatory and names one path (U-1); the block is the container for the recommendation, not a menu. |
| Dash-glyph mismatch in the format | Canonical form uses `--` (double hyphen); the test asserts semantic tokens, not the dash glyph (Q-B normalization note). |

## Dependencies

- Builds on SDD-044 (PI-7), which added the brevity rule to the same skill. SDD-053 adds the format container on top; it does not reword SDD-044's rules.
- No external/library dependency. stdlib-only is trivially satisfied (skill/charter Markdown + one `unittest` module).
- No ADR (Level-1; no authority/gate/constitution change -- Q-A).

## Definition of Done (design, F-56)

- CLARIFY done; SPEC/PLAN/TASKS/validation authored and `status: active`.
- `schema_lint.py` exit 0; pytest unchanged at 590 passed / 2 skipped (design docs only).
- F-57 implementation tasks enumerated in [`tasks.md`](tasks.md) and ready to feed `fleet.py dispatch`.
