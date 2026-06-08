# SPRINT 8 KICKOFF -- PI-5 Sprint 4 / ADO-GitHub Bridge + Model Upgrade Discipline

You are leading **Sprint 8**, which is **PI-5 Sprint 4**. Your job is to
ship **SDD-022** (ADO / GitHub Issues sync bridge -- `/taskstoissues`
pattern, GitHub-first with ADO fast-follow) and **SDD-015** (model
upgrades as Level-2 decisions with regression-test branch + A/B + cost
analysis). Both must close DONE with full validation contracts; per the
Sprint 7 no-deferral precedent (owner direction 2026-06-08, Option 3
hybrid; reinforced at Sprint 7 close), no REQUIRED item from this sprint
may be silently slipped.

You are the **Principal Executive Manager** for this kickoff. The PM and
Architect own F-12 (SDD-022 CLARIFY -> SPEC -> PLAN -> TASKS) and F-13
(SDD-015 CLARIFY -> SPEC -> PLAN -> TASKS). The SW Dev and dispatched
workers own F-14 (joint implementation). The SW Dev owns F-15 (sprint
close + QA + retro + SPRINT-09 authoring if Sprint 5 is ready).

---

## HARD PREREQUISITE -- STOP IF NOT MET

This sprint **must not start** until **all six** of the following are true:

1. **Sprint 7 marked CLOSED** in
   [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
   (Sprint 3 section status = `CLOSED 2026-06-08`; close commit
   `22b72d8` plus Article XII landing commit `55b05cb` both present;
   owner pre-push ratification stamp present once collected by EM).
2. **Sprint 7 close block present** in
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) with the
   F-10 (pass 1 + pass 2), F-11, and `### Sprint 7 -- CLOSED` entries
   appended. Owner ratification of Article XII (commit `55b05cb`,
   2026-06-08) and the pre-push approval stamp are both recorded.
3. **Tests >= 305** baseline (the Sprint 7 close baseline preserved).
   Verify with
   `python -m pytest spec-driven-development/ --tb=no -q`. 2 skipped
   (platform-conditional) is normal and not a regression.
4. **BACKLOG entries present and correct** in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) -- specifically:
   SDD-032 reads **DONE 2026-06-09**; SDD-018 reads **DONE 2026-06-08**;
   SDD-019, SDD-020, SDD-027 read **DONE 2026-06-09** (R-items closed
   via SDD-032 chain); SDD-022 (P2) is filed for PI-5 Sprint 4 with
   CLARIFY status; SDD-015 (P1) is filed for PI-5 Sprint 4.
5. **SDD-022 and SDD-015 spec dirs are EITHER pre-scaffolded OR
   explicitly authored in F-12 pass 1 / F-13 pass 1.** Sprint 7 ran
   F-09 against a pre-scaffolded spec dir (`b005e66`); F-10 scaffolded
   from scratch inside its own session. Either pattern is acceptable
   for Sprint 8 -- the EM decides per-feature at dispatch time. If
   pre-scaffolding is chosen, do it in a separate `chore(sprint-8):
   scaffold ...` commit before F-12 starts; if from-scratch, F-12 and
   F-13 each open with the scaffold step.
6. **Owner has explicitly approved Sprint 8 start.**

Verify all six before any F-## prompt below is loaded. If any fail, STOP
and surface the failure to the owner. Do not start Sprint 8 on an
unratified Sprint 7 close, on a missing pre-push approval stamp, or on
an unapproved kickoff.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above (six checks).
3. Execute the sprint sequence below. **Each F-## runs in its own fresh
   chat session** (Article VII: one feature, one session). The Sprint 7
   precedent of EM-routed multi-pass dispatch (where the owner
   explicitly authorized overriding "fresh session" for productivity --
   see Sprint 6 + Sprint 7 retros) is documented and available; if you
   judge a consolidated execution is warranted, route to the owner via
   the EM and obtain explicit authorization before collapsing sessions.
   The default is four sessions (F-12, F-13, F-14, F-15).
4. Append a sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) when DONE.

---

## 1. Sprint goal

Sprint 8 has **two outcomes** (both must ship):

