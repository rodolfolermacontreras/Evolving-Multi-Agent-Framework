---
id: SDD-20260609UIVARIANT-clarification
type: clarification
status: active
owner: principal-product-manager
updated: 2026-06-09
feature: 2026-06-09-ui-lifecycle-variant
---

# CLARIFY: UI Lifecycle Variant (SDD-018)

- Date: 2026-06-09
- Authors: Principal Product Manager + Principal Architect (jointly)
- Status: ACTIVE -- awaiting owner answers
- Spec ID: SDD-018
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7), F-10 pass 1 of 2
- Gating: /spec finalization, validation contract lock, /plan, ADR
  drafting (if Q-F confirms), and any `constitution/` edit are ALL
  blocked until these answers are recorded and the Executive Manager
  commits this file.

---

## Ground Rules

- One question at a time is the **author** discipline -- the questions
  below are pre-staged so the owner can answer in a single round, but
  the owner may answer them one at a time across multiple sessions if
  preferred.
- PM and Architect each give a recommendation. Where they agree, a
  **Joint recommendation** is recorded. Where they disagree, both
  positions are stated honestly and the owner picks. Divergences are
  called out in the F-10 pass 1 final report so the Executive Manager
  can surface them at executive register.
- This file is the **only** source of truth for SDD-018 design
  decisions. Anything decided in chat or hallway must be back-filled
  here before the spec finalizes.

---

## Scope

### Q1: Which Article X rules relax for the UI variant?

**Context**: Article X ("Validation Is a Pre-Implementation Contract")
in `constitution/principles.md` v1.0.0 contains three operative rules
that together constitute the validation-as-contract discipline:

1. **Lock timing**: `validation.md` is LOCKED at `/tasks` time
   (before any implementation begins).
2. **No-loosening clause**: REQUIRED items cannot be loosened after
   lock without an explicit decision recorded in the contract itself
   (i.e. an audit-trail edit, not a silent edit).
3. **Required-completeness rule**: zero unchecked REQUIRED items before
   implementation is considered complete.

SDD-018's premise is that one or more of these is too strict for
iterative UI work. We need an explicit per-rule decision -- "relax all
of Article X for UI" is too broad and would re-introduce the very
discipline gap that Article X exists to close.

