---
pi: PI-1
status: Closed
theme: Framework Extraction and Generalization
started: 2026-05-12
closed: 2026-05-13
owner: principal-executive-manager
last_updated: 2026-05-25
---

# PI-1 -- Framework Extraction and Generalization

## Goal
Extract the Spec-Driven Development framework from the Day-to-Day Agent host project into a standalone repository, generalize all constitution and context files, and validate the lifecycle end-to-end with a dogfood pilot (fleet ledger).

## Sprint List

<!-- BEGIN auto-generated:sprints (refreshed by `cli/state_builder.py build-index`) -->
| Sprint | Title | Status | Dispatches | Last Outcome | Detail |
|--------|-------|--------|------------|--------------|--------|
| 1 | Extraction and Generalization | DONE | -- | success | [Sprint-1-extraction-and-generalization](Sprint-1-extraction-and-generalization/) |
| 2 | Fleet Ledger Pilot | DONE | -- | success | [Sprint-2-fleet-ledger-pilot](Sprint-2-fleet-ledger-pilot/) |
<!-- END auto-generated:sprints -->

## What Was Done (feature-by-feature)
- **SDD-001 (Fleet Ledger)**: First feature through full SDD lifecycle. Schema created, CLI scaffold built, 4 lessons captured. See [spec](../../../specs/2026-05-12-fleet-ledger/).
- **Framework extraction**: 82 files, 12,663 lines migrated from Day-to-Day Agent to standalone repo.
- **Constitution generalization**: `principles.md` fully rewritten with 9 binding articles. Other constitution files partially generalized (carried forward to PI-2+).

## Key Decisions
- **ADR-001**: SDD Framework adoption ([link](../../ADR/001-sdd-framework.md))
- **ADR-002**: Two-folder split -- `.github/` for Copilot-native, `spec-driven-development/` for process state ([link](../../ADR/002-two-folder-split.md))
- **ADR-003**: Specialization naming conventions ([link](../../ADR/003-specialization-naming.md))
- **ADR-004**: Executive Manager as single human entry point ([link](../../ADR/004-executive-manager-as-orchestrator.md))
- **ADR-005**: Validation as pre-implementation contract ([link](../../ADR/005-validation-as-pre-implementation-contract.md))
- **ADR-006**: Constitution semantic versioning ([link](../../ADR/006-constitution-semantic-versioning.md))
- **ADR-007**: /hire command and role lifecycle ([link](../../ADR/007-hire-command-and-role-lifecycle.md))

## Lessons Captured
- **LESSON-001**: Add a Python stdlib CLI utility pattern. Status: shipped ([source](../../../sprints/PI-1/lessons.md))
- **LESSON-002**: Clarify task ID convention inside feature directories. Status: shipped ([source](../../../sprints/PI-1/lessons.md))
- **LESSON-003**: Reduce validation prose duplication. Status: shipped ([source](../../../sprints/PI-1/lessons.md))
- **LESSON-004**: Define ledger migration policy before v0.2. Status: shipped in PI-2 ([source](../../../sprints/PI-1/lessons.md))

## On-the-Ground Notes (synthesized)
PI-1 predates the formal agent dispatch workflow. No AGENT_NOTES were captured at the time. Sprint folders contain retrospective reconstructions created during PI-3/S5 for navigability. The key ground-truth insight: the fleet ledger pilot validated that the SDD lifecycle works end-to-end, and the 4 lessons it surfaced became the seed for PI-2's operational tooling push.

## Links
- Tracker: [HIGH_LEVEL_DEV_TRACKER.md](../../HIGH_LEVEL_DEV_TRACKER.md)
- Lessons: [sprints/PI-1/lessons.md](../../../sprints/PI-1/lessons.md)
- Roadmap section: [constitution/roadmap.md](../../../constitution/roadmap.md)
