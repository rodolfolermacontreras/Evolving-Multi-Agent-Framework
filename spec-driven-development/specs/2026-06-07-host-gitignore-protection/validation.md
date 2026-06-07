---
id: SDD-20260607GITIGN-validation
type: validation
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# Validation Contract: Host `.gitignore` Protection (SDD-027)

- Spec ID: SDD-027
- Status: SKELETON -- contract NOT locked. Locks at /tasks.
- Rule (when locked): zero unchecked REQUIRED items before implementation is
  considered complete.

> **DO NOT IMPLEMENT until this contract is locked.** All REQUIRED items
> below are TODO placeholders pending CLARIFY answers. Each placeholder
> names the CLARIFY question(s) it traces to.

---

## Required Items (TODO -- locked at /tasks)

- [ ] R1. TODO -- Article X fit per CLARIFY Q1. If the answer is
  "amendment needed", an ADR + amendment ship in the same sprint; if
  "fits as-is", the spec proceeds without constitutional change.
- [ ] R2. TODO -- detection strategy per CLARIFY Q2 (static parse, live
  git check, or both). Test: detector correctly identifies conflicts in
  each representative `.gitignore` variant.
- [ ] R3. TODO -- action-on-conflict policy per CLARIFY Q3 is honored.
  Test: each mode (strict / prompt / warn / skip, or the chosen subset)
  produces the agreed behavior on fixture conflicts.
- [ ] R4. TODO -- opt-in vs opt-out default per CLARIFY Q4. Test:
  default `host-link` invocation runs (or skips) the check per the
  chosen default; the opt flag inverts it.
- [ ] R5. TODO -- no-host-`.gitignore` behavior per CLARIFY Q5. Test:
  fixture host with no `.gitignore` produces the agreed outcome
  (refuse / create / proceed-with-warning).
- [ ] R6. TODO -- framework path lists live in the form chosen at
  CLARIFY Q6 (Python constant / JSON manifest / parsed markdown). Test:
  manifest is loadable, schema-valid, and matches the actual framework
  file layout.
- [ ] R7. TODO -- non-git-host behavior per CLARIFY Q7. Test: fixture
  with no `.git/` produces the agreed message.
- [ ] R8. TODO -- existing `host-link` happy-path stays green. Test:
  Sprint 5 baseline tests (test_bootstrap.py host-link cases) all pass
  unchanged.
- [ ] R9. TODO -- cross-platform: tests cover both Windows (junction)
  and Linux/macOS (symlink) paths.
- [ ] R10. TODO -- full existing test suite passes (no regression).
  Sprint 5 baseline: 213 tests.
- [ ] R11. TODO -- schema_lint stays clean.
- [ ] R12. TODO -- `docs/HOST-INTEGRATION.md` documents the new check,
  flags, modes, and remediation steps.

## Optional / Best-Effort Items (TODO)

- [ ] O1. TODO -- dashboard surface flags hosts whose last `host-link`
  install reported a conflict (if ledger captures install events).
- [ ] O2. TODO -- machine-readable conflict report (`--format json`)
  mirroring the SDD-FDC-001 `count` convention.

## Notes

- Contract is SKELETON. Required-item count and exact wording will change
  at /spec finalization once CLARIFY answers land.
- Q1 (Article X fit) may add an R0 row for "ADR + amendment shipped" if
  the spec concludes amendment is required.
- Lock the contract at /tasks; do not loosen REQUIRED items after lock
  without an explicit decision recorded here.
