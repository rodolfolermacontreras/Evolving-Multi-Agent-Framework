---
id: SDD-20260626DEAUTHOR-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# SPEC: SDD-047 -- De-author the framework

- Epic ID: SDD-047 (PI-7 Sprint 16)
- CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Spec source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) Parts A + D
- Per-item validation: [`validation-A2.md`](validation-A2.md), [`validation-A3.md`](validation-A3.md), [`validation-D1.md`](validation-D1.md), [`validation-D3.md`](validation-D3.md)

---

## Goal

A teammate who clones the framework cannot tell who wrote it or which project it
grew out of. Owner/identity is a config value, the generic files teach with
stack-neutral examples, every shipped skill is wired or gone, and no doc claims a
"conflict detection" the code does not perform. At close the A-6 origin/identity
lint returns 0 hits in the generic files.

## Non-goals

- Rewriting history. Historical `specs/`, `sprints/`, retros, and ADRs keep the
  author's name and origin references -- that is the record.
- SDD-048 (C-1/C-2/C-3/D-2 maintainability) -- that is Sprint 17.
- Azure decommission (SDD-035) -- out-of-band.
- Building a real file-overlap conflict detector (D-3 is a rename only; a real
  detector, if wanted, is filed as SDD-049).
- Closing PI-7 -- a separate owner-approved decision after Sprint 17.

## Requirements

### A-2 -- owner/identity as config

- R-A2-1: One config surface `project.config.json` at repo root holds `owner`,
  `team`, `repo_url`. (Acceptance: file exists, valid JSON, stdlib-readable.)
- R-A2-2: No GENERIC framework file (`.github/agents/**`, `.github/skills/**`,
  `INSTRUCTIONS.md`, README-as-instruction) carries a hardcoded personal name;
  references resolve to config or to "the host project's owner."
- R-A2-3: The PM agent traces value to "the host project's owner," not a person.
- R-A2-4: Skill `author:` frontmatter is a neutral value (`emf-framework`).
- R-A2-5: The A-6 lint reads the config-derived personal-name denylist so a
  re-added personal name in a generic file fails the lint.
- R-A2-6 (Level-2, owner-gated): `constitution/mission.md` and
  `constitution/decision-policy.md` owner-name lines are de-authored under an
  approved ADR + version bump.

### A-3 -- scrub origin leakage

- R-A3-1: The flagged generic files carry no origin tokens
  (`engine.py`/`FastAPI`/`HTMX`/`Day-to-Day`/`World State`/`Outlander`/`743`)
  outside a labeled `<!-- example: ... -->` / history block.
- R-A3-2: `principal-architect.agent.md` design examples are stack-neutral;
  the `engine.py` lazy-singleton table relocates to the host archetype.
- R-A3-3: The README / `copilot-instructions.md` origin story is present and
  clearly marked as history (labeled block), not instruction.
- R-A3-4: Examples are replaced/relocated, not just deleted (no concept loss).
- R-A3-5 (Level-2, owner-gated): the 3 origin-bearing `constitution/**` files are
  de-authored under the same ADR as R-A2-6.

### D-1 -- wire-or-delete dead skills

- R-D1-1: `tdd-gate` is referenced from the SW Dev review flow.
- R-D1-2: Each of the other 9 dead skills is either referenced by >=1
  agent/prompt or removed (decision recorded in `validation-D1.md`).
- R-D1-3: A `schema_lint` rule flags any shipped skill referenced by zero
  agents/prompts (lock-in).

### D-3 -- rename the over-claim

- R-D3-1: `GENERALIZATION_SDD.md` no longer claims "conflict detection" the code
  does not perform; wording matches the serial CLARIFY/SPEC gate.
- R-D3-2 (Level-2, owner-gated): `constitution/roadmap.md` line is renamed under
  the same ADR.
- R-D3-3: If a true file-overlap detector is wanted, it is filed as an honest
  backlog item (SDD-049).

## Traceability

| Req | Audit Acceptance | Validation item |
|-----|------------------|-----------------|
| R-A2-1..5 | A-2 Acceptance (config; no hardcoded name; PM trace; grep 0) | validation-A2 R-1..R-5 |
| R-A2-6 | A-2 Acceptance (grep 0 incl. constitution) | validation-A2 R-6 (Level-2) |
| R-A3-1..4 | A-3 Acceptance (no origin tokens; stack-neutral; history label) | validation-A3 R-1..R-4 |
| R-A3-5 | A-3 Acceptance (22 files clean) | validation-A3 R-5 (Level-2) |
| R-D1-1..3 | D-1 Acceptance (every skill referenced or removed) | validation-D1 R-1..R-3 |
| R-D3-1..3 | D-3 Acceptance (no over-claim) | validation-D3 R-1..R-3 |

## Constraints

- Stdlib-only (Article V); Article X locked render functions immutable.
- Constitution edits (R-A2-6, R-A3-5, R-D3-2) are Level-2: ADR
  ([`../../docs/ADR/022-de-author-constitution.md`](../../docs/ADR/022-de-author-constitution.md), drafted)
  + recorded owner approval + version bump required before they land.
- Append-only ledger; explicit-path git staging; no push without owner approval.

## Definition of Done

All per-item REQUIRED items in the four validation contracts checked with
real-run evidence; A-6 lint 0 hits in generic files; the unreferenced-skill
schema_lint rule present; tests >= 518/2-skipped; schema lint clean; Article X
lock held; ledger shows real Sprint 16 rows; the three Level-2 constitution lines
landed under an approved ADR; owner pre-push approval recorded.
