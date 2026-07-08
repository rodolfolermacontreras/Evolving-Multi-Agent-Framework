---
id: SDD-20260626MAKEPROMISESTRUE-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-make-promises-true
depends_on: [SDD-045]
---

# VALIDATION: SDD-046 -- "Make promises true"

- Feature ID: SDD-046. Items: B-1, B-2, B-4. Sprint: PI-7 Sprint 15.
- Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Tasks: [tasks.md](tasks.md).

---

## Lock Statement

This contract is LOCKED at design time (F-38). F-39 may not add, remove, or weaken a REQUIRED item to make the feature pass. New REQUIRED items may only be added by the architect with an explicit note.

DA-Evidence Discipline applies to every REQUIRED item: the box may be checked ONLY after a real command was run end-to-end and its artifact/output read. No item is satisfied by prediction, by "the code looks right", or by a harness that simulates the outcome. Each item names the command that proves it.

---

## Required Items

### B-1 -- Make the ledger true

- [x] R-B1-1: `fleet.py mark --dispatch-id <N> --outcome success` writes/updates a `dispatches` row. Proof: run it against a scratch db, then `SELECT outcome FROM dispatches WHERE rowid=<N>` shows the value. (AC-2, FR-B1-1)
    - PROVEN 2026-06-26: scratch db built from schema.sql, row inserted, `fleet.py mark --dispatch-id 1 --outcome success --db <scratch>` -> "Dispatch #1 marked success."; `SELECT outcome FROM dispatches WHERE id=1` -> ('success',). Real ledger untouched.
- [x] R-B1-2: `/qa` prompt and `/retro` prompt each contain an explicit ledger close step. Proof: `grep -i "fleet.py mark" .github/prompts/qa.prompt.md` and a ledger-check line in `.github/prompts/retro.prompt.md` both return a hit. (AC-3, FR-B1-2, FR-B1-3)
    - PROVEN 2026-06-26: qa.prompt.md -> "Close each open dispatch: `python ...fleet.py mark --dispatch-id <N> --outcome success`"; retro.prompt.md -> "`python ...fleet.py mark --dispatch-id <N> --outcome <success|failed|blocked>`". Both hit.
- [x] R-B1-3: `run_doctor` FAILS the "current-PI dispatch rows" check when the active PI has zero rows. Proof: against a fixture db with no rows for PI-7, `bootstrap.py doctor` prints `[FAIL] current-PI dispatch rows` and exits non-zero. (AC-1, FR-B1-4)
    - PROVEN 2026-06-26: `test_bootstrap.py::TestCurrentPiDispatchRowsCheck::test_fails_on_zero_rows_for_active_pi` PASSED (fixture db, 0 rows -> FAIL + non-zero).
- [x] R-B1-4: The same check PASSES once a row exists, and SKIPS when no `CURRENT_PI.md` marker is present. Proof: add a PI-7 row -> check PASS; rename markers away -> check absent/skipped, doctor still green. (AC-2, FR-B1-4)
    - PROVEN 2026-06-26: `test_passes_with_a_row` + `test_skips_with_no_marker` PASSED; live `bootstrap.py doctor` -> `[PASS] current-PI dispatch rows: PI-7: 2 row(s)`.
- [x] R-B1-5: The new `current_pi_name` helper is read-only and touches no Article X locked function. Proof: `git diff` shows no edit to `render_markdown`/`render_html`/locked peers; `TestS1FootprintLockGuard` PASS. (AC-4, FR-B1-5)
    - PROVEN 2026-06-26: `TestS1FootprintLockGuard` -> 3 passed, 234 deselected (golden SHA-256 intact); helper lives in bootstrap.py, not state_builder.py.
- [x] R-B1-6: After Sprint 15's dispatches are logged, the current PI shows real rows in `state.html`. Proof: regenerate state, `grep` shows PI-7 dispatch rows; doctor current-PI check PASSES. (AC-2, FR-B1-6)
    - PROVEN 2026-06-26: ledger PI-7 = rows 12 (architect, success) + 13 (software-developer, success); state regenerated; doctor `[PASS] current-PI dispatch rows: PI-7: 2 row(s)`.

### B-2 -- Turn the rules into blocking checks

