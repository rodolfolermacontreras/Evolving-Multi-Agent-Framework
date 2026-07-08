---
title: PI-8 Truth in the Window — Human-Facing Surface Audit
status: proposed
owner: principal-architect
audience: developers and agents working on the Evolving Multi-Agent Framework
created: 2026-07-08
source: full framework audit (2026-07-08, post-PI-7-close at 7088f35)
---

# PI-8 Truth in the Window — Audit

This is the authoritative spec source for PI-8, the same role
[`EMF-HARDENING-PLAN.md`](EMF-HARDENING-PLAN.md) played for PI-7. Each defect
below carries root causes, fix scope, and an Acceptance block. Sprint sessions
build each per-item `validation.md` from the matching Acceptance block. No emojis
(Rule 1).

---

## 1. Bottom line up front

PI-7 hardened the engine: the ledger is real, the rules that matter block, CI
fires for everyone, identity is config, and the god-module is split. The suite is
558 passed / 2 skipped; `doctor` is green; schema + origin lint are clean.

But the **human-facing surfaces lie about that healthy engine**. A closed feature
reads as REVIEW or IMPLEMENT on the dashboard. Every closed PI shows a partial
percentage. The onboarding docs a teammate reads first are frozen at PI-3 with
"60 tests" and "10 articles" (it is 12). The roadmap is missing an entire PI (PI-6)
and calls the just-closed PI "current."

Nothing here is an engine defect. The engine is right; the window onto it is wrong.
PI-8 makes the dashboard, the onboarding docs, and the roadmap as trustworthy as
the engine — so a closed feature reads DONE, and no session-start doc carries a
stale count.

