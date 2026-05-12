---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Mission

## Project

{{PROJECT_NAME}} is a Python web service: FastAPI-first Python HTTP service with explicit contracts, maintainable workflows, and SDD traceability.

## Owner

{{OWNER}}

## Vision

Make {{PROJECT_NAME}} easy to understand, validate, run, and evolve without hiding critical assumptions.

## Users

Primary users are the people or systems that consume the project outputs. Secondary users are maintainers and AI agents contributing through the SDD lifecycle.

## Success Criteria

The project succeeds when:

- The first useful capability is documented and reproducible
- Quality gates run locally through documented commands
- Edge cases and failures are represented in tests or validation checks
- Releases or milestones can be recreated from a clean checkout
- Contributions trace from idea -> triage -> spec -> plan -> tasks -> implementation -> QA

## Core Values

1. CONTRACT FIRST: State expected behavior before implementation.
2. TESTABLE BY DEFAULT: New behavior has a repeatable validation path.
3. CLEAR ERRORS: Failures explain what happened and how to fix it.
4. SMALL SURFACE AREA: Prefer focused capabilities over broad accidental scope.
5. PORTABLE TOOLING: Development commands work on Windows, Linux, and macOS.
6. HUMAN OWNERSHIP: {{OWNER}} approves Level 1 and Level 2 product and architecture decisions.

## Non-Negotiables

- No major behavior without a validation contract
- No dependency or platform change without rationale
- No secret, credential, or private data committed to source
- No skipped quality gate without {{OWNER}} approval
- Dates use `YYYY-MM-DD`
