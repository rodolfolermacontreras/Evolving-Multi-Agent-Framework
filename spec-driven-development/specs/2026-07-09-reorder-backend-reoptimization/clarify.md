---
id: SDD-20260709REOPT-clarify
type: clarification
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-reorder-backend-reoptimization
---

# CLARIFY: SDD-054 -- Backlog reorder -> backend re-optimization (SDD-041 Option B)

- Feature ID: SDD-054 (PM-assigned fresh ID for SDD-041 Option B, per kickoff Q-D)
- Sprint: PI-9 / Sprint 1 (Sprint 22); design + implementation F-61
- Predecessor: SDD-041 Option A (PI-6 Sprint 13) shipped the in-browser drag +
  safeguarded `move()` + `reorder-audit.jsonl` + dependency-lock (ADR-017).

---

## Questions, recommendations, answers

### Q-D -- backend surface + ID
- Question: what is the exact "prioritization/optimization logic on the backend"
  the drag should feed, and what ID does Option B take?
- Recommendation: extend the existing `move()`/audit path (not a new module); PM
  assigns the next free ID (SDD-054).
- Answer (owner default, "jump to these two"): **extend `cli/backlog_reorder.py`
  `move()` + audit; ID = SDD-054.** The drag now also produces a persisted backend
  priority artifact `backlog/effective-priority.json`, computed under the SAME
  dependency-lock + audit governance as the display overlay.
- Status: RESOLVED.

### Q-semantics -- what does "re-optimization" mean (honest, no over-claim)
- Question: how should the manual drag interact with the RICE priority so this is
  a real re-optimization and not a relabelled display overlay?
- Answer: **the manual drag order is the PRIMARY signal, made dependency-legal**
  (an item is demoted below any incomplete dependency it would otherwise outrank,
  reusing the Option A dependency check) **and emitted as a scored, RICE-annotated
  ranking** (`priority_score` descending by effective rank; `rice_priority`
  recorded as secondary context). **BACKLOG.md RICE scores are NOT mutated**
  (ADR-017 held). This is the concrete difference from Option A: Option A wrote a
  display-only overlay the backend never saw; Option B produces a
  dependency-corrected, scored priority ranking the backend consumes via
  `effective_priority_order()`.
- Status: RESOLVED.

### Q-lock -- Article X impact
- Answer: **No locked function touched.** All work is in `cli/backlog_reorder.py`,
  a leaf module with no Article X locked render/load function.
  `TestS1FootprintLockGuard` stays GREEN.
- Status: RESOLVED.

### Q-level -- decision level
- Answer: **Level-1, no ADR, no `constitution/**` edit, no version bump.** Builds
  additively on ADR-017's accepted machinery; introduces no new governance rule.
  Stdlib-only (Article V). Architect-confirmed.
- Status: RESOLVED.

---

## Lock

CLARIFY closed at F-61 design. `validation.md` is LOCKED; implementation must
satisfy every REQUIRED item with evidence.
