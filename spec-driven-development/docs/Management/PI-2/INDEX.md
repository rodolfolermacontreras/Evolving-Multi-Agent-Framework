---
pi: PI-2
status: Closed
theme: Fleet Maturity and Operational Tooling
started: 2026-05-16
closed: 2026-05-16
owner: principal-executive-manager
last_updated: 2026-05-25
---

# PI-2 -- Fleet Maturity and Operational Tooling

## Goal
Mature the fleet operations tooling: build the state dashboard, implement fleet/QA/retro/schema-lint CLIs, hire the first specialist worker, and establish the PI retro ceremony.

## Sprint List

<!-- BEGIN auto-generated:sprints (refreshed by `cli/state_builder.py build-index`) -->
| Sprint | Title | Status | Dispatches | Last Outcome | Detail |
|--------|-------|--------|------------|--------------|--------|
| A | State Builder + Fleet Bridge | DONE | 4 | success | [Sprint-A-state-builder-fleet-bridge](Sprint-A-state-builder-fleet-bridge/) |
| B | QA + Retro + Schema Lint | DONE | 4 | success | [Sprint-B-qa-retro-schema-lint](Sprint-B-qa-retro-schema-lint/) |
| C | Batch Dispatch + Specialist Hire | DONE | 4 | success | [Sprint-C-batch-dispatch-specialist-hire](Sprint-C-batch-dispatch-specialist-hire/) |
<!-- END auto-generated:sprints -->

## What Was Done (feature-by-feature)
- **SDD-002 (State Builder)**: `cli/state_builder.py` -- generates `exec/state.md` from fleet.db + artifacts. See [spec](../../../specs/2026-05-16-state-builder/).
- **SDD-003 (Fleet CLI)**: `cli/fleet.py` -- dispatch and ledger writes. See [spec](../../../specs/2026-05-16-fleet-cli/).
- **SDD-004 (QA CLI)**: `cli/qa.py` -- two-stage review automation. See [spec](../../../specs/2026-05-16-qa-cli/).
- **SDD-005 (Retro CLI)**: `cli/retro.py` -- sprint retrospective generator. See [spec](../../../specs/2026-05-16-retro-cli/).
- **SDD-006 (Schema Lint)**: Schema validation for YAML frontmatter. See [spec](../../../specs/2026-05-16-schema-lint/).
- **SDD-007 (State Dashboard)**: `exec/state.html` Bridge-style live dashboard. See [spec](../../../specs/2026-05-16-state-dashboard/).
- **Specialist Hire**: `developer-cli-specialist-1` earned permanent identity (5 CLIs, 70 tests, CLI-PATTERN.md adherence).

## Key Decisions
- **ADR-008**: Hire cloud security architect principal ([link](../../ADR/008-hire-cloud-security-architect.md))
- **ADR-009**: CI OIDC deploys to production ([link](../../ADR/009-ci-oidc-deploys-to-production.md))

## Lessons Captured
- **LESSON-005**: EM should recommend, not present a menu. Status: shipped ([source](../../../sprints/PI-2/lessons.md))
- **LESSON-006**: Closure ceremonies must touch ALL "current" markers. Status: OPEN ([source](../../../sprints/PI-2/lessons.md))
- **LESSON-007**: Pre-spec design exploration transfers cheaply. Status: OPEN ([source](../../../sprints/PI-2/lessons.md))
- **LESSON-008**: Two parallel specs for the same file: declare one canonical. Status: OPEN ([source](../../../sprints/PI-2/lessons.md))
- **LESSON-009**: Windows SQLite + tempdir tests need explicit cleanup. Status: OPEN ([source](../../../sprints/PI-2/lessons.md))
- **LESSON-010**: ACA Easy Auth needs companion app reg with id_token issuance enabled. Status: OPEN ([source](../../../sprints/PI-2/lessons.md))

## On-the-Ground Notes (synthesized)
PI-2 compressed three logical sprints into a single day, delivering 7 features with a 100% dispatch success rate. The key insight: the stdlib CLI pattern (LESSON-001 from PI-1) provided a consistent skeleton that made batch dispatch of 3 CLIs in one sprint feasible. The specialist hire mechanic validated the "earn, don't assign" philosophy -- `developer-cli-specialist-1` earned its identity through demonstrated competence across 5 implementations. LESSON-005 (EM communication discipline) was the most impactful human-facing improvement, immediately shipped as a skill. Five lessons remain open for PI-3 curation (S3).

## Links
- Tracker: [HIGH_LEVEL_DEV_TRACKER.md](../../HIGH_LEVEL_DEV_TRACKER.md)
- Retro: [sprints/PI-2-retro.md](../../../sprints/PI-2-retro.md)
- Lessons: [sprints/PI-2/lessons.md](../../../sprints/PI-2/lessons.md)
- Roadmap section: [constitution/roadmap.md](../../../constitution/roadmap.md)
