# Feature Spec: {TITLE}

<!--
Optional: SDD-018 UI Lifecycle Variant marker.
If this feature is iterative visual / UI work and you want the variant's
post-lock delta mechanism, add the line below to your spec.md frontmatter:

    ui-variant: true

See spec-driven-development/docs/UI-LIFECYCLE-VARIANT.md for marker syntax,
delta entry schema, item-type values, the forward-only migration rule, and
the state-dashboard demo reference. Default (absent or `false`) keeps
strict Article X behavior.
-->

- Date: {DATE}
- Author: {AUTHOR}
- Status: {STATUS}
- Priority: {PRIORITY}
- Sprint: {SPRINT}
- Spec ID: {SPEC_ID}

---

## Problem Statement

{PROBLEM_STATEMENT}

## Proposed Solution

{PROPOSED_SOLUTION}

## Acceptance Criteria

Each criterion MUST be phrased as a testable assertion that an automated or
manual check can prove true or false.

1. Given {PRECONDITION_001}, when {ACTION_001}, then {ASSERTABLE_OUTCOME_001}.
2. Given {PRECONDITION_002}, when {ACTION_002}, then {ASSERTABLE_OUTCOME_002}.
3. Given {PRECONDITION_003}, when {ACTION_003}, then {ASSERTABLE_OUTCOME_003}.

## Affected Modules

- Files:
  - {FILE_PATH_001}
  - {FILE_PATH_002}
- Directories:
  - {DIRECTORY_PATH_001}
  - {DIRECTORY_PATH_002}

## Data Model Changes

{DATA_MODEL_CHANGES_OR_NONE}

## API Changes

{API_CHANGES_OR_NONE}

## Test Strategy

- Unit: {UNIT_TEST_PLAN}
- Integration: {INTEGRATION_TEST_PLAN}
- End-to-end/manual: {E2E_OR_MANUAL_TEST_PLAN}
- Regression: {REGRESSION_TEST_PLAN}

## Validation Contract

The binding validation contract for this feature lives in the sibling file
`validation.md` in this feature directory. It is written during `/spec`, locked
at `/tasks`, and must have zero unchecked required items before implementation
can be considered complete.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| {REQ_001} | {TEST_001} | {MODULE_001} |
| {REQ_002} | {TEST_002} | {MODULE_002} |

## Open Questions

- {OPEN_QUESTION_001}
- {OPEN_QUESTION_002}

## Out of Scope

- {OUT_OF_SCOPE_001}
- {OUT_OF_SCOPE_002}
