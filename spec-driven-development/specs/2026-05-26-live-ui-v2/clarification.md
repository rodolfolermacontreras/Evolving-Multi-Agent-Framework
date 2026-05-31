# Live UI v2 -- Clarification Log

**Sprint:** PI-3/S4
**Owner:** principal-ui-designer (lead), principal-architect (review)
**Date:** 2026-05-26
**Status:** IN PROGRESS

---

## Required Decisions (HITL)

The following questions need human input before the spec can be authored.

### Q1: Visual style preference

The current dashboard (v1) uses the "Bridge" aesthetic -- dark carbon background,
monospace typography, oxblood/amber/jade signal colors. Options:

- (a) **Evolve Bridge**: Keep the existing dark aesthetic, refine the information
  architecture and layout grid. Minimal visual disruption.
- (b) **Clean break**: New visual language -- potentially lighter, more modern,
  different typography. Bigger redesign effort.
- (c) **Dual theme**: Light + dark mode with a toggle. More implementation work
  but broader usability.

### Q2: Information priority

The kickoff prompt lists five visualizations. Rank by importance (1 = most important):

- [ ] Per-agent activity (what each agent is working on)
- [ ] Current sprint (which sprint is active, what is its goal)
- [ ] Work-in-progress summary (tasks in-flight, % complete)
- [ ] Current PI (which PI is active, how far along)
- [ ] What comes next (next gate, next sprint, blockers)

### Q3: Navigation layer in the dashboard

You requested the Management/ navigation pyramid be visible in the dashboard
(captured in IDEAS.md 2026-05-25). How deep should the dashboard go?

- (a) **Tier 1 only**: Show the PI list with status, link out to Markdown for detail
- (b) **Tier 1 + Tier 2**: Show PI list AND sprint table per PI, link out for sprint detail
- (c) **Full drill-down**: Render all three tiers in the dashboard (most implementation work)

### Q4: Live agent visibility

You asked about seeing each worker agent's context window in real-time (captured
in IDEAS.md 2026-05-25). For the v2 spec, should this be:

- (a) **Deferred to PI-4/PI-5**: Significant infrastructure work; spec the dashboard
  layout now without this feature
- (b) **Placeholder in spec**: Reserve a UI region for "live agent activity" but
  spec it as "coming soon" with a defined data contract
- (c) **Full spec**: Design the real-time agent visibility UX as part of v2 (extends
  the spec timeline significantly)

### Q5: Responsive targets

- (a) **Desktop only**: Optimize for 1280px+ viewport. Simplest.
- (b) **Desktop + tablet**: Down to 768px. Moderate effort.
- (c) **Full responsive**: Down to 375px mobile. Significant CSS work.

### Q6: Motion / animation preference

- (a) **No animation**: Static renders. Fastest to implement, most accessible.
- (b) **Subtle transitions**: Fade-in on load, smooth hover states. Low cost.
- (c) **Rich motion**: Progress animations, live-updating counters, etc. Higher cost.

---

## Answers

EM recommendations below (2026-05-31). Human: approve, override, or comment per question.

| Q | EM Recommendation | Rationale | Human Answer | Date |
|---|-------------------|-----------|--------------|------|
| Q1 | **(a) Evolve Bridge** | The dark aesthetic is already established and recognizable. Refinement > rebuild. | | |
| Q2 | 1. Current sprint, 2. What comes next, 3. WIP summary, 4. Current PI, 5. Per-agent activity | Sprint + next-action are the "where are we" questions you ask most. Agent activity is cool but lower priority until the data pipeline exists. | | |
| Q3 | **(b) PI list + sprint table** | Matches the 3-tier nav layer we just built. Full drill-down (c) is too much implementation for a v2 spec; tier-1-only (a) is too shallow. | | |
| Q4 | **(b) Placeholder** | Reserve the UI region and define the data contract now; implement when infrastructure exists. Full spec (c) delays v2 significantly. | | |
| Q5 | **(b) Desktop + tablet (768px+)** | You're literally on your phone right now asking about the dashboard -- tablet minimum makes sense. Full mobile (375px) is overkill for a dev tool. | | |
| Q6 | **(b) Subtle transitions** | Fade-in + hover states are low cost and make the dashboard feel alive without accessibility concerns. | |
