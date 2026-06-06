---
id: SDD-PI-5-S1-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-06
feature: symlink-portability
sprint: PI-5 / Sprint 1
spec: spec.md
---

# Validation Contract: Brownfield Portability Bundle (SDD-016 + SDD-017)

- Spec Reference: `spec.md` in this directory
- Contract Date: 2026-06-06
- Author: Principal Architect
- Lock Point: `/tasks` (this contract becomes immutable when `tasks.md` is
  authored; loosening it during `/implement` requires an Article X
  amendment).

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Required Items (R1..R7)

R1..R7 are REQUIRED. Zero unchecked REQUIRED items before /qa pass.

### R1 -- Explicit subcommand, dry-run default

- [ ] **R1**: `python bootstrap.py host-link --target <tmp>` (without
  `--apply`) prints a dry-run summary and exits 0 without mutating the
  filesystem. Verified by `test_host_link_dry_run` in
  `cli/test_bootstrap.py`. Proves AC-1 / AC-2.

### R2 -- Clean install (Linux/macOS path)

- [ ] **R2**: `python bootstrap.py host-link --target <tmp> --apply`
  against a clean target creates a symlink at `<tmp>/.github` that resolves
  to the framework's `.github/` directory. Verified by
  `test_host_link_apply_clean` in `cli/test_bootstrap.py`. Proves AC-1.

### R3 -- Conflict abort (default)

- [ ] **R3**: When the target already has `.github/` and neither `--backup`
  nor `--force` is passed, the tool aborts with a non-zero exit code and
  the stderr message names both `--backup` and `--force`. Verified by
  `test_host_link_conflict_abort`. Proves AC-3.

### R4 -- Conflict resolution via `--backup` / `--force`

- [ ] **R4**: `--backup --apply` moves the existing `.github/` to
  `.github.bak.<timestamp>` and creates the link; `--force --apply`
  recursively removes the existing `.github/` and creates the link. Both
  preserve the framework's `.github/` source unchanged. Verified by
  `test_host_link_backup` and `test_host_link_force`. Proves AC-4 / AC-5.

### R5 -- Windows junction fallback

- [ ] **R5**: When `os.symlink` raises `OSError` (mocked), the tool falls
  back to invoking `mklink /J` via `subprocess.run` with the resolved
  absolute paths. The fallback path is exercised by
  `test_host_link_windows_junction_fallback` with `unittest.mock.patch`,
  so the test runs on any platform. Proves AC-6.

### R6 -- Non-git-repo guard

- [ ] **R6**: When `--target` is a directory that is not a git repository,
  the tool aborts with a clear "not a git repository" message and exits 1.
  Verified by `test_host_link_not_a_git_repo`. Proves AC-7.

### R7 -- Roster + agent file + skill artifacts present and lint-clean

- [ ] **R7**: All four new artifacts exist and lint-clean:
  - `.github/agents/dev-env-manager-general.agent.md` (frontmatter:
    description present; `schema_lint.py` passes).
  - `.github/skills/operational/host-integration-symlink/SKILL.md`
    (frontmatter: name == directory name, description, license,
    metadata.author, quoted metadata.version; `schema_lint.py` passes).
  - `spec-driven-development/roster/agents.json` row for
    `dev-env-manager-general` with `kind: generic`, `role: dev-env-manager`.
  - `spec-driven-development/roster/skills.json` row for
    `host-integration-symlink` with `category: operational`.
  Verified by `python spec-driven-development/cli/schema_lint.py` (full
  repo scan) exits 0 plus a manual read of both JSON files.
  Proves the SDD-017 hire.

---

## Optional Items (O1..O2)

### O1 -- HOST-INTEGRATION.md walkthrough exists

- [ ] **O1**: `docs/HOST-INTEGRATION.md` exists and contains:
  - End-to-end install walkthrough.
  - The three CI/Actions mitigation options from clarification C6.
  - The conflict-mode decision tree (abort / backup / force).
  - A "rollback" subsection that describes how to remove the link and
    restore the host's original `.github/` from a `.github.bak.*` backup.
  Verified by manual read. Proves AC-8.

### O2 -- skill content rigor

- [ ] **O2**: `.github/skills/operational/host-integration-symlink/SKILL.md`
  body instructs the worker to (a) confirm `--target`, (b) prefer dry-run
  first, (c) prefer `--backup` over `--force`, (d) escalate to Architect
  on any unrecognised host state. Verified by manual read of the SKILL.md
  body. Proves AC-9.

---

## Specific Test Coverage Required

- [ ] Unit coverage for the `host-link` subparser (argparse routing, dry-run
  default behavior).
- [ ] Integration coverage for the clean-install path against a `tmp_path`
  fixture containing a `git init`-ed repo.
- [ ] Regression coverage for `bootstrap.py greenfield` and `bootstrap.py
  brownfield` -- the existing behavior MUST NOT change (smoke test that
  both subparsers still parse).
- [ ] Error, empty, boundary, or permission cases:
  - target does not exist (handled in `validate_brownfield_target`-style guard)
  - target is a file, not a directory
  - target is not a git repo
  - `.github/` already exists, no flag (R3)
  - `--backup` and `--force` both passed (mutually exclusive; argparse
    enforces)
  - dry-run does not touch the filesystem (assert no link, no backup dir
    after dry-run)

---

## Manual Checks

- [ ] `python spec-driven-development/cli/schema_lint.py spec-driven-development/specs/
  spec-driven-development/sprints/` exits 0 (no findings in the new spec
  dir's three frontmatter blocks).
- [ ] `python spec-driven-development/cli/schema_lint.py` (default scan)
  exits 0 (covers the new agent file and the new skill file).
- [ ] `python -m pytest spec-driven-development/ --tb=no -q` shows tests
  count >= 200 baseline + new tests for this feature (target +5 minimum;
  R1..R6 plus regression smoke gives 7-9 net new).
- [ ] Manual read of `docs/HOST-INTEGRATION.md` confirms walkthrough and
  the three CI mitigation options.

## Tone / UX Check

Applicable for the CLI output and the docs:

- [ ] CLI dry-run output is human-readable and lists the planned action +
  the path that would be created. No JSON in default mode.
- [ ] Error messages name the remediation (e.g. "use --backup or --force",
  "target is not a git repository").
- [ ] `docs/HOST-INTEGRATION.md` is written for a host operator who has
  never used SDD; minimum context required.

## Definition of Done

Implementation is merge-ready only when:

- R1..R7 are all checked.
- O1 + O2 are checked (treated as REQUIRED for this feature per
  clarification-log; the "optional" tier exists for items the implementation
  may defer with written justification -- nothing in this contract is
  deferred).
- All listed automated tests pass.
- The full test suite passes (>= 200 baseline + new tests for this
  feature).
- The new spec dir's three artifacts (clarification-log.md, spec.md,
  validation.md) are committed with valid SDD-FDC-001 frontmatter.
- The schema_lint full scan exits 0.
- `BACKLOG.md` rows for SDD-016 and SDD-017 are marked DONE with the
  implementation commit SHA.
- `sprints/PI-5/CURRENT_PI.md` Sprint 1 entry is marked DONE with date,
  commit SHAs, and a one-paragraph retro.
