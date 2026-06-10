---
id: SDD-20260610STATEBUILDERFIX-plan
type: plan
status: active
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Implementation Plan: SDD-040 -- state_builder.py parser fix + auto-refresh

- Spec Reference: [`spec.md`](./spec.md) (SDD-040)
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slot F-21
- Author: Principal Architect (EM-routed Sprint 10 prep)
- Date: 2026-06-10

---

> **SKELETON PLAN -- 2026-06-10.** The approach and file scope below
> are final at scaffold. The Risk Assessment table and any detailed
> design choices (active-focus signal source, auto-refresh mechanism,
> cadence) are TODO blocks that reference open CLARIFY questions in
> [`clarify.md`](./clarify.md). The full plan is finalized at F-21
> after CLARIFY closes.

---

## Approach Summary

SDD-040 ships two defect fixes inside one feature against
`cli/state_builder.py`:

- **Parser fix (Defect 1).** Replace the stale active-focus
  heuristic in `derive_next_action` (line 562) with a heuristic that
  consumes a runtime signal (commit recency, validation-completeness,
  sprint-frontmatter, or a combination per CLARIFY Q-A). The fix is
  **additive**: a new helper function is introduced; the existing
  `derive_next_action` body is preserved as the final fallback path
  and is not modified in place beyond replacing its first-pick line
  with a call to the new helper.
- **Auto-refresh (Defect 2).** Extend the serve subcommand
  (`cli/state_builder.py serve`, line ~2385) with an auto-refresh
  mechanism per CLARIFY Q-B at the cadence chosen in Q-C, constrained
  to stdlib-only per Q-D. The existing `DashboardHandler.do_GET`
  (line 2358) is preserved and continues to rebuild on every request;
  the new behavior layers on top (either client-side polling via
  HTML meta-refresh or `<script>`, server-side mtime sweep on a
  background thread, or SSE -- F-21 picks).

The two defects touch different code paths inside the same file and
can be implemented in parallel within a single session. Fleet
dispatch is **not** justified for this feature (small scope, single
file, two tasks that serialize at the import level even if logically
independent). The F-22 IMPLEMENT session runs sequentially:
T-040-02 (parser fix) -> T-040-03 (auto-refresh) -> T-040-04
(cadence flag) -> T-040-05 (regression) -> T-040-06 (close).

---

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 0 | CLARIFY (F-21) | None | [`clarify.md`](./clarify.md) Q-A through Q-E answered; [`spec.md`](./spec.md), [`validation.md`](./validation.md), [`tasks.md`](./tasks.md) finalized; validation contract LOCKED |
| 1 | Parser fix (active-focus heuristic) | Phase 0 (Q-A locked) | `cli/state_builder.py` additive helper + `cli/test_state_builder.py` new tests |
| 2 | Auto-refresh handler | Phase 0 (Q-B, Q-C locked); serial with Phase 1 in same session | `cli/state_builder.py` additive handler + `cli/test_state_builder.py` new tests |
| 3 | Cadence flag | Phase 2 complete | argparse flag on `serve` + test |
| 4 | Regression sweep | Phases 1-3 | Byte-identical static-output check + existing-tests-green check |
| 5 | Sprint 10 close | Phases 1-4 | Full pytest, schema_lint, state regen, smoke test, owner pre-push approval |

---

## File Scope (constrained, additive only)

| File | Change Type | R-Items | Owner |
|------|-------------|---------|-------|
| `cli/state_builder.py` | **Additive only**: new active-focus heuristic helper (Phase 1) + new auto-refresh handler logic in serve mode (Phase 2) + new argparse flag for cadence (Phase 3). Existing `render_markdown` (line 528), `derive_next_action` (line 562 -- body preserved; first-pick line replaced with a call to the new helper), `DashboardHandler.do_GET` (line 2358 -- body preserved; additive layering only), and `serve` (line 2385 -- body preserved; new flag plumbed through) all stay byte-stable in body. | R1, R3, R4, R5 | T-040-02, T-040-03, T-040-04 |
| `cli/test_state_builder.py` | **New tests only**: new test classes for active-focus heuristic, auto-refresh handler, and cadence flag. Existing test classes and test names untouched. | R1, R3, R5, R6, R7 | T-040-02, T-040-03, T-040-04, T-040-05 |

