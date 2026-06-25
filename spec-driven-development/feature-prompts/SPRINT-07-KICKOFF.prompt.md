# SPRINT 7 KICKOFF -- PI-5 Sprint 3 / Sprint 6 Completion + UI Lifecycle Variant

You are leading **Sprint 7**, which is **PI-5 Sprint 3**. Your job is to
(a) close the four LOCKED REQUIRED items deferred from Sprint 6 via the
SDD-032 completion bundle (F-09 -- implementation-only; spec + validation
+ plan + tasks already LOCKED at scaffold), then (b) take SDD-018 (UI
Lifecycle Variant -- relaxed Article X with `validation.md` delta entries)
through the full SDD lifecycle (F-10 = CLARIFY + SPEC + PLAN + TASKS;
F-11 = IMPLEMENT + QA + RETRO + sprint close).

You are the **Principal Executive Manager** for this kickoff. The SW Dev
and a Developer worker own F-09 (implementation only -- no spec work).
The PM and Architect own F-10 (SDD-018 CLARIFY through TASKS, including
any ADR drafting if the lifecycle variant requires an Article X amendment
or a new Article XII). The SW Dev and dispatched workers own F-11
(IMPLEMENT, QA, RETRO, sprint close).

---

## HARD PREREQUISITE -- STOP IF NOT MET

This sprint **must not start** until **all six** of the following are true:

1. **Sprint 6 marked CLOSED** in
   [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
   (Sprint 2 section status = "CLOSED 2026-06-07"; close commit
   `4a6941c` plus owner ratification commit `6c70e30` both present on
   `origin/master`).
2. **Sprint 6 close block present** in
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) with the
   owner ratification stamp recorded (Option 3 hybrid, 2026-06-08).
3. **Tests >= 259** baseline (the Sprint 6 close baseline preserved
   through owner ratification). Verify with
   `python -m pytest spec-driven-development/ --tb=no -q`.
4. **BACKLOG entries present and correct** in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) -- specifically:
   SDD-019, SDD-020, SDD-027 read **DONE-WITH-DEFERRED**; SDD-032 (P1)
   is filed and allocated to PI-5 Sprint 3 as F-09; SDD-033 (P3) is
   filed as unscheduled R12 doc carry-over. All filed at commit
   `6c70e30`.
5. **SDD-032 spec dir scaffolded** at
   [`../specs/2026-06-09-sprint-6-completion/`](../specs/2026-06-09-sprint-6-completion/)
   with **all four artifacts present** (`spec.md`, `validation.md`,
   `plan.md`, `tasks.md`) and the validation contract LOCKED at scaffold
   (7 REQUIRED + 2 OPTIONAL). Filed at commit `b005e66`.
6. **Owner has explicitly approved Sprint 7 start.**

Verify all six before any F-## prompt below is loaded. If any fail, STOP
and surface the failure to the owner. Do not start Sprint 7 on an
unratified Sprint 6 close, on a missing SDD-032 scaffold, or on an
unapproved kickoff.

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

Sprint 7 has **two outcomes** (both must ship):

1. **Close all 4 deferred LOCKED REQUIRED items from Sprint 6** (SDD-019.R7
   queue + SDD-019.R8 grandfather; SDD-020.R6 log writers + SDD-020.R8
   prompt hooks) via SDD-032 implementation. Per owner direction
   2026-06-08 (Option 3 hybrid ratification): **NO further deferral of
   REQUIRED items from this sprint's close, period.** If a REQUIRED item
   cannot close in F-09, F-09 does not close -- it stays in-flight or
   escalates to the owner via the EM.
2. **Ship SDD-018 (UI Lifecycle Variant)** -- relaxed Article X with
   `validation.md` delta entries -- through the full SDD lifecycle:
   CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> QA -> RETRO.

### Scope

- **Primary scope (P1, must ship)**: SDD-032 (Sprint 6 completion
  bundle), SDD-018 (UI Lifecycle Variant).
- **Capacity housekeeping (P3, if room)**: SDD-033 (HOST-INTEGRATION.md
  docs refresh -- doc-only carry-over from SDD-027 R12). May be pulled
  into F-09 close-out if capacity permits, or carried to a future sprint.
