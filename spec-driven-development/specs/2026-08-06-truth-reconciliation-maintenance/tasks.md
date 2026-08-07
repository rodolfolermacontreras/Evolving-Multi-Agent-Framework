---
id: MAINT-2026-08-06-TRUTH-RECONCILIATION-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-08-06
feature: 2026-08-06-truth-reconciliation-maintenance
---

# TASKS: Truth Reconciliation Maintenance

- Spec: [`spec.md`](./spec.md) -- APPROVED
- Plan: [`plan.md`](./plan.md)
- Validation: [`validation.md`](./validation.md) -- LOCKED
- Rule: direct file scope is an allowlist; generated files are builder-owned.

---

## Atomic Tasks

| Task | Tags | Description | Files | Depends on | Verification | Status |
|------|------|-------------|-------|------------|--------------|--------|
| T-TR-01 | [S][AFK] | Capture baseline, authorized dirty scope, SDD-035 checkbox/file inventory, backlog RICE values, and Article X hashes. | `tasks.md`, `validation.md` | none | Baseline and immutable evidence recorded | done |
| T-TR-02 | [S][AFK] | Add RED regressions for shared terminal feature/backlog semantics, evidence outside `spec.md`, zero-active behavior, active-PI compatibility, and generated exclusions. | `cli/test_state_builder.py` | T-TR-01 | Focused selector fails only for missing TR behavior | done |
| T-TR-03 | [S][AFK] | Implement shared normalization, terminal classification, artifact resolution, and zero-active feature/focus semantics. | `cli/state_builder_data.py`, `cli/test_state_builder.py` | T-TR-02 | Same focused selector passes immediately | done |
| T-TR-04 | [S][AFK] | Consume the shared predicate for Sprint Plan and work-index IN-FLIGHT/QUEUED without local terminal lists. | `cli/state_builder_markdown.py`, `cli/state_builder_html.py`, `cli/test_state_builder.py` | T-TR-03 | Renderer-focused tests and structural assertion pass | done |
| T-TR-05 | [S][AFK] | Add RED tests for false leadership PI/work/ID claims and zero-active current claims while retaining existing exemptions and guard behavior. | `cli/test_staledoc_lint.py` | T-TR-01 | Focused lint selector fails for intended missing checks | done |
| T-TR-06 | [S][AFK] | Extend bounded stale-doc scanning for the leadership brief and exact unauthorized claims. | `cli/staledoc_lint.py`, `cli/test_staledoc_lint.py` | T-TR-05 | Same focused lint selector passes immediately | done |
| T-TR-07 | [P][AFK] | Refresh current tracker and onboarding current-state guidance with zero-active authoritative pointers. | `docs/HIGH_LEVEL_DEV_TRACKER.md`, `docs/ONBOARDING_KICK_OFF.md` | T-TR-03 | V-10 content assertions and lint pass | done |
| T-TR-08 | [P][AFK] | Replace the leading session checkpoint while preserving older history; convert leadership page to dated capability evidence. | `sessions/SESSION-MEMORY.md`, `docs/LEADERSHIP-ONE-PAGER.html` | T-TR-03 | V-10/V-11 assertions and lint pass | done |
| T-TR-09 | [S][AFK] | Reconcile only spec-required old lifecycle metadata, including retro-closure row status where present; preserve SDD-035 evidence. | `specs/2026-06-08-azure-decommission/spec.md`, `specs/2026-06-08-azure-decommission/validation.md`, `backlog/BACKLOG.md` | T-TR-01 | V-01/V-04/V-05 comparisons pass | done |
| T-TR-10 | [S][AFK] | Run focused suites, schema/origin/governance/stale-doc checks, structural checks, and exact Article X lock; repair only local defects. | `tasks.md`, `validation.md` | T-TR-04, T-TR-06, T-TR-07, T-TR-08, T-TR-09 | All pre-rebuild checks exit 0 | done |
| T-TR-11 | [S][AFK] | Record implementation evidence and move maintenance lifecycle metadata to review-ready terminal state without changing locked requirements. | `clarification.md`, `spec.md`, `validation.md` | T-TR-10 | Schema lint passes; all 18 items have concrete evidence | done |
| T-TR-12 | [S][AFK] | Execute the sole builder-owned rebuild of all executive outputs. | `exec/state.md`, `exec/state.html`, `exec/work-index.md` | T-TR-11 | Builder exits 0; deterministic no-write comparison matches | done |
| T-TR-13 | [S][AFK] | Run generated truth assertions, deterministic no-write parity, full doctor/tests, diff/scope checks, and editor diagnostics; for HTML parity normalize only the three `generated_at` render sites and numeric Git `%cr` text in COMMIT activity `when` nodes; prepare but do not self-approve both reviews. | `cli/test_state_builder.py`, `tasks.md`, `validation.md` | T-TR-12 | V-01..V-18 complete; Markdown/work-index match byte-for-byte; HTML structure and product-state content match after only the documented volatile-field normalization; no forbidden action or file | done |
| T-TR-14 | [S][AFK] | Implement the Architect-adjudicated owning-artifact precedence, bounded lifecycle parsing, review veto, and leadership same-clause negation repairs test-first. | `cli/state_builder_data.py`, `cli/staledoc_lint.py`, focused tests | T-TR-13 | Architect-listed RED cases fail before production edits, then the same selector passes | done |
| T-TR-20 | [S][AFK] | Implement the sole remaining Stage 2 Markdown terminal-presentation repair test-first, prove real SDD-036 and an independent real-source oracle are absent from Sprint Plan and QUEUED, rebuild builder-owned outputs, and rerun all required gates at HEAD `6bd215c`. | `cli/state_builder_data.py`, `cli/test_state_builder.py`, generated outputs, `tasks.md`, `validation.md` | T-TR-19 | V-29 passes with exact RED/GREEN, oracle, parity, doctor, and scope evidence | done |
| T-TR-15 | [S][HITL] | Perform independent Stage 2 re-review after all repair evidence and generated REVIEW outputs are current. | repair diff and evidence | T-TR-20 | Independent reviewer records verdict; implementation does not self-approve | done |
| T-TR-16 | [S][AFK] | Implement the final Architect-adjudicated Markdown lifecycle normalization, ordered metadata winner/display precedence, bounded HTML visible-text parsing, and corrected stage documentation test-first. | `cli/state_builder_data.py`, `cli/staledoc_lint.py`, focused tests | T-TR-14 | Required RED cases fail for intended reasons; complete focused files pass | done |
| T-TR-17 | [S][AFK] | Run final pre-rebuild gates, builder-only regeneration, generated truth/parity assertions, and one full bootstrap doctor; preserve REVIEW lifecycle for independent re-review. | generated outputs, `tasks.md`, `validation.md` | T-TR-16 | All required gates and generated assertions pass; doctor is green | done |
| T-TR-18 | [S][AFK] | Implement the second Architect-adjudicated candidate-local negation and canonical backlog parser repairs test-first, including real SDD-035/008/059 source coverage. | `cli/test_staledoc_lint.py`, `cli/staledoc_lint.py`, `cli/test_state_builder.py`, `cli/state_builder_data.py`, `backlog/BACKLOG.md` | T-TR-17 | Exact RED selectors fail for intended defects, then exact selectors and both complete focused files pass | done |
| T-TR-19 | [S][AFK] | Run pre-rebuild gates, builder-only regeneration, lifecycle/truth assertions, and semantic generated-output parity at the recorded HEAD basis; run doctor once. | generated outputs, `tasks.md`, `validation.md` | T-TR-18 | V-25..V-28 and required repository gates pass; generated REVIEW outputs are current | done |

