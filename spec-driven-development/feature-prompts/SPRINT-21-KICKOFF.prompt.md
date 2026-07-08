# SPRINT 21 KICKOFF -- PI-8 Sprint 4 / Decision-request format for human-facing agents

You are leading **Sprint 21**, which is **PI-8 Sprint 4** -- a capacity slice of
**PI-8 ("Truth in the Window")**. Sprint 18 fixed the dashboard detectors, Sprint
19 refreshed the stale session-start docs and added a stale-doc guard, and Sprint
20 repaired the roadmap and backfilled status/checklists so the dashboard tells
one true story. Sprint 21 fixes the last "truth" gap -- not in the dashboard, but
in **how agents talk to the owner.** Today the Sprint EM and other human-facing
agents send long status updates with the actual decision buried in prose, so the
owner cannot quickly see what is being asked, what the options are, or the impact.
SDD-044 (PI-7) made the language plainer; it did not fix HOW a decision is
surfaced. After Sprint 21, every human-facing agent that needs an owner decision
surfaces it as a short, clearly-marked **DECISION-REQUEST block** at the very end
of the message -- one decision per message, nothing buried. Your job is to ship
one anchor feature (SDD-053) and leave PI-8 ready for its close decision:

1. **SDD-053** -- Decision-request format for human-facing agents. Extend the
   `em-communication-discipline` skill
   ([`../../.github/skills/operational/em-communication-discipline/SKILL.md`](../../.github/skills/operational/em-communication-discipline/SKILL.md))
   and the two EM agent charters
   ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md),
   [`../../.github/agents/principal-executive-manager.agent.md`](../../.github/agents/principal-executive-manager.agent.md))
   with a mandatory DECISION-REQUEST FORMAT: short status ABOVE, then a
   clearly-marked decision block at the very END with nothing after it --
   `DECISION NEEDED: <one line>`, numbered Options each with a one-line impact,
   and a Recommendation (which + one-line why). One decision block per message;
   never bury a question in prose; if no decision is needed, no block (just a
   short status). CLARIFY assigns per-item SDD-IDs as needed, each with its own
   `validation.md`.

**Closing Sprint 21 does NOT automatically close PI-8.** Sprint 21's close
produces a sprint-close summary and reports up to the project EM; the PI-8 CLOSE
is a separate, owner-approved decision taken after this sprint.

Do NOT pull in any other PI-8 work: **SDD-049** (file-overlap detector) and
**SDD-041 Option B** (reorder -> backend re-optimization) remain open,
unallocated candidates and are NOT in Sprint 21. **SDD-035** (Azure decommission)
remains out-of-band.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent -- the sprint-scoped
EM shipped in Sprint 14 (SDD-043 / ADR-020). It is NOT the project Executive
Manager.

- In the fresh session, **activate the `sprint-executive-manager` agent**
  ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md)),
  not `principal-executive-manager`.
- The Sprint EM coordinates exactly this one sprint. It **routes** feature work
  to the Principal Product Manager, Principal Architect, and Principal Software
  Developer, synthesizes their answers, and surfaces escalations. It makes NO
  product, technical, or implementation decisions itself (Level 0).
- The Sprint EM **cannot create sprints or PIs** -- it may only SUGGEST to the
  project EM. At sprint close it produces a sprint-close summary and **reports UP
  to the project Executive Manager**, who folds it into project-wide state and
  owns the owner conversation.
- Human-facing output from the Sprint EM is **short and plain** (SDD-044) -- and
  this sprint dogfoods its own feature: every decision the Sprint EM brings to the
  owner during Sprint 21 uses the new DECISION-REQUEST FORMAT.

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-053 (including the
Level-1-vs-Level-2 call on the skill/charter edits). The Principal Software
Developer owns implementation, QA, and the Sprint 21 close (reporting up to the
project EM through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 21 must not start until all checks are true:

1. **Sprint 20 is CLOSED and pushed.** Confirm Sprint 20 (PI-8 Sprint 3, roadmap
   repair + status/checklist backfill) CLOSED at commit `31a9b81` (push head
   `36b7f3e` or later) with SDD-052 (and its per-item IDs) marked DONE in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md), and that
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) marks PI-8
   **ACTIVE** (`status: active`).
2. **Tests are green at the Sprint 20 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **590 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint, origin lint, and stale-doc lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0,
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files, and `python spec-driven-development/cli/staledoc_lint.py`
   is green on the current tree.
