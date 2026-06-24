---
id: SDD-20260610STATEBUILDERFIX-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Feature Spec: SDD-040 -- state_builder.py parser fix + auto-refresh

- Date: 2026-06-10
- Author: Principal Architect (EM-routed Sprint 10 F-21)
- Status: **APPROVED** -- CLARIFY closed; implementation remains F-22
- Priority: P1
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slot F-21
- Spec ID: SDD-040
- Parent objective: PI-6 Dashboard Reinvestment + Carryover Cleanup ([`sprints/PI-6/CURRENT_PI.md`](../../sprints/PI-6/CURRENT_PI.md))
- Backlog row: [`BACKLOG.md`](../../backlog/BACKLOG.md) / SDD-040 (P1, S effort)
- Decision source: [`clarify.md`](./clarify.md), Q-A through Q-E answered by EM-synthesized owner-approved Sprint 10 kickoff decision, 2026-06-10.

---

## Problem Statement

The executive state dashboard (`exec/state.md` and the live `exec/state.html` served by `cli/state_builder.py`) has two defects that together undermine its single job: showing the owner what is actually happening on the project right now.

**Defect 1 -- stale active-focus heuristic.** The `Active focus:` line in `state.md` is computed by `derive_next_action` in `cli/state_builder.py`, which walks features by stage in fixed order (IMPLEMENT > REVIEW > PI commitments > backlog) using only spec-dir frontmatter as input. There is no runtime signal: no commit recency, no validation-completeness check, and no awareness of which feature has actually shipped. Owner verbatim 2026-06-10 via EM: "Still says Active focus: azure-decommission (stale -- that wrapped up)." The azure-decommission spec dir shipped at PI-5 close (`8417818`, 2026-06-09); the dashboard still points to it because the heuristic does not look at what shipped most recently or what is currently owed by the sprint validation contract.

**Defect 2 -- served dashboard page does not refresh itself.** The non-serve invocation (`python state_builder.py`) writes static `state.md`, `state.html`, and `work-index.md` files for git/diff use; that path is intentionally static. The serve subcommand rebuilds state on every HTTP GET, but served HTML does not drive periodic GETs in the browser. Owner verbatim 2026-06-10 via EM: "Static -- refreshes only when you re-run state_builder.py." SDD-040 makes the serve-mode refresh cadence explicit without changing the non-serve static-output contract.

---

## Goal

After this feature ships, the executive dashboard reflects what is actually active on the project without manual CLI re-runs in serve mode:

1. The `Active focus:` line tracks the current Sprint 10 / SDD-040 allocation first, then unchecked REQUIRED validation items, then bounded git-log recency, then current sprint anchor, then the existing fallback chain. It is no longer allowed to select unrelated stale work such as azure-decommission when SDD-040 is the current sprint anchor and has open REQUIRED validation work.
2. Served HTML refreshes itself using handler-side meta refresh. Each refresh issues a normal browser GET, and the existing HTTP handler rebuilds state on that request. No JavaScript, SSE, file watcher, polling thread, or background process is introduced.
3. The refresh cadence defaults to 5 seconds and can be configured only for serve mode through `serve --refresh-seconds N`, where `N` must be a positive integer.
4. Non-serve invocation continues writing static `state.md`, `state.html`, and `work-index.md` for git/diff use. Auto-refresh is serve-only. Controlled inputs where the new helper returns no candidate preserve the pre-SDD-040 output baseline; active-focus may intentionally differ when the helper contributes.

After this feature ships, the smoke test from [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md) section 5 passes: the regenerated `state.md` must NOT say "Active focus: azure-decommission".

---

## Acceptance Criteria

