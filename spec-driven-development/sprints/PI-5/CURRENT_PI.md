---
id: SDD-PI-5-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-06-08
sprint: PI-5
---

# PI-5: Brownfield Adoption + Anti-Conflict + Stakeholder Discipline

- Status: **Active** (Sprint 1 CLOSED 2026-06-06, Sprint 2 CLOSED 2026-06-07, Sprint 3 CLOSED 2026-06-08, Sprint 4 CLOSED 2026-06-08; 1 sprint remaining)
- Theme: Make the framework safely adoptable by other teams, harden the gates that prevent two features from colliding, and finish the discipline tools surfaced by the Scott Feedback Bundle.
- Started: 2026-06-06
- Owner: principal-executive-manager
- Predecessor: PI-4 (Alpha Release) closed DONE-WITH-DEFERRED on 2026-06-06.
- Authorization: Owner directive 2026-06-06 in Sprint 5 worker session (consolidated F-03 -> F-05 execution); EM rollup 2026-06-05.

---

## Goal

Close the brownfield-adoption story (symlink portability + a worker that owns
environment plumbing), then harden the framework against the multi-feature
context-bleed failure modes that surfaced during PI-4 (anti-conflict gates,
uniform user gates, UI lifecycle variant), and finish absorbing the Scott
Feedback Bundle so the framework is ready for a second-project test.

---

## PI Objectives

### 1. Brownfield Portability Finisher (SDD-016 + SDD-017)
**Why**: The framework currently lives in its own repo. Without the `.github/`
symlink trick a host project must copy our `.github/` and maintain a fork.
That's the wall stopping any second-project bootstrap. SDD-017 hires the
worker who will own this and every future env/worktree/branch-hygiene concern.

**Success Criteria**: `bootstrap.py host-link --target <host>` installs a
symlink (or junction on Windows) without overwriting the host's `.github/`;
dry-run is the default; new `dev-env-manager-general` worker is rostered.
Full validation contract green.

**Features**: SDD-016 (`.github/` symlink portability), SDD-017 (hire
`dev-env-manager-general`).

---

### 2. Anti-Conflict + Uniform Gates (SDD-019 + SDD-020 + SDD-023)
**Why**: Multiple in-flight features can step on each other at /clarify and
/spec time. The 2026-06-02 Scott meeting flagged this as the single highest-
return discipline change. SDD-023 makes "user gate" a first-class declared
construct rather than an ad-hoc per-prompt convention.

**Success Criteria**: A serial gate exists at /clarify and /spec phase
entries; a dedup pass runs over the active spec dirs; user gates are
declared explicitly in spec.md and surfaced in the dashboard.

**Features**: SDD-019 (serial gate on CLARIFY/SPEC), SDD-020 (cross-feature
dedup at triage/clarify), SDD-023 (first-class user gates).

---

### 3. UI Lifecycle Variant (SDD-018)
**Why**: The Live UI v2 dashboard work in PI-3/PI-4 exposed that Article X's
strict validation lock is too rigid for iterative visual work. SDD-018
introduces a controlled relaxation (delta entries in validation.md) without
loosening the rule for the rest of the framework.

**Success Criteria**: An ADR or new `/spec-ui` command defines the variant;
validation.md schema supports delta entries; one retroactive validation on a
PI-3 dashboard change demonstrates the workflow.

**Features**: SDD-018.

---

### 4. ADO/GitHub Bridge + Model Upgrade Discipline (SDD-022 + SDD-015)
**Why**: SDD-022 is the gap Scott named as blocking his team's adoption --
they live in ADO and need work items synced. SDD-015 codifies that model
upgrades are Level-2 decisions with a regression-test branch + A/B + cost
analysis, preventing silent quality drift.

**Success Criteria**: `/taskstoissues` (or equivalent) round-trips tasks.md
to GitHub Issues (ADO fast-follow); a model-upgrade SOP exists in
`docs/MODEL-UPGRADE-PROTOCOL.md` and is referenced from decision-policy.md.

