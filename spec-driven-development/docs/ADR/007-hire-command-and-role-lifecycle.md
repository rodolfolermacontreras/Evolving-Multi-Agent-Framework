# ADR-0007: Hire Command and Role Lifecycle

- Status: Accepted
- Date: 2026-05-12
- Deciders: Rodolfo Lerma (project owner)
- Supersedes: none
- Related: ADR-0003 (Specialization Naming), ADR-0006 (Constitution Semantic Versioning and Propagation Check)

---

## Context

The framework's operating model has four Principal agents coordinating worker
agents that do the actual work. The initial worker fleet includes only four
generic templates: `developer-general`, `ux-designer-general`,
`qa-engineer-general`, and `data-scientist-general`.

ADR-0003 documented how specialist names should work, but it left role creation
as prose. That created an implementation gap: when a project needs a Data
Analyst, AI Engineer, Azure Data Engineer, or any other missing role, the
Principal Software Developer had no first-class workflow for creating that role.
Likewise, when a generic worker repeatedly proves excellent in a domain, there
was no governed promotion path from generic worker to permanent specialist.

Role creation is a permanent fleet change. It affects dispatch routing,
executive state, future skill loading, and the audit trail for why the team
changed. The framework needs a single command that makes those changes visible,
approvable, and traceable.

## Decision

Add `/hire` as the Principal Software Developer's command for worker role
lifecycle management.

Concretely:

1. Add `.github/prompts/hire.prompt.md` as the slash command protocol.
2. Add `.github/skills/operational/role-creation/SKILL.md` for the mechanical
   templates, roster schema, Fleet state schema, and ledger decision convention.
3. Support two modes:
   - `generic`: create `.github/agents/<role-name>-general.agent.md` for a new
     recurring worker role the project now needs.
   - `specialist`: promote a proven generic worker to
     `.github/agents/<role>-<name>-<domain>-<n>.agent.md` with a domain skill
     pack under `.github/skills/domain/<role>-<domain>/`.
4. Require Level 2 human approval before files land because role creation is a
   permanent fleet change.
5. Add `.github/agents/_TEMPLATE-worker.agent.md` as the canonical worker
   skeleton used by `/hire`.
6. Migrate `spec-driven-development/roster/agents.json` to a flat schema that
   records `kind`, `role`, `specialization`, `created_at`, and `provenance`.
7. Add a `## Fleet` section to `spec-driven-development/exec/state.md` so the
   Executive Manager can answer who is on the team without querying the ledger.
8. Record approved role creation events in the existing `decisions` table of
   `spec-driven-development/ledger/fleet.db` using:
   `HIRE <kind>:<role-id> -- <one-sentence rationale>`.
9. Notify the Executive Manager through the standard Principal Software
   Developer return handoff after approval.

The state file gives fast awareness; the ledger gives provenance. Both are
required for role creation events.

## Considered Alternatives

### Rejected: auto-promotion based on heuristics

The framework could automatically promote workers after a threshold number of
successful dispatches. We rejected this because specialization is a durable team
change and success quality is contextual. Dispatch count alone does not prove a
worker deserves a permanent identity or domain skill pack.

### Rejected: per-role slash commands such as `/hire-developer`

The framework could create separate commands for each role family. We rejected
this because role names are open-ended. A single `/hire` command with generic and
specialist modes keeps lifecycle policy centralized and avoids command sprawl.

### Rejected: only update the roster

The framework could treat `agents.json` as the sole source of fleet truth. We
rejected this because the Executive Manager needs an immediate state summary and
future auditors need the rationale for why a role was created. Roster, state,
and ledger serve different purposes.

## Consequences

### Positive

- The Principal Software Developer can create missing worker roles without
  waiting for a broader framework evolution cycle.
- Specialist promotion now requires evidence and provenance instead of ad hoc
  naming.
- Executive state shows the current fleet at a glance.
- The ledger can answer why a role exists and who approved it.
- The worker template keeps newly hired roles consistent with existing generic
  workers.
- ADR-0003's naming model is now executable through `/hire`.

### Negative or risky

- The workflow adds ceremony to role creation. Mitigation: only permanent fleet
  changes use `/hire`; temporary needs can still be handled with dispatch briefs.
- The roster schema migration requires consumers to read the new flat array
  format. Mitigation: every entry now has explicit `kind` and `path` fields.
- Specialist promotion can be delayed when evidence is missing. Mitigation: the
  ledger dispatch history is the intended evidence source.
- Domain skill packs can become too granular. Mitigation: specialist mode limits
  each promotion to one to three skills and defaults to one.

### Process changes

- `/hire` becomes the only command for permanent worker role creation and
  specialist promotion.
- Role creation is a Level 2 approval event.
- `exec/state.md` includes a Fleet section.
- `decisions` rows with `HIRE` descriptions become the provenance trail for
  approved role changes.
- Principal Software Developer owns the worker role lifecycle and returns results
  to the Executive Manager after approval.

## Status

Accepted. Implemented in commit that introduces this ADR.
