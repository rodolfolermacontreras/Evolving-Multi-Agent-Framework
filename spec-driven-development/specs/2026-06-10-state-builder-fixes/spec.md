---
id: SDD-20260610STATEBUILDERFIX-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# Feature Spec: SDD-040 -- state_builder.py parser fix + auto-refresh

- Date: 2026-06-10
- Author: Principal Architect (EM-routed Sprint 10 prep)
- Status: SKELETON (pre-CLARIFY) -- finalized at F-21 after CLARIFY closes
- Priority: P1
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), feature slot F-21
- Spec ID: SDD-040
- Parent objective: PI-6 Dashboard Reinvestment + Carryover Cleanup
  ([`sprints/PI-6/CURRENT_PI.md`](../../sprints/PI-6/CURRENT_PI.md))
- Backlog row: [`BACKLOG.md`](../../backlog/BACKLOG.md) / SDD-040 (P1, S effort)

> **SKELETON SCAFFOLD -- 2026-06-10.** This spec dir is staged for the
> Sprint 10 F-21 CLARIFY round. The Problem Statement and Goal below are
> final at scaffold; Acceptance Criteria, Out of Scope additions, Test
> Strategy details, and the Traceability Matrix are TODO blocks that
> reference open CLARIFY questions in [`clarify.md`](./clarify.md). The
> sibling [`validation.md`](./validation.md) is also a SKELETON -- its
> contract is **NOT LOCKED** and must not be implemented against until
> F-21 closes CLARIFY in a fresh Sprint 10 session (Article VII context
> isolation).

---

## Problem Statement

The executive state dashboard (`exec/state.md` and the live
`exec/state.html` served by `cli/state_builder.py`) has two defects that
together undermine its single job: showing the owner what is actually
happening on the project right now.

**Defect 1 -- stale active-focus heuristic.** The `Active focus:` line
in `state.md` is computed by `derive_next_action` in
`cli/state_builder.py` (around line 562), which walks features by stage
in fixed order (IMPLEMENT > REVIEW > PI commitments > backlog) using
only spec-dir frontmatter as input. There is no runtime signal -- no
commit recency, no validation-completeness check, no awareness of which
feature has actually shipped. Owner verbatim 2026-06-10 via EM: "Still
says Active focus: azure-decommission (stale -- that wrapped up)." The
azure-decommission spec dir (`specs/2026-06-08-azure-decommission/`)
shipped at PI-5 close (`8417818`, 2026-06-09); the dashboard still
points to it because the heuristic does not look at what shipped most
recently or what is currently being worked on.

