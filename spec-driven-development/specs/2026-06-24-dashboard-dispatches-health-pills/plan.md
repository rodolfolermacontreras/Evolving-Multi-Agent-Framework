---
id: SDD-20260624DASHHEALTH-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-24
feature: 2026-06-24-dashboard-dispatches-health-pills
---

# PLAN: SDD-037 -- Dispatches card + dashboard health-pills strip

- Feature ID: SDD-037
- Spec: [`spec.md`](./spec.md) | CLARIFY: [`clarify.md`](./clarify.md) | Validation: [`validation.md`](./validation.md)
- Sprint: PI-6 / Sprint 3 (overall Sprint 12); this plan governs **F-28 implementation**. Plan authored at F-27 (design-only).

---

## Approach Summary

Implement two additive, read-only dashboard surfaces inside `cli/state_builder.py`, mirroring the existing `inject_lifecycle_html` post-processor discipline:

1. **Widen the existing single ledger read** (`load_ledger` / `LedgerView`) with a grouped/all-rows accessor populated **inside the same single `sqlite3.connect`** -- no second connection, no new public ledger API, no schema change.
2. **`inject_dispatches_html`** -- renders a Dispatches card grouped by feature then sprint, with empty and disabled (unreachable) states that never crash.
3. **Four read-only health-check helpers** -- constitution semver (read-only over `constitution/**`), skill validity (reuse `schema_lint.check_skill`), ledger reachability (from the single `LedgerView`), stale-tracker (N=7 against `exec/sprint-progress.md`). Each returns a (status, reason, detail) triple and never raises.
4. **`inject_health_pills_html`** -- renders the four-pill header strip with server-rendered click-through detail sections and same-page anchors; no JavaScript.
5. **Wire both injectors in `build()`** immediately after `inject_lifecycle_html`; add the supporting CSS blocks.

Every change is additive. The five Article X locked S1 functions (`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`) are not touched; `TestS1FootprintLockGuard` is the guard. The no-JS invariant (`script tags:0`) is preserved.

## Phases

| Phase | Name | Output |
|-------|------|--------|
| P0 | Baseline capture | Recorded pre-F-28 pytest passed/skipped counts and `schema_lint` exit 0 |
| P1 | Additive ledger widening | `LedgerView` grouped accessor + `load_ledger` populates it in the existing single connection; `build()` passes it through |
| P2 | Dispatches card | `inject_dispatches_html` + CSS; empty + disabled states; wired after `inject_lifecycle_html` |
| P3 | Health-check helpers | Four pure read-only status helpers (semver, skill via `check_skill`, ledger, stale N=7), each degrade-safe |
| P4 | Health-pills strip | `inject_health_pills_html` + CSS + server-rendered detail sections + anchors; wired after the Dispatches injector |
| P5 | Invariant + regenerate | Indicators-not-gates + S1-lock + no-JS guards; regenerate `state.html`; `schema_lint` 0; full suite >= baseline + new |

## File Scope (Constrained)

- `cli/state_builder.py` -- additive only:
  - widen `LedgerView` (new grouped/all-rows field) and `load_ledger` (populate it in the existing connection)
  - add `inject_dispatches_html(html_doc, *, ledger, sdd_root)`
  - add `constitution_semver_status(sdd_root)`, `skill_validity_status(repo_root)`, `ledger_reachability_status(ledger)`, `stale_tracker_status(sdd_root, now=None, stale_days=7)`
  - add `inject_health_pills_html(html_doc, *, sdd_root, ledger, now=None)`
  - add wiring lines in `build()` after the `inject_lifecycle_html` call
  - add CSS blocks (`_DISPATCHES_STYLE`, `_HEALTH_PILLS_STYLE`) alongside the existing `_LIFECYCLE_STYLE`
- `cli/test_state_builder.py` -- additive test classes only.

## Files Not In Scope (do not edit)

