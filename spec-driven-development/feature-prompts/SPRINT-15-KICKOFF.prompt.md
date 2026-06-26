# SPRINT 15 KICKOFF -- PI-7 Sprint 2 / Make promises true (ledger + checks + CI)

You are leading **Sprint 15**, which is **PI-7 Sprint 2** of PI-7 ("Hardening +
Orchestration Maturity"). Sprint 14 made the framework clone-and-run portable
and matured the orchestration layer. Sprint 15 is the credibility sprint: the
framework stops promising things it does not deliver. The ledger becomes
genuinely true, the rules that matter stop being honor-system prose and start
blocking on violation, and CI fires the checks for everyone on every push. Your
job is to ship one epic feature (SDD-046) and leave PI-7 ready to continue into
Sprint 16:

1. **SDD-046** -- Make promises true (audit epic, spec source
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   Part B): **B-1** (make the ledger true), **B-2** (turn high-payoff rules into
   blocking checks -- start with the TDD gate), **B-4** (one GitHub Actions CI
   workflow running the `doctor` set on push and PR). CLARIFY assigns per-item
   SDD-IDs, each with its own `validation.md` from the audit Acceptance blocks.

**The B-1 fork is already decided.** The owner ruled 2026-06-26 (via the project
Executive Manager): B-1 = **MAKE IT REAL** (audit Option 1), NOT retract the
claim. Mandatory dispatch logging becomes a REQUIRED close step. A feature or
sprint cannot be stamped DONE until its dispatch outcomes are in the ledger; the
`/qa` and `/retro` flows (or the close flow) write the rows; `doctor` warns if
the current PI has zero ledger rows. **Do NOT re-open this fork at CLARIFY.**
CLARIFY only refines HOW: where the close-gate check lives, and how logging
stays a one-liner so it adds no friction.

Do NOT pull in any Sprint 16/17 work: **SDD-047** (A-2/A-3/D-1/D-3 de-author)
and **SDD-048** (C-1/C-2/C-3/D-2 maintainability) are later PI-7 sprints and
must not be started here. Do NOT touch Azure decommission (SDD-035). PI-7 CLOSE
is a separate, owner-approved decision taken AFTER Sprint 17 -- closing Sprint 15
does not close PI-7.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent -- the new
sprint-scoped EM shipped in Sprint 14 (SDD-043 / ADR-020). It is NOT the project
Executive Manager.

- In the fresh session, **activate the `sprint-executive-manager` agent**
  ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md)),
  not `principal-executive-manager`.
- The Sprint EM coordinates exactly this one sprint. It **routes** feature work
  to the Principal Product Manager, Principal Architect, and Principal Software
  Developer, synthesizes their answers, and surfaces escalations. It makes NO
  product, technical, or implementation decisions itself (Level 0).
- The Sprint EM **cannot create sprints or PIs** -- it may only SUGGEST to the
  project EM. At sprint close it produces a sprint-close summary and **reports it
  UP to the project Executive Manager**, who folds it into project-wide state and
  owns any project-wide human conversation.
- Human-facing output from the Sprint EM is **short and plain** (SDD-044). Save
  the detail for agent-to-agent handoffs.

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-046. The Principal
Software Developer owns implementation, QA, and the Sprint 15 close (reporting up
to the project EM through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 15 must not start until all checks are true:

1. **Sprint 14 is CLOSED and pushed.** Confirm Sprint 14 (PI-7 Sprint 1) closed
   at commit `ecd13b3` (with the backfill at head `7fe1e39`), that
   [`../sprints/PI-7/CURRENT_PI.md`](../sprints/PI-7/CURRENT_PI.md) marks PI-7
   **ACTIVE** and names Sprint 15 as the next sprint, and that SDD-043, SDD-044,
   and SDD-045 are marked DONE in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md).
2. **Tests are green at the Sprint 14 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **501 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
4. **SDD-046 is filed and allocated to Sprint 15.** Confirm the SDD-046 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-7 Sprint 15.
5. **SDD-047 and SDD-048 remain allocated to Sprints 16/17.** Confirm neither is
   pulled into Sprint 15.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   exists; SDD-046's per-item `validation.md` files are built from its Part B
   (B-1 / B-2 / B-4) "Acceptance" blocks.
