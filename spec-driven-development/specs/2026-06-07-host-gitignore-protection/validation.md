---
id: SDD-20260607GITIGN-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Validation Contract: Host `.gitignore` Protection (SDD-027)

- Spec ID: SDD-027
- Status: LOCKED at /tasks 2026-06-07
- Rule: zero unchecked REQUIRED items before implementation is
  considered complete. REQUIRED items cannot be loosened after lock
  without an explicit decision recorded here (Article X).

---

## Required Items (locked at /tasks)

- [ ] R1. No constitutional amendment shipped; no `constitution/` edits (Q1). Test: `git diff constitution/` is empty after implementation.
- [ ] R2. Detection uses both static parse of host `.gitignore` and live `git check-ignore` (Q2). Test: fixture with `.gitignore` + global excludes; both methods report correctly.
- [ ] R3. `--gitignore-mode strict|prompt|warn|skip` each produce correct behavior on fixture conflicts (Q3). Test: one fixture per mode.
- [ ] R4. Check runs by default; `--no-gitignore-check` disables (Q4). Test: default invocation runs check; flag invocation skips it.
- [ ] R5. Host with no `.gitignore` -> refuse with recommended content (Q5). Test: fixture host with no `.gitignore`.
- [ ] R6. MUST-BE-IGNORED + MUST-BE-TRACKED in `cli/host_gitignore_manifest.json`, loadable, schema-valid (Q6). Test: load + validate + verify matches framework layout.
- [ ] R7. Non-git host -> refuse (Q7). Test: fixture with no `.git/` directory.
- [ ] R8. Existing `host-link` happy-path tests pass unchanged. Test: run Sprint 5 `test_bootstrap.py` host-link tests.
- [ ] R9. Cross-platform: Windows junction + Linux symlink paths tested (mocked where needed).
- [ ] R10. Full test suite passes (>= 213 baseline, no regression).
- [ ] R11. `schema_lint` stays clean.
- [ ] R12. `docs/HOST-INTEGRATION.md` documents check, flags, modes, remediation.

## Optional / Best-Effort Items

- [ ] O1. Dashboard surface flags hosts whose last `host-link` install reported a conflict.
- [ ] O2. Machine-readable conflict report (`--format json`) mirroring SDD-FDC-001 `count` convention.

## Notes

- Contract populated at /spec finalization 2026-06-07. All 7 CLARIFY
  answers recorded; required items trace to specific questions.
- No constitutional amendment needed (Q1). Article X misreading corrected.
  No R0 row for "ADR + amendment shipped" -- not applicable.
- Contract LOCKED at /tasks 2026-06-07. Do not loosen REQUIRED items after
  lock without an explicit decision recorded here.