- The five Article X locked S1 functions inside `cli/state_builder.py` (`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`).
- `cli/schema_lint.py` (imported/reused read-only; `check_skill` is called, not modified).
- `constitution/**` (read-only; Article VIII).
- `ledger/__init__.py` (stays empty), `ledger/schema.sql`, `ledger/fleet.db` (read-only; no schema change).
- `exec/sprint-progress.md` (read-only).
- Any other `cli/*.py`, any prompt/agent/skill file.

## Lock-Surface Protections

- New code is added as **new top-level functions** and **new wiring lines in `build()`** only. No locked S1 function body is edited.
- `TestS1FootprintLockGuard` (golden SHA-256 vs commit 257b081) runs unchanged and must pass.
- The `<script>` tag count of the generated document must remain 0 (no-JS invariant); a test asserts this.

## File Dependency Graph (F-28)

```
                 +-------------------------------+
                 |   cli/state_builder.py        |  (single shared file)
                 |                               |
  P1  LedgerView/load_ledger widening (1 conn)   |
                 |        |                       |
  P2             |        v   inject_dispatches_html
                 |        |                       |
  P3             |        +-> 4 health-check helpers (read-only)
                 |        |        |              |
  P4             |        |        v   inject_health_pills_html
                 |        |        |              |
  P5             |        +--------+--> build() wiring (after inject_lifecycle_html)
                 +-------------------------------+
                                |
                                v
                 +-------------------------------+
                 |  cli/test_state_builder.py    |  (single shared file)
                 |  new test classes for P1..P5  |
                 +-------------------------------+
                                |
        reads (no edit): schema_lint.check_skill, constitution/*.md,
                         ledger/fleet.db (existing schema), exec/sprint-progress.md
```

Every node mutates one of exactly two files: `cli/state_builder.py` and `cli/test_state_builder.py`.

## Parallel-Safe Tasks

- **None.** All implementation tasks write to the same two shared files (`cli/state_builder.py`, `cli/test_state_builder.py`). There is no independent new module (unlike SDD-036's `backlog_reorder.py`).

## Sequential Tasks

- All F-28 tasks (T-037-01 .. T-037-07) run **in order** in a single serialized session: baseline -> ledger widening -> Dispatches card -> health helpers -> pills strip -> invariant guard -> regenerate/verify.

## Serialization Verdict

**F-28 is serialized, single-session, NOT fleet-dispatch eligible.** Justification: both touched files are shared, and the surfaces are interdependent (the pills strip consumes the same widened `LedgerView` as the Dispatches card; both wire into the same `build()`). Concurrent worker dispatch would guarantee merge conflicts in `cli/state_builder.py`. This matches the SDD-036 precedent where even a separable helper was serialized for the shared `state_builder.py` surface.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| S1 lock broken by stray edit | Low | High | New top-level functions only; `TestS1FootprintLockGuard` guard; P5 verifies |
| Second `sqlite3.connect` added | Low | Medium | Widen inside `load_ledger`'s existing connection; AC-4 single-connection test |
| Health check raises and aborts build | Medium | High | Each helper wrapped to degrade to red/yellow + reason; AC-11 forced-failure tests |
| Constitution accidentally written | Low | High | Read-only `parse_frontmatter`; Article VIII; tests assert no mutation |
| JavaScript creeps in | Low | Medium | Server-rendered anchors only; `<script>`-count test |
| Test baseline regresses | Low | Medium | P0 captures baseline; P5 asserts >= baseline + new (two known skips unchanged) |

## Effort Estimate

- P0: XS | P1: S | P2: M | P3: M | P4: M | P5: S
- Total: ~M-L, single serialized session (F-28). Design (F-27) is complete with this artifact set.

## Validation Criteria Pointer

The binding validation contract is [`validation.md`](./validation.md), LOCKED at F-27. All REQUIRED items remain UNCHECKED until F-28 verification. Strict items (ledger-read/health-check correctness, S1 lock, no-JS, indicators-not-gates, schema_lint 0, test baseline) may not be loosened; UI-Variant items (card and pill visual rendering) are delta-eligible.
