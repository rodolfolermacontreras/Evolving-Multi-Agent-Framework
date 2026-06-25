# SPRINT 13 KICKOFF -- PI-6 Sprint 4 / True drag + PI-label fix + Article VII wording (PI-6 close)

You are leading **Sprint 13**, which is **PI-6 Sprint 4** and the **final PI-6
sprint** -- the "value sprint" that closes PI-6. Your job is to ship the three
remaining high-value PI-6 items and leave PI-6 ready to close:

1. **SDD-042** (smallest, ships first): fix the dashboard PI-label parser so the
   `exec/state.html` / `exec/state.md` header stops printing a stale
   `Current PI: PI-5` and instead surfaces the newest ACTIVE PI (PI-6). Same
   parser-lag class SDD-040 already fixed for active-focus, but on the PI-label
   line. Restores dashboard trust before the other two land.
2. **SDD-041**: true browser drag-and-drop backlog reorder, built ON TOP of the
   SDD-036 safeguard machinery (`depends_on` frontmatter, dependency-lock,
   append-only `reorder-audit.jsonl`, force-as-Level-2 governance / ADR-017).
   Vanilla JS drag/drop events only (Article V); keyboard reorder stays as the
   accessible fallback.
3. **SDD-039**: Article VII wording clarification -- amend the Article VII
   corollary in `principles.md` plus the four SPRINT-04..07 kickoff prompts and
   the kickoff template to say "fresh chat session OR subagent dispatch -- both
   satisfy the context-isolation property." This is a constitution edit:
   it **requires an ADR (Article VIII) + recorded owner approval + a
   `principles.md` version bump**.

Do not absorb **SDD-038** (aesthetic lifecycle color tokens), **SDD-034**
(content-shingle dedup), or **PI-4 housekeeping** (domain-skill annotations, GH
Actions Node.js bump) -- those are **deferred to PI-7 hardening** and must not be
pulled into Sprint 13. Do not touch Azure decommission work (SDD-035). PI-7 is a
separate, later increment, not part of this close.

You are the **Principal Executive Manager** for this kickoff. PM + Architect own
CLARIFY/SPEC/PLAN/TASKS for all three features. The Principal Software Developer
owns implementation, QA, and the Sprint 13 close. PI-6 CLOSE is a **separate,
owner-approved decision** taken AFTER Sprint 13 closes -- closing Sprint 13 does
not automatically close PI-6.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 13 must not start until all checks are true:

1. **Sprint 12 is closed and pushed at `84db2de`.** Confirm HEAD / `origin/master`
   is at commit `84db2de`
   (`chore(sdd-037): close Sprint 12 -- SDD-037 DONE, PI-6 sprint allocation + close block`),
   that [`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md) marks
   PI-6 Sprint 3 / Sprint 12 **CLOSED**, still marks PI-6 **ACTIVE**, and names
   Sprint 13 as the next (final) planned sprint.
2. **Sprint 12 close is recorded.** Confirm
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) contains a
   `### Sprint 12 -- CLOSED` block with owner ratification
   `APPROVED FOR COMMIT + PUSH` and the commit SHA `84db2de`.
3. **Tests are green at the Sprint 12 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   **450 passed** with the known **2** platform-conditional skips. Run from the
   repo root, not from inside `spec-driven-development/`.
4. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
5. **SDD-037 is DONE in BACKLOG** with evidence (450 passed / 2 skipped, schema
   lint clean, 13/13 REQUIRED, Article X lock held, dashboard smoke). Confirm the
   SDD-037 row in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) reads
   **DONE** 2026-06-25.
6. **SDD-041, SDD-042, and SDD-039 remain open and allocated to Sprint 13.**
   Confirm those three rows in [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md)
   are open (not DONE) and allocated to PI-6 Sprint 13.
7. **SDD-038, SDD-034, and PI-4 housekeeping remain deferred to PI-7.** Confirm
   none of SDD-038, SDD-034, or PI-4 housekeeping (domain-skill annotations, GH
   Actions Node.js bump) is pulled into Sprint 13.
