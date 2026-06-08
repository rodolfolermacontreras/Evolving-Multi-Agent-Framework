---
id: SDD-20260608SELFREVIEW-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-end-of-session-self-review
---

# Feature Spec: End-of-Session Self-Review Loop (SDD-021)

- Date: 2026-06-08
- Author: Principal Architect + Principal Product Manager
- Status: APPROVED FOR PLAN/TASKS
- Priority: P2
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Spec ID: SDD-021

---

## Problem Statement

The framework improves through retrospectives and `/evolve`, but feature-session lessons are still easy to lose. The current pattern depends on an agent or human remembering, after the fact, that a session had repeated tool failures, unclear instructions, approval friction, redundant searches, or a missing skill. That creates four risks:

1. Useful process lessons remain in chat history instead of committed artifacts.
2. Agents may respond to friction by silently editing skills or instructions without reviewed promotion.
3. Gate-related problems are described inconsistently instead of using the SDD-023 user-gate model.
4. Sprint retros become less accurate because they reconstruct session friction from memory.

SDD-021 defines a lightweight self-review loop that runs at feature handoff/close and sprint close, emits structured findings, and routes durable changes through existing framework governance.

## Proposed Solution

Add a `session-self-review` workflow that produces a small structured review record at the end of feature sessions and sprint close. The record identifies what went well, what caused friction, whether any SDD-023 user gate was missing or pressured, and which findings deserve promotion.

The loop is intentionally advisory. It MAY propose lessons, backlog candidates, skill updates, prompt updates, template updates, or agent deltas. It MUST NOT directly apply durable framework changes. Durable changes move through `/evolve`, `lesson-capture`, PM triage, `/constitution`, or an approved implementation task.

## Self-Review Record Shape

Each self-review output MUST use these fields:

| Field | Required | Definition |
|-------|----------|------------|
| `source_feature` | Yes | Feature directory or sprint close identifier being reviewed. |
| `trigger` | Yes | `feature-handoff`, `feature-done`, `feature-blocked`, `owner-attention`, `sprint-close`, `friction-detected`, or `manual-request`. |
| `evidence_used` | Yes | Artifact paths, commands, validation results, or sanitized transcript summary used for the review. |
| `friction_observed` | Yes | Concrete issue or `none`. |
| `gate_findings` | Yes | SDD-023 gate references or `none`. |
| `promotion_target` | Yes | `no-op`, `session-note`, `lesson-candidate`, `backlog-candidate`, `gate-friction`, or `agent-skill-delta`. |
| `recommended_owner` | Yes | EM, PM, Architect, SW Dev, QA, owner, or `/evolve`. |
| `next_action` | Yes | One concrete action or `none`. |

## Gate Vocabulary Reuse

SDD-021 does not define a second approval model. When a self-review identifies missing approval, gate friction, pressure to proceed, or an approval-related lesson, it MUST cite SDD-023 gate fields:

- `gate_id`
- `gate_type`
- `blocking_scope`
- `approver`
- `evidence_type`
- `evidence_ref`
- `status`
- `next_action`

The review MUST treat generated executive surfaces as visibility only, not approval evidence. It MUST NOT infer approval from tests, silence, elapsed time, task status, or agent confidence.

## Requirements

- **R1: Trigger model.** The framework MUST require self-review at feature handoff/close states and sprint close, and MAY allow manual or friction-detected self-review at any time.
- **R2: Output shape.** The framework MUST define a structured self-review record with source, trigger, evidence, friction, gate findings, promotion target, owner, and next action.
- **R3: Transcript-independent evidence.** The self-review MUST function without raw transcript access by using committed artifacts, validation results, git metadata, and sanitized summaries.
- **R4: Privacy boundary.** The self-review MUST NOT require private transcript export, M365/WorkIQ access, or external system reads to operate.
- **R5: Promotion path.** Durable changes MUST route through `/evolve`, `lesson-capture`, PM triage, `/constitution`, or approved implementation tasks; self-review MUST NOT silently edit agents, skills, prompts, templates, or constitution files.
- **R6: Gate friction reuse.** Approval-related findings MUST reuse SDD-023 gate vocabulary and evidence taxonomy without redefining incompatible fields.
- **R7: Destination rules.** The implementation MUST distinguish no-op observations, session notes, lesson candidates, backlog candidates, gate friction, and agent/skill deltas.
- **R8: Sprint integration.** Sprint close MUST summarize open or promoted self-review findings so sprint retros and PI lessons do not rely on chat memory alone.
- **R9: Validation discipline.** REQUIRED validation items for SDD-021 MUST remain unchecked until implementation evidence exists; no REQUIRED item may be silently deferred.
- **R10: Approval-required changes.** Constitution edits, new dependencies, schema migrations, M365 permission changes, production-branch impact, external write behavior changes, or direct agent/skill mutation implied by implementation MUST be called out and stopped for the appropriate approval path.

## Acceptance Criteria

