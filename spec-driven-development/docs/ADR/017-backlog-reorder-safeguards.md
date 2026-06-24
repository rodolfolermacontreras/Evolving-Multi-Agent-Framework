---
id: ADR-017
type: spec
status: draft
owner: principal-architect
updated: 2026-06-11
feature: 2026-06-24-dashboard-lifecycle-reorder
---

# ADR-017: Backlog reorder safeguards -- optional `depends_on`, append-only audit, dependency-lock, force-as-Level-2

- Date: 2026-06-11
- Status: **proposed**
- Authors: Principal Architect + Principal Product Manager (F-24 design slot, Sprint 11)
- Feature: SDD-036 (lifecycle pipeline + 4-card docs row + drag-to-reorder safeguards)

> **Frontmatter note:** `status: draft` is the schema-lint carrier value for a not-yet-accepted ADR (the frontmatter status enum has no `proposed`). The body Status is the authoritative ADR lifecycle state: **proposed**, pending owner acceptance.

## Context

SDD-036 makes backlog ordering operable on the local dashboard. The owner correction of 2026-06-08 is binding: leadership reorders priority in meetings without the PM present, so the framework must make reordering **friction-free** while preserving an **audit trail** and protecting **dependency** integrity. The CLARIFY phase (Q-D..Q-J) settled ten decisions that, taken together, introduce: a new optional frontmatter field, a new persisted audit artifact, a new dependency-lock governance rule, and a new schema-lint validator. Per the decision-policy, changes that cross modules and introduce a new pattern are Level-1 Principal decisions and must be recorded as an ADR. This ADR records those choices and explicitly documents why the two genuinely irreversible (Level-2) alternatives were rejected so they do not block F-25.

## Decision

1. **Optional `depends_on` frontmatter field (Q-E/Q-F).** `spec.md` MAY declare `depends_on` as an inline list of feature IDs. It is OPTIONAL and is NOT added to `REQUIRED_CONTRACT_FIELDS`; an absent field means "no declared dependencies." No historical spec is backfilled (no flag day).
2. **`check_depends_on` validator (Q-F).** `schema_lint.py` validates `depends_on` ONLY when present: list shape, ID shape `^[A-Z]{2,}-\d{2,3}$`, no duplicates, and no self-dependency are ERROR; referenced-ID existence in BACKLOG is WARNING. The validator parses the inline `[...]` string by hand (the stdlib frontmatter parser returns a raw string; no PyYAML -- Article V).
3. **Append-only audit artifact, not a SQLite table (Q-G).** Reorders append one JSON object per move to `spec-driven-development/ledger/reorder-audit.jsonl` with fields `event_type`, `actor`, `timestamp` (ISO-8601 UTC `Z`), `item_id`, `from_rank`, `to_rank`, `reason`, `dependency_check`, `force_override`. The file is append-only and never rewritten.
4. **Display-order overlay, not BACKLOG mutation.** Reorder writes `backlog/display-order.json` (an ordered ID list); `backlog/BACKLOG.md` stays PM-authoritative and is not mutated by reorder. Absent overlay = BACKLOG natural order.
5. **Dependency-lock semantics (Q-D).** An item cannot outrank an incomplete item it depends on; cycle-creating moves are blocked; blocked moves emit a human-readable reason. Dependencies are feature IDs only.
6. **Force-override is a Level-2 runtime gate (Q-H).** A dependency-violating move is rejected unless `--force` is invoked with a non-empty reason; forced moves record `force_override: true`; the tool never silently forces. Using `--force` at runtime requires a recorded Level-2 decision (Friction Analysis brief + owner approval). Designing the mechanism is Level-1; F-24/F-25 do not trigger a force.

## Consequences

- Positive: reordering stays friction-free for legal moves (honors the owner correction); every move is auditable; dependency integrity is protected; no new runtime dependency; no schema migration; existing specs are unaffected (field is optional).
- Positive: keeping the audit in a JSON Lines file keeps the change Level-1 (no `fleet.db` migration, which would be Level-2).
- Negative: an inline-list field parsed from a raw string is a sharp edge -- both the lint validator and the dashboard reader must parse `[...]` themselves; mitigated by explicit tests (R-3, R-4).
- Negative: two ordering sources now exist (BACKLOG RICE order + display overlay); mitigated by making the overlay display-only and validating its IDs against BACKLOG.
- Neutral: `depends_on` existence is WARNING (not ERROR), so a referenced-but-renamed/closed ID does not fail lint; this is intentional to avoid coupling lint to BACKLOG churn.

## Alternatives Considered

- **SQLite audit table in `ledger/fleet.db` (REJECTED -- Level-2).** A schema migration is irreversible and credential/production-adjacent; it would require an owner-approved Level-2 Friction Analysis before implementation and would block F-25. The append-only JSONL file delivers the same audit value at Level-1.
- **Required `depends_on` across all specs (REJECTED -- Level-2 flag day).** Making the field required would force a backfill of every historical spec dir (a flag-day migration). The kickoff and Q-E forbid this without recorded migration cost + owner approval. Optional-when-present keeps the change additive and Level-1.
- **Mutating BACKLOG.md order directly (REJECTED).** BACKLOG.md is PM-authoritative (RICE-scored); ad-hoc meeting reorders should not overwrite it. A separate display overlay preserves the PM source of truth while enabling the dashboard reorder.
- **True browser drag/drop with a JS library (REJECTED).** Adds a JavaScript-framework dependency (Article V / kickoff "do-NOT"). A keyboard-accessible stdlib-backed control ships the value now; pointer drag/drop is deferred to a possible v2.
