# F-05 -- SDD-016 + SDD-017 PLAN + TASKS + IMPLEMENT + QA + RETRO + close Sprint 5

| Field | Value |
|---|---|
| Backlog IDs | SDD-016, SDD-017 |
| Priority | P1 |
| Size | M-L |
| Sprint | PI-5 / Sprint 1 (= overall Sprint 5) |
| Phase | PLAN + TASKS + IMPLEMENT + REVIEW + RETRO + SPRINT CLOSE |
| Owner | Principal Software Developer (lead); workers via dispatch |
| Prerequisite | F-04 DONE (spec + validation locked) |
| Blocks | PI-5 Sprint 2 |

---

## 0. How to use this prompt

Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) first. Then `/plan` ->
`/tasks` -> `/implement` -> `/qa` -> `/retro` on the symlink-portability
spec from F-04. Close Sprint 5 (= PI-5 Sprint 1). Append result blocks to
`sprint-progress.md`.

This is the **implementation feature** of Sprint 5. May dispatch worker
sessions via `cli/fleet.py dispatch` if task count warrants.

---

## 1. Project goal (short)

Ship the brownfield-portability bundle: `bootstrap.py` extension to install
the framework as a `.github/` symlink in a host repo, a new
`host-integration-symlink` skill, and a new `dev-env-manager` worker agent
(rostered, with its skill pack). All REQUIRED validation items pass. The
framework can now be dropped into Day-to-Day Agent (or any host) without
overwriting the host's `.github/`.

---

## 2. The rules

See [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md). Load-bearing:

- **Stdlib only** for `bootstrap.py`. Use `os.symlink`, `pathlib`,
  `subprocess` for git interactions.
- **Windows + Linux + macOS**: the symlink path must detect platform and use
  `mklink /J` (junction) on Windows when symlink permission unavailable. Per
  C2 decision in F-04 clarification-log.
- **No host pollution**: opt-in install only (`bootstrap.py --install-symlink
  --target <host-repo-path>`). Dry-run by default. Conflict handling per C3
  decision in F-04.
- **Tests-first within each task.** Add failing test, then code, then green
  test.
- **Article X**: validation.md from F-04 is LOCKED. R1..R<N> must all check.
- **No constitution edits.** New agent + new skill = roster + skills dir, not
  `constitution/`.

---

## 3. Onboarding on this task

### What you produce

Per the F-04 spec (re-stated for grounding -- the locked spec is
authoritative):

1. **Plan**: `specs/YYYY-MM-DD-symlink-portability/plan.md` -- phased
   implementation plan (Architect + SW Dev co-authored; this session may
   draft).
2. **Tasks**: `specs/YYYY-MM-DD-symlink-portability/tasks.md` -- sequenced,
   file-scoped task list with traceability matrix to R1..R<N>.
3. **Implementation**:
   - `cli/bootstrap.py` -- extended with `install_symlink()` function +
     argparse subcommand or flag. Cross-platform (symlink/junction).
   - `cli/test_bootstrap.py` (new or extended) -- tests for dry-run,
     install, conflict handling, Windows junction detection (use
     `unittest.mock.patch` for platform branches if running on a single
     platform).
   - `.github/skills/operational/host-integration-symlink/SKILL.md` -- new
     skill the `dev-env-manager` worker loads when handling symlink
     installs.
   - `.github/agents/dev-env-manager-general.agent.md` -- new generic worker
     agent file (use existing `developer-general.agent.md` as template).
   - `roster/agents.json` -- add row for `dev-env-manager-general` with
     `status: generic`, `provenance: "Hired via /hire generic at PI-5 S1 to
     own SDD-016 + SDD-017 (brownfield portability). Approved YYYY-MM-DD."`
   - `roster/skills.json` -- add row for `host-integration-symlink` skill.
4. **Documentation**:
   - `docs/HOST-INTEGRATION.md` (new) -- how a host repo adopts the framework
     via the symlink trick. End-to-end walkthrough including Day-to-Day Agent
     as a worked example.
