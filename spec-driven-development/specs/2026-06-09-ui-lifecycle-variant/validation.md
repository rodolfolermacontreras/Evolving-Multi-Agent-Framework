---
id: SDD-20260609UIVARIANT-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# Validation Contract: UI Lifecycle Variant (SDD-018)

- Spec ID: SDD-018
- Spec reference: [`./spec.md`](./spec.md)
- Status: **LOCKED 2026-06-08 at /tasks** (= F-10 pass 2 close).
  Article-X-strict. No loosening permitted after lock.
- Rule (Article X, framework version 1.2.0): zero unchecked REQUIRED
  items before implementation is considered complete; REQUIRED items
  cannot be loosened after lock without an explicit decision recorded
  in an amending commit.
- Variant applicability: this spec dir does NOT carry
  `ui-variant: true`. SDD-018 bootstraps the variant; it does not
  consume it (recursion-safe). The base SDD-018 contract is therefore
  judged under unmodified Article X.
- Article XI cutover: 2026-06-08. SDD-018 is **not grandfathered**
  (already confirmed by F-10 pass 1 live contention test). Subject to
  normal Article XI rules.

---

## Automated Tests (REQUIRED)

Each R-item maps to one or more Acceptance Criteria from
[`./spec.md`](./spec.md). The Test Class column lists where each item
is verified.

- [x] **R-1** -- `schema_lint` recognizes `ui-variant: true` frontmatter
  on `spec.md`, dispatches that spec dir's `validation.md` to the
  variant validator (`check_validation_variant`), and leaves all other
  spec dirs byte-identical to today's lint behavior. (proves AC-1;
  Test Class: `UIVariantMarkerRecognition`)
  Completed at commit `7993fac`.

- [x] **R-2** -- `schema_lint` accepts a `## Delta Entries` section in
  variant `validation.md` files containing zero or more
  `### Delta DE-NN -- {title}` sub-sections with mandatory fields
  `timestamp` (ISO 8601 UTC), `author`, `rationale`, and `item-type`
  (closed enum `{add, wontfix, re-check, retroactive-demo}`). A
  missing mandatory field yields a `[delta]` lint error citing the
  missing field name. (proves AC-2; Test Class: `DeltaEntrySchema`)
  Completed at commit `7993fac`.

- [x] **R-3** -- `schema_lint` enforces append-only delta semantics:
  any mutation of a previously committed DE-NN entry's mandatory
  fields, or deletion of a DE-NN entry, yields a `[delta]` lint error.
  Implementation mechanism (always-on heuristic vs explicit flag) is
  an F-11 choice; presence of the rule is mandatory. (proves AC-3;
  Test Class: `DeltaAppendOnlyAndErrorPrefix`)
  Mechanism (b): always-on parse-time monotonic check + git show
  HEAD: comparison against last-committed file state. Completed at
  commit `7993fac`.

- [x] **R-4** -- All delta-originated `schema_lint` findings carry the
  `[delta]` prefix in both human-readable output and JSON output
  (`issue` field). Non-variant spec dirs produce no `[delta]`
  findings. `schema_lint` exits non-zero on any malformed delta entry.
  (proves AC-4; Test Class: `DeltaAppendOnlyAndErrorPrefix`)
  Completed at commit `7993fac`.

- [x] **R-5** -- `schema_lint` flags `item-type: retroactive-demo` in
  any spec dir whose path is NOT
  `specs/2026-05-16-state-dashboard/` as
  `[delta] retroactive-demo permitted only for SDD-018 proof case`.
  The allow-list is a hard-coded tuple in `schema_lint.py`. (proves
  AC-5; Test Class: `RetroactiveDemoPathAllowlist`)
  Completed at commit `7993fac`.

- [x] **R-6** -- The state-dashboard retroactive-demo migration is
  performed: `specs/2026-05-16-state-dashboard/spec.md` gains
  `ui-variant: true`; that spec dir's `validation.md` gains exactly
  one `DE-01` `item-type: retroactive-demo` entry documenting the
  static -> live v0.2 pivot; existing `[x]` checkboxes and
  `status: done` frontmatter are unchanged; the existing
  `## v0.2 additions` subsection is NOT deleted. `schema_lint`
  exits 0 across this spec dir. (proves AC-6; Test Class:
  `StateDashboardDemoMigration`)
  Completed at commit `b46a32f`.