- **PI-4 deferrals (carry-along, if room)**: domain-skill annotations,
  GitHub Actions Node.js bump. Both still outstanding from PI-4; pull in
  only if F-09 + F-10 + F-11 finish with headroom.
- **PI-5 Sprint 6 follow-ups already absorbed**: SDD-019, SDD-020, and
  SDD-027 carry-over are fully accounted for in F-09 (SDD-032 covers the
  four R-items from SDD-019 and SDD-020; SDD-033 holds the SDD-027 R12
  doc gap separately).

---

## 2. Sprint sequence

| Order | Feature | File | Owner | Why this order |
|-------|---------|------|-------|----------------|
| 1 | F-09: SDD-032 IMPLEMENT (Sprint 6 completion bundle) | [F-09-sprint7-completion.prompt.md](F-09-sprint7-completion.prompt.md) | Principal Software Developer + Developer worker | **Implementation only** -- spec, validation, plan, and tasks are all LOCKED at scaffold (commit `b005e66`). The 4 deferred R-items from Sprint 6 must close before any new feature work. Closing them first restores the no-further-deferral promise the owner ratified on 2026-06-08. |
| 2 | F-10: SDD-018 CLARIFY + SPEC + PLAN + TASKS | [F-10-sprint7-sdd018-design.prompt.md](F-10-sprint7-sdd018-design.prompt.md) | Principal Product Manager + Principal Architect | SDD-018 has **no spec dir yet** -- F-10 scaffolds from scratch, runs a full CLARIFY round (likely heavy: the "relaxation surface" needs explicit owner guidance on which Article X rules relax, what replaces them, and how the delta entries flow into `validation.md`), finalizes `spec.md`, locks `validation.md`, writes `plan.md` and `tasks.md`. Depends on F-09 close so the SDD-020 prompt hooks (R8) and log writers (R6) exist and are wired before /clarify pulls in the dedup scanner during SDD-018's own CLARIFY round. |
| 3 | F-11: SDD-018 IMPLEMENT + QA + RETRO + sprint close | [F-11-sprint7-sdd018-implement.prompt.md](F-11-sprint7-sdd018-implement.prompt.md) | Principal Software Developer + workers | Depends on F-10's locked validation contract. Implements SDD-018, runs QA, writes the retro, closes Sprint 7. Closes **PI-5 Sprint 3**, not PI-5 itself (two sprints remain after this one: Sprint 8 = SDD-022 + SDD-015; Sprint 9 = SDD-021 + SDD-023 + SDD-025). |

### Coordination notes

- F-09, F-10, F-11 run **sequentially**. Each must close cleanly before
  the next session starts.
- **F-09 must close with all 7 REQUIRED items checked** in
  [`../specs/2026-06-09-sprint-6-completion/validation.md`](../specs/2026-06-09-sprint-6-completion/validation.md)
  before F-10 starts. Per owner direction 2026-06-08, **deferral of any
  REQUIRED item is explicitly prohibited from this sprint's close**.
- **F-10 will likely require a heavy CLARIFY round for SDD-018.** The
  phrase "relaxed Article X" is the key uncertainty: which Article X
  rules relax (the validation lock? the at-implementation contract? the
  no-loosening clause?), what replaces them (a new `delta` field in
  `validation.md`? a separate slash command? an opt-in marker on the
  spec dir?), and how delta entries flow through `schema_lint`. F-10
  must surface these as explicit CLARIFY questions to the owner before
  drafting the spec.
- **SDD-018 may require an Article X amendment OR a new Article XII**
  for the lifecycle variant. If F-10's CLARIFY round confirms a
  constitutional amendment is needed, **F-10 drafts the ADR** under
  `docs/ADR/` and routes it to the owner as a Level-2 decision via the
  EM. This is analogous to how ADR-013 (Article XI) was drafted during
  Sprint 6 F-07. The constitution edit itself does NOT happen in F-10
  or F-11 unless the owner explicitly approves it after reading the ADR.
