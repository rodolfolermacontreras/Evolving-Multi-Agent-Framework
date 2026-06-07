---
id: SDD-20260607SERIAL-spec
type: spec
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Feature Spec: Serial Gate on CLARIFY/SPEC (Sprint 6)

- Date: 2026-06-07
- Author: Principal Architect (scaffold) / TBD owner at /spec finalization
- Status: SKELETON -- CLARIFY pending (do NOT proceed to /plan until clarify.md answered)
- Priority: P1
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Spec ID: SDD-019

> **CONSTITUTIONAL AMENDMENT CANDIDATE.** This feature is expected to require
> an amendment to `constitution/principles.md` (Article VII -- "One Feature,
> One Session") and/or `constitution/decision-policy.md` to formalize the
> serial gate. **An ADR MUST be drafted before any `constitution/` edit, and
> the ADR drafting is BLOCKED until CLARIFY answers are recorded in
> `clarification-log.md` and reviewed by the Principal Architect + owner.**
> The CLARIFY round must explicitly decide which Article is touched and
> whether a new Article is needed.

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

The shape of the gate (per-phase vs per-repo, batch vs strict serial,
advisory vs hard refusal, which Article is amended) is **deliberately
unresolved** at scaffold time. See `clarify.md` for the CLARIFY questions
that gate /spec finalization. The Proposed Solution section will be
expanded once CLARIFY answers land.

Likely components, subject to CLARIFY:

- A gate state file or ledger query that names the single feature currently
  holding the CLARIFY-or-SPEC lock.
- A `fleet.py` check that refuses to dispatch a worker for a `/clarify` or
  `/spec` task against a feature that does not hold the lock.
- A dashboard widget surfacing "current CLARIFY/SPEC holder" + queue.
- A constitutional amendment (Article TBD per CLARIFY) recording the rule.
- A migration / backwards-compatibility story for features already
  mid-CLARIFY or mid-SPEC at the moment of enforcement turn-on.

## Acceptance Criteria

> **TODO -- BLOCKED ON CLARIFY.** Acceptance criteria cannot be authored
> until the CLARIFY questions in `clarify.md` are answered. Each criterion
> MUST trace to a CLARIFY answer (`See clarify.md Q-NN`). Draft outline:
>
> 1. Given two features simultaneously requesting CLARIFY, when fleet.py
>    dispatches, then exactly one holds the lock and the other is queued
>    with a deterministic ordering rule (CLARIFY Q-?).
> 2. Given a feature holds the SPEC lock, when a worker attempts to start
>    CLARIFY on a different feature, then fleet.py refuses with a clear
>    message naming the lock holder (CLARIFY Q-?).
> 3. Given the constitution is amended, when schema_lint runs, then the
>    amended Article version-bump is enforceable by lint (CLARIFY Q-?).
> 4. ... (additional ACs once CLARIFY closes)

## Affected Modules

> **TENTATIVE -- subject to CLARIFY answers.**
>
> - Files (likely):
>   - `spec-driven-development/cli/fleet.py` (enforcement)
>   - `spec-driven-development/cli/state_builder.py` (dashboard surface)
>   - `spec-driven-development/constitution/principles.md` (amendment if CLARIFY says Article VII)
>   - `spec-driven-development/constitution/decision-policy.md` (amendment if CLARIFY says decision policy)
>   - `spec-driven-development/docs/ADR/ADR-XXX-serial-clarify-spec-gate.md` (new, drafted post-CLARIFY)
> - Directories (likely read-only):
>   - `spec-driven-development/specs/**` (lock-state discovery)
>   - `spec-driven-development/ledger/` (lock persistence, if ledger-backed)

## Data Model Changes

> **TBD via CLARIFY.** Possible options:
>
> - Lock-state file at `spec-driven-development/fleet/clarify-spec-lock.json`.
> - Ledger row (new event type `lock_acquired` / `lock_released`).
> - Convention: derive lock from the most-recent open spec dir state.

## API Changes

> **TBD via CLARIFY.** Possible options:
>
> - `fleet.py lock acquire <feature>` / `lock release <feature>` / `lock status` subcommands.
> - Pre-dispatch hook in `fleet.py dispatch` that consults lock state.

## Test Strategy

> **OUTLINE only.** Lock at /tasks.
>
> - Unit: lock acquire/release, queue ordering, refusal message format.
> - Integration: end-to-end `fleet.py` dispatch refusal scenario.
> - Regression: existing 213-test suite stays green; schema_lint clean.
> - Constitutional amendment: lint enforces new Article version.

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

> **TODO -- BLOCKED ON CLARIFY.** Out-of-scope items must be enumerated
> explicitly after CLARIFY closes. Tentative candidates:
>
> - Multi-repo / cross-repo serial gates (single-repo only for v1).
> - Serial gates on PLAN/TASKS/IMPLEMENT phases (CLARIFY/SPEC only).
> - Auto-resolution of lock contention (queue + manual order only for v1).

## Cross-Feature Notes

- **SDD-020 (cross-feature dedup)** is synergistic. CLARIFY must resolve
  ordering: does dedup-detection (SDD-020) become a *precondition* of
  acquiring the SDD-019 lock, or are they independent and composable?
- **SDD-027 (host `.gitignore` protection)** is independent at the
  feature level but shares the Sprint 6 capacity budget.
