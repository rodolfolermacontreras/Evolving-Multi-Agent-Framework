---
id: SDD-20260626TWOTIEREM-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-two-tier-executive-manager
---

# CLARIFY: SDD-043 -- Two-tier Executive Manager (Sprint EM agent)

- Date: 2026-06-26
- Authors: Principal Product Manager + Principal Architect (jointly), at F-34
- Status: **DONE** -- Q-A through Q-C answered; ADR-020 authored (Proposed); Q-B constitution finding recorded
- Spec ID: SDD-043
- Sprint: PI-7 / Sprint 1 (= overall Sprint 14), feature slot F-34 (CLARIFY + ADR + SPEC + PLAN + TASKS; IMPLEMENT is F-36)
- Decision source: BACKLOG SDD-043 row (filed 2026-06-26) + [`SPRINT-14-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-14-KICKOFF.prompt.md) section 3 (Q-A..Q-C) + owner approval to start Sprint 14 (2026-06-26, "lets go").

---

## Ground Rules

- This file is the source of truth for SDD-043 design decisions.
- F-34 is design-only. **No implementation, no new agent file, no kickoff-template edit, no constitution edit, no commit, no push** is authorized by this file. Implementation is F-36.
- The Sprint EM agent IDENTITY file is created in F-36; the SPRINT-NN kickoff-template activation lands in F-36. This CLARIFY only DESIGNS them.
- Article II (single human entry point), Article VIII (constitution edits require an ADR + owner approval), and Article IX/decision-policy authority levels remain binding.

---

## Decision Summary (Q-A..Q-C)

| Q | Topic | Locked Decision | Level |
|---|-------|-----------------|-------|
| Q-A | Sprint EM name + tier | Name: "Sprint Executive Manager". Tier: a sprint-scoped orchestrator UNDER the project EM, NOT a new principal tier. Constraints live in the agent IDENTITY file. | Level-1 |
| Q-B | Article II constitution impact | **NO constitution edit required.** The project EM remains the single human entry point per Article II; the Sprint EM is a delegated, sprint-scoped orchestrator beneath it that never becomes the human's project-level entry point. Achieve the two-tier model via ADR-020 + new agent file + `_SHARED_ONBOARDING.md` activation block. | Level-1 (no Level-2 trigger) |
| Q-C | Kickoff-template activation | The shared kickoff template (`_SHARED_ONBOARDING.md`) activates the Sprint EM going FORWARD; do NOT retrofit already-shipped kickoff prompts. | Level-1 |

---

### Q-A: Sprint EM name and tier

**Context.** SDD-043 introduces a sprint-scoped Executive Manager. The open question is its name, its place in the role model, and where its behavioral constraints are encoded.

**Options.**

- Option A: Name "Sprint Executive Manager"; a sprint-scoped orchestrator UNDER the project EM (a delegated role, not a new principal). Identity-level constraints in the agent file.
- Option B: A new fifth "principal" tier peer to PM / Architect / SW Dev.
- Option C: No new agent; keep relying on per-sprint kickoff prose to scope the project EM.

**PM recommendation:** Option A. The role is a delegated single-sprint orchestrator, not a peer principal and not a human entry point.

**Architect recommendation:** Option A. A new principal tier (B) over-models the role; prose-only scoping (C) is the failure mode SDD-043 exists to fix (scope drift + authority creep observed at the Sprint 12 close). The durable place for a behavioral constraint is the agent identity file, loaded every session.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Name the agent "Sprint Executive Manager". It is a sprint-scoped orchestrator under the project EM -- not a new principal tier and not a human entry point. Its constraints (scope lock to the sprint's features; route to PM/Architect/SW Dev; report up at close; cannot create sprints/PIs, may only SUGGEST; Level 0 only; defers project-wide human Q&A to the project EM) live in the agent IDENTITY file created in F-36.
**Rationale:** Identity-level constraints are durable and reliable; a kickoff prompt is per-sprint and drifts. This matches the owner's BACKLOG SDD-043 framing ("Constraints live in the agent IDENTITY file, not only the kickoff prompt").

---

### Q-B: Article II constitution impact

**Context.** Article II of `constitution/principles.md` is titled "Single Human Entry Point" and reads: "The Principal Executive Manager is the human's default entry point to the fleet... Documented in ADR-0004." Introducing a second agent that carries "Executive Manager" in its name raises the question of whether Article II must change. A constitution edit is Level-2 (ADR + recorded owner approval + version bump), so this must be resolved before any implementation.

**Options.**

- Option A: No constitution edit. Achieve the two-tier model via ADR-020 + the new agent file + the kickoff-template change; state explicitly (in the ADR and the agent file) that the project EM remains the single human entry point.
- Option B: Amend Article II to name the two-tier model (Level-2: ADR + recorded owner approval + MINOR version bump, ADR-018 style).

**PM recommendation:** Option A. Article II governs the *human* entry point; the human still talks to one agent (the project EM) first. The Sprint EM is internal orchestration, not a competing entry point.

**Architect recommendation:** Option A. Article II is about the human entry point, which remains the single project EM. The Sprint EM is a delegated, sprint-scoped orchestrator that operates inside an already context-isolated sprint working session (Article VII) and reports up; it never becomes the human's project-level entry point. The two-tier model is therefore *additive* and does not contradict Article II. The shared "Executive Manager" name is disambiguated by stating, in the agent file and ADR-020, that the project EM is the single human entry point -- no constitution wording needs to change.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision (Q-B FINDING):** **NO** -- Article II does NOT require a constitution edit. One-sentence rationale: the project Executive Manager remains the single human entry point per Article II; the Sprint EM is a delegated, sprint-scoped orchestrator beneath it that reports up and never becomes the human's project-level entry point, so the two-tier model is additive and non-contradictory -- achieved via ADR-020 + the new agent file + the `_SHARED_ONBOARDING.md` activation block.
**Not OWNER-ATTENTION:** because no contradiction exists, this is NOT a Level-2 constitution blocker. An OPTIONAL future clarification of Article II to *name* the two-tier model (a MINOR bump in the ADR-018 style) remains available at owner discretion as a separate, non-blocking item; it is explicitly out of SDD-043 scope.

---

### Q-C: Kickoff-template activation

**Context.** The Sprint EM must be activated when a sprint starts. The shared kickoff boilerplate that every `SPRINT-##-KICKOFF.prompt.md` loads end-to-end as step 1 is `spec-driven-development/feature-prompts/_SHARED_ONBOARDING.md` (this is the de facto "SPRINT-NN kickoff template"; there is no separate template file today). The open question is which surface activates the Sprint EM and whether shipped prompts are retrofitted.

**Options.**

- Option A: Add a Sprint-EM activation block to `_SHARED_ONBOARDING.md`; applies to FUTURE sprints. Do not rewrite already-shipped kickoff prompts.
- Option B: Retrofit every existing `SPRINT-##-KICKOFF.prompt.md` to invoke the Sprint EM.

**PM recommendation:** Option A. Forward-only; do not churn historical prompts.

**Architect recommendation:** Option A. `_SHARED_ONBOARDING.md` is the single inherited surface, so one edit there activates the Sprint EM for all future sprints. Retrofitting shipped prompts (B) is unnecessary churn and risks diffing closed sprint history.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** The SPRINT-NN kickoff template (`_SHARED_ONBOARDING.md`) activates the Sprint EM going forward. Already-shipped kickoff prompts are NOT retrofitted. The actual edit lands in F-36; this CLARIFY only records the target surface and the forward-only rule.
**Rationale:** One inherited surface, one edit, forward-only -- consistent with how ADR-018 treated `_SHARED_ONBOARDING.md` as the shared template.

---

## Open Questions

- None blocking. Q-A..Q-C answered; Q-B finding recorded (NO constitution edit).
- **ADR required: yes** -- ADR-020 (Proposed), the two-tier EM model.

## Out of Scope

- Creating the Sprint EM agent file (F-36).
- Editing `_SHARED_ONBOARDING.md` (F-36).
- Any `constitution/**` edit (Q-B finding: not required).
- SDD-044 plain-language comms (paired but separate spec dir).
- SDD-045 Detach epic (F-35).
