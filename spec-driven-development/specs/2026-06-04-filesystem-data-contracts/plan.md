---
id: SDD-FDC-001-plan
type: plan
status: done
owner: principal-architect
updated: 2026-06-06
feature: filesystem-data-contracts
sprint: PI-4 / Sprint 4
spec: spec.md (APPROVED WITH CONDITIONS 2026-06-05)
adr: docs/ADR/012-filesystem-frontmatter-data-contract.md
implementation_targets: cli/schema_lint.py, cli/state_builder.py, cli/hooks/commit-msg
test_targets: cli/test_schema_lint.py, cli/test_state_builder.py
---

# Implementation Plan: Filesystem Data Contracts (Sprint 4)

- Spec Reference: `specs/2026-06-04-filesystem-data-contracts/spec.md` (SDD-FDC-001)
- Validation Contract: `specs/2026-06-04-filesystem-data-contracts/validation.md`
- ADR: `docs/ADR/012-filesystem-frontmatter-data-contract.md`
- Author: Principal Architect (co-authored with Principal Software Developer)
- Status: active
- Last Updated: 2026-06-05

---

## 1. Approach Summary

Ship the filesystem data contract for `specs/**` + `sprints/**` as five additive
deliverables, in dependency order:

1. A documented frontmatter schema (the data contract) with locked closed enums.
2. A schema-lint extension that validates the contract, reusing the existing
   `parse_frontmatter` parser.
3. A stdlib doc-count rollup helper + a new `count` subcommand on
   `state_builder.py` (its own handler, never touching locked S1 code).
4. A commit-message convention doc + an opt-in `commit-msg` hook script.
5. A frontmatter backfill of all in-scope artifacts so the lint runs green.

Two cross-cutting guards run alongside: an automated S1 lock guard test
(`inspect.getsource` + `hashlib.sha256` vs golden hashes from `b7ce642`) and the
full existing suite (no regression).

The binding decisions, enums, and the `parse_frontmatter` shared-boundary
rationale are recorded in ADR-012. This plan is the technical "how"; task
decomposition (`/tasks`) is handed to the Principal Software Developer next.

### Hard constraints enforced throughout

- `render_html()` and T-001..T-004 (`load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`) from `b7ce642` are IMMUTABLE.
  Additive code only.
- Stdlib only (LESSON-001 / CLI-PATTERN rule 1). No PyYAML.
- Reuse `parse_frontmatter` via `sys.path.insert(0, str(CLI_DIR))` import. Do NOT
  duplicate the parser.
- A `{}` parse result is treated as missing/unparseable -- skip or flag, never
  crash.

### Locked decisions (owner/Architect-approved)

| Item | Locked value |
|------|--------------|
| Required fields | `id`, `type`, `status`, `owner`, `updated` |
| `type` enum | `spec \| plan \| tasks \| validation \| clarification \| sprint \| retro \| lessons \| index \| session` |
| `status` enum | `draft \| active \| blocked \| done \| superseded \| archived` |
| In scope | `specs/**` + `sprints/**` markdown only |
| `count` default | flat global `{ by_status, by_type, total }` (D5) |
| `--sprint <id>` | optional selector, narrows rollup, no top-level shape change (D5) |
| `by_sprint` | optional grouped key, additive, no top-level shape change (D5) |
| Zero-count policy | emit every known enum key with explicit `0` |
| Hook path | `spec-driven-development/cli/hooks/commit-msg` |
| Commit convention | doc + opt-in hook only (no CI, no auto-install) (D3) |

---

## 2. Implementation Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Schema contract doc + locked enums | none | `frontmatter-schema.md` |
| 2 | Schema-lint extension | Phase 1 | `schema_lint.py` contract validator + tests |
| 3 | Doc-count rollup + `count` subcommand | Phase 1 | `state_builder.py count` + tests |
| 4 | S1 lock guard test | none (parallel) | golden-hash guard test |
| 5 | Commit convention doc + opt-in hook | none (parallel) | `COMMIT-CONVENTION.md` + `cli/hooks/commit-msg` |
| 6 | Frontmatter backfill | Phase 1 | all in-scope artifacts carry valid frontmatter |

