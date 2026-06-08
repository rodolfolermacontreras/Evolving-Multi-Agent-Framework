---
id: SDD-20260608PRESSUREDEFENSE-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-stakeholder-pressure-defense
---

# CLARIFY: Stakeholder-Pressure Defense Pattern (SDD-025)

- Date: 2026-06-08
- Owners: Principal Product Manager + Principal Architect
- Sprint: PI-5 Sprint 5 (= overall Sprint 9)
- Source item: SDD-025 -- Stakeholder-pressure defense pattern invoking SDD-014 Friction Analysis template
- Status: CLOSED for SPEC/PLAN/TASKS

---

## Context Verified

- Sprint 8 ratification is recorded in commit `8b7d5b9` with owner evidence: "yes Sprint 8 was ratified, we are good".
- Sprint 9 F-16 / SDD-023 is complete in commit `6345366` and defines the reusable User Gate vocabulary.
- Sprint 9 F-17 / SDD-021 is complete in commit `82689d3` and defines the self-review promotion path for reusable process lessons, gate friction, and agent/skill deltas.
- SDD-014 shipped in PI-4 Sprint 3 commit `85b39be`. The current Friction Analysis template is `spec-driven-development/templates/level-2-decision.md`; the worked example is `spec-driven-development/templates/level-2-decision-EXAMPLE.md`.
- This F-18 pass is design-only. It does not edit `.github/skills/**`, `.github/agents/**`, `.github/prompts/**`, `constitution/**`, `cli/**`, generated executive state, or external systems.

---

## Q-J: Trigger Examples

Question: Which pressure patterns matter most: speed over validation, skipping owner approval, reducing scope without traceability, pushing before approval, accepting unverified external claims, or other high-risk patterns?

Recommended answer: Treat stakeholder pressure as a pattern when a request asks an agent or Principal to proceed while a required quality, traceability, evidence, or approval condition is missing. The v1 trigger list MUST include:

- Speed over validation: pressure to mark DONE, merge, close, or hand off without running required lint/tests or checking REQUIRED validation items.
- Skipping owner approval: pressure to bypass owner approval for Level-2 decisions, constitution edits, model upgrades, external writes, production/push behavior, or validation exceptions.
- Reducing scope without traceability: pressure to drop committed requirements, acceptance criteria, or validation items without a spec/task/validation update.
- Pushing before approval: pressure to push, close a sprint, or close a PI while `push-approval`, `sprint-close`, or `pi-close` gates lack evidence.
- Accepting unverified external claims: pressure to quote numbers, stakeholder claims, external system state, or production impact without durable evidence.
- Novelty or prestige pressure: pressure to adopt a newer model, tool, cloud path, or agent pattern because it sounds current rather than because Friction Analysis shows net benefit.
- External-write pressure: pressure to write to GitHub, ADO, M365, cloud resources, or other systems without the correct dry-run, token, approval, or evidence path.
- Silent exception pressure: pressure to treat a failing REQUIRED item as optional, already handled, or not applicable without approval evidence.

Why this matters: The defense pattern is not only for model or tool requests. It protects validation discipline, approval gates, stakeholder trust, and external-write safety whenever urgency tries to outrun evidence.

Answer: Adopt the recommendation. F-19 must implement the full trigger taxonomy and keep it extensible without weakening any REQUIRED gate.

Status: CLOSED.

---

## Q-K: Friction Analysis Integration

Question: Does the playbook instantiate `templates/level-2-decision.md`, add a new defense template, or both?

Recommended answer: Use both, with clear separation of authority:

- For Level-2 pressure or irreversible shortcuts, the playbook MUST instantiate the existing SDD-014 Friction Analysis brief at `spec-driven-development/templates/level-2-decision.md` before implementation or approval work proceeds.
- For non-Level-2 stakeholder responses, add a lightweight stakeholder-pressure response template that formats the answer at executive register: request summary, gate or evidence gap, risk, options, recommended next action, and owner decision needed if any.
- The new response template MUST NOT replace the SDD-014 brief. It is a communication wrapper and triage surface only.
- The playbook SHOULD cite `spec-driven-development/templates/level-2-decision-EXAMPLE.md` as an example when the pressure involves a high-risk architectural or governance change.

Why this matters: A one-page stakeholder response helps EM communicate without sounding obstructive, but Level-2 decisions already have a binding constitutional path. Creating a second Level-2 template would fragment governance.

Answer: Adopt the recommendation. F-19 should create the playbook/skill and a response template, while Level-2 cases must use the existing SDD-014 `level-2-decision.md` template.

Status: CLOSED.

---

## Q-L: Principal Routing

Question: Which cases route to EM, PM, Architect, SW Dev, or owner?

Recommended answer: Route by the decision being pressured, not by who raised the pressure:

- Executive Manager: intake, stakeholder-facing synthesis, tone calibration, status framing, and escalation routing.
- Product Manager: scope reductions, priority tradeoffs, backlog movement, acceptance criteria changes, sprint/PI commitment impacts.
- Principal Architect: Level-2 classification, Friction Analysis, architecture/ADR implications, constitution-edit implications, model/tool/platform novelty pressure.
- Principal Software Developer: implementation sequencing, test/lint feasibility, code-quality gate pressure, push readiness, external-write execution safety.
- Owner: Level-2 approvals, push approval, PI close, sprint-close approval when not delegated, validation exceptions, and any disputed cross-principal decision.

Why this matters: Pressure often arrives as an implementation urgency, but the real decision may be product scope, architecture risk, or owner approval. Routing by pressured decision keeps each Principal in its lane.

Answer: Adopt the recommendation. The playbook must include a routing matrix and require owner escalation for Level-2 or disputed decisions.

Status: CLOSED.

---

## Q-M: Tone And Evidence

Question: What is the expected executive-register response when defending quality without sounding obstructive?

Recommended answer: The response should acknowledge the stakeholder's goal, state the missing gate or evidence plainly, offer a concrete path, and preserve momentum. It should avoid defensive language, bureaucratic labels, or implying the stakeholder is wrong.

Required response pattern:

1. Acknowledge the goal or urgency.
2. Name the blocked transition using SDD-023 vocabulary when a gate is involved.
3. Name the missing evidence or validation result.
4. State the risk of proceeding without it in business or delivery terms.
5. Offer two or three options: fastest compliant path, safer full path, or explicit owner decision path.
6. Recommend one option and identify the next action.
7. If Level-2 pressure exists, route to `spec-driven-development/templates/level-2-decision.md` before any implementation or irreversible action.

Why this matters: The framework should defend quality as delivery insurance, not as process theater. A useful answer helps the stakeholder get to a decision faster while preserving evidence and approval discipline.

Answer: Adopt the recommendation. F-19 must include copy-ready response guidance and examples that defend gates without sounding obstructive.

Status: CLOSED.

---

## Clarify Close

- Q-J through Q-M are CLOSED.
- SDD-025 reuses SDD-023 gate vocabulary for pressured approvals, missing evidence, blocked transitions, and next actions.
- SDD-025 cites SDD-014 through `spec-driven-development/templates/level-2-decision.md` and `spec-driven-development/templates/level-2-decision-EXAMPLE.md`.
- SDD-025 reuses SDD-021 for promoting repeated pressure lessons into self-review, lesson-capture, `/evolve`, or PM triage.
- F-18 does not perform constitution edits, ADR creation, new dependencies, schema migrations, M365 permission changes, production-branch changes, external writes, or agent/skill/template implementation.
- F-19 implementation must stop for owner approval if it discovers any Level-2 trigger not already approved.