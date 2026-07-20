---
id: SDD-20260712BROWNFIELD-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-07-12
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# TASKS: SDD-058 -- Brownfield bootstrap correctness

- Spec: [spec.md](spec.md)
- Plan: [plan.md](plan.md)
- Validation: [validation.md](validation.md) -- **LOCKED / ACTIVE at TASKS**
- Architecture: [ADR-026](../../docs/ADR/026-transactional-brownfield-adoption.md) -- accepted
- Approval basis: owner-approved ADR-026/SPEC package, 2026-07-12, local ledger decision 5
- Baseline authority: Sprint 24 kickoff and Sprint EM evidence, **668 passed / 2 skipped / 6 subtests** using the repository venv
- Status: TASKS complete; implementation, worker dispatch, commit, push, and non-fixture mutation remain unauthorized

---

## Execution rules

- RED precedes GREEN for every behavior group. A RED task changes tests/fixtures only and records the intended failing assertion before its paired GREEN task may start.
- Every File Scope is an exact mutation allowlist. Anything in Blocked Paths is read-only even when needed for context.
- Every task modifies zero to three files. Shared-file tasks are serial. A task marked parallel-eligible may run only in its named batch after the SDD-049 preflight reports no overlap.
- Use exactly `C:\Training\Projects\Evolving-Multi-Agent-Framework\.venv\Scripts\python.exe` for Python checks. Do not accept a regression below 668 passed / 2 skipped.
- ADR-026 Appendix A is immutable. `brownfield-core@1` membership may be encoded and tested but not added to, removed from, globbed, substituted, or made silently optional.
- Fixture mutation is allowed only beneath positively identified disposable temporary roots. No task may mutate a real host or the real framework ledger/exec surfaces except the explicitly named local evidence/close tasks.
- The transaction path, compatibility/bootstrap integration, QA, owner approval, push, public CI, and close are serial.
- Stage 1 must be performed by a QA reviewer who did not implement. Stage 2 starts only after Stage-1 PASS and uses a different reviewer.
- No `--allow-overlap`, force bypass, shell execution, new dependency, constitution edit, ledger schema edit, broad-tree copy, contamination deletion, or unapproved real-host apply is allowed.

## Atomic task index

