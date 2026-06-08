---
id: SDD-20260609S6COMPLETE-plan
type: plan
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-sprint-6-completion
---

# Implementation Plan: Sprint 6 Completion Bundle (SDD-032)

- Spec Reference: `spec.md` (SDD-032)
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7), feature slot F-09
- Author: Principal Architect (EM prep session)
- Date: 2026-06-09

---

## Approach Summary

**Implementation-only**. No new architectural decisions. Reuse the
parent-spec `plan.md` decisions for both SDD-019 and SDD-020:

- SDD-019 design: see
  `specs/2026-06-07-serial-clarify-spec-gate/plan.md` "Key Design
  Decisions" sections 1-5.
- SDD-020 design: see `specs/2026-06-07-cross-feature-dedup/plan.md`
  "Key Design Decisions" sections 1-4.

This plan only adds the implementation choices for the four deferred
R-items, all of which are **additive** to the Sprint 6 codebase.

### Additive Design Choices (no new ADRs required)

1. **R7 (SDD-019) priority lookup.** Queue ordering reads BACKLOG
   priority by scanning the row in `backlog/BACKLOG.md` whose first
   cell starts with the feature's SDD-NNN ID. Fallback when not found:
   priority P3 (least). No new state, no API surface added beyond a
   private `_lookup_backlog_priority(feature_id)` helper in
   `cli/fleet.py`.

2. **R8 (SDD-019) cutover constant.** The Article XI ratification
   cutover is `2026-06-08` (date of commit `524872b`). Encoded as a
   module-level constant `ARTICLE_XI_CUTOVER = "2026-06-08"` in
   `cli/fleet.py`. Grandfather predicate: parse `updated` field from
   the relevant frontmatter, compare to cutover, pre-cutover entries
   are flagged grandfathered.

3. **R6 (SDD-020) log writer signatures.** Three private functions
   added to `cli/dedup.py`, all stdlib-only, all callable with
   `--no-emit-logs` to short-circuit:
   - `_write_ledger_rows(db_path, scan_run, overlaps)` -- inserts
     one `dedup_scan_run` row + N `dedup_overlap_flagged` rows.
     Reuses the existing `ledger/init_ledger.py` connection helper.
   - `_write_per_spec_dedup_scan(spec_dir, overlap)` -- writes a
     `dedup-scan.md` file with valid SDD-FDC-001 frontmatter (id,
     type=session, status=active, owner, updated) plus a short body
     section describing the flagged overlap.
   - `_append_rolling_log(log_path, scan_summary)` -- appends one
     pipe-delimited line to `backlog/DEDUP-LOG.md`; creates the file
     with a header on first call.

4. **R8 (SDD-020) hook content.** The instruction line added to
   each prompt is a single numbered list item with exactly this
   payload (final wording owned by F-09 implementer, but the literal
   substring `cli/dedup.py scan` MUST be present and the tier-action
   guidance MUST cover HARD / SOFT / ADVISORY):

   > Before drafting, run `python spec-driven-development/cli/dedup.py
   > scan --scope all`. If HARD, stop and report. If SOFT, surface the
   > candidate to the owner. If ADVISORY, note it in the dedup log and
   > continue.

---

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Close SDD-019 R7 + R8 (queue + grandfather) | None | `cli/fleet.py` updates + `cli/test_fleet.py` new tests |
| 2 | Close SDD-020 R6 (log writers) | None (parallel with Phase 1) | `cli/dedup.py` updates + `cli/test_dedup.py` new tests + `backlog/DEDUP-LOG.md` header |
| 3 | Close SDD-020 R8 (prompt hooks) | Phase 2 complete (so `cmd_scan` emits logs the hooks rely on) | `.github/prompts/triage.prompt.md` + `.github/prompts/clarify.prompt.md` edits + markdown lint test |
| 4 | Close verification (R5-R7) | Phases 1-3 complete | Full test suite green, `schema_lint` clean, `exec/state.md` regenerated, validation.md all checked |

---

## File Scope (constrained, additive only)

