---
id: SDD-20260607DEDUP-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Feature Spec: Cross-Feature Deduplication at /triage and /clarify (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect + Owner
- Status: APPROVED
- Priority: P1
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-020

CLARIFY resolved 2026-06-07. SDD-020 is independent and composable with
SDD-019 (confirmed jointly at SDD-019 Q5 / SDD-020 Q5). SDD-020 ships
first (lower risk, no constitutional amendment).

---

## Problem Statement

At `/triage` and `/clarify`, duplicate or overlapping backlog items can
slip into `BACKLOG.md` without an explicit overlap scan. Concrete
failures observed:

1. **Verbatim duplicates.** Two triage rounds pulling from the same
   stakeholder transcript can produce two BACKLOG rows with near-identical
   titles and identical scope. There is no automated check.
2. **Semantic duplicates.** Two items with different titles but
   overlapping problem statements (e.g., one framed by symptom, one by
   root cause) can both reach SPEC before the overlap is noticed.
3. **Spec-dir overlap.** Two open spec dirs can claim overlapping
   problem statements or touch overlapping module surfaces with no
   pre-spec collision detection.

Today, dedup is implicit owner discipline at triage. The framework
provides no CLI, no skill, and no dashboard surface that flags overlap.
Sprint 5 Architect audit (2026-06-07) flagged this as the second-highest
source of wasted CLARIFY work after the SDD-019 serial gate gap.

## Proposed Solution

Introduce a **pre-spec overlap-detection pass** that runs at `/triage` and
`/clarify`, flags candidate duplicates against existing BACKLOG entries
and open spec dirs, and writes its finding to a dedup log that informs
the triage decision.

CLARIFY resolved all open questions (2026-06-07). The detector shape is:

- **Scan scope**: `backlog/BACKLOG.md` + `backlog/IDEAS.md` + open spec dirs
  (`specs/**/spec.md` where status != done/archived). Closed specs excluded.
- **Three-layer heuristic (stdlib-only, no LLM)**:
  - Layer 1: exact frontmatter `id` collision (HARD). Reuses `parse_frontmatter`
    from `cli/schema_lint.py`.
  - Layer 2: title fuzzy match via `difflib.SequenceMatcher` ratio >= 0.8 (SOFT).
  - Layer 3: keyword Jaccard on tokenized problem-statement text (ADVISORY).
- **Standalone `cli/dedup.py`**: new module with `main(argv)` signature,
  argparse, stdlib-only. NOT a `fleet.py` subcommand (avoids file-scope
  collision with SDD-019).
- **Tiered action**: HARD blocks, SOFT prompts owner, ADVISORY warns.
  Auto-merge never used in v1.
- **Triple-destination dedup log**: ledger rows + per-spec-dir
  `dedup-scan.md` + rolling `backlog/DEDUP-LOG.md`.
- **Empty corpus**: explicit "0 candidates scanned" notice, not silent skip.
- **Independent of SDD-019**: no dependency coupling; composable.

## Acceptance Criteria

- **AC-1**: Dedup scans `backlog/BACKLOG.md` + `backlog/IDEAS.md` + open spec dirs (`specs/**/spec.md` where status != done/archived); closed/archived specs excluded. (Q1)
- **AC-2**: Three-layer heuristic fires correctly: exact frontmatter `id` collision = HARD, title fuzzy match (SequenceMatcher ratio >= 0.8) = SOFT, keyword Jaccard overlap = ADVISORY. (Q2)
- **AC-3**: Standalone `cli/dedup.py` with `main(argv)` signature, argparse, stdlib-only. Independently runnable. (Q3)
- **AC-4**: HARD blocks triage/clarify from proceeding; SOFT prompts owner to decide (merge / keep-both / discard / rewrite); ADVISORY warns and proceeds. (Q4)
- **AC-5**: Independent of SDD-019; no import dependency on `fleet.py` lock state, no lock check. (Q5)
- **AC-6**: Dedup log written to all three destinations: ledger row (`dedup_scan_run`, `dedup_overlap_flagged`, `dedup_decision_recorded`) + per-spec-dir `dedup-scan.md` + rolling `backlog/DEDUP-LOG.md`. (Q6)
- **AC-7**: Empty/near-empty corpus emits explicit "no corpus to dedup against; 0 candidates scanned" notice, not silent skip. (Q7)
- **AC-8**: `/triage` and `/clarify` prompts invoke dedup pass automatically.
- **AC-9**: Full test suite passes (>= 213 baseline, no regression).

## Affected Modules

- `cli/dedup.py` -- new module: scan function, CLI entry point, `main(argv)` signature
- `cli/test_dedup.py` -- new tests for all three heuristic layers + tiered actions + edge cases
- `.github/skills/workflow/cross-feature-dedup/SKILL.md` -- new skill invoking CLI
- `.github/prompts/triage.prompt.md` -- hook to invoke dedup at /triage
- `.github/prompts/clarify.prompt.md` -- hook to invoke dedup at /clarify
- `backlog/DEDUP-LOG.md` -- new rolling dedup log

## Data Model Changes

Dedup findings persisted in three locations:
- **Ledger**: new event types `dedup_scan_run`, `dedup_overlap_flagged`, `dedup_decision_recorded` in `ledger/fleet.db`.
- **Per-spec-dir**: `dedup-scan.md` written to the candidate's spec dir when the overlap is spec-bound.
- **Rolling log**: `backlog/DEDUP-LOG.md` appended on every triage-round dedup pass.

No schema changes to existing tables. Reuses `parse_frontmatter` from `cli/schema_lint.py` for frontmatter `id` extraction.

## API Changes

- `dedup.py scan [--scope backlog|specs|all] [--format table|json]` -- run dedup scan against the specified corpus.
- `dedup.py scan --candidate "<title or path>"` -- check a single candidate against the corpus.
- Exit codes: 0 = clean, 1 = HARD overlap found, 2 = SOFT overlap found (prompt needed).

## Test Strategy

**OUTLINE -- lock at /tasks.**

- Unit: match heuristic (exact ID, fuzzy title, keyword Jaccard), output
  format, no-overlap path, empty-corpus path.
- Integration: end-to-end dedup invocation at /triage; verify decision
  prompt + dedup-log write to all three destinations.
- Regression: existing 213-test suite stays green; schema_lint clean.

## Validation Contract

The binding validation contract lives in the sibling file `validation.md`.
Required items have been drafted at /spec finalization (2026-06-07) and
will be locked at /tasks (F-07). Implementation MUST NOT begin until the
validation contract is locked and all REQUIRED items are explicitly listed.

## Traceability Matrix

| Requirement | Acceptance Criterion | Module |
|-------------|---------------------|--------|
| R1: Scan scope | AC-1 | cli/dedup.py |
| R2: Three-layer heuristic | AC-2 | cli/dedup.py |
| R3: Standalone CLI | AC-3 | cli/dedup.py |
| R4: Tiered action | AC-4 | cli/dedup.py |
| R5: SDD-019 independence | AC-5 | cli/dedup.py (no fleet.py import) |
| R6: Triple-destination log | AC-6 | cli/dedup.py, ledger/, backlog/ |
| R7: Empty corpus notice | AC-7 | cli/dedup.py |
| R8: Prompt integration | AC-8 | .github/prompts/triage.prompt.md, clarify.prompt.md |
| R9: No regression | AC-9 | cli/test_dedup.py |

## Open Questions

CLARIFY closed 2026-06-07. All 7 questions answered in `clarify.md`.
No remaining open questions.

## Out of Scope

- LLM-based semantic similarity (deferred to a future feature once layered heuristics prove insufficient).
- Auto-merge of detected duplicates (v1 prompts owner, never auto-merges).
- Cross-repo / multi-project dedup.
- Retroactive dedup of historical (done/archived) spec dirs.
- Dedup of post-SPEC artifacts (plans, tasks, validations, retros).

## Cross-Feature Notes

- **SDD-019** -- independent and composable (confirmed SDD-019 Q5 /
  SDD-020 Q5). SDD-020 ships first; no dependency on SDD-019 lock state.
- **SDD-FDC-001 (filesystem data contracts, Sprint 4, shipped)** -- the
  frontmatter `id` field is the canonical key for exact-match dedup.
  Reuse the existing `parse_frontmatter` from `cli/schema_lint.py`.
