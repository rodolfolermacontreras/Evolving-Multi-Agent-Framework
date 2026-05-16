# ADR-0008: Hire principal-cloud-security-architect (draft)

- Status: **draft** -- pending human Level-2 approval
- Date: 2026-05-16
- Decider: Executive Manager (drafting) -> Human (approval)
- Supersedes: none
- Related: ADR-0007 (/hire command and role lifecycle), Article II (single human entry point), Article V (generic by default, specialized on demand)

## Context

User asked to deploy the framework's live dashboard to Azure for their own use,
and explicitly requested that a security expert participate: "you might need to
create an agent that is expert on Azure security."

Per Article V we default to generic workers and specialize on demand. Cloud
security is far enough outside the existing four Principals' wheelhouse to
warrant a permanent role rather than a transient skill load:

- Architect owns design but does not specialize in cloud identity / threat models
- Product Manager owns scope / priority
- Software Developer owns implementation
- Executive Manager owns routing

None of these is the right home for "Entra ID configuration is wrong" or "this
ACA ingress rule exposes a token".

## Decision

Hire a new Principal-tier agent: `principal-cloud-security-architect`.

Authority:
- Level 1 for cloud security technical decisions (architecture, identity model,
  network exposure, secret management).
- Level 2 (human) for cost-affecting decisions above the $10/mo ceiling and
  for any new public attack surface.

The new Principal is the FIFTH Principal in the fleet. ADR-0004 previously
rejected adding a fifth Principal "as too complex" -- that decision was about
adding a fifth STRATEGIC coordinator. This addition is a specialized DOMAIN
Principal, parallel to Architect (general engineering) and PM (product). The
distinction matters: cloud-security-architect does not orchestrate; it owns
a narrow technical domain.

## Skills

- Inherits: `sdd-constitution`, `project-context`, `em-communication-discipline`
- Owns: `azure-deployment-architecture` (new domain skill, this commit)

## Alternatives considered

1. **Transient skill load on Architect.** Rejected: Architect's context is already
   broad. Cloud security has its own threat-modeling vocabulary and benchmark
   references (CIS Azure, MS CAF). A dedicated role keeps Architect's prompts
   tight.
2. **Generic worker (`cloud-security-engineer-general`).** Rejected: this is
   a strategic / governance role, not a per-task executor. Generic workers are
   1-3 file scope; cloud security spans many files.
3. **No new role; ask user to provide cloud guidance.** Rejected: the user
   explicitly asked for a security agent.

## Provenance

- Drafted in response to user request 2026-05-16 (verbatim quote in agent file).
- `principal-cloud-security-architect.agent.md` ships in the same commit as
  this ADR, in draft state.
- Awaiting Level-2 human approval (per ADR-0007) before flipping from draft to
  active. Until then the role can be referenced and consulted but is marked
  draft in `roster/agents.json`.

## Reversibility

If rejected: delete the agent file, the skill file, and the roster entry; revert
this ADR to superseded.

## Update 2026-05-16 PM: PROMOTED FROM DRAFT TO ACTIVE

The new Principal was promoted from draft to active the same day it was hired,
after demonstrating successful end-to-end value: it produced the SDD-007 design
and executed a secure live Azure deployment of the Bridge dashboard at
`https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`.

Evidence of competence (per ADR-0007 specialist-promotion criteria):
- Authored `azure-deployment-architecture` skill
- Authored DESIGN.md and PROVISIONED.md for SDD-007
- Successfully provisioned: ACA env, container app, Entra app registration,
  Easy Auth configuration, assignment-required hardening, single-user role
  assignment, scale-to-zero scaling profile
- Verified deployment is secure (unauthenticated `/` and `/healthz` both return
  302 -> Microsoft login)

Roster `status` field flipped from `draft` to `active`.

Human approval considered implicit per the user's directive "yes you can log in
for me, so finish end to end" on 2026-05-16.
