# ADR-012: Filesystem Frontmatter Data Contract for specs/** + sprints/**

- Date: 2026-06-05
- Status: accepted

## Context

Markdown artifacts under `spec-driven-development/specs/**` and
`spec-driven-development/sprints/**` carry no machine-readable header. Any
"doc count" or status surfaced by the dashboard is derived ad hoc, cannot be
validated, and silently drifts from reality. Reviewers cannot tell an
artifact's `status` or `owner` without reading prose, and there is no enforced
shape for artifact metadata.

The framework already has the machinery to fix this without new dependencies:

- `cli/schema_lint.py` owns a stdlib-only frontmatter parser,
  `parse_frontmatter`, used to validate `.github/agents`, `.github/skills`, and
  `.github/prompts`. It has no import-time side effects.
- `cli/state_builder.py` produces the executive dashboard and is the natural
  home for a reproducible doc-count rollup.

Two architectural questions must be settled before Sprint 4 implementation:

1. **What is the data contract** for in-scope markdown artifacts -- the required
   field set and the closed enum value sets for `type` and `status` -- and which
   directories does it bind?
2. **Where does frontmatter parsing live** when a second consumer
   (`state_builder.py count`) needs it. Duplicating the parser creates two
   sources of truth that can diverge; the alternative is a shared boundary.

A hard constraint frames both: the S1 dashboard footprint shipped in commit
`b7ce642` -- `render_html()` and the four data-layer functions T-001..T-004
(`load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
`load_decisions`) -- MUST NOT change. Any new contract must be enforced by
additive code only.

## Decision

### 1. A filesystem frontmatter data contract binds specs/** and sprints/**

Every in-scope markdown artifact under `specs/**` and `sprints/**` MUST carry a
YAML frontmatter block with exactly these five required fields:

```yaml
---
id: <stable-id>        # required, string
type: <artifact-type>  # required, enum (closed set below)
status: <status>       # required, enum (closed set below)
owner: <owner>         # required, string
updated: <YYYY-MM-DD>  # required, ISO date
---
```

Locked closed enums (owner/Architect-approved):

- `type`: `spec | plan | tasks | validation | clarification | sprint | retro | lessons | index | session`
- `status`: `draft | active | blocked | done | superseded | archived`

Scope is deliberately narrow. `docs/**` and constitution files are OUT of scope
for this contract (deferred past Sprint 4). The contract is the data model for
the doc-count rollup and the schema-lint extension; there is no `fleet.db`
change.

An artifact is assumed to carry exactly one `type` and exactly one `status`,
counted once. A frontmatter block that parses to `{}` (no delimiters, or an
unterminated block) is treated as missing/unparseable -- consumers skip or flag
it; they never crash.

### 2. parse_frontmatter is the single shared parsing boundary

`parse_frontmatter` in `cli/schema_lint.py` remains the one and only
frontmatter parser. The new `count` consumer in `cli/state_builder.py` imports
it via the established `sys.path.insert(0, str(CLI_DIR))` bootstrap (the same
pattern `fleet.py` and `retro.py` use to import the ledger module). The parser
is NOT duplicated, re-implemented, or copy-pasted.

This keeps a single source of truth for "what valid frontmatter looks like."
The schema-lint contract validator and the dashboard rollup necessarily agree
because they parse with the same function.

Lifting the parser into `cli/common/frontmatter.py` and having both CLIs import
it from there was considered and explicitly deferred: it adds regression surface
to the existing `schema_lint` tests with no Sprint-4 benefit. The import-via-
`sys.path` boundary is the minimal change that achieves single-source-of-truth.

## Consequences

Positive:

- The dashboard's doc metrics gain a validated source of truth; drift becomes a
  lint failure instead of a silent error.
- Reviewers read `status`/`owner` from the header, not from prose.
- One parser, one definition of valid frontmatter, shared by lint and rollup --
  they cannot disagree.
- No new dependency, no `fleet.db` change, no change to the locked S1 footprint.
  All new code is additive.

Negative:

- `state_builder.py` acquires a runtime import dependency on `schema_lint.py`
  via `sys.path` insertion. Mitigated: this is an established in-repo pattern,
  both modules are stdlib-only, and the import has no side effects.
- Closed enums require maintenance. Adding a new artifact `type` or `status`
  later is a deliberate, reviewed change to the enum sets (and this ADR), not an
  ad-hoc string. This is intended -- the closure is the point.
- Existing in-scope artifacts must be backfilled with frontmatter before
  schema-lint can run green. One-time migration cost, bounded by the current
  `specs/**` + `sprints/**` file count.

Neutral:

- The contract is filesystem-only; it does not touch the database or the ledger
  schema.
- A future ADR may lift the parser to `cli/common/` if a third consumer appears;
  this ADR records that path as deferred, not rejected.

## Alternatives Considered

- **Duplicate `parse_frontmatter` inside `state_builder.py`.** Rejected: two
  copies of the parser become two definitions of "valid frontmatter" that drift
  apart; the rollup and the lint would silently disagree.
- **Add PyYAML and parse properly.** Rejected: violates LESSON-001 (stdlib only)
  and requires Level-2 dependency approval for a need the existing stdlib parser
  already covers.
- **Bind the contract to all `.md` (including `docs/**` + constitution).**
  Rejected for Sprint 4: balloons effort from L to XL, risks touching the locked
  S1 footprint indirectly, and the dashboard only rolls up `specs/**` +
  `sprints/**`. Broader scope is deferred.
- **Open (free-string) `type`/`status` instead of closed enums.** Rejected:
  free strings reintroduce the drift problem -- `done` vs `Done` vs `complete`
  fragment the rollup. Closed enums make the count deterministic and
  dashboard-friendly.
- **Lift the parser to `cli/common/frontmatter.py` now.** Deferred (not
  rejected): correct long-term home, but adds regression surface to
  `schema_lint` tests with no Sprint-4 benefit. Revisit when a third consumer
  appears.
