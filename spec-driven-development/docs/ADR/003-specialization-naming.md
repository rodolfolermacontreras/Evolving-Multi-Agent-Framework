# ADR-003: Standardize Agent Specialization Names

- Date: 2026-05-20
- Status: accepted

## Context

As the worker roster grows, ad-hoc names will drift, make dispatch harder, and reduce clarity about role, focus area, and uniqueness.

## Decision

Adopt the `{role}-{firstname}-{domain}-{NNN}` naming convention for specialized agents. Use a fixed first-name pool to prevent naming drift, keep the role explicit for routing, include a domain tag for dispatch context, and end with a numeric suffix for uniqueness.

## Consequences

Names become easier to sort, search, and reason about during fleet dispatch and roster maintenance. The tradeoff is a slightly more rigid naming scheme, but that rigidity supports better consistency and machine-readable dispatching.

## Alternatives Considered

- Free-form specialized agent names
- Role-only identifiers without domain tags
