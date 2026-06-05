# F-02 -- FDC implement, validate, QA, retro, close Sprint 4

| Field | Value |
|---|---|
| Backlog ID | SDD-FDC-001 |
| Priority | P2 |
| Size | M |
| Sprint | PI-4 / Sprint 4 |
| Phase | IMPLEMENT + REVIEW + RETRO + SPRINT CLOSE |
| Owner | Principal Software Developer (lead); workers per dispatch |
| Prerequisite | F-01 DONE (`tasks.md` exists and is locked) |
| Blocks | Sprint 5 (PI-5 kickoff) -- cannot start until this finishes |

---

## 0. How to use this prompt

Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) first. Then implement the
tasks in `tasks.md`, run QA, write retro, close Sprint 4 and (with owner
approval) close PI-4. Append result block to `sprint-progress.md`.

This is a **single-feature, multi-session-possible** prompt: if the task list
is large, you (as SW Dev) dispatch worker sessions via
`cli/fleet.py dispatch`. Each dispatched worker gets its own session, but they
all roll up to this F-02 result block.

---

## 1. Project goal (short)

Take the FDC `tasks.md` (locked by F-01) and ship every REQUIRED item from the
validation contract. Result: schema-lint + frontmatter on every `specs/**` and
`sprints/**` doc + `state_builder count` subcommand + opt-in commit-msg hook +
S1 lock guard test. Then close Sprint 4 cleanly and (with owner approval)
close PI-4.

---

## 2. The rules

See [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) sections 3-7. Load-bearing:

- **S1 footprint lock from commit `b7ce642`**: `render_html()` +
  `load_sprint_table` + `load_sprint_goal` + `detect_current_sprint` +
  `load_decisions` are byte-identical to `b7ce642`. The lock guard test
  enforces this with `inspect.getsource` + `hashlib.sha256`. **If your changes
  break this test, you have violated the spec. Revert and re-approach.**
- **Stdlib only.** No PyYAML, no Requests, no Click. `argparse`, `sqlite3`,
  `pathlib`, `json`, `re`, `hashlib`, `inspect`, `sys`, `os`.
- **Reuse `parse_frontmatter`** from existing CLI; do not duplicate.
- **Tests-first within each task.** Add the failing test, then the code, then
  the green test. CLI-PATTERN rule applies.
- **Article X**: `validation.md` is LOCKED. R1-R7 must all check; you do not
  edit the contract.

---

## 3. Onboarding on this task

### What exists at start

- F-01 has produced `specs/2026-06-04-filesystem-data-contracts/tasks.md`
  with a sequenced task list and traceability matrix.
- Spec, plan, validation, ADR-012 all already committed.
- 152 tests passing on `master` at start.

### What you produce

Per the FDC plan (re-stated for grounding -- the locked plan in `plan.md` is
authoritative):

1. `specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md` -- the
   documented schema with locked enums (Phase 1).
2. `cli/schema_lint.py` -- extended with frontmatter contract validator (Phase
   2). Reuses `parse_frontmatter`. Tests in `cli/test_schema_lint.py`.
3. `cli/state_builder.py` -- new `count` subcommand handler ONLY (Phase 3).
   Additive. No edits to `render_html` or T-001..T-004.
   - Output shape (default): `{ "by_status": {...}, "by_type": {...}, "total": N }`
   - `--format table` prints human-readable table.
   - `--sprint <id>` selector (optional, additive).
4. `docs/COMMIT-CONVENTION.md` + `cli/hooks/commit-msg` -- opt-in hook (Phase
   4). Documentation + script only. No CI, no auto-install.
5. Frontmatter backfill: every markdown under `specs/**` and `sprints/**`
   gains valid frontmatter (`id`, `type`, `status`, `owner`, `updated`)
   (Phase 5).
6. S1 lock guard test: `cli/test_state_builder.py::test_b7ce642_lock_guard`
   asserts byte-identity of the 5 locked symbols vs golden hashes computed
   from `b7ce642`. (Compute the hashes once; commit them as constants in the
   test file.)

