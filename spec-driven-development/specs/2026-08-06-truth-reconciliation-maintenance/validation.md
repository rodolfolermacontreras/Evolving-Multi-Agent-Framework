---
id: MAINT-2026-08-06-TRUTH-RECONCILIATION-validation
type: validation
status: active
owner: principal-architect
updated: 2026-08-06
feature: 2026-08-06-truth-reconciliation-maintenance
status_note: LOCKED at SPEC gate 2026-08-06 before implementation
---

# VALIDATION: Truth Reconciliation Maintenance

- Maintenance ID: `MAINT-2026-08-06-TRUTH-RECONCILIATION`
- Contract status: **LOCKED 2026-08-06 AT SPEC GATE**
- PI / sprint: none
- Required items: 29
- Optional items: 0

This contract is locked before implementation under Article X. Implementation
MUST satisfy every REQUIRED item. No required item may be removed, weakened,
reclassified as optional, or checked without concrete evidence. A discovered
gap may be added only as an append-only architect delta that sharpens the
contract; a scope increase requiring owner approval stops the maintenance gate.

**Count audit -- 2026-08-06:** The approved plan recorded the original locked
baseline of 18 required items. Append-only architect deltas V-19 through V-29
expanded the current validation contract by 11 items, so the truthful current
total is 29 required items. This arithmetic correction changes no requirement,
evidence obligation, or historical planning intent.

---

## Required items (LOCKED)

### Product and historical truth

- [x] **V-01 (backlog truth and RICE preservation).** Authoritative backlog rows
  show the exact AC-TR-01 terminal dispositions; SDD-008 and SDD-059 remain
  unscheduled; before/after comparison proves every existing RICE field is
  unchanged and no score was invented. Covers TR-01, TR-02; AC-TR-01,
  AC-TR-03; TAC-01.

- [x] **V-02 (terminal backlog excluded from Sprint Plan).** Focused tests seed
  shipped/done, archived, superseded, historical/retired, and abandoned backlog
  rows with stale sprint values and prove none enters rendered Sprint Plan.
  A non-terminal scheduled row remains visible as a regression control. Covers
  TR-02, TR-04, TR-05; AC-TR-01, AC-TR-04; TAC-01, TAC-04.

- [x] **V-03 (terminal backlog excluded from QUEUED).** Focused tests seed P1-P3
  terminal backlog rows and prove none enters work-index QUEUED. SDD-008 and
  SDD-059 may appear only as unscheduled candidates and must not be described as
  scheduled or authorized. Covers TR-01, TR-02, TR-04; AC-TR-01, AC-TR-03;
  TAC-01.

- [x] **V-04 (SDD-035 abandoned, never done).** SDD-035 spec and validation
  remain present and explicitly ABANDONED / HISTORICAL. Resolver and build tests
  prove it is neither DONE nor IN-FLIGHT. Covers TR-03, TR-05; AC-TR-02;
  TAC-02.

- [x] **V-05 (SDD-035 evidence integrity).** Diff review proves pre-existing
  checked SDD-035 items remain checked, unchecked items remain unchecked, no
  artifact is deleted, and fresh owner authorization remains mandatory for any
  future Azure cleanup. Covers TR-03, TR-09; AC-TR-02; TAC-02, TAC-09.

### Shared resolver and generated semantics

- [x] **V-06 (all-closed means zero active).** Focused data and build tests seed
  an all-closed roadmap, no active `CURRENT_PI.md`, terminal old features, and
  old sprint artifacts. They prove no active PI, no current sprint, no active
  focus, and no IN-FLIGHT row; rendered output says `No active PI`. Covers
  TR-04, TR-05; AC-TR-04, AC-TR-05; TAC-03.

- [x] **V-07 (terminal status outside spec.md respected).** Focused fixtures put
  terminal frontmatter or explicit disposition in supported feature artifacts
  outside `spec.md`, including a missing or stale `spec.md`. The shared resolver
  respects that terminal evidence and never classifies the directory as
  operational. Contradictory terminal evidence follows the documented
  deterministic conservative rule. Covers TR-04, TR-05; AC-TR-04; TAC-04.