**Features**: SDD-022 (ADO/GitHub Issues bridge), SDD-015 (model upgrades as
Level-2).

---

### 5. Self-Review + Stakeholder Defense (SDD-021 + SDD-025) + Carry-over Housekeeping
**Why**: Closes the Scott Bundle. SDD-021 turns each session into a feedback
loop; SDD-025 is the playbook for stakeholder pressure that invokes the
Friction Analysis template shipped in SDD-014. Carry-over: PI-4's two
deferred housekeeping items (domain-skill annotations, GitHub Actions Node.js
deprecation bump) ride along.

**Success Criteria**: `/evolve` ingests a self-review skill output; a
`stakeholder-pressure-defense` skill exists and is wired into the EM agent;
the two PI-4 carry-overs are committed.

**Features**: SDD-021, SDD-025, PI-4-carry-over (domain-skill annotations,
GitHub Actions bump).

---

## Sprint Allocation

| Sprint | Overall | Title | Items | Size | Why this order |
|--------|---------|-------|-------|------|----------------|
| **PI-5 Sprint 1** | Sprint 5 | Brownfield Portability | SDD-016 + SDD-017 | M | Highest-impact brownfield finisher; unblocks every future second-project bootstrap; self-contained (no upstream blockers). |
| **PI-5 Sprint 2** | Sprint 6 | Anti-Conflict Gates + Carry-Over | SDD-019 + SDD-020 + SDD-027 + SDD-028 + SDD-029 + PI-4 carry-over housekeeping | M-L | Biggest reduction in cross-feature context bleed; bundles well because dedup logic is the data SDD-019 needs to gate on. Picks up the Sprint 5 Architect audit follow-ups (SDD-027 host `.gitignore` protection P1; SDD-028 + SDD-029 P2 housekeeping if capacity permits) alongside PI-4 carry-over (domain-skill annotations, GH Actions bump). |
| **PI-5 Sprint 3** | Sprint 7 | UI Lifecycle Variant | SDD-018 | M | Stand-alone; depends on no other PI-5 item; needed before the next dashboard iteration. |
| **PI-5 Sprint 4** | Sprint 8 | ADO/GitHub Bridge + Model Upgrade Discipline | SDD-022 + SDD-015 | M-L | Heaviest sprint; gates external-team adoption (SDD-022) and process maturity (SDD-015). Best done after the anti-conflict + UI gates land so the bridge maps a stable model. |
| **PI-5 Sprint 5** | Sprint 9 | Self-Review + Stakeholder Defense + Uniform Gates | SDD-021 + SDD-023 + SDD-025 | M | All three are skills-and-process items that benefit from everything earlier in PI-5. SDD-023 (uniform gates) ships last so it can declare the gates the prior sprints have already invented. |

**Unscheduled** (out of PI-5 scope):

- **SDD-024** -- Microsoft self-improving skills paper memo (P3, single-task,
  not PI-bound; can be picked up at any time without sprint commitment).
- **SDD-026** -- Trim agent traceability scope (P4, deferred indefinitely per
  PM override; re-evaluate at PI-5 retrospective when ledger has accumulated
  two PIs of usage data).

---

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| Symlink behavior differs across Windows / Linux / macOS, breaking adoption | High | High | Mitigated | SW Dev | Cross-platform: `os.symlink` primary, fallback to `mklink /J` (junction) on Windows when symlink permission unavailable; mocked tests cover both branches. |
| Host repo CI silently runs framework workflows after symlink install | Medium | Medium | Owned | dev-env-manager-general | Documented in HOST-INTEGRATION.md; future iteration may add `--no-workflows` flag. |
| SDD-019 serial gate creates throughput chokepoint | Medium | Medium | Owned | PM | CLARIFY in Sprint 2 must define batch semantics; gate is serial per-phase, not per-repo. |
| SDD-022 ADO API surface drift breaks the bridge | Medium | High | Mitigated | SW Dev | GitHub-first; ADO is fast-follow under a clean adapter layer. |
| SDD-018 UI lifecycle relaxation leaks into non-UI features | High | Low | Mitigated | Architect | The variant is opt-in via a marker on the spec dir, not a global Article X amendment. |
| Sprint scope creep from absorbing all 11 items | Medium | High | Mitigated | EM | Five sprints; each bundle sized M; carry-over items ride along as housekeeping shoulders, not as primary scope. |

