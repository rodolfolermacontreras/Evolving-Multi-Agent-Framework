---
id: SDD-20260710SPRINT23POLISH-plan
type: plan
status: active
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-sprint-23-dashboard-polish
---

# PLAN: F-63 Sprint 23 dashboard polish

- IDs: SDD-038, SDD-056, SDD-057
- Spec: [`spec.md`](./spec.md)
- Validation: [`validation.md`](./validation.md) -- LOCKED
- Implementation owner: Principal Software Developer

---

## Approach Summary

Reuse the established additive SDD-037/040/042 pattern:

1. Add a pure active-sprint loader to `state_builder_data.py`; re-export it from
   the facade and choose its result in `build()` before the unchanged legacy
   loader fallback. Always pass the selected list to unchanged
   `detect_current_sprint`.
2. Add a PI-nav HTML post-processor to `state_builder_html.py`; re-export it and
   call it after `render_html` from `build()` using already-loaded `pis` and the
   resolved active PI.
3. Add a lifecycle-token HTML post-processor to `state_builder_html.py`; re-export
   it and call it immediately after `inject_lifecycle_html`. It adds state classes
   and the locked CSS tokens without changing either renderer.
4. Repair only two historical sentences in their two prompt files.
5. Regenerate executive surfaces once, then run full lock/gate/CI validation.

No ADR: this applies existing additive helper/injector patterns and changes no
schema, dependency, API contract, or governance rule.

## Phases

| Phase | Goal | Output | Dependencies |
|-------|------|--------|--------------|
| P0 | Capture baseline and lock hashes | >=623/2 baseline, lints/doctor/lock evidence | none |
| P1 | TDD RED | Failing tests for loader, nav, tokens, wording | P0 |
| P2 | Current Sprint truth | Additive loader + build fallback wiring | P1 |
| P3 | PI-nav truth | Additive nav injector + build wiring | P2 |
| P4 | Lifecycle semantics | Additive token injector + contrast/accessibility behavior | P3 |
| P5 | Exact wording | Two prompt replacements only | P1; file-disjoint from P2-P4 |
| P6 | Real source + generated smoke | PI-9 explicitly marks Sprint 23 active; build regenerates exec | P2-P5 |
| P7 | Close gates | Full tests/lints/doctor/fresh CI/public CI/ledger/lock | P6 |

## Parsing and Selection Contract (SDD-057)

- Scan `sprints/PI-*/CURRENT_PI.md`; parse numeric PI suffix; ignore malformed dirs.
- Candidate PI requires frontmatter `status: active` and a body status declaration
  beginning ACTIVE. Choose highest numeric PI.
- Extract explicit active sprint candidates from, in precedence order:
  1. body Status line containing an overall `Sprint N` with ACTIVE/CURRENT/
     IN-PROGRESS and not CLOSED/DONE/PROPOSED;
  2. active/current/in-progress `### Sprint N` heading, enriched with an overall
     number from the matching Sprint Allocation row when present;
  3. Sprint Allocation row whose status/explanation explicitly marks it active.
- Normalize to `{num, title, status, path}`. `num` is overall Sprint when explicit.
- Exactly one semantic candidate is required. Duplicate identical mentions may
  collapse; conflicting numbers/titles reject the live result.
- OSError, malformed marker, no explicit active marker, or conflict returns `[]`.
- `build()` uses live result when non-empty, else unchanged `load_sprint_table`;
  unchanged `detect_current_sprint` consumes whichever list is selected.

## Injector Ordering

```
render_html(...)
  -> inject_pi_pills_html(..., pis, active_pi)
  -> inject_user_gates_html(...)
  -> inject_lifecycle_html(...)
  -> inject_lifecycle_tokens_html(...)
  -> existing dispatch/health/backlog/drag injectors
```

Both new injectors are marker-bounded and idempotent. Nav replacement changes
only the existing `pi-pills` nav. Token injection changes only lifecycle elements
and adds one style block with a stable marker.

## File-Scope and SDD-049 Overlap Matrix

| Work packet | Mutable files | Intersection | Dispatch verdict |
|-------------|---------------|--------------|------------------|
| A tests RED | `cli/test_state_builder.py`, `cli/test_sdd056.py` | Seeds all packets | Serial first |
| B SDD-057 | `cli/state_builder_data.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | Facade/test with C/D | Serial |
| C SDD-056 nav | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | Full overlap with D; partial B | Serial after B |
| D SDD-038 tokens | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | Full overlap with C | Serial after C |
| E SDD-056 wording | two named kickoff prompts, `cli/test_sdd056.py` | Empty vs B/C/D after A | Parallel-safe after RED tests |
| F source marker | `sprints/PI-9/CURRENT_PI.md` | None, but semantic dependency | Sprint EM/PM before smoke |
| G generated/close | `exec/state.md`, `exec/state.html`, `exec/work-index.md`, validation/tasks/progress artifacts | Consumes all | Serial last |

Before any multi-worker dispatch, run SDD-049's normalized file-scope overlap
check. No `--allow-overlap` is justified for B/C/D; they are deliberately serial.

## Locked and Forbidden Surfaces

- Five Article X functions: no edits.
- `render_markdown`: no edit.
- `constitution/**`: no edit.
- Generated exec files: no hand edit.
- All prompts except the exact Sprint 5 and Sprint 6 files: no edit.

## Test and Close Plan

- TDD: tests fail before each production helper/injector/replacement and pass after.
- Focused state-builder tests, exact-wording test, and unchanged lock guard.
- Real build assertions: PI-9 current; Sprint 23 active; nine token variables/classes;
  two stale phrases absent.
- Accessibility: computed WCAG ratios, retained labels/ARIA, no opacity semantics,
  keyboard/focus and forced-colors inspection.
- Full suite >=623/2 plus additions; schema/origin/staledoc lints; strict local
  doctor; clean-checkout CI doctor; public CI green after authorized push.
- B-1 real outcome rows must exist before close; B-2 and B-4 remain blocking.

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sprint parser guesses from closed prose | Medium | High | Explicit active grammar, conflict rejection, empty fallback |
| Shared-state edits conflict | High if parallel | High | SDD-049 matrix and mandatory serialization |
| Token contrast regresses | Low | High | Locked values + computed test |
| Injector duplicates markup | Medium | Medium | Stable marker + double-application idempotence tests |
| Historical wording scope broadens | Low | Medium | Exact-string replacement test and two-file allowlist |
| Locked function drifts accidentally | Low | High | Hash guard before/after and independent hash report |

## Effort

- SDD-056: S-M
- SDD-057: M
- SDD-038: M
- Combined serialized implementation: L, because shared surfaces prevent safe
  concurrency despite individually small features.