1. **AC-1 -- Active-focus combination rule.** Given PI-6 Sprint 10 is allocated to SDD-040 in CURRENT_PI and BACKLOG, and SDD-040 has unchecked REQUIRED validation items, when `state_builder.py` derives `Active focus:`, then it selects SDD-040 ahead of unrelated stale feature frontmatter. If multiple scoped candidates have unchecked REQUIRED validation items, bounded `git log` recency via stdlib `subprocess.run` breaks the tie. If the new helper returns no candidate, the existing fallback chain runs unchanged.
2. **AC-2 -- Serve-mode meta refresh.** Given the dashboard is served through `python spec-driven-development/cli/state_builder.py serve`, when the root page is returned, then the served HTML includes a meta refresh tag with the configured cadence and each browser refresh uses the existing rebuild-on-GET path. The meta refresh is present only in served HTML and is absent from static `state.html` written by non-serve invocation.
3. **AC-3 -- Configurable positive cadence.** Given the serve command is invoked without `--refresh-seconds`, then the refresh cadence is 5 seconds. Given `serve --refresh-seconds N` with a positive integer, then the served meta refresh uses `N`. Given zero, a negative integer, or a non-integer value, then argument validation rejects the command before the server starts.
4. **AC-4 -- Article V stdlib-only implementation.** The implementation adds no third-party dependencies and does not import `watchdog`, `flask`, `fastapi`, `requests`, `pygit2`, or any other PyPI package. `subprocess` is permitted only for bounded `git log` recency.
5. **AC-5 -- Non-serve backwards compatibility.** Non-serve invocation continues to write static `state.md`, `state.html`, and `work-index.md`. For controlled inputs where the active-focus helper returns no candidate, the rendered non-serve outputs remain byte-identical to the pre-SDD-040 baseline. When the helper contributes a candidate, only the intended `Active focus:` content may differ.
6. **AC-6 -- Close verification.** F-22 close evidence includes new tests for active-focus selection, served meta refresh, cadence parsing, and static-output compatibility; full pytest passes at or above the PI-5 close baseline of 337 passed with the known 2 platform-conditional skips; schema lint exits 0; regenerated `state.md` does not say "Active focus: azure-decommission".

---

## Affected Modules

- Files planned for F-22 implementation:
  - `spec-driven-development/cli/state_builder.py` -- additive helper for active-focus selection, serve-only meta refresh support, and serve-only `--refresh-seconds` argument plumbing.
  - `spec-driven-development/cli/test_state_builder.py` -- new tests only; existing test names and behavior are preserved.
- Files not in scope for F-22:
  - `constitution/` -- no constitution edit; any future constitution change requires ADR and owner approval outside SDD-040.
  - `spec-driven-development/exec/state.md`, `state.html`, and `work-index.md` -- regenerated artifacts, not source.
  - SDD-036/037/038/034/039 and Azure decommission artifacts.

## Data Model Changes

None. The active-focus helper reads existing frontmatter, existing validation.md checkbox state, PI-6 CURRENT_PI / BACKLOG allocation, and bounded `git log` output. The serve refresh path injects a tag into served HTML only. No persistent cache, new table, new frontmatter field, or schema migration is introduced.

## API Changes

- `cli/state_builder.py serve` gains one serve-only CLI flag: `--refresh-seconds N`, default `5`, positive integer required.
- Existing `serve --host`, `serve --port`, and `serve --no-open` behavior is preserved.
- Non-serve invocation gains no flags and no long-running behavior.

---

## Test Strategy

- **Unit: active-focus helper.** Add `TestActiveFocusHeuristic` tests in `cli/test_state_builder.py` covering current sprint scope guard, unchecked REQUIRED validation preference, bounded git recency tie-break via mocked stdlib `subprocess.run`, and fallback-chain preservation when the helper returns no candidate.
- **Unit/integration: served refresh.** Add `TestServeModeRefresh` tests covering served HTML meta refresh at the default cadence, served HTML meta refresh at an override cadence, static `state.html` without meta refresh, and no `<script>` tags.
- **Unit: cadence argument validation.** Add `TestRefreshCadenceFlag` tests covering default `5`, positive override, and rejection of zero/negative or non-integer values before `serve()` starts.
- **Regression: static-output compatibility.** Add or extend tests so a controlled fixture where the new helper returns no candidate preserves existing non-serve output. Existing tests in `cli/test_state_builder.py`, including `TestDeterministic`, `TestSecurityAudit`, `TestS1FootprintLockGuard`, and `TestCountSubcommand`, must continue to pass unmodified.
- **Import audit.** Reuse the existing stdlib import audit pattern and extend allow-list only for stdlib modules required by SDD-040, especially `subprocess` if not already present in the local allow-list.
- **Full validation.** Run `python -m pytest spec-driven-development/ --tb=no -q` and `python spec-driven-development/cli/schema_lint.py` at F-22 close.
- **Manual checks.** Regenerate state and confirm `Active focus:` is not azure-decommission; start serve mode, edit a file under `specs/**`, and confirm the browser refreshes without manual CLI re-run.

