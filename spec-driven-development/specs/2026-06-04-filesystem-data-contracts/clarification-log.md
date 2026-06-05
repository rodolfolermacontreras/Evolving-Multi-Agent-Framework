# Clarification Log: Sprint 4 -- Filesystem Data Contracts

- Date: 2026-06-04
- Participants: Rodolfo Lerma (owner), Principal Product Manager
- Status: in-progress
- Triage: P2 / HITL / Clarify (see triage 2026-06-04)
- Locked constraint (from request): Do NOT modify `render_html()` or the four data-layer
  functions (T-001..T-004) shipped in commit b7ce642. The S1 footprint is locked.

---

## Scope (one line)

Establish filesystem data contracts for Sprint 4: a YAML frontmatter schema, a
schema-lint extension to enforce it, a doc-count rollup, a commit-message
convention, and a new `count` subcommand in `cli/state_builder.py`.

---

## Q1: [Scope] Artifact classes + required field set

Question: Which artifact classes get the new frontmatter contract, and what is the
exact required field set?
Recommended answer: Apply to `specs/**` and `sprints/**` markdown first (the artifacts
the dashboard rolls up), with required fields: `id`, `type`, `status`, `owner`,
`updated`. Leave `docs/**` and constitution files out of scope for Sprint 4.
Why this matters: This defines the lint surface and the count keys. Going too broad
(all `.md`) risks touching the locked S1 footprint indirectly and balloons effort
from L to XL; too narrow makes the rollup uninteresting.
Answer: Accepted. Apply to `specs/**` and `sprints/**` markdown. Required fields:
`id`, `type`, `status`, `owner`, `updated`. `docs/**` and constitution out of scope
for Sprint 4.
Status: answered

## Q2: [Decisions] Rollup semantics + `count` output contract

Question: What does the doc-count rollup count, and what does `count` emit?
Recommended answer: Roll up artifact counts grouped by `status` and by `type`, scoped
per sprint. `count` emits JSON to stdout by default (machine contract for the
dashboard) with a `--format table` human option. JSON shape:
`{ "by_status": {...}, "by_type": {...}, "total": N }`.
Why this matters: The output is a data contract the dashboard depends on. Locking the
JSON shape now prevents a breaking change later and keeps `count` decoupled from the
locked `render_html()`.
Answer: Accepted. Rollup groups by `status` and by `type`, scoped per sprint.
`count` emits JSON to stdout by default, shape
`{ "by_status": {...}, "by_type": {...}, "total": N }`, with `--format table`
human option. `count` reads frontmatter independently; never calls locked S1 code.
Status: answered

## Q3: [Context] Commit-message convention -- documented vs enforced

Question: Is the commit-message convention documentation-only, or enforced via a hook?
Recommended answer: Sprint 4 ships documentation + an OPT-IN `commit-msg` hook script
that contributors install manually; no auto-install, no CI gate yet. Enforcement is a
separate, later HITL decision.
Why this matters: A repo-wide enforced hook is shared infra (Level 2 / human approval).
Keeping Sprint 4 documentation + opt-in avoids an irreversible change and keeps the
sprint AFK-able after clarify.
Answer: Accepted. Sprint 4 ships documentation + an opt-in `commit-msg` hook script
(manual install). No auto-install, no CI gate. Mandatory enforcement deferred as a
separate later HITL decision.
Status: answered

## Decisions Made

- **D1 (Scope):** Frontmatter contract applies to `specs/**` and `sprints/**` markdown
  only. Required fields: `id`, `type`, `status`, `owner`, `updated`. `docs/**` and
  constitution out of scope for Sprint 4.
- **D2 (Rollup/count):** Doc-count rollup groups artifacts by `status` and by `type`,
  scoped per sprint. New `count` subcommand emits JSON to stdout by default
  (`{ "by_status": {...}, "by_type": {...}, "total": N }`) with a `--format table`
  option. `count` parses frontmatter independently and never calls the locked S1 code.
- **D3 (Commit convention):** Documentation + opt-in `commit-msg` hook script only.
  No auto-install, no CI gate in Sprint 4. Mandatory enforcement is a later HITL/Level-2
  decision.
- **D4 (Lock):** `render_html()` and the four data-layer functions (T-001..T-004) from
  commit b7ce642 are immutable for this feature. New code is additive only.
- **D5 (JSON scoping, confirmed 2026-06-05):** `count` default output is the FLAT global
  rollup `{ "by_status": {...}, "by_type": {...}, "total": N }` (stable contract). An
  optional `--sprint <id>` selector narrows to one sprint without changing the top-level
  shape; an optional `by_sprint` key may be added for the grouped view. Resolves the
  AC-3-vs-D2 tension surfaced in Architect review.

## Spec Impact

- Scope section -- artifact classes + field set (Q1)
- Requirements section -- rollup semantics + `count` JSON contract (Q2)
- Constraints section -- S1 lock (b7ce642) + commit-convention enforcement boundary (Q3)
