---
name: design-tokens
description: >
  Use when authoring or reviewing design token files (DESIGN_TOKENS.md). Enforces
  the framework's visual token structure: semantic color palette, modular type scale,
  spacing scale, motion principles, accessibility contract. Ensures tokens are
  implementable as CSS custom properties and maintain WCAG 2.1 AA compliance.
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
  origin: LESSON-007 (PI-3/S3 DEFER, shipped S4)
---

# Design Tokens

Canonical reference for authoring, reviewing, and evolving `DESIGN_TOKENS.md` files.
Tokens are the visual contract between the UI Designer (who specs them) and the
Software Developer (who implements them as CSS custom properties).

---

## When to Use

Load this skill when:
- Authoring a new `DESIGN_TOKENS.md` for a UI spec
- Evolving an existing token file (adding tokens, changing values)
- Reviewing a mockup or spec for token compliance
- Running a pre-spec design exploration to discover visual vocabulary

Do NOT load when:
- Implementing tokens as CSS custom properties (that is developer work)
- Working on backend logic, state builders, or data pipelines
- Making content decisions (what data to show -- PM owns that)

---

## The LESSON-007 Pattern

> "Design exploration before spec produces tokens that transfer to the formal
> spec at near-zero cost."

Before entering the formal `/spec` phase for any UI feature, run a lightweight
design exploration using `gem-designer` or `ux-designer-general`. The goal is to
discover the color palette, type scale, and spacing vocabulary early. These
tokens transfer directly into the spec's `DESIGN_TOKENS.md` with minimal rework.

Sequence: **explore first, then spec.**

---

## Token Structure (8 Sections)

Every `DESIGN_TOKENS.md` must contain exactly these sections, in this order:

### 1. Color Palette
- **Backgrounds** -- page, surface, elevated surface
- **Ink** -- primary text, secondary text, muted text
- **Accent** -- primary action, hover/active states
- **Signals** -- success, warning, error, info
- **Structural** -- borders, dividers, focus rings
- **Semantic aliases** -- map every token to a CSS custom property name
  (e.g. `--color-bg-page`, `--color-ink-primary`)

### 2. Type Scale
- Named modular ratio (minor third 1.200, major third 1.250, etc.)
- Font stacks: monospace primary, system sans fallback
- Weights: regular (400), medium (500), semibold (600), bold (700)
- Line heights per scale step

### 3. Spacing Scale
- Base unit: **4px**
- Named tokens: `--space-xs` (4px), `--space-sm` (8px), `--space-md` (16px),
  `--space-lg` (24px), `--space-xl` (32px), `--space-2xl` (48px)
- Additional tokens are additive; document any beyond the base set

### 4. Layout Grid
- Breakpoints (compact, default, wide) with pixel thresholds
- Grid template for the primary layout (sidebar + main, zones, etc.)
- Max content width

### 5. Motion Principles
- Duration tokens: `--duration-fast` (120ms), `--duration-normal` (200ms),
  `--duration-slow` (350ms)
- Easing function (e.g. `cubic-bezier(0.4, 0, 0.2, 1)`)
- What animates: opacity, transform, color. Never layout properties.
- All transitions gated by `prefers-reduced-motion`

### 6. Elevation / Depth
- Background tiers (page < surface < elevated)
- Border treatments per tier
- No box-shadow unless explicitly justified

### 7. Accessibility Contract
- Contrast targets: body text >= 7:1, large text >= 4.5:1, UI components >= 3:1
- Focus ring: 2px solid, high-contrast color, 2px offset
- Keyboard navigation: logical tab order documented per layout zone
- Screen reader: landmark roles, live regions for dynamic content

### 8. Icon / Glyph System
- Status indicators (dots, Unicode glyphs, emoji fallbacks)
- Size tokens aligned to type scale
- Color inheritance from parent text

---

## Rules

1. **Semantic names required.** Every color is `--color-{category}-{role}`,
   never a raw hex value in specs or mockups.

2. **Contrast documented.** Every color token states its contrast ratio against
   `--color-bg-page`. Use the format: `#1e1e2e (ink-primary, 15.4:1 on bg-page)`.

3. **Accent constraint.** Accent colors below 4.5:1 contrast must document
   their usage constraint: "large text only (>=18px)" or "decorative / non-text".

4. **Named ratio.** The type scale must declare a named ratio. Do not use
   arbitrary font sizes without a scale relationship.

5. **4px base.** All spacing tokens are multiples of 4px. No odd-pixel values.

6. **Reduced-motion gate.** Every `transition` or `animation` token must
   include a `prefers-reduced-motion: reduce` override that disables or
   shortens the motion.

7. **CSS custom properties.** Tokens must be expressible as `--token-name: value`.
   No Sass variables, Less variables, or JS theme objects.

8. **Additive only.** New tokens can be added freely. Removing or renaming a
   token requires a migration note in the Migration Notes section.

9. **AA baseline.** The token file must not introduce any color pairing that
   violates WCAG 2.1 AA. If a pairing is decorative, document it explicitly.

---

## Migration Notes Section

Every `DESIGN_TOKENS.md` must end with a `## Migration Notes` section containing:

```markdown
## Migration Notes (vX.Y -> vX.Z)

### Unchanged
- List tokens carried forward without changes

### Added
- `--new-token`: value -- reason for addition

### Modified
- `--changed-token`: old-value -> new-value -- reason

### Removed
- `--removed-token`: old-value -- migration path (what replaces it)
```

For the first version, use `## Migration Notes (v1.0 -- initial)` and mark all
tokens as new.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Raw hex without semantic name | Assign `--color-{category}-{role}` name first |
| Skipping contrast verification | State ratio for every color token |
| Mixing `px` and `rem` in the same scale | Pick one unit per scale; document the conversion |
| Forgetting `prefers-reduced-motion` gate | Add override for every transition/animation token |
| Treating tokens as implementation | Tokens are the **spec**, not the CSS file. The developer implements them. |
| Choosing font sizes without a ratio | Declare the ratio name, derive sizes from it |
| Removing a token without migration note | Add a Migration Notes entry with the replacement path |

---

## Checklist (use before locking a token file)

- [ ] All 8 sections present and in order
- [ ] Every color has a semantic name and documented contrast ratio
- [ ] Type scale names a modular ratio
- [ ] Spacing uses 4px base, no odd values
- [ ] Motion tokens have `prefers-reduced-motion` gate noted
- [ ] All tokens use CSS custom property naming (`--category-role`)
- [ ] Migration Notes section present
- [ ] No AA violations in any documented color pairing
