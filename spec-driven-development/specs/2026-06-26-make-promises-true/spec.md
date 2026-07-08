---
id: SDD-20260626MAKEPROMISESTRUE-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-make-promises-true
depends_on: [SDD-045]
---

# SPEC: SDD-046 -- "Make promises true" (B-1 ledger, B-2 blocking checks, B-4 CI)

- Feature ID: SDD-046 (epic). Per-item codes: B-1, B-2, B-4 (verbatim from EMF-HARDENING-PLAN Part B).
- Sprint: PI-7 Sprint 15.
- Status: active.
- Clarify: [clarify.md](clarify.md). Plan: [plan.md](plan.md). Tasks: [tasks.md](tasks.md). Validation: [validation.md](validation.md).
- Source audit: `spec-driven-development/docs/Temp/EMF-HARDENING-PLAN.md` Part B.
- Depends on: SDD-045 (doctor / `run_doctor` aggregation point, `governance_check.py`, `origin_lint.py`, `make setup`/`make doctor` -- all merged).

---

## Problem Statement

The framework makes three audit-trail / enforcement promises that the repository contradicts.

- B-1 (the ledger is not true): Article VII and RULES Rule 4 claim universal dispatch logging, and RULES Section 4 ("What counts as DONE") lists a ledger row in the DONE checklist. Live: `fleet.db` holds 11 dispatch rows, all from PI-2 / `N/A`; PI-3..PI-6 closed with none. `/qa` (Phase 8) and `/retro` (Phase 9) prompts produce verdicts and retros but write no ledger row. The promise is structurally unenforced.
- B-2 (the rules are honor-system prose): the methodology that matters is text, not code. `tdd-gate/SKILL.md` carries a full "Mechanical Check" algorithm but is referenced by zero agents or prompts; only `schema_lint.py` actually fails a command. An agent under pressure can ignore the TDD gate and the DONE checklist with no mechanical consequence.
- B-4 (no CI): no `.github/workflows/` exists, so every enforceable check only runs when a human remembers. `ADR-009` (status: proposed) describes a CI OIDC deploy to Azure Container Apps that (a) was never created and (b) is now moot -- the Azure dashboard was decommissioned (ADR-015 / SDD-035). The repo claims CI it does not have.

The B-1 disposition is owner-LOCKED to Option 1 ("make it real"); this spec makes the promises TRUE rather than retracting them, so no `constitution/**` edit is required.

---

## Goal

Make all three promises true with the smallest honest change:
- B-1: a feature/sprint cannot be stamped DONE until its dispatch outcomes are in the ledger; `doctor` turns red when the current PI has zero dispatch rows; the current PI shows real rows in `state.html`.
- B-2: at least two named rules (TDD gate, DONE-completeness) fail a command when violated, are wired into `doctor`, and the prose skills point at the enforcing scripts.
- B-4: one GitHub Actions workflow runs the exact `doctor` set on push and PR using the identical entrypoint as `make doctor`; ADR-009 is superseded by ADR-021 so the recorded CI decision matches reality.

All within stdlib-only, with Article X locked functions untouched and the test baseline only growing.

---

## Non-Goals