| Task ID | Type | Description | Exact File Scope | Deps | Role | Evidence | Parallel Eligible | Blocked Paths | Status |
|---------|------|-------------|------------------|------|------|----------|-------------------|---------------|--------|
| T-058-001 | [S][AFK] | Reconfirm locked contract, authoritative baseline, and no-real-host preimage before implementation. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md` | NONE | Principal Software Developer | V-01..V-04; baseline/gate outputs; checkout hashes | No | All production/tests/workflows; real hosts | complete |
| T-058-002 | [S][AFK] | Build disposable Node/Python git fixture factory and write the first no-real-host/cross-platform RED tests. | `spec-driven-development/cli/brownfield_test_fixtures.py`; `spec-driven-development/cli/test_brownfield_cross_platform.py` | T-058-001 | QA Engineer | RED-1; V-49..V-51, V-65 | No | Production modules; real checkout ledger/exec/proposal | complete |
| T-058-003 | [S][AFK] | Write inventory, evidence, path-safety, link, and redaction RED matrix. | `spec-driven-development/cli/test_brownfield_inventory.py` | T-058-002 | QA Engineer | RED-2A; V-45, V-47, V-48, V-51 | No | Production modules; fixture helper; real hosts | complete |
| T-058-004 | [S][AFK] | Implement read-only inventory/evidence/path primitives to make the inventory matrix GREEN. | `spec-driven-development/cli/brownfield_inventory.py`; `spec-driven-development/cli/test_brownfield_inventory.py` | T-058-003 | Developer | GREEN-2A; R-034, R-037; V-45, V-47, V-48 | No | All other production modules; fixture helper | complete |
| T-058-005 | [P][AFK] | Write proposal preservation, baseline, five-outcome refresh, and legacy-adoption RED tests. | `spec-driven-development/cli/test_brownfield_proposal.py` | T-058-004 | QA Engineer | RED-2B; V-05..V-09 | Batch B3 | Proposal production file; fixture helper; apply paths | complete |
| T-058-006 | [P][AFK] | Implement proposal/baseline/refresh/adoption behavior to make proposal tests GREEN. | `spec-driven-development/cli/brownfield_proposal.py`; `spec-driven-development/cli/test_brownfield_proposal.py` | T-058-005 | Developer | GREEN-2B; R-001..R-005; AC-01, AC-02 | Batch B4 | Manifest/identity/migration/transaction/bootstrap | complete |
| T-058-007 | [P][AFK] | Write exact Appendix A, graph/default-deny, seed/fingerprint, ledger-schema, and preview RED tests. | `spec-driven-development/cli/test_brownfield_manifest.py` | T-058-002 | QA Engineer | RED-3A; V-10..V-16, V-23..V-27 | Batch B3 | Manifest production file; ADR-026; schema.sql | complete |
| T-058-008 | [P][AFK] | Encode immutable `brownfield-core@1`, dependency closure, seeds, and six-category preview to GREEN. | `spec-driven-development/cli/brownfield_manifest.py`; `spec-driven-development/cli/test_brownfield_manifest.py` | T-058-007 | Developer | GREEN-3A; R-006..R-012, R-018..R-020; AC-03, AC-04, AC-06 | Batch B4 | ADR-026 Appendix A; schema.sql; broad source trees | complete |
| T-058-009 | [P][AFK] | Write Appendix B identity, remote sanitization, confirmation, renderer, and ownership RED tests. | `spec-driven-development/cli/test_brownfield_identity.py` | T-058-004 | QA Engineer | RED-3B; V-17, V-17A, V-18..V-22 | Batch B3 | Identity production file; framework config/instructions | complete |
| T-058-010 | [P][AFK] | Implement identity validation/sanitization and deterministic host renderers to GREEN. | `spec-driven-development/cli/brownfield_identity.py`; `spec-driven-development/cli/test_brownfield_identity.py` | T-058-009 | Developer | GREEN-3B; R-013..R-017 incl. R-016A; AC-05 | Batch B4 | ADR-026 Appendix B; framework identity files | complete |
| T-058-011 | [P][AFK] | Write installation/path classification, preservation, legacy, no-op, and host-link RED tests. | `spec-driven-development/cli/test_brownfield_migration.py` | T-058-006, T-058-008, T-058-010 | QA Engineer | RED-4A; V-39..V-44 | Batch B5 | Migration production file; fixture helper; host content | complete |
| T-058-012 | [P][AFK] | Implement read-only migration classification/planning and idempotent no-op behavior to GREEN. | `spec-driven-development/cli/brownfield_migration.py`; `spec-driven-development/cli/test_brownfield_migration.py` | T-058-011 | Developer | GREEN-4A; R-029..R-033; AC-09 | Batch B6 | Transaction/bootstrap; contamination deletion | complete |
| T-058-013 | [P][AFK] | Write bounded host-readiness composition, N/A, exits, wording, and quality-disclosure RED tests. | `spec-driven-development/cli/test_host_readiness.py` | T-058-008, T-058-010 | QA Engineer | RED-5; V-34..V-38A | Batch B5 | Readiness production file; framework doctor | complete |
| T-058-014 | [P][AFK] | Implement distinct structural/quality host readiness to GREEN without invoking framework doctor. | `spec-driven-development/cli/host_readiness.py`; `spec-driven-development/cli/test_host_readiness.py` | T-058-013 | Developer | GREEN-5; R-025..R-028 incl. R-028A; AC-08 | Batch B6 | `bootstrap.py` doctor local/CI implementation | complete |
| T-058-015 | [S][AFK] | Write approval, stage, backup, journal, interruption, rollback, recovery, and cleanup RED tests. | `spec-driven-development/cli/test_brownfield_transaction.py` | T-058-012, T-058-014 | QA Engineer | RED-6; V-22, V-24, V-26, V-28..V-33, V-53 | No | Transaction production file; real hosts | complete |
| T-058-016 | [S][AFK] | Implement the complete preview-bound transaction/recovery path to GREEN. | `spec-driven-development/cli/brownfield_transaction.py`; `spec-driven-development/cli/test_brownfield_transaction.py` | T-058-015 | Developer | GREEN-6; R-021..R-024, R-036; AC-07 | No | Compatibility/bootstrap; real hosts; active backups outside fixtures | complete |
| T-058-017 | [S][AFK] | Write canonical action, legacy syntax, exit/redaction, fixture-proof, and no-unsafe-route RED tests. | `spec-driven-development/cli/test_brownfield_cli.py` | T-058-006, T-058-008, T-058-010, T-058-012, T-058-014, T-058-016 | QA Engineer | RED-7; V-05, V-19, V-27, V-38, V-42, V-46..V-48, V-65 | No | `bootstrap.py`; compatibility production file; real hosts | complete |
| T-058-018 | [S][AFK] | Implement canonical compatibility service and thin bootstrap dispatcher; remove every reachable unsafe brownfield route. | `spec-driven-development/cli/brownfield_compat.py`; `spec-driven-development/cli/bootstrap.py`; `spec-driven-development/cli/test_brownfield_cli.py` | T-058-017 | Developer | GREEN-7; R-001, R-018..R-020, R-028, R-031, R-035, R-037, R-038, R-044; AC-01, AC-06, AC-08..AC-10, AC-12, AC-15 | No | Greenfield/host-link/setup/framework-doctor behavior; real hosts | complete |
| T-058-019 | [S][AFK] | Complete the full Node/Python scenario matrix and Windows/POSIX workflow wiring. | `spec-driven-development/cli/test_brownfield_cross_platform.py`; `.github/workflows/doctor.yml` | T-058-018 | QA Engineer | V-25, V-49..V-54A; R-039..R-041; AC-11 | No | Fixture helper interface; production behavior; cloud credentials | complete |
| T-058-020 | [S][AFK] | Run local regression, schema/origin/staledoc/governance, Article X, doctor, B-1/B-2, dependency, scope, and evidence-integrity gates. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`; `spec-driven-development/ledger/fleet.db` | T-058-019 | Principal Software Developer | V-55..V-60, V-63, V-64; >=668/2; genuine ledger outcomes | No | Production/test/workflow files; fabricated ledger rows | complete |
| T-058-021 | [S][AFK] | Perform independent Stage-1 spec-compliance review and re-review owning fixes until PASS. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/review-stage-1.md`; `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md` | T-058-020 | QA Engineer (reviewer A; no implementation) | Every R/AC/V; MISSING/EXTRA/WRONG; V-61, V-63..V-65 | No | Production edits; Stage-2 artifact | blocked |
| T-058-022 | [S][AFK] | After Stage-1 PASS, perform independent Stage-2 quality/security review and re-review owning fixes until APPROVED. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/review-stage-2.md`; `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md` | T-058-021 | Principal Cloud Security Architect (reviewer B) | Quality/security verdict after Stage 1; V-61 | No | Production edits; Stage-1 artifact; owner evidence | pending |
| T-058-023 | [S][HITL] | Present the exact pre-push package and record owner approval without pushing. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`; `spec-driven-development/exec/sprint-progress.md` | T-058-022 | Sprint Executive Manager | Exact diff/commit package, owner quote/time; first half of V-62 | No | Git push; implementation; generated exec surfaces | pending |
| T-058-024 | [S][HITL] | Push only the owner-approved exact package to `origin/master`. | NONE (external git operation only) | T-058-023 | Principal Software Developer | Remote SHA equals approved package; no pre-approval push | No | All file edits; force push; alternate branch | pending |
| T-058-025 | [S][HITL] | Observe public Windows/POSIX CI/B-4 and record real run IDs/URLs/results. | `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`; `spec-driven-development/exec/sprint-progress.md` | T-058-024 | QA Engineer | Green public run; V-54, V-62 | No | Workflow edits; retry-result fabrication; DONE markers | pending |
| T-058-026 | [S][HITL] | Run DONE completeness and close SDD-058 only after all 70 validation items are evidenced. | `spec-driven-development/backlog/BACKLOG.md`; `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`; `spec-driven-development/exec/sprint-progress.md` | T-058-025 | Principal Product Manager + Principal Software Developer | 70/70 REQUIRED; AC-01..AC-15 accepted; SDD-058 DONE | No | PI/Sprint close; generated exec surfaces | pending |
| T-058-027 | [S][HITL] | Close Sprint 24 and record the authorized PI-9 close handoff without pre-closing or opening a successor. | `spec-driven-development/sprints/PI-9/CURRENT_PI.md`; `spec-driven-development/constitution/roadmap.md`; `spec-driven-development/exec/sprint-progress.md` | T-058-026 | Sprint Executive Manager | Sprint 24 close evidence and project-EM handoff | No | Generated exec surfaces; successor PI/sprint; unrelated backlog | pending |
| T-058-028 | [S][AFK] | Regenerate and verify the three executive surfaces from authoritative closed artifacts. | `spec-driven-development/exec/state.md`; `spec-driven-development/exec/state.html`; `spec-driven-development/exec/work-index.md` | T-058-027 | Principal Software Developer | Canonical builder diff; final schema/doctor checks | No | Hand edits; source artifacts; push without any newly required approval | pending |

## Batch and overlap schedule

- **B0:** T-058-001, serial. One task; no overlap pair. Checkpoint:
	validation locked, baseline and preimage recorded.
- **B1:** T-058-002, serial. One task; no overlap pair. Checkpoint:
	fixture interface frozen and intended RED recorded.
- **B2:** T-058-003 -> T-058-004, serial because they share the inventory test
	file. Checkpoint: inventory/path API frozen and GREEN.
- **B3:** T-058-005, T-058-007, T-058-009, parallel with empty pairwise
	intersections. Checkpoint: three focused RED commands recorded before their
	production edits.
- **B4:** T-058-006, T-058-008, T-058-010, parallel with empty pairwise
	intersections. Checkpoint: proposal, manifest, and identity suites GREEN;
	schemas frozen.
- **B5:** T-058-011, T-058-013, parallel with empty pairwise intersections.
	Checkpoint: migration/readiness RED evidence recorded.
- **B6:** T-058-012, T-058-014, parallel with empty pairwise intersections.
	Checkpoint: migration/readiness suites GREEN; callbacks frozen.
- **B7:** T-058-015 -> T-058-016, serial because they share the transaction test
	file. Checkpoint: transaction/recovery suite GREEN.
- **B8:** T-058-017 -> T-058-018, serial because they share the CLI test file and
	bootstrap is the integration point. Checkpoint: canonical CLI/adapter suite
	GREEN and unsafe routes absent.
- **B9:** T-058-019, serial. Checkpoint: cross-stack/platform matrix ready.
- **B10:** T-058-020, serial. Checkpoint: all local gates green at or above the
	authoritative baseline.
- **B11:** T-058-021 -> T-058-022, serial because both touch validation and the
	reviewer order is mandatory. Checkpoint: Stage-1 PASS, then Stage-2 APPROVED.
- **B12:** T-058-023 -> T-058-024 -> T-058-025, serial HITL because owner
	approval, push, and public CI cannot overlap. Checkpoint: exact package
	approved/pushed and public CI green.
- **B13:** T-058-026 -> T-058-027 -> T-058-028, serial close because lifecycle
	state and generated outputs are ordered. Checkpoint: feature and sprint close
	truthfully and exec surfaces regenerate.

Parallel preflight input is the task IDs plus the exact File Scope strings in the index. B3, B4, B5, and B6 each have zero pairwise overlaps under `fleet.detect_file_overlaps`; all other batches are deliberately serial. A correction to `brownfield_test_fixtures.py`, any frozen schema, or a shared test file immediately suspends affected parallel work and creates a new serial checkpoint.

## Task details

## Task T-058-001: Lock contract and capture pre-implementation evidence

**Story**: [US-13] Gate ordering and validation lock are provable.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`
**Files Blocked**: all production/test/workflow paths; every non-fixture host
**Depends on**: NONE
**Role**: Principal Software Developer
**Evidence**: V-01..V-04 plus exact baseline/gate commands and checkout preimage hashes

