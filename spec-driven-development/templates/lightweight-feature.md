---
id: {ARTIFACT_ID}
type: feature
status: draft
owner: principal-software-developer
updated: {DATE}
---

# Lightweight Feature: {TITLE}

<!--
SDD-048 D-2 -- combined lightweight-feature artifact.

ONE file that collapses the four lifecycle docs (clarify/spec + plan +
tasks + validation) for SMALL work. Use this ONLY when the `## Eligibility`
rule below is satisfied. For anything larger, use the full four-doc path
(feature-spec.md + plan.md + task-list.md + validation.md).

`type: feature` is recognized by `cli/schema_lint.py`
(ARTIFACT_TYPE_ENUM). The four-doc types are unchanged.

Article X is preserved: the `## Validation Contract` section is authored
BEFORE implementation and its REQUIRED items are checkable. The lightweight
path does NOT bypass the validation contract -- it inlines it.
-->

## Story

{What is being built and why, in two or three sentences. This is the
CLARIFY/SPEC essence: the user-visible behavior and the motivation. Name
the smallest change that delivers the value.}

## Requirements

RFC-2119 items, each with a stable per-item ID. Keep them testable.

- R-1 ({MUST|SHOULD|MAY}) {requirement}.
- R-2 ({MUST|SHOULD|MAY}) {requirement}.
- R-3 ({MUST|SHOULD|MAY}) {requirement}.

## Plan

For <5-file work an inline plan is sufficient; cross-link only if needed.

- Files in scope (max 4): {file-1}, {file-2}, ...
- Files OUT of scope (do not modify): {protected-files-or-NONE}.
- Approach: {one short paragraph -- the how}.
- Test strategy: {what tests prove the requirements; TDD red-first}.

## Validation Contract

> Authored DURING this doc's creation, LOCKED before implementation begins.
> The Article X lock holder for this feature. NOT weakened by the
> lightweight path.

### Required Items (strict)

- [ ] R-1 proven by {test name or check}.
- [ ] R-2 proven by {test name or check}.
- [ ] R-3 proven by {test name or check}.
- [ ] Full suite passes (no decrease in test count).
- [ ] `cli/schema_lint.py` exits 0.

### Manual Checks

- [ ] {MANUAL_CHECK_001}
- [ ] {MANUAL_CHECK_002_OR_NONE}

### Definition of Done

Merge-ready only when every REQUIRED item above is checked, the full suite
passes with no test-count decrease, the branch is clean (no debug prints or
throwaway instrumentation), and this contract has zero unchecked required
items. Any skipped item carries a written justification accepted by the
spec-compliance reviewer. Production-code changes without a corresponding
test require a `[NO-TEST-NEEDED]` tag with accepted justification.

## Eligibility

The lightweight (combined) path is permitted ONLY when ALL hold:

- The change touches fewer than five (5) files.
- No Level-2 architectural decision is required (no new dependency, no new
  cross-module pattern, no schema/data-contract change).
- No new public surface that warrants a standalone spec.

This mirrors the Spec Sizing Rule and the framework's tiered-ceremony
principle (Constitution Article VI). If any condition fails, STOP and use
the full four-doc lifecycle instead.