- [x] **V-08 (single shared predicate/resolver).** Structural inspection proves
  feature detection, Sprint Plan selection, and work-index IN-FLIGHT/QUEUED
  selection consume one status-normalization/terminal-classification contract
  owned by `state_builder_data.py`. No duplicate ad hoc terminal substring list
  exists in either renderer. Covers TR-04; AC-TR-04; TAC-04.

- [x] **V-09 (active PI regression preserved).** Existing and focused fixtures
  with a valid active roadmap PI plus active `CURRENT_PI.md` still resolve and
  render that PI and its sprint as active. Supported explicit override behavior
  remains green. Covers TR-05; AC-TR-04; TAC-03.

### Current hand-authored surfaces and lint

- [x] **V-10 (current operating documents agree).**
  `docs/HIGH_LEVEL_DEV_TRACKER.md`, the leading checkpoint of
  `sessions/SESSION-MEMORY.md`, and the current pipeline section of
  `docs/ONBOARDING_KICK_OFF.md` state no active PI, sprint, feature, or scheduled
  work and point to authoritative sources. Historical body sections are
  preserved where feasible and clearly historical. Covers TR-06; AC-TR-05;
  TAC-05.

- [x] **V-11 (leadership brief is dated capability evidence).**
  `docs/LEADERSHIP-ONE-PAGER.html` carries a 2026-08-06 evidence date and contains
  no PI-10 active, `Now building`, active SDD-068, or no-feature-scheduled
  contradiction. SDD-060 through SDD-067 are absent as product IDs; retained
  ideas, if any, are untriaged concept themes with an explicit no-authority
  statement. SDD-059 remains unscheduled. Covers TR-01, TR-06; AC-TR-05,
  AC-TR-06; TAC-05, TAC-06.

- [x] **V-12 (leadership false claims caught).** Focused stale-doc tests prove
  the guard fails for each leadership defect independently: false PI active,
  `Now building` during zero-active state, active SDD-068, and unauthorized
  SDD-060 through SDD-067 product labels. Covers TR-07; AC-TR-06, AC-TR-07;
  TAC-07.

- [x] **V-13 (zero-active current claims caught).** Focused stale-doc tests prove
  a current PI or equivalent active-state assertion is rejected when live source
  records have no active PI, including the leadership one-pager as a bounded
  scan target. Covers TR-07; AC-TR-06, AC-TR-07; TAC-07.

- [x] **V-14 (lint remains narrow and compatible).** Existing article-count,
  roman-range, current-PI, marker-exemption, missing-doc, scope, CLI-exit, and
  stdlib-only stale-doc tests remain green. Structural review proves no broad
  arbitrary-prose scan or third-party dependency was added. Covers TR-07,
  TR-09; AC-TR-07; TAC-07, TAC-09.

### Rebuild, locks, and final scope

- [x] **V-15 (source and focused tests precede rebuild).** Durable execution
  evidence records this order: authoritative source corrections; RED/GREEN
  focused state-builder and stale-doc tests; schema/structural checks; maintenance
  artifact closure; state-builder rebuild. No generated artifact changes appear
  before the successful source/test gate. Covers TR-08; AC-TR-04, AC-TR-08;
  TAC-08.

- [x] **V-16 (generated artifacts free of false claims).** After the sole
  state-builder rebuild, `exec/state.md`, `exec/state.html`, and
  `exec/work-index.md` contain no PI-10 active, SDD-060 through SDD-068 product
  or active claim, current sprint, active product feature, terminal IN-FLIGHT,
  terminal Sprint Plan, or terminal QUEUED row. They explicitly represent no
  active PI and no work in flight. Covers TR-05, TR-08; AC-TR-04, AC-TR-08;
  TAC-03, TAC-08.

