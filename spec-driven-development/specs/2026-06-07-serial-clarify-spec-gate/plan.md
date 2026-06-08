---
id: SDD-20260607SERIAL-plan
type: plan
status: active
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# Implementation Plan: Serial Gate on CLARIFY/SPEC (SDD-019)

- Feature: SDD-019
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Plan Author: Principal Software Developer
- Date: 2026-06-07

---

## Implementation Approach

Extend `cli/fleet.py` with a `lock` subcommand group (`acquire`, `release`,
`status`, `force-release`) and a pre-dispatch gate check. Lock state is
derived from frontmatter scan of spec dirs, reusing the SDD-FDC-001
filesystem data contract as the lock substrate. No new state file.

ADR-013 is drafted this sprint (F-07, this commit). Article XI is added to
`constitution/principles.md` in F-08 after owner approval of the ADR.

### Key Design Decisions

1. **Lock scanner**: a function that walks `specs/` directories and parses
   frontmatter to determine CLARIFY and SPEC lock holders. Reuses
   `parse_frontmatter` from `cli/schema_lint.py` (shared boundary, per
   ADR-012 / SDD-FDC-001).

2. **Lock subcommands**: `fleet.py lock acquire|release|status|force-release`.
   `acquire` and `release` are explicit operations for CLI and automation.
   `status` is read-only. `force-release` requires `--reason` and writes a
   ledger audit row.

3. **Pre-dispatch gate**: before any fleet dispatch that targets a CLARIFY
   or SPEC phase, `fleet.py` calls the lock scanner. If the lock is held by
   another feature, dispatch exits non-zero naming the lock holder.

4. **Queue**: priority-weighted FIFO. Queue state persisted in fleet ledger
   event rows (`lock_queued`, `lock_acquired`, `lock_released`,
   `lock_force_released`).

5. **Grandfather**: on first run, any spec dir already in CLARIFY or SPEC
   is treated as a pre-existing lock holder, not blocked.

---

## File Scope

| File | Change Type | Owner |
|------|------------|-------|
| `cli/fleet.py` | Extend: lock subcommands + pre-dispatch gate | SDD-019 ONLY |
| `cli/test_fleet.py` | Extend: lock mechanics, refusal, queue, force-release tests | SDD-019 ONLY |
| `constitution/principles.md` | Amend: Article XI (BLOCKED on owner approval of ADR-013) | SDD-019, F-08 |
| `docs/ADR/013-serial-clarify-spec-gate.md` | New: ADR (committed in F-07) | SDD-019 |

### File Collision Analysis

- `cli/fleet.py`: SDD-019 ONLY. SDD-020 uses separate `cli/dedup.py` (no collision).
- `cli/bootstrap.py`: NOT touched by SDD-019 (SDD-027 track).
- `constitution/principles.md`: SDD-019 ONLY. Edit deferred to F-08 after ADR approval.

---

## Dependencies

| Dependency | Status | Impact |
|-----------|--------|--------|
| SDD-FDC-001 (frontmatter contract) | LOCKED, shipped Sprint 4 | `parse_frontmatter` reuse for lock scanner |
| ADR-013 | Committed this sprint (F-07) | Required before constitution edit |
| Owner approval of ADR-013 | Pending | Gates T-019-06 (Article XI edit) |
| SDD-020 | Independent | No coupling; composable |

---

## Implementation Order

1. **ADR-013** committed (F-07, this commit).
2. **T-019-01**: Lock-state scanner (frontmatter-based lock detection).
3. **T-019-02**: Lock subcommands (`acquire`, `release`, `status`, `force-release`).
4. **T-019-03**: Pre-dispatch gate check.
5. **T-019-04**: Queue ordering (priority-weighted FIFO).
6. **T-019-05**: Grandfather migration for existing open features.
7. **T-019-06**: Article XI edit to `constitution/principles.md` (BLOCKED on owner approval).
8. **T-019-07**: Full test suite + `schema_lint` regression check.

Tasks T-019-01 through T-019-05 are sequential (all modify `cli/fleet.py`).
T-019-06 is gated on external approval. T-019-07 is the final checkpoint.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `fleet.py` merge conflict with SDD-020 | LOW | SDD-020 uses `cli/dedup.py` | File-scope isolation confirmed |
| Owner rejects ADR-013 | LOW | Article XI deferred | Article XI is the last task; all mechanics work without it |
| Lock scanner perf on large spec trees | LOW | Frontmatter scan is fast for <100 dirs | Test with fixtures at 50+ dirs |
| Grandfather logic edge cases | MEDIUM | False blocks on existing features | Comprehensive fixture coverage |

---

## Test Strategy

- **Unit**: lock acquire/release, queue ordering, refusal message format,
  force-release ledger write, grandfather detection.
- **Integration**: end-to-end `fleet.py` dispatch refusal scenario (mock
  two features, dispatch second while first holds lock).
- **Regression**: existing 213-test suite stays green; `schema_lint` clean.
- **Constitutional amendment**: `schema_lint` enforces new Article version
  after T-019-06.

---

## Dispatch Plan (F-08)

Track A: SDD-019 (serial, all tasks touch `cli/fleet.py`).
Track B: SDD-027/028/029 (parallel with Track A, touches `cli/bootstrap.py`).

SDD-020 ships first in Track A (lower risk), then SDD-019. Track A and
Track B run in parallel because they touch different files.
