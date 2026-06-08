---
id: ADR-013
type: spec
status: active
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# ADR-013: Serial CLARIFY/SPEC Gate (Article XI)

- Date: 2026-06-07
- Status: accepted

## Context

CLARIFY and SPEC phases run in parallel per feature. There is no repo-wide
gate that enforces "one feature at a time in CLARIFY" or "one feature at a
time in SPEC." This creates two concrete failure modes:

1. **Cross-feature context bleed.** A session writing the spec for feature A
   can absorb framing, vocabulary, and constraints from feature B that is
   still in CLARIFY, silently applying them to A. Article VII ("One Feature,
   One Session") addresses intra-session contamination but does not prevent
   inter-feature contamination at the repo level.

2. **Spec-dir races.** Two parallel CLARIFY rounds can both produce specs
   that touch the same module, claim overlapping problem statements, or
   occupy the same spec dir path. SDD-020 (cross-feature dedup) covers
   detection after the fact; SDD-019 covers prevention by serializing the
   upstream phases.

Sprint 5 Architect audit (2026-06-07) identified this as the gate keeping
the framework from safely running multi-worker dispatch across features.
Today the rule is implicit (owner discipline); the framework provides no
enforcement, no surface in `exec/state.md`, and no refusal in `fleet.py`.

SDD-019 CLARIFY (2026-06-07) confirmed that this requires a new
constitutional article, not an extension of Article VII. Article VII is
session-scoped; the serial gate is repo-scoped. Conflating them muddies
both rules and prevents independent amendment.

## Decision

Add **Article XI "Cross-Feature Serial Gate at CLARIFY and SPEC"** to
`constitution/principles.md`. Bump the constitution version from 1.1.0 to
1.2.0 (MINOR: new article added, no breaking changes to existing articles).

The article establishes:

1. **Two independent per-phase locks.** One for CLARIFY, one for SPEC. Each
   holds at most one feature at a time. Per-phase granularity preserves
   throughput: a feature finishing CLARIFY frees its slot before its SPEC
   starts.

2. **Lock state derived from frontmatter.** The SDD-FDC-001 filesystem data
   contract is the lock substrate. A feature holds the CLARIFY lock if any
   clarification file in its spec dir has `status != done`. It holds the SPEC
   lock if its `spec.md` has `status == draft`. No new state file.

3. **Hybrid enforcement.** Hard refusal in `fleet.py` automated dispatch
   (no human in the loop to override safely). Advisory warning in
   interactive slash commands (`/clarify`, `/spec`) where the owner is
   present and can make the override call.

4. **Force-release with ledger audit.** `fleet.py lock force-release
   <feature> --reason "..."` writes a ledger row (`lock_force_released`)
   with mandatory `--reason`. Subsequent dispatch proceeds. Explicit,
   audited, scriptable.

5. **Priority-weighted FIFO queue.** When multiple features wait for the
   same lock, release order follows PM's RICE-based backlog priority with
   FIFO timestamp as tiebreak.

6. **Grandfather existing features.** Features already open at enforcement
   turn-on are not retroactively blocked. The lock applies only to new
   CLARIFY/SPEC starts after the cutover commit.

7. **Carve-outs.** `/triage`, `/plan`, `/tasks`, `/implement`, `/qa`,
   `/retro`, and <3-file bug fixes stay parallelizable and are NOT gated.

## Consequences

- `cli/fleet.py` gains `lock` subcommand group (`acquire`, `release`,
  `status`, `force-release`) and a pre-dispatch gate check.
- Every CLARIFY or SPEC entry requires an implicit lock check, adding a
  frontmatter scan to the dispatch path.
- Throughput impact mitigated by per-phase (not per-repo) granularity:
  one feature can be in CLARIFY while another is in SPEC simultaneously.
- Propagation scan needed for any skill, prompt, or doc that enumerates
  "Articles I-X" -- these must update to "Articles I-XI".
- Constitution version bump from 1.1.0 to 1.2.0 requires `schema_lint`
  to accept the new version.

## Alternatives Considered

- **Extend Article VII with a repo-wide clause.** Rejected: Article VII
  addresses session-scope discipline ("One Feature, One Session"). The
  serial gate addresses repo-scope discipline. Conflating them prevents
  independent amendment and muddies both rules.

- **Amend `decision-policy.md` only.** Rejected: the rule would be harder
  to discover outside `principles.md`. Framework principles should be
  explicit and enumerable in a single document.

- **No constitutional change, enforcement-only.** Rejected: enforcement
  without a stated principle is fragile. If `fleet.py` is bypassed (manual
  dispatch, direct slash command), the rule evaporates. A constitutional
  article makes the rule explicit and independently challengeable.
