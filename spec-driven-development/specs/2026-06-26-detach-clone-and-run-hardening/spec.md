---
id: SDD-20260626DETACHHARDENING-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-detach-clone-and-run-hardening
depends_on: [SDD-039]
---

# SPEC: SDD-045 -- Detach + clone-and-run hardening

- Feature ID: SDD-045 (epic; per-item IDs A-1, A-4, A-5, A-6, B-3)
- Sprint: PI-7 / Sprint 1 (Sprint 14), design slot F-35; implementation F-36
- Status: **active** (design locked; implementation pending in F-36)
- CLARIFY: [`clarify.md`](clarify.md)
- Audit source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) (items A-1, A-4, A-5, A-6, B-3)
- Validation contract: [`validation.md`](validation.md)
- Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)

---

## Problem Statement

A teammate who clones the EMF repository today cannot get to a clean, runnable, personal-state-free state in one step, and the repo leaks the maintainer's operational and identity state into shared history:

- **A-1:** The personal fleet ledger `spec-driven-development/ledger/fleet.db` (a binary SQLite file containing this owner's dispatch rows) is committed and tracked. A fresh clone inherits the owner's dispatch history; teammates then commit their own rows back, mixing personal operational state into shared history. `.gitignore` does not exclude it.
- **A-4:** There is no single setup command for a teammate who cloned EMF itself. `bootstrap.py` only personalizes *host* projects (greenfield/brownfield/host-link); it offers nothing to make EMF itself runnable.
- **A-5:** There is no health/`doctor` command and no CI, so a clone can silently run on stale, broken, or personalized state with no way to detect it.
- **A-6:** No lint prevents origin tokens -- personal names, the origin project name, `engine.py`, or hardcoded host paths -- from leaking into portable `.github/**` or `constitution/**` files.
- **B-3:** Governance docs have drifted: `principles.md` (v1.4.0) declares twelve binding articles (I-XII), but `RULES.md` (v1.1.0) still says "Articles I-X" in two places (lines 18 and 202).

SDD-045 specifies the fixes so F-36 can implement them with no design ambiguity. F-35 produces design artifacts only.

## Goal

Make a fresh clone of EMF reach a clean, runnable, personalized, governance-consistent state via one command, with automated guards that keep it that way:

- The personal ledger is no longer tracked; a fresh clone has no `fleet.db` until setup creates a correct, empty one (A-1).
- `make setup` / `bootstrap.py setup` takes a fresh clone to lint-clean + test-passing + fresh-ledger + personalized in one idempotent step (A-4).
- `bootstrap.py doctor` reports repo health on one screen and exits non-zero on any failure, matching the checks CI runs (A-5).
- An origin-token lint fails when personal/origin/host tokens leak into portable files (A-6).
- A governance-consistency check keeps RULES.md and principles.md in lockstep, and the current RULES.md drift is fixed (B-3).

## Non-Goals

- Implementing any of the above (all implementation is F-36).
- Editing `.gitignore`, running `git rm`, or initializing any ledger in F-35.
- Any history rewrite (BFG / filter-repo) -- A-1 is forward-only stop-tracking, not history purge.
- Any `constitution/**` edit. (B-3 fixes `docs/RULES.md`, not the constitution; the constitution is unchanged.)
- Any Article X locked-render-function edit.
- A new third-party dependency (Article V: stdlib-only).
- Audit items outside this epic: B-1/B-2/B-4 (SDD-046), A-2/A-3/D-1/D-3 (SDD-047), C-1/C-2/C-3/D-2 (SDD-048).

## Functional Requirements (per-item, stable IDs)

- **FR-1 (A-1, detach personal ledger).** F-36 MUST stop tracking `spec-driven-development/ledger/fleet.db` via `git rm --cached` (NOT a history rewrite), MUST add `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, and `*.db-shm` to `.gitignore`, and MUST make setup initialize a fresh `fleet.db` from `spec-driven-development/ledger/schema.sql` (correct schema, zero dispatch rows) -- replacing the current empty-file `touch()` behavior in `initialize_ledger()`. A guard MUST FAIL if `fleet.db` is tracked.
- **FR-2 (A-4, one setup command).** F-36 MUST add a `setup` subcommand to `bootstrap.py` and a thin `make setup` wrapper that: verify Python >= 3.12; create `.venv` if absent; init a fresh `fleet.db` from `schema.sql`; install the commit-msg hook; prompt/write owner config; run `schema_lint` and the test suite; print a green ready message. Setup MUST be idempotent on re-run.
- **FR-3 (A-5, doctor/health check).** F-36 MUST add a `doctor` subcommand to `bootstrap.py` that checks: (a) ledger reachable AND untracked; (b) `schema_lint` clean; (c) constitution semver coherence and the B-3 article-range match; (d) no origin tokens (FR-4); (e) tests pass. It MUST emit a one-screen green/red report and exit non-zero on any failure with a specific reason. The doctor checks MUST be the same checks CI runs.
- **FR-4 (A-6, origin-token + identity lint).** F-36 MUST add a stdlib-only `cli/origin_lint.py` that FAILS when a configurable denylist token (personal names, origin project names, `engine.py`, hardcoded host paths) appears in any file under `.github/**` or `constitution/**`, with an `<!-- example: ... -->` escape for intentionally-illustrative blocks. It MUST be wired into `doctor`.
- **FR-5 (B-3, governance consistency).** F-36 MUST add a governance-consistency check asserting RULES.md's stated article range equals the article count in `principles.md` and that version/`last_amended` are coherent across the six constitution files + RULES.md; AND MUST fix the current RULES.md drift (change "Articles I-X" to "Articles I-XII" at lines 18 and 202). The RULES.md content edit is **owner-gated** (`amendable_by: human-only`) and MUST obtain owner approval at F-36 before it is applied; the automated check itself is not owner-gated.

## Acceptance Criteria

- **AC-1 (A-1: not tracked).** After F-36, `git ls-files` does NOT list `spec-driven-development/ledger/fleet.db`; `.gitignore` excludes `fleet.db`, `*.db`, `*.db-wal`, `*.db-shm`. (FR-1)
- **AC-2 (A-1: fresh clone clean).** A fresh clone has no `fleet.db` until setup runs. (FR-1)
- **AC-3 (A-1: setup creates correct empty DB).** After `bootstrap.py setup`, `fleet.db` exists, has zero dispatch rows, and matches `schema.sql` (init reads `schema.sql`, not an empty `touch()`). (FR-1, FR-2)
- **AC-4 (A-1: guard).** `schema_lint` (or `origin_lint`, surfaced by doctor) FAILS if `fleet.db` is tracked. (FR-1)
- **AC-5 (A-4: one command).** A single `make setup` / `bootstrap.py setup` invocation leaves a fresh clone lint-clean, test-passing, fresh-ledger, and personalized. (FR-2)
- **AC-6 (A-4: idempotent).** Re-running setup does not corrupt or duplicate state and prints the green ready message again. (FR-2)
- **AC-7 (A-4: README quickstart).** The README quickstart reduces to clone -> setup -> talk-to-EM. (FR-2)
- **AC-8 (A-5: doctor exit code).** `bootstrap.py doctor` exits non-zero on any failed check, naming the failed check and reason; exits zero when all checks pass. (FR-3)
- **AC-9 (A-5: doctor == CI).** The set of checks doctor runs equals the set CI runs. (FR-3)
- **AC-10 (A-6: leak fails).** Adding a denylisted token (e.g., a personal author name) to a `.github/` or `constitution/` file makes `origin_lint` FAIL; doctor surfaces it. (FR-4)
- **AC-11 (A-6: example escape passes).** A token inside a labeled `<!-- example: ... -->` block does NOT trigger a failure. (FR-4)
- **AC-12 (B-3: RULES.md fixed).** RULES.md references "Articles I-XII" at both former drift sites (lines 18 and 202); no "Articles I-X" remains. (FR-5)
- **AC-13 (B-3: check enforces).** Adding a thirteenth article to `principles.md` without updating RULES.md makes the governance-consistency check FAIL. (FR-5)
- **AC-14 (B-3: owner-gated edit recorded).** The RULES.md content edit is applied only after recorded owner approval (it is `amendable_by: human-only`). (FR-5)
- **AC-15 (stdlib-only).** All new F-36 code (`setup`, `doctor`, `origin_lint.py`, governance check) imports only the Python standard library (Article V). (FR-2..FR-5)
- **AC-16 (schema-lint clean).** All SDD-045 design artifacts (this spec dir) pass `python spec-driven-development/cli/schema_lint.py` with exit 0; F-36's new code/tests keep it at exit 0. (all)
- **AC-17 (no regression / no locked-fn edit).** F-36 does not reduce the test count below the 481 passed / 2 skipped baseline (it ADDS tests), introduces no third-party dependency, no schema-of-record change to Article X locked functions, and no `constitution/**` edit. (all)

## Affected Modules

| Module / file | Change | When |
|---------------|--------|------|
| `.gitignore` | Add `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, `*.db-shm` | F-36 |
| `spec-driven-development/ledger/fleet.db` | `git rm --cached` (stop tracking; local file preserved) | F-36 (owner-visible) |
| `spec-driven-development/cli/bootstrap.py` | NEW `setup` + `doctor` subcommands; `initialize_ledger()` inits from `schema.sql` instead of empty `touch()` | F-36 |
| `Makefile` (root) | NEW `setup` target wrapping `bootstrap.py setup` | F-36 |
| `spec-driven-development/cli/origin_lint.py` | NEW stdlib-only origin-token lint + denylist config | F-36 |
| `spec-driven-development/cli/schema_lint.py` | NEW guard: FAIL if `fleet.db` tracked (or implement in origin_lint, surfaced by doctor) | F-36 |
| `spec-driven-development/cli/test_*.py` | NEW tests for setup, doctor, origin_lint, governance check, fresh-DB init | F-36 |
| `spec-driven-development/docs/RULES.md` | Fix "Articles I-X" -> "Articles I-XII" at lines 18 + 202 (owner-gated, `amendable_by: human-only`) | F-36 (owner approval required) |
| `README.md` (root) | Quickstart reduced to clone -> setup -> talk-to-EM | F-36 |
| `spec-driven-development/specs/2026-06-26-detach-clone-and-run-hardening/*` | Design artifacts | F-35 (here) |

## Traceability

| Audit item | FR | ACs | Validation |
|------------|----|-----|------------|
| A-1 | FR-1 | AC-1..AC-4 | R-1..R-4 |
| A-4 | FR-2 | AC-3, AC-5..AC-7 | R-5..R-7 |
| A-5 | FR-3 | AC-8, AC-9 | R-8, R-9 |
| A-6 | FR-4 | AC-10, AC-11 | R-10, R-11 |
| B-3 | FR-5 | AC-12..AC-14 | R-12..R-14 |
| cross-cutting | FR-2..FR-5 | AC-15..AC-17 | R-15..R-17 |
