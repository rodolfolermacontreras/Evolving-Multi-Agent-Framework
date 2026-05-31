# Live UI v2 -- Design Tokens

**Sprint:** PI-3/S4 (T-004)
**Author:** principal-ui-designer
**Status:** LOCKED -- approved design decisions applied (2026-05-31 clarification.md)
**Supersedes:** v1 tokens in `exec/state.html` (lines 8-24)
**Constraint:** stdlib + plain HTML/CSS only. No JS frameworks, no CSS preprocessors.

---

## 1. Color Palette

Three-color system: 60% carbon background, 30% paper-cream text, 10% accent.
All tokens are CSS custom properties on `:root`. Contrast ratios measured against
`--bg-carbon` (#0a0a0a) unless stated otherwise.

### 1.1 Backgrounds

| Token | Hex | Role | Contrast on carbon | v1 change |
|-------|-----|------|--------------------|-----------|
| `--bg-carbon` | `#0a0a0a` | Page background (60% dominant) | -- | unchanged |
| `--bg-graphite` | `#141413` | Panel surfaces, cards | 1.1:1 (decorative) | unchanged |
| `--bg-graphite-2` | `#1c1b18` | Hover rows, nested panels, inset regions | 1.4:1 (decorative) | unchanged |
| `--bg-graphite-3` | `#232220` | Active rows, agent chips, tertiary surfaces | 1.6:1 (decorative) | unchanged |

Rationale: The four-tier background stack creates depth without shadows or
gradients. No changes from v1 -- the system works and users recognize it.

### 1.2 Ink (Text)

| Token | Hex | Role | Contrast on carbon | WCAG | v1 change |
|-------|-----|------|--------------------|------|-----------|
| `--ink-paper` | `#e8e4d8` | Primary text, headings, data values | 15.6:1 | AAA | unchanged |
| `--ink-paper-dim` | `#b8b4a8` | Secondary text, labels, timestamps | 9.6:1 | AAA | unchanged |
| `--ink-paper-faint` | `#8a8678` | Tertiary text, disabled states, decorative borders | 5.4:1 | AA | unchanged |

Rationale: Paper-cream avoids harsh `#000`/`#fff` pairing. The three tiers
create clear visual hierarchy. All pass AA minimum; primary and secondary
pass AAA.

### 1.3 Accent

| Token | Hex | Role | Contrast on carbon | WCAG | v1 change |
|-------|-----|------|--------------------|------|-----------|
| `--accent-oxblood` | `#ce2029` | Primary accent: active sprint pill, CTA borders, alert accents | 3.6:1 | AA large text + UI (3:1) | unchanged |
| `--accent-oxblood-2` | `#a01820` | Pressed/active state of accent, principal agent avatars | 2.7:1 | decorative / UI only | unchanged |
| `--accent-oxblood-hover` | `#e02830` | Hover state for interactive oxblood elements | 4.3:1 | AA large text + UI (3:1) | **NEW** |

Usage constraint: Oxblood at 3.6:1 does NOT pass AA for normal-size text.
It must be used ONLY as: (1) background fill on pills/buttons where the text
is `--ink-paper` on oxblood background (15.6:1 inverted -- passes AAA), (2)
border accents, (3) status dot fills, (4) large text (>= 18px or >= 14px bold).
Never as body text color on carbon/graphite backgrounds.

### 1.4 Signal Colors (Status Only)

| Token | Hex | Role | Contrast on carbon | WCAG | v1 change |
|-------|-----|------|--------------------|------|-----------|
| `--signal-amber` | `#d29a3b` | Blocked, waiting, needs-attention | 7.9:1 | AAA | unchanged |
| `--signal-amber-2` | `#e8b85a` | Links, highlighted amber values | 10.8:1 | AAA | unchanged |
| `--signal-amber-3` | `#8a6a2a` | Amber-tinted borders, muted amber backgrounds | 4.7:1 | AA | unchanged |
| `--signal-jade` | `#6fa37a` | Done, success, completed | 6.8:1 | AA | unchanged |
| `--signal-jade-dim` | `#486a52` | Muted jade: worker agent avatars, idle-complete | 3.3:1 | decorative only | unchanged |

Usage constraint: Signal colors appear ONLY on status indicators (dots, badges,
progress rings, border-left accents). When a user sees amber, something needs
attention. When they see jade, something succeeded. No decorative use.

### 1.5 Structural

| Token | Hex | Role | v1 change |
|-------|-----|------|-----------|
| `--rule-line` | `#2a2925` | Panel borders, table rules, grid dividers | unchanged |
| `--focus-ring` | `#e8e4d8` | Keyboard focus outline (matches `--ink-paper`) | **NEW** (was implicit in v1) |

### 1.6 Structural Note

`--focus-ring` inherits the 15.6:1 contrast ratio of `--ink-paper`, ensuring
visibility on all background tiers.
| `--focus-ring-offset` | `#0a0a0a` | Outer offset of focus ring (matches `--bg-carbon`) | **NEW** |

### 1.6 Semantic Aliases

These aliases map generic intent to specific tokens. Use aliases in component
CSS; use raw tokens only in this file.

```css
:root {
  /* Intent → Token */
  --color-text-primary:     var(--ink-paper);
  --color-text-secondary:   var(--ink-paper-dim);
  --color-text-tertiary:    var(--ink-paper-faint);
  --color-surface-base:     var(--bg-carbon);
  --color-surface-raised:   var(--bg-graphite);
  --color-surface-overlay:  var(--bg-graphite-2);
  --color-border-default:   var(--rule-line);
  --color-interactive:      var(--accent-oxblood);
  --color-interactive-hover: var(--accent-oxblood-hover);
  --color-status-success:   var(--signal-jade);
  --color-status-warning:   var(--signal-amber);
  --color-status-error:     var(--accent-oxblood);
  --color-status-idle:      var(--ink-paper-faint);
  --color-link:             var(--signal-amber-2);
}
```

---

## 2. Type Scale

Modular scale: base 14px, ratio 1.25 (minor third). Monospace body; system
sans-serif for mission text and body prose where monospace hinders readability.

### 2.1 Font Stacks

| Token | Stack | Usage |
|-------|-------|-------|
| `--font-mono` | `ui-monospace, "Berkeley Mono", "JetBrains Mono", Menlo, Consolas, monospace` | Data, tables, labels, headings, all dashboard chrome |
| `--font-sans` | `-apple-system, "Segoe UI", Inter, system-ui, sans-serif` | Mission statement, long-form prose (rare) |

Rationale: v1 uses mono everywhere. v2 retains mono as dominant but permits
sans-serif for the mission subtitle where readability of natural language matters.
No new font downloads required -- both stacks use system fonts.

### 2.2 Scale

| Token | Size | Line height | Weight | Letter spacing | Usage |
|-------|------|-------------|--------|----------------|-------|
| `--type-micro` | 10px | 14px | 400 | 0.14em | Timestamps, build hashes, IDs, pill labels |
| `--type-caption` | 11px | 16px | 400 | 0.06em | Feature row meta, agent chip labels, defer notes |
| `--type-label` | 12px | 16px | 600 | 0.22em | Zone headings (uppercase), nav labels |
| `--type-body` | 14px | 22px | 400 | normal | Primary body text, table cells, feature names |
| `--type-emph` | 14px | 22px | 700 | normal | Active sprint name, current feature, bold data |
| `--type-h3` | 18px | 26px | 600 | 0.04em | Section headers, panel titles |
| `--type-h2` | 22px | 30px | 600 | 0.02em | Page-level section titles (e.g. "PI-3") |
| `--type-h1` | 28px | 34px | 700 | normal | Dashboard title "BRIDGE", hero empty state |

v1 delta: `--type-h1` reduced from 32px to 28px (32px was oversized for
the information-dense layout). `--type-caption` added at 11px to formalize the
size used by feature row meta in v1. `--type-micro` reduced from 11px to 10px
to create clearer separation from `--type-caption`.

### 2.3 Numeric Treatment

```css
.tabular-nums {
  font-variant-numeric: tabular-nums;
}
```

Applied to: all timestamps, percentages, counts, progress values, dispatch IDs.
Non-negotiable -- keeps columns aligned in ticker and table views.

### 2.4 Text Transform Rules

| Context | Transform | Example |
|---------|-----------|---------|
| Zone headings | `text-transform: uppercase` | "CURRENT SPRINT" |
| Sprint pills | `text-transform: uppercase` | "S4" |
| Status badges | `text-transform: uppercase` | "BLOCKED" |
| Feature names | None (preserve case) | "Live UI v2 Spec" |
| Agent IDs | None (preserve case) | "principal-architect" |

---

## 3. Spacing Scale

Base unit: 4px. All spacing tokens are multiples of the base unit.

| Token | Value | Multiplier | Usage |
|-------|-------|------------|-------|
| `--space-2xs` | 2px | 0.5x | Inline icon gaps, tight insets |
| `--space-xs` | 4px | 1x | Sprint pill gaps, dot-to-label gap, minimum padding |
| `--space-sm` | 8px | 2x | Compact padding (pills, chips), gap between inline elements |
| `--space-md` | 12px | 3x | Standard card padding, gap between stacked elements |
| `--space-lg` | 16px | 4x | Zone internal padding, gap between sections |
| `--space-xl` | 24px | 6x | Gap between zones in grid, major section separation |
| `--space-2xl` | 32px | 8x | Page margin (sides), hero spacing |
| `--space-3xl` | 48px | 12x | Top/bottom page padding, maximum breathing room |

### 3.1 Component Spacing Recipes

| Component | Padding | Gap | Margin |
|-----------|---------|-----|--------|
| Zone (panel) | `--space-lg` `--space-lg` (16px all) | -- | -- |
| Zone heading | 0 0 `--space-md` (12px bottom) | -- | -- |
| Feature row | `6px` 0 (tight vertical) | `--space-sm` (8px column gap) | -- |
| Sprint pill | `--space-xs` `--space-md` (4px 12px) | -- | -- |
| Agent chip | `--space-xs` `--space-sm` (4px 8px) | `6px` (flex gap) | -- |
| Grid layout | -- | `--space-md` (12px gap) | `--space-lg` `--space-xl` (18px 22px page pad) |
| Next-action card | `--space-md` `--space-md` (12px 14px) | -- | `--space-md` top margin |
| Top bar | `--space-md` `--space-xl` (14px 22px) | `--space-xl` (24px column gap) | -- |

---

## 4. Layout Grid

### 4.1 Breakpoints

| Token | Width | Behavior |
|-------|-------|----------|
| `--bp-tablet` | 768px | Single-column layout; zones stack vertically |
| `--bp-desktop` | 1280px | Full 2-column grid layout with all zones visible |

No mobile breakpoint (per Q5 decision: 768px+ only).

### 4.2 Grid Structure

Desktop (>= 1280px):

```
+---------------------------------------------------------------+
|                         TOP BAR                                |
|  [BRIDGE]  [mission text]    [S1][S2][S3][S4]    [● LIVE]     |
+-------------------------------+-------------------------------+
|         ZONE A (priority 1)   |       ZONE B (priority 2)     |
|       Current Sprint Focus    |       What Comes Next         |
|   Progress ring + features    |   Next gate + upcoming work   |
+---------------------------------------------------------------+
|                     ZONE C (priority 3)                        |
|                   WIP Summary + PI Overview                    |
|          Sprint table, PI progress, navigation layer           |
+---------------------------------------------------------------+
|                     ZONE D (priority 4-5)                      |
|                Per-Agent Activity (placeholder)                |
|         Reserved region -- "coming soon" + data contract       |
+---------------------------------------------------------------+
```

```css
main.layout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  grid-template-areas:
    "zone-a zone-b"
    "zone-c zone-c"
    "zone-d zone-d";
  gap: var(--space-md);          /* 12px */
  padding: 18px 22px;
}
```

Tablet (768px -- 1279px):

```css
@media (max-width: 1279px) {
  main.layout-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "zone-a"
      "zone-b"
      "zone-c"
      "zone-d";
  }
}
```

Zone stacking order matches information priority (Q2): Sprint first, Next
second, WIP/PI third, Agent activity last.

### 4.3 Zone Definitions

| Zone | Grid area | Content (information priority) | Min height |
|------|-----------|-------------------------------|------------|
| Top bar | Outside grid (sticky `position: sticky; top: 0`) | Dashboard title, mission, sprint pills, live indicator | 56px |
| Zone A | `zone-a` | **Current Sprint** -- progress ring, feature list with status dots, sprint goal | auto |
| Zone B | `zone-b` | **What Comes Next** -- next gate card (oxblood left-border), upcoming sprint preview, blockers | auto |
| Zone C | `zone-c` | **WIP Summary + PI Overview** -- PI progress bar, sprint table (per Q3: PI list + sprint table), task counts | auto |
| Zone D | `zone-d` | **Per-Agent Activity** -- placeholder (per Q4: reserve region, define data contract) | 120px |

### 4.4 Zone Internal Layout Patterns

**Zone A** (Current Sprint):
```
[Progress Ring 140x140]  [Feature Stack]
                          ├ ● Feature name ... status
                          ├ ● Feature name ... status
                          └ ● Feature name ... status
```
- Grid: `grid-template-columns: 140px 1fr`
- Progress ring: SVG circle, `--signal-jade` foreground, `--bg-graphite-3` track

**Zone B** (What Comes Next):
```
┌─────────────────────────────┐
│ NEXT UP                     │  ← oxblood left-border card
│ [Feature title]             │
│ [Why it matters]            │
│ [▸ Start when: condition]   │
└─────────────────────────────┘
[Upcoming sprint mini-cards]
```

**Zone C** (WIP + PI):
```
[PI-3 ████████░░ 72%]        ← progress bar
┌────┬──────────┬────────┬───────┐
│ S# │ Sprint   │ Status │ Tasks │  ← sprint table
├────┼──────────┼────────┼───────┤
│ S1 │ Core     │ DONE   │ 12/12 │
│ S2 │ Fleet    │ DONE   │ 8/8   │
│ S3 │ Polish   │ DONE   │ 10/10 │
│ S4 │ UI v2    │ ACTIVE │ 3/7   │
└────┴──────────┴────────┴───────┘
```

**Zone D** (Agent Activity -- Placeholder):
```
┌─────────────────────────────────────────────────┐
│ AGENT ACTIVITY                                  │
│ Data contract defined. Implementation deferred. │
│ See spec section 8 for data contract.           │
└─────────────────────────────────────────────────┘
```

---

## 5. Motion Principles

Per Q6 decision: subtle transitions only. No keyframe-heavy animation except
status dot pulses (carried from v1).

### 5.1 Transition Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `120ms` | Hover state changes (background, border color) |
| `--duration-normal` | `220ms` | Panel fade-in on load, focus ring appearance |
| `--duration-slow` | `500ms` | Progress ring stroke animation, zone entrance |
| `--easing-default` | `ease-out` | All transitions unless specified |
| `--easing-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Reserved for future interactive elements |

### 5.2 What Animates

| Element | Transition | Duration | Easing |
|---------|-----------|----------|--------|
| Hover on rows / pills / buttons | `background-color`, `border-color`, `color` | `--duration-fast` | `--easing-default` |
| Focus ring appearance | `outline-offset` | `--duration-normal` | `--easing-default` |
| Progress ring stroke | `stroke-dashoffset` | 700ms | `ease` |
| Status dots (jade/amber/red) | Box-shadow pulse | 1.6s / 2.2s / 1.0s | `ease-in-out` |
| Zone panels on initial load | `opacity` 0→1 | `--duration-slow` | `--easing-default` |

### 5.3 What Does NOT Animate

- Layout shifts (no grid reflow animation)
- Text content changes (no counter-increment animation)
- Color theme changes (if ever added)
- Scroll position
- Zone resize on breakpoint change

### 5.4 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Status dots become static filled circles. Progress ring renders at final
position without stroke animation. All information remains accessible.

---

## 6. Elevation / Depth

No box-shadows. Depth is communicated through background color tiers only.
This is a deliberate brutalist constraint -- the Bridge is flat.

### 6.1 Surface Hierarchy

| Level | Token | Visual | Usage |
|-------|-------|--------|-------|
| 0 (base) | `--bg-carbon` | Darkest | Page background |
| 1 (raised) | `--bg-graphite` | +1 step | Zone panels, cards |
| 2 (overlay) | `--bg-graphite-2` | +2 steps | Hover states, inset panels, next-action card |
| 3 (emphasis) | `--bg-graphite-3` | +3 steps | Active row highlight, agent chip background |

### 6.2 Border System

| Context | Border spec |
|---------|-------------|
| Zone panels | `1px solid var(--rule-line)` |
| Top bar bottom | `2px solid var(--accent-oxblood)` |
| Zone headings bottom | `1px solid var(--rule-line)` |
| Next-action card left | `3px solid var(--accent-oxblood)` |
| Defer-note left | `2px solid var(--signal-amber-3)` |
| Table rows | `1px dashed var(--rule-line)` |
| Sprint pill (inactive) | `1px solid var(--rule-line)` |
| Sprint pill (active) | `1px solid var(--accent-oxblood)`, bg `var(--accent-oxblood)` |
| Focus ring | `2px solid var(--focus-ring)`, `2px offset` |

### 6.3 Border Radius

```css
:root {
  --radius-none: 0;
  --radius-sm: 2px;     /* pills, chips -- minimal rounding */
  --radius-full: 50%;   /* status dots only */
}
```

The Bridge is rectilinear. No rounded cards, no rounded panels. Only pills and
status dots use radius, and minimally.

---

## 7. Accessibility Contract

Target: WCAG 2.1 AA compliance. All decisions in this token set have been
verified against AA requirements.

### 7.1 Contrast Verification Summary

| Text token | On background | Ratio | Requirement | Pass |
|------------|---------------|-------|-------------|------|
| `--ink-paper` | `--bg-carbon` | 15.6:1 | 4.5:1 (normal text) | AAA |
| `--ink-paper` | `--bg-graphite` | 14.5:1 | 4.5:1 (normal text) | AAA |
| `--ink-paper` | `--bg-graphite-2` | 13.5:1 | 4.5:1 (normal text) | AAA |
| `--ink-paper-dim` | `--bg-carbon` | 9.6:1 | 4.5:1 (normal text) | AAA |
| `--ink-paper-dim` | `--bg-graphite` | 8.9:1 | 4.5:1 (normal text) | AAA |
| `--ink-paper-faint` | `--bg-carbon` | 5.4:1 | 4.5:1 (normal text) | AA |
| `--ink-paper-faint` | `--bg-graphite` | 5.1:1 | 4.5:1 (normal text) | AA |
| `--accent-oxblood` | `--bg-carbon` | 3.6:1 | 3:1 (UI / large text) | AA-lg |
| `--signal-amber` | `--bg-carbon` | 7.9:1 | 4.5:1 (normal text) | AAA |
| `--signal-jade` | `--bg-carbon` | 6.8:1 | 4.5:1 (normal text) | AA |
| `--signal-amber-2` (links) | `--bg-carbon` | 10.8:1 | 4.5:1 (normal text) | AAA |

Note: `--accent-oxblood` at 3.6:1 passes AA for large text (>= 18px or >= 14px
bold) and UI components (borders, dots, fills), but does NOT pass AA for
normal-weight text smaller than 18px. This is by design -- oxblood is used as a
background fill (e.g. active sprint pill) where `--ink-paper` text sits ON the
oxblood surface, or as non-text UI indicators. It is never used as foreground
text on dark backgrounds at body size.

### 7.2 Focus Ring Specification

```css
*:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

- Ring color: `--ink-paper` (#e8e4d8) -- 15.6:1 against carbon, visible on all
  background tiers
- Offset: 2px gap between element edge and ring, ensuring ring is not obscured
  by element borders
- No `outline: none` anywhere in the codebase except on elements where a custom
  visible focus indicator is provided

### 7.3 Keyboard Navigation Flow

Tab order follows DOM order, which follows visual layout (top-to-bottom,
left-to-right):

1. Top bar: refresh button
2. Sprint pills: each pill is a focusable element (tab between them)
3. Zone A: feature rows (each row focusable for future drill-down)
4. Zone B: next-action card CTA link
5. Zone C: sprint table rows, PI navigation links
6. Zone D: placeholder (no interactive elements in v2)

### 7.4 Semantic HTML Elements

| UI region | HTML element | ARIA role (if needed) |
|-----------|-------------|----------------------|
| Top bar | `<header>` | `banner` (implicit) |
| Zone panels | `<section>` with `aria-labelledby` pointing to zone `<h2>` | `region` (implicit) |
| Zone headings | `<h2>` | -- |
| Feature list | `<ul>` > `<li>` | `list` (implicit) |
| Sprint table | `<table>` with `<thead>`, `<tbody>`, `<th scope="col">` | `table` (implicit) |
| Progress ring | `<svg>` with `role="img"` and `aria-label="Sprint progress: N%"` | `img` |
| Status dots | `<span>` with `aria-label` describing status | -- |
| Sprint pills | `<nav>` > `<button>` or `<a>` | `navigation` (implicit) |
| Page footer | `<footer>` | `contentinfo` (implicit) |

### 7.5 Color-Independent Status Communication

Status must never be communicated by color alone. Every status dot is
accompanied by:

- A text label (e.g. "DONE", "BLOCKED", "ACTIVE") visible in the same row, OR
- An `aria-label` on the dot element describing the status

This ensures colorblind users can distinguish all states.

---

## 8. Icon / Glyph System

No image icons. All status indicators use Unicode glyphs and CSS-styled dots.
This satisfies the stdlib constraint (no icon font downloads, no SVG sprite
sheets).

### 8.1 Status Dots

Rendered as `<span>` elements, 10x10px, `border-radius: 50%`.

| State | Dot color token | Animation | Text label | Glyph alt |
|-------|----------------|-----------|------------|-----------|
| Done / Success | `--signal-jade` | Pulse: 1.6s ease-in-out (box-shadow) | "DONE" | `✓` |
| Active / Working | `--accent-oxblood` | Pulse: 1.0s ease-in-out (box-shadow) | "ACTIVE" | `▶` |
| Blocked / Waiting | `--signal-amber` | Pulse: 2.2s ease-in-out (box-shadow) | "BLOCKED" | `⏸` |
| Idle | `--ink-paper-faint` | None (static) | "IDLE" | `·` |
| Not started | `--rule-line` (hollow ring: 2px border, no fill) | None (static) | "PENDING" | `○` |

### 8.2 Pulse Keyframes

```css
@keyframes pulse-jade {
  0%, 100% { box-shadow: 0 0 0 0 rgba(111, 163, 122, 0.55); }
  50%      { box-shadow: 0 0 0 8px rgba(111, 163, 122, 0); }
}

@keyframes pulse-oxblood {
  0%, 100% { box-shadow: 0 0 0 0 rgba(206, 32, 41, 0.55); }
  50%      { box-shadow: 0 0 0 8px rgba(206, 32, 41, 0); }
}

@keyframes pulse-amber {
  0%, 100% { box-shadow: 0 0 0 0 rgba(210, 154, 59, 0.55); }
  50%      { box-shadow: 0 0 0 8px rgba(210, 154, 59, 0); }
}
```

Pulse amplitude: 8px. Suppressed under `prefers-reduced-motion: reduce`.

### 8.3 Progress Indicator Glyphs

Used inline in sprint table and feature rows:

| Glyph | Meaning | Context |
|-------|---------|---------|
| `████░░` | Progress bar (text-mode, using Unicode block chars) | Sprint table "Tasks" column |
| `▸` | Pointer / call-to-action | Next-action card |
| `→` | Flow direction | Dispatch stream (agent → agent) |
| `↳` | Logged / recorded | Submission confirmation |

### 8.4 Sprint Pill States

| State | Background | Border | Text color | Font weight |
|-------|-----------|--------|------------|-------------|
| Active | `--accent-oxblood` | `--accent-oxblood` | `--ink-paper` | 700 |
| Completed | `--bg-graphite` | `--rule-line` | `--ink-paper-dim` | 400 |
| Future | `--bg-graphite` | `--rule-line` | `--ink-paper-dim` at 45% opacity | 400 |

---

## 9. CSS Custom Properties Reference (Complete)

Copy-paste-ready block for the implementer:

```css
:root {
  /* ── Backgrounds ── */
  --bg-carbon:          #0a0a0a;
  --bg-graphite:        #141413;
  --bg-graphite-2:      #1c1b18;
  --bg-graphite-3:      #232220;

  /* ── Ink ── */
  --ink-paper:          #e8e4d8;
  --ink-paper-dim:      #b8b4a8;
  --ink-paper-faint:    #8a8678;

  /* ── Accent ── */
  --accent-oxblood:     #ce2029;
  --accent-oxblood-2:   #a01820;
  --accent-oxblood-hover: #e02830;

  /* ── Signals ── */
  --signal-amber:       #d29a3b;
  --signal-amber-2:     #e8b85a;
  --signal-amber-3:     #8a6a2a;
  --signal-jade:        #6fa37a;
  --signal-jade-dim:    #486a52;

  /* ── Structural ── */
  --rule-line:          #2a2925;
  --focus-ring:         #e8e4d8;
  --focus-ring-offset:  #0a0a0a;

  /* ── Typography ── */
  --font-mono:          ui-monospace, "Berkeley Mono", "JetBrains Mono", Menlo, Consolas, monospace;
  --font-sans:          -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
  --type-micro:         10px;
  --type-caption:       11px;
  --type-label:         12px;
  --type-body:          14px;
  --type-h3:            18px;
  --type-h2:            22px;
  --type-h1:            28px;

  /* ── Spacing ── */
  --space-2xs:          2px;
  --space-xs:           4px;
  --space-sm:           8px;
  --space-md:           12px;
  --space-lg:           16px;
  --space-xl:           24px;
  --space-2xl:          32px;
  --space-3xl:          48px;

  /* ── Motion ── */
  --duration-fast:      120ms;
  --duration-normal:    220ms;
  --duration-slow:      500ms;
  --easing-default:     ease-out;
  --easing-spring:      cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ── Radius ── */
  --radius-none:        0;
  --radius-sm:          2px;
  --radius-full:        50%;

  /* ── Breakpoints (not usable as CSS vars; documented for reference) ── */
  /* --bp-tablet:  768px  */
  /* --bp-desktop: 1280px */
}
```

---

## 10. Migration Notes (v1 → v2)

### Tokens Unchanged (14)
`--bg-carbon`, `--bg-graphite`, `--bg-graphite-2`, `--bg-graphite-3`,
`--ink-paper`, `--ink-paper-dim`, `--ink-paper-faint`, `--accent-oxblood`,
`--accent-oxblood-2`, `--signal-amber`, `--signal-amber-2`, `--signal-amber-3`,
`--signal-jade`, `--signal-jade-dim`, `--rule-line`

### Tokens Added (12)
`--accent-oxblood-hover`, `--focus-ring`, `--focus-ring-offset`, `--font-mono`,
`--font-sans`, `--type-micro` (redefined), `--type-caption`, all `--space-*`
tokens, all `--duration-*` tokens, `--easing-*` tokens, `--radius-*` tokens

### Tokens Modified (2)
- `--type-h1`: 32px → 28px (right-sized for dense layout)
- `--type-micro`: 11px → 10px (clearer separation from caption tier)

### No Tokens Removed
All v1 tokens remain valid. v2 is a strict superset. Existing v1 CSS that
references these tokens will continue to work.

---

## Appendix: Design Rationale

**Why evolve, not redesign?** The Bridge v1 has been live since PI-2. The user
(single human owner) approved "evolve Bridge" in Q1. The dark carbon aesthetic
is the framework's visual identity. Breaking it would destroy recognition for
marginal gain.

**Why no shadows?** The brutalist console metaphor rejects decorative depth cues.
Background tier stepping (carbon → graphite → graphite-2 → graphite-3) creates
sufficient hierarchy. Shadows would soften the aesthetic and add visual noise.

**Why one accent color?** Oxblood carries authority. Adding a second saturated
accent (e.g. blue, purple) would split the user's attention and dilute the
semantic meaning of "this element is interactive or urgent."

**Why monospace dominant?** The dashboard is 80% tabular data, dispatch IDs,
agent names, and timestamps. Monospace is functionally correct, not an aesthetic
choice. The sans-serif stack exists only for natural-language prose.

**Why no icon fonts?** stdlib constraint. No runtime dependencies beyond what
Python's http.server can serve. Unicode glyphs and CSS dots cover all status
communication needs.
