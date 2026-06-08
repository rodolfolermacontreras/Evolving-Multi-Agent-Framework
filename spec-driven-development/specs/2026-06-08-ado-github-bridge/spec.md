---
id: SDD-20260608ADOGHBRIDGE-spec
type: spec
status: blocked
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---
# Feature Spec: ADO / GitHub Issues Sync Bridge (SDD-022)

> **Status note**: this spec is blocked on CLARIFY answers in
> [`clarify.md`](./clarify.md). SDD-FDC-001 has no `clarify` status,
> so `status: blocked` is the valid carrier for this phase. Do not
> implement against this file until CLARIFY closes and this spec is

- Date: 2026-06-08
- Authors: Principal Product Manager + Principal Architect
- Status: BLOCKED (F-12 pass 1; owner decisions pending)
- Priority: P2
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Spec ID: SDD-022
- Parent objective: PI-5 Objective 4 -- ADO/GitHub Bridge + Model
  Upgrade Discipline
Decision sections are authored in this pass. Acceptance Criteria,
Traceability Matrix, Plan, and Tasks are intentionally left as pending.
Reason: Q-A through Q-H in [`clarify.md`](./clarify.md) are owner-level
surfaces for an external issue-tracker bridge. Locking a spec before
those decisions are answered would invent owner decisions and violate
Article IX. Locking validation before the spec is complete would violate
Article X.

---

## Problem Statement

The framework currently produces implementation work as committed repo
artifacts: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, sprint
boards, and ledger rows. That works for a single developer inside VS
Code, but it does not meet the adoption pattern Scott Epperly surfaced
appear in their operational tracker.

The adoption gap is specific and practical:

1. **External teams need tracker-native visibility.** A teammate should
   be able to see SDD tasks as GitHub Issues or ADO Work Items without
   learning the whole spec directory structure first.
2. **The framework must not abandon file-backed traceability.** The
   reviewed source of truth still lives in repo files. An issue bridge
   must not silently overwrite specs, tasks, validation contracts, or
   sprint state.
3. **The bridge must stay portable.** The framework is meant to be
   adopted by arbitrary host projects. The sync mechanism cannot depend
   on host-specific files, cloud services, or third-party Python
   packages.
   Sprint 8 kickoff says GitHub-first with ADO fast-follow; the owner
   must confirm whether live ADO is v1-required or a provider contract
   after GitHub is proven.

---

## Goal

Define a `/taskstoissues` bridge that can turn SDD `tasks.md` rows into
external tracker issues while preserving the framework's file-backed
contract and Article V stdlib-only discipline.

locked validation contract for F-14 that specifies:

- Which artifact is authoritative (`tasks.md`, tracker, or
- Which tracker provider is live in v1.
- How sync is invoked.
- Which auth model is used without committing secrets.
- That HTTP access uses Python stdlib `urllib.*` only.
---
## Constraints

  only. No `requests`, `httpx`, `PyGithub`, `azure-devops`, or other
  third-party package.
- **No constitution edits** in F-12.
  spec directory or framework CLI surfaces, not in host project files.
- **No F-13 work**: model-upgrade discipline remains a separate Sprint 8
---
## Out-of-Scope for SDD-022 v1 Unless Owner Upgrades Scope

- Background daemon, webhook listener, or state-dashboard-triggered
  write behavior.
- Automatic mutation of `tasks.md` from issue tracker state.
- Third-party SDK wrappers for GitHub or ADO.
- GitHub App installation flow.
- ADO service connection setup.
- Assignee, milestone, dependency graph, estimate, or sprint-capacity
  synchronization.
- Any edits under `constitution/**`.
- Any writes into an adopted host project's application files.

---

## Open Decisions Blocking SPEC Finalization


| ID | Decision | Status |
|----|----------|--------|
| Q-A | Direction of authority | OPEN |
| Q-B | Canonical issue system for v1 | OPEN |
| Q-C | Sync cadence | OPEN |
| Q-D | Conflict resolution semantics | OPEN |


Expected AC areas, not yet locked:

- AC area for authority model and mutation boundaries.
- AC area for GitHub provider behavior and ADO fast-follow boundary.
- AC area for synced field rendering.
- AC area for schema_lint, full tests, and no host-project writes.

---


**TBD pending CLARIFY close.** Candidate surfaces only:

- `spec-driven-development/cli/taskstoissues.py` (new, candidate)
- `spec-driven-development/cli/test_taskstoissues.py` (new, candidate)
- `spec-driven-development/templates/task-list.md` (possible doc-only
  guidance if mapping file is confirmed)
  per-spec-dir state if Q-F recommendation is accepted)
No candidate surface is approved until CLARIFY closes.


**TBD pending CLARIFY close.** Expected strategy:

- Unit tests for task parsing, body rendering, mapping serialization,
  conflict detection, auth/env-var validation, and stdlib HTTP request
  construction.
  doubles; no live network in automated tests.
- Manual check only for optional live GitHub token smoke, if owner
  approves live write validation.
- `python spec-driven-development/cli/schema_lint.py` clean.
- Full suite only in F-14 if code is touched.

---

## Validation Contract

The sibling [`validation.md`](./validation.md) is a draft scaffold only.
It must be populated and locked after owner decisions are recorded.

---

## Traceability Matrix

**TBD pending CLARIFY close.**
