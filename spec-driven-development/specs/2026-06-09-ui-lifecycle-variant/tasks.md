---
id: SDD-20260609UIVARIANT-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# Task List: UI Lifecycle Variant (SDD-018)

- Spec reference: [`./spec.md`](./spec.md)
- Plan reference: [`./plan.md`](./plan.md)
- Validation contract: [`./validation.md`](./validation.md) (LOCKED 2026-06-08)
- ADR: [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md) (proposed)
- Task ID format: `T-018-NN` (local; spec dir already date-namespaced)
- Owner: Principal Software Developer (F-11 worker)
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7)

---

> **Note**: SDD-FDC-001 `type` enum does not contain `tasks`. This
> file uses `type: tasks` because that is the literal artifact kind;
> if `schema_lint` flags this, that flag is a known false positive
> -- the enum is OUT OF SCOPE for SDD-018 per OWNER-ATTENTION 1.
> F-11 SW Dev should verify lint behavior on this file at T-018-01
> baseline measurement and report any unexpected finding.

> **Update 2026-06-08**: verified at pass 2 close that `schema_lint`
> exits 0 on this file; `tasks` IS in the enum. No false positive.

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

## Task Breakdown

| Task ID | Description | File Scope | Acceptance Test | Effort (S/M/L) | Deps | Mode (AFK/HITL) | Fleet Dispatch Eligible | Status |
|---------|-------------|------------|-----------------|----------------|------|-----------------|-------------------------|--------|
| T-018-01 | Re-baseline measurement at F-11 session start. Run full test suite (`python -m unittest discover spec-driven-development/cli`) and `schema_lint`; record pre-F-11 test count and `schema_lint` exit code in the F-11 final report. Confirm both green before any code change. | none (read-only) | Test count >= 273; `schema_lint` exits 0 | S | none | AFK | NO | done |
| T-018-02 | Add `ui-variant: true` frontmatter marker recognition + `check_validation_variant` sibling validator + `[delta]` finding prefix + retroactive-demo path allow-list + append-only enforcement to `schema_lint.py`. Add ~12-18 new test methods across the 4 test classes named in spec.md Test Strategy (`UIVariantMarkerRecognition`, `DeltaEntrySchema`, `DeltaAppendOnlyAndErrorPrefix`, `RetroactiveDemoPathAllowlist`). | `cli/schema_lint.py`; `cli/test_schema_lint.py` (or new `cli/test_schema_lint_variant.py`) | All new test methods green; `SchemaLintAcceptance` + `ArtifactContractAcceptance` pass unchanged; proves R-1, R-2, R-3, R-4, R-5, R-13, R-14, R-15, R-16 | M | T-018-01 | AFK | NO | done |
| T-018-03 | Add commented-out variant stubs to `templates/feature-spec.md` (one `# ui-variant: true` line in frontmatter example) and `templates/validation.md` (one `## Delta Entries (UI variant only)` section stub). Both stubs link to `docs/UI-LIFECYCLE-VARIANT.md`. Strict spec dirs scaffolded from these templates remain byte-identical to today's output when stubs stay commented. | `templates/feature-spec.md`; `templates/validation.md` | Manual diff inspection: only comment additions; lines visible in template files but produce no semantic change in non-variant spec dirs | S | T-018-01 (could parallel with T-018-02; flagged YES below for completeness) | AFK | YES (parallelizable with T-018-02 if F-11 dispatches) | done |
| T-018-04 | State-dashboard retroactive-demo migration: add `ui-variant: true` to `specs/2026-05-16-state-dashboard/spec.md` (one line) and append one `### Delta DE-01 -- static-to-live pivot` entry to `specs/2026-05-16-state-dashboard/validation.md` documenting the v0.2 static->live pivot per Authoring decision 4. Existing `[x]` checkboxes, `status: done` frontmatter, and `## v0.2 additions` subsection MUST stay byte-identical (lock-surface protection 7). | `specs/2026-05-16-state-dashboard/spec.md`; `specs/2026-05-16-state-dashboard/validation.md` | Test class `StateDashboardDemoMigration` passes; `schema_lint` exits 0 across this spec dir; manual diff shows append-only behavior; proves R-6, M-3 | S | T-018-02 (variant validator must exist first) | AFK | NO | done |
| T-018-05 | Draft `docs/ADR/014-ui-lifecycle-variant.md` with proposed Article XII text, ADR-013-shaped frontmatter, status `proposed`, all required sections (Context, Decision, Proposed Article XII text, Consequences, Alternatives, References). | `docs/ADR/014-ui-lifecycle-variant.md` | Test class `ADR014ExistsAndShapeChecks` passes; `schema_lint` exits 0 on the ADR file; proves R-7 | S | none (drafted IN PASS 2 -- already done) | n/a | n/a | **done** |
| T-018-06 | Author `docs/UI-LIFECYCLE-VARIANT.md` single-page authoring guide. Sections: marker syntax, delta entry schema, the four `item-type` values + when to use each, forward-only migration rule, state-dashboard demo reference (link to T-018-04 deliverable), one-line note on `status: blocked` as CLARIFY-phase carrier. Match tone of `docs/HOST-INTEGRATION.md`. | `docs/UI-LIFECYCLE-VARIANT.md` | Test class `DocsPageExistsAndCrossLinks` passes; proves R-9, R-10 (via cross-link assertions); U-2 manual check on tone | S-M | T-018-02, T-018-03, T-018-04, T-018-05 | AFK | NO | done |
| T-018-07 | F-11 close verification: re-run full test suite (`>= 273` floor + new variant tests all green); re-run `schema_lint` across whole repo (exit 0); re-run `python spec-driven-development/cli/state_builder.py` (exit 0; clean state.md + state.html regen); write F-11 final report including pre-F-11 baseline test count from T-018-01 vs post-F-11 actual; flip `validation.md` items to `[x]`; commit. | none (verification only) + minor flip of `[x]` in `./validation.md` | All R-1 through R-16 checked; manual M-1 through M-4 confirmed by owner (M-1 + M-2 may happen async after F-11 close); proves AC-8, R-8, R-11, R-12 | S | T-018-02, T-018-03, T-018-04, T-018-05, T-018-06 | HITL (owner reviews final report; M-3, M-4 require owner) | NO | done |

