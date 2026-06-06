---
id: SDD-20260526PRIN-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-26-principal-agent-hygiene
---

# Principal Agent & Skill Hygiene -- Remove Day-to-Day References

**Date:** 2026-05-26
**Priority:** P3 (tech debt)
**Deferred to:** PI-4
**Source:** PI-3/S3/T-007 tech debt sweep

## Problem

Several agent definitions and skill files reference the Day-to-Day Agent project
(FastAPI, HTMX, 743-test baseline, etc.) which is the framework's origin project,
not the framework itself. These references should be generalized.

## Files affected

### Agent files (`.github/agents/`)

- `data-scientist-general.agent.md` -- line 6: "Day-to-Day Agent's spec-driven development framework"
- `developer-general.agent.md` -- line 6: "Day-to-Day Agent's spec-driven development framework"
- `principal-architect.agent.md` -- lines 18, 20, 36: title and identity tied to Day-to-Day Agent
- `principal-product-manager.agent.md` -- lines 15, 17: title and identity tied to Day-to-Day Agent
- `principal-software-developer.agent.md` -- lines 18, 20, 36, 106, 282, 356: title, identity, repo name, .venv path
- `qa-engineer-general.agent.md` -- line 6: "Day-to-Day Agent's spec-driven development framework"
- `ux-designer-general.agent.md` -- line 6: "Day-to-Day Agent's spec-driven development framework"

Note: `principal-executive-manager.agent.md` line 26 uses "day-to-day" as a common
English phrase ("day-to-day questions come to you"), not as a project name reference.
This line does NOT need updating.

### Skill files (`.github/skills/core/`)

- `git-workflow/SKILL.md` -- line 13: "Day-to-Day Agent parallel development framework"
- `git-workflow/SKILL.md` -- line 123: "Baseline 743 tests must all pass"
- `project-context/SKILL.md` -- line 87: "Day-to-Day dashboard"
- `project-context/SKILL.md` -- line 88: FastAPI /tasks endpoints reference
- `sdd-constitution/SKILL.md` -- line 21: "Day-to-Day Agent codebase"
- `testing-conventions/SKILL.md` -- lines 3, 12: "Day-to-Day Agent" and "743-test baseline"
- `testing-conventions/SKILL.md` -- line 90: hardcoded "743 tests" baseline count

## Acceptance Criteria

- AC1: No agent file under `.github/agents/` references "Day-to-Day" by name
- AC2: Skills under `.github/skills/` that reference Day-to-Day-specific details
  (743 tests, FastAPI, HTMX) are either generalized or clearly marked as
  "domain skill examples"
- AC3: No functional behavior changes -- only documentation/prompt text updates
