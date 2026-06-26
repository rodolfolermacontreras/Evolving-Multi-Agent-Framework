# SPRINT 14 KICKOFF -- PI-7 Sprint 1 / Detach + Orchestration Maturity

You are leading **Sprint 14**, which is **PI-7 Sprint 1** and the first sprint
of PI-7 ("Hardening + Orchestration Maturity"). This is the highest-trust,
demo-first slice: a teammate should be able to clone the repo and run it on a
clean machine, the governance docs should agree with themselves, and the
orchestration layer should grow up (a sprint-scoped Executive Manager + plain
human-facing language). Your job is to ship three features and leave PI-7 ready
to continue into Sprint 15:

1. **SDD-043** -- Two-tier Executive Manager: a NEW sprint-scoped "Sprint EM"
   agent that knows it reports up to the project EM at sprint close, routes
   feature work to PM / Architect / SW Dev, and CANNOT create sprints or PIs
   (it may only SUGGEST to the project EM). Constraints live in the agent
   IDENTITY file, not just the kickoff prompt. This likely needs an ADR
   (two-tier EM model) and MAY touch `constitution/principles.md` Article II
   (a Level-2 constitution edit -- ADR + recorded owner approval + version bump).
2. **SDD-044** -- Plain-language human-facing communication discipline: extend
   the `em-communication-discipline` skill from EM-only to ALL human-facing
   principals/EMs. Human-facing output (status, progress, questions to the
   owner) must be SHORT, PLAIN, to the point; agent-to-agent detail stays
   allowed. This is a SKILL amendment, not a constitution edit.
3. **SDD-045** -- Detach (audit epic, spec source
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)):
   A-1 (stop committing `fleet.db` -- gitignore + `git rm --cached` + setup
   creates a fresh empty ledger), A-4 (one setup command, clone -> productive),
   A-5 (`doctor` / health check), A-6 (origin-token + identity lint), B-3
   (governance consistency -- RULES.md and principles.md agree on the article
   range). CLARIFY assigns per-item SDD-IDs.

Do NOT pull in any Sprint 15/16/17 work: **SDD-046** (B-1/B-2/B-4 make-promises-
true), **SDD-047** (A-2/A-3/D-1/D-3 de-author), and **SDD-048** (C-1/C-2/C-3/D-2
maintainability) are later PI-7 sprints and must not be started here. Do NOT
touch Azure decommission (SDD-035). PI-7 CLOSE is a separate, owner-approved
decision taken AFTER Sprint 17 -- closing Sprint 14 does not close PI-7.

You are the **Sprint Executive Manager** for this kickoff once SDD-043 ships;
until then you run as the project Executive Manager acting for a single sprint.
PM + Architect own CLARIFY/SPEC/PLAN/TASKS for all three features. The Principal
Software Developer owns implementation, QA, and the Sprint 14 close.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 14 must not start until all checks are true:

