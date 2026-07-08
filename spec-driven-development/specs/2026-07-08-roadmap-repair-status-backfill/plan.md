---
id: SDD-20260708RMREPAIR-plan
type: plan
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-roadmap-repair-status-backfill
depends_on: [SDD-050]
---

# PLAN: SDD-052 -- Roadmap repair + status backfill

Implementation-oriented plan for F-54. This plan is authored at F-53 (design);
**no live artifact is edited during F-53.** Every step below runs in F-54, and
the constitution steps are blocked on the owner-approval gate.

---

## Gate summary (must clear before F-54 execution)

| Gate | Type | Blocks | Approver | Cleared by |
|------|------|--------|----------|-----------|
| G-1 ADR-024 ratification | adr-acceptance | Phase 2, Phase 4 | owner | Owner sets ADR-024 status to `accepted` |
| G-2 roadmap.md constitution edit | constitution-edit | Phase 2, Phase 4 | owner | Recorded owner approval quote before push (Article VIII) |

Phases 1 and 3 (status backfill, ADR-count verify) are Level-1 data hygiene and
do not require a gate; they are batched under the same F-54 approval for
coherence with the roadmap edit and to keep one atomic sprint deliverable.

---

## Phase 0 -- Pre-flight (F-54 start, read-only)

1. Re-read this plan, `spec.md`, `validation.md`, and audit Section 5 + Section 7.
2. Confirm owner approval for G-1 and G-2 is recorded (quote in sprint-progress).
   If not recorded: STOP. Do not touch `roadmap.md`.
3. Snapshot baseline: `python spec-driven-development/cli/schema_lint.py`
   (expect exit 0) and `python -m pytest spec-driven-development/cli -q`
   (record baseline count; must not decrease).

## Phase 1 -- SDD-052B status backfill (Level-1, no gate)

Flip the 24 stale `status: active` lines to `done` across the five closed PI-7
dirs (enumerated in `tasks.md` T-B1..T-B5). Leave SDD-047 untouched.

- Verify: `grep -rn "^status: active"` in the five dirs returns 0.
- Verify: schema-lint exit 0 (done is a valid enum value).

## Phase 2 -- SDD-052A + SDD-052C roadmap edit (Level-2, gated G-1 + G-2)

Serialized single-writer edit of `constitution/roadmap.md` (shared surface):

1. Insert the PI-6 section between PI-5 and PI-7, header
   `## PI-6: <title> (closed YYYY-MM-DD)`, matching PI-5 / PI-7 section shape.
2. Rewrite the PI-7 header from `(current, closed 2026-07-07)` to
   `(closed 2026-07-07)`.
3. Append a PI-8 section with header `## PI-8: <title> (current)`.
4. Add the "PI status conventions" note (SDD-052C, C-1) capturing the marker
   convention + carry-forward semantics.
5. Bump frontmatter `version: '1.1.0'` -> `version: '1.2.0'`.

- Verify: exactly one `(current` in PI headers; PI-6 + PI-8 present; no
  `(current, closed`.

## Phase 3 -- SDD-052D ADR-count verify (Level-1, no gate)

- `grep -rn "24 ADR" spec-driven-development/` restricted to live docs. Confirm
  no live forward-looking text asserts 24. Record result in `validation.md`
  D-1 evidence. No edit expected (SDD-051 already fixed).

## Phase 4 -- ADR-024 acceptance + close (gated G-1)

1. Owner flips `docs/ADR/024-closed-pi-roadmap-semantics.md` status
   `proposed` -> `accepted` with ratification note.
2. Flip this feature's own artifact `status:` lines to `done` at sprint close
   (spec, plan, tasks, validation; clarify already `done`).
3. Update `constitution/roadmap.md` PI-8 checklist for SDD-052 and record the
   close in `exec/sprint-progress.md` with the close commit SHA.

## Verification (F-54 exit)

- All AC-1..AC-7 in `validation.md` proven with real evidence.
- schema-lint exit 0; pytest count not decreased.
- `TestS1FootprintLockGuard` GREEN (no reader/Article X change).
- Owner approval recorded for G-1 and G-2 before push.

## Rollback

Every change is a text edit under git. Rollback = `git restore` the roadmap and
the 24 flipped files, and revert ADR-024 to `proposed`. No schema migration, no
data loss, no reader change to unwind.

## Effort

- Size: **S** (docs/data-only; 1 constitution file + 24 frontmatter lines + 1
  new ADR). No code. Risk concentrated in the Level-2 gate, not the edit.