- B-3 (governance cross-reference consistency) -- delivered in SDD-045; not touched here.
- File-scope (>3 production files) enforcement -- deferred to optional O-1; not required this sprint.
- Any edit to `constitution/**` (Article VII and Rule 4 are made true, not rewritten).
- Any edit to an Article X locked function (`render_markdown`, `render_html`, and peers). New read-only helpers only.
- Any Azure / deploy CI (ADR-009's original premise). The B-4 workflow validates; it does not deploy.
- Adding any third-party dependency (Article V).
- Closing PI-7 or pulling SDD-047 / SDD-048 forward.

---

## Functional Requirements

### B-1 -- Make the ledger true (owner-locked: Option 1)

- FR-B1-1: `fleet.py mark --dispatch-id <N> --outcome {success|failed|blocked} [--notes ...] [--db ...]` is documented as the REQUIRED close step for recording a dispatch outcome. No new subcommand is introduced.
- FR-B1-2: The `/qa` prompt (`.github/prompts/qa.prompt.md`) gains an explicit close step instructing the agent to record each dispatch outcome via `fleet.py mark` before declaring a feature DONE.
- FR-B1-3: The `/retro` prompt (`.github/prompts/retro.prompt.md`) gains an explicit close step instructing the agent to ensure the sprint's dispatch outcomes are in the ledger before the retro is final.
- FR-B1-4: `run_doctor` gains a check "current-PI dispatch rows". It resolves the current PI name from the newest active `sprints/PI-*/CURRENT_PI.md` marker via a NEW read-only helper, counts `dispatches` rows WHERE `pi = <current PI name>`, and FAILS the check (red doctor) when the count is zero for an active PI.
- FR-B1-5: The new current-PI helper is read-only and does NOT modify or replace any Article X locked function; it may read the same `sprints/PI-*/CURRENT_PI.md` markers that `state_builder` reads.
- FR-B1-6: No promise about the ledger is left contradicted by `fleet.db`: after this feature, `state.html` / `state.md` for the current PI reflect real dispatch rows (dogfooded by Sprint 15 logging its own dispatches at close).

### B-2 -- Turn the rules into blocking checks (two rules)

- FR-B2-1: A new stdlib-only module `spec-driven-development/cli/tdd_gate_check.py` exposes `main(argv) -> int` and, given a diff or commit range, FAILS (non-zero exit) when one or more production paths changed without a corresponding test change AND no `[NO-TEST-NEEDED]` tag is present in the commit range. The algorithm mirrors `tdd-gate/SKILL.md` "Mechanical Check".
- FR-B2-2: A new stdlib-only module `spec-driven-development/cli/done_check.py` exposes `main(argv) -> int` and, given a feature dir, FAILS when the dir lacks any of: `spec.md`, a `validation.md` whose REQUIRED `[ ]` checkboxes are not all checked, or a retro artifact.
- FR-B2-3: Both checks are wired into `run_doctor`'s aggregated `checks` list so a `doctor` run exercises them.
- FR-B2-4: `tdd-gate/SKILL.md` gains an "Enforced by: spec-driven-development/cli/tdd_gate_check.py" pointer; the DONE-completeness prose (RULES Section 4 reference in a skill or prompt) points at `done_check.py`. The scripts -- not the prose -- are the source of truth for pass/fail.
- FR-B2-5: Each rule has at least one test proving it catches a real violation (a fixture that the check FAILS) and at least one proving a clean case PASSES.

### B-4 -- CI so the checks fire for everyone

- FR-B4-1: A new workflow `.github/workflows/doctor.yml` runs on `push` and `pull_request` and invokes `make doctor` (== `python spec-driven-development/cli/bootstrap.py doctor`) -- the byte-identical entrypoint used locally.
- FR-B4-2: The workflow uses only what a fresh runner needs to run the doctor set (checkout + Python); it adds NO deploy step, NO Azure login, NO stored secret.
- FR-B4-3: A new ADR-021 (doctor-CI) is authored under `spec-driven-development/docs/ADR/`, and ADR-009 status is set to `superseded` with a pointer to ADR-021. (Authored in F-39; this spec records the decision and the assigned number.)
- FR-B4-4: A PR that breaks any enforced rule (a B-2 check, schema_lint, origin lint, the B-1 ledger check on an active PI, or the test baseline) makes the workflow red.

### Cross-cutting

- FR-X-1: All new code is Python stdlib-only (argparse, sqlite3, pathlib, json, sys, os, subprocess, re). No new dependency.
- FR-X-2: No Article X locked function is edited; `TestS1FootprintLockGuard` golden SHA-256 stays PASS.
- FR-X-3: `python spec-driven-development/cli/schema_lint.py` exits 0 after all changes.
- FR-X-4: The test baseline is >= 501 passed / 2 skipped and only grows.

---

## Acceptance Criteria

- AC-1 (B-1): With the current PI active and zero `dispatches` rows for it, `doctor` reports the current-PI dispatch check as FAILED (red). [FR-B1-4]
- AC-2 (B-1): After recording Sprint 15's dispatch outcomes via `fleet.py mark`, the same `doctor` check PASSES and the current PI shows real rows in `state.html`. [FR-B1-1, FR-B1-6]
- AC-3 (B-1): `/qa` and `/retro` prompts each contain an explicit "record dispatch outcome(s) in the ledger" close step. [FR-B1-2, FR-B1-3]
- AC-4 (B-1): The current-PI helper is read-only; the locked-function guard test stays PASS. [FR-B1-5, FR-X-2]
- AC-5 (B-2): `tdd_gate_check.py` exits non-zero on a fixture where a production file changed with no test change and no `[NO-TEST-NEEDED]` tag; exits 0 on a clean fixture. [FR-B2-1, FR-B2-5]
- AC-6 (B-2): `done_check.py` exits non-zero on a feature dir missing a required artifact or with an unchecked REQUIRED box; exits 0 on a complete dir. [FR-B2-2, FR-B2-5]
- AC-7 (B-2): Both checks appear in `run_doctor`'s `checks` list; the two prose skills carry an "Enforced by:" pointer to their scripts. [FR-B2-3, FR-B2-4]
- AC-8 (B-4): `.github/workflows/doctor.yml` invokes `make doctor`; CI and local run the identical entrypoint. [FR-B4-1]
- AC-9 (B-4): The workflow has no deploy / Azure / secret step. [FR-B4-2]
- AC-10 (B-4): ADR-021 exists describing doctor-CI; ADR-009 status == `superseded` and references ADR-021. [FR-B4-3]
- AC-11 (cross): `schema_lint` exits 0; no new dependency added; baseline >= 501/2 and grows. [FR-X-1, FR-X-3, FR-X-4]

---

## Affected Modules

| Path | Change | Item | Locked? |
|------|--------|------|---------|
| `spec-driven-development/cli/bootstrap.py` | ADD read-only current-PI helper + 1 check call in `run_doctor`; wire 2 B-2 checks | B-1, B-2 | No (additive; do not edit locked render fns) |
| `spec-driven-development/cli/fleet.py` | Doc/usage only -- `mark` is the close step (no signature change) | B-1 | No |
| `.github/prompts/qa.prompt.md` | ADD ledger-write close step | B-1 | No |
| `.github/prompts/retro.prompt.md` | ADD ledger-write close step | B-1 | No |
| `spec-driven-development/cli/tdd_gate_check.py` (NEW) | TDD gate enforcing check | B-2 | New file |
| `spec-driven-development/cli/done_check.py` (NEW) | DONE-completeness enforcing check | B-2 | New file |
| `.github/skills/engineering/tdd-gate/SKILL.md` | ADD "Enforced by:" pointer | B-2 | No (prose) |
| DONE-completeness prose skill/prompt | ADD "Enforced by:" pointer | B-2 | No (prose) |
| `.github/workflows/doctor.yml` (NEW) | CI = `make doctor` | B-4 | New file |
| `spec-driven-development/docs/ADR/021-*.md` (NEW) | doctor-CI ADR (authored F-39) | B-4 | New file |
| `spec-driven-development/docs/ADR/009-ci-oidc-deploys-to-production.md` | status -> superseded | B-4 | No |
| `spec-driven-development/cli/test_*.py` (NEW/extended) | tests for both B-2 checks + B-1 helper | all | New tests |

---

## Traceability

| Audit item | FR | Acceptance | Validation |
|------------|----|-----------|------------|
| B-1 close step + prompts | FR-B1-1, FR-B1-2, FR-B1-3 | AC-2, AC-3 | R-B1-1, R-B1-2 |
| B-1 doctor check + helper | FR-B1-4, FR-B1-5, FR-B1-6 | AC-1, AC-2, AC-4 | R-B1-3, R-B1-4, R-B1-5 |
| B-2 TDD gate | FR-B2-1, FR-B2-5 | AC-5 | R-B2-1, R-B2-4 |
| B-2 DONE-completeness | FR-B2-2, FR-B2-5 | AC-6 | R-B2-2, R-B2-4 |
| B-2 wiring + pointers | FR-B2-3, FR-B2-4 | AC-7 | R-B2-3, R-B2-5 |
| B-4 workflow | FR-B4-1, FR-B4-2, FR-B4-4 | AC-8, AC-9 | R-B4-1, R-B4-2 |
| B-4 ADR | FR-B4-3 | AC-10 | R-B4-3 |
| cross-cutting | FR-X-1..4 | AC-4, AC-11 | R-X-1, R-X-2, R-X-3, R-X-4 |