1. **Ship SDD-022 (ADO / GitHub Issues sync bridge).** Scott Epperly
   (2026-06-02 meeting) named this as the single gap keeping his team
   from adopting the framework -- they live in ADO and need work items
   synced. BACKLOG line: "ADO / GitHub Issues sync bridge --
   `/taskstoissues` pattern (GitHub-first, ADO fast-follow)" at P2 / H
   reach. The framework's `tasks.md` -> external issue tracker
   round-trip must work for GitHub Issues first; ADO can be a clean
   fast-follow adapter behind the same interface.
2. **Ship SDD-015 (model-upgrade discipline).** BACKLOG line: "Model
   upgrades as Level-2 decisions w/ regression-test branch + A/B + cost
   analysis." A `docs/MODEL-UPGRADE-PROTOCOL.md` exists and is
   referenced from `constitution/decision-policy.md`; any model swap
   (Claude major version bump, GPT swap, model-vendor change) goes
   through Level-2 routing with a regression-test branch, an A/B run
   on a representative sprint workload, and a cost-per-token + quality
   delta written into the friction analysis. Unblocked by SDD-014
   (Friction Analysis template; shipped PI-4 Sprint 3 commit `85b39be`).

Per owner direction 2026-06-08 (Option 3 hybrid; reinforced at Sprint 7
close): **NO further deferral of REQUIRED items from this sprint's
close, period.** If a REQUIRED item cannot close in F-14, F-14 does not
close -- it stays in-flight or escalates to the owner via the EM. The
Sprint 7 SDD-032 completion bundle precedent is now the floor.

### Scope

- **Primary scope (P1/P2, must ship)**: SDD-022 (ADO/GitHub bridge),
  SDD-015 (model-upgrade discipline).
- **Capacity housekeeping (P3, if room)**: SDD-034 (dedup heuristic
  upgrade -- content-shingle for spec.md problem statements, filed
  2026-06-08 from F-10 pass 1 Article XI live contention test). May
  be pulled into F-14 close-out if capacity permits; otherwise it
  remains unscheduled.
- **PI-4 carry-along (still outstanding, if room)**: domain-skill
  annotations (mark `.github/skills/domain/*` as reference examples
  not framework essentials); GitHub Actions Node.js bump (advance
  `actions/checkout` + `azure/login` past Node 16/18 deprecation in
  `.github/workflows/`). Both deferred from PI-4 Sprint 4 -> PI-5
  Sprint 2 -> Sprint 7 with no take-up; if Sprint 8 finishes early,
  pull them in. Neither is a blocker for Sprint 8 close.

---

## 2. Sprint sequence

| Order | Feature | File | Owner | Why this order |
|-------|---------|------|-------|----------------|
| 1 | F-12: SDD-022 CLARIFY + SPEC + PLAN + TASKS | (author at sprint start) | Principal Product Manager + Principal Architect | SDD-022 is the larger and more uncertain of the two. CLARIFY is expected to be HEAVY (see "Likely Level-1 CLARIFY surfaces" below). The bridge must land as a stable model that SDD-015's MODEL-UPGRADE-PROTOCOL.md can reference (e.g., "this is how a model swap is announced and tracked across both issue trackers"); doing SDD-022 first means F-13's protocol can cite a real working bridge instead of a hypothetical one. |
| 2 | F-13: SDD-015 CLARIFY + SPEC + PLAN + TASKS | (author at sprint start) | Principal Product Manager + Principal Architect | SDD-015 is bounded (model-upgrade discipline is conceptually clear -- decision-policy.md + MODEL-UPGRADE-PROTOCOL.md + a checklist + a CI/A-B harness). CLARIFY will be lighter than F-12. **The EM may authorize bundling F-12 + F-13 CLARIFY into a single session** if F-12 CLARIFY closes faster than expected and the owner approves the consolidated execution per the Sprint 6/Sprint 7 precedent. The default split is two sessions. |
| 3 | F-14: SDD-022 + SDD-015 IMPLEMENT + QA | (author after F-12 + F-13 lock) | Principal Software Developer + dispatched workers | Depends on both F-12 and F-13's locked validation contracts. Implementation may use fleet dispatch IF the file footprints of the two specs are disjoint at TASKS time; otherwise linear single-session execution per the Sprint 5/6/7 precedents. SW Dev decides at task-decomposition time. |
| 4 | F-15: Sprint 8 close + RETRO + SPRINT-09 authoring | (author after F-14 close) | Principal Software Developer + EM coordination | Closes **PI-5 Sprint 4**, not PI-5 itself (one sprint remains: PI-5 Sprint 5 = SDD-021 + SDD-023 + SDD-025). Authors `SPRINT-09-KICKOFF.prompt.md` if Sprint 5 is ready; otherwise defers and notes "owner to request from EM." |