- [x] R-B2-1: `tdd_gate_check.py` exits non-zero on a fixture where a production file changed with no test change and no `[NO-TEST-NEEDED]` tag. Proof: run `python cli/tdd_gate_check.py` against the FAIL fixture; exit code 1; message names the unguarded path. (AC-5, FR-B2-1)
    - PROVEN 2026-06-26: `tdd_gate_check.py --files done_check.py` -> `[FAIL] ... done_check.py`, EXIT 1; `--files done_check.py test_done_check.py` -> `[PASS]`, EXIT 0.
- [x] R-B2-2: `done_check.py` exits non-zero on a feature dir missing a required artifact or with an unchecked REQUIRED box. Proof: run against the FAIL fixture (no retro) and against a fixture with an unchecked `[ ]`; both exit 1 and list the gap. (AC-6, FR-B2-2)
    - PROVEN 2026-06-26: temp FAIL fixture -> `[FAIL] ... missing RETRO file` + `unchecked REQUIRED box R1`, EXIT 1; complete fixture -> `[PASS]`, EXIT 0.
- [x] R-B2-3: Both checks appear in `run_doctor`'s output. Proof: `bootstrap.py doctor` prints a `tdd gate` line and a `DONE completeness` line. (AC-7, FR-B2-3)
    - PROVEN 2026-06-26: live doctor printed `[PASS] tdd gate: ok` and `[PASS] DONE completeness: ok`; also `test_doctor_output_lists_three_new_checks` PASSED.
- [x] R-B2-4: Each rule has >= 1 test proving it catches a real violation AND >= 1 proving a clean case passes. Proof: the new `test_tdd_gate_check.py` and `test_done_check.py` contain both polarities and pass. (AC-5, AC-6, FR-B2-5)
    - PROVEN 2026-06-26: `pytest test_tdd_gate_check.py test_done_check.py -v` -> 11 passed; FAIL cases `test_prod_change_no_test_no_tag_fails`, `test_missing_retro_fails`, `test_unchecked_required_box_fails`; PASS cases present.
