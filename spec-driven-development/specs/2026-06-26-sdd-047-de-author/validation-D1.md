---
id: SDD-20260626DEAUTHOR-validation-d1
type: validation
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# VALIDATION: SDD-047 / D-1 -- wire-or-delete the 10 dead skills

- Per-item ID: D-1 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN D-1 Acceptance
- Lock statement: LOCKED at F-41. F-42 records the per-skill wire/delete decision and CHECKS with evidence.

## Per-skill disposition (decided at F-42 implement; recommendation recorded now)

| Skill | Recommended call | Rationale |
|-------|------------------|-----------|
| `tdd-gate` | WIRE (SW Dev review flow) | B-2 made it a real check; must be referenced |
| `diagnose` | WIRE (SW Dev / QA flow) | Real engineering value |
| `grill-with-docs` | WIRE (PM/Architect CLARIFY) or DELETE | Overlaps `grill-me`; confirm value |
| `host-integration-symlink` | WIRE (dev-env-manager / host-link) | Backs SDD-016 host-link |
| `lesson-capture` | WIRE (retro flow) or DELETE | Confirm vs existing retro |
| `respect-existing` | WIRE (implement flow) or DELETE | Brownfield guardrail |
| `session-self-review` | WIRE (handoff/close) or DELETE | Confirm vs handoff skill |
| `stakeholder-pressure-defense` | WIRE (EM/PM) or DELETE | Has its own spec; likely wire |
| `to-plan` | WIRE (Architect plan flow) | Lifecycle peer of to-spec/to-tasks |
| `weekly-status-report` | WIRE (EM) or DELETE | Confirm vs status flow |

## Required Items (Strict)

- [x] **R-1 (tdd-gate wired).** `tdd-gate` is referenced from the SW Dev review flow. Evidence: referenced in `principal-software-developer.agent.md` review flow and `implement.prompt.md`.
- [x] **R-2 (no orphan skills).** Every shipped skill is referenced by >=1 agent/prompt. Final disposition: ALL 10 candidate skills WIRED, 0 deleted; `roster/skills.json` unchanged. Evidence: orphan enumeration COUNT 0; `schema_lint --check-orphans` ORPHAN_EXIT=0.
- [x] **R-3 (lock-in rule).** A `schema_lint` rule fails when a shipped skill is referenced by zero agents/prompts; a test covers both an orphan (fails) and a referenced skill (passes). Evidence: `check_orphan_skills` + `--check-orphans` flag; `test_schema_lint.py::OrphanSkillRule` (unreferenced flagged, referenced-in-agent/prompt/instruction not flagged, domain exempt, real-repo zero) all pass.

## Manual Checks

- [x] **M-1.** Reviewer confirms each WIRE adds a real reference (not a token mention). Final calls: tdd-gate->SW Dev agent + implement.prompt; diagnose->SW Dev; host-integration-symlink->SW Dev; respect-existing->SW Dev; to-plan->Architect; grill-with-docs->PM; stakeholder-pressure-defense->EM; weekly-status-report->EM; lesson-capture->EM; session-self-review->EM.

## Definition of Done

R-1..R-3 checked with real-run evidence; M-1 confirmed; schema_lint green.
