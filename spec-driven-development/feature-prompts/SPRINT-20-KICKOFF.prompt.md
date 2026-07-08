# SPRINT 20 KICKOFF -- PI-8 Sprint 3 / Roadmap repair + status & checklist backfill

You are leading **Sprint 20**, which is **PI-8 Sprint 3** -- the third sprint of
**PI-8 ("Truth in the Window")**. Sprint 18 fixed the dashboard detectors; Sprint
19 refreshed the four stale session-start docs and added an automated stale-doc
guard. Sprint 20 finishes **"dashboard truth."** Two truths still don't render:
the roadmap is missing an entire PI (PI-6), calls the just-closed PI-7 "current,
closed" in one breath, and has no PI-8 entry; and 5-6 PI-7 spec dirs still carry
`status: active` while 4 genuinely-DONE PI-7 features (SDD-043/044/045/048) never
had their per-folder validation checklists ticked. After Sprint 20, a teammate who
opens the dashboard sees **all 6 PI-7 features render DONE, PI-6 renders, every
closed PI (PI-1..PI-7) at 100%, PI-7 is not current, and PI-8 has its own roadmap
entry.** Your job is to ship one anchor feature (SDD-052) and leave PI-8 ready to
continue to Sprint 21:

1. **SDD-052** -- Roadmap repair + status backfill + PI-7 4-feature checklist
   backfill + ADR-count correction (audit spec source
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   Section 5 roadmap defects + Section 4 / Section 3 Defect-1(c) stale-status):
   **(1) roadmap repair** -- backfill the entirely-missing PI-6 section, fix
   PI-7's self-contradictory `"(current, closed 2026-07-07)"` header, add a PI-8
   roadmap entry, and define/apply closed-PI semantics so the dashboard renders
   closed PIs at 100% (Sprint 18's SDD-050 already reads the `(closed)` marker
   defensively -- this backfills the markers and the PI-6 section it depends on);
   **(2) spec-dir status backfill** -- flip the 5-6 stale PI-7 spec-dir frontmatter
   `status: active -> done` (the carry deferred from Sprint 18); **(3) PI-7
   4-feature checklist backfill** -- tick the per-folder validation checklists for
   SDD-043/044/045/048 with real evidence from the sprint-close records (these
   features shipped and were validated at the time; the checkboxes are a
   data-hygiene backfill, NOT fabricated checkmarks); **(4) ADR-count correction**
   -- correct any lingering "24 ADRs" figure in live planning/audit text to **23
   ADRs (001-023)**. CLARIFY assigns per-item SDD-IDs as needed, each with its own
   `validation.md` from the audit Acceptance blocks.

**Closing Sprint 20 does NOT close PI-8.** Sprint 20's close produces a
sprint-close summary and continues PI-8 to Sprint 21; the PI-8 CLOSE is a
separate, owner-approved decision taken after the final PI-8 sprint.

Do NOT pull in any other PI-8 work: the Sprint 21 owner-pick slice (**SDD-049**
file-overlap detector or **SDD-041 Option B** reorder re-optimization) is NOT in
Sprint 20. **SDD-035** (Azure decommission) remains out-of-band.

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
- Human-facing output from the Sprint EM is **short and plain** (SDD-044). Save
  the detail for agent-to-agent handoffs.

PM + Architect own CLARIFY / SPEC / PLAN / TASKS for SDD-052 (including the
ADR-or-not decision on the roadmap edit and the closed-PI-semantics definition).
The Principal Software Developer owns implementation, QA, and the Sprint 20 close
(reporting up to the project EM through the Sprint EM).

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 20 must not start until all checks are true:

1. **Sprint 19 is CLOSED and pushed.** Confirm Sprint 19 (PI-8 Sprint 2,
   Doc-freshness sweep + stale-doc guard) CLOSED at commit `4feee24` (head
   `ed89193` or later, which records the push SHA) with SDD-051 (and any per-item
   IDs) marked DONE in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md), and that
   [`../sprints/PI-8/CURRENT_PI.md`](../sprints/PI-8/CURRENT_PI.md) marks PI-8
   **ACTIVE** (`status: active`).
