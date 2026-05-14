# Product Backlog

Prioritized backlog with RICE scoring. Managed by Principal Product Manager.

## Priority Levels
- P1 (Must): Blocks daily usage or breaks existing features
- P2 (Should): Improves daily workflow significantly
- P3 (Could): Nice-to-have, quality-of-life
- P4 (Won't): Defer to future PI

## Format
| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|

## P1 - Must Have
(empty -- ready for first PI planning)

## P2 - Should Have
(empty)

## P3 - Could Have

| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|
| SDD-001 | Fleet Bridge Dashboard -- single-page ops console rendering fleet hierarchy, dispatch ledger, and spec lifecycle | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design exploration complete |

Notes:
- Design spec pre-built at `specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md`
- Depends on: Fleet Ledger v0.1 (done), `cli/fleet.py` (PI-2)
- Next step when prioritized: `/clarify` then `/spec`
- Rationale for P3: high demo value but does not unblock PI-2 CLI maturity work; becomes more valuable after fleet dispatches real work

## P4 - Won't (this PI)
(empty)

---

## insights_ai Project Follow-ups (retrospective intake 2026-05-07)

Note: These are work items for Rodolfo's insights_ai project (separate from Day-to-Day Agent features). Triaged from PROJECT_STATUS.md Update #31 open items.

| ID | Title | Priority | R | I | C | E | RICE | Tag | Status |
|----|-------|----------|---|---|---|---|------|-----|--------|
| IAI-02 | Nandini CVP demo (May 8) | P1 | 10 | 3 | 1.0 | 1 | 30.0 | [HITL] | Scheduled |
| IAI-03 | Merge 112 commits to dev | P1 | 8 | 2 | 1.0 | 1 | 16.0 | [BLOCKED on IAI-01] | Pending |
| IAI-01 | Full 178-leader batch re-run (Sprint 14.5) | P1 | 9 | 3 | 1.0 | 2 | 13.5 | [AFK] | Awaiting batch window |
| IAI-04 | ZS QC second-round validation | P1 | 7 | 2 | 0.8 | 1 | 11.2 | [BLOCKED on ZS] | Awaiting ZS feedback |
| IAI-05 | Azure Static Web App AAD auth deployment | P2 | 6 | 1 | 0.8 | 2 | 2.4 | [AFK] | Config ready, not deployed |
| IAI-06 | SEGMENT_MAPPING EPS/MG gap (61 sellers) | P4 | 3 | 0.5 | 0.5 | 2 | 0.375 | [AFK] | Documented, deferred |