| File | Change Type | R-Items | Owner |
|------|-------------|---------|-------|
| `cli/fleet.py` | **Additive only**: new helpers `_lookup_backlog_priority`, `_compute_queue_order`, `_is_grandfathered`, integration into existing `lock status` + pre-dispatch gate output | R7, R8 (SDD-019) | T-032-01, T-032-02 |
| `cli/dedup.py` | **Additive only**: three new writer functions + three calls from `cmd_scan` + new `--emit-logs` / `--no-emit-logs` argparse flag | R6 (SDD-020) | T-032-03 |
| `cli/test_fleet.py` | **New tests only**: `TestQueueOrdering` (3 tests), `TestGrandfather` (3 tests) | R7, R8 (SDD-019) | T-032-01, T-032-02 |
| `cli/test_dedup.py` | **New tests only**: `TestDedupLogWriters` (4 tests), `TestPromptHooks` (3 tests) | R6, R8 (SDD-020) | T-032-03, T-032-04, T-032-05 |
| `.github/prompts/triage.prompt.md` | **Minimal edit**: one new numbered list item invoking dedup scan | R8 (SDD-020) | T-032-04 |
| `.github/prompts/clarify.prompt.md` | **Minimal edit**: one new numbered list item invoking dedup scan | R8 (SDD-020) | T-032-05 |
| `backlog/DEDUP-LOG.md` | **New file**: rolling log header + first-run placeholder entry | R6 (SDD-020) | T-032-03 |
| `exec/state.md`, `exec/state.html`, `exec/work-index.md`, `exec/sprint-progress.md` | **Regenerated** by `state_builder.py` at close | R7 | T-032-06 |

### Files NOT in scope (NEW MODULES NOT NEEDED)

Optional `spec-driven-development/cli/__init__.py` addition mentioned
in the spec is **NOT needed**. The three log writers fit cleanly in
`cli/dedup.py` and the two new fleet helpers fit cleanly in
`cli/fleet.py`. No new module factor is justified by the four deferred
R-items.

---

## Lock-Surface Protections (DO NOT EDIT)

The following code surfaces are **LOCKED** by Sprint 6 commits and
**MUST NOT** be modified by any T-032-NN task. Implementers verify by
`git diff --stat` and by reviewing diff hunks before commit.

### From commit `524872b` (`cli/fleet.py` -- SDD-019 implementation)

- `_scan_lock_state(specs_root)` -- lock scanner function body
  (lines around 292). May read, must not modify.
- `cmd_lock_status`, `cmd_lock_acquire`, `cmd_lock_release`,
  `cmd_lock_force_release` -- existing lock subcommand handlers.
  Output may be **extended** (additive lines after existing prints)
  but existing print statements must remain byte-identical so existing
  tests stay green.
- Pre-dispatch gate check in `cmd_dispatch` -- the "lock held by X"
  refusal path. May read, must not modify.

### From commit `8eb564d` (`cli/dedup.py` -- SDD-020 implementation)

- `load_corpus`, `_parse_backlog_table`, `_parse_ideas`,
  `_parse_spec_entry` -- corpus loader. Must not modify.
- `_tokenize`, `_jaccard`, `find_overlaps` -- three-layer heuristic.
  Must not modify.
- `_format_overlap`, `handle_overlaps` -- tiered action handler.
  Must not modify.
- `parse_args` -- existing argparse subparser shape. New
  `--emit-logs` / `--no-emit-logs` flag is **added** to `p_scan`; no
  existing flags are removed, renamed, or have their defaults changed.
- `cmd_scan` body -- existing scan-execution logic stays
  byte-identical. The three new writer calls are added at the **end**
  of the function (after exit-code is known) guarded by
  `if args.emit_logs:`.

### From `cli/test_fleet.py` and `cli/test_dedup.py`

- **No existing test classes** are modified or renamed.
- **No existing test names** are changed.
- New tests are added as new classes (`TestQueueOrdering`,
  `TestGrandfather`, `TestDedupLogWriters`, `TestPromptHooks`).

---

## Parallel-Safe Tasks

- **T-032-01 (R7 queue) vs T-032-03 (R6 log writers)** -- different
  files (`cli/fleet.py` vs `cli/dedup.py`). PARALLEL-SAFE.
- **T-032-02 (R8 grandfather)** -- same file as T-032-01
  (`cli/fleet.py`). Must serialize after T-032-01.
