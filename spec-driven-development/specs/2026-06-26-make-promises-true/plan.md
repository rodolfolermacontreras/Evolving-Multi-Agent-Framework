---
id: SDD-20260626MAKEPROMISESTRUE-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-make-promises-true
depends_on: [SDD-045]
---

# PLAN: SDD-046 -- "Make promises true"

- Feature ID: SDD-046. Items: B-1, B-2, B-4. Sprint: PI-7 Sprint 15.
- Spec: [spec.md](spec.md). Tasks: [tasks.md](tasks.md). Validation: [validation.md](validation.md).
- Implementation happens in F-39 (IMPLEMENT + QA). This plan is the build order and the attach-point map.

---

## Approach (numbered sequence)

1. B-1 first (it is the priority and it is what Sprint 15 dogfoods at close). Land the doctor current-PI check + read-only helper, then the `/qa` + `/retro` close steps. After this, Sprint 15's own dispatches must be logged before F-40 closes.
2. B-2 second. Port the TDD-gate algorithm into `cli/tdd_gate_check.py`, add `cli/done_check.py`, wire both into `run_doctor`, point the prose skills at them. Tests for both rules land WITH the rule (TDD on ourselves).
3. B-4 last. Add `.github/workflows/doctor.yml` == `make doctor`; author ADR-021; mark ADR-009 superseded. CI lands only after the checks it runs are green locally.
4. Re-run `make doctor` and `schema_lint`; confirm baseline grows; log Sprint 15 dispatches; F-40 close gate verifies the current PI shows real rows.

---

## Item-by-item implementation notes (attach points)

### B-1 -- ledger truth

- `run_doctor` attach point: `spec-driven-development/cli/bootstrap.py`, the `checks: list[tuple[str, bool, str]]` aggregation (the (a)-(e) block ending at the tests check). ADD a new entry (f) "current-PI dispatch rows" after (a) ledger reachable, gated on `is_framework`.
- New read-only helper (same module): `current_pi_name(root) -> str | None`. Resolve by globbing `root / "spec-driven-development" / "sprints" / "PI-*" / "CURRENT_PI.md"` (the same markers `state_builder` reads at `state_builder.py` line ~666) and selecting the highest-numbered PI that has an active marker. Read-only; it MUST NOT import or edit `render_markdown` / `render_html` or any Article X locked function. If `state_builder` exposes a reusable read-only resolver, prefer calling it over duplicating; otherwise add a minimal local glob.
- Check body: open `fleet.db`, `SELECT COUNT(*) FROM dispatches WHERE pi = ?` with the resolved PI name; `ok = count > 0`; detail = `f"{count} row(s) for {pi}"` or `"0 rows for {pi} -- log dispatch outcomes with fleet.py mark"`. If no current PI marker is found, the check is skipped (not failed) -- doctor must stay green on a repo between PIs.
- Close step (no code): `fleet.py mark --dispatch-id <N> --outcome {success|failed|blocked} [--notes ...]` already exists (`cli/fleet.py`). Document it as THE close one-liner in `cli/fleet.py` usage/help text only -- no signature change.
- Prompt edits: `.github/prompts/qa.prompt.md` -- add a "Ledger close step" bullet under the QA flow: before declaring DONE, record each dispatch outcome with `fleet.py mark`. `.github/prompts/retro.prompt.md` -- add a "Ledger check" bullet: confirm the sprint's dispatch outcomes are in the ledger before the retro is final.

### B-2 -- blocking checks

- `cli/tdd_gate_check.py` (NEW, stdlib-only, `main(argv) -> int`):
  - Accepts `--base <ref>` / `--head <ref>` (commit range) and, with no range, evaluates the working-tree diff (`git diff --name-only` + `git diff --cached --name-only`). On an empty diff -> nothing to gate -> exit 0 (keeps doctor green on a clean tree).
  - Classifies changed paths into production vs test using the repo convention (test = basename matches `test_*.py` or path under a `tests/` dir; production = other `*.py` under `spec-driven-development/cli/` and `agent`-style source dirs). Port the exact classification + `[NO-TEST-NEEDED]` escape-hatch logic from `.github/skills/engineering/tdd-gate/SKILL.md` "Mechanical Check".
  - FAILS (exit 1) when >= 1 production path changed, no test path changed in the same range, and no `[NO-TEST-NEEDED]` tag appears in the range's commit messages. Else exit 0.
