---
id: SDD-20260626MAINT-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# TASKS: SDD-048 -- Maintainability + right-sizing

- Spec: [`spec.md`](spec.md) | Plan: [`plan.md`](plan.md) | Validations: [`validation-C1.md`](validation-C1.md), [`validation-C2.md`](validation-C2.md), [`validation-C3.md`](validation-C3.md), [`validation-D2.md`](validation-D2.md)
- Execution: F-45, SERIAL. One module extraction per commit. Locked functions NEVER edited.
- Pre-flight (every task): suite at 540/2 before starting; locked-function guard green.

| Task ID | Item | Description | File Scope | Verify |
|---------|------|-------------|-----------|--------|
| T-048-01 | C-3 | Add `"article_xi_cutover": "2026-06-08"` to config; in `fleet.py` resolve cutover via stdlib `json` with `ARTICLE_XI_CUTOVER` fallback constant + retained comment; keep `_is_grandfathered` default sourced from resolved value. | ALLOW: `project.config.json`, `cli/fleet.py`. BLOCK: everything else. | `python -m pytest spec-driven-development/cli/test_fleet.py -q` green; new unit test asserts config + fallback both yield `2026-06-08` and `_is_grandfathered` verdicts unchanged. |
| T-048-02 | C-1 | Extract `doc_count.py` (leaf): `_iter_in_scope_artifacts`, `_resolve_sprint_id`, `build_doc_count`, `build_doc_count_by_sprint`, `render_count_table`, `cmd_count`. Re-import into `state_builder.py`. | ALLOW: new `cli/doc_count.py`, `cli/state_builder.py` (re-export lines + removed non-locked bodies only). BLOCK: any locked function body. | Suite 540/2; build diff empty; `from cli.state_builder import cmd_count` resolves; lock guard green. |
| T-048-03 | C-1 | Extract `dashboard_server.py`: `served_html_with_refresh`, `DashboardHandler`, `_port_available`, `serve`, `handle_reorder_request`. Re-import. | ALLOW: new `cli/dashboard_server.py`, `cli/state_builder.py` (re-exports). BLOCK: locked functions. | Suite 540/2; `serve` subcommand still works; lock guard green. |
| T-048-04 | C-1 | Extract `work_index.py`: `build_index`, `_discover_sprints`, `_detect_sprint_status`, `_query_ledger_for_pi`, `_render_sprint_table`. Re-import. | ALLOW: new `cli/work_index.py`, `cli/state_builder.py` (re-exports). BLOCK: locked functions. | Suite 540/2; `build-index` subcommand works; lock guard green. |
| T-048-05 | C-1 | Extract `state_builder_data.py`: all NON-locked `load_*`, dataclasses (`Feature`, `PIBlock`, `BacklogItem`, `LedgerView`), `detect_stage`, `current_pi`, `resolve_display_pi`, `derive_next_action`, `repo_root_for`, `_normalize_status_to_stage`, `_group_dispatches`, private helpers. Re-import. | ALLOW: new `cli/state_builder_data.py`, `cli/state_builder.py` (re-exports). BLOCK: 5 locked funcs (esp. `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions` STAY in facade). | Suite 540/2; all `from cli.state_builder import <data name>` resolve; lock guard green (golden hashes unchanged). |
| T-048-06 | C-1 + C-2 | Extract `state_builder_html.py`: non-locked html helpers + injectors (per plan map). Factor large interpolation into `string.Template` helpers (stdlib). `render_html` STAYS in facade (locked, untouched). Re-import. | ALLOW: new `cli/state_builder_html.py`, `cli/state_builder.py` (re-exports). BLOCK: `render_html` body + 4 other locked funcs. | Suite 540/2; `state.html` build byte-equivalent; no non-locked html function > ~120 lines; lock guard green. |
| T-048-07 | C-1 + C-2 | Extract `state_builder_markdown.py`: decompose `render_markdown` (762 lines) into per-section helpers (header/lifecycle/features/backlog/dispatches/decisions/footer) via `string.Template` (stdlib). Re-import. | ALLOW: new `cli/state_builder_markdown.py`, `cli/state_builder.py` (re-exports). BLOCK: locked functions. | Suite 540/2; `state.md` build byte-equivalent; no helper > ~120 lines; lock guard green. |
| T-048-08 | C-2 | Finalize ADR-023 cross-references; confirm no third-party import anywhere in `cli/**`; `render_html` exemption documented. | ALLOW: `docs/ADR/023-dashboard-render-stdlib-only.md` (cross-ref polish only). BLOCK: code. | Import scan over `cli/**` = stdlib only; `schema_lint.py` exit 0; ADR present, Status Proposed. |
| T-048-09 | D-2 | Create combined lightweight-feature template under `templates/` per plan shape (Story / Requirements / Plan / Validation Contract / Eligibility); ensure `schema_lint` recognizes its frontmatter `type`. | ALLOW: new `templates/lightweight-feature.md`, possibly `cli/schema_lint.py` (type recognition). BLOCK: four-doc path regressions. | `schema_lint.py` exit 0; four-doc path still accepted; template sections present. |
| T-048-10 | D-2 | Prove the lightweight path on ONE real <5-file feature end-to-end; its lock holder validates (Article X intact). | ALLOW: a new real spec dir using the combined doc. BLOCK: weakening any existing validation. | The real feature's fleet/lock check passes; validation contract present + checkable. |
| T-048-11 (OPT) | Q-F | OPTIONAL stdlib `ast` max-function-length advisory lint over `cli/**`; excludes the 5 locked functions; non-blocking. | ALLOW: new `cli/length_lint.py` (+ test). BLOCK: any change that fails the suite/gate. | Lint runs as advisory `--check`; excludes locked funcs; suite still 540/2 (not gated by lint). |
| T-048-12 | all | Close: flip ADR-023 to Accepted under owner approval; QA pass; ledger entries; owner pre-push gate. | ALLOW: `docs/ADR/023-*.md` (Status flip), ledger. BLOCK: code. | Full suite 540/2; `schema_lint.py` exit 0; owner approves push. |

## Notes

- **Locked-function guard (every code task):** before committing, confirm
  `TestS1FootprintLockGuard` is green and golden SHA-256 hashes are unchanged. If
  a task cannot meet its target without editing a locked function, STOP and raise
  OWNER-ATTENTION (Q-A) -- do NOT proceed with approach (b).
- **One extraction per commit (T-048-02..07):** suite 540/2 + build diff empty
  after EACH. Never batch two module extractions into one commit.
- **Backward-compat imports:** every extraction adds explicit re-import lines to
  `state_builder.py` so `cli/test_state_builder.py` imports are unmodified.
- **Serial only:** all tasks touch shared serial surfaces -- no parallel fleet.
- **Staging:** explicit-path `git add <file>` only, never `git add -A`.
- **C-2 has no standalone extraction task:** it folds into T-048-06 and T-048-07
  (factoring) + T-048-08 (ADR/scan). `render_html` stays locked throughout.
