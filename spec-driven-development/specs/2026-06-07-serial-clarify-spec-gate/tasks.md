---
id: SDD-20260607SERIAL-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Task List: Serial Gate on CLARIFY/SPEC (SDD-019)

- Feature: SDD-019
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Author: Principal Software Developer
- Date: 2026-06-07
- Test baseline: >= 213

---

## Task T-019-01: Implement lock-state scanner

**Story**: [R3, R2] Lock state derived from frontmatter; two independent per-phase locks
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/fleet.py
**Files Blocked**: cli/dedup.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: NONE

### Description

Add a `_scan_lock_state(specs_root)` function to `cli/fleet.py` that walks
`specs/` directories, parses frontmatter via `parse_frontmatter` (imported
from `cli/schema_lint.py`), and returns a dict with:
- `clarify_holder`: feature name holding the CLARIFY lock (or None)
- `spec_holder`: feature name holding the SPEC lock (or None)

CLARIFY lock = any clarification file in a spec dir with `status != done`.
SPEC lock = `spec.md` with `status == draft`.

### Acceptance Criteria

- [ ] Scanner correctly identifies CLARIFY lock holder from fixture spec dirs
- [ ] Scanner correctly identifies SPEC lock holder from fixture spec dirs
- [ ] Scanner returns None for both when no locks held
- [ ] Two features in different phases (one CLARIFY, one SPEC) both detected independently
- [ ] Reuses `parse_frontmatter` from `cli/schema_lint.py` (no parser duplication)

### Verification

```
python -m pytest cli/test_fleet.py -k "lock_scan" -v --tb=short
```

---

## Task T-019-02: Implement lock subcommands (acquire/release/status/force-release)

**Story**: [R4, R5, O2] Lock subcommands with force-release audit
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: cli/fleet.py
**Files Blocked**: cli/dedup.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-019-01

### Description

Add `fleet.py lock` subcommand group with four actions:
- `fleet.py lock acquire <feature>` -- explicitly acquire the lock for the
  feature's current phase (inferred from frontmatter state).
- `fleet.py lock release <feature>` -- release the lock.
- `fleet.py lock status` -- display current CLARIFY and SPEC lock holders
  plus queue contents.
- `fleet.py lock force-release <feature> --reason "..."` -- force-release
  with mandatory `--reason`; writes ledger row with `event_type =
  lock_force_released`, feature name, reason, and timestamp.

All subcommands follow CLI-PATTERN.md: `main(argv)` signature, argparse,
stdlib-only, exit codes 0/1.

### Acceptance Criteria

- [ ] `lock acquire` succeeds when no lock held; fails when lock held by another feature
- [ ] `lock release` succeeds for the lock holder; fails for non-holder
- [ ] `lock status` reports both lock holders and queue contents
- [ ] `lock force-release` requires `--reason`; omitting it exits non-zero
- [ ] `lock force-release` writes ledger row with event_type, feature, reason, timestamp
- [ ] All subcommands produce clean `--help` output

### Verification

```
python -m pytest cli/test_fleet.py -k "lock_acquire or lock_release or lock_status or lock_force" -v --tb=short
```

---

## Task T-019-03: Implement pre-dispatch gate check

**Story**: [R1, R2, R6, R9] Hard refusal when lock held by another feature
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/fleet.py
**Files Blocked**: cli/dedup.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-019-02

### Description

Before `fleet.py dispatch` executes a CLARIFY or SPEC phase task, call the
lock scanner. If the target phase lock is held by a different feature:
- Exit non-zero (exit code 1)
- Print message: "BLOCKED: {phase} lock held by '{holder_feature}'. Release
  or force-release before dispatching '{target_feature}'."

If the target phase is post-SPEC (`/plan`, `/tasks`, `/implement`, `/qa`,
`/retro`) or <3-file bug fix: proceed without check.

Intra-feature dispatch (same feature holds the lock) proceeds unrestricted.

### Acceptance Criteria

- [ ] Dispatch second CLARIFY feature while first holds lock -> exit 1 + message naming holder
- [ ] Dispatch second SPEC feature while first holds lock -> exit 1 + message naming holder
- [ ] Intra-feature parallel dispatch proceeds unrestricted
- [ ] Post-SPEC phase dispatch proceeds regardless of lock state
- [ ] <3-file bug fix dispatch proceeds regardless of lock state

### Verification

```
python -m pytest cli/test_fleet.py -k "gate" -v --tb=short
```

