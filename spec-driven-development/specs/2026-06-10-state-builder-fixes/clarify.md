---
id: SDD-20260610STATEBUILDERFIX-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# CLARIFY: SDD-040 -- state_builder.py parser fix + auto-refresh

- Date: 2026-06-10
- Authors: Principal Product Manager + Principal Architect (jointly, at F-21)
- Status: **DONE** -- Q-A through Q-E answered; validation contract locked in [`validation.md`](./validation.md)
- Spec ID: SDD-040
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), F-21 (CLARIFY+SPEC+PLAN+TASKS fused per [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md) section 2)
- Decision source: EM-synthesized owner-approved Sprint 10 kickoff decision, 2026-06-10.

---

## Ground Rules

- This file is the source of truth for SDD-040 design decisions.
- All answers are attributed to the EM-synthesized owner-approved Sprint 10 kickoff decision dated 2026-06-10.
- Article V (stdlib-only CLI) and Article VII (context isolation) remain binding.
- No implementation is authorized by this file alone; implementation starts only after the locked validation contract in [`validation.md`](./validation.md) is honored by F-22.

---

## Scope

### Q-A: Active-focus signal source

**Context.** The current `derive_next_action` heuristic in `cli/state_builder.py` picks the active focus by walking features by stage in fixed order: IMPLEMENT > REVIEW > PI commitments > backlog fallback. Source of truth is frontmatter only -- no runtime signal. Owner verbatim 2026-06-10 via EM proves this fails empirically: "Still says Active focus: azure-decommission (stale -- that wrapped up)." azure-decommission shipped at PI-5 close (`8417818`, 2026-06-09); the dashboard still picks it because the heuristic does not know what shipped most recently.

**PM recommendation:** Use a combination rule. Scope the candidate set first to the current PI/Sprint allocation, which for Sprint 10 is SDD-040 per [`CURRENT_PI.md`](../../sprints/PI-6/CURRENT_PI.md) and [`BACKLOG.md`](../../backlog/BACKLOG.md). Within that guarded scope, prefer features with unchecked REQUIRED validation items. If more than one candidate remains, tie-break by bounded git-log recency. If the runtime helper produces no candidate, fall back to the current sprint anchor and then the existing fallback chain.

**Architect recommendation:** Same. The scope guard prevents unrelated stale specs, including Azure decommission work, from outranking the current Sprint 10 feature. Bounded git-log recency is acceptable under Article V when invoked through stdlib `subprocess.run`; no Python git library is allowed.

**Joint recommendation:** **Combination rule**:

1. Scope guard: current PI/Sprint allocation from PI-6 CURRENT_PI and BACKLOG; for Sprint 10 this means SDD-040.
2. Prefer scoped candidates with unchecked REQUIRED validation items.
3. Tie-break by bounded `git log` recency via stdlib `subprocess.run`.
4. Fall back to the current sprint anchor.
5. If no candidate is found, run the existing fallback chain unchanged.

**Status:** ANSWERED.
**Answer:** Owner-approved via EM synthesis, 2026-06-10: choose the combination rule above. The active-focus helper may intentionally change the `Active focus:` line when it contributes a candidate; when it returns no candidate, the existing fallback chain must preserve the controlled-output baseline.

---

### Q-B: Auto-refresh mechanism

**Context.** Article V rules out `watchdog`, `flask`, `fastapi`, and other third-party web/file-watch dependencies. The existing serve subcommand already rebuilds state on every HTTP GET through `DashboardHandler.do_GET` and `build(... write=False, live_html=True ...)`. The defect is that served HTML does not refresh itself in the browser.

**PM recommendation:** Use handler-side meta refresh plus the existing rebuild-on-request behavior. Keep the browser behavior predictable and avoid adding JavaScript, SSE, or a watcher thread.

**Architect recommendation:** Same. `<meta http-equiv="refresh" content="N">` in served HTML is the lowest-risk implementation: stdlib-only, compatible with the existing handler, and scoped to serve mode. It does not require CSP relaxation, a background thread, or any new route.

**Joint recommendation:** **Handler-side meta refresh plus existing rebuild-on-request.** No JavaScript, no SSE, no watcher/background thread. Serve mode already rebuilds on GET; SDD-040 makes that cadence explicit, tested, configurable, and applies refresh only to served HTML.

**Status:** ANSWERED.
**Answer:** Owner-approved via EM synthesis, 2026-06-10: implement handler-side meta refresh in served HTML only. Existing rebuild-on-GET remains the server-side freshness mechanism.

---

### Q-C: Refresh cadence

