---
id: ADR-020
type: spec
status: draft
owner: principal-architect
updated: 2026-06-26
feature: SDD-043
---

# ADR-020: Two-tier Executive Manager -- a sprint-scoped Sprint EM beneath the project EM

- Date: 2026-06-26
- Status: **Accepted** (owner ratified at the Sprint 14 close gate, 2026-06-26)
- Authors: Principal Architect + Principal Product Manager (F-34 design slot, PI-7 Sprint 1)
- Feature: SDD-043 (two-tier Executive Manager)

> **Frontmatter note (same convention as ADR-018):** the schema-lint frontmatter `status` enum has no `accepted` value, so `status: draft` is retained as the schema-lint carrier. The body Status above is the authoritative ADR lifecycle state: **Accepted** (owner ratified 2026-06-26 at the Sprint 14 close). This ADR was design-only at authoring (F-34); the Sprint EM agent file and the onboarding activation block landed in implementation (F-36).

---

## Context

Today a single-sprint working session reuses the project Executive Manager identity (`.github/agents/principal-executive-manager.agent.md`). That identity is built for project-wide, cross-PI awareness: it routes ad-hoc human questions across the whole backlog, tracks every in-flight feature, and coordinates ceremonies at the project level. When that same identity drives one sprint, three problems appear:

1. **Scope drift.** A sprint session inherits project-wide framing and can wander beyond the sprint's own features -- commenting on, re-prioritizing, or starting work outside the sprint scope.
2. **Authority creep.** Nothing in the identity stops a single-sprint session from inventing the next sprint or PI, authoring a future kickoff, or making PI-level commitments. Sprint 12's close (2026-06-25) had to be corrected by hand: the this-sprint EM was explicitly told it was "not the Highest Executive" and must NOT author the next sprint kickoff. That correction lived only in a kickoff prompt, so it is not reliably enforced.
3. **Reliance on prompts, not identity.** The only place the "this is a single sprint, do not create the next one" rule exists is the kickoff prompt text. Prompts are per-sprint and easy to drift from; an agent identity file is loaded every session and is the durable place for a behavioral constraint.

The owner's #1 PI-7 item (BACKLOG SDD-043, filed 2026-06-26) is to make the two-tier model a first-class, identity-level construct: a sprint-scoped "Sprint Executive Manager" that runs ONE sprint, routes feature work to the four Principals, reports UP to the project EM at sprint close, and CANNOT create sprints or PIs (it may only SUGGEST them upward).

A design question must be resolved first: does the two-tier model require editing Article II ("Single Human Entry Point") of `constitution/principles.md`? Article II reads: "The Principal Executive Manager is the human's default entry point to the fleet. The human talks to one agent first... Documented in ADR-0004." Introducing a second agent that carries "Executive Manager" in its name could be read as conflicting with "single entry point."

## Decision

1. **Adopt a two-tier Executive Manager model.** There are two distinct EM roles, related by delegation, not duplication:
   - **Project Executive Manager (existing, unchanged):** the single human entry point for the whole project. Owns ad-hoc human Q&A routing, project-wide status, escalation, and big-picture awareness across all PIs and sprints. This is the agent the human talks to first, by default, for anything project-level. Article II governs this role and is preserved unchanged.
   - **Sprint Executive Manager (new, sprint-scoped):** a delegated orchestrator that runs exactly ONE sprint. It is activated by that sprint's kickoff, is scoped strictly to that sprint's features, routes feature work to PM / Architect / SW Dev, and reports UP to the project EM at sprint close. It is **not** a human entry point and **not** a new "principal" tier.

2. **The Sprint EM constraints live in the agent IDENTITY file**, not only in the kickoff prompt. The new `.github/agents` Sprint EM agent file (created in F-36) MUST encode, at identity level:
   - **Scope lock:** operate only within the named sprint's features; do not comment on, re-prioritize, or start work outside the sprint.
   - **No sprint/PI creation:** the Sprint EM CANNOT create a sprint or a PI, author the next sprint's kickoff, or make PI-level commitments. It may only SUGGEST the next sprint/PI to the project EM (a recommendation, never an action).
   - **Report up at close:** at sprint close it produces a close summary and hands up to the project EM; the project EM (with the owner) owns what happens next.
   - **Not the human entry point:** the Sprint EM explicitly defers project-wide human Q&A to the project EM; it does not present itself as the single entry point.
   - **Level 0 only:** like the project EM, the Sprint EM makes no Level 1 or Level 2 decisions; it routes, summarizes, and surfaces.

3. **Activation lives in the kickoff template, applied going forward.** The shared kickoff boilerplate (`spec-driven-development/feature-prompts/_SHARED_ONBOARDING.md`, the file every `SPRINT-##-KICKOFF.prompt.md` loads "end to end" as step 1) gains a Sprint-EM activation block so future sprints run under the Sprint EM rather than the project EM. Already-shipped kickoff prompts are NOT retrofitted (forward-only; no rewrite of historical prompts). The template edit lands in F-36.

4. **No constitution edit is required (Q-B finding: NO).** Article II governs the *human entry point*, which remains the single project EM. The Sprint EM is a delegated, sprint-scoped orchestrator beneath the project EM; it never becomes the human's project-level entry point, so the two-tier model is additive and does not contradict Article II. The model is achieved entirely via this ADR + the new agent identity file + the `_SHARED_ONBOARDING.md` activation block. The new agent file and the ADR state explicitly that the project EM remains the single human entry point, removing any ambiguity from the shared "Executive Manager" name without amending the constitution.

## Consequences

- **Positive:**
  - The scope and authority limits that previously lived only in kickoff prose become a durable, every-session identity constraint -- the Sprint 12 hand-correction is no longer needed.
  - The project EM stays the single human entry point (Article II honored), so the human's mental model ("I talk to one agent") is unchanged.
  - Sprint sessions get a right-sized identity (one sprint, its features, report up) instead of inheriting project-wide framing.
- **Negative / cost:**
  - One more agent file to maintain and keep consistent with the project EM identity.
  - The kickoff template gains an activation block, so the project EM vs Sprint EM distinction must be taught once.
- **Neutral:**
  - No code, no schema, no dependency, no ledger change. Pure governance/identity design; implementation is docs/agent/skill text in F-36.
  - ADR lifecycle is normal Level-1: Proposed here, Accepted at the Sprint 14 close gate with recorded owner ratification.

## Alternatives Considered

- **Alternative A -- keep the single project EM and rely on kickoff prompts for sprint scoping (status quo).** Rejected: this is exactly the failure mode (scope drift + authority creep) the owner's #1 item asks to fix; prompt-only constraints proved unreliable at the Sprint 12 close.
- **Alternative B -- make the Sprint EM a new "principal" tier.** Rejected: it is not a peer of the four Principals and not a human entry point; a new tier would over-complicate the role model. The Sprint EM is a delegated orchestrator under the project EM, not a fifth principal.
- **Alternative C -- amend Article II to name the two-tier model.** Deferred, not adopted. Per the Q-B finding, Article II is not contradicted, so a Level-2 constitution edit is not required to ship SDD-043. An OPTIONAL future clarification of Article II to *name* the two-tier model (a MINOR bump in the ADR-018 style) remains available at owner discretion as a separate, non-blocking item; it is explicitly out of SDD-043's scope and is not an OWNER-ATTENTION blocker.