- [x] **V-17 (generated ownership and repository checks).** Diff review proves
  all three generated files changed only as one coherent state-builder output;
  no manual-only edit is present. Focused and repository schema lint, artifact
  structural checks, stale-doc lint, and `git diff --check` all exit 0. Covers
  TR-08, TR-09; AC-TR-08, AC-TR-09; TAC-08, TAC-09.

- [x] **V-18 (Article X and scope boundary).**
  `TestS1FootprintLockGuard` proves `render_html`, `load_sprint_table`,
  `load_sprint_goal`, `detect_current_sprint`, and `load_decisions` are
  byte-identical to their locked hashes. Final status/diff proves no Azure
  operation evidence, PI/sprint creation, SDD assignment, SDD-059 scheduling,
  setup-repair behavior change, product feature implementation, constitution
  edit, new dependency, historical deletion, commit, push, or merge. Covers
  TR-01, TR-09; AC-TR-02, AC-TR-09; TAC-02, TAC-09.

- [x] **V-19 (owning artifact allowlist and precedence).** Focused tests prove
  that normal `spec.md`, a single lightweight artifact with frontmatter
  `type: feature`, design-only legacy `DESIGN.md`, and task-only legacy
  `tasks.md` are the only lifecycle owners in that order. `validation*.md` may
  provide only a non-operational override; clarification, plan, retro,
  security, provisioning, reference, and arbitrary Markdown statuses are
  ignored. Non-operational evidence wins over review, review wins over owning
  done/shipped, then validation/stage inference and file presence apply.

- [ ] **V-20 (review and integration lifecycle).** The maintenance spec remains
  `status: active` with `lifecycle_status: review`; tasks and validation remain
  active; generated outputs classify the package as REVIEW and never Already
  shipped. Owning completion is not asserted before the later commit and
  integration gate, and independent Stage 2 re-review remains pending.

- [x] **V-21 (bounded lifecycle and leadership negation).** Focused tests prove
  frontmatter precedes body lifecycle metadata, body metadata is accepted only
  from bounded initial full lines, status terms must begin the value with a
  bounded suffix, and negated/reopened/reactivated/pending-review/changes-
  required/blocked values cannot complete work. Leadership active assertions
  are evaluated candidate-by-clause: same-clause negations are suppressed while
  a later positive clause is still detected.

- [x] **V-22 (Markdown lifecycle presentation normalization).** Supported
  lifecycle metadata and backlog Status values trim and repeatedly unwrap only
  matching leading Markdown emphasis/code spans while preserving following
  text. Comparison collapses whitespace, lowercases, and accepts bounded
  `.`, `!`, and `?` suffixes. Real `**DONE.**` and
  `**SUPERSEDED / HISTORICAL.**` backlog rows are excluded from Sprint Plan and
  QUEUED, while `Work is **DONE.**` remains nonterminal.

- [x] **V-23 (ordered metadata winner and display determinism).** Lifecycle
  fields are traversed in the fixed order `lifecycle_disposition`,
  `lifecycle_status`, `disposition`, `status`, with repeated values retaining
  document order. Semantic precedence remains validation non-operational,
  owning non-operational, owning review, owning completed, then fallback; the
  winning value is displayed. `status: active` plus `lifecycle_status: review`
  resolves exactly to REVIEW / `review` under three `PYTHONHASHSEED` values.

- [x] **V-24 (bounded HTML visible-text active-PI lint).** Leadership active-PI
  checks use stdlib `HTMLParser(convert_charrefs=True)`, ignore comments,
  attributes, script, and style content, retain inline text continuity, and
  create boundaries for supported block tags. Candidate and negation checks run
  independently per punctuation/block clause. Focused tests cover marked-up
  positives and negations, adjacent blocks, later positives, hidden noise, and
  conservative findings at 64 KiB input, 16 KiB visible text, and 512 clauses.

- [ ] **V-25 (REVIEW lifecycle and closure contract).** The package remains
  `status: active` and `lifecycle_status: review` through T-TR-15/V-20.
  APPROVED means independent review approval awaiting separately
  owner-authorized integration, not DONE. Terminal metadata may be applied only
  at the closure gate after Stage 2 approval and authorized integration, then
  the builder must run before DONE.