### Description

Confirm the lock metadata, accepted ADR/SPEC chronology, authoritative 668/2/6 baseline, and clean no-real-host preimage. Do not edit implementation files or weaken the floor.

### Acceptance Criteria

- [ ] Validation is LOCKED / ACTIVE at TASKS with V-01, V-02, and V-04 checked only from existing evidence; V-03 remains unchecked until history evidence is durable.
- [ ] Exact commands/output and protected checkout hashes are recorded before the first RED edit.

### Verification

Run only the kickoff-required focused gates unless a full baseline rerun is necessary. If the exact venv full run differs from 668 passed / 2 skipped, stop with exact command/output.

## Task T-058-002: Create isolated cross-stack fixture RED foundation

**Story**: [US-11] Node and Python hosts prove behavior without touching a real host.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_test_fixtures.py`, `spec-driven-development/cli/test_brownfield_cross_platform.py`
**Files Blocked**: production modules; real framework ledger/exec/proposal; every non-temp host
**Depends on**: T-058-001
**Role**: QA Engineer
**Evidence**: RED-1; V-49, V-50, V-51, V-65

### Description

Create stdlib temporary committed Node/Express and Python repositories, local bare remotes, sentinel-bound disposable roots, newline/mode variants, snapshots, and failure injectors. Add tests that fail because the verified-fixture production API does not exist.

### Acceptance Criteria

- [ ] Both realistic stacks and explicit `main`/`trunk` branch evidence are deterministic and offline.
- [ ] Negative cases reject the real checkout, ancestors, siblings, links, copied sentinels, and temp-looking names before mutation.

### Verification

Run the focused cross-platform test module with the exact repository venv and record the intended missing-API failure.

## Task T-058-003: Specify inventory and path security in RED

**Story**: [US-10] Unsafe paths and sensitive evidence fail closed.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_inventory.py`
**Files Blocked**: `brownfield_inventory.py`; fixture helper; real hosts
**Depends on**: T-058-002
**Role**: QA Engineer
**Evidence**: RED-2A; V-45, V-47, V-48, V-51

