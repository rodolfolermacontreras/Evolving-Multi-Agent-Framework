---
id: SDD-PI-9-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-07-10
sprint: PI-9
---

# PI-9: Experience Polish

- Status: **ACTIVE; overall Sprint 23 ACTIVE (PI-9 Sprint 2).** F-63 design is
  complete; F-64 dashboard truth and F-65 lifecycle/wording implementation + QA
  are complete locally; F-66 close package is next. This marker records the
  current sprint gate and does not claim Sprint 23 close. The prior gate was
  F-64 implementation + QA after F-63 design. Sprint 22 CLOSED
  locally 2026-07-09 and shipped SDD-049 and SDD-054 with 616 passed / 2 skipped,
  clean schema/origin/staledoc lints, local doctor green, Article X 3/3 PASS, and
  PI-9 ledger rows 30-32 all success. The Sprint EM opened PI-9 in the same edit
  that closed PI-8 (exactly one `(current)` marker at a time). Follows PI-8 CLOSED
  2026-07-09 / DONE (Sprint 21 close at `07a2296`; PI-8 closed at Sprint 22 open).

- Theme: Turn two long-standing quality-of-life gaps into shipped features. PI-8
  made the window onto the engine tell the truth; PI-9 polishes the experience of
  using the framework. The fleet gets an automated pre-dispatch file-overlap check
  (replacing the manual per-worker file-scope discipline), and dragging a backlog
  item to a new position re-optimizes the priority order on the backend instead of
  only persisting the visual arrangement.
- Drafted: 2026-07-09 (activated same day at Sprint 22 open)
- Owner: principal-executive-manager
- Predecessor: PI-8 (Truth in the Window) CLOSED 2026-07-09 as DONE at the start
  of Sprint 22.
- Authorization: Owner approval 2026-07-09 via Executive Manager ("jump to these
  two"), carried in the Sprint 22 kickoff. Owner communication rule (in force from
  2026-06-26, structured by SDD-053): all human-facing output uses SHORT, PLAIN
  language and every owner decision uses the DECISION-REQUEST FORMAT; agent-to-agent
  detail is fine.

---

## Current sprint

### Overall Sprint 23 -- ACTIVE

- Current gate: F-65 implementation + two-stage QA complete locally.
- Next gate: F-66 close package -- remaining close validation, manual UX checks,
  owner pre-push approval, public CI, and Sprint 23 close.
- PI status: PI-9 remains ACTIVE.
- Close state: not closed; no implementation outcome is claimed by this update.

---

## Goal

After PI-9 the fleet no longer relies on manual per-worker file scopes to avoid
same-file dispatch conflicts — an automated detector reads each worker brief's
declared IN-scope file set and blocks (or warns) when two briefs in the same batch
intersect. And a backlog reorder is no longer cosmetic — dragging an item to a new
position feeds the new order into the backend prioritization/optimization logic,
not just the display-order overlay, on the same safeguarded `move()` + audit-trail
machinery (ADR-017).

---

## PI Objectives

### 1. File-overlap conflict detector (SDD-049) -- DONE
**Why**: Today `cli/fleet.py` performs only the serial CLARIFY/SPEC gate
(`_scan_lock_state`, SDD-019). Avoiding same-file dispatch within a batch is a
manual discipline (explicit per-worker file scopes), not an automated check — the
honest placeholder left when the "conflict detection" over-claim was removed from
`GENERALIZATION_SDD.md` + `constitution/roadmap.md` (SDD-047 D-3).

**Success Criteria**: A real pre-dispatch check reads each worker brief's declared
IN-scope file set and blocks (or warns) when two briefs in the same batch
intersect, with tests. Lives in `cli/fleet.py` — a leaf CLI with NO Article X
locked function; `TestS1FootprintLockGuard` stays GREEN. Stdlib-only; TDD
(failing test first). Block-vs-warn behavior fixed at CLARIFY.

**Feature**: SDD-049 (anchor). **Sprint**: 22 (PI-9 Sprint 1).

---

### 2. Backlog reorder → backend re-optimization (SDD-054) -- DONE
**Why**: SDD-041 Option A (PI-6 Sprint 13) shipped a real in-browser drag that
round-trips through the safeguarded `move()` and persists a display-order overlay.
The order is visual only — it does not feed the backend prioritization logic.

**Success Criteria**: When a backlog item is dragged to a new position, the new
order feeds the backend prioritization/optimization logic, not only the
display-order overlay — built on the existing safeguarded `move()` +
`reorder-audit.jsonl` + dependency-lock machinery (ADR-017), same audit trail,
same governance. Confirmed at CLARIFY to touch NO Article X locked render/load
function (`TestS1FootprintLockGuard` stays GREEN). The PM assigns Option B a fresh
SDD-ID at CLARIFY. Stdlib-only; TDD.

**Feature**: SDD-054 (PM-assigned ID for SDD-041 Option B). **Sprint**: 22
(PI-9 Sprint 1).

---

## Close criteria

PI-9 closes when SDD-049 and SDD-041 Option B are both shipped with tests and
evidence, the dashboard shows PI-9 current and both features DONE, the suite does
not regress (>= 596 passed, 2 skipped, growing with the new feature tests), the
Article X render lock holds, `doctor` + CI are green, and the owner ratifies the
close via the Executive Manager.

Sprint 22 local close evidence is complete: both features are DONE, the
dashboard/state surfaces show PI-9 current and both features DONE, 616 tests passed
/ 2 skipped, Article X held, local doctor is green, and ledger rows 30-32 are
success. CI and owner pre-push ratification remain pending; no pre-push CI result
is claimed. PI-9 remains current/active and no next sprint or PI is created here.
