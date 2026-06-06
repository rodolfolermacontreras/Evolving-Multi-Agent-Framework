---
feature: fleet-bridge-dashboard
status: superseded
created: 2026-05-13
designer: gem-designer (sub-agent)
spec_status: not yet written -- this is design exploration, not approved scope
supersedes: none
id: SDD-FBDASH-design
type: spec
owner: principal-ui-designer
updated: 2026-06-06
---

# Fleet Bridge — Design Specification

> Visibility surface for the Evolving Multi-Agent Framework. Renders the live state
> of the fleet (Executive Manager → Principals → Workers), the dispatch ledger, and
> the spec lifecycle in a single dense screen. Operator-first; visitor-readable.

This document is a **design specification** — not implementation. It defines the
visual system, layout, components, tokens, motion, accessibility contract, and
implementer guidance. A future feature spec (under SDD lifecycle) will translate
this into requirements before implementation begins.

---

## 1. Visual Theme

### Metaphor
**The Bridge.** The dashboard is a flight director's console for the fleet, not
a virtual office. The user is mission control; agents are instruments and
telemetry, not avatars. Information density wins over visual metaphor.

### Movement reference
**Brutalism × monospace operations console.** Closest visual cousins: Bloomberg
Terminal, Linear's command palette aesthetic, NASA flight-control screens, the
recently-popular "boring software" trend (Plain UI, Beepberry, Berkeley Mono
landing page).

### The one memorable thing
**The Dispatch Stream.** A live, monospaced, ticker-style chronological feed of
every fleet event — pulled directly from `fleet.db.dispatches` joined with
`fleet.db.decisions`. It is the visual centerpiece, occupies the largest grid
cell, and is the surface a visitor will photograph or screenshot. It says
"this fleet is *real* and *traceable*" in one glance.

### What we are explicitly NOT
- Not a Sims-style virtual office with agent avatars at desks.
- Not a generic Kanban with rounded cards and pastel column headers.
- Not a glassmorphic dashboard with translucent panels and a purple gradient mesh.
- Not "AI dashboard chic" — no glowing neural-network background visuals, no
  spinning torus loaders, no chrome avatars with circuit patterns.

### Brand alignment
The framework's character is rigorous, traceable, lifecycle-driven. The Bridge
encodes that visually before a single label is read: dense layout, monospaced
type, hard borders, no decorative chrome. This is the visual analogue of the
constitution.

---

## 2. Color Palette

Three-color system (plus utility neutrals). 60-30-10 ratio is intentional:
60% carbon background, 30% paper-cream surface text, 10% sharp accents.

### Tokens

| Token                | Hex       | Role                                         | Contrast on `--bg-carbon` |
| -------------------- | --------- | -------------------------------------------- | ------------------------- |
| `--bg-carbon`        | `#0a0a0a` | Dominant background (60%)                    | —                         |
| `--bg-graphite`      | `#141413` | Panel surface, slightly lifted from carbon   | 1.1:1 (decorative only)   |
| `--bg-graphite-2`    | `#1c1b18` | Hover/active row background in stream        | 1.4:1 (decorative only)   |
| `--ink-paper`        | `#e8e4d8` | Primary text — paper-cream, not stark white  | **15.8:1 ✓ AAA**          |
| `--ink-paper-dim`    | `#a8a497` | Secondary text, timestamps, labels           | **8.4:1 ✓ AAA**           |
| `--ink-paper-faint`  | `#6e6a5e` | Tertiary text, separators, disabled states   | **4.6:1 ✓ AA**            |
| `--accent-oxblood`   | `#ce2029` | Active dispatches, EM input border, alerts   | **5.1:1 ✓ AA large+UI**   |
| `--accent-oxblood-2` | `#a01820` | Pressed / active state of accent             | 3.6:1 (UI elements only)  |
| `--signal-amber`     | `#d29a3b` | Waiting / blocked / awaiting-human status    | **8.9:1 ✓ AAA**           |
| `--signal-jade`      | `#6fa37a` | Completed / done / outcome=success           | **7.1:1 ✓ AAA**           |
| `--rule-line`        | `#2a2925` | Borders, grid rules, panel dividers          | 1.6:1 (decorative)        |
| `--focus-ring`       | `#e8e4d8` | Keyboard focus outline (high contrast on bg) | 15.8:1                    |