8. **Owner has approved the Sprint 13 start** (the PI-6-closing value sprint).
9. **The dashboard surfaces SDD-042 and SDD-041 build on exist.** After
   `python spec-driven-development/cli/state_builder.py`,
   [`../exec/state.html`](../exec/state.html) must render the SDD-036 lifecycle
   pipeline, the SDD-037 Dispatches card + health pills, and must reproduce the
   stale `Current PI: PI-5` header (that is the SDD-042 defect to fix).

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 13 on a
red test baseline (< 450), an unpushed/mismatched Sprint 12 (not at `84db2de`),
a backlog that accidentally closed SDD-041/042/039 or pulled in the PI-7-deferred
items, or without recorded owner approval to start.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 13 in isolated feature sessions or EM-routed subagent
   dispatches that preserve Article VII context isolation. Do not ask the owner
   to open another session when subagent dispatch gives equivalent isolation and
   the owner has approved that execution shape. (SDD-039 is the feature that
   makes this equivalence explicit in the constitution; until it ships, follow
   the existing corollary while honoring the owner's approved execution shape.)
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 13 ships **three features** that deliver the remaining PI-6 value and
leave PI-6 ready to close: restore dashboard PI-label trust (SDD-042), deliver
true mouse drag-and-drop reorder on the existing safeguard machinery (SDD-041),
and make the Article VII context-isolation principle explicit so subagent
dispatch is a first-class alternative to a fresh session (SDD-039).

### Scope

- **SDD-042 (F-30)**: fix the PI-detection heuristic in `cli/state_builder.py`
  so the dashboard header surfaces the newest ACTIVE `CURRENT_PI.md` (PI-6)
  instead of a stale `PI-5`. Additive and lock-surface-safe.
- **SDD-041 (F-31)**: add a browser drag/drop UI layer ON TOP of the SDD-036
  reorder safeguards -- same `reorder-audit.jsonl` audit trail, same
  `depends_on` dependency-lock, same force-as-Level-2 path -- mouse-driven
  instead of keyboard-driven. Keyboard control remains the accessible fallback.
- **SDD-039 (F-32)**: amend the Article VII corollary in
  `constitution/principles.md` and the four SPRINT-04..07 kickoff prompts plus
  the kickoff template to say "fresh chat session OR subagent dispatch -- both
  satisfy the context-isolation property." Requires an ADR and a `principles.md`
  version bump.
- **Prompts/docs in scope**: the three SDD spec dir artifacts, the SDD-039 ADR,
  the Sprint 13 close block, and PI-6 close-readiness recording.

### Explicit exclusions

- **SDD-038** (aesthetic lifecycle color tokens), **SDD-034** (content-shingle
  dedup), and **PI-4 housekeeping** (domain-skill annotations, GH Actions
  Node.js bump) are **deferred to PI-7 hardening**. They are NOT in Sprint 13.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 13 scope.
- **PI-6 close**: closing PI-6 is a separate owner-approved decision after the
  Sprint 13 close. Sprint 13 leaves PI-6 ready-to-close; it does not close it.
- **Constitution edits beyond SDD-039**: the only permitted `constitution/**`
  change is the SDD-039 Article VII wording amendment, and only with an ADR +
  recorded owner approval + version bump. No other constitution edits.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-30: SDD-042 CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT + QA | PM + Architect (design); SW Dev + workers (impl) | Smallest, highest-trust-restoring fix. Ships first so the dashboard header is correct before the other two land. Must be lock-surface-safe: do not touch Article X locked fns. |
| 2 | F-31: SDD-041 CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT + QA | PM + Architect (design); SW Dev + workers (impl) | True drag builds on the SDD-036 safeguard machinery already shipped. Larger UI surface; sequence after the cheap fix lands. Use the UI Lifecycle Variant if CLARIFY confirms iterative UI validation. |
| 3 | F-32: SDD-039 CLARIFY -> ADR -> SPEC -> IMPLEMENT (wording) + owner approval | PM + Architect (ADR + wording); SW Dev (apply) | Constitution edit. Author the ADR and get recorded owner approval BEFORE amending `principles.md`, the four kickoff prompts, the template, and bumping the `principles.md` version. |
| 4 | F-33: Sprint 13 close + PI-6 close-readiness | SW Dev + EM | Close Sprint 13, regenerate state, request owner pre-push approval, mark SDD-041/042/039 DONE, and record PI-6 as ready-to-close (the PI-6 CLOSE decision itself is a separate owner-approved step). |

The default is sequential. Fleet dispatch is allowed only after CLARIFY produces
a file dependency graph that proves no two workers modify the same file. Shared
`cli/state_builder.py` (SDD-042 + SDD-041 both touch the dashboard generator),
`constitution/principles.md`, generated exec surfaces, or shared spec artifacts
force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- SDD-042 PI-detection signal source

Lock where the PI label comes from. Default recommendation: derive the dashboard
PI label from the newest ACTIVE `sprints/PI-N/CURRENT_PI.md` (the highest N
marked ACTIVE), not from roadmap or sprint frontmatter that lags. Decide
backwards-compat behavior when no `CURRENT_PI.md` is ACTIVE (fall back to the
prior heuristic, not to a hard-coded value).

### Q-B -- SDD-042 lock-surface safety

Confirm the fix is additive and does NOT modify any Article X locked function
(`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
`load_decisions`). If the stale PI label currently flows through a locked
function, the fix must compute the correct value in a new helper and feed it in
before render (the SDD-036 `inject_*` pattern), keeping the golden SHA-256 hashes
in `TestS1FootprintLockGuard` byte-identical.

### Q-C -- SDD-041 drag mechanism (HTML5 drag/drop vs pointer events)

Decide the browser mechanism. Default recommendation: native HTML5 drag-and-drop
events (`dragstart`/`dragover`/`drop`) in vanilla JS (Article V; no framework).
If CLARIFY finds HTML5 DnD too coarse for the reorder affordance, pointer events
are the fallback -- still vanilla JS. Decide the visual affordance (drag handle,
drop-target highlight).

### Q-D -- SDD-041 mapping to the safeguard machinery

Confirm the drop action maps onto the existing SDD-036 reorder path: it calls the
same `backlog_reorder.py` `move()` logic, writes the same append-only
`reorder-audit.jsonl` record (from-rank / to-rank / reason), and respects the
`depends_on` dependency-lock (cycle-creating drops greyed-out / rejected with a
tooltip). No new reorder code path; the drag UI is a new front-end onto the
existing safeguarded operation.

### Q-E -- SDD-041 accessibility parity and force-override UX

Confirm the keyboard reorder controls remain a fully working accessible fallback
(no regression). Decide the force-override UX for a dependency-blocked drop: a
blocked drop must NOT silently succeed; force is a Level-2 escalation (ADR-017),
surfaced explicitly to the human, never auto-applied by the drag gesture.

### Q-F -- SDD-039 exact Article VII text + ADR + version bump level

Lock the exact wording change to the Article VII corollary and confirm the ADR is
required (it is -- this is a constitution edit under Article VIII). Decide the
`principles.md` semver bump level (recommend a minor bump: clarifying an existing
principle's wording without changing its intent). Enumerate every file touched:
`constitution/principles.md`, SPRINT-04/05/06/07 kickoff prompts, and the kickoff
template. Recorded owner approval is mandatory before applying any of it.

---

## 4. Hard constraints

- **Stdlib-only (Article V).** `cli/**` uses argparse, sqlite3, pathlib, json,
  sys, os only. SDD-041's drag layer is vanilla JS in the generated HTML -- no
  third-party JS framework, no new Python dependency.
- **Article X locked render functions are immutable.** Do NOT edit `render_html`,
  `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or
  `load_decisions`. SDD-042's PI-label fix and SDD-041's drag wiring must be
  additive (`inject_*` / helper pattern). `TestS1FootprintLockGuard` golden
  SHA-256 hashes must still PASS.
- **Constitution edit is gated.** The ONLY permitted `constitution/**` change is
  the SDD-039 Article VII wording amendment, and only after an ADR is authored
  AND owner approval is recorded AND the `principles.md` version is bumped. No
  other constitution edits.
- **Reuse the safeguard machinery.** SDD-041 reuses `backlog_reorder.py`,
  `reorder-audit.jsonl`, `depends_on`, and the ADR-017 force-as-Level-2 path. Do
  not fork or reimplement the reorder logic.
- **No new gates / no silent REQUIRED deferral.** Do not defer a REQUIRED
  validation item silently; surface it. Drag affordances are UI, not blocking
  gates.
- **Append-only ledger.** Report progress in `exec/sprint-progress.md`
  append-only. Never rewrite prior blocks.
- **Git discipline.** Explicit path staging only. Never `git add -A` or
  `git add .`. Pre-push owner approval is mandatory.

---

## 5. Close criteria (Definition of Done)

Sprint 13 closes only when all are true:

1. **SDD-042 implemented**: the dashboard header surfaces the newest ACTIVE PI
   (PI-6); the stale `Current PI: PI-5` no longer renders.
2. **SDD-041 implemented**: mouse drag-and-drop reorder works in the browser,
   writes the `reorder-audit.jsonl` record, respects `depends_on` dependency-lock,
   routes force as a Level-2 escalation, and keyboard reorder still works.
3. **SDD-039 implemented**: the Article VII corollary in `principles.md` and the
   four SPRINT-04..07 kickoff prompts + the kickoff template read "fresh chat
   session OR subagent dispatch -- both satisfy the context-isolation property";
   the ADR is committed; owner approval is recorded; `principles.md` version is
   bumped.
4. All three features' REQUIRED validation items checked with real-run evidence
   (100% REQUIRED); manual/tone checks checked at close.
5. Tests: `python -m pytest spec-driven-development/ --tb=no -q` returns >= 450
   passed, 2 skipped (the Sprint 12 baseline), and grows with the SDD-042,
   SDD-041, and SDD-039 tests.
6. Schema lint clean (exit 0).
7. Article X lock held (`TestS1FootprintLockGuard` PASS).
8. Dashboard smoke: regenerated `exec/state.html` shows the correct PI label and
   the drag-enabled reorder UI; 0 unexpected `<script>` injection beyond the
   intended vanilla drag JS.
9. SDD-041, SDD-042, and SDD-039 marked DONE in BACKLOG with evidence.
10. Owner pre-push approval recorded before any push.
11. **PI-6 recorded as ready-to-close.** The PI-6 CLOSE itself is a SEPARATE
    owner-approved decision taken after this close; Sprint 13 does not close PI-6.

---

## 6. Reporting template (append to exec/sprint-progress.md at close)

```markdown
### Sprint 13 -- CLOSED
- Date: <YYYY-MM-DD>
- Owner: Principal Executive Manager (lead); PM + Architect owned design + ADR; SW Dev + workers owned implementation and close
- Features completed: F-30, F-31, F-32, F-33
- Commits: <commit SHAs>
- Tests: 450 -> <N> (>= 450 required)
- Schema lint: clean
- Validation: SDD-042 <r>/<r> + SDD-041 <r>/<r> + SDD-039 <r>/<r> REQUIRED + manual checks
- ADRs: <ADR-018 SDD-039 Article VII wording> (required)
- principles.md version: <old> -> <new> (SDD-039 bump)
- PI-6 status: ACTIVE -> READY TO CLOSE (PI-6 CLOSE is a separate owner-approved decision)
- SDD-042: DONE (dashboard PI-label parser fix)
- SDD-041: DONE (true browser drag-and-drop reorder)
- SDD-039: DONE (Article VII wording clarification + ADR + version bump)
- Dashboard smoke: PASS (correct PI label; drag-enabled reorder)
- Deferred to PI-7: SDD-038 + SDD-034 + PI-4 housekeeping; SDD-035 out-of-band
- Owner ratification: <APPROVED FOR COMMIT + PUSH | LOCAL CLOSE PREP ONLY>
- Notes: <one paragraph Sprint 13 lessons>
- Next: PI-6 close decision (separate owner-approved step); PI-7 hardening kickoff
```

---

## 7. Do NOT do

- Do NOT close PI-6 automatically. PI-6 CLOSE is a separate owner-approved
  decision taken after Sprint 13 closes.
- Do NOT pull in SDD-038, SDD-034, or PI-4 housekeeping -- those are deferred to
  PI-7 hardening.
- Do NOT touch Azure decommission (SDD-035) or any cloud reference.
- Do NOT edit the Article X locked render functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`).
- Do NOT edit `constitution/**` except the SDD-039 Article VII wording, and only
  with an authored ADR + recorded owner approval + `principles.md` version bump.
- Do NOT add third-party dependencies; SDD-041's drag layer is vanilla JS.
- Do NOT let a dependency-blocked drag silently succeed; force is Level-2.
- Do NOT silently defer a REQUIRED validation item.
- Do NOT push without recorded owner approval.
- Do NOT use `git add -A` / `git add .`; stage explicit paths only.
- Do NOT scaffold the SDD-041/042/039 spec dirs here -- F-30/F-31/F-32 do that
  inside the Sprint 13 working sessions.
