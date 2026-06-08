---
id: ADR-014
type: spec
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# ADR-014: UI Lifecycle Variant -- Article XII

- Date: 2026-06-08
- Status: **accepted**
- Accepted: 2026-06-08 by Rodolfo Lerma via Executive Manager. Constitution edit landed in the same commit (Article XII added to principles.md; version 1.2.0 -> 1.3.0).
- Authors: Principal Architect + Principal Product Manager (jointly,
  in F-10 pass 2)

> **Frontmatter note**: `status: draft` is the SDD-FDC-001 carrier
> used for "ADR drafted but not accepted." The substantive ADR status
> (the top-level "Status:" line above) reads `proposed` per ADR
> convention. The SDD-FDC-001 enum does not contain `proposed`; this
> is consistent with how ADR-013 was carried before owner ratification.

---

## Context

PI-3 (Live UI v2 redesign) and PI-4 (state-dashboard live-server
pivot) both produced UI features whose REQUIRED behaviors emerged
during implementation rather than before. Article X
("Validation Is a Pre-Implementation Contract", framework v1.2.0)
locks `validation.md` at `/tasks` and forbids loosening REQUIRED
items after lock. The rule is sound for back-end and CLI work but
generated friction on UI work in two ways:

1. **Pre-lock guesswork.** UI authors were either over-specifying
   (forcing guesses about palette / spacing / panel behavior that
   the implementation would later refute) or under-specifying
   (forcing override-ceremony re-locks every time a visual decision
   cascaded).

2. **Constitutional grey-zone events.** Multiple PI-3 / PI-4 spec
   dirs show `validation.md` edits after lock that have no sanctioned
   audit-trail mechanism. These are unrecorded variants happening
   anyway -- the framework should either codify the variant or
   confront the discipline gap.

The PI-5 risk register (`sprints/PI-5/CURRENT_PI.md`, Risk row 5)
flagged the leakage concern explicitly:

> "SDD-018 UI lifecycle relaxation leaks into non-UI features --
> Mitigated -- the variant is opt-in via a marker on the spec dir,
> not a global Article X amendment."

The Sprint 6 Architect audit (2026-06-07) identified the same gap;
SDD-018 was filed as the response. CLARIFY closed 2026-06-08 at
commit `754fda6` with all 9 questions and 3 OWNER-ATTENTION items
resolved. See [`../../specs/2026-06-09-ui-lifecycle-variant/clarify.md`](../../specs/2026-06-09-ui-lifecycle-variant/clarify.md).

---

## Decision

Introduce a **UI Lifecycle Variant of Article X** as a **new
Article XII** of `constitution/principles.md` (Path B; rejected Path
A and Path C, see Alternatives below). The variant:

1. **Opt-in per spec dir** via `ui-variant: true` in `spec.md`
   frontmatter. Per-path auto-activation explicitly rejected.
2. **Relaxes Article X rule 2 only** (the no-loosening clause).
   Rule 1 (lock at `/tasks`) and rule 3 (zero unchecked REQUIRED at
   done) stay firm.
3. **Provides an append-only `## Delta Entries` section** in
   `validation.md` for variant spec dirs. Each entry is a
   level-3 sub-section with mandatory fields `timestamp`, `author`,
   `rationale`, `item-type` (closed enum `{add, wontfix, re-check,
   retroactive-demo}`), and a free-Markdown body.
4. **Is machine-checkable**: `cli/schema_lint.py` recognizes the
   marker, dispatches variant spec dirs to a new
   `check_validation_variant` sub-validator, and prefixes
   delta-originated findings with `[delta]`. Non-variant spec dirs
   are byte-identical to today's lint behavior.
5. **Migration is forward-only.** The single retroactive-demo
   exception is the SDD-018 proof case
   ([`specs/2026-05-16-state-dashboard/`](../../specs/2026-05-16-state-dashboard/)),
   enforced via a hard-coded path allow-list in `schema_lint.py`.
   Any other `item-type: retroactive-demo` use is a `[delta]`
   error.
