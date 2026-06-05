# SPRINT 4 KICKOFF -- PI-4 / Filesystem Data Contracts (FDC) finish

You are leading **Sprint 4** of **PI-4 (Alpha Release)** on the Evolving
Multi-Agent Framework. Your job in this session is to drive the FDC feature
(spec ID `SDD-FDC-001`) from `/tasks` through `/implement`, `/qa`, and `/retro`
to DONE -- closing PI-4 Sprint 4.

You are the **Principal Software Developer** (the SW Dev runs `/tasks` and
owns dispatch). If decomposition is large enough that you want to hand work to
worker sessions, use the F-## feature prompts referenced below.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) **end to end** before
   doing anything else. That file holds the rules; this file is sprint-specific.
2. Verify live state with the commands in section 1 of `_SHARED_ONBOARDING.md`.
3. Execute the sprint sequence below in order.
4. Append a sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) when DONE.

---

## 1. Sprint goal

Ship **Filesystem Data Contracts** (`SDD-FDC-001`):

- YAML frontmatter schema for `specs/**` + `sprints/**` markdown
- Schema-lint extension (`cli/schema_lint.py`) that validates the contract
- `state_builder.py count` subcommand that rolls up doc counts by `status` and
  `type`
- Documented commit-message convention + opt-in `commit-msg` hook
- Frontmatter backfill of all in-scope artifacts
- Automated S1 lock guard (`render_html()` + T-001..T-004 byte-identical to
  commit `b7ce642`)

All five deliverables and the locked decisions are pre-approved. The spec is
APPROVED with conditions resolved. The plan and ADR-012 are committed (commit
`58f3af3` and `ae603c4`).

---

## 2. Hard constraints (DO NOT VIOLATE)

- **S1 footprint lock from commit `b7ce642`**: `render_html()` and data-layer
  functions `T-001..T-004` (`load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`) are **byte-identical** to
  `b7ce642`. Additive code only. An automated guard test (R5 in
  `validation.md`) enforces this.
- **Stdlib only** for any new CLI code (Article V).
- **Reuse `parse_frontmatter`** from existing CLI; do not duplicate the parser.
- The validation contract at
  [`../specs/2026-06-04-filesystem-data-contracts/validation.md`](../specs/2026-06-04-filesystem-data-contracts/validation.md)
  is **LOCKED** at `/tasks`. R1-R7 must pass before DONE. O1-O2 are optional
  but expected.
- File scope is constrained to:
  - `cli/schema_lint.py` (additive validator only)
  - `cli/test_schema_lint.py`
  - `cli/state_builder.py` (additive `count` subcommand handler ONLY -- do not
    touch `render_html` or T-001..T-004)
  - `cli/test_state_builder.py` (new tests only -- do not modify existing
    tests covering the locked surface)
  - `cli/hooks/commit-msg` (new file, opt-in)
  - `specs/2026-06-04-filesystem-data-contracts/tasks.md` (created in F-01)
  - `specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md`
  - `docs/COMMIT-CONVENTION.md`
  - Backfilled frontmatter across `specs/**` and `sprints/**` markdown (R6)

---

## 3. Sprint sequence

Execute in this order. Each F-## is a separate prompt file you (or a worker
session) load in a fresh chat.

### Order

| Order | Feature | File | Why this order |
|-------|---------|------|----------------|
| 1 | F-01: produce `tasks.md` for FDC | [F-01-fdc-tasks.prompt.md](F-01-fdc-tasks.prompt.md) | `/tasks` must complete before `/implement` -- this is the gate the sprint is currently parked on |
| 2 | F-02: implement, validate, QA, retro, close sprint | [F-02-fdc-implement.prompt.md](F-02-fdc-implement.prompt.md) | Only runnable after `tasks.md` exists. Closes the sprint and the PI-4 increment. |

### Coordination notes

- F-01 and F-02 **must run sequentially**. F-02 reads the tasks file F-01
  produces.
- Both features write to `cli/state_builder.py`. They cannot run in parallel
  with each other or with any other feature touching that file. (PI-4 has no
  other in-flight features touching it, so no collision risk today.)
- If F-02 produces more than 6 implementation tasks, decompose them into
  worker dispatches via `python spec-driven-development/cli/fleet.py dispatch`
  (writes a packet to `dispatches/PI-4/NNNNNN.md`). One worker session per
  dispatched task.

---

## 4. Open question to resolve in this sprint

`exec/state.md` shows `friction-analysis-template` at IMPLEMENT 0/12
validation, but SDD-014 closed DONE in commit `7438bfd`. This is likely a
state_builder heuristic miss, not a real bug. As part of F-02 cleanup, **verify
the friction-analysis-template validation file** and either:

- Mark its REQUIRED items checked (if the work is genuinely done), then
  regenerate `state.md`, OR
- Open a small follow-up note in `sprint-progress.md` describing the
  state_builder heuristic gap (would become a PI-5 P3 cleanup item).

This is a 5-minute investigation, not a real workstream. Do not let it expand.

---

## 5. Sprint close criteria

Sprint 4 closes DONE when:

1. All REQUIRED items (R1-R7) in
   [`../specs/2026-06-04-filesystem-data-contracts/validation.md`](../specs/2026-06-04-filesystem-data-contracts/validation.md)
   are checked.
2. Full test suite passes (>= 152 baseline + new tests added in F-02).
3. `b7ce642` S1 lock guard test PASSES.
4. `sprints/PI-4/CURRENT_PI.md` Sprint 4 section status updated to **DONE**
   with date + commit SHAs.
5. A retro block appended to `sprints/PI-4/CURRENT_PI.md` (one paragraph:
   what worked, what to improve, lessons for PI-5).
6. `exec/state.md` regenerated.
7. Owner has approved the close (Level-2 -- the close is the sprint promotion).
8. PI-4 closure: with Sprint 4 DONE, PI-4 itself can close. Either mark PI-4
   `roadmap.md` and `CURRENT_PI.md` accordingly (PI-4 -> DONE), OR explicitly
   note any deferred PI-4 work and the rationale.

---

## 6. Reporting

When the sprint closes, append a sprint-close block to
[`../exec/sprint-progress.md`](../exec/sprint-progress.md) under "Sprint 4":

```markdown
### Sprint 4 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Software Developer
- Features completed: F-01, F-02
- Commits: <list>
- Tests: 152 -> N
- Validation: 7/7 REQUIRED checked; <N>/2 OPTIONAL checked
- PI-4 status: DONE / DEFERRED-ITEMS=...
- Notes: <one paragraph>
- Next: Sprint 5 ready -- paste SPRINT-05-KICKOFF.prompt.md in a fresh session
```

Then tell the owner the SHA and that Sprint 5 is unblocked.

---

## 7. Do NOT do

- Do NOT touch `render_html()` or T-001..T-004 in `state_builder.py`.
- Do NOT add PyYAML or any other third-party dependency.
- Do NOT skip the lock-guard test.
- Do NOT close the sprint without owner approval.
- Do NOT start Sprint 5 in this session. It runs in its own fresh session
  using `SPRINT-05-KICKOFF.prompt.md`.
