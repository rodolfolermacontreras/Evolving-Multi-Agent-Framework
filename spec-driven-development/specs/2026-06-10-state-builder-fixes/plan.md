---
id: SDD-20260610STATEBUILDERFIX-plan
type: plan
status: done
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Implementation Plan: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slot F-21
- Author: Principal Architect (EM-routed Sprint 10 F-21)
- Date: 2026-06-10
- Status: **APPROVED** -- implementation remains F-22

---

## Approach Summary

SDD-040 ships two defect fixes inside one feature against `cli/state_builder.py`:

- **Parser fix (Defect 1).** Add a small active-focus helper that applies the locked combination rule from [`clarify.md`](./clarify.md) Q-A: current PI/Sprint allocation first, unchecked REQUIRED validation items second, bounded git-log recency third, current sprint anchor fourth, and existing fallback chain last. The existing `derive_next_action` fallback chain is preserved for helper-none cases.
- **Serve-mode auto-refresh (Defect 2).** Add handler-side meta refresh to served HTML only. The existing HTTP handler continues to rebuild on every GET; the browser refresh drives those GETs at the configured cadence. No JavaScript, SSE, watcher/background thread, or third-party web/file dependency is introduced.
- **Cadence control.** Add a serve-only `--refresh-seconds` flag with default `5` and positive integer validation. Non-serve invocation does not accept or use the flag.

The two defects touch different concerns inside the same file and should be implemented sequentially in F-22. Fleet dispatch is not justified: this is a small, single-file CLI/handler change with a tight regression surface.

---

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 0 | CLARIFY/SPEC/PLAN/TASKS finalization (F-21) | Owner-approved Sprint 10 kickoff decisions | [`clarify.md`](./clarify.md) done; [`spec.md`](./spec.md) approved; [`validation.md`](./validation.md) locked; [`tasks.md`](./tasks.md) ready |
| 1 | Baseline read and test-first setup | Phase 0 | Document baseline behavior in [`tasks.md`](./tasks.md); add failing tests for R1/R3/R5/R2 before code |
| 2 | Parser fix | Phase 1 | Add helper + prepend call in `derive_next_action`; tests for scope guard, unchecked validation, git recency tie-break, fallback preservation |
| 3 | Serve-mode meta refresh | Phase 2 | Add served-only meta refresh injection and tests proving static HTML remains unchanged |
| 4 | Cadence flag | Phase 3 | Add `serve --refresh-seconds`; default 5; reject zero/negative/non-integer inputs before server start |
| 5 | Regression and close verification | Phases 2-4 | Existing tests green; full pytest; schema lint; state regen; smoke test; serve-mode manual check; owner pre-push approval request |

---

## File Scope (Constrained, Additive Only)

| File | Change Type | R-Items | Owner |
|------|-------------|---------|-------|
| `cli/state_builder.py` | Additive helper for active-focus combination rule; serve-only meta refresh injection; serve-only cadence flag. Existing fallback chain, static render contract, security headers, and count/build-index behavior preserved. | R1, R2, R3, R4, R5, R6 | T-040-02, T-040-03, T-040-04, T-040-05 |
| `cli/test_state_builder.py` | New tests only. Existing test classes and test names remain untouched. | R1, R2, R3, R5, R6, R7 | T-040-02, T-040-03, T-040-04, T-040-05 |

### Files Not In Scope

- All other files under `cli/` (`fleet.py`, `dedup.py`, `qa.py`, `retro.py`, `schema_lint.py`, etc.).
- `constitution/`.
- `backlog/BACKLOG.md`, `sprints/PI-6/CURRENT_PI.md`, and `exec/sprint-progress.md` during F-22 implementation. Sprint-close updates happen in F-23.
- `exec/state.md`, `exec/state.html`, `exec/work-index.md` except as regenerated artifacts during F-22/F-23 verification.
- SDD-036/037/038/034/039 and Azure decommission artifacts.

---

## Lock-Surface Protections (Do Not Modify In Place)

The following surfaces in `cli/state_builder.py` are protected by prior dashboard and filesystem-data-contract work. F-22 should add helpers and small call-site plumbing; it should not rewrite these surfaces.

### Render Path

- **`render_markdown(...)`.** The canonical 7-section markdown output remains unchanged except for data supplied through the existing `next_action` parameter.
- **`derive_next_action(sdd_root, pi, features)`.** Existing fallback order remains intact. The new helper is a prepended check: if it returns a candidate, return it; if it returns `None`, run the existing chain.

