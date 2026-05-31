---
sprint: PI-3 / S-4
title: live-ui-v2-spec
owner: principal-ui-designer
last_updated: 2026-05-31
---

# Agent Notes -- PI-3 / Sprint-4

Ground-truth notes from agents who actually did the work. The *why*, *what
surprised us*, *what worked*, *what didn't*, and *what is worth remembering*.
Not a status report; a working journal.

## Session log
- **2026-05-26** by `principal-executive-manager`: ADR-0010 approved, CLARIFY doc created with 6 design questions (Q1-Q6).
- **2026-05-31** by `principal-executive-manager`: EM prefilled recommendations for all 6 questions. Human approved all recommendations in one pass.
- **2026-05-31** by `principal-ui-designer` (T-004): Authored DESIGN_TOKENS.md -- 59 CSS custom properties across 8 sections. Corrected v1 oxblood contrast ratio (3.6:1, not 5.1:1 as previously documented). v2 is strict superset of v1.
- **2026-05-31** by `principal-ui-designer` (T-006): Authored spec.md -- 37KB, 12 sections. Sprint-first information architecture per Q2 priority ranking. Three open questions flagged for architect.
- **2026-05-31** by `ux-designer-general` (T-005): Built static HTML mockup -- 34KB, all 6 spec sections rendered, semantic HTML with 25 ARIA labels, responsive at 768px+.
- **2026-05-31** by `principal-architect` (T-007): Reviewed spec. APPROVED WITH NOTES. Resolved 3 open questions (filesystem parsing, details/summary, 50-event feed cap). Flagged render_html rewrite as M effort.
- **2026-05-31** by `principal-software-developer` (T-008/T-009/T-010): Authored plan (4 phases), tasks (14 atomic), validation (LOCKED, 15+21 criteria).
- **2026-05-31** by `principal-ui-designer` (T-011): Authored design-tokens skill v1.0. Closes LESSON-007 (deferred from S3).
- **2026-05-31** by `human` (mockup review): OVERALL GREAT WORK. 7 feedback items captured as Appendix D in spec.md. Key requests: all PIs expandable with themes, project context section, backlog visibility, full agent traceability per feature, agent promotion tracking, dynamic graphical timeline. Mockup rebuilt by `ux-designer-general` with D-1 through D-5 incorporated. D-6/D-7 deferred to PI-5.
- **2026-05-31** by `human` (mockup review round 2): Sprint naming inconsistency flagged (PI-1 "Sprint 1/2", PI-2 "Sprint A/B/C", PI-3 "S1-S5"). Timeline too simple -- requested more graphical treatment. Dispatched `principal-ui-designer` for timeline v2.
- **2026-05-31** by `principal-ui-designer` (timeline v2): Full timeline redesign -- 3-column CSS grid (date pill | conduit | expandable panel), PI boundary markers (Bootstrap/PI-1/PI-2/PI-3), expandable details cards with stat blocks, "You are here" pulsing badge. Sprint naming standardized to S1/S2/S3 across all PIs.

## Surprises
- The v1 DESIGN.md claimed `--accent-oxblood` has 5.1:1 contrast on carbon. Actual computed ratio is 3.6:1. The design tokens now document this accurately and constrain oxblood to large text / UI elements only.
- The EM "recommend, don't menu" approach worked extremely well for the CLARIFY phase -- human approved all 6 recommendations in a single pass with zero overrides. Prefilling recommendations with rationale dramatically reduces HITL latency.
- state_builder.py is ~1600 lines (not ~430 as documented in copilot-instructions.md). The existing build-index machinery (`_discover_sprints`, `_query_ledger_for_pi`) covers most of the v2 data needs.

## What worked
- Parallel dispatch of T-004 (tokens) and T-006 (spec) -- no file conflicts, both completed in ~6 min.
- Parallel dispatch of T-011 (skill) alongside T-007 (architect review) -- independent scopes.
- EM prefilling CLARIFY answers with recommendations reduced human decision time to seconds.
- The architect review caught real issues (blocker threshold discrepancy, render_html rewrite sizing) that would have caused rework in PI-4.

## What didn't
- The sprint SPEC references `specs/2026-05-25-live-ui-v2/` in some places and `specs/2026-05-26-live-ui-v2/` in others. The actual directory is `2026-05-26`. Minor inconsistency.

## To remember
- LESSON candidate: EM "recommend, don't menu" for CLARIFY phases cuts HITL latency from multiple rounds to one pass.
- LESSON candidate: Design token contrast claims should be computationally verified, not copied from design exploration docs.
- LESSON candidate: state_builder.py line count in copilot-instructions.md is stale (~430 vs ~1600). Update it.