### Likely Level-1 CLARIFY surfaces for F-12 (SDD-022)

The SDD-022 BACKLOG row is intentionally terse ("ADO / GitHub Issues
sync bridge -- `/taskstoissues` pattern (GitHub-first, ADO fast-follow)").
F-12 CLARIFY will likely surface several Level-1 design decisions that
the owner must resolve before SPEC. Surface these explicitly in the
CLARIFY question battery:

- **Q-A: Direction of authority.** Is `tasks.md` (in-repo) the source of
  truth and the issue tracker a read-only mirror? Or is the issue
  tracker authoritative and `tasks.md` regenerated from it? Or
  bidirectional with conflict resolution? Scott's "live in ADO" framing
  suggests bidirectional, but the framework's spec-driven contract
  suggests `tasks.md` as source of truth.
- **Q-B: Which issue system is canonical for v1.** BACKLOG says
  "GitHub-first, ADO fast-follow." Confirm: is the v1 close criterion
  only that GitHub Issues round-trips? Or must ADO also work at v1?
- **Q-C: Sync cadence.** On-demand via `/taskstoissues` slash command?
  On every commit-msg hook? On every state-dashboard refresh? GitHub
  webhook subscription on the host side?
- **Q-D: Conflict resolution semantics.** If a `tasks.md` row says
  `status: done` and the corresponding GitHub Issue is reopened (or
  vice versa), who wins? Last-writer-wins? Always tasks.md? Always
  issue tracker? Surface to user?
- **Q-E: What triggers a sync.** Spec-dir change? `/triage` invocation?
  `/tasks` close? An explicit `/taskstoissues` slash command?
- **Q-F: Identity mapping.** How does a `tasks.md` task ID
  (e.g., `T-022-04`) map to a GitHub Issue number? Append issue number
  to task row? Store in a separate `cli/issue-mapping.json`? Use a
  ledger table?
- **Q-G: Auth model.** GitHub PAT in env var? GitHub App? ADO PAT?
  Where do these live for the framework's CI, the host's CI, and the
  developer's local machine?
- **Q-H: Scope of fields synced.** Title only? Title + description?
  Acceptance criteria? Assignee? Labels (and which labels)?
- **Q-I: Dependencies.** Stdlib-only is hard for HTTP + JSON; do we
  amend Article V to permit `urllib.request` only (already stdlib)? Or
  do we need to add `requests` (third-party) and amend Article V via
  ADR? GitHub REST API works fine with `urllib`; ADO REST API also
  works with `urllib`. **PM + Architect: lean to urllib-only and
  preserve Article V.**

### Likely Level-1 CLARIFY surfaces for F-13 (SDD-015)

SDD-015 is more bounded but still has a few Level-1 surfaces:

- **Q-J: Trigger definition.** What counts as a "model upgrade"? Major
  version bump (Claude 4.7 -> Claude 5.0)? Any version bump?
  Vendor swap (Claude -> GPT)? Model role change (one agent
  switches model)? Surface explicitly so the protocol is not
  ambiguous.
- **Q-K: Regression-test branch shape.** A dedicated long-lived branch
  (`model-upgrade/<old>-to-<new>`)? Or a per-upgrade ephemeral
  branch + tag? What sprint workload is "representative" -- last 3
  sprints replayed? A canonical fixture?
- **Q-L: A/B harness implementation.** New CLI subcommand (`cli/ab.py`
  or `cli/model_upgrade.py`)? Or a `tests/` harness? Owner gates the
  decision -- but per Article V it must be stdlib-only.
- **Q-M: Cost-delta capture.** Token-per-task baseline? Vendor pricing
  table maintained in `docs/MODEL-UPGRADE-PROTOCOL.md`? Cost A/B
  reported in the Friction Analysis section of the Level-2 decision?
- **Q-N: Quality-delta capture.** Pass/fail of the regression test
  suite? A diff in commit message quality? A diff in spec-quality
  reviewer scores? Owner must define "quality" measurably.

### Coordination notes

- F-12, F-13, F-14, F-15 run **sequentially**. Each must close cleanly
  before the next session starts. **Exception**: if the EM judges F-12
  + F-13 can be bundled into a single CLARIFY session and the owner
  approves (per Sprint 6/Sprint 7 precedent), that is permitted.
- **F-12 must close with all REQUIRED items checked** in
  `specs/<date>-ado-github-bridge/validation.md` before F-14 starts.
  Per owner direction 2026-06-08 (Option 3 hybrid; reinforced at
  Sprint 7 close), **deferral of any REQUIRED item is explicitly
  prohibited from this sprint's close**.
- **F-13 must close with all REQUIRED items checked** in
  `specs/<date>-model-upgrade-discipline/validation.md` before F-14
  starts. Same rule.
- **Article XI lock contention is now LIVE.** Sprint 7 F-10 pass 1
  was the first real-world contention test (PASS -- gate fired
  correctly when SDD-018 entered CLARIFY; grandfather correctly
  excluded SDD-018; ledger event recorded). Sprint 8 will likely see
  **two specs queued at /clarify and /spec at various points** (F-12
  on SDD-022; F-13 on SDD-015). The priority-weighted FIFO queue
  (SDD-019.R7 closed in Sprint 7 commit `557b672`) is now the
  **binding rule for that contention**. F-12 holds the CLARIFY lock
  while F-13 waits in the queue (or vice versa, per EM dispatch
  order); the queue position is visible via
  `python spec-driven-development/cli/fleet.py lock status`.
- **SDD-022 may require an Article V amendment** if F-12 CLARIFY
  concludes that `urllib.request` is insufficient and a third-party
  HTTP library is required. If so, F-12 drafts the ADR (analogous to
  ADR-013 for Article XI, ADR-014 for Article XII) and routes it to
  the owner as a Level-2 decision via the EM. The constitution edit
  itself does NOT happen in F-12, F-13, or F-14 unless the owner
  explicitly approves it after reading the ADR. **PM + Architect:
  default lean is urllib-only, no amendment needed.**
- **SDD-015 will modify `constitution/decision-policy.md`** (not
  `principles.md`) to cross-reference the new
  `docs/MODEL-UPGRADE-PROTOCOL.md`. Per Article VIII, any
  `constitution/**` edit requires an ADR if it changes a principle;
  a cross-reference addition arguably does not (it adds a pointer,
  does not change a principle). F-13 must surface this explicitly in
  CLARIFY: ADR or no-ADR for this specific decision-policy.md edit.
- **SDD-034 (P3 doc/code carry-over)** may be pulled into F-14
  close-out if capacity permits. It is a dedup heuristic upgrade
  (content-shingle for spec.md problem statements) that closes the
  one known limitation surfaced in Sprint 7. Not a blocker; F-14
  decides.
- **Two PI-4 carry-overs** (domain-skill annotations, GitHub Actions
  Node.js bump) may also ride along. Neither has been pulled in for
  three sprints; F-14 decides per remaining capacity. If neither
  fits, they carry to Sprint 9 or beyond.

---

## 3. Hard constraints

- **Stdlib only** for any new CLI code (Article V). Likely touchpoints
  in F-14 are `cli/issues.py` or `cli/taskstoissues.py` (NEW, SDD-022),
  `cli/model_upgrade.py` or `cli/ab.py` (NEW, SDD-015 -- TBD per
  F-13 CLARIFY Q-L), prompt-file edits at
  `.github/prompts/taskstoissues.prompt.md` (NEW), and possibly
  `cli/fleet.py` extensions if the bridge writes to the ledger. All
  Python must remain `argparse` + `sqlite3` + `pathlib` + `json` +
  `sys` + `os` + `urllib.request` + `urllib.parse` + `urllib.error`
  only. No `requests`, no `httpx`, no `azure-devops` SDK, no
  `PyGithub`. If a CLARIFY round concludes otherwise, draft an ADR
  amending Article V and route to the owner.
- **No `constitution/**` edit without an ADR** (Article VIII).
  SDD-022 may require one (Article V amendment if `urllib` is
  insufficient); SDD-015 may require one (decision-policy.md
  cross-reference); both are surfaced in CLARIFY. The constitution
  edit happens only after explicit owner approval (Level-2 routing
  via the EM).
- **No host-project pollution.** SDD-027's protections (committed at
  `302bee5`; HOST-INTEGRATION.md docs at SDD-033) still bind any
  implementation work; SDD-022 must not write into host trees as
  part of any issue-sync artifact, and SDD-015 must not write into
  host trees as part of any A/B harness.