7. **Owner has approved the Sprint 15 start** (the second PI-7 hardening sprint).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 15 on a
red test baseline (< 501), an unpushed/mismatched Sprint 14 (not closed at
`ecd13b3` / head `7fe1e39`), a backlog that accidentally closed SDD-046 or
pulled in SDD-047/048, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 15 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 15 ships **one epic feature** (SDD-046) that makes the framework's
promises true: the ledger genuinely records dispatch outcomes because logging is
now a REQUIRED close step (B-1, make-real -- owner-decided), at least the TDD
gate becomes a real blocking check instead of prose (B-2), and one GitHub
Actions CI workflow runs the `doctor` set on push and PR so the checks fire for
everyone (B-4). A teammate who reads the universal-logging claim and opens the
ledger now finds real rows; a rule that matters now fails a command when
violated; and the same checks run locally and in CI.

### Scope

- **SDD-046 -- B-1 (make the ledger true, MAKE-REAL / Option 1)**: make dispatch
  logging a REQUIRED close step. A feature/sprint cannot be stamped DONE until
  its dispatch outcomes are in the ledger; the `/qa` and `/retro` flows (or the
  close flow) write the rows; `doctor` warns if the current PI has zero rows.
  **This fork is LOCKED to make-real** -- CLARIFY does not re-decide it; it only
  refines where the close-gate check lives and how logging stays a one-liner.
- **SDD-046 -- B-2 (turn high-payoff rules into blocking checks)**: pick two or
  three rules with the highest payoff and make them real, fast, stdlib checks
  runnable locally and in CI. **Start with the TDD gate** -- the prose logic
  already exists in the `tdd-gate` skill's "Mechanical Check" step; turn it into
  code. The corresponding prose skill(s) must then point at the enforcing
  script, and each enforced rule must have tests proving it catches a real
  violation.
- **SDD-046 -- B-4 (CI for everyone, every push)**: add **one** GitHub Actions
  workflow that runs the exact `doctor` set (tests + schema_lint + the B-2
  checks + B-3 consistency + A-6 origin lint) on push and PR. Local `doctor` and
  CI must invoke the **identical** entrypoint so they never diverge. ADR-009
  references CI that does not exist; this workflow either makes ADR-009 real or
  supersedes it (decided at CLARIFY).
- **Per-item SDD-IDs**: CLARIFY assigns a per-item SDD-ID to B-1, B-2, and B-4,
  each with its own `validation.md` built from the audit "Acceptance" block.
- **Dogfood the new rule**: the mandatory-ledger close gate applies to **this
  sprint's own dispatches**. Sprint 15's own dispatch outcomes must be in the
  ledger before Sprint 15 can be stamped DONE.

### Explicit exclusions

- **SDD-047** (A-2/A-3/D-1/D-3 de-author) and **SDD-048** (C-1/C-2/C-3/D-2
  maintainability) are later PI-7 sprints. They are NOT in Sprint 15.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 15 scope.
- **PI-7 close**: closing PI-7 is a separate owner-approved decision after the
  Sprint 17 close. Sprint 15 leaves PI-7 continuing; it does not close it.
- **Re-opening the B-1 fork**: the make-real decision is final (owner,
  2026-06-26). Do NOT rewrite Article VII / RULES Rule 4 to retract the claim
  (that was the rejected Option 2).

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-38: SDD-046 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs (B-1/B-2/B-4) and builds each `validation.md` from the audit Acceptance blocks. B-1 is locked to make-real -- CLARIFY only refines the close-gate mechanism and keeps logging a one-liner. The B-4 / ADR-009 supersede-vs-update call is made here. |
| 2 | F-39: SDD-046 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. The mandatory-ledger close gate, the TDD-gate blocking check (and any second/third B-2 check), and the CI workflow land with real-run evidence per `validation.md`. Dogfood B-1: log this sprint's own dispatches. |
| 3 | F-40: Sprint 15 close | Sprint EM + SW Dev | Close Sprint 15, regenerate state, request owner pre-push approval, mark SDD-046 (and the per-item IDs) DONE, and record PI-7 as continuing into Sprint 16. The Sprint EM produces the sprint-close summary and reports it UP to the project Executive Manager. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces
a file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `cli/state_builder.py`, `cli/fleet.py`, `cli/qa.py`, `cli/retro.py`,
`cli/bootstrap.py` (doctor), `cli/schema_lint.py`, `constitution/**`, the
`.github/workflows/` CI file, generated exec surfaces, or shared spec artifacts
-- force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- B-1 close-gate mechanism (HOW only; the fork is locked)

