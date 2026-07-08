---
id: SDD-20260626MAINT-validation-c1
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# VALIDATION: SDD-048 / C-1 -- break up the `state_builder.py` god-module

- Per-item ID: C-1 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN C-1 Acceptance
- Lock statement: LOCKED at F-44. F-45 may CHECK with real-run evidence; may not weaken a REQUIRED item. Deltas are numbered DE-xx and must SHARPEN.

## Required Items (Strict)

- [ ] **R-1 (modules exist).** `state_builder.py` is decomposed into focused sibling modules under `cli/` covering at least: data assembly, markdown render, non-locked html, HTTP server, doc-count, work-index (boundaries per [`plan.md`](plan.md)). Evidence: the new module files exist and import cleanly with stdlib only.
- [ ] **R-2 (no oversized non-locked function).** No NON-locked top-level function across the `state_builder*` / sibling module set exceeds ~120 lines. Evidence: an `ast`-based line-count over each module's top-level `def`/`async def`, excluding the five locked names, shows max <= ~120.
- [ ] **R-3 (server + doc-counter isolated).** The HTTP server (`DashboardHandler`, `serve`, `handle_reorder_request`, `served_html_with_refresh`, `_port_available`) lives in its own module, and the doc-counter (`build_doc_count`, `build_doc_count_by_sprint`, `render_count_table`, `cmd_count`) lives in its own module. Evidence: grep confirms each symbol's defining module.
- [ ] **R-4 (locked functions byte-identical).** All five S1-footprint functions (`render_html`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, `load_decisions`) remain physically in `state_builder.py` and byte-identical. Evidence: `TestS1FootprintLockGuard` passes; golden SHA-256 hashes UNCHANGED (commit `257b081` anchor).
- [ ] **R-5 (backward-compatible imports).** Every name imported by `cli/test_state_builder.py` still resolves via `from cli.state_builder import <name>` (re-export from siblings). Evidence: the test module's import block is unmodified; suite collects with zero import errors.
- [ ] **R-6 (one extraction per commit, suite green).** Each module extraction is a single commit that leaves `python -m pytest spec-driven-development/ --tb=no -q` at 540 passed / 2 skipped. Evidence: per-commit suite run logged; no assertion text changed.
- [ ] **R-7 (no behavior change).** The rendered `state.md`, `state.html`, and HTTP responses are byte-equivalent before/after the split. Evidence: a build before vs after produces identical output (diff empty).

## Manual Checks

- [ ] **M-1.** Reviewer confirms NO locked function was edited, moved, or renamed -- only NON-locked helpers were extracted and re-imported.
- [ ] **M-2 (OPTIONAL, Q-F).** If the optional max-function-length lint was built, it is stdlib-only (`ast`), excludes the five locked functions, and does NOT block the suite. If not built, this check is N/A (it is a nice-to-have, not a gate).
- [ ] **M-3.** Reviewer confirms `render_html` (658 lines, locked) is the ONLY function over ~120 lines remaining, and it is documented as the Article X exception (no escalation opened).

## Definition of Done

R-1..R-7 checked with real-run evidence; `TestS1FootprintLockGuard` green with
unchanged golden hashes; full suite 540/2 after every extraction; M-1 and M-3
confirmed; M-2 N/A-or-pass. No third-party import introduced.