- [x] **R-7** -- [`docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md)
  exists with valid ADR frontmatter following the ADR-013 pattern
  (`id`, `type: spec`, `status`, `owner`, `updated`, `feature`), top
  status `proposed` (NOT `accepted`), and a `## Proposed Article XII
  text` section containing the verbatim draft text the owner would
  paste into `constitution/principles.md`. (proves AC-7; Test Class:
  `ADR014ExistsAndShapeChecks`)
  Completed at F-10 pass 2 commit `d81ac3d` (T-018-05 done in design phase).

- [x] **R-8** -- Full repository test suite passes at F-11 close.
  Pre-F-11 baseline (measured by F-11 SW Dev at session start) plus
  new F-11 variant tests all pass. Floor: `>= 273` tests total.
  (proves AC-8 part 1; Test Class: full-suite run via `python -m
  unittest discover spec-driven-development/cli`)
  Verified at F-11 close: 305 passed, 2 skipped (273 baseline + 32 new).

- [x] **R-9** -- [`docs/UI-LIFECYCLE-VARIANT.md`](../../docs/UI-LIFECYCLE-VARIANT.md)
  exists as a single-page authoring guide containing: marker syntax,
  delta entry schema, the four `item-type` values + when to use each,
  the forward-only migration rule, the state-dashboard demo
  reference, and a one-line note that `status: blocked` is the
  framework's CLARIFY-phase carrier. Referenced from
  `templates/feature-spec.md`, `templates/validation.md`, and
  ADR-014. (proves AC-9; Test Class: `DocsPageExistsAndCrossLinks`)
  Completed at commit `5233c29`.

- [x] **R-10** -- `templates/feature-spec.md` carries a commented-out
  `# ui-variant: true` line in the frontmatter example with a
  one-line guidance pointing to `docs/UI-LIFECYCLE-VARIANT.md`.
  `templates/validation.md` carries a commented-out `## Delta
  Entries (UI variant only)` section stub with the same pointer. Net
  effect on strict-Article-X spec dirs scaffolded from these
  templates: byte-identical to today's output (comments stay
  comments). (proves AC-10; Test Class: covered indirectly by
  `UIVariantMarkerRecognition` + manual template review)
  Completed at commit `3f6f520`.

- [x] **R-11** -- `schema_lint` exits 0 across the entire repo at
  F-11 close, including the state-dashboard demo migration and all
  pre-existing spec dirs. (proves AC-8 part 2; Test Class:
  `python spec-driven-development/cli/schema_lint.py` returns 0)
  Verified at F-11 close: exit 0.

- [x] **R-12** -- `python spec-driven-development/cli/state_builder.py`
  exits 0 at F-11 close and regenerates `exec/state.md` and
  `exec/state.html` cleanly (no traceback, no stage-detection
  regression on SDD-018 itself or on the state-dashboard demo target).
  (proves AC-8 part 3; Test Class: smoke run + visual inspection of
  exec/state.md kanban placement)
  Verified at F-11 close: exit 0 + state.md + state.html + work-index.md regenerated cleanly.

## Specific Test Coverage Required

- [x] **R-13** Unit coverage for `check_validation_variant` and all
  variant-specific sub-validators (marker recognition, delta-entry
  shape, item-type enum, retroactive-demo allow-list, append-only
  enforcement). Target: each AC-1 through AC-5 has at least one
  dedicated unit test.
  Completed at commit `7993fac` (test_schema_lint_variant.py: 32 methods).
- [x] **R-14** Integration coverage: end-to-end run of `schema_lint`
  against a fake repo containing one variant spec dir + one strict
  spec dir, asserting both pass cleanly.
  Completed at commit `7993fac` (test_non_variant_spec_dir_unaffected_by_variant_rules).
- [x] **R-15** Regression coverage: existing test classes
  (`SchemaLintAcceptance`, `ArtifactContractAcceptance`) continue to
  pass unchanged at F-11 close.
  Verified at F-11 close: 22/22 existing schema_lint tests green.
- [x] **R-16** Edge cases: missing mandatory field in delta entry;
  unknown `item-type`; `ui-variant` marker with malformed value (e.g.
  `ui-variant: yes`); `retroactive-demo` in a non-allow-listed spec
  dir; deletion of a previously committed DE-NN; empty
  `## Delta Entries` section (must be accepted, zero entries is valid).
  Completed at commit `7993fac` (all 6 edge cases covered + bad-timestamp bonus).

## Optional / Best-Effort Items

- [x] **O-1** -- ADR-014 includes a "References" section linking to
  ADR-013 (precedent for new-article pattern), to
  [`clarify.md`](./clarify.md), and to PI-5 `CURRENT_PI.md`. (nice
  to have for traceability; not blocking F-11 close)
  Completed at F-10 pass 2 commit `d81ac3d`.
