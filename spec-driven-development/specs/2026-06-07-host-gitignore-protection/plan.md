---
id: SDD-20260607GITIGN-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Implementation Plan: Host `.gitignore` Protection (SDD-027)

- Feature: SDD-027
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Plan Author: Principal Software Developer
- Date: 2026-06-07

---

## Implementation Approach

Extend `cli/bootstrap.py` `host-link` subcommand with a
`_check_host_gitignore()` function that runs BEFORE the symlink/junction
install. The check uses dual detection:

1. **Static parse**: read the host's `.gitignore` file and compare rules
   against the framework-defined manifest.
2. **Live `git check-ignore`**: subprocess call for the authoritative
   answer (catches global excludes, parent-dir `.gitignore` files,
   `core.excludesFile`).

A JSON manifest at `cli/host_gitignore_manifest.json` declares two lists:
- **MUST-BE-IGNORED**: framework paths the host must NEVER commit.
- **MUST-BE-TRACKED**: framework paths the host MUST keep visible to git.

Mode flag `--gitignore-mode {strict|prompt|warn|skip}` (default: `prompt`)
controls behavior on conflict. `--no-gitignore-check` opts out entirely.
Host with no `.gitignore` is refused with recommended content. Non-git
host continues to be refused (existing Sprint 5 behavior).

### Key Design Decisions

1. **Dual detection**: static parse for readable diff display + live
   `git check-ignore` for authoritative answer. If they disagree, the
   live check wins.

2. **Mode flag default = `prompt`**: interactive for first-real-host
   dispatch; `strict` for CI pipelines.

3. **Opt-out by default**: check runs unless `--no-gitignore-check` is
   passed. Safety-first approach.

4. **No constitutional amendment**: Article X misreading corrected at
   CLARIFY. Ships as normal spec.

### Pull-In Decision: SDD-028 + SDD-029

SDD-028 (real Windows junction test) and SDD-029 (stale-symlink vs
real-directory distinction) are PULLED INTO Sprint 6 as <3-file
housekeeping tasks, sequenced AFTER SDD-027 in the same
`cli/bootstrap.py` code path. They do not need full specs.

---

## File Scope

| File | Change Type | Owner |
|------|------------|-------|
| `cli/bootstrap.py` | Extend: `_check_host_gitignore()` + mode flag + opt-out | SDD-027 + SDD-028 + SDD-029 |
| `cli/test_bootstrap.py` | Extend: gitignore check tests + cross-platform + SDD-028/029 | SDD-027 + SDD-028 + SDD-029 |
| `cli/host_gitignore_manifest.json` | New: MUST-BE-IGNORED + MUST-BE-TRACKED | SDD-027 |
| `docs/HOST-INTEGRATION.md` | Extend: document new check, flags, modes | SDD-027 |

### File Collision Analysis

- `cli/bootstrap.py`: SDD-027 + SDD-028 + SDD-029 (sequential within track).
  NOT touched by SDD-019 or SDD-020.
- `cli/fleet.py`: NOT touched by SDD-027 (SDD-019 track).
- `cli/dedup.py`: NOT touched by SDD-027 (SDD-020 track).

---

## Dependencies

| Dependency | Status | Impact |
|-----------|--------|--------|
| Sprint 5 host-link (30482d5) | Shipped | Upstream for SDD-027 extension |
| SDD-019 | Independent | Different file track |
| SDD-020 | Independent | Different file track |

---

## Implementation Order

1. **T-027-01**: Create `host_gitignore_manifest.json`.
2. **T-027-02**: Implement static `.gitignore` parser.
3. **T-027-03**: Implement live `git check-ignore` detection.
4. **T-027-04**: Implement `--gitignore-mode` flag + `--no-gitignore-check`.
5. **T-027-05**: Implement missing-`.gitignore` refusal.
6. **T-027-06**: Integration with `host-link` flow.
7. **T-027-07**: Update `HOST-INTEGRATION.md`.
8. **T-027-08**: Cross-platform tests.
9. **T-027-09**: Full test suite + `schema_lint` regression check.
10. **T-027-10**: SDD-028 -- Real Windows junction integration test (pull-in).
11. **T-027-11**: SDD-029 -- Stale-symlink vs real-directory distinction (pull-in).

Tasks T-027-01 through T-027-06 are sequential (build up the gitignore
check layer). T-027-07 (docs) can parallelize after T-027-06. T-027-08
parallels T-027-07. T-027-10 and T-027-11 are sequential after T-027-09.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `git check-ignore` unavailable in test env | MEDIUM | Mock subprocess | Mock in unit tests; real in integration |
| Manifest paths drift from framework layout | LOW | False positives/negatives | Manifest validated against actual tree in test |
| Cross-platform edge cases (Windows junctions) | MEDIUM | Test coverage gap | SDD-028 pull-in adds real junction test |
| Stale symlink detection failure | LOW | Confusing error message | SDD-029 pull-in adds specific error class |

---

## Test Strategy

- **Unit**: parse `.gitignore`, classify rules, detect conflicts, generate
  remediation diff, manifest loading and validation.
- **Integration**: end-to-end `host-link` against `tmp_path` "fake host"
  directories with synthetic `.gitignore` variants (clean, missing rules,
  over-aggressive, missing file, no `.git/`).
- **Regression**: existing 213-test suite stays green; existing
  `test_bootstrap.py` host-link tests stay green.
- **Cross-platform**: test on Windows (junction path, real in SDD-028) and
  Linux (symlink path) since `host-link` is cross-platform.

---

## Dispatch Plan (F-08)

Track B: SDD-027 (all tasks touch `cli/bootstrap.py`) then SDD-028 +
SDD-029 (same file, sequential after SDD-027).

Track B runs in parallel with Track A (SDD-020 + SDD-019) because they
touch different files.
