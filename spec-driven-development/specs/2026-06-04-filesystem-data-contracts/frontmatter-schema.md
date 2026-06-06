---
id: SDD-FDC-001-frontmatter-schema
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: filesystem-data-contracts
sprint: PI-4 / Sprint 4
spec: spec.md (APPROVED 2026-06-05)
adr: ../../docs/ADR/012-filesystem-frontmatter-data-contract.md
---

# Frontmatter Schema -- Filesystem Data Contract (SDD-FDC-001)

This is the human-readable data contract referenced by ADR-012. It defines
the YAML frontmatter required on every in-scope markdown artifact under
`spec-driven-development/specs/**` and `spec-driven-development/sprints/**`.

The schema is enforced by `spec-driven-development/cli/schema_lint.py`
(checker kind `artifact`) and consumed by
`spec-driven-development/cli/state_builder.py count`.

## Scope

In scope (must carry valid frontmatter):

- All `*.md` files under `spec-driven-development/specs/**`.
- All `*.md` files under `spec-driven-development/sprints/**`.

Out of scope (Sprint 4):

- `spec-driven-development/docs/**`
- `spec-driven-development/constitution/**`
- `spec-driven-development/templates/**`
- `spec-driven-development/exec/**` (DERIVED, regenerated)
- `spec-driven-development/backlog/**`, `sessions/**`, `dispatches/**`
- Repository root markdown (`README.md`, `INSTRUCTIONS.md`).

## Required Fields

Every in-scope `*.md` MUST carry a YAML frontmatter block delimited by two
`---` lines containing all five fields below.

| Field | Type | Semantics |
|-------|------|-----------|
| `id` | string | Stable identifier for the artifact. Convention: `SDD-<FEATURE>-NNN[-suffix]` (e.g. `SDD-FDC-001-tasks`). |
| `type` | string (enum) | Role of the artifact -- see `type` enum below. Exactly one value per artifact. |
| `status` | string (enum) | Lifecycle state -- see `status` enum below. Exactly one value per artifact. |
| `owner` | string | Principal role responsible (e.g. `principal-architect`, `principal-software-developer`, `principal-product-manager`). |
| `updated` | ISO date | `YYYY-MM-DD` of the most recent meaningful edit. |

A missing or empty value for any required field is a lint finding (R1).

## Enums

### `type`

Closed enum. Exactly one of:

- `spec` -- a feature spec (`spec.md`).
- `plan` -- an implementation plan (`plan.md`).
- `tasks` -- a task list (`tasks.md`).
- `validation` -- a validation contract (`validation.md`).
- `clarification` -- a clarification log (`clarification-log.md`).
- `sprint` -- a sprint plan or status doc (e.g. `CURRENT_PI.md`, `sprint-*.md`).
- `retro` -- a retrospective doc (e.g. `sprint-NN-retro.md`).
- `lessons` -- a lessons-learned doc (e.g. `LESSONS.md`).
- `index` -- a sprint or feature index (e.g. `sprints/PI-N/INDEX.md`).
- `session` -- a session-scoped note (e.g. handoff records, kickoff notes).

If a future artifact does not fit any value, STOP and escalate to the
Architect; do NOT silently invent an enum value (per `tasks.md` notes for
T-FDC-08).

### `status`

Closed enum. Exactly one of:

- `draft` -- under authoring, not yet active.
- `active` -- in flight; the artifact is the working source of truth.
- `blocked` -- explicitly blocked; cannot proceed without a decision.
- `done` -- shipped; the work it describes is complete.
- `superseded` -- replaced by a newer artifact (link to the successor in the body).
- `archived` -- preserved for historical reference; not consulted in active work.

## One-`type`/one-`status`-per-artifact rule

Each artifact carries EXACTLY one `type` and EXACTLY one `status`. This is what
makes the rollup invariant in `state_builder.py count` hold:

```
total == sum(by_status.values()) == sum(by_type.values())
```

If you find yourself wanting two `type` values, the artifact should be split.

## `{}` parse result policy

A frontmatter parse that yields `{}` (empty dict) means "no YAML frontmatter
delimiters were found." Consumers MUST handle this without crashing:

- `schema_lint.check_artifact` emits a finding ("no YAML frontmatter delimiters")
  and exits non-zero (R1).
- `state_builder.build_doc_count` skips the file silently (it is the lint's
  job to flag it, not the counter's).

## Canonical example

```yaml
---
id: SDD-FDC-001-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-05
feature: filesystem-data-contracts
sprint: PI-4 / Sprint 4
---

# Feature Spec: Filesystem Data Contracts

...body...
```

Additional keys beyond the five required ones (such as `feature`, `sprint`,
`adr`, `spec`, `plan`) are PERMITTED but not enforced -- they are
human-readable cross-references. They do not affect the rollup or lint
verdict.

## Lint verdict semantics

- Any in-scope `*.md` missing a required field, or carrying an out-of-enum
  value for `type` or `status` -> ERROR finding -> non-zero exit (R1).
- All in-scope `*.md` valid -> exit zero, no frontmatter findings (R2).
- Templates and example fragments under in-scope trees that exist solely as
  reference material are filtered by an explicit skip list defined in
  `schema_lint.py`; the skip list is documented at the constant definition.

## Backfill

Existing in-scope artifacts predating SDD-FDC-001 receive frontmatter via
T-FDC-08. The Architect-assigned `type` mapping (verbatim from `tasks.md`):

- `spec.md` -> `spec`
- `plan.md` -> `plan`
- `tasks.md` -> `tasks`
- `validation.md` -> `validation`
- `clarification-log.md` -> `clarification`
- `sprint`-shaped docs (`CURRENT_PI.md`, `sprint-*.md`) -> `sprint`
- `INDEX.md` under `sprints/PI-N/` -> `index`
- retro docs -> `retro`
- lessons docs -> `lessons`
- session/handoff docs -> `session`

`status` mapping (verbatim from `tasks.md`):

- shipped specs -> `done`
- in-flight -> `active`
- never started -> `draft`
- explicitly blocked -> `blocked`
- superseded -> `superseded`
- archived/historical -> `archived`

## References

- ADR-012 (`docs/ADR/012-filesystem-frontmatter-data-contract.md`) -- the
  binding architectural decision and the `parse_frontmatter` shared-boundary
  rationale.
- `spec.md` -- the feature spec.
- `plan.md` -- the implementation plan (section 1 carries the locked-decisions
  table that this doc mirrors).
- `validation.md` -- R1..R7 contract (LOCKED at /tasks).
