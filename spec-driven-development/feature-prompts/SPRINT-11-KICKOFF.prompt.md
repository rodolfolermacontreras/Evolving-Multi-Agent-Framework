# SPRINT 11 KICKOFF -- PI-6 Sprint 2 / Lifecycle pipeline + drag-to-reorder safeguards

You are leading **Sprint 11**, which is **PI-6 Sprint 2**. Your job is to ship
**SDD-036** only: import the three approved local-dashboard patterns into the
framework dashboard surface:

1. Lifecycle status pipeline on feature and sprint cards.
2. Four-card documentation row: Constitution / Spec / Sprint / ADRs.
3. Drag-to-reorder backlog with dependency-lock and audit-trail safeguards.

Do not absorb **SDD-037** (Sprint 12 Dispatches card + health pills). Do not
absorb **SDD-038** or carryovers (Sprint 13 contingency). Do not touch Azure
decommission work. Sprint 11 is intentionally large enough with SDD-036 alone.

You are the **Principal Executive Manager** for this kickoff. PM + Architect own
SDD-036 CLARIFY/SPEC/PLAN/TASKS. The Principal Software Developer owns
implementation, QA, sprint close, and Sprint 12 kickoff authoring if Sprint 11
closes cleanly.

---

## HARD PREREQUISITE -- STOP IF NOT MET

Sprint 11 must not start until all checks are true:

1. **Sprint 10 is closed locally.** Confirm
   [`../sprints/PI-6/CURRENT_PI.md`](../sprints/PI-6/CURRENT_PI.md) marks
   PI-6 Sprint 1 / Sprint 10 **CLOSED locally** on 2026-06-10 and still marks
   PI-6 **ACTIVE**.
2. **Owner approval evidence is recorded.** Confirm
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md) contains a
   `### Sprint 10 -- CLOSED` block with owner evidence:
   `Approve close prep, no push`.
3. **No commit/push was performed by Sprint 10 F-23.** The Sprint 10 close
   block must say local close prep, commit pending, and no push performed.
4. **Tests are green at the Sprint 10 close baseline**:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least
   349 passed with the known 2 platform-conditional skips.
5. **Schema lint is clean**:
   `python spec-driven-development/cli/schema_lint.py` exits 0.
6. **SDD-040 is DONE locally in BACKLOG** with evidence for F-21/F-22/F-23,
   349 passed / 2 skipped, schema lint clean, active-focus smoke, and serve
   verification. Do not require a commit SHA; F-23 explicitly leaves commit
   pending.
7. **The dashboard complaint that launched Sprint 10 stays resolved.** After
   `python spec-driven-development/cli/state_builder.py`,
   [`../exec/state.md`](../exec/state.md) must not say
   `Active focus: azure-decommission`.
8. **SDD-036 remains open and allocated as Sprint 11 next planned.** Confirm the
   SDD-036 row under `Post-Sprint-7 Bundle` in
   [`../backlog/BACKLOG.md`](../backlog/BACKLOG.md) is still open and not marked
   DONE.
9. **SDD-037 and SDD-038 remain open for later sprints.** Confirm SDD-037 is
   Sprint 12 scope and SDD-038/carryovers are Sprint 13 contingency. Do not
   pull either into Sprint 11.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not start Sprint 11 on a
red test baseline, stale active-focus output, missing Sprint 10 owner evidence,
or a backlog that accidentally closed or absorbed SDD-037/SDD-038.

---

## 0. How to use this prompt

1. Read [_SHARED_ONBOARDING.md](_SHARED_ONBOARDING.md) end to end.
2. Verify the HARD PREREQUISITE above.
3. Execute Sprint 11 in isolated feature sessions or EM-routed subagent
   dispatches that preserve Article VII context isolation. Do not ask the owner
   to manually open another session when subagent dispatch gives equivalent
   isolation and the owner has approved that execution shape.