### Phase 1 -- Schema contract doc (Effort: S)

Author `specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md`. It is
the human-readable data contract referenced by ADR-012. Contents:

- The five required fields with type and semantics.
- The locked `type` and `status` enum value sets (verbatim from the table above).
- The one-`type`/one-`status`-per-artifact assumption.
- The "`{}` parse result = missing/unparseable" rule for consumers.
- A canonical example block.

No code. This doc is the single prose reference both the lint and the rollup
point to.

### Phase 2 -- Schema-lint extension (Effort: M)

Extend `cli/schema_lint.py` additively. The existing checkers
(`check_agent`/`check_skill`/`check_prompt`), the `Finding` dataclass,
`parse_frontmatter`, and `scan()` are extended, not rewritten.

New module-level constants:

```python
REQUIRED_CONTRACT_FIELDS = ("id", "type", "status", "owner", "updated")
ARTIFACT_TYPE_ENUM = {"spec", "plan", "tasks", "validation", "clarification",
                      "sprint", "retro", "lessons", "index", "session"}
ARTIFACT_STATUS_ENUM = {"draft", "active", "blocked", "done", "superseded",
                        "archived"}
```

New checker function:

```python
def check_artifact(path: Path) -> list[Finding]:
    """specs/** + sprints/** markdown require the frontmatter data contract."""
```

Behavior (kind = `"artifact"`):

- `parse_frontmatter(text)` -> `{}` => one finding: "no YAML frontmatter
  delimiters" (treated as missing/unparseable, never a crash).
- For each field in `REQUIRED_CONTRACT_FIELDS` absent/empty => a finding naming
  the file and the missing field (satisfies R1/AC-1).
- `type` present but not in `ARTIFACT_TYPE_ENUM` => a finding naming the bad
  value and the allowed set.
- `status` present but not in `ARTIFACT_STATUS_ENUM` => a finding likewise.
- (Best-effort, non-blocking) `updated` not matching `^\d{4}-\d{2}-\d{2}$` =>
  a `WARNING` severity finding; does not by itself fail the gate unless promoted.

`scan()` gains an in-scope walk:

```python
specs_dir = repo_root / "spec-driven-development" / "specs"
sprints_dir = repo_root / "spec-driven-development" / "sprints"
for base in (specs_dir, sprints_dir):
    if base.is_dir():
        for p in sorted(base.rglob("*.md")):
            findings.extend(check_artifact(p))
```

`check_artifact` reuses the existing `parse_frontmatter`; no parser duplication.
Exit-code behavior is unchanged: non-empty findings => `return 1` (R1), empty =>
`return 0` (R2). Template/example markdown that should be excluded (if any) is
filtered by an explicit skip list defined in Phase 2, decided at `/tasks`.

### Phase 3 -- Doc-count rollup + `count` subcommand (Effort: M)

This is the core CLI deliverable. It follows CLI-PATTERN.md and the existing
`state_builder.py` subparser style.

**3a. Shared-parser bootstrap.** Near the top of `state_builder.py`, after the
existing imports, add the established `sys.path` bootstrap and import:

```python
CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))
from schema_lint import parse_frontmatter  # noqa: E402  (shared boundary, ADR-012)
```

No fallback re-implementation. If the import fails, that is a real environment
error surfaced to stderr, not silently patched.

**3b. Rollup helper (pure, testable):**

```python
def build_doc_count(sdd_root: Path, sprint: str | None = None) -> dict:
    """Walk specs/** + sprints/** markdown, parse frontmatter, roll up counts.

    Returns the flat global contract:
        { "by_status": {<status>: int}, "by_type": {<type>: int}, "total": int }
    When `sprint` is given, only artifacts whose resolved sprint matches are
    counted; the top-level shape is unchanged (D5).
    """
```

Rules:

- Imports the locked enums from `schema_lint` (`ARTIFACT_TYPE_ENUM`,
  `ARTIFACT_STATUS_ENUM`) so rollup and lint share one definition.
