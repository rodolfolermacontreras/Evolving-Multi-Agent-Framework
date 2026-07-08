---
id: SDD-20260626MAKEPROMISESTRUE-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-make-promises-true
depends_on: [SDD-045]
---

# TASKS: SDD-046 -- "Make promises true"

- Feature ID: SDD-046. Sprint: PI-7 Sprint 15. Implementation feature: F-39.
- Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Validation: [validation.md](validation.md).

---

## No Silent Deferral Rule

Every task below is either DONE this feature or explicitly marked `blocked` / `deferred` with a reason in Notes. A task may not vanish. The only pre-approved deferral is O-1 (file-scope check), tracked in validation.md as an Optional item -- it is NOT silently dropped; it is named and parked. Closing F-39 with any `todo` task unaccounted for is a No-Silent-Deferral violation and must fail the DONE gate.

---

## Status Legend

- `todo` -- not started
- `doing` -- in progress
- `done` -- complete, tests pass, reviewed
- `blocked` -- cannot proceed (reason in Notes)

---

## Baseline Block

- Test baseline at design time: 501 passed / 2 skipped (Sprint 14 close).
- Baseline only grows. F-39 must end at >= 501 passed / 2 skipped, plus the new tests for B-1 helper, B-2 TDD gate, and B-2 DONE-completeness.
- `python spec-driven-development/cli/schema_lint.py` must exit 0.
- `TestS1FootprintLockGuard` must stay PASS (no locked-function edit).

---

## Task Breakdown

| Task ID | Description | File Scope | Required Tests | Effort | Deps | Mode | Fleet-Eligible | Status |
|---------|-------------|-----------|----------------|--------|------|------|----------------|--------|
| T-046-B1-01 | Add read-only `current_pi_name(root)` helper resolving newest active `sprints/PI-*/CURRENT_PI.md` (reuse state_builder resolver if available) | `cli/bootstrap.py` | helper returns `PI-7` for current tree; returns None when no marker | S | none | serial (bootstrap.py) | No | todo |
| T-046-B1-02 | Add `run_doctor` check (f) "current-PI dispatch rows": count `dispatches WHERE pi=?`, FAIL on 0 for active PI, SKIP when no marker | `cli/bootstrap.py` | doctor FAILS on 0-row active PI fixture; PASSES with >=1 row; SKIPs with no marker | M | T-046-B1-01 | serial (bootstrap.py) | No | todo |
| T-046-B1-03 | Document `fleet.py mark` as the close one-liner in fleet.py usage/help (no signature change) | `cli/fleet.py` | existing fleet tests stay green | S | none | parallel | Yes | todo |
| T-046-B1-04 | Add ledger-write close step to `/qa` prompt | `.github/prompts/qa.prompt.md` | n/a (prose) -- manual M-1 | S | none | serial (qa.prompt.md) | No | todo |
| T-046-B1-05 | Add ledger-check close step to `/retro` prompt | `.github/prompts/retro.prompt.md` | n/a (prose) -- manual M-2 | S | none | parallel | Yes | todo |
| T-046-B2-01 | Create `cli/tdd_gate_check.py` (`main(argv)`, stdlib-only) porting tdd-gate Mechanical Check + `[NO-TEST-NEEDED]` hatch | `cli/tdd_gate_check.py` | FAIL fixture (prod change, no test, no tag); PASS fixture (prod+test); PASS empty diff; PASS with `[NO-TEST-NEEDED]` | M | none | parallel | Yes | todo |
| T-046-B2-02 | Create `cli/done_check.py` (`main(argv)`, stdlib-only): spec.md + all REQUIRED `[ ]` checked + retro present; `--pi` scope | `cli/done_check.py` | FAIL fixture (missing retro); FAIL fixture (unchecked REQUIRED box); PASS fixture (complete dir) | M | none | parallel | Yes | todo |
| T-046-B2-03 | Wire B-2 checks (g tdd gate, h DONE completeness) into `run_doctor` checks list, in-process, `is_framework`-gated; done_check scoped to current PI | `cli/bootstrap.py` | doctor exercises both checks; current-PI done dirs pass | M | T-046-B2-01, T-046-B2-02, T-046-B1-02 | serial (bootstrap.py) | No | todo |
| T-046-B2-04 | Add "Enforced by: cli/tdd_gate_check.py" pointer to tdd-gate SKILL.md | `.github/skills/engineering/tdd-gate/SKILL.md` | n/a (prose) -- manual M-3 | S | T-046-B2-01 | parallel | Yes | todo |
| T-046-B2-05 | Add "Enforced by: cli/done_check.py" pointer in QA close section (NOT in constitution/RULES.md) | `.github/prompts/qa.prompt.md` | n/a (prose) -- manual M-4 | S | T-046-B2-02, T-046-B1-04 | serial (qa.prompt.md) | No | todo |
| T-046-B4-01 | Create `.github/workflows/doctor.yml` = checkout + Python 3.12 + `make doctor`; no deploy/Azure/secret | `.github/workflows/doctor.yml` | manual M-5 (YAML lints; job graph) | M | T-046-B2-03 | parallel | Yes | todo |
| T-046-B4-02 | Author ADR-021 (doctor-CI) under docs/ADR/; record supersede of ADR-009 + local==CI rationale | `docs/ADR/021-ci-doctor-validation.md` | manual M-6 | S | T-046-B4-01 | parallel | Yes | todo |
| T-046-B4-03 | Set ADR-009 Status -> `superseded by ADR-021` with pointer line | `docs/ADR/009-ci-oidc-deploys-to-production.md` | manual M-6 | S | T-046-B4-02 | serial (ADR-009) | No | todo |
| T-046-X-01 | Run `make doctor` + `schema_lint`; confirm all green, baseline grows, lock guard PASS | (verification only) | full suite green; schema_lint exit 0 | S | all above | serial (gate) | No | todo |
| T-046-X-02 | Dogfood B-1: record Sprint 15 dispatch outcomes via `fleet.py mark`; confirm current PI shows real rows in state.html | `ledger/fleet.db` (rows), regenerated `exec/state.*` | doctor current-PI check PASSES post-log | S | T-046-B1-02 | serial (close) | No | todo |