### Serve / HTTP Handler

- **`DashboardHandler._send`.** Security headers are preserved. No CSP relaxation is needed because the chosen mechanism uses meta refresh, not JavaScript.
- **`DashboardHandler.do_GET`.** Existing rebuild-on-GET behavior remains the server-side freshness path. Meta refresh is layered into the returned HTML only for root page responses.
- **`serve(...)`.** Existing host/port/no-open behavior is preserved. The new cadence argument is plumbed through without changing `--host`, `--port`, or `--no-open` defaults.

### Test Surface

- Existing test classes and test names in `cli/test_state_builder.py` are preserved. New coverage lands in new classes such as `TestActiveFocusHeuristic`, `TestServeModeRefresh`, and `TestRefreshCadenceFlag`.

### Article XII Compatibility

- SDD-040 does not carry the `ui-variant: true` marker.
- Article X is fully binding: validation contract locks at F-21, and no REQUIRED item may be loosened or silently deferred after lock.

---

## Parallel-Safe Tasks

None. All F-22 implementation tasks serialize on `cli/state_builder.py` and the same test module. Parallel dispatch would add coordination cost without reducing risk.

## Sequential Tasks

1. T-040-01 -- baseline read and task baseline documentation.
2. T-040-02 -- parser fix tests and implementation.
3. T-040-03 -- serve-mode meta refresh tests and implementation.
4. T-040-04 -- cadence flag tests and implementation.
5. T-040-05 -- regression sweep.
6. T-040-06 -- close verification and owner-gate evidence.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-1: Active-focus helper selects wrong feature because scope guard parsing is too broad | Medium | Medium | Parse current PI/Sprint allocation from PI-6 CURRENT_PI and BACKLOG; tests must prove SDD-040 outranks stale azure-decommission-style frontmatter and that fallback chain still runs when helper returns no candidate. |
| R-2: Bounded `git log` recency becomes flaky on fresh clones or shallow history | Medium | Low | Git recency is tie-break only, not primary source. If subprocess fails or returns no match, helper falls back to current sprint anchor and then existing chain. Tests mock `subprocess.run`. |
| R-3: Meta refresh accidentally appears in static `state.html` | Low | Medium | Inject only in served HTML path. R3 tests served HTML has meta refresh; R2/R6 tests static output does not. |
| R-4: Invalid cadence values start the server | Low | Low | Positive integer validation is part of argument parsing or a pre-serve validation branch. Tests cover zero, negative, and non-integer rejection. |
| R-5: CSP/security tests fail because implementation uses JavaScript | Low | High | Q-B prohibits JavaScript. Existing `TestSecurityAudit.test_no_script_tags` must pass unchanged. |
| R-6: Scope creep into SDD-036/037/038 or carryover work | Medium | High | File scope excludes those paths. F-22 must stop as OWNER-ATTENTION if asked to absorb lifecycle pipeline, dispatch cards, aesthetic tokens, dedup upgrade, Article VII wording, or Azure decommission work. |
| R-7: Non-serve output comparison is over-applied to intentional active-focus changes | Medium | Low | R2 explicitly applies byte-identical comparison only to controlled fixtures where helper returns no candidate. Real repo active-focus may intentionally differ. |

---

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 0 (F-21 finalization) | S | Completed by this artifact set. |
| 1 (baseline + tests) | S | Documentation plus test-first setup. |
| 2 (parser fix) | S | One helper, one call-site prepend, mocked git recency tests. |
| 3 (meta refresh) | S | Meta tag injection is simpler than watcher/SSE/polling thread. |
| 4 (cadence flag) | S | One argparse arg or equivalent validation branch. |
| 5 (regression/close) | S | Standard Sprint 10 validation commands and manual check. |

Total remains **S**. The no-JS/no-watcher decision avoids the complexity that would have moved the feature to M.

---

## Validation Criteria

See [`validation.md`](./validation.md), locked at F-21. Summary:

- [ ] AC-1 -> R1, R7 (active-focus combination rule)
- [ ] AC-2 -> R3, R7 (serve-only meta refresh)
- [ ] AC-3 -> R5, R7 (positive cadence flag)
- [ ] AC-4 -> R4 (stdlib-only)
- [ ] AC-5 -> R2, R6 (non-serve compatibility)
- [ ] AC-6 -> R8, R9, M1, M2, M3 (full close evidence)

All checkboxes intentionally remain unchecked until F-22 supplies evidence.
