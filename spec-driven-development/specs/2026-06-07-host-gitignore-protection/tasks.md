---
id: SDD-20260607GITIGN-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Task List: Host `.gitignore` Protection (SDD-027)

- Feature: SDD-027 (+ SDD-028, SDD-029 pull-ins)
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Author: Principal Software Developer
- Date: 2026-06-07
- Test baseline: >= 213

---

## Task T-027-01: Create host_gitignore_manifest.json

**Story**: [R6] MUST-BE-IGNORED and MUST-BE-TRACKED path lists
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/host_gitignore_manifest.json
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: NONE

### Description

Create `cli/host_gitignore_manifest.json` with two arrays:
- `must_be_ignored`: framework paths the host must NEVER commit (e.g.,
  generated artifacts, ledger DB, session state).
- `must_be_tracked`: framework paths the host MUST keep visible to git
  (e.g., `.github/agents/`, `.github/skills/`, `.github/prompts/`).

Paths should match the framework's actual layout. Schema:
```json
{
  "must_be_ignored": ["pattern1", "pattern2"],
  "must_be_tracked": ["pattern3", "pattern4"]
}
```

### Acceptance Criteria

- [ ] JSON file loads without error
- [ ] Schema valid: two top-level arrays of strings
- [ ] `must_be_ignored` paths match framework-internal artifacts
- [ ] `must_be_tracked` paths match framework-external-facing artifacts
- [ ] No overlap between the two lists

### Verification

```
python -c "import json; d=json.load(open('cli/host_gitignore_manifest.json')); assert 'must_be_ignored' in d and 'must_be_tracked' in d"
```

---

## Task T-027-02: Implement static .gitignore parser

**Story**: [R2] Detection uses static parse of host .gitignore
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-01

### Description

Add `_parse_gitignore(gitignore_path)` to `cli/bootstrap.py` that:
- Reads the host's `.gitignore` file.
- Parses ignore rules (handling comments, negation, wildcards).
- Compares rules against the manifest's MUST-BE-IGNORED and
  MUST-BE-TRACKED lists.
- Returns a conflict report: paths that should be ignored but aren't,
  and paths that should be tracked but are ignored.

### Acceptance Criteria

- [ ] Parses standard `.gitignore` syntax (comments, blank lines, negation)
- [ ] Detects MUST-BE-IGNORED paths missing from `.gitignore`
- [ ] Detects MUST-BE-TRACKED paths present in `.gitignore` (over-aggressive)
- [ ] Returns structured conflict report

### Verification

```
python -m pytest cli/test_bootstrap.py -k "parse_gitignore" -v --tb=short
```

---

## Task T-027-03: Implement live git check-ignore detection

**Story**: [R2] Live git check-ignore for authoritative answer
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-02

### Description

Add `_git_check_ignore(host_root, paths)` to `cli/bootstrap.py` that:
- Runs `git check-ignore` via subprocess against the manifest paths.
- Returns which manifest paths are actually ignored by git (catches
  global excludes, parent-dir `.gitignore`, `core.excludesFile`).
- If static parse and live check disagree, live check wins.

### Acceptance Criteria

- [ ] Subprocess `git check-ignore` called correctly
- [ ] Global excludes caught by live check but not static parse
- [ ] Conflict report includes both static and live results
- [ ] Graceful fallback if `git` not available (error message, not crash)

### Verification

```
python -m pytest cli/test_bootstrap.py -k "check_ignore" -v --tb=short
```

---

## Task T-027-04: Implement --gitignore-mode flag + --no-gitignore-check

**Story**: [R3, R4] Four modes with opt-out
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-03

### Description

Add to `host-link` subcommand:
- `--gitignore-mode {strict|prompt|warn|skip}` (default: `prompt`):
  - `strict`: any conflict -> exit 1 (no interactive prompt).
  - `prompt`: conflict -> display diff + prompt owner to fix or proceed.
  - `warn`: conflict -> display warning + proceed.
  - `skip`: skip gitignore check entirely.