### Description

Write the complete lexical/resolved path matrix, committed-root/evidence tests, secret-redaction canaries, link/reparse handling, and actionable error contract before production code.

### Acceptance Criteria

- [ ] Applicable Windows/POSIX absolute, traversal, `.git`, reserved/control, case-fold, link, and containment cases are covered.
- [ ] The focused suite fails only because inventory/path behavior is absent.

### Verification

Run only `test_brownfield_inventory.py`; save the intended RED assertion/output.

## Task T-058-004: Implement inventory and safe-path core

**Story**: [US-10] Read-only evidence and path boundaries are deterministic.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_inventory.py`, `spec-driven-development/cli/test_brownfield_inventory.py`
**Files Blocked**: every other SDD-058 production module; fixture helper
**Depends on**: T-058-003
**Role**: Developer
**Evidence**: GREEN-2A; R-034, R-037; AC-10; V-45, V-47, V-48

### Description

Implement immutable evidence/observation dataclasses, committed-root validation, non-following inventory, remote redaction before object creation, and shared fail-closed path primitives.

### Acceptance Criteria

- [ ] Inventory is read-only, stable, POSIX-relative, secret-free, and uses tokenized git commands.
- [ ] Every malicious path case fails before unsafe access or mutation with no traceback.

### Verification

Run the same focused command from T-058-003 and record GREEN.

## Task T-058-005: Specify proposal preservation and refresh in RED

**Story**: [US-1, US-2] Apply preserves reviewed bytes and refresh is explicit.
**Type**: [P] parallelizable in B3
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_proposal.py`
**Files Blocked**: proposal production file; fixture helper; apply/transaction files
**Depends on**: T-058-004
**Role**: QA Engineer
**Evidence**: RED-2B; V-05..V-09

### Description

Write apply non-invocation spies, complete baseline schema/hash tests, five-outcome truth table, recoverability/conflict tests, invalid baseline matrix, and legacy baseline-adoption preview tests.

### Acceptance Criteria

- [ ] Human-edited proposal/baseline bytes are explicit test preimages.
- [ ] The suite fails for absent SDD-058 proposal behavior, not fixture defects.

### Verification

Run `test_brownfield_proposal.py` and record intended RED.

## Task T-058-006: Implement proposal and baseline core

**Story**: [US-1, US-2] Proposal decisions survive apply and refresh conflicts.
**Type**: [P] parallelizable in B4
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_proposal.py`, `spec-driven-development/cli/test_brownfield_proposal.py`
**Files Blocked**: manifest/identity/migration/transaction/bootstrap modules
**Depends on**: T-058-005
**Role**: Developer
**Evidence**: GREEN-2B; R-001..R-005; AC-01, AC-02; V-05..V-09

### Description

Implement proposal generation, lossless baseline validation, exact three-way refresh classification, conflict resolution requirements, recoverable proposal updates, and explicit legacy baseline adoption. Normal apply must remain absent.

### Acceptance Criteria

- [ ] All five outcomes and invalid/legacy behavior match ADR-026 exactly.
- [ ] No TODO/content heuristic or implicit regeneration path exists.

### Verification

Run the paired focused test command and record GREEN.

## Task T-058-007: Specify immutable bundle and preview in RED

**Story**: [US-3, US-4, US-6] Only approved assets and clean seeds enter a host.
**Type**: [P] parallelizable in B3
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_manifest.py`
**Files Blocked**: manifest production file; ADR-026; `schema.sql`; source trees
**Depends on**: T-058-002
**Role**: QA Engineer
**Evidence**: RED-3A; V-10..V-16, V-23..V-27

### Description

Write structural equality against every Appendix A member, graph/path/hash/renderer failures, unlisted canary prevention, roster/seed/fingerprint/schema proof, and exact six-category deterministic preview tests.

### Acceptance Criteria

- [ ] Appendix A membership is compared as a frozen exact set, including conditional fleet-worker membership semantics.
- [ ] Broad-copy-then-clean and every bypass fail structurally before preview.

### Verification

Run `test_brownfield_manifest.py` and record intended RED.

## Task T-058-008: Implement exact manifest, seeds, and preview

