---
feature: schema-lint
status: implementing
created: 2026-05-16
pi: PI-2
sprint: B
priority: P2
spec_id: SDD-006
---

# Feature Spec: cli/schema_lint.py (SDD-006)

- Date: 2026-05-16
- Author: Principal Software Developer

## Problem

YAML frontmatter on agent (`.agent.md`), skill (`SKILL.md`) and prompt (`.prompt.md`) files is hand-written. Missing required fields, wrong types (e.g. `version: 1.0` instead of `'1.0'` per ADR-0006), and name/path mismatches go undetected until an agent fails to load. No automated guard exists.

## Solution

A stdlib-only Python CLI: `cli/schema_lint.py` that walks `.github/agents/`, `.github/skills/`, and `.github/prompts/`, parses each file's frontmatter, and verifies required fields by file type. Non-zero exit on any failure.

## Acceptance Criteria

1. `python schema_lint.py` (no args) scans `.github/agents/`, `.github/skills/**/SKILL.md`, and `.github/prompts/` from the repo root and exits 0 when all files conform.
2. Agent files require: `description` field.
3. Skill files require: `name`, `description`, `license`, and nested `metadata.author` + `metadata.version`.
4. Prompt files require: `description` field.
5. When a `version` field exists at any nesting level, it must be a quoted string (matches ADR-0006). `version: 1.0` (unquoted) fails.
6. When a skill's `name:` does not match its containing directory name, fail.
7. `--json` flag emits machine-readable findings to stdout.
8. `--repo-root <path>` overrides the default scan root for testability.
9. Returns exit code 0 on clean, 1 if any findings, 2 on usage error.
10. Pure Python stdlib at runtime.

## Out of scope

- Auto-fixing findings (read-only linter)
- Validating cross-references between files (separate concern, future)
- Schema for ADRs, templates, roster JSON (separate file types)

## Validation Contract

See sibling `validation.md`.
