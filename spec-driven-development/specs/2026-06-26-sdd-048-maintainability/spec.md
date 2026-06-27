---
id: SDD-20260626MAINT-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# SPEC: SDD-048 -- Maintainability + right-sizing

- Epic ID: SDD-048 (PI-7 Sprint 17)
- CLARIFY: [`clarify.md`](clarify.md) | Plan: [`plan.md`](plan.md) | Tasks: [`tasks.md`](tasks.md)
- Spec source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) Part C (C-1/C-2/C-3) + Part D (D-2)
- Per-item validation: [`validation-C1.md`](validation-C1.md), [`validation-C2.md`](validation-C2.md), [`validation-C3.md`](validation-C3.md), [`validation-D2.md`](validation-D2.md)
- C-2 decision record: [`../../docs/ADR/023-dashboard-render-stdlib-only.md`](../../docs/ADR/023-dashboard-render-stdlib-only.md)

---

## Goal

The dashboard generator is maintainable and the framework's ceremony fits the
work. `state_builder.py` (now ~4153 lines, ~79 functions) is split into focused
sibling modules so no NON-locked function exceeds ~120 lines; the stdlib-only
rule is consciously preserved with a factored `string.Template` rendering layer
instead of one f-string wall; the Article XI cutover date lives in config, not
in CLI logic; and a <5-file feature can complete the lifecycle with one combined
artifact while still satisfying Article X. All of this is achieved WITHOUT
touching the five Article X S1-footprint locked functions and WITHOUT introducing
any third-party dependency.

## Non-goals

- Touching, moving, or rewriting any of the five locked functions
  (`render_html`, `load_sprint_table`, `load_sprint_goal`,
  `detect_current_sprint`, `load_decisions`). Approach (a) refactors AROUND them.
- Any Article X re-baseline / golden-hash change. (That would be a separate
  Level-2 owner-ratified amendment; it is explicitly out of scope.)
- Any behavior change to the dashboard output (markdown, HTML, or HTTP server).
  C-1/C-2 are pure refactors -- the rendered bytes do not change.
- Introducing a third-party templating dependency. Article V stands.
- Implementation. F-44 produces design artifacts only; F-45 implements.
- Weakening the Article X validation lock via D-2. D-2 collapses duplication only.
- Closing PI-7 (a separate owner-approved decision after this sprint).

## Requirements

Per-item SDD-IDs use the audit labels (C-1/C-2/C-3/D-2) as handles. RFC-2119
language. "Locked functions" = the five S1-footprint functions guarded by
`TestS1FootprintLockGuard`.

### C-1 -- break up the `state_builder.py` god-module

- **R-C1-1**: `state_builder.py` MUST be decomposed into focused sibling modules.
  The split MUST cover, at minimum: data assembly, markdown render, html render
  (non-locked helpers/injectors only), HTTP server, doc-count, and work-index.
  Concrete module boundaries are fixed in [`plan.md`](plan.md).
- **R-C1-2**: After the split, no NON-locked top-level function MAY exceed ~120
  lines. The five locked functions are an explicit, documented exception
  (`render_html` is the only locked function over 120 lines).
- **R-C1-3**: The HTTP server (`DashboardHandler`, `serve`, `handle_reorder_request`,
  `served_html_with_refresh`, `_port_available`) and the doc-counter
  (`build_doc_count*`, `render_count_table`, `cmd_count`) MUST each live in their
  own module.
- **R-C1-4**: All five locked functions MUST remain byte-identical and physically
  in `state_builder.py`. `TestS1FootprintLockGuard` MUST pass unchanged (golden
  hashes untouched).
- **R-C1-5**: The public import surface MUST stay backward-compatible. Every name
  imported by `cli/test_state_builder.py` MUST still resolve via
  `from cli.state_builder import <name>` (re-export from siblings). No test
  assertion changes.
- **R-C1-6**: Each module extraction MUST be a single commit that leaves the full
  suite green (540 passed / 2 skipped) -- pure refactor, no behavior change.

### C-2 -- right-size the stdlib-only rule (render wall)

- **R-C2-1**: The framework MUST remain stdlib-only (Article V). No third-party
  dependency is added or proposed.
- **R-C2-2**: The NON-locked render surface (`render_markdown` at 762 lines, plus
  the non-locked html injectors) MUST be factored into `string.Template`-based
  (stdlib) helpers so it is no longer one monolithic f-string wall.
- **R-C2-3**: `render_html` (658 lines, LOCKED) is explicitly EXEMPT from R-C2-2
  and remains a documented Article X exception. C-2 does NOT attempt to factor it.