- [x] R-B2-5: `tdd-gate/SKILL.md` carries an "Enforced by: ...tdd_gate_check.py" pointer; the DONE prose surface carries an "Enforced by: ...done_check.py" pointer. Proof: `grep -i "Enforced by"` returns both. No `constitution/**` or `RULES.md` edit. (AC-7, FR-B2-4)
    - PROVEN 2026-06-26: tdd-gate/SKILL.md -> `## Enforced by` + `tdd_gate_check.py`; qa.prompt.md -> `Enforced by: ...done_check.py`. No constitution/** or RULES.md change.

### B-4 -- CI for everyone

- [x] R-B4-1: `.github/workflows/doctor.yml` exists and its run step invokes `make doctor`. Proof: file present; `grep "make doctor" .github/workflows/doctor.yml` returns a hit. (AC-8, FR-B4-1)
    - PROVEN 2026-06-26: `make doctor` present at line 3 (comment) and line 29 (`run: make doctor`).
- [x] R-B4-2: The workflow has no deploy / Azure-login / secret step. Proof: read the YAML; confirm only checkout + Python + `make doctor`; `grep -Ei "azure|deploy|secrets\\." ` returns nothing. (AC-9, FR-B4-2)
    - PROVEN 2026-06-26: whole-file `Select-String azure|deploy|secrets\.` over doctor.yml -> no matches; steps are checkout@v4 -> setup-python@v5 (3.12) -> `make doctor` only.
- [x] R-B4-3: ADR-021 (doctor-CI) exists and ADR-009 Status == superseded with a pointer to ADR-021. Proof: both files read; ADR-009 `Status` line shows `superseded by ADR-021`. (AC-10, FR-B4-3)
    - PROVEN 2026-06-26: ADR-009 -> `- Status: superseded by ADR-021` + `## Superseded by ADR-021`; ADR-021 -> `- Status: accepted` + `- Supersedes: ADR-009` (bidirectional).

### Cross-cutting

- [x] R-X-1: No new third-party dependency. Proof: `git diff` adds no install; all new modules import stdlib only. (AC-11, FR-X-1)
    - PROVEN 2026-06-26: tdd_gate_check.py imports pathlib/argparse/subprocess/sys; done_check.py imports pathlib/argparse/re/sys. All stdlib; no install added.
- [x] R-X-2: Article X locked functions intact; `TestS1FootprintLockGuard` PASS. Proof: run that test; PASS. (AC-4, FR-X-2)
    - PROVEN 2026-06-26: `TestS1FootprintLockGuard` -> 3 passed, 234 deselected, EXIT 0.
- [x] R-X-3: `python spec-driven-development/cli/schema_lint.py` exits 0. Proof: run it; exit 0. (AC-11, FR-X-3)
    - PROVEN 2026-06-26: schema_lint.py -> "Schema lint clean", EXIT 0.
- [x] R-X-4: Test baseline >= 501 passed / 2 skipped and grew. Proof: `pytest spec-driven-development -q` last line shows >= 501 passed plus the new tests. (AC-11, FR-X-4)
    - PROVEN 2026-06-26: `pytest spec-driven-development -q` -> "518 passed, 2 skipped", EXIT 0 (grew from 501/2).
- [x] R-X-5: Sprint 15 dogfoods B-1 -- it closes with its own dispatch outcomes in the ledger (this contract's R-B1-6 proves it for the current PI). (FR-B1-6)
    - PROVEN 2026-06-26: PI-7 dispatch rows 12 + 13 recorded success in the real append-only ledger (13 rows total).

---

## Optional Items

- [ ] O-1: file-scope check (FAIL when > 3 production files change in one task without justification). DEFERRED by clarify Q-C (highest false-positive risk; depends on diff plumbing proven by the TDD gate). Parked, not dropped. If picked up later it becomes a third B-2 rule with its own FAIL/PASS fixtures.

---

## Specific Test Coverage Required

- `test_tdd_gate_check.py`: (1) prod change + no test + no tag -> exit 1; (2) prod change + test change -> exit 0; (3) empty diff -> exit 0; (4) `[NO-TEST-NEEDED]` tag present -> exit 0.
- `test_done_check.py`: (1) dir missing retro -> exit 1; (2) dir with an unchecked REQUIRED `[ ]` -> exit 1; (3) complete dir -> exit 0.
- `test_bootstrap.py` (extend): (1) doctor current-PI check FAILS on 0-row active PI; (2) PASSES with a row; (3) SKIPS with no marker; (4) `current_pi_name` returns `PI-7` for the current tree.
- All new tests must use `tmp_path` isolation and a scratch `fleet.db` (never the real ledger).

---

## Manual Checks

- [x] M-1: `/qa` prompt close step reads correctly to a human (ledger write before DONE). -- read 2026-06-26: "## Ledger Close (required before DONE)" with fleet.py mark step.
- [x] M-2: `/retro` prompt ledger-check step reads correctly (rows present before retro final). -- read 2026-06-26: "## Ledger Check (before finalizing)" with fleet.py mark + doctor line.
- [x] M-3: `tdd-gate/SKILL.md` "Enforced by:" pointer resolves to the real script path. -- read 2026-06-26: points to `spec-driven-development/cli/tdd_gate_check.py`, which exists.
- [x] M-4: QA-section DONE "Enforced by: done_check.py" pointer resolves and does NOT live in `constitution/**`. -- read 2026-06-26: pointer in `.github/prompts/qa.prompt.md` -> `spec-driven-development/cli/done_check.py`; not under constitution/**.
- [x] M-5: `doctor.yml` job graph is valid (checkout -> python -> make doctor); triggers on push and pull_request. -- read 2026-06-26: `on: push / pull_request`; job `doctor` runs checkout@v4 -> setup-python@v5 -> `make doctor`.
- [x] M-6: ADR-021 reads as a coherent decision; ADR-009 supersede pointer is bidirectional-readable. -- read 2026-06-26: ADR-021 accepted, `Supersedes: ADR-009`; ADR-009 `superseded by ADR-021` + `## Superseded by ADR-021`.

---

## Definition of Done

F-39 (and Sprint 15) is DONE only when:
1. All REQUIRED items R-B1-1..R-X-5 are checked with real-command evidence.
2. All Manual Checks M-1..M-6 are checked.
3. `make doctor` is green end-to-end (every check PASS), including the two new B-2 checks and the B-1 current-PI check.
4. `schema_lint` exits 0; baseline >= 501/2 and grew; `TestS1FootprintLockGuard` PASS.
5. The current PI (PI-7) shows real dispatch rows in `state.html` -- the framework's own promise is no longer contradicted by `fleet.db`.
6. No task in tasks.md is left as `todo` without a named deferral (O-1 is the only pre-approved one).
