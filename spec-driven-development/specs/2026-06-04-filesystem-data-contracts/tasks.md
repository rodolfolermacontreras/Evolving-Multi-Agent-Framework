---
id: SDD-FDC-001-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: filesystem-data-contracts
sprint: PI-4 / Sprint 4
spec: spec.md (APPROVED 2026-06-05)
plan: plan.md (locked at SPEC sign-off)
validation: validation.md (LOCKED at /tasks per Article X)
adr: ../../docs/ADR/012-filesystem-frontmatter-data-contract.md
---

# Task List: Filesystem Data Contracts (SDD-FDC-001)

- Spec Reference: `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/plan.md`
- Validation Contract: `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/validation.md` (LOCKED)
- ADR Reference: `spec-driven-development/docs/ADR/012-filesystem-frontmatter-data-contract.md`
- Task ID Format: `T-FDC-NN` (local to this date-prefixed feature dir; LESSON-002).
- Owner: Principal Software Developer
- Total tasks: 9
- Worktrees: 0 (PI-4 convention; do not introduce one).

---

## Status Legend

- `pending` -- not yet started
- `in-progress` -- a worker has accepted it and is working
- `done` -- acceptance ties green, committed
- `blocked` -- waiting on a decision or another task

## Hard constraints (apply to every task)

1. **S1 footprint lock (b7ce642).** `render_html()` and the four data-layer
   functions T-001..T-004 (`load_sprint_table`, `load_sprint_goal`,
   `detect_current_sprint`, `load_decisions`) in `cli/state_builder.py` MUST
   stay byte-identical to commit `b7ce642`. Every task that touches
   `state_builder.py` MUST treat these five functions as **DO NOT TOUCH**.
   Additive code only.
2. **Stdlib only.** No `pip install`, no `import yaml`, no `import requests`,
   no third-party imports anywhere in `cli/**`. LESSON-001 / CLI-PATTERN rule 1.
3. **Reuse `parse_frontmatter`.** Import it from `cli/schema_lint` via the
   established `sys.path.insert(0, str(CLI_DIR))` bootstrap. Do NOT duplicate
   the parser. ADR-012.
4. **`{}` parse result.** A frontmatter parse that returns `{}` means missing
   or unparseable: lint flags it, count skips it, neither crashes.
5. **`validation.md` is LOCKED.** R1-R7 statement bodies cannot be modified.
   Only checkbox state and the matrix annotations may change post-/tasks.
6. **No emojis** in code, docs, commits, or this file.

## Frontmatter contract note (one-time deviation)

AC-1 of the F-01 prompt mandates literal `status: locked` in this tasks.md
frontmatter. The locked status enum (plan §1, ADR-012) is
`draft | active | blocked | done | superseded | archived` and does NOT include
`locked`. AC-1's verification column is a literal `cat` check (not a lint
check), so this file complies with F-01. T-FDC-08 reconciles the deviation
during backfill by either updating this file to `status: active` OR (if the
Architect decides during F-02) extending the enum to include `locked`. F-02
must NOT advance the gate until reconciliation is complete and R2 (lint exits
zero) is green over the in-scope tree.

---

## Task Breakdown

> **Cross-reference rule:** the Acceptance Test column cites validation R-ids
> and spec AC-ids rather than restating prose. Full per-task `allowed_files`
> and `blocked_files` scope lives in section "Per-Task Detailed Scope" below
> (AC-3).
> Provenance: LESSON-003, source feature `specs/2026-05-12-fleet-ledger/`.