- [x] **V-26 (commit-semantic HTML parity).** Markdown state and work index
  match no-write renders exactly. HTML differs only at the three documented
  `generated_at` sites. COMMIT relative times may be normalized only after the
  ordered commit SHA identities and subjects match exactly; commit count,
  order, SHA, and subject are never normalized. Generation-basis HEAD is
  recorded and represented in the rebuilt activity feed.

- [x] **V-27 (candidate-local active-PI negation).** Visible-text checks
  independently enumerate `PI-N ... active`, `active PI-N`, and
  `active PI PI-N` candidates. A supported negation suppresses only its local PI
  relation; a remaining positive candidate is a finding. Required plain-text,
  marked-up, both-negated, and existing block-boundary controls pass.

- [x] **V-28 (canonical backlog Notes and dash-RICE parsing).** The canonical
  11-column table is parsed by header position so optional trailing Notes never
  becomes Status. `--` RICE is accepted and preserved. Real-source tests load
  SDD-035, SDD-008, and SDD-059 with correct status, schedule, and terminal
  exclusion semantics while preserving the `BacklogItem` API.

- [x] **V-29 (anchored Markdown terminal presentation and real-source oracle).**
  Approved Markdown presentation delimiters are recognized only at character
  zero around a complete leading terminal term with balanced matching closes.
  Exact regression, malformed/prose controls, real SDD-036 exclusion, an
  independently constructed canonical-source oracle, complete focused suites,
  repository gates, builder-only regeneration, semantic parity, and one full
  doctor run must pass before this item and T-TR-20 are complete.

---

## Pre-rebuild evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-01 | HEAD/current comparison: 56 backlog rows retained identical Priority, Reach, Impact, Confidence, Effort, and RICE fields; SDD-008 remains 0.26 and unscheduled; no score was added. |
| V-02, V-03 | Truth-reconciliation state-builder selector: 31 passed, 294 deselected. Six terminal variants were excluded independently from Sprint Plan and QUEUED with non-terminal controls retained. |
| V-04, V-05 | Explicit SDD-035 build test passed. HEAD/current integrity probe: 8 files preserved and validation checkbox counts remain exactly 4 checked / 19 unchecked; fresh authorization language present. |
| V-06, V-07, V-09 | Truth-reconciliation selector passed all-closed, outside-spec terminal evidence, conflict-conservative, missing-spec, zero-focus, and active-PI control tests. |
| V-08 | Structural ownership test passed: both renderers consume `is_terminal_status`; terminal vocabularies remain owned by `state_builder_data.py`. |
| V-10, V-11 | Current-surface assertion passed: tracker, leading session checkpoint, onboarding, and leadership brief state zero active; brief dated 2026-08-06, retains SDD-059 unscheduled, contains no PI-10, `Now building`, or SDD-060..068 label. |
| V-12, V-13 | Focused leadership lint selector: 6 passed, 13 deselected after RED was 4 failed / 2 passed. Each forbidden defect fails independently; clean-control and missing-doc cases pass. |
| V-14 | Complete stale-doc suite: 19 passed. `staledoc_lint.py --root spec-driven-development` clean. No third-party import or broad arbitrary-prose rule added. |
| V-15 | Durable order: baseline 1118 passed / 5 skipped; state-builder RED then GREEN; renderer RED then GREEN; leadership lint RED then GREEN; full state-builder 325 passed; full stale-doc 19 passed; focused/repository schema, origin, governance, stale-doc, Article X, source-integrity, and generated-ownership checks all passed before this closure. Pre-rebuild generated ownership probe confirmed none of the three generated outputs changed. |

Additional pre-rebuild gates: focused schema lint is clean for the maintenance,
SDD-035, and retro-closure directories; repository schema lint is clean;
origin lint is clean with tracked-database check; governance is clean from the
repository root; `TestS1FootprintLockGuard` passed 3/3; `git diff --check`
passed; pre-rebuild name-status contains modifications only and no generated
executive file.

