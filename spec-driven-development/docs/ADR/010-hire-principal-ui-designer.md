# ADR-0010: Hire principal-ui-designer

- Status: **accepted** -- approved by human 2026-05-26
- Date: 2026-05-25
- Decider: Executive Manager (drafting) -> Human (approval)
- Supersedes: none
- Related: ADR-0003 (specialization naming), ADR-0004 (Executive Manager as orchestrator), ADR-0007 (/hire command and role lifecycle), ADR-0008 (precedent: hire principal-cloud-security-architect as 5th domain Principal)

## Context

The PI-3 kickoff prompt (2026-05-25) frames the framework as one that "ships
with a minimalist, aesthetically clean user interface, one instance attached
to one project at a time, that visualizes what each agent is working on, the
current sprint, a summary of work in progress, the current PI, and what comes
next."

The framework already has a live UI (Bridge dashboard v2.1) deployed to Azure
Container Apps at https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/.
But this UI evolved as a side-output of `cli/state_builder.py` -- it was built
to serve a CLI's HTML rendering, not to be a deliberate visual product. The
4-zone redesign in v2.1 was an ad-hoc improvement responding to user feedback,
not the output of a designed information architecture.

For the UI to become a **first-class framework concern** (per the kickoff
prompt), the framework needs a Principal who owns:

- Information architecture and visual hierarchy
- Design tokens (palette, type scale, spacing, motion) reusable across versions
- Accessibility targets (AA contrast, semantic HTML, keyboard navigation)
- The visual language that distinguishes this framework's instances from each other

None of the existing 4-5 Principals is the right home for this:

- **Architect** owns technical design; not visual hierarchy
- **Product Manager** owns scope/priority; not look-and-feel
- **Software Developer** owns implementation; not design tokens
- **Executive Manager** owns routing; never absorbs depth
- **Cloud Security Architect** owns Azure/identity; not visual layer

A `ux-designer-general` worker exists, but workers are scoped to 1-3 files per
task (Article IV). UI/UX leadership spans many files (CSS, HTML, design tokens,
mockup, spec) and requires sustained vision. This is a Principal-tier responsibility.

## Decision

Hire a new Principal-tier agent: `principal-ui-designer`.

Authority:
- Level 1 for visual decisions (palette, type scale, layout, motion, accessibility approach)
- Level 1 for UI information architecture decisions
- Level 2 (human) for any decision that adds a new runtime dependency to the
  UI stack (e.g. adopting HTMX, Alpine, React) -- such a decision triggers a
  constitution amendment per Article VIII
- Level 2 (human) for any decision that breaks accessibility AA targets

The new Principal is the SIXTH Principal in the fleet. Same precedent as
ADR-0008: this is a specialized DOMAIN Principal (UI/UX), not an additional
strategic coordinator. It does NOT orchestrate; it owns a narrow technical
domain (the visual layer).

## Scope

**What the principal-ui-designer owns:**

1. **Information architecture** -- what is shown, where, in what order, with what hierarchy
2. **Design tokens** -- palette, type scale, spacing scale, motion principles
3. **Accessibility** -- semantic HTML, AA contrast, keyboard navigation, screen reader hints
4. **Visual specs** -- what `state.html` should look like, expressed as a SPEC the Software Developer can implement
5. **Static mockups** -- non-functional HTML/CSS prototypes for human preview before implementation
6. **UI evolution policy** -- when v2 supersedes v1; deprecation path; coexistence rules

**What the principal-ui-designer does NOT own:**

- HTML/CSS implementation (Software Developer dispatches a worker for that)
- Backend logic in `state_builder.py` (Architect + Software Developer own)
- Runtime dependency choices (Level 2 escalation if any new dep is needed)
- Cloud deployment of the UI (Cloud Security Architect owns)
- Content of the dashboard (PM owns what data appears; UI Designer owns how it appears)

## Skills

- Inherits: `sdd-constitution`, `project-context`, `em-communication-discipline`
- Owns: `design-tokens` (new skill, to be authored in PI-3/S4 per LESSON-007 SHIP path)

## Alternatives considered

1. **Promote `ux-designer-general` to `ux-designer-dashboard-specialist-1`.**
   Rejected: specialists are workers (1-3 file scope) per ADR-0007. This is
   strategic UI leadership, not a tactical executor. Different layer.
2. **Load UI skills onto the existing Architect.** Rejected: Architect's
   context is already broad (specs, ADRs, pattern enforcement across all
   technical domains). UI/UX has its own vocabulary (design tokens, type
   scale, motion principles, accessibility audits) that pollutes Architect
   prompts unnecessarily.
3. **Stay with `ux-designer-general` worker + Architect oversight.** Considered.
   Workable for small UI work but inadequate for the kickoff's vision of a
   first-class framework UI. Defer if the user vetoes the hire; pi3/s4
   becomes worker-led.
4. **Hire only when UI implementation begins (PI-4).** Considered. Rejected
   because PI-3/S4 is the SPEC sprint -- the Principal authors the spec.
   Hiring at impl time is too late.

## Provenance

- Drafted in response to user decision at PI-3 kickoff (2026-05-25) selecting
  "Yes, hire principal-ui-designer now" via vscode_askQuestions session.
- Authored alongside `principal-ui-designer.agent.md` (this commit) and roster
  entry. All three artifacts land together.
- Per ADR-0007, Level-2 draft-first: artifacts exist with status `draft`; agent
  cannot be dispatched until human flips status to `active`. The human's
  selection at kickoff is the recorded intent; explicit "approve ADR-0010"
  flips the status.

## Reversibility

If rejected: delete the agent file, the roster entry, and this ADR. Revert
PI-3/S4 ownership to `ux-designer-general` worker with Architect review.

## Promotion criteria (draft -> active)

Per ADR-0007 generic-mode hire:

- Human reads ADR-0010 + the agent file
- Human explicitly approves: "approve ADR-0010" or "approve principal-ui-designer"
- Executive Manager flips `roster/agents.json` `status` from `draft` to
  `active` in a follow-up commit and notifies the SW Dev that PI-3/S4 can dispatch

## Update log

| Date | Event |
|------|-------|
| 2026-05-25 | Drafted at PI-3 kickoff |
| 2026-05-26 | Human approved ("approve") -- status flipped to accepted, roster updated to active |