### Light-mode transformation
Light mode is **not shipped in v1**. The Bridge is a dark-first surface; light
mode would betray the operations-console identity. If demanded later, invert
`--bg-carbon`/`--ink-paper`, keep `--accent-oxblood` saturated, replace
`--signal-amber`/`--signal-jade` with darker variants for AA contrast.

### Why these colors
- **Carbon + paper-cream**: avoids the harsh `#000`/`#fff` pairing every "dark
  dashboard" defaults to; the cream introduces warmth without softening the
  brutalist character.
- **Oxblood as sole accent**: a single saturated red carries authority (alerts,
  active dispatches, the EM input). Using purple/blue would be generic; using
  multiple accents would dilute meaning.
- **Amber + jade as status-only**: never decorative. They appear *only* on
  status dots, outcome badges, and the alert ribbon — so when a user sees
  amber, they know something needs attention, full stop.

---

## 3. Typography

### Pairing
- **Body / data:** Berkeley Mono (preferred, paid) or **JetBrains Mono** as the
  free fallback. Variable-axis preferred. Justification: the dashboard is
  mostly tabular, ticker-style data — a monospace body is functional, not
  decorative.
- **Display:** **PP Supply Mono** (Pangram Pangram, free) for panel titles and
  the EM input prompt. Slab-cut monospace with strong personality; reads as
  "operations console" without slipping into retro-terminal cliché.
- **Reject:** Inter, Roboto, Roboto Mono (overused), Source Code Pro (banking
  cliché), Fira Code (programming-tutorial cliché), JetBrains Mono Display.

### Loading
Self-hosted WOFF2, `font-display: swap`. Both fonts must be on the critical
path; the dashboard reads as broken if monospaced rhythm collapses to a serif
fallback.

### Type scale (base 14px, ratio 1.25 minor third)

| Token          | Size  | Line  | Weight | Use                                |
| -------------- | ----- | ----- | ------ | ---------------------------------- |
| `--type-micro` | 11px  | 16px  | 400    | Timestamps, IDs, hint text         |
| `--type-body`  | 14px  | 22px  | 400    | Stream rows, hierarchy items       |
| `--type-emph`  | 14px  | 22px  | 600    | Active row in stream, current task |
| `--type-label` | 12px  | 16px  | 500    | Panel titles (Supply Mono, caps)   |
| `--type-h3`    | 18px  | 26px  | 500    | Drawer headers                     |
| `--type-h2`    | 22px  | 30px  | 500    | "Executive Manager" prompt label   |
| `--type-h1`    | 32px  | 38px  | 500    | Empty-state hero only              |

### Tabular numerals
All numeric data (timestamps, counts, dispatch IDs) uses
`font-variant-numeric: tabular-nums`. Non-negotiable — keeps the ticker stable.

### Letter-spacing
Panel titles (Supply Mono, uppercase): `letter-spacing: 0.08em`. Body and
stream rows: default. No other tracking adjustments.

---

## 4. Component Stylings

Five components carry the entire screen. Specs below define visual treatment
only — not data contracts.

### 4.1 Executive Manager Input (top bar)

**Anatomy:** Full-bleed strip, 96px tall. Left: oxblood square dot (12×12,
slow-pulsing when input is empty/idle, static when focused). Center: prompt
label "EXECUTIVE MANAGER ▌ talk to me" in Supply Mono. Right: input field
spans remaining width, monospaced placeholder "type or paste a request, idea,
or question…".

**States**
- Default: 1px border `--rule-line` bottom only; oxblood dot pulses 4s ease.
- Focus: 2px border `--accent-oxblood` bottom; dot becomes solid oxblood; the
  letters "MANAGER" gain underline-thin oxblood stroke.
