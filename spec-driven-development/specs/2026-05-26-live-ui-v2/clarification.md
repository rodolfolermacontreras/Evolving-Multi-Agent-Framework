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

(To be filled by human)

| Q | Answer | Date |
|---|--------|------|
| Q1 | | |
| Q2 | | |
| Q3 | | |
| Q4 | | |
| Q5 | | |
| Q6 | | |