---

## Dependencies

**Internal**:
- SDD-FDC-001 frontmatter contract (LOCKED 2026-06-06): new artifacts in PI-5
  must carry valid frontmatter; schema_lint guards this.
- ADR-012 (`docs/ADR/012-filesystem-frontmatter-data-contract.md`).
- `cli/state_builder.py` count subcommand: PI-5 dashboards consume the rollup.
- `cli/schema_lint.py` artifact checker.

**External**:
- None for Sprint 1. Sprint 4 (SDD-022) depends on GitHub Issues API
  availability and an ADO project handle (TBD when Sprint 4 plans).

---

## Success Metrics

- All five PI-5 sprints close DONE with full validation contracts checked.
- Test count goes from 200 (PI-4 close baseline) to >= 230 by PI-5 close.
- One end-to-end brownfield bootstrap demo (Day-to-Day Agent or equivalent
  host) succeeds against `bootstrap.py host-link`.
- The Scott Feedback Bundle is fully resolved (DONE, deferred-indefinitely, or
  shipped under an alias) by PI-5 close.
- Two of the five sprints touch external collaborators (Sprint 1 for
  bootstrap demo; Sprint 4 for ADO/GH bridge).

---

## Cross-References

- Backlog: [`../../backlog/BACKLOG.md`](../../backlog/BACKLOG.md) (Scott
  Feedback Bundle sections P1/P2/P3)
- Predecessor PI: [`../PI-4/CURRENT_PI.md`](../PI-4/CURRENT_PI.md)
- PI-4 close ratification: commit `163cf42` 2026-06-06
- Sprint kickoff prompt: [`../../feature-prompts/SPRINT-05-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-05-KICKOFF.prompt.md)
- EM scope-allocation rationale: [`../../feature-prompts/F-03-pi5-kickoff.prompt.md`](../../feature-prompts/F-03-pi5-kickoff.prompt.md) section 3 (EM recommendation 2026-06-05)
- Management index: [`../../docs/Management/PI-5/INDEX.md`](../../docs/Management/PI-5/INDEX.md)

---

## Sprints

### Sprint 1 -- Brownfield Portability -- CLOSED 2026-06-06
**Status**: **DONE** (ratified by owner directive 2026-06-06)
**Closed**: 2026-06-06
**Spec dir**: `specs/2026-06-06-symlink-portability/`
**Spec**: APPROVED 2026-06-06; validation contract LOCKED R1..R7 + O1..O2 -- all checked.
**Sprint kickoff**: [`../../feature-prompts/SPRINT-05-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-05-KICKOFF.prompt.md)
**Sprint chain (chronological, on master)**:
- `7cf90fe` plan(pi-5): launch PI-5 -- sprint allocation
- `7182841` spec(symlink-portability): SDD-016 + SDD-017 co-spec approved
- `1a5e127` plan(symlink-portability): plan + tasks
- `30482d5` feat(symlink-portability): SDD-016 host-link + SDD-017 dev-env-manager hire
- (next: close + state regen)
**Tests**: 200 -> 213 (+13 net; all new in `cli/test_bootstrap.py` covering R1..R6 plus argparse regression smoke and roster sanity).
**Validation**: 7/7 REQUIRED checked, 2/2 OPTIONAL checked.
**Retro (one paragraph)**: Sprint 5 ran as a consolidated F-03 -> F-04 -> F-05
worker session (owner directive 2026-06-06), departing from the default
Article VII one-feature-one-session pattern. The departure was justified by
the sprint's tight coupling (F-03's allocation is needed to write F-04 + F-05;
F-04's spec is needed to write F-05; the three artifacts share a single
brownfield concern) and the precedent set by PI-4 Sprint 4's F-02 linear
single-session execution. The TDD discipline held: 13 tests authored before
implementation, the Windows-fallback test required one mock-scope adjustment
(only intercept `mklink`, let `git rev-parse` pass through) caught by a
clear failure message. Schema_lint clean throughout. Two PI-4 carry-over
housekeeping items (domain-skill annotations, GitHub Actions Node.js bump)
intentionally NOT pulled into Sprint 5 -- allocated to PI-5 Sprint 2 per
the plan. Net: 11 commits anticipated (4 already on master + close +
state-regen), 200 -> 213 tests, zero contract loosening.
**Capacity**: ~10 tasks, effort M. Dispatch pattern: linear single-session
execution (no fleet split) consistent with the PI-4 Sprint 4 precedent for
additive well-scoped CLI work.