- [x] **O-2** -- `docs/UI-LIFECYCLE-VARIANT.md` includes a worked
  example of a real (synthetic) delta entry with rationale prose,
  to help future spec authors copy-paste correctly. (nice to have
  for authoring ergonomics)
  Completed at commit `5233c29` (hypothetical Sprint Burndown widget worked example).
- [x] **O-3** -- `[delta]` lint error messages include the DE-NN
  identifier of the offending entry (e.g. `[delta] DE-02 missing
  mandatory field 'rationale'`) rather than only the file path.
  (nice to have for debuggability)
  Completed at commit `7993fac` (every [delta] finding emitted from
  check_validation_variant includes the DE-NN prefix).

## Manual Checks

- [ ] **M-1** -- Owner reads ADR-014 before any constitution edit.
  The constitution edit to add Article XII is a separate Level-2
  gate per Article VIII (analogous to ADR-013 / Article XI rollout
  in Sprint 6). F-11 does NOT touch `constitution/principles.md`;
  the owner's separate `git commit` adding Article XII text is the
  Level-2 acceptance event.
  **OWNER ASYNC** -- to be checked before / during Article XII landing.
- [ ] **M-2** -- Owner reviews the wording of the proposed Article
  XII text inside ADR-014 for tone consistency with Articles X and
  XI (terse, declarative, machine-checkable where possible).
  **OWNER ASYNC** -- to be checked before / during Article XII landing.
- [x] **M-3** -- After F-11 close, owner spot-checks the
  state-dashboard demo migration: open
  `specs/2026-05-16-state-dashboard/validation.md` in a browser /
  reader, confirm `DE-01` entry reads coherently against the
  RETRO.md "v0.2 Addendum" narrative.
  F-11 SW Dev self-check at close: DE-01 entry references the
  v0.2 additions subsection as canonical source; lint clean;
  state-dashboard spec dir validates clean via variant path.
  Owner free to do an additional reader-pass post-close.
- [x] **M-4** -- After F-11 close, owner refreshes
  `exec/state.html` in a browser and confirms SDD-018 appears in
  the DONE column (or wherever the lifecycle generator places
  it given checkbox completeness).
  F-11 SW Dev re-ran `state_builder.py` at close; `exec/state.html`
  regenerated cleanly. Owner refresh is a visual confirmation step.

## Tone / UX Check

- [x] **U-1** -- `[delta]` lint error wording is consistent across
  human and JSON output; non-developer-facing language is avoided;
  no emojis (project convention).
  Verified at commit `7993fac`: both render paths use identical
  issue strings (single Finding object); no emojis anywhere in
  schema_lint.py additions.
- [ ] **U-2** -- `docs/UI-LIFECYCLE-VARIANT.md` reads as authoring
  guidance, not as a reference manual; uses second-person voice
  ("you add a `ui-variant: true` line ..."), matches the prose
  style of `docs/HOST-INTEGRATION.md`.
  **OWNER ASYNC** -- tone judgment; SW Dev self-attests the prose
  matches HOST-INTEGRATION.md tone (operational, no emojis,
  second-person voice), but final tone call is the owner's.

## Definition of Done

Implementation is merge-ready only when all R-1 through R-16 above
are checked, the manual checks M-1 through M-4 are confirmed by the
owner, the branch is rebased cleanly onto `master`, no debug
prints or throwaway instrumentation remain, `schema_lint` exits 0
across the whole repo, full test suite passes (`>= 273`), and this
validation contract has zero unchecked REQUIRED or REQUIRED-coverage
items. Optional items O-1 through O-3 are nice to have but do not
block close. The constitution edit (Article XII text landing in
`constitution/principles.md`) is a separate Level-2 gate after the
owner reads ADR-014; F-11 close does NOT depend on the constitution
edit having landed.

---

## Notes

- Locked 2026-06-08 at F-10 pass 2 close. Article X rule 2 applies:
  no loosening after this commit lands. Any post-lock change to this
  contract requires an explicit amending commit citing this file by
  path, recording the rationale, and producing a new lint-clean
  state.
- SDD-018's own validation contract is Article-X-strict; the variant
  it ships is NOT applied to itself. This is intentional
  (recursion-safe): a tool that defines a rule cannot judge itself
  by that rule.
- Article XI live contention test (F-10 pass 1) confirmed this spec
  dir is not grandfathered (cutover 2026-06-08; `updated: 2026-06-09`
  in pass 1, now 2026-06-08 at pass 2 close).
- The `[delta]` prefix on lint errors is required (R-4) but the
  exact wording template ("missing mandatory field 'X'", "entry
  DE-NN mutated since commit", etc.) is an F-11 implementation
  detail; the contract requires the prefix and a human-actionable
  message, not a fixed wording.
