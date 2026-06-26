# SPRINT 16 KICKOFF -- PI-7 Sprint 3 / De-author (strip personal + origin fingerprints)

You are leading **Sprint 16**, which is **PI-7 Sprint 3** of PI-7 ("Hardening +
Orchestration Maturity"). Sprint 14 made the framework clone-and-run portable.
Sprint 15 made its promises true (the ledger is real, the rules that matter
block, CI fires for everyone). Sprint 16 is the de-author sprint: the framework
stops carrying the fingerprints of the person and the project it was born in. A
teammate who clones it should not be able to tell who wrote it or which app it
grew out of, every shipped skill should be wired to something or gone, and the
docs should stop claiming a "conflict detection" the code does not perform. Your
job is to ship one epic feature (SDD-047) and leave PI-7 ready to continue into
Sprint 17:

1. **SDD-047** -- De-author the content (audit epic, spec source
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   Parts A + D): **A-2** (owner/identity becomes a config value, not a hardcoded
   name), **A-3** (scrub origin-project leakage out of the generic framework
   files), **D-1** (wire-or-delete the 10 dead skills), **D-3** (rename "parallel
   dispatch with conflict detection" to the "serial CLARIFY/SPEC gate" the code
   actually implements). CLARIFY assigns per-item SDD-IDs, each with its own
   `validation.md` from the audit Acceptance blocks.

**De-author the GENERIC files only -- preserve the historical record.** A-2 and
A-3 Acceptance explicitly allow historical `specs/`, `sprints/`, retros, and
ADRs to KEEP their record: the author's name in the PI-1..PI-6 history is fine,
that is what happened. Sprint 16 de-authors only the GENERIC framework surfaces a
new teammate reads as instruction -- agent definitions, skills, constitution,
`INSTRUCTIONS.md`, and the README-as-instruction. Keep the README origin story as
clearly-marked history, not as guidance. Do NOT rewrite history.

The A-6 origin-token/identity lint already shipped in Sprint 14. A-2/A-3 should
make that lint pass clean on the generic files: where the lint currently relies
on allowed exceptions, de-authoring removes the need for them. At close the A-6
grep returns **0 hits in non-historical files**.

Do NOT pull in any Sprint 17 work: **SDD-048** (C-1/C-2/C-3/D-2 maintainability)
is the next PI-7 sprint and must not be started here. Do NOT touch Azure
decommission (SDD-035). PI-7 CLOSE is a separate, owner-approved decision taken
AFTER Sprint 17 -- closing Sprint 16 does not close PI-7.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent -- the
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

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-047. The Principal
Software Developer owns implementation, QA, and the Sprint 16 close (reporting up
to the project EM through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 16 must not start until all checks are true:

1. **Sprint 15 is CLOSED and pushed.** Confirm Sprint 15 (PI-7 Sprint 2) closed
   at commit `44d546d` (with the backfill at head `db98dbd`), that
   [`../sprints/PI-7/CURRENT_PI.md`](../sprints/PI-7/CURRENT_PI.md) marks PI-7
   **ACTIVE** and names Sprint 16 as the next sprint, and that SDD-046 (with its
   per-item B-1/B-2/B-4 IDs) is marked DONE in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md).
2. **Tests are green at the Sprint 15 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **518 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
4. **`doctor` is green and CI is green.** The Sprint 14/15 health set passes:
   `doctor` reports green (8/8), and the GitHub Actions CI workflow (B-4) is
   green on the `db98dbd` head. The live B-1/B-2/B-4 gates from Sprint 15 are in
   force for Sprint 16 (see point 8).
5. **SDD-047 is filed and allocated to Sprint 16.** Confirm the SDD-047 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-7 Sprint 16.
6. **SDD-048 remains allocated to Sprint 17.** Confirm it is not pulled into
   Sprint 16.
7. **The audit spec source is present.** Confirm
   [`../docs/Temp/EMF-HARDENING-PLAN.md`](../docs/Temp/EMF-HARDENING-PLAN.md)
   exists; SDD-047's per-item `validation.md` files are built from its Part A
   (A-2 / A-3) and Part D (D-1 / D-3) "Acceptance" blocks.
8. **The live Sprint 15 gates apply to Sprint 16.** The mandatory-ledger close
   gate (B-1) is LIVE -- Sprint 16's own dispatch outcomes must be logged in the
   ledger before Sprint 16 can be stamped DONE. The blocking checks (B-2: TDD
   gate + DONE-completeness) and CI (B-4) are LIVE -- Sprint 16 must pass them.
9. **Owner has approved the Sprint 16 start** (the third PI-7 hardening sprint).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 16 on a
red test baseline (< 518), an unpushed/mismatched Sprint 15 (not closed at
`44d546d` / head `db98dbd`), a red `doctor` or CI, a backlog that accidentally
closed SDD-047 or pulled in SDD-048, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 16 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

---

## 1. Sprint goal

Sprint 16 ships **one epic feature** (SDD-047) that strips the personal and
origin fingerprints out of the generic framework. Owner/identity becomes a config
value instead of a hardcoded name (A-2); the origin-project examples
(`engine.py`, FastAPI, Day-to-Day, World State, etc.) leave the 22 generic files
for the host archetype or a clearly-labeled example block (A-3); the 10 dead
skills are each wired to the agent/prompt that should use it or deleted (D-1);
and the over-claimed "conflict detection" is renamed to the "serial CLARIFY/SPEC
gate" the code actually implements (D-3). A new teammate reading any agent or
core skill cannot tell who wrote the framework or which project it came from, the
A-6 origin/identity lint returns 0 hits in the generic files, and every shipped
skill is referenced or gone.

### Scope

- **SDD-047 -- A-2 (owner/identity becomes a config value)**: introduce one
  config surface -- `project.config.json` or `constitution/owner.md` -- holding
  `owner`, `team`, `repo_url`. Replace hardcoded names in the agent files,
  `INSTRUCTIONS.md`, and the PM "single user" line with a reference to that
  value (the PM agent traces value to "the host project's owner," not a person).
  Change skill `author:` frontmatter to a neutral value (e.g. `emf-framework`) or
  read it from config. The A-4 setup prompt fills the owner in. The A-6 lint
  must read this config so a re-added personal name fails it.
- **SDD-047 -- A-3 (scrub origin-project leakage)**: move the origin-specific
  examples out of the 22 flagged generic files into either the host-project
  archetype where they belong or a clearly-labeled `examples/` block. **Replace
  in-place examples with stack-neutral ones -- do not just delete them**
  (over-scrubbing removes useful concrete examples). Keep the origin story in
  `README` as clearly-marked history, not as instruction.
- **SDD-047 -- D-1 (wire-or-delete the 10 dead skills)**: for each unreferenced
  skill (`diagnose`, `grill-with-docs`, `host-integration-symlink`,
  `lesson-capture`, `respect-existing`, `session-self-review`,
  `stakeholder-pressure-defense`, `to-plan`, `weekly-status-report`,
  `tdd-gate`), either wire it into the agent/prompt that should use it or delete
  it. **Start with `tdd-gate`**: Sprint 15's B-2 turned it into a real check, so
  reference it from the SW Dev review flow -- an unreferenced enforcement skill is
  worse than none.
- **SDD-047 -- D-3 (rename the over-claim)**: rename "parallel dispatch with
  conflict detection" to "serial CLARIFY/SPEC gate" everywhere it appears, to
  match the `fleet.py` `_scan_lock_state` behavior (a serial per-phase lock, not
  a file-dependency graph). If a true file-overlap detector is genuinely wanted,
  file it as an **honest backlog item** -- do not paper over the gap.
- **Per-item SDD-IDs**: CLARIFY assigns a per-item SDD-ID to A-2, A-3, D-1, and
  D-3, each with its own `validation.md` built from the audit "Acceptance" block.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1, live
  from Sprint 15) applies to **this sprint's own dispatches**. Sprint 16's own
  dispatch outcomes must be in the ledger before Sprint 16 can be stamped DONE.

