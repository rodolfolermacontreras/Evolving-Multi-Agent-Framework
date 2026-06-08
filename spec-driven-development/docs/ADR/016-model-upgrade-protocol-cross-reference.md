---
id: ADR-016
type: spec
status: accepted
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# ADR-016: Model Upgrade Protocol Cross-Reference

- Date: 2026-06-08
- Status: **accepted**
- Authors: Principal Architect + Principal Software Developer
- Related: `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/`
- Acceptance evidence: Rodolfo Lerma explicitly accepted ADR-016 on 2026-06-08 via Executive Manager owner decision: "accept ADR-016".

---

## Context

SDD-015 creates `docs/MODEL-UPGRADE-PROTOCOL.md` and a no-network comparison
harness for model-upgrade proposals. The protocol treats major model version
bumps, vendor swaps, model-family swaps, and role-critical model assignment
changes as Level-2 decisions that require the existing Friction Analysis brief.

`constitution/decision-policy.md` already defines Level 2 and its Friction Analysis
brief, but it does not name model upgrades as a specialization. Adding a short
cross-reference would make the model-upgrade protocol discoverable from the
constitution-level decision policy.

Because `decision-policy.md` is a constitution file, Article VIII requires ADR
acceptance or an explicit owner waiver before the edit lands.

---

## Decision

Accepted: add a short model-upgrade paragraph under the Level 2 section of
`constitution/decision-policy.md` that links to
`docs/MODEL-UPGRADE-PROTOCOL.md` and states that in-scope model upgrades remain
Level-2 decisions subject to the existing Friction Analysis requirements.

Owner acceptance was recorded on 2026-06-08. F-14 may now apply the minimal
`decision-policy.md` cross-reference required by SDD-015.

---

## Consequences

### Positive

- Model-upgrade governance becomes discoverable from the decision policy.
- The cross-reference preserves SDD-014 Friction Analysis rather than creating a
  parallel approval path.
- Future agents get a clear stop condition before changing model assignments.

### Negative

- Adds one more constitution-level reference that must stay current if the
  protocol file moves.
- Requires owner approval before SDD-015 can close DONE because V-9 is locked as
  REQUIRED.

---

## Alternatives Considered

- **Protocol doc only**: rejected because SDD-015 acceptance criteria require the
  decision policy to reference the protocol.
- **Amend principles.md instead**: rejected because the existing decision-policy
  Level-2 section is the right owner-approval surface.
- **New model-upgrade article**: rejected as too heavy for a specialized decision
  route that can reuse the existing Level-2 mechanism.