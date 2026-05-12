---
version: '1.0.0'
ratified: {{DATE}}
last_amended: {{DATE}}
---
# Decision Policy

{{PROJECT_NAME}} uses the standard three-tier decision model.

## Level 1: Human Approval Required

Level 1 decisions materially change product direction, risk, or external commitments. {{OWNER}} is the final approver.

Examples:

- Changing the library's mission or target user
- Introducing a breaking public API change after users depend on it
- Publishing the package publicly or changing licensing posture
- Adding telemetry, network behavior, or data collection
- Accepting a security risk or skipping a required quality gate

## Level 2: Principal Recommendation + Owner Approval

Level 2 decisions are important technical or product choices. The relevant Principal agent recommends; {{OWNER}} approves.

Examples:

- Choosing or changing build backend, package manager, or CI provider
- Adding runtime dependencies
- Changing supported Python versions
- Establishing release cadence or versioning policy
- Creating new domain skills or quality gates

## Level 3: Agent-Executable Within Guardrails

Level 3 decisions are local implementation choices covered by an approved task, plan, or existing convention.

Examples:

- Naming private helper functions
- Adding parametrized cases for an already-approved behavior
- Refactoring internals without changing public API
- Updating docs to match implemented behavior

## Escalation Rule

When uncertain, agents escalate one level. A small delay is cheaper than an accidental public API or release-policy decision.
