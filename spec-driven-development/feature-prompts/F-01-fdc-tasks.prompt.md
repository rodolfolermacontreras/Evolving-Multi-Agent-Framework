# F-01 -- FDC `/tasks` -- produce `tasks.md` for SDD-FDC-001

| Field | Value |
|---|---|
| Backlog ID | SDD-FDC-001 |
| Priority | P2 |
| Size | S |
| Sprint | PI-4 / Sprint 4 |
| Phase | TASKS |
| Owner | Principal Software Developer |
| Prerequisite | FDC spec + plan + ADR-012 committed (already true at HEAD `ae603c4`) |
| Blocks | F-02 (cannot start until `tasks.md` exists) |

---

## 0. How to use this prompt

Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) first. Then run `/tasks` on
the FDC spec to produce `tasks.md`. Commit it. Append a result block to
`sprint-progress.md`. Hand off to F-02.

This is a **single-session, single-feature** prompt. One-feature-one-session
applies (Article VII corollary).

---

## 1. Project goal (short)

Decompose the FDC plan into ordered, file-scoped tasks that the F-02 worker
can implement. The plan and validation contract are already locked; you are
not re-planning, you are converting the plan into a sequenced task list with
acceptance ties.

---

## 2. The rules

See [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) sections 3, 4, 5. Load-bearing
ones here:

- **Article X**: `validation.md` is LOCKED at `/tasks`. You may NOT modify
  R1-R7. You may add traceability (which task satisfies which R) but not relax
  the contract.
- **S1 footprint lock from commit `b7ce642`**: every task must be additive.
  Mark any task that comes close to the locked surface with an explicit "DO
  NOT TOUCH" boundary.
- **Stdlib only.** Tasks that hint at adding dependencies are invalid.

---

## 3. Onboarding on this task

### What exists

- Spec: [`../specs/2026-06-04-filesystem-data-contracts/spec.md`](../specs/2026-06-04-filesystem-data-contracts/spec.md)
  -- APPROVED with conditions resolved.
- Plan: [`../specs/2026-06-04-filesystem-data-contracts/plan.md`](../specs/2026-06-04-filesystem-data-contracts/plan.md)
  -- 5-phase implementation plan, locked decisions table.
- Validation: [`../specs/2026-06-04-filesystem-data-contracts/validation.md`](../specs/2026-06-04-filesystem-data-contracts/validation.md)
  -- R1-R7 required, O1-O2 optional.
- ADR: [`../docs/ADR/012-filesystem-frontmatter-data-contract.md`](../docs/ADR/012-filesystem-frontmatter-data-contract.md).
- Tasks template: [`../templates/task-list.md`](../templates/task-list.md).

### What is missing

- `specs/2026-06-04-filesystem-data-contracts/tasks.md` does not exist yet.
  That is what you write.

### Required structure of `tasks.md`

Use the template at [`../templates/task-list.md`](../templates/task-list.md).
At minimum, your task list must:

1. Cover all 5 plan phases (schema doc, schema-lint extension, doc-count +
   `count` subcommand, commit-msg convention + hook, frontmatter backfill).
2. Include the **S1 lock guard test** (R5) as its own explicit task with a
   golden-hash test.
3. Sequence tasks by dependency: schema doc -> schema-lint -> backfill ->
   count subcommand -> hook (the hook depends on nothing else; can run last
   or in parallel only if file-scope-disjoint).
4. For each task, list:
   - Task ID (T-FDC-NN)
   - Owner (developer-general unless skill-pack required)
   - File scope (allowed files + blocked files)
   - Acceptance ties (which R or O it satisfies)
   - Effort (XS/S/M)
   - Worktree: **none** (PI-4 has not used worktrees; do not introduce them)
5. End with a **traceability matrix** (T-FDC-NN -> R/O coverage), so reviewers
   can audit zero gaps.

---

## 4. Acceptance criteria (testable)

| AC | Statement | Verification |
|----|-----------|--------------|
| AC-1 | `specs/2026-06-04-filesystem-data-contracts/tasks.md` exists with YAML frontmatter (`id: SDD-FDC-001-tasks`, `type: tasks`, `status: locked`, `owner: principal-software-developer`, `updated: YYYY-MM-DD`) | `cat` the file; lint with `cli/schema_lint.py` once F-02 ships it |
| AC-2 | Every R1-R7 from `validation.md` is mapped to at least one task in the traceability matrix | Manual review |
| AC-3 | Every task has explicit `allowed_files` + `blocked_files` scope | Manual review |
| AC-4 | No task implies modifying `render_html()` or T-001..T-004 | Grep tasks.md for those names + verify boundary notes |
| AC-5 | No task implies a third-party dependency | Grep tasks.md for `pip install`, `import yaml`, `import requests`, etc. |
| AC-6 | Full test suite green (>= 152) | `python -m pytest spec-driven-development/ --tb=no -q` |
| AC-7 | Sprint-progress block appended; commit message conforms (`tasks(fdc): SDD-FDC-001 tasks.md authored`) | Read the file; check `git log -1` |

---

## 5. SDD workflow

- Spec dir: `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/`
- Slug: `filesystem-data-contracts`
- Worktree: **none** -- work directly on `master`.
- Branch: `master`.

You run `/tasks` (the slash command lives at
[`../../.github/prompts/tasks.prompt.md`](../../.github/prompts/tasks.prompt.md)).
Apply it to the FDC spec. Produce `tasks.md`. Commit. Done.

---

## 6. Definition of done + report

Sections 7-10 of [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) apply. Append to
[`../exec/sprint-progress.md`](../exec/sprint-progress.md) under "Sprint 4 / F-01":

```markdown
### F-01 -- fdc-tasks -- DONE

- Date: YYYY-MM-DD
- Owner: Principal Software Developer
- Commits: <sha>
- Files changed: 1
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/tasks.md
- Tests: 152 -> 152 (no code changes)
- Validation: tasks.md frontmatter present; traceability matrix complete (N
  tasks -> R1..R7 mapped)
- Notes: Decomposed FDC plan into <N> tasks across 5 phases. Sequence:
  <T-FDC-01> ... <T-FDC-NN>. Lock guard test is T-FDC-NN. Backfill is
  T-FDC-NN.
- Next: F-02 ready -- paste F-02-fdc-implement.prompt.md in a fresh session
```

Then tell the owner: "F-01 done at SHA `<sha>`. Paste
`spec-driven-development/feature-prompts/F-02-fdc-implement.prompt.md` in a
fresh session to start implementation."

---

## 7. Do NOT do

- Do NOT modify `validation.md` (locked).
- Do NOT modify `plan.md` (locked at SPEC sign-off).
- Do NOT write any implementation code in this session. That is F-02.
- Do NOT add tasks for items outside the locked plan (e.g. new features). If
  you find a gap, append a note to `sprint-progress.md` and flag the EM.
- Do NOT touch `render_html()` or T-001..T-004 in `state_builder.py`.
- Do NOT start F-02 in this session. New session, new prompt.
