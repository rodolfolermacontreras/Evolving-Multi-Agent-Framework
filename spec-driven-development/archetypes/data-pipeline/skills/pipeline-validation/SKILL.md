---
name: pipeline-validation
description: "Use when working on Great Expectations, pandera, and pydantic-as-validator patterns for pipeline data contracts."
argument-hint: "What should this skill help design, implement, or review?"
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
  archetype: data-pipeline
---

# Pipeline Validation

Great Expectations, pandera, and pydantic-as-validator patterns for pipeline data contracts.

## When to Use

Load this skill when a task touches this archetype-specific concern, especially during specs, plans, implementation, tests, or review.

Do not load when the task is unrelated README prose, generic repository maintenance, or a different archetype's implementation concern.

## Working Rules

- Start from the host constitution and the approved task.
- Define the contract before implementation.
- Prefer small, testable units and explicit failure modes.
- Keep examples portable across Windows, Linux, and macOS.
- Document any trade-off that changes user-visible behavior.

## Checklist

- The behavior is described in user-facing terms.
- Validation covers happy path and at least one failure path.
- Error messages are actionable.
- Dependencies and platform assumptions are documented.
- The implementation can be verified from a clean checkout.