- `--no-gitignore-check`: alias for `--gitignore-mode skip`.

### Acceptance Criteria

- [ ] `strict` mode: conflict -> exit 1
- [ ] `prompt` mode: conflict -> interactive prompt
- [ ] `warn` mode: conflict -> warning + proceed
- [ ] `skip` mode: no check performed
- [ ] `--no-gitignore-check` equivalent to `--gitignore-mode skip`
- [ ] Default mode is `prompt`

### Verification

```
python -m pytest cli/test_bootstrap.py -k "gitignore_mode" -v --tb=short
```

---

## Task T-027-05: Implement missing-.gitignore refusal

**Story**: [R5] Refuse host-link if host has no .gitignore
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-04

### Description

If the host directory has no `.gitignore` file:
- Refuse the `host-link` install (exit 1).
- Print a clear message explaining why.
- Emit recommended `.gitignore` content (minimal rules from the manifest).

### Acceptance Criteria

- [ ] Host with no `.gitignore` -> exit 1
- [ ] Error message explains `.gitignore` is required
- [ ] Recommended content printed to stdout
- [ ] `--no-gitignore-check` bypasses this check

### Verification

```
python -m pytest cli/test_bootstrap.py -k "no_gitignore" -v --tb=short
```

---

## Task T-027-06: Integration with host-link flow

**Story**: [R8] Wire check into host_link() before symlink/junction
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-05

### Description

Wire `_check_host_gitignore()` into the `host_link()` function so it
runs BEFORE the symlink/junction creation. The check:
1. Loads the manifest.
2. Verifies `.gitignore` exists.
3. Runs static parse + live `git check-ignore`.
4. Acts on conflicts per `--gitignore-mode`.
5. If check passes (or mode = skip/warn), proceed to symlink/junction.

Existing happy-path tests must stay green.

### Acceptance Criteria

- [ ] Check runs before symlink/junction creation
- [ ] Existing `host-link` happy-path tests pass unchanged
- [ ] New conflict scenarios properly handled per mode
- [ ] Non-git host refusal (Sprint 5 behavior) unchanged

### Verification

```
python -m pytest cli/test_bootstrap.py -k "host_link" -v --tb=short
```

---

## Task T-027-07: Update HOST-INTEGRATION.md

**Story**: [R12] Documentation for new check, flags, modes
**Type**: [P] parallelizable
**Execution**: [AFK] autonomous
**Size**: S
**Files**: docs/HOST-INTEGRATION.md
**Files Blocked**: cli/bootstrap.py, cli/fleet.py, cli/dedup.py
**Depends on**: T-027-06

### Description

Update `docs/HOST-INTEGRATION.md` to document:
- The `.gitignore` conflict-detection layer.
- `--gitignore-mode` flag and its four modes.
- `--no-gitignore-check` opt-out.
- How to remediate detected conflicts.
- The manifest file and its contents.

### Acceptance Criteria

- [ ] New section documents gitignore check
- [ ] All four modes described
- [ ] Remediation steps included
- [ ] Manifest file referenced

### Verification

```
grep -l "gitignore-mode" docs/HOST-INTEGRATION.md
```

---

## Task T-027-08: Cross-platform tests (Windows junction + Linux symlink)

**Story**: [R9] Cross-platform coverage
**Type**: [P] parallelizable
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/test_bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-06

### Description

Add cross-platform test coverage for the gitignore check:
- Windows: mocked junction path (or real junction via SDD-028).
- Linux: real symlink path.
- Both platforms: verify gitignore check runs before link creation.

### Acceptance Criteria

- [ ] Windows path tested (mocked junction or skip-marked on non-Windows)
- [ ] Linux path tested (real symlink)
- [ ] Both paths verify gitignore check precedes link creation

### Verification

```
python -m pytest cli/test_bootstrap.py -k "cross_platform or junction or symlink" -v --tb=short
```

