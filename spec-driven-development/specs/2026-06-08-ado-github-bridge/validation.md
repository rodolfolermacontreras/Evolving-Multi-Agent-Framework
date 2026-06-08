---
id: SDD-20260608ADOGHBRIDGE-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Validation Contract: ADO / GitHub Issues Sync Bridge (SDD-022)

- Spec ID: SDD-022
- Spec reference: `./spec.md`
- Status: **LOCKED at F-12 pass 2 / TASKS 2026-06-08**
- Rule: zero unchecked REQUIRED items before SDD-022 implementation is considered complete. REQUIRED items cannot be loosened after lock without an explicit decision recorded here (Article X).

---

## Required Items (locked for F-14)

- [ ] V-1. Task parser reads `tasks.md` as the authoritative local source and extracts task ID, title, status, description, file scope, acceptance criteria references, and verification references. Covers AC-1 / R1 / R7.
- [ ] V-2. Dry-run GitHub sync renders deterministic issue payloads, performs no network write, and exits 0 for a valid spec directory. Covers AC-2 / R2 / R3.
- [ ] V-3. Apply-mode GitHub sync requires `GITHUB_TOKEN` or `GH_TOKEN`, constructs GitHub REST requests through stdlib `urllib.*`, and fails before writes when tokens are missing. Covers AC-3 / R2 / R6 / R8.
- [ ] V-4. Per-spec-dir `issue-map.json` is written as deterministic JSON with schema version, spec ID, provider, repository, task ID, remote ID, URL, `last_synced_at`, `last_seen_remote_status`, and sync fingerprint. Covers AC-4 / R5.
- [ ] V-5. Re-running sync against an existing mapping is idempotent: unchanged tasks do not duplicate issues, and changed generated body sections update only the generated region. Covers AC-5 / R5 / R7.
- [ ] V-6. Remote/local status conflicts produce a non-mutating conflict report with task ID, local status, remote status, remote URL, conflict type, and recommended owner action; command exits non-zero and does not mutate `tasks.md`. Covers AC-6 / R1 / R4.
- [ ] V-7. No implicit sync triggers exist: no commit hook, no dashboard-triggered write, no webhook listener, and no background daemon. Covers AC-7 / R3.
- [ ] V-8. No credentials or token fragments are committed, stored in `issue-map.json`, written to conflict reports, or printed in command output. Covers AC-3 / R6.
- [ ] V-9. Provider boundary includes GitHub live provider and ADO-compatible provider/test double shape without requiring live ADO execution. Covers AC-9 / R2.
- [ ] V-10. Generated issue fields are limited to title, generated body, labels, status, source links, and task ID; no assignee, milestone, or dependency graph fields are emitted. Covers AC-8 / R7.
- [ ] V-11. `.github/prompts/taskstoissues.prompt.md` exists and documents explicit `/taskstoissues` usage, dry-run default, apply-mode requirements, conflict handling, and no implicit writes. Covers AC-7 / R3 / R11.
- [ ] V-12. Import scan/test proves no third-party tracker or HTTP libraries are imported: no `requests`, `httpx`, `PyGithub`, `github`, `azure-devops`, or ADO SDK. Covers AC-10 / R8.
- [ ] V-13. Path guard tests prove generated sync state is written only in framework-owned spec directories and never into host application files. Covers AC-11 / R9.
- [ ] V-14. CLI follows `docs/CLI-PATTERN.md`: argparse, `main(argv)`, pathlib, deterministic exit codes, and stderr for expected failures. Covers R10.
- [ ] V-15. `python spec-driven-development/cli/schema_lint.py` exits 0 after F-14 implementation. Covers AC-12 / R12.
- [ ] V-16. Full pytest suite exits 0 after F-14 implementation, with test count at or above the Sprint 8 baseline plus new SDD-022 tests. Covers AC-12 / R12.

---

## Optional / Best-Effort Items

- [ ] O-1. Optional live GitHub smoke test using a safe owner-provided token and disposable issue target; skip cleanly when no token/repo is provided.
- [ ] O-2. Human-readable Markdown sync report summarizing created, updated, unchanged, and conflicted tasks.
- [ ] O-3. ADO dry-run fixture demonstrates equivalent payload shape for Work Item creation without live ADO network calls.

---

## Lock Notes

- CLARIFY closed 2026-06-08 after owner approved defaults for Q-A through Q-H; Q-I was already resolved by dispatch constraint.
- This contract intentionally makes GitHub live round-trip REQUIRED and ADO live execution OPTIONAL/fast-follow.
- No Article V amendment, ADR, or constitution edit is required for this validation contract.---
id: SDD-20260608ADOGHBRIDGE-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---

# Validation Contract: ADO / GitHub Issues Sync Bridge (SDD-022)

- Spec ID: SDD-022
- Spec reference: [`./spec.md`](./spec.md)
- Status: **DRAFT -- NOT LOCKED**
- Lock Point: F-12 pass 2, after Q-A through Q-H are answered and
  `spec.md` is finalized.

---

> **F-12 pass 1 boundary**: this file is intentionally a scaffold.
> REQUIRED items are not enumerated in pass 1 because the owner has not
> resolved the authority, provider, cadence, conflict, mapping, auth,
> and field-scope decisions in [`clarify.md`](./clarify.md). Locking a
> validation contract now would invent the owner's decisions.

---

## Required Items

**TBD pending owner answers.** Expected item areas, not commitments:

- R-area for Q-A authority model and mutation boundary.
- R-area for Q-B v1 provider scope (GitHub live vs ADO live).
- R-area for Q-C/Q-E explicit sync cadence and trigger.
- R-area for Q-D conflict report semantics.
- R-area for Q-F task-to-issue identity mapping.
- R-area for Q-G auth model and no-secret logging.
- R-area for Q-H synced field set and generated body shape.
- R-area for Q-I stdlib-only `urllib.*` implementation and import scan.
- R-area for no host-project writes.
- R-area for `.github/prompts/taskstoissues.prompt.md`, if confirmed.
- R-area for schema_lint clean exit.
- R-area for full test suite after F-14 code changes.

## Optional / Best-Effort Items

**TBD pending owner answers.** Candidate optional areas:

- ADO dry-run provider fixture if live ADO is not v1-required.
- Human-readable sync report in Markdown.
- Optional live GitHub smoke test, only if owner supplies a safe token
  and confirms external write validation.

## Notes

- This contract must be locked before F-14 implementation starts.
- No REQUIRED item may be silently deferred from Sprint 8 close.
- If the owner changes Q-I and requests a third-party dependency, F-12
  must stop and route a Level-2 dependency brief before this contract
  can be locked.