### Sprint 2 -- Anti-Conflict Gates + Carry-Over -- CLOSED 2026-06-07
**Status**: **DONE** (consolidated execution per owner directive 2026-06-07)
**Closed**: 2026-06-07
Owner ratification: Rodolfo Lerma 2026-06-08 via Executive Manager (Level-2; Option 3 hybrid -- SDD-032 + SDD-033 absorb 5 deferred REQUIRED items).
**Spec dirs**:
- `specs/2026-06-07-serial-clarify-spec-gate/` (SDD-019)
- `specs/2026-06-07-cross-feature-dedup/` (SDD-020)
- `specs/2026-06-07-host-gitignore-protection/` (SDD-027)
**Sprint kickoff**: [`../../feature-prompts/SPRINT-06-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-06-KICKOFF.prompt.md)
**Sprint chain (chronological, on master)**:
- `2c3e45a` chore: pre-Sprint-6 exec/ state refresh
- `93aadf3` spec(serial-gate): SDD-019 CLARIFY closed + spec finalized
- `718221a` spec(dedup): SDD-020 CLARIFY closed + spec finalized
- `a0ebe08` spec(gitignore): SDD-027 CLARIFY closed + spec finalized
- `ebf740d` docs(adr): ADR-013 serial CLARIFY/SPEC gate (Article XI)
- `1c0454b` plan(serial-gate): SDD-019 plan + tasks + validation locked
- `7d9a206` plan(dedup): SDD-020 plan + tasks + validation locked
- `d922a5b` plan(gitignore): SDD-027 plan + tasks + validation locked
- `8eb564d` feat(dedup): SDD-020 implement cli/dedup.py + tests
- `524872b` feat(serial-gate): SDD-019 implement lock scanner + gate + subcommands
- `0449805` feat(constitution): add Article XI -- serial gate (ADR-013)
- `302bee5` feat(gitignore): SDD-027 implement host .gitignore protection
- `4a8c03c` fix(bootstrap): SDD-028 junction test + SDD-029 stale-symlink distinction
- `e112fde` spec(sprint-6): check validation contracts
- `649fbf4` close(sprint-6): mark all spec artifacts done
- `89e630f` chore: regenerate exec/ state -- Sprint 6 close
**Tests**: 213 -> 258 (+45 net; +22 dedup, +9 serial gate, +13 gitignore, +4 SDD-028/029; 2 skipped platform-conditional).
**Validation**: SDD-019 9/11 REQUIRED checked (R7 queue, R8 grandfather deferred); SDD-020 8/10 REQUIRED checked (R6 log writers, R8 prompt hooks deferred); SDD-027 11/12 REQUIRED checked (R12 docs deferred). 5 REQUIRED items carry to Sprint 7 as P2 housekeeping.
**ADRs**: ADR-013 (serial CLARIFY/SPEC gate, Article XI).
**SDD-019**: DONE (core: lock scanner, gate check, force-release; deferred: priority queue, grandfather migration)
**SDD-020**: DONE (core: three-layer heuristic, tiered action, CLI; deferred: log writers, prompt hooks)
**SDD-027**: DONE (core: gitignore detection, mode flag, manifest; deferred: HOST-INTEGRATION.md update)
**SDD-028**: DONE (documented Windows junction limitation + platform-conditional skip)
**SDD-029**: DONE (stale-symlink vs real-directory distinction + tests)
**PI-4 carry-over**: domain-skill annotations and GH Actions Node.js bump NOT pulled in -- carried to Sprint 7 or later.
**Retro (one paragraph)**: Sprint 6 ran as a consolidated EM-routed execution
(owner directive 2026-06-07 "get this done, route tasks to the right agent"),
departing from the default Article VII three-session split. The EM routed the
Architect for read-only CLARIFY analysis (all 23 questions), escalated two L2
constitutional decisions to the owner (SDD-019 Article XI = new article not
Article VII extension; SDD-027 Article X misreading corrected = no amendment
needed), then dispatched F-06 (spec finalization), F-07 (plan + tasks + ADR),
and F-08 (implementation) sequentially through principal subagents. The
highest-impact finding was the Article X misreading: the kickoff prompt and
three scaffolded spec dirs all referenced "Article X (Host Integration)" but
Article X is actually "Validation Is a Pre-Implementation Contract." The
Architect caught this in analysis; the owner confirmed no amendment needed.
Five REQUIRED validation items (2 from SDD-019, 2 from SDD-020, 1 from
SDD-027) are deferred as Sprint 7 P2 carry-over -- all are last-mile items
(queue ordering, grandfather migration, log writers, prompt hooks, docs) while
core functionality shipped for all three features. Net: 16 commits, 213 -> 258
tests, 1 ADR, 1 constitutional amendment (Article XI, principles.md 1.2.0).
**Goal**: Land the serial CLARIFY/SPEC gate plus the cross-feature dedup
pass; ship the host `.gitignore` protection that blocks the first real-host
dispatch; ship the two PI-4 housekeeping items.
**SDD-027 handling**: SDD-027 is an Article X amendment CANDIDATE. Owner
direction 2026-06-07 (via EM): handle as a normal spec first; only escalate
to an Article X amendment IF the spec proves the article must change.
Friction Analysis NOT required up front. The CLARIFY round must explicitly
decide whether the host-`.gitignore` rule fits within Article X as written
or requires a constitutional amendment; only if the latter does the work
branch into amendment ceremony.
**Status**: PLANNED. Kickoff prompt to be authored at PI-5 Sprint 1 close.

### Sprint 3 -- UI Lifecycle Variant -- CLOSED 2026-06-08
**Status**: **CLOSED 2026-06-08** (F-11 final pass; Article XII ratified mid-flight by owner)
**Closed**: 2026-06-08
Owner ratification (Article XII): Rodolfo Lerma 2026-06-08 commit `55b05cb` (mid-flight Level-2 ratification before sprint close -- refinement on the Option 3 hybrid model: the controlling ADR is ratified first so the sprint close itself happens against an already-binding constitution).
Owner ratification: Rodolfo Lerma 2026-06-08 via Executive Manager (Level-2; retroactive ratification -- push preceded stamp per Sprint 6 Option 3 hybrid pattern). Article XII (commit `55b05cb`) and Sprint 7 close commit chain (ending `a802ef3`) both ratified.
**Spec dir**: `specs/2026-06-09-ui-lifecycle-variant/`
**Spec**: APPROVED 2026-06-08 (F-10 pass 2); validation contract LOCKED 16 REQUIRED + 3 OPTIONAL + 4 manual + 2 UX -- 16/16 R + 3/3 O + 4/4 manual + 2/2 UX all satisfied (M-1/M-2/U-2 owner-async, all satisfied implicitly by Article XII landing commit `55b05cb`).
**Sprint kickoff**: [`../../feature-prompts/SPRINT-07-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-07-KICKOFF.prompt.md)
**Sprint chain (chronological, on master)**:
- `5cab91e` chore(prompts): SPRINT-07 kickoff authored
- `b005e66` spec(sprint-6-completion): SDD-032 scaffold + validation LOCKED at scaffold
- `8d55952` chore(sprint-7): stamp owner approval + prereq verification (Sprint 7 STARTED)
- `557b672` feat(sdd-032): T-032-01 + T-032-02 close SDD-019.R7 + R8 in cli/fleet.py (F-09)
- `8025a50` feat(sdd-032): T-032-03 close SDD-020.R6 triple-destination log writers (F-09)
- `a6a25e4` feat(sdd-032): T-032-04 + T-032-05 close SDD-020.R8 prompt hooks (F-09)
- `6827689` close(sprint-7-f-09): SDD-032 Sprint 6 completion bundle DONE
- `e7274e1` chore(sdd-032): stamp HITL Manual Check 1 -- owner approved hook wording
- `df3bffb` spec(sdd-018): F-10 pass 1 -- scaffold + CLARIFY question battery + Article XI live contention test PASS
- `754fda6` docs(sdd-018): F-10 CLARIFY closed -- Q1-Q9 + OWNER-ATTENTION resolutions + SDD-034 filed
- `d81ac3d` spec(sdd-018): F-10 pass 2 -- spec/validation/plan/tasks finalized; ADR-014 drafted (proposed)
- `7993fac` feat(sdd-018): T-018-02 schema_lint variant dispatch + append-only enforcement
- `3f6f520` feat(sdd-018): T-018-03 template stubs for UI Lifecycle Variant
- `b46a32f` feat(sdd-018): T-018-04 state-dashboard retroactive-demo migration
- `5233c29` docs(sdd-018): T-018-06 UI-LIFECYCLE-VARIANT.md authoring guide
- `22b72d8` close(sdd-018): F-11 T-018-01 + T-018-07 -- F-11 implementation closed
- `55b05cb` feat(constitution): land Article XII -- UI Lifecycle Variant ratified (ADR-014 accepted; principles.md 1.2.0 -> 1.3.0)
- (next: sprint close commit + state regen)
**Tests**: 259 -> 305 (+46 net; +14 F-09 in cli/test_fleet.py + cli/test_dedup.py; +32 F-11 in cli/test_schema_lint_variant.py; 2 skipped platform-conditional baseline preserved).
**Validation**: SDD-032 7/7 REQUIRED + 2/2 OPTIONAL; SDD-018 16/16 REQUIRED + 3/3 OPTIONAL + 4/4 manual + 2/2 UX. **No silent deferral** (Option 3 hybrid no-silent-slip discipline honored throughout).
**ADRs**: ADR-014 (UI Lifecycle Variant, drafted 2026-06-08 status `proposed`; ratified 2026-06-08 status `accepted`; Article XII landed in principles.md `1.2.0` -> `1.3.0` commit `55b05cb`).
**SDD-032**: DONE (4 deferred LOCKED REQUIRED items from Sprint 6 close commit `4a6941c` fully closed: SDD-019.R7 + SDD-019.R8 + SDD-020.R6 + SDD-020.R8; lock surface preserved against `524872b` + `8eb564d`).
**SDD-018**: DONE (variant validator shipped at `schema_lint.check_validation_variant`; templates carry stubs; state-dashboard retroactive-demo migration committed cleanly as the SDD-018 proof case; authoring guide at `docs/UI-LIFECYCLE-VARIANT.md`).
**SDD-033**: DONE (pulled in at F-09 close; HOST-INTEGRATION.md `.gitignore` Conflict Protection section appended; closed SDD-027.R12).
**SDD-034**: filed P3 unscheduled (dedup content-shingle upgrade; surfaced at F-10 pass 1 Article XI live contention test as the one known heuristic limitation).
**PI-4 carry-over**: domain-skill annotations and GH Actions Node.js bump NOT pulled in -- carried forward to Sprint 8 or beyond.
**Article XI live contention test**: PASS (first real-world test, observed at F-10 pass 1 when SDD-018 entered CLARIFY; gate fired correctly; grandfather correctly excluded SDD-018 per 2026-06-08 cutover; dedup writers auto-fired; ledger event recorded; SDD-034 filed for one surfaced heuristic gap).
**Retro (one paragraph)**: Sprint 7 shipped two complete features (SDD-032
Sprint 6 completion bundle; SDD-018 UI Lifecycle Variant) and absorbed two
unplanned constitutional refinements (Article XI's first live contention
test; the owner's mid-flight Level-2 ratification of Article XII before
sprint close). F-09 closed the 4 deferred LOCKED REQUIRED items from
Sprint 6 in a single linear single-session pass (per Option 3 hybrid
no-silent-slip discipline) -- 7/7 REQUIRED + 2/2 OPTIONAL, +14 tests,
lock-surface preserved against the SDD-019 + SDD-020 base commits. F-10
ran as a deliberate two-pass design (pass 1 = scaffold + CLARIFY question
battery + Article XI live contention test; pass 2 = spec + validation +
plan + tasks + ADR-014) which separated the constitutional design (ADR
text) from the runtime change cleanly. The Article XI live contention
test was the highest-value moment of F-10: the gate fired correctly under
real load, the dedup writers populated their artefacts (DEDUP-LOG.md got
its first real entry; per-spec-dir `dedup-scan.md` auto-written), and the
one heuristic gap (title-shingle vs content-shingle prior-art detection)
was surfaced and filed as SDD-034 without blocking the sprint. F-11
implemented in single-worker sequential mode (7 tasks, tight sequencing
T-018-02 -> T-018-04 -> T-018-06) and surfaced one durable framework
convention -- `status: blocked` as the CLARIFY-phase carrier -- that
landed in `docs/UI-LIFECYCLE-VARIANT.md`. The owner ratified Article XII
mid-flight (commit `55b05cb`) before sprint close, refining the Option 3
hybrid model into a "ratify-the-controlling-ADR-then-close" pattern --
the sprint close itself happens against an already-binding Article XII
rather than a `proposed` ADR. Net: 17 commits this sprint chain + 1 close
commit, 259 -> 305 tests (+46), 1 ADR drafted-then-accepted, 1
constitutional amendment (Article XII, principles.md `1.2.0` -> `1.3.0`),
0 silently deferred REQUIRED items.