---

## Task T-019-04: Implement queue ordering

**Story**: [R7] Priority-weighted FIFO queue
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/fleet.py
**Files Blocked**: cli/dedup.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-019-03

### Description

When a feature requests a lock that is currently held:
- Add the request to a queue with: feature name, priority (from backlog),
  request timestamp.
- When the lock is released, grant it to the highest-priority queued feature
  (FIFO tiebreak for same priority).
- Queue state persisted as ledger event rows (`lock_queued`).

### Acceptance Criteria

- [ ] 3 features queue for CLARIFY lock; highest-priority released first
- [ ] Same-priority features break ties by FIFO timestamp
- [ ] Queue state visible via `lock status`
- [ ] Ledger contains `lock_queued` event for each queued request

### Verification

```
python -m pytest cli/test_fleet.py -k "queue" -v --tb=short
```

---

## Task T-019-05: Implement grandfather migration

**Story**: [R8] Existing open features not retroactively blocked
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/fleet.py
**Files Blocked**: cli/dedup.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-019-04

### Description

On first run with the serial gate active, any spec dir already in CLARIFY
or SPEC state is treated as a grandfathered lock holder. These features
are not blocked and do not need to explicitly acquire the lock. They hold
the lock implicitly until their phase completes.

Detection: compare spec dir frontmatter timestamps against the cutover
commit timestamp (first commit containing the gate logic).

### Acceptance Criteria

- [ ] Fixture with pre-existing open spec dirs in CLARIFY -> not blocked
- [ ] Fixture with pre-existing open spec dirs in SPEC -> not blocked
- [ ] New feature entering CLARIFY after cutover -> normal lock rules apply
- [ ] Mixed: one grandfathered + one new -> new feature blocked correctly

### Verification

```
python -m pytest cli/test_fleet.py -k "grandfather" -v --tb=short
```

---

## Task T-019-06: Add Article XI to constitution/principles.md

**Story**: [R5] Constitutional amendment via ADR
**Type**: [S] sequential
**Execution**: [HITL] human-needed (owner approval required)
**Size**: S
**Files**: constitution/principles.md
**Files Blocked**: cli/fleet.py, cli/dedup.py, cli/bootstrap.py
**Depends on**: T-019-05 + ADR-013 committed + owner approval

### Description

BLOCKED ON: ADR-013 committed (done in F-07) + owner approval of ADR-013.

Add Article XI "Cross-Feature Serial Gate at CLARIFY and SPEC" to
`constitution/principles.md`. Content per ADR-013 Decision section.
Bump version from 1.1.0 to 1.2.0. Ensure `schema_lint` accepts the new
version.

### Acceptance Criteria

- [ ] Article XI present in `constitution/principles.md`
- [ ] Version reads 1.2.0
- [ ] `schema_lint` exits 0
- [ ] No changes to Articles I-X

### Verification

```
python -m pytest cli/test_schema_lint.py -v --tb=short
python cli/schema_lint.py
```

---

## Task T-019-07: Full test suite + schema_lint regression check

**Story**: [R10, R11] No regression
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: (none -- verification only)
**Files Blocked**: (none)
**Depends on**: T-019-06

### Description

Run the full test suite and `schema_lint` to confirm no regressions.
Test count must be >= 213 baseline. All existing tests pass. All new
lock-related tests pass.

### Acceptance Criteria

- [ ] `pytest` exits 0 with >= 213 tests passed
- [ ] `schema_lint` exits 0
- [ ] No warnings or deprecations introduced

### Verification

```
python -m pytest spec-driven-development/cli/ -v --tb=short
python spec-driven-development/cli/schema_lint.py
```

---

## Dependency Graph

```
T-019-01 -> T-019-02 -> T-019-03 -> T-019-04 -> T-019-05 -> T-019-06 [HITL] -> T-019-07
```

All tasks are [S] sequential: they all modify `cli/fleet.py` (except
T-019-06 which modifies `constitution/principles.md` and T-019-07 which
is verification-only).

## Batch Plan

- **Batch 1** (F-08): T-019-01, T-019-02 (sequential within batch)
- **Batch 2** (F-08): T-019-03, T-019-04, T-019-05 (sequential within batch)
- **CHECKPOINT**: Run full test suite after Batch 2
- **Batch 3** (F-08, HITL): T-019-06 (requires owner approval)
- **Batch 4** (F-08): T-019-07 (final regression check)