- **One feature, one session** (Article VII). F-12, F-13, F-14, F-15
  each run in their own fresh chat session. Do not collapse them into
  a single session unless the owner explicitly approves a consolidated
  execution (the Sprint 6/Sprint 7 precedent exists and is
  authorized-by-owner only).
- **NO REQUIRED-item deferral from Sprint 8 close** per owner direction
  2026-06-08 (Option 3 hybrid established the no-silent-slip
  precedent in writing) and Sprint 7 close precedent (where the
  precedent was honored -- SDD-032 closed 7/7 REQUIRED + 2/2 OPTIONAL,
  SDD-018 closed 16/16 REQUIRED + 3/3 OPTIONAL with the 2 unreached
  manual checks routed to the owner async, NOT silently deferred).
  If a REQUIRED item cannot close, the relevant feature does not close
  -- the EM routes to the owner before any close commit lands.
- **No push without explicit owner approval.** Sprint 7 close
  criterion #8 + the F-15 close commit must request approval from
  the owner via the EM and wait for an explicit ratification before
  pushing the close commit chain to `origin/master`.

---

## 4. Sprint close criteria

Sprint 8 closes DONE when **all nine** of the following are true:

1. **SDD-022 validation contract at 100% REQUIRED items checked** in
   `specs/<date>-ado-github-bridge/validation.md` (item count TBD --
   the contract is locked in F-12).
