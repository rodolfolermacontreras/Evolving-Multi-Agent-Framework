---
id: SDD-20260608PRESSUREDEFENSE-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-stakeholder-pressure-defense
---

# Task List: Stakeholder-Pressure Defense Pattern (SDD-025)

- Spec Reference: `./spec.md`
- Plan Reference: `./plan.md`
- Validation Reference: `./validation.md`
- Sprint: PI-5 / Sprint 5 (= overall Sprint 9)
- Owner: Principal Software Developer
- Test baseline: >= 331 passed, 2 skipped
- Lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

---

## Batch Overview

| Batch | Tasks | Mode | Notes |
|-------|-------|------|-------|
| B1 | T-025-01 -> T-025-03 | Sequential | Primary skill shape, gate reuse, Friction Analysis routing. |
| B2 | T-025-04 -> T-025-05 | Sequential | Principal routing and executive-register response pattern. |
| B3 | T-025-06 -> T-025-07 | Sequential | Self-review promotion and response template. |
| B4 | T-025-08 | Sequential close-out | Approval trigger check, lint, optional tests, validation close. |

---

## Task T-025-01: Create pressure-defense skill and trigger taxonomy

**Story**: [R1] Detect stakeholder-pressure patterns consistently
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`
**Files Blocked**: `spec-driven-development/constitution/**`, `spec-driven-development/templates/level-2-decision.md`
**Depends on**: SDD-023 implementation artifact shape and SDD-021 self-review skill, if F-19 implements Sprint 9 sequentially

### Description

Create the operational skill with valid frontmatter and a trigger taxonomy covering speed over validation, skipping owner approval, reducing scope without traceability, pushing before approval, accepting unverified external claims, novelty/prestige pressure, external-write pressure, and silent validation exceptions.

### Acceptance Criteria

- [ ] Skill frontmatter is valid and names `stakeholder-pressure-defense`.
- [ ] Every trigger from R1 appears with at least one concrete example.
- [ ] The skill states it defends validation, approval, traceability, evidence, and irreversible-change discipline.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'speed-over-validation|skip-owner-approval|unverified-external-claim|silent-exception-pressure'
```

---

## Task T-025-02: Add SDD-023 gate-pressure classification

**Story**: [R2, R7] Express approval and scope pressure with existing gate vocabulary
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`
**Files Blocked**: NONE
**Depends on**: T-025-01

### Description

Document how pressure cases map to SDD-023 fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`. Include scope-reduction handling that requires traceable spec/plan/tasks/validation updates before changed scope is claimed.

### Acceptance Criteria

- [ ] Skill cites all SDD-023 fields.
- [ ] Scope-reduction pressure routes to PM + Architect and requires artifact updates.
- [ ] Skill does not define a competing gate schema.

### Verification

```powershell
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'gate_id|blocking_scope|required-validation-exception|scope-reduction'
```

---

## Task T-025-03: Add SDD-014 Friction Analysis routing

**Story**: [R3, R8] Route Level-2 and irreversible shortcut pressure through the existing brief
**Type**: [S] sequential
**Execution**: [AFK] autonomous unless owner approval trigger occurs
**Size**: S
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`
**Files Blocked**: `spec-driven-development/templates/level-2-decision.md`, `spec-driven-development/constitution/**`, `spec-driven-development/docs/ADR/**`
**Depends on**: T-025-02

### Description

Add explicit routing to `spec-driven-development/templates/level-2-decision.md` for Level-2 pressure, model/tool/platform novelty pressure with irreversible impact, schema migration pressure, new dependency pressure, production/push behavior pressure, M365 permission pressure, privacy-sensitive logging pressure, and external-write behavior pressure.

### Acceptance Criteria

- [ ] Skill names `spec-driven-development/templates/level-2-decision.md` as the mandatory Level-2 brief.
- [ ] Skill may cite `spec-driven-development/templates/level-2-decision-EXAMPLE.md` as a worked example.
- [ ] Skill states a response template does not replace Friction Analysis.
- [ ] Required validation exceptions remain gated by SDD-023 owner evidence.

### Verification

```powershell
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'level-2-decision.md|level-2-decision-EXAMPLE.md|Friction Analysis|required-validation-exception'
```

---

## Task T-025-04: Add Principal routing matrix

**Story**: [R4] Send pressure to the right Principal or owner
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`
**Files Blocked**: NONE
**Depends on**: T-025-03

### Description

Add routing rules for EM, PM, Architect, SW Dev, and owner. Route by the decision surface being pressured: stakeholder synthesis, product scope, architecture/Level-2, implementation/test/push readiness, or human approval.

### Acceptance Criteria

- [ ] Routing matrix includes EM, PM, Architect, SW Dev, and owner.
- [ ] Level-2 and disputed cross-principal decisions route to owner.
- [ ] Push readiness and external-write execution safety route through SW Dev plus owner where required.

### Verification

```powershell
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'Executive Manager|Product Manager|Architect|Software Developer|owner'
```

---

## Task T-025-05: Add executive-register response pattern

**Story**: [R5, R6] Defend quality without sounding obstructive
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`
**Files Blocked**: NONE
**Depends on**: T-025-04

### Description

Add copy-ready response guidance that acknowledges urgency, states the blocked transition or evidence gap, explains risk, offers options, recommends one path, and rejects invalid approval evidence such as tests, silence, dashboards, elapsed time, or agent confidence.

### Acceptance Criteria

- [ ] Response pattern contains every step from `spec.md`.
- [ ] Guidance rejects invalid approval evidence.
- [ ] At least one example response is included or explicitly deferred to the response template task.

### Verification

```powershell
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'acknowledge|missing evidence|recommend|agent confidence|generated executive surfaces'
```

---

## Task T-025-06: Add SDD-021 self-review promotion guidance

**Story**: [R9] Capture repeated pressure lessons without direct self-modification
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: pending
**Files**: `.github/skills/operational/stakeholder-pressure-defense/SKILL.md`, `.github/skills/operational/session-self-review/SKILL.md`
**Files Blocked**: `.github/agents/**`, `spec-driven-development/constitution/**`
**Depends on**: T-025-05 and SDD-021 implementation artifact if available

### Description

Document that repeated pressure patterns, routing confusion, or pressure-defense misses route through SDD-021 self-review promotion targets: `gate-friction`, `lesson-candidate`, `backlog-candidate`, or `agent-skill-delta`. Extend the self-review skill only if F-19 has already created it and a small cross-reference is needed.

### Acceptance Criteria

- [ ] Pressure-defense skill names SDD-021 promotion targets.
- [ ] Proposed agent/skill/prompt/template changes route through `/evolve` or approved tasks.
- [ ] No direct self-modification is authorized.

### Verification

```powershell
Select-String -Path .github/skills/operational/stakeholder-pressure-defense/SKILL.md -Pattern 'gate-friction|lesson-candidate|backlog-candidate|agent-skill-delta|evolve'
```

---

## Task T-025-07: Create stakeholder-pressure response template

**Story**: [R3, R5] Provide a communication wrapper without replacing Friction Analysis
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: pending
**Files**: `spec-driven-development/templates/stakeholder-pressure-response.md`
**Files Blocked**: `spec-driven-development/templates/level-2-decision.md`
**Depends on**: T-025-05

### Description

Create a template with fields for request summary, trigger classification, affected gate or requirement, missing evidence, risk, options, recommendation, next action, and Friction Analysis handoff when Level-2 pressure exists.

### Acceptance Criteria

- [ ] Template is communication-only and says Level-2 cases use `spec-driven-development/templates/level-2-decision.md`.
- [ ] Template supports the executive-register response pattern.
- [ ] Template has a compact response checklist.

### Verification

```powershell
Select-String -Path spec-driven-development/templates/stakeholder-pressure-response.md -Pattern 'level-2-decision.md|missing evidence|recommendation|next action'
```

---

## Task T-025-08: Close validation and regression checks

**Story**: [R10, R11] No silent deferral, no approval bypass, no regressions
**Type**: [S] sequential
**Execution**: [AFK] autonomous with HITL stop if approval trigger occurs
**Size**: S
**Status**: pending
**Files**: `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/validation.md`, `spec-driven-development/specs/2026-06-08-stakeholder-pressure-defense/tasks.md`
**Files Blocked**: `spec-driven-development/constitution/**`, `spec-driven-development/ledger/**`, dependency manifests, external service configuration
**Depends on**: T-025-06, T-025-07

### Description

Before closeout, verify whether implementation introduced a constitution edit, ledger schema migration, new dependency, M365 permission change, production-branch impact, external write behavior change, required-validation exception, or SDD-014 template edit. If yes, stop for owner approval and the correct ADR/Friction Analysis path. Run schema lint and full pytest if executable code changed. Check V-1 through V-13 only when evidence exists.

### Acceptance Criteria

- [ ] `GATE-025-001`, `GATE-025-002`, and `GATE-025-003` are approved or marked not-triggered with evidence.
- [ ] Manual checks M-1 through M-3 are addressed truthfully.
- [ ] `python spec-driven-development/cli/schema_lint.py` exits 0.
- [ ] Full pytest is run when executable code changes, or docs/skill/template-only rationale is recorded.
- [ ] Every REQUIRED V-item is checked with evidence, or the feature is not marked DONE.
- [ ] No REQUIRED item is silently deferred.

### Verification

```powershell
git diff --name-only HEAD
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```

---

## Traceability Summary

| Task | Requirements | Validation |
|------|--------------|------------|
| T-025-01 | R1 | V-1 |
| T-025-02 | R2, R7 | V-2, V-7 |
| T-025-03 | R3, R8 | V-3, V-8 |
| T-025-04 | R4 | V-4 |
| T-025-05 | R5, R6 | V-5, V-6 |
| T-025-06 | R9 | V-9 |
| T-025-07 | R3, R5 | V-3, V-5 |
| T-025-08 | R10, R11 | V-10, V-11, V-12, V-13, M-1, M-2, M-3 |