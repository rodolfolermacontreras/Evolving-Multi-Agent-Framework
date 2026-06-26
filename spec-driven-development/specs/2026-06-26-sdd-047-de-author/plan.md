---
id: SDD-20260626DEAUTHOR-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# PLAN: SDD-047 -- De-author the framework

- CLARIFY: [`clarify.md`](clarify.md) | Spec: [`spec.md`](spec.md) | Tasks: [`tasks.md`](tasks.md)

## Sequencing rationale

Shared surfaces (`cli/origin_lint.py`, `cli/schema_lint.py`,
`project.config.json`, `INSTRUCTIONS.md`, README, the skill library,
`constitution/**`) force a SERIAL plan -- no two workers touch the same file.
The serial CLARIFY/SPEC gate is the only conflict mechanism (there is no
file-overlap detector; D-3 makes that honest).

## Phases

### Phase 1 -- A-2 config surface (foundation)

1. Create `project.config.json` (`owner`, `team`, `repo_url`) + a stdlib reader
   helper. Setup (A-4) writes `owner` here.
2. Replace personal-name references in `.github/agents/**`, `INSTRUCTIONS.md`,
   and README-as-instruction with a config reference / "the host project's
   owner." Neutralize PM agent "single user: Rodolfo Lerma" line.
3. Set skill `author:` frontmatter -> `emf-framework` across all `SKILL.md`.

### Phase 2 -- A-6 lint reads config (lock-in for A-2)

4. Extend `cli/origin_lint.py` to load a personal-name denylist from
   `project.config.json` (TDD: a test proves a re-added name fails). Promote the
   stricter origin tokens (`engine.py`, origin project names) into the active
   denylist now that the generic files are clean.

### Phase 3 -- A-3 origin scrub

5. Replace origin examples in the flagged agents/skills with stack-neutral ones.
   Relocate the `engine.py` lazy-singleton table from
   `principal-architect.agent.md` into the host archetype.
6. Wrap the README / `copilot-instructions.md` origin story in a labeled
   `<!-- example: history -->` block so A-6 exempts it as history.

### Phase 4 -- D-1 wire-or-delete skills

7. Wire `tdd-gate` into the SW Dev review flow (agent + prompt reference).
8. For each remaining dead skill, wire or delete per `validation-D1.md`; update
   `roster/skills.json` for any removal.
9. Add a `schema_lint` rule: shipped skill referenced by zero agents/prompts ->
   fail (TDD: test for both a referenced and an orphan skill).

### Phase 5 -- D-3 rename

10. Rename "parallel dispatch with conflict detection" -> "serial CLARIFY/SPEC
    gate" in `GENERALIZATION_SDD.md`. File SDD-049 (honest backlog item) for a
    real file-overlap detector.

### Phase 6 -- Level-2 constitution (OWNER-GATED -- blocked this session)

11. Under approved ADR-022 + version bump: de-author `constitution/mission.md`,
    `constitution/decision-policy.md`, and rename the `constitution/roadmap.md`
    conflict-detection line. DO NOT land without recorded owner approval.

### Phase 7 -- QA + close (LOCAL ONLY this session)

12. Run full pytest (>= 518/2), schema_lint (0), `doctor` (green incl. A-6 0
    hits in generic files), Article X lock guard. Log Sprint 16 dispatches in the
    ledger (B-1 dogfood). Owner pre-push approval before any push.

## Risk / mitigation

- Over-scrubbing (A-3): replace, never bare-delete; reviewer confirms concept
  retained.
- A-6 false positives after denylist tightening: test the labeled-example escape.
- Level-2 blocker: Phases 1-5 proceed; Phase 6 + final close wait for owner.
