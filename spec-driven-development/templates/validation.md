# Validation Contract: {TITLE}

- Spec Reference: {SPEC_REFERENCE}
- Contract Date: {DATE}
- Author: {AUTHOR}
- Lock Point: `/tasks`

This contract is written DURING `/spec`, locked at `/tasks`, and verified at `/qa`.

---

## Automated Tests

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
