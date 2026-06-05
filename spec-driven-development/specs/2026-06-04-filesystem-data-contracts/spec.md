# Feature Spec: Filesystem Data Contracts (Sprint 4)

- Date: 2026-06-04
- Author: Principal Product Manager (requirements) / Principal Architect (technical reviewer)
- Status: APPROVED WITH CONDITIONS (Architect, 2026-06-05) -- conditions resolved in /plan
- Priority: P2
- Sprint: PI-4 / Sprint 4
- Spec ID: SDD-FDC-001

---

## Problem Statement

Markdown artifacts under `specs/` and `sprints/` carry no machine-readable header,
so any "doc count" shown on the dashboard is derived ad hoc and cannot be validated.
There is no enforced shape for artifact metadata (id, type, status, owner, last
update), no lint that proves the metadata is present and well-formed, no reproducible
rollup of artifact counts, and no agreed commit-message convention to make history
traceable.

This creates three concrete failures:
1. Dashboard doc metrics can silently drift from reality (no source of truth).
2. Reviewers cannot tell an artifact's `status`/`owner` without reading prose.
3. Commit history is inconsistent, weakening traceability the framework promises.

Constraint: the S1 dashboard footprint is locked. `render_html()` and the four
data-layer functions (T-001..T-004) shipped in commit `b7ce642` MUST NOT change.

## Proposed Solution

Introduce a filesystem data contract for `specs/**` and `sprints/**` markdown,
enforced by an extension to the existing schema-lint, surfaced by a reproducible
doc-count rollup exposed through a new `count` subcommand, and supported by a
documented (opt-in) commit-message convention.

Five deliverables:

1. **YAML frontmatter schema** -- a documented contract requiring fields `id`,
   `type`, `status`, `owner`, `updated` on every `specs/**` and `sprints/**`
   markdown artifact in scope. Backfill existing in-scope artifacts.
2. **Schema-lint extension** -- extend `cli/schema_lint.py` to validate the new
   frontmatter contract for the in-scope artifact classes, reusing the existing
   stdlib `parse_frontmatter` (no PyYAML).
3. **Doc-count rollup** -- a counting function that groups in-scope artifacts by
   `status` and by `type`, scoped per sprint.
4. **`count` subcommand** -- a new additive subparser on `cli/state_builder.py`
   that emits the rollup as JSON to stdout by default and `--format table` for
   humans. It parses frontmatter independently and never calls locked S1 code.
5. **Commit-message convention** -- documentation plus an opt-in `commit-msg`
   hook script contributors install manually. No auto-install, no CI gate.

## Acceptance Criteria

1. Given an in-scope artifact missing any required frontmatter field, when
   schema-lint runs, then it reports a finding naming the file and the missing
   field and exits non-zero.
2. Given all in-scope artifacts have valid frontmatter, when schema-lint runs,
   then it exits zero with no frontmatter findings.
3. Given the in-scope artifact set, when `state_builder.py count` runs with no
   `--format`, then it prints JSON to stdout matching
   `{ "by_status": {<status>: int}, "by_type": {<type>: int}, "total": int }`
   where `total` equals the sum of `by_status` values and the sum of `by_type`
   values.
4. Given the in-scope artifact set, when `state_builder.py count --format table`
   runs, then it prints a human-readable table of the same counts and exits zero.
5. Given commit `b7ce642`, when this feature is fully implemented, then a diff of
   `render_html()` and the four data-layer functions (T-001..T-004) against
   `b7ce642` shows zero changes.
6. Given the documented commit-message convention, when a contributor installs the
   opt-in `commit-msg` hook and writes a non-conforming message, then the hook
   rejects the commit with a message pointing to the convention doc; when the hook
   is not installed, commits are unaffected.
7. Given the existing test suite, when the full suite runs after implementation,
   then all previously passing tests still pass (no regression).

## Affected Modules

- Files:
  - `spec-driven-development/cli/schema_lint.py` (extend: new contract validator)
  - `spec-driven-development/cli/test_schema_lint.py` (new tests)
  - `spec-driven-development/cli/state_builder.py` (additive: `count` subparser +
    rollup helper; locked functions untouched)
  - `spec-driven-development/cli/test_state_builder.py` (new tests for `count`)
  - `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md`
    (new: schema contract doc)
  - `spec-driven-development/docs/COMMIT-CONVENTION.md` (new: convention doc)
  - `.githooks/commit-msg` or `spec-driven-development/cli/hooks/commit-msg`
    (new: opt-in hook script -- final path is an Architect decision)