| Task ID | Tag | Description | File Scope (summary) | Acceptance Ties | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|----------------------|-----------------|--------|------|------|-------|--------|
| T-FDC-01 | [P] | Author `frontmatter-schema.md` (Phase 1) -- the human-readable data contract: five required fields, locked `type` + `status` enums verbatim, one-`type`/one-`status` rule, `{}` policy, canonical example. | new doc, single file | enables R1, R2 | S | none | AFK | Yes | done |
| T-FDC-02 | [P] | S1 lock guard test (Phase 4): capture golden sha256 of `render_html` and T-001..T-004 from `b7ce642`, pin in `GOLDEN_S1_HASHES`, add `test_s1_footprint_locked` to `test_state_builder.py`. **DOES NOT modify `state_builder.py`.** Tripwire must exist BEFORE T-FDC-04/05 touch state_builder.py. | extend `cli/test_state_builder.py` only | R5 (AC-5) | S | none | AFK | Yes | done |
| T-FDC-03 | [S] | Phase 2 schema-lint extension: add `REQUIRED_CONTRACT_FIELDS`, `ARTIFACT_TYPE_ENUM`, `ARTIFACT_STATUS_ENUM`, `check_artifact()`, extend `scan()` to walk `specs/**` + `sprints/**`. Reuse existing `parse_frontmatter`. Exit semantics unchanged. Include explicit skip list for in-tree templates/examples. | `cli/schema_lint.py`, `cli/test_schema_lint.py` | R1 (AC-1), R2 (AC-2) | M | T-FDC-01 | AFK | Yes | done |
| T-FDC-04 | [S] | Phase 3a-3b: in `state_builder.py`, add `CLI_DIR`/`sys.path` bootstrap, import `parse_frontmatter` + enums from `schema_lint`, implement pure `build_doc_count(sdd_root, sprint=None) -> dict`, `build_doc_count_by_sprint(sdd_root) -> dict`, `render_count_table(rollup) -> str`. Zero-count seeding. Invariant `total == sum(by_status) == sum(by_type)`. Tests in `test_state_builder.py`. **Locked S1 functions untouched.** | `cli/state_builder.py` (additive only), `cli/test_state_builder.py` | R3 (AC-3) | M | T-FDC-02, T-FDC-03 | AFK | No (same file as T-FDC-05) | done |
| T-FDC-05 | [S] | Phase 3c-3e: add `cmd_count(args, sdd_root) -> int` handler (CLI-PATTERN rule 9), wire `count` subparser (`--format`, `--sprint`, `--by-sprint`), add ONE dispatch branch in `main()`. Tests for `--format json` shape, `--format table` exit 0, `--sprint` narrowing, `--by-sprint` additive key, `{}` skip behavior. **Locked S1 functions untouched.** `main()` stays thin. | `cli/state_builder.py` (additive only), `cli/test_state_builder.py` | R3 (AC-3), R4 (AC-4) | S-M | T-FDC-04 | AFK | No (same file as T-FDC-04) | done |
| T-FDC-06 | [P] | Phase 5a: author `docs/COMMIT-CONVENTION.md` documenting the `type(scope): short` format with valid/invalid examples and install instructions (two paths: `git config core.hooksPath` or copy). Per D3: doc + opt-in only, no CI gate. | new doc, single file | O2 | S | none | AFK | Yes | done |
| T-FDC-07 | [S] | Phase 5b: ship opt-in `cli/hooks/commit-msg` (stdlib Python or POSIX `sh`) that validates the first line against `^(feat|fix|refactor|test|docs|chore|spec|plan)(\([\w-]+\))?: .+`, exits 0 on match, points failures at `COMMIT-CONVENTION.md` and exits non-zero otherwise. Subprocess tests in NEW `cli/test_commit_hook.py` (keeps `test_state_builder.py` focused). | new `cli/hooks/commit-msg`, new `cli/test_commit_hook.py` | O1 (AC-6) | S | T-FDC-06 | AFK | Yes | done |
| T-FDC-08 | [S] | Phase 6 frontmatter backfill: add five-field block to every in-scope `specs/**` + `sprints/**` markdown that lacks it; reconcile `status: locked` on THIS file per "Frontmatter contract note" above; choose enum values per filename role (e.g. `spec.md` -> `spec`, `plan.md` -> `plan`, `validation.md` -> `validation`, `clarification-log.md` -> `clarification`, sprint `INDEX.md` -> `index`, retro -> `retro`, lessons -> `lessons`, session -> `session`). Splittable per directory for fleet dispatch with one-file-per-task scoping. After: `schema_lint` must run GREEN over the in-scope tree (R2). | `spec-driven-development/specs/**/*.md`, `spec-driven-development/sprints/**/*.md` | R6, R2 (AC-2) | M | T-FDC-03 | AFK | Yes (per-file split) | done |
| T-FDC-09 | [S] | Validation closeout: run full suite, confirm >= 152 passing (R7/AC-7), re-run `schema_lint` to confirm zero findings (R2), re-run `count` and validate JSON shape + invariant (R3), check `--format table` (R4), check lock guard test green (R5), spot-check three backfilled files (R6). Tick the R1-R7 checkboxes in `validation.md` (statements untouched -- only `[ ]` -> `[x]`). | `spec-driven-development/specs/2026-06-04-filesystem-data-contracts/validation.md` (checkbox state only) | R1-R7 (AC-1..AC-7) | S | T-FDC-04, T-FDC-05, T-FDC-07, T-FDC-08 | AFK | No (sequencing close) | done |

