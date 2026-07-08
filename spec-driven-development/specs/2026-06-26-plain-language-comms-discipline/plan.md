---
id: SDD-20260626PLAINLANG-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-plain-language-comms-discipline
---

# PLAN: SDD-044 -- Plain-language human-facing communication discipline

- Feature ID: SDD-044
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Validation: [`validation.md`](validation.md)
- Implementation slot: **F-36** (this PLAN is authored in F-34, design-only)

---

## Approach

SDD-044 is a one-file skill-text amendment plus a few agent-file references:

1. **Broaden the skill applicability.** In `.github/skills/operational/em-communication-discipline/SKILL.md`, edit the scope/applicability prose (and the `description` frontmatter) so the discipline binds ALL human-facing principals/EMs, not just the EM. Keep `name`, `license`, `metadata.author`, and the quoted `metadata.version` unchanged so schema-lint stays green.
2. **State the rule and the carve-out.** Make the short/plain rule explicit for human-facing output and explicitly carve out agent-to-agent / internal engineering detail.
3. **Wire the loaders.** Ensure the human-facing agents reference the skill as always-active -- the project EM already does; the new Sprint EM (SDD-043) loads it; add the reference for other human-facing principals where their agent files exist and they speak to the owner.

No new skill (Q-D), no constitution edit, no CLI/schema/ledger change.

## Phasing

- **Phase 1 (F-34, here):** CLARIFY + SPEC + PLAN + TASKS + validation contract. No skill edit, no commit, no push.
- **Phase 2 (F-36):** edit the skill applicability/scope + `description`; confirm/add always-active references in human-facing agent files; run schema-lint + full pytest.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Renaming the skill or its dir breaks schema-lint | Do NOT rename; only broaden scope wording + `description`. `name` must keep matching the directory (ADR-0006). |
| Over-broad rule strips detail from agent-to-agent traffic | Explicit carve-out (AC-3): short/plain binds human-facing output only. |
| Editing many agent files for loaders causes churn | Required loaders are project EM (already) + Sprint EM (SDD-043). Other principals are optional/where-applicable, not blocking. |
| Drift between SDD-043 and SDD-044 | SDD-043's AC-8 loads this exact skill; the two are designed together in F-34 and implemented together in F-36. |

## Dependencies

- **Pairs with SDD-043** -- the Sprint EM (SDD-043) loads this skill; both implement in F-36.
- No external/library dependency. stdlib-only is trivially satisfied (no code).
- No ADR (skill amendment; no authority/gate change).

## Definition of Done (design, F-34)

- CLARIFY done; SPEC/PLAN/TASKS/validation authored and `status: active`.
- `schema_lint.py` exit 0; pytest unchanged at 481 passed / 2 skipped (docs-only).
- F-36 implementation tasks enumerated in [`tasks.md`](tasks.md).