4. Append feature blocks and the sprint-close block to
   [`../exec/sprint-progress.md`](../exec/sprint-progress.md). Keep the ledger
   append-only.

---

## 1. Sprint goal

Sprint 11 ships **one feature** (SDD-036): a more useful local dashboard that
makes lifecycle state, documentation routes, and backlog ordering visible and
operable without ceremony.

### Scope

- **Primary scope**: SDD-036 only.
- **Dashboard surfaces in scope**: generated `exec/state.html` and the data
  structures in `cli/state_builder.py` that feed it.
- **Schema surfaces in scope**: `cli/schema_lint.py` and tests if CLARIFY locks
  `depends_on` frontmatter validation.
- **Ledger surfaces in scope**: audit-trail row shape for drag-to-reorder if
  CLARIFY locks a SQLite-backed ledger write.
- **Prompts/docs in scope**: SDD-036 spec dir artifacts, Sprint 11 close block,
  and Sprint 12 kickoff prompt if Sprint 11 closes.

### Explicit exclusions

- **SDD-037**: Dispatches card + health pills is Sprint 12. Do not implement
  ledger visibility cards or dashboard health pills in Sprint 11.
- **SDD-038**: aesthetic tokens are Sprint 13 contingency. Do not define or
  apply the lifecycle color-token system in Sprint 11 except minimal existing
  styles needed for readability.
- **Carryovers**: SDD-034, SDD-039, and PI-4 housekeeping remain outside Sprint
  11 unless the owner explicitly replans PI-6.
- **Azure decommission**: SDD-035 remains out-of-band. No Azure docs, workflows,
  deployment files, or cloud references are in Sprint 11 scope.

---

## 2. Sprint sequence

| Order | Feature | Owner | Why this order |
|-------|---------|-------|----------------|
| 1 | F-24: SDD-036 CLARIFY -> SPEC -> PLAN -> TASKS | PM + Architect, with SW Dev task input | SDD-036 has genuine Level-1/Level-2 design surfaces: dependency-lock semantics, audit-trail ledger row, `depends_on` frontmatter, schema_lint extension, and drag force-override governance. Lock the contract first. |
| 2 | F-25: IMPLEMENT + QA for SDD-036 | SW Dev + workers | Implementation only after the dashboard/UI validation model and dependency safeguards are locked. Use the UI Lifecycle Variant if CLARIFY confirms iterative UI validation is needed. |
| 3 | F-26: Sprint 11 close + SPRINT-12 kickoff authoring | SW Dev + EM | Close Sprint 11, regenerate state, request owner approval before any push, and author `SPRINT-12-KICKOFF.prompt.md` for SDD-037 only. |

The default is sequential. Fleet dispatch is allowed only after F-24 produces a
file dependency graph that proves no two workers modify the same file. Shared
`cli/state_builder.py`, `cli/schema_lint.py`, generated exec surfaces, or SDD-036
artifacts force serialization.

---

## 3. Likely CLARIFY surfaces

### Q-A -- Lifecycle pipeline scope and state source

Decide which lifecycle states render and where the source of truth comes from.
Default recommendation: render `IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN ->
TASKS -> IMPLEMENT -> REVIEW -> DONE` from existing spec-dir artifacts,
validation completeness, and backlog/sprint allocation. Avoid introducing a new
state registry unless current artifacts cannot support the display.

### Q-B -- Four-card documentation row

Lock the exact four cards and target routes. Default recommendation:
Constitution, Spec, Sprint, ADRs. Each card should resolve to existing local
artifacts and show a disabled/missing state when a target is absent. Do not add
SDD-037 ledger cards under this feature.

### Q-C -- Drag-to-reorder interaction model

Decide whether Sprint 11 implements true browser drag/drop, keyboard-accessible
move controls, or a phased local-only model. Default recommendation: ship a
keyboard-accessible reorder control first if true drag/drop requires too much
JavaScript or raises validation ambiguity. The owner correction still stands:
reordering must be possible without ceremony; the value-add is the audit trail,
not blocking the human.

### Q-D -- Dependency-lock semantics

Define what a dependency lock means. At minimum: a backlog item cannot be moved
ahead of an incomplete item it depends on; cycle-creating moves are blocked;
blocked moves surface a human-readable reason. Decide whether dependencies are
feature IDs only (`SDD-036`) or can reference spec-dir slugs.

### Q-E -- `depends_on` frontmatter field

Decide the schema for the new field. Default recommendation: optional list field
on `spec.md` frontmatter, e.g. `depends_on: [SDD-018]`, with absent field treated
as an empty dependency list. Avoid flag-day backfill across all spec dirs unless
CLARIFY finds a concrete reason.

### Q-F -- `schema_lint.py` extension

Decide what lint validates: field type, valid ID shape, duplicate dependencies,
self-dependency, and possibly existence of referenced IDs. Existence checks may
be warning-level if historical artifacts are incomplete. Any schema migration or
strict required-field rule is a Level-2 risk and needs owner approval.

### Q-G -- Audit-trail ledger row

Define the reorder audit row shape before implementation. Minimum fields:
`event_type`, actor/agent, timestamp UTC, backlog item ID, from-rank, to-rank,
reason, dependency-check result, and force-override flag. Decide whether this
writes to `ledger/fleet.db`, a new ledger table, or an append-only markdown/JSON
artifact. New SQLite schema requires explicit Architect review and owner-visible
approval.

### Q-H -- Force override as Level-2 decision

Define the override path for moving an item in a way that violates dependency
ordering. Default recommendation: blocked by default; force requires a recorded
Level-2 decision with Friction Analysis and owner approval. The UI can expose the
path, but must not silently force the move.

### Q-I -- UI Lifecycle Variant applicability

Decide whether SDD-036 opts into the UI Lifecycle Variant from SDD-018. Default
recommendation: yes for the visual dashboard surfaces, but keep schema/ledger
requirements strict under normal Article X. If mixed validation is needed, make
the split explicit in `validation.md`.

### Q-J -- ADR requirement

Default: an ADR is likely required only if Sprint 11 introduces a new ledger
schema/table, changes backlog ordering governance, or makes `depends_on`
frontmatter required across historical specs. If the implementation remains
optional-field + UI rendering + append-only existing artifact logging, an ADR may
not be required. CLARIFY must decide explicitly.

---

## 4. Hard constraints

- **No silent REQUIRED deferral.** Sprint 11 inherits the Sprint 7/8/9/10 rule:
  if a REQUIRED item cannot close, the feature or sprint does not close.
- **Pre-push approval is mandatory.** Record owner approval status before any
  push. Green tests and generated state do not substitute for approval.
- **Stdlib-only CLI is binding (Article V).** No third-party runtime dependency
  for dashboard generation, schema lint, or ledger writes.
- **No constitution edit without ADR and owner approval.** SDD-036 may reference
  Article XII / UI Lifecycle Variant, but it must not edit `constitution/**`
  unless an ADR and owner approval explicitly authorize it.
- **Preserve unrelated dirty work.** Stage explicit Sprint 11 paths only. Do not
  sweep in Sprint 10 implementation files unless they are intentionally part of
  the Sprint 10 close commit approved by the owner.
- **Do not absorb SDD-037 or SDD-038.** SDD-037 is Sprint 12; SDD-038/carryovers
  are Sprint 13 contingency.
- **Do not close PI-6 automatically.** Sprint 11 closes only Sprint 11. PI-6
  remains ACTIVE after Sprint 11 unless the owner separately approves a PI close,
  which is not expected before Sprint 12.

---

## 5. Sprint close criteria

Sprint 11 closes DONE when all of the following are true:

1. SDD-036 CLARIFY decisions are recorded and all NEEDS-CLARIFICATION items are
   closed.
2. SDD-036 `spec.md`, `plan.md`, `tasks.md`, and `validation.md` exist and pass
   schema lint.
3. All REQUIRED validation items are checked, including lifecycle pipeline,
   4-card docs row, dependency-lock behavior, audit trail, and force-override
   governance.
4. Full test suite passes at or above the Sprint 10 close baseline:
   `python -m pytest spec-driven-development/ --tb=no -q` returns at least 349
   passed with the known 2 platform-conditional skips.
5. Schema lint exits 0:
   `python spec-driven-development/cli/schema_lint.py`.
6. `exec/state.md`, `exec/state.html`, and `exec/work-index.md` are regenerated
   with `python spec-driven-development/cli/state_builder.py`.
7. Manual dashboard smoke confirms lifecycle pipeline and 4-card docs row render
   for at least one active/done feature and one sprint card.
8. Drag/reorder smoke confirms dependency-blocked moves are blocked with a reason
   and allowed moves record an audit trail row.
9. BACKLOG marks SDD-036 DONE with evidence. SDD-037 and SDD-038 remain open.
10. `sprints/PI-6/CURRENT_PI.md` marks Sprint 2 / Sprint 11 CLOSED with date,
    tests, validation, ADRs if any, and retro paragraph. PI-6 remains ACTIVE;
    Sprint 12 (SDD-037) is the next planned sprint.
11. `exec/sprint-progress.md` has `### Sprint 11 -- CLOSED` appended.
12. `SPRINT-12-KICKOFF.prompt.md` is authored for SDD-037 only and the prompt
    README index is updated.
13. Owner approval is requested and recorded before any push.

---

## 6. Reporting template

Append this at Sprint 11 close:

```markdown
### Sprint 11 -- CLOSED

- Date: YYYY-MM-DD
- Owner: Principal Executive Manager (lead); PM + Architect owned design; SW Dev + workers owned implementation and close
- Features completed: F-24, F-25, F-26
- Commits: <list or local close prep, commit pending>
- Tests: 349 -> N (>= 349 required)
- Schema lint: clean
- Validation: SDD-036 N/N REQUIRED + N/N OPTIONAL + manual checks
- ADRs: <list or none>
- PI-6 status: ACTIVE; Sprint 12 (SDD-037) is the next planned sprint
- SDD-036: DONE (<one-sentence summary of lifecycle pipeline + docs row + reorder safeguards>)
- Dashboard smoke: PASS (<pipeline/docs/reorder evidence>)
- Dependency-lock smoke: PASS (<blocked move + allowed move evidence>)
- Carry-forward: SDD-037 remains Sprint 12; SDD-038 + SDD-034 + SDD-039 + PI-4 housekeeping remain Sprint 13 contingency; SDD-035 remains out-of-band
- Owner ratification: REQUIRED BEFORE PUSH; <pending or approved with evidence>
- Notes: <one paragraph with Sprint 11 lessons>
- Next: SPRINT-12-KICKOFF.prompt.md authored at <path>; SDD-037 is the Sprint 12 anchor
```

---

## 7. Do NOT do

- Do NOT start Sprint 11 until the HARD PREREQUISITE passes.
- Do NOT close PI-6 in Sprint 11.
- Do NOT mark any REQUIRED item done without evidence.
- Do NOT push without explicit owner approval.
- Do NOT absorb SDD-037, SDD-038, SDD-034, SDD-039, PI-4 housekeeping, or
  Azure decommission work into Sprint 11.
- Do NOT introduce new JavaScript frameworks or Python dependencies for this
  dashboard work.
- Do NOT make `depends_on` required across all historical spec dirs unless
  CLARIFY records the migration cost and owner approves the Level-2 impact.
- Do NOT silently force reorder operations that violate dependency locks.
- Do NOT hand-edit `exec/state.md`, `exec/state.html`, or `exec/work-index.md`;
  regenerate them via `state_builder.py`.