### Files NOT in scope

- `cli/state_builder.py` outside the four enumerated additive sites.
- All other files under `cli/` (`fleet.py`, `dedup.py`, `qa.py`,
  `retro.py`, `schema_lint.py`, etc.).
- `constitution/` (no constitution edit expected).
- `backlog/BACKLOG.md`, `sprints/PI-6/CURRENT_PI.md`,
  `exec/sprint-progress.md` -- updates happen at Sprint 10 close
  (F-23), not in F-22 implementation.
- `exec/state.md`, `exec/state.html`, `exec/work-index.md` --
  regenerated artifacts, not source.

---

## Lock-Surface Protections (DO NOT MODIFY)

The following surfaces in `cli/state_builder.py` are **LOCKED** by
PI-4 / PI-5 work and **MUST NOT** be modified in their existing
bodies by any T-040-NN task. Verification is by `git diff` against
the PI-5 close commit (`8417818`) at T-040-05 (regression sweep) and
T-040-06 (close verification).

### Render path (PI-4 / SDD-FDC-001 lock surface)

- **`render_markdown(...)` -- line 528.** The canonical 7-section
  output format is locked by SDD-002 (the original state_builder
  feature). SDD-040 does not modify this function's body. The new
  active-focus signal source feeds the existing `next_action[0]`
  call site at line 621 unchanged.
- **`derive_next_action(sdd_root, pi, features)` -- line 562.**
  Existing body (IMPLEMENT > REVIEW > PI commitments > backlog
  fallback chain) is preserved. The new active-focus helper from
  R1 is layered as a **prepended** check at the top of the function
  body; if the new helper returns a non-None result, that result is
  returned. If it returns None (no recent commit signal, no
  validation gap, no sprint match -- per Q-A), the existing fallback
  chain runs unchanged. This guarantees AC-4 (byte-identical
  non-serve output for cases where the new helper has nothing to
  contribute).

### Serve / HTTP handler (PI-3 / state-dashboard lock surface)

- **`DashboardHandler` class -- line 2330.** Class identity, class
  variables (`server_port`, `sdd_root`), `_send` body, and security
  headers (REC-2 from SECURITY-REVIEW.md) are all preserved.
- **`DashboardHandler.do_GET` -- line 2358.** Existing body
  (rebuilds state on every GET via `build(... write=False,
  live_html=True ...)`) is preserved. Any auto-refresh hook the
  chosen Q-B mechanism needs is **additive** -- e.g. a new
  `_send_with_refresh_meta` helper, or a new background thread
  started in `serve()`, or a new `text/event-stream` branch added
  alongside the existing routes (`/`, `/healthz`, `/favicon.ico`,
  404).
- **`serve(sdd_root, host, port, open_browser)` -- line 2385.**
  Existing body (port-availability sweep, ThreadingHTTPServer
  bring-up, browser open, KeyboardInterrupt handling) is preserved.
  The new cadence flag (R5) is plumbed through the existing argparse
  surface at `sub_serve.add_argument(...)` near line 2784; no
  rename, no default change for `--port` or `--no-open`.

### Test surface (PI-3 / PI-4 lock)

- **All existing test classes and test names** in
  `cli/test_state_builder.py` are preserved. New tests are added
  as **new** test classes (e.g. `TestActiveFocusHeuristic`,
  `TestAutoRefreshHandler`, `TestRefreshCadenceFlag`).
- **No existing test fixtures** are renamed or have their behavior
  changed.

### Article XII (UI Lifecycle Variant) compatibility

- SDD-040 does **NOT** carry the `ui-variant: true` frontmatter
  marker. Article XII relaxation does not apply. Article X
  (Validation Is a Pre-Implementation Contract) is fully binding:
  validation contract locks at F-21, no post-lock loosening.