- Submitting: dot rotates to filled square (CSS transform); "talk to me"
  changes to "logged ↳ session_2026-05-13_…"; cleared after 2s.
- Disabled (ledger unreachable): dot turns `--ink-paper-faint`, label reads
  "EXECUTIVE MANAGER ▌ ledger unreachable".

**Behavior:** Submit (Enter) writes a row to `decisions` (level=1,
decider="human", description=input). The user then opens VS Code Copilot Chat
in their normal flow. v1 does not auto-invoke an agent.

### 4.2 Hierarchy Panel (left rail)

**Anatomy:** Vertical tree. Three indent levels: Executive (0), Principals (1),
Workers (2). Each row: status dot · agent id · last-activity timestamp.

**Status dot legend** (each 8×8, no border)
- `▶ working`  — `--accent-oxblood`, 1.5s slow blink
- `✓ idle/done` — `--signal-jade`, static
- `⏸ idle long` — `--ink-paper-faint`, static (>1h since last dispatch)
- `? blocked` — `--signal-amber`, 0.8s blink
- `· unused`  — hollow `--rule-line` ring

**Selection:** click a row → entire row gets oxblood left-border (3px),
filters Dispatch Stream to that agent. Clicking again clears.

**Tree rules:** No icons, no avatars, no role colors. The tree is a text
artifact. Indent uses 24px Unicode box-drawing (`├`, `└`, `│`) in
`--ink-paper-faint`.

### 4.3 Dispatch Stream (center, dominant)

**Anatomy:** Reverse-chronological ticker. Each row, single line:
`HH:MM  from-agent  →  to-agent  glyph  task-summary`

| Glyph | Meaning                          | Color              |
| ----- | -------------------------------- | ------------------ |
| `▶`   | dispatch sent, in flight         | `--accent-oxblood` |
| `✓`   | outcome=success                  | `--signal-jade`    |
| `✗`   | outcome=failed                   | `--accent-oxblood` |
| `⏸`   | outcome=null (still in progress) | `--signal-amber`   |
| `◇`   | decision logged (level 1/2/3)    | `--ink-paper-dim`  |

**Row states**
- Default: `--ink-paper`, transparent background.
- Hover: `--bg-graphite-2` background.
- Selected (clicked): `--bg-graphite-2` + 2px oxblood left border + drawer opens.
- New (just inserted via poll): 220ms fade-in + 1px horizontal slide from left;
  the timestamp briefly highlights `--accent-oxblood` for 600ms then resolves
  to `--ink-paper-dim`.

**Filter chips** above the stream: `[ all ]  [ in-flight ]  [ blocked ]
[ today ]  [ feature: <name> ]`. Active chip: filled `--accent-oxblood`,
text `--bg-carbon`. Inactive: 1px border `--rule-line`, text
`--ink-paper-dim`.

**Drawer (slide-in from right):** opens when a row is clicked. Shows full
dispatch payload — task title, feature_dir, PI/sprint, outcome notes, link to
the spec file in the repo. Drawer is 480px wide on ≥1280px viewports; full
width below.

### 4.4 Lifecycle Panel (right rail)

**Anatomy:** Vertical mini-Kanban. Eight rows, one per phase:
IDEA / BACKLOG / CLARIFY / SPEC / PLAN / TASKS / IMPLEMENT / REVIEW / DONE.

Each row: phase label (Supply Mono caps, 12px) · count · sparkbar.

**Sparkbar:** A 6×6 unicode block (`▓`) repeated up to 12 chars, representing
features in that phase. Color: `--ink-paper-dim`. If any feature in the phase
is blocked, replace the leftmost block with `▒` in `--signal-amber`.

**Click behavior:** clicking a phase label expands an inline list of feature
names (truncated to 32 chars), each linking to its `specs/<dir>/` folder.

**Why vertical:** horizontal Kanban requires 8 columns and breaks the
asymmetric grid. Vertical preserves the right rail and reads like a stack of
gauges, reinforcing the console metaphor.

