---
id: SDD-20260708DASHBOARDTRUTH-retro
type: retro
status: done
owner: principal-software-developer
updated: 2026-07-08
feature: 2026-07-08-dashboard-truth
depends_on: [SDD-046]
---

# RETRO: SDD-050 -- "Dashboard truth"

- Feature ID: SDD-050. Sprint: PI-8 Sprint 18.
- Spec: [spec.md](spec.md). Plan: [plan.md](plan.md). Tasks: [tasks.md](tasks.md). Validation: [validation.md](validation.md).

---

## What shipped

- Defect 1: `detect_stage` rewritten evidence-first in `cli/state_builder_data.py`; `cli/done_check.py` widened to glob `validation*.md` and expose a shared validation-completeness reader. Test arc 558 -> 571.
- Defect 2: `PIBlock.is_closed` + `pct`=100-when-closed; `load_pis` closed detection; `_pi_number` helper; `current_pi` newest-open-PI fallback. Test arc 571 -> 576.
- Full suite 576 passed / 2 skipped. Lock guard 3/3. `schema_lint` exit 0. `origin_lint` clean.

## Deviations (delegated autonomy)

- On `master`: work was performed on `master` per explicit owner delegation ("owner unavailable, full autonomy; do NOT push, do NOT flip the PI marker"). Normally the mode stop-condition forbids `master` work; the brief overrides it. All changes left in the working tree for the Sprint EM to stage/commit. Reported as a deviation.
- Q-A backfill 5 -> 0 (evidence-justified): the CLARIFY default anticipated backfilling five stale `spec.md` status lines. A real `detect_stage` run on 2026-07-08 (after the new glob reader) showed the backfills are unnecessary and contrary to intent -- the evidence-first label surfaces truth from the checked REQUIRED boxes, so relabeling the input status line is both redundant and against the "show truth, do not relabel" principle. STEP D skipped. Parked as Optional O-1 in validation.md (named, not silently dropped).

## Audit corrections (prediction reversals)

- (a) Article X locked set is 5, not 6: `render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`. `render_markdown` is NOT in `LOCKED_S1_FUNCTIONS` and is not locked (though it was not modified either).
- (b) sdd-048-maintainability is 0/19 REQUIRED -- NOT done. An earlier "shipped -> force DONE" prediction was WRONG; it was based on the old `done_check` reading only `validation.md`. With the glob reader, its four split validation files (C1/C2/C3/D2) aggregate to 0/19 REQUIRED checked. It correctly stays IMPLEMENT. DA-Evidence Discipline caught this before a false DONE shipped.
- (c) make-promises-true was already DONE via the evidence-first Step 1 (validation required-complete), not via any status backfill. No hand-edit applied.
- (d) sdd-047-de-author was already correctly DONE via its split validation files once the glob reader landed.
- (e) The three 0%-carryover PI-7 features (detach-clone-and-run-hardening, plain-language-comms-discipline, two-tier-executive-manager) and azure-decommission correctly render in-progress (IMPLEMENT); cross-feature-dedup and serial-clarify-spec-gate correctly render REVIEW with parked DEFERRED items.

## Smoke Test (dashboard regeneration)

- Command: `python spec-driven-development/cli/state_builder.py` (no `--pi`), 2026-07-08.
- DONE set observed: make-promises-true, sdd-047-de-author.
- In-progress set observed: sdd-048-maintainability (IMPLEMENT 0/19), azure-decommission (IMPLEMENT), detach-clone-and-run-hardening (IMPLEMENT 0%), plain-language-comms-discipline (IMPLEMENT 0%), two-tier-executive-manager (IMPLEMENT 0%).
- Closed PIs: PI-1..PI-5, PI-7 render at 100%.
- Header: resolves to the newest open PI (PI-7; PI-6 is a roadmap gap), never PI-1.

## Ledger

- PI-8 dogfood dispatch row logged for the Fleet-eligible task T-050-02 (`fleet.py dispatch` + `fleet.py mark ... success`). PI marker NOT flipped; activation is the Sprint EM's job.
- Real dispatch id: 22 (pi=PI-8, task=T-050-02, agent=principal-software-developer, role=software-developer, outcome=success, dispatched_at=2026-07-08T15:47:23Z). Verified via `fleet.py status --feature spec-driven-development/specs/2026-07-08-dashboard-truth`.
- Note: the dashboard's "Dispatches in ledger" counter reports a scoped slice (10), not the raw row count; row 22 persists in `ledger/fleet.db` and is confirmed by `fleet.py status`. This is pre-existing dashboard behavior, not a SDD-050 regression.

## Lessons

- DA-Evidence Discipline is load-bearing: the real `detect_stage` run reversed a would-be false DONE for sdd-048 (0/19). Never promote a predicted stage; run the production entry point and read the artifacts.
- Evidence-first beats status-line-first: the strongest signal (checked REQUIRED boxes) should drive the label, not the weakest (prose status line). This also removed the need for status backfills.
- Widen readers carefully: the `validation*.md` glob was the single change that made split-validation features count correctly for BOTH the label and the gate -- one reader, no divergence.