### Architect Stage 2 repair evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-19 | Architect-focused RED selector: 20 failed / 34 passed before production repair. The same owning-artifact, arbitrary-Markdown, validation-override, review-veto, conflict-precedence, and historical-compatibility selector is GREEN as part of 54 passed. |
| V-21 | The same focused GREEN includes frontmatter-first, bounded initial body metadata, anchored status term, negated/reopened/reactivated/blocked status, same-clause leadership negation, and later-positive mixed-clause cases. Complete state-builder suite: 355 passed. Complete stale-doc suite: 23 passed. |
| Pre-rebuild gate | Focused maintenance schema clean; repository schema, origin, governance, and stale-doc checks clean; Article X exact lock 3 passed; full framework suite 1201 passed / 5 skipped; editor diagnostics clean; `git diff --check` clean. |

---

### Final local repair evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-22 | RED: lifecycle/backlog selector finished 6 failed / 59 passed. Failures were the four formatted lifecycle cases, exact REVIEW display under hash-seed subprocesses, and real Markdown backlog exclusion. GREEN: complete focused state-builder plus stale-doc files passed 394/394. Real SDD-001 and SDD-002 rows are absent from generated Sprint Plan and QUEUED; arbitrary `Work is **DONE.**` remains nonterminal. |
| V-23 | Three subprocesses with `PYTHONHASHSEED` 1, 7, and 29 each returned exactly `["REVIEW", "review", "owning artifact review veto"]`. The maintenance row renders REVIEW / `review` and is absent from Already shipped. |
| V-24 | RED: leadership selector finished 6 failed / 12 passed for marked-up positives, later positive, hidden noise, and overflow behavior. GREEN: 18/18 leadership tests. Repository-compatible conservative bounds are 64 KiB HTML input, 16 KiB visible text, and 512 clauses; the real page measures 51,240 characters, 13,799 visible characters, and 386 clauses. |
| Pre-rebuild gate | Maintenance and repository schema lint, origin with tracked-database guard, governance, stale-doc, TDD gate, and `git diff --check` all exited 0; exact S1 footprint lock passed 3/3. The builder then ran once and wrote only the three executive outputs. |
| Generated assertions | PI is `None`; `No active PI`, `No feature scheduled`, and `Nothing in flight` are truthful. SDD-001/002 are absent from Sprint Plan and QUEUED. Markdown and work-index no-write output match byte-for-byte; HTML matches after only the documented generated-time and COMMIT-relative-time normalization. |
| Full doctor | One `bootstrap.py doctor` run passed every check: 1217 tests passed, 5 skipped in 386.09s; tracked databases, ledger, schema, governance, origin, stale-doc, TDD, and zero-active DONE completeness all passed. |

### Architect second repair pass evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-27 | RED selector: 2 failed / 1 passed. Both mixed positive/negative directions failed while the both-negated control passed. GREEN: exact selector 3/3; complete stale-doc file 34/34. Plain-text, marked-up, `PI-N ... active`, `active PI-N`, and `active PI PI-N` relations are candidate-local. |
| V-28 | RED selector: 2 failed. The canonical fixture loaded zero rows and real SDD-035/SDD-059 were absent. GREEN: exact selector 2/2; complete state-builder file 365/365. Header-position parsing preserves `--` RICE, reads Status before optional Notes, and real SDD-035/008/059 load with correct terminal/unscheduled semantics. |
| Pre-rebuild gates | Focused and repository schema lint, origin with tracked-database guard, governance, stale-doc, TDD gate, exact Article X lock 3/3, and `git diff --check` passed. Editor diagnostics reported no errors in the four touched code/test files. |
| V-26 | `state.md` and `work-index.md` matched no-write output byte-for-byte. HTML matched after only the three documented `generated_at` sites and COMMIT relative-time normalization, performed only after all 10 ordered SHA+subject pairs matched exactly. Generation basis `6bd215c` with subject `fix: restore fresh-clone setup contract` is present in the feed. |
| Generated truth | PI is `None`; generated state says `No active PI` and `No feature scheduled`; work-index says `Nothing in flight`. The maintenance renders REVIEW / `review`, is absent from Already shipped, and retains ACTIVE / REVIEW source metadata. |
| Full doctor | The single second-pass `bootstrap.py doctor` run passed every check: 1222 tests passed, 5 skipped in 366.81s; tracked databases, ledger, schema, governance, origin, stale-doc, TDD, and zero-active DONE completeness all passed. |

