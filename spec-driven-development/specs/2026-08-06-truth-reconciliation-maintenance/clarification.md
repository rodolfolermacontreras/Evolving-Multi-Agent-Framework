---
id: MAINT-2026-08-06-TRUTH-RECONCILIATION-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-08-06
feature: 2026-08-06-truth-reconciliation-maintenance
---

# Product Clarification and Acceptance: Truth Reconciliation Maintenance

- Maintenance ID: `MAINT-2026-08-06-TRUTH-RECONCILIATION`
- Classification: owner-authorized corrective maintenance between PIs
- Product gate: CLARIFY closed 2026-08-06
- PI / sprint: none; this package does not create or imply PI-10 or a sprint
- Next gate: Principal Architect authors the full technical spec before any
  implementation or generated rebuild

## Identifier decision

Use `MAINT-2026-08-06-TRUTH-RECONCILIATION`, not an SDD feature number. The
date makes the identifier collision-free, `MAINT` keeps corrective maintenance
outside the product-feature namespace, and the descriptive suffix makes the
authorized outcome explicit. This identifier does not legitimize, reserve, or
authorize the leadership one-pager's SDD-060 through SDD-068 labels. SDD-059
remains an unscheduled candidate exactly as ADR-027 and the PI-9 close record
require; SDD-008 remains unscheduled in the backlog.

## Owner decision evidence

Exact approval context from the owner conversation on 2026-08-06:

> "The owner has now explicitly approved the recommendation on 2026-08-06:
> classify SDD-035 Azure decommission as ABANDONED/HISTORICAL, preserve partial
> evidence, remove it from active views, and require fresh authorization for any
> future Azure cleanup. The owner previously approved Option 1 (setup repair then
> truth reconciliation) and said \"les go\" to proceed."

This approval authorizes truth reconciliation after the completed setup repair.
It does not authorize Azure actions, a successor PI or sprint, or the one-pager's
SDD-060 through SDD-068 labels.

## Resolved product questions

### Q1: Scope

- **Question:** Is this a new product feature or corrective maintenance?
- **Recommended answer:** Corrective maintenance between PIs under the dated
  `MAINT` identifier.
- **Why this matters:** A feature ID or PI allocation would fabricate product
  scope after ADR-027 established a truthful zero-active state.
- **Owner answer:** Approved through Option 1 and "les go" on 2026-08-06.
- **Status:** answered.

### Q2: SDD-035 lifecycle

- **Question:** Should partial SDD-035 work be closed as DONE, resumed, or
  preserved as abandoned history?
- **Recommended answer:** ABANDONED / HISTORICAL; preserve checked and unchecked
  evidence exactly, remove active classification, and require fresh owner
  authorization before any Azure cleanup.
- **Why this matters:** DONE would falsely assert destructive and validation work
  that did not occur; deletion would destroy audit evidence.
- **Owner answer:** Explicitly approved 2026-08-06.
- **Status:** answered.

### Q3: Authorization boundary

- **Question:** Does truth reconciliation authorize PI-10, a sprint, Azure work,
  or SDD-060 through SDD-068?
- **Recommended answer:** No. It authorizes only the corrective truth package and
  its normal downstream SPEC, implementation, review, and generated rebuild gates.
- **Why this matters:** The leadership one-pager is not an authoritative backlog
  or scheduling source, and ADR-027 forbids a synthetic successor.
- **Owner answer:** The approved sequence is setup repair, then truth
  reconciliation; no broader authorization was given.
- **Status:** answered.

## Accepted scope

The full technical spec must cover all of the following outcomes as one
maintenance package:

1. **Backlog truth.** Correct terminal status drift without changing historical
   RICE values or inventing scores; keep genuine candidates unscheduled.
2. **Old feature lifecycle truth.** Remove abandoned or superseded work from
   active classification while preserving every historical artifact and every
   unchecked validation item.
3. **Zero-active generated truth.** Rebuild generated state and work-index from
   corrected sources so they show no active PI, sprint, or feature.
4. **Tracker, session, and onboarding refresh.** Correct current operational
   guidance and pointers without rewriting frozen historical snapshots.
5. **Leadership brief correction.** Remove false active-work implications and
   treat SDD-060 through SDD-068 as unauthorized labels, not backlog IDs.
6. **Stale-doc guard extension.** Extend the existing guard to detect recurrence
   of the specific active-state and unauthorized-ID drift covered here.
7. **Generated rebuild.** Regenerate source-derived executive artifacts only
   after source corrections and focused checks pass; do not hand-edit generated
   files.

## Non-goals

- No Azure query, mutation, teardown, resource verification, credential change,
  or cleanup of any kind.
- No PI-10, successor PI, sprint, allocation, current marker, or roadmap theme.
- No authorization or reservation of SDD-060 through SDD-068.
- No new product feature work and no scheduling of SDD-008 or SDD-059.
- No push, merge, production-branch action, or commit authorization.
- No change to the completed setup repair behavior or its commit.
- No deletion, relocation, or rewriting of historical evidence merely to reduce
  search results.
- No unchecked SDD-035 requirement may be checked, waived, or inferred complete.

## Product acceptance criteria

| ID | Acceptance criterion |
|----|----------------------|
| AC-TR-01 | Authoritative backlog rows show SDD-002..006, SDD-009/010, and SDD-055 as DONE; SDD-001 as SUPERSEDED / HISTORICAL; and SDD-007 as HISTORICAL / RETIRED cloud direction with SDD-035 abandoned. Existing RICE fields remain unchanged. |
| AC-TR-02 | SDD-035 is archived as ABANDONED / HISTORICAL, never DONE; all partial artifacts remain present, checked evidence remains checked, unchecked requirements remain unchecked, and fresh owner authorization is stated as mandatory for future Azure cleanup. |
| AC-TR-03 | SDD-008 remains unscheduled in the backlog, and SDD-059 remains unscheduled wherever authoritatively represented. No new score is invented for either candidate. |
| AC-TR-04 | Source records establish zero active PI, zero active sprint, and zero active feature; regenerated state and work-index reproduce that truth without hand edits. |
| AC-TR-05 | Current tracker, session-memory, onboarding, and leadership-brief surfaces agree on the between-PI state and do not present abandoned, superseded, or unauthorized work as active. Frozen historical evidence is preserved. |
| AC-TR-06 | The leadership brief no longer treats SDD-060 through SDD-068 as authorized product identifiers, and the repository contains an explicit statement that those labels confer no backlog, PI, sprint, or implementation authority. |
| AC-TR-07 | The stale-doc guard has focused regression coverage for the corrected active-state and unauthorized-ID drift and passes with all existing guard checks. |
| AC-TR-08 | The generated rebuild occurs only after source correction and relevant schema/stale-doc checks pass; generated artifacts are not manually edited. |
| AC-TR-09 | The final diff contains no Azure operation evidence, PI/sprint creation, product feature implementation, setup-repair behavior change, historical-file deletion, push, or merge. |

## Gate disposition

CLARIFY is **closed**: scope, lifecycle treatment, identifier, authorization
boundary, acceptance criteria, and non-goals are resolved by the owner's
2026-08-06 decision. Because the package spans more than five governance and
generated-state surfaces and extends a guard, the repository's full-spec path
applies. The Principal Architect owns the next SPEC gate and technical approach;
the Principal Software Developer owns later plan, tasks, implementation, and
generated rebuild. No implementation is authorized by this clarification alone.
