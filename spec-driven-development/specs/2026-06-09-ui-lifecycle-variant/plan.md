---
id: SDD-20260609UIVARIANT-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# Implementation Plan: UI Lifecycle Variant (SDD-018)

- Feature: SDD-018
- Spec reference: [`./spec.md`](./spec.md)
- Validation contract: [`./validation.md`](./validation.md) (LOCKED 2026-06-08)
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7)
- Plan Authors: Principal Architect + Principal Product Manager (drafted in F-10 pass 2; F-11 SW Dev owns execution)
- Date: 2026-06-08

---

## Approach Summary

SDD-018 ships the variant as five small, mostly-additive surfaces:

1. A `ui-variant: true` frontmatter marker on `spec.md` (Authoring
   decision 3 / AC-1 / R-1).
2. An optional `## Delta Entries` section in `validation.md` whose
   entries follow the closed-enum field schema documented in
   [`./spec.md`](./spec.md) "Authoring decision 1" (AC-2 / R-2).
3. A new `check_validation_variant` code path inside
   `cli/schema_lint.py`, dispatched once per spec dir based on the
   marker -- byte-identical lint behavior for non-variant spec dirs
   (AC-1, AC-4 / R-1, R-4).
4. A retroactive-demo migration of
   `specs/2026-05-16-state-dashboard/` (one `DE-01` entry,
   `item-type: retroactive-demo`) as the SDD-018 proof case
   (AC-5, AC-6 / R-5, R-6).
5. ADR-014 (drafted in this pass, status `proposed`) carrying the
   verbatim proposed-Article-XII text for the owner to accept in a
   separate Level-2 commit. The constitution edit itself is OUT OF
   SCOPE for F-11.

A single-page authoring guide
([`docs/UI-LIFECYCLE-VARIANT.md`](../../docs/UI-LIFECYCLE-VARIANT.md))
and template parity in `feature-spec.md` + `validation.md` complete
the surface (AC-9, AC-10 / R-9, R-10).

The plan is deliberately stdlib-only (Article V, framework rule):
argparse, sqlite3 (unused here), pathlib, json, sys, os, re. No new
third-party dependencies.

---

## Phases

| Phase | Goal | Dependencies | Deliverables |
|-------|------|--------------|--------------|
| 1 | Pass 2 finalization (this commit) | CLARIFY closed at `754fda6` | spec.md (active), validation.md (LOCKED), plan.md (active), tasks.md (created), ADR-014 (proposed) |
| 2 | `schema_lint.py` variant dispatch + variant validator + tests | Phase 1 commit | Modified `cli/schema_lint.py`; new test classes in `cli/test_schema_lint.py` (or `test_schema_lint_variant.py`) proving AC-1 through AC-5 |
| 3 | Template stubs (feature-spec.md + validation.md) | Phase 2 lands locally | Modified `templates/feature-spec.md` and `templates/validation.md` with commented-out variant stubs + docs page pointer |
| 4 | State-dashboard retroactive-demo migration | Phase 2 lands locally | Modified `specs/2026-05-16-state-dashboard/spec.md` (one-line marker add) and `specs/2026-05-16-state-dashboard/validation.md` (one `DE-01` entry append) |
| 5 | Docs page authoring | Phase 2 + decision points settled | New `docs/UI-LIFECYCLE-VARIANT.md` |
| 6 | F-11 close verification + QA | All prior phases | Full test suite passes; `schema_lint` exits 0; `state_builder.py` exits 0; F-11 SW Dev writes final report |

Phase 1 is this commit; Phases 2-6 are F-11 work.

---

## File Scope

| File | Phase | Type | Lines (approx) | Lock-surface? |
|------|-------|------|---------------|---------------|
| `specs/2026-06-09-ui-lifecycle-variant/spec.md` | 1 | Modify | ~470 final | No (active spec) |
| `specs/2026-06-09-ui-lifecycle-variant/validation.md` | 1 | Modify | ~210 final | **YES** (LOCKED at pass 2 close) |
| `specs/2026-06-09-ui-lifecycle-variant/plan.md` | 1 | Modify | ~250 final | No |
| `specs/2026-06-09-ui-lifecycle-variant/tasks.md` | 1 | Create | ~100 | No |
| `docs/ADR/014-ui-lifecycle-variant.md` | 1 | Create | ~180 | No (status: proposed; owner ratifies separately) |
| `cli/schema_lint.py` | 2 | Modify | +~120 net | **YES** (existing validators and dispatch path for non-variant spec dirs MUST stay byte-identical) |
| `cli/test_schema_lint.py` (or new `test_schema_lint_variant.py`) | 2 | Modify / Create | +~250 net | **YES** (existing `SchemaLintAcceptance` + `ArtifactContractAcceptance` test classes MUST pass unchanged) |
| `templates/feature-spec.md` | 3 | Modify | +3 (comment block) | **YES** (existing scaffold output for non-variant spec dirs MUST stay byte-identical when the comment is unused) |
| `templates/validation.md` | 3 | Modify | +5 (comment block) | **YES** (same as above) |
| `specs/2026-05-16-state-dashboard/spec.md` | 4 | Modify | +1 (marker line) | **YES** (no other content touched; `status: done` preserved) |
| `specs/2026-05-16-state-dashboard/validation.md` | 4 | Modify | +~25 (one DE-01 entry) | **YES** (no existing `[x]` checkboxes touched; no existing `## v0.2 additions` subsection touched) |
| `docs/UI-LIFECYCLE-VARIANT.md` | 5 | Create | ~150 | No |