- **AC-1:** A `session-self-review` skill or equivalent workflow artifact defines the triggers from R1.
- **AC-2:** The workflow artifact emits or documents every field in the Self-Review Record Shape table.
- **AC-3:** The workflow artifact lists transcript-independent evidence sources and explicitly treats raw transcripts as optional enrichment.
- **AC-4:** The workflow artifact prohibits private transcript export and external data access as required inputs.
- **AC-5:** Agent, skill, prompt, template, and constitution deltas are emitted only as lesson candidates or curation inputs, not directly applied by the self-review step.
- **AC-6:** Gate-related findings cite SDD-023 fields and accepted evidence types.
- **AC-7:** The workflow distinguishes `no-op`, `session-note`, `lesson-candidate`, `backlog-candidate`, `gate-friction`, and `agent-skill-delta` outcomes.
- **AC-8:** Sprint close instructions or templates include a place to summarize self-review findings or explicitly record `none`.
- **AC-9:** F-19 implementation updates validation without checking REQUIRED items until evidence exists.
- **AC-10:** `python spec-driven-development/cli/schema_lint.py` exits 0 after implementation.
- **AC-11:** Full pytest suite exits 0 after implementation with test count at or above the Sprint 9 baseline when implementation touches executable code.

## Affected Modules For F-19

| File | Expected Change | Notes |
|------|-----------------|-------|
| `.github/skills/operational/session-self-review/SKILL.md` | New | Primary workflow surface. Must have valid SKILL.md frontmatter. |
| `.github/skills/operational/lesson-capture/SKILL.md` | Optional extend | Only if handoff wording to self-review is needed. |
| `.github/prompts/evolve.prompt.md` | Optional extend | Only if `/evolve` needs explicit self-review input handling. |
| `spec-driven-development/templates/review.md` or closest existing review template | Optional extend | Add self-review section only if template exists and pattern is stable. |
| `spec-driven-development/templates/agent-brief.md` or handoff template | Optional extend | Add end-of-session review reminder if low-risk. |
| `spec-driven-development/sprints/README.md` | Optional extend | Document where sprint-level self-review summaries land. |
| `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md` | Update | Check REQUIRED items only after evidence exists. |
| `spec-driven-development/specs/2026-06-08-end-of-session-self-review/tasks.md` | Update | Mark implementation tasks done during F-19. |

## Data Model Changes

No data model or ledger schema change is approved by F-17. If F-19 determines that self-review findings require a new durable event table or incompatible ledger schema change, implementation MUST stop for ADR + owner approval before changing schema files.

## API / CLI Changes

No CLI change is required by F-17. If F-19 chooses to add CLI support, it MUST be stdlib-only, follow `docs/CLI-PATTERN.md`, and include tests. A CLI addition is optional, not required for SDD-021 v1.

## Test Strategy

- Skill/frontmatter validation: schema lint clean for the new `session-self-review` skill.
- Link/path validation: references to SDD-023, `/evolve`, and `lesson-capture` resolve.
- Contract review: sample self-review output includes every required record field.
- Governance review: no durable agent/skill/constitution edits occur as a side effect of self-review.
- Regression: full pytest if executable code or CLI behavior changes; docs/skill-only implementation may rely on schema lint plus targeted link/path checks unless F-19 touches code.

## Validation Contract

The binding validation contract lives in `validation.md`. It is locked by this F-17 `/tasks` pass for F-19 implementation. No REQUIRED item may be loosened or silently deferred during implementation.

## Traceability Matrix

| Requirement | Acceptance Criteria | Validation Items | Implementation Tasks |
|-------------|---------------------|------------------|----------------------|
| R1 | AC-1 | V-1 | T-021-01, T-021-02 |
| R2 | AC-2 | V-2 | T-021-02 |
| R3 | AC-3 | V-3 | T-021-02, T-021-03 |
| R4 | AC-4 | V-4 | T-021-03 |
| R5 | AC-5 | V-5 | T-021-04, T-021-05 |
| R6 | AC-6 | V-6 | T-021-02, T-021-06 |
| R7 | AC-7 | V-7 | T-021-02, T-021-04 |
| R8 | AC-8 | V-8 | T-021-05 |
| R9 | AC-9, AC-10, AC-11 | V-9, V-10, V-11 | T-021-07 |
| R10 | AC-5 | M-1, M-2, M-3 | T-021-06, T-021-07 |

## Open Questions

None for F-17. CLARIFY closed Q-F through Q-I in `clarification-log.md`.

## Out of Scope

- Implementing the self-review skill during F-17.
- Editing `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, or templates during F-17.
- Editing `constitution/**` during F-17.
- Adding new dependencies.
- Adding a ledger schema migration.
- Requiring raw transcript export or private data access.
- Closing Sprint 9 or PI-5.

## Approval-Required Items Before Or During F-19

- Constitution wording changes require ADR + owner approval.
- Ledger schema migration requires ADR + owner approval.
- New dependencies require Level-2 Friction Analysis + owner approval.
- M365 permission changes require owner approval.
- Production-branch or push behavior changes require owner approval.
- External write behavior changes require owner approval.
- Direct agent/skill mutation by self-review requires redesign; proposed deltas must route through `/evolve` or another approved path.