---
id: SDD-PI-5-S1-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: symlink-portability
sprint: PI-5 / Sprint 1
backlog: SDD-016, SDD-017
clarification: clarification-log.md
validation: validation.md
---

# Feature Spec: Brownfield Portability Bundle (SDD-016 + SDD-017)

- Date: 2026-06-06
- Author: Principal Architect (consolidated worker session per owner directive 2026-06-06)
- Status: Active (locks at /tasks)
- Priority: P1
- Sprint: PI-5 / Sprint 1 (= overall Sprint 5)
- Spec ID: SDD-PI-5-S1

---

## Problem Statement

The Evolving Multi-Agent Framework is currently confined to its own
repository. A team that wants to adopt SDD on an existing project (a host
repo) has only two ugly options today:

1. **Copy the framework's `.github/` into the host.** Creates a fork that
   drifts from the framework's `master` and must be manually rebased on every
   framework update. Defeats the central-update model.
2. **Bootstrap greenfield/brownfield into a fresh adjacent directory and
   tell the host's team to switch.** Requires destructive migration of host
   code and history.

Neither path is acceptable for adoption. The Scott Feedback Bundle
(2026-06-02 meeting; triaged 2026-06-03) flagged this as the brownfield
finisher with the highest leverage: ship the symlink trick so any host can
`bootstrap.py host-link --target .` and inherit the framework's `.github/`
without polluting their own.

Two backlog items co-spec this bundle because they share a feature surface:

- **SDD-016** -- `.github/` symlink portability trick (cli + skill).
- **SDD-017** -- Hire a `dev-env-manager-general` worker that owns
  environment plumbing (the symlink, plus future worktree/branch/env work).

A worker (SDD-017) cannot be evaluated for promotion without real work to do;
the symlink trick (SDD-016) is the natural first task. They ship together.

---

## Proposed Solution

### Overview

Add a third subcommand to `cli/bootstrap.py`:

```
python bootstrap.py host-link --target <host-repo-path> [--apply] [--backup] [--force]
```

Implementation strategy:

1. Resolve the framework's `.github/` directory to an absolute path
   (already a helper in `bootstrap.py` via `framework_root()`).
2. Validate the target is an existing git repo (reuse
   `validate_brownfield_target()` logic).
3. Detect any existing `.github/` in the target.
4. Per-platform create the link:
   - Linux/macOS: `os.symlink(framework_github_dir, target_link_path,
     target_is_directory=True)`.
   - Windows: try `os.symlink` first; on `OSError` fall back to
     `subprocess.run(["cmd", "/c", "mklink", "/J", str(link_path),
     str(target)])`.
5. Apply conflict handling per C3 (`--backup` / `--force` / abort).
6. Dry-run mode is the default; `--apply` is required to mutate the
   filesystem.
7. Print a structured summary of action taken and next steps.

### New Files

- `.github/agents/dev-env-manager-general.agent.md` -- new generic worker
  agent file (templated from `developer-general.agent.md`).
- `.github/skills/operational/host-integration-symlink/SKILL.md` -- new
  skill describing the install/rollback procedure, conflict modes, and
  platform branches.
- `docs/HOST-INTEGRATION.md` -- end-to-end walkthrough for a host operator,
  including the CI/Actions trade-off and the three mitigation options
  documented in clarification-log C6.
- `cli/test_bootstrap.py` -- new test module covering the `host-link`
  subcommand. Stdlib only (`tempfile`, `unittest.mock.patch`, `pathlib`).

### Roster Additions

- `roster/agents.json` -- new row for `dev-env-manager-general`.
- `roster/skills.json` -- new row for `host-integration-symlink`.

### Extended Files

- `cli/bootstrap.py` -- additive extension. New `host-link` subparser, new
  `run_host_link(args)` handler, new helpers (`resolve_framework_github`,
  `install_link_unix`, `install_link_windows_with_fallback`,
  `handle_existing_github`, `format_dry_run_report`). Existing
  `greenfield` and `brownfield` behavior remains byte-for-byte unchanged.

### Clarification Decisions Locked In Spec

All nine C-rows in `clarification-log.md` are CLOSED. Quick reference:

| C | Decision |
|---|----------|
| C1 | Explicit `host-link` subcommand; dry-run default; `--apply` required for mutation. |
| C2 | Try `os.symlink` first; fall back to `mklink /J` (junction) on Windows OSError. |
| C3 | Abort by default; `--backup` (timestamped) and `--force` (destructive) are opt-in mutually-exclusive flags. |
| C4 | No auto-detection of host context; `--target` is always explicit. Out of scope for v1. |
| C5 | Live symlink; no version pin in v1. |
| C6 | Host CI inherits framework workflows; documented with three mitigation options; do not split the link in v1. |
| C7 | `dev-env-manager-general` is a generic worker, not a Principal. |
| C8 | New agent file + new skill pack + two roster rows. |
| C9 | Dispatch via existing `cli/fleet.py dispatch`; no new slash command in v1. |

---

## Acceptance Criteria

1. Given a clean target directory with no `.github/`, when the user runs
   `python bootstrap.py host-link --target <tmp> --apply`, then a symlink
   (Linux/macOS) or junction (Windows) is created at `<tmp>/.github`
   pointing at the framework's `.github/`.
2. Given the same precondition and the same command WITHOUT `--apply`,
   then the tool prints a dry-run report describing the action it WOULD
   take and exits 0 without mutating the filesystem.
3. Given a target whose `.github/` already exists and no conflict flag,
   when the user runs `host-link --target <tmp> --apply`, then the tool
   aborts with a non-zero exit code and a remediation message naming
   `--backup` and `--force`.
