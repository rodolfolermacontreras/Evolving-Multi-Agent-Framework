---
id: SDD-20260608SELFREVIEW-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-end-of-session-self-review
---

# Task List: End-of-Session Self-Review Loop (SDD-021)

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
| B1 | T-021-01 -> T-021-03 | Sequential | Primary skill shape and privacy boundary. |
| B2 | T-021-04 -> T-021-05 | Sequential | Promotion and sprint-close integration. |
| B3 | T-021-06 | HITL-sensitive | Stop for approval-required triggers. |
| B4 | T-021-07 | Sequential close-out | Lint, optional tests, validation close. |

---

## Task T-021-01: Create session-self-review skill

**Story**: [R1] Trigger self-review at the right lifecycle points
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `.github/skills/operational/session-self-review/SKILL.md`
**Files Blocked**: `spec-driven-development/constitution/**`, `spec-driven-development/ledger/**`
**Depends on**: NONE

### Description

Create the operational skill with valid frontmatter and clear trigger conditions: feature handoff, feature DONE, feature BLOCKED, OWNER-ATTENTION, sprint close, friction-detected, and manual request.

### Acceptance Criteria

- [ ] Skill frontmatter is valid and names `session-self-review`.
- [ ] Required and optional triggers from R1 are listed.
- [ ] The skill states it is advisory and does not directly modify durable framework files.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
```

---

## Task T-021-02: Define record shape and gate findings

**Story**: [R2, R6, R7] Emit structured output and reuse SDD-023 gate vocabulary
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `.github/skills/operational/session-self-review/SKILL.md`
**Files Blocked**: NONE
**Depends on**: T-021-01

### Description

Document the self-review record fields and outcome classifications. Gate-related findings must cite SDD-023 fields: `gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, and `next_action`.

### Acceptance Criteria

- [ ] Every required record field from `spec.md` appears in the skill.
- [ ] Outcome classes include `no-op`, `session-note`, `lesson-candidate`, `backlog-candidate`, `gate-friction`, and `agent-skill-delta`.
- [ ] Gate findings reuse SDD-023 fields and accepted evidence types.

### Verification

```powershell
Select-String -Path .github/skills/operational/session-self-review/SKILL.md -Pattern 'source_feature|gate_id|promotion_target|lesson-candidate'
```

---

## Task T-021-03: Document evidence and privacy boundaries

**Story**: [R3, R4] Run without raw transcript access or private data export
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `.github/skills/operational/session-self-review/SKILL.md`
**Files Blocked**: NONE
**Depends on**: T-021-02

### Description

List allowed evidence sources and explicitly state that raw transcripts are optional enrichment, not required input. Prohibit private transcript export, M365/WorkIQ access, and external system reads as mandatory evidence.

### Acceptance Criteria

- [ ] Artifact-based evidence sources are listed.
- [ ] Raw transcript access is optional only.
- [ ] Privacy-sensitive data copying is prohibited unless sanitized.

### Verification

```powershell
Select-String -Path .github/skills/operational/session-self-review/SKILL.md -Pattern 'transcript|privacy|M365|WorkIQ'
```

---

## Task T-021-04: Route durable learning through existing governance

**Story**: [R5, R7] Propose changes without silently applying them
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `.github/skills/operational/session-self-review/SKILL.md`, `.github/skills/operational/lesson-capture/SKILL.md`, `.github/prompts/evolve.prompt.md`
**Files Blocked**: `.github/agents/**`, `spec-driven-development/constitution/**`
**Depends on**: T-021-03

### Description

Ensure self-review directs durable framework changes to `lesson-capture`, `/evolve`, PM triage, `/constitution`, or an approved implementation task. Update lesson-capture or evolve wording only if needed and only in small additive text.

### Acceptance Criteria

- [ ] Self-review outputs use `lesson-candidate` for reusable framework changes.
- [ ] `/evolve` is named as the curation path for agent/skill/prompt/template deltas.
- [ ] No direct agent or skill mutation is authorized by the self-review skill.

### Verification

```powershell
Select-String -Path .github/skills/operational/session-self-review/SKILL.md,.github/prompts/evolve.prompt.md -Pattern 'evolve|lesson-capture|agent-skill-delta'
```

---

## Task T-021-05: Add sprint-close summary guidance

**Story**: [R8] Make sprint-level lessons visible
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/sprints/README.md`, `spec-driven-development/templates/review.md` or nearest existing review template
**Files Blocked**: NONE
**Depends on**: T-021-04

### Description

Add a compact instruction for sprint close or retro to summarize self-review findings or record `none`. If no stable template exists, document the choice in the validation closeout instead of inventing a new artifact shape.

### Acceptance Criteria

- [ ] Sprint close or retro has a self-review summary destination, or the task records why no stable target was modified.
- [ ] The guidance does not duplicate the whole self-review record.
- [ ] Findings intended for framework evolution still route to lessons and `/evolve`.

### Verification

```powershell
Select-String -Path spec-driven-development/sprints/README.md -Pattern 'self-review|lessons|evolve'
```

---

## Task T-021-06: Check approval-required triggers

**Story**: [R10] Stop before Level-2 or governance-sensitive changes
**Type**: [S] sequential, HITL-sensitive
**Execution**: [HITL] owner/Architect approval required if trigger occurs
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md`
**Files Blocked**: `spec-driven-development/constitution/**`, `spec-driven-development/ledger/**`, dependency manifests, external service configuration
**Depends on**: T-021-05

### Description

Before closeout, verify whether implementation introduced a constitution edit, ledger schema migration, new dependency, M365 permission change, production-branch impact, external write behavior change, or direct agent/skill mutation behavior. If yes, stop for owner approval and the correct ADR/Friction Analysis path.

### Acceptance Criteria

- [ ] `GATE-021-001` is approved or marked not-triggered with evidence.
- [ ] Manual checks M-1 through M-3 are addressed truthfully.
- [ ] No Level-2 change lands without owner approval.

### Verification

```powershell
git diff --name-only HEAD
```

---

## Task T-021-07: Close validation and regression checks

**Story**: [R9, R10] No silent deferral, no regressions
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-end-of-session-self-review/validation.md`, `spec-driven-development/specs/2026-06-08-end-of-session-self-review/tasks.md`
**Files Blocked**: NONE
**Depends on**: T-021-06

### Description

Run schema lint and any targeted checks. Run full pytest if executable code changed. Check V-1 through V-12 only when evidence exists. If any REQUIRED item cannot close, stop as OWNER-ATTENTION and leave it unchecked.

### Acceptance Criteria

- [ ] `python spec-driven-development/cli/schema_lint.py` exits 0.
- [ ] Full pytest is run when executable code changes, or docs/skill-only rationale is recorded.
- [ ] Every REQUIRED V-item is checked with evidence, or the feature is not marked DONE.
- [ ] No REQUIRED item is silently deferred.

### Verification

```powershell
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```

---

## Traceability Summary

| Task | Requirements | Validation |
|------|--------------|------------|
| T-021-01 | R1 | V-1 |
| T-021-02 | R2, R6, R7 | V-2, V-6, V-7 |
| T-021-03 | R3, R4 | V-3, V-4 |
| T-021-04 | R5, R7 | V-5, V-7 |
| T-021-05 | R8 | V-8 |
| T-021-06 | R10 | V-12, M-1, M-2, M-3 |
| T-021-07 | R9, R10 | V-9, V-10, V-11, V-12 |