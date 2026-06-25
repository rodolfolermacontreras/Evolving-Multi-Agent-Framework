# SPRINT 6 KICKOFF -- PI-5 Sprint 2 / Anti-Conflict Gates + Carry-Over

You are leading **Sprint 6**, which is **PI-5 Sprint 2**. Your job is to (a)
close the 23-question CLARIFY load that the Architect scaffolded into the
three Sprint 6 spec dirs on 2026-06-07, (b) lock validation contracts and
produce plans + tasks for all three specs, and (c) implement, QA, retro, and
close the sprint.

You are the **Principal Executive Manager** for this kickoff. The PM and
Architect own CLARIFY and spec finalization (F-06); the Architect and SW Dev
own PLAN + TASKS (F-07); the SW Dev and dispatched workers own IMPLEMENT, QA,
RETRO, and close (F-08).

---

## HARD PREREQUISITE -- STOP IF NOT MET

This sprint **must not start** until **all six** of the following are true:

1. **Sprint 5 marked DONE** in
   [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md) (Sprint 1
   section status = "CLOSED 2026-06-06"; close commit `3cb7dea` on
   `origin/master`).
2. **Sprint 5 close block present** in
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md).
3. **Tests >= 213** baseline (the Sprint 5 close baseline). Verify with
   `python -m pytest spec-driven-development/ --tb=no -q`.
4. **BACKLOG entries SDD-027..031 present** in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) (filed at commit
   `17e7cc0` -- audit follow-ups; renumbered from owner-specified
   SDD-026..030 due to collision with existing SDD-026, see commit body).
5. **Sprint 6 spec dirs scaffolded** with CLARIFY questions present (filed
   at commit `d08cd73` -- three dirs under `specs/2026-06-07-*`):
   - [`../specs/2026-06-07-serial-clarify-spec-gate/`](../specs/2026-06-07-serial-clarify-spec-gate/) -- 9 CLARIFY questions
   - [`../specs/2026-06-07-cross-feature-dedup/`](../specs/2026-06-07-cross-feature-dedup/) -- 7 CLARIFY questions
   - [`../specs/2026-06-07-host-gitignore-protection/`](../specs/2026-06-07-host-gitignore-protection/) -- 7 CLARIFY questions
6. **Owner has explicitly approved Sprint 6 start.**

Verify all six before any F-## prompt below is loaded. If any fail, STOP and
surface the failure to the owner. Do not start Sprint 6 on a broken or
unfinished Sprint 5, on a missing audit backlog, or on a missing spec
scaffold.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above (six checks).
3. Execute the sprint sequence below. **Each F-## runs in its own
   context-isolated unit** -- a fresh chat session OR an EM-routed subagent
   dispatch (both satisfy context isolation) (Article VII: one feature, one
   context-isolated unit).
4. Append a sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) when DONE.

---

## 1. Sprint goal

Ship the anti-conflict gates (SDD-019 + SDD-020) and clear the
high-priority Sprint 5 audit carry-over (SDD-027 host `.gitignore`
protection) through the full SDD lifecycle: CLARIFY -> SPEC -> PLAN -> TASKS
-> IMPLEMENT -> QA -> RETRO.

- **Primary scope (P1, must ship)**: SDD-019, SDD-020, SDD-027.
- **Capacity housekeeping (P2, if room)**: SDD-028 (real-Windows junction
  integration test) and SDD-029 (stale-symlink vs real-directory conflict
  distinction). Both touch the same `bootstrap.py host_link()` code path
  SDD-027 modifies, so they bundle naturally if the F-08 implementation
  session has bandwidth.
- **PI-4 deferrals (carry-along, if room)**: domain-skill annotations,
  GitHub Actions Node.js bump.

This is the **highest-CLARIFY-load sprint in PI-5** (23 questions across
three specs). Budget the F-06 session accordingly.

---

## 2. Sprint sequence

| Order | Feature | File | Owner | Why this order |
|-------|---------|------|-------|----------------|
| 1 | F-06: CLARIFY answers for all 3 specs + spec finalization | [F-06-sprint6-clarify.prompt.md](F-06-sprint6-clarify.prompt.md) | PM + Architect | 23 CLARIFY questions across 3 specs is a CLARIFY-heavy load and must complete before PLAN. Spec dirs already scaffolded at `d08cd73`; this session answers, finalizes, and locks validation contracts. |
| 2 | F-07: PLAN + TASKS for all 3 specs | [F-07-sprint6-plan-tasks.prompt.md](F-07-sprint6-plan-tasks.prompt.md) | Architect + SW Dev | Depends on finalized specs from F-06. Produces the locked validation contracts and per-spec `plan.md` + `tasks.md`. If SDD-019 CLARIFY confirmed a constitutional amendment, F-07 also drafts the ADR. |
| 3 | F-08: IMPLEMENT + QA + RETRO + sprint close | [F-08-sprint6-implement.prompt.md](F-08-sprint6-implement.prompt.md) | SW Dev + workers | Depends on locked validation contracts from F-07. Implements the three specs, runs QA, writes retro, closes Sprint 6. Closes **PI-5 Sprint 2**, not PI-5 itself (three sprints remain after this one). |

### Coordination notes

- F-06, F-07, F-08 run **sequentially**. Each must DONE before the next
  starts.
- **SDD-019 <-> SDD-020 ordering** is decided inside F-06: SDD-020's
  CLARIFY Q5 explicitly forces the integration ordering decision
  (dedup-first / gate-first / independent). The Architect's prep note
  (`sprints/PI-5/SPRINT-2-PREP-NOTES.md`) recommends answering SDD-019 Q5
  and SDD-020 Q5 **jointly** to avoid divergent decisions. F-06 honors
  that recommendation.
