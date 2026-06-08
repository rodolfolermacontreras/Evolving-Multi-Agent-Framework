---
id: SDD-20260607DEDUP-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Implementation Plan: Cross-Feature Deduplication (SDD-020)

- Feature: SDD-020
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Plan Author: Principal Software Developer
- Date: 2026-06-07

---

## Implementation Approach

Create a new standalone `cli/dedup.py` module with `main(argv)` signature,
argparse, stdlib-only. The module implements a three-layer heuristic for
detecting duplicate or overlapping backlog items and spec dirs:

1. **Layer 1 (HARD)**: exact frontmatter `id` collision via `parse_frontmatter`
   (reused from `cli/schema_lint.py`).
2. **Layer 2 (SOFT)**: title fuzzy match via `difflib.SequenceMatcher` with
   ratio >= 0.8 threshold.
3. **Layer 3 (ADVISORY)**: keyword Jaccard on tokenized problem-statement text.

Each layer maps to a tiered action: HARD blocks, SOFT prompts the owner,
ADVISORY warns. Triple-destination logging: fleet ledger rows + per-spec-dir
`dedup-scan.md` + rolling `backlog/DEDUP-LOG.md`.

A new skill file at `.github/skills/workflow/cross-feature-dedup/SKILL.md`
wraps the CLI for agent invocation. `/triage` and `/clarify` prompts are
updated to reference the dedup pass.

### Key Design Decisions

1. **Standalone `cli/dedup.py`**: NOT a `fleet.py` subcommand. Avoids
   file-scope collision with SDD-019 (which extends `fleet.py`). Both
   features can be implemented in parallel.

2. **stdlib-only heuristics**: `difflib.SequenceMatcher` for fuzzy title
   match, set operations for Jaccard. No LLM, no external deps.

3. **`parse_frontmatter` reuse**: import from `cli/schema_lint.py` for
   exact-ID layer. Shared boundary per ADR-012.

4. **Exit codes**: 0 = clean, 1 = HARD overlap found, 2 = SOFT overlap
   found (prompt needed). Follows CLI-PATTERN.md convention.

---

## File Scope

| File | Change Type | Owner |
|------|------------|-------|
| `cli/dedup.py` | New: scanner, heuristics, CLI entry point | SDD-020 ONLY |
| `cli/test_dedup.py` | New: tests for all layers + tiers + edge cases | SDD-020 ONLY |
| `.github/skills/workflow/cross-feature-dedup/SKILL.md` | New: skill file | SDD-020 ONLY |
| `.github/prompts/triage.prompt.md` | Extend: hook dedup invocation | SDD-020 |
| `.github/prompts/clarify.prompt.md` | Extend: hook dedup invocation | SDD-020 |
| `backlog/DEDUP-LOG.md` | New: rolling dedup log template | SDD-020 |

### File Collision Analysis

- `cli/dedup.py`: New file. No collision with any other feature.
- `cli/fleet.py`: NOT touched by SDD-020 (SDD-019 owns fleet.py).
- `cli/bootstrap.py`: NOT touched by SDD-020 (SDD-027 track).
- `.github/prompts/triage.prompt.md` and `clarify.prompt.md`: minor hook
  additions; no conflict with other features.

---

## Dependencies

| Dependency | Status | Impact |
|-----------|--------|--------|
| SDD-FDC-001 (frontmatter contract) | LOCKED, shipped Sprint 4 | `parse_frontmatter` reuse for Layer 1 |
| SDD-019 | Independent | No coupling; composable (confirmed CLARIFY Q5) |

---

## Implementation Order

1. **T-020-01**: Dedup scanner (corpus loader) -- load and parse sources.
2. **T-020-02**: Three-layer match heuristic.
3. **T-020-03**: Tiered action handler (HARD/SOFT/ADVISORY).
4. **T-020-04**: CLI entry point with argparse.
5. **T-020-05**: Dedup log writers (ledger + per-spec-dir + rolling).
6. **T-020-06**: Cross-feature-dedup skill file.
7. **T-020-07**: Hook dedup into `/triage` and `/clarify` prompts.
8. **T-020-08**: Empty corpus handling.
9. **T-020-09**: Full test suite + `schema_lint` regression check.

Tasks T-020-01 through T-020-05 are sequential (all modify `cli/dedup.py`).
T-020-06 and T-020-07 can parallelize after T-020-05 completes.
T-020-08 is an edge-case addition to T-020-01.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Fuzzy threshold too aggressive (false positives) | MEDIUM | SOFT prompts overwhelm owner | Tune threshold in test; 0.8 is conservative |
| Keyword Jaccard too noisy on short texts | MEDIUM | ADVISORY floods | Minimum token count filter |
| `parse_frontmatter` API change | LOW | Import breaks | SDD-FDC-001 is locked; API is stable |
| File collision with SDD-019 | NONE | N/A | Confirmed: separate files |

---

## Test Strategy

- **Unit**: match heuristic per layer (exact ID, fuzzy title, keyword
  Jaccard), output format, no-overlap path, empty-corpus path, tiered
  action exit codes.
- **Integration**: end-to-end dedup invocation with fixture backlog +
  spec dirs; verify decision prompt + dedup-log write to all three
  destinations (ledger, per-spec-dir, rolling).
- **Regression**: existing 213-test suite stays green; `schema_lint` clean.

---

## Dispatch Plan (F-08)

SDD-020 ships FIRST in Track A (lower risk, no constitutional amendment).
All tasks are within `cli/dedup.py` (new file) so no collision with
any other feature. After SDD-020 is green, SDD-019 proceeds in the
same track.