1. **PI-6 is closed and pushed at `4ad0521`.** Confirm HEAD / `origin/master`
   is at commit `4ad0521`, that [`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md)
   marks PI-6 **CLOSED**, and that
   [`../sprints/PI-7/CURRENT_PI.md`](../sprints/PI-7/CURRENT_PI.md) exists,
   marks PI-7 **ACTIVE**, and names Sprint 14 as the first PI-7 sprint.
2. **Tests are green at the PI-6 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **481 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
4. **SDD-043, SDD-044, and SDD-045 are filed and allocated to Sprint 14.**
   Confirm those three rows in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md)
   (under "### PI-7 Hardening Bundle (filed 2026-06-26)") are OPEN (not DONE)
   and allocated to PI-7 Sprint 14.
5. **SDD-046, SDD-047, and SDD-048 remain allocated to Sprints 15/16/17.**
   Confirm none of them is pulled into Sprint 14.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   exists; SDD-045's `validation.md` is built from its Part A (A-1/A-4/A-5/A-6)
   and B-3 "Acceptance" blocks.
7. **Owner has approved the Sprint 14 start** (the first PI-7 hardening sprint).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 14 on a
red test baseline (< 481), an unpushed/mismatched PI-6 (not at `4ad0521`), a
backlog that accidentally closed SDD-043/044/045 or pulled in the later PI-7
epics, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 14 in isolated feature sessions or EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property, per the
   SDD-039 wording shipped in PI-6).
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 14 ships **three features** that make the framework demonstrably a team
tool and mature its orchestration: a teammate can clone-and-run on a clean
machine (SDD-045), the governance docs stop contradicting themselves (B-3 inside
SDD-045), a single-sprint session runs under a sprint-scoped Executive Manager
that cannot invent sprints/PIs (SDD-043), and every human-facing principal
speaks in short plain language (SDD-044).

### Scope

- **SDD-043 (F-34)**: add a new `.github/agents` Sprint EM agent with
  identity-level scope constraints (reports up to the project EM; routes to
  PM/Architect/SW Dev; cannot create sprints/PIs, only suggest); author an ADR
  for the two-tier EM model; update the SPRINT-NN kickoff template to activate
  the Sprint EM (not the project EM). Any `constitution/principles.md` Article II
  reference change is Level-2 (ADR + recorded owner approval + version bump).
- **SDD-044 (F-34, paired)**: amend the `em-communication-discipline` skill so
  it applies to ALL human-facing principals/EMs (short plain status/progress/
  questions; agent-to-agent detail allowed). Skill amendment only.
- **SDD-045 (F-35)**: the Detach audit epic -- A-1 (gitignore `fleet.db` +
  `git rm --cached` + setup creates a fresh empty ledger), A-4 (one setup
  command), A-5 (`doctor` / health check), A-6 (origin-token + identity lint),
  B-3 (RULES.md article range == principles.md). CLARIFY assigns per-item
  SDD-IDs, each with its own `validation.md` from the audit Acceptance block.
- **Prompts/docs in scope**: the SDD-043/044/045 spec dir artifacts, the SDD-043
  ADR, the per-item SDD-045 validations, the Sprint 14 close block.

### Explicit exclusions

- **SDD-046** (B-1/B-2/B-4), **SDD-047** (A-2/A-3/D-1/D-3), and **SDD-048**
  (C-1/C-2/C-3/D-2) are later PI-7 sprints. They are NOT in Sprint 14.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 14 scope.
- **PI-7 close**: closing PI-7 is a separate owner-approved decision after the
  Sprint 17 close. Sprint 14 leaves PI-7 continuing; it does not close it.
- **Constitution edits beyond the SDD-043 Article II reference**: the ONLY
  permitted `constitution/**` change is the SDD-043 Article II reference (if
  CLARIFY confirms it is needed) and the B-3 article-range consistency fix in
  RULES.md/principles.md -- each only with an ADR (where applicable) + recorded
  owner approval + version bump. No other constitution edits.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-34: SDD-043 + SDD-044 CLARIFY -> ADR (SDD-043) -> SPEC -> PLAN -> TASKS | PM + Architect (design + ADR); SW Dev (apply) | Orchestration maturity is foundational and small. Author the two-tier-EM ADR and get recorded owner approval BEFORE any `constitution/principles.md` Article II change. SDD-044 (skill amendment) pairs naturally -- both are orchestration hygiene and touch no shared code with SDD-045. |
| 2 | F-35: SDD-045 CLARIFY -> SPEC (per-item validation.md) -> PLAN -> TASKS | PM + Architect (design); SW Dev + workers (impl) | The Detach epic. CLARIFY assigns per-item SDD-IDs (A-1/A-4/A-5/A-6/B-3) and builds each `validation.md` from the audit Acceptance blocks. A-1 changes `.gitignore` + `git rm --cached fleet.db` (owner-visible); setup must create a fresh empty ledger so `doctor` and the dashboard still find a DB. |
| 3 | F-36: SDD-043 + SDD-044 + SDD-045 IMPLEMENT + QA | SW Dev + workers | Implement after both designs lock. The Sprint EM agent, the skill amendment, and the Detach items land with real-run evidence per `validation.md`. |
| 4 | F-37: Sprint 14 close | Sprint EM + SW Dev | Close Sprint 14, regenerate state, request owner pre-push approval, mark SDD-043/044/045 (and per-item IDs) DONE, and record PI-7 as continuing into Sprint 15. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces
a file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `cli/state_builder.py`, `cli/fleet.py`, `cli/schema_lint.py`,
`constitution/**`, the kickoff template, generated exec surfaces, or shared spec
artifacts -- force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- SDD-043 Sprint EM tier and naming

Lock the agent's name and tier. Default recommendation: a sprint-scoped
"Sprint Executive Manager" that is NOT a new "principal" tier but a scoped
orchestrator under the project EM. Decide the exact identity-level constraints
(reports up at close; routes to PM/Architect/SW Dev; cannot create sprints/PIs,
may SUGGEST only) and confirm they live in the agent file, not just the kickoff.

### Q-B -- SDD-043 constitution Article II impact

Decide whether the two-tier EM model requires a `constitution/principles.md`
Article II reference change. Default recommendation: prefer the ADR + agent file
+ kickoff-template change FIRST; touch the constitution only if Article II
materially names the EM model. If a constitution edit is needed, it is Level-2:
author the ADR, get recorded owner approval, then edit and bump the version.

### Q-C -- SDD-043 kickoff-template activation

Confirm the SPRINT-NN kickoff template activates the Sprint EM (not the project
EM) going forward, and decide whether existing kickoff prompts are retrofitted
(recommend: template change applies to FUTURE sprints; do not rewrite shipped
kickoffs in this sprint).

### Q-D -- SDD-044 skill scope and wording

Lock how the `em-communication-discipline` skill is extended to all human-facing
principals/EMs. Default recommendation: amend the existing skill's applicability
(not a new skill) so the short-plain-language rule binds every principal/EM in
human-facing output, with agent-to-agent detail explicitly still allowed.

### Q-E -- SDD-045 A-1 ledger detachment + fresh-DB-on-setup

Confirm the A-1 mechanism: add `*.db` / `*.db-wal` / `*.db-shm` (or the specific
`ledger/fleet.db`) to `.gitignore`, `git rm --cached` the tracked DB, and have
the setup path create a fresh empty ledger from `ledger/schema.sql` (an
`init_ledger` step). Confirm the dashboard and `doctor` still find a DB on a
clean clone. This is owner-visible (it changes what is tracked) -- surface it.

### Q-F -- SDD-045 A-4/A-5 setup + doctor shape

Decide the one setup command (recommend a `bootstrap.py setup` subcommand and/or
a `make setup` wrapper) and the `doctor` / health check (recommend a
`bootstrap.py doctor` that runs schema lint + tests-presence + ledger
reachability + origin-token/identity lint and reports green or names the
failure). Confirm stdlib-only (Article V): argparse, sqlite3, pathlib only.

### Q-G -- SDD-045 A-6 + B-3 lint and governance consistency

Confirm the A-6 origin-token + identity lint (flags hardcoded owner name +
origin-project tokens in generic files) and the B-3 fix (RULES.md and
principles.md agree on the article range -- e.g. RULES.md "Articles I-X" ->
"Articles I-XII"). Decide whether A-6 runs inside `doctor` and/or schema_lint.
The B-3 RULES.md edit is a docs fix; if it touches `constitution/**` wording it
is owner-gated.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` uses argparse, sqlite3, pathlib, json,
  sys, os only. The `setup` / `doctor` / lint additions add NO third-party
  Python dependency.
- **Article X locked render functions are immutable.** Do NOT edit `render_html`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or
  `load_decisions`. Sprint 14 does not touch the dashboard renderer; any state
  regeneration is read-only. `TestS1FootprintLockGuard` golden SHA-256 hashes
  must still PASS.
- **Constitution edits are gated.** The only permitted `constitution/**` changes
  are the SDD-043 Article II reference (if CLARIFY confirms it is needed) and the
  B-3 article-range consistency, each only after an ADR (where applicable) +
  recorded owner approval + a version bump. No other constitution edits.
- **Ledger detachment is owner-visible.** A-1 changes what git tracks
  (`git rm --cached fleet.db` + `.gitignore`). Surface it to the owner; it is a
  Level-2-adjacent change. Setup must create a fresh empty ledger so nothing
  downstream breaks on a clean clone.
- **Spec source is authoritative but stale-checked.** Build each SDD-045 per-item
  `validation.md` from the audit "Acceptance" block, but verify each "Evidence"
  line against the live repo before acting (the plan was written against an
  earlier `master`). If an item is wrong on inspection, file a clarification and
  surface it -- do not silently drop it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044, owner rule 2026-06-26).** All
  human-facing output in this sprint (status, progress, questions to the owner)
  is short and plain; agent-to-agent detail may stay detailed.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 14 closes only when all are true:

1. **SDD-043 implemented**: a new `.github/agents` Sprint EM agent exists with
   identity-level scope constraints (reports up; routes to PM/Architect/SW Dev;
   cannot create sprints/PIs); the two-tier-EM ADR is committed; the SPRINT-NN
   kickoff template activates the Sprint EM; any Article II change is owner-
   approved and version-bumped.
2. **SDD-044 implemented**: the `em-communication-discipline` skill applies to
   ALL human-facing principals/EMs with the short-plain-language rule explicit.
3. **SDD-045 implemented**: `fleet.db` is gitignored + removed from tracking and
   setup creates a fresh empty ledger (A-1); one setup command takes a clone to
   productive (A-4); a `doctor` / health check reports green or names the failure
   (A-5); an origin-token + identity lint exists (A-6); RULES.md and
   principles.md agree on the article range (B-3).
4. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual/tone checks checked at close.
5. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 481
   passed, 2 skipped (the PI-6 close baseline), and grows with the new tests.
6. Schema lint clean (exit 0).
7. Article X lock held (`TestS1FootprintLockGuard` PASS).
8. **Clone-and-run smoke**: on a fresh checkout, the one setup command produces a
   clean lint-passing test-passing tree with a fresh empty ledger, and `doctor`
   reports green (or names the failure on purpose).
9. SDD-043, SDD-044, SDD-045 (and the per-item SDD-IDs) marked DONE in BACKLOG
   with evidence.
10. Owner pre-push approval recorded before any push.
11. **PI-7 recorded as continuing into Sprint 15.** The PI-7 CLOSE itself is a
    SEPARATE owner-approved decision taken after Sprint 17; Sprint 14 does not
    close PI-7.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 14 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead); PM + Architect owned design + ADR; SW Dev + workers owned implementation and close
- Features completed: F-34, F-35, F-36, F-37
- Commits: <commit SHAs>
- Tests: 481 -> <N> (>= 481 required)
- Schema lint: clean
- Validation: SDD-043 <r>/<r> + SDD-044 <r>/<r> + SDD-045 per-item (A-1/A-4/A-5/A-6/B-3) <r>/<r> REQUIRED + manual checks
- ADRs: <two-tier EM model ADR> (required); <C-2-style ADRs not in this sprint>
- principles.md version: <old> -> <new> (only if SDD-043 Article II change landed)
- Per-item SDD-IDs assigned for SDD-045: <list>
- PI-7 status: ACTIVE -> continues into Sprint 15
- SDD-043: DONE (Sprint EM agent + ADR + kickoff-template activation)
- SDD-044: DONE (plain-language comms across all human-facing principals)
- SDD-045: DONE (A-1 ledger detach + A-4 setup + A-5 doctor + A-6 lint + B-3 governance consistency)
- Clone-and-run smoke: PASS (fresh setup -> clean tree + fresh ledger; doctor green)
- Deferred to later PI-7 sprints: SDD-046 (S2), SDD-047 (S3), SDD-048 (S4); SDD-035 out-of-band
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 14 lessons>
- Next: SPRINT-15 kickoff (PI-7 Sprint 2 -- Make promises true: SDD-046 B-1/B-2/B-4)
```

---

## 7. Do NOT do

- Do NOT close PI-7 automatically. PI-7 CLOSE is a separate owner-approved
  decision taken after Sprint 17 closes.
- Do NOT pull in SDD-046, SDD-047, or SDD-048 -- those are Sprints 15/16/17.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT edit the Article X locked render functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`).
- Do NOT edit `constitution/**` except the SDD-043 Article II reference (if
  CLARIFY confirms it is needed) and the B-3 article-range consistency, each only
  with an ADR (where applicable) + recorded owner approval + version bump.
- Do NOT add third-party dependencies; the setup / doctor / lint additions are
  stdlib-only.
- Do NOT delete the ledger history destructively; A-1 is `git rm --cached`
  (stop tracking) + gitignore + fresh-DB-on-setup, not a history rewrite.
- Do NOT silently drop a SDD-045 audit item; if an "Evidence" line no longer
  matches the repo, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-043/044/045 spec dirs here -- F-34/F-35 do that inside
  the Sprint 14 working sessions.