2. **SDD-015 validation contract at 100% REQUIRED items checked** in
   `specs/<date>-model-upgrade-discipline/validation.md` (item count
   TBD -- the contract is locked in F-13).
3. **Full test suite passes** with test count >= 305 (Sprint 7
   baseline) plus the new tests added in F-14.
4. [`../sprints/PI-5/CURRENT_PI.md`](../sprints/PI-5/CURRENT_PI.md)
   Sprint 4 section marked **DONE** with date, commit SHAs, and a
   one-paragraph retro (mirror the prose density of the Sprint 1,
   Sprint 2, and Sprint 3 retros already in the file).
5. [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) entries SDD-022
   and SDD-015 status updated to **DONE** with commit SHAs. SDD-034
   either DONE if pulled into F-14 close-out or carried forward with
   a note. PI-4 carry-over items either DONE or explicitly carried
   forward.
6. **If any ADR was drafted** in F-12 (Article V amendment for HTTP
   lib) or F-13 (decision-policy.md edit), it is committed under
   `docs/ADR/` and **approved by the owner** before any
   `constitution/**` edit.
7. `exec/state.md` regenerated via
   `python spec-driven-development/cli/state_builder.py`.
8. **Owner has explicitly approved the close before any close commit
   is pushed.** This is **NOT** inferred from a green test suite --
   the F-15 session must request approval from the owner via the EM
   and wait for an explicit ratification before pushing the close
   commit chain to `origin/master`. Sprint 6 close (`6c70e30`
   ratification AFTER push) -> Sprint 7 close (pre-push approval
   collected by EM at close) -> Sprint 8 close should now treat
   pre-push approval as the established floor.
9. **`SPRINT-09-KICKOFF.prompt.md` authored** if PI-5 Sprint 5 is
   ready to start (Sprint 5 = SDD-021 self-review + SDD-023 first-
   class user gates + SDD-025 stakeholder-pressure defense). If
   Sprint 9 is not ready, append an explicit "deferred to next
   session" note to the Sprint 8 close block and tell the owner.

---

## 5. Reporting

Append to [`../exec/sprint-progress.md`](../exec/sprint-progress.md):

