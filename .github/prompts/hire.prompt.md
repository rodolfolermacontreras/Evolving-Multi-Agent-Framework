---
name: hire
description: "Create a new worker role -- generic (a new role the project needs, e.g. data-analyst, ai-engineer, azure-data-engineer) or specialist (promote a generic worker who has proven excellence in a domain to a permanent named specialist with their own skill pack). Owned by the Principal Software Developer. Level 2 decision: human approves the draft before files land. Backs ADR-0003 + ADR-0007."
argument-hint: "Role name and mode: '<role-name> generic' or '<role>-<name>-<domain>-<n> specialist'"
---
You are running `/hire`, the Principal Software Developer workflow for permanent worker role lifecycle changes.
## Purpose
Create a human-approved draft for either a missing generic worker role or an earned specialist promotion. This makes ADR-0003 executable and records fleet changes in roster, Executive state, and ledger provenance.
## Authority
- Owner: Principal Software Developer.
- Approval: Level 2; human approves before files land.
- Scope: worker roles only, never Principal agents.
- Notification: after approval, return to the Executive Manager through the standard handoff.
## Arguments
Accepted forms:
```text
/hire <role-name> generic
/hire <role>-<name>-<domain>-<n> specialist
```
Examples:
```text
/hire data-analyst generic
/hire ai-engineer generic
/hire azure-data-engineer generic
/hire data-scientist-bob-forecast-1 specialist
/hire azure-data-engineer-claire-pipelines-1 specialist
```
If mode is missing or not exactly `generic` or `specialist`, stop and request corrected input.
## Required reading
Read before drafting:
1. `.github/agents/_TEMPLATE-worker.agent.md`
2. `.github/agents/developer-general.agent.md`
3. `.github/agents/principal-software-developer.agent.md`
4. `.github/skills/operational/role-creation/SKILL.md`
5. `spec-driven-development/roster/agents.json`
6. `spec-driven-development/exec/state.md`
7. `spec-driven-development/ledger/schema.sql`
8. `spec-driven-development/docs/ADR/003-specialization-naming.md`
9. `spec-driven-development/docs/ADR/007-hire-command-and-role-lifecycle.md`
Do not rely on memory for roster entries, paths, or ledger fields.
## Shared pre-checks
Confirm before drafting:
1. Requested id is kebab-case.
2. Requested id is unique in `agents.json`.
3. Target agent file does not already exist.
4. Request is for a worker, not a Principal.
5. Rationale describes recurring capability.
6. No constitution file or ledger schema change is needed.
If any check fails, return a blocked draft report with evidence.
## Mode A: generic
Use when the project needs a recurring role that is not in the fleet.
Input:
```text
<role-name>
```
Draft id and path:
```text
<role-name>-general
.github/agents/<role-name>-general.agent.md
```
Generic checks:
1. `<role-name>-general` is absent from roster.
2. Target file is absent.
3. Role has clear DO and DO NOT boundaries.
4. Role can inherit `sdd-constitution` and `project-context` by default.
Generic draft artifacts:
- Agent file from `_TEMPLATE-worker.agent.md`.
- Roster entry: `kind: "generic"`, `role: "<role-name>"`, `specialization: null`, `provenance: null`.
- Fleet section with generic worker count updated.
- Pending ledger description: `HIRE generic:<role-id> -- <rationale>`.
Generic placeholders:
- `{{ROLE_NAME}}`: `<role-name>-general`
- `{{ROLE_DESCRIPTION}}`: concise role description
- `{{CREATED_DATE}}`: today's `YYYY-MM-DD`
- `{{ROLE_KIND}}`: `generic`
- `{{SPECIALIST_PROVENANCE}}`: `None; generic role created via /hire.`
## Mode B: specialist
Use when a generic worker has proven repeated excellence in a domain. Specialization is earned, not guessed.
Specialist id format from ADR-0003:
```text
<role>-<name>-<domain>-<n>
```
Draft paths:
```text
.github/agents/<role>-<name>-<domain>-<n>.agent.md
.github/skills/domain/<role>-<domain>/SKILL.md
```
Specialist checks:
1. Matching `<role>-general` exists.
2. Domain is narrower than the generic role.
3. Prior dispatch ids or SHAs are cited.
4. Evidence exists in `fleet.db` or is supplied by the human.
5. Skill pack path does not collide with unrelated skills.
If evidence is missing, stop and request dispatch ids or SHAs.
Specialist draft artifacts:
- Specialist agent file from `_TEMPLATE-worker.agent.md`.
- Domain skill pack under `.github/skills/domain/<role>-<domain>/`, one to three skills, default one.
- Roster entry with `kind: "specialist"`, role, specialization, and provenance.
- Fleet section with specialist count updated.
- Pending ledger description: `HIRE specialist:<role-id> -- <rationale>`.
Specialist provenance:
```json
{
  "promoted_from": "<role>-general",
  "evidence_dispatches": ["dispatch-id-or-sha"],
  "promoted_via": "/hire",
  "ledger_decision_id": null
}
```
Patch `ledger_decision_id` after the approved ledger insert.
## Agent file requirements
Every drafted agent must include frontmatter `name`, `description`, handoff `Return to Software Developer`, identity, scope, DO and DO NOT lists, inherited skills, dispatch intake rules, verification, and output format.
## Roster schema
After approval, `spec-driven-development/roster/agents.json` remains a JSON array. Every entry uses:
```json
{
  "id": "agent-id",
  "path": ".github/agents/agent-id.agent.md",
  "kind": "principal | generic | specialist",
  "role": "role-name",
  "specialization": null,
  "created_at": "YYYY-MM-DD",
  "provenance": null
}
```
Valid `kind` values: `principal`, `generic`, `specialist`.
## Fleet section schema
After approval, update or create exactly one `## Fleet` section in `spec-driven-development/exec/state.md`:
```markdown
## Fleet

- Principals: 4 (Executive Manager, Product Manager, Architect, Software Developer)
- Generic workers: <N> (developer-general, ux-designer-general, qa-engineer-general, data-scientist-general[, ...])
- Specialists: <M> (<list of specialist IDs>)
- Last role created: <YYYY-MM-DD> -- <role-name> (<kind>)
```
Use `Specialists: 0 (none)` when empty and `Last role created: none` before the first approved `/hire`.
## Ledger convention
After approval, insert one row into `spec-driven-development/ledger/fleet.db` using existing table `decisions`; never alter `schema.sql`.
- `decided_at`: current `YYYY-MM-DD`
- `level`: `2`
- `decider`: `human`
- `artifact`: new agent file path
- `description`: `HIRE <kind>:<role-id> -- <one-sentence rationale>`
## Draft report
Before approval, return this structure:
```markdown
# /hire Draft Report

## 1. Request
- Mode: generic | specialist
- Requested role id: ...
- Owner: Principal Software Developer
- Approval level: Level 2 human approval required

## 2. Preconditions
| Check | Result | Evidence |
|-------|--------|----------|
| Roster id unique | PASS/FAIL | ... |
| File path available | PASS/FAIL | ... |
| Evidence dispatches cited | PASS/FAIL/NOT APPLICABLE | ... |

## 3. Draft artifacts
- Agent file: `...`
- Skill pack: `...` or `not applicable`
- Roster update: `spec-driven-development/roster/agents.json`
- State update: `spec-driven-development/exec/state.md`
- Ledger decision: pending human approval

## 4. Draft content
<proposed file contents or unified diff>

## 5. Approval request
Reply with approval to land these files, or requested edits to revise the draft.
```
## Apply after approval
1. Re-read roster and paths to catch races.
2. Apply exactly the approved files.
3. Update `agents.json`.
4. Update `## Fleet`.
5. Insert the `decisions` row.
6. Patch specialist provenance with ledger decision id.
7. Validate `agents.json` parses.
8. Confirm drafted files exist.
9. Notify Executive Manager.
## Executive Manager handoff
Include role id, kind, rationale, files created, ledger decision id, and updated Fleet summary.
## Guardrails
- Do not create Principal agents through `/hire`.
- Do not create specialists without dispatch evidence.
- Do not skip human approval.
- Do not change constitution files, ledger schema, specs, archetypes, or CLI files.
- Do not delete or rename existing workers.
- Use `YYYY-MM-DD` dates and kebab-case ids.
- No emojis.
