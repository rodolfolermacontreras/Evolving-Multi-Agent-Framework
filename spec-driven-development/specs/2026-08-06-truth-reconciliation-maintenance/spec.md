---
id: MAINT-2026-08-06-TRUTH-RECONCILIATION-spec
type: spec
status: done
lifecycle_status: done
owner: principal-architect
updated: 2026-08-06
feature: 2026-08-06-truth-reconciliation-maintenance
---

# SPEC: Truth Reconciliation Maintenance

- Maintenance ID: `MAINT-2026-08-06-TRUTH-RECONCILIATION`
- Classification: owner-authorized corrective maintenance between PIs
- PI / sprint: none
- Product gate: closed in [`clarification.md`](clarification.md)
- Validation contract: [`validation.md`](validation.md), LOCKED 2026-08-06
- Governing decision: [`../../docs/ADR/027-between-pi-zero-active-state.md`](../../docs/ADR/027-between-pi-zero-active-state.md)
- Implementation owner: Principal Software Developer after SPEC approval

---

## Problem statement

The repository's authoritative product records, historical feature artifacts,
current operating documents, and generated executive views disagree about what
is active and what has shipped. The roadmap and PI-9 close establish an
owner-ratified between-PI state, but stale feature and backlog classifications
can still enter generated IN-FLIGHT, Sprint Plan, and QUEUED views. A leadership
brief also presents PI-10 and SDD-060 through SDD-068 as authorized work even
though no such authorization exists.

This is a truth-reconciliation defect, not new product work. Correcting only the
prose would leave the generators able to recreate false claims. Correcting only
the generators would leave high-value hand-authored operating surfaces stale.
The maintenance package must therefore repair authoritative source status,
centralize terminal-status interpretation, refresh the bounded current-document
set, add narrow drift detection, and rebuild generated outputs in that order.

## Goals

1. Make authoritative backlog, feature, roadmap, sprint, and current-document
   surfaces agree that no PI, sprint, or product feature is scheduled or active.
2. Preserve terminal lifecycle truth so completed, archived, superseded, and
   abandoned/historical work cannot re-enter operational views.
3. Make status interpretation a shared stdlib-only data-layer responsibility
   consumed by state Markdown and work-index rendering.
4. Preserve SDD-035 as partial historical evidence without claiming completion
   or authorizing future Azure work.
5. Add focused regression protection against the exact leadership and
   zero-active-state drift corrected by this package.

## Source-of-truth hierarchy

When sources disagree, implementation and review MUST apply this precedence:

1. **Owner-ratified governance decisions:** accepted ADRs and recorded owner
   dispositions define authorization and lifecycle semantics. ADR-027 governs
   the zero-active between-PI state; the 2026-08-06 owner disposition governs
   SDD-035 as ABANDONED / HISTORICAL.
2. **Authoritative product and scheduling records:**
   `constitution/roadmap.md`, `backlog/BACKLOG.md`, and
   `sprints/PI-*/CURRENT_PI.md` define active PI, backlog status, and active
   sprint. A document that narrates future work cannot override these records.
3. **Feature lifecycle artifacts:** machine-readable frontmatter and explicit
   lifecycle disposition across a feature directory define whether that work is
   operational or terminal. The resolver must not assume `spec.md` is the only
   status-bearing artifact.
4. **Current hand-authored operating surfaces:** the tracker, leading session
   checkpoint, onboarding current-state section, and dated leadership capability
   brief summarize levels 1-3. They do not create product or scheduling authority.
5. **Generated executive surfaces:** `exec/state.md`, `exec/state.html`, and
   `exec/work-index.md` are derived views only. They MUST be rebuilt by
   `state_builder.py` and MUST NOT be hand-edited.
6. **Frozen historical narrative:** closed prompts, retrospectives, evidence,
   and dated snapshots remain historical evidence. They may retain old claims
   when context makes their historical nature clear and they are not consumed
   as current authority.

The higher source wins. An explicit terminal disposition at levels 1-3 MUST NOT
be overridden by unchecked validation items, artifact-presence inference, stale
prose, or generated output.

## Status semantics

### Terminal feature statuses

The shared resolver MUST recognize these semantic terminal classes without
adding a new schema enum:

- `done` and `shipped`: completed terminal work; eligible for DONE history.
- `archived`: terminal non-operational work; never IN-FLIGHT.
- `superseded`: terminal replaced work; never IN-FLIGHT.
- `abandoned/historical`, including equivalent explicit wording in an existing
  status or disposition field: terminal incomplete history; never DONE and never
  IN-FLIGHT.

For an abandoned/historical directory, checked validation evidence remains
checked and unchecked items remain unchecked. Validation completeness MUST NOT
convert that disposition to DONE. Any future SDD-035 Azure cleanup requires new,
explicit owner authorization and a separately established execution scope.

The resolver MUST inspect supported frontmatter or explicit lifecycle
disposition outside `spec.md` when `spec.md` is absent, stale, or less
authoritative. Conflict handling MUST be deterministic: an explicit terminal
disposition wins over non-terminal inference; contradictory explicit terminal
dispositions MUST be surfaced as a testable diagnostic or conservative terminal
classification, never guessed into IN-FLIGHT.

### Terminal backlog statuses

Backlog rows whose status semantically denotes DONE, SHIPPED, ARCHIVED,
SUPERSEDED, HISTORICAL, RETIRED, or ABANDONED are terminal. They MUST NOT appear
in Sprint Plan or QUEUED output regardless of priority or a stale sprint cell.
Unscheduled non-terminal candidates MAY remain visible as unscheduled backlog,
but they MUST NOT be presented as scheduled or authorized.

### Zero-active roadmap semantics

When every roadmap PI is closed and no `CURRENT_PI.md` is active:

- the active PI resolver MUST return no active PI;
- generated state MUST say `No active PI` and MUST NOT derive an active focus
  from old feature or sprint artifacts;
- no sprint is current;
- terminal features MUST NOT populate IN-FLIGHT;
- historical latest-PI context MAY be displayed only with an explicitly closed
  or historical label.

The existing active-PI behavior remains required: a valid active roadmap marker
and active `CURRENT_PI.md` MUST continue to resolve and render as active.

## Technical requirements

### TR-01: Preserve maintenance identity and authorization boundary

The package MUST retain `MAINT-2026-08-06-TRUTH-RECONCILIATION`. It MUST NOT
receive an SDD number, PI, sprint, allocation, or roadmap commitment. It MUST NOT
create PI-10 or activate SDD-068. SDD-059 remains owner-preserved and
unscheduled. SDD-060 through SDD-067 MAY remain only as plainly labeled,
untriaged concept themes without product IDs or authority.

### TR-02: Reconcile authoritative backlog truth

`backlog/BACKLOG.md` MUST retain existing RICE values while recording the product
statuses accepted by AC-TR-01 and AC-TR-03. SDD-008 and SDD-059 MUST remain
unscheduled; no score may be invented. Terminal rows MUST be excluded by shared
terminal-status semantics from Sprint Plan and QUEUED views.

### TR-03: Preserve SDD-035 as abandoned history

The SDD-035 spec and validation contract MUST remain present and state
ABANDONED / HISTORICAL, never DONE. Existing partial evidence MUST be preserved
exactly in lifecycle meaning: checked evidence stays checked, unchecked items
stay unchecked, and future Azure cleanup requires fresh owner authorization.

### TR-04: Provide one shared status predicate and resolver

`cli/state_builder_data.py` MUST own a single reusable status-normalization and
terminal-classification path for feature and backlog lifecycle decisions. State
Markdown and work-index rendering MUST consume the resolved data or shared
predicate; `state_builder_markdown.py` and `state_builder_html.py` MUST NOT add
independent ad hoc terminal-status substring lists.

The implementation MUST remain stdlib-only and respect existing module
ownership: data interpretation in `state_builder_data.py`, Markdown composition
in `state_builder_markdown.py`, work-index composition in
`state_builder_html.py`, and orchestration in `state_builder.py`. Existing public
interfaces SHOULD remain stable unless a focused failing test proves a minimal
additive field is required.

### TR-05: Enforce truthful generated state

The state builder MUST exclude terminal feature statuses from operational
IN-FLIGHT and exclude terminal backlog rows from Sprint Plan and QUEUED. In the
all-closed case, `derive_next_action` and rendered output MUST not infer active
focus from old artifacts. Active-PI behavior and explicit supported overrides
MUST remain compatible with ADR-027.

