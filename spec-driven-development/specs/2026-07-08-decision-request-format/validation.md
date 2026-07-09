---
id: SDD-20260708DECREQ-validation
type: validation
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-decision-request-format
---

# VALIDATION: SDD-053 -- Decision-request format for human-facing agents

- Feature ID: SDD-053
- Sprint: PI-8 / Sprint 4 (Sprint 21); design F-56; implementation F-57
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Status: **active** -- contract LOCKED at F-56, checked off in F-57

---

## Lock Statement

This contract is LOCKED at the close of F-56 (design). F-57 (implementation) MUST satisfy every REQUIRED item (R-1..R-7) with evidence and MUST NOT loosen, drop, or silently defer any REQUIRED item. If a REQUIRED item cannot be met, F-57 stops, records the reason here, and surfaces it to the owner via the DECISION-REQUEST FORMAT this feature defines. Optional items (O-1) are nice-to-have and may be deferred with a one-line note.

---

## Required Items (Strict)

- [x] **R-1 (skill carries the format).** `.github/skills/operational/em-communication-discipline/SKILL.md` contains a DECISION-REQUEST FORMAT section with, case-insensitively, all of: `DECISION NEEDED:`, `Options:`, a per-option `impact:`, `Recommendation:`, `one decision block per message`, the block placement rule (`at the very end`), and the no-decision rule (`no decision`). (AC-1) -- EVIDENCE: `test_sdd053.py::TestSkillCarriesFormat` (all 8 REQUIRED_TOKENS asserted) PASS.
- [x] **R-2 (both charters bind to the skill as SSOT).** Both `.github/agents/sprint-executive-manager.agent.md` and `.github/agents/principal-executive-manager.agent.md` require the format for owner decisions and reference `em-communication-discipline` by name for the `decision-request format`. Neither charter restates the full block. (AC-2) -- EVIDENCE: `TestChartersBindToSkill` + `test_charters_do_not_restate_full_block` PASS (neither charter contains `decision needed:`).
- [x] **R-3 (structural test passes, stdlib-only).** `spec-driven-development/cli/test_sdd053.py` exists, is stdlib-only (import audit passes), asserts R-1 (skill tokens/rules) and R-2 (both charter references), and passes. (AC-3) -- EVIDENCE: 6 passed in isolation; `TestStdlibOnly` AST audit PASS (LOCAL_OK={bootstrap}).
- [x] **R-4 (lints clean).** `schema_lint.py` exits 0; `origin_lint.py` is clean; `staledoc_lint.py` is green after the F-57 edits. (AC-4) -- EVIDENCE: schema_lint exit 0; origin-lint clean; staledoc-lint clean.
- [x] **R-5 (no pytest regression).** Full `spec-driven-development/` pytest is >= 590 passed / 2 skipped and grows by the new `test_sdd053.py` cases; the count does not regress. (AC-5) -- EVIDENCE: 596 passed, 2 skipped (was 590/2; +6 new cases).
- [x] **R-6 (Article X intact).** Article X FootprintLockGuard stays PASS; no locked render/load function is touched. (AC-6) -- EVIDENCE: `-k FootprintLockGuard` -> 3 passed, 595 deselected.
- [x] **R-7 (no Level-2 trigger).** No `constitution/**` edit, no ADR, no `metadata.version` bump, no third-party dependency (stdlib-only, Article V). (AC-7) -- EVIDENCE: only SKILL.md + 2 charters + new test edited; version stayed `'1.1'`; stdlib-only audit PASS.

---

## Optional Items

- [x] **O-1 (self-consistent example).** The skill's DECISION-REQUEST FORMAT section itself models the discipline (short lead-in, one worked example block). Nice-to-have; not blocking. -- EVIDENCE: section leads with a short status directive and includes one fenced worked example block.

---

## Specific Test Coverage

`spec-driven-development/cli/test_sdd053.py` (stdlib-only, `unittest`) MUST cover:

- Skill contains every required token/rule from R-1 (case-insensitive substring assertions).
- Sprint EM charter contains both `em-communication-discipline` and `decision-request format` (case-insensitive).
- Project EM charter contains both `em-communication-discipline` and `decision-request format` (case-insensitive).
- Stdlib-only audit of the new test module (no third-party imports), mirroring `test_sdd045.py`.

---

## Manual Checks

- [x] **M-1 (wording fidelity).** The locked format wording in the skill matches [`clarify.md`](clarify.md) Q-B (double-hyphen `--` impact separator; block at the very end; one block per message; no decision -> no block). -- EVIDENCE: skill uses `-- impact:` separator, `at the very end`, `one decision block per message`, and `If no decision is needed, there is NO block`.
- [x] **M-2 (no duplication drift).** Neither charter restates the full format block; each only names the skill and its DECISION-REQUEST FORMAT. -- EVIDENCE: `test_charters_do_not_restate_full_block` PASS; charters add a one-line binding referencing `em-communication-discipline`.
- [x] **M-3 (owner pre-push approval).** Owner pre-push approval is recorded before any push of the F-57 implementation. (AC-8) -- EVIDENCE: owner approved commit + push 2026-07-08 via Executive Manager ("option 1"); recorded in the Sprint 21 close block in `exec/sprint-progress.md`.

---

## Tone / UX Check

- [x] **U-1 (container, not menu).** The added format keeps `Recommendation:` mandatory and names one path; it does not reintroduce menuing. The skill's existing "recommend, do not menu" rule remains consistent with the new block. -- EVIDENCE: `test_recommendation_stays_mandatory_container` PASS; section states the block is "the container for the recommendation ... name one path".

---

## Definition of Done (F-57)

- R-1..R-7 checked with evidence; O-1 done or deferred with a one-line note.
- M-1..M-3 and U-1 satisfied.
- Ledger rows recorded for Sprint 21's real feature-level dispatches (B-1 dogfood). -- SATISFIED via `ledger_cli.py record-dispatch` (rows 28 `T-053-DESIGN`/architect, 29 `T-053-IMPL`/software-developer, both `success`, pi=PI-8, sprint=Sprint 21), matching the Sprint 19/20 precedent; doctor B-1 check green (`PI-8: 8 row(s)`). See DE-01.
- Owner pre-push approval recorded before push.

---

## Deviations

- **DE-01 (B-1 ledger dogfood satisfied via the sprint-level record-dispatch precedent, not `fleet.py dispatch`).** `fleet.py dispatch` gates on `is_eligible`, which rejects any task whose `Fleet Dispatch Eligible` cell is exactly `no`. In the LOCKED [`tasks.md`](tasks.md) all five SDD-053 tasks are `no` -- correct behavior, because they are serial single-file edits, not fleet-parallelizable work. The plan.md phrasing "ready to feed `fleet.py dispatch`" was a design imprecision: granular serial tasks are not the unit that gets dispatched. B-1 does NOT require `fleet.py dispatch`; it requires Sprint 21's real dispatch outcomes in the ledger. The established precedent (Sprints 18/19/20) logs one synthetic DESIGN row (to the Architect) and one IMPL row (to the SW Dev) per feature via `ledger/ledger_cli.py record-dispatch`. Sprint 21 followed that precedent exactly: the Sprint EM's two real dispatches (F-56 design -> principal-architect; F-57 implement -> principal-software-developer) were recorded as rows 28 (`T-053-DESIGN`) and 29 (`T-053-IMPL`), pi=PI-8, sprint=Sprint 21, both `success`. The doctor B-1 check (`check_current_pi_dispatch_rows`) is green: `PI-8: 8 row(s)`. No `is_eligible` gate was altered and no locked `tasks.md` eligibility was loosened (no CLI-behavior change). RESOLVED at Level 0 by following documented precedent; no owner decision required.
