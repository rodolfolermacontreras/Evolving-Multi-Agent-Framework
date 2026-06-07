---
id: SDD-20260607DEDUP-spec
type: spec
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Feature Spec: Cross-Feature Deduplication at /triage and /clarify (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect (scaffold) / TBD owner at /spec finalization
- Status: SKELETON -- CLARIFY pending (do NOT proceed to /plan until clarify.md answered)
- Priority: P1
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-020

> **SYNERGISTIC WITH SDD-019 (serial CLARIFY/SPEC gate).** Order of
> implementation matters and must be resolved at CLARIFY. Two viable
> orderings:
>
> 1. **Dedup first, gate second.** Dedup output becomes a precondition
>    for SDD-019 lock acquisition (if a candidate overlaps an existing
>    backlog entry, acquiring the lock is refused).
> 2. **Gate first, dedup second.** Dedup runs inside the locked CLARIFY
>    phase as a quality gate.
> 3. **Independent and composable.** Neither depends on the other; they
>    ship in parallel.
>
> CLARIFY Q5 below forces this decision before /spec finalization.

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

The shape of the detector (match heuristic, action on overlap, tooling
form, integration with SDD-019) is **deliberately unresolved** at scaffold
time. See `clarify.md`. The Proposed Solution will be expanded once
CLARIFY closes.

Likely components, subject to CLARIFY:

- A scan function that reads `backlog/BACKLOG.md`, `backlog/IDEAS.md`, and
  open spec dirs (`specs/**/spec.md`) and emits an overlap report.
- A CLI subcommand (`fleet.py dedup`, `state_builder.py dedup`, or a new
  `dedup.py`) that invokes the scan.
- A skill or slash-command hook that runs the scan automatically at
  `/triage` and `/clarify` entry.
- A dedup-log artifact under the spec dir (or under `backlog/`) recording
  what was scanned, what overlapped, and what the owner decided.
- Integration glue with SDD-019 lock acquisition (form TBD per CLARIFY Q5).

## Acceptance Criteria

> **TODO -- BLOCKED ON CLARIFY.** Each criterion MUST trace to a CLARIFY
> answer (`See clarify.md Q-NN`). Draft outline:
>
> 1. Given a candidate item identical to an existing BACKLOG row, when
>    the dedup pass runs, then it flags the overlap and the owner sees a
>    decision prompt (CLARIFY Q4 action-on-overlap).
> 2. Given a candidate item semantically overlapping an open spec dir,
>    when the dedup pass runs, then it flags the spec dir by ID and path
>    (CLARIFY Q1 scope + Q2 match heuristic).
> 3. Given no overlap exists, when the dedup pass runs, then it emits a
>    clean report and the triage / clarify flow proceeds.
> 4. ... (additional ACs once CLARIFY closes)

## Affected Modules

> **TENTATIVE -- subject to CLARIFY answers.**
>
> - Files (likely):
>   - `spec-driven-development/cli/fleet.py` (new `dedup` subcommand, OR)
>   - `spec-driven-development/cli/dedup.py` (new module, OR)
>   - `spec-driven-development/cli/state_builder.py` (subcommand extension)
>   - `.github/skills/workflow/cross-feature-dedup/SKILL.md` (new skill, if CLARIFY Q3 says skill-first)
>   - `.github/prompts/triage.prompt.md` (hook to invoke dedup at /triage)
>   - `.github/prompts/clarify.prompt.md` (hook to invoke dedup at /clarify)
> - Directories (read-only):
>   - `spec-driven-development/backlog/`
>   - `spec-driven-development/specs/**`

## Data Model Changes

> **TBD via CLARIFY.** Possible options:
>
> - Dedup log appended to each spec dir as `dedup-scan.md`.
> - Single rolling `backlog/DEDUP-LOG.md`.
> - Ledger event type `dedup_scan` with overlap candidates.

## API Changes

> **TBD via CLARIFY.** Possible CLI surface:
>
> - `fleet.py dedup --candidate "<title or path>" [--scope backlog|specs|all]`
> - Output: JSON by default, table on `--format table` (mirroring SDD-FDC `count`).

## Test Strategy

> **OUTLINE only.** Lock at /tasks.
>
> - Unit: match heuristic (exact, fuzzy, semantic per CLARIFY Q2), output
>   format, no-overlap path.
> - Integration: end-to-end dedup invocation at /triage; verify decision
>   prompt + dedup-log write.
> - Regression: existing 213-test suite stays green; schema_lint clean.

## Validation Contract

The binding validation contract lives in the sibling file `validation.md`.
It is a SKELETON at scaffold time; required items will be drafted at /spec
finalization and locked at /tasks. Implementation MUST NOT begin until the
validation contract is locked and all REQUIRED items are explicitly listed.

## Traceability Matrix

> **TODO -- populate at /spec finalization once CLARIFY closes.**
>
> | Requirement | Acceptance Test | Module |
> |-------------|-----------------|--------|
> | TBD | TBD | TBD |

## Open Questions

See `clarify.md`. CLARIFY questions are the gate, not casual open notes.

## Out of Scope

> **TODO -- BLOCKED ON CLARIFY.** Tentative candidates:
>
> - Auto-merge of detected duplicates (v1 prompts owner, never auto-merges).
> - Cross-repo dedup (single-repo only for v1).
> - LLM-based semantic similarity (CLARIFY Q2 may choose simpler heuristics for v1).
> - Retroactive dedup of historical BACKLOG entries (v1 is forward-looking).

## Cross-Feature Notes

- **SDD-019** -- ordering and integration explicitly resolved in CLARIFY Q5.
- **SDD-FDC-001 (filesystem data contracts, Sprint 4, shipped)** -- the
  frontmatter `id` field is the canonical key for exact-match dedup.
  Reuse the existing `parse_frontmatter` from `cli/schema_lint.py`.