### TR-06: Refresh the four hand-authored current surfaces

The following bounded surfaces MUST be refreshed without broad historical
rewrites:

- `docs/HIGH_LEVEL_DEV_TRACKER.md`: current snapshot states no active PI,
  sprint, feature, or scheduled work and points to authoritative live sources.
- `sessions/SESSION-MEMORY.md`: replace the leading checkpoint with the current
  between-PI truth and implementation handoff; preserve older checkpoint and
  history sections where feasible.
- `docs/ONBOARDING_KICK_OFF.md`: current pipeline guidance distinguishes
  current truth from historical examples and directs readers to the zero-active
  sources.
- `docs/LEADERSHIP-ONE-PAGER.html`: become a dated capability brief, not a
  product schedule. It MUST remove PI-10 active, `Now building`, and active
  SDD-068 claims. SDD-060 through SDD-067 labels MUST be removed as product IDs;
  useful ideas MAY remain only as untriaged concept themes. It MUST state that
  concept labels confer no backlog, PI, sprint, or implementation authority.

### TR-07: Extend stale-doc lint narrowly

`cli/staledoc_lint.py` MUST include the leadership one-pager in its bounded scan
and detect only the corrected high-risk claims: a PI asserted active when the
live source has none, `Now building` or equivalent active-work claims in the
leadership brief during zero-active state, and unauthorized SDD-060 through
SDD-068 product labels. The guard MUST use focused exact patterns or structured
anchors and MUST NOT become a broad prose-truth scanner. Existing article-count
and current-PI behavior and marker exemptions MUST remain green.

### TR-08: Rebuild generated artifacts last and only through state_builder

After source corrections and focused tests pass, the maintenance artifacts MUST
be moved to their terminal completed state so they do not self-populate
IN-FLIGHT. Only then may `state_builder.py` rebuild:

- `exec/state.md`
- `exec/state.html`
- `exec/work-index.md`

These three files MUST NOT be manually edited. The rebuilt files MUST contain no
false PI-10, SDD-060 through SDD-068, current sprint, active feature, Sprint Plan,
IN-FLIGHT, or QUEUED claims derived from terminal records.

### TR-09: Preserve architecture and scope locks

All five Article X locked functions in `cli/state_builder.py` MUST remain
byte-identical. No new dependency, schema enum, constitution edit, Azure action,
PI/sprint creation, setup-repair behavior change, product implementation,
historical deletion, commit, push, or merge is in scope.

## Non-functional requirements

- **Determinism:** identical source fixtures and fixed date MUST produce
  identical status classification and generated output.
- **Conservatism:** ambiguous terminal evidence MUST never produce an
  operational classification.
- **Compatibility:** active-PI fixtures and non-terminal lifecycle stages MUST
  retain existing behavior.
- **Auditability:** every status exclusion MUST be explainable from a source
  status and shared resolver outcome.
- **Maintainability:** no duplicated terminal-status filter tables across
  renderers; no third-party dependency.
- **Data integrity:** no historical artifact or validation evidence is deleted,
  checked, or rewritten merely to make generated output pass.

## Expected implementation files and ownership

| Owner | Expected file | Purpose |
|-------|---------------|---------|
| Product Manager source correction, already authorized | `backlog/BACKLOG.md` | accepted terminal and unscheduled product truth; preserve RICE |
| Product Manager source correction, already authorized | `specs/2026-06-08-azure-decommission/spec.md` | SDD-035 abandoned/historical disposition |
| Product Manager source correction, already authorized | `specs/2026-06-08-azure-decommission/validation.md` | preserve partial evidence and authorization boundary |
| Software Developer | `cli/state_builder_data.py` | shared status predicate/resolver and resolved lifecycle data |
| Software Developer | `cli/state_builder_markdown.py` | consume resolved backlog status for Sprint Plan; no local status list |
| Software Developer | `cli/state_builder_html.py` | consume shared resolver for work-index IN-FLIGHT/QUEUED; no local status list |
| Software Developer, orchestration only if required | `cli/state_builder.py` | wire resolved data and rebuild outputs; locked functions untouched |
| Software Developer | `cli/test_state_builder.py` | focused resolver, renderer, all-closed, active-PI, build, and lock regressions |
| Software Developer | `cli/staledoc_lint.py` | bounded leadership and zero-active drift checks |
| Software Developer | `cli/test_staledoc_lint.py` | focused leadership and existing-guard regressions |
| Executive Manager / document owner | `docs/HIGH_LEVEL_DEV_TRACKER.md` | current zero-active operational snapshot |
| Executive Manager / document owner | `sessions/SESSION-MEMORY.md` | leading current checkpoint; preserve historical body |
| Executive Manager / document owner | `docs/ONBOARDING_KICK_OFF.md` | current pipeline and source guidance |
| Executive Manager / document owner | `docs/LEADERSHIP-ONE-PAGER.html` | dated capability brief without unauthorized schedule |
| State builder only | `exec/state.md` | generated Markdown state |
| State builder only | `exec/state.html` | generated HTML state |
| State builder only | `exec/work-index.md` | generated principal work index |