### 4.5 Alert Ribbon (bottom, conditional)

**Anatomy:** Full-bleed strip, 40px tall. Only renders when one or more
conditions hold:
- A dispatch has `outcome IS NULL AND age > 4h` (probable stuck task)
- A `decisions` row exists with `level=1 AND description LIKE '%needs-human%'`
- The ledger DB is unreachable

**Visual treatment:** background `--signal-amber` at 12% opacity over carbon;
full saturation 2px top border; text `--ink-paper`, Supply Mono caps.
Auto-dismisses 5min after the underlying condition clears.

**Never uses:** modal dialogs, toast popups, browser notifications. The
ribbon is the only alert surface. It does not steal focus.

---

## 5. Layout Principles

### Grid
**Three-column asymmetric CSS Grid**, named areas:

```
grid-template-columns: 240px 1fr 280px;
grid-template-rows:    96px 1fr auto;   /* auto = ribbon, 0 if absent */
grid-template-areas:
  "exec  exec    exec"
  "tree  stream  cycle"
  "alert alert   alert";
```

The **2fr center** dominates intentionally — the Dispatch Stream is the
truth surface. The 240/1fr/280 ratio breaks the predictable equal-thirds
dashboard layout and signals "this is not a generic Kanban."

### Spacing scale (8pt grid, with one exception)

| Token       | Value | Use                                         |
| ----------- | ----- | ------------------------------------------- |
| `--sp-1`    | 4px   | Within tabular rows (timestamp ↔ agent id)  |
| `--sp-2`    | 8px   | Padding inside dots and chips               |
| `--sp-3`    | 12px  | Hierarchy row vertical padding              |
| `--sp-4`    | 16px  | Stream row vertical padding, panel inset    |
| `--sp-6`    | 24px  | Indent step in hierarchy tree               |
| `--sp-8`    | 32px  | Panel padding (top/bottom)                  |
| `--sp-12`   | 48px  | Section gaps (rare; mostly drawer headers)  |
| `--sp-em`   | 96px  | Reserved exclusively for EM input height    |

### Container widths
The Bridge is **full-bleed** — no max-width container, no centered column.
Density is the point. Side rails are fixed-width (240/280px); center stream
flexes.

### Asymmetry sources (intentional)
1. Unequal column widths (240 / flex / 280)
2. EM input is full-bleed top *with no margin* — visually fused to the screen edge
3. Dispatch Stream rows extend slightly past the panel grid line on hover
   (`margin-right: -8px`) — a brutalist tell that the data is "live"
4. Lifecycle sparkbars are right-aligned, hierarchy tree is left-aligned —
   the two rails mirror, they don't match

### Visible structure
Borders are 1px `--rule-line`. **Visible**, not decorative. Brutalism
demands that the grid is exposed. No rounded corners except the EM input dot
(circular).

---

## 6. Depth & Elevation

The Bridge uses **flat depth with hierarchy via borders, not shadows**.
This is a deliberate brutalist choice and inverts the standard 5-level
elevation system.

| Level | Treatment                                                         | Use                          |
| ----- | ----------------------------------------------------------------- | ---------------------------- |
| 0     | `--bg-carbon`, no border                                          | Page background              |
| 1     | `--bg-carbon`, 1px `--rule-line` border                           | Panels (hierarchy, lifecycle) |
| 2     | `--bg-graphite`                                                   | Stream rows on hover         |
| 3     | `--bg-graphite-2` + 2px `--accent-oxblood` left border            | Selected stream row, focused EM input |
| 4     | `--bg-carbon` + 1px `--accent-oxblood` border, `box-shadow: 0 0 0 4px rgba(206,32,41,0.15)` | Drawer (slides from right)   |
| 5     | `--signal-amber` 12% bg + 2px top border                          | Alert ribbon                 |

**Glow not shadow.** When a state needs to "lift," it gets a colored
outer-ring glow (level 4) rather than a Y-axis shadow. This honors the dark-mode
inversion principle and avoids the "Material on dark" cliché.

