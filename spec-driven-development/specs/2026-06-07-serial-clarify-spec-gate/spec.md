---
id: SDD-20260607SERIAL-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Feature Spec: Serial Gate on CLARIFY/SPEC (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect + Owner
- Status: APPROVED
- Priority: P1
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-019

CLARIFY resolved 2026-06-07. Constitutional amendment scope confirmed:
new Article XI ("Cross-Feature Serial Gate at CLARIFY and SPEC") in
`constitution/principles.md`. Version bump 1.1.0 -> 1.2.0. ADR to be
drafted in F-07; constitution edit in F-08 after owner approval. The
erroneous "Article VIII" label from the scaffold has been corrected --
Article VIII already exists (Constitution Immutability); the new article
is XI.

---

## Problem Statement

CLARIFY and SPEC phases currently run in parallel per feature. There is no
repo-wide gate that enforces "one feature at a time may sit in CLARIFY or
SPEC." This creates two concrete failure modes:

1. **Cross-feature context bleed.** A session writing the spec for feature
   A can absorb framing, vocabulary, and constraints from feature B that is
   still in CLARIFY, and silently apply them to A. Article VII addresses
   *intra-session* contamination but does not prevent *inter-feature*
   contamination at the repo level.
2. **Two features racing to the same spec dir / overlapping spec dirs.** With
   no serial gate, two parallel CLARIFY rounds can both produce specs that
   touch the same module, the same artifact, or even claim overlapping
   problem statements. SDD-020 (cross-feature dedup) covers detection;
   SDD-019 covers prevention by serializing the upstream phases.

Sprint 5 Architect audit (2026-06-07) noted this is the gate keeping the
framework from safely running multi-worker dispatch across features. Today
the rule is implicit (owner discipline); the framework provides no
enforcement, no surface in `exec/state.md`, and no refusal in `fleet.py`.

## Proposed Solution

Introduce a **repo-wide serial gate** at the CLARIFY and SPEC phases,
enforced by `cli/fleet.py` (or an adjacent CLI), surfaced on the dashboard,
and codified in the constitution.

CLARIFY resolved all open questions (2026-06-07). The gate shape is:

- **Per-phase locks**: two independent locks (CLARIFY and SPEC), each
  holding at most one feature. Per-phase preserves throughput.
- **Lock state from frontmatter**: no new state file. CLARIFY lock = any
  clarification file with status != done; SPEC lock = spec.md with
  status == draft. Reuses SDD-FDC-001 as the lock substrate.
- **Hybrid enforcement**: hard refusal in `fleet.py` automated dispatch;
  advisory warning in interactive slash commands.
- **Force-release**: `fleet.py lock force-release <feature> --reason "..."`
  with ledger audit row.
- **Article XI**: new constitutional article "Cross-Feature Serial Gate at
  CLARIFY and SPEC" (not Article VIII, which already exists). Version
  bump 1.1.0 -> 1.2.0. ADR in F-07, constitution edit in F-08.
- **Intra-feature parallelism**: unlimited workers within the lock holder;
  zero workers for other features in the same phase.
- **Queue**: priority-weighted with FIFO tiebreak.
- **Migration**: grandfather existing open features at enforcement turn-on.
- **Carve-outs**: /triage, /plan, /tasks, /implement, /qa, /retro, and
  <3-file bug fixes stay parallelizable.

## Acceptance Criteria

- **AC-1**: `fleet.py` hard-refusal -- dispatching a second CLARIFY while another feature holds the CLARIFY lock exits non-zero with message naming the lock holder. (Q1, Q3)
- **AC-2**: `fleet.py` hard-refusal -- dispatching a second SPEC while another feature holds the SPEC lock exits non-zero with message naming the lock holder. (Q1, Q3)
- **AC-3**: Interactive slash commands (`/clarify`, `/spec`) emit advisory warning, not hard block, when the lock is held by another feature. (Q3)
- **AC-4**: Lock state derived from frontmatter -- clarification file with status != done = CLARIFY lock held; spec.md with status == draft = SPEC lock held. No new state file. (Q2)
- **AC-5**: `fleet.py lock force-release <feature> --reason "..."` writes a ledger row (event_type `lock_force_released`) with mandatory `--reason`; subsequent dispatch proceeds. (Q4)
- **AC-6**: Article XI ("Cross-Feature Serial Gate at CLARIFY and SPEC") added to `constitution/principles.md` via ADR; version bumped 1.1.0 -> 1.2.0. (Q5)
- **AC-7**: Intra-feature parallel workers proceed unrestricted; inter-feature workers in the same phase (CLARIFY or SPEC) are blocked. (Q6)
- **AC-8**: Queue releases in priority-weighted order with FIFO tiebreak, aligning with PM's RICE-based backlog ordering. (Q7)
- **AC-9**: Existing open features at enforcement turn-on are grandfathered; lock applies only to new CLARIFY/SPEC starts after the cutover commit. (Q8)
- **AC-10**: `/triage`, `/plan`, `/tasks`, `/implement`, `/qa`, `/retro`, and <3-file bug fixes stay parallelizable and are NOT gated. (Q9)
- **AC-11**: Full test suite passes (>= 213 baseline, no regression).

## Affected Modules

- `cli/fleet.py` -- lock acquire/release/status subcommands + pre-dispatch gate check
- `cli/test_fleet.py` -- new tests for lock mechanics, refusal, queue, force-release
- `constitution/principles.md` -- Article XI addition (via ADR in F-07)
- `docs/ADR/ADR-NNN-serial-clarify-spec-gate.md` -- new (drafted in F-07)

## Data Model Changes

Lock state derived from artifact frontmatter per SDD-FDC-001 -- no new state file or table. A feature holds the CLARIFY lock if any clarification file in its spec dir has `status != done`; it holds the SPEC lock if its `spec.md` has `status == draft`. Queue ordering persisted in fleet ledger event rows (`lock_queued`, `lock_acquired`, `lock_released`, `lock_force_released`).

## API Changes

- `fleet.py lock acquire <feature>` -- explicitly acquire the CLARIFY or SPEC lock (inferred from feature's current phase).
- `fleet.py lock release <feature>` -- release the lock for the given feature.
- `fleet.py lock status` -- display current lock holders + queue.
- `fleet.py lock force-release <feature> --reason "..."` -- force-release with mandatory reason, writes ledger audit row.

## Test Strategy

**OUTLINE -- lock at /tasks.**

- Unit: lock acquire/release, queue ordering, refusal message format.
- Integration: end-to-end `fleet.py` dispatch refusal scenario.
- Regression: existing 213-test suite stays green; schema_lint clean.
- Constitutional amendment: lint enforces new Article version.

## Validation Contract

The binding validation contract lives in the sibling file `validation.md`.
Required items have been drafted at /spec finalization (2026-06-07) and
will be locked at /tasks (F-07). Implementation MUST NOT begin until the
validation contract is locked and all REQUIRED items are explicitly listed.

## Traceability Matrix

| Requirement | Acceptance Criterion | Module |
|-------------|---------------------|--------|
| R1: CLARIFY lock refusal | AC-1 | cli/fleet.py |
| R2: SPEC lock refusal | AC-2 | cli/fleet.py |
| R3: Advisory in interactive | AC-3 | .github/prompts/ slash commands |
| R4: Frontmatter-derived lock | AC-4 | cli/fleet.py, specs/**/clarify.md, specs/**/spec.md |
| R5: Force-release audit | AC-5 | cli/fleet.py, ledger/ |
| R6: Article XI amendment | AC-6 | constitution/principles.md, docs/ADR/ |
| R7: Intra-feature parallel | AC-7 | cli/fleet.py |
| R8: Priority-weighted queue | AC-8 | cli/fleet.py, ledger/ |
| R9: Grandfather existing | AC-9 | cli/fleet.py |
| R10: Post-SPEC parallel | AC-10 | cli/fleet.py |
| R11: No regression | AC-11 | cli/test_fleet.py |

## Open Questions

CLARIFY closed 2026-06-07. All 9 questions answered in `clarify.md`.
No remaining open questions.

## Out of Scope

- Multi-repo / cross-repo serial gates.
- Serial gates on PLAN, TASKS, IMPLEMENT, QA, or RETRO phases.
- Auto-resolution of lock contention (lock-holder liveness probe); v1 relies on owner discipline + force-release override.
- Integration with SDD-020 cross-feature dedup (independent and composable per SDD-019 Q5 / SDD-020 Q5).

## Cross-Feature Notes

- **SDD-020 (cross-feature dedup)** is independent and composable
  (confirmed SDD-019 Q5 / SDD-020 Q5). Neither blocks the other.
  SDD-020 ships first (lower risk, no constitutional amendment).
- **SDD-027 (host `.gitignore` protection)** is independent at the
  feature level; shares the Sprint 6 capacity budget.
