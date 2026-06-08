# Validation Contract: {TITLE}

<!--
Optional: SDD-018 UI Lifecycle Variant `## Delta Entries` section.
If your spec.md carries `ui-variant: true`, you may append a
`## Delta Entries` section to record post-lock additions. Example:

    ## Delta Entries

    ### Delta DE-01 -- short title

    - timestamp: 2026-MM-DDTHH:MMZ
    - author: principal-{role}
    - rationale: <one-sentence reason>
    - item-type: add | wontfix | re-check | retroactive-demo

    Free Markdown body for the new REQUIRED item, the wontfix note,
    the re-check decision, or the retroactive-demo record.

Rules: DE-NN IDs are zero-padded, monotonically increasing, never re-used.
Entries are append-only (mutation or deletion fails `cli/schema_lint.py`).
`item-type: retroactive-demo` is allow-listed to a single spec dir
(SDD-018 proof case). See spec-driven-development/docs/UI-LIFECYCLE-VARIANT.md
for full schema and operational guidance. Strict-mode (no marker) spec
dirs are unaffected by this section.
-->

- Spec Reference: {SPEC_REFERENCE}
- Contract Date: {DATE}
- Author: {AUTHOR}
- Lock Point: `/tasks`

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Automated Tests

> **Cross-reference rule:** Each test name below maps to one or more AC
> identifiers from `spec.md`. Use the format `proves AC1` to link the
> test to its requirement. The spec is the single source of truth for
> acceptance criteria wording.
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

- [ ] {AUTOMATED_TEST_001}: proves {AC_OR_FR_REFERENCE_001}
- [ ] {AUTOMATED_TEST_002}: proves {AC_OR_FR_REFERENCE_002}
- [ ] {AUTOMATED_TEST_003}: proves {AC_OR_FR_REFERENCE_003}

## Specific Test Coverage Required

- [ ] Unit coverage for {UNIT_SCOPE_OR_NONE}
- [ ] Integration coverage for {INTEGRATION_SCOPE_OR_NONE}
- [ ] Regression coverage for {REGRESSION_SCOPE_OR_NONE}
- [ ] Error, empty, boundary, or permission cases: {EDGE_CASE_SCOPE_OR_NONE}

## Manual Checks

- [ ] {MANUAL_CHECK_001}
- [ ] {MANUAL_CHECK_002}
- [ ] {MANUAL_CHECK_003}

## Tone / UX Check

If applicable:

- [ ] User-facing copy is clear, concise, and consistent with product voice.
- [ ] Interaction states are verified: loading, success, empty, error, and disabled.
- [ ] Accessibility expectations are met for keyboard use, labels, focus, and contrast.

If not applicable, mark this section `[NO-UX-CHECK-NEEDED]` with a one-sentence
justification.

## Definition of Done

Implementation is merge-ready only when all automated tests listed above pass,
all required manual checks are confirmed, the branch is rebased cleanly, no debug
prints or throwaway instrumentation remain, and this validation contract has zero
unchecked required items. Any skipped item must include a written justification
accepted by the spec-compliance reviewer. Production-code changes without a
corresponding test require a task-level `[NO-TEST-NEEDED]` tag and accepted
justification before the IMPLEMENT gate can pass.
