---
id: SDD-PI-9-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-07-12
sprint: PI-9
---

# PI-9: Experience Polish

- Status: **ACTIVE; overall Sprint 24 ACTIVE/prepared (PI-9 Sprint 3), the final
  PI-9 sprint.** It is dedicated exclusively to SDD-058, the approved P1
  brownfield bootstrap correctness defect. Owner authorization 2026-07-12:
  "Owner approved Option 1 on 2026-07-12: authorize one final PI-9 sprint
  dedicated exclusively to the approved P1 brownfield bootstrap correctness
  defect, then close PI-9 after it ships." Overall Sprint 23 CLOSED (PI-9 Sprint
  2): SDD-038,
  SDD-056, and SDD-057 are DONE with 17/17 REQUIRED + 3/3 manual evidence,
  668 passed / 2 skipped, Article X held, and public doctor SUCCESS for
  `4e319fa`. PI-9 remains ACTIVE; no sprint beyond Sprint 24 and no successor PI
  is opened. Sprint 22
  CLOSED
  locally 2026-07-09 and shipped SDD-049 and SDD-054 with 616 passed / 2 skipped,
  clean schema/origin/staledoc lints, local doctor green, Article X 3/3 PASS, and
  PI-9 ledger rows 30-32 all success. The Sprint EM opened PI-9 in the same edit
  that closed PI-8 (exactly one `(current)` marker at a time). Follows PI-8 CLOSED
  2026-07-09 / DONE (Sprint 21 close at `07a2296`; PI-8 closed at Sprint 22 open).

- Theme: Finish PI-9 by pairing the shipped experience polish with trustworthy
  brownfield adoption. Sprints 22-23 delivered file-overlap protection, meaningful
  backlog reorder, and dashboard truth. The owner-authorized final sprint addresses
  the separately evidenced bootstrap correctness defect without reopening those
  completed features.
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

### Overall Sprint 24 -- ACTIVE / PREPARED (PI-9 Sprint 3, final)

- Sprint goal: make brownfield bootstrap safe and truthful so applying an edited
  proposal preserves human decisions, installs only reusable framework assets,
  creates host-specific identity/configuration and clean runtime state, and
  presents an honest host-readiness contract.
- Feature: SDD-058 only. Capacity: one full cross-cutting feature. Carry-over:
  none. Primary risk: changing refresh/copy/readiness semantics without a precise
  migration and safety contract.
- Scope: B1 edited-proposal preservation; B2 reusable-asset allowlist with no
  framework-state contamination; B3 host-specific `.github/copilot-instructions.md`
  plus `project.config.json`; B4 host-mode doctor or honest docs/contract.
- Sequence: CLARIFY -> SPEC/ADR -> PLAN/TASKS -> TDD IMPLEMENT/QA -> close.
  Article XI serial gates apply. No feature spec artifacts are created by this
  sprint-establishment update.
- Baseline: clean `d77d4ab == origin/master`; 668 passed / 2 skipped; public CI
  green. Owner pre-push approval remains mandatory.
- Exclusions: SDD-035 Azure decommission out-of-band; retro reconciliation as a
  separate cleanup; SDD-034; dashboards; all unrelated work.
- Close intent: when SDD-058 ships with all acceptance evidence and owner-approved
  push/public CI, Sprint 24 closes and the PI-9 close is then executed. PI-9 is
  ACTIVE now; this update does not close it.

### Overall Sprint 23 -- CLOSED

- Close gate: owner approved Option 1; prepared push completed; the first public
  run exposed a cross-platform wording-hash test defect, repaired at `4e319fa`;
  repaired public doctor run `29139276251` completed SUCCESS in 18s.
- Evidence: 17/17 REQUIRED + 3/3 manual; B-1/B-2/B-4 green; Article X held;
  full local suite 668 passed / 2 skipped / 6 subtests.
- PI status: PI-9 remains ACTIVE.
- Historical handoff: the Sprint 23 close authored no successor and reported the
  next-sprint decision upward. The owner subsequently authorized Sprint 24 on
  2026-07-12; the current-sprint section above records that separate decision.

---

## Goal

After PI-9, the shipped fleet and backlog improvements remain intact, the dashboard
reports current lifecycle truth, and brownfield bootstrap converts an approved
proposal into a clean host-specific installation without silent edit loss,
framework-state contamination, or a misleading readiness claim. The exact
refresh, copy, identity, and readiness contracts remain undecided until SDD-058
completes CLARIFY and its ADR-backed SPEC gate.

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

PI-9 closes after SDD-049, SDD-054, SDD-038, SDD-056, SDD-057, and final-sprint
SDD-058 are shipped with tests and evidence; the suite does not regress from
668 passed / 2 skipped; Article X and B-1/B-2/B-4 hold; public CI is green; and
the owner ratifies the close via the Executive Manager. SDD-058 must prove B1-B4
on clean representative Windows/POSIX host fixtures, including realistic
Node/Express and at least one cross-stack fixture, with migration/backward-
compatibility and dry-run/diff/backup safety covered. No destructive real-host
apply occurs without owner approval.

Sprint 22 local close evidence is complete: both features are DONE, the
dashboard/state surfaces show PI-9 current and both features DONE, 616 tests passed
/ 2 skipped, Article X held, local doctor is green, and ledger rows 30-32 are
success. CI and owner pre-push ratification remain pending; no pre-push CI result
is claimed. PI-9 remains current/active. Sprint 24 is the authorized final PI-9
sprint; no successor PI is created here.