### File scope (cumulative across all tasks in this feature)

**Allowed (additive only)**:
- `cli/schema_lint.py`
- `cli/test_schema_lint.py`
- `cli/state_builder.py` (handler additions only; no edits to the 5 locked symbols)
- `cli/test_state_builder.py` (new test functions only; do not modify existing tests covering the locked surface)
- `cli/hooks/commit-msg` (new file)
- `specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md` (new file)
- `docs/COMMIT-CONVENTION.md` (new file)
- Any `specs/**/*.md` or `sprints/**/*.md` for the backfill (frontmatter prepend only; body untouched)
- `sprints/PI-4/CURRENT_PI.md` (status update + retro paragraph at sprint close)
- `constitution/roadmap.md` (PI-4 -> DONE marker at sprint close)
- `exec/sprint-progress.md` (your result block + sprint-close block)
- `exec/state.md`, `exec/state.html`, `exec/work-index.md` (regenerated via `state_builder.py`)
- `docs/Management/PI-4/INDEX.md` (regenerated via `state_builder.py build-index --pi PI-4`)

**Blocked**:
- `cli/state_builder.py` -- the bodies of `render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`.
- `constitution/principles.md`, `decision-policy.md`, `quality-policy.md`,
  `mission.md`, `tech-stack.md`, `CONTEXT.md` (Article VIII).
- `specs/2026-06-04-filesystem-data-contracts/spec.md`, `plan.md`,
  `validation.md`, `clarification-log.md` (locked).
- Any other in-flight feature's spec dir (none currently active besides FDC).

### Optional dispatch path

If `tasks.md` has more than 6 tasks, use
`python spec-driven-development/cli/fleet.py dispatch` to produce per-task
dispatch packets under `dispatches/PI-4/NNNNNN.md`. Each packet is pasted in
its own worker session. The ledger at `ledger/fleet.db` records the dispatch.
You (SW Dev) integrate the results back into this F-02 block.

If `tasks.md` has 6 or fewer tasks, you can implement them in this session
without dispatch.

---

## 4. Acceptance criteria (testable)

| AC | Statement | Verification |
|----|-----------|--------------|
| AC-1 | R1: schema-lint reports finding + exits non-zero for missing required field | `cli/test_schema_lint.py` |
| AC-2 | R2: schema-lint exits zero with no findings when all valid | `cli/test_schema_lint.py` |
| AC-3 | R3: `state_builder.py count` default JSON shape matches contract; `total` equals sum of `by_status` and `by_type` | `cli/test_state_builder.py::test_count_default_json_shape` |
| AC-4 | R4: `state_builder.py count --format table` exits zero, prints table | `cli/test_state_builder.py::test_count_table_format` |
| AC-5 | R5: lock guard test passes -- `render_html`, T-001..T-004 byte-identical to `b7ce642` golden hashes | `cli/test_state_builder.py::test_b7ce642_lock_guard` |
| AC-6 | R6: every in-scope `specs/**` + `sprints/**` markdown has valid frontmatter (lint exits 0 on full repo scan) | `python cli/schema_lint.py specs/ sprints/` |
| AC-7 | R7: full existing test suite passes (no regression) | `python -m pytest spec-driven-development/ --tb=no -q` |
| AC-8 | O1: opt-in commit-msg hook rejects non-conforming and accepts conforming; uninstalled state unchanged | Shell test in `cli/test_schema_lint.py` or smoke script |
| AC-9 | O2: `docs/COMMIT-CONVENTION.md` exists with examples | File present |
| AC-10 | Tests count: >= 152 + N new tests added (target +6 minimum: R1, R2, R3, R4, R5, hook smoke) | `pytest -q` count |
| AC-11 | Sprint 4 section in `sprints/PI-4/CURRENT_PI.md` marked DONE with date, commit SHAs, and a 1-paragraph retro | Read file |
| AC-12 | `exec/state.md` regenerated; FDC shows DONE; PI-4 shows correct close status | Read file after regenerate |

