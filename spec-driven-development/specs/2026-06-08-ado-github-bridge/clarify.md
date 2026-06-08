---
id: SDD-20260608ADOGHBRIDGE-clarification
type: clarification
status: active
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-ado-github-bridge
---
# CLARIFY: ADO / GitHub Issues Sync Bridge (SDD-022)

- Date: 2026-06-08
- Authors: Principal Product Manager + Principal Architect (jointly)
- Status: **ACTIVE -- OWNER-ATTENTION REQUIRED**
- Spec ID: SDD-022
- Gating: `/spec` finalization, validation contract lock, `/plan`,
  `/tasks`, and F-14 implementation are blocked until Q-A through Q-H
  are answered. Q-I is resolved by the F-12 dispatch constraint.
- PM and Architect recommendations are defaults, not owner decisions.
- The owner may answer the questions one at a time or as a single batch.
- No `constitution/**` edits are in scope for F-12.
  Python stdlib only: `urllib.request`, `urllib.parse`, `urllib.error`,
  and `json` for HTTP + serialization.
- No host-project pollution: all framework-owned sync state must live
## Decision Battery


**Question**: For v1, what is authoritative: in-repo `tasks.md`, the
external issue tracker, or a bidirectional model with conflict

**Context**: Scott's adoption blocker is that his team lives in ADO,
which argues for an external tracker workflow. The framework's core
contract argues the opposite: spec, plan, tasks, and validation live in
repo files and are reviewed before implementation.

**PM recommendation**: `tasks.md` remains the source of truth for v1.
The issue tracker is a mirror plus collaboration surface. External
changes can be imported as a conflict report, but they do not mutate
`tasks.md` without an explicit local sync command and review.

**Architect recommendation**: Same. Make v1 unidirectional for state
authority: repo artifact -> issue tracker. Add a `pull` or `diff`
mode only as a non-mutating conflict detector. Bidirectional mutation
can be a later adapter once the mapping file and conflict report are
proven.

mirror in v1; external tracker edits produce a conflict report, not
automatic repo mutation.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---

### Q-B: Which issue system is canonical for v1

**Question**: Is v1 complete when GitHub Issues round-trips, with ADO
implemented as a fast-follow adapter contract, or must ADO also work in
the same v1 close?

Sprint 8 goal is named ADO/GitHub Bridge because Scott's adoption need
is ADO-facing. Treating both systems as hard v1 runtime requirements
raises auth, API, and test-matrix risk in the heaviest sprint of PI-5.

**PM recommendation**: GitHub Issues round-trip is the v1 close
criterion. ADO is specified through the same adapter interface, mapping
schema, and auth/env-var contract, but live ADO API execution is a
fast-follow unless the owner explicitly upgrades it to REQUIRED now.

**Architect recommendation**: Same. Build a provider boundary in the
spec so ADO is not designed out, but prove one provider end to end
first. A fake ADO provider test fixture is acceptable in F-14 only if
the owner confirms ADO is not a live v1 close criterion.
**Joint recommendation**: **GitHub Issues live round-trip for v1;
ADO adapter contract + dry-run/test fixture as fast-follow.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---

### Q-C: Sync cadence

**Question**: When should sync happen: on demand via `/taskstoissues`,
on every commit hook, on every state-dashboard refresh, through a
webhook, or some combination?

**Context**: Automatic sync sounds convenient but creates hidden writes
has a strong bias for explicit gates and logged dispatches.

**PM recommendation**: Explicit on-demand sync only in v1. The human or
agent invokes `/taskstoissues` when a task list is ready to mirror.
State-dashboard refresh may show sync freshness later, but must not
write externally.

**Architect recommendation**: Same. Webhooks and commit hooks add
stateful failure modes and credentials to passive workflows. Keep v1 as
an explicit command with dry-run default and no background daemon.

**Joint recommendation**: **On-demand `/taskstoissues` command only;
no commit hook, no dashboard-triggered writes, no webhook in v1.**

**Answer**: (pending owner)

---

### Q-D: Conflict resolution semantics

**Question**: If `tasks.md` says a task is done but the mapped issue is
reopened, or the issue is closed while `tasks.md` still says pending,
who wins?

**Context**: Last-writer-wins is simple but risky: it can silently
weaken the validation contract or overwrite the reviewed repo artifact
with external tracker state.

reported as a conflict requiring an explicit choice. The command exits
non-zero when a destructive or status-changing conflict is detected.

**Architect recommendation**: Same. Conflict report should identify
task ID, mapped issue ID, local status, remote status, and recommended
resolution. No automatic status flips across systems.

**Joint recommendation**: **`tasks.md` wins; conflicts are surfaced and
block mutation until resolved explicitly. No last-writer-wins.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---


**Question**: Which lifecycle action creates or updates issues: spec-dir
change, `/triage`, `/tasks` close, explicit `/taskstoissues`, or sprint
close?
 description, acceptance criteria, labels, assignee, status,

**Context**: This overlaps with Q-C but is slightly narrower: cadence is
how often sync can run; trigger is the lifecycle event that makes it
appropriate.

**PM recommendation**: Explicit `/taskstoissues` is the only v1 trigger.
Recommended operating convention: invoke it after `/tasks` locks a task
list, and again at close if the task statuses changed during
close.

**Architect recommendation**: Same. The CLI can expose subcommands such
as `diff`, `push`, and `pull-conflicts`, but all must be explicitly
invoked. Slash prompt may wrap the CLI.