## Validation Contract

The binding validation contract for this feature lives in [`validation.md`](./validation.md). It is LOCKED at F-21 on 2026-06-10. All R1-R9 checkboxes remain unchecked until F-22 supplies implementation and verification evidence. No REQUIRED item may be silently deferred.

## Traceability Matrix

| Requirement | CLARIFY Question | Acceptance Criterion | Validation Row | Task ID |
|-------------|------------------|----------------------|----------------|---------|
| Current-sprint active-focus combination rule | Q-A | AC-1 | R1, R7 | T-040-02 |
| Preserve fallback chain when helper has no candidate | Q-A, Q-E | AC-1, AC-5 | R1, R2, R6 | T-040-02, T-040-05 |
| Serve-only handler-side meta refresh | Q-B | AC-2 | R3, R7 | T-040-03 |
| Positive integer cadence flag with default 5 seconds | Q-C | AC-3 | R5, R7 | T-040-04 |
| Stdlib-only implementation and dependency prohibition | Q-D | AC-4 | R4 | T-040-02..T-040-05 |
| Non-serve static artifact compatibility | Q-E | AC-5 | R2, R6 | T-040-05 |
| Close verification, smoke test, schema lint, full pytest | -- | AC-6 | R8, R9, M1, M2, M3 | T-040-06 |

## Open Questions

- **None for F-21.** Q-A through Q-E are answered in [`clarify.md`](./clarify.md).
- OWNER-ATTENTION: none.
- ADR required: no.

## Out of Scope

- **SDD-036 (lifecycle pipeline + drag-to-reorder w/ safeguards).** PI-6 Sprint 11. MUST NOT be absorbed into Sprint 10.
- **SDD-037 (Dispatches + health pills).** PI-6 Sprint 12. MUST NOT be absorbed into Sprint 10.
- **SDD-038 (aesthetic tokens / polish).** PI-6 Sprint 13 contingency. MUST NOT be absorbed into Sprint 10.
- **SDD-034 content-shingle dedup upgrade.** Carry-forward item; not part of SDD-040.
- **SDD-039 Article VII wording clarification.** Requires ADR/owner approval before any constitution wording change; not part of SDD-040.
- **Azure decommission work.** Explicitly excluded from Sprint 10.
- **Any constitution edit, schema migration, ledger schema change, new route family, JavaScript, SSE, watcher thread, or third-party dependency.**
- **Any change to non-serve CLI behavior beyond the active-focus parser fix.** Non-serve remains static and finite.

## Risks

- **R-1 (active-focus helper over-selects current sprint).** Probability LOW, Impact MEDIUM. The combination rule intentionally scopes to current PI/Sprint first, but fallback-chain preservation is required when no candidate exists. Mitigation: R1 and R2 tests must cover both helper-hit and helper-none cases.
- **R-2 (meta refresh accidentally lands in static HTML).** Probability LOW, Impact MEDIUM. Static `state.html` is a git/diff artifact and must not auto-refresh. Mitigation: R3 requires serve-only injection; R2/R6 require static-output compatibility.
- **R-3 (cadence validation starts server with invalid input).** Probability LOW, Impact LOW. Mitigation: R5 binds positive integer validation before server start.
- **R-4 (PI-4/PI-5 lock surface drift).** Probability LOW, Impact HIGH. Mitigation: implementation tasks are additive; existing tests and lock guards remain unmodified; T-040-05 runs a regression sweep.
- **R-5 (scope creep into SDD-036/037/038 or carryovers).** Probability MEDIUM, Impact HIGH. Mitigation: out-of-scope list is explicit and F-21 close block records no implementation was done.

## Cross-Feature Notes

- **PI-5 close baseline.** Sprint 10 starts on commit `8417818` (PI-5 close). Test baseline is 337 passing with 2 known platform-conditional skips. Schema lint is clean.
- **SDD-036 readiness.** Sprint 11 builds on the same dashboard surface. SDD-040 must close cleanly before Sprint 11 opens.
- **No silent REQUIRED deferral.** Sprint 10 inherits the Sprint 7/8/9 rule: if a REQUIRED item cannot close, the feature or sprint does not close.
