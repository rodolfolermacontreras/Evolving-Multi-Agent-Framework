---
id: SDD-20260607GITIGN-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Feature Spec: Host `.gitignore` Protection for `bootstrap.py host-link` (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect + Owner
- Status: APPROVED
- Priority: P1 (carry-over from Sprint 5 Architect audit, 2026-06-07)
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-027

No constitutional amendment required. Article X is "Validation Is a
Pre-Implementation Contract" and does not govern host integration. The
kickoff prompt's "Article X amendment CANDIDATE" framing was based on a
misreading. Ships as normal spec + ADR documenting the host-gitignore
contract design.

---

## Problem Statement

The `bootstrap.py host-link` subcommand (shipped Sprint 5, commit
`30482d5`) installs a `.github/` symlink from the framework into a host
repository so the host can consume framework agents, skills, and prompts
without copying. The installer does NOT currently verify the host's
`.gitignore`, which creates two concrete failure modes blocking the first
real-host dispatch:

1. **Framework-internal files leak into host commits.** If the host's
   `.gitignore` does not exclude the framework-installed `.github/` path
   (or specific generated artifacts), a routine `git add .` in the host
   stages files that belong to the framework, not to the host product.
   The host commits framework state; the framework's source of truth
   forks silently across the symlink.
2. **Framework-required-tracked files get accidentally ignored.** The
   inverse: an overly aggressive host `.gitignore` (e.g., a sweeping
   `**/agents/**` rule) ends up ignoring framework files the host MUST
   keep tracked for the symlink contract to work. The host's `git status`
   looks clean but the framework's expected file set is invisible.

Sprint 5 Architect audit (2026-06-07) flagged this as the gate blocking
the first real-host dispatch. The audit explicitly noted: "the first real
host install requires this protection layer or we will spend the first
dispatch un-corrupting a host repo."

## Proposed Solution

Add a **`.gitignore` conflict-detection layer** to `bootstrap.py host-link`
that runs before the symlink is installed. The layer:

1. Reads the host's `.gitignore` (if any).
2. Compares its ignore rules against two framework-defined sets:
   - **MUST-BE-IGNORED**: framework paths the host must NEVER commit.
   - **MUST-BE-TRACKED**: framework paths the host MUST keep visible to git.
3. Reports conflicts.
4. Acts on conflicts per a policy decided at CLARIFY (auto-fix, prompt,
   or refuse install).

The shape (detection strategy depth, exact path lists, action policy,
opt-in vs opt-out) has been resolved via CLARIFY (2026-06-07):

- **Dual detection**: static parse of host `.gitignore` for readable diff
  display + live `git check-ignore` for the authoritative answer (catches
  global excludes, parent-dir `.gitignore` files, `core.excludesFile`).
- **Mode flag**: `--gitignore-mode {strict|prompt|warn|skip}` with default
  = `prompt`. Interactive for first-real-host dispatch; `strict` for CI.
- **Opt-out default**: check runs by default; `--no-gitignore-check` to
  disable.
- **No-gitignore host**: refuse the install with recommended content.
- **JSON manifest**: MUST-BE-IGNORED and MUST-BE-TRACKED lists in
  `cli/host_gitignore_manifest.json`.
- **Non-git host**: refuse (existing Sprint 5 behavior, no change).
- **No constitutional amendment**: Article X misreading corrected.

## Acceptance Criteria

- **AC-1**: No constitutional amendment; spec ships without `constitution/` edits. (Q1)
- **AC-2**: Detection uses static parse of host `.gitignore` + live `git check-ignore` for authoritative answer. (Q2) Test: fixture conflicts detected by both methods.
- **AC-3**: `--gitignore-mode {strict|prompt|warn|skip}` flag with default = `prompt`. Each mode produces correct behavior on fixture conflicts. (Q3)
- **AC-4**: Check runs by default; `--no-gitignore-check` disables it. (Q4)
- **AC-5**: Host with no `.gitignore` -> refuse with clear message listing minimal recommended content. (Q5)
- **AC-6**: MUST-BE-IGNORED and MUST-BE-TRACKED lists in `cli/host_gitignore_manifest.json`; manifest loads, schema-valid, matches framework layout. (Q6)
- **AC-7**: Non-git host -> refuse (existing Sprint 5 behavior, no change). (Q7)
- **AC-8**: Existing `host-link` happy-path tests stay green.
- **AC-9**: `docs/HOST-INTEGRATION.md` documents new check, flags, modes, and remediation steps.
- **AC-10**: Full test suite passes (>= 213 baseline, no regression).

## Affected Modules

- `cli/bootstrap.py` -- extend `host-link` subcommand with gitignore check
- `cli/test_bootstrap.py` -- new tests for gitignore check, modes, edge cases
- `cli/host_gitignore_manifest.json` -- new JSON manifest (MUST-BE-IGNORED + MUST-BE-TRACKED)
- `docs/HOST-INTEGRATION.md` -- document new check, flags, modes, remediation
- `docs/ADR/ADR-NNN-host-gitignore-protection.md` -- new (drafted in F-07)

## Data Model Changes

New file: `cli/host_gitignore_manifest.json` -- JSON manifest declaring
MUST-BE-IGNORED and MUST-BE-TRACKED path lists. Schema:
```json
{
  "must_be_ignored": ["pattern1", "pattern2"],
  "must_be_tracked": ["pattern3", "pattern4"]
}
```
No database or ledger schema changes. Bootstrap reads the manifest at
runtime; no new state files.

## API Changes

- `bootstrap.py host-link` gains `--gitignore-mode {strict|prompt|warn|skip}` (default: `prompt`).
- `bootstrap.py host-link` gains `--no-gitignore-check` opt-out flag.
- Existing `host-link` flags and behavior unchanged when gitignore check passes.

## Test Strategy

**OUTLINE -- lock at /tasks.**

- Unit: parse `.gitignore`, classify rules, detect conflicts, generate
  remediation diff, manifest loading and validation.
- Integration: end-to-end `host-link` against `tmp_path` "fake host"
  directories with synthetic `.gitignore` variants (clean, missing
  rules, over-aggressive, missing file, no `.git/`).
- Regression: existing 213-test suite stays green; existing
  `test_bootstrap.py` host-link tests stay green.
- Cross-platform: test on Windows (junction path) and Linux (symlink
  path) since `host-link` is cross-platform.

## Validation Contract

The binding validation contract lives in the sibling file `validation.md`.
Required items have been drafted at /spec finalization (2026-06-07) and
will be locked at /tasks (F-07). Implementation MUST NOT begin until the
validation contract is locked and all REQUIRED items are explicitly listed.

## Traceability Matrix

| Requirement | Acceptance Criterion | Module |
|-------------|---------------------|--------|
| R1: No constitutional amendment | AC-1 | (none -- no constitution/ edits) |
| R2: Dual detection | AC-2 | cli/bootstrap.py |
| R3: Mode flag | AC-3 | cli/bootstrap.py |
| R4: Opt-out default | AC-4 | cli/bootstrap.py |
| R5: No-gitignore refuse | AC-5 | cli/bootstrap.py |
| R6: JSON manifest | AC-6 | cli/host_gitignore_manifest.json |
| R7: Non-git refuse | AC-7 | cli/bootstrap.py |
| R8: Happy-path unchanged | AC-8 | cli/test_bootstrap.py |
| R9: Docs updated | AC-9 | docs/HOST-INTEGRATION.md |
| R10: No regression | AC-10 | cli/test_bootstrap.py |

## Open Questions

CLARIFY closed 2026-06-07. All 7 questions answered in `clarify.md`.
No remaining open questions.

## Out of Scope

- `.gitattributes` enforcement (`.gitignore` only for v1).
- Per-file LFS or large-file rules.
- Auto-PR-on-host to fix the host's `.gitignore` (manual or in-place only for v1).
- Retroactive cleanup of already-committed framework files in the host (out of scope for install-time check; covered by follow-up if needed).
- Multi-host / fleet-wide gitignore audit (per-host invocation only).
- Constitutional amendment (Article X misreading corrected; no amendment needed).

## Cross-Feature Notes

- **SDD-016 / SDD-017** (host-link subcommand + dev-env-manager,
  shipped Sprint 5) are the upstream. This feature extends them; the
  CLI signature for `host-link` is additive only.
- **SDD-028 / SDD-029** (P2 housekeeping, also Sprint 6 if capacity)
  touch the same `host_link()` code path; sequencing decision is the
  PM's at /plan time.
- **SDD-019 / SDD-020** are unrelated at the feature level but share the
  Sprint 6 capacity budget.
