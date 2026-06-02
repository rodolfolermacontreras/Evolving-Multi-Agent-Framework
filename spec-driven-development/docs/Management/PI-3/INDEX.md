---
pi: PI-3
status: Done
theme: Portability Validation + Live UI v2 + Navigation Layer
started: 2026-05-25
closed: 2026-06-02
owner: principal-executive-manager
last_updated: 2026-05-26
---

# PI-3 -- Portability Validation + Live UI v2 + Navigation Layer

## Goal
Validate the framework's portability by bootstrapping onto the Day-to-Day Agent project (brownfield), spec a Live UI v2 with a dedicated UI Designer Principal, curate PI-2 lessons into framework improvements, and establish a durable human-readable navigation layer for the repo.

## Sprint List

<!-- BEGIN auto-generated:sprints (refreshed by `cli/state_builder.py build-index`) -->
| Sprint | Title | Status | Dispatches | Last Outcome | Detail |
|--------|-------|--------|------------|--------------|--------|
| 1 | Dashboard Freshness Unblock | BLOCKED on HITL Azure provisioning | 0 | -- | [Sprint-1-dashboard-freshness-unblock](Sprint-1-dashboard-freshness-unblock/) |
| 2 | Day To Day Brownfield Bootstrap | Proposed (awaiting Principal sign-off) | 0 | -- | [Sprint-2-day-to-day-brownfield-bootstrap](Sprint-2-day-to-day-brownfield-bootstrap/) |
| 3 | Pi2 Lessons Curation | **DONE** (7 parallel tasks, all shipped) | 7 | All SHIPPED/CLOSED/DEFERRED | [Sprint-3-pi2-lessons-curation](Sprint-3-pi2-lessons-curation/) |
| 4 | Live Ui V2 Spec | **DONE** (6 dispatches, all artifacts delivered) | 6 | APPROVED WITH NOTES (Architect) | [Sprint-4-live-ui-v2-spec](Sprint-4-live-ui-v2-spec/) |
| 5 | Management Navigation Layer | **DONE** | 14 | All tasks complete, merged | [Sprint-5-management-navigation-layer](Sprint-5-management-navigation-layer/) |
<!-- END auto-generated:sprints -->

## What Was Done (feature-by-feature)
- **SDD-009 (Navigation Layer)**: Three-tier Markdown navigation pyramid (Tracker -> PI INDEX -> Sprint SPEC + AGENT_NOTES). ADR-0011 accepted, Rule 13 added, PI-1/PI-2 backfilled, Temp/ migrated, build-index CLI subcommand operational. **DONE via S5.**
- **SDD-010 (UI Designer Hire)**: ADR-0010 approved 2026-05-26. `principal-ui-designer` agent active. Unblocks S4.
- **PI-2 Lessons Curation (S3)**: All 6 open lessons curated. LESSON-004 closed retrospectively (already shipped PI-2). LESSON-006/008/009/010 SHIPPED (4 skills amended to v1.1). LESSON-007 DEFERRED to S4. Tech debt spec filed for PI-4 (agent hygiene). Schema lint clean, 60/60 tests passing. **DONE via S3.**
- **SDD-013 (Live UI v2 Spec)**: Full spec authored with sprint-first IA, design tokens (59 CSS properties), static mockup, architect review (APPROVED WITH NOTES), PI-4 plan/tasks/validation (LOCKED). design-tokens skill v1.0 shipped (closes LESSON-007). 7 artifacts in `specs/2026-05-26-live-ui-v2/`. **DONE via S4.**

## Key Decisions
- **ADR-010**: Hire Principal UI Designer -- draft, pending human approval ([link](../../ADR/010-hire-principal-ui-designer.md))
- **ADR-011**: Three-Tier Navigation Layer -- accepted 2026-05-25 ([link](../../ADR/011-three-tier-navigation-layer.md))

## Lessons Captured
- Parallel dispatch to non-overlapping directory trees is safe and fast (S5 T-003/T-004/T-005).
- Backfill of historical PIs is archaeology, not automation -- mark provenance.
- Marker-block auto-generation is the right boundary between human and machine content in versioned Markdown.

## On-the-Ground Notes (synthesized)
PI-3 opened with an external feedback loop: a parallel team adopting the framework reported that the repo lacks glanceability despite strong tooling (ledger + dashboard). This led to S5 being inserted into the sprint board and prioritized to land first, so S2/S3/S4 adopt the new Management/ structure from day one. S5 governance (ADR-0011 + Rule 13) was approved by the human in a single session. T-002 through T-005 executed as a parallel batch with zero file conflicts. S1 remains HITL-blocked on 9 Azure provisioning steps.

## Links
- Tracker: [HIGH_LEVEL_DEV_TRACKER.md](../../HIGH_LEVEL_DEV_TRACKER.md)
- Roadmap section: [constitution/roadmap.md](../../../constitution/roadmap.md)