- **Zero-count policy:** seed `by_status` and `by_type` with EVERY known enum key
  at `0` before counting, so the output shape is stable for the dashboard
  regardless of which values are present.
- For each in-scope `*.md`: `fm = parse_frontmatter(text)`. If `fm == {}` =>
  skip (unparseable/missing) -- never crash. Otherwise increment `by_type[fm[type]]`
  and `by_status[fm[status]]` when present and in-enum; an out-of-enum value is
  skipped (lint, not count, reports it).
- `total = sum(by_status.values())`. **Invariant (asserted in tests):**
  `total == sum(by_status.values()) == sum(by_type.values())`, which holds
  because each counted artifact contributes exactly one `type` and one `status`
  (the one-`type`/one-`status` assumption from ADR-012).
- Optional `by_sprint`: a separate helper `build_doc_count_by_sprint(sdd_root)`
  returns `{ <sprint_id>: <flat contract> }` and is attached under a `by_sprint`
  key ONLY when explicitly requested (`--by-sprint`), never altering the
  top-level keys.

**3c. `count` handler (CLI-PATTERN rule 9 -- its own function, main() not
bloated):**

```python
def cmd_count(args: argparse.Namespace, sdd_root: Path) -> int:
    """Handler for the `count` subcommand."""
    rollup = build_doc_count(sdd_root, sprint=args.sprint)
    if getattr(args, "by_sprint", False):
        rollup["by_sprint"] = build_doc_count_by_sprint(sdd_root)
    if args.format == "table":
        print(render_count_table(rollup))
    else:
        print(json.dumps(rollup, indent=2))
    return 0
```

Plus a small `render_count_table(rollup) -> str` formatter (human view, R4/AC-4).

**3d. Subparser wiring** (in `parse_args`, alongside `serve` / `build-index`):

```python
sub_count = sub.add_parser("count",
    help="Roll up specs/** + sprints/** artifact counts by status and type.")
sub_count.add_argument("--format", choices=("json", "table"), default="json")
sub_count.add_argument("--sprint", default=None,
    help="Narrow the rollup to one sprint id (top-level shape unchanged).")
sub_count.add_argument("--by-sprint", action="store_true",
    help="Attach an additive by_sprint grouped view.")
```

**3e. `main()` dispatch** -- add ONE branch, delegating to the handler (main stays
thin):

```python
if args.cmd == "count":
    return cmd_count(args, sdd_root)
```

`render_html()` and T-001..T-004 are not referenced anywhere in this path.
Decoupling is provable by construction (Architect review, verified).

### Phase 4 -- S1 lock guard test (Effort: S; parallel-safe)

Satisfies R5/AC-5. Lives in `cli/test_state_builder.py` (new test, e.g.
`test_s1_footprint_locked`). Mechanism: stdlib only, no git dependency at test
time.

```python
import hashlib, inspect
import state_builder as sb

LOCKED = ("render_html", "load_sprint_table", "load_sprint_goal",
          "detect_current_sprint", "load_decisions")

GOLDEN_S1_HASHES = {
    # captured once from the b7ce642 checkout -- see capture procedure below
    "render_html": "<sha256>",
    "load_sprint_table": "<sha256>",
    "load_sprint_goal": "<sha256>",
    "detect_current_sprint": "<sha256>",
    "load_decisions": "<sha256>",
}

def _sha(name):
    src = inspect.getsource(getattr(sb, name))
    return hashlib.sha256(src.encode("utf-8")).hexdigest()

def test_s1_footprint_locked():
    for name in LOCKED:
        assert _sha(name) == GOLDEN_S1_HASHES[name], f"S1 lock broken: {name}"
```

**Golden-hash capture procedure (one-time, done during `/tasks`/implement):**

1. `git stash` any working changes, then
   `git worktree add ../wt-b7ce642 b7ce642` (or `git checkout b7ce642` in a
   scratch clone) to materialize the locked source.
2. Run a tiny stdlib capture snippet against that checkout's `state_builder.py`:
   `python -c "import hashlib,inspect,state_builder as sb; [print(n, hashlib.sha256(inspect.getsource(getattr(sb,n)).encode()).hexdigest()) for n in (...)]"`
   from inside `cli/`.