**Story**: [US-3, US-4, US-6] Default-deny installation is dependency-closed and auditable.
**Type**: [P] parallelizable in B4
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_manifest.py`, `spec-driven-development/cli/test_brownfield_manifest.py`
**Files Blocked**: ADR-026 Appendix A; `schema.sql`; broad source trees
**Depends on**: T-058-007
**Role**: Developer
**Evidence**: GREEN-3A; R-006..R-012, R-018..R-020; AC-03, AC-04, AC-06

### Description

Explicitly enumerate and validate `brownfield-core@1`, source hashes, renderers, dependencies, enabled condition, clean seeds, forbidden fingerprints, and canonical preview/hash. Never select by recursive tree copy.

### Acceptance Criteria

- [ ] Exact Appendix A equality and dependency closure pass with zero unlisted source reads.
- [ ] Fresh candidate state has positive seeds, unchanged schema, zero operational rows, and no framework fingerprints.

### Verification

Run the paired focused suite and record GREEN.

## Task T-058-009: Specify identity and renderer contract in RED

**Story**: [US-5] Host identity is confirmed, provenance-bearing, and secret-free.
**Type**: [P] parallelizable in B3
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_identity.py`
**Files Blocked**: identity production file; framework config/instructions
**Depends on**: T-058-004
**Role**: QA Engineer
**Evidence**: RED-3B; V-17, V-17A, V-18..V-22

### Description

Write exact Appendix B type/order/null/confirmation tests, missing/ambiguous blocking, remote credential sanitization, deterministic Node/Python rendering, token substitution, and existing identity ownership cases.

### Acceptance Criteria

- [ ] Every Appendix B field and exact project-config key order is covered.
- [ ] Secret canaries never enter any expected output or error assertion.

### Verification

Run `test_brownfield_identity.py` and record intended RED.

## Task T-058-010: Implement identity validation and host renderers

**Story**: [US-5] Generated instructions/config describe the host, never the framework.
**Type**: [P] parallelizable in B4
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_identity.py`, `spec-driven-development/cli/test_brownfield_identity.py`
**Files Blocked**: ADR-026 Appendix B; framework identity files; free-form replacement
**Depends on**: T-058-009
**Role**: Developer
**Evidence**: GREEN-3B; R-013..R-017 including R-016A; AC-05

### Description

Implement exact identity dataclasses/schema, confirmation rules, sanitization before object creation, bounded renderer registry, deterministic UTF-8/LF project config/instructions/constitution/rosters/seeds, and host-owned replacement classification inputs.

### Acceptance Criteria

- [ ] Missing/ambiguous/unconfirmed identity blocks before preview.
- [ ] Equivalent confirmed inputs render byte-identically without framework identity, secrets, TODOs, or temp roots.

### Verification

Run the paired focused suite and record GREEN.

## Task T-058-011: Specify migration and idempotence in RED

**Story**: [US-9] Existing and contaminated hosts are classified and preserved.
**Type**: [P] parallelizable in B5
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_migration.py`
**Files Blocked**: migration production file; fixture helper; host content
**Depends on**: T-058-006, T-058-008, T-058-010
**Role**: QA Engineer
**Evidence**: RED-4A; V-39..V-44

### Description

Write all eight installation and seven path classes, precedence, contamination preservation, explicit migration, safe legacy behavior inputs, no-op rerun, managed drift, and symlink/junction guidance tests.

### Acceptance Criteria

- [ ] Unknown/modified/history bytes are snapshotted and required to survive.
- [ ] No expected plan contains a contamination-delete operation.

### Verification

Run `test_brownfield_migration.py` and record intended RED.

## Task T-058-012: Implement migration classification and planning

**Story**: [US-9] Migration is inventory-first, non-destructive, and idempotent.
**Type**: [P] parallelizable in B6
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_migration.py`, `spec-driven-development/cli/test_brownfield_migration.py`
**Files Blocked**: transaction/bootstrap modules; contamination deletion
**Depends on**: T-058-011
**Role**: Developer
**Evidence**: GREEN-4A; R-029..R-033; AC-09; V-39..V-44

### Description

Implement deterministic receipt/hash-first classification and read-only migration planning. Preserve all unlisted/unknown content, require explicit migration for existing installs, detect links without traversal, and return semantic no-op for unchanged managed state.

### Acceptance Criteria

- [ ] Every class/reason/precedence is stable and exact.
- [ ] No-op produces no operation requiring backup, journal, receipt, or ledger change.

### Verification

Run the paired focused suite and record GREEN.

## Task T-058-013: Specify bounded host readiness in RED

**Story**: [US-8] Host readiness is truthful and distinct from framework health.
**Type**: [P] parallelizable in B5
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_host_readiness.py`
**Files Blocked**: readiness production file; framework doctor
**Depends on**: T-058-008, T-058-010
**Role**: QA Engineer
**Evidence**: RED-5; V-34..V-38A

### Description

Write exact structural checker composition, explicit framework N/A rows, 0/1/2/3 exits, bounded success wording, staged structural-only behavior, and disclosed token-array quality execution tests.

### Acceptance Criteria

- [ ] Framework doctor cannot satisfy or emit host readiness.
- [ ] Apply-time tests prove quality commands are not run.

### Verification

Run `test_host_readiness.py` and record intended RED.

## Task T-058-014: Implement host readiness

**Story**: [US-8] A bounded PASS means only the approved portable checks passed.
**Type**: [P] parallelizable in B6
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/host_readiness.py`, `spec-driven-development/cli/test_host_readiness.py`
**Files Blocked**: existing framework doctor local/CI paths
**Depends on**: T-058-013
**Role**: Developer
**Evidence**: GREEN-5; R-025..R-028 including R-028A; AC-08

### Description

Implement structural/final/quality reports, exact check set, N/A rows, exit mapping, disclosure, no-shell subprocess execution, and distinct `main(argv) -> int` host-doctor entry.

### Acceptance Criteria

- [ ] Structural readiness covers every approved portable check and never runs host quality.
- [ ] Quality mode discloses policy and treats confirmed not-configured as N/A.

### Verification

Run the paired focused suite and record GREEN.

## Task T-058-015: Specify transaction and recovery in RED

**Story**: [US-7] Every approved mutation is staged, backed up, journaled, and recoverable.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_transaction.py`
**Files Blocked**: transaction production file; real hosts
**Depends on**: T-058-012, T-058-014
**Role**: QA Engineer
**Evidence**: RED-6; V-22, V-24, V-26, V-28..V-33, V-53