Total F-11 net diff target: ~+450 LOC across 5 modify + 2 create.

---

## Lock-Surface Protections (binding on F-11 worker)

The F-11 worker MUST NOT modify the following, even incidentally:

1. **The existing `schema_lint` validators** for non-variant spec
   dirs (`check_artifact`, `check_agent`, `check_skill`,
   `check_prompt`). The variant adds a sibling validator; the
   existing validators stay byte-identical. Test class
   `SchemaLintAcceptance` is the canary.

2. **The SDD-FDC-001 status / type enums.** Per OWNER-ATTENTION
   resolution 1, `status: blocked` stays as the CLARIFY-phase
   carrier; the enum is NOT amended. F-11 may add comments
   explaining the convention but MUST NOT mutate
   `ARTIFACT_STATUS_ENUM` or `ARTIFACT_TYPE_ENUM`.

3. **Any LOCKED `validation.md` in any spec dir OTHER than
   `specs/2026-05-16-state-dashboard/`.** The forward-only migration
   rule (AC-5 / R-5) is hard-coded into `schema_lint` as an
   allow-list of length 1.

4. **The 7 RFC-2119 REQUIRED items in already-DONE specs.** F-11's
   surface is narrowly scoped to the files listed in the File Scope
   table above; no other spec dir is touched.

5. **`constitution/principles.md`.** The Article XII text is drafted
   inside ADR-014 only. The actual constitution edit is a separate
   Level-2 commit performed by the owner after they read ADR-014.
   F-11 does NOT touch this file under any circumstance.

6. **Existing test classes in `cli/test_schema_lint.py`**
   (`SchemaLintAcceptance`, `ArtifactContractAcceptance`). They
   stay unchanged at F-11 close. New test classes are appended.

7. **The `[x]` checkboxes and `status: done` frontmatter in
   `specs/2026-05-16-state-dashboard/`** (the migration target).
   The DE-01 entry is appended; no existing content is mutated.

A violation of any of these is a Stage 2 (architectural review)
rejection per `code-review` skill.

---

## Parallel-Safe Tasks vs Sequential Tasks

### Parallel-safe (Fleet Dispatch Eligible: YES)

- **T-018-03** (template stubs) -- touches `templates/feature-spec.md`
  and `templates/validation.md` only. Independent of T-018-02 once
  the variant API shape is locked here in pass 2.
- **T-018-05** (ADR-014 drafting) -- already done in this pass; no
  F-11 dispatch needed. Listed as `done` in `tasks.md`.

### Sequential (Fleet Dispatch Eligible: NO)

- **T-018-01** (re-baseline measurement) -- MUST run first at F-11
  session start to capture pre-F-11 test count. Single CLI call;
  reported in F-11 final report.
- **T-018-02** (schema_lint variant dispatch + new test classes) --
  cannot parallel with T-018-04 because T-018-04's validation depends
  on T-018-02's validator being available.
- **T-018-04** (state-dashboard demo migration) -- depends on
  T-018-02 (the validator must exist before the migration target can
  be lint-clean). Sequential after T-018-02.
- **T-018-06** (docs page) -- depends on T-018-02 + T-018-03 +
  T-018-04 + T-018-05 settling so the docs page reflects final
  behavior. Sequential, but a short task.
- **T-018-07** (F-11 close verification) -- ALWAYS LAST. Runs full
  suite, runs schema_lint, runs state_builder, writes final report.

### Dependency-graph summary

```
T-018-01 (baseline)
   |
   v
T-018-02 (schema_lint variant dispatch) --+--> T-018-04 (demo migration)
   |                                       |
   |                                       v
   +-> T-018-03 (template stubs) ---->  T-018-06 (docs page) -> T-018-07 (close verify)
                                          ^
                                          |
                            T-018-05 (ADR-014) [done in pass 2]
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `schema_lint` variant dispatch accidentally breaks strict-mode behavior on existing spec dirs | Low | High | Lock-surface protection 1 + regression test `test_non_variant_spec_dir_unaffected_by_variant_rules` (R-4 / `DeltaAppendOnlyAndErrorPrefix`). |
| Append-only enforcement (R-3) is hard to implement without git history access | Medium | Medium | Two acceptable implementations: (a) git-diff-based when invoked in a git repo; (b) always-on parse-time heuristic that compares the on-disk file to a checked-in snapshot. F-11 author chooses; either satisfies R-3. |
| Owner amends the proposed Article XII text after F-11 closes | Medium | Low | ADR-014 status is `proposed`; the constitution edit is a separate Level-2 gate. Amendments land in `constitution/principles.md` (or as ADR-015), NOT in F-11's deliverables. F-11 close is independent of ADR-014 acceptance. |
| State-dashboard demo migration drift (the F-11 worker mutates `[x]` checkboxes or `## v0.2 additions` content) | Low | High | Lock-surface protection 7; T-018-04 acceptance test asserts file diff is append-only. |
| Test count baseline confusion (273 vs actual measured) | Low | Low | T-018-01 re-baselines at session start; AC-8 floor is `>= 273` regardless. |
| Article XII text drifts in tone from Articles X / XI | Medium | Medium | M-2 (owner manual review of ADR-014 wording). PM + Architect drafted the ADR-014 article text jointly in this pass with explicit tone alignment. |
| F-11 exceeds Article VII session boundary by also editing `constitution/principles.md` | Low | High | Lock-surface protection 5 is explicit; the F-11 prompt already excludes it; this plan reinforces it. |