3. Paste the five resulting digests into `GOLDEN_S1_HASHES` in the test.
4. Remove the worktree (`git worktree remove ../wt-b7ce642`).

Because `inspect.getsource` returns only the function body text (robust to line
shifts elsewhere in the file), additive edits around the locked functions do not
break the hash; only edits to the locked functions themselves do. That is the
intended trip-wire.

### Phase 5 -- Commit convention doc + opt-in hook (Effort: S; parallel-safe)

Satisfies O1/O2 (best-effort). Per D3: documentation + opt-in only, no CI gate,
no auto-install.

- `docs/COMMIT-CONVENTION.md`: documents the `type: short description` format
  (matching the existing repo convention: `feat`, `fix`, `refactor`, `test`,
  `docs`, etc.), with valid/invalid examples and the install instructions.
- `cli/hooks/commit-msg`: a stdlib Python (or POSIX `sh`) script that reads the
  commit message file (argv[1]), checks the first line against
  `^(feat|fix|refactor|test|docs|chore|spec|plan)(\([\w-]+\))?: .+`, exits `0`
  on match, prints a pointer to `COMMIT-CONVENTION.md` and exits non-zero
  otherwise. No emojis in output.
- Install path documented two ways: `git config core.hooksPath
  spec-driven-development/cli/hooks` OR copy into `.git/hooks/commit-msg`.
  Uninstalled state leaves commits unaffected (AC-6).

### Phase 6 -- Frontmatter backfill (Effort: M)

Satisfies R6. Add the five-field frontmatter block to every in-scope `specs/**`
and `sprints/**` markdown artifact that lacks it, choosing the correct `type`
from the enum (e.g. `spec.md` -> `spec`, `plan.md` -> `plan`,
`validation.md` -> `validation`, `clarification-log.md` -> `clarification`,
sprint `INDEX.md` -> `index`, retro docs -> `retro`, lessons -> `lessons`,
session docs -> `session`). `status` is set from the artifact's real state
(`done` for shipped specs, `active` for in-flight, etc.); `owner` and `updated`
from git history / known authorship. After backfill, `schema_lint` must run
green over the in-scope tree (R2). This phase MUST land before the gate closes.

---

## 3. Module Boundaries and Exact New Names

