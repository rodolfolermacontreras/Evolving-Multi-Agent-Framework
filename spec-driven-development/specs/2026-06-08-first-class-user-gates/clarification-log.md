---
id: SDD-20260608USERGATES-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-first-class-user-gates
---

# CLARIFY: First-Class User Gates (SDD-023)

- Date: 2026-06-08
- Owners: Principal Product Manager + Principal Architect
- Sprint: PI-5 Sprint 5 (= overall Sprint 9)
- Source item: SDD-023 -- First-class user gates as a uniform construct
- Status: CLOSED for SPEC/PLAN/TASKS

---

## Context Verified

- Sprint 8 ratification is recorded in commit `8b7d5b9` with owner evidence: "yes Sprint 8 was ratified, we are good".
- Sprint 8 closed with 331 passing tests, 2 skipped, and schema lint clean.
- SDD-023 is Sprint 9 item 1. Its vocabulary must be reusable by SDD-021 end-of-session self-review and SDD-025 stakeholder-pressure defense.
- The existing constitution already establishes human approval authority in Article IX and validation discipline in Article X.
- This F-16 pass is design-only. It does not edit `constitution/**`, `cli/**`, generated exec state, or external systems.

---

## Q-A: Gate Inventory

Question: Which lifecycle phases or decision surfaces require explicit user gates by default?

Recommended answer: Define required user gates by decision risk rather than by every phase name. By default, explicit user gates are required for: owner answers that close CLARIFY when unresolved choices affect scope or governance; ADR acceptance before ADR-dependent edits; constitution edits; Level-2 decisions; external writes; model upgrades; sprint close; push approval; PI close; production-branch impact; and any attempt to close with a REQUIRED validation item unchecked, deferred, or converted to optional.

Why this matters: A phase-only list is too blunt. Some CLARIFY and SPEC decisions are routine, while a single external write or constitution cross-reference can carry Level-2 risk. The inventory must catch the high-risk surfaces without adding ceremony to every local task.

Answer: Adopt the recommendation. The default inventory is codified in `spec.md` as R1 and AC-1. Implementation may add more gate types later, but may not remove these defaults without a new approved spec or ADR.

Status: CLOSED.

---

## Q-B: Gate Schema

Question: Should gates live in spec frontmatter, `validation.md`, a new `gates.md`, the ledger, or all of the above?

Recommended answer: Use a layered schema with one authoritative contract and multiple derived surfaces:

- `validation.md` is the authoritative per-feature gate contract. It lists every required user gate, its blocking scope, accepted evidence, owner, and status.
- `spec.md` frontmatter receives a compact implementation-time summary for discovery, such as whether the feature declares required user gates and whether any are pending.
- The fleet ledger records gate events and approval evidence once implementation exists.
- `exec/state.md`, `exec/state.html`, and `exec/work-index.md` derive pending-gate displays from validation/frontmatter/ledger state.
- Do not add `gates.md` in v1. Reconsider only if validation files become unreadable after one sprint of use.

Why this matters: A new `gates.md` creates another file to keep consistent during every feature. The framework already treats `validation.md` as the pre-implementation contract, so user gates belong there until there is evidence that the contract is overloaded.

Answer: Adopt the recommendation. No new `gates.md` is in F-19 scope unless F-19 records an explicit implementation blocker and routes it back through Architect review.

Status: CLOSED.

---

## Q-C: Approval Evidence

Question: What counts as accepted evidence for a user gate?

Recommended answer: Accept evidence that is durable, attributable, and reviewable:

- Verbatim owner quote captured in a committed artifact.
- EM-synthesized decision only when it cites the original owner quote, issue comment, or committed source.
- ADR status change to accepted with date and owner evidence.
- Commit stamp that records the approval evidence in a committed artifact.
- GitHub or ADO issue/PR comment that is referenced by stable URL or issue ID.
- CLI gate record once F-19 implements the gate event path.

Do not accept inferred approval from green tests, agent confidence, silence, task completion, or a generated dashboard state.

Why this matters: Sprint 7 and Sprint 8 both showed that approval can become ambiguous when agents treat procedural progress as evidence. Gates need proof, not vibes.

Answer: Adopt the recommendation. The evidence taxonomy is codified as R3 / AC-3 and validation V-3.

Status: CLOSED.

---

## Q-D: Dashboard And State Surface

Question: How should pending gates appear in `exec/state.md`, `exec/state.html`, and `exec/work-index.md`?

Recommended answer: Surface user gates as a first-order executive signal, not as buried validation detail:

- `exec/state.md` should show a compact "Pending User Gates" section with feature, gate ID, blocking scope, required evidence, and next owner action.
- `exec/state.html` should show the same data in the dashboard with blocked gates visually distinct from informational gates.
- `exec/work-index.md` should list pending gates per active feature so Principals can run pre-work checks before starting adjacent work.
- Generated surfaces are read-only derivatives. They do not constitute approval evidence by themselves.

Why this matters: The EM and Principals need to see before starting work whether a gate blocks implementation, close, push, or PI closure. Hidden gates create false DONE states.

Answer: Adopt the recommendation. F-19 should extend `state_builder.py` only after the validation/frontmatter contract is in place.

Status: CLOSED.

---

## Q-E: Failure Semantics

Question: What does a missing required user gate block?

Recommended answer: A missing required user gate blocks the narrowest downstream transition that would make the decision irreversible or misleading, and it must also block any close artifact that would claim the blocked transition is done.

Default blocking scopes:

- `clarify-close`: blocks CLARIFY close and SPEC finalization.
- `adr-dependent-edit`: blocks the edit that depends on the ADR and blocks feature close if the edit is required.
- `constitution-edit`: blocks the constitution edit and any DONE claim relying on it.
- `external-write`: blocks live write/apply/push/deploy actions; dry-run remains allowed.
- `model-upgrade`: blocks model assignment changes and protocol close.
- `feature-close`: blocks feature DONE.
- `sprint-close`: blocks sprint close.
- `push`: blocks push approval.
- `pi-close`: blocks PI close.

Why this matters: Blocking everything for every gate is too heavy, but allowing a feature to close while a required gate is missing repeats the no-silent-deferral failure mode.

Answer: Adopt the recommendation. Missing REQUIRED gates cannot be silently deferred. If a required gate is unavailable, the feature or sprint stops as OWNER-ATTENTION with the unchecked gate visible.

Status: CLOSED.

---

## Clarify Close

- Q-A through Q-E are CLOSED.
- F-16 does not edit constitution files, create ADRs, change CLI behavior, touch external services, or regenerate executive surfaces.
- F-19 implementation may require an ADR if it changes ledger schema or amends constitution wording. Without explicit owner approval, those tasks must stop as OWNER-ATTENTION rather than marking SDD-023 DONE.
- SDD-021 and SDD-025 should reference the gate vocabulary defined here: gate ID, gate type, blocking scope, evidence type, evidence reference, approver, status, and next action.