Total: **9 tasks**. Parallel batches available: { T-FDC-01, T-FDC-02, T-FDC-06 }; later { T-FDC-07 alongside T-FDC-04/05 }; T-FDC-08 splittable per subdirectory.

---

## Per-Task Detailed Scope (AC-3)

Each task block lists `allowed_files` (the worker may add/extend) and
`blocked_files` (the worker MUST NOT touch). Files outside both sets are
implicitly out-of-scope unless the worker escalates to the Principal Software
Developer.

### T-FDC-01 -- frontmatter-schema.md

```yaml
allowed_files:
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md  # NEW
blocked_files:
  - cli/**                                       # no code
  - constitution/**                              # immutable (Article VIII)
  - spec-driven-development/docs/ADR/**          # no ADR edits
  - any file outside allowed_files
```

### T-FDC-02 -- S1 lock guard test (Phase 4)

```yaml
allowed_files:
  - spec-driven-development/cli/test_state_builder.py   # ADDITIVE -- new test function only
blocked_files:
  - spec-driven-development/cli/state_builder.py        # DO NOT TOUCH (entire file)
  - spec-driven-development/cli/state_builder.py::render_html              # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_table        # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_goal         # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::detect_current_sprint    # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_decisions           # DO NOT TOUCH
  - any third-party dependency
notes:
  - Golden-hash capture procedure: per plan §2 Phase 4, run a stdlib snippet
    against the b7ce642 checkout (worktree or scratch clone), paste the five
    digests into GOLDEN_S1_HASHES, then remove the worktree.
  - Pin LOCKED tuple and GOLDEN_S1_HASHES dict at module top of the test.
  - Test must fail loudly with the function name on mismatch.
```

### T-FDC-03 -- schema-lint extension (Phase 2)

```yaml
allowed_files:
  - spec-driven-development/cli/schema_lint.py            # extend, do not rewrite
  - spec-driven-development/cli/test_schema_lint.py       # new tests
blocked_files:
  - spec-driven-development/cli/state_builder.py          # do not touch in this task
  - spec-driven-development/cli/state_builder.py::render_html              # DO NOT TOUCH ever
  - spec-driven-development/cli/state_builder.py::load_sprint_table        # DO NOT TOUCH ever
  - spec-driven-development/cli/state_builder.py::load_sprint_goal         # DO NOT TOUCH ever
  - spec-driven-development/cli/state_builder.py::detect_current_sprint    # DO NOT TOUCH ever
  - spec-driven-development/cli/state_builder.py::load_decisions           # DO NOT TOUCH ever
  - any third-party dependency (no PyYAML, no requests, no imports outside stdlib)
  - the existing parse_frontmatter signature/semantics (use as-is)
notes:
  - New checker kind: "artifact".
  - Add explicit skip list for templates/examples in spec_dir/sprints_dir.
  - {} from parse_frontmatter must produce a "no YAML frontmatter delimiters"
    finding, never an exception.
```

### T-FDC-04 -- rollup helpers (Phase 3a-3b)

```yaml
allowed_files:
  - spec-driven-development/cli/state_builder.py          # ADDITIVE ONLY
  - spec-driven-development/cli/test_state_builder.py     # new tests
blocked_files:
  - spec-driven-development/cli/state_builder.py::render_html              # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_table        # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_goal         # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::detect_current_sprint    # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_decisions           # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::build                    # do not modify
  - spec-driven-development/cli/state_builder.py::serve                    # do not modify
  - spec-driven-development/cli/state_builder.py::build_index              # do not modify
  - spec-driven-development/cli/schema_lint.py                             # do not modify in this task
  - any third-party dependency
notes:
  - Add new symbols only: CLI_DIR/sys.path bootstrap, build_doc_count,
    build_doc_count_by_sprint, render_count_table.
  - Import parse_frontmatter, ARTIFACT_TYPE_ENUM, ARTIFACT_STATUS_ENUM from
    schema_lint via the bootstrapped path. No re-implementation.
  - Zero-count policy: seed by_status and by_type with every known enum key
    at 0 before counting.
  - Test the total invariant explicitly.
```

### T-FDC-05 -- cmd_count handler + subparser (Phase 3c-3e)