4. **`doctor` is green and CI is green.** The health set passes and the GitHub
   Actions CI workflow (B-4) is green on the `36b7f3e` head. The Article X lock
   guard (`TestS1FootprintLockGuard`) is PASS at this baseline.
5. **SDD-053 is filed and allocated to Sprint 21.** Confirm the SDD-053 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-8 Sprint 21.
6. **The live PI-8 gates apply to Sprint 21.** The mandatory-ledger close gate
   (B-1) is LIVE -- Sprint 21's own dispatch outcomes must be logged in the ledger
   before Sprint 21 can be stamped DONE. The blocking checks (B-2: TDD gate +
   DONE-completeness) and CI (B-4) are LIVE -- Sprint 21 must pass them.
7. **Owner has approved the Sprint 21 start** (via the Executive Manager).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 21 on a
red test baseline (< 590), an unpushed/mismatched Sprint 20 (not closed at
`31a9b81` / pushed at `36b7f3e`), a red `doctor` / origin lint / staledoc lint /
CI, a broken Article X lock, a backlog that accidentally closed SDD-053, PI-8 not
marked ACTIVE, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 21 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

PI-8 is already ACTIVE. There is no PI-activation step in Sprint 21; the
current-PI dispatch-rows check (B-1) is satisfied by logging Sprint 21's own
dispatches into the ledger.

---

## 1. Sprint goal

Sprint 21 ships **one anchor feature** (SDD-053) so that every human-facing agent
that needs an owner decision surfaces it the same way: a short status, then a
clearly-marked decision block at the very end with nothing after it. The payoff is
felt directly -- the owner can read the ask, the options, and the recommendation
in seconds, and never has to hunt for a buried question again. The sprint dogfoods
its own rule: the Sprint EM uses the new format for every decision it brings to
the owner during Sprint 21.

### Scope

- **SDD-053 -- `em-communication-discipline` skill edit**
  ([`../../.github/skills/operational/em-communication-discipline/SKILL.md`](../../.github/skills/operational/em-communication-discipline/SKILL.md)):
  add a mandatory DECISION-REQUEST FORMAT section that codifies:
  - short status ABOVE the block, lead-with-answer as today;
  - a clearly-marked decision block at the very END, nothing after it:
    `DECISION NEEDED: <one line>`, then numbered `Options:` each with a one-line
    `impact:`, then `Recommendation: <which + one-line why>`;
  - **one decision block per message**; never bury a question in prose;
  - if no decision is needed, **no block** -- just a short status.
  Keep it consistent with the skill's existing "recommend, do not menu" guidance
  (the format is the container for the recommendation, not a return to menuing).
- **SDD-053 -- EM agent charter edits**
  ([`../../.github/agents/sprint-executive-manager.agent.md`](../../.github/agents/sprint-executive-manager.agent.md),
  [`../../.github/agents/principal-executive-manager.agent.md`](../../.github/agents/principal-executive-manager.agent.md)):
  bind both EM charters to the DECISION-REQUEST FORMAT so the rule is enforced
  where the EMs are defined, cross-referencing the skill as the single source of
  truth (do not duplicate the full spec in each charter -- point at the skill).
- **SDD-053 -- test/lint if feasible**: prose is hard to lint, so the skill +
  charter edits are the core deliverable. If a cheap, high-signal check is
  feasible (for example, a structural test that the skill contains the required
  format headings and both charters reference it), add it stdlib-only. Do not
  invent a brittle prose linter.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1) applies
  to **this sprint's own dispatches**. Sprint 21's own dispatch outcomes must be
  in the ledger before Sprint 21 can be stamped DONE.

### Is this a constitution edit? -- READ THIS

The edits land under `.github/skills/` and `.github/agents/` -- **not**
`constitution/**`. On precedent these are **Level-1 documentation/behavior edits
and do NOT require an ADR or a constitution version bump.** SDD-044 (the prior
plain-language comms change) broadened the same skill without a constitution edit.
The Architect confirms the Level-1 call at CLARIFY. If CLARIFY finds the change
would actually alter a binding constitution article (it should not), STOP and
surface it as a Level-2 escalation -- but the expected path is Level-1.

Owner approval before push is still required as a matter of house discipline
(every push in this project is owner-gated), but no ADR / version bump is expected.

### Explicit exclusions

