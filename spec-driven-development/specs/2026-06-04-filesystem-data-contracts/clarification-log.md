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

## Q5: [Amendment] R5/AC-5 lock anchor re-anchored b7ce642 -> 257b081

Date: 2026-06-06
Participants: Rodolfo Lerma (owner, ratifying), Principal Architect (drafting), Principal Executive Manager (routing), Principal Software Developer (blocked-finding)
Authority: Article X amendment (validation contract change, pre-implementation, with owner ratification)

### Question

R5 (and AC-5) requires `render_html` and T-001..T-004 to be byte-identical to commit
`b7ce642`. Hash verification at /implement time (T-FDC-02 lock guard) shows two of
the five functions already diverged before the spec was authored. What is the
correct anchor SHA?

### Finding

Independently verified via `git log b7ce642..257b081 -- spec-driven-development/cli/state_builder.py`:
nine commits intentionally evolved `state_builder.py` during Sprint 3 (the dashboard
v3.0 rewrite plus a sqlite resource-leak fix), all landing 2026-06-02 -- three days
before the FDC spec was committed (2026-06-05, `58f3af3`). Two functions are
affected: `render_html` (rewrite `a16819a`) and `load_decisions` (fix `86748f3`).
The other three are unchanged.

Hash evidence:

| function | b7ce642 hash | 257b081 hash | match |
|---|---|---|---|
| render_html | ff94e248a81459703c27526029ade0cc0d96de2b3311a240fa9c15f09e7e7742 | 5b41283be94e5db1adfb99692b457d370b84fe100eeda7734c95cafe823a705b | NO |
| load_sprint_table | 35ab5ad467970ec88709ef923ac608511d49408d31a7787cf2146fccb0e7248f | (unchanged) | YES |
| load_sprint_goal | a50e52427f26b489b98f1030cb99f004127fc177d37dedc8de9c5f3e7de00716 | (unchanged) | YES |
| detect_current_sprint | 81af06480d402b032665be3d6a2a34c343be0a7005704dc096d52a7280263311 | (unchanged) | YES |
| load_decisions | 64f4318eb68b7f97e1f32f7919b9e31d7025be026aa67fb1ec5f02b51fb2b48e | 98ba432c79d2a3c6e3c9eb84a69b07ea8af6d7deb7a5cf8fa3245692cd712eaf | NO |

### Decision

Re-anchor R5/AC-5 from `b7ce642` to `257b081`. This is a mechanical correction of the
literal SHA, not a change of intent. The spec author's stated intent in this log's
opening ("S1 footprint is locked" -- meaning immutable for *this feature*) is
preserved; what changes is only the snapshot the lock test compares against. R5/AC-5
semantics, the lock-guard mechanism (`inspect.getsource` + `hashlib.sha256`), and the
forward additive-only constraint on F-02 are all unchanged.

Authority: Article X permits validation amendments only with explicit authorization.
The owner pre-authorized Option A on 2026-06-06 via EM after reviewing the drift
evidence and three options (A re-anchor, B revert, C shrink R5 scope). Architect
drafts; owner ratifies by retaining this commit.

### Action

- validation.md R5: SHA updated to 257b081.
- spec.md: all 9 occurrences of b7ce642 updated to 257b081; one inline note at
  the first occurrence pointing back to this Q5.
- tasks.md and plan.md are NOT touched (no SHA references; T-FDC-02 task body
  cites validation.md / plan.md indirectly and remains correct).
- T-FDC-02 implementation will capture golden hashes from 257b081 (the five hashes
  in the table above are pre-computed and authoritative).

### Status

answered (amendment pending owner ratification on commit landing)