```yaml
allowed_files:
  - spec-driven-development/cli/state_builder.py          # ADDITIVE ONLY -- one subparser, one handler, one main() branch
  - spec-driven-development/cli/test_state_builder.py     # new tests
blocked_files:
  - spec-driven-development/cli/state_builder.py::render_html              # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_table        # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_sprint_goal         # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::detect_current_sprint    # DO NOT TOUCH
  - spec-driven-development/cli/state_builder.py::load_decisions           # DO NOT TOUCH
  - existing subparsers (serve, build-index) behavior must be unchanged
  - any third-party dependency
notes:
  - cmd_count gets its own function (CLI-PATTERN rule 9); main() gets ONE
    dispatch branch (`if args.cmd == "count": return cmd_count(args, sdd_root)`).
  - Tests cover: default JSON shape, --format table prints + exits 0, --sprint
    narrows without changing top-level shape, --by-sprint adds the additive
    key without changing top-level shape.
```

### T-FDC-06 -- COMMIT-CONVENTION.md (Phase 5a)

```yaml
allowed_files:
  - spec-driven-development/docs/COMMIT-CONVENTION.md     # NEW
blocked_files:
  - cli/**                                                 # no code
  - any CI/workflow files (.github/workflows/**)           # D3: no CI gate
  - constitution/**                                        # immutable
notes:
  - Doc-only deliverable per D3 (no CI gate, no auto-install).
  - Include valid/invalid examples and two install paths (core.hooksPath OR
    manual copy).
```

### T-FDC-07 -- opt-in commit-msg hook (Phase 5b)

```yaml
allowed_files:
  - spec-driven-development/cli/hooks/commit-msg          # NEW (mkdir cli/hooks/)
  - spec-driven-development/cli/test_commit_hook.py       # NEW (do NOT bloat test_state_builder.py)
blocked_files:
  - spec-driven-development/cli/state_builder.py          # do not touch
  - spec-driven-development/cli/schema_lint.py            # do not touch
  - .git/hooks/**                                          # never install automatically
  - any CI/workflow files                                  # D3
  - any third-party dependency
notes:
  - Hook reads argv[1] (commit message file path), exits 0 on regex match,
    prints pointer to COMMIT-CONVENTION.md and exits non-zero otherwise.
  - Tests run the hook as a subprocess on a scratch temp file. No real git
    invocations.
  - No emojis in hook output.
```

### T-FDC-08 -- frontmatter backfill (Phase 6)

```yaml
allowed_files:
  - spec-driven-development/specs/**/*.md
  - spec-driven-development/sprints/**/*.md
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/tasks.md  # reconcile status: locked
blocked_files:
  - spec-driven-development/specs/**/validation.md::R1..R7 statement bodies  # LOCKED at /tasks (Article X). Frontmatter ADD is allowed; R-text edits are not.
  - spec-driven-development/specs/**/plan.md                                  # LOCKED at SPEC sign-off. Frontmatter ADD is allowed; body edits are not.
  - spec-driven-development/docs/**                                           # out of scope for FDC contract (deferred past Sprint 4 per ADR-012)
  - spec-driven-development/constitution/**                                   # immutable (Article VIII); out of scope
  - spec-driven-development/templates/**                                      # out of scope
  - cli/**                                                                    # no code in this task
  - any third-party dependency
notes:
  - Splittable per top-level subdirectory for fleet dispatch with
    one-file-per-task or one-directory-per-task scoping.
  - Type mapping: spec.md -> spec, plan.md -> plan, tasks.md -> tasks,
    validation.md -> validation, clarification-log.md -> clarification,
    sprint INDEX.md -> index, retro docs -> retro, lessons docs -> lessons,
    session docs -> session, handoff-* -> closest matching type or skip
    (Architect adjudicates if no enum value fits).
  - status mapping: shipped specs -> done; in-flight -> active; superseded
    -> superseded; never started -> draft; explicitly blocked -> blocked;
    archived/historical -> archived.
  - Reconciliation step (one-time): if `status: locked` is not added to the
    enum by F-02, change THIS tasks.md to `status: active` before running
    schema_lint to verify R2.
  - Gate: schema_lint must exit zero over the in-scope tree before this task
    is `done`.
```

### T-FDC-09 -- validation closeout

```yaml
allowed_files:
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/validation.md  # checkbox state only ([ ] -> [x]); statements R1..R7 are LOCKED
blocked_files:
  - all R1..R7 statement bodies in validation.md
  - all source code (cli/**, schema_lint.py, state_builder.py)
  - all docs/, constitution/, templates/
notes:
  - Run order: full suite -> schema_lint -> state_builder.py count (json) ->
    state_builder.py count --format table -> verify lock guard test green ->
    spot-check three backfilled files manually.
  - On failure of any R: STOP, return to the failing task. Do not tick the
    box.
```

