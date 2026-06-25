# SPRINT 5 KICKOFF -- PI-5 launch + Brownfield-portability bundle (SDD-016 + SDD-017)

You are leading **Sprint 5**, which is also the **first sprint of PI-5**. Your
job is to (a) launch PI-5 cleanly by allocating the deferred Scott Feedback
Bundle across PI-5 sprints, and (b) execute the first PI-5 sprint:
brownfield-portability (SDD-016 `.github/` symlink trick + SDD-017
`dev-env-manager` worker).

You are the **Principal Executive Manager** for this kickoff. The PM and
Architect own the planning features; the SW Dev owns the implementation
feature.

---

## HARD PREREQUISITE -- STOP IF NOT MET

This sprint **must not start** until:

1. Sprint 4 (FDC) is marked DONE in `sprints/PI-4/CURRENT_PI.md`.
2. `exec/sprint-progress.md` shows the Sprint 4 close block with PI-4 status.
3. Full test suite passes (>= the post-Sprint-4 baseline).
4. `git log` shows the FDC commits on `origin/master`.
5. Owner has explicitly approved Sprint 4 close.

**Verify all five before any F-## prompt below is loaded.** If any fail, STOP
and return to Sprint 4. Do not start PI-5 planning on a broken or unfinished
PI-4.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute the sprint sequence below. Each F-## runs in its own fresh session.
4. Append a sprint-close block to `exec/sprint-progress.md` when DONE.

---

## 1. Sprint goal

Two outcomes:

A. **Launch PI-5** with a real plan: `sprints/PI-5/CURRENT_PI.md` exists,
   BACKLOG.md sprint assignments updated for the 11 deferred Scott items,
   PI-5 sprint allocation proposed and approved by owner.

B. **Ship the brownfield-portability bundle** (SDD-016 + SDD-017) through the
   full SDD lifecycle: CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> QA ->
   RETRO.

The bundle is the recommended PI-5 starter per the EM rationale on
2026-06-05: it is the highest-impact brownfield finisher (lets the framework
be dropped into any existing repo via `.github/` symlink without polluting the
host's `.github/`), unblocks future portability tests, and is self-contained
(no upstream blockers).

---

## 2. Sprint sequence

| Order | Feature | File | Owner | Why this order |
|-------|---------|------|-------|----------------|
| 1 | F-03: PI-5 kickoff -- allocate Scott bundle, write `sprints/PI-5/CURRENT_PI.md`, update BACKLOG sprint assignments | [F-03-pi5-kickoff.prompt.md](F-03-pi5-kickoff.prompt.md) | PM | Cannot run any PI-5 implementation without PI-5 existing |
| 2 | F-04: CLARIFY + SPEC for SDD-016 + SDD-017 bundle | [F-04-symlink-portability-clarify-spec.prompt.md](F-04-symlink-portability-clarify-spec.prompt.md) | PM + Architect | SDD-016 is flagged "CLARIFY first; co-spec with SDD-017" in BACKLOG; spec must precede implementation |
| 3 | F-05: PLAN + TASKS + IMPLEMENT + QA + RETRO for the bundle | [F-05-symlink-portability-implement.prompt.md](F-05-symlink-portability-implement.prompt.md) | SW Dev + workers | Depends on F-04 spec |

### Coordination notes

- F-03, F-04, F-05 run **sequentially**. Each must DONE before the next
  starts.
- F-03 writes `sprints/PI-5/CURRENT_PI.md`, `backlog/BACKLOG.md` (sprint
  column updates only -- no new SDD-IDs), and `docs/Management/PI-5/INDEX.md`
  (new folder).
- F-04 writes a new spec dir
  `specs/YYYY-MM-DD-symlink-portability/` (slug chosen by Architect).
- F-05 writes implementation files. The implementation scope likely touches
  `cli/bootstrap.py` (extension), a new skill file, a new agent file. The
  Architect's spec in F-04 will name the exact file scope.

---

## 3. Hard constraints

- **Constitution edits**: SDD-017 hires a new worker, which adds a row to
  `roster/agents.json` -- that is NOT a constitution edit (Article VIII
  applies only to `constitution/**`). If, during F-04, the Architect determines
  a constitution amendment is needed, that becomes a Level-2 decision with a
  Friction Analysis (`templates/level-2-decision.md`) before any change.
- **Stdlib only** for any new CLI code.
- **No host-project pollution**: SDD-016 must respect the host repo's
  `.gitignore` and never overwrite a host's existing `.github/` content
  without explicit opt-in. The Architect spec must encode this.
- **One feature, one context-isolated unit** (Article VII): F-03, F-04, F-05
  each run in their own fresh chat session OR EM-routed subagent dispatch
  (both satisfy context isolation).

---

## 4. Sprint close criteria

Sprint 5 closes DONE when:

1. PI-5 has a real `CURRENT_PI.md` with sprint allocation approved by owner.
2. SDD-016 + SDD-017 spec, plan, tasks, implementation all done; validation
   contract 100% on REQUIRED.
3. Full test suite passes (>= post-Sprint-4 baseline + new bundle tests).
4. `sprints/PI-5/CURRENT_PI.md` Sprint 1 (this sprint) marked DONE with date,
   commit SHAs, and retro.
5. `BACKLOG.md` shows SDD-016 + SDD-017 as DONE with commit SHAs.
6. `exec/state.md` regenerated.
7. Owner has approved the close.
8. The next PI-5 sprint is identified (by the PM in F-03's plan) and a
   `SPRINT-06-KICKOFF.prompt.md` is added to `feature-prompts/` if the next
   sprint is ready to start. (Or note "PI-5 Sprint 2 plan deferred to next
   session" if not ready.)

---

## 5. Reporting

Append to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### Sprint 5 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM, Architect, SW Dev per feature
- Features completed: F-03, F-04, F-05
- Commits: <list>
- Tests: <baseline> -> N
- PI-5 status: ACTIVE; Sprint 1 closed; <N> sprints remaining
- SDD-016 + SDD-017: DONE
- Notes: <one paragraph -- what shipped, what was learned, what to carry to
  PI-5 Sprint 2>
- Next: PI-5 Sprint 2 = <bundle>. Kickoff prompt: <file or "not yet authored
  -- owner to request from EM">
```

---

## 6. Do NOT do

- Do NOT start any F-## before HARD PREREQUISITE is met.
- Do NOT skip CLARIFY for SDD-016. BACKLOG explicitly tags it as
  CLARIFY-required.
- Do NOT bundle SDD-018 (UI lifecycle variant), SDD-019/020 (serial gate +
  dedup), SDD-021/022/023, or SDD-025 into this sprint. Those are future PI-5
  sprints (the PM allocates in F-03).
- Do NOT touch `constitution/**` without an ADR (Article VIII).
- Do NOT pollute host-project `.github/` in any portability work (this is
  the whole point of SDD-016 -- symlink, not copy).
- Do NOT promote any PI-5 work to anything other than `origin/master`.
