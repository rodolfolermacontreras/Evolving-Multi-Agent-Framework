---
id: SDD-20260708RMREPAIR-clarify
type: clarification
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-roadmap-repair-status-backfill
---

# CLARIFY: SDD-052 -- Roadmap repair + status backfill

CLARIFY closed at F-53 design. Every answer is backed by real evidence from the
live tree (DA-Evidence discipline: cite real commit SHAs and file state, no
fabricated conclusions). Five questions were resolved.

---

## Q-A -- ADR or plan-only for the closed-PI convention?

**Question:** The audit says the `roadmap.md` edit must be "under an ADR + owner
approval + version bump." Does the closed-PI semantics decision warrant a full
ADR, or can it be recorded in `plan.md`?

**Decision: ADR-024.**

**Justification:** Closed-PI semantics form a durable cross-surface data contract
that binds the roadmap format (`constitution/roadmap.md`) to the dashboard reader
(`cli/state_builder_data.py::load_pis`). This is directly analogous to ADR-012
(filesystem-frontmatter-data-contract), which the framework already treats as
ADR-worthy. The audit's own "Acceptance (Roadmap)" names "edit under an ADR +
version bump," and a `constitution/**` edit that introduces a new written
convention warrants an ADR + owner ratification per Article VIII and ADR-006.

- Title: **"Closed-PI roadmap semantics and marker convention."**
- Filename: `docs/ADR/024-closed-pi-roadmap-semantics.md`.
- Status at F-53: **draft** (proposed). Owner ratifies at F-54.
- Roadmap version bump: **1.1.0 -> 1.2.0** (MINOR -- additive PI-6/PI-8 sections
  + convention note, no breaking change), per ADR-006 semantic versioning.
- ADR count today: 23 (001-023 + TEMPLATE). Next is **024** -- confirmed by
  listing `docs/ADR/`.

---

## Q-B -- Exact closed-PI marker text and convention

**Question:** What is the exact marker string and the one-sentence convention,
and does it require a reader change?

**Decision:** Marker text `(closed YYYY-MM-DD)` appended to the PI section header.

- Example: `## PI-6: <title> (closed 2026-06-26)`.
- Convention (one sentence): *Exactly one PI header carries `(current)`; every
  completed PI header carries `(closed YYYY-MM-DD)` and renders 100% on the
  dashboard regardless of unchecked carry-forward boxes; the two markers are
  never combined as `(current, closed ...)`.*
- This matches the established convention already used by PI-4 `(closed
  2026-06-06)` and PI-5 `(closed 2026-06-09)`.

**Reader change: NONE.** `cli/state_builder_data.py::load_pis` (read lines
200-290) computes:

- `is_closed = "closed" in low`
- `is_current = ("(current" in low) and not is_closed`
- `pct` returns 100 when `is_closed`.

"closed" wins over "current," so a header carrying `(closed ...)` renders 100%
and is not treated as current. The reader is already defensive. This also fixes
the PI-7 header contradiction for free: once PI-7 reads `(closed 2026-07-07)`
with no "current," the reader renders it 100% and stops treating it as current.
No Article X locked function is involved.

---

## Q-C -- Four-feature box -> evidence mapping (why PI-7 renders 100%)

**Question:** The roadmap PI-7 section shows unchecked carry-forward boxes. What
real evidence proves the four PI-7 sprint features are genuinely done, so the
closed marker is honest?

**Answer:** All four are closed with real commit evidence in
`exec/sprint-progress.md`:

- **Sprint 14 (SDD-043/044/045):** CLOSED 2026-06-26, close commit `ecd13b3`;
  test count 481 -> 501; ADR-020 Accepted (owner "accept and approve"); SDD-043
  11/11 REQUIRED, SDD-044 7/7, SDD-045 17/17.
- **Sprint 15 (SDD-046):** CLOSED 2026-06-26, commit `44d546d`; 501 -> 518;
  19/19 REQUIRED; ADR-021 supersedes ADR-009.
- **Sprint 16 (SDD-047):** CLOSED, commit `e93862d`; 518 -> 540; ADR-022.
- **Sprint 17 (SDD-048):** CLOSED 2026-07-07, close commit `71bba51`; 540 -> 558;
  C-1 7/7 + C-2 4/4 + C-3 4/4 + D-2 4/4 REQUIRED; ADR-023 Accepted (owner
  "approve!").
- **PI-7 close:** 2026-07-07, DONE-WITH-CARRYOVER; owner "lets close, but lets
  do it right"; PI-7 push commit `7088f35`.

The unchecked boxes are the three carry-forward items re-homed into PI-8; they
are honest carryover, not incomplete work. The closed-PI convention (C-1)
explains them; they are NOT ticked (see non-goals).

---

## Q-D -- Status-backfill flip list

**Question:** Exactly which spec-dir frontmatter `status:` lines flip to `done`?

**Answer:** Five dirs flip (SDD-043/044/045/046/048); SDD-047 is already fully
`done`. The true per-artifact surface is **24 `status: active` lines** (grep of
`^status:\s*\w+` across the six PI-7 dirs returned 36 matches):

- SDD-043 `two-tier-executive-manager`: spec, plan, tasks, validation -> 4
  (clarify already done).
- SDD-044 `plain-language-comms-discipline`: spec, plan, tasks, validation -> 4
  (clarify already done).
- SDD-045 `detach-clone-and-run-hardening`: spec, plan, tasks, validation -> 4
  (clarify already done).
- SDD-046 `make-promises-true`: spec, plan, tasks, validation -> 4 (clarify
  already done).
- SDD-048 `sdd-048-maintainability`: clarify, spec, plan, tasks, validation-C1,
  validation-C2, validation-C3, validation-D2 -> 8 (all active).
- SDD-047 `sdd-047-de-author`: 0 -- all 8 artifacts already `done` (no-op).

The audit named "6 spec-dir status lines" at DIR granularity; the sixth it
hedged about is SDD-047, which is already done. The per-artifact truth is 24
lines across 5 dirs. Terminal `status` for all artifact types is `done` (Sprint 4
FDC backfill precedent).

---

## Q-E -- Live "24 ADRs" locations

**Question:** Where does live text still assert "24 ADRs," and what must change?

**Answer:** NONE remaining in live planning/audit text. SDD-051 (Sprint 19)
already corrected the session-start docs to 23 ADRs (asserted in SDD-051
`validation-051A.md` line 30). The only literal "24 ADRs" assertions live in the
frozen historical `SPRINT-19-KICKOFF.prompt.md` (EXCLUDE -- frozen).
`SPRINT-20-KICKOFF.prompt.md` and `feature-prompts/README.md` reference the
correction TASK, not asserting 24 as truth. SDD-052D is therefore a verification
(confirm 23, no live edit) -- surfaced as "already satisfied."