```markdown
### Sprint 8 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM + Architect owned F-12 (SDD-022 CLARIFY -> TASKS); PM + Architect owned F-13 (SDD-015 CLARIFY -> TASKS); SW Dev + workers owned F-14 (joint implementation); SW Dev owned F-15 (sprint close + SPRINT-09 authoring)
- Features completed: F-12, F-13, F-14, F-15
- Commits: <list>
- Tests: 305 -> N
- Validation: SDD-022 N/N REQUIRED + N/N OPTIONAL; SDD-015 N/N REQUIRED + N/N OPTIONAL
- ADRs: <list any drafted in F-12 or F-13, or "none">
- PI-5 status: ACTIVE; Sprint 4 closed; 1 sprint remaining (Sprint 5 = SDD-021 + SDD-023 + SDD-025)
- SDD-022: DONE (ADO/GitHub Issues sync bridge: <one-sentence summary of canonical direction, sync cadence, conflict semantics, auth model>)
- SDD-015: DONE (model-upgrade discipline: docs/MODEL-UPGRADE-PROTOCOL.md + decision-policy.md cross-reference + A/B harness + cost/quality delta capture)
- SDD-034: <DONE if pulled in | carried forward with reason>
- PI-4 carry-over (domain-skill annotations, GH Actions Node.js bump): <DONE | carried forward>
- Article XI live contention observation: <how many CLARIFY queue contentions observed; whether the priority-weighted FIFO behavior matched expectations; any heuristic gaps surfaced for SDD-034 follow-up>
- Owner ratification: <commit SHA of ratification stamp + date; pre-push approval per Sprint 7 floor>
- Notes: <one paragraph -- what shipped, what Sprint 8 learned about external-system integration under stdlib-only discipline, the model-upgrade protocol's first dry-run if one was performed, anything Sprint 9 needs to know>
- Next: PI-5 Sprint 5 = Self-Review + Uniform Gates + Stakeholder Defense (SDD-021 + SDD-023 + SDD-025). Kickoff prompt: <file or "not yet authored -- owner to request from EM">
```

---

## 6. Do NOT do

- Do NOT start any F-## before HARD PREREQUISITE is met (all six
  checks).
- Do NOT pre-scaffold the SDD-022 or SDD-015 spec dirs without owner
  approval to do so as a separate `chore(sprint-8): scaffold ...`
  commit. The default (per Sprint 7 F-10) is that F-12 / F-13
  scaffolds from scratch in its own fresh session.
- Do NOT defer any REQUIRED item from Sprint 8's close. The owner
  ratified the no-silent-slip precedent on 2026-06-08 (Option 3
  hybrid) and Sprint 7 honored it. If a REQUIRED item cannot close,
  the feature does not close -- escalate to the owner via the EM
  before any close commit lands.
- Do NOT touch `constitution/**` without an ADR (Article VIII). If
  F-12 CLARIFY concludes Article V must be amended (third-party HTTP
  library required), the ADR is drafted in F-12 and routed to the
  owner before the constitution edit. If F-13 CLARIFY concludes
  decision-policy.md must be edited, the ADR-vs-no-ADR decision is
  surfaced explicitly in CLARIFY. The edit itself never happens in
  F-12, F-13, or F-14 without explicit owner approval after reading
  the ADR (or after explicit owner waiver of the ADR requirement for
  a pure cross-reference addition).
- Do NOT add `requests`, `httpx`, `PyGithub`, `azure-devops`, or any
  other third-party HTTP/issue-tracker dependency to `cli/**`
  (Article V). Use `urllib.request` + `urllib.parse` + `urllib.error`
  + `json` only.
- Do NOT push a Sprint 8 close commit without explicit owner
  approval. Close criterion #8 requires the approval **before** the
  push, not inferred from a green test run or a clean schema_lint.
- Do NOT promote anything to a branch other than `origin/master`.
- Do NOT close PI-5 in this sprint. Sprint 8 closes **PI-5 Sprint 4**
  only. One more sprint (Sprint 9 = PI-5 Sprint 5) remains in PI-5.
- Do NOT start Sprint 9 in this session. It runs in its own fresh
  session using `SPRINT-09-KICKOFF.prompt.md` (which F-15 authors if
  Sprint 5 is ready, or defers if not).