4. Given the same precondition and `--backup --apply`, then the tool moves
   `<tmp>/.github` to `<tmp>/.github.bak.<timestamp>` and creates the link.
5. Given the same precondition and `--force --apply`, then the tool deletes
   `<tmp>/.github` recursively and creates the link.
6. Given a Windows-like platform where `os.symlink` raises OSError, when the
   tool runs `--apply`, then it falls back to a `mklink /J` invocation that
   creates a junction. Verified via mocked test (`unittest.mock.patch` on
   `os.symlink` and `subprocess.run`).
7. Given a target that is not a git repository, when the user runs
   `host-link --apply`, then the tool aborts with a clear "not a git
   repository" message (matches brownfield validation behavior).
8. Given a successful install, when the user reads `docs/HOST-INTEGRATION.md`,
   then they find an end-to-end walkthrough including the three CI/Actions
   mitigation options documented in clarification C6.
9. Given a worker dispatch loads
   `.github/skills/operational/host-integration-symlink/SKILL.md`, then the
   skill instructs the worker to (a) confirm `--target`, (b) prefer dry-run
   first, (c) prefer `--backup` over `--force`, (d) escalate to Architect
   on any unrecognised host state.

---

## Affected Modules

- Files:
  - `spec-driven-development/cli/bootstrap.py` (extension)
  - `spec-driven-development/cli/test_bootstrap.py` (new)
  - `.github/agents/dev-env-manager-general.agent.md` (new)
  - `.github/skills/operational/host-integration-symlink/SKILL.md` (new)
  - `spec-driven-development/roster/agents.json` (additive row)
  - `spec-driven-development/roster/skills.json` (additive row)
  - `spec-driven-development/docs/HOST-INTEGRATION.md` (new)
- Directories:
  - `.github/skills/operational/host-integration-symlink/` (new)

**Blocked (not touched by this spec)**:

- `cli/state_builder.py` (PI-4 locked surface still applies).
- `constitution/**` (Article VIII -- this work hires a worker via roster
  rows only; no constitutional amendment is needed).
- Any other in-flight spec dir.

---

## Data Model Changes

None. The roster additions are additive JSON rows under the existing
schema. The host-link operation creates a filesystem symlink/junction;
nothing persists in the ledger or in any database.

---

## API Changes

CLI additions only:

- `bootstrap.py host-link --target PATH [--apply] [--backup] [--force]`.
- Exit codes: 0 success / dry-run, 1 validation failure or conflict abort,
  2 usage error (argparse default).

---

## Test Strategy

- **Unit**: `cli/test_bootstrap.py` covers dry-run output, clean install,
  conflict-abort, backup mode, force mode, windows-junction fallback (via
  mock), not-a-git-repo guard.
- **Integration**: an end-to-end test creates a temp host directory with
  `git init`, runs the dry-run, then runs the apply, then asserts the
  symlink/junction exists and resolves to the framework's `.github/`.
- **Schema lint regression**: `python schema_lint.py spec-driven-development/specs/
  spec-driven-development/sprints/` exits 0; the new spec dir's three
  markdown artifacts (clarification-log, spec, validation) carry valid
  frontmatter per SDD-FDC-001.
- **Regression**: existing 200-test suite continues to pass; no PI-4
  test removed or skipped.

---

## Validation Contract

The binding validation contract for this feature lives in
[`validation.md`](validation.md). It is locked at /tasks.

---

## Traceability Matrix

| Requirement (clarification + AC) | Acceptance Test | Module |
|-----------------------------------|-----------------|--------|
| C1 / AC-1 / AC-2 (explicit subcommand, dry-run default) | `test_host_link_dry_run`, `test_host_link_apply_clean` | `cli/bootstrap.py`, `cli/test_bootstrap.py` |
| C2 / AC-6 (Windows junction fallback) | `test_host_link_windows_junction_fallback` | `cli/bootstrap.py`, `cli/test_bootstrap.py` |
| C3 / AC-3, AC-4, AC-5 (conflict handling) | `test_host_link_conflict_abort`, `test_host_link_backup`, `test_host_link_force` | `cli/bootstrap.py`, `cli/test_bootstrap.py` |
| C6 / AC-8 (CI/Actions trade-off documented) | manual read of `docs/HOST-INTEGRATION.md` | `docs/HOST-INTEGRATION.md` |
| C7 / AC-? (generic worker rostered) | manual read of `roster/agents.json` row; `schema_lint` clean | `roster/agents.json`, `.github/agents/dev-env-manager-general.agent.md` |
| C8 / AC-? (skill rostered) | manual read of `roster/skills.json` row; `schema_lint` clean | `roster/skills.json`, `.github/skills/operational/host-integration-symlink/SKILL.md` |
| AC-7 (non-git-repo guard) | `test_host_link_not_a_git_repo` | `cli/bootstrap.py`, `cli/test_bootstrap.py` |
| AC-9 (skill content) | manual read of `SKILL.md` body | `.github/skills/operational/host-integration-symlink/SKILL.md` |

---

## Open Questions

None at SPEC time. All nine clarification rows are CLOSED.

The first realistic question for a future iteration: do we want a
`host-link --pin <commit-sha>` mode that pins the framework to a tagged
commit by linking to a separate worktree? Not in scope for v1.

---

## Out of Scope

- Auto-detection of host context (per C4).
- Version pinning of the framework via the link (per C5).
- Splitting the link into per-subdirectory granularity (`.github/agents`,
  `.github/skills`, `.github/prompts` separately) (per C6).
- A new `/env` slash command (per C9).
- Live integration against the Day-to-Day Agent host repo. The validation
  is `tmp_path` only in Sprint 1; a live demo is its own decision.
- Any change to `cli/state_builder.py` (PI-4 locked surface).
- Any constitution amendment.