### Historical-record carve-out (do NOT scrub history)

A-2 and A-3 Acceptance preserve the historical record. The author's name and the
origin-project references in **historical** `specs/`, `sprints/`, retros, and
ADRs (PI-1..PI-6) are part of what happened and stay. Sprint 16 de-authors only
the **generic framework files** a teammate reads as instruction:

- `.github/agents/**` (agent definitions)
- `.github/skills/**` (skills, including `author:` frontmatter)
- `constitution/**` (any wording touch is Level-2 -- see constraints)
- `INSTRUCTIONS.md`
- `README.md` **as instruction** (the origin story stays, clearly marked as
  history, not as guidance)

At close, the A-6 origin-token/identity grep returns **0 hits in
non-historical files**; historical artifacts are out of the lint's scope.

### Explicit exclusions

- **SDD-048** (C-1/C-2/C-3/D-2 maintainability) is PI-7 Sprint 17. It is NOT in
  Sprint 16.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 16 scope.
- **PI-7 close**: closing PI-7 is a separate owner-approved decision after the
  Sprint 17 close. Sprint 16 leaves PI-7 continuing; it does not close it.
- **Rewriting history**: do NOT scrub the author's name or origin references out
  of historical `specs/`, `sprints/`, retros, or ADRs. Those are the record.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-41: SDD-047 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs (A-2/A-3/D-1/D-3) and builds each `validation.md` from the audit Acceptance blocks. The A-2 config shape (`project.config.json` vs `constitution/owner.md`) and the D-1 per-skill wire-or-delete calls are made here. Any constitution wording change is flagged Level-2. |