- **SDD-049** (file-overlap detector) and **SDD-041 Option B** (reorder -> backend
  re-optimization) remain open, unallocated candidates and are NOT in Sprint 21.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 21 scope.
- **Article X locked render functions** are out of scope. SDD-053 touches a skill,
  two agent charters, and (optionally) a structural test; it does NOT touch
  `render_html`, `render_markdown`, or any locked function.
  `TestS1FootprintLockGuard` stays GREEN.
- **PI-8 close**: closing PI-8 is a separate owner-approved decision AFTER this
  sprint. Sprint 21 reports up; it does not close PI-8.
- **Do NOT scrub history.** Sprint 21 changes forward-looking agent behavior; it
  does not rewrite historical `specs/`, `sprints/`, retros, ADRs, or frozen
  kickoff prompts.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-56: SDD-053 CLARIFY -> SPEC (`validation.md`) -> PLAN -> TASKS | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs, builds `validation.md` from the acceptance criteria below, **confirms the Level-1 (no-ADR) call** on the skill/charter edits, decides whether a cheap structural test is worth adding, and pins the exact format wording so the skill and both charters agree. |
| 2 | F-57: SDD-053 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks. Add the DECISION-REQUEST FORMAT to the skill, bind both EM charters to it (cross-reference, do not duplicate), and add the optional structural test. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. `TestS1FootprintLockGuard` stays GREEN; no locked function touched. |
| 3 | F-58: Sprint 21 close | Sprint EM + SW Dev | Close Sprint 21, regenerate state, verify the skill + both charters carry the format and any structural test is green, request owner pre-push approval, mark SDD-053 (and per-item IDs) DONE, and produce the sprint-close summary. The Sprint EM reports UP to the project Executive Manager and surfaces the PI-8-close decision as the next owner call. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph that proves no two workers modify the same file. Shared
surfaces -- the skill file, either charter, generated exec surfaces, or shared
spec artifacts -- force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- Level-1 vs Level-2 on the skill/charter edits (Architect confirms)

Confirm the edits are Level-1 documentation/behavior changes under `.github/`
(skill + agent charters), NOT a `constitution/**` change, so no ADR or version
bump is needed. Precedent: SDD-044 broadened the same skill without a constitution
edit. Default recommendation: Level-1, no ADR; owner approval before push still
required as house discipline. If CLARIFY finds a genuine constitution impact,
STOP and escalate as Level-2. Surface the call to the owner.

### Q-B -- exact DECISION-REQUEST FORMAT wording (lock it once)

Lock the exact format so the skill and both charters are byte-consistent: the
`DECISION NEEDED:` line, the numbered `Options:` with one-line `impact:` each, the
`Recommendation:` line, the "one block per message," the "block at the very end,
nothing after it," and the "no decision -> no block" rule. Default recommendation:
define it once in the skill and have both charters point at the skill as the
single source of truth (no duplicated spec that can drift). Surface the final
wording to the owner.

### Q-C -- how far to enforce (skill/charter only, or add a check?)

Decide whether to add a cheap structural test or lint. Prose is hard to lint, so
the core deliverable is the skill + charter edits. Default recommendation: add a
small stdlib-only structural test that asserts the skill contains the required
format headings and that both charters reference the skill -- high signal, low
brittleness. Do NOT build a prose-quality linter. Surface the choice to the owner.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** If any test or helper is added it uses argparse,
  sqlite3, pathlib, json, sys, os, re only. Sprint 21 adds NO third-party Python
  dependency.
