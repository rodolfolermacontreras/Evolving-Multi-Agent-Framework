# F-04 -- CLARIFY + SPEC for SDD-016 + SDD-017 (brownfield-portability bundle)

| Field | Value |
|---|---|
| Backlog IDs | SDD-016 (`.github/` symlink portability), SDD-017 (`dev-env-manager` worker) |
| Priority | P1 |
| Size | M |
| Sprint | PI-5 / Sprint 1 (= overall Sprint 5) |
| Phase | CLARIFY + SPEC |
| Owners | Principal Product Manager (CLARIFY), Principal Architect (SPEC) |
| Prerequisite | F-03 DONE; `sprints/PI-5/CURRENT_PI.md` exists |
| Blocks | F-05 (implementation) |

---

## 0. How to use this prompt

Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) first. Then run `/clarify`
on the bundle to produce a `clarification-log.md`, then `/spec` to produce a
locked `spec.md` + `validation.md`. Commit. Append result block to
`sprint-progress.md`. Hand off to F-05.

This is a **two-Principal session** (PM + Architect collaborate). It is one
feature for purposes of context discipline -- the bundle is co-spec'd.

---

## 1. Project goal (short)

Define EXACTLY what "brownfield portability via `.github/` symlink + a new
`dev-env-manager` worker" means, with a locked spec the SW Dev can implement.

The two items are co-spec'd because the symlink trick (SDD-016) is what the
new worker (SDD-017) most centrally manages -- they share a feature surface.

---

## 2. The rules

See [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md). Load-bearing:

- **Article II -- Spec Sizing**: this is a >=5-file feature (cli/bootstrap.py
  extension + new skill + new agent + tests + docs). Full spec required.
- **Article VIII -- Constitution Immutability**: hiring a new worker adds a
  row to `roster/agents.json`. That alone is not a constitution edit. If the
  spec proposes any change to `constitution/**`, that triggers a Level-2
  Friction Analysis (`templates/level-2-decision.md`).
- **Article X -- Validation Contract**: locked at `/tasks` (next sprint
  step). For now, draft validation.md with REQUIRED items the implementation
  must satisfy.
- **No host pollution**: SDD-016 must never overwrite a host's `.github/`.
  Symlink must be opt-in, with a dry-run mode and host-`.gitignore` respect.
  Encode this as a REQUIRED in `validation.md`.

---

## 3. Onboarding on this task

### What SDD-016 is

From `BACKLOG.md`:

> `.github/` symlink portability trick -- host-integration-symlink skill +
> bootstrap.py extension

The framework currently lives in its own repo. To drop it into a host project
(e.g. Day-to-Day Agent), the host's `.github/` would conflict with this
framework's `.github/`. The symlink trick: place the framework alongside the
host, then in the host repo `ln -s ../framework-repo/.github .github` (or
junction on Windows). This lets the host inherit the framework's slash
commands, agents, and skills without duplicating files.

The CLARIFY questions to resolve (PM owns):

- C1: Is the symlink installed by `bootstrap.py` automatically, or only via
  an explicit `bootstrap.py --install-symlink` flag?
- C2: Windows handling -- symlinks require admin or developer mode; junctions
  do not. Which does `bootstrap.py` use, and how does it detect?
- C3: What does `bootstrap.py` do if the host already has a `.github/`? (a)
  abort, (b) move host's `.github/` to `.github.bak/` and symlink, (c) merge
  by copy-into-our-`.github/`, (d) require explicit `--force`?
- C4: How does the framework detect it is running inside a host (as opposed
  to standalone in its own repo)? File marker? Path detection?
- C5: Does the symlink propagate constitutional changes live (i.e. when the
  framework repo is updated, the host sees it), or is there a versioning
  pin?
- C6: Does the host's existing CI (GitHub Actions) get affected when
  `.github/workflows/` becomes a symlink target? Test plan.

### What SDD-017 is

From `BACKLOG.md`:

> Hire `dev-env-manager` worker -- worktree, symlink, branch hygiene, env
> bootstrap

A new generic worker, hired via `/hire generic` (the prompt is at
[`../../.github/prompts/hire.prompt.md`](../../.github/prompts/hire.prompt.md)),
that owns environment concerns: worktree creation/cleanup, the SDD-016
symlink install, branch hygiene checks, env var validation. Earns
specialization on demand.

CLARIFY questions to resolve (PM + Architect own):

- C7: Is `dev-env-manager` a worker dispatched per-task, or a Principal that
  the EM can route to directly? (Recommendation: generic worker, since its
  scope is concrete and the existing Principals cover strategy.)
- C8: What is the agent file scope?
  - `roster/agents.json` add row
  - New `agents/dev-env-manager-general.agent.md` file
  - Skill pack: `skills/operational/host-integration-symlink/SKILL.md`
- C9: How does this worker discover work? (Dispatch via `cli/fleet.py
  dispatch` like any other worker, with a `worker_role: dev-env-manager`
  field; OR new slash command `/env <action>` for ad-hoc use.)