| 2 | F-42: SDD-047 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. The owner/identity config, the origin-token scrub, the wire-or-delete skill changes, and the conflict-detection rename land with real-run evidence per `validation.md`. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. |
| 3 | F-43: Sprint 16 close | Sprint EM + SW Dev | Close Sprint 16, regenerate state, request owner pre-push approval, mark SDD-047 (and the per-item IDs) DONE, and record PI-7 as continuing into Sprint 17. The Sprint EM produces the sprint-close summary and reports it UP to the project Executive Manager. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces
a file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `cli/schema_lint.py`, `cli/origin_lint.py`, the config surface
(`project.config.json` / `constitution/owner.md`), `constitution/**`,
`INSTRUCTIONS.md`, `README.md`, the skill library, generated exec surfaces, or
shared spec artifacts -- force serialization. (Note: D-3 is a documentation
rename, not a real file-overlap detector -- the serial CLARIFY/SPEC gate remains
the only conflict mechanism.)

---

## 3. Likely CLARIFY surfaces

### Q-A -- A-2 config shape and how the A-6 lint reads it

Decide the owner/identity config surface and how A-6 consumes it. Default
recommendation: a single `project.config.json` at the repo root holding `owner`,
`team`, `repo_url`, read by the A-4 setup prompt (which fills `owner`) and by the
A-6 lint (which loads the configured personal-name denylist from it, so a
re-added name fails). `constitution/owner.md` is the alternative if the owner
prefers a human-readable constitution-adjacent surface -- but that touches
`constitution/**` and is Level-2. Recommend the JSON config to keep the change
out of the constitution.

### Q-B -- A-3 scrub-vs-replace and where origin examples go

Lock the disposition of each origin example: replace in place with a stack-neutral
example, move it to the host-project archetype, or move it to a labeled
`examples/` block. Default recommendation: **replace, do not delete** -- a generic
example that teaches the same concept without naming the origin project. Move
genuinely host-specific examples (the `engine.py` lazy-singleton table in
`principal-architect.agent.md`) into the host archetype. Keep the README origin
story as labeled history. Over-scrubbing that strips all concrete examples is a
regression, not a fix.

### Q-C -- D-1 per-skill wire-or-delete decisions

Decide, for each of the 10 dead skills, whether it is wired or removed. Default
recommendation: **wire `tdd-gate`** into the SW Dev review flow first (B-2 made
it real in Sprint 15 -- it must be referenced). For the remaining nine
(`diagnose`, `grill-with-docs`, `host-integration-symlink`, `lesson-capture`,
`respect-existing`, `session-self-review`, `stakeholder-pressure-defense`,
`to-plan`, `weekly-status-report`), wire each into the agent/prompt that should
use it if it carries real value, otherwise delete it. Surface the per-skill call
list to the owner; a schema_lint rule that flags unreferenced skills locks the
outcome in.

