---
id: SDD-20260610STATEBUILDERFIX-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Validation Contract: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Contract Date: 2026-06-10
- Lock Timestamp: 2026-06-10 F-21 close
- Author: Principal Architect (EM-routed Sprint 10 F-21)
- Lock Point: `/tasks` (= F-21 close, fresh Sprint 10 session)
- Status: **DONE** -- F-22 implementation evidence complete; F-23 owner approval recorded for close prep with no push performed

---

## Lock Statement

This contract is LOCKED as of 2026-06-10 F-21 close. All REQUIRED items below are concrete and testable. F-22 implementation evidence checked R1-R9 plus M1/M2; F-23 close prep records M3 owner approval evidence.

Rule (Article X): zero unchecked REQUIRED items before implementation is considered complete. REQUIRED items cannot be loosened after lock without an explicit decision recorded here.

Sprint 10 inherits the Sprint 7/8/9 owner direction: **no silent REQUIRED deferral.** If a REQUIRED item cannot close at F-22, the feature does not close and Sprint 10 does not close.

---

## Required Items

- [x] **R1 -- Active-focus combination rule.** `state_builder.py` implements the CLARIFY Q-A rule: scope candidates to current PI/Sprint allocation (Sprint 10 / SDD-040 from PI-6 CURRENT_PI and BACKLOG), prefer scoped candidates with unchecked REQUIRED validation items, tie-break with bounded `git log` recency via stdlib `subprocess.run`, fall back to the current sprint anchor, then run the existing fallback chain if no candidate exists. Tests: `TestActiveFocusHeuristic.test_scope_guard_prefers_current_sprint_sdd040_over_stale_frontmatter`, `test_prefers_unchecked_required_validation_in_scoped_candidates`, `test_git_recency_breaks_ties_with_bounded_subprocess`, `test_falls_back_to_existing_chain_when_helper_returns_none`. Closes AC-1. Task: T-040-02. Evidence: `python -m pytest spec-driven-development/cli/test_state_builder.py -q` -> 135 passed; active-focus smoke regenerated `state.md` as `Finish validation for 'state-builder-fixes' (SDD-040)`.
- [x] **R2 -- Existing static generation preserved.** Non-serve invocation continues to write static `state.md`, `state.html`, and `work-index.md`. In a controlled fixture where the new active-focus helper returns no candidate, static output is byte-identical to the pre-SDD-040 baseline. Real-repo active-focus output may intentionally differ when the helper contributes. Tests: existing deterministic/static-output tests plus a helper-none regression test if needed. Closes AC-5. Task: T-040-05. Evidence: `TestActiveFocusHeuristic.test_falls_back_to_existing_chain_when_helper_returns_none`, `TestDeterministic.test_deterministic_output`, and `TestServeModeRefresh.test_static_html_written_without_meta_refresh` passed in focused and full pytest runs; regenerated static `state.html` has no refresh meta.
- [x] **R3 -- Serve-only meta refresh.** Served HTML includes `<meta http-equiv="refresh" content="N">` with the configured cadence. Static `state.html` written by non-serve invocation does not include that meta refresh. Implementation uses existing rebuild-on-GET behavior and introduces no JS, SSE, watcher, or background thread. Tests: `TestServeModeRefresh.test_served_html_includes_meta_refresh_with_default_5_seconds`, `test_served_html_uses_refresh_seconds_override`, `test_static_html_written_without_meta_refresh`, `test_served_refresh_adds_no_script_tag`. Closes AC-2. Task: T-040-03. Evidence: focused pytest passed; serve smoke with `--refresh-seconds 7` returned `meta7 True`, `focus True`, `script False`; second serve smoke with `--refresh-seconds 6` returned `meta6 True` after an allowed `validation.md` edit without rerunning the CLI.
- [x] **R4 -- Stdlib-only constraint (Article V).** No new third-party dependency is added. Implementation uses only stdlib modules and existing in-tree modules. Specifically prohibited: `watchdog`, `flask`, `fastapi`, `requests`, `pygit2`, and any other PyPI dependency. `subprocess` is permitted only for bounded `git log` recency. Tests: existing import audit in `TestSecurityAudit.test_stdlib_only_imports` updated only for stdlib additions if needed. Closes AC-4. Tasks: T-040-02, T-040-03, T-040-04, T-040-05. Evidence: no new imports added; `TestSecurityAudit.test_stdlib_only_imports` and `TestStdlibOnly.test_runtime_imports_are_stdlib_only` passed in the full suite.
- [x] **R5 -- Refresh cadence configurable via serve-only CLI flag.** The `serve` subcommand supports `--refresh-seconds N`, defaults to `5`, accepts positive integers, and rejects zero, negative, and non-integer values before the server starts. The flag does not apply to non-serve invocation. Tests: `TestRefreshCadenceFlag.test_parse_args_serve_refresh_seconds_default_is_5`, `test_parse_args_serve_refresh_seconds_accepts_positive_integer`, `test_parse_args_serve_refresh_seconds_rejects_zero`, `test_parse_args_serve_refresh_seconds_rejects_negative`. Closes AC-3. Task: T-040-04. Evidence: focused pytest passed; serve smoke confirmed override cadences 7 and 6 in served HTML.
- [x] **R6 -- Backwards compatibility sweep.** Existing tests in `cli/test_state_builder.py` pass without renaming or behavior changes, especially `TestDeterministic.test_deterministic_output`, `TestSecurityAudit.test_no_script_tags`, `TestS1FootprintLockGuard.test_s1_footprint_locked`, and `TestCountSubcommand.test_count_no_subparser_breakage_serve_unchanged`. Closes AC-5. Task: T-040-05. Evidence: `python -m pytest spec-driven-development/cli/test_state_builder.py -q` -> 135 passed; `python -m pytest spec-driven-development/ --tb=no -q` -> 349 passed, 2 skipped.
- [x] **R7 -- New tests cover both defects and cadence.** `cli/test_state_builder.py` gains new tests for active-focus selection, serve-only meta refresh, cadence parsing/validation, and helper-none static-output compatibility if not already covered. Test classes: `TestActiveFocusHeuristic`, `TestServeModeRefresh`, and `TestRefreshCadenceFlag`. Closes AC-1, AC-2, AC-3, and half of AC-6. Tasks: T-040-02, T-040-03, T-040-04. Evidence: all named classes are present and passed in the focused 135-test run.
- [x] **R8 -- Full test suite at PI-5 close baseline.** `python -m pytest spec-driven-development/ --tb=no -q` returns at least 337 passed plus the new SDD-040 tests, with the known 2 platform-conditional skips permitted and 0 failures. Closes AC-6. Task: T-040-06. Evidence: `python -m pytest spec-driven-development/ --tb=no -q` -> 349 passed, 2 skipped.
- [x] **R9 -- Schema lint clean.** `python spec-driven-development/cli/schema_lint.py` exits 0 after the SDD-040 spec directory is fully populated and the F-22 implementation has updated any artifact statuses it owns. Closes AC-6. Task: T-040-06. Evidence: `Schema lint clean. Scanned: C:\Training\Projects\Evolving-Multi-Agent-Framework`.