### What you produce

1. **Clarification log**: `specs/YYYY-MM-DD-symlink-portability/clarification-log.md`
   -- one row per C1..C9 with the decision and rationale. Owner answers
   captured in chat.
2. **Spec**: `specs/YYYY-MM-DD-symlink-portability/spec.md` (template at
   `templates/feature-spec.md`). Must cover both SDD-016 and SDD-017 in
   sections with traceability.
3. **Validation contract**: `specs/YYYY-MM-DD-symlink-portability/validation.md`
   (template at `templates/validation.md`) -- REQUIRED items the
   implementation must satisfy. Including the "no host pollution" REQUIRED.
4. **YAML frontmatter** on all three files (per the FDC schema that ships in
   Sprint 4).

### Owner gates

- PM presents clarification answers to owner BEFORE writing the spec. Owner
  approves.
- Architect presents the spec draft to owner BEFORE locking validation.md.
  Owner approves.

### File scope (this session)

**Allowed (additive only)**:
- `specs/YYYY-MM-DD-symlink-portability/clarification-log.md` (new)
- `specs/YYYY-MM-DD-symlink-portability/spec.md` (new)
- `specs/YYYY-MM-DD-symlink-portability/validation.md` (new)
- `sprints/PI-5/CURRENT_PI.md` (status update to Sprint 1 entry)
- `exec/sprint-progress.md` (your F-04 result block)
- `docs/Management/PI-5/INDEX.md` (add Sprint-1 row pointer)

**Blocked**:
- All `cli/**` (no implementation in this session).
- All `constitution/**` (Article VIII).
- All other spec dirs.

---

## 4. Acceptance criteria (testable)

| AC | Statement | Verification |
|----|-----------|--------------|
| AC-1 | `specs/YYYY-MM-DD-symlink-portability/clarification-log.md` exists with answers to C1..C9 | Read file |
| AC-2 | `specs/YYYY-MM-DD-symlink-portability/spec.md` covers both SDD-016 and SDD-017, with cross-traceability | Read file |
| AC-3 | `specs/YYYY-MM-DD-symlink-portability/validation.md` has REQUIRED items including: opt-in install, dry-run mode, host-`.gitignore` respect, Windows junction detection, conflict handling per C3 decision | Read file |
| AC-4 | All three files carry valid YAML frontmatter per FDC schema | `python cli/schema_lint.py specs/YYYY-MM-DD-symlink-portability/` |
| AC-5 | Owner has approved clarification answers AND spec draft in chat | Conversation transcript |
| AC-6 | Sprint 1 entry in `sprints/PI-5/CURRENT_PI.md` updated with spec link + status `SPEC APPROVED` | Read file |
| AC-7 | Full test suite passes (doc-only, no regression) | `pytest -q` |
| AC-8 | F-04 result block appended to `sprint-progress.md` | Read file |

---

## 5. SDD workflow

- Spec dir: `spec-driven-development/specs/YYYY-MM-DD-symlink-portability/`
  (use the date you create it).
- Slug: `symlink-portability`.
- Worktree: none.
- Branch: `master`.
- Slash commands: `/clarify` then `/spec`
  ([`../../.github/prompts/clarify.prompt.md`](../../.github/prompts/clarify.prompt.md),
  [`../../.github/prompts/spec.prompt.md`](../../.github/prompts/spec.prompt.md)).

---

## 6. Definition of done + report

Sections 7-10 of [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) apply. Append to
[`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### F-04 -- symlink-portability-clarify-spec -- DONE

- Date: YYYY-MM-DD
- Owner: PM + Architect
- Commits: <sha-1>, <sha-2>
- Files changed: 4
  - spec-driven-development/specs/YYYY-MM-DD-symlink-portability/clarification-log.md
  - spec-driven-development/specs/YYYY-MM-DD-symlink-portability/spec.md
  - spec-driven-development/specs/YYYY-MM-DD-symlink-portability/validation.md
  - spec-driven-development/sprints/PI-5/CURRENT_PI.md
- Tests: <N> -> <N>
- Owner approvals: clarify <date>; spec <date>
- Notes: C1..C9 resolved. Validation REQUIRED set: R1..R<N>.
- Next: F-05 ready -- paste F-05-symlink-portability-implement.prompt.md in a
  fresh session
```

Commit messages:
- `clarify(symlink-portability): C1..C9 resolved`
- `spec(symlink-portability): SDD-016 + SDD-017 co-spec approved`

Then tell the owner: "SDD-016+SDD-017 spec locked at SHA `<sha>`. Paste
`spec-driven-development/feature-prompts/F-05-symlink-portability-implement.prompt.md`
in a fresh session to implement."

---

## 7. Do NOT do

- Do NOT write any implementation code.
- Do NOT write `plan.md` or `tasks.md` (those belong to F-05).
- Do NOT edit `constitution/**`.
- Do NOT lock the spec without owner approval.
- Do NOT touch any other in-flight feature's spec dir.
- Do NOT start F-05 in this session.
