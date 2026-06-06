---
id: SDD-PI-4-LESSONS-lessons
type: lessons
status: active
owner: principal-software-developer
updated: 2026-06-06
sprint: PI-4
---

# PI-4 Lessons Learned

Capture lessons during PI-4 execution. Format: one lesson per section, tagged by phase.

---

## LESSON-014: Implementation preceded spec amendment

- **Phase:** IMPLEMENT
- **Tag:** `process-violation`
- **Date:** 2026-06-02
- **Feature:** live-ui-v2 (Section 5.6 Agent Activity)
- **What happened:** The human requested agent lineage visualization during PI-4
  implementation. The team implemented the feature directly (roster table + promotion
  timeline) without first amending the spec, which originally called for a placeholder
  only (deferred to PI-5). The spec was amended retroactively after the code shipped.
- **Root cause:** The Executive Manager routed the human's verbal request directly to
  implementation instead of routing to the Architect to check spec alignment first.
  The SDD lifecycle was bypassed: the correct path was
  IDEA -> check spec -> amend spec -> implement.
- **Deeper root cause:** An approved design for agent hierarchy visualization already
  existed in `specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md` Section 4.2
  (Hierarchy Panel), created 2026-05-13 in session `6ab90d07`. This design was
  demoted to a placeholder when the Live UI v2 spec (2026-05-26) was authored. The
  agent who implemented the lineage feature did not search for prior design artifacts
  before inventing a new solution. The framework's own history was ignored.
- **Impact:** Low (the feature works and tests pass), but the process violation
  undermines the traceability chain that SDD exists to protect. The shipped roster
  table does not match the approved Hierarchy Panel design (tree with status dots,
  indent levels, last-activity timestamps).
- **Action items:**
  1. When the human requests a change to an already-spec'd feature, the EM must route
     to the Architect first to determine if a spec amendment is needed -- even if the
     change seems small.
  2. Add a "spec alignment check" step to the `implement` skill: before coding,
     verify that the task matches the current spec. If not, flag for amendment.
  3. Before implementing any UI feature, search for prior design artifacts
     (`DESIGN.md`, `DESIGN_TOKENS.md`, mockups) in the specs directory. Do not
     invent new designs when approved ones exist.
- **Reference:** The canonical agent hierarchy design is in
  `specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md` Section 4.2.
- **Disposition:** SHIP -- this lesson should become a guardrail in the `implement`
  skill and/or a constitution amendment candidate.
