---
version: '1.1.0'
ratified: 2026-05-12
last_amended: 2026-06-03
---

# Decision Policy

All agents operate within three authority levels. The level determines who may approve
a decision and whether it can be executed autonomously or requires a pause.

---

## Level 0: Worker Decision

**Authority**: Any worker agent, autonomously
**Approval**: None required
**Documentation**: None (or task comment)

Decisions that are entirely local to the current task scope and reversible with a single
`git revert`. Examples:

- Extracting a helper function within the same module
- Renaming a variable or function within the task's file scope
- Reorganizing test functions within a single test file
- Choosing between two equivalent stdlib approaches
- Adding a docstring or inline comment
- Fixing an obvious typo

**Rule**: If it affects only the files listed in the task brief, it is Level 0.

---

## Level 1: Principal Decision

**Authority**: Principal Architect or Principal Software Developer
**Approval**: Relevant Principal must agree (logged in task or ADR)
**Documentation**: ADR entry in `spec-driven-development/docs/ADR/`

Decisions that cross module boundaries, establish patterns others will follow, or affect
the shape of the public API. Examples:

- Changing a route signature or response schema
- Moving a function from one module to another
- Choosing a new architectural pattern (e.g., adding a registry, changing data flow)
- Deciding between two implementation approaches with different trade-offs
- Adding a new column to an existing database table (no migration required)
- Creating a new module
- Changing how shared state is assembled

**Rule**: If it affects files outside the task brief, or sets a precedent, it is Level 1.

---

## Level 2: Human Decision

**Authority**: Rodolfo (human owner)
**Approval**: Explicit human approval required before implementation begins
**Documentation**: Level-2 decision brief (see template below) submitted FIRST; on approval, an ADR is drafted that links back to the brief; a note is added to the relevant spec.

Decisions that are irreversible, high-risk, privacy-sensitive, or that affect production.
Implementation must STOP until approval is received. Examples:

- Adding a new pip dependency (any package not already in the host project's requirements)
- Schema migration (dropping/renaming columns, changing table structure)
- Changing authentication or authorization configuration
- Merging integration branch into the production branch
- Any operation on the production branch
- Deleting or archiving historical data
- Changing how tokens or credentials are stored or transmitted
- Introducing a new external API integration
- Changing privacy-sensitive behavior (what data is logged, what is sent to LLM)

**Rule**: If it cannot be cleanly reverted, affects production, or involves credentials/privacy, it is Level 2.

### Required: Friction Analysis brief

Every Level 2 submission MUST use the brief template at
`spec-driven-development/templates/level-2-decision.md` and fill in all
five sections: money cost (one-time + recurring), complexity cost
(added moving parts; new dependencies), maintenance burden (who maintains;
cadence of upkeep), expected benefit (concrete, measurable where possible),
and alternatives considered (cheaper paths evaluated and why rejected).
The brief is the input to the human approval gate; the ADR drafted on
approval links back to the brief as evidence. A worked example for
ADR-0008 (Cloud-Security Architect hire) lives at
`spec-driven-development/templates/level-2-decision-EXAMPLE.md`.

Model-upgrade proposals covered by `spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md`
are a specialized Level 2 path. They MUST still use the Friction Analysis brief
above before any in-scope model assignment change lands.

Level 0 and Level 1 decisions are not required to use this template.

---

## Escalation Path

```
Worker blocked or uncertain
  -> ask Principal SW Dev
      -> Principal SW Dev cannot resolve alone
          -> ask Principal Architect (architecture) or Principal PM (scope)
              -> cross-principal disagreement or Level 2 trigger
                  -> STOP and ask Human
```

Stop conditions that always trigger immediate escalation to Human:
1. Current branch is `master`
2. No linked spec for a non-trivial change
3. A gate fails twice consecutively
4. Any Level 2 example above is encountered

---

## ADR Format

ADRs live in `spec-driven-development/docs/ADR/NNN-title.md`.
Template: `spec-driven-development/docs/ADR/TEMPLATE.md`

An ADR documents: context, decision, rationale, consequences, status.
ADRs are never deleted -- superseded ADRs are marked `SUPERSEDED by ADR-NNN`.