- Directories:
  - `spec-driven-development/specs/**` (frontmatter backfill)
  - `spec-driven-development/sprints/**` (frontmatter backfill)

## Data Model Changes

No database/schema (`fleet.db`) changes. The "data model" here is the filesystem
frontmatter contract:

```yaml
---
id: <stable-id>        # required, string
type: <artifact-type>  # required, enum (e.g. spec | sprint | retro | plan | tasks)
status: <status>       # required, enum (e.g. draft | active | done | blocked)
owner: <owner>         # required, string
updated: <YYYY-MM-DD>  # required, ISO date
---
```

Exact enum value sets for `type` and `status` are an Architect decision during
`/plan`; the required key set is fixed by D1.

## API Changes

New CLI surface (additive only):

```
state_builder.py count [--format json|table] [--sdd-root PATH]
```

Default `--format json`. JSON contract:
`{ "by_status": {str: int}, "by_type": {str: int}, "total": int }`.
This FLAT global rollup is the stable default (confirmed 2026-06-05). An optional
`--sprint <id>` selector narrows the rollup to one sprint without changing the
top-level shape; an optional `by_sprint` key may be added for the grouped view.
No changes to `serve`, `build-index`, or default build behavior.

## Test Strategy

- Unit:
  - `schema_lint`: valid artifact passes; each missing required field produces a
    finding; malformed frontmatter handled gracefully.
  - `count` rollup: by_status/by_type/total consistency; empty set yields zeros;
    JSON and table formats.
- Integration:
  - Run `count` over a temp fixture tree of in-scope artifacts; assert JSON shape
    and totals.
  - Run `schema_lint` end-to-end over a fixture tree; assert exit codes.
- End-to-end/manual:
  - Install opt-in `commit-msg` hook in a scratch clone; verify a bad message is
    rejected and a good one passes; verify uninstalled state is unaffected.
- Regression:
  - Full existing suite must stay green.
  - Lock check: assert `render_html()` and T-001..T-004 are byte-identical to
    `b7ce642` (manual diff or a guard test).

## Validation Contract

The binding validation contract lives in the sibling `validation.md`, written
during `/spec`, locked at `/tasks`, with zero unchecked required items before
implementation is considered complete. The S1 lock check (AC-5) is a required
validation item.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| Frontmatter contract enforced | AC-1, AC-2 | `schema_lint.py` |
| Rollup JSON contract | AC-3 | `state_builder.py count` |
| Rollup human view | AC-4 | `state_builder.py count` |
| S1 footprint locked | AC-5 | `state_builder.py` (guard) |
| Commit convention (opt-in) | AC-6 | `COMMIT-CONVENTION.md` + hook |
| No regression | AC-7 | full suite |

## Open Questions

Resolved by Architect (2026-06-05), to be locked in `/plan`:

- `type` enum (recommended): `spec | plan | tasks | validation | clarification |
  sprint | retro | lessons | index | session`.
- `status` enum (recommended): `draft | active | blocked | done | superseded |
  archived`.
- Opt-in hook path (recommended): `spec-driven-development/cli/hooks/commit-msg`
  (keeps all framework assets under the SDD root; no top-level `.githooks/`).

## Architect Review (2026-06-05)

Verdict: **APPROVED WITH CONDITIONS**. Technically sound, correctly constrained,
additive surface, no `fleet.db` changes, no new dependencies. Conditions are
`/plan` deliverables (none block kickoff):

1. Resolve per-sprint vs global JSON scoping. AC-3/API show a flat global object;
   D2 says "per sprint." Keep the flat shape as the stable contract; add an
   optional `--sprint <id>` selector (default = global); optionally add a
   `by_sprint` key WITHOUT changing the top-level shape.
2. Specify an AUTOMATED S1 lock guard test: stdlib `inspect.getsource` +
   `hashlib.sha256` over `render_html` and T-001..T-004, compared to golden
   hashes captured from the `b7ce642` checkout (satisfies AC-5 / R5). Replaces
   the brittle manual/line-range diff.
3. Author one ADR for the filesystem frontmatter data contract + the
   `parse_frontmatter` shared-boundary decision.