- `cli/done_check.py` (NEW, stdlib-only, `main(argv) -> int`):
  - Accepts one or more feature-dir paths (or `--pi <name>` to scan the current PI's done dirs). For each: assert `spec.md` exists; assert a `validation.md` exists and every REQUIRED `[ ]` checkbox under its "Required Items" sections is checked `[x]`; assert a retro artifact exists (RETRO.md or the sprint retro referencing the feature). FAIL (exit 1) on any miss; list each gap.
  - In `run_doctor`, invoke with `--pi <current PI>` so it only gates the current PI's done dirs (bounds false positives on historical dirs that predate the rule).
- `run_doctor` wiring: add checks (g) "tdd gate" and (h) "DONE completeness" to the same `checks` list, gated on `is_framework`. Call the modules' functions in-process (import + call), NOT via subprocess, so doctor and CI share one code path.
- Prose pointers: `tdd-gate/SKILL.md` -- add "Enforced by: spec-driven-development/cli/tdd_gate_check.py". The DONE-completeness prose home (RULES Section 4 is constitution-adjacent and must NOT be edited; instead add the pointer in the QA/retro flow or a DONE skill) -- add "Enforced by: spec-driven-development/cli/done_check.py" to whichever non-constitution prose surface describes the DONE checklist (preferred: `qa.prompt.md` close section). Do NOT edit `constitution/**` or `RULES.md`.

### B-4 -- CI

- `.github/workflows/doctor.yml` (NEW): triggers `on: [push, pull_request]`; one job: `actions/checkout`, set up Python (3.12), `run: make doctor`. No deploy, no Azure login, no secret. For PRs the TDD gate receives the PR range via `--base ${{ github.event.pull_request.base.sha }} --head ${{ github.sha }}` if a thin wrapper is desired; otherwise `make doctor`'s working-tree default is sufficient for push and the gate runs clean (note: CI red on rule break comes from the doctor checks already in the set).
- ADR-021 (NEW, authored in F-39): "CI runs the doctor set on push and PR". Records: scope = validation only (no deploy); entrypoint = `make doctor` for local==CI parity; supersedes ADR-009 (Azure ACA deploy CI, never built, premise removed by ADR-015/SDD-035). Set ADR-009 `Status` to `superseded by ADR-021` with a one-line pointer.

---

## Sequencing / dependencies

- B-1 doctor check depends on the current-PI helper (same task).
- B-2 doctor wiring depends on both check modules existing.
- B-4 workflow depends on B-2 checks being green locally (CI just runs `make doctor`).
- ADR-021 depends on the B-4 decision (already locked in clarify Q-D); ADR-009 edit depends on ADR-021 existing.
- Shared-file serialization (CRITICAL for F-39 dispatch): `cli/bootstrap.py` is touched by BOTH B-1 (check f + helper) and B-2 (checks g/h wiring). These MUST be serialized -- one dispatch owns all `bootstrap.py` edits, or B-1's bootstrap edit completes and merges before B-2's begins. Likewise `qa.prompt.md` is touched by B-1 (close step) and possibly B-2 (DONE pointer) -- serialize.

---

## Constraints honored

- Stdlib-only: argparse, sqlite3, pathlib, json, sys, os, subprocess, re. No new dependency (Article V).
- Article X: only new read-only helpers + new modules + additive `checks` entries. No locked render function is edited; `TestS1FootprintLockGuard` golden SHA-256 stays PASS.
- Append-only ledger: `fleet.py mark` updates outcome on an existing dispatch row; no destructive rewrite.
- No `constitution/**` edit: promises are made true; Article VII and RULES Rule 4 keep their wording.
- Baseline >= 501 passed / 2 skipped and grows (each new check adds tests).
- Local == CI: doctor functions are called in-process; CI calls `make doctor`.

---

## Risks

- R-a (TDD-gate false positives on refactors / doc-only changes): a production-file rename with no test change could trip the gate. Mitigate: port the SKILL.md `[NO-TEST-NEEDED]` escape hatch faithfully; default doctor to the working-tree diff (empty on a clean tree); start strict only on `cli/**` production paths. File-scope (the higher-FP rule) is deliberately deferred to O-1.
- R-b (DONE-completeness flags historical dirs): older closed feature dirs may lack a retro or have unchecked REQUIRED boxes, turning doctor red immediately. Mitigate: scope the doctor invocation to the CURRENT PI's done dirs (`--pi`); fixing a genuinely-incomplete current-PI dir is make-true work, not scope creep. If a historical dir must be swept, do it as an explicit, separate, owner-visible task -- not silently inside this check.
- R-c (current-PI helper drifts from state_builder's resolver): two code paths for "what is the current PI" can disagree. Mitigate: prefer importing/reusing state_builder's read-only marker reader; if duplicated, add a test asserting the helper agrees with the `CURRENT_PI.md` marker for PI-7.
