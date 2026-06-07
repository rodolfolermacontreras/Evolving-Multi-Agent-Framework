---
id: SDD-20260607GITIGN-spec
type: spec
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Feature Spec: Host `.gitignore` Protection for `bootstrap.py host-link` (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect (scaffold) / TBD owner at /spec finalization
- Status: SKELETON -- CLARIFY pending (do NOT proceed to /plan until clarify.md answered)
- Priority: P1 (carry-over from Sprint 5 Architect audit, 2026-06-07)
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-027

> **Article X amendment CANDIDATE per owner direction 2026-06-07 (via EM).**
> Handle as a normal spec first; only escalate to an Article X amendment
> IF the spec proves the article must change. Friction Analysis is NOT
> required up front. The CLARIFY round must explicitly decide whether the
> host-`.gitignore` rule fits within Article X as written or requires a
> constitutional amendment; only if the latter does the work branch into
> amendment ceremony.

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
opt-in vs opt-out) is **deliberately unresolved** at scaffold time. See
`clarify.md`. The Proposed Solution will be expanded once CLARIFY closes.

Likely components, subject to CLARIFY:

- A `_check_host_gitignore(host_repo: Path) -> GitignoreReport` function
  in `cli/bootstrap.py` (or an extracted helper module).
- Framework-side declaration of the MUST-BE-IGNORED and MUST-BE-TRACKED
  lists (a manifest file, an in-code constant, or a hybrid).
- Integration point: invoked from `host_link()` before the actual
  symlink/junction call; behavior on conflict per CLARIFY Q3.
- Documentation update in `docs/HOST-INTEGRATION.md`.

## Acceptance Criteria

> **TODO -- BLOCKED ON CLARIFY.** Each criterion MUST trace to a CLARIFY
> answer (`See clarify.md Q-NN`). Draft outline:
>
> 1. Given a host with no `.gitignore`, when `host-link` runs, then the
>    behavior matches CLARIFY Q5 (e.g., create a minimal `.gitignore`
>    with framework-required rules, OR refuse, OR proceed with warning).
> 2. Given a host whose `.gitignore` is missing a MUST-BE-IGNORED rule,
>    when `host-link` runs, then the conflict is reported and the
>    action policy from CLARIFY Q3 is applied.
> 3. Given a host whose `.gitignore` ignores a MUST-BE-TRACKED path,
>    when `host-link` runs, then the conflict is reported and resolved
>    per CLARIFY Q3.
> 4. Given a clean host `.gitignore`, when `host-link` runs, then no
>    conflict is reported and the symlink install proceeds as today.
> 5. ... (additional ACs once CLARIFY closes)

## Affected Modules

> **TENTATIVE -- subject to CLARIFY answers.**
>
> - Files (likely):
>   - `spec-driven-development/cli/bootstrap.py` (extend `host-link` subcommand)
>   - `spec-driven-development/cli/test_bootstrap.py` (new tests)
>   - `spec-driven-development/docs/HOST-INTEGRATION.md` (doc update)
>   - Possibly: `spec-driven-development/cli/common/host_gitignore.py` (extracted helper, if size warrants)
>   - Possibly: `spec-driven-development/cli/host_gitignore_manifest.json` (manifest, if CLARIFY Q2 chooses file form)
> - Directories (read-only):
>   - `spec-driven-development/.github/` (source of MUST-BE-TRACKED list)

## Data Model Changes

> **TBD via CLARIFY.** Possible options:
>
> - Hard-coded Python constants for MUST-BE-IGNORED and MUST-BE-TRACKED.
> - JSON manifest under `cli/` versioned with the framework.
> - Markdown spec under `docs/` parsed at runtime (least preferred).

## API Changes

> **TBD via CLARIFY.** Likely additive flags on `host-link`:
>
> - `--gitignore-mode {strict|prompt|warn|skip}` (per CLARIFY Q3).
> - `--no-gitignore-check` opt-out (per CLARIFY Q4).

## Test Strategy

> **OUTLINE only.** Lock at /tasks.
>
> - Unit: parse `.gitignore`, classify rules, detect conflicts, generate
>   remediation diff.
> - Integration: end-to-end `host-link` against `tmp_path` "fake host"
>   directories with synthetic `.gitignore` variants (clean, missing
>   rules, over-aggressive, missing file).
> - Regression: existing 213-test suite stays green; existing
>   `test_bootstrap.py` host-link tests stay green.
> - Cross-platform: test on Windows (junction path) and Linux (symlink
>   path) since `host-link` is cross-platform.

## Validation Contract

The binding validation contract lives in the sibling file `validation.md`.
It is a SKELETON at scaffold time; required items will be drafted at /spec
finalization and locked at /tasks. Implementation MUST NOT begin until the
validation contract is locked and all REQUIRED items are explicitly listed.

## Traceability Matrix

> **TODO -- populate at /spec finalization once CLARIFY closes.**
>
> | Requirement | Acceptance Test | Module |
> |-------------|-----------------|--------|
> | TBD | TBD | TBD |

## Open Questions

See `clarify.md`. CLARIFY questions are the gate, not casual open notes.

## Out of Scope

> **TODO -- BLOCKED ON CLARIFY.** Tentative candidates:
>
> - `.gitattributes` enforcement (`.gitignore` only for v1).
> - Per-file LFS or large-file rules.
> - Auto-PR-on-host to fix the host's `.gitignore` (manual or in-place
>   only for v1).
> - Retroactive cleanup of already-committed framework files in the host
>   (out of scope for the install-time check; covered by a follow-up if
>   needed).

## Cross-Feature Notes

- **SDD-016 / SDD-017** (host-link subcommand + dev-env-manager,
  shipped Sprint 5) are the upstream. This feature extends them; the
  CLI signature for `host-link` is additive only.
- **SDD-028 / SDD-029** (P2 housekeeping, also Sprint 6 if capacity)
  touch the same `host_link()` code path; sequencing decision is the
  PM's at /plan time.
- **SDD-019 / SDD-020** are unrelated at the feature level but share the
  Sprint 6 capacity budget.
