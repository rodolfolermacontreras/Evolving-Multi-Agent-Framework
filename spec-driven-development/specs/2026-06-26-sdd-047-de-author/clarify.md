---
id: SDD-20260626DEAUTHOR-clarify
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# CLARIFY: SDD-047 -- De-author the framework (A-2 / A-3 / D-1 / D-3)

- Epic ID: SDD-047 (PI-7 Sprint 16 / PI-7 Sprint 3)
- Spec source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) Parts A (A-2, A-3) + D (D-1, D-3)
- Lead: Sprint Executive Manager (routes); PM + Architect own this CLARIFY/SPEC.

---

## Per-item SDD-IDs

CLARIFY assigns one ID per audit item, each with its own validation contract
(mirrors the SDD-046 B-1/B-2/B-4 pattern). The audit item label IS the per-item
ID under the SDD-047 umbrella:

| Per-item ID | Audit item | Validation contract |
|-------------|-----------|---------------------|
| A-2 | Owner/identity becomes a config value | [`validation-A2.md`](validation-A2.md) |
| A-3 | Scrub origin-project leakage from generic files | [`validation-A3.md`](validation-A3.md) |
| D-1 | Wire-or-delete the 10 dead skills | [`validation-D1.md`](validation-D1.md) |
| D-3 | Rename "conflict detection" -> "serial CLARIFY/SPEC gate" | [`validation-D3.md`](validation-D3.md) |

---

## Stale-check against the live repo (2026-06-26, HEAD 0becb36)

The audit was written 2026-06-24. Sprints 14/15 shipped A-1, A-4, A-5, A-6, B-1,
B-2, B-4 already. Verified live state before CLARIFY:

- A-6 origin-lint (`cli/origin_lint.py`) EXISTS. Its shipped `DEFAULT_DENYLIST`
  catches only home-dir paths; `RECOMMENDED_DENYLIST` (with `engine.py`, project
  roots) is opt-in. Personal author names are NOT yet in either list. So today
  `doctor`'s "origin tokens absent" passes only because the default list is lax.
- Personal-name hits remain in generic files: `INSTRUCTIONS.md` (line 5),
  `.github/copilot-instructions.md` (owner + origin story), the PM agent
  (`principal-product-manager.agent.md` lines 19/29/33/35), ~15 skill `author:`
  frontmatter values, `weekly-status-report` + `pi-planning` skill bodies.
- Constitution name/origin hits remain: `constitution/mission.md` (line 17,
  owner name), `constitution/decision-policy.md` (line 57, "Rodolfo (human
  owner)").
- D-3 over-claim lives in `constitution/roadmap.md` (line 78) and
  `GENERALIZATION_SDD.md` (lines 772, 900). Most other "conflict detection" hits
  are HISTORICAL specs (out of scope -- the record) or the kickoff/audit source.
- No `project.config.json` exists yet.

No audit item is stale enough to drop. One scope correction is recorded (DE-1
below): A-2 and D-3 reach into `constitution/**`, which is Level-2.

---

## Resolutions

### Q-A -- A-2 config shape and how A-6 reads it -> RESOLVED (default)

Adopt a single root `project.config.json` holding `owner`, `team`, `repo_url`.
The A-4 setup prompt fills `owner`; the A-6 lint loads a personal-name denylist
derived from config so a re-added personal name fails. Chosen over
`constitution/owner.md` to keep the change OUT of `constitution/**` (avoids an
extra Level-2 surface). Stdlib-only JSON reader (Article V).

### Q-B -- A-3 scrub-vs-replace and where origin examples go -> RESOLVED (default)

Replace in place with stack-neutral examples; do NOT just delete. Relocate
genuinely host-specific examples (the `engine.py` lazy-singleton table in
`principal-architect.agent.md`) into the host-project archetype. Keep the README
/ `copilot-instructions.md` origin story as a clearly-labeled history block
(wrapped in an `<!-- example: ... -->` marker so A-6 exempts it), not as
instruction.

### Q-C -- D-1 per-skill wire-or-delete -> RESOLVED (default + per-skill calls)

Wire `tdd-gate` FIRST into the SW Dev review flow (B-2 made it a real check in
Sprint 15). For the other nine, the per-skill call is recorded in
[`validation-D1.md`](validation-D1.md). Add a `schema_lint` rule that flags any
shipped skill referenced by zero agents/prompts, locking the outcome in.

### Q-D -- D-3 rename scope -> RESOLVED (default)

Rename the over-claim in the GENERIC files only: `constitution/roadmap.md`
(Level-2 -- see DE-1) and `GENERALIZATION_SDD.md`. Historical specs keep their
wording (the record). No true file-overlap detector is built here; if wanted it
is filed as an honest backlog item (SDD-049, proposed).

### Q-E -- constitution wording (owner-gated) -> ESCALATED (Level-2)

A-2 and D-3 cannot fully close without editing `constitution/**`:

- A-2: `constitution/mission.md` (owner name), `constitution/decision-policy.md`
  ("Rodolfo (human owner)").
- D-3: `constitution/roadmap.md` (the "Conflict-detection workflow ... deferred"
  line).

Per `constitution/decision-policy.md` and the kickoff Hard Constraints, any
`constitution/**` wording change is **Level-2**: it needs an ADR + recorded
owner approval + a constitution version bump. This is surfaced as an ESCALATION
(below). The non-constitution surfaces (agents, skills, INSTRUCTIONS.md, README
-as-instruction, config, lint, D-1) are Level-0/1 and proceed without it.

---

## Deltas

- **DE-1 (scope sharpen).** The audit framed A-2/A-3/D-3 as generic-file work,
  but three target lines live under `constitution/**` (mission.md,
  decision-policy.md, roadmap.md). These are Level-2. This delta SHARPENS the
  contract by splitting each affected item into a Level-0/1 portion (proceeds)
  and a Level-2 portion (owner-gated via ADR). It does not loosen any acceptance
  criterion -- the constitution lines still must be clean for full close.

---

## ESCALATION

Severity: MEDIUM
Issue: A-2 and D-3 require Level-2 constitution edits (mission.md,
decision-policy.md, roadmap.md); the owner is unavailable to approve.
Impact: SDD-047 cannot be stamped DONE this session -- A-2 / A-3 / D-3 acceptance
each require the constitution lines to be de-authored, and that is owner-gated.
Options:
  1. Land the Level-0/1 portions now (config, agents, skills, INSTRUCTIONS,
     README, lint, D-1), draft the ADR, and leave the three constitution lines +
     final close for owner approval -- LOCAL design + partial-implement, no push,
     SDD-047 stays OPEN. (Trade-off: epic spans two sessions; no false close.)
  2. Wait for owner approval before any implementation -- design only this
     session. (Trade-off: slower; nothing lands.)
Recommendation: Option 1. The Level-0/1 work is the bulk and is safe; the
constitution touch is one ADR + three line edits the owner ratifies next session.
Decision needed by: next owner-available session (before SDD-047 close + push).