## Optional / Best-Effort Items

- [ ] **O1 -- Not applicable: file-watch fallback.** CLARIFY Q-B explicitly chose handler-side meta refresh plus existing rebuild-on-request, with no watcher/background thread. No OS-specific file-watch fallback is required.
- [ ] **O2 -- Not applicable: manual refresh endpoint.** CLARIFY Q-B and Q-C intentionally avoid new routes. The manual escape hatch remains browser refresh or a normal GET to `/`; no `POST /refresh` or `GET /refresh` endpoint is in scope.

## Specific Test Coverage Required

- [x] **Unit (R1):** `TestActiveFocusHeuristic` covers current Sprint 10 scope guard, unchecked REQUIRED validation preference, bounded git recency tie-break, and fallback-chain preservation.
- [x] **Unit/integration (R3):** `TestServeModeRefresh` covers meta refresh in served HTML, override cadence, static HTML exclusion, and no script tags.
- [x] **Unit (R5):** `TestRefreshCadenceFlag` covers default 5 seconds, positive override, and invalid cadence rejection.
- [x] **Regression (R2, R6):** helper-none non-serve fixture preserves static output; existing deterministic/security/lock/count tests pass unmodified.
- [x] **Import audit (R4):** no new third-party import in modified files.

## Manual Checks

- [x] **M1 -- Smoke test (R1).** After SDD-040 lands, regenerate `exec/state.md` with `python spec-driven-development/cli/state_builder.py` and confirm the `Active focus:` line does NOT say `Active focus: azure-decommission`. Evidence: regenerated `state.md` reported `Active focus: Finish validation for 'state-builder-fixes' (SDD-040)` during F-22 smoke.
- [x] **M2 -- Serve-mode verification (R3).** Start `python spec-driven-development/cli/state_builder.py serve`, edit a file under `specs/**`, and confirm the dashboard refreshes without a manual CLI re-run. Record the verification in the Sprint 10 close block at `exec/sprint-progress.md`. Evidence: served on port 8877 with `--refresh-seconds 6`; after editing this `validation.md` while the server was running, a later stdlib `urllib` GET returned `meta6 True` and `focus True` without rerunning `state_builder.py`.
- [x] **M3 -- Owner close-prep approval with no push.** Sprint 10 inherits the Sprint 7/8/9 owner direction: pre-push approval is mandatory. Evidence from Executive Manager prompt, 2026-06-10: owner selected `Approve close prep, no push`. This approval covers local Sprint 10 close prep and explicitly confirms no push should be performed. No commit or push was performed by F-23; commit remains pending.

## Tone / UX Check

The serve-mode dashboard is the only user-facing surface SDD-040 touches. No layout, color, typography, lifecycle pipeline, dispatch card, or aesthetic token work is in scope.

- [ ] **U1 -- No UX copy review required unless implementation adds visible refresh copy.** The locked mechanism is invisible meta refresh. If F-22 adds visible text such as `Last refreshed`, that copy must match the existing dashboard voice and be recorded here before close.

## Definition of Done

Implementation is merge-ready only when:

1. All REQUIRED items (R1-R9) above are checked, with concrete test-name evidence. No commit SHA is fabricated for F-23 because this close prep is local only; commit remains pending.
2. This contract lock remains intact from F-21; no REQUIRED item is loosened after lock without an explicit recorded decision.
3. No REQUIRED item is silently deferred.
4. Full test suite passes at PI-5 close baseline + new tests; schema lint exits 0; smoke test passes (M1); serve-mode is manually verified (M2); owner close-prep approval with no push is recorded (M3).

Production-code changes without a corresponding test require a task-level `[NO-TEST-NEEDED]` tag and accepted justification before the IMPLEMENT gate can pass.
