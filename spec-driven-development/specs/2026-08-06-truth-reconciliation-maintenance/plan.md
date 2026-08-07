---
id: MAINT-2026-08-06-TRUTH-RECONCILIATION-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-08-06
feature: 2026-08-06-truth-reconciliation-maintenance
---

# PLAN: Truth Reconciliation Maintenance

- Maintenance: `MAINT-2026-08-06-TRUTH-RECONCILIATION`
- Spec: [`spec.md`](./spec.md) -- APPROVED
- Validation: [`validation.md`](./validation.md) -- original locked baseline 18 REQUIRED; append-only expanded total 29 REQUIRED
- PI / sprint: none

**Validation count audit -- 2026-08-06:** The 18-item figure is the original
planned baseline. Architect deltas appended V-19 through V-29 without replacing
or weakening that baseline, producing the truthful current total of 29 required
items. The plan's historical intent and requirements are unchanged.

---

## Approach

1. Preserve the authorized backlog and SDD-035 source corrections and capture
   baseline tests plus Article X hashes.
2. Add focused RED regressions for terminal feature evidence, terminal backlog
   exclusion, zero-active state, active-PI compatibility, and leadership lint.
3. Implement one stdlib-only status normalizer and terminal predicate in
   `state_builder_data.py`; make feature discovery and both renderers consume it.
4. Refresh only the four current hand-authored surfaces and required historical
   metadata. Preserve frozen evidence and unchecked SDD-035 items.
5. Run focused tests, schema/structural/lint checks, and the Article X lock.
   Close maintenance lifecycle metadata only when evidence supports review.
6. Run `state_builder.py` once to rebuild all three generated executive files,
   then execute generated-truth, full-doctor, diff, scope, and editor checks.

No ADR, schema enum, dependency, constitution edit, Azure action, PI, sprint,
SDD assignment, setup-repair change, commit, push, merge, or evidence deletion is
authorized.

## Data Contract

- Normalize lifecycle text case-insensitively across separators and explicit
  status/disposition fields.
- Terminal classes are completed (`done`, `shipped`) and non-operational
  (`archived`, `superseded`, `historical`, `retired`, `abandoned`).
- Explicit terminal evidence in supported feature artifacts wins over inferred
  progress. Conflicting terminal evidence remains conservatively terminal.
- Terminal backlog rows never enter Sprint Plan or QUEUED.
- With no active roadmap PI and no active `CURRENT_PI.md`, active PI, sprint,
  focus, and IN-FLIGHT are empty. Existing active-PI and override behavior stays
  unchanged.

## File Ownership and Sequence

| Phase | Direct files | Dependency |
|-------|--------------|------------|
| Baseline / RED | `cli/test_state_builder.py`, `cli/test_staledoc_lint.py` | none |
| Shared semantics | `cli/state_builder_data.py` | RED tests |
| Renderer consumption | `cli/state_builder_markdown.py`, `cli/state_builder_html.py` | shared semantics |
| Narrow lint | `cli/staledoc_lint.py` | lint RED tests |
| Current docs | tracker, session memory, onboarding, leadership brief | source truth stable |
| Historical metadata | only spec-required existing rows/artifacts | source truth stable |
| Validation / closure | maintenance `spec.md`, `clarification.md`, `validation.md` | all source checks green |
| Generated rebuild | `exec/state.md`, `exec/state.html`, `exec/work-index.md` | closure and checks green |

Renderer and lint work are logically parallel after the shared contract, but this
invocation integrates serially to preserve immediate focused validation after
each edit. Generated files are command-owned and never hand-edited.

## Validation Order

1. Baseline: 1118 passed, 5 skipped; capture Article X hashes and initial scope.
2. RED: focused new state-builder tests and focused new stale-doc tests fail for
   the intended missing behavior.
3. GREEN: run the same focused selector immediately after each production edit.
4. Run complete state-builder and stale-doc test files, focused maintenance
   schema lint, repository schema/origin/governance/stale-doc checks, and the
   exact Article X lock selector.
5. Close maintenance source metadata and run the sole state-builder rebuild.
6. Assert generated zero-active truth and deterministic no-write parity.
7. Run full doctor through `.venv`, full tests if doctor does not include them,
   `git diff --check`, scope/status/stat/name checks, and editor diagnostics.

## Risks

| Risk | Mitigation |
|------|------------|
| Terminal prose is over-scanned | inspect only supported frontmatter and explicit lifecycle fields |
| Active PI regresses | retain dedicated active roadmap + `CURRENT_PI.md` control |
| Renderer filters diverge | import one data-layer predicate; structural test forbids local lists |
| Historical evidence changes | compare SDD-035 checkbox state and file inventory before/after |
| Generated output changes early | defer the only builder write until all source gates pass |
| Scope expands materially | stop and return to Architect rather than changing the contract |
