---
id: SDD-20260626MAINT-d2proof
type: feature
status: done
owner: principal-software-developer
updated: 2026-06-26
---

<!--
  SDD-048 D-2 PROOF ARTIFACT.

  This is the single combined lightweight-feature artifact (story +
  requirements + plan + validation contract in one file) authored from
  templates/lightweight-feature.md. It proves the D-2 lightweight path
  end-to-end on a REAL <5-file feature: the C-3 config-sourced Article XI
  cutover (3 files), already delivered at commit 6383049.

  The combined path does NOT bypass the validation contract -- it merges the
  four documents (story + requirements + plan + validation) into one file
  while preserving the Article X lock (Required Items strict + Manual Checks
  + Definition of Done authored as a checkable contract). It collapses
  duplication, not rigor.

  Eligibility: 3 files (< 5), no Level-2 decision, no new public surface,
  no new dependency. Per Constitution Article VI (Ceremony Proportional To
  Risk), this work qualifies for the lightweight single-artifact path.
-->

# Feature: config-source the Article XI grandfather cutover (C-3)

## Story

The Article XI grandfather cutover date was a bare string literal
(`ARTICLE_XI_CUTOVER = "2026-06-08"`) buried in `fleet.py` control flow. A
host-project owner adopting the framework had no documented way to find or
override it. C-3 moves the value into `project.config.json` (read with
stdlib `json`), keeps a documented fallback constant for when the field is
absent, and leaves `_is_grandfathered` behavior byte-identical for existing
spec dirs.

## Requirements

- **R-1 (MUST -- config-sourced cutover).** `ARTICLE_XI_CUTOVER` MUST be read
  from `project.config.json` via stdlib `json`, not defined as a bare literal
  in CLI control flow.
- **R-2 (MUST -- fallback + comment retained).** `fleet.py` MUST keep a
  fallback constant for when the config field is absent, and MUST retain a
  comment explaining WHY the cutover exists (SDD-019.R8 Article XI grandfather
  migration).
- **R-3 (MUST -- no hardcoded date in CLI logic).** No hardcoded calendar
  date MUST remain in CLI control flow without a config source and
  explanatory comment.
- **R-4 (MUST -- behavior unchanged).** `_is_grandfathered` MUST return the
  same verdict for existing spec dirs as before the change.

## Plan

- **Files in scope (3, max 4):**
  - `project.config.json` -- add the `article_xi_cutover` field.
  - `cli/fleet.py` -- add `_resolve_article_xi_cutover()` reading config with
    a documented fallback constant; bind `RESOLVED_ARTICLE_XI_CUTOVER`;
    `_is_grandfathered` defaults to the resolved value.
  - `cli/test_fleet.py` -- add `TestArticleXICutoverConfig` (config-sourced
    and fallback paths agree for `2026-06-08`).
- **Files out of scope:** the five Article X locked functions in
  `state_builder.py`; any constitution file; any third-party dependency.
- **Approach:** read the cutover from config at module import via a small
  resolver; keep the literal only as a clearly-commented fallback; preserve
  identical grandfather verdicts.
- **Test strategy:** TDD -- new `TestArticleXICutoverConfig` asserts the
  config path and the fallback path both yield `2026-06-08`; existing fleet
  tests guard behavior parity.

## Validation Contract

### Required Items (strict)

- [x] **R-1 (config-sourced cutover).** `fleet.py` resolves the cutover from
  `project.config.json` via stdlib `json`. Evidence: commit `6383049`;
  `project.config.json` carries `article_xi_cutover`;
  `_resolve_article_xi_cutover()` reads it.
- [x] **R-2 (fallback + comment retained).** Fallback constant at
  `fleet.py:50` retained with the SDD-019.R8 Article XI comment. Evidence:
  commit `6383049`; `TestArticleXICutoverConfig` covers the fallback path.
- [x] **R-3 (no hardcoded date in CLI logic).** Grep for `"20\d\d-\d\d-\d\d"`
  literals across `cli/**` shows only the documented `fleet.py:50` fallback
  constant; none in control flow without a config-backed source + comment.
- [x] **R-4 (behavior unchanged).** `_is_grandfathered` verdicts unchanged;
  config-sourced and fallback paths agree for `2026-06-08`. Evidence: 6
  `TestArticleXICutoverConfig` tests pass; full suite 546 passed / 2 skipped
  at commit `6383049`.

### Manual Checks

- [x] **M-1.** The `article_xi_cutover` field name and location in
  `project.config.json` are documented so a host-project owner can
  find/override it.
- [x] **M-2.** Stdlib-only: only `json` is used to read the config (Article V
  holds).

### Definition of Done

R-1..R-4 checked with real-run evidence; fleet tests green; config field
documented; stdlib-only; full suite >= 540/2 and `schema_lint` exit 0. The
Article X lock is intact -- this validation contract was authored as a
checkable Required-Items / Manual-Checks / Definition-of-Done block and is
not weakened by the combined-doc format.

## Eligibility

This feature touches 3 files (< 5), carries no Level-2 decision (no new
dependency, pattern, or schema change), and adds no new public surface. Per
Constitution Article VI (Ceremony Proportional To Risk), it qualifies for the
D-2 lightweight single-artifact path. Cross-cutting changes, new public
surfaces, or any Level-2 decision require the full four-doc path.