**Scope note (lock-safety):** the dashboard detector bugs live in
`cli/state_builder_data.py`, a leaf module split out of `state_builder.py` in PI-7
(SDD-048). It holds **no Article X locked functions** — the five locked functions
(`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
`load_decisions`) stay in their modules. Fixes in `state_builder_data.py` are
lock-safe: `TestS1FootprintLockGuard` must stay GREEN and `render_html` /
`render_markdown` are not touched.

---

## 2. Definition of done for PI-8

PI-8 is complete when all three are true and provable:

- **Dashboard truth:** every DONE feature renders as DONE on the regenerated
  dashboard (SDD-043..048 are the smoke test), and every closed PI renders as
  done / 100% — no closed PI shows a partial percentage.
- **Doc freshness:** the four session-start docs
  (`HIGH_LEVEL_DEV_TRACKER.md`, `INSTRUCTIONS.md`, `ONBOARDING_KICK_OFF.md`,
  `CONTEXT.md`) match the live repo, and a `doctor`/lint check flags any future
  stale PI / test-count / article-count claim so the rot cannot return silently.
- **Roadmap truth:** the roadmap has no missing PI section (PI-6 backfilled),
  no self-contradictory "current, closed" header, defined closed-PI semantics,
  and its own PI-8 entry — and the six spec-dir frontmatter `status:` lines that
  should be `done` are `done`.

---

## 3. Dashboard defects (`cli/state_builder_data.py`)

### Defect 1 — DONE features render as REVIEW / IMPLEMENT / TASKS

**Symptom:** features that are closed and marked DONE in the backlog render on the
dashboard at an earlier lifecycle stage (REVIEW, IMPLEMENT, or TASKS) instead of
DONE.

**Root causes:**

- **(a) RETRO requirement mismatch.** `detect_stage()` demands a per-spec-dir
  `RETRO.md` before it will call a feature DONE. This framework keeps retros at
  the **PI / sprint level**, not per spec dir, so done features are silently
  downgraded one stage.
- **(b) Validation reader is blind to split validation files.** The validation
  reader only reads a file literally named `validation.md`. Many features split
  validation into per-item files (`validation-A2.md`, `validation-C1.md`, etc.),
  which the reader never sees — so it reports validation as incomplete and the
  stage never advances to DONE.
- **(c) Stale frontmatter.** 5 of the 6 PI-7 spec dirs still carry frontmatter
  `status: active` — they were never flipped to `done` at close. Even a correct
  detector reads them as in-flight.

**Fix scope:**

- Drop the per-spec-dir `RETRO.md` requirement for `status: done` — treat a spec
  dir whose frontmatter says `done` (with its validation satisfied) as DONE
  regardless of a per-dir retro, since retros live at PI/sprint level here.
- Glob `validation*.md` (not just the literal `validation.md`) so split
  per-item validation files count toward completeness.
- Backfill the 5 stale `status: active` → `done` lines (decide at CLARIFY whether
  this backfill lands here in SDD-050 or with the roadmap/status backfill in
  SDD-052; do not do it in both).
- **Single source of truth for "done":** reconcile `detect_stage()` with
  `cli/done_check.py` so the dashboard and `doctor` agree on what "done" means —
  one definition, read by both.

**Acceptance (Defect 1):**
- The regenerated dashboard renders SDD-043, SDD-044, SDD-045, SDD-046, SDD-047,
  and SDD-048 as DONE (the smoke test).
- `detect_stage()` returns DONE for a spec dir with `status: done` and satisfied
  validation, with NO per-dir `RETRO.md` present.
- A feature that split validation into `validation-*.md` files reads as
  validation-complete (the glob works).
- The 5 stale `status: active` PI-7 spec-dir lines are `done` (here or tracked to
  SDD-052 — not left ambiguous).
- The dashboard "done" definition and `done_check.py` reference a single shared
  helper / definition; a feature that is DONE in one is DONE in the other.
- `TestS1FootprintLockGuard` PASS; `render_html` / `render_markdown` untouched.

### Defect 2 — closed PIs show a partial percentage

**Symptom:** closed PIs render partial completion (PI-1 33%, PI-2 67%, etc.)
instead of done / 100%, and the just-closed PI-7 is flagged as "current."

**Root causes:**

- **No concept of "closed."** `pct = done / total` counted over checkboxes, with
  no notion that a PI can be closed with deferred/carryover items left unchecked.
  A closed PI with any unchecked (deferred) box therefore reads as partial.
- **`is_current` too naive.** `is_current = "(current" in title`. PI-7's title is
  `"(current, closed 2026-07-07)"` — the substring `(current` matches, so a
  **closed** PI is flagged as current.
- **PI-6 missing from the roadmap.** The roadmap headers jump PI-5 → PI-7, so
  PI-6 never renders at all (see Roadmap defects).

**Fix scope:**

- Read the `(closed YYYY-MM-DD)` marker on a PI header: a PI carrying a closed
  marker renders as **done / 100%** regardless of unchecked deferred/carryover
  boxes.
- Harden `is_current` so `"(current, closed ...)"` does NOT count as current —
  a closed marker wins over the `current` substring.
- Depend on the roadmap PI-6 backfill (SDD-052) for PI-6 to render at all.
  **Dependency:** SDD-052 supplies the roadmap data (PI-6 section + closed
  markers) that this fix reads. Resolve the ordering at Sprint 18 CLARIFY — either
  pull the roadmap-marker part of SDD-052 earlier, or have SDD-050 read
  closed-state defensively so it does not hard-block on SDD-052.

**Acceptance (Defect 2):**
- Every closed PI (PI-1..PI-7) renders as done / 100% on the regenerated
  dashboard — no closed PI shows a partial percentage.
- PI-7 (`"(current, closed 2026-07-07)"`) is NOT flagged as the current PI.
- Once SDD-052 backfills PI-6, PI-6 renders (done / 100%).
- The closed-PI reader tolerates a roadmap that has not yet been backfilled
  (defensive read) OR the CLARIFY dependency decision is recorded.
- `TestS1FootprintLockGuard` PASS.

---

## 4. Doc staleness

The docs a teammate reads at session start disagree with the live repo. Worst
offenders first.

| Doc | Stale claim | Truth (2026-07-08) | Severity |
|-----|-------------|--------------------|----------|
| `docs/HIGH_LEVEL_DEV_TRACKER.md` | Frozen at PI-3; "60 tests" | 7 PIs closed; 558 tests | HIGH (onboarding read #3) |
| `INSTRUCTIONS.md` | "10 articles" | 12 articles | Medium |
| `docs/ONBOARDING_KICK_OFF.md` | "10 articles" | 12 articles | Medium |
| `CONTEXT.md` | "four Principal agents" | five roles (two-tier EM added the Sprint EM) | Medium |
| `docs/RULES.md` | — (B-3 fix landed; says I–XII) | correct | CLEAN — leave |
| root `README.md` | — (no hardcoded counts) | correct — good pattern | CLEAN — leave |

**Fix scope:**

- Refresh the four stale docs to the live counts (PIs closed, test count, article
  count, principal/role count).
- **Prevent recurrence:** add a `doctor` / lint check that flags stale PI /
  test-count / article-count claims in the session-start docs, so they cannot rot
  silently again. Model the "no hardcoded count" good pattern (root `README.md`)
  where practical.

**Acceptance (Doc staleness):**
- `HIGH_LEVEL_DEV_TRACKER.md`, `INSTRUCTIONS.md`, `ONBOARDING_KICK_OFF.md`, and
  `CONTEXT.md` match the live repo (PI count, test count, article count, role
  count).
- A new stale-doc `doctor`/lint check exists, is wired into the `doctor` set, and
  goes RED when a session-start doc carries a stale PI/test/article claim (proven
  by a deliberate red).
- `RULES.md` and root `README.md` are left unchanged (already clean).

---

## 5. Roadmap defects (`constitution/roadmap.md`)

**Note:** `roadmap.md` is a `constitution/**` file. Editing it is a Level-2
change requiring an ADR + recorded owner approval + version bump. SDD-052 carries
that gating.

**Defects:**

- **PI-6 section entirely MISSING.** The roadmap headers jump PI-5 → PI-7; there
  is no PI-6 section. Confirmed. This is why the dashboard cannot render PI-6.
- **PI-7 header self-contradiction.** The PI-7 header reads
  `"(current, closed 2026-07-07)"` — a PI cannot be both current and closed.
- **Closed PIs carry unchecked checkboxes.** Deferred/carryover items on closed
  PIs are left unchecked, and the dashboard reads those as "% complete" (this is
  the roadmap-side cause of Defect 2).

**Fix scope:**

- Backfill the missing PI-6 section (matching the PI-5 / PI-7 section shape) with
  a `(closed YYYY-MM-DD)` marker.
- Fix the PI-7 header to a clean closed marker (drop "current").
- Define **closed-PI semantics**: a closed PI renders done / 100% and its
  deferred/carryover items are tracked as carryover, not as "incomplete" — write
  this convention down so the dashboard reader (SDD-050) and the roadmap agree.
- Backfill the 6 spec-dir `status: active` → `done` frontmatter lines (the 5 from
  Defect 1(c) plus any sixth surfaced at CLARIFY), if not already done in SDD-050.
- **Add PI-8's own roadmap entry** — so PI-8 does not repeat the PI-6 gap.

**Acceptance (Roadmap):**
- `roadmap.md` has a PI-6 section with a closed marker; headers no longer jump
  PI-5 → PI-7.
- The PI-7 header carries a clean closed marker (no "current").
- A written closed-PI convention exists and matches what SDD-050 reads.
- The 6 spec-dir frontmatter `status:` lines are `done`.
- `roadmap.md` has a PI-8 section.
- The `roadmap.md` edit is under an ADR + recorded owner approval + version bump.

---

## 6. Backlog (clean — note only)

The backlog is honestly tracked; nothing is falsely DONE (good). One status
re-check is worth doing but is not a defect: **SDD-035 (Azure decommission)** is
still "Pending Level-2 approval" — worth confirming its current status, but it is
not falsely marked done and is out-of-band for PI-8.

---

## 7. Fix-scope summary (seeds the PI-8 backlog rows)

| Item | Defect | Fix scope | Sprint |
|------|--------|-----------|--------|
| SDD-050 | Dashboard Defects 1 + 2 | `state_builder_data.py` `detect_stage()` (drop per-dir RETRO for `status:done`; glob `validation*.md`) + `load_pis`/current-PI (read `(closed)` marker → done/100%; harden `is_current`); single source of truth for "done" (reconcile with `done_check.py`) | S18 (anchor) |
| SDD-051 | Doc staleness | Refresh HIGH_LEVEL_DEV_TRACKER / INSTRUCTIONS / ONBOARDING / CONTEXT; add a stale-doc `doctor`/lint check | S19 |
| SDD-052 | Roadmap defects | Backfill PI-6; fix PI-7 "current, closed"; define closed-PI semantics; backfill 6 spec-dir `status:active`→`done`; add PI-8 roadmap entry (Level-2 ADR + owner approval) | S20 |

**Sequencing:** SDD-052's roadmap PI-6 backfill + closed markers are a
data-prerequisite for SDD-050's closed-PI percentage fix. The Architect resolves
the ordering at Sprint 18 CLARIFY (pull the roadmap-marker part earlier, or have
SDD-050 read closed-state defensively so it does not block on S20).
