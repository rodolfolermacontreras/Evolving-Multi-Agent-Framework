---
id: SDD-PI-5-S1-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-06
feature: symlink-portability
sprint: PI-5 / Sprint 1
spec: spec.md
plan: plan.md
validation: validation.md
---

# Tasks: Brownfield Portability Bundle (SDD-016 + SDD-017)

Locks validation.md at this point. Loosening any R-row from here on requires
an Article X amendment.

Total: 11 tasks across 5 phases. Each task names its `allowed_files`,
`blocked_files`, and the R-row(s) it proves.

---

## Phase 1 -- TASKS scaffold

### T-01 -- author tasks.md (this file)

- Owner: Principal Software Developer
- Allowed files: `specs/2026-06-06-symlink-portability/tasks.md`
- Blocked files: all `cli/**`, all `roster/**`, all `.github/**`
- Proves: structural; not bound to an R-row.
- Status: done (this file, in this commit).

---

## Phase 2 -- TESTS first

### T-02 -- author `cli/test_bootstrap.py` (failing)

- Owner: Principal Software Developer
- Allowed files: `cli/test_bootstrap.py` (new)
- Blocked files: `cli/bootstrap.py`, all `roster/**`, all `.github/**`
- Tests authored:
  - `test_host_link_dry_run` (R1, AC-2)
  - `test_host_link_apply_clean` (R2, AC-1)
  - `test_host_link_conflict_abort` (R3, AC-3)
  - `test_host_link_backup` (R4, AC-4)
  - `test_host_link_force` (R4, AC-5)
  - `test_host_link_windows_junction_fallback` (R5, AC-6) -- mocked
  - `test_host_link_not_a_git_repo` (R6, AC-7)
  - `test_greenfield_subparser_unchanged` (regression smoke)
  - `test_brownfield_subparser_unchanged` (regression smoke)
- Acceptance: all seven new tests fail with the expected "no `host-link`
  subcommand" or attribute errors. The two regression smoke tests pass.
- Proves: R1..R6.

---

## Phase 3 -- IMPLEMENT bootstrap.py extension

### T-03 -- add `host-link` subparser

- Owner: Principal Software Developer
- Allowed files: `cli/bootstrap.py` (additive only -- new subparser block
  inside `parse_args`)
- Blocked files: anything that changes existing `greenfield` or `brownfield`
  semantics
- Acceptance: `test_host_link_dry_run` reaches the dispatcher (it no longer
  fails on "no such subcommand"); the regression smoke tests still pass.

### T-04 -- add helpers

- Owner: Principal Software Developer
- Allowed files: `cli/bootstrap.py` (additive helpers)
- New functions:
  - `resolve_framework_github() -> Path` -- returns absolute path to the
    framework's `.github/`.
  - `validate_host_link_target(target: Path) -> Path` -- reuses the
    is-git-repo guard from `validate_brownfield_target`; returns the
    resolved target.
  - `install_link(framework_github: Path, link_path: Path) -> str` --
    creates the symlink/junction; returns "symlink" or "junction" depending
    on which path succeeded. Raises `BootstrapError` on hard failure.
  - `handle_existing_github(link_path: Path, mode: str) -> str | None` --
    given mode in {"abort", "backup", "force"}, either raises
    `BootstrapError` (abort), moves to timestamped backup, or recursively
    deletes. Returns the backup path string (mode=backup) or None.
  - `format_dry_run_report(target, link_path, action) -> str` -- builds the
    multi-line dry-run summary.
- Acceptance: helpers exist; calls from `run_host_link` (T-05) succeed.

### T-05 -- add `run_host_link(args)` and wire into `main()`

- Owner: Principal Software Developer
- Allowed files: `cli/bootstrap.py` (additive dispatcher + 1-line wire-up
  in `main`)
- Acceptance: all seven `test_host_link_*` tests pass. Regression smoke
  tests still pass. Full suite green.
- Proves: R1, R2, R3, R4, R5, R6 (all the test-backed REQUIRED rows).

---

## Phase 4 -- Roster + agent + skill

### T-06 -- write `.github/agents/dev-env-manager-general.agent.md`

- Owner: Principal Software Developer
- Allowed files: `.github/agents/dev-env-manager-general.agent.md` (new)
- Blocked files: anything else
- Template: based on `.github/agents/developer-general.agent.md` with
  scope substituted for env/symlink/worktree concerns.
- Frontmatter: name (auto), description (required). Body sections: Identity,
  What You Need Before Starting, Core Responsibilities, Workflow,
  Implementation Rules, Pre-Flight Checklist, Self-Review, Escalate When,
  Promotion Path.
- Acceptance: file exists; schema_lint default scan exits 0.

