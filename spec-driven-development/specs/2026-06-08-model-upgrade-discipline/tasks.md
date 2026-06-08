---
id: SDD-20260608MODELUPGRADE-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# Task List: Model Upgrade Discipline (SDD-015)

- Spec Reference: `./spec.md`
- Plan Reference: `./plan.md`
- Validation Reference: `./validation.md`
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Owner: Principal Software Developer
- Test baseline: >= 305
- Lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE

---

## Status Legend

- `pending`
- `in-progress`
- `done`
- `blocked`

---

## Batch Overview

| Batch | Tasks | Mode | Notes |
|-------|-------|------|-------|
| B1 | T-015-01 -> T-015-02 | Sequential | Protocol before fixtures so fixture choices trace to doc rules |
| B2 | T-015-03 -> T-015-05 | Sequential | Shared `cli/model_upgrade.py` surface and tests |
| B3 | T-015-06 | HITL-gated | Constitution cross-reference requires ADR acceptance or owner waiver |
| B4 | T-015-07 | Sequential close-out | Validation, schema_lint, full pytest, checkbox close |

---

## Task T-015-01: Author model-upgrade protocol

**Story**: [R1, R2, R6, R7, R8] Create the operating procedure
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md`
**Files Blocked**: `constitution/**`, dependency manifests, live model configuration
**Depends on**: NONE

### Description

Create the protocol document that explains trigger taxonomy, Level-2 routing, regression branch shape, representative workload, A/B workflow, cost capture, quality rubric, approval gate, rejection path, and how evidence maps into the existing Level-2 Friction Analysis template.

### Acceptance Criteria

- [ ] Defines full Level-2 triggers and minor patch log-only behavior.
- [ ] Requires `templates/level-2-decision.md` for in-scope upgrades.
- [ ] Documents branch naming and no-merge-before-approval behavior.
- [ ] Documents cost and quality evidence required before owner approval.
- [ ] Documents reject and owner-review outcomes.

### Verification

```powershell
Select-String -Path spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md -Pattern 'major version|vendor swap|model-family|role-critical|level-2-decision|model-upgrade/'
```

---

## Task T-015-02: Add workload and pricing fixtures

**Story**: [R4, R6] Commit representative no-network inputs
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/templates/model-upgrade-workload.json`, `spec-driven-development/templates/model-upgrade-pricing.json`
**Files Blocked**: `spec-driven-development/cli/model_upgrade.py`, live model configuration
**Depends on**: T-015-01

### Description

Create deterministic JSON fixtures. The workload fixture must include CLARIFY, SPEC, PLAN/TASKS, IMPLEMENT-report, and REVIEW-report scenarios derived from recent Sprint 7 and Sprint 8 artifacts. The pricing fixture must contain owner-editable placeholder prices and source notes.

### Acceptance Criteria

- [ ] Workload fixture has schema version and the five required scenario kinds.
- [ ] Pricing fixture has schema version, currency, model entries, and source notes.
- [ ] JSON formatting is stable and deterministic.
- [ ] No secrets, tokens, or live endpoint values are committed.

### Verification

```powershell
python -m json.tool spec-driven-development/templates/model-upgrade-workload.json > $null
python -m json.tool spec-driven-development/templates/model-upgrade-pricing.json > $null
```

---

## Task T-015-03: Implement CLI skeleton and branch naming

**Story**: [R3, R5, R10] Establish stdlib CLI shape
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Status**: done
**Files**: `spec-driven-development/cli/model_upgrade.py`, `spec-driven-development/cli/test_model_upgrade.py`
**Files Blocked**: dependency manifests, `constitution/**`
**Depends on**: T-015-02

### Description

Create `cli/model_upgrade.py` using the local CLI pattern: argparse, `main(argv)`, pathlib, custom expected-error exception, stderr for expected failures, and deterministic exit codes. Implement `branch-name` first with safe slug handling.

### Acceptance Criteria

- [ ] `main(argv)` is testable without subprocess.
- [ ] `branch-name --old X --new Y` prints `model-upgrade/<old>-to-<new>`.
- [ ] Unsafe characters are collapsed to safe ASCII hyphenated slugs.
- [ ] Empty identifiers fail with exit code 1 and stderr.
- [ ] `--help` output is clean.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_model_upgrade.py -k "branch or cli" -v --tb=short
```

---

## Task T-015-04: Implement no-network A/B compare reports

**Story**: [R4, R5, R6, R7] Compare captured old/new outputs deterministically
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Status**: done
**Files**: `spec-driven-development/cli/model_upgrade.py`, `spec-driven-development/cli/test_model_upgrade.py`
**Files Blocked**: live model APIs, third-party libraries
**Depends on**: T-015-03

### Description

Implement `compare` and `summarize`. `compare` reads the workload fixture, pricing fixture, and captured old/new output JSON files. It calculates cost deltas, aggregates quality rubric scores, and writes deterministic Markdown and JSON reports. It must not call model APIs or the network.

### Acceptance Criteria

- [ ] Reads workload, pricing, old-output, and new-output files.
- [ ] Writes stable `comparison.json` and `comparison.md` files.
- [ ] Calculates old/new/delta costs from committed pricing inputs.
- [ ] Aggregates quality rubric scores and recommendation.
- [ ] Produces `owner-review` when ambiguous quality wins are present.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_model_upgrade.py -k "compare or report or cost or quality" -v --tb=short
```

---

## Task T-015-05: Add stdlib and no-network guard tests

**Story**: [R10, R11] Protect Article V and deterministic validation
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Status**: done
**Files**: `spec-driven-development/cli/test_model_upgrade.py`
**Files Blocked**: dependency manifests
**Depends on**: T-015-04

### Description

Add tests that inspect imports and behavior. The tests should fail if `model_upgrade.py` imports third-party model, HTTP, benchmark, or data-analysis libraries, or if the comparison path attempts network access.

### Acceptance Criteria

- [ ] Import guard rejects `requests`, `httpx`, model SDKs, benchmark SDKs, `pandas`, and other third-party dependencies.
- [ ] No-network behavior is represented in tests.
- [ ] Tests prove fixture-driven comparison can run in a tmp_path.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_model_upgrade.py -k "import or network or fixture" -v --tb=short
```

---

## Task T-015-06: Add ADR-backed decision-policy cross-reference

**Story**: [R9] Reference protocol from constitution through safe governance path
**Type**: [S] sequential, HITL-gated
**Execution**: [HITL] owner/EM approval required before constitution edit
**Size**: S
**Status**: done
**Files**: `spec-driven-development/docs/ADR/016-model-upgrade-protocol-cross-reference.md`, `spec-driven-development/constitution/decision-policy.md`
**Files Blocked**: `spec-driven-development/constitution/principles.md`
**Depends on**: T-015-01

### Description

Draft ADR-016 explaining why `decision-policy.md` should reference `docs/MODEL-UPGRADE-PROTOCOL.md` as a Level-2 specialization. Apply the decision-policy cross-reference only after ADR-016 is accepted or the owner grants an explicit waiver. If approval is not available, stop as OWNER-ATTENTION with V-9 unchecked.

### Acceptance Criteria

- [x] ADR-016 exists if `decision-policy.md` is edited.
- [x] ADR-016 status is accepted or owner waiver is recorded before the constitution edit.
- [x] `decision-policy.md` references `docs/MODEL-UPGRADE-PROTOCOL.md` without weakening SDD-014 Friction Analysis requirements.
- [x] No edit is made to `constitution/principles.md`.

### Verification

```powershell
Select-String -Path spec-driven-development/constitution/decision-policy.md -Pattern 'MODEL-UPGRADE-PROTOCOL.md'
Select-String -Path spec-driven-development/docs/ADR/016-model-upgrade-protocol-cross-reference.md -Pattern 'Status: **accepted**|owner waiver'
```

---

## Task T-015-07: Close validation and artifact status

**Story**: [R11] Prove SDD-015 is done without REQUIRED deferral
**Type**: [S] sequential
**Execution**: [AFK] autonomous unless T-015-06 is blocked
**Size**: S
**Status**: done
**Files**: `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/validation.md`, `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/spec.md`, `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/tasks.md`
**Files Blocked**: unrelated spec dirs, SDD-035 files
**Depends on**: T-015-01, T-015-02, T-015-03, T-015-04, T-015-05, T-015-06

### Description

Run targeted tests, schema_lint, and full pytest. Check V-1 through V-12 only after evidence exists. Flip this feature's spec/tasks/validation frontmatter to `done` only if every REQUIRED item is checked. No REQUIRED item may be deferred.

### Acceptance Criteria

- [x] V-1 through V-12 are checked with evidence.
- [x] Targeted model-upgrade tests pass.
- [x] `python spec-driven-development/cli/schema_lint.py` exits 0.
- [x] Full pytest exits 0 with test count at or above baseline plus new tests.
- [x] This spec dir's statuses are updated to done only after checks pass.

### Verification

```powershell
python -m pytest spec-driven-development/cli/test_model_upgrade.py -v --tb=short
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```

---

## F-14 Dispatch Notes

- T-015-01 and T-015-02 are doc/data work and can proceed before SDD-022 implementation.
- T-015-03 through T-015-05 share `cli/model_upgrade.py` and should be handled sequentially.
- T-015-06 is the only HITL task. It must not be skipped because Sprint 8 success criteria require the decision-policy cross-reference.
- T-015-07 cannot close if T-015-06 is blocked.