- **Article X locked render functions are immutable.** Sprint 21 does NOT touch
  `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, or `load_decisions`. `TestS1FootprintLockGuard` stays
  GREEN.
- **The edits are `.github/` (Level-1), not `constitution/**`.** No ADR or version
  bump is expected; the Architect confirms at CLARIFY. Owner approval before push
  is still required as house discipline.
- **Single source of truth.** Define the format once in the skill; both charters
  reference it. Do not duplicate the full spec in each charter (it will drift).
- **Do not regress the `doctor`/CI set.** After the edit, the health set
  (including the stale-doc check) stays green.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 21's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 21 must pass the TDD
  gate and DONE-completeness checks and keep CI green.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Dogfood SDD-044 + SDD-053.** All human-facing output in this sprint is short
  and plain, and every owner decision uses the new DECISION-REQUEST FORMAT. The
  Sprint EM holds this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Do NOT scrub history.** Sprint 21 changes forward-looking agent behavior; it
  does not rewrite historical `specs/`, `sprints/`, retros, ADRs, or frozen
  kickoff prompts.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 21 closes only when all are true:

1. **The skill carries the format.** `em-communication-discipline/SKILL.md`
   contains a DECISION-REQUEST FORMAT section with the `DECISION NEEDED:` line,
   numbered `Options:` with one-line `impact:` each, a `Recommendation:` line, the
   "one block per message," "block at the very end," and "no decision -> no block"
   rules.
2. **Both EM charters are bound.** `sprint-executive-manager.agent.md` and
   `principal-executive-manager.agent.md` require the format and reference the
   skill as the single source of truth (no duplicated drift-prone spec).
3. **Structural check (if added) is green.** Any added test asserts the skill
   headings and the two charter references; it passes.
4. All per-item REQUIRED validation items checked with real evidence (100%
   REQUIRED); manual checks checked at close.
5. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 590
   passed, 2 skipped (grows if a structural test is added; must not regress).
6. Schema lint clean (exit 0), origin lint clean (0 hits in generic files), and
   stale-doc lint green.
7. **Article X lock held**: `TestS1FootprintLockGuard` PASS; the locked render/
   load functions are byte-identical.
8. **`doctor` green and CI green**: the health set and the GitHub Actions workflow
   pass on the Sprint 21 head; the B-2 blocking checks pass.
9. **Ledger shows real Sprint 21 rows**: the dogfood holds -- Sprint 21's own
   dispatches are in the ledger and the B-1 close gate is satisfied.
10. SDD-053 (and any per-item SDD-IDs) marked DONE in BACKLOG with evidence.
11. **Owner pre-push approval recorded before any push.**
12. **PI-8 close surfaced as the next decision.** Sprint 21 does not close PI-8;
    the Sprint EM reports up to the project Executive Manager, who surfaces the
    PI-8-close decision to the owner.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 21 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-56, F-57, F-58
- Commits: <commit SHAs>
- Tests: 590 -> <N> (>= 590 required; must not regress)
- Schema lint: clean; origin lint: 0 hits in generic files; stale-doc lint: green
- Validation: SDD-053 per-item <r>/<r> REQUIRED + manual checks
- Skill edit: em-communication-discipline carries DECISION-REQUEST FORMAT -- <PASS | FAIL>
- Charter edits: sprint-executive-manager + principal-executive-manager reference the format -- <PASS | FAIL>
- Structural test: <added (N tests) | not added, rationale>
- Level-1-vs-Level-2 call: Level-1 (no ADR / no version bump), Architect-confirmed -- <YES>
- Per-item SDD-IDs assigned for SDD-053: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 21 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS); render_html / render_markdown untouched
- History preserved: YES (no historical specs/sprints/retros/ADRs/frozen prompts rewritten)
- SDD-053: DONE (decision-request format in skill + both EM charters)
- Deferred / out of scope: SDD-049 + SDD-041 Option B (open, unallocated candidates), SDD-035 out-of-band
- PI-8 status: ACTIVE -- Sprint 21 CLOSED; PI-8-close decision surfaced to owner
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 21 lessons>
- Next: PI-8 close decision (owner) -- and/or a future sprint for SDD-049 / SDD-041 Option B
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close PI-8. Sprint 21 reports up; the PI-8 CLOSE is a separate
  owner-approved decision after this sprint.
- Do NOT treat the skill/charter edits as a constitution change. They are
  `.github/` Level-1 edits; no ADR / version bump is expected. If CLARIFY finds a
  genuine constitution impact, STOP and escalate as Level-2 -- do not proceed
  silently either way.
- Do NOT duplicate the full format spec in each charter -- define it once in the
  skill and reference it, or the two copies will drift.
- Do NOT build a brittle prose-quality linter. A cheap structural check is fine;
  a prose grader is out of scope.
- Do NOT pull in SDD-049, SDD-041 Option B, or any other PI-8 candidate.
- Do NOT edit, move, or rewrite the Article X locked functions (`render_html`,
  `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`). `TestS1FootprintLockGuard` stays
  GREEN.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 21's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT scrub or rewrite history; a count or status inside a historical record
  or a frozen kickoff prompt stays as written.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-053 spec dir here -- F-56 does that inside the Sprint 21
  working sessions.
- Do NOT have the Sprint EM create a sprint or PI (or author the next kickoff) --
  it may only SUGGEST to the project EM and reports up at close.
