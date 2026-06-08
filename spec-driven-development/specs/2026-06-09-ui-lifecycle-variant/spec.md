---
id: SDD-20260609UIVARIANT-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# Feature Spec: UI Lifecycle Variant (SDD-018)

- Date: 2026-06-09 (created); 2026-06-08 (finalized at F-10 pass 2)
- Authors: Principal Product Manager + Principal Architect (jointly)
- Status: ACTIVE (CLARIFY closed at commit `754fda6`; pass 2 finalization)
- Priority: P1
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7)
- Spec ID: SDD-018
- Parent objective: PI-5 Objective 3 -- UI Lifecycle Variant
  ([`sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md))
- Backlog row: [`BACKLOG.md`](../../backlog/BACKLOG.md) / SDD-018 (P1, M effort)

> **Status convention note (`status: blocked` -> `status: active`)**:
> SDD-FDC-001's closed status enum (`{draft, active, blocked, done,
> superseded, archived}`) contains no `clarify` value. Per owner
> direction 2026-06-08 ([`clarify.md`](./clarify.md) "OWNER-ATTENTION
> resolutions" item 1), `status: blocked` is the framework's official
> CLARIFY-phase carrier going forward; the enum is NOT amended. With
> CLARIFY now closed, this spec transitions `blocked` -> `active`, and
> will transition `active` -> `done` at F-11 close. This convention is
> documented in [`docs/UI-LIFECYCLE-VARIANT.md`](../../docs/UI-LIFECYCLE-VARIANT.md)
> (authored in F-11) and in ADR-014.

---

## Problem Statement

Article X of `constitution/principles.md` ("Validation Is a Pre-Implementation
Contract", framework version 1.2.0) locks `validation.md` at `/tasks` time
and forbids loosening REQUIRED items after lock. The rule is sound for
back-end and CLI work where requirements can be enumerated up front and
remain stable through implementation. It is **too rigid for iterative
visual / UI work**, where the following are normal and expected:

1. **The contract surfaces during implementation, not before.** A
   dashboard panel's REQUIRED behavior (e.g. "the kanban column must
   highlight stale items older than N hours") is often only discoverable
   once the panel is rendered against real data. Pre-locking the contract
   either over-specifies (forcing guesses) or under-specifies (forcing
   re-locks via override ceremony).
2. **Visual decisions cascade.** Choosing a palette, type scale, or
   spacing token in week 1 changes the REQUIRED items in week 2 for every
   downstream panel. Article X's "no-loosening" clause turns each
   cascade into an override.
3. **The PI-3 / PI-4 dashboard work proved the friction empirically.**
   [`specs/2026-05-26-live-ui-v2/`](../2026-05-26-live-ui-v2/) and
   [`specs/2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
   both show validation contracts that had to be edited after lock to
   absorb visual decisions made during implementation -- each edit a
   constitutional grey-zone event, none currently auditable as a
   sanctioned variant.

Article XI ("Cross-Feature Serial Gate at CLARIFY and SPEC", ratified
2026-06-07, ADR-013) hardened the upstream gates; SDD-018 must NOT undo
that hardening for UI work. The variant introduced here is **narrow,
opt-in, and additive** to Article X -- not a global loosening.

PI-5 risk-register entry confirmed and now operative:

> "SDD-018 UI lifecycle relaxation leaks into non-UI features --
> Mitigated -- the variant is opt-in via a marker on the spec dir, not
> a global Article X amendment."
> ([`CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md) Risks row 5)

---

## Goal

Define and ship a **controlled, opt-in, auditable variant of Article X
for UI work** that:

1. Permits `validation.md` to evolve during implementation through a
   structured **delta** mechanism (post-lock additions recorded with
   timestamp + rationale + author + item-type + body), instead of forcing
   an override or a friction-analysis re-lock.
2. Is **opt-in per spec dir** via an explicit `ui-variant: true`
   frontmatter marker on `spec.md`, so the variant cannot leak into
   back-end, CLI, schema, or constitution work.
3. Stays **machine-checkable** through `cli/schema_lint.py` -- the
   variant introduces a new schema branch, not a relaxation of the
   existing one. Delta-related lint errors are prefixed `[delta]`.
4. Demonstrates the variant by **retroactively validating one PI-2
   dashboard change** -- specifically the
   [`specs/2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
   static -> live pivot -- so the rule is proven against real prior art
   before any new UI feature adopts it.
5. Resolves the **constitutional path** by drafting **ADR-014** (UI
   Lifecycle Variant -- new Article XII) for owner Level-2 approval.
   The constitution edit itself remains a separate gate after the owner
   reads ADR-014.

---

## Out-of-Scope

- **Loosening Article X for non-UI features.** Back-end, CLI, schema,
  and constitution work continue to lock validation at `/tasks` with no
  delta mechanism. The variant is opt-in only.
- **Loosening Article XI.** The serial CLARIFY/SPEC gate stays as
  ratified 2026-06-07. SDD-018 is itself subject to Article XI.
- **Loosening Article VII** (One Feature, One Session). F-10 pass 2
  runs in its own session; F-11 (implementation) runs in another.
- **Rewriting `validation.md`'s base schema.** The variant adds a
  `## Delta Entries` section, not a rewrite. Existing locked items
  continue to parse and check identically.
- **New UI features in PI-5.** PI-5 ships no UI features after SDD-018;
  the first real UI feature exercising the variant is F-beta (Sprint
  Burndown / Velocity widget in `exec/state.html`), targeted
  non-bindingly for PI-6 ([`clarify.md`](./clarify.md) Q7).
- **Back-porting prior locked contracts.** Migration is forward-only.
  The single state-dashboard demo (`item-type: retroactive-demo`) is
  the sole sanctioned exception ([`clarify.md`](./clarify.md) Q8).
- **A `/spec-ui` slash command.** Deferred to P3 (SDD-035 if filed)
  per [`clarify.md`](./clarify.md) Q2.
- **The constitution edit itself.** ADR-014 is drafted in this pass;
  the actual edit to `constitution/principles.md` (Article XII, version
  bump 1.2.0 -> 1.3.0) is a separate Level-2 gate triggered by owner
  acceptance of ADR-014 after they read it.
- **Implementing the `[delta]` error prefix in `schema_lint`.** That is
  F-11 work; this pass specifies the requirement only.

---

## Cross-Feature Notes

Dedup scan run as part of the Article XI live contention test (F-10
pass 1) classified the following prior-art relationships. Final
disposition recorded in [`backlog/DEDUP-LOG.md`](../../backlog/DEDUP-LOG.md).

| Prior-art spec dir | Relationship | Disposition |
|---|---|---|
| [`2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/) | Earliest dashboard spec dir; RETRO.md documents the "static -> live" pivot mid-implementation -- the canonical prior-art match for the delta mechanism. | **Retroactive-demo target (Q5 = C2).** F-11 surgically migrates this spec dir's `validation.md` (one delta entry, `item-type: retroactive-demo`). See "Authoring decision 4" below. |
| [`2026-05-26-live-ui-v2/`](../2026-05-26-live-ui-v2/) | PI-3/S4 design + PI-4 implementation; full UI redesign with Principal UI Designer ownership. | NOT migrated in SDD-018. Remains a future stretch candidate (post-PI-6) per owner direction. |
| [`2026-05-16-dashboard-about-and-freshness/`](../2026-05-16-dashboard-about-and-freshness/) | SDD-009 + SDD-010 bundled dashboard mods. | NOT migrated. Context only. |
| [`2026-05-13-fleet-bridge-dashboard/`](../2026-05-13-fleet-bridge-dashboard/) | Design exploration (DESIGN.md only). | NOT migrated (no `validation.md` to retro-validate). Context only. |
| [`2026-06-07-serial-clarify-spec-gate/`](../2026-06-07-serial-clarify-spec-gate/) (SDD-019) | Provides the Article XI lock substrate this spec dir is subject to. | Hard cross-dependency: SDD-018 lock holder behavior assumes SDD-019 active. |
| [`2026-06-07-cross-feature-dedup/`](../2026-06-07-cross-feature-dedup/) (SDD-020) | Source of the dedup scan that surfaced these rows. | Hard cross-dependency: dedup hook fires at `/clarify` (this spec). |

**Article XI live contention test (F-10 pass 1) confirmed**: this spec
dir held the CLARIFY-phase lock per the rules ratified 2026-06-07. The
grandfather predicate returned `False`; the spec was subject to normal
Article XI rules. Lock released at `clarify.md` `status: done` (commit
`754fda6`). This spec dir does NOT carry `ui-variant: true` -- SDD-018
bootstraps the variant; it does not consume it (recursion-safe).

---

## Authoring decisions (recorded at pass 2)

These are author decisions made jointly by PM + Architect at pass 2.
They are NOT new CLARIFY questions; they implement the answered
CLARIFY decisions.

### 1. Delta entry field schema (frontmatter-style key:value, per ADR-012)

Each entry under `## Delta Entries` is a Markdown level-3 sub-section
of the form:

```markdown
### Delta DE-NN -- short title

- timestamp: 2026-MM-DDTHH:MMZ      # ISO 8601 UTC, mandatory
- author: principal-{role}           # agent identity, mandatory
- rationale: <one-sentence reason>   # why this delta is being added, mandatory
- item-type: add | wontfix | re-check | retroactive-demo  # closed enum, mandatory

item-body (the new REQUIRED item, the wontfix note against an existing
REQUIRED item, the re-check decision, or -- only for retroactive-demo --
the historical pivot being recorded). Free Markdown; may include code
blocks, checkboxes, and links.
```

Rules (enforced by `schema_lint` variant validator in F-11):

- DE-NN IDs are zero-padded two-digit and monotonically increasing
  within a single spec dir; never re-used.
- `item-type: add` creates a new REQUIRED checkbox elsewhere in
  `validation.md` and is gated by Article X rule 3 (zero unchecked
  REQUIRED at done).
- `item-type: wontfix` annotates an existing REQUIRED item; the item
  remains in the contract (NOT deleted) with `[wontfix-DE-NN]`
  appended; Article X rule 3 still fires against it unless explicitly
  reclassified by a follow-on `re-check`.
- `item-type: re-check` requests a re-verification of an existing
  REQUIRED item without rewriting it; surfaces in the manual-check
  list.
- `item-type: retroactive-demo` is the **single sanctioned exception**
  for the SDD-018 proof case ([`clarify.md`](./clarify.md) Q8). Any
  other use is a `[delta]` lint error gated by the path allow-list
  in AC-5.
- Delta entries are **append-only**: edits to existing DE-NN entries
  (other than fixing a typo flagged by lint) are forbidden; new deltas
  supersede via `item-type: re-check` referencing the older DE-NN.

### 2. `schema_lint` dispatch placement

Single marker check at the top of the per-spec-dir validation step.
F-11 will introduce a new `check_validation_variant(path)` sibling to
`check_artifact`; the dispatch decision happens **once per spec dir**,
not per sub-validator. Shared sub-validators (frontmatter shape, ISO
date, enum membership) stay single-implementation. Rationale: one
decision point is easier to reason about, easier to test, and easier
for future spec authors to grep.

### 3. Where the variant docs page lives

[`spec-driven-development/docs/UI-LIFECYCLE-VARIANT.md`](../../docs/UI-LIFECYCLE-VARIANT.md)
(authored in F-11). One markdown page, no sub-pages. Sits alongside
existing top-level docs (`ARCHITECTURE.md`, `CLI-PATTERN.md`,
`HOST-INTEGRATION.md`). Linked from the spec template, the validation
template, ADR-014, and (post-acceptance) the constitution's Article XII
text.

### 4. State-dashboard retroactive-demo migration scope

The reformatting in [`specs/2026-05-16-state-dashboard/validation.md`](../2026-05-16-state-dashboard/validation.md)
that F-11 performs:

- Add `ui-variant: true` to that spec dir's `spec.md` frontmatter (one
  line addition; spec.md is otherwise untouched).
- Append a `## Delta Entries` section to that spec dir's
  `validation.md` containing **one** entry, `DE-01`,
  `item-type: retroactive-demo`, documenting the "v0.2 additions
  (2026-05-16, post user UX feedback)" pivot already recorded in
  that file's existing `## v0.2 additions` subsection and in
  RETRO.md "v0.2 Addendum". The existing `## v0.2 additions`
  subsection is NOT deleted -- it stays as the historical narrative;
  the new delta entry references it as the canonical pivot record.
- No other changes to that spec dir. The pre-existing `[x]` checkboxes
  remain checked. The `status: done` frontmatter is unchanged.

F-11 work only. **Pass 2 (this file) does NOT edit
`specs/2026-05-16-state-dashboard/`.**

---

## Acceptance Criteria

Each criterion is testable. The Traceability Matrix at the end of this
spec maps each AC to its source CLARIFY question, its locked
`validation.md` R-item, the planned task, and the test class that
proves it.

- **AC-1**: `ui-variant: true` frontmatter marker on `spec.md` is
  recognized by `schema_lint` and dispatches that spec dir's
  `validation.md` to the variant validator. Absent or `false` value
  keeps Article X strict behavior. Source: Q2, Q3.
- **AC-2**: A `## Delta Entries` section in `validation.md` accepts
  zero or more `### Delta DE-NN -- {title}` entries with the field
  schema in "Authoring decision 1" above. A missing mandatory field
  yields a `[delta]` lint error citing the missing field name.
  Source: Q1, Q2, Q9.
- **AC-3**: Delta entries are append-only: `schema_lint` flags any
  spec dir where a previously committed DE-NN entry's mandatory fields
  have been mutated (timestamp / author / item-type / rationale
  changed) or where a DE-NN has been deleted. Detection mechanism
  (git-diff vs always-on heuristic) is an F-11 implementation
  choice; the rule itself is mandatory.
  Source: Q1, Q8.
- **AC-4**: `schema_lint` exits non-zero on any malformed delta entry
  in a `ui-variant: true` spec dir; all delta-originated findings are
  prefixed `[delta]` in both human and JSON output. Existing non-variant
  spec dirs are byte-identical to today's lint output. Source: Q4.
- **AC-5**: Migration is forward-only: `schema_lint` flags
  `item-type: retroactive-demo` in any spec dir whose path is NOT
  [`specs/2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
  as `[delta] retroactive-demo permitted only for SDD-018 proof
  case`. The path allow-list is hard-coded in `schema_lint.py` (a
  one-line tuple). Source: Q5, Q8.
- **AC-6**: The state-dashboard retroactive-demo migration is
  performed (F-11): `specs/2026-05-16-state-dashboard/spec.md` gains
  `ui-variant: true`; that spec dir's `validation.md` gains exactly
  one `DE-01` `item-type: retroactive-demo` entry per "Authoring
  decision 4" above; `schema_lint` exits 0 with the spec dir present
  in the variant walk. Source: Q5.
- **AC-7**: [`docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md)
  exists, carries valid ADR frontmatter (per existing ADR-013
  pattern), status `proposed` (NOT `accepted`), and includes a
  verbatim proposed-Article-XII draft text section the owner can
  paste into `constitution/principles.md` without rewriting.
  Constitution itself is NOT edited by F-11; that is a separate
  Level-2 gate. Source: Q6.
- **AC-8**: Full test suite passes (`>= 273` baseline at F-10 pass 2
  commit + new tests from F-11); `schema_lint` exits 0 across the
  whole repo (including the state-dashboard demo migration);
  `exec/state.md` regenerates cleanly after F-11 close. Source:
  Article X rule 3 applied to SDD-018 itself.
- **AC-9**: [`spec-driven-development/docs/UI-LIFECYCLE-VARIANT.md`](../../docs/UI-LIFECYCLE-VARIANT.md)
  exists as a single-page authoring guide for future spec authors,
  including: marker syntax, delta entry schema, the four `item-type`
  values + when to use each, the forward-only migration rule, the
  state-dashboard demo reference, and a one-line note that
  `status: blocked` is the framework's CLARIFY-phase carrier. Linked
  from spec/validation templates and ADR-014. Source: Q1-Q9 + the
  OWNER-ATTENTION 1 resolution.
- **AC-10**: Template parity: [`templates/feature-spec.md`](../../templates/feature-spec.md)
  gains an optional `ui-variant: true` frontmatter line (commented
  with a one-line explanation pointing to the docs page) and
  [`templates/validation.md`](../../templates/validation.md) gains an
  optional `## Delta Entries (UI variant only)` section (also
  commented with explanation). Strict Article X spec dirs remain
  byte-identical to today's template output when the comments stay
  unused. Source: Q2 (hybrid implementation surface).

---

## Affected Modules

Files that F-11 will create or modify. **Pass 2 (this file) authors
only this spec dir + ADR-014; it does NOT touch any of the F-11
implementation modules listed below.**

| File | Type | Change |
|------|------|--------|
| `spec-driven-development/cli/schema_lint.py` | Modify | Add `ui-variant` marker recognition, variant dispatch in the per-spec-dir validation step, new `check_validation_variant` sibling, `[delta]` finding prefix, retroactive-demo path allow-list, append-only enforcement. Additive; no behavior change for non-variant spec dirs. |
| `spec-driven-development/cli/test_schema_lint.py` | Modify (or add `test_schema_lint_variant.py` if cleaner) | New test classes covering AC-1 through AC-7 + AC-9 + AC-10; ~12-18 new test methods. Class names from the Test Strategy section below. |
| `spec-driven-development/templates/feature-spec.md` | Modify | Add commented-out `# ui-variant: true` line in the frontmatter example with one-line guidance + link to `docs/UI-LIFECYCLE-VARIANT.md`. |
| `spec-driven-development/templates/validation.md` | Modify | Add commented-out `## Delta Entries (UI variant only)` section stub with one-line guidance + link to `docs/UI-LIFECYCLE-VARIANT.md`. |
| `spec-driven-development/specs/2026-05-16-state-dashboard/spec.md` | Modify | Add `ui-variant: true` frontmatter line. ONE line addition; spec.md is otherwise untouched. |
| `spec-driven-development/specs/2026-05-16-state-dashboard/validation.md` | Modify | Append `## Delta Entries` section with one `DE-01` `retroactive-demo` entry per Authoring decision 4. |
| `spec-driven-development/docs/ADR/014-ui-lifecycle-variant.md` | Create | New ADR drafted in this pass (status: proposed). Owner reviews; constitution edit is a separate gate. |
| `spec-driven-development/docs/UI-LIFECYCLE-VARIANT.md` | Create (F-11) | Single-page authoring guide for the variant. |
| `spec-driven-development/specs/2026-06-09-ui-lifecycle-variant/spec.md` | Modify (this pass) | Pass 2 finalization (you are here). |
| `spec-driven-development/specs/2026-06-09-ui-lifecycle-variant/validation.md` | Modify (this pass) | Lock REQUIRED items at pass 2 close. |
| `spec-driven-development/specs/2026-06-09-ui-lifecycle-variant/plan.md` | Modify (this pass) | Pass 2 authoring. |
| `spec-driven-development/specs/2026-06-09-ui-lifecycle-variant/tasks.md` | Create (this pass) | Pass 2 authoring. |

Total F-11 surfaces: 7 files (5 modify, 2 create).
Total pass 2 surfaces (this commit): 5 files (4 modify in this spec
dir + 1 ADR create).

**Out of scope for F-11**: `constitution/principles.md` (separate
Level-2 gate after owner reads ADR-014); any other spec dir's
`validation.md`; any non-`schema_lint` CLI tool; any third-party
Python dependency (Article V; stdlib only).

---

## API Changes

Additive only. No new third-party Python dependencies (Article V;
stdlib only -- argparse, sqlite3, pathlib, json, sys, os, re).

- **`schema_lint.py` behavior change (additive)**: a new code path
  triggered by `ui-variant: true` on a spec dir's `spec.md`. For such
  spec dirs, `validation.md` is dispatched to the variant validator
  (`check_validation_variant`) which accepts the `## Delta Entries`
  section. For all other spec dirs, behavior is **byte-identical** to
  the pre-SDD-018 implementation.
- **No new CLI flags in F-11 v1.** Append-only enforcement (AC-3) is
  always-on for variant spec dirs. If F-11 testing surfaces a need for
  an opt-out flag, F-11 may add it; otherwise no new flags.
- **No new exit codes.** Existing `{0, 1, 2}` semantics preserved:
  0 clean, 1 findings, 2 usage error. `[delta]` findings count as
  ordinary findings (exit 1).
- **JSON output schema preserved**: existing
  `{path, kind, issue, severity}` shape unchanged. Delta-originated
  findings carry `issue` strings prefixed `[delta] ...`.

---

## Test Strategy

All tests live in `spec-driven-development/cli/test_schema_lint.py`
(or, if that file exceeds ~600 lines after adds, F-11 may split into a
new `test_schema_lint_variant.py` -- F-11 author's call). Existing
test pattern (`tempfile.TemporaryDirectory` + write fake repo +
invoke `schema_lint.scan()`) carries over.

Test classes (target ~12-18 new methods total):

1. **`UIVariantMarkerRecognition`** -- proves AC-1
   - `test_marker_true_dispatches_to_variant_validator`
   - `test_marker_false_keeps_strict_behavior`
   - `test_marker_absent_keeps_strict_behavior`
   - `test_marker_malformed_value_is_lint_error`

2. **`DeltaEntrySchema`** -- proves AC-2
   - `test_well_formed_entry_passes`
   - `test_missing_timestamp_yields_delta_error`
   - `test_missing_author_yields_delta_error`
   - `test_missing_item_type_yields_delta_error`
   - `test_missing_rationale_yields_delta_error`
   - `test_item_type_outside_enum_yields_delta_error`
   - `test_de_id_non_monotonic_yields_delta_error`

3. **`DeltaAppendOnlyAndErrorPrefix`** -- proves AC-3 and AC-4
   - `test_delta_findings_carry_delta_prefix_in_human_output`
   - `test_delta_findings_carry_delta_prefix_in_json_output`
   - `test_non_variant_spec_dir_unaffected_by_variant_rules`

4. **`RetroactiveDemoPathAllowlist`** -- proves AC-5
   - `test_retroactive_demo_in_state_dashboard_accepted`
   - `test_retroactive_demo_in_other_spec_dir_yields_delta_error`

5. **`StateDashboardDemoMigration`** -- proves AC-6 (integration; runs
   against the real spec dir after F-11 migration)
   - `test_state_dashboard_validation_md_passes_variant_validator`
   - `test_state_dashboard_spec_md_has_ui_variant_marker`

6. **`ADR014ExistsAndShapeChecks`** -- proves AC-7
   - `test_adr_014_file_exists_with_proposed_status`
   - `test_adr_014_contains_proposed_article_xii_section`

7. **`DocsPageExistsAndCrossLinks`** -- proves AC-9 and AC-10
   - `test_ui_lifecycle_variant_doc_exists`
   - `test_doc_referenced_from_templates_and_adr_014`

Test-count math (binding R-item): pre-F-11 baseline is the test count
at the close of F-10 pass 2. The PI-5 risk-register cites 273 as the
working baseline; F-11 SW Dev must re-measure at session start and
report the actual number in the F-11 final report. AC-8 R-item
asserts `>= 273` as the floor; the F-11 effective floor is
`actual_baseline + new_variant_tests`.

No regression: the existing test classes (`SchemaLintAcceptance`,
`ArtifactContractAcceptance`) must continue to pass unchanged.

---

## Traceability Matrix

| CLARIFY Q | Acceptance Criterion | Validation R-item(s) | Planned Task(s) | Test Class |
|-----------|---------------------|---------------------|-----------------|------------|
| Q2, Q3 | AC-1 marker recognition | R-1 | T-018-02 | `UIVariantMarkerRecognition` |
| Q1, Q2, Q9 | AC-2 delta entry schema | R-2 | T-018-02; T-018-03 | `DeltaEntrySchema` |
| Q1, Q8 | AC-3 append-only | R-3 | T-018-02 | `DeltaAppendOnlyAndErrorPrefix` |
| Q4 | AC-4 `[delta]` prefix | R-4 | T-018-02 | `DeltaAppendOnlyAndErrorPrefix` |
| Q5, Q8 | AC-5 retroactive-demo allow-list | R-5 | T-018-02 | `RetroactiveDemoPathAllowlist` |
| Q5 | AC-6 state-dashboard migration | R-6 | T-018-04 | `StateDashboardDemoMigration` |
| Q6 | AC-7 ADR-014 drafted | R-7 | T-018-05 (done in F-10 pass 2) | `ADR014ExistsAndShapeChecks` |
| Q1-Q9 + OWNER-ATTENTION 1 | AC-9 docs page | R-9 | T-018-06 | `DocsPageExistsAndCrossLinks` |
| Q2 | AC-10 template parity | R-10 | T-018-03 | `UIVariantMarkerRecognition` + manual review |
| Article X rule 3 | AC-8 test suite + lint + state.md | R-8, R-11, R-12 | T-018-07 (close verification) | full-suite run; manual check |
| Q7 (non-binding) | n/a (PI-6 plan input only) | n/a | n/a (documented in [`plan.md`](./plan.md) "Future Work") | n/a |

---

## CLARIFY State

CLARIFY is **closed**. All 9 questions + OWNER-ATTENTION items
answered at commit `754fda6`. See [`clarify.md`](./clarify.md) for
verbatim owner answers and the post-close summary table.

---

## Cross-References

- PI plan: [`../../sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md)
  (PI Objective 3, Sprint 3 row, Risk row 5)
- Sprint 3 prep notes: [`../../sprints/PI-5/SPRINT-3-PREP-NOTES.md`](../../sprints/PI-5/SPRINT-3-PREP-NOTES.md)
- Backlog row: [`../../backlog/BACKLOG.md`](../../backlog/BACKLOG.md) (SDD-018; SDD-034 P3 follow-up)
- F-10 kickoff prompt: [`../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md`](../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md)
- F-11 implementation prompt: [`../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md`](../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md)
- Sibling artifacts:
  [`./clarify.md`](./clarify.md) (closed, status: done) |
  [`./validation.md`](./validation.md) (LOCKED at pass 2 close) |
  [`./plan.md`](./plan.md) (authored in pass 2) |
  [`./tasks.md`](./tasks.md) (created in pass 2)
- Article X (current strict rule): `constitution/principles.md` Article X
- Article XI (serial gate; precedent for new-article path): `constitution/principles.md` Article XI; ADR-013
- ADR-014 (drafted in this pass, status: proposed): [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md)
- Retroactive demo target: [`../2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
