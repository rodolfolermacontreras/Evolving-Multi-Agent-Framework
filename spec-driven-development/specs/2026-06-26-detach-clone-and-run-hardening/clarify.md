---
id: SDD-20260626DETACHHARDENING-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-detach-clone-and-run-hardening
---

# CLARIFY: SDD-045 -- Detach + clone-and-run hardening

- Date: 2026-06-26
- Authors: Principal Product Manager + Principal Architect (jointly), at F-35
- Status: **DONE** -- Q-E, Q-F, Q-G answered; per-item stale-checks recorded; owner-gated flags surfaced
- Spec ID: SDD-045 (epic). Per-item stable IDs: A-1, A-4, A-5, A-6, B-3 (audit codes, carried verbatim from the hardening plan)
- Sprint: PI-7 / Sprint 1 (= overall Sprint 14), feature slot F-35 (CLARIFY + SPEC + PLAN + TASKS; IMPLEMENT is F-36)
- Decision source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) audit items A-1, A-4, A-5, A-6, B-3 + [`SPRINT-14-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-14-KICKOFF.prompt.md) section 3 (Q-E..Q-G)

---

## Ground Rules

- This file is the source of truth for SDD-045 design decisions.
- F-35 is design-only. **No implementation, no `.gitignore` edit, no `git rm`, no ledger init, no CLI code, no constitution edit, no commit, no push** is authorized by this file. Implementation is F-36.
- A-1 stops *tracking* the personal ledger via `git rm --cached`; it is NOT a history rewrite and does NOT delete anyone's local `fleet.db`.
- Article V (stdlib-only) binds all F-36 CLI work designed here: argparse, sqlite3, pathlib, json, sys, os only -- no third-party dependency.
- Article X locked render functions (`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`) stay byte-identical. SDD-045 touches none of them.

---

## Scope (epic decomposition)

SDD-045 bundles five audit items from EMF-HARDENING-PLAN.md into one "make a fresh clone runnable and personal-state-free" epic:

| Item | Title | Effort | Owner-gated? |
|------|-------|--------|--------------|
| A-1 | Stop committing the personal ledger (`fleet.db`) | S | Owner-VISIBLE (changes git tracking at F-36) |
| A-4 | One setup command (`bootstrap.py setup` + `make setup`) | M | No |
| A-5 | `doctor` / health check (`bootstrap.py doctor`) | M | No |
| A-6 | Origin-token + identity lint | S | No |
| B-3 | Governance consistency (RULES.md article range) | S | **YES** -- RULES.md is `amendable_by: human-only` |

Explicitly OUT of scope for Sprint 14 (other SDD epics): B-1, B-2, B-4 (SDD-046); A-2, A-3, D-1, D-3 (SDD-047); C-1, C-2, C-3, D-2 (SDD-048).

---

## Per-item stale-check (Evidence verified against the LIVE repo on 2026-06-26)

Per the kickoff stale-check rule, each audit "Evidence" line was re-verified before locking. Results stated explicitly:

### A-1 -- STALE-CHECK: CONFIRMED (evidence holds, with one sharpening)

- Audit said: `git ls-files` lists `spec-driven-development/ledger/fleet.db`; `.gitignore` does not exclude it; DB has author rows.
- LIVE verify: `git ls-files` **does** list `spec-driven-development/ledger/fleet.db` -> still tracked. `.gitignore` contains only `Thumbs.db` -> no db exclusion. **CONFIRMED.**
- SHARPENING found during verify: `spec-driven-development/ledger/schema.sql` **EXISTS**, so a fresh-DB init has a real source. AND `bootstrap.py:initialize_ledger()` (lines ~306-309) currently only `Path.touch()`es an empty file -- it does NOT initialize the schema from `schema.sql`. F-36's setup MUST init the ledger from `schema.sql` (real schema, zero dispatch rows), not merely touch an empty file. This sharpens A-1/A-4 and is recorded in the validation contract.

### A-4 -- STALE-CHECK: CONFIRMED

- Audit said: README quickstart exists; `bootstrap.py` personalizes new host projects but does nothing for a teammate who cloned EMF itself.
- LIVE verify: `bootstrap.py` exposes exactly three subcommands -- `greenfield`, `brownfield`, `host-link` (no `setup`). There is no `make setup` / Makefile target for cloning EMF itself. **CONFIRMED.**

### A-5 -- STALE-CHECK: CONFIRMED

- Audit said: no CI, no health command; the dashboard can show stale data.
- LIVE verify: `bootstrap.py` has no `doctor` subcommand; no health command exists anywhere in `cli/`. **CONFIRMED.**

### A-6 -- STALE-CHECK: CONFIRMED

- Audit said: no lint guards origin tokens (personal names, origin project names, host paths) leaking into `.github/` or `constitution/`.
- LIVE verify: `schema_lint.py` validates frontmatter only; it has no content denylist rule. No standalone `origin_lint.py` exists. **CONFIRMED.**

### B-3 -- STALE-CHECK: CONFIRMED (and drift is now slightly different from the audit snapshot)

- Audit said: `principles.md` (v1.3.0) declares "Twelve binding articles" (I-XII); `RULES.md` (v1.1.0) still says "Articles I-X."
- LIVE verify: `principles.md` is now **v1.4.0** (audit captured v1.3.0) but still declares **Twelve** articles -- enumerated I, II, III, IV, V, VI, VII, VIII, IX, X, XI, XII. `RULES.md` is still **v1.1.0** and still says "Articles I-X" -- in **two** places: line 18 (`constitution/principles.md (Articles I-X, semver'd, ADR to amend)`) and line 202 (`If the change affects an Article (I-X) in principles.md`). **CONFIRMED real drift.** The only delta from the audit snapshot is the principles.md version bump (1.3.0 -> 1.4.0); the count is unchanged, so the finding stands and is sharpened to "fix BOTH occurrences in RULES.md."
- OWNER-GATED finding: `RULES.md` frontmatter declares `amendable_by: human-only`. Therefore the B-3 text fix is an **owner-gated** edit at F-36 (Level requires human approval), even though RULES.md lives under `docs/`, not `constitution/`. This is recorded as an OWNER-ATTENTION item.

---

## Decision Summary (Q-E..Q-G)

| Q | Item(s) | Locked Decision | Level |
|---|---------|-----------------|-------|
| Q-E | A-1 | Detach `fleet.db` from tracking via `git rm --cached` (NOT history rewrite); add `fleet.db` + `*.db` + `*.db-wal` + `*.db-shm` to `.gitignore`; setup initializes a fresh DB from `ledger/schema.sql` (0 dispatch rows); schema_lint/doctor fails if `fleet.db` is tracked. | Level-1 (owner-visible at F-36) |
| Q-F | A-4, A-5 | Single entrypoint = `bootstrap.py setup` with a thin `make setup` wrapper; health command = `bootstrap.py doctor`. Both are new stdlib-only subcommands of the existing `bootstrap.py` (no new top-level CLI). Setup is idempotent. Doctor runs the same checks CI will run. | Level-1 |
| Q-G | A-6, B-3 | A-6 = a new `cli/origin_lint.py` (standalone, stdlib-only) with a configurable denylist + `<!-- example: ... -->` escape, wired into doctor. B-3 = a governance-consistency check (article-range + version coherence) plus the actual one-line RULES.md fix; the RULES.md edit is owner-gated and is the only SDD-045 change requiring human approval at F-36. | Level-1 (B-3 owner-gated) |

---

### Q-E: A-1 detach mechanism + fresh-DB init

**Context.** The personal ledger `fleet.db` (binary SQLite with this owner's dispatch rows) is committed. A teammate cloning EMF inherits the owner's dispatch history and then commits their own rows back -- mixing personal operational state into shared history.

**Options.**

- Option A (recommended): `git rm --cached spec-driven-development/ledger/fleet.db` (stop tracking, keep the local file), add the db globs to `.gitignore`, and make setup initialize a fresh DB from `ledger/schema.sql`. A schema_lint/doctor check fails if `fleet.db` is ever tracked again.
- Option B: Rewrite history to purge `fleet.db` from all past commits (BFG / filter-repo).
- Option C: Leave it tracked but document "don't commit your rows."

**PM + Architect recommendation:** Option A. Option B is a destructive, irreversible, all-collaborator-coordinated history rewrite -- disproportionate to the risk and explicitly out of scope for a hardening sprint; the personal rows already in history are low-sensitivity and a forward-only stop-tracking is the proportionate fix (Article VI). Option C does not actually solve the problem. **F-36 mechanism (designed, not executed here):** (1) `git rm --cached spec-driven-development/ledger/fleet.db`; (2) add `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, `*.db-shm` to `.gitignore`; (3) `bootstrap.py setup` initializes a fresh `fleet.db` from `ledger/schema.sql` (correct schema, 0 dispatch rows) -- replacing the current empty-file `touch()` behavior; (4) add a guard (in `schema_lint.py` or `origin_lint.py`, surfaced by doctor) that FAILS if `fleet.db` is tracked.

### Q-F: A-4 setup + A-5 doctor shape

**Context.** A teammate who clones EMF itself has no one-command path to a runnable, personalized, lint-clean repo, and no health command to confirm the repo is sound.

**Options.**

- Option A (recommended): Extend the existing `bootstrap.py` with two new subcommands -- `setup` and `doctor` -- plus a thin `make setup` wrapper. Stdlib-only.
- Option B: A separate new CLI tool (`cli/setup.py`, `cli/doctor.py`).
- Option C: A shell script.

**PM + Architect recommendation:** Option A. `bootstrap.py` already owns clone-time concerns and the CLI-PATTERN.md `main(argv)` shape; adding subcommands keeps one entrypoint and reuses the existing arg-parsing skeleton. A shell script would break the stdlib-Python, cross-platform, testable-`main(argv)` convention. **`bootstrap.py setup` (designed):** verify Python >= 3.12; create `.venv` if absent; init a fresh `fleet.db` from `schema.sql`; install the commit-msg hook; prompt/write owner config; run `schema_lint` + the test suite; print a green ready message. Idempotent on re-run. **`bootstrap.py doctor` (designed):** check (a) ledger reachable AND untracked, (b) `schema_lint` clean, (c) constitution semver coherence + B-3 article-range match, (d) no origin tokens (A-6), (e) tests pass -- emit a one-screen green/red report and exit non-zero on any failure with a specific reason. Doctor == the checks CI will run.

### Q-G: A-6 origin-token lint + B-3 governance check

**Context.** Nothing stops a personal name, the origin project name, `engine.py`, or a hardcoded host path from leaking into a portable `.github/` or `constitution/` file; and RULES.md has drifted out of sync with the article count in principles.md.

**Options (A-6).**

- Option A (recommended): A standalone `cli/origin_lint.py` with a configurable denylist (personal names, origin project names, `engine.py`, hardcoded host paths) scanning `.github/**` + `constitution/**`, with an `<!-- example: ... -->` escape for intentionally-illustrative blocks. Wired into `doctor`.
- Option B: A new rule inside `schema_lint.py`.

**Recommendation (A-6):** Option A -- keep `schema_lint.py` focused on frontmatter (it already has 1100+ lines and a locked footprint guard); origin-token scanning is a distinct concern that deserves its own testable module. The denylist is data (a small config), so a host project can tune it.

**Options (B-3).**

- Option A (recommended): Add a governance-consistency check (asserting RULES.md's stated article range equals the article count in principles.md, plus version/last_amended coherence across the six constitution files + RULES.md) AND make the actual one-line fix to RULES.md (I-X -> I-XII at lines 18 and 202).
- Option B: Only add the check; fix RULES.md later.

**Recommendation (B-3):** Option A, with the explicit caveat that the **RULES.md content edit is owner-gated** (`amendable_by: human-only`). F-36 proposes the exact two-line diff and the optional version bump and obtains owner approval before applying it; the automated check itself is not owner-gated and can land independently.

---

## OWNER-ATTENTION (surfaced now; actioned at F-36 with approval)

- **B-3 RULES.md edit is owner-gated.** `RULES.md` frontmatter is `amendable_by: human-only`. The (mechanical) fix -- change "Articles I-X" to "Articles I-XII" at lines 18 and 202, optionally bump `version` 1.1.0 -> 1.2.0 and `last_amended` -- requires explicit owner approval at F-36. No automated agent may apply it unattended.
- **A-1 is owner-visible.** F-36 runs `git rm --cached fleet.db` and edits `.gitignore`. This stops tracking a file that is currently in history. It is not destructive (local files preserved, no history rewrite) but the owner should see and approve the stop-tracking + `.gitignore` change before the F-36 commit.
- No other SDD-045 item requires human approval; A-4/A-5/A-6 are additive Level-1 CLI/code work.

## Carry-forward to SPEC

- Stable per-item IDs A-1, A-4, A-5, A-6, B-3 map 1:1 to FR-1..FR-5 in `spec.md`.
- The "fresh DB from schema.sql, not touch()" sharpening (A-1) is a locked REQUIRED item.
- The "fix BOTH RULES.md occurrences (lines 18 + 202)" sharpening (B-3) is a locked REQUIRED item.
- Owner-gated B-3 and owner-visible A-1 are recorded as manual/owner checks in `validation.md`.