**PM recommendation**: Relax **rule 2 only** (the no-loosening clause)
via a structured `delta` mechanism. Keep rule 1 (lock at `/tasks`) and
rule 3 (zero unchecked REQUIRED items at done). Rationale: the friction
in the PI-3/PI-4 dashboard work was not that requirements were locked
too early -- it was that **new** requirements emerged during
implementation and had no sanctioned add-after-lock path. A delta
mechanism that lets new REQUIRED items be appended (with timestamp +
rationale + author) preserves the contract discipline (every item is
still locked the moment it's added; rule 3 still applies at done) while
removing the friction.

**Architect recommendation**: Same as PM -- relax rule 2 only, via a
delta mechanism. Additional architectural note: the delta mechanism
should be **append-only** (you can add a new REQUIRED item, you can
add a `wontfix` note against an existing one with rationale, but you
cannot silently delete or rewrite a previously locked item). This
keeps `schema_lint` semantics simple and preserves the git-diff audit
trail.

**Joint recommendation**: **Relax rule 2 only**, via an append-only
delta mechanism. Rules 1 and 3 stay firm. The delta is itself part of
the contract -- every delta entry is locked the moment it's added.

**Status**: OPEN
**Answer**: (pending owner)

---

### Q2: What replaces the relaxed rule -- delta field, separate command, opt-in marker, or hybrid?

**Context**: Assuming Q1 lands on "relax rule 2 via a delta mechanism",
there are three implementation shapes (plus combinations):

- **(a) Delta field/section in `validation.md`**: add an optional
  `## Delta Entries` section to the existing `validation.md` template.
  Each delta entry is a markdown sub-section with frontmatter-like
  fields (timestamp, rationale, author, item-type [add | wontfix |
  re-check], item body). `schema_lint` recognizes the section and
  enforces its shape. Spec dirs without the section behave exactly as
  today (full Article X). Spec dirs WITH the section + the opt-in
  marker (see Q-C) get the variant.
- **(b) Separate `/spec-ui` slash command**: a new prompt under
  `.github/prompts/spec-ui.prompt.md` that scaffolds spec dirs with a
  different `validation.md` template (one that has `delta` baked in).
  Spec dirs scaffolded by the standard `/spec` command stay Article X
  strict.
- **(c) Opt-in marker on the spec dir**: a frontmatter field (e.g.
  `ui-variant: true`) on `spec.md`. When set, `schema_lint` applies
  the variant rules. No new template, no new command.
- **(d) Hybrid**: marker + delta field, with the slash command
  optional convenience scaffolding.

**PM recommendation**: **(d) hybrid -- marker + delta field; defer
the `/spec-ui` slash command to a P3 backlog item.** Rationale: the
marker (Q-C) is the **policy** signal (one bit: "this spec dir is a
UI variant"); the delta section is the **data** signal (the actual
post-lock additions). Coupling them is the simplest mental model for
the spec author ("set the marker, get the delta section"). A separate
slash command duplicates scaffolding logic for marginal author
convenience -- can be added later if friction emerges. Hybrid keeps
the variant inside the existing `/spec` flow, which is one fewer
command to teach future framework adopters (SDD-016 brownfield
target).

**Architect recommendation**: **(d) hybrid is also my preference,
with one architectural refinement: the marker should be a
**boolean-shaped string** (`ui-variant: true`), not a free-form
string field, so `schema_lint` can validate it deterministically.**
The delta section should use the **same frontmatter-style key:value
shape** the rest of the framework uses (SDD-FDC-001 / ADR-012); do
NOT invent a new mini-DSL for delta entries.

**Joint recommendation**: **(d) hybrid -- `ui-variant: true`
frontmatter marker on `spec.md` (validated by `schema_lint` as a
boolean string), plus an append-only `## Delta Entries` section in
`validation.md` (each entry as a sub-section with timestamp +
rationale + author + item-type + item-body fields). DEFER `/spec-ui`
slash command to a P3 backlog item.**

**Status**: OPEN
**Answer**: (pending owner)

---

### Q3: Opt-in granularity -- per spec dir, or globally per path?

**Context**: PI-5 risk register says: "Mitigated -- opt-in via a
marker on the spec dir." That phrasing is per-dir. But there's a real
alternative: globally opt-in any spec dir whose path matches a
designated pattern (e.g. anything under
`specs/*-dashboard/` or `specs/*-ui-*/`). The two options trade
explicitness (per-dir) for friction-removal (global).

**PM recommendation**: **Per spec dir.** Rationale: the marker is a
discipline signal that the spec author actively chose to opt into the
variant. Globally opting-in by path makes the variant the default for
anything that *looks* like UI work, which is exactly the leakage risk
the PI-5 risk register flags. Per-dir is more typing for the author
(one frontmatter line) but the explicit choice IS the discipline.

**Architect recommendation**: **Per spec dir, same as PM.** Path-based
matching also creates a maintenance trap: as soon as a spec dir is
renamed, the variant silently activates or deactivates. The marker
field travels with the spec dir wherever it goes (rename, move, copy
for a new project bootstrap via SDD-016) and is grep-able. Path
patterns are not grep-able cleanly without knowing the pattern.

**Joint recommendation**: **Per spec dir, via the `ui-variant: true`
marker in `spec.md` frontmatter.** Confirms the PI-5 risk register
mitigation as written.

**Status**: OPEN
**Answer**: (pending owner)

---

### Q4: How do delta entries flow through `schema_lint`?

**Context**: `cli/schema_lint.py` is the framework's machine-checkable
artifact discipline. It validates frontmatter shape, checkbox
completeness, and required-section presence across `agent.md`,
`prompt.md`, `SKILL.md`, `spec.md`, `validation.md`, and friends. The
linter currently treats `validation.md` as a single fixed schema.
Two design paths for the variant:

- **(a) Linter recognizes the marker and applies a different rule
  set.** If `spec.md` has `ui-variant: true`, the linter (for that
  spec dir's `validation.md`) accepts a `## Delta Entries` section,
  validates each delta entry's shape, and applies the "rule 3 still
  fires at done" check across both base REQUIRED items AND delta
  entries.
- **(b) Linter stays strict; the variant simply tolerates more
  `[ ]` boxes at `done` status.** I.e. the variant is a docs-only
  convention; the linter doesn't know about it.

**Architect recommendation (leads this answer)**: **(a) Linter
recognizes the marker.** Rationale: option (b) makes the variant a
discipline gap (the linter cannot tell the difference between "this
is a legitimate variant" and "this spec dir is broken"), which is
exactly the gap Article X exists to close. The linter MUST be the
enforcement floor for both the base contract AND the variant.
Implementation: a new code path in `schema_lint.validate_spec_dir`
that checks for the marker once at the top, then dispatches to the
variant validator OR the strict validator. Shared sub-validators
across both paths (frontmatter shape, item shape) stay
single-implementation -- this is not a fork, it's a marker-gated
extension.

**PM recommendation (user-impact lens)**: **Agree with Architect on
(a).** Additional user-impact note: the lint failure messages for
delta entries must be **as clear as the messages for base REQUIRED
items**. The spec author should never have to guess whether a failure
is "delta entry malformed" vs "base REQUIRED item missing." Concrete
ask: prefix lint errors that originate in delta validation with
`[delta]`.

**Joint recommendation**: **(a) Linter recognizes the marker.** New
code path in `schema_lint.validate_spec_dir` that marker-gates the
variant validator. Shared sub-validators stay single-implementation.
Delta-related lint errors must be prefixed `[delta]` for author
clarity.

**Status**: OPEN
**Answer**: (pending owner)

---

### Q5: Which PI-3 / PI-4 dashboard change is the retroactive validation target?

**Context**: PI-5 CURRENT_PI.md Sprint 3 success criteria says: "one
retroactive validation on a PI-3 dashboard change demonstrates the
workflow." We need to name the specific spec dir whose `validation.md`
will be retroactively reformatted to use the new variant (marker +
delta entries), to prove the workflow against real prior art before
any new UI feature adopts it.

Candidates surfaced by the F-10 pass 1 dedup scan (see Cross-Feature
Notes in [`spec.md`](./spec.md)):

- **C1**: [`specs/2026-05-26-live-ui-v2/`](../2026-05-26-live-ui-v2/)
  -- PI-3/S4 design + PI-4 implementation; full UI redesign with
  Principal UI Designer ownership; the canonical "the validation
  contract had to evolve during implementation" case.
- **C2**: [`specs/2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
  -- earliest dashboard spec dir (`cli/state_builder.py` + initial
  `exec/state.html`); RETRO.md explicitly notes the "static -> live"
  mid-implementation pivot, which is exactly the kind of post-lock
  evolution the variant is designed to absorb.
- **C3**: [`specs/2026-05-16-dashboard-about-and-freshness/`](../2026-05-16-dashboard-about-and-freshness/)
  -- SDD-009 + SDD-010 bundled; smaller scope; was CLARIFY-gated on
  three data-freshness options.

**PM recommendation**: **C1 (`2026-05-26-live-ui-v2/`).** Rationale:
it is the most-explicit prior-art match -- a full UI feature with
dedicated Principal UI Designer ownership, Design Tokens, mockup,
multi-week implementation across PI boundaries. Retro-validating it
demonstrates the variant against the hardest case. If the variant
works for live-ui-v2, it works for any future dashboard iteration.

**Architect recommendation**: **C2 (`2026-05-16-state-dashboard/`)
as primary; C1 as stretch.** Rationale: C2 has the cleanest
"static -> live" mid-implementation pivot story documented in its
RETRO.md, which is the single most photogenic example of "the
contract had to evolve" the framework has. It's also smaller in
scope (one CLI + one HTML template) which makes the retroactive
rewrite a faithful demonstration rather than a heavy backfill. C1
is bigger and would teach the variant under heavier load -- valuable
but better as a follow-up. The Architect's vote: **C2 first, C1
later if C2 is informative.**

**PM/Architect divergence**: Yes -- PM votes C1 (canonical case),
Architect votes C2 (cleanest demo). **Owner adjudicates.** Both are
valid; the choice is risk-appetite: prove the variant under hardest
case (PM) vs prove the variant via cleanest demo (Architect).

**Status**: OPEN
**Answer**: (pending owner)

---

### Q6: Constitutional path -- Article X amendment, new Article XII, or neither?

**Context**: Depending on the answers to Q1-Q4, the variant either
modifies Article X, sits beside Article X as a new article, or lives
entirely in spec / process conventions with no `constitution/` edit.

- **Path A: Article X amendment.** Edit `constitution/principles.md`
  Article X to add an explicit "UI variant" carve-out clause. Bump
  Article X minor version (1.0.0 -> 1.1.0). Document via new ADR (next
  available is ADR-014).
- **Path B: New Article XII (UI Lifecycle Variant).** Leave Article
  X untouched. Add new Article XII that declares the variant,
  references Article X, and defines the marker + delta mechanism.
  Same precedent as Article XI (sat beside existing articles rather
  than modifying them). Bump `constitution/principles.md` minor
  version (1.2.0 -> 1.3.0). Document via new ADR-014.
- **Path C: No constitution edit.** The variant lives entirely in
  `schema_lint.py` + `templates/validation.md` + `templates/spec.md`
  + a new docs page (e.g. `docs/UI-LIFECYCLE-VARIANT.md`). Article X
  is read by the framework as "the strict rule; here is the
  process-level carve-out." No ADR required (process change, not
  architectural change).

**PM recommendation**: **Path B -- new Article XII.** Rationale:
this is a constitutional change in substance (it changes what the
framework requires of a class of features), and Article XI just
proved that "new article beside existing article" is a clean
precedent. Path A makes Article X harder to read (it accumulates
carve-out clauses); Path C is too quiet -- a future framework adopter
reading `constitution/principles.md` would not learn the variant
exists. **Recommend ADR-014 to accompany the new article.**

**Architect recommendation**: **Path B as primary; Path C as
fallback.** Rationale: same logic as PM on Path B. The Architect's
nuance: if CLARIFY Q1-Q4 collectively turn out to be "smaller than
expected" (e.g. only a marker + a docs convention, no `schema_lint`
change), Path C becomes defensible and Path B becomes ceremony. The
test: **if the variant changes the framework's enforcement surface
(`schema_lint` rule, fleet.py behavior, prompt scaffolding), it is
constitutional and Path B applies. If it changes only documentation
and templates, Path C applies.** Given the joint recommendations on
Q1-Q4 above (which DO include a `schema_lint` change), the Architect
also recommends Path B and ADR-014.

**Joint recommendation**: **Path B -- new Article XII, accompanied by
ADR-014.** Conditional: if the owner amends any of Q1-Q4 such that the
variant no longer touches `schema_lint`, the Architect re-evaluates
and may downgrade to Path C.

**Status**: OPEN
**Answer**: (pending owner)

---

### Q7: What is the first real UI feature after SDD-018 that exercises this variant?

**Context**: PI-5 has no UI features remaining (Sprint 4 = ADO/GH
bridge + model upgrade discipline; Sprint 5 = self-review + uniform
gates). The first real exercise of the variant is in PI-6 (not yet
planned). Naming the target feature now sets the success bar for
SDD-018 and gives the variant a concrete first consumer to design
against.

Plausible candidates (none are committed; PM is sketching):

- **F-alpha**: SDD-001 Fleet Bridge Dashboard full scope (P3 in
  BACKLOG.md) -- the parked design from
  `specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md` taken to a full
  spec. Would prove the variant on the biggest UI surface area the
  framework has on backlog.
- **F-beta**: A "Sprint Burndown / Velocity" widget added to
  `exec/state.html`. Smaller, incremental, would exercise the variant
  on a typical "iterate during impl" panel.
- **F-gamma**: An interactive (mutating) control surface (e.g. a
  "force-release lock" button wired to `fleet.py lock force-release`).
  Would exercise the variant AND surface uniform-gate work (SDD-023,
  PI-5 Sprint 5).
- **F-delta**: A second-project bootstrap (SDD-016 host adoption) of
  a UI dashboard on a host repo. Would exercise the variant in the
  brownfield context the framework is being hardened for.

**PM recommendation**: **F-beta (Sprint Burndown / Velocity widget).**
Rationale: smallest, most-incremental, and matches the iterative
discovery pattern the variant is designed to absorb. Naming a smaller
first consumer is lower-risk for the variant's debut. F-alpha is too
large (whole new spec dir + workflow); F-gamma couples too much
(needs SDD-023 to ship first); F-delta is gated on a real host adopter.

**Architect recommendation**: **F-beta also, with a stipulation: the
PI-6 plan must explicitly name F-beta as "the variant proof case" so
the spec author knows they are the canary.** Without that label, the
variant's first real consumer might not realize they're piloting
something and revert to Article X strict.

**Joint recommendation**: **F-beta (Sprint Burndown / Velocity
widget) as the first real UI feature exercising the variant. PI-6
plan to label it explicitly as "the variant proof case."** This is a
NON-BINDING directional answer for PI-6 PM planning -- the owner can
override at PI-6 plan time.

**Status**: OPEN
**Answer**: (pending owner)

---

## Authors-added (open the door for the owner)

### Q8: Migration of pre-existing locked validation contracts -- forward-only, or back-port allowed?

**Context**: Authors-added in pass 1. Once the variant ships, existing
spec dirs with already-LOCKED `validation.md` files (most of PI-3 and
PI-4) cannot retroactively become UI variants without a defined
migration rule. Two options:

- **(a) Forward-only**: existing locked contracts stay locked under
  Article X. Only new spec dirs (created after SDD-018 ships) may opt
  into the variant. The single retroactive demo case (Q5 answer) is
  the EXCEPTION, surgically migrated by the SDD-018 author as proof.
- **(b) Back-port allowed**: any spec dir may at any time add the
  marker and convert to the variant, including back-porting delta
  entries that document what *actually* happened during implementation
  (i.e. an audit trail authored after the fact, marked as
  "back-ported").

**PM recommendation**: **(a) Forward-only with the single Q5 demo
exception.** Rationale: back-porting opens an audit-trail
contamination risk (the author writes the "as if locked at
implementation time" delta from memory; the git history shows it was
authored later). Forward-only keeps each contract honest to its own
era's rules. If we later want broader back-port, it can be a P3
backlog item with explicit "back-ported, authored YYYY-MM-DD" tagging
on delta entries.

**Architect recommendation**: **(a) Forward-only, same as PM.**
Architectural detail: the Q5 demo migration should be marked with a
distinctive delta-entry field (e.g. `item-type: retroactive-demo`)
so `schema_lint` can recognize it as "this is the SDD-018 proof case,
not a back-port template."

**Joint recommendation**: **(a) Forward-only.** Q5 demo is the
sanctioned exception, tagged with a distinctive delta-entry type
(e.g. `item-type: retroactive-demo`) so it cannot be misread as a
general back-port permission.

**Status**: OPEN
**Answer**: (pending owner)

---

### Q9: Naming -- "delta" vs "amendment" vs "addendum" vs other?

**Context**: Authors-added in pass 1. Naming the post-lock-addition
mechanism matters for searchability and intuitive comprehension. The
F-10 prompt and the BACKLOG row both use "delta." Alternatives:

- **delta** (current default; short; precedent in diff/change tooling)
- **amendment** (legal-style; intuitive for "post-lock change"; but
  collides with constitutional "amendment" used in ADR-013 and the
  upcoming ADR-014)
- **addendum** (legal-style; intuitive for "post-lock addition"; no
  collision)
- **revision** (publishing-style; implies the original changed,
  which is wrong since the variant is append-only)

**PM recommendation**: **"delta"** as currently used. Rationale:
short, already in BACKLOG and CURRENT_PI prose, and the audience
(framework adopters who are developers) reads "delta" cleanly as
"change set." "amendment" collides with constitutional vocabulary.

**Architect recommendation**: **"delta"** as well. Same rationale.
Architectural note: whatever name lands here MUST be used
consistently across `templates/validation.md`, `schema_lint.py`
error messages, the new docs page (per Q-F Path B's ADR-014), and
the constitution edit (if Q-F lands on Path B). One name, one
spelling, no synonyms.

**Joint recommendation**: **"delta"** as currently used. Locked
consistently across all surfaces.

**Status**: OPEN
**Answer**: (pending owner)

---

## Notes for the owner

- Questions Q1, Q2, Q3, Q4, Q6, Q7, Q8, Q9 have a **joint PM +
  Architect recommendation**. The owner can accept all of these and
  the variant ships with the recommended shape.
- **Q5 is the only Level-1 divergence**: PM votes
  `2026-05-26-live-ui-v2/`; Architect votes
  `2026-05-16-state-dashboard/`. Owner must pick.
- If the owner amends Q1, Q2, or Q4 substantively, the Architect's
  Q6 recommendation may shift from Path B to Path C (see Q6
  conditional clause).
- The Executive Manager surfaces these answers; this CLARIFY round
  runs through the EM, not direct PM/Architect/owner contact.

---

## Cross-References

- Parent spec: [`./spec.md`](./spec.md)
- Validation contract (locks at pass 2 close):
  [`./validation.md`](./validation.md)
- Implementation plan (authored at pass 2): [`./plan.md`](./plan.md)
- PI plan: [`../../sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md)
- Sprint 3 prep notes: [`../../sprints/PI-5/SPRINT-3-PREP-NOTES.md`](../../sprints/PI-5/SPRINT-3-PREP-NOTES.md)
- F-10 kickoff prompt: [`../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md`](../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md)
- Article X (current strict rule): `constitution/principles.md` Article X
- Article XI (serial gate; precedent for new-article path): `constitution/principles.md` Article XI; ADR-013
- Prior-art dashboard spec dirs: see Q5 candidates above