- **Article XI lock behavior -- first live contention test.** When
  F-10's SDD-018 spec dir enters CLARIFY status, the new Article XI
  gate (now fully wired by SDD-032 R7 queue + R8 grandfather) should
  observe it. **This is the first real-world test of Article XI under
  live contention.** F-10 must explicitly verify the gate fires
  correctly when SDD-018 enters CLARIFY, and log the observed behavior
  (queue state, grandfather classification, any unexpected blocks) in
  the F-10 session report.
- **SDD-033 (P3 doc refresh)** may be pulled into F-09 close-out if
  capacity permits (it is a single HOST-INTEGRATION.md update, no code
  touched). Otherwise it carries to a future sprint with capacity. F-09
  decides; F-10 and F-11 do not touch it.

---

## 3. Hard constraints

- **Stdlib only** for any new CLI code (Article V). Likely touchpoints in
  F-09 are `cli/fleet.py` (additive helpers for queue + grandfather),
  `cli/dedup.py` (additive log-writer functions and `--emit-logs` flag),
  and prompt-file edits at `.github/prompts/triage.prompt.md` +
  `.github/prompts/clarify.prompt.md`. All Python must remain `argparse`
  + `sqlite3` + `pathlib` + `json` + `sys` + `os` only. No PyYAML, no
  `rich`, no `click`.
- **No `constitution/**` edit without an ADR** (Article VIII). SDD-018
  may require one; if so, the ADR is drafted in F-10 and the
  constitution edit happens only after explicit owner approval (Level-2
  routing via the EM).
- **No host-project pollution.** SDD-027's protections (committed at
  `302bee5`) still bind any implementation work; SDD-032 must not
  weaken them, and SDD-018 must not write into host trees as part of any
  UI artifact.
- **One feature, one context-isolated unit** (Article VII). F-09, F-10, F-11
  each run in their own fresh chat session OR EM-routed subagent dispatch
  (both satisfy context isolation). Do not collapse them into a single
  session unless the owner explicitly approves a consolidated execution
  (the default is three isolated units).
- **NO REQUIRED-item deferral from Sprint 7 close** per owner direction
  2026-06-08 (Option 3 hybrid established the no-silent-slip precedent
  in writing). If a REQUIRED item cannot close, the relevant feature
  does not close -- the EM routes to the owner before any close commit
  lands.

---

## 4. Sprint close criteria

Sprint 7 closes DONE when **all nine** of the following are true:

1. **SDD-032 validation contract at 100% REQUIRED items checked
   (7 / 7)** in
   [`../specs/2026-06-09-sprint-6-completion/validation.md`](../specs/2026-06-09-sprint-6-completion/validation.md).
2. **SDD-018 validation contract at 100% REQUIRED items checked**
   (item count TBD -- the contract is locked in F-10).
3. **Full test suite passes** with test count >= 259 (Sprint 6 baseline)
   plus the new tests added in F-09 and F-11.
