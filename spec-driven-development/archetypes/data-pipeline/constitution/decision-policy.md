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

- Changing mission, target users, public commitments, or licensing posture
- Accepting security, privacy, data-loss, publication, or compatibility risk
- Skipping a required quality gate

## Level 2: Principal Recommendation + Owner Approval

Level 2 decisions are important technical or product choices. The relevant Principal agent recommends; {{OWNER}} approves.

Examples:

- Choosing or changing core framework, package manager, storage, orchestration, or distribution strategy
- Adding runtime dependencies
- Changing supported Python versions or operating systems
- Creating new domain skills or quality gates

## Level 3: Agent-Executable Within Guardrails

Level 3 decisions are local implementation choices covered by an approved task, plan, or existing convention.

Examples:

- Naming private helpers
- Adding tests for already-approved behavior
- Refactoring internals without changing public contracts
- Updating docs to match implemented behavior

## Escalation Rule

When uncertain, agents escalate one level. A small delay is cheaper than an accidental product or architecture decision.