### Shape language
- **Border-radius is forbidden** except: oxblood status dot (full circle), filter
  chips (2px radius). Two values total: `0` and `9999px`.
- **Corners are sharp.** This is the single most important shape choice —
  it locks the brutalist register and prevents drift toward generic SaaS.

---

## 7. Do's and Don'ts

### Do
- Use monospaced type everywhere — body, data, labels, prompts.
- Treat oxblood as scarce. If everything is red, nothing is.
- Show real timestamps (`14:22:08`), not relative ("2 minutes ago"). Operators
  trust absolutes.
- Let the Dispatch Stream breathe — rows have `--sp-4` vertical padding even
  though density is the goal. Crowding kills scannability.
- Animate **only** state transitions tied to real events (new dispatch row,
  outcome resolved, focus change). Decorative motion is forbidden.
- Use status dots, not status badges with rounded backgrounds. Dots scale
  from 1 agent to 100.
- Honor `prefers-reduced-motion`: disable the EM dot pulse, the stream slide-in,
  and the blocked-status blink. Replace with instant state changes.

### Don't
- Don't add agent avatars, illustrations, or character art. Agents are skill
  packs, not personas.
- Don't introduce a fourth color. The amber/jade/oxblood + neutral system is
  load-bearing — adding blue/purple/teal collapses meaning.
- Don't use rounded cards. The radius=0 rule is the brutalist load-bearing
  constraint.
- Don't add a sidebar collapse toggle. The hierarchy and lifecycle rails are
  fixed; collapsibility implies they're optional, and they are not.
- Don't render relative times ("just now", "5m ago"). Use absolute `HH:MM:SS`
  in the user's local timezone.
- Don't add a search bar. Filter chips cover the realistic query surface.
  Search invites the dashboard to grow into a different product.
- Don't add charts. Counts and sparkbars are sufficient. A bar chart of
  "dispatches per principal" is generic SaaS-think.
- Don't use Material Icons, Heroicons, Lucide, or any icon library. The
  Bridge uses **Unicode glyphs** (`▶`, `✓`, `⏸`, `◇`, `├`, `└`) exclusively —
  no SVG icon files. This is a brutalist load-bearing choice.

---

## 8. Responsive Behavior

The Bridge is **a desktop-first operator surface**. It does not pretend to be
mobile-friendly and that is a deliberate scope choice.

### Breakpoints

| Breakpoint  | Width      | Behavior                                                  |
| ----------- | ---------- | --------------------------------------------------------- |
| `bridge-xl` | ≥ 1600px   | Native layout; drawer 480px                               |
| `bridge-lg` | 1200–1599  | Native layout; drawer 400px; lifecycle rail to 240px      |
| `bridge-md` | 900–1199   | Right rail (lifecycle) collapses to a single header strip below the EM input; stream and hierarchy occupy the rest |
| `bridge-sm` | 600–899    | Hierarchy collapses to a horizontal scroll-strip below the EM input; stream is the only column |
| `bridge-xs` | < 600px    | Renders a stub: "Bridge is desktop-only. Open on a screen ≥ 900px." Includes a fallback link to a static read-only summary endpoint. |

### Touch targets
At `bridge-md` and below, all interactive elements (filter chips, stream rows,
hierarchy rows) have a minimum tap area of 44×44px via padding — even when the
visual element is smaller. Hit area > visual area is preferred to maintain
density.

### What does NOT change responsively
- Type scale: the same scale at every breakpoint. Fluid type would distort
  the monospace rhythm.
- Color tokens: identical across breakpoints.
- Motion: identical (still respects `prefers-reduced-motion`).

---

## 9. Agent Prompt Guide

Guidance for the future implementer agent who will translate this design into
HTML/CSS/JS in a feature spec.

### Implementation contract
1. **Single self-contained HTML file** at
   `spec-driven-development/dashboard/index.html`, mirroring the precedent set
   by `spec-driven-development/docs/CHEAT-SHEET.html`. Inline CSS in `<style>`,
   inline JS in `<script>`. No build step. No npm. No bundler.