### Q-D -- D-3 rename scope

Confirm which files carry the "parallel dispatch with conflict detection"
over-claim and get the "serial CLARIFY/SPEC gate" rename. Default recommendation:
`roadmap.md`, the relevant agent/skill prose, and any prompt or doc that repeats
the claim. If the owner wants a genuine file-overlap detector, file an honest
backlog item rather than implementing it under this sprint's scope. At close, no
doc claims a conflict detection the code does not perform.

### Q-E -- constitution wording (owner-gated)

If A-2 or A-3 requires changing constitution wording (e.g. the PM "single user"
phrasing if it lives in a constitution file, or any principle that references the
author or origin project), that is a **Level-2** change requiring an ADR +
recorded owner approval + a version bump. Default recommendation: keep the
de-author changes in agent/skill/`INSTRUCTIONS`/config surfaces and avoid
constitution edits; if a constitution touch is unavoidable, surface it explicitly
to the owner with an ADR draft. Do NOT edit `constitution/**` silently.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**`, the A-6 lint, and any config reader use
  argparse, sqlite3, pathlib, json, sys, os only. The de-author work adds NO
  third-party Python dependency.
- **Article X locked render functions are immutable.** Do NOT edit `render_html`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or
  `load_decisions`. Sprint 16 does not touch the dashboard renderer; any state
  regeneration is read-only. `TestS1FootprintLockGuard` golden SHA-256 hashes
  must still PASS.
- **Do NOT scrub the historical record.** De-author only the generic framework
  files (agents, skills, constitution, `INSTRUCTIONS`, README-as-instruction).
  Historical `specs/`, `sprints/`, retros, and ADRs keep the author's name and
  origin references -- that is the record.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 16's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 16 must pass the TDD
  gate and DONE-completeness checks and keep CI green; a change that breaks an
  enforced rule must fail loudly.
- **Constitution edits are gated.** No `constitution/**` change without an ADR +
  recorded owner approval + a version bump. A-2/A-3 may touch constitution
  wording (e.g. the PM "single user" line, an author/origin reference) -- treat
  any such touch as **Level-2** and surface it; do not edit silently.
- **Spec source is authoritative but stale-checked.** Build each SDD-047 per-item
  `validation.md` from the audit "Acceptance" block, but verify each "Evidence"
  line against the live repo before acting (Sprints 14/15 may have already moved
  some of the 93 name hits or 22 origin-token files). If an item is wrong on
  inspection, file a clarification and surface it -- do not silently drop it.
- **A-3: replace, do not just delete.** Over-scrubbing that removes useful
  concrete examples is a regression. Replace origin examples with stack-neutral
  ones; relocate genuinely host-specific examples to the archetype.
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

Sprint 16 closes only when all are true:

1. **SDD-047 A-2 implemented**: owner/identity is config-driven (one config
   surface); no generic framework file (agents, skills, constitution,
   `INSTRUCTIONS`) carries a hardcoded personal name; the PM agent traces value to
   "the host project's owner," not a person; skill `author:` frontmatter is
   neutral or config-read; the A-6 lint reads the config and fails a re-added name.
2. **SDD-047 A-3 implemented**: the 22 flagged generic files carry no origin
   tokens outside a labeled example/history block; `principal-architect.agent.md`
   design examples are stack-neutral; the README origin story is present and
   clearly marked as history, not instruction; examples were replaced/relocated,
   not just deleted.
3. **SDD-047 D-1 implemented**: every shipped skill is referenced by at least one
   agent or prompt, or is removed; `tdd-gate` is wired into the SW Dev flow; a
   schema_lint rule flags unreferenced skills.
4. **SDD-047 D-3 implemented**: no doc claims "conflict detection" the code does
   not perform; the wording matches the serial CLARIFY/SPEC gate; if a true
   file-overlap detector is wanted, it is filed as an honest backlog item.
5. All per-item REQUIRED validation items checked with real-run evidence (100%
   REQUIRED); manual checks checked at close.
6. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 518
   passed, 2 skipped (the Sprint 15 close baseline), and grows with any new tests.
7. Schema lint clean (exit 0).
8. Article X lock held (`TestS1FootprintLockGuard` PASS).
9. **`doctor` green and CI green**: the Sprint 14/15 health set and the GitHub
   Actions workflow pass on the Sprint 16 head; the B-2 blocking checks pass.
10. **A-6 origin-token/identity lint returns 0 hits in generic files**: the lint
    is clean on `.github/` and `constitution/` (historical artifacts excluded).
11. **Ledger shows real Sprint 16 rows**: the dogfood holds -- Sprint 16's own
    dispatches are in the ledger and the B-1 close gate is satisfied.
12. SDD-047 (and the per-item SDD-IDs) marked DONE in BACKLOG with evidence.
13. Owner pre-push approval recorded before any push.
14. **PI-7 recorded as continuing into Sprint 17.** The PI-7 CLOSE itself is a
    SEPARATE owner-approved decision taken after Sprint 17; Sprint 16 does not
    close PI-7.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 16 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-41, F-42, F-43
- Commits: <commit SHAs>
- Tests: 518 -> <N> (>= 518 required)
- Schema lint: clean
- Validation: SDD-047 per-item (A-2/A-3/D-1/D-3) <r>/<r> REQUIRED + manual checks
- A-2 config surface: <project.config.json | constitution/owner.md (Level-2)>; A-6 lint reads it
- A-3 scrub: 22 generic files clean; examples replaced/relocated (not deleted); README origin story = labeled history
- D-1 skills: <wired list> / <deleted list>; tdd-gate wired into SW Dev flow; unreferenced-skill schema_lint rule added
- D-3 rename: "conflict detection" -> "serial CLARIFY/SPEC gate" in <files>; honest backlog item filed for true file-overlap detector: <YES/NO>
- Historical record preserved: YES (PI-1..PI-6 specs/sprints/retros/ADRs untouched)
- A-6 origin/identity lint: 0 hits in generic files
- Per-item SDD-IDs assigned for SDD-047: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 16 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS)
- PI-7 status: ACTIVE -> continues into Sprint 17
- SDD-047: DONE (A-2 config identity + A-3 origin scrub + D-1 wire/delete skills + D-3 rename)
- Deferred to later PI-7 sprints: SDD-048 (S4); SDD-035 out-of-band
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 16 lessons>
- Next: SPRINT-17 kickoff (PI-7 Sprint 4 -- Maintainability + right-sizing: SDD-048 C-1/C-2/C-3/D-2)
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT scrub the historical record. De-author only the generic framework files
  (agents, skills, constitution, `INSTRUCTIONS`, README-as-instruction).
  Historical `specs/`, `sprints/`, retros, and ADRs keep the author's name and
  origin references -- that is the record.
- Do NOT close PI-7 automatically. PI-7 CLOSE is a separate owner-approved
  decision taken after Sprint 17 closes.
- Do NOT pull in SDD-048 -- that is Sprint 17.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT edit the Article X locked render functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`).
- Do NOT edit `constitution/**` without an ADR + recorded owner approval +
  version bump. A-2/A-3 constitution wording touches are Level-2 -- surface them.
- Do NOT add third-party dependencies; the config reader and the A-6 lint are
  stdlib-only.
- Do NOT just delete origin examples (A-3): replace with stack-neutral ones or
  relocate to the host archetype. Over-scrubbing is a regression.
- Do NOT leave an enforcement skill unreferenced. `tdd-gate` (made real in B-2)
  must be wired into the SW Dev flow or the framework keeps claiming enforcement
  it does not invoke.
- Do NOT claim a "conflict detection" the code does not perform; rename to the
  serial CLARIFY/SPEC gate and file an honest backlog item if a real detector is
  wanted.
- Do NOT silently drop a SDD-047 audit item; if an "Evidence" line no longer
  matches the repo, file a clarification and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 16's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-047 spec dir here -- F-41 does that inside the
  Sprint 16 working sessions.
- Do NOT have the Sprint EM create a sprint or PI -- it may only SUGGEST to the
  project EM and reports up at close.