### T-07 -- write `.github/skills/operational/host-integration-symlink/SKILL.md`

- Owner: Principal Software Developer
- Allowed files: `.github/skills/operational/host-integration-symlink/SKILL.md`
  (new)
- Blocked files: anything else
- Frontmatter required (per `check_skill`): `name` (matches directory),
  `description`, `license: MIT`, `metadata.author`, `metadata.version` (quoted).
- Body sections: Why This Matters, Canonical Instruction, Protocol (the
  4 steps from C8: confirm target, prefer dry-run, prefer backup over force,
  escalate on unrecognised state), Conflict Decision Tree, Platform Notes
  (Windows fallback), Compliance Example, Escape Hatch.
- Acceptance: schema_lint default scan exits 0.

### T-08 -- add roster rows

- Owner: Principal Software Developer
- Allowed files: `roster/agents.json`, `roster/skills.json`
- Append:
  - `agents.json`: row for `dev-env-manager-general`.
  - `skills.json`: row for `host-integration-symlink`.
- Acceptance: JSON validates (no trailing comma); schema_lint full scan
  exits 0; full pytest suite green.
- Proves: R7 (together with T-06 and T-07).

---

## Phase 5 -- Docs + sprint close

### T-09 -- write `docs/HOST-INTEGRATION.md`

- Owner: Principal Software Developer
- Allowed files: `spec-driven-development/docs/HOST-INTEGRATION.md` (new)
- Blocked files: anything else
- Required sections (per O1):
  - Overview
  - Prerequisites
  - End-to-end walkthrough
  - Conflict decision tree (abort / backup / force)
  - Three CI/Actions mitigation options (from C6)
  - Rollback procedure
- Note: file is under `docs/**` which is OUT of scope for SDD-FDC-001; no
  frontmatter required, but a heading and short metadata block is good
  practice.
- Acceptance: file exists with all six sections; manual read passes.
- Proves: O1 (treated as REQUIRED).

### T-10 -- mark BACKLOG SDD-016 + SDD-017 as DONE

- Owner: Principal Software Developer
- Allowed files: `backlog/BACKLOG.md`
- Acceptance: both rows show DONE with the implementation commit SHA.

### T-11 -- close Sprint 5

- Owner: Principal Software Developer + Executive Manager (close stamp)
- Allowed files:
  - `specs/2026-06-06-symlink-portability/validation.md` (tick R1..R7,
    O1..O2)
  - `specs/2026-06-06-symlink-portability/tasks.md` (status pending -> done)
  - `specs/2026-06-06-symlink-portability/spec.md` (status active -> done)
  - `specs/2026-06-06-symlink-portability/plan.md` (status active -> done)
  - `specs/2026-06-06-symlink-portability/clarification-log.md` (already done)
  - `sprints/PI-5/CURRENT_PI.md` (Sprint 1 retro + DONE)
  - `exec/sprint-progress.md` (F-05 + Sprint 5 close blocks)
  - `exec/state.md`, `exec/state.html`, `exec/work-index.md` (regenerated)
  - `docs/Management/PI-5/INDEX.md` (regenerated)
- Acceptance: AC-9 through AC-13 from F-05 prompt section 4 all met.
- Proves: sprint close gates.

---

## Traceability matrix

| R-row | Task(s) | Test(s) | Source |
|-------|---------|---------|--------|
| R1 | T-02, T-05 | `test_host_link_dry_run` | spec AC-1, AC-2 |
| R2 | T-02, T-05 | `test_host_link_apply_clean` | spec AC-1 |
| R3 | T-02, T-04, T-05 | `test_host_link_conflict_abort` | spec AC-3 |
| R4 | T-02, T-04, T-05 | `test_host_link_backup`, `test_host_link_force` | spec AC-4, AC-5 |
| R5 | T-02, T-04, T-05 | `test_host_link_windows_junction_fallback` | spec AC-6 |
| R6 | T-02, T-04, T-05 | `test_host_link_not_a_git_repo` | spec AC-7 |
| R7 | T-06, T-07, T-08 | `schema_lint` clean | spec C7, C8 |
| O1 | T-09 | manual read | spec AC-8 |
| O2 | T-07 | manual read of SKILL body | spec AC-9 |

No orphan R-rows. No orphan tasks (every task proves at least one R-row or
is a structural/closure task).

---

## Frontmatter contract note

This `tasks.md` carries `status: active` (per the SDD-FDC-001 enum). It is
flipped to `status: done` in T-11 when the sprint closes -- consistent with
the FDC `tasks.md status: active` convention introduced in PI-4 Sprint 4
(see `specs/2026-06-04-filesystem-data-contracts/tasks.md` "Frontmatter
contract note").