---

## Traceability Matrix (AC-2)

Every R1-R7 (REQUIRED) is mapped to at least one task. O1-O2 (OPTIONAL) are
mapped to dedicated tasks per D3.

| Validation Item | Statement (paraphrase, see validation.md for binding text) | Owning Task(s) | Supporting Task(s) |
|-----------------|-----------------------------------------------------------|----------------|--------------------|
| R1 (AC-1) | Missing required field => named finding + non-zero exit | T-FDC-03 | T-FDC-01 (defines fields) |
| R2 (AC-2) | Valid in-scope tree => exit 0, no frontmatter findings | T-FDC-08 (backfill makes tree green) | T-FDC-03 (lint correctness), T-FDC-09 (verification) |
| R3 (AC-3) | `count` JSON shape `{by_status, by_type, total}` + total invariant | T-FDC-04 (helpers), T-FDC-05 (handler) | T-FDC-01 (enums + zero-count policy) |
| R4 (AC-4) | `count --format table` prints table, exits 0 | T-FDC-05 | T-FDC-04 (`render_count_table`) |
| R5 (AC-5) | S1 footprint locked (golden sha256 vs b7ce642) | T-FDC-02 | (none -- standalone tripwire) |
| R6 | All in-scope `specs/**` + `sprints/**` carry valid frontmatter | T-FDC-08 | T-FDC-01 (schema), T-FDC-03 (lint to verify) |
| R7 (AC-7) | Full existing suite green (>= 152) | T-FDC-09 | every task (no regression discipline) |
| O1 (AC-6) | Opt-in hook rejects bad / allows good; uninstalled unaffected | T-FDC-07 | T-FDC-06 (doc the hook points at) |
| O2 | `COMMIT-CONVENTION.md` documents format with examples | T-FDC-06 | (none) |

**Coverage check:** R1, R2, R3, R4, R5, R6, R7 each map to at least one task.
O1 and O2 each map to one task. No requirement is orphaned.

**No-touch check (AC-4):** Tasks T-FDC-02, T-FDC-04, T-FDC-05 explicitly list
`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`,
`load_decisions` in their `blocked_files` notes. No other task references
`state_builder.py`. Search this file for those function names to audit.

**Stdlib-only check (AC-5):** Every task's `blocked_files` includes "any
third-party dependency." This file contains no `pip install`, no `import yaml`,
no `import requests`. Search this file to audit.

---

## Dispatch Sequence (recommended for F-02)

The Software Developer worker in F-02 may execute in this order:

1. **Wave 1 (parallel-safe):** T-FDC-01, T-FDC-02, T-FDC-06 -- disjoint files.
2. **Wave 2:** T-FDC-03 (depends on T-FDC-01) and T-FDC-07 (depends on T-FDC-06)
   can run in parallel.
3. **Wave 3:** T-FDC-04 (depends on T-FDC-02 + T-FDC-03).
4. **Wave 4:** T-FDC-05 (depends on T-FDC-04; same file).
5. **Wave 5:** T-FDC-08 (depends on T-FDC-03; splittable per subdirectory for
   internal parallelization).
6. **Wave 6:** T-FDC-09 (closeout; depends on all prior).

Worktrees: **none**. PI-4 has used zero worktrees; do not introduce one unless
T-FDC-08 is sharded across multiple concurrent agents on disjoint
subdirectories AND each writes only to its own subdirectory.

---

## Notes

- All tasks except T-FDC-06 and the closeout reference `cli/**`; the
  CLI-PATTERN must be honored (stdlib only, `main(argv)` for testability,
  subparser style, exit codes 0/1/2).
- T-FDC-04 + T-FDC-05 are serialized because they edit the same file
  (`state_builder.py`). Do NOT mark them `[P]`.
- T-FDC-08 may be split into N per-subdirectory subtasks during F-02 dispatch
  WITHOUT amending this file -- the Software Developer dispatches them as
  ad-hoc subtasks of T-FDC-08.
- If F-02 discovers a real gap (e.g. an in-scope artifact whose role does not
  fit any `type` enum value), STOP and escalate to the Architect; do NOT
  silently invent an enum value.
- Test baseline at /tasks: 152 passing. F-02 close gate: >= 152 with new tests
  added on top.