6. **Naming is fixed.** The mechanism is named **delta** across
   all surfaces (templates, lint errors, ADR, docs, Article XII
   text). No synonyms.

Bumps `constitution/principles.md` version 1.2.0 -> 1.3.0 (MINOR:
new article added; no breaking changes to Articles I-XI).

ADR-014 itself ships with SDD-018 (status `proposed`). The
constitution edit landing Article XII is a **separate Level-2
commit** by the owner after they read this ADR. ADR-014 status
flips `proposed -> accepted` at that point.

---

## Proposed Article XII text

The owner copy-pastes the following block into
`constitution/principles.md` immediately after Article XI:

```markdown
## Article XII: UI Lifecycle Variant of the Validation Contract

A spec dir MAY opt into the UI Lifecycle Variant of Article X by
declaring `ui-variant: true` in its `spec.md` frontmatter. The variant
applies only to that spec dir; it does NOT propagate to siblings,
parents, or path-pattern matches. Variant spec dirs follow these
amendments to Article X:

1. **Lock timing is preserved.** `validation.md` is still LOCKED at
   `/tasks` time. The variant does not loosen the lock event.
2. **Append-only delta mechanism replaces the no-loosening clause.**
   After lock, variant spec dirs MAY append entries to a
   `## Delta Entries` section in `validation.md`. Each entry is a
   level-3 sub-section with mandatory fields `timestamp` (ISO 8601
   UTC), `author`, `rationale`, and `item-type` (closed enum
   `{add, wontfix, re-check, retroactive-demo}`). Existing locked
   items are not edited; deltas are append-only and themselves
   become part of the locked contract the moment they are committed.
3. **Required-completeness rule is preserved.** Zero unchecked
   REQUIRED items before implementation is considered complete --
   for both base items AND `item-type: add` delta entries.
   `item-type: wontfix` entries annotate without removing; the
   underlying REQUIRED item remains in the contract unless an
   explicit `re-check` supersedes it.
4. **Forward-only migration.** Pre-existing locked contracts are
   not retroactively eligible to adopt the variant. The single
   sanctioned exception is the SDD-018 proof case
   (`specs/2026-05-16-state-dashboard/`), tagged
   `item-type: retroactive-demo` and enforced by a hard-coded
   `schema_lint` allow-list.