**Defect 2 -- effectively static dashboard page.** Two facets:
(a) The non-serve invocation (`python state_builder.py`) writes static
`state.md` and `state.html` files that only update when the CLI is
re-run by hand. (b) The serve subcommand (`python state_builder.py
serve`) does rebuild on every HTTP GET (line 2362 in
`cli/state_builder.py`), but there is no in-page auto-refresh
mechanism beyond a print-statement claim ("Page auto-refreshes every
20s" at line 2402) that needs verification. Owner verbatim
2026-06-10 via EM: "Static -- refreshes only when you re-run
state_builder.py." Either the existing 20s claim is not wired in the
served HTML, or the cadence is wrong, or the owner expects file-system
change to drive refresh rather than a fixed timer. F-21 CLARIFY Q-B
and Q-C resolve the refresh-mechanism shape.

---

## Goal

After this feature ships, the executive dashboard reflects what is
actually active on the project without manual CLI re-runs:

1. The `Active focus:` line tracks recent shipping reality, not
   frontmatter alone. Source of truth for "what is active" is decided
   in F-21 CLARIFY Q-A (commit-recency, validation-completeness,
   sprint-frontmatter, or a combination) and locked in
   `validation.md` R1.
2. The live dashboard updates without manual re-invocation when files
   under `specs/**`, `sprints/**`, `exec/**`, or `ledger/fleet.db`
   change. Mechanism is decided in F-21 CLARIFY Q-B (handler-side
   rebuild, polling, mtime sweep, or SSE) and cadence in Q-C, all
   constrained by stdlib-only (Article V) per Q-D.
3. The non-serve CLI invocation continues to produce byte-identical
   static `state.md` and `state.html` artifacts for git/diff use
   (Q-E confirms). Auto-refresh is a serve-mode-only behavior.

After this feature ships, the smoke test from
[`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
section 5 passes: the regenerated `state.md` must NOT say "Active focus:
azure-decommission".

---

## Acceptance Criteria

> **TODO -- finalized at F-21 after CLARIFY closes.** Acceptance criteria
> below are placeholders that bind to the five open CLARIFY questions in
> [`clarify.md`](./clarify.md). Each AC will be re-written as a testable
> Given/When/Then assertion once Q-A through Q-E are answered and the
> validation contract is locked.

1. **AC-1 (depends on CLARIFY Q-A).** The `Active focus:` line in
   `state.md` reflects the signal source chosen in Q-A. Concrete
   Given/When/Then to be written at F-21.
2. **AC-2 (depends on CLARIFY Q-B + Q-C).** The serve-mode dashboard
   updates without manual CLI re-invocation when relevant files
   change. Concrete Given/When/Then (including refresh cadence) to be
   written at F-21.
3. **AC-3 (depends on CLARIFY Q-D).** Implementation uses only stdlib
   modules already imported by `cli/state_builder.py` (plus any other
   stdlib modules; no third-party additions). Concrete check (import
   audit) to be written at F-21.
4. **AC-4 (depends on CLARIFY Q-E).** Non-serve invocation produces
   byte-identical static output to the pre-SDD-040 baseline. Concrete
   diff check to be written at F-21.
5. **AC-5 (close verification).** Full test suite passes at PI-5 close
   baseline (>= 337 + new tests; no regression); `schema_lint` exits 0;
   `exec/state.md` regenerates and the smoke test (no "Active focus:
   azure-decommission") passes. Final wording at F-21.

---

## Affected Modules

- Files:
  - `spec-driven-development/cli/state_builder.py` -- **additive only**;
    new active-focus heuristic helper and new auto-refresh handler
    behavior. Lock-surface protections in
    [`plan.md`](./plan.md) "Lock-Surface Protections".
  - `spec-driven-development/cli/test_state_builder.py` -- new tests
    only; existing tests untouched.
- Directories:
  - `spec-driven-development/cli/` (no new modules expected; SDD-040
    fits cleanly in the two files above).
- Out-of-scope files (DO NOT TOUCH per
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  Hard Constraints):
  - `constitution/` (no constitution edit expected; if CLARIFY surfaces
    one, draft an ADR and split into a separate feature).
  - `exec/state.md`, `exec/state.html`, `exec/work-index.md` -- these
    are regenerated artifacts, not source.

## Data Model Changes

None expected. The active-focus heuristic reads existing frontmatter,
existing validation.md REQUIRED state, and (per CLARIFY Q-A) possibly
`git log` output -- no new persistent state. The auto-refresh
mechanism reads file mtimes or polls -- no new persistent state.

If F-21 CLARIFY surfaces a data-model addition (e.g. a cache file),
this section is updated and the change is flagged as an OWNER-ATTENTION
decision before /tasks.

## API Changes

- `cli/state_builder.py serve` may gain new CLI flags for refresh
  cadence (per CLARIFY Q-C). Existing flags `--port` and `--no-open`
  are preserved.
- `cli/state_builder.py` (non-serve) gains no new flags and produces
  byte-identical output (per CLARIFY Q-E).

## Test Strategy

> **TODO -- finalized at F-21 after CLARIFY closes.**

- Unit: tests for the new active-focus heuristic helper covering
  each source signal chosen in Q-A.
- Unit/integration: tests for the auto-refresh handler covering the
  mechanism chosen in Q-B at the cadence chosen in Q-C.
- Regression: full pytest run at PI-5 close baseline (>= 337);
  byte-identical diff of non-serve output (per Q-E).
- Schema lint: `schema_lint` exit 0 after spec dir is fully populated.
- Manual: serve-mode verification per
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  section 5 item 9 -- start serve, edit a `specs/**` file, confirm
  refresh without CLI re-run.

## Validation Contract

The binding validation contract for this feature lives in the sibling
file [`validation.md`](./validation.md). At scaffold (2026-06-10) the
contract is a **SKELETON** with REQUIRED placeholders that lock at
F-21 after CLARIFY closes. **NO IMPLEMENTATION** may begin before the
contract is locked.

## Traceability Matrix

> **TODO -- finalized at F-21 after CLARIFY closes.**

| Requirement | CLARIFY Question | Acceptance Criterion | Validation Row | Task ID |
|-------------|------------------|----------------------|----------------|---------|
| Active-focus signal source | Q-A | AC-1 | R1 (TODO) | T-040-02 |
| Auto-refresh mechanism | Q-B | AC-2 | R3 (TODO) | T-040-03 |
| Refresh cadence | Q-C | AC-2 | R5 (TODO) | T-040-04 |
| Stdlib-only constraint | Q-D | AC-3 | R4 (TODO) | T-040-02..04 |
| Non-serve backwards compat | Q-E | AC-4 | R2, R6 (TODO) | T-040-05 |
| Close verification | -- | AC-5 | R7, R8, R9 (TODO) | T-040-06 |

## Open Questions

All open design questions live in [`clarify.md`](./clarify.md) as
Q-A through Q-E. No other open questions at scaffold (2026-06-10).

> If F-21 CLARIFY surfaces a question not anticipated in Q-A..Q-E,
> the F-21 owner adds it as Q-F (and onward) in `clarify.md` and
> records the addition in the F-21 close report. Do not invent
> answers; do not silently widen scope.

## Out of Scope

- **SDD-036 (lifecycle pipeline + drag-to-reorder w/ safeguards).**
  PI-6 Sprint 11. Per
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  Hard Constraints, MUST NOT be absorbed into Sprint 10.
- **SDD-037 (Dispatches + health pills).** PI-6 Sprint 12. Same
  rule as SDD-036.
- **SDD-038 (aesthetic tokens / polish).** PI-6 Sprint 13
  (contingency). Same rule as SDD-036.
- **Any change to the constitution.** SDD-040 should not require a
  constitution edit. If CLARIFY surfaces one, draft an ADR first,
  route to owner, and split the constitution work into its own
  feature.
- **Any new third-party dependency.** Article V is binding;
  `watchdog`, `flask`, `fastapi`, `requests` are all excluded by
  CLARIFY Q-D.
- **Any change to the non-serve CLI behavior beyond the parser fix.**
  Per CLARIFY Q-E, `python state_builder.py` (without `serve`)
  continues to produce byte-identical static output for git/diff use.
- **Any modification to the PI-4/PI-5 render path lock surface.**
  The existing `render_markdown` (line 528) and `derive_next_action`
  (line 562) bodies in `cli/state_builder.py` are protected; SDD-040
  ships additive helpers, not edits to those functions. See
  [`plan.md`](./plan.md) "Lock-Surface Protections" for the full
  DO-NOT-MODIFY list.

## Risks

- **R-1 (file-watch on Windows).** Probability MEDIUM, Impact LOW.
  Python stdlib has no inotify equivalent on Windows; any file-watch
  mechanism must be polling-based (`os.stat` over a configurable
  interval). Mitigation: CLARIFY Q-B explicitly constrains the
  mechanism to stdlib-only (Q-D); the F-21 owner picks among polling,
  handler-side rebuild, or SSE -- all of which work on Windows.
- **R-2 (PI-4/PI-5 lock surface).** Probability LOW, Impact HIGH.
  The existing render path is the lock surface for SDD-FDC-001
  (filesystem data contracts) and Article XII (UI lifecycle variant).
  Mitigation: `plan.md` "Lock-Surface Protections" enumerates the
  DO-NOT-MODIFY functions; T-040-05 (regression) and T-040-06
  (close verification) both gate on byte-identical non-serve output
  (per AC-4 / R2 / R6).
- **R-3 (cadence vs CPU cost).** Probability LOW, Impact LOW. A
  poll cadence that is too aggressive burns laptop CPU; one that is
  too lazy looks broken. Mitigation: CLARIFY Q-C decides the default
  and exposes a CLI flag for override; R5 in `validation.md` will
  bind both.

## Cross-Feature Notes

- **PI-5 close baseline.** Sprint 10 starts on commit `8417818` (PI-5
  close). Test baseline is 337 passing (with 2 known platform-conditional
  skips). Schema lint clean. SDD-040 ships on top of this baseline;
  no regression permitted.
- **SDD-036 readiness.** Sprint 11 (SDD-036) builds on the same
  dashboard surface. SDD-040 must close cleanly before Sprint 11
  opens, so that SDD-036 inherits a working active-focus signal and
  a working auto-refresh path.
- **No silent REQUIRED deferral.** Sprint 10 inherits the Sprint 7/8/9
  rule per
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  Hard Constraints item 1: if a REQUIRED item cannot close, the
  feature or sprint does not close.
