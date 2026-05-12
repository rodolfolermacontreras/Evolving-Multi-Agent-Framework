# ADR-002: Use a Two-Folder Split for SDD Assets

- Date: 2026-05-20
- Status: accepted

## Context

The SDD framework needs both Copilot-native assets and framework-owned operational assets. Mixing them in one place would make discovery, reuse, and tooling behavior less predictable.

## Decision

Use `.github/` for Copilot-native assets such as agents (`.agent.md`), prompts, instructions, and skills. Use `spec-driven-development/` for custom framework artifacts such as specs, templates, CLI tools, ledgers, backlog files, sprint files, and executive state.

## Consequences

Agents and prompt commands are auto-discovered where Copilot expects them, while the framework remains composable and tool-independent under `spec-driven-development/`. This split adds one more location to remember, but it keeps agents selectable, skills composable, and process state clearly separated from tool configuration.

## Alternatives Considered

- Store all SDD assets under `.github/`
- Store all SDD assets under `spec-driven-development/` only