### Description

Write exact preview authorization, same-volume stage, complete backup, write-ahead states, per-operation interruption points, atomic replace, verified rollback, exit-3 retention/recovery, cleanup, metadata, locking, and stale-input tests.

### Acceptance Criteria

- [ ] Failure injection spans every prepared/applied/verified boundary and representative operation.
- [ ] Tests assert proposal and unrelated host bytes remain exact.

### Verification

Run `test_brownfield_transaction.py` and record intended RED.

## Task T-058-016: Implement serial transaction/recovery engine

**Story**: [US-7] Failure leaves verified original state or explicit retained recovery state.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_transaction.py`, `spec-driven-development/cli/test_brownfield_transaction.py`
**Files Blocked**: compatibility/bootstrap modules; real hosts; unrelated backups
**Depends on**: T-058-015
**Role**: Developer
**Evidence**: GREEN-6; R-021..R-024, R-036; AC-07

### Description

Implement authorization, preflight, complete stage/structural callback, backup, durable journal, per-path promotion, hash-based unknown-state resolution, verified rollback, recovery-required retention, and explicit cleanup.

### Acceptance Criteria

- [ ] No mutation precedes validated stage, complete backup, and flushed preimage journal.
- [ ] Every failure proves all-or-nothing verified restoration or deterministic exit 3 with retained evidence.

### Verification

Run the paired focused suite and record GREEN.

## Task T-058-017: Specify canonical compatibility and CLI in RED

**Story**: [US-1, US-6, US-8, US-9, US-15] All syntax reaches one safe path.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_cli.py`
**Files Blocked**: `brownfield_compat.py`; `bootstrap.py`; real hosts
**Depends on**: T-058-006, T-058-008, T-058-010, T-058-012, T-058-014, T-058-016
**Role**: QA Engineer
**Evidence**: RED-7; V-05, V-19, V-27, V-38, V-42, V-46..V-48, V-65

### Description

Write old/new parser/action tests, apply non-refresh spies, migration routing, exact exits/stderr, unsafe helper unreachability, owner-receipt binding, fixture API non-exposure, unexpected exception behavior, and no success overclaim.

### Acceptance Criteria

- [ ] Legacy syntax remains parse-compatible but cannot reach broad copy or auto-refresh.
- [ ] No CLI/environment input can forge fixture authorization.

### Verification

Run `test_brownfield_cli.py` and record intended RED.

## Task T-058-018: Integrate canonical service and thin bootstrap

**Story**: [US-1, US-6, US-8, US-9, US-15] Preview-first behavior is the only brownfield route.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/brownfield_compat.py`, `spec-driven-development/cli/bootstrap.py`, `spec-driven-development/cli/test_brownfield_cli.py`
**Files Blocked**: greenfield/host-link/setup/framework-doctor contracts; real hosts
**Depends on**: T-058-017
**Role**: Developer
**Evidence**: GREEN-7; R-001, R-018..R-020, R-028, R-031, R-035, R-037, R-038, R-044

### Description

Implement one orchestration service and thin parser/formatter, explicit actions, corrected legacy mapping, owner-versus-fixture authorization, exact exit propagation, adoption receipt, and removal of every reachable unsafe brownfield call. Preserve unrelated bootstrap behavior.

### Acceptance Criteria

- [ ] Apply reads existing reviewed inputs and never invokes inventory-driven proposal generation/refresh.
- [ ] No broad-tree copy, force bypass, public fixture switch, shell interpolation, or framework-doctor readiness path remains reachable.

### Verification

Run CLI, existing bootstrap, and all focused SDD-058 suites with the exact venv.

## Task T-058-019: Prove cross-platform end-to-end behavior

**Story**: [US-11] Equivalent Node/Python behavior runs on Windows and POSIX.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/cli/test_brownfield_cross_platform.py`, `.github/workflows/doctor.yml`
**Files Blocked**: fixture helper interface; production files; credentials/cloud actions
**Depends on**: T-058-018
**Role**: QA Engineer
**Evidence**: V-25, V-49..V-54A; R-039..R-041; AC-11

### Description

Complete every SPEC 9.1 cell, semantic preview comparison, LF/CRLF and UTF-8/LF proof, permission/link/rename equivalents, failures/recovery, rerun/migration, and workflow matrix for `ubuntu-latest` and `windows-latest`.

### Acceptance Criteria

- [ ] All scenario cells and platform-neutral class matrices are represented without absolute temp roots.
- [ ] Workflow remains read-only, credential-free, and invokes focused SDD-058 tests before CI doctor.

### Verification

Run the focused cross-platform suite locally where applicable; validate workflow syntax through existing repository tests. Public evidence waits for T-058-025.

## Task T-058-020: Run complete local quality and governance gates

