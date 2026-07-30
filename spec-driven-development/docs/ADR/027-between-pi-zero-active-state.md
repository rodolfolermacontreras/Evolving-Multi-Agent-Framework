# ADR-027: Between-PI zero-active state and truthful display labels

- Date: 2026-07-30
- Status: accepted
- Supersedes: ADR-024 Decision 1 marker cardinality
- Decision authority: Level 2, project owner
- Constitution impact: `constitution/roadmap.md` MINOR bump `1.2.0 -> 1.3.0`

## Owner approval evidence

The project owner directed formal PI-9 closure without opening a successor and
explicitly approved the resulting lifecycle model in this conversation on
2026-07-30: "Treat this as owner approval of the truthful zero-active-PI model,
but do not invent PI-10." The same direction requires the package to preserve
SDD-059 as unscheduled. This is explicit Level-2 approval for the constitution
contract change and its narrow truthfulness correction; it is not approval to
create PI-10, create a successor sprint, schedule SDD-059, or bypass normal
implementation and test gates.

## Context

ADR-024 requires exactly one `(current)` roadmap marker. That rule assumes a
successor PI opens in the same transition that closes its predecessor. PI-9 is
instead closing after all planned work shipped, while the owner has deliberately
not selected or opened a successor increment. Keeping PI-9 marked `(current)`
would contradict its owner-ratified closed state. Creating PI-10 merely to
satisfy the marker rule would invent product scope and violate owner direction.

The state builder already parses closed and current markers separately, but
`current_pi()` and `resolve_display_pi()` fall back to the newest closed PI when
all PIs are closed. Generated Markdown, HTML, and work-index surfaces then label
that historical fallback as `Current PI`. The fallback was useful when ADR-024
made a zero-active state invalid; under the approved between-PI model it becomes
a false operational claim.

## Options considered

### Option A: Open PI-10 during PI-9 close

- Pros: preserves ADR-024's exactly-one marker invariant; requires no reader or
  renderer correction.
- Cons: invents an unapproved increment, implies unapproved scope and cadence,
  and conflicts directly with the owner's instruction not to invent PI-10.

### Option B: Allow zero markers but continue labeling PI-9 as current

- Pros: limits the change to roadmap wording; preserves existing state-builder
  fallback behavior and tests.
- Cons: makes generated operational surfaces false by conflating latest history
  with active work; undermines PI-8's Truth in the Window objective.

### Option C: Model zero-or-one active PI and separate active from historical display

- Pros: represents the real between-PI state, preserves exactly one marker when
  an active PI exists, keeps history available, and requires only a narrow
  stdlib reader/test correction.
- Cons: changes an accepted constitution contract and one established fallback;
  requires a MINOR roadmap version bump plus focused regression coverage.

## Decision

Adopt Option C.

1. **Active-PI cardinality.** The roadmap MUST carry at most one `(current)`
   marker. When an active PI exists, exactly one PI MUST carry `(current)` and
   its `sprints/PI-N/CURRENT_PI.md` artifact MUST also be active. Zero `(current)`
   markers is valid only in an owner-ratified between-PI state after a close and
   before a successor opens.
2. **No synthetic successor.** Agents MUST NOT create a PI, sprint, allocation,
   or `(current)` marker solely to avoid the zero-active state. PI-10 remains
   nonexistent and SDD-059 remains unscheduled under this decision.
3. **Truthful labels.** `Current PI` is reserved for an active PI. When no active
   PI exists, generated operational surfaces MUST say `No active PI`. A surface
   MAY separately show `Latest PI: PI-9 (closed)` as historical context, but
   MUST NOT label the latest closed PI as current or active.
4. **Selection semantics.** Active selection and historical selection are
   distinct concepts. The active-PI resolver MUST return no active PI when all
   roadmap PIs are closed and no active `CURRENT_PI.md` exists. Any newest-PI
   fallback needed for history MUST use a separately named path and label.
5. **Narrow implementation.** The Software Developer MUST apply the smallest
   TDD correction in `cli/state_builder_data.py` and
   `cli/test_state_builder.py`. Start with a failing all-closed assertion, then
   make `current_pi()` return `None` for the all-closed case and verify
   `resolve_display_pi()` propagates `None`. Add a build-level regression proving
   generated `state.md`, `state.html`, and `work-index.md` contain no false
   `Current PI: PI-9` claim and show `No active PI` (or an explicitly historical
   `Latest PI: PI-9 (closed)` label). Preserve explicit override behavior and the
   defensive newest-open fallback for malformed open roadmaps.
6. **Article X.** The correction MUST follow test-first ordering and MUST keep
   the Article X footprint lock green. Locked render functions MUST not be edited
   unless the failing regression proves their existing `None` handling cannot
   satisfy this decision; any such exception requires the normal Article X gate.
7. **Constitution version.** This adds a valid lifecycle state and loosens the
   prior exactly-one rule. Per ADR-006 it is a backward-compatible additive
   governance change: `roadmap.md` receives a MINOR bump `1.2.0 -> 1.3.0` and
   `last_amended: 2026-07-30`.

## Consequences

- Positive: PI-9 can close truthfully without fabricated successor scope;
  generated surfaces distinguish operational state from historical context.
- Positive: the active state remains unambiguous because exactly one marker is
  still mandatory whenever an active PI exists.
- Negative: one SDD-050 fallback test and its production behavior must change.
- Neutral: no dependency, schema, external integration, successor PI, sprint,
  backlog allocation, or Article X contract change is authorized.

## Compliance and propagation

- [x] Owner Level-2 approval recorded verbatim before the constitution edit.
- [x] No new dependencies or schema changes.
- [x] No successor PI/sprint created; SDD-059 remains unscheduled.
- [x] ADR-024 preserved for history and marked superseded only for cardinality.
- [x] `roadmap.md` receives the required MINOR version bump and precise wording.
- [x] Software Developer TDD correction completed and focused tests green.
- [x] Generated close surfaces regenerated from the corrected builder.
- [x] Article X footprint lock and relevant state-builder suite green.

Propagation review: state-builder active selection and generated labels were
corrected through the narrow handoff above. No skill, prompt, template,
archetype constitution, or decision-policy wording encodes ADR-024's
exactly-one-at-all-times rule strongly enough to require amendment in this close
package.