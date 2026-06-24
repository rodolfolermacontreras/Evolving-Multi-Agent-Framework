---
id: SDD-20260610STATEBUILDERFIX-tasks
type: tasks
status: done
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Task List: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Plan Reference: [`plan.md`](./plan.md)
- Validation Reference: [`validation.md`](./validation.md)
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slots F-21 (CLARIFY/SPEC/PLAN/TASKS) + F-22 (IMPLEMENT) + F-23 (close prep + Sprint 11 kickoff)
- Author: Principal Architect (EM-routed Sprint 10 F-21)
- Date: 2026-06-10
- Test baseline: 337 passed, 2 skipped (PI-5 close, commit `8417818`)
- Status: **DONE LOCALLY** -- F-23 owner close-prep approval recorded; no commit or push performed; commit pending

---

## No Silent Deferral Rule

Sprint 10 inherits the Sprint 7/8/9 owner direction: if a REQUIRED item in [`validation.md`](./validation.md) cannot close at F-22, the feature does not close and Sprint 10 does not close. No REQUIRED item may be marked deferred silently.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

---

## Baseline Block (T-040-01)

Current behavior captured at F-21 before any implementation:

- `derive_next_action(sdd_root, pi, features)` in `cli/state_builder.py` currently chooses active focus by static feature stage order: IMPLEMENT first, REVIEW second, first unchecked PI checkbox third, and backlog fallback last.
- The current active-focus path uses frontmatter-derived feature state and PI checkboxes only. It does not inspect validation checkbox state, current Sprint 10 / SDD-040 allocation, or git recency.
- `DashboardHandler.do_GET` currently rebuilds state on every root-page GET by calling `build(... write=False, live_html=True, port=server_port)`.
- Served HTML currently has no locked, tested, configurable meta refresh contract. The serve command prints a refresh claim, but the artifact contract does not bind it.
- `serve(sdd_root, host, port, open_browser)` currently accepts `--host`, `--port`, and `--no-open`; it has no `--refresh-seconds` flag.
- Non-serve invocation writes static `state.md`, `state.html`, and `work-index.md`; this behavior remains required.

T-040-01 is complete for planning purposes. T-040-02 through T-040-06 remain pending and must be executed in F-22.

---

## Task Breakdown

| Task ID | Description | File Scope | Required Tests / Verification | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-------------------------------|--------|------|------|-------------------------|--------|
| T-040-01 | Read current `state_builder.py` active-focus path, serve handler, and argparse surface; document baseline in this file. | Read-only: `cli/state_builder.py`; write: this `tasks.md` baseline block. | Baseline block present and consistent with current code; no implementation files modified. | S | none | AFK | No | done |
| T-040-02 | Implement active-focus combination rule: current PI/Sprint allocation scope guard, unchecked REQUIRED validation preference, bounded git-log recency tie-break via stdlib `subprocess.run`, current sprint anchor, then existing fallback chain. | `cli/state_builder.py` additive helper + prepend call in `derive_next_action`; `cli/test_state_builder.py` new tests only. | Add `TestActiveFocusHeuristic.test_scope_guard_prefers_current_sprint_sdd040_over_stale_frontmatter`; `test_prefers_unchecked_required_validation_in_scoped_candidates`; `test_git_recency_breaks_ties_with_bounded_subprocess`; `test_falls_back_to_existing_chain_when_helper_returns_none`. Closes R1 and part of R7. Evidence: focused pytest 135 passed; active-focus smoke selects SDD-040. | S | T-040-01 | AFK | No | done |
| T-040-03 | Implement serve-only handler-side meta refresh while preserving existing rebuild-on-GET behavior. No JS, SSE, watcher, or background thread. | `cli/state_builder.py` served HTML path only; `cli/test_state_builder.py` new tests only. | Add `TestServeModeRefresh.test_served_html_includes_meta_refresh_with_default_5_seconds`; `test_served_html_uses_refresh_seconds_override`; `test_static_html_written_without_meta_refresh`; `test_served_refresh_adds_no_script_tag`. Closes R3 and part of R7. Evidence: focused pytest 135 passed; serve smoke `meta7 True`, `script False`. | S | T-040-02 | AFK | No | done |
| T-040-04 | Wire serve-only `--refresh-seconds` cadence flag with default 5 and positive integer validation. Reject zero, negative, and non-integer values before server start. | `cli/state_builder.py` argparse/main/serve plumbing; `cli/test_state_builder.py` new tests only. | Add `TestRefreshCadenceFlag.test_parse_args_serve_refresh_seconds_default_is_5`; `test_parse_args_serve_refresh_seconds_accepts_positive_integer`; `test_parse_args_serve_refresh_seconds_rejects_zero`; `test_parse_args_serve_refresh_seconds_rejects_negative`. Closes R5 and part of R7. Evidence: focused pytest 135 passed; served override cadences 7 and 6 verified by urllib. | S | T-040-03 | AFK | No | done |
| T-040-05 | Regression sweep: preserve non-serve static generation and stdlib-only contract. Verify helper-none fixture keeps static output stable and existing tests stay green. | Verification against `cli/state_builder.py`, `cli/test_state_builder.py`, generated `exec/state.md`, `exec/state.html`, `exec/work-index.md` as artifacts only. | Existing `TestDeterministic.test_deterministic_output`, `TestSecurityAudit.test_no_script_tags`, `TestSecurityAudit.test_stdlib_only_imports`, `TestS1FootprintLockGuard.test_s1_footprint_locked`, and `TestCountSubcommand.test_count_no_subparser_breakage_serve_unchanged` pass unmodified. Add static-output helper-none regression test if existing coverage is not enough. Closes R2, R4, R6. Evidence: focused pytest 135 passed; full pytest 349 passed, 2 skipped; schema lint clean. | S | T-040-02, T-040-03, T-040-04 | AFK | No | done |
| T-040-06 | F-22/F-23 close verification: full pytest, schema lint, state regeneration, smoke test, serve-mode manual check, validation audit, owner close-prep approval record. | Verification only; close artifacts updated in F-23, not during implementation. | Run `python -m pytest spec-driven-development/ --tb=no -q`; run `python spec-driven-development/cli/schema_lint.py`; run `python spec-driven-development/cli/state_builder.py`; confirm regenerated `state.md` does not say `Active focus: azure-decommission`; start serve, edit a `specs/**` file, confirm browser refresh without manual CLI re-run; record owner approval evidence before any push. Closes R8, R9, M1, M2, M3. Evidence: full pytest 349 passed, 2 skipped; schema lint clean; state regenerated; M1/M2 checked; M3 checked from owner evidence via EM prompt, 2026-06-10: `Approve close prep, no push`. No commit or push performed; commit pending. | S | T-040-05 | HITL | No | done |