5. **Test for "no host pollution"**: integration-style test that creates a
   temp host dir with an existing `.github/`, runs `bootstrap.py
   --install-symlink --target <tmp>` in dry-run, confirms abort/conflict
   handling per C3 decision; then with conflict-resolution flag, confirms
   correct behaviour.
6. **Retro**: write the Sprint 5 retro into `sprints/PI-5/CURRENT_PI.md`
   under Sprint 1's section. Capture: what worked, what to improve, what to
   carry to PI-5 Sprint 2.
7. **Sprint close + PI-5 Sprint 2 staging**: mark Sprint 1 DONE. Identify
   PI-5 Sprint 2 from F-03's allocation. If PI-5 Sprint 2 is ready to start
   (no upstream blockers), notify the EM to author
   `SPRINT-06-KICKOFF.prompt.md`. If not ready, capture the blocker.

### Optional dispatch path

If `tasks.md` has more than 6 tasks, decompose via `cli/fleet.py dispatch`
into `dispatches/PI-5/NNNNNN.md` packets. Each worker session owns one task.
Integrate results back into this F-05 block.

### File scope (cumulative)

**Allowed (additive unless noted)**:
- `cli/bootstrap.py` (extension; preserve existing behaviour)
- `cli/test_bootstrap.py` (new tests; do not delete existing)
- `.github/skills/operational/host-integration-symlink/SKILL.md` (new)
- `.github/agents/dev-env-manager-general.agent.md` (new)
- `roster/agents.json` (add row)
- `roster/skills.json` (add row)
- `docs/HOST-INTEGRATION.md` (new)
- `specs/YYYY-MM-DD-symlink-portability/plan.md` (new)
- `specs/YYYY-MM-DD-symlink-portability/tasks.md` (new)
- `sprints/PI-5/CURRENT_PI.md` (Sprint 1 status + retro)
- `backlog/BACKLOG.md` (SDD-016 + SDD-017 status to DONE with SHA)
- `exec/sprint-progress.md` (F-05 + Sprint 5 close blocks)
- `exec/state.md`, `exec/state.html`, `exec/work-index.md` (regenerated)
- `docs/Management/PI-5/INDEX.md` (regenerated)

**Blocked**:
- `cli/state_builder.py` (any non-additive change; the locked surface from
  PI-4 still applies)
- `constitution/**` (Article VIII)
- `specs/YYYY-MM-DD-symlink-portability/spec.md`, `validation.md`,
  `clarification-log.md` (locked at F-04)
- Any other in-flight feature's spec dir

---

## 4. Acceptance criteria (testable)

| AC | Statement | Verification |
|----|-----------|--------------|
| AC-1 | All REQUIRED items (R1..R<N>) in `validation.md` check | Read file; cross-check tests |
| AC-2 | `bootstrap.py --install-symlink --target <tmp> --dry-run` lists the planned action without writing | `cli/test_bootstrap.py::test_install_symlink_dry_run` |
| AC-3 | `bootstrap.py --install-symlink --target <tmp>` installs symlink (or junction on Windows) when no conflict | `cli/test_bootstrap.py::test_install_symlink_clean` |
| AC-4 | `bootstrap.py --install-symlink --target <tmp>` handles existing `.github/` per C3 decision (abort / backup / merge / force, whichever was chosen) | `cli/test_bootstrap.py::test_install_symlink_conflict_handling` |
| AC-5 | Platform detection: junction on Windows when symlink permission unavailable | Mocked test in `cli/test_bootstrap.py` |
| AC-6 | New agent file present + rostered; `roster/agents.json` lints clean | `python cli/schema_lint.py roster/agents.json` |
| AC-7 | New skill file present + rostered; `roster/skills.json` lints clean | `python cli/schema_lint.py roster/skills.json` |
| AC-8 | `docs/HOST-INTEGRATION.md` exists with worked example | Read file |
| AC-9 | Full test suite passes (>= baseline + new tests; target +5 minimum) | `pytest -q` |
| AC-10 | `sprints/PI-5/CURRENT_PI.md` Sprint 1 marked DONE with date, SHAs, retro paragraph | Read file |
| AC-11 | `BACKLOG.md` SDD-016 + SDD-017 marked DONE with SHAs | Read file |
| AC-12 | `exec/state.md` regenerated; SDD-016 + SDD-017 show DONE; PI-5 shows ACTIVE with Sprint 1 closed | Read file after regenerate |
| AC-13 | Sprint 5 close block appended; next-sprint hand-off noted | Read `sprint-progress.md` |