---

## Effort Estimate

| Phase | Estimate (S/M/L) | Notes |
|-------|------------------|-------|
| 1 -- pass 2 finalization (this commit) | M | 4 modified files + 1 created ADR in this spec dir; ~1000 LOC across the pass-2 surface. |
| 2 -- schema_lint variant dispatch | M | ~120 LOC in `schema_lint.py` + ~250 LOC in tests; well-trodden pattern. |
| 3 -- template stubs | S | 2 files, ~8 LOC total. Comment-only additions. |
| 4 -- state-dashboard demo migration | S | 2 files, ~26 LOC total. Surgical. |
| 5 -- docs page authoring | S-M | One ~150 LOC markdown page. Tone matters more than length. |
| 6 -- close verification | S | Full suite + lint + state_builder + final report. |

Total F-11 effort: roughly M (single multi-task feature implementation,
no fleet dispatch needed given the small surface and tight sequencing).

---

## Fleet Dispatch Plan (for F-11)

Sequential single-worker execution is the recommended shape. The
File Scope table shows 5 modify + 2 create across F-11; the dependency
graph has only T-018-03 (templates) and T-018-05 (ADR; already done)
as parallel-eligible. Given the small surface, the overhead of fleet
dispatch outweighs the parallelism gain.

If the F-11 SW Dev disagrees and wants to dispatch T-018-03 in
parallel with T-018-02, that is permitted -- the conflict surface is
zero (different files).

---

## Validation Criteria (cross-reference to spec.md ACs)

- [ ] R-1 -- proves AC-1
- [ ] R-2 -- proves AC-2
- [ ] R-3 -- proves AC-3
- [ ] R-4 -- proves AC-4
- [ ] R-5 -- proves AC-5
- [ ] R-6 -- proves AC-6
- [ ] R-7 -- proves AC-7
- [ ] R-8, R-11, R-12 -- prove AC-8
- [ ] R-9 -- proves AC-9
- [ ] R-10 -- proves AC-10
- [ ] R-13 through R-16 -- coverage floor
- [ ] M-1 through M-4 -- manual checks (owner)
- [ ] O-1 through O-3 -- nice to have, not blocking

Full mapping: see [`./spec.md`](./spec.md) Traceability Matrix.

---

## Future Work (non-binding, post-PI-5)

These are not in scope for F-11 but are recorded here so the next
spec author has the lineage:

- **F-beta (Sprint Burndown / Velocity widget)** -- first real
  variant consumer per [`clarify.md`](./clarify.md) Q7. PI-6 PM to
  label it explicitly as "the variant proof case" at plan time.
- **`/spec-ui` slash command** -- deferred to P3; file SDD-035 if
  friction emerges per [`clarify.md`](./clarify.md) Q2 +
  OWNER-ATTENTION 1.
- **`live-ui-v2` retroactive migration** -- C1 stretch candidate per
  [`clarify.md`](./clarify.md) Q5; post-PI-6 if it earns priority.
- **Dedup content-shingle upgrade (SDD-034)** -- P3 unscheduled per
  OWNER-ATTENTION 2; not blocking SDD-018.

---

## Cross-References

- Parent spec: [`./spec.md`](./spec.md)
- CLARIFY: [`./clarify.md`](./clarify.md) (closed)
- Validation contract: [`./validation.md`](./validation.md) (LOCKED 2026-06-08)
- Tasks: [`./tasks.md`](./tasks.md)
- ADR-014 (proposed): [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md)
- F-10 kickoff prompt: [`../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md`](../../feature-prompts/F-10-sprint7-sdd018-design.prompt.md)
- F-11 implementation prompt: [`../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md`](../../feature-prompts/F-11-sprint7-sdd018-implement.prompt.md)
- ADR-013 (Article XI precedent): [`../../docs/ADR/013-serial-clarify-spec-gate.md`](../../docs/ADR/013-serial-clarify-spec-gate.md)
- Retroactive demo target: [`../2026-05-16-state-dashboard/`](../2026-05-16-state-dashboard/)
- PI plan: [`../../sprints/PI-5/CURRENT_PI.md`](../../sprints/PI-5/CURRENT_PI.md)