### Sole remaining local Stage 2 repair evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-29 RED/GREEN | Exact RED selector: 3 failed / 14 passed. Failures were the leading-whitespace control, real SDD-036 terminal recognition/exclusion, and independent source-oracle predicate agreement. Exact GREEN selector: 17/17. The complete focused `test_state_builder.py` plus `test_staledoc_lint.py` files passed 416/416 after retaining real SDD-035 compatibility. |
| V-29 grammar | Only `**`, `__`, `*`, `_`, and backtick presentation at character zero are normalized. A complete leading terminal term, balanced reverse-order closing delimiters, and an existing boundary are required. Prose prefixes, links, HTML, fused DONEish, leading whitespace, and mismatched/unclosed wrappers remain nonterminal. |
| V-29 oracle | The independent canonical-source oracle does not call `is_terminal_status` to build expectations. It found 33 terminal IDs including SDD-036; every oracle ID satisfies the shared predicate and both Sprint Plan and QUEUED intersections are empty. |
| Gates and parity | Maintenance/repository schema, origin plus tracked-database, governance, stale-doc, TDD, `git diff --check`, and Article X 3/3 passed. PI is `None`; maintenance is REVIEW / `review`; zero-active state is truthful. Markdown and work-index match no-write output exactly. All 10 ordered COMMIT SHA+subject pairs match before HTML comparison; HTML matches after only documented generated times and COMMIT-relative times are normalized. Required basis `6bd215c` / `fix: restore fresh-clone setup contract` is present. |
| Full doctor | The single T-TR-20 `bootstrap.py doctor` run passed every check: 1239 tests passed, 5 skipped in 369.35s; tracked databases, ledger, schema, governance, origin, stale-doc, TDD, and zero-active DONE completeness all passed. |

### Independent Stage 2 verdict -- 2026-08-06

| Review | Concrete evidence |
|--------|-------------------|
| Verdict | **APPROVED** with zero CRITICAL and zero IMPORTANT findings. The independent reviewer explicitly authorized marking T-TR-15 Stage 2 approved. |
| Focused evidence | Exact V-29 selector passed 17/17; focused artifact suites passed 416/416; exact Article X lock passed 3/3. |
| Repository evidence | `bootstrap.py doctor --skip-tests` was green; generated parity was exact/semantic as defined; `git diff --check` was clean; the recorded full doctor passed 1239 tests with 5 skipped. |
| Disposition | T-TR-15 is complete. The package is ready only for an owner decision on a local review-approved commit. No push, merge, integration, terminal metadata, closure, or DONE authority is implied. |

V-20 and V-25 remain pending until separately owner-authorized integration and
closure. The package remains ACTIVE / REVIEW; no commit, integration, terminal
metadata, or DONE claim is recorded.

---

## Post-rebuild evidence -- 2026-08-06

