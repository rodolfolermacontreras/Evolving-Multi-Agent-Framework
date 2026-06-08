---
id: SDD-20260609S6COMPLETE-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-09-sprint-6-completion
---

# Feature Spec: Sprint 6 Completion Bundle (SDD-032)

- Date: 2026-06-09
- Author: Principal Architect (EM prep session)
- Status: APPROVED (pre-approved by owner 2026-06-08 as Option 3 hybrid)
- Priority: P1
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7), feature slot F-09
- Spec ID: SDD-032

> **CLARIFY not required.** This is an implementation-only completion bundle.
> All design questions are already final in the parent spec dirs
> (`specs/2026-06-07-serial-clarify-spec-gate/` and
> `specs/2026-06-07-cross-feature-dedup/`). This spec re-uses those
> answers verbatim and adds only the implementation tasks + validation lift
> required to close the four LOCKED REQUIRED items that were deferred from
> Sprint 6 close.
>
> Owner direction 2026-06-08 (Option 3 hybrid): **NO further deferral**
> may be taken on any REQUIRED item at Sprint 7 F-09 close.

---

## Problem Statement

Sprint 6 (PI-5 / Sprint 2) closed on 2026-06-08 with four LOCKED REQUIRED
validation items explicitly deferred from the parent feature contracts. The
deferral was recorded in the parent `validation.md` files at commit
`4a6941c` and ratified by the owner at commit `6c70e30`, with the explicit
carry-over commitment to file a Sprint-6-completion bundle (`SDD-032`).

The four deferred items are split across two parent specs:

- **SDD-019 (Serial Gate on CLARIFY/SPEC), R7 -- priority-weighted FIFO queue.**
  Sprint 6 shipped the per-phase locks, the pre-dispatch gate, and
  `lock force-release`, but the v1 implementation uses *first-found*
  semantics when multiple features contend for the same locked phase.
  Without R7, the gate works for the steady-state two-feature case but
  has undefined behavior under contention.
- **SDD-019 (Serial Gate on CLARIFY/SPEC), R8 -- grandfather migration.**
  Sprint 6 treats every open feature uniformly at lock-scan time. There
  is no defined treatment for features that were already mid-flight in
  CLARIFY or SPEC when Article XI shipped (commit `524872b`,
  2026-06-08). Without R8, a pre-existing in-flight feature can be
  surprise-blocked the first time a Sprint 7 lock check fires.
- **SDD-020 (Cross-Feature Deduplication), R6 -- triple-destination log writers.**
  Sprint 6 shipped the standalone `cli/dedup.py`, the three-layer
  heuristic, the tiered action handler, the CLI entry point, and empty-
  corpus handling. The Q6 CLARIFY answer mandated three-destination
  logging (ledger row + per-spec-dir `dedup-scan.md` + rolling
  `backlog/DEDUP-LOG.md`); the v1 implementation stubs all three. Every
  dedup run today produces console output and an exit code, then
  evaporates with no audit trail.
- **SDD-020 (Cross-Feature Deduplication), R8 -- prompt hooks.**
  Sprint 6 shipped a CLI that is fully invokable from the shell but is
  not wired into any agent workflow. `/triage` and `/clarify` slash
  commands do not call `cli/dedup.py scan`. The dedup scanner is
  shipped-but-not-wired -- it will never run in the normal SDD
  lifecycle until R8 ships.

The combined effect is: SDD-020 is **shipped dead** (the scanner exists
but nothing invokes it), and Article XI behavior is **incomplete**
(queue and migration paths undefined). Both gaps must close before
SDD-018 (UI Lifecycle Variant) opens in Sprint 7 F-10/F-11, since
SDD-018 will exercise both gates as part of its dispatch flow.

## Proposed Solution

Ship a four-item implementation-only bundle that closes the four
deferred R-items with zero new design decisions. Every behavior is
already specified verbatim in the parent CLARIFY answers; this spec
re-binds those answers to new task IDs (`T-032-NN`) and a new
validation contract that LOCKS at scaffold time.

