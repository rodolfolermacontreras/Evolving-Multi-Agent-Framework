# ADR-023: Dashboard render stays stdlib-only via string.Template

- Date: 2026-06-26
- Status: accepted (owner ratified 2026-07-07 at Sprint 17 close, F-46)

## Context

`state_builder.py` has grown to ~4153 lines (~79 functions). Two of its render
functions are very large: `render_markdown` (762 lines, non-locked) and
`render_html` (658 lines, locked under Article X / `TestS1FootprintLockGuard`).
Both are effectively single f-string "walls" -- long interpolated string blocks
that are hard to read, diff, and review.

SDD-048 item C-2 ("right-size the stdlib-only rule") asks whether the framework
should keep paying the readability cost of stdlib-only string building, or adopt
a templating library (Jinja2, etc.) to make the render surface maintainable.

This is a genuine architectural fork because it touches Article V (stdlib-only):
the framework deliberately ships zero third-party dependencies so it can be
dropped into any host project without a dependency-resolution step, and so its
CI is a pure `setup-python` + validation run (see ADR-021). A templating library
would buy ergonomics at the cost of that property.

A complication: `render_html` is one of the five Article X S1-footprint locked
functions. Its source bytes are pinned to commit `257b081` via golden SHA-256
hashes. It cannot be refactored without an owner-ratified Article X re-baseline,
which is explicitly out of scope for SDD-048.

## Decision

Keep the dashboard render **stdlib-only**. Factor the NON-locked render surface
(`render_markdown` and the non-locked HTML injectors) into `string.Template`-based
section helpers. Do NOT introduce a third-party templating dependency.

Concretely:
- Each large interpolated block becomes a module-level `string.Template` constant
  filled by a small named helper via `substitute` / `safe_substitute`.
- This is applied to `render_markdown` (decomposed into per-section helpers under
  ~120 lines each) and the non-locked HTML helpers/injectors.
- `render_html` (locked) is EXEMPT. It stays byte-identical in `state_builder.py`
  and remains the single documented Article X exception to the ~120-line target.

## Options Considered

### Option A: Adopt a templating library (Jinja2)
- Pros: idiomatic templates, separation of markup from logic, mature tooling.
- Cons: breaks Article V (first third-party runtime dependency); adds an install
  step to every host bootstrap and to CI; larger supply-chain surface; still
  cannot touch the locked `render_html` without a re-baseline, so it would only
  cover part of the surface anyway.

### Option B: Keep stdlib, factor with `string.Template` (CHOSEN)
- Pros: preserves Article V and the zero-dependency promise; CI stays a pure
  validation run; `string.Template` is enough to break the f-string walls into
  reviewable named helpers; no re-baseline needed; composes cleanly with C-1's
  module split.
- Cons: `string.Template` is less expressive than a real template engine (no
  loops/conditionals inside the template -- those stay in Python helpers);
  `render_html` remains a locked exception that this ADR cannot fix.

### Option C: Leave the render walls as-is
- Pros: zero work, zero risk.
- Cons: fails C-2's maintainability goal; the 762-line `render_markdown` stays an
  unreadable wall; does not satisfy C-1's ~120-line target for non-locked code.

## Consequences

Positive:
- Article V holds: the framework remains stdlib-only and drop-in portable; CI is
  unchanged (no dependency install).
- The non-locked render surface becomes a set of small, named, diff-friendly
  helpers, satisfying C-1's ~120-line target and C-2's "no f-string wall" goal
  for everything that is allowed to change.
- The decision composes with the C-1 module split (helpers land in
  `state_builder_markdown.py` and `state_builder_html.py`).

Negative:
- `render_html` (locked) is NOT improved by this decision; the "no 700-line wall"
  outcome honestly applies to the NON-locked surface only. This trade-off is
  recorded explicitly so the win is not overstated.
- `string.Template`'s limited logic means control flow stays in Python rather than
  in markup; contributors accustomed to Jinja-style templates must adjust.

Neutral:
- A future owner-ratified Article X re-baseline could later factor `render_html`
  the same way; this ADR neither requires nor blocks that.

## Compliance

- [x] No new dependencies (stdlib `string.Template` only) -- Article V preserved.
- [x] Backward compatible: render output is byte-equivalent (pure refactor).
- [ ] Tests updated to cover new pattern -- N/A for design; F-45 keeps the suite
      green at 546/2 with no assertion changes (pure refactor; output byte-equivalent).
- [x] No convention change to `.github/copilot-instructions.md` required.
- Note: Status is **proposed** at F-44 (design). The owner ratifies to **accepted**
  at SDD-048 close (F-46) after the factoring is implemented and verified.