2. **Backend** is a single Python CGI script at
   `spec-driven-development/dashboard/cgi-bin/fleet_state.py` using only the
   stdlib: `sqlite3`, `json`, `cgi`, `pathlib`. Reads `ledger/fleet.db`, returns
   JSON. No FastAPI, no Flask, no async runtime.
3. **Polling, not WebSockets.** The frontend polls `/cgi-bin/fleet_state.py`
   every 10 seconds. WebSockets are dishonest — the fleet doesn't change at
   sub-second cadence; pretending it does invites users to expect what doesn't
   exist.
4. **All tokens declared as CSS custom properties** in a `:root` block at the
   top of `<style>`. Token names match Section 2-6 exactly. No hard-coded
   hex values anywhere else in the file.
5. **Zero icon files.** Use the Unicode glyphs listed in this spec. If you
   need a glyph not in this spec, propose it via `/evolve` rather than
   inventing one inline.

### Forbidden choices
- Do NOT add Tailwind, Bootstrap, Bulma, or any utility CSS framework. The
  framework precedent is hand-written CSS in a single file.
- Do NOT use React, Vue, Svelte, Alpine, htmx, or any JS framework. Vanilla
  DOM with `document.querySelector` and `fetch()`.
- Do NOT add tooltips on hover. Operators learn the legend once; tooltips
  add motion noise to a surface that values stillness.
- Do NOT add a "settings" gear icon, theme toggle, or user profile menu.
  There is one user. There is one theme.
- Do NOT add a logo. The framework's identity is in its work, not its branding.

### Required choices
- DO use `font-variant-numeric: tabular-nums` on all numeric elements.
- DO set `prefers-reduced-motion` styles before shipping. The EM dot pulse,
  the stream row slide-in, and the blocked-status blink must all degrade to
  static state.
- DO test all four colored tokens against `--bg-carbon` for WCAG AA contrast
  before committing. Document the ratios in a comment block at the top of
  the CSS.
- DO render the alert ribbon conditionally. An empty ribbon is a worse signal
  than no ribbon — collapse the grid row when no alerts exist.

### Iteration guide

| If the design feels…           | …consider this rule                                    |
| ------------------------------ | ------------------------------------------------------ |
| "Too dense / overwhelming"     | Increase `--sp-4` to 20px in the stream — density is the goal but breathing room sells it. Do NOT remove panels.    |
| "Generic dashboard-y"          | Check rounded corners crept in. Audit `border-radius` — only dot and chips allowed. |
| "Too monochrome"               | The temptation will be to add blue. Resist. Add **one** unicode glyph variation in the stream instead. |
| "Status colors are confusing"  | Verify amber appears ONLY for blocked/waiting and jade ONLY for done. If they appear elsewhere, you have a token leak. |
| "Hard to find a feature"       | Add a filter chip for `feature: <name>`, not a search bar. Search invites scope creep. |
| "Unclear what's clickable"     | Hover state already provides the affordance via `--bg-graphite-2`. If users still miss it, increase hover bg contrast — do NOT add underlines or button styling. |
| "Visitors don't 'get' it"      | They are not the primary audience. Consider building a separate `/firm` view (Concept B from the design exploration) instead of softening The Bridge. |

### Design lint rules

For an automated style lint (or a code-review checklist):

