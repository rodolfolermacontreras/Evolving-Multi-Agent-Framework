---
id: SDD-20260626DETACHHARDENING-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-detach-clone-and-run-hardening
---

# VALIDATION: SDD-045 -- Detach + clone-and-run hardening

- Feature ID: SDD-045
- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Audit source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md)
- Checked off in: **F-36**

---

## Lock Statement

This contract is LOCKED at F-35. F-36 may CHECK items with evidence; it may NOT add, remove, or weaken REQUIRED items. Any delta must be recorded as a numbered DE-xx entry with rationale and must SHARPEN, never loosen, an item. Per DA-Evidence Discipline, every REQUIRED data claim (e.g., "fresh DB has 0 dispatch rows", "git ls-files no longer lists fleet.db") MUST be proved by a real command run against the real repo with the output captured -- not predicted by a harness.

## Required Items (Strict)

> Evidence backfill -- F-54b / SDD-052 item 052C (owner-approved 2026-07-08). All 17 REQUIRED items below were validated at the **Sprint 14 close (commit `ecd13b3`)**, whose close record in `exec/sprint-progress.md` states "SDD-045 17/17 REQUIRED ... covering per-item A-1/A-4/A-5/A-6/B-3 ... All real-run evidence on disk (DA-Evidence Discipline)". The granular per-R captured command output lives in the F-36 implementation block of `exec/sprint-progress.md`. This corrective pass ticks the boxes to match that authoritative close record; it CHECKS with captured evidence only -- no REQUIRED item is added, removed, or weakened (Lock Statement honored).

### A-1 -- detach personal ledger

- [x] **R-1 (not tracked).** `git ls-files | Select-String fleet.db` returns NOTHING after `git rm --cached`. Evidence: captured command output. (AC-1, FR-1)
- [x] **R-2 (.gitignore excludes db).** `.gitignore` contains `spec-driven-development/ledger/fleet.db`, `*.db`, `*.db-wal`, `*.db-shm`. Evidence: file diff. (AC-1, FR-1)
- [x] **R-3 (fresh DB from schema, 0 rows).** After `bootstrap.py setup` on a clean checkout, `fleet.db` exists, its schema matches `schema.sql`, and `SELECT COUNT(*)` on the dispatch table = 0. Evidence: real `sqlite3` query output, NOT a predicted value. `initialize_ledger()` reads `schema.sql` (not empty `touch()`). (AC-2, AC-3, FR-1)
- [x] **R-4 (tracked-db guard fails).** With `fleet.db` deliberately re-added to the index, the guard (schema_lint or origin_lint via doctor) exits non-zero. Evidence: captured non-zero exit. (AC-4, FR-1)

### A-4 -- one setup command

- [x] **R-5 (one command end-to-end).** A single `make setup` / `bootstrap.py setup` on a fresh clone yields lint-clean + tests-passing + fresh-ledger + personalized. Evidence: captured run transcript ending in the green ready message. (AC-5, FR-2)
- [x] **R-6 (idempotent).** A second `setup` run succeeds, corrupts/duplicates nothing, prints the ready message again. Evidence: captured second-run transcript. (AC-6, FR-2)
- [x] **R-7 (README quickstart).** README quickstart is reduced to clone -> setup -> talk-to-EM. Evidence: README diff. (AC-7, FR-2)

### A-5 -- doctor / health check

- [x] **R-8 (non-zero on failure).** `bootstrap.py doctor` exits non-zero when any check fails, naming the failed check + reason; exits zero when all pass. Evidence: captured both a green run (exit 0) and a deliberately-broken run (exit non-zero). (AC-8, FR-3)
- [x] **R-9 (doctor == CI checks).** The check set doctor runs equals the set CI runs (CI invokes `bootstrap.py doctor`). Evidence: doctor source + CI config (or documented intent) listing identical checks. (AC-9, FR-3)

### A-6 -- origin-token + identity lint

- [x] **R-10 (leak fails).** Adding a denylisted token (e.g., a personal author name) to a `.github/` or `constitution/` file makes `origin_lint` exit non-zero; doctor surfaces it. Evidence: captured failing run. (AC-10, FR-4)
- [x] **R-11 (example escape passes).** The same token inside a labeled `<!-- example: ... -->` block does NOT fail the lint. Evidence: captured passing run. (AC-11, FR-4)

### B-3 -- governance consistency

- [x] **R-12 (RULES.md fixed).** RULES.md says "Articles I-XII" at both former drift sites (lines 18 and 202); no "Articles I-X" remains anywhere in RULES.md. Evidence: file diff + `Select-String "Articles I-X" RULES.md` returns nothing. (AC-12, FR-5)
- [x] **R-13 (check enforces).** Adding a thirteenth article to `principles.md` (in a scratch copy) without updating RULES.md makes the governance-consistency check exit non-zero. Evidence: captured failing run. (AC-13, FR-5)
- [x] **R-14 (owner approval recorded).** The owner-gated RULES.md content edit (`amendable_by: human-only`) is applied only after recorded owner approval. Evidence: owner-approval note in the F-36 progress block. (AC-14, FR-5)

### Cross-cutting

- [x] **R-15 (stdlib-only).** All new F-36 modules import only the standard library (Article V). Evidence: import audit / grep showing no third-party imports. (AC-15)
- [x] **R-16 (schema-lint clean).** `python spec-driven-development/cli/schema_lint.py` -> exit 0 with all SDD-045 artifacts + F-36 code present. Evidence: captured exit 0. (AC-16)
- [x] **R-17 (no regression / locked fns intact).** Full pytest >= 481 passed / 2 skipped (F-36 ADDS tests, never fewer); `TestS1FootprintLockGuard` PASS (Article X locked functions byte-identical); no third-party dependency; no `constitution/**` edit. Evidence: captured pytest summary + footprint-guard PASS. (AC-17)

## Optional Items

- [ ] **O-1.** `doctor --fast` mode (skip full pytest, run lint + governance + origin only). Nice-to-have; out of scope now.
- [ ] **O-2.** A presence test asserting `.gitignore` contains the db globs (additive; must not weaken R-2).

## Specific Test Coverage Required

- New unit tests for: `initialize_ledger()` schema-init (proves R-3), `setup` happy path + idempotency (proves R-5, R-6), `doctor` green + red exit codes (proves R-8), `origin_lint` leak + escape (proves R-10, R-11), governance-consistency check pass + fail (proves R-13), tracked-`fleet.db` guard (proves R-4).
- Full `spec-driven-development/` pytest suite must stay >= 481 passed / 2 skipped AFTER F-36 adds the above (count grows; never shrinks).
- `TestS1FootprintLockGuard` golden SHA-256 must remain PASS (proves no Article X locked-function edit).

## Manual Checks

- [ ] **M-1.** Reviewer confirms FR-1 used `git rm --cached` (stop-tracking), NOT a history rewrite, and that local `fleet.db` files were preserved.
- [ ] **M-2.** Owner reviews and approves the A-1 stop-tracking + `.gitignore` diff before the F-36 commit (owner-visible).
- [ ] **M-3.** Owner reviews and approves the B-3 RULES.md content edit before it is applied (owner-gated; `amendable_by: human-only`).
- [ ] **M-4.** Owner pre-push approval recorded before any push of the F-36 implementation.

## Definition of Done

SDD-045 is DONE when R-1..R-17 are checked with REAL-run evidence, M-1..M-4 are confirmed (including the two owner approvals for A-1 and B-3), the full suite stays >= 481 passed / 2 skipped with the footprint guard PASS, schema-lint is exit 0, and no third-party dependency or constitution edit was introduced. Optional O-1/O-2 do not block.