**Story**: [US-12, US-13] The exact implementation is regression-free and evidence-backed.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`, `spec-driven-development/ledger/fleet.db`
**Files Blocked**: production/tests/workflow; fabricated ledger rows; weakened checks
**Depends on**: T-058-019
**Role**: Principal Software Developer
**Evidence**: V-55..V-60, V-63, V-64; B-1/B-2; authoritative regression floor

### Description

Record focused RED/GREEN commands, dependency/module-boundary review, exact full suite, schema/origin/staledoc/governance, `git diff --check`, Article X 3/3, strict local doctor, genuine Sprint 24 ledger outcomes, TDD gate, DONE completeness, protected preimage hashes, and scope history.

### Acceptance Criteria

- [ ] Full exact-venv suite is at least 668 passed / 2 skipped with no weakened/removed test.
- [ ] Every local gate is green and all ledger/evidence records are genuine.

### Verification

Run the commands named by V-57..V-60. Stop and report exact command/output on any baseline difference or failed gate.

## Task T-058-021: Stage-1 spec-compliance review

**Story**: [US-13] Independent compliance review precedes quality review.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/review-stage-1.md`, `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`
**Files Blocked**: all production files; Stage-2 report
**Depends on**: T-058-020
**Role**: QA Engineer reviewer A, not an implementer
**Evidence**: every R/AC/V; V-61, V-63..V-65
**Status**: blocked -- two unresolved WRONG findings in [review-stage-1.md](review-stage-1.md)

### Description

Independently classify only MISSING/EXTRA/WRONG against all 46 requirement IDs, 15 ACs, 70 validation IDs, Appendix A/B, no-real-host proof, and both platform artifacts. Return findings to each owning implementation task; re-review after fixes before PASS.

### Acceptance Criteria

- [ ] Zero orphan requirement, acceptance, or validation identifier remains.
- [ ] Stage-1 PASS timestamp and evidence precede any Stage-2 work.

### Verification

Run traceability scripts/checks and all relevant focused commands; record a formal PASS only after every finding is re-reviewed.

## Task T-058-022: Stage-2 quality and security review

**Story**: [US-13] A different reviewer validates quality only after compliance PASS.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/review-stage-2.md`, `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`
**Files Blocked**: all production files; Stage-1 report; owner evidence
**Depends on**: T-058-021
**Role**: Principal Cloud Security Architect reviewer B
**Evidence**: V-61; critical/important/suggestion findings and re-review

### Description

Review dependency direction, path/secret controls, TOCTOU and journal durability, rollback certainty, authorization, no-shell behavior, determinism, performance, maintainability, and test quality. Return fixes to owning tasks and re-review before APPROVED.

### Acceptance Criteria

- [ ] Reviewer identity differs from Stage 1 and no review starts before Stage-1 PASS.
- [ ] No critical or unresolved important issue remains at approval.

### Verification

Re-run affected focused tests and complete local gates after any fix; record final APPROVED verdict.

## Task T-058-023: Obtain exact-package owner approval

**Story**: [US-14] Owner approves the exact package before any push.
**Type**: [S] sequential
**Execution**: [HITL] human approval required
**Size**: S
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`, `spec-driven-development/exec/sprint-progress.md`
**Files Blocked**: git push; production edits; generated exec surfaces
**Depends on**: T-058-022
**Role**: Sprint Executive Manager
**Evidence**: exact diff/package identifier, owner quote, timestamp; V-62 pre-push half

### Description

Present a concise exact package with local gates and review results. Record approval only from a real owner response. Any post-approval byte change invalidates approval and returns to local gates/reviews.

### Acceptance Criteria

- [ ] Approval identifies the exact immutable package and explicitly precedes push.
- [ ] No inferred, bundled, or fabricated approval is recorded.

### Verification

Compare the approved package identifier to the pending push SHA/diff and verify no intervening changes.

## Task T-058-024: Push the approved package

**Story**: [US-14] Only the approved package reaches the public remote.
**Type**: [S] sequential
**Execution**: [HITL] external write
**Size**: S
**Files**: NONE (external git operation only)
**Files Blocked**: every file edit; force push; alternate branch
**Depends on**: T-058-023
**Role**: Principal Software Developer
**Evidence**: local/remote SHA equality and push output

### Description

Push the exact owner-approved package to `origin/master` without rewriting history. Do not amend or include new bytes after approval.

### Acceptance Criteria

- [ ] Remote SHA equals the approved package.
- [ ] Push is absent from history/evidence before T-058-023 approval.

### Verification

Compare `HEAD`, approved SHA, and `origin/master` after the push.

## Task T-058-025: Verify public CI/B-4

**Story**: [US-14] Public Windows/POSIX evidence is green before DONE.
**Type**: [S] sequential
**Execution**: [HITL] observed external evidence
**Size**: S
**Files**: `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`, `spec-driven-development/exec/sprint-progress.md`
**Files Blocked**: workflow edits; fabricated/relabelled results; DONE markers
**Depends on**: T-058-024
**Role**: QA Engineer
**Evidence**: public run ID/URL, exact SHA, Windows/POSIX job results; V-54, V-62

### Description

Observe the public run for the exact approved SHA. Record actual results only. A failure returns to repair under the locked contract and requires a new exact-package approval before another push.

### Acceptance Criteria

- [ ] B-4 and both platform jobs are green for the exact SHA.
- [ ] Run IDs/URLs and observed statuses are recorded without inference.

### Verification

Inspect the public workflow details and match its commit SHA to T-058-024.

## Task T-058-026: Close SDD-058

**Story**: [US-1..US-15] The feature closes only with complete locked evidence.
**Type**: [S] sequential
**Execution**: [HITL] lifecycle close
**Size**: M
**Files**: `spec-driven-development/backlog/BACKLOG.md`, `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`, `spec-driven-development/exec/sprint-progress.md`
**Files Blocked**: PI/Sprint close; generated exec surfaces; unrelated backlog
**Depends on**: T-058-025
**Role**: Principal Product Manager and Principal Software Developer
**Evidence**: 70/70 validation items; AC-01..AC-15 acceptance; DONE completeness

### Description

Check only evidence-backed remaining validation items, run DONE completeness, accept all ACs, mark SDD-058 DONE, and append feature-close evidence. This task does not close Sprint 24 or PI-9.

### Acceptance Criteria