Constraints baked into the solution:

- **No new architecture.** Reuse the parent-spec plan.md design
  decisions for both SDD-019 and SDD-020. No ADRs needed. No
  constitution edits.
- **Additive-only file edits.** The Sprint 6 lock scanner
  (`_scan_lock_state` in `cli/fleet.py`, commit `524872b`) and the
  Sprint 6 dedup core (`load_corpus`, `find_overlaps`, `handle_overlaps`
  in `cli/dedup.py`, commit `8eb564d`) are LOCKED. New functions are
  added; existing functions are not modified.
- **Frontmatter-derived queue ordering (R7).** Queue contents are
  derived at lock-scan time from the same frontmatter source the lock
  scanner already uses, then ranked by the priority field on the
  feature's `BACKLOG.md` row (P1/P2/P3) with submission timestamp
  (`updated` frontmatter) as FIFO tiebreak. No new state file.
- **Cutover-commit grandfather (R8 / SDD-019).** Any spec dir whose
  `clarify.md` or `spec.md` `updated` timestamp is **strictly older
  than** the Article XI ratification commit (`524872b`,
  2026-06-08) is treated as a grandfathered lock holder. It is not
  retroactively blocked. On the first edit after Article XI shipped,
  the feature claims the lock if free, or queues if held.
- **Triple-destination log writers (R6 / SDD-020).** Implement three
  thin writer functions in `cli/dedup.py` that fire from `cmd_scan`:
  `_write_ledger_rows(...)` (writes `dedup_scan_run` and one
  `dedup_overlap_flagged` per overlap to `ledger/fleet.db`),
  `_write_per_spec_dedup_scan(...)` (writes `dedup-scan.md` to the
  candidate's spec dir when the overlap is spec-bound), and
  `_append_rolling_log(...)` (appends a one-line entry to
  `backlog/DEDUP-LOG.md`). Log writers fire on every scan, including
  clean scans (so the audit trail proves the scanner ran).
- **Prompt-hook wiring (R8 / SDD-020).** Add one new instruction line
  to `.github/prompts/triage.prompt.md` and one to
  `.github/prompts/clarify.prompt.md` that tells the agent to invoke
  `python spec-driven-development/cli/dedup.py scan --scope all` before
  proceeding and to act on the tiered output (HARD = stop, SOFT =
  surface to owner, ADVISORY = note and continue). Edits are minimal
  (one numbered list item per prompt) and verifiable by a markdown lint
  test.

## Goal

Close all four deferred LOCKED REQUIRED validation items in a single
implementation pass, with implementation that matches the parent-spec
CLARIFY answers verbatim. After this spec is DONE:

- `cli/fleet.py lock status` shows queue contents ordered priority +
  FIFO.
- Pre-existing in-flight features are grandfathered (no surprise
  blocks).
- Every run of `cli/dedup.py scan` writes three log artifacts.
- `/triage` and `/clarify` automatically invoke the dedup scanner.

## Acceptance Criteria

Each criterion below is a one-line success definition that traces to
one of the four deferred R-items and to a completion task ID
(`T-032-NN`). Detailed test names live in `validation.md`.

1. **AC-1 (closes SDD-019.R7).** Given two or more features queued for
   the same locked phase, when the lock holder releases, then the next
   acquirer is the queued feature with the highest BACKLOG priority,
   breaking ties by submission timestamp (FIFO). Task: T-032-01.
2. **AC-2 (closes SDD-019.R8).** Given a spec dir whose CLARIFY or
   SPEC frontmatter `updated` date predates the Article XI ratification
   commit (`524872b`, 2026-06-08), when the lock scanner runs, then
   the spec dir is treated as a grandfathered lock holder and is not
   retroactively blocked. On its next post-cutover edit, it claims the
   lock if free or queues if held. Task: T-032-02.
3. **AC-3 (closes SDD-020.R6).** Given any invocation of
   `cli/dedup.py scan` (clean, HARD, SOFT, or ADVISORY), when the scan
   completes, then exactly three log artifacts are produced: (a) a
   `dedup_scan_run` ledger row and one `dedup_overlap_flagged` ledger
   row per overlap; (b) a `dedup-scan.md` file in each candidate spec
   dir that was flagged in a spec-bound overlap; (c) a one-line append
   to `backlog/DEDUP-LOG.md`. Task: T-032-03.
4. **AC-4a (closes SDD-020.R8, /triage half).** The file
   `.github/prompts/triage.prompt.md` contains a literal instruction to
   invoke `cli/dedup.py scan --scope all` as a pre-step, with explicit
   guidance on how to act on HARD / SOFT / ADVISORY results. Task:
   T-032-04.
5. **AC-4b (closes SDD-020.R8, /clarify half).** Same as AC-4a for
   `.github/prompts/clarify.prompt.md`. Task: T-032-05.
6. **AC-5 (close verification).** Full test suite passes (>= 259
   baseline + new tests; no regression); `schema_lint` exits 0;
   `exec/state.md` regenerates cleanly; all 4 R-items in this spec's
   `validation.md` are checked. Task: T-032-06.

## Affected Modules

| Module / File | Change Type | R-Item |
|---------------|-------------|--------|
| `cli/fleet.py` | Additive: queue ordering helper + grandfather predicate; integrate into existing lock-status / pre-dispatch paths | R7, R8 (SDD-019) |
| `cli/test_fleet.py` | New tests only; existing tests untouched | R7, R8 (SDD-019) |
| `cli/dedup.py` | Additive: 3 log-writer functions + 3 calls from `cmd_scan` | R6 (SDD-020) |
| `cli/test_dedup.py` | New tests only; existing tests untouched | R6 (SDD-020) |
| `.github/prompts/triage.prompt.md` | Minimal edit: one instruction line added | R8 (SDD-020) |
| `.github/prompts/clarify.prompt.md` | Minimal edit: one instruction line added | R8 (SDD-020) |
| `backlog/DEDUP-LOG.md` | New file: rolling log header + first entry | R6 (SDD-020) |

## Data Model Changes

None new beyond what the parent specs already approved.

- **R7 queue ordering** reuses the existing
  `lock_queued` / `lock_acquired` / `lock_released` ledger event types
  approved in SDD-019. Queue state is derived at scan time from
  frontmatter + BACKLOG.md priority lookup; no new persistent table.
- **R8 grandfather** reuses the existing frontmatter `updated` field.
  Cutover comparison is against a single constant in `cli/fleet.py`
  (`ARTICLE_XI_CUTOVER = "2026-06-08"`).
- **R6 log writers** reuse the existing `dedup_scan_run`,
  `dedup_overlap_flagged`, `dedup_decision_recorded` event types
  approved in SDD-020. Per-spec-dir `dedup-scan.md` filename and
  rolling `backlog/DEDUP-LOG.md` path are also pre-approved.

## API Changes

- `cli/fleet.py lock status` output gains a "Queue" section showing
  pending features in priority + FIFO order (additive; existing output
  preserved).
- `cli/dedup.py scan` adds an `--emit-logs` flag that defaults to
  `true`; set `--no-emit-logs` to suppress the three log writes
  (preserves the existing scratch / dry-run path used in tests).

No backward-incompatible changes.

## Test Strategy

Outline (lock at this spec is at scaffold; tests are added during
implementation):

- **Unit (R7)**: queue ordering -- three features queued at mixed
  priorities, FIFO tiebreak on equal priorities, empty-queue case.
- **Unit (R8)**: grandfather detection -- pre-cutover dir not blocked,
  post-cutover dir blocked when lock held, mixed (one pre + one post)
  yields correct outcome.
- **Unit (R6)**: each writer in isolation (ledger row shape, per-spec
  file content, rolling-log append idempotence). Integration: single
  `cmd_scan` run produces all three artifacts.
- **Markdown lint (R8 / SDD-020)**: a new test asserts that both
  prompt files contain the literal substring `cli/dedup.py scan` and
  the tier-action guidance.
- **Regression**: full pytest run >= 259 baseline; `schema_lint` exit 0.

## Validation Contract

The binding validation contract for this feature lives in the sibling
file `validation.md`. It is **LOCKED at scaffold time** (2026-06-09)
per owner direction 2026-06-08 (Option 3 hybrid). No further CLARIFY
round is needed; the contract re-uses the parent-spec answers verbatim.

## Traceability Matrix

| Parent R-Item | Source Spec | Completion Task | This Spec's Validation Row |
|---------------|-------------|-----------------|----------------------------|
| SDD-019.R7 (priority-weighted FIFO queue) | `specs/2026-06-07-serial-clarify-spec-gate/validation.md` | T-032-01 | R1 |
| SDD-019.R8 (grandfather existing-feature migration) | `specs/2026-06-07-serial-clarify-spec-gate/validation.md` | T-032-02 | R2 |
| SDD-020.R6 (triple-destination log writers) | `specs/2026-06-07-cross-feature-dedup/validation.md` | T-032-03 | R3 |
| SDD-020.R8 (prompt hooks at /triage + /clarify) | `specs/2026-06-07-cross-feature-dedup/validation.md` | T-032-04 (triage) + T-032-05 (clarify) | R4 |

## Open Questions

None. All design questions are final in the parent CLARIFY answers
(`specs/2026-06-07-serial-clarify-spec-gate/clarify.md` Q1-Q9 and
`specs/2026-06-07-cross-feature-dedup/clarify.md` Q1-Q7).

> If any ambiguity surfaces during implementation that the parent
> CLARIFY did not resolve, the implementer MUST mark it explicitly
> in this section as **OWNER GUIDANCE REQUIRED** with a one-paragraph
> problem statement, then STOP that line of inquiry. Do not invent an
> answer. As of scaffold (2026-06-09), no such ambiguity has been
> identified.

## Out of Scope

- **SDD-027.R12 docs gap** (now SDD-033, P3 docs polish). Filed
  separately at Sprint 6 close per owner direction.
- **Any new CLARIFY questions.** This is an implementation-only
  completion bundle. Re-opening CLARIFY would void the Option 3 hybrid
  ratification.
- **Any change to Article XI text or `constitution/principles.md`.**
  Article XI is final at version 1.2.0 (ratified Sprint 6).
- **Any change to the parent CLARIFY answers** in
  `specs/2026-06-07-serial-clarify-spec-gate/clarify.md` or
  `specs/2026-06-07-cross-feature-dedup/clarify.md`. The parent files
  are historical record; this spec adds new behavior, it does not
  rewrite the past.
- **Any change to the parent validation files.** The parent
  `validation.md` files keep their deferred markers as historical
  record. The DONE-WITH-DEFERRED note in `backlog/BACKLOG.md` (rows
  for SDD-019 and SDD-020) traces them to SDD-032. This new
  `validation.md` is the authoritative completion check for the four
  R-items.
- **LLM-based dedup, auto-merge, multi-repo dedup, cross-PI queue.**
  All out of scope per parent CLARIFY answers and re-affirmed here.

## Cross-Feature Notes

- **SDD-018 (UI Lifecycle Variant)** opens in Sprint 7 F-10/F-11. It
  will exercise both the serial gate (Article XI) and the dedup pass
  during its own /clarify and /spec rounds. SDD-032 MUST close before
  SDD-018 opens, so that SDD-018 does not get caught in the
  undefined-queue / undefined-grandfather state.
- **Sprint 6 lock surface** is protected. The lock scanner
  (`_scan_lock_state`, commit `524872b`) and the dedup core
  (`find_overlaps` / `load_corpus` / `handle_overlaps`, commit
  `8eb564d`) are NOT modified. See `plan.md` "Lock-Surface Protections"
  for the full DO-NOT-EDIT list.