- **SDD-019 is a CONSTITUTIONAL AMENDMENT CANDIDATE.** ADR drafting is
  BLOCKED until CLARIFY closes. If F-06's CLARIFY round confirms an
  amendment is required (extend Article VII, add a new Article, or amend
  `decision-policy.md`), F-07 includes ADR drafting. The amendment itself
  becomes a Level-2 decision and is routed to the owner via the EM before
  any `constitution/**` edit.
- **SDD-027 is an Article X amendment CANDIDATE** per owner direction
  2026-06-07. Handle SDD-027 as a normal spec first. Only escalate to an
  Article X amendment IF the spec proves the article must change.
  **Friction Analysis is NOT required up front.** F-06's CLARIFY Q1 in the
  SDD-027 spec dir explicitly decides whether the host-`.gitignore` rule
  fits within Article X as written or requires an amendment; only if the
  latter does F-07 branch into amendment ceremony.

---

## 3. Hard constraints

- **Stdlib only** for any new CLI code (Article V). The likely touchpoints
  are `cli/schema_lint.py`, `cli/bootstrap.py`, and possibly new gate
  helpers; all must be `argparse` + `sqlite3` + `pathlib` + `json` + `sys`
  + `os` only. No PyYAML, no `rich`, no `click`.
- **No `constitution/**` edit without an ADR** (Article VIII). SDD-019 may
  require one; if so, the ADR is committed before the constitution edit
  and the edit is owner-approved.
- **No host-project pollution.** SDD-027 is explicitly about NOT writing
  into a host repo's tree without explicit opt-in; the spec must encode
  this in its acceptance criteria.
- **One feature, one context-isolated unit** (Article VII). F-06, F-07, F-08
  each run in their own fresh chat session OR EM-routed subagent dispatch
  (both satisfy context isolation). Do not collapse them into a single session
  unless the owner explicitly approves a Sprint-5-style consolidated
  execution; the default is three isolated units.

---

## 4. Sprint close criteria

Sprint 6 closes DONE when **all eight** of the following are true:

1. All three spec validation contracts (SDD-019, SDD-020, SDD-027) at
   **100% REQUIRED** items checked.
2. Full test suite passes (>= **213 baseline** + new tests added in F-08).
3. [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
   Sprint 2 section marked **DONE** with date, commit SHAs, and one-
   paragraph retro.
4. [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) entries SDD-019,
   SDD-020, and SDD-027 status updated to **DONE** with commit SHAs.
   SDD-028 and SDD-029 either DONE (if pulled in) or explicitly carried
   forward with a note.
5. If any ADR was drafted (SDD-019 amendment, SDD-027 Article X amendment,
   or otherwise), it is committed under `docs/ADR/` and approved by the
   owner.
6. `exec/state.md` regenerated via
   `python spec-driven-development/cli/state_builder.py`.
7. **Owner has approved the close.**
8. **`SPRINT-07-KICKOFF.prompt.md` authored** if PI-5 Sprint 3 is ready
   to start (PI-5 Sprint 3 = UI Lifecycle Variant, SDD-018). If not
   ready, append an explicit "deferred to next session" note to the
   Sprint 6 close block and tell the owner.

---

## 5. Reporting

Append to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### Sprint 6 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM + Architect owned F-06; Architect + SW Dev owned F-07; SW Dev + workers owned F-08
- Features completed: F-06, F-07, F-08
- Commits: <list>
- Tests: 213 -> N
- Validation: SDD-019 N/N REQUIRED, SDD-020 N/N REQUIRED, SDD-027 N/N REQUIRED
- ADRs: <list any drafted, or "none">
- PI-5 status: ACTIVE; Sprint 2 closed; 3 sprints remaining (Sprint 3 = SDD-018 UI Lifecycle Variant)
- SDD-019: DONE
- SDD-020: DONE
- SDD-027: DONE
- SDD-028 / SDD-029: <DONE | carried forward with reason>
- PI-4 carry-over (domain-skill annotations, GH Actions Node.js bump): <DONE | carried forward>
- Notes: <one paragraph -- what shipped, what was learned, anti-conflict gate behavior in practice, anything Sprint 7 needs to know>
- Next: PI-5 Sprint 3 = UI Lifecycle Variant (SDD-018). Kickoff prompt: <file or "not yet authored -- owner to request from EM">
```

---

## 6. Do NOT do

- Do NOT start any F-## before HARD PREREQUISITE is met (all six checks).
- Do NOT answer CLARIFY questions in this kickoff session. CLARIFY runs in
  F-06's fresh session per Article VII.
- Do NOT edit any of the three scaffolded spec dirs in this kickoff
  session. They are F-06's territory.
- Do NOT touch `constitution/**` without an ADR (Article VIII). If
  SDD-019 or SDD-027 CLARIFY confirms an amendment is needed, the ADR is
  drafted in F-07 and the constitution edit happens only after owner
  approval.
- Do NOT add PyYAML or any other third-party dependency to `cli/**`
  (Article V).
- Do NOT pollute host-project trees in any SDD-027 implementation work --
  no writes to the host's `.gitignore` or `.github/` without explicit
  opt-in. The spec encodes this; the implementation honors it.
- Do NOT close Sprint 6 without owner approval.
- Do NOT promote anything to a branch other than `origin/master`.
- Do NOT start Sprint 7 in this session. It runs in its own fresh session
  using `SPRINT-07-KICKOFF.prompt.md` (which F-08 authors if Sprint 3 is
  ready, or defers if not).
