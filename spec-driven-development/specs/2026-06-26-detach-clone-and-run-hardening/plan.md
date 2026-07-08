---
id: SDD-20260626DETACHHARDENING-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-detach-clone-and-run-hardening
---

# PLAN: SDD-045 -- Detach + clone-and-run hardening

- Feature ID: SDD-045
- Spec: [`spec.md`](spec.md) | CLARIFY: [`clarify.md`](clarify.md) | Validation: [`validation.md`](validation.md)
- Audit source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md)
- Implementation slot: **F-36** (this PLAN is authored in F-35, design-only)

---

## Approach

SDD-045 is a clone-and-run hardening epic with five independent-ish items. The implementation (F-36) is a sequence of stdlib-only CLI additions plus one owner-gated docs edit. Order matters only where items depend on each other (doctor wires in origin_lint and the governance check; setup depends on the fresh-DB init). All new code is stdlib-only (Article V): `argparse`, `sqlite3`, `pathlib`, `json`, `sys`, `os`, `subprocess` (for venv/test invocation), `re`.

Sequence:

1. **FR-1 (A-1) ledger init first.** Change `bootstrap.py:initialize_ledger()` to create the DB by executing `ledger/schema.sql` instead of `Path.touch()`. This is the foundation both setup (FR-2) and the fresh-clone story depend on.
2. **FR-1 (A-1) detach + ignore.** `git rm --cached spec-driven-development/ledger/fleet.db`; add the db globs to `.gitignore`. Add a tracked-`fleet.db` guard. **Owner-visible**: surface the stop-tracking + `.gitignore` diff before the F-36 commit.
3. **FR-4 (A-6) origin_lint.** Author `cli/origin_lint.py` standalone so doctor can call it.
4. **FR-5 (B-3) governance check.** Author the article-range/version coherence check; propose the owner-gated RULES.md two-line fix.
5. **FR-3 (A-5) doctor.** Wire ledger-untracked + schema_lint + governance + origin_lint + tests into one report.
6. **FR-2 (A-4) setup + make.** Compose the above into the one-command path; add `make setup`; shrink the README quickstart.

## Item-by-item implementation notes

### A-1 -- detach personal ledger (FR-1)

- **Attach point:** `bootstrap.py:initialize_ledger()` (currently ~lines 306-309, body is `ledger.touch()`). Replace with: open a `sqlite3` connection to a fresh `fleet.db` path and `executescript(schema_sql_text)` read from `spec-driven-development/ledger/schema.sql`; if `fleet.db` already exists and is non-empty, leave it (idempotent). `schema.sql` is CONFIRMED present.
- **Detach mechanism:** `git rm --cached spec-driven-development/ledger/fleet.db` (forward-only stop-tracking; local file preserved). NOT BFG/filter-repo.
- **`.gitignore` additions:** `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, `*.db-shm`.
- **Guard:** add a check (in `schema_lint.py` or `origin_lint.py`, called by doctor) that runs `git ls-files` for `*.db` under `ledger/` and FAILS if `fleet.db` is tracked. Prefer placing the tracked-file guard where doctor already aggregates checks to avoid bloating the locked-footprint `schema_lint.py`; if added to `schema_lint.py`, it must not touch Article X locked functions.

### A-4 -- one setup command (FR-2)

- **Attach point:** new `setup` subcommand registered in `bootstrap.py:main(argv)` (alongside greenfield/brownfield/host-link). Reuse the existing argparse subparser skeleton.
- **Steps (idempotent):** (1) check `sys.version_info >= (3, 12)`; (2) create `.venv` via `python -m venv` if `.venv` absent; (3) `initialize_ledger()` (fresh DB from schema); (4) install commit-msg hook (reuse existing hook-install logic if present in `cli/hooks/`); (5) prompt/write owner config (reuse `bootstrap.py` placeholder/owner-config writer); (6) run `schema_lint` + `pytest`; (7) print green ready message. Each step checks "already done?" before acting so re-runs are safe.
- **`make setup`:** a one-line Makefile target invoking `python spec-driven-development/cli/bootstrap.py setup`.
- **README:** reduce quickstart to clone -> `make setup` -> talk-to-EM.

### A-5 -- doctor / health check (FR-3)

- **Attach point:** new `doctor` subcommand in `bootstrap.py:main(argv)`.
- **Checks (each returns pass/fail + reason):** ledger reachable AND untracked; `schema_lint` exit 0; constitution semver coherence + B-3 article-range match (calls the FR-5 check); origin tokens absent (calls `origin_lint`); tests pass. Aggregate to a one-screen report; `return 1` (non-zero) if any fail.
- **CI parity:** doctor is the single source of truth for "what CI runs"; a future CI job just calls `bootstrap.py doctor`.

### A-6 -- origin-token + identity lint (FR-4)

- **New module:** `cli/origin_lint.py`, stdlib-only, `main(argv)` shape per CLI-PATTERN.md, `sys.exit(main())`.
- **Denylist:** a small config (literal default list in-module + optional JSON override) of personal names, origin project names, `engine.py`, hardcoded host path patterns. Scan `.github/**` + `constitution/**` text files.
- **Escape:** a line/block containing `<!-- example: ... -->` is exempt (so intentionally-illustrative origin references pass).
- **Wire:** doctor calls it; it also stands alone for CI.

### B-3 -- governance consistency (FR-5)

- **New check:** assert the article range cited in RULES.md (`Articles I-XII`) equals the article count parsed from `principles.md`, and that `version`/`last_amended` are coherent across the six `CONSTITUTION_FILES` + RULES.md. Reuse `bootstrap.py:CONSTITUTION_FILES` tuple.
- **RULES.md fix (owner-gated):** change "Articles I-X" -> "Articles I-XII" at line 18 (`constitution/principles.md (Articles I-X, ...)`) and line 202 (`If the change affects an Article (I-X) in principles.md`); optionally bump RULES.md `version` 1.1.0 -> 1.2.0 and `last_amended`. RULES.md is `amendable_by: human-only` -> obtain recorded owner approval before applying.

## Sequencing / dependencies

- FR-1 init (step 1) -> FR-2 setup (step 6).
- FR-4 origin_lint (step 3) -> FR-3 doctor (step 5).
- FR-5 governance check (step 4) -> FR-3 doctor (step 5).
- FR-1 detach (step 2) is owner-visible; FR-5 RULES.md edit is owner-gated -- both gated at the F-36 commit.

## Constraints honored

- Stdlib-only (Article V): no new dependency.
- Article X locked render functions untouched; `TestS1FootprintLockGuard` golden SHA stays PASS.
- No `constitution/**` edit (B-3 edits `docs/RULES.md` only).
- A-1 is forward-only stop-tracking; NO history rewrite.
- Test baseline 481 passed / 2 skipped only grows (new tests added), never shrinks.

## Risks

- **R-a:** Adding the tracked-`fleet.db` guard to `schema_lint.py` could perturb the locked footprint test. Mitigation: prefer placing it in `origin_lint.py`/doctor; if in `schema_lint.py`, keep it outside the locked functions and re-run `TestS1FootprintLockGuard`.
- **R-b:** `make setup` running the full pytest suite may be slow. Mitigation: setup prints progress; doctor offers a `--fast` future option (out of scope now).
- **R-c:** origin_lint false positives on legitimate doc text. Mitigation: the `<!-- example: ... -->` escape + a tunable denylist; scope limited to `.github/**` + `constitution/**`.