### Sprint 4 -- ADO/GitHub Bridge + Model Upgrade Discipline -- CLOSED 2026-06-08
**Status**: **CLOSED 2026-06-08** (F-15 local close; owner approval required before push remains pending)
**Closed**: 2026-06-08
**Spec dirs**:
- `specs/2026-06-08-ado-github-bridge/` (SDD-022)
- `specs/2026-06-08-model-upgrade-discipline/` (SDD-015)
**Sprint kickoff**: [`../../feature-prompts/SPRINT-08-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-08-KICKOFF.prompt.md) (authored 2026-06-08 commit `e26b032`)
**Sprint chain (chronological, on master)**:
- `df5a957` spec(sdd-022): scaffold ADO GitHub bridge clarify
- `3d3fa89` spec(sdd-022): finalize ADO GitHub bridge plan
- `c3ac624` spec(sdd-015): finalize model upgrade discipline plan
- `0b47def` feat(sprint-8): implement F-14 sync and model-upgrade gates
- `a2c1476` docs: accept ADR-016 governance unblock
- `dbfe3c6` close(sprint-8-f-14): mark implementation done
- `fd804a6` close(sprint-8): close F-15 and author Sprint 9 kickoff (local only until owner pre-push approval)
**Tests**: 305 -> 331 (+26 net; 2 skipped platform-conditional baseline preserved). F-15 verification: `python -m pytest spec-driven-development/ --tb=no -q` -> 331 passed, 2 skipped; `python spec-driven-development/cli/schema_lint.py` -> Schema lint clean.
**Validation**: SDD-022 16/16 REQUIRED + 1/3 OPTIONAL; SDD-015 12/12 REQUIRED + 1/3 OPTIONAL + 1/2 manual. No REQUIRED item was deferred or loosened.
**ADRs**: ADR-016 (Model Upgrade Protocol Cross-Reference, accepted 2026-06-08 before `constitution/decision-policy.md` edit).
**SDD-022**: DONE (`/taskstoissues` stdlib CLI; `tasks.md` remains authoritative; explicit dry-run default; apply mode requires `GITHUB_TOKEN`/`GH_TOKEN`; generated-region idempotency; conflict reports are non-mutating; GitHub live provider plus ADO dry-run provider boundary).
**SDD-015**: DONE (`docs/MODEL-UPGRADE-PROTOCOL.md`; no-network fixture-driven A/B compare CLI; pricing/workload fixtures; cost and quality delta reports; ADR-backed `decision-policy.md` cross-reference).
**SDD-034**: carried forward. The content-shingle dedup upgrade was not pulled into Sprint 8; the Sprint 7 heuristic limitation remains visible and non-blocking.
**PI-4 carry-over**: domain-skill annotations and GitHub Actions Node.js bump carried forward. The dirty workflow/Azure work present during F-15 was unrelated and intentionally preserved, not staged.
**Article XI live contention observation**: No new CLARIFY/SPEC contention was observed during F-15. Sprint 8 reused the Sprint 7 lesson: required validation deferral is prohibited, and any governance blocker must stop the feature until owner approval is recorded. ADR-016 followed that pattern before SDD-015 closed.
**Retro (one paragraph)**: Sprint 8 proved the framework can ship an external-system bridge without weakening Article V: `/taskstoissues` stayed stdlib-only, no-network tests carried the default validation path, GitHub live writes are explicitly token-gated, and ADO remains a clean fast-follow provider shape instead of an untested SDK dependency. The model-upgrade work exposed a healthy governance stop: F-14 initially blocked on SDD-015 V-9, then resumed only after the owner accepted ADR-016, so the constitution cross-reference landed with approval rather than as a silent process shortcut. The sprint also reinforced a close discipline for future sprints: local close can be recorded when tests, schema lint, validation, backlog, state regeneration, and kickoff authoring are complete, but push remains gated on explicit owner approval. Net: 6 implementation/planning commits before F-15, 305 -> 331 tests, 1 accepted ADR, 0 silently deferred REQUIRED items, PI-5 remains active with Sprint 5 still to run.

### Sprint 5 -- Self-Review + Stakeholder Defense + Uniform Gates (planned)
**Items**: SDD-021, SDD-023, SDD-025.
**Status**: READY TO KICK OFF after owner approval/push decision for Sprint 8 close. Kickoff prompt: [`../../feature-prompts/SPRINT-09-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-09-KICKOFF.prompt.md).

---

## Notes for the next sprint lead

- PI-5 Sprint 2 (= overall Sprint 6) is the highest-CLARIFY-load sprint in
  PI-5 (SDD-019 + SDD-020 are both CLARIFY-tagged in BACKLOG). Budget a
  longer clarification round than Sprint 1 used.
- The PI-4 carry-over housekeeping items are P1 and P2 cosmetic; do not let
  them slip past Sprint 2 or they undermine the alpha-release readiness story.
- SDD-018 (Sprint 3) needs an explicit decision on ADR-vs-new-slash-command
  before SPEC. Bring the Architect in early.
