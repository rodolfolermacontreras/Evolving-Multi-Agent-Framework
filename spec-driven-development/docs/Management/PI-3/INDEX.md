---
pi: PI-3
status: Active
theme: Portability Validation + Live UI v2 + Navigation Layer
started: 2026-05-25
closed: in flight
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
| 3 | Pi2 Lessons Curation | Proposed | 0 | -- | [Sprint-3-pi2-lessons-curation](Sprint-3-pi2-lessons-curation/) |
| 4 | Live Ui V2 Spec | Proposed (depends on ADR-0010 hire approval) | 0 | -- | [Sprint-4-live-ui-v2-spec](Sprint-4-live-ui-v2-spec/) |
| 5 | Management Navigation Layer | In-Flight (ADR-0011 approved, Rule 13 landed; T-002 unblocked for dispatch) | 0 | -- | [Sprint-5-management-navigation-layer](Sprint-5-management-navigation-layer/) |
<!-- END auto-generated:sprints -->

## What Was Done (feature-by-feature)
- **SDD-009 (Navigation Layer)**: Three-tier Markdown navigation pyramid (Tracker -> PI INDEX -> Sprint SPEC + AGENT_NOTES). ADR-0011 accepted, Rule 13 added, PI-1/PI-2 backfilled, Temp/ migrated, build-index CLI subcommand operational. **DONE via S5.**
- **SDD-010 (UI Designer Hire)**: ADR-0010 drafted, `principal-ui-designer` agent created (both pending human approval). Unblocks S4.

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