**Joint recommendation**: **Explicit `/taskstoissues` trigger, normally
used after `/tasks` lock and optionally at close; no implicit lifecycle
auto-sync in v1.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---
### Q-F: Identity mapping

**Question**: How should a task ID such as `T-022-04` map to a GitHub
Issue or ADO Work Item ID?

**Context**: Inline issue numbers in `tasks.md` are easy to see but
dirty the reviewed task contract with external IDs. A ledger table is
stronger but implies a schema migration and Level-2 approval. A
separate JSON mapping keeps v1 reversible and stdlib-only.

**PM recommendation**: Use a per-spec-dir mapping file,
`issue-map.json`, committed beside `tasks.md`. It maps local task IDs
to provider, remote ID, URL, last synced timestamp, and last seen remote
status. `tasks.md` remains the human-readable contract.

Use deterministic JSON so future ADO support and future ledger
promotion can replay from committed mappings if needed.


**Answer**: (pending owner)
---

### Q-G: Auth model

**Question**: What auth shape should v1 use for local development, CI,
and future ADO support?

**Context**: Tokens are privacy/security sensitive. Committed files must
never contain credentials. Adding a GitHub App or ADO service principal
would raise setup and governance cost. PAT/env-var auth is simplest for
v1 but still requires careful docs and redaction.

**PM recommendation**: Use environment variables only. Local GitHub sync
reads `GITHUB_TOKEN` first, then `GH_TOKEN`. Future ADO adapter reads
`ADO_PAT`, `ADO_ORG_URL`, and `ADO_PROJECT`. CI uses repository secrets
with the same names if automation is later approved. No token is stored
in mappings, logs, or validation artifacts.

**Architect recommendation**: Same, with a dry-run mode as default and a
hard failure if required env vars are missing for a write operation.
GitHub App and ADO service connection stay out of v1.

**Joint recommendation**: **Environment-variable token model; dry-run
default; no committed credentials; no GitHub App or ADO service
connection in v1.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---

### Q-H: Scope of fields synced

**Question**: Which task fields should sync to issues: title only,
title + description, acceptance criteria, labels, assignee, status,
dependencies, milestones?

**Context**: More fields improve tracker usefulness but increase
round-trip conflicts. v1 should make issues useful without pretending
the issue tracker is the full spec system.

**PM recommendation**: Sync title, body, labels, status, source links,
and task ID. Body includes description, spec/plan/tasks links,
acceptance criteria references, file scope, and validation references.
Labels include `sdd`, spec ID, priority, and lifecycle/status. Do not
sync assignee, milestone, or dependency graph in v1.

**Architect recommendation**: Same. Keep body rendering deterministic
and idempotent. Add a generated marker comment in the issue body so the
command can update only the generated section without clobbering human
comments.

**Joint recommendation**: **Sync title + generated body + labels +
status + source links; no assignee/milestone/dependency sync in v1.**

**Status**: OPEN -- OWNER DECISION REQUIRED
**Answer**: (pending owner)

---

### Q-I: Dependencies

**Question**: Should SDD-022 preserve Article V with stdlib `urllib.*`,
or request a third-party HTTP dependency such as `requests`, `httpx`,
`PyGithub`, or an ADO SDK?

**Context**: GitHub REST and ADO REST can both be called with
`urllib.request`, `urllib.parse`, `urllib.error`, and `json`. A
third-party dependency would trigger Level-2 decision routing and likely
an ADR/constitution discussion.

**PM recommendation**: Preserve Article V. Use stdlib only.

**Architect recommendation**: Preserve Article V. Use stdlib only. If a
future provider proves `urllib` insufficient, file a separate Level-2
dependency brief after v1 rather than widening SDD-022 now.

**Joint recommendation**: **Use stdlib `urllib.*` only. No third-party
dependency, no Article V amendment, no constitution edit.**

**Status**: ANSWERED 2026-06-08 BY OWNER DISPATCH CONSTRAINT
**Answer**: Preserve Article V: stdlib `urllib.*`; no third-party deps;
no constitution edits.

---

## Owner Decision Summary

| ID | Decision Surface | Recommendation | Status |
|----|------------------|----------------|--------|
| Q-A | Direction of authority | `tasks.md` authoritative; issue tracker mirror in v1 | OPEN |
| Q-B | Canonical issue system for v1 | GitHub live round-trip; ADO adapter fast-follow | OPEN |
| Q-C | Sync cadence | Explicit on-demand `/taskstoissues` only | OPEN |
| Q-D | Conflict resolution | `tasks.md` wins; conflicts block mutation | OPEN |
| Q-E | Sync trigger | Explicit `/taskstoissues`, normally after `/tasks` lock | OPEN |
| Q-F | Identity mapping | Per-spec-dir `issue-map.json`; no ledger migration | OPEN |
| Q-G | Auth model | Env vars only; dry-run default; no committed tokens | OPEN |
| Q-H | Synced fields | Title/body/labels/status/source links; no assignee/milestone/deps | OPEN |
| Q-I | Dependencies | Stdlib `urllib.*`; no third-party deps | ANSWERED |

---

## SPEC Impact

- `spec.md` cannot be finalized until Q-A through Q-H are answered.
- `validation.md` cannot lock until `spec.md` acceptance criteria are
  derived from the owner decisions.
- `plan.md` and `tasks.md` remain scaffolds only. Implementing against
  them before CLARIFY closes violates Articles IX, X, and XI.
- If the owner rejects Q-I and requests a third-party dependency, F-12
  must STOP and route a Level-2 dependency brief + ADR path before any
  implementation work.
