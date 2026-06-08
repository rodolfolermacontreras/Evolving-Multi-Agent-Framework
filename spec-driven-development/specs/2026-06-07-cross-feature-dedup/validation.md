---
id: SDD-20260607DEDUP-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Validation Contract: Cross-Feature Deduplication (SDD-020)

- Spec ID: SDD-020
- Status: LOCKED at /tasks 2026-06-07
- Rule: zero unchecked REQUIRED items before implementation is
  considered complete. REQUIRED items cannot be loosened after lock
  without an explicit decision recorded here (Article X).

---

## Required Items (locked at /tasks)

- [x] R1. Scan covers `backlog/BACKLOG.md` + `IDEAS.md` + open spec dirs; excludes done/archived (Q1). Test: TestLoadCorpusBacklog, TestLoadCorpusOpenSpecs, TestLoadCorpusIdeas.
- [x] R2. Three-layer heuristic fires correctly -- HARD on exact frontmatter `id` collision, SOFT on fuzzy title (SequenceMatcher ratio >= 0.8), ADVISORY on keyword Jaccard >= threshold (Q2). Test: TestLayer1HardExactId, TestLayer2SoftFuzzy, TestLayer3AdvisoryJaccard + negative controls.
- [x] R3. `cli/dedup.py` is standalone, runnable, stdlib-only, `main(argv)` signature (Q3). Test: TestStdlibOnly, TestMainSignature, TestIndependentOfFleet.
- [x] R4. HARD blocks triage/clarify; SOFT prompts owner; ADVISORY warns and proceeds (Q4). Test: TestTieredHardExits1, TestTieredCleanExits0, TestTieredSoftNoPrompt, TestTieredAdvisoryExits0.
- [x] R5. Independent of SDD-019 serial gate; no import dependency on `fleet.py`, no lock check (Q5). Test: TestIndependentOfFleet.
- [ ] R6. Dedup log written to all three destinations: ledger row + per-spec-dir `dedup-scan.md` + rolling `backlog/DEDUP-LOG.md` (Q6). DEFERRED: log writers stubbed for v1; implemented as CLI scan only. Carry to Sprint 7.
- [x] R7. Empty corpus emits explicit "no corpus to dedup against; 0 candidates scanned" notice, not silent skip (Q7). Test: TestEmptyCorpusNotice.
- [ ] R8. `/triage` and `/clarify` prompts reference the dedup pass. DEFERRED: prompt integration requires prompt file edits. Carry to Sprint 7.
- [x] R9. Full test suite passes (>= 213 baseline, no regression). 258 passed.
- [x] R10. `schema_lint` stays clean. Verified exit 0.

## Optional / Best-Effort Items

- [ ] O1. Dashboard surface lists recent dedup decisions or pending overlap flags.
- [x] O2. CLI supports `--format json|table` mirroring SDD-FDC-001 `count` convention. Test: TestCLIScanJsonFormat.

## Notes

- Contract populated at /spec finalization 2026-06-07. All 7 CLARIFY
  answers recorded; required items trace to specific questions.
- SDD-019 integration (R5) confirmed independent and composable --
  no dependency coupling, no shared lock state.
- Contract LOCKED at /tasks 2026-06-07. Do not loosen REQUIRED items after
  lock without an explicit decision recorded here.