2. **Tests are green at the Sprint 19 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **590 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
3. **Schema lint, origin lint, and the new stale-doc lint are clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0,
   `python spec-driven-development/cli/origin_lint.py` returns 0 hits in the
   generic framework files, and `python spec-driven-development/cli/staledoc_lint.py`
   (the guard shipped in Sprint 19) is green on the current tree.
4. **`doctor` is green and CI is green.** The health set passes: `doctor` reports
   green (including the new stale-doc check), and the GitHub Actions CI workflow
   (B-4) is green on the `4feee24` / `ed89193` head. The Article X lock guard
   (`TestS1FootprintLockGuard`) is PASS at this baseline.
5. **SDD-052 is filed and allocated to Sprint 20.** Confirm the SDD-052 row in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is OPEN (not DONE) and
   allocated to PI-8 Sprint 20.
6. **The audit spec source is present.** Confirm
   [`../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
   exists; SDD-052's per-item `validation.md` files are built from its Section 5
   "Acceptance (Roadmap)" block plus the Section 3 Defect-1(c) / Section 4
   stale-status findings.
7. **The live PI-7/PI-8 gates apply to Sprint 20.** The mandatory-ledger close
   gate (B-1) is LIVE -- Sprint 20's own dispatch outcomes must be logged in the
   ledger before Sprint 20 can be stamped DONE. The blocking checks (B-2: TDD
   gate + DONE-completeness) and CI (B-4) are LIVE -- Sprint 20 must pass them.
8. **Owner has approved the Sprint 20 start** (via the Executive Manager).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 20 on a
red test baseline (< 590), an unpushed/mismatched Sprint 19 (not closed at
`4feee24`), a red `doctor` / origin lint / staledoc lint / CI, a broken Article X
lock, a backlog that accidentally closed SDD-052, PI-8 not marked ACTIVE, or
without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. **Activate the Sprint Executive Manager agent** for this kickoff session.
4. Execute Sprint 20 in isolated feature sessions or Sprint-EM-routed subagent
   dispatches that preserve Article VII context isolation (fresh chat session OR
   subagent dispatch -- both satisfy the context-isolation property).
5. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only. Dogfood B-1: log this sprint's own dispatch outcomes before close.

PI-8 is already ACTIVE. There is no PI-activation step in Sprint 20; the
current-PI dispatch-rows check (B-1) is satisfied by logging Sprint 20's own
dispatches into the ledger.

---

## 1. Sprint goal

Sprint 20 ships **one anchor feature** (SDD-052) that finishes "dashboard truth."
After Sprint 20 the roadmap tells one story that agrees with itself and with the
dashboard: PI-6 exists, PI-7 is closed (not "current"), PI-8 has its own entry, a
written closed-PI convention says a closed PI renders 100% with its
deferred/carryover items tracked as carryover, the 5-6 stale PI-7 spec-dir
`status:` lines read `done`, and the 4 genuinely-DONE PI-7 features
(SDD-043/044/045/048) carry ticked per-folder checklists backed by their real
sprint-close evidence. The smoke test is the payoff: **the regenerated dashboard
renders all 6 PI-7 features (SDD-043..048) as DONE, PI-6 renders, every closed PI
is at 100%, PI-7 is not current, and PI-8 has a roadmap entry.**

### Scope

- **SDD-052 -- roadmap repair (`constitution/roadmap.md`)**:
  - Backfill the entirely-missing **PI-6 section** (headers currently jump
    PI-5 -> PI-7) in the PI-5 / PI-7 section shape, with a `(closed YYYY-MM-DD)`
    marker.
  - Fix the **PI-7 header self-contradiction**: `"(current, closed 2026-07-07)"`
    -> a clean closed marker with no "current."
  - Add a **PI-8 roadmap entry** so PI-8 does not repeat the PI-6 gap.
  - Define and apply **closed-PI semantics**: a closed PI renders done / 100% and
    its deferred/carryover items are tracked as carryover, not "incomplete."
    Write the convention down so it matches what SDD-050 reads (Sprint 18 already
    reads the `(closed)` marker defensively; this backfills the markers + PI-6
    that read depends on).
- **SDD-052 -- spec-dir status backfill**: flip the 5-6 stale PI-7 spec-dir
  frontmatter `status: active -> done` so `detect_stage()` sees them as done. The
  known dirs:
  [`../specs/2026-06-26-two-tier-executive-manager/`](../specs/2026-06-26-two-tier-executive-manager/)
  (SDD-043),
  [`../specs/2026-06-26-plain-language-comms-discipline/`](../specs/2026-06-26-plain-language-comms-discipline/)
  (SDD-044),
  [`../specs/2026-06-26-detach-clone-and-run-hardening/`](../specs/2026-06-26-detach-clone-and-run-hardening/)
  (SDD-045),
  [`../specs/2026-06-26-make-promises-true/`](../specs/2026-06-26-make-promises-true/)
  (SDD-046),
  [`../specs/2026-06-26-sdd-048-maintainability/`](../specs/2026-06-26-sdd-048-maintainability/)
  (SDD-048), and **check** the SDD-047 de-author dir -- confirm whether it is
  already `done` or is the sixth line. This backfill was deferred from Sprint 18
  (SDD-050) to here; it lands in **one place** (here), not both.
- **SDD-052 -- PI-7 4-feature checklist backfill (the ratified Sprint 18 carry)**:
  SDD-043/044/045/048 are genuinely DONE but their per-folder validation
  checklists were never ticked. Tick them with **real evidence** cross-referenced
  from the sprint-close records (Sprint 14 close for 043/044/045; Sprint 17 close
  for 048). This is a **data-hygiene backfill of a genuinely-done work item**, NOT
  a fabricated checkmark -- each ticked box points at the real close evidence.
  After this, the dashboard renders all 6 PI-7 features DONE.
- **SDD-052 -- ADR-count correction**: the live count is **23 ADRs (001-023)**,
  not 24. Correct any lingering "24 ADRs" figure in live planning/audit text
  (grep `24 ADR`). Do NOT rewrite frozen historical prompts (e.g. the Sprint 19
  kickoff is a historical record -- leave it); only correct live planning/audit
  text that a teammate reads as current.
- **Dogfood the live ledger gate**: the mandatory-ledger close gate (B-1) applies
  to **this sprint's own dispatches**. Sprint 20's own dispatch outcomes must be
  in the ledger before Sprint 20 can be stamped DONE.

### The roadmap edit is constitution-gated -- READ THIS

`constitution/roadmap.md` is a **`constitution/**` file (Article VIII)**. Editing
it is a gated change. Two things must be settled before any push:

- **ADR-or-not is an Architect decision at CLARIFY.** Precedent: PI-close ENTRIES
  in `roadmap.md` were added at prior PI closes **without** a separate ADR
  (treated as documentation-consistency, not a principle change). But a full PI-6
  backfill **plus a written closed-PI-semantics definition** is more substantial
  than a one-line close entry. The Architect decides at CLARIFY whether the
  Sprint 20 roadmap repair rises to an ADR (with a `roadmap.md` version bump) or
  is documentation-consistency like the prior close entries. Surface the call.
- **Owner approval before push is required regardless.** Because `roadmap.md` is
  `constitution/**`, recorded owner approval is mandatory before the roadmap edit
  is pushed, ADR or not. **No worker edits `roadmap.md` silently.** The edit lands
  in F-54 only after F-53 records the ADR-or-not decision and the owner-approval
  gate is set.

### Explicit exclusions

- **SDD-049** (true file-overlap detector) and **SDD-041 Option B** (reorder ->
  backend re-optimization) are the Sprint 21 owner-pick candidates and are NOT in
  Sprint 20.
- **PI-6 carryovers** (SDD-038 color tokens, SDD-034 dedup, PI-4 housekeeping,
  SDD-042 pill-nav, SDD-039 wording) are NOT in Sprint 20. Note: Sprint 20
  **backfills the PI-6 roadmap section** (a documentation fix) but does NOT
  implement the PI-6 carryover features.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 20 scope.
- **Article X locked render functions** are out of scope. SDD-052 touches
  `roadmap.md`, spec-dir frontmatter, per-folder checklists, and planning text; it
  does NOT touch `render_html`, `render_markdown`, or any locked function.
  `TestS1FootprintLockGuard` stays GREEN.
- **PI-8 close**: closing PI-8 is a separate owner-approved decision AFTER the
  final PI-8 sprint. Sprint 20 continues PI-8 to Sprint 21; it does not close
  PI-8.
- **Do NOT scrub history.** Sprint 20 backfills forward-looking status and
  checklists with real evidence; it does not rewrite historical `specs/`,
  `sprints/`, retros, or ADRs. A count or status inside a historical record stays
  as written.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-53: SDD-052 CLARIFY -> SPEC (per-item `validation.md`) -> PLAN -> TASKS (+ ADR if needed) | PM + Architect (design) | Design-first. CLARIFY assigns per-item SDD-IDs, builds each `validation.md` from the audit Section 5 "Acceptance (Roadmap)" + Section 4 / Section 3 Defect-1(c) blocks, **decides ADR-or-not on the roadmap edit** (Architect call; version bump if ADR), **defines closed-PI semantics** so the dashboard reader (SDD-050) and the roadmap agree, confirms the **4-feature checklist evidence source** (real sprint-close records -- not fabricated), confirms the **spec-dir status backfill happens here** (deferred from Sprint 18) and enumerates the exact 5 or 6 dirs, and pins the **"23 ADRs" correction locations** (grep `24 ADR`; live planning/audit text only, not frozen prompts). Sets the **owner-approval gate on the `roadmap.md` edit** (constitution/). |
| 2 | F-54: SDD-052 IMPLEMENT + QA | SW Dev + workers | Implement after the design locks and the ADR-or-not + owner-approval gate is set. Apply the roadmap repair (PI-6 section + PI-7 header fix + PI-8 entry + closed-PI convention), flip the 5-6 spec-dir `status:` lines to `done`, tick the SDD-043/044/045/048 per-folder checklists with real sprint-close evidence, and correct the "24 -> 23 ADRs" figure in live planning/audit text. Dogfood B-1: log this sprint's own dispatches. Pass the live B-2 (TDD gate + DONE-completeness) and B-4 CI gates. `TestS1FootprintLockGuard` stays GREEN; no locked function touched. The `roadmap.md` edit does NOT push without recorded owner approval. |
| 3 | F-55: Sprint 20 close | Sprint EM + SW Dev | Close Sprint 20, regenerate state, run the **6-features-DONE smoke test** (dashboard renders SDD-043..048 all DONE, PI-6 renders, every closed PI at 100%, PI-7 not current, PI-8 has a roadmap entry), request owner pre-push approval (mandatory for the constitution/ edit), mark SDD-052 (and the per-item IDs) DONE, and produce the sprint-close summary. The Sprint EM reports UP to the project Executive Manager and confirms PI-8 continues to Sprint 21. |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces a
file dependency graph that proves no two workers modify the same file. Shared
surfaces -- `constitution/roadmap.md`, any spec-dir frontmatter, any per-folder
checklist, generated exec surfaces, or shared spec artifacts -- force
serialization. (Note: the only conflict mechanism is the serial CLARIFY/SPEC gate;
there is no file-overlap detector -- SDD-049 remains a Sprint 21 candidate.)

---

## 3. Likely CLARIFY surfaces

### Q-A -- does the roadmap repair rise to an ADR? (Architect decides)

Decide whether the Sprint 20 `roadmap.md` repair is an ADR-level change (with a
`roadmap.md` version bump) or documentation-consistency like prior PI-close
entries. Precedent: PI-close entries were added at prior closes **without** a
separate ADR. But a full PI-6 backfill **plus a written closed-PI-semantics
convention** is more substantial. Default recommendation: the Architect treats the
**closed-PI-semantics definition** as the deciding factor -- if it codifies a new
rule the dashboard reader relies on, lean ADR + version bump; if it merely writes
down existing behavior, documentation-consistency may suffice. **Owner approval
before push is required either way** (roadmap is `constitution/**`). Surface the
call to the owner.

### Q-B -- closed-PI semantics definition (how a closed PI is marked)

Lock exactly how a closed PI is marked so the dashboard and any check agree:
which marker (`(closed YYYY-MM-DD)`) sits on the PI header, and the written rule
that a closed PI renders done / 100% with deferred/carryover items tracked as
carryover, not "incomplete." Default recommendation: match the marker SDD-050
already reads defensively (Sprint 18) so no `state_builder_data.py` change is
needed -- the roadmap backfills the data the reader already expects. Surface the
exact marker + convention text to the owner.

### Q-C -- the 4-feature checklist backfill evidence source (real, not fabricated)

Confirm the evidence source for ticking the SDD-043/044/045/048 per-folder
checklists: the **real sprint-close records** (Sprint 14 close for 043/044/045;
Sprint 17 close for 048), where these features were validated at the time. Default
recommendation: each ticked box cites its close-record evidence (commit SHA /
sprint-progress block) so the backfill is a **data-hygiene tick of genuinely-done
work**, auditable, not a fabricated checkmark. Surface the evidence mapping to the
owner.

### Q-D -- spec-dir status backfill happens here (deferred from Sprint 18)

Confirm the 5-6 PI-7 spec-dir `status: active -> done` backfill lands in Sprint 20
(SDD-052), not Sprint 18 -- it was deferred here at Sprint 18 CLARIFY. Enumerate
the exact dirs (two-tier-executive-manager, plain-language-comms-discipline,
detach-clone-and-run-hardening, make-promises-true, sdd-048-maintainability) and
**check** whether sdd-047-de-author is already `done` or is the sixth line.
Default recommendation: verify each dir's current `status:` at IMPLEMENT time
(some may already read `done`) and flip only the stale ones. Surface the final
dir list (5 or 6) to the owner.

### Q-E -- the "23 ADRs" correction locations

Pin where the "24 ADRs -> 23" correction applies. Default recommendation: grep
`24 ADR` across the repo and correct **only live planning/audit text** a teammate
reads as current; do NOT rewrite frozen historical prompts (the Sprint 19 kickoff
is a historical record -- leave it), and do NOT touch historical spec/retro text.
The live count is **23 ADRs (001-023)**. Surface the correction list to the owner.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** SDD-052 touches docs, frontmatter, checklists, and
  planning text; if any test or helper is added it uses argparse, sqlite3,
  pathlib, json, sys, os, re only. Sprint 20 adds NO third-party Python
  dependency.
- **Article X locked render functions are immutable.** Sprint 20 does NOT touch
  `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, or `load_decisions`. `TestS1FootprintLockGuard` stays
  GREEN. Touching a locked function is an Article X re-baseline (ADR + owner
  approval, Level-2) and is NOT expected for Sprint 20.
- **`roadmap.md` is `constitution/**` (Article VIII) -- gated.** The ADR-or-not
  call is an Architect decision at CLARIFY; recorded owner approval before push is
  mandatory regardless. No worker edits `roadmap.md` silently, and it is not
  pushed without the owner-approval gate satisfied.
- **The checklist backfill is real evidence, not fabricated.** Every ticked box on
  SDD-043/044/045/048 cites its sprint-close evidence. A tick with no traceable
  close evidence is a Level-1 review fail.
- **Do not regress the `doctor`/CI set.** After the backfill, the health set
  (including the Sprint 19 stale-doc check) stays green; the stale-doc guard goes
  RED only on a genuine stale claim, not on the corrected tree.
- **The live B-1 mandatory-ledger gate applies to THIS sprint.** Dogfood it:
  Sprint 20's own dispatch outcomes must be logged in the ledger before close.
- **The live B-2 blocking checks + B-4 CI apply.** Sprint 20 must pass the TDD
  gate and DONE-completeness checks and keep CI green; a change that breaks an
  enforced rule must fail loudly.
- **Spec source is authoritative but stale-checked.** Build SDD-052's per-item
  `validation.md` from the audit Section 5 / Section 4 / Section 3 Defect-1(c)
  blocks, but verify each finding against the live tree before acting (a status
  may already read `done`, a checklist may already be ticked). If an item is
  already satisfied on inspection, note it done and surface it -- do not silently
  drop or double-apply it.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it.
- **Plain human-facing language (SDD-044).** All human-facing output in this
  sprint (status, progress, questions to the owner) is short and plain;
  agent-to-agent detail may stay detailed. The Sprint EM holds this rule.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Do NOT scrub history.** Sprint 20 backfills forward-looking status/checklists
  with real evidence and repairs the live roadmap; it does not rewrite historical
  `specs/`, `sprints/`, retros, or ADRs, or frozen kickoff prompts.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory (and doubly so for the
  `roadmap.md` constitution edit).

---

## 5. Close criteria (Definition of Done)

Sprint 20 closes only when all are true:

1. **The 6-features-DONE smoke test passes**: the regenerated dashboard renders
   SDD-043, SDD-044, SDD-045, SDD-046, SDD-047, and SDD-048 as DONE.
2. **The roadmap tells one story**: `constitution/roadmap.md` has a PI-6 section
   with a closed marker (headers no longer jump PI-5 -> PI-7), the PI-7 header
   carries a clean closed marker (no "current"), a PI-8 section exists, and a
   written closed-PI convention exists that matches what SDD-050 reads.
3. **Every closed PI renders 100%**: on the regenerated dashboard PI-1..PI-7 each
   render done / 100%, PI-6 renders, and PI-7 is NOT flagged current.
4. **Spec-dir status backfilled**: the 5-6 stale PI-7 spec-dir frontmatter
   `status:` lines are `done` (backfilled here, one place, not also in Sprint 18).
5. **PI-7 4-feature checklists ticked with evidence**: SDD-043/044/045/048
   per-folder validation checklists are ticked, each box citing its real
   sprint-close evidence (not a fabricated checkmark).
6. **ADR count corrected**: live planning/audit text reads **23 ADRs (001-023)**;
   no live planning/audit text still says "24 ADRs" (frozen historical prompts
   left as-is).
7. All per-item REQUIRED validation items checked with real evidence (100%
   REQUIRED); manual checks checked at close.
8. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 590
   passed, 2 skipped (grows if a backfill test is added; must not regress).
9. Schema lint clean (exit 0), origin lint clean (0 hits in generic files), and
   the stale-doc lint green on the corrected tree.
10. **Article X lock held**: `TestS1FootprintLockGuard` PASS; `render_html` /
    `render_markdown` and the four locked load_* functions are byte-identical.
11. **`doctor` green and CI green**: the health set and the GitHub Actions
    workflow pass on the Sprint 20 head; the B-2 blocking checks pass.
12. **Ledger shows real Sprint 20 rows**: the dogfood holds -- Sprint 20's own
    dispatches are in the ledger and the B-1 close gate is satisfied.
13. SDD-052 (and any per-item SDD-IDs) marked DONE in BACKLOG with evidence.
14. **Owner pre-push approval recorded before any push** -- mandatory, and
    explicitly covers the `constitution/roadmap.md` edit (ADR-or-not per the
    CLARIFY decision).
15. **PI-8 continues to Sprint 21.** Sprint 20 does not close PI-8; the Sprint EM
    reports up to the project Executive Manager and confirms Sprint 21 is next.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 20 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Sprint Executive Manager (lead, reports up to project EM); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-53, F-54, F-55
- Commits: <commit SHAs>
- Tests: 590 -> <N> (>= 590 required; must not regress)
- Schema lint: clean; origin lint: 0 hits in generic files; stale-doc lint: green
- Validation: SDD-052 per-item <r>/<r> REQUIRED + manual checks
- Roadmap repair: PI-6 section backfilled (closed marker); PI-7 header fixed (no "current"); PI-8 section added; closed-PI convention written
- Roadmap edit gating: ADR-or-not <ADR-0NN + version bump | documentation-consistency, no ADR> (Architect call); owner approval recorded before push -- <YES>
- Spec-dir status backfill: <5 | 6> PI-7 dirs flipped active -> done: <list>
- PI-7 4-feature checklists ticked with evidence: SDD-043 (S14 close), SDD-044 (S14), SDD-045 (S14), SDD-048 (S17) -- <PASS | FAIL>
- ADR count corrected: 24 -> 23 in <locations | none remaining>; frozen prompts left as-is
- 6-features-DONE smoke test: dashboard renders SDD-043..048 all DONE, PI-6 renders, every closed PI 100%, PI-7 not current, PI-8 has roadmap entry -- <PASS | FAIL>
- Per-item SDD-IDs assigned for SDD-052: <list>
- Live gates satisfied: B-1 ledger dogfood (<N> real Sprint 20 rows), B-2 (TDD gate + DONE-completeness), B-4 CI green
- Article X lock: held (TestS1FootprintLockGuard PASS); render_html / render_markdown untouched
- History preserved: YES (no historical specs/sprints/retros/ADRs/frozen prompts rewritten)
- SDD-052: DONE (roadmap repaired + status backfilled + 4-feature checklists ticked + ADR count corrected)
- Deferred / out of scope: Sprint 21 owner-pick (SDD-049 or SDD-041 Option B), PI-6 carryovers, SDD-035 out-of-band
- PI-8 status: ACTIVE -- Sprint 20 CLOSED; continues to Sprint 21
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 20 lessons>
- Next: Sprint 21 (PI-8 Sprint 4 owner-pick: SDD-049 file-overlap detector OR SDD-041 Option B)
- Reported up to project EM: <YES + date | PENDING>
```

---

## 7. Do NOT do

- Do NOT close PI-8. Sprint 20 is the third PI-8 sprint; it continues PI-8 to
  Sprint 21. PI-8 CLOSE is a separate owner-approved decision after the final PI-8
  sprint.
- Do NOT edit `constitution/roadmap.md` silently. It is `constitution/**` (Article
  VIII): the ADR-or-not call is an Architect decision at CLARIFY, and recorded
  owner approval before push is mandatory regardless. The edit lands in F-54, not
  in this kickoff and not without the gate.
- Do NOT fabricate the PI-7 checklist ticks. Every box on SDD-043/044/045/048
  must cite real sprint-close evidence; the work is genuinely done -- the tick is
  a data-hygiene backfill, not an invented checkmark.
- Do NOT pull in SDD-049, SDD-041 Option B, or the PI-6 carryover features
  (backfilling the PI-6 roadmap section is in scope; implementing PI-6 carryover
  features is NOT).
- Do NOT edit, move, or rewrite the Article X locked functions (`render_html`,
  `render_markdown`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`). `TestS1FootprintLockGuard` stays
  GREEN.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT silently drop or double-apply a SDD-052 audit item; if a status already
  reads `done` or a checklist is already ticked, note it and surface it.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT skip the live B-1/B-2/B-4 gates: log Sprint 20's dispatches, pass the
  TDD gate + DONE-completeness checks, and keep CI green.
- Do NOT scrub or rewrite history; a count or status inside a historical record
  or a frozen kickoff prompt stays as written.
- Do NOT push without recorded owner approval (mandatory, and doubly so for the
  `roadmap.md` constitution edit).
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-052 spec dir here -- F-53 does that inside the Sprint 20
  working sessions.
- Do NOT edit `roadmap.md`, any spec-dir `status:` line, or any checklist in this
  kickoff -- those edits are F-54 inside the Sprint 20 working sessions.
- Do NOT have the Sprint EM create a sprint or PI (or author the next kickoff) --
  it may only SUGGEST to the project EM and reports up at close.