- [ ] All 70 REQUIRED validation IDs, including suffixes, are checked with real evidence.
- [ ] SDD-058 alone is marked DONE; no unrelated row/status changes.

### Verification

Run the canonical DONE checker plus schema lint and `git diff --check` on the exact close diff.

## Task T-058-027: Close Sprint 24 and hand off PI-9 close

**Story**: [US-14] Sprint close follows shipped feature and preserves PI authority.
**Type**: [S] sequential
**Execution**: [HITL] lifecycle close
**Size**: M
**Files**: `spec-driven-development/sprints/PI-9/CURRENT_PI.md`, `spec-driven-development/constitution/roadmap.md`, `spec-driven-development/exec/sprint-progress.md`
**Files Blocked**: generated exec surfaces; successor PI/sprint; unrelated backlog
**Depends on**: T-058-026
**Role**: Sprint Executive Manager
**Evidence**: Sprint 24 close record, all gates, report-up to project EM

### Description

Close Sprint 24 only after SDD-058 DONE, record the final-sprint result, and report the separately authorized PI-9 close execution upward. Do not invent a successor or pre-close another lifecycle unit.

### Acceptance Criteria

- [ ] Sprint 24 closure cites exact feature, baseline, approvals, and public CI evidence.
- [ ] PI-9 handling follows owner-authorized sequence and project-EM authority.

### Verification

Run schema/staledoc/governance checks and inspect the lifecycle markers for a single coherent current/closed state.

## Task T-058-028: Regenerate executive surfaces

**Story**: [US-14] Derived state reflects authoritative closure without hand edits.
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: `spec-driven-development/exec/state.md`, `spec-driven-development/exec/state.html`, `spec-driven-development/exec/work-index.md`
**Files Blocked**: all source artifacts; manual edits; unauthorized push
**Depends on**: T-058-027
**Role**: Principal Software Developer
**Evidence**: canonical builder output and final checks

### Description

Run the canonical state builder once, inspect only generated diffs, and verify the rendered lifecycle, task counts, links, and work index reflect the authoritative close.

### Acceptance Criteria

- [ ] All three files are command-generated and internally consistent.
- [ ] Final schema, stale-doc, governance, Article X, doctor, and diff checks remain green.

### Verification

Run the canonical builder with the exact venv, then the final focused checks. Do not push any post-approval close package unless its applicable owner approval gate is satisfied.

## Complete traceability matrix

- **T-058-001:** R-043; AC-13; V-01, V-02, V-03, V-04.
- **T-058-002:** R-039, R-041, R-044; AC-11, AC-15; V-49, V-50, V-51,
	V-65.
- **T-058-003/T-058-004:** R-034, R-037; AC-10; V-45, V-47, V-48,
	V-51.
- **T-058-005/T-058-006:** R-001..R-005; AC-01, AC-02; V-05..V-09.
- **T-058-007/T-058-008:** R-006..R-012 and R-018..R-020; AC-03, AC-04,
	AC-06; V-10..V-16 and V-23..V-27.
- **T-058-009/T-058-010:** R-013..R-017 including R-016A; AC-05; V-17,
	V-17A, V-18..V-22 including V-21A.
- **T-058-011/T-058-012:** R-029..R-033; AC-09; V-39..V-44.
- **T-058-013/T-058-014:** R-025..R-028 including R-028A; AC-08; V-34..
	V-38 including V-38A.
- **T-058-015/T-058-016:** R-021..R-024 and R-036; AC-07, AC-11; V-22,
	V-24, V-26, V-28..V-33 including V-31A, and V-53.
- **T-058-017/T-058-018:** R-001, R-018..R-020, R-028, R-031, R-035,
	R-037, R-038, R-044; AC-01, AC-06, AC-08..AC-10, AC-12, AC-15; V-05,
	V-19, V-27, V-38, V-42, V-46..V-48, V-55, V-56, V-65.
- **T-058-019:** R-036, R-039..R-041; AC-07, AC-11; V-25, V-49..V-54
	including V-54A.
- **T-058-020:** R-038, R-042, R-043; AC-12, AC-13; V-55..V-60, V-63,
	V-64.
- **T-058-021:** all R-001..R-044 including R-016A and R-028A; all AC-01..
	AC-15; all V-01..V-65 including suffixes, especially V-61 and V-63..V-65.
- **T-058-022:** R-043; AC-13; V-61.
- **T-058-023/T-058-024/T-058-025:** R-040, R-043; AC-11, AC-14; V-54,
	V-62.
- **T-058-026:** all requirements including suffixes; all acceptance criteria;
	all 70 REQUIRED validation items.
- **T-058-027/T-058-028:** R-043; AC-14; V-62, V-63, V-64.

Traceability totals are fixed: **46 requirement IDs** (`R-001` through `R-044` plus `R-016A` and `R-028A`), **15 acceptance criteria**, and **70 validation IDs** (`V-01` through `V-65` plus `V-17A`, `V-21A`, `V-31A`, `V-38A`, and `V-54A`). The matrix intentionally permits multiple owning tasks for integration evidence but permits zero orphans.

## Appendix A preservation record

T-058-007/T-058-008 must derive their frozen expected set directly from accepted ADR-026 Appendix A. The expected set includes every render, seed, agent, prompt, named skill, instruction condition, template/doc, CLI/ledger member, and all eight new SDD-058 modules exactly as accepted. Tests must reject additions, omissions, substitutions, globs, disabled-member deletion, source-hash drift, and whole-tree selection. No task in this file authorizes an Appendix A membership change.

## Handoff boundary

This TASKS artifact and the validation lock authorize only a later TDD implementation dispatch. They do not dispatch a worker, run implementation, commit, push, mutate a real host, approve the exact package, satisfy public CI, mark SDD-058 DONE, close Sprint 24, or close PI-9.