4. Reuse `parse_frontmatter` from `schema_lint` via the established
   `sys.path.insert(CLI_DIR)` import pattern -- do NOT duplicate the parser.
   `count` must treat a `{}` parse result as missing/unparseable (skip or flag),
   not crash.
5. Define zero-count key policy: emit all known enum keys with explicit `0`
   (stable, dashboard-friendly). The `total == sum(by_status) == sum(by_type)`
   invariant holds only if each artifact has exactly one `type`/`status` counted
   once -- make that explicit.

Give `count` its own handler function (CLI-PATTERN rule 9); do not bloat `main()`.

## Out of Scope

- Applying frontmatter to `docs/**` or constitution files (deferred past Sprint 4).
- Mandatory commit-message enforcement via CI or auto-installed hooks (later HITL /
  Level-2 decision).
- Any change to `render_html()` or the b7ce642 data-layer functions.
- `fleet.db` schema changes.

---

## Architect Review

- Reviewer: Principal Architect
- Date: 2026-06-05
- Verdict: **APPROVED WITH CONDITIONS**

### Decoupling of `count` from locked S1 code (verified)

`render_html()` and T-001..T-004 (`load_sprint_table`, `load_sprint_goal`, +2)
are self-contained functions. A new `count` subparser plus a new rollup helper
that walks `specs/**` and `sprints/**` and parses frontmatter calls none of them.
Decoupling is provable by construction. `parse_frontmatter` in `schema_lint.py`
is a clean module-level stdlib function with no import-time side effects, so
reusing it does not touch locked code.

Recommended module boundary: import `parse_frontmatter` from `schema_lint` via
the established `sys.path.insert(CLI_DIR)` bootstrap (same pattern `fleet.py` and
`retro.py` use for the ledger module). Single source of truth for the parser; do
NOT duplicate it. Optional future cleanup: lift the parser to
`cli/common/frontmatter.py` and have both CLIs import it -- deferred (extra
regression surface on `schema_lint` tests, no Sprint-4 benefit).

### Open questions: resolvable in /plan, NOT blocking

Both are configuration decisions, not architectural unknowns.

- `type` enum (recommended, closed + covers in-scope files):
  `spec | plan | tasks | validation | clarification | sprint | retro | lessons |
  index | session`.
- `status` enum (recommended):
  `draft | active | blocked | done | superseded | archived`.
- Hook path (recommended): ship the script at
  `spec-driven-development/cli/hooks/commit-msg` (lives with the CLIs it belongs
  to, survives `git clean`, install via documented `git config core.hooksPath`
  or copy). Avoid a top-level `.githooks/` to keep framework assets under
  `spec-driven-development/`.

### JSON contract -- sound, ONE tension to resolve

`{ by_status, by_type, total }` is a sound, stable shape. Two conditions:
- D2 says "scoped per sprint" but AC-3/API show a single flat (global) object.
  Resolve in /plan: keep the flat shape as the stable contract and add an
  optional `--sprint <id>` selector (default = global rollup); optionally add a
  `by_sprint` key for the grouped view without breaking the top-level shape.
- Zero-count policy: emit all known enum keys with explicit `0` (stable,
  dashboard-friendly) rather than sparse maps. Document this in /plan.

### S1 lock enforcement -- automated guard required

Manual diff is insufficient (not enforced per-change, humans forget). Lightest
reliable mechanism: a guard test using stdlib `inspect.getsource` +
`hashlib.sha256` over `render_html` and the four functions, compared to golden
hashes captured from the `b7ce642` checkout and pinned in the test. Stdlib-only,
no git dependency, robust to surrounding line shifts. This satisfies AC-5/R5.

### ADR / patterns

- Needs ONE ADR: the filesystem frontmatter data contract is a new cross-cutting
  convention for `specs/**` + `sprints/**` (and records the `parse_frontmatter`
  shared-boundary decision). Enum/hook details stay in /plan, not the ADR.
- No pattern violations. `count` must follow CLI-PATTERN.md (own handler
  function, `main(argv)`, stdlib only -- LESSON-001). Watch: do not bloat `main()`.

### Conditions before /plan completes

1. Resolve per-sprint vs global JSON scoping (recommend `--sprint` filter + stable
   flat shape; optional `by_sprint`).
2. Specify the automated S1 lock guard test (inspect + hashlib golden hash).
3. Author the frontmatter-contract ADR.
4. Reuse `parse_frontmatter` via import (no duplicate parser).
5. Define the zero-count key policy (recommend explicit zeros).
