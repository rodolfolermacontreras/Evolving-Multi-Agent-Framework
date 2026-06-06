# Validation Contract: Filesystem Data Contracts (Sprint 4)

- Spec ID: SDD-FDC-001
- Status: draft (written at /spec, locked at /tasks)
- Rule: zero unchecked REQUIRED items before implementation is considered complete.

---

## Required Items

- [ ] R1. Schema-lint reports a finding (file + missing field) and exits non-zero for
  any in-scope artifact missing a required frontmatter field. (AC-1)
- [ ] R2. Schema-lint exits zero with no frontmatter findings when all in-scope
  artifacts are valid. (AC-2)
- [ ] R3. `state_builder.py count` (default) prints JSON matching
  `{ "by_status": {...}, "by_type": {...}, "total": int }`; `total` equals the sum of
  `by_status` and the sum of `by_type`. (AC-3)
- [ ] R4. `state_builder.py count --format table` prints a human-readable table and
  exits zero. (AC-4)
- [ ] R5. LOCK: `render_html()` and data-layer functions T-001..T-004 are
  byte-identical to commit `257b081` (re-anchored 2026-06-06 -- see clarification-log Q5), enforced by an automated guard test
  (stdlib `inspect.getsource` + `hashlib.sha256` vs golden hashes from `257b081`). (AC-5)
- [ ] R6. All in-scope `specs/**` and `sprints/**` markdown carry valid frontmatter
  (`id`, `type`, `status`, `owner`, `updated`). (Backfill complete)
- [ ] R7. Full existing test suite passes (no regression). (AC-7)

## Optional / Best-Effort Items

- [ ] O1. Opt-in `commit-msg` hook rejects a non-conforming message and allows a
  conforming one; uninstalled state is unaffected. (AC-6)
- [ ] O2. `COMMIT-CONVENTION.md` documents the format with examples.

## Notes

- R5 is the hard constraint from the original request (S1 footprint lock; anchor re-anchored to 257b081 on 2026-06-06 -- see clarification-log Q5).
- O1/O2 are optional because Sprint 4 ships the convention as documentation + opt-in
  only; mandatory enforcement is deferred (D3).