No other file is expected. A plan that adds a file MUST justify it against a
specific requirement and confirm it does not broaden product or governance
scope.

## Required sequence and parallelism constraints

1. **Baseline and RED tests, serial:** capture the current diff and Article X
   hashes; add focused failing tests before production edits.
2. **Authoritative source correction, serial:** retain and verify the accepted
   backlog and SDD-035 edits before generator behavior is changed.
3. **Shared resolver, serial:** implement and prove `state_builder_data.py`
   semantics before either renderer is changed. Renderer work depends on this
   resolved contract.
4. **Independent consumers, parallel after step 3:** Sprint Plan consumption in
   `state_builder_markdown.py` and work-index consumption in
   `state_builder_html.py` MAY proceed in parallel because file ownership does
   not overlap. Their tests MUST use the same shared status semantics.
5. **Current-document refresh, parallel after source truth stabilizes:** the four
   hand-authored documents MAY be refreshed in parallel only with one owner per
   file. `SESSION-MEMORY.md` leading checkpoint and leadership brief require a
   final serial consistency review against the resolved source state.
6. **Stale-doc guard, parallel with step 4:** lint and lint-test changes MAY run
   in parallel with renderer consumers; they MUST not edit current documents in
   the same dispatch.
7. **Focused validation, serial integration:** run state-builder and stale-doc
   tests, schema lint, structural checks, Article X lock, and diff checks. Repair
   source or code before proceeding if any fail.
8. **Review, integration, and closure, serial:** after implementation evidence
  is complete, keep this spec ACTIVE / REVIEW through independent Stage 2 and
  keep generated review outputs at REVIEW. APPROVED means review-approved and
  awaiting integration, not DONE. Only after Stage 2 approval and separately
  owner-authorized integration may terminal metadata be applied at the closure
  gate; rebuild all three `exec/` artifacts after that metadata change and
  before DONE. Never hand-edit those outputs.
9. **Final review, serial:** prove generated absence claims, full traceability,
   no unauthorized files/actions, and all required validation items.

### Sequencing audit note -- 2026-08-06

The Architect-adjudicated sequence above supersedes only earlier wording that
placed terminal metadata before independent review. It does not change any
requirement, acceptance criterion, product scope, or authorization boundary.
Implementation completion remains ACTIVE / REVIEW; Stage 2 approval produces
review-approved work awaiting integration; separately owner-authorized
integration and the closure gate precede terminal metadata, the final builder
rebuild, and DONE.

Parallel workers MUST NOT share a file, edit generated artifacts, or independently
invent status semantics. The Software Developer owns integration order and the
single resolver contract.

## Acceptance criteria

The product acceptance criteria remain authoritative. Technical proof is bound
in `validation.md`.

- **TAC-01:** Accepted backlog terminal and unscheduled truth is preserved with
  unchanged RICE data and terminal rows absent from scheduled/queued output.
- **TAC-02:** SDD-035 remains abandoned/historical with partial evidence intact,
  never DONE or operational.
- **TAC-03:** All-closed roadmap and inactive sprint markers produce no active PI,
  sprint, feature focus, or IN-FLIGHT work; active-PI regression remains green.
- **TAC-04:** A single shared resolver handles terminal feature and backlog
  semantics, including status evidence outside `spec.md`; renderers contain no
  duplicate ad hoc terminal filters.