---

## 5. SDD workflow

- Spec dir: `spec-driven-development/specs/YYYY-MM-DD-symlink-portability/`
- Slug: `symlink-portability`
- Worktree: none
- Branch: `master`
- Commands, in order:
  1. `/plan` ([`../../.github/prompts/plan.prompt.md`](../../.github/prompts/plan.prompt.md))
  2. `/tasks` ([`../../.github/prompts/tasks.prompt.md`](../../.github/prompts/tasks.prompt.md))
  3. `/implement` per task ([`../../.github/prompts/implement.prompt.md`](../../.github/prompts/implement.prompt.md))
  4. `/qa` ([`../../.github/prompts/qa.prompt.md`](../../.github/prompts/qa.prompt.md))
  5. `/retro` ([`../../.github/prompts/retro.prompt.md`](../../.github/prompts/retro.prompt.md))

---

## 6. Definition of done + report

Sections 7-10 of [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) apply. Append
two blocks to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### F-05 -- symlink-portability-implement -- DONE

- Date: YYYY-MM-DD
- Owner: Principal Software Developer (+ workers: <list>)
- Commits: <list>
- Files changed: <count>
  - cli/bootstrap.py (extension)
  - cli/test_bootstrap.py
  - .github/skills/operational/host-integration-symlink/SKILL.md
  - .github/agents/dev-env-manager-general.agent.md
  - roster/agents.json
  - roster/skills.json
  - docs/HOST-INTEGRATION.md
  - specs/YYYY-MM-DD-symlink-portability/plan.md
  - specs/YYYY-MM-DD-symlink-portability/tasks.md
- Tests: <baseline> -> N (+M)
- Validation: <N>/N REQUIRED checked
- Notes: <one paragraph>
- Next: Sprint 5 close block below

### Sprint 5 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM, Architect, SW Dev per feature
- Features completed: F-03, F-04, F-05
- Commits: <list>
- Tests: <baseline> -> N
- PI-5 status: ACTIVE; Sprint 1 closed; <N> sprints remaining
- SDD-016, SDD-017: DONE
- Notes: <one paragraph -- bundle shipped; brownfield portability validated
  by <test or live host integration>; lessons for PI-5 Sprint 2>
- Next: PI-5 Sprint 2 = <bundle from F-03 allocation>. Kickoff prompt:
  <SPRINT-06-KICKOFF.prompt.md if EM has authored, else "owner to request
  from EM">
```

Then:

1. `python spec-driven-development/cli/state_builder.py`
2. `python spec-driven-development/cli/state_builder.py build-index --pi PI-5`
3. Commit regeneration as `chore: regenerate exec/ state -- Sprint 5 close`
4. Push `origin/master`.
5. Tell the owner: "Sprint 5 closed at SHA `<sha>`. PI-5 Sprint 2 ready:
   `<bundle>`. Request next kickoff prompt from EM."

---

## 7. Do NOT do

- Do NOT add third-party Python dependencies.
- Do NOT modify the locked spec, validation, or clarification log.
- Do NOT modify `constitution/**`.
- Do NOT modify `render_html()` or T-001..T-004 in `cli/state_builder.py`
  (lock from `b7ce642` still applies).
- Do NOT install the symlink against a real host repo without owner approval
  (test against `tmp_path` only in this session).
- Do NOT close Sprint 5 without owner approval.
- Do NOT start PI-5 Sprint 2 in this session.
