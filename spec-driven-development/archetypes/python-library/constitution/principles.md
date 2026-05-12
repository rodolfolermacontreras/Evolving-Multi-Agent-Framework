---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Principles

{{PROJECT_NAME}} inherits the framework's Articles I-X for spec-driven development: ideas are clarified before design, plans precede implementation, tasks are scoped, quality gates are explicit, and human approval governs significant product and architecture choices.

Host-specific articles for this Python library are listed below. Rename, amend, or expand them after the first architecture review.

## Article H1: Public API Stability

Public symbols are intentional. Adding, renaming, or removing public functions, classes, modules, exceptions, or configuration keys requires an explicit note in the spec or plan.

## Article H2: Imports Are Safe

Importing {{PROJECT_NAME}} must not perform network calls, write files, read secrets, start subprocesses, or execute long-running computation.

## Article H3: Tests Describe Behavior

Tests should verify observable behavior from the user perspective. Prefer parametrized pytest cases for boundary tables and regression tests for every confirmed bug.

## Article H4: Types Are Part of the Interface

Public call signatures use precise type hints. If a type is intentionally broad, document why and validate at runtime where user input crosses a boundary.

## Article H5: Dependencies Must Earn Their Place

Runtime dependencies require a clear benefit. Development-only tools belong in optional dependency groups and should not leak into the consumer install path.

## Article H6: Documentation Follows the API

Every public capability has a README example or docstring showing the normal path and at least one failure or edge case when relevant.

## Amendment Process

{{OWNER}} may approve amendments after an Architect recommendation. Amendments update `last_amended` and preserve the versioned frontmatter.