---

## Task T-027-09: Full test suite + schema_lint regression check

**Story**: [R10, R11] No regression
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: (none -- verification only)
**Files Blocked**: (none)
**Depends on**: T-027-08

### Description

Run the full test suite and `schema_lint` to confirm no regressions.
Test count must be >= 213 baseline. All existing tests pass. All new
gitignore-related tests pass.

### Acceptance Criteria

- [ ] `pytest` exits 0 with >= 213 tests passed
- [ ] `schema_lint` exits 0
- [ ] No warnings or deprecations introduced

### Verification

```
python -m pytest spec-driven-development/cli/ -v --tb=short
python spec-driven-development/cli/schema_lint.py
```

---

## Task T-027-10: SDD-028 -- Real Windows junction integration test

**Story**: BACKLOG SDD-028 (P2 housekeeping, <3-file, pulled into Sprint 6)
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/test_bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-09

### Description

Replace the mocked `mklink` test with one that actually creates and
traverses a Windows junction (NTFS junction point) in `test_bootstrap.py`.
On non-Windows platforms, the test is skip-marked with a clear message.

This is a <3-file bug fix pulled into Sprint 6. No spec required.

### Acceptance Criteria

- [ ] Test creates a real junction on Windows using `os.path` or `subprocess`
- [ ] Test traverses the junction and verifies content accessibility
- [ ] Test skip-marked on non-Windows with `@pytest.mark.skipif`
- [ ] Existing mocked tests not removed (kept as fallback)

### Verification

```
python -m pytest cli/test_bootstrap.py -k "junction" -v --tb=short
```

---

## Task T-027-11: SDD-029 -- Stale-symlink vs real-directory conflict distinction

**Story**: BACKLOG SDD-029 (P2 housekeeping, <3-file, pulled into Sprint 6)
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/bootstrap.py, cli/test_bootstrap.py
**Files Blocked**: cli/fleet.py, cli/dedup.py, constitution/principles.md
**Depends on**: T-027-10

### Description

When `host-link` encounters a conflict at the target path, distinguish
between:
- **Broken/stale symlink**: target is a symlink that points to a
  non-existent path. Remediation: "Remove stale link: `rm <path>`"
- **Populated directory**: target is a real directory with content.
  Remediation: "Back up and remove: `mv <path> <path>.bak`"

Currently both cases produce the same generic error. Add separate error
classes and remediation hints.

This is a <3-file bug fix pulled into Sprint 6. No spec required.

### Acceptance Criteria

- [ ] Broken symlink -> specific message: "stale symlink detected" + removal command
- [ ] Populated directory -> specific message: "directory exists" + backup command
- [ ] Each case has its own test with fixture
- [ ] Error messages include actionable remediation

### Verification

```
python -m pytest cli/test_bootstrap.py -k "stale or conflict_type" -v --tb=short
```

---

## Dependency Graph

```
T-027-01 -> T-027-02 -> T-027-03 -> T-027-04 -> T-027-05 -> T-027-06 -> T-027-07 [P]
                                                                        -> T-027-08 [P]
                                                              T-027-08 -> T-027-09
                                                              T-027-07 -> T-027-09
                                                              T-027-09 -> T-027-10 -> T-027-11
```

## Batch Plan

- **Batch 1** (F-08): T-027-01 (manifest, quick)
- **Batch 2** (F-08): T-027-02, T-027-03, T-027-04, T-027-05 (sequential, build parser + modes)
- **CHECKPOINT**: Run test suite after Batch 2
- **Batch 3** (F-08): T-027-06 (integration)
- **Batch 4** (F-08, parallel): T-027-07 + T-027-08 (docs + cross-platform tests)
- **Batch 5** (F-08): T-027-09 (regression check)
- **Batch 6** (F-08): T-027-10, T-027-11 (SDD-028 + SDD-029 pull-ins, sequential)