---

## Serialization flags (for F-39 dispatch)

- `cli/bootstrap.py` -- touched by T-046-B1-01, T-046-B1-02, T-046-B2-03. SERIALIZE: one owner for all three, or land B-1 bootstrap edits and merge before B-2 wiring begins.
- `.github/prompts/qa.prompt.md` -- touched by T-046-B1-04 and T-046-B2-05. SERIALIZE.
- `docs/ADR/009-*.md` and ADR-021 -- ADR-009 edit depends on ADR-021 existing. SERIALIZE B4-02 -> B4-03.
- Parallel-safe (distinct new files / distinct prose): T-046-B1-03, T-046-B1-05, T-046-B2-01, T-046-B2-02, T-046-B2-04, T-046-B4-01, T-046-B4-02.

---

## Notes

- O-1 (file-scope >3 production files check) is DEFERRED by design (clarify Q-C). It is NOT a task here; it is parked as an Optional item in validation.md. This is the single pre-approved deferral.
- ADR authoring (T-046-B4-02) is an F-39 task, not F-38. F-38 (this design) only assigned the number (ADR-021) and recorded the supersede decision.
- B-1's prompt edits are prose, validated by manual checks M-1/M-2, not unit tests (prompts are not executable). Their EFFECT (ledger rows for the current PI) is validated mechanically by T-046-X-02 + the doctor check.
- No `constitution/**` or `RULES.md` edit appears in any task. If F-39 finds itself wanting to edit either, STOP and escalate -- it means the make-true approach broke down.