| Validation | Concrete evidence |
|------------|-------------------|
| V-16 | The sole `state_builder.py` write exited 0 and reported PI `None`, 47 features, and all three executive outputs written. Generated-content assertions passed across all three files: `No active PI`, `No feature scheduled`, and `Nothing in flight` are present; PI-10 and SDD-060..068 are absent; Sprint Plan has no SDD row; IN-FLIGHT is empty; terminal QUEUED controls are absent. |
| V-17 | Generated-scope name-status contains exactly the three modified executive outputs. A focused regression first failed because `generated_at`-only normalization left the COMMIT activity timestamp difference (`11 hours ago` versus `12 hours ago`), then passed after the comparison helper was narrowed to the documented volatile fields. A read-only current-file probe confirms normal no-write builds match written Markdown and work index byte-for-byte. HTML matches after normalizing only `generated_at` in the title, freshness div, and footer plus numeric Git `%cr` text in `<span class="when">` nodes immediately followed by the exact COMMIT badge; a scope guard proves dispatch timestamps, commit descriptions, and relative-looking prose remain compared. Repeated no-write output is deterministic under that same normalization. Focused helper evidence: 2 passed, 325 deselected; current-file parity probe: PASS. Final repository schema, origin plus tracked-database, governance, stale-doc, and `git diff --check` commands exit 0. |
| V-18 | Exact `TestS1FootprintLockGuard`: 3 passed. Final full CLI suite: 1157 passed, 5 skipped. CI doctor with tests skipped after the full suite: all applicable checks passed. Workspace diagnostics: no errors. Final name-status contains modifications plus the new maintenance directory and no deletion; protected constitution, PI/sprint, workflow, setup-repair, and transaction paths have zero diff. Branch remains `fix/fresh-clone-setup-contract`; work remains uncommitted. No Azure operation, PI/sprint creation, SDD assignment, SDD-059 scheduling, dependency, commit, push, merge, or historical deletion occurred. |

During final doctor validation, the bounded leadership regex misclassified the
truthful same-line footer `PI-9 closed ...; no active PI`. A precise regression
was added RED, the negated phrase was excluded locally, and the resulting
leadership class passed 7/7, stale-doc suite 20/20, exact doctor regression 1/1,
real-root stale-doc lint clean, and final full suite: 1157 passed, 5 skipped.

---

## Required command evidence

The implementation plan may refine exact selectors but MUST preserve these
validation classes and order:

1. Focused state-builder tests for V-02, V-03, V-04, V-06, V-07, V-08, V-09,
   V-16, and V-18.
2. Focused stale-doc tests for V-12, V-13, and V-14.
3. Focused schema lint on this maintenance directory, then repository schema
   lint.
4. Artifact/frontmatter structural checks for the maintenance and changed
   historical feature directories.
5. Stale-doc lint against the repository.
6. `TestS1FootprintLockGuard` by exact test selector.
7. State-builder run only after steps 1-6 pass.
8. Generated-content assertions and deterministic no-write/build comparison.
9. `git diff --check`, `git status --short --branch`, `git diff --stat`, and
   `git diff --name-only` for final scope review.

All Python commands MUST use the repository `.venv` interpreter. Test evidence
must report actual pass/fail counts and exit codes, not predicted outcomes.

## Traceability completeness

| Product AC | Required validation IDs |
|------------|-------------------------|
| AC-TR-01 | V-01, V-02, V-03 |
| AC-TR-02 | V-04, V-05, V-18 |
| AC-TR-03 | V-01, V-03 |
| AC-TR-04 | V-06, V-07, V-08, V-09, V-15, V-16 |
| AC-TR-05 | V-06, V-10, V-11 |
| AC-TR-06 | V-11, V-12, V-13 |
| AC-TR-07 | V-12, V-13, V-14 |
| AC-TR-08 | V-15, V-16, V-17 |
| AC-TR-09 | V-17, V-18 |

Every AC-TR-01 through AC-TR-09 has technical requirements in `spec.md` and at
least two locked validation paths here. No acceptance criterion is deferred.

## ADR and constitution gate

- ADR required: **No.** ADR-027 already governs the zero-active architecture.
- Constitution edit required: **No.** ADR-027 already amended the roadmap
  contract; this package is corrective propagation.
- New owner gate required: **No**, provided implementation stays within this
  locked scope. Any new dependency, schema enum, constitution edit, Azure action,
  PI/sprint creation, or product identifier requires a stop and fresh approval.

## Lock disposition

**LOCKED: 29 REQUIRED, 0 OPTIONAL, 0 UNRESOLVED.** The Software Developer may
plan and implement only against this frozen set. Completion requires all 29
items checked with evidence; inability to satisfy one item blocks closure rather
than permitting silent deferral.