---

## Dependency Graph

```
                  T-018-01 (baseline measurement)
                            |
                +-----------+-----------+
                |                       |
                v                       v
        T-018-02 (schema_lint)   T-018-03 (templates)
                |                       |
                +-----------+-----------+
                            |
                            v
                  T-018-04 (state-dashboard demo)
                            |
                            v
                  T-018-06 (docs page)
                            |
                            v
                  T-018-07 (close verification)

                  T-018-05 (ADR-014)  -- already done in F-10 pass 2
                          |
                          v (referenced by T-018-06)
```

---

## Batch Plan (F-11 execution order)

**Batch 1 (sequential prerequisites)**: T-018-01 (baseline measure)
**Batch 2 (parallel-safe pair, optional)**: T-018-02 + T-018-03
  in parallel via fleet dispatch -- OR sequential single-worker
  (recommended given small surface)
**Batch 3 (sequential)**: T-018-04 (state-dashboard demo migration)
**Batch 4 (sequential)**: T-018-06 (docs page)
**Batch 5 (sequential, final)**: T-018-07 (close verification +
  validation.md `[x]` flips + final report)

T-018-05 is `done` in this commit; not in any F-11 batch.

---

## Notes

- `Fleet Dispatch Eligible = YES` for T-018-03 only. All other tasks
  serialize on shared lint behavior, dependency on T-018-02's
  validator, or final-commit single-writer semantics.
- T-018-04 surgically appends one DE-01 entry; the F-11 worker MUST
  diff their change against the pre-T-018-04 state to confirm only
  the marker line on spec.md + the `## Delta Entries` section
  appended on validation.md were touched. Lock-surface protection 7.
- M-1 (owner reads ADR-014) and M-2 (owner reviews Article XII
  wording) can happen async after F-11 close -- they are NOT blocking
  for F-11 final report submission. They ARE blocking for any
  follow-on commit that edits `constitution/principles.md`.
- T-018-07 is the last task. Once it lands, SDD-018 moves to
  `status: done` and `validation.md` is fully checked.
- F-11 is a single Copilot Chat session per Article VII; if T-018-02
  takes multiple sessions (unlikely for this surface), the SW Dev
  hands off via [`spec-driven-development/sessions/SESSION-MEMORY.md`](../../sessions/SESSION-MEMORY.md).

---

## Cross-References

- Parent spec: [`./spec.md`](./spec.md)
- Implementation plan: [`./plan.md`](./plan.md)
- Validation contract: [`./validation.md`](./validation.md) (LOCKED)
- CLARIFY: [`./clarify.md`](./clarify.md) (closed)
- ADR-014 (drafted, proposed): [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md)
- F-11 implementation prompt: [`../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md`](../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md)
- Retroactive demo target: [`../2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