## Dependency Graph

```text
T-TR-01 -> T-TR-02 -> T-TR-03 -> T-TR-04
       \-> T-TR-05 -> T-TR-06
T-TR-03 -> T-TR-07
T-TR-03 -> T-TR-08
T-TR-01 -> T-TR-09
T-TR-04 + T-TR-06..09 -> T-TR-10 -> T-TR-11 -> T-TR-12 -> T-TR-13
T-TR-13 -> T-TR-14 -> T-TR-16 -> T-TR-17 -> T-TR-18 -> T-TR-19 -> T-TR-20 -> T-TR-15
```

T-TR-07 and T-TR-08 are file-disjoint and parallelizable. All implementation in
this invocation remains serial where immediate focused validation is required.

## Checkpoints

- **Checkpoint A:** T-TR-01 through T-TR-04 -- shared semantics GREEN.
- **Checkpoint B:** T-TR-05 through T-TR-09 -- bounded lint/docs/source GREEN.
- **Checkpoint C:** T-TR-10 and T-TR-11 -- all pre-rebuild gates GREEN.
- **Checkpoint D:** T-TR-12 and T-TR-13 -- generated and repository evidence complete.
- **Checkpoint E:** T-TR-16 and T-TR-17 -- final local repair and review-ready evidence complete.
- **Checkpoint F:** T-TR-18 and T-TR-19 -- second adjudicated repair and regenerated review evidence complete before T-TR-15.
- **Checkpoint G:** T-TR-20 -- sole remaining local Stage 2 repair and regenerated review evidence complete before T-TR-15.
- **Checkpoint H:** T-TR-15 -- independent Stage 2 verdict APPROVED with zero CRITICAL and zero IMPORTANT findings; package remains ACTIVE / REVIEW pending separately owner-authorized commit, integration, and closure decisions.