| File | New symbol | Kind | Notes |
|------|-----------|------|-------|
| `cli/schema_lint.py` | `REQUIRED_CONTRACT_FIELDS`, `ARTIFACT_TYPE_ENUM`, `ARTIFACT_STATUS_ENUM` | constants | shared by rollup via import |
| `cli/schema_lint.py` | `check_artifact(path) -> list[Finding]` | function | new checker, kind `"artifact"` |
| `cli/schema_lint.py` | (extend) `scan()` | function | additive specs/** + sprints/** walk |
| `cli/state_builder.py` | `from schema_lint import parse_frontmatter` (+ enums) | import | via `sys.path.insert(0, CLI_DIR)` |
| `cli/state_builder.py` | `build_doc_count(sdd_root, sprint=None) -> dict` | function | pure rollup helper |
| `cli/state_builder.py` | `build_doc_count_by_sprint(sdd_root) -> dict` | function | optional grouped view |
| `cli/state_builder.py` | `render_count_table(rollup) -> str` | function | human formatter |
| `cli/state_builder.py` | `cmd_count(args, sdd_root) -> int` | handler | CLI-PATTERN rule 9 |
| `cli/state_builder.py` | (extend) `parse_args` / `main` | functions | one subparser + one dispatch branch |
| `cli/hooks/commit-msg` | hook script | executable | opt-in only |
| `docs/COMMIT-CONVENTION.md` | doc | markdown | convention reference |
| `specs/.../frontmatter-schema.md` | doc | markdown | data-contract reference |

Explicitly NOT touched: `render_html`, `load_sprint_table`, `load_sprint_goal`,
`detect_current_sprint`, `load_decisions`, `build()`, `serve()`, `build_index()`.

---

## 4. Data-Contract Schema + Locked Enums

```yaml
---
id: <stable-id>        # required, string (e.g. SDD-FDC-001)
type: <artifact-type>  # required, one of the type enum
status: <status>       # required, one of the status enum
owner: <owner>         # required, string
updated: <YYYY-MM-DD>  # required, ISO date
---
```

- `type` enum: `spec | plan | tasks | validation | clarification | sprint |
  retro | lessons | index | session`
- `status` enum: `draft | active | blocked | done | superseded | archived`
- One `type` and one `status` per artifact, counted once.
- A `{}` parse result is missing/unparseable: lint flags it, count skips it,
  neither crashes.

Full prose lives in `frontmatter-schema.md` (Phase 1) and the rationale in
ADR-012.

---

## 5. `count` CLI Surface + JSON Contract

```
state_builder.py count [--format json|table] [--sprint <id>] [--by-sprint] [--sdd-root PATH]
```

- Default `--format json`. Stable flat contract (D5):

  ```json
  { "by_status": { "<status>": 0 }, "by_type": { "<type>": 0 }, "total": 0 }
  ```

  Every enum key is present with an explicit integer (zero-count policy). `total`
  == `sum(by_status.values())` == `sum(by_type.values())`.
- `--sprint <id>`: narrows the counted set to one sprint; top-level shape
  unchanged.
- `--by-sprint`: additively attaches `"by_sprint": { "<sprint>": { <flat
  contract> } }`; top-level keys unchanged.
- `--format table`: human-readable table of the same counts; exit 0 (R4/AC-4).

---

## 6. Lint Extension Approach

Additive only: new constants + `check_artifact` + an extended `scan()` walk over
`specs/**` and `sprints/**`. Reuses `parse_frontmatter` (no duplication). Exit
semantics unchanged (`1` on findings, `0` clean). A small, explicit skip list
(decided at `/tasks`) excludes any in-tree templates/examples that must not be
linted as real artifacts.

---

## 7. Commit-msg Hook + Doc Approach

`docs/COMMIT-CONVENTION.md` documents `type: short description` with examples.
`cli/hooks/commit-msg` is an opt-in, stdlib-only script validating the first
line against the convention, pointing failures at the doc. Install via
`git config core.hooksPath spec-driven-development/cli/hooks` or manual copy.
No CI gate, no auto-install (D3). Uninstalled state leaves commits unaffected.

---

## 8. Frontmatter Backfill Approach

Add the five-field block to every in-scope artifact, deriving `type` from the
filename/role, `status` from real state, `owner`/`updated` from git history.
Run `schema_lint` iteratively until the in-scope tree is green. Backfill must
complete before the gate closes (R6). This is a mechanical, reviewable pass --
candidate for fleet dispatch with one-file-per-task scoping during `/tasks`.

---

## 9. Test Plan (mapped to validation.md)

| Validation item | Test(s) | File |
|-----------------|---------|------|
| R1 (missing field => finding + non-zero) | `test_check_artifact_missing_field`, `test_check_artifact_bad_enum` | `test_schema_lint.py` |
| R2 (valid set => exit 0, no findings) | `test_check_artifact_valid`, `test_scan_in_scope_clean` | `test_schema_lint.py` |
| R3 (count JSON shape + total invariant) | `test_count_json_contract`, `test_count_total_invariant`, `test_count_zero_counts`, `test_count_unparseable_skipped` | `test_state_builder.py` |
| R4 (`--format table` exits 0) | `test_count_table_format` | `test_state_builder.py` |
| R5 (S1 lock, golden hash) | `test_s1_footprint_locked` | `test_state_builder.py` |
| R6 (backfill complete) | `test_scan_in_scope_clean` (real tree) + manual run | `test_schema_lint.py` |
| R7 (no regression) | full existing suite | all `test_*.py` |
| O1 (opt-in hook behavior) | `test_commit_msg_hook_rejects_bad` / `_allows_good` (subprocess on scratch) | `test_state_builder.py` or new `test_commit_hook.py` |
| O2 (convention documented) | doc-presence assertion (optional) | n/a |

Test conventions: `tmp_path` fixture trees for in-scope artifacts; construct
frontmatter blocks inline; assert on `Finding` contents and `main(argv)` return
codes (no subprocess for lint/count); subprocess only for the hook (it is a real
git hook). `--sprint` and `--by-sprint` each get a focused test asserting the
top-level shape is unchanged.

---

## 10. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `sys.path` import of `schema_lint` fails in some run context | Low | Med | Use the same bootstrap `fleet.py`/`retro.py` use; surface real import errors to stderr; cover with a test that imports `parse_frontmatter` through `state_builder`. |
| Golden hashes captured from the wrong checkout | Low | High | Documented capture procedure pins `b7ce642`; review the digests in PR; the guard test fails loudly if wrong. |
| Backfill assigns wrong `type`/`status` to an artifact | Med | Low | Enum-validated by lint; reviewed per file; one-file-per-task dispatch keeps blast radius small. |
| Templates/examples in-tree get linted as real artifacts | Med | Low | Explicit skip list defined at `/tasks`; lint findings are reversible. |
| `count` and `lint` enum definitions drift | Low | Med | Single source: `count` imports the enums from `schema_lint`; a test asserts both reference the same sets. |
| Out-of-enum value silently dropped from count | Low | Low | By design count skips it; lint reports it -- documented; a test covers the split. |
| Total invariant violated by a multi-status artifact | Low | Med | One-`type`/one-`status` assumption enforced by contract; invariant asserted in tests. |

---

## 11. Effort Estimate

| Phase | Estimate | Notes |
|-------|----------|-------|
| 1 Schema doc | S | Prose only |
| 2 Lint extension | M | New checker + scan walk + tests |
| 3 count + rollup | M | Core CLI deliverable + tests |
| 4 S1 guard test | S | One test + one-time hash capture |
| 5 Convention + hook | S | Doc + opt-in script |
| 6 Backfill | M | Mechanical, file count bound; fleet-dispatchable |

Overall: **L** (sum), dominated by Phases 2, 3, and 6.

---

## 12. Validation Criteria

> Cross-reference rule: items reference spec AC / validation R-ids, not restated prose.

- [ ] AC-1 / R1 -- missing field => named finding + non-zero exit
- [ ] AC-2 / R2 -- valid in-scope tree => exit 0, no frontmatter findings
- [ ] AC-3 / R3 -- `count` JSON matches `{by_status, by_type, total}`; total invariant holds
- [ ] AC-4 / R4 -- `count --format table` prints table, exits 0
- [ ] AC-5 / R5 -- S1 lock guard test green (golden sha256 vs b7ce642)
- [ ] R6 -- all in-scope artifacts carry valid frontmatter (backfill complete)
- [ ] AC-7 / R7 -- full existing suite green
- [ ] AC-6 / O1 -- opt-in hook rejects bad / allows good; uninstalled unaffected
- [ ] O2 -- `COMMIT-CONVENTION.md` documents the format with examples

---

## 13. Handoff to /tasks

Task decomposition is handed to the **Principal Software Developer**. Suggested
decomposition boundaries (one concern per task, fleet-safe file scoping):

- T-A: `frontmatter-schema.md` (Phase 1) -- doc only.
- T-B: `schema_lint.py` contract validator + `test_schema_lint.py` (Phase 2).
- T-C: `state_builder.py` shared-parser import + `build_doc_count` +
  `render_count_table` (Phase 3a-3b) + tests.
- T-D: `state_builder.py` `cmd_count` handler + subparser + `main` dispatch
  (Phase 3c-3e) + tests. (Sequenced after T-C -- same file.)
- T-E: S1 lock guard test + golden-hash capture (Phase 4).
- T-F: `COMMIT-CONVENTION.md` + `cli/hooks/commit-msg` (Phase 5) -- parallel.
- T-G: frontmatter backfill (Phase 6) -- splittable per directory.

Watch items for the Software Developer during `/tasks`: T-C and T-D both edit
`state_builder.py` (sequence them, do not parallel-dispatch the same file); the
golden-hash capture (T-E) must run against the real `b7ce642` checkout before
the guard test is meaningful; the lint skip list for templates must be settled
before T-B closes.