- **T-032-04 (triage hook) vs T-032-05 (clarify hook)** -- different
  files. PARALLEL-SAFE. Both depend on T-032-03.

## Sequential Tasks

1. T-032-01 -- R7 queue ordering (`cli/fleet.py` first edit).
2. T-032-02 -- R8 grandfather (`cli/fleet.py` second edit; must
   merge with T-032-01).
3. T-032-03 -- R6 log writers (`cli/dedup.py`; runs in parallel with
   T-032-01 + T-032-02 because different file).
4. T-032-04 -- /triage hook (depends on T-032-03 land).
5. T-032-05 -- /clarify hook (depends on T-032-03 land; parallel
   with T-032-04).
6. T-032-06 -- Close verification (depends on all of T-032-01..05).

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Prompt-hook wiring (R8) is hard to test programmatically -- it's a slash-command behavior change | Medium | Medium | Capture exact prompt-file edits and verify with a markdown lint test (`TestPromptHooks`). The test asserts both files contain the literal substring `cli/dedup.py scan` plus the HARD/SOFT/ADVISORY tier-action guidance. Runtime invocation by the agent is verified by manual check at close (validation.md "Manual Checks" item 1). |
| Grandfather behavior conflicts with already-pushed Sprint 6 lock state -- some spec dirs are mid-flight at the cutover commit | Medium | Medium | Spec the migration explicitly: "on first edit after Article XI ratification, the feature claims the lock if it's free, else queues" (encoded in AC-2 and R2). Cutover constant is `2026-06-08` (date of commit `524872b`). Grandfather predicate compares frontmatter `updated` to cutover; pre-cutover entries get the implicit-lock treatment. |
| Queue ordering reads BACKLOG priority but the priority column format drifts | Low | Low | Fallback to priority P3 (least) when row not parseable. Tested by `TestQueueOrdering.test_priority_lookup_fallback` (new). |
| Log-writer DB schema collision with existing ledger rows | Low | Low | Reuses existing event types (`dedup_scan_run`, `dedup_overlap_flagged`) approved in SDD-020 parent CLARIFY Q6. No schema change needed. Verified by `cli/test_dedup.py` integration test. |
| `cmd_scan` regression -- adding writer calls breaks existing tests | Medium | High | Writer calls guarded by `if args.emit_logs:`; default in test fixtures is `--no-emit-logs` to preserve existing scratch-only test behavior. New writer-specific tests use a tmp dir + tmp DB. |
| Markdown lint test for prompt hooks too brittle (whitespace, casing) | Low | Low | Test uses `"cli/dedup.py scan" in content.lower()` (case-insensitive substring match) plus tier-keyword checks (`"hard"`, `"soft"`, `"advisory"` all present). Allows future prompt wording polish without test breakage. |

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 | M | Two additive helpers + 6 new tests in `cli/fleet.py` / `cli/test_fleet.py`. Sequential within the file. |
| 2 | M | Three writer functions + flag + 4 new tests + new log header file. |
| 3 | S | Two minimal prompt edits + 3 lint tests. |
| 4 | S | Verification only -- regen state, run pytest, run schema_lint, check validation.md. |

Total: **M** (one fresh F-09 session per Article VII; estimated 2-3
hours of focused worker time).

## Validation Criteria

> Cross-reference rule: each validation checkbox below references the
> spec AC and the validation.md R-item it covers.

- [ ] Validates AC-1 / R1 (queue ordering).
- [ ] Validates AC-2 / R2 (grandfather).
- [ ] Validates AC-3 / R3 (log writers).
- [ ] Validates AC-4a / R4 (triage hook).
- [ ] Validates AC-4b / R4 (clarify hook).
- [ ] Validates AC-5 / R5-R7 (close verification).

## Cross-Feature Notes

- **SDD-018 (UI Lifecycle Variant)** opens at Sprint 7 F-10. F-09
  (this spec) MUST land first so SDD-018 does not get caught in the
  undefined-queue / undefined-grandfather state.
- **SDD-033 (SDD-027 R12 docs gap)** is filed separately as P3 docs
  polish and is NOT in this bundle.