- The serve-mode dashboard surface is the same surface SDD-018
  retroactively validated. SDD-040 changes runtime behavior (when
  the page rebuilds) but does not change the visible 7-section
  contract from SDD-002 or the FDC-001 frontmatter contract.

---

## Parallel-Safe Tasks

SDD-040 tasks **all serialize on `cli/state_builder.py`** -- they
are not parallel-safe across the file boundary. Within the same
file, the parser-fix logic (T-040-02) and the auto-refresh logic
(T-040-03) touch different functions and can be implemented in
either order, but fleet dispatch is not justified (single file,
small diff, single session is the right shape per Article VII).

- T-040-02 (parser fix in `derive_next_action` + new helper)
- T-040-03 (auto-refresh in `DashboardHandler` / `serve` + new
  handler logic)
- T-040-04 (cadence flag in argparse near line 2784)
- T-040-05 (regression sweep)
- T-040-06 (close verification)

All listed sequentially in [`tasks.md`](./tasks.md).

## Sequential Tasks

(See [`tasks.md`](./tasks.md) for full breakdown.) Order:

1. T-040-01 (read existing state, document baseline heuristic)
2. T-040-02 (parser fix)
3. T-040-03 (auto-refresh)
4. T-040-04 (cadence flag)
5. T-040-05 (regression sweep)
6. T-040-06 (close)

---

## Risk Assessment

> **TODO -- finalized at F-21 after CLARIFY closes.** Initial risks
> identified at scaffold; mitigation strength depends on the Q-A,
> Q-B, Q-C answers.

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-1: File-watch on Windows (no stdlib inotify) | MEDIUM | LOW | Constrain Q-B to polling, mtime sweep, handler-side rebuild, or SSE (all stdlib-compatible on Windows). Article V binding. |
| R-2: PI-4/PI-5 lock surface drift | LOW | HIGH | Enumerate DO-NOT-MODIFY surfaces above; verify by `git diff` at T-040-05 and T-040-06. |
| R-3: Refresh cadence too aggressive (CPU cost) | LOW | LOW | Q-C decides default; R5 binds a CLI flag for override. |
| R-4: New helper returns None for all PI-6 work and dashboard regresses to existing fallback chain | LOW | MEDIUM | Smoke test (M1) gates close: regenerated state.md must NOT say "Active focus: azure-decommission". T-040-06 enforces. |
| R-5: CLARIFY surfaces a constitutional question (e.g. on the stdlib boundary) | LOW | HIGH | Per `SPRINT-10-KICKOFF.prompt.md` Hard Constraints item 4: draft an ADR, route to owner, split constitution work into a separate feature. SDD-040 does not absorb a constitution edit. |

---

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 0 (CLARIFY) | S | 5 questions, owner-routed via EM; lock at F-21 close. |
| 1 (parser fix) | S | One additive helper + 2-4 unit tests. |
| 2 (auto-refresh) | M | One mechanism per Q-B; complexity depends on whether SSE is chosen vs polling/mtime. |
| 3 (cadence flag) | S | One argparse arg + 1 unit test. |
| 4 (regression) | S | Diff harness + run existing tests. |
| 5 (close) | S | Standard close pattern (pytest + schema_lint + state regen + validation audit + smoke test + owner approval). |

Total backlog estimate was **S** (small). Plan confirms S is
achievable provided Q-B does not pick SSE; if SSE is chosen, total
moves to **M**.

---

## Validation Criteria

(See [`validation.md`](./validation.md) for the full SKELETON.
Each AC in [`spec.md`](./spec.md) maps to one or more REQUIRED
rows there.)

- [ ] AC-1 -> R1 (active-focus signal source)
- [ ] AC-2 -> R3, R5 (auto-refresh mechanism + cadence)
- [ ] AC-3 -> R4 (stdlib-only constraint)
- [ ] AC-4 -> R2, R6 (backwards compat + existing tests)
- [ ] AC-5 -> R7, R8, R9 (new tests, test count, schema lint)
- [ ] Smoke test M1 + serve verification M2 + owner approval M3

All bind to concrete tests / commits / SHAs at F-21 lock.
