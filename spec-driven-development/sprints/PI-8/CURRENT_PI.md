---
id: SDD-PI-8-CURRENT_PI-sprint
type: sprint
status: draft
owner: principal-product-manager
updated: 2026-07-08
sprint: PI-8
---

# PI-8: Truth in the Window

- Status: **QUEUED — drafted 2026-07-08 (owner-approved via Executive Manager:
  "yes, this is critical").** PI-8 opens when Sprint 18 (PI-8 Sprint 1) starts:
  the Sprint EM's FIRST act is to flip this marker's status field to `active`
  and log
  the first PI-8 ledger dispatch (dogfood the ledger — doctor's current-PI
  dispatch-rows check requires it). Until then PI-8 stays drafted so the
  post-PI-7-close interim invariant (no active PI, doctor green) holds. Follows
  PI-7 CLOSED 2026-07-07 / DONE-WITH-CARRYOVER (Sprint 17 close at `7088f35`).

- Theme: Make the human-facing surfaces (dashboard, onboarding docs, roadmap) as
  trustworthy as the engine. PI-7 hardened the engine — the ledger is real, the
  rules block, CI fires, identity is config, the god-module is split (558 tests,
  doctor green). But the window onto that engine lies: a closed feature reads
  REVIEW/IMPLEMENT on the dashboard, every closed PI shows a partial percentage,
  the onboarding docs are frozen at PI-3 with stale counts, and the roadmap is
  missing an entire PI (PI-6) while calling the just-closed PI-7 "current." PI-8
  fixes the window, not the engine.
- Drafted: 2026-07-08 (activation deferred to Sprint 18 open)
- Owner: principal-executive-manager
- Predecessor: PI-7 (Hardening + Orchestration Maturity) CLOSED 2026-07-07 as
  DONE-WITH-CARRYOVER at commit `7088f35`.