- **TAC-05:** The four current hand-authored surfaces agree on the between-PI
  state while frozen historical sections remain intact where feasible.
- **TAC-06:** The leadership capability brief contains no PI-10 active, `Now
  building`, active SDD-068, or SDD-060 through SDD-067 product-ID claim.
- **TAC-07:** Narrow stale-doc tests catch the specified leadership and
  zero-active drift without broad prose linting or existing-guard regression.
- **TAC-08:** Source and focused checks precede one state-builder-only rebuild;
  generated artifacts contain none of the specified false claims.
- **TAC-09:** Article X functions remain byte-identical and the final scope
  contains no Azure, PI/sprint, setup behavior, product implementation, deletion,
  commit, push, or merge action.

## Traceability matrix

| Product AC | Technical requirements | Technical acceptance | Validation evidence |
|------------|------------------------|----------------------|---------------------|
| AC-TR-01 | TR-02 | TAC-01 | V-01, V-02, V-03 |
| AC-TR-02 | TR-03, TR-09 | TAC-02, TAC-09 | V-04, V-05, V-18 |
| AC-TR-03 | TR-01, TR-02 | TAC-01 | V-01, V-03 |
| AC-TR-04 | TR-04, TR-05, TR-08 | TAC-03, TAC-04, TAC-08 | V-06, V-07, V-08, V-09, V-15, V-16 |
| AC-TR-05 | TR-05, TR-06 | TAC-03, TAC-05 | V-06, V-10, V-11 |
| AC-TR-06 | TR-01, TR-06, TR-07 | TAC-06, TAC-07 | V-11, V-12, V-13 |
| AC-TR-07 | TR-07 | TAC-07 | V-12, V-13, V-14 |
| AC-TR-08 | TR-08 | TAC-08 | V-15, V-16, V-17 |
| AC-TR-09 | TR-01, TR-09 | TAC-09 | V-17, V-18 |

## ADR and constitution decision

No new ADR is required. ADR-027 already establishes zero-or-one active PI,
separates active from historical selection, forbids a synthetic successor, and
requires truthful generated labels. This package applies that accepted decision
to status resolution and stale current surfaces; it does not introduce a new
cross-module architectural policy.

No constitution edit is required. The valid between-PI state was already added
to `constitution/roadmap.md` under ADR-027. This package changes neither the
constitution contract nor its version.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Archived work becomes DONE because validation is complete | explicit terminal disposition precedes completeness inference |
| Abandoned work becomes REVIEW/IMPLEMENT because validation is incomplete | terminal predicate excludes it before ratio/artifact inference |
| Backlog rows leak into QUEUED because they retain P1-P3 | shared terminal predicate gates queue selection |
| A stale sprint cell leaks shipped work into Sprint Plan | shared terminal predicate gates grouping independently of sprint text |
| Renderer filters drift apart | one data-layer resolver; tests reject duplicate local status lists |
| Zero-active fix breaks real active PI behavior | dedicated active-PI regression fixture |
| Historical evidence is rewritten to satisfy lint | bounded scan and explicit historical exemption mechanism |
| Generated files are edited directly | diff ownership check plus state-builder deterministic rebuild evidence |

## Open issues

None. Product scope, SDD-035 disposition, maintenance identity, authorization
boundary, and architecture are resolved. Any discovery requiring a new schema
enum, constitution change, dependency, Azure action, or new product identifier
stops implementation and returns to the appropriate owner gate.

## SPEC gate verdict

**APPROVED.** The technical design is complete and testable. Implementation may
proceed only under the locked validation contract and the sequence above. This
approval does not authorize a PI, sprint, SDD ID, Azure action, commit, push, or
merge.

---

## Closure gate -- 2026-08-06

**DONE.** Owner-authorized closure followed independent Stage 2 approval and
integration of the exact approved implementation through PR #4. The integrated
baseline is merge commit `f8b6b24edaff7112c2a783da09faed3e11e853bf`, whose
ancestry contains `6bd215c07a9f17f64017eabbebf3616b0192e8a0` and
`9487cd05dc99be62592e83dc4240a1fadc1c6d6c`. Required PR and push Doctor jobs
for Ubuntu and Windows, plus Greptile Review, completed successfully.

This terminal transition creates no PI, sprint, product allocation, or new SDD
identifier. The next gate is owner-led product triage.