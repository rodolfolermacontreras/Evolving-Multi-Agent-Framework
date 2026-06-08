# UI Lifecycle Variant (SDD-018, Article XII candidate)

A guide for using the **opt-in** UI Lifecycle Variant of Article X. Use this
variant only for iterative visual / UI work where the validation contract
must legitimately evolve during implementation. Back-end, CLI, schema, and
constitution work continue under unmodified Article X (strict
pre-implementation lock).

Companion to:

- Spec: [`../specs/2026-06-09-ui-lifecycle-variant/spec.md`](../specs/2026-06-09-ui-lifecycle-variant/spec.md)
- ADR: [`./ADR/014-ui-lifecycle-variant.md`](./ADR/014-ui-lifecycle-variant.md)
- Constitution (when Article XII lands): `../constitution/principles.md`
- Validator: [`../cli/schema_lint.py`](../cli/schema_lint.py) function
  `check_validation_variant`

---

## When to use the variant

Opt in when ALL of the following are true:

1. The feature is iterative visual / UI work (dashboard panel, layout,
   widget, palette, type scale, motion timing).
2. The REQUIRED items in `validation.md` cannot be honestly enumerated
   before implementation begins -- some only surface after rendering
   against real data.
3. You expect cascading visual decisions to add REQUIRED items mid-flight
   (e.g. spacing token chosen in week 1 forces a new "card padding stays
   on the 8px grid" REQUIRED for the panel in week 2).

Opt OUT (i.e. stay with strict Article X) when ANY of the following is true:

- The feature is back-end logic, CLI, schema, or constitution work.
- You can enumerate REQUIRED items up front and they are unlikely to
  change.
- You only need a couple of post-lock additions and the override path
  (friction analysis + amending commit) is acceptable.

The variant is opt-in per spec dir, not project-wide. There is no global
Article X loosening.

---

## How to opt in

Add one line to your spec's frontmatter:

```yaml
---
id: SDD-NN-spec
type: spec
status: active
owner: principal-architect
updated: YYYY-MM-DD
ui-variant: true
---
```

That's it. The marker is the only opt-in switch. `cli/schema_lint.py`
detects the marker, and from that point on dispatches the spec dir's
`validation.md` to the variant validator. Other spec dirs are unaffected.

### Marker syntax rules

- The key is `ui-variant` (lowercase, hyphenated).
- The value MUST be exactly `true` or `false` (case-insensitive).
  Anything else (`yes`, `1`, `True!`, empty) produces a `[delta]` lint
  error.
- Absent key = same as `false` = strict Article X behavior.
- The marker lives on `spec.md` only; do not duplicate it on `plan.md`,
  `tasks.md`, or `validation.md`.

---

## Delta entry schema

Once the marker is set, you may append a `## Delta Entries` section to
your `validation.md`. Each entry is a level-3 sub-section in this exact
shape:

```markdown
## Delta Entries

### Delta DE-01 -- short descriptive title

- timestamp: 2026-MM-DDTHH:MMZ
- author: principal-{role}
- rationale: one-sentence reason this delta is being added
- item-type: add | wontfix | re-check | retroactive-demo

Free Markdown body. May include checkboxes, code blocks, and links.
This is where the new REQUIRED item, the wontfix note, the re-check
decision, or the retroactive-demo record actually lives.
```

### Field reference

| Field | Required | Format | Notes |
|-------|----------|--------|-------|
| heading | yes | `### Delta DE-NN -- {title}` | DE-NN is zero-padded two-digit, monotonically increasing across the file, never re-used. |
| `timestamp` | yes | `YYYY-MM-DDTHH:MMZ` or `YYYY-MM-DDTHH:MM:SSZ` | ISO 8601 UTC. Lint rejects other formats. |
| `author` | yes | `principal-{role}` or worker identity | The agent or human who recorded the delta. |
| `rationale` | yes | one sentence | Why this delta is being added. |
| `item-type` | yes | closed enum (see below) | Drives downstream behavior. |
| body | yes (any non-empty content) | Markdown | The actual new REQUIRED item, note, or record. |

### The four `item-type` values and when to use each

- **`add`** -- you are adding a new REQUIRED item to the contract. The
  body should be the checkbox-formatted REQUIRED item itself (e.g.
  `- [ ] Sidebar columns auto-collapse below 1024px viewport width`).
  Article X rule 3 (zero unchecked REQUIRED at done) applies to the
  new item just like any other.
- **`wontfix`** -- you are annotating an existing REQUIRED item that
  you have decided not to ship. The original item stays in the contract
  (do NOT delete it). The body explains the reasoning. The annotated
  item remains under Article X rule 3 unless a follow-on `re-check`
  delta explicitly reclassifies it.
- **`re-check`** -- you want the contract re-verified without rewriting
  it (typical use: an existing REQUIRED item changed environment but
  the contract text is still correct). The body surfaces this as a
  manual-check task at REVIEW.
- **`retroactive-demo`** -- the **single sanctioned exception** for the
  SDD-018 proof case. The `schema_lint` allow-list hard-codes the only
  spec dir permitted to use this value:
  [`specs/2026-05-16-state-dashboard/`](../specs/2026-05-16-state-dashboard/).
  Any other spec dir using `retroactive-demo` produces a `[delta]`
  error: `retroactive-demo permitted only for SDD-018 proof case`.

---

## Append-only enforcement

Delta entries are append-only across commits. Specifically:

- Once a DE-NN entry lands in a commit, its mandatory fields
  (`timestamp`, `author`, `rationale`, `item-type`) MUST NOT be edited
  in any subsequent commit.
- Once a DE-NN entry lands in a commit, it MUST NOT be deleted.
- New DE-NN entries may be appended at any time (DE-02 after DE-01,
  DE-03 after DE-02, and so on).
- DE-NN IDs MUST be monotonically increasing and never re-used. If you
  change your mind about DE-02, you do not edit DE-02; you append DE-03
  with `item-type: re-check` referencing DE-02 in its body.

The enforcement mechanism is `cli/schema_lint.py`'s parse-time monotonic
check plus a `git show HEAD:<validation.md>` comparison against the
last-committed file state. If a previously committed DE-NN entry's
mandatory field changed, or the entry was deleted, `schema_lint` emits
a `[delta]` error and exits non-zero.

Practical implication: **the first DE-NN entry for any variant spec dir
must land in a single commit**. You cannot stage half of DE-01 in one
commit and finish it in the next. Once committed, the entry is frozen.

---

## Forward-only migration

The variant does NOT back-port to pre-SDD-018 spec dirs. The lone
exception is the retroactive-demo target
([`specs/2026-05-16-state-dashboard/`](../specs/2026-05-16-state-dashboard/)),
hard-coded in `schema_lint.py`'s allow-list. No other historical UI
spec dir is migrated as part of SDD-018. If a future PI decides to
retro-migrate `specs/2026-05-26-live-ui-v2/` or another historical
spec dir, that requires a new ADR amending the allow-list -- a Level-2
decision, not an authoring change.

---

## State-dashboard demo reference

The SDD-018 proof case lives at
[`../specs/2026-05-16-state-dashboard/`](../specs/2026-05-16-state-dashboard/):

- `spec.md` carries `ui-variant: true` in its frontmatter.
- `validation.md` carries one DE-01 entry with
  `item-type: retroactive-demo`, recording the v0.1 -> v0.2 static-to-live
  pivot already captured in the file's pre-existing
  `## v0.2 additions (2026-05-16, post user UX feedback)` subsection
  and in the spec dir's `RETRO.md` "v0.2 Addendum".

The original `## v0.2 additions` subsection was NOT deleted by the
migration; it remains as the historical narrative. The DE-01 entry is
the variant's sanctioned representation of the same historical event.
Treat this as the canonical worked example when you write your own
delta entries.

---

## `[delta]` lint error reference

All variant-originated findings carry the `[delta]` prefix in both
human-readable and JSON output. Common messages:

- `[delta] ui-variant marker must be 'true' or 'false'; saw '...'`
  -- malformed marker value on `spec.md`.
- `[delta] DE-NN missing mandatory field 'X'` -- a required delta
  field is absent or empty.
- `[delta] DE-NN item-type 'X' not in enum [...]` -- unknown
  `item-type` value.
- `[delta] DE-NN timestamp 'X' is not ISO 8601 UTC` -- timestamp
  shape rejected.
- `[delta] DE-NN not monotonically increasing (prior was DE-MM)` --
  IDs must rise.
- `[delta] DE-NN duplicated in this file (IDs MUST be unique)` --
  do not re-use IDs.
- `[delta] DE-NN retroactive-demo permitted only for SDD-018 proof
  case (spec dir 'X' not in allow-list)` -- you tried to use the
  retroactive-demo type outside the one allow-listed spec dir.
- `[delta] DE-NN field 'X' modified (append-only violation: ...)` --
  you edited a previously committed delta.
- `[delta] DE-NN deleted (append-only violation: ...)` -- you
  removed a previously committed delta.

Non-variant spec dirs produce zero `[delta]` findings. If you see a
`[delta]` finding on a spec dir you did not opt in, check `spec.md`
for an accidental `ui-variant: true` line.

---

## Worked example

A hypothetical Sprint Burndown widget (`specs/2026-06-15-burndown-widget/`)
that opted in:

```yaml
# spec.md frontmatter
---
id: SDD-BURNDOWN-spec
type: spec
status: active
owner: principal-ui-designer
updated: 2026-06-15
ui-variant: true
---
```

```markdown
# validation.md (after a couple of weeks of implementation)

- [x] R-1 Widget renders ideal-line vs actual-line for the current sprint
- [x] R-2 Tooltips show day-by-day point values on hover
- [x] R-3 Renders empty-state when ledger has zero completed tasks

## Delta Entries

### Delta DE-01 -- color-blind safe palette

- timestamp: 2026-06-22T14:30Z
- author: principal-ui-designer
- rationale: ideal-line and actual-line currently collide for protanopia (red-green) viewers; ship-blocker per QA pass
- item-type: add

- [ ] R-4 Lines distinguishable for protanopia and deuteranopia: lint
  passes WCAG AAA contrast and shape differentiation (solid vs dashed)
```

Once committed, DE-01 is frozen. If a downstream QA cycle revisits the
palette choice, the operator appends DE-02 with `item-type: re-check`
referencing DE-01 -- never edits DE-01 in place.

---

## `status: blocked` is the framework's CLARIFY-phase carrier

SDD-018's CLARIFY round surfaced a friction point: the SDD-FDC-001
`status` enum (`{draft, active, blocked, done, superseded, archived}`)
contains no `clarify` value. Per owner direction 2026-06-08, the
framework uses `status: blocked` as the carrier while a spec dir's
CLARIFY round is open, transitioning to `status: active` once CLARIFY
closes and to `status: done` at REVIEW close. The enum itself is NOT
amended.

This convention applies to all spec dirs (variant and strict alike) and
is documented here because authoring guidance for UI work tends to land
in spec dirs that exercise the CLARIFY phase heavily.

---

## What this variant does NOT do

- It does not amend Article X for non-UI features.
- It does not amend Article XI (the serial CLARIFY/SPEC gate).
- It does not amend Article VII (one feature, one session).
- It does not introduce a `/spec-ui` slash command (deferred to P3,
  SDD-035 if filed).
- It does not loosen REQUIRED items already locked in pre-SDD-018 spec
  dirs (those remain Article-X-strict; back-porting is forbidden).
- It does not auto-amend `constitution/principles.md`. The Article XII
  text proposed in [`./ADR/014-ui-lifecycle-variant.md`](./ADR/014-ui-lifecycle-variant.md)
  becomes binding only when the owner accepts it in a separate
  Level-2 commit.

---

## Cross-references

- Spec: [`../specs/2026-06-09-ui-lifecycle-variant/spec.md`](../specs/2026-06-09-ui-lifecycle-variant/spec.md)
- Validation: [`../specs/2026-06-09-ui-lifecycle-variant/validation.md`](../specs/2026-06-09-ui-lifecycle-variant/validation.md)
- Plan: [`../specs/2026-06-09-ui-lifecycle-variant/plan.md`](../specs/2026-06-09-ui-lifecycle-variant/plan.md)
- Tasks: [`../specs/2026-06-09-ui-lifecycle-variant/tasks.md`](../specs/2026-06-09-ui-lifecycle-variant/tasks.md)
- ADR-014 (proposed): [`./ADR/014-ui-lifecycle-variant.md`](./ADR/014-ui-lifecycle-variant.md)
- ADR-013 (Article XI precedent): [`./ADR/013-serial-clarify-spec-gate.md`](./ADR/013-serial-clarify-spec-gate.md)
- Demo target: [`../specs/2026-05-16-state-dashboard/`](../specs/2026-05-16-state-dashboard/)
- Validator entry point: [`../cli/schema_lint.py`](../cli/schema_lint.py)
  (`check_validation_variant`)
- Test coverage: [`../cli/test_schema_lint_variant.py`](../cli/test_schema_lint_variant.py)
