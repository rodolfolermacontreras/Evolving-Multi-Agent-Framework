---
version: '1.2.0'
ratified: 2026-05-25
last_amended: 2026-06-26
owner: principal-executive-manager
amendable_by: human-only
binding_source: constitution/principles.md
---

# RULES

The binding, non-negotiable constraints for every agent on every project run
through the Evolving Multi-Agent Framework. Short by design. Each rule names its
authoritative source so disputes resolve against a single canonical document.

**Hierarchy of authority**, top to bottom:

1. `constitution/principles.md` (Articles I-XII, semver'd, ADR to amend)
2. `constitution/decision-policy.md` (Level 0/1/2 authority)
3. `constitution/quality-policy.md` (test baseline, two-stage review, DoD)
4. This file (`RULES.md`) -- the agent-facing distillation
5. `.github/copilot-instructions.md` (session-start authority)
6. Per-skill `SKILL.md` files (tactical)

If this file and the constitution disagree, the constitution wins. File a PR to
this file via `/constitution` (Level 1, ADR required) to reconcile.

---

## The 13 Standing Rules

### Rule 1 -- No emojis
No emojis in code, commits, documentation, agent prompts, skill files, or
artifacts. Plain ASCII. This applies to professional output; private chat
freeform is fine.
**Source:** copilot-instructions.md conventions.

### Rule 2 -- Test as you go (TDD gate)
Any code that will be used in production is covered by an automated test before
it is considered DONE. Validation criteria are written DURING `/spec`, locked at
`/tasks`, and verified at `/qa`. Tests come before implementation, not after.
**Source:** Article X (ADR-0005). Enforced by `.github/skills/engineering/tdd-gate/`.

### Rule 3 -- Track and delete scaffolding
Throwaway exploration scripts and debugging files are tracked when created
(`scratch/` or noted in the sprint detail doc) and deleted before the sprint
closes. The repo does not accumulate orphan files.
**Source:** This file.

### Rule 4 -- Full traceability
Every decision is an artifact (ADR, spec, plan, retro). Every fleet dispatch
is a row in `ledger/fleet.db`. The answer to "why was this built this way?"
is always a file path. The answer to "who did this and when?" is always a
ledger row.
**Source:** Article VII.

### Rule 5 -- Document as you go
Documentation is concurrent with the work, not an afterthought. Prefer
amending an existing doc over creating a new one. New docs require a clear
home in the repo structure -- never floating Markdown in random folders.
**Source:** This file + Article VII.

### Rule 6 -- Conventional commits
Format: `type: short description`. Types: `feat | fix | docs | chore | refactor |
test | spec | plan | qa | retro | design`. Keep commits small and reviewed.
Subject line under 72 chars.
**Source:** copilot-instructions.md conventions.

### Rule 7 -- Worktrees for parallel work
Every active sprint runs in its own git worktree named `wt-pi{N}-s{M}-{slug}`.
Branch matches worktree name. `master` stays clean. Worktrees are torn down
when the sprint is DONE and merged.
**Source:** `.github/instructions/fleet-workers.instructions.md`.

### Rule 8 -- File-scope limits (workers 1-3 files)
A worker dispatched on a single task modifies 1-3 files maximum. If the task
needs more, decompose it further or escalate to the SW Dev for re-tasking.
Reviewers review; they do not implement.
**Source:** Article IV.

### Rule 9 -- Earned specialization
Workers start generic. A specialist is hired only when prior dispatches prove
recurring demand for the specialization. Promotion is Level-2, requires
evidence (count of dispatches, tests written, pattern adherence), and follows
ADR-0007 `/hire specialist`.
**Source:** Article V (ADR-0003) + ADR-0007.

### Rule 10 -- Two-stage review
Every implementation passes spec-compliance review FIRST (different agent),
then code-quality review. Quality review never starts before compliance
passes. Order is fixed.
**Source:** Article III.

### Rule 11 -- Context discipline
Each level of the org holds exactly the context it needs and no more.
- Executive Manager: big picture, never absorbs deep sprint detail.
- Principals: their domain, never the other Principals' deep detail.
- Workers: their 1-3 files and the embedded spec, never the full repo.
The Executive Manager points to detail docs; it does not reproduce them.
**Source:** Articles II + IV.

### Rule 12 -- HITL gates (see Section 2 below)
Pause for explicit human approval before any irreversible or high-stakes
action.
**Source:** `constitution/decision-policy.md` Level-2 + Section 2 below.

### Rule 13 -- No untracked sprint work
No work on a sprint may begin without a corresponding
`docs/Management/PI-#/Sprint-#-{title}/` folder and a tracker entry in
`HIGH_LEVEL_DEV_TRACKER.md`. Untracked work is not permitted. The Executive
Manager owns the tracker and PI INDEX files. This rule applies prospectively
from ratification; existing in-flight sprints are grandfathered via the
migration in PI-3/S5.
**Source:** ADR-0011 (Three-Tier Navigation Layer).

---

## Section 2 -- HITL Gates (Human-in-the-Loop)

Stop and request explicit human approval before doing any of the following.
The agent that hits a HITL gate writes the prompt for the human and waits.

| # | Action | Reason |
|---|--------|--------|
| 1 | Provisioning any cloud resource | Money, blast radius, credentials |
| 2 | Any irreversible action (force-push, drop table, delete branch with history) | Recoverable only by backup |
| 3 | Scope change to an active sprint or PI | Re-plan needed |
| 4 | Cross-sprint merge conflict resolution to `master` | Principals collaborate, human approves merge |
| 5 | New dependency added to `tech-stack.md` | Portability claim at stake |
| 6 | Schema migration on `ledger/fleet.db` (or any persisted DB) | Data loss risk |
| 7 | Credential changes (Entra ID, OIDC, GitHub secrets) | Security blast radius |
| 8 | Any new ADR with `status: binding` | Architectural commitment |
| 9 | Any `/hire` command (generic or specialist) | Org chart change |
| 10 | **Pushing to `origin/master`** | Public artifact; human owns publication |
| 11 | Anything else `decision-policy.md` flags as Level-2 | Authoritative tiebreaker |

Default mode at every HITL gate: the agent recommends ONE option with a
one-line reason and waits for OK/veto. Menus only when the agent genuinely
cannot recommend (LESSON-005, `em-communication-discipline` skill).

---

## Section 3 -- Conflict Resolution

When a worker hits a cross-sprint dependency or merge conflict it cannot
resolve in its own worktree:

1. Worker escalates to the Principal Software Developer.
2. SW Dev pulls in the other affected Principal(s) (Architect for design,
   PM for scope, UI Designer for visual layer).
3. Principals decide together; if they cannot agree, escalate to Executive
   Manager, who synthesizes options and surfaces to human (Level-2 if
   irreversible).
4. Resolution merges to `master` only after human approval per HITL gate #4.
5. Affected worktrees pull from `master` and resume.
6. Resolution is logged as a ledger `decisions` row and noted in both
   sprints' detail docs.

---

## Section 4 -- What Counts As DONE

A task is DONE when ALL of the following are true:

- [ ] Validation contract from `spec/validation.md` -- every box checked OR
      explicitly marked `[NO-TEST-NEEDED]` with reason.
- [ ] All new code covered by automated tests (Rule 2).
- [ ] Two-stage review passed: COMPLIANT + APPROVED (Rule 10).
- [ ] Dispatch outcome marked in `ledger/fleet.db` (Rule 4).
- [ ] Sprint `SPEC.md` in `docs/Management/PI-#/Sprint-#-{title}/` updated with
      current task status and any notes from this dispatch/REVIEW cycle.
- [ ] Worktree merged to `master` (human-approved per HITL #4 if cross-cutting).
- [ ] Scaffolding deleted (Rule 3).

A feature is DONE when all its tasks are DONE and the feature's
`specs/YYYY-MM-DD-{slug}/RETRO.md` exists.

A sprint is DONE when all its features are DONE and:
- [ ] The sprint's `SPEC.md` is finalized in `docs/Management/PI-#/Sprint-#-{title}/`.
- [ ] `AGENT_NOTES.md` in the same folder is populated with on-the-ground findings.
- [ ] The PI `INDEX.md` (`docs/Management/PI-#/INDEX.md`) is updated with what was
      done, key decisions, and lessons from this sprint.
- [ ] `HIGH_LEVEL_DEV_TRACKER.md` sprint row updated to reflect DONE status.

A PI is DONE when all its sprints are DONE, `roadmap.md` is updated,
`sprints/PI-N/lessons.md` is curated via `/evolve`, and the PI `INDEX.md`
is finalized.

**Ceremony bindings (ADR-0011):**
- `SPEC.md` updated each dispatch/REVIEW cycle (task-level).
- PI `INDEX.md` updated at sprint DONE and at `/replan` (sprint-level).
- `HIGH_LEVEL_DEV_TRACKER.md` updated every session (project-level).

---

## Section 5 -- Amendment Process

This file is amendable only by the human (the executive sponsor).
Process to amend:

1. Propose change via PR or `/constitution` command.
2. If the change affects an Article (I-XII) in `principles.md`, amend the
   constitution FIRST and let `RULES.md` follow downstream.
3. Bump the `version:` field in this file's frontmatter (semver: MAJOR for
   removing a rule, MINOR for adding, PATCH for clarification).
4. Update `last_amended:` to today's date.
5. Run the `constitution-sync` propagation scan to find dependent files.
6. Commit as `docs(rules): amend Rule N -- <one-line rationale>`.

---

*This file is the agent-facing rulebook. The constitution is the binding
source. Read both.*