| Rule ID  | Check                                                                                          | Severity |
| -------- | ---------------------------------------------------------------------------------------------- | -------- |
| BRG-001  | No hex values outside the `:root` token block.                                                 | Critical |
| BRG-002  | `border-radius` is `0`, `9999px`, or `2px` (chips only) — no other values.                     | Critical |
| BRG-003  | All font-family declarations use `--font-mono-body` or `--font-mono-display`.                  | Critical |
| BRG-004  | No SVG/PNG icon files in the dashboard directory (Unicode glyphs only).                        | Critical |
| BRG-005  | No `prefers-reduced-motion` media query missing if any `animation` or `transition` is declared. | Critical |
| BRG-006  | No `box-shadow` Y-offset > 0 (shadows are forbidden; glows only).                              | High     |
| BRG-007  | No relative-time strings (e.g. "5m ago"); use `HH:MM:SS`.                                      | High     |
| BRG-008  | Numeric elements include `font-variant-numeric: tabular-nums`.                                 | High     |
| BRG-009  | No new color token added without contrast ratio comment.                                       | High     |
| BRG-010  | No JS framework or build tooling introduced.                                                   | Critical |
| BRG-011  | Polling interval is exactly 10s; not less, not more.                                           | Medium   |
| BRG-012  | No tooltips, modals, toasts, or browser notifications. Alert ribbon only.                      | High     |

---

## Accessibility Contract

### WCAG 2.1 AA compliance plan

| Criterion                          | Approach                                                                                                  |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1.4.3 Contrast (Minimum)           | All body text on carbon meets ≥4.5:1; all UI elements ≥3:1. Tokens documented in §2 with measured ratios. |
| 1.4.11 Non-text Contrast           | Status dots use both color AND glyph (`▶`, `✓`, `⏸`). Color alone is never the carrier of meaning.        |
| 1.4.12 Text Spacing                | Line-height ≥1.5× for body; paragraph spacing 2× line-height in drawer prose.                              |
| 2.1.1 Keyboard                     | All interactive elements (EM input, filter chips, stream rows, hierarchy rows, drawer close) reachable via Tab. |
| 2.4.7 Focus Visible                | 2px `--focus-ring` outline with 2px offset; never removed.                                                |
| 2.5.5 Target Size                  | At ≤bridge-md, all targets ≥44×44px via padding (visual element may be smaller).                          |
| 2.3.3 Animation from Interactions  | All animation respects `prefers-reduced-motion: reduce`.                                                  |
| 4.1.2 Name, Role, Value            | Semantic HTML: `<header>`, `<nav>`, `<main>`, `<aside>`, `<section>`. ARIA `role="log"` on Dispatch Stream with `aria-live="polite"`.    |
| 4.1.3 Status Messages              | Alert ribbon uses `role="status"` for non-critical, `role="alert"` for ledger-unreachable.                |

### Screen-reader behavior
- Dispatch Stream announces new rows via `aria-live="polite"` (not assertive —
  the stream updates frequently; assertive would be hostile).
- Status dots have `aria-label` (e.g., `aria-label="working"`); the visual
  glyph is `aria-hidden="true"`.
- The hierarchy tree uses `role="tree"` with `role="treeitem"` and proper
  `aria-level`/`aria-expanded` attributes.

---

## Open design decisions (deferred)

These are intentional gaps for the feature-spec phase to resolve, not v1
requirements:

1. **Authentication.** Is the dashboard local-only (file://) or served? If
   served, what protects it? Default assumption: local-only `python -m http.server`
   in v1; auth deferred.
2. **Multi-PI view.** Currently shows current PI only. Filter for historical
   PIs deferred until PI-2 closes.
3. **Audit export.** "Export this view as PDF/markdown" is tempting but
   premature; defer until a stakeholder asks.
4. **The Atrium.** A secondary visual/whimsical view (the rejected
   floor-plan concept). Defer entirely; revisit only if visitors specifically
   ask for it.
5. **Specialist agent visualization.** Once `/hire specialist` produces named
   specialists, the hierarchy tree may need depth=3. v1 supports depth=2;
   extension to depth=3 is a v2 concern.

---

## What this spec does NOT cover

- HTML/CSS/JS implementation (belongs in feature spec + tasks)
- The CGI Python script logic (belongs in feature spec)
- The data contract between frontend and `fleet_state.py` (belongs in feature spec)
- Test plan (belongs in feature spec)
- Deployment / how to run locally (belongs in README of dashboard module)

This is design only. The next step is `/spec` to produce a feature spec, then
`/plan` and `/tasks` per the SDD lifecycle.