**Context.** Cadence balances dashboard freshness against laptop CPU cost. With handler-side meta refresh, the browser drives periodic GETs; each GET triggers the existing rebuild path.

**PM recommendation:** Default to 5 seconds, exposed through a serve-only CLI flag named `--refresh-seconds`.

**Architect recommendation:** Same. Require positive integer validation; reject zero and negative values before the server starts. Do not apply the flag to non-serve invocation.

**Joint recommendation:** **Default 5 seconds**, with serve-only CLI flag `--refresh-seconds` and positive integer validation.

**Status:** ANSWERED.
**Answer:** Owner-approved via EM synthesis, 2026-06-10: default refresh cadence is 5 seconds; `serve --refresh-seconds N` overrides it when `N` is a positive integer.

---

### Q-D: Stdlib-only constraint (Article V) confirmation

**Context.** Article V (Stdlib-Only CLI Pattern, see [`docs/CLI-PATTERN.md`](../../docs/CLI-PATTERN.md)) binds all `cli/*.py` modules. SDD-040 must re-affirm the constraint explicitly.

Concrete confirmation:

- Implementation MUST use only stdlib modules.
- New stdlib modules are permitted when justified by the locked design; for SDD-040 that includes `subprocess` for bounded git-log recency.
- Implementation MUST NOT add `watchdog`, `flask`, `fastapi`, `requests`, `pygit2`, or any other PyPI dependency.
- If commit recency is used, the implementation reads `git log` via `subprocess.run`, not through a Python git library.

**PM recommendation:** **CONFIRM Article V binding.** No exceptions for SDD-040.

**Architect recommendation:** **CONFIRM Article V binding.** `subprocess` is a stdlib boundary and is acceptable for bounded `git log` inspection.

**Joint recommendation:** **CONFIRM Article V binding.** No new third-party dependency. Implementation uses only stdlib modules.

**Status:** ANSWERED.
**Answer:** Owner-approved via EM synthesis, 2026-06-10: Article V is confirmed. `subprocess` is acceptable for bounded git recency; the named third-party dependencies are prohibited.

---

### Q-E: Backwards compatibility for non-serve invocation

**Context.** `python state_builder.py` (without `serve`) writes static `state.md`, `state.html`, and `work-index.md` to `exec/` for git/diff use. Sprint 10's parser fix must not regress this path.

Concrete confirmation:

- Non-serve invocation MUST continue writing static `state.md`, `state.html`, and `work-index.md`.
- Auto-refresh behavior MUST be serve-mode-only. Non-serve invocation MUST NOT gain a background thread, watcher, browser loop, or any new long-running side effect.
- Byte-identical comparison applies to controlled inputs where the new active-focus helper returns no candidate.
- Active-focus output MAY intentionally differ when the new helper does contribute a candidate; that difference is the parser fix, not a regression.

**PM recommendation:** **CONFIRM backwards compatibility.**

**Architect recommendation:** **CONFIRM** with the controlled-input clarification above.

**Joint recommendation:** **CONFIRM backwards compatibility.** R2 and R6 in [`validation.md`](./validation.md) bind the controlled-baseline test.

**Status:** ANSWERED.
**Answer:** Owner-approved via EM synthesis, 2026-06-10: non-serve static generation remains unchanged except for intentional `Active focus:` differences when the new helper contributes. Auto-refresh is serve-only.

---

## OWNER-ATTENTION Items (F-21 close)

- **None.** The owner-approved Sprint 10 kickoff decision resolved Q-A through Q-E. No Level-2 approval, dependency approval, CSP relaxation, schema migration, constitution edit, or production-branch decision is surfaced by F-21.

## ADR Decision

- **No ADR.** The active-focus heuristic and handler-side meta-refresh are implementation choices inside an existing stdlib CLI/HTTP-handler surface. They do not introduce a new dependency, schema migration, constitutional rule, security-policy change, or irreversible external integration.

## F-21 Close Checklist

1. Q-A through Q-E answered with EM-synthesized owner-approved decisions.
2. This file frontmatter set to `status: done` and `updated: 2026-06-10`.
3. [`spec.md`](./spec.md) Acceptance Criteria, Test Strategy, Traceability Matrix, Open Questions, and Out-of-Scope finalized.
4. [`validation.md`](./validation.md) R1-R9 finalized and contract locked with timestamp/date; checkboxes remain unchecked for F-22.
5. [`plan.md`](./plan.md) Risk Assessment and file scope finalized for the no-JS/no-watcher path.
6. [`tasks.md`](./tasks.md) T-040-01..T-040-06 finalized; implementation tasks remain pending.
7. ADR decision recorded as no.
8. No implementation, commit, or push performed in F-21.