- Authorization: Owner approval 2026-07-08 via Executive Manager ("yes, this is
  critical"). Owner communication rule (still in force from 2026-06-26): all
  human-facing output (status, progress, questions to the owner) uses SHORT,
  PLAIN language; agent-to-agent detail is fine.
- Spec source for the PI-8 work: the tracked file
  [`../../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md`](../../docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md)
  (each defect's "Acceptance" block seeds that feature's `validation.md`), the
  same role `EMF-HARDENING-PLAN.md` played for PI-7.

---

## Goal

After PI-8 a human who opens the dashboard, reads the onboarding docs, or looks
at the roadmap sees the truth. A closed feature reads DONE. A closed PI reads
done / 100%, not a partial percentage. No session-start doc carries a stale PI
count, test count, or article count — and a `doctor` check keeps it that way. The
roadmap has no missing PI, no self-contradictory "current, closed" header, a
written closed-PI convention, and its own PI-8 entry. The engine and its window
finally agree.

---

## PI Objectives

### 1. Dashboard truth (SDD-050)
**Why**: Closed, DONE features render at an earlier lifecycle stage
(REVIEW/IMPLEMENT/TASKS) and closed PIs show partial percentages. Two detector
defects in `cli/state_builder_data.py`: (Defect 1) `detect_stage()` demands a
per-spec-dir `RETRO.md` this framework keeps at PI/sprint level, the validation
reader is blind to split `validation-*.md` files, and 5 of 6 PI-7 spec dirs still
carry status `active`; (Defect 2) percentage is `done/total` with no "closed"
concept, `is_current` matches `"(current, closed ...)"`, and PI-6 is missing from
the roadmap so it never renders.

**Success Criteria**: The regenerated dashboard renders SDD-043..048 as DONE
(smoke test); `detect_stage()` returns DONE for `status: done` with satisfied
validation and no per-dir retro; split `validation-*.md` files count; every
closed PI renders done / 100%; PI-7 is not flagged current; the dashboard "done"
definition and `cli/done_check.py` share one source of truth. `state_builder_data.py`
is a leaf module with NO Article X locked functions — `TestS1FootprintLockGuard`
stays GREEN and `render_html` / `render_markdown` are untouched.

**Feature**: SDD-050 (anchor). **Sprint**: 18 (PI-8 Sprint 1). **Spec source**:
`docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 3.

---

### 2. Doc-freshness sweep + automated stale-doc check (SDD-051)
**Why**: The docs a teammate reads first disagree with the repo.
`HIGH_LEVEL_DEV_TRACKER.md` is frozen at PI-3 / "60 tests" (worst — it is
onboarding read #3); `INSTRUCTIONS.md` and `ONBOARDING_KICK_OFF.md` say "10
articles" (it is 12); `CONTEXT.md` says "four Principal agents" (it is five roles
since the two-tier EM). `RULES.md` and root `README.md` are already clean.

**Success Criteria**: The four stale docs match the live repo (PI/test/article/
role counts); a new `doctor`/lint check flags stale PI/test/article claims in the
session-start docs and goes RED on a deliberate stale claim; `RULES.md` and root
`README.md` left unchanged.

**Feature**: SDD-051. **Sprint**: 19 (PI-8 Sprint 2). **Spec source**:
`docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 4.

---

### 3. Roadmap repair + status backfill (SDD-052)
**Why**: `constitution/roadmap.md` skips PI-6 entirely (headers jump PI-5 →
PI-7), calls PI-7 `"(current, closed 2026-07-07)"` (self-contradictory), and
leaves closed PIs with unchecked checkboxes the dashboard reads as "% complete."
Six spec-dir frontmatter `status:` lines that should be `done` still say `active`.

**Success Criteria**: `roadmap.md` has a PI-6 section with a closed marker; the
PI-7 header carries a clean closed marker; a written closed-PI convention exists
that matches what SDD-050 reads; the 6 spec-dir `status:` lines are `done`;
`roadmap.md` has a PI-8 section (so PI-8 does not repeat the PI-6 gap). The
`roadmap.md` edit is a `constitution/**` Level-2 change — ADR + recorded owner
approval + version bump.

**Feature**: SDD-052. **Sprint**: 20 (PI-8 Sprint 3). **Spec source**:
`docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` Section 5.

---

## Sprint Allocation

| Sprint | Overall | Title | Items | Size | Why this order |
|--------|---------|-------|-------|------|----------------|
| **PI-8 Sprint 1** | Sprint 18 | Dashboard truth (fix stale detectors) | SDD-050 (Defects 1 + 2) | M | Anchor. The dashboard is the most-looked-at human surface; a closed feature reading REVIEW is the loudest lie. Fix lives in the `state_builder_data.py` leaf module (lock-safe). Ships first so the rest of PI-8's changes render correctly as they land. |
| **PI-8 Sprint 2** | Sprint 19 | Doc-freshness sweep + stale-doc check | SDD-051 | S | Refresh the four session-start docs and add the `doctor`/lint check so the rot cannot return silently. Runs after the dashboard fix so the tracker refresh reflects an already-truthful dashboard state. |
| **PI-8 Sprint 3** | Sprint 20 | Roadmap repair + status backfill | SDD-052 | M | Backfill PI-6, fix the "current, closed" contradiction, define closed-PI semantics, backfill the 6 spec-dir `status:` lines, and add the PI-8 roadmap entry. Level-2 `constitution/**` edit (ADR + owner approval + version bump), so it lands after the non-gated work. |
| **PI-8 Sprint 4** | Sprint 21 | Owner-pick capacity slice | SDD-049 (P3 file-overlap detector) OR SDD-041 Option B (reorder → backend re-optimization) | — | Owner picks the final PI-8 slice from the standing candidates once the three truth features land. Not committed here. |

**IMPORTANT sequencing note (data-prerequisite):** SDD-052's roadmap PI-6
backfill + closed markers are a **data-prerequisite** for SDD-050's closed-PI
percentage fix — SDD-050 reads the `(closed)` marker and needs PI-6 in the
roadmap to render it. The **Architect must resolve this dependency at Sprint 18
CLARIFY**: either pull the roadmap-marker part of SDD-052 earlier, or have SDD-050
read closed-state **defensively** so Sprint 18 does not hard-block on Sprint 20.
This PI **adds its own PI-8 roadmap entry (in SDD-052)** so PI-8 does not repeat
the PI-6 gap.

**Unscheduled / carry-forward into PI-8 (candidates, not anchored here):**

- **SDD-049** — true file-overlap conflict detector (P3, filed 2026-06-26 from
  SDD-047 D-3). Sprint 21 candidate.
- **SDD-041 Option B** — reorder triggers backend re-optimization (PI-7
  carryover). Sprint 21 candidate.
- PI-6 carryovers (SDD-038 color tokens, SDD-034 dedup, PI-4 housekeeping,
  SDD-042 pill-nav, SDD-039 wording) remain triaged separately.
- **SDD-035** — Azure decommission remains out-of-band (worth a status re-check;
  not falsely DONE).

---

## Owner forks to resolve at the relevant sprint CLARIFY

1. **SDD-050 Defect-1 backfill placement** — do the 5 (or 6) stale
   status `active` → `done` spec-dir lines get backfilled in Sprint 18 (SDD-050)
   or with the roadmap/status backfill in Sprint 20 (SDD-052)? Resolve at
   **Sprint 18 CLARIFY**; do it in ONE place, not both.
2. **SDD-050 closed-PI dependency on SDD-052** — pull the roadmap-marker part of
   SDD-052 earlier, or have SDD-050 read closed-state defensively? Resolve at
   **Sprint 18 CLARIFY**.
3. **SDD-052 constitution edit** — the `roadmap.md` repair is Level-2; the ADR +
   owner approval + version bump are settled at **Sprint 20 CLARIFY**.
4. **Sprint 21 slice** — SDD-049 vs SDD-041 Option B; owner picks after the three
   truth features land.

---

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| SDD-050's closed-PI fix hard-blocks on SDD-052's roadmap PI-6 backfill (Sprint 20), stalling the Sprint 18 anchor | High | Medium | Owned | PM + Architect | Sprint 18 CLARIFY decides the dependency: either pull the roadmap-marker part of SDD-052 forward, or have SDD-050 read closed-state defensively so it ships without waiting on Sprint 20. |
| A dashboard detector change accidentally touches `render_html` / `render_markdown` or an Article X locked function | High | Low | Mitigated | SW Dev + Architect | The fix is scoped to `state_builder_data.py` (leaf module, NO locked functions); `TestS1FootprintLockGuard` is the guard and must stay GREEN; render modules are out of scope. |
| Refreshing docs to live counts (SDD-051) reintroduces new hardcoded counts that rot again | Medium | Medium | Mitigated | SW Dev | The stale-doc `doctor`/lint check is the mitigation — it goes RED on any future stale claim; model the "no hardcoded count" good pattern (root README.md) where practical. |
| The `roadmap.md` repair (SDD-052) is a `constitution/**` Level-2 edit done without the ADR / owner approval / version bump | High | Low | Owned | PM + Architect | Sprint 20 CLARIFY gates the edit behind an ADR + recorded owner approval + version bump; no silent constitution edit. |
| "Single source of truth for done" reconciliation between `detect_stage()` and `done_check.py` changes `done_check` behavior and breaks a live B-2 gate | Medium | Medium | Owned | SW Dev + Architect | Reconcile behind the existing tests; if `done_check.py` behavior must change, surface it at CLARIFY — it feeds the B-2 blocking check and cannot regress silently. |

---

## Dependencies

**Internal**:
- PI-7 close commit `7088f35` is the PI-8 base. Tests at 558 passed + 2 skipped
  is the floor; PI-8 must hold or improve this baseline.
- `docs/Temp/PI-8-TRUTH-IN-THE-WINDOW-AUDIT.md` is the spec source; each feature's
  `validation.md` is built from its "Acceptance" block.
- `cli/state_builder_data.py`: SDD-050 fixes `detect_stage()` + `load_pis` /
  current-PI here. Leaf module, NO Article X locked functions — the five locked
  functions and `TestS1FootprintLockGuard` golden hashes are immutable and out of
  scope.
- `cli/done_check.py`: SDD-050 reconciles the dashboard "done" definition with
  this (B-2 blocking check) — one source of truth.
- `constitution/roadmap.md`: SDD-052 backfills PI-6 + fixes PI-7 header + adds
  PI-8 — a Level-2 edit (ADR + owner approval + version bump). SDD-050 depends on
  its `(closed)` markers.
- `docs/HIGH_LEVEL_DEV_TRACKER.md`, `INSTRUCTIONS.md`, `docs/ONBOARDING_KICK_OFF.md`,
  `CONTEXT.md`: SDD-051 refreshes these; the stale-doc check watches them.
- The 6 PI-7 spec-dir frontmatter `status:` lines: backfilled in SDD-050 or
  SDD-052 (decided at Sprint 18 CLARIFY — one place).

**External**:
- None. PI-8 is entirely in-repo and stdlib-only (Article V).

---

## Success Metrics

- All three truth features (SDD-050/051/052) close DONE with full per-item
  validation contracts (100% REQUIRED each), tests at or above the 558 floor, and
  schema + origin lint clean.
- On the regenerated dashboard, SDD-043..048 render DONE and every closed PI
  (PI-1..PI-7) renders done / 100% — no closed PI shows a partial percentage and
  PI-7 is not flagged current.
- The four session-start docs match the live repo, and a teammate can add a stale
  count on purpose and watch the `doctor` check go red.
- `roadmap.md` has PI-6, a clean PI-7 closed marker, a written closed-PI
  convention, and a PI-8 entry; the 6 spec-dir `status:` lines are `done`.
- `doctor`, CI, schema lint, origin lint, and `TestS1FootprintLockGuard` are all
  green across the PI.

---

## PI-8 CLOSE

PI-8 CLOSE is a separate owner-approved decision taken AFTER the final PI-8
sprint closes, on a PI-8 close-readiness report — the same pattern as PI-7. No
sprint closes PI-8 automatically.