---

## 5. SDD workflow

- Spec dir: `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/`
- Slug: `filesystem-data-contracts`
- Worktree: **none**.
- Branch: `master`.
- Commands you run, in order:
  1. `/implement` per task in `tasks.md` (TDD: test first, then code).
  2. `/qa` -- two-stage review (spec compliance, then code quality). Slash
     command at [`../../.github/prompts/qa.prompt.md`](../../.github/prompts/qa.prompt.md).
  3. `/retro` -- write retro into `sprints/PI-4/CURRENT_PI.md` (or a separate
     `sprints/PI-4/sprint-04-retro.md`). Slash command at
     [`../../.github/prompts/retro.prompt.md`](../../.github/prompts/retro.prompt.md).
- Sprint close: update `sprints/PI-4/CURRENT_PI.md` Sprint 4 status to DONE.
  Update `constitution/roadmap.md` PI-4 row appropriately.

---

## 6. Definition of done + report

Sections 7-10 of [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) apply. Append two
blocks to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### F-02 -- fdc-implement -- DONE

- Date: YYYY-MM-DD
- Owner: Principal Software Developer (+ workers: <list if dispatched>)
- Commits: <sha-1>, <sha-2>, ...
- Files changed: <count>
  - cli/schema_lint.py
  - cli/test_schema_lint.py
  - cli/state_builder.py (additive only)
  - cli/test_state_builder.py
  - cli/hooks/commit-msg
  - specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md
  - docs/COMMIT-CONVENTION.md
  - <N> frontmatter backfills across specs/** + sprints/**
- Tests: 152 -> N (+M)
- Validation: 7/7 REQUIRED checked; <N>/2 OPTIONAL checked
- Lock guard: PASS (b7ce642 byte-identity verified)
- Notes: <one paragraph>
- Next: Sprint 4 close block below

### Sprint 4 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Software Developer
- Features completed: F-01, F-02
- Commits: <list>
- Tests: 152 -> N
- Validation: 7/7 REQUIRED, <N>/2 OPTIONAL
- PI-4 status: DONE (or: DONE-WITH-DEFERRED ... )
- Notes: <one paragraph -- what shipped, what was learned, what to carry to PI-5>
- Next: Sprint 5 unblocked. Paste
  spec-driven-development/feature-prompts/SPRINT-05-KICKOFF.prompt.md in a
  fresh session.
```

Then:

1. Run `python spec-driven-development/cli/state_builder.py` (regenerate
   exec/).
2. Run `python spec-driven-development/cli/state_builder.py build-index --pi PI-4`
   (refresh PI-4 management index).
3. Commit the regeneration as `chore: regenerate exec/ state -- Sprint 4 close`.
4. Push to `origin/master`.
5. Tell the owner: "Sprint 4 closed at SHA `<sha>`. PI-4 status: `<DONE|...>`.
   Sprint 5 unblocked -- paste
   `spec-driven-development/feature-prompts/SPRINT-05-KICKOFF.prompt.md`."

---

## 7. Do NOT do

- Do NOT touch `render_html()` or T-001..T-004 in `state_builder.py`. The lock
  guard test will catch it; revert immediately if it fails.
- Do NOT add third-party dependencies.
- Do NOT skip the backfill (R6 is REQUIRED -- not optional).
- Do NOT loosen `validation.md` if R5 (lock guard) fails. Revert and approach
  the code differently.
- Do NOT close Sprint 4 without owner approval.
- Do NOT close PI-4 in this session if any PI-4 commitment is not actually
  done -- mark deferred items explicitly in `roadmap.md`.
- Do NOT start Sprint 5 in this session. New session, new prompt.
- Do NOT promote to anything other than `origin/master` (there is no other
  branch).
