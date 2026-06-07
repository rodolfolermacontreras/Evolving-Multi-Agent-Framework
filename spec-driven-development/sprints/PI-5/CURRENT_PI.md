---
id: SDD-PI-5-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-06-06
sprint: PI-5
---

# PI-5: Brownfield Adoption + Anti-Conflict + Stakeholder Discipline

- Status: **Active** (Sprint 1 CLOSED 2026-06-06; 4 sprints remaining)
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

### Sprint 2 -- Anti-Conflict Gates + Carry-Over (planned)
**Items**: SDD-019, SDD-020, **SDD-027** (P1 host `.gitignore` protection;
filed from Sprint 5 Architect audit 2026-06-07), SDD-028 + SDD-029 (P2
audit housekeeping if capacity permits), PI-4 carry-over (domain-skill
annotations, GH Actions Node.js bump).
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

### Sprint 3 -- UI Lifecycle Variant (planned)
**Items**: SDD-018.
**Goal**: Define and ship the UI lifecycle variant (Article X relaxation
through delta entries).
**Status**: PLANNED.

### Sprint 4 -- ADO/GitHub Bridge + Model Upgrade Discipline (planned)
**Items**: SDD-022, SDD-015.
**Status**: PLANNED.

### Sprint 5 -- Self-Review + Stakeholder Defense + Uniform Gates (planned)
**Items**: SDD-021, SDD-023, SDD-025.
**Status**: PLANNED.

---

## Notes for the next sprint lead

- PI-5 Sprint 2 (= overall Sprint 6) is the highest-CLARIFY-load sprint in
  PI-5 (SDD-019 + SDD-020 are both CLARIFY-tagged in BACKLOG). Budget a
  longer clarification round than Sprint 1 used.
- The PI-4 carry-over housekeeping items are P1 and P2 cosmetic; do not let
  them slip past Sprint 2 or they undermine the alpha-release readiness story.
- SDD-018 (Sprint 3) needs an explicit decision on ADR-vs-new-slash-command
  before SPEC. Bring the Architect in early.
