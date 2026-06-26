---
name: role-creation
description: "Use during /hire. Knows the agent file templates, agents.json roster schema, exec/state.md Fleet section schema, and ledger decisions row convention for role-creation events. Generates draft files for human approval; never auto-applies."
argument-hint: "Which role and mode (generic | specialist)?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---
# Role Creation
Use this operational skill only from `/hire`. The slash command owns orchestration and approval; this skill owns the templates, naming rules, roster schema, Fleet state schema, and ledger convention.
## Inputs
- Mode: `generic` or `specialist`.
- Requested role id and one-sentence rationale.
- Today's `YYYY-MM-DD` date.
- Current `agents.json` and `exec/state.md`.
- For specialists: promoted-from generic id plus dispatch ids or SHAs.
## Generic agent template
Create `.github/agents/<role-name>-general.agent.md` from `.github/agents/_TEMPLATE-worker.agent.md`.
Fill placeholders:
- `{{ROLE_NAME}}`: `<role-name>-general`
- `{{ROLE_DESCRIPTION}}`: concise generic worker description
- `{{CREATED_DATE}}`: current date
- `{{ROLE_KIND}}`: `generic`
- `{{SPECIALIST_PROVENANCE}}`: `None; generic role created via /hire.`
The file must have frontmatter `name`, `description`, and handoff back to `principal-software-developer`.
## Specialist agent template
Create `.github/agents/<role>-<name>-<domain>-<n>.agent.md` from the same template. Specialist ids follow ADR-0003: `<role>-<name>-<domain>-<n>`.
Fill placeholders:
- `{{ROLE_NAME}}`: specialist id
- `{{ROLE_DESCRIPTION}}`: domain-specific permanent specialist description
- `{{CREATED_DATE}}`: current date
- `{{ROLE_KIND}}`: `specialist`
- `{{SPECIALIST_PROVENANCE}}`: cited dispatch ids or SHAs
## Specialist skill pack
Specialist mode drafts `.github/skills/domain/<role>-<domain>/SKILL.md`:
```markdown
---
name: <role>-<domain>
description: "Use when dispatching <role> work in the <domain> domain to the promoted specialist. Captures domain rules, inputs, quality checks, and escalation triggers."
argument-hint: "Dispatch brief for <domain> work"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# <Title>

## When to Use
## Dispatch Inputs
## Domain Rules
## Quality Checks
## Escalation Rules
## Evidence and Provenance
```
Allow one to three skills; default to one.
## Roster schema
`spec-driven-development/roster/agents.json` is a JSON array. Every entry uses:
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
Specialist provenance:
```json
{
  "promoted_from": "<role>-general",
  "evidence_dispatches": ["dispatch-id-or-sha"],
  "promoted_via": "/hire",
  "ledger_decision_id": null
}
```
Patch `ledger_decision_id` after approved ledger insert.
## Fleet schema
`spec-driven-development/exec/state.md` must contain one section:
```markdown
## Fleet

- Principals: 4 (Executive Manager, Product Manager, Architect, Software Developer)
- Generic workers: <N> (developer-general, ux-designer-general, qa-engineer-general, data-scientist-general[, ...])
- Specialists: <M> (<list of specialist IDs>)
- Last role created: <YYYY-MM-DD> -- <role-name> (<kind>)
```
Use `Specialists: 0 (none)` when empty and `Last role created: none` before first approved `/hire`.
## Ledger convention
Use existing table `decisions` in `spec-driven-development/ledger/fleet.db`; do not migrate schema.
- `level`: `2`
- `decider`: `human`
- `artifact`: new agent file path
- `description`: `HIRE <kind>:<role-id> -- <one-sentence rationale>`
Insert only after approval.
## Validation rules
- Kebab-case role ids.
- Generic ids end in `-general`.
- Specialist ids follow `<role>-<name>-<domain>-<n>`.
- Target files do not exist and roster id is unique.
- Specialists cite evidence dispatches.
- Skill pack path is under `.github/skills/domain/`.
- No constitution or ledger schema edits.
## Examples
Generic: `/hire azure-data-engineer generic` drafts `.github/agents/azure-data-engineer-general.agent.md`, adds a generic roster row, updates Fleet, and prepares `HIRE generic:azure-data-engineer-general -- Needed recurring ownership for Azure data pipeline implementation tasks.`
Specialist: `/hire data-scientist-bob-forecast-1 specialist` requires dispatch evidence, drafts `.github/agents/data-scientist-bob-forecast-1.agent.md` and `.github/skills/domain/data-scientist-forecast/SKILL.md`, adds provenance from `data-scientist-general`, and prepares `HIRE specialist:data-scientist-bob-forecast-1 -- Promoted after repeated successful forecasting dispatches.`
## Output
Return a draft report and proposed file contents. Never write files, update JSON, or insert ledger rows before human approval.