4. [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
   Sprint 3 section marked **DONE** with date, commit SHAs, and a
   one-paragraph retro.
5. [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) entries SDD-032 and
   SDD-018 status updated to **DONE** with commit SHAs. SDD-033 either
   DONE if pulled into F-09 close-out or explicitly carried forward
   with a note.
6. If any ADR was drafted in F-10 (SDD-018 lifecycle amendment -- new
   Article XII or Article X amendment), it is committed under
   `docs/ADR/` and **approved by the owner** before any
   `constitution/**` edit.
7. `exec/state.md` regenerated via
   `python spec-driven-development/cli/state_builder.py`.
8. **Owner has explicitly approved the close before any close commit
   is pushed.** This is **NOT** inferred from a green test suite -- the
   F-11 session must request approval from the owner via the EM and
   wait for an explicit ratification before pushing the close commit
   chain to `origin/master`. The Option 3 hybrid precedent established
   on 2026-06-08 (Sprint 6 close required owner ratification at commit
   `6c70e30` *after* the close commit at `4a6941c`) is the model:
   close-commit-then-ratify is the floor, but for Sprint 7 the
   ratification request happens **before** the push, not after.
9. **`SPRINT-08-KICKOFF.prompt.md` authored** if PI-5 Sprint 4 is ready
   to start (PI-5 Sprint 4 = SDD-015 + SDD-022; ADO/GitHub Issues sync +
   model-upgrade discipline). If Sprint 8 is not ready, append an
   explicit "deferred to next session" note to the Sprint 7 close block
   and tell the owner.

---

## 5. Reporting

Append to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### Sprint 7 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); SW Dev + Developer worker owned F-09 (implementation only); PM + Architect owned F-10 (SDD-018 CLARIFY -> TASKS); SW Dev + workers owned F-11 (SDD-018 IMPLEMENT -> sprint close)
- Features completed: F-09, F-10, F-11
- Commits: <list>
- Tests: 259 -> N
- Validation: SDD-032 7/7 REQUIRED + 2/2 OPTIONAL; SDD-018 N/N REQUIRED
- ADRs: <list any drafted in F-10, or "none">
- PI-5 status: ACTIVE; Sprint 3 closed; 2 sprints remaining (Sprint 4 = SDD-022 + SDD-015; Sprint 5 = SDD-021 + SDD-023 + SDD-025)
- SDD-032: DONE (4 deferred R-items from Sprint 6 fully closed: SDD-019.R7 + SDD-019.R8 + SDD-020.R6 + SDD-020.R8; lock surface preserved against commits 524872b + 8eb564d)
- SDD-018: DONE (UI Lifecycle Variant lifecycle: CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> QA -> RETRO complete)
- SDD-033: <DONE if pulled in | carried forward with reason>
- PI-4 carry-over (domain-skill annotations, GH Actions Node.js bump): <DONE | carried forward>
- Article XI live contention test: <observed behavior summary from F-10 when SDD-018 entered CLARIFY>
- Owner ratification: <commit SHA of ratification stamp + date>
- Notes: <one paragraph -- what shipped, what was learned about the relaxed-Article-X variant in practice, the dedup scanner's first cross-feature run during SDD-018 CLARIFY, anything Sprint 8 needs to know>
- Next: PI-5 Sprint 4 = ADO/GitHub Bridge + Model Upgrade Discipline (SDD-022 + SDD-015). Kickoff prompt: <file or "not yet authored -- owner to request from EM">
```

---

## 6. Do NOT do

- Do NOT start any F-## before HARD PREREQUISITE is met (all six checks).
- Do NOT edit the SDD-032 spec dir
  ([`../specs/2026-06-09-sprint-6-completion/`](../specs/2026-06-09-sprint-6-completion/))
  in this kickoff session. All four artifacts are LOCKED at scaffold
  (commit `b005e66`); F-09 implements against them without modification.
- Do NOT scaffold the SDD-018 spec dir in this kickoff session. That is
  F-10's territory -- F-10 scaffolds from scratch in a fresh session.
- Do NOT defer any REQUIRED item from Sprint 7's close. The owner
  ratified the no-silent-slip precedent on 2026-06-08 (Option 3 hybrid).
  If a REQUIRED item cannot close, the feature does not close --
  escalate to the owner via the EM before any close commit lands.
- Do NOT touch `constitution/**` without an ADR (Article VIII). If
  SDD-018 CLARIFY confirms an amendment is needed (Article X relaxation
  or new Article XII), the ADR is drafted in F-10 and routed to the
  owner before the constitution edit. The edit itself never happens in
  F-10 or F-11 without explicit owner approval after reading the ADR.
- Do NOT add PyYAML or any other third-party dependency to `cli/**`
  (Article V).
- Do NOT push a Sprint 7 close commit without explicit owner approval.
  Close criterion #8 requires the approval **before** the push, not
  inferred from a green test run or a clean schema_lint.
- Do NOT promote anything to a branch other than `origin/master`.
- Do NOT close PI-5 in this sprint. Sprint 7 closes **PI-5 Sprint 3**
  only. Two more sprints (Sprint 8 and Sprint 9) remain in PI-5.
- Do NOT start Sprint 8 in this session. It runs in its own fresh
  session using `SPRINT-08-KICKOFF.prompt.md` (which F-11 authors if
  Sprint 4 is ready, or defers if not).
