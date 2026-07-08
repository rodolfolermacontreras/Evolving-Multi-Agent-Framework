---
id: SDD-20260626MAINT-plan
type: plan
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# PLAN: SDD-048 -- Maintainability + right-sizing

- Spec: [`spec.md`](spec.md) | Tasks: [`tasks.md`](tasks.md) | CLARIFY: [`clarify.md`](clarify.md)
- ADR (C-2): [`../../docs/ADR/023-dashboard-render-stdlib-only.md`](../../docs/ADR/023-dashboard-render-stdlib-only.md)
- Execution: F-45, SERIAL (shared serial surfaces -- no parallel fleet).

---

## C-1 -- module decomposition (locked boundaries)

`state_builder.py` is split into six sibling modules plus a thin facade. The
facade (`state_builder.py`) RETAINS the five locked functions physically and
byte-identical, plus the CLI entry points, and RE-EXPORTS everything else so the
public import surface is unchanged.

### Target module map

| Module | Holds (NON-locked unless noted) | Notes |
|--------|----------------------------------|-------|
| `state_builder.py` (facade) | **LOCKED:** `render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`. Plus `build`, `build_index` dispatch, `main`, `parse_args`, `_resolve_sdd_root`, `_positive_int`. Plus `from cli.<sibling> import *`-style explicit re-exports. | Locked funcs NEVER move. Re-exports keep `from cli.state_builder import X` working. |
| `state_builder_data.py` | `repo_root_for`, `Feature`, `_normalize_status_to_stage`, `detect_stage`, `load_features`, `PIBlock`, `load_pis`, `current_pi`, `resolve_display_pi`, `BacklogItem`, `load_backlog`, `load_roster`, `LedgerView`, `_group_dispatches`, `load_ledger`, `load_recent_commits`, `derive_next_action` + private derive helpers | Pure data assembly. No rendering. Foundation other modules import. |
| `state_builder_markdown.py` | `render_markdown` decomposed into per-section helpers (header, lifecycle, features, backlog, dispatches, decisions, footer) | **Primary C-1 + C-2 decompose target** (762 lines -> sub-120 helpers). NON-locked. |
| `state_builder_html.py` | non-locked html helpers: `split_commit_type`, `h`, `_pulse`, `_weighted_progress`, `_next_what`, `active_user_gates`, `_agents_for_feature`, `_stage_short`, `_next_for`; injectors: `inject_user_gates_html`, `render_lifecycle_pipeline`, `resolve_docs_cards`, `render_docs_row`, `load_display_order`, `order_features_for_display`, `inject_lifecycle_html`, backlog-reorder injectors, `inject_drag_html`, `inject_dispatches_html`, health-pill functions, `render_work_index` | NON-locked. `render_html` itself STAYS in the facade (locked). |
| `dashboard_server.py` | `served_html_with_refresh`, `DashboardHandler`, `_port_available`, `serve`, `handle_reorder_request` | HTTP server isolated (R-C1-3). |
| `doc_count.py` | `_iter_in_scope_artifacts`, `_resolve_sprint_id`, `build_doc_count`, `build_doc_count_by_sprint`, `render_count_table`, `cmd_count` | Doc-counter isolated (R-C1-3). `main` imports `cmd_count` back. |
| `work_index.py` | `build_index`, `_discover_sprints`, `_detect_sprint_status`, `_query_ledger_for_pi`, `_render_sprint_table` | Work-index builder isolated. |

### Lock-safety mechanism

- The five locked functions stay physically in `state_builder.py`; their source
  bytes are untouched, so `inspect.getsource()` -> `sha256` matches the golden
  hashes and `TestS1FootprintLockGuard` passes.
- Extract ONLY non-locked helpers into siblings, then add explicit re-import
  lines in `state_builder.py` (e.g. `from cli.state_builder_data import load_features, Feature, ...`)
  so `from cli.state_builder import load_features` still resolves. Zero test
  assertion changes (R-C1-5).
- `render_html` (locked, 658 lines) stays in the facade and is the ONLY remaining
  >120-line function -- the documented Article X exception (M-3 in validation-C1).

### Extraction order (one module per commit, suite green after each)

Leaf-first for confidence; the biggest decompose last:

1. **C1-E1 `doc_count.py`** -- self-contained leaf with its own tests.
2. **C1-E2 `dashboard_server.py`** -- HTTP server leaf (no data deps beyond build).
3. **C1-E3 `work_index.py`** -- build-index + sprint discovery.
4. **C1-E4 `state_builder_data.py`** -- data-assembly foundation.
5. **C1-E5 `state_builder_html.py`** -- non-locked html helpers + injectors.
6. **C1-E6 `state_builder_markdown.py`** -- `render_markdown` decomposed (highest value, done last).

After EACH commit: run `python -m pytest spec-driven-development/ --tb=no -q`
(540/2) and a before/after build diff (empty). If any extraction would require
editing a locked function, STOP and raise OWNER-ATTENTION (per Q-A).

---

## C-2 -- `string.Template` factoring (stdlib)

- Replace large interpolated f-string blocks in `render_markdown` (C1-E6) and the
  non-locked html injectors (C1-E5) with `string.Template`-based section helpers.
  Templates are module-level `string.Template` constants; helpers fill them with
  a `substitute`/`safe_substitute` mapping.
- `render_html` is NOT touched (locked). Its 658-line wall remains the documented
  exception.
- Net effect: the NON-locked render surface is composed of small, named helpers
  (each < ~120 lines), satisfying C-1 R-2 and C-2 R-2 together.
- ADR-023 records the decision (stdlib-only + `string.Template` + render_html
  exception). Proposed at F-44; Accepted at close.

---

## C-3 -- cutover date to config

- Add `"article_xi_cutover": "2026-06-08"` to `project.config.json` (the existing
  config surface from SDD-047).
- In `fleet.py`: read the field via a small stdlib `json` loader; keep
  `ARTICLE_XI_CUTOVER` as a module-level FALLBACK constant for when the field is
  absent; retain the existing explanatory comment (SDD-019.R8 Article XI
  grandfather migration). `_is_grandfathered` keeps its `cutover` parameter
  default sourced from the resolved value.
- A unit test asserts: config-present path and fallback path both yield
  `2026-06-08`, and `_is_grandfathered` verdicts are unchanged for existing
  spec dirs.

---

## D-2 -- combined lightweight-spec doc (shape only in F-44)

- F-45 creates ONE template under `templates/` (e.g. `lightweight-feature.md`)
  combining the four lifecycle docs into a single file with these sections:
  - Frontmatter (`type: feature` or a new combined type recognized by schema_lint).
  - `## Story` (what + why; the CLARIFY/SPEC essence).
  - `## Requirements` (RFC-2119 items with per-item IDs).
  - `## Plan` (cross-link or short inline; for <5-file work, inline is fine).
  - `## Validation Contract` (Required Items strict + Manual Checks + Definition
    of Done -- the Article X lock holder, NOT weakened).
  - `## Eligibility` (when the lightweight path is allowed: <5 files, no Level-2
    surface; references Article VI).
- Article X stays satisfied because the Validation Contract section is authored
  before implementation and its REQUIRED items are checkable.
- F-45 proves the path by running ONE real <5-file feature through the combined
  doc end-to-end (its lock holder validates).
- F-44 does NOT create the template file (that is implementation) -- it fixes the
  shape here and in [`validation-D2.md`](validation-D2.md).

---

## Q-F -- optional max-function-length lint

- OPTIONAL. If built: a stdlib `ast` walk over `cli/**` flags NON-locked
  top-level functions over a configured budget (default ~120). It MUST exclude
  the five locked names and MUST NOT fail the suite/gate. Surface as a `--check`
  advisory, not a blocking test.

---

## File-dependency note (F-45 serial execution)

The split touches shared serial surfaces:

- `cli/state_builder.py` (+ 6 new sibling modules) -- C-1/C-2.
- `cli/fleet.py` + `project.config.json` -- C-3.
- `cli/schema_lint.py` (possibly) + `templates/` -- D-2, optional Q-F.

All are shared, serially-edited files. F-45 therefore runs SERIAL -- no parallel
fleet workers on these files. One module extraction per commit; suite green after
each; locked functions never touched.

## Phasing summary

| Phase | Item(s) | Commits | Gate after |
|-------|---------|---------|-----------|
| P1 | C-3 | 1 | suite 540/2 + fleet tests |
| P2 | C-1 (E1..E6) + C-2 (folded into E5/E6) | 6 (one per module) | suite 540/2 + build diff empty + lock guard green, after EACH |
| P3 | D-2 | 1-2 | schema_lint clean + real <5-file proof |
| P4 (opt) | Q-F lint | 1 | advisory only, non-blocking |
| Close | ADR-023 -> Accepted; QA; ledger; owner pre-push | -- | all gates green |