`cli/schema_lint.py` enforces this article. Delta-originated lint
findings are prefixed `[delta]`. Authoring guidance lives in
`docs/UI-LIFECYCLE-VARIANT.md`. The variant is documented in
ADR-014.
```

Length: ~38 lines including code fence. Matches the prose density
of Article X (~10 lines) and Article XI (~13 lines) within roughly
3x because Article XII is mechanism-bearing rather than principle-
only.

---

## Consequences

### Positive

- UI authors get a sanctioned audit-trail for post-lock additions,
  closing the PI-3 / PI-4 constitutional grey-zone.
- The variant is **opt-in per spec dir**: back-end, CLI, schema,
  and constitution work continue to lock validation at `/tasks` with
  no delta mechanism. No leakage into non-UI features.
- Variant remains **machine-checkable**: `schema_lint` is the
  enforcement floor, not human discipline. The `[delta]` finding
  prefix gives spec authors clear failure diagnostics.
- Article X stays **readable** (Path A rejected): Article X is not
  amended with carve-out clauses; the variant lives in Article XII,
  parallel to how Article XI sits beside Articles I-X.

### Negative

- One more article for future framework adopters to learn. Total
  article count goes from 11 to 12.
- Article XII references Article X by number; if Article X is ever
  re-numbered (unlikely), Article XII text must update in lockstep.
- The `item-type: retroactive-demo` allow-list is hard-coded; any
  future retroactive demo (none planned) requires both a constitution
  edit and a `schema_lint.py` allow-list edit.
- Append-only enforcement in `schema_lint` is a non-trivial
  implementation surface (git-diff vs always-on heuristic). F-11
  carries the design choice.

### Neutral

- Constitution version bump 1.2.0 -> 1.3.0 (MINOR; ADR-0006).
- The `[delta]` prefix on lint findings is a new surface in error
  output. JSON consumers see `issue` strings prefixed `[delta] ...`;
  human consumers see the same prefix. Existing parsers that only
  look at `path` / `kind` / `severity` are unaffected.
- `templates/feature-spec.md` and `templates/validation.md` carry
  commented-out variant stubs. Strict spec dirs scaffolded from
  these templates remain byte-identical to today's output when the
  stubs stay commented.

---

## Alternatives Considered

### Path A: Amend Article X with a UI carve-out clause

Edit `constitution/principles.md` Article X to add an explicit
"UI variant" sub-clause. Bump Article X minor version (1.0.0 ->
1.1.0). **Rejected** because Article X then accumulates carve-out
clauses over time (UI today, performance tomorrow, data-migration
the day after), making the article harder to read for future
framework adopters. The "one article, one principle" pattern that
Articles I-XI follow is sacrificed for marginal terseness.

### Path C: No constitution edit -- process / template only

The variant lives entirely in `schema_lint.py` +
`templates/validation.md` + `templates/spec.md` + a new
`docs/UI-LIFECYCLE-VARIANT.md`. **Rejected** because the rule
becomes too quiet: a future framework adopter reading
`constitution/principles.md` would not learn the variant exists.
Article X's premise ("validation is a contract") is constitutional;
a variant of that premise is therefore also constitutional. Routing
it through process-only documentation hides it from the audience
that most needs to see it.

The Architect's Q6 conditional clause (`clarify.md`) explicitly
noted that Path C would become defensible IF Q1-Q4 amended to
"smaller than expected" (no `schema_lint` change). They did not;
Path C is correctly rejected.

### Path B: New Article XII (this ADR)

**Accepted.** Uses the same "new article sits beside existing
articles" pattern that ADR-013 established for Article XI. Each
article stays single-purpose. The variant is visible to future
adopters reading `constitution/principles.md` cover-to-cover.

---

## References

- [`../../specs/2026-06-09-ui-lifecycle-variant/spec.md`](../../specs/2026-06-09-ui-lifecycle-variant/spec.md) -- SDD-018 finalized spec
- [`../../specs/2026-06-09-ui-lifecycle-variant/clarify.md`](../../specs/2026-06-09-ui-lifecycle-variant/clarify.md) -- 9 CLARIFY questions + verbatim owner answers
- [`../../specs/2026-06-09-ui-lifecycle-variant/validation.md`](../../specs/2026-06-09-ui-lifecycle-variant/validation.md) -- LOCKED validation contract for SDD-018 itself
- [`../../specs/2026-06-09-ui-lifecycle-variant/plan.md`](../../specs/2026-06-09-ui-lifecycle-variant/plan.md) -- F-11 implementation plan
- [`../../specs/2026-06-09-ui-lifecycle-variant/tasks.md`](../../specs/2026-06-09-ui-lifecycle-variant/tasks.md) -- F-11 task list
- [`./013-serial-clarify-spec-gate.md`](./013-serial-clarify-spec-gate.md) -- ADR-013 (precedent for new-article path; Article XI rollout)
- [`../../sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md) -- PI-5 plan (PI Objective 3, Sprint 3, Risk row 5)
- [`../../specs/2026-05-16-state-dashboard/`](../../specs/2026-05-16-state-dashboard/) -- retroactive-demo target (state-dashboard); RETRO.md documents the static -> live pivot
- [`../../specs/2026-05-26-live-ui-v2/`](../../specs/2026-05-26-live-ui-v2/) -- future stretch retroactive-demo candidate (NOT migrated in SDD-018)
- `constitution/principles.md` Article X -- current strict rule
- `constitution/principles.md` Article XI -- precedent for new-article pattern