The make-real decision is final. Decide WHERE the close-gate check lives and HOW
logging stays a one-liner. Default recommendation: the close flow (`/qa` and/or
`/retro`) writes the dispatch rows via a single `fleet.py mark` one-liner, and a
`doctor` check warns/fails if the current PI has zero ledger rows at close.
Confirm the gate is a check (not just prose) and that it does not block on a
PI that legitimately ran zero dispatches mid-sprint -- it gates at the DONE/close
boundary. Do NOT re-decide make-real vs retract.

### Q-B -- B-2 which rules become blocking checks

Lock which two or three rules become real checks. Default recommendation: start
with the **TDD gate** (the `tdd-gate` skill's "Mechanical Check" already
specifies the logic -- a diff/commit-range script that fails if production paths
changed without a corresponding test change and no `[NO-TEST-NEEDED]` tag).
Strong second/third candidates: **file-scope** (flag a single dispatch/commit
touching > 3 production files without escalation) and **DONE-completeness** (a
closed feature dir has spec + all-REQUIRED-checked `validation.md` + RETRO).
Decide how many to ship in Sprint 15 (recommend: TDD gate is mandatory; add one
more only if it stays low-friction).

### Q-C -- B-2 false-positive tuning

Decide the thresholds/tags that keep the new checks from eroding trust. Default
recommendation: support an explicit opt-out tag (`[NO-TEST-NEEDED]`) for the TDD
gate, a documented escalation path for the file-scope check, and tests that
prove each check both catches a real violation AND passes a legitimate change
(no false positive on the framework's own recent commits). Start strict-but-
escapable; tune before expanding.

### Q-D -- B-4 CI entrypoint = local == CI

Confirm the single `doctor` entrypoint that both `make doctor` (local) and the
GitHub Actions workflow invoke, so they never diverge. Default recommendation:
the CI workflow runs the exact same `bootstrap.py doctor` command (tests +
schema_lint + B-2 checks + B-3 consistency + A-6 origin lint) shipped in
Sprint 14, with no CI-only steps. Keep the workflow minimal and stdlib-friendly
(Article V): a single Python setup + one command.

### Q-E -- B-4 vs ADR-009

Decide whether the new CI workflow makes ADR-009 real (update it to reflect the
actual workflow) or supersedes it (a new ADR that replaces the stale CI claim).
Default recommendation: if ADR-009's intent matches the shipped workflow, update
ADR-009 to point at the real file; if it diverges materially, supersede it with
a new ADR. Either path is owner-visible documentation hygiene, not a constitution
edit.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` and the new checks use argparse,
  sqlite3, pathlib, json, sys, os only. The B-2 checks and the B-4 CI workflow
  add NO third-party Python dependency.
- **Article X locked render functions are immutable.** Do NOT edit `render_html`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or
  `load_decisions`. Sprint 15 does not touch the dashboard renderer; any state
  regeneration is read-only. `TestS1FootprintLockGuard` golden SHA-256 hashes
  must still PASS.
- **B-1 make-real is locked.** Do NOT re-open the fork. Implement mandatory
  logging at close (Option 1); do NOT retract the universal-logging claim
  (Option 2 is rejected).
- **The new mandatory-ledger rule applies to THIS sprint.** Dogfood it: Sprint
  15's own dispatch outcomes must be logged in the ledger before close.
- **Constitution edits are gated.** No `constitution/**` change without an ADR +
  recorded owner approval + a version bump. The B-4 / ADR-009 work is ADR
  hygiene under `docs/ADR/`, not a constitution edit; treat any constitution
  wording touch as Level-2.
- **Spec source is authoritative but stale-checked.** Build each SDD-046 per-item
  `validation.md` from the audit "Acceptance" block, but verify each "Evidence"
  line against the live repo before acting. If an item is wrong on inspection,
  file a clarification and surface it -- do not silently drop it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044).** All human-facing output in this
  sprint (status, progress, questions to the owner) is short and plain;
  agent-to-agent detail may stay detailed. The Sprint EM holds this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 15 closes only when all are true:

1. **SDD-046 B-1 implemented (make-real)**: dispatch logging is a REQUIRED close
   step; a feature/sprint cannot be stamped DONE with unlogged dispatches; the
   `/qa` and `/retro` (or close) flows write ledger rows; `doctor` warns if the
   current PI has zero rows; the current PI shows real rows in `state.html`.
2. **SDD-046 B-2 implemented**: at least the TDD gate is a real blocking check
   that fails a command on violation; the corresponding prose skill points at the
   enforcing script; each enforced rule has tests proving it catches a real
   violation (and does not false-positive a legitimate change).
3. **SDD-046 B-4 implemented**: one GitHub Actions workflow runs the `doctor` set
   on push and PR; CI and `make doctor` invoke the same entrypoint; ADR-009
   either reflects the real workflow or is superseded.
4. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual checks checked at close.
5. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 501
   passed, 2 skipped (the Sprint 14 close baseline), and grows with the new
   tests.
6. Schema lint clean (exit 0).
7. Article X lock held (`TestS1FootprintLockGuard` PASS).
8. **CI present and green**: the GitHub Actions workflow exists and passes on the
   Sprint 15 head; a change that breaks an enforced rule would make it red.
9. **Ledger shows real Sprint 15 rows**: the dogfood holds -- Sprint 15's own
   dispatches are in the ledger and `doctor` is green.
10. SDD-046 (and the per-item SDD-IDs) marked DONE in BACKLOG with evidence.
11. Owner pre-push approval recorded before any push.
12. **PI-7 recorded as continuing into Sprint 16.** The PI-7 CLOSE itself is a
    SEPARATE owner-approved decision taken after Sprint 17; Sprint 15 does not
    close PI-7.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 15 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-38, F-39, F-40
- Commits: <commit SHAs>
- Tests: 501 -> <N> (>= 501 required)
- Schema lint: clean
- Validation: SDD-046 per-item (B-1/B-2/B-4) <r>/<r> REQUIRED + manual checks
- B-1 decision: MAKE-REAL (Option 1) -- owner-locked 2026-06-26; mandatory dispatch logging at close
- B-2 blocking checks shipped: <TDD gate + any second/third>
- B-4 CI: <workflow file>; entrypoint == `make doctor`; ADR-009 <updated | superseded by ADR-0NN>
- Per-item SDD-IDs assigned for SDD-046: <list>
- Ledger dogfood: <N> real Sprint 15 rows; doctor green
- PI-7 status: ACTIVE -> continues into Sprint 16
- SDD-046: DONE (B-1 ledger truth + B-2 blocking checks + B-4 CI)
- Deferred to later PI-7 sprints: SDD-047 (S3), SDD-048 (S4); SDD-035 out-of-band
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 15 lessons>
- Next: SPRINT-16 kickoff (PI-7 Sprint 3 -- De-author: SDD-047 A-2/A-3/D-1/D-3)
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT re-open the B-1 fork. The make-real decision is final (owner,
  2026-06-26). Do NOT retract the universal-logging claim (rejected Option 2).
- Do NOT close PI-7 automatically. PI-7 CLOSE is a separate owner-approved
  decision taken after Sprint 17 closes.
- Do NOT pull in SDD-047 or SDD-048 -- those are Sprints 16/17.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT edit the Article X locked render functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`).
- Do NOT edit `constitution/**` without an ADR + recorded owner approval +
  version bump. The B-4 / ADR-009 work is `docs/ADR/` hygiene, not a
  constitution edit.
- Do NOT add third-party dependencies; the B-2 checks and the B-4 CI workflow are
  stdlib-only.
- Do NOT ship a B-2 check that false-positives the framework's own legitimate
  commits; prove each check on a real violation AND a legitimate change.
- Do NOT silently drop a SDD-046 audit item; if an "Evidence" line no longer
  matches the repo, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-046 spec dir here -- F-38 does that inside the
  Sprint 15 working sessions.
- Do NOT have the Sprint EM create a sprint or PI -- it may only SUGGEST to the
  project EM and reports up at close.