- **R-C2-4**: An ADR (023) MUST record the stdlib-only decision, the
  `string.Template` factoring choice, and the `render_html`-locked trade-off.
  ADR status is Proposed at F-44; owner ratifies to Accepted at close.

### C-3 -- replace the hardcoded grandfather date

- **R-C3-1**: `ARTICLE_XI_CUTOVER` MUST be sourced from `project.config.json`
  (stdlib `json`), not hardcoded as a literal in CLI logic.
- **R-C3-2**: A fallback constant and a comment explaining WHY the cutover exists
  (SDD-019.R8 Article XI grandfather migration) MUST be retained in `fleet.py`.
- **R-C3-3**: No hardcoded calendar date MAY remain in CLI control flow without a
  config source and an explanatory comment. `_is_grandfathered` behavior is
  unchanged for existing spec dirs.

### D-2 -- lightweight-spec path for small features

- **R-D2-1**: There MUST be a documented ONE-document combined artifact shape
  (story + requirements + validation contract) usable for <5-file features, with
  cross-links replacing the four near-duplicate lifecycle files.
- **R-D2-2**: The combined artifact MUST still satisfy Article X: a checkable
  validation contract is authored BEFORE implementation; REQUIRED items remain
  strict. The lock is NOT weakened.
- **R-D2-3**: The combined-doc shape MUST be proven on one real <5-file feature in
  F-45 (design-only in F-44).

### Q-F (OPTIONAL) -- max-function-length lint

- **R-QF-1 (OPTIONAL)**: A stdlib (`ast`) lint MAY flag NON-locked functions over
  a configured line budget. If built, it MUST exclude the five locked functions
  and MUST NOT block the sprint. This is a nice-to-have, not a gate.

## Acceptance criteria (measurable)

| ID | Criterion | Verifies |
|----|-----------|----------|
| AC-1 | After C-1, no NON-locked top-level function in the `state_builder*` module set exceeds ~120 lines | R-C1-2 |
| AC-2 | HTTP server and doc-counter each live in their own module | R-C1-3 |
| AC-3 | `TestS1FootprintLockGuard` passes; golden hashes unchanged; 5 locked funcs byte-identical in `state_builder.py` | R-C1-4 |
| AC-4 | `cli/test_state_builder.py` imports unchanged; full suite 540 passed / 2 skipped after every extraction | R-C1-5, R-C1-6 |
| AC-5 | `render_markdown` + non-locked html injectors factored via `string.Template`; no third-party import anywhere in `cli/**` | R-C2-1, R-C2-2 |
| AC-6 | ADR-023 exists recording stdlib-only + `render_html`-locked trade-off (Proposed) | R-C2-4 |
| AC-7 | `ARTICLE_XI_CUTOVER` resolves from `project.config.json` with fallback + comment; `_is_grandfathered` behavior unchanged | R-C3-1..3 |
| AC-8 | A combined-doc lightweight-spec shape is documented and Article-X-compliant; proven on a real <5-file feature | R-D2-1..3 |
| AC-9 | Stdlib-only preserved: `schema_lint.py` exit 0; no new dependency | R-C2-1, Article V |

## Traceability

| Story | Requirement(s) | Acceptance | Validation |
|-------|----------------|-----------|------------|
| Maintainable generator | R-C1-1..6 | AC-1..4 | [`validation-C1.md`](validation-C1.md) |
| Conscious stdlib choice | R-C2-1..4 | AC-5, AC-6, AC-9 | [`validation-C2.md`](validation-C2.md) |
| Config-driven cutover | R-C3-1..3 | AC-7 | [`validation-C3.md`](validation-C3.md) |
| Right-sized ceremony | R-D2-1..3 | AC-8 | [`validation-D2.md`](validation-D2.md) |
| Optional length lint | R-QF-1 | (optional) | [`validation-C1.md`](validation-C1.md) (M-checks) |

## Constraints (binding)

- Stdlib-only (Article V). No third-party dependency introduced or proposed.
- Five Article X locked functions IMMUTABLE (approach (a) refactors around them).
- C-1/C-2 are pure refactors: no behavior change, no test-assertion change, one
  module extraction per commit.
- D-2 does NOT weaken the Article X validation lock.
- F-45 runs serial: the split touches shared serial surfaces
  (`cli/state_builder.py` + new siblings, `cli/fleet.py`, `project.config.json`,
  optionally `cli/schema_lint.py`, `templates/`). No parallel fleet on shared files.
- End-state gates: `python -m pytest spec-driven-development/ --tb=no -q` ->
  540 passed / 2 skipped; `python spec-driven-development/cli/schema_lint.py` -> exit 0.
