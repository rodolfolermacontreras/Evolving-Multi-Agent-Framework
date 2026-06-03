# Level-2 Decision Brief: Hire principal-cloud-security-architect (worked example)

- Date: 2026-05-16
- Proposing Principal: principal-executive-manager (drafting on user's request)
- Trigger: User asked the framework to deploy its live dashboard to Azure
  for their own use AND explicitly requested a security expert: "you might
  need to create an agent that is expert on Azure security."
- Requested approval from: Rodolfo (human)
- Related ADR (drafted on approval): ADR-0008
- Status: **Approved 2026-05-16; promoted from draft to active same day after
  successful end-to-end deployment**

> This file is the retrospective worked example for SDD-014. The original
> ADR-0008 was drafted before this template existed. The friction analysis
> here is reconstructed from ADR-0008's "Alternatives considered" and from
> the SDD-007 design / provisioning artifacts to show what a populated
> Level-2 brief looks like in practice. Future Level-2 decisions submit the
> brief FIRST and the ADR follows on approval.

---

## 1. Money cost (one-time + recurring)

- One-time: $0 (no software license; Azure resource creation uses existing
  subscription).
- Recurring (monthly): under $10 (Azure Container Apps scale-to-zero
  profile + minimal Entra app registration; verified post-deploy).
- Recurring (annual): under $120 expected.
- Cost source / quote: Azure Container Apps pricing page + the
  scale-to-zero configuration captured in `SDD-007 PROVISIONED.md`.

Justification: cost ceiling was set at $10/month in the brief; actual cost
stayed within that envelope.

## 2. Complexity cost (added moving parts; new dependencies)

- New runtime dependency: none (cloud deployment uses existing Azure CLI
  and stdlib tooling; no new pip packages).
- New service / external integration: Azure Container Apps environment,
  Azure Container Registry, Microsoft Entra app registration, Easy Auth.
- New agent role: yes -- `principal-cloud-security-architect` becomes the
  fifth Principal in the fleet.
- New failure modes introduced: misconfigured Entra app registration could
  expose the dashboard publicly; an ACA ingress rule could leak tokens.
  These are mitigated by the new role's domain expertise.

## 3. Maintenance burden (who maintains; cadence of upkeep)

- Owner of new surface: principal-cloud-security-architect (Azure
  identity, network exposure, secret rotation) plus principal-software-developer
  (deployment automation).
- Upkeep cadence: as-needed for incident response; quarterly review of
  Entra app registration, RBAC assignments, and ACA scaling profile.
- What happens if the owner is unavailable: the role's playbooks live in
  `.github/skills/operational/azure-deployment-architecture/SKILL.md`;
  the Architect can execute them in the security role's absence with a
  Level-2 escalation if any change is irreversible.
- Estimated upkeep effort per cadence: ~1 hour quarterly for review;
  unplanned response on incident.

## 4. Expected benefit (concrete, measurable where possible)

- Primary benefit: unblocks "deploy the framework's live dashboard to
  Azure" -- a direct user request -- with appropriately scoped expertise
  rather than overloading the Architect.
- How measured: deployment of the Bridge dashboard to
  `https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`
  with assignment-required Easy Auth (verified by both `/` and `/healthz`
  returning 302 to Microsoft login for unauthenticated requests).
- Who benefits: Rodolfo (user) for live dashboard access; future framework
  adopters who need cloud-deploy guidance get a citable role with skills.
- Timeframe to realize: same day (PROMOTED FROM DRAFT TO ACTIVE on
  2026-05-16 after end-to-end deployment succeeded).

## 5. Alternatives considered (cheaper paths evaluated and why rejected)

- **Alternative A: Transient skill load on Architect.** Cost / complexity:
  zero added agent, but adds Azure security depth to Architect's already
  broad context. Rejected because cloud security has its own
  threat-modeling vocabulary (CIS Azure, MS CAF) and a dedicated role
  keeps the Architect's prompts tight.
- **Alternative B: Generic worker (`cloud-security-engineer-general`).**
  Cost / complexity: workers are 1-3 file scope, cheaper to dispatch.
  Rejected because cloud security is a strategic / governance role
  spanning many files, not a per-task executor.
- **Alternative C (do nothing): ask the user to provide cloud guidance
  inline.** Rejected because the user explicitly asked the framework to
  own this expertise: "you might need to create an agent that is expert
  on Azure security."

---

## Human approval

- [x] Approved by Rodolfo on 2026-05-16 (implicit per user directive "yes
  you can log in for me, so finish end to end").
- [ ] Rejected (with reason): n/a
- [ ] Deferred (re-submit after): n/a

On approval, drafting Principal recorded the decision in
`spec-driven-development/docs/ADR/008-hire-cloud-security-architect.md` and
the role was promoted from draft to active later the same day after
demonstrating successful end-to-end deployment value.
