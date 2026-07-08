---
id: SDD-20260626PLAINLANG-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-plain-language-comms-discipline
---

# VALIDATION: SDD-044 -- Plain-language human-facing communication discipline

- Feature ID: SDD-044
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Checked off in: **F-36**

---

## Lock Statement

This contract is LOCKED at F-34. F-36 may CHECK items with evidence; it may NOT add, remove, or weaken REQUIRED items. Any delta must be recorded as a numbered DE-xx entry with rationale and must SHARPEN, never loosen, an item. SDD-044 is a skill applicability amendment; acceptance is verified by schema-lint plus manual review of the F-36 skill edit.

## Required Items (Strict)

> Evidence backfill -- F-54b / SDD-052 item 052C (owner-approved 2026-07-08). All 7 REQUIRED items below were validated at the **Sprint 14 close (commit `ecd13b3`)**, whose close record in `exec/sprint-progress.md` states "SDD-044 7/7 REQUIRED" with real-run evidence. This corrective pass ticks the boxes to match the authoritative close record; it CHECKS with evidence only -- no REQUIRED item is added, removed, or weakened (Lock Statement honored).

- [x] **R-1 (applicability broadened).** The `em-communication-discipline` skill's stated applicability/scope binds ALL human-facing principals/EMs (project EM, Sprint EM, PM, Architect, SW Dev when addressing the owner), not the EM alone. (AC-1)
- [x] **R-2 (rule content).** The amended skill states human-facing output -- status, progress, owner questions, recommendations -- must be short, plain, lead-with-answer, recommend-not-menu, no long engineering detail unless asked. (AC-2)
- [x] **R-3 (agent-to-agent carve-out).** The amended skill explicitly states agent-to-agent / internal engineering detail (dispatch briefs, tasks/validation tables, ADR bodies) is allowed and not constrained by the short/plain rule. (AC-3)
- [x] **R-4 (single skill, name preserved).** No new skill is created; `name` stays `em-communication-discipline` and matches the directory; `metadata.version` stays quoted; required skill frontmatter remains valid. (AC-4)
- [x] **R-5 (loaders wired).** The project EM still loads the skill as always-active and the new Sprint EM (SDD-043) loads it; other human-facing principals reference it where applicable. (AC-5)
- [x] **R-6 (schema-lint clean).** `python spec-driven-development/cli/schema_lint.py` -> exit 0 after the skill edit. (AC-6)
- [x] **R-7 (no regression / no Level-2 trigger).** Full pytest >= 481 passed / 2 skipped; no constitution edit, no dependency, no schema change, no Article X locked-function edit. (AC-7)

## Optional Items

- [ ] **O-1.** Optional additive presence test asserting the skill mentions human-facing applicability (must not weaken existing assertions).

## Specific Test Coverage

- schema-lint must validate the amended skill (name matches dir; version quoted; required frontmatter present).
- Full `spec-driven-development/` pytest suite stays at >= 481 passed / 2 skipped (skill text only).

## Manual Checks

- [ ] **M-1.** Reviewer confirms R-1..R-3 wording is actually present in the F-36 skill edit (not just claimed).
- [ ] **M-2.** Reviewer confirms no new skill was created and the directory/name was not renamed.
- [ ] **M-3.** Owner pre-push approval recorded before any push of the F-36 implementation.

## Tone / UX Check

- [ ] **U-1.** The amended skill itself is written short and plain, and the carve-out for agent-to-agent detail is unambiguous.

## Definition of Done

SDD-044 is DONE when R-1..R-7 are checked with evidence, M-1..M-3 are confirmed, U-1 holds, and the full suite + schema-lint are green. Optional O-1 is nice-to-have and does not block.