## Dependency Graph

```
T-040-01 (baseline doc) -> T-040-02 (parser fix) -> T-040-03 (meta refresh) -> T-040-04 (cadence flag) -> T-040-05 (regression) -> T-040-06 (close verification)
```

All tasks serialize within the same file (`cli/state_builder.py`) and within the same F-22 implementation session.

## Batch Plan

- **Batch 0 (F-21):** CLARIFY Q-A..Q-E answered; spec/plan/tasks finalized; validation contract locked. **Done by this artifact set.**
- **Batch 1 (F-22):** T-040-02 -> T-040-03 -> T-040-04 -> T-040-05 -> T-040-06, sequential, single session.
- **Batch 2 (F-23):** Sprint 10 close and SPRINT-11 kickoff authoring, owned by Principal SW Dev + EM. Done locally with owner approval evidence `Approve close prep, no push`; no commit or push performed.

## Constraints

Implementers MUST NOT modify:

- `render_markdown` output contract except through existing `next_action` input.
- The existing fallback behavior inside `derive_next_action` for helper-none cases.
- `DashboardHandler._send` security headers or CSP semantics.
- Existing rebuild-on-GET behavior in `DashboardHandler.do_GET`.
- Existing `serve --host`, `serve --port`, or `serve --no-open` behavior.
- Any existing test class or test name in `cli/test_state_builder.py`.
- `constitution/**`, SDD-036/037/038/034/039, or Azure decommission work.

## Notes

- Maximum task count budget: 9. Actual: 6.
- T-040-01 is documentation-only and complete at F-21. Implementation tasks remain pending.
- Owner review is required at T-040-06 for M1/M2 evidence and pre-push approval.
- Fleet dispatch is not justified: one source file, one test file, and a tight validation surface.

## F-22 Evidence Summary

- Focused tests: `python -m pytest spec-driven-development/cli/test_state_builder.py -q` -> 135 passed.
- Full tests: `python -m pytest spec-driven-development/ --tb=no -q` -> 349 passed, 2 skipped.
- Schema lint: `python spec-driven-development/cli/schema_lint.py` -> clean.
- State regeneration: `python spec-driven-development/cli/state_builder.py` wrote `exec/state.md`, `exec/state.html`, and `exec/work-index.md`; active focus no longer says `azure-decommission`.
- Serve verification: `serve --no-open --port 8877 --refresh-seconds 6`; after editing `validation.md`, a later stdlib `urllib` GET returned configured meta refresh and SDD-040 focus without rerunning the CLI.
- F-23 close prep: owner evidence from EM prompt, 2026-06-10: `Approve close prep, no push`; M3 checked; Sprint 10 closed locally; no commit or push performed; commit pending.

## F-23 Evidence Summary

- Owner approval: `Approve close prep, no push` from Executive Manager prompt, 2026-06-10. Approval covers local close prep and explicitly disallows push.
- Backlog/PI close: SDD-040 marked DONE locally in BACKLOG; PI-6 Sprint 1 / Sprint 10 marked CLOSED locally with PI-6 still ACTIVE and Sprint 11 / SDD-036 next planned.
- Sprint close ledger: `exec/sprint-progress.md` appended with `### Sprint 10 -- CLOSED` and the no-push/no-commit caveat.
- Sprint 11 kickoff: `feature-prompts/SPRINT-11-KICKOFF.prompt.md` authored for SDD-036 only; `feature-prompts/README.md` indexed it.
- Regeneration: `exec/state.md`, `exec/state.html`, and `exec/work-index.md` regenerated only via `python spec-driven-development/cli/state_builder.py`.
- Commit chain: local close prep, commit pending.
