---
id: SDD-20260611DASHREORDER-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-11
feature: 2026-06-24-dashboard-lifecycle-reorder
ui-variant: true
depends_on: [SDD-018]
---

# SPEC: SDD-036 -- Lifecycle pipeline + 4-card docs row + drag-to-reorder safeguards

- Feature ID: SDD-036
- Sprint: PI-6 / Sprint 2 (Sprint 11), design slot F-24
- Status: **active** -- design complete at F-24; implementation pending in F-25
- CLARIFY: [`clarify.md`](./clarify.md) (Q-A..Q-J, all ANSWERED)
- Validation contract: [`validation.md`](./validation.md) (LOCKED at F-24)
- ADR: [ADR-017 -- Backlog reorder safeguards](../../docs/ADR/017-backlog-reorder-safeguards.md) (`proposed`)
- UI Lifecycle Variant: **opted in** (`ui-variant: true`); applies to visual surfaces only -- see Validation Contract split.

---

## Problem Statement

The generated local dashboard ([`exec/state.html`](../../exec/state.html), produced by [`cli/state_builder.py`](../../cli/state_builder.py)) shows feature and sprint data but does not make three things operable: (1) where each feature sits in the lifecycle, (2) where the governing documents for a feature live, and (3) how to reorder backlog priority without losing the audit trail or violating dependencies. Scott's local dashboard demonstrated all three; SDD-036 imports the three approved patterns into the framework dashboard surface.

The owner correction (2026-06-08) is binding: leadership meetings happen without the PM present, so reordering must be possible **without ceremony** -- the framework value-add is the **audit trail**, not blocking the human. This spec must therefore deliver reorder that is friction-free for legal moves while making every move auditable and every dependency-violating move a deliberate, governed exception.

## Goal

Make lifecycle state, documentation routes, and backlog ordering **visible and operable** on the local dashboard, with dependency-lock and append-only audit-trail safeguards, using stdlib only and no new JavaScript framework.

## Non-Goals (Out of Scope)

- True browser pointer drag/drop (deferred to a possible v2 -- Q-C).
- SDD-037 Dispatches card and dashboard health pills (Sprint 12).
- SDD-038 aesthetic / lifecycle color-token system (Sprint 13 contingency); only minimal existing styles needed for readability.
- Any new SQLite table or modification to `ledger/fleet.db` schema (Q-G chose an append-only file).
- Making `depends_on` required across historical spec dirs (Q-E keeps it optional; no flag-day backfill).
- Any Azure decommission (SDD-035) artifacts.
- Any constitution edit.

## Acceptance Criteria

- **AC-1 (Lifecycle pipeline render).** Each feature card and each sprint card renders the horizontal pipeline `IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE`, with the current state emphasized, prior states marked complete, and later states outlined. The current state is derived from the existing `detect_stage()` result (features) or sprint status (sprints). No new state registry or frontmatter state field is added. (Q-A)
- **AC-2 (Four-card docs row).** Each feature card renders a four-card row -- Constitution / Spec / Sprint / ADRs -- each deep-linking to the resolved existing local artifact. An unresolved target renders a disabled "missing" card. No SDD-037 cards are added. (Q-B)
- **AC-3 (`depends_on` schema).** `spec.md` MAY carry an optional inline-list `depends_on` field of feature IDs (e.g. `depends_on: [SDD-018]`). An absent field is treated as an empty dependency list. No spec dir is required to add the field. (Q-E)
- **AC-4 (`schema_lint` validation).** When `depends_on` is present, `schema_lint.py` validates list shape, ID shape `^[A-Z]{2,}-\d{2,3}$`, no duplicates, and no self-dependency at ERROR severity, and referenced-ID existence in BACKLOG at WARNING severity. `depends_on` is NOT added to `REQUIRED_CONTRACT_FIELDS`; absent field produces zero findings. (Q-F)
- **AC-5 (Dependency-lock behavior).** A reorder that would move an item above an incomplete item it depends on is blocked with a human-readable reason; a cycle-creating move is blocked; a legal move succeeds. Dependencies are feature IDs only. (Q-D)
- **AC-6 (Audit-trail append).** Every reorder appends exactly one JSON object to `ledger/reorder-audit.jsonl` with the locked row shape (`event_type`, `actor`, `timestamp` ISO-8601 UTC, `item_id`, `from_rank`, `to_rank`, `reason`, `dependency_check`, `force_override`). The file is append-only and never rewritten. (Q-G)
- **AC-7 (Force-override governance).** A dependency-violating move is rejected unless a `--force` path is invoked; the forced move records `force_override: true` and a non-empty `reason`; the tool never silently forces. (Q-H)
- **AC-8 (Reorder control on dashboard).** The dashboard exposes a keyboard-accessible move control (no JS framework) that invokes the reorder operation; the displayed order reflects the current display-order overlay. (Q-C)
- **AC-9 (Schema lint clean).** After all changes, `python spec-driven-development/cli/schema_lint.py` exits 0.
- **AC-10 (Test baseline preserved).** `python -m pytest spec-driven-development/ --tb=no -q` returns at least 349 passed with the known 2 platform-conditional skips, plus the new SDD-036 tests.

## Affected Modules

| Module | Change | Shared? |
|--------|--------|---------|
| [`cli/state_builder.py`](../../cli/state_builder.py) | Render lifecycle pipeline (AC-1), four-card docs row (AC-2), reorder control + display-order overlay read (AC-8); parse optional `depends_on` (read-only). | **Shared** (also touched by SDD-040 history, SDD-037 future) -> forces serialization |
| [`cli/schema_lint.py`](../../cli/schema_lint.py) | Add `check_depends_on` validator wired into the spec.md path (AC-4). | **Shared** -> forces serialization |
| `cli/backlog_reorder.py` | **NEW** stdlib module: reorder operation, dependency-lock (AC-5), audit append (AC-6), force governance (AC-7). CLI-PATTERN compliant. | New file |
| `cli/test_state_builder.py` | New tests for AC-1, AC-2, AC-8. | Paired w/ state_builder |
| `cli/test_schema_lint.py` | New tests for AC-4. | Paired w/ schema_lint |
| `cli/test_backlog_reorder.py` | **NEW** tests for AC-5, AC-6, AC-7. | New file |
| `backlog/display-order.json` | **NEW** display-order overlay artifact (the reorder target; BACKLOG.md stays PM-authoritative). | New artifact |
| `ledger/reorder-audit.jsonl` | **NEW** append-only audit artifact (Q-G). | New artifact |
| One demonstrator `spec.md` | Add a non-empty `depends_on` as the proof case (additive frontmatter). | Additive |

## Data Model Changes

- **New optional frontmatter field** `depends_on` on `spec.md`: inline list of feature IDs. Absent = empty list. **Not** added to `REQUIRED_CONTRACT_FIELDS`.
- **Parsing caveat (binding for F-25):** the stdlib frontmatter parser (`schema_lint.parse_frontmatter`) stores `depends_on: [SDD-018]` as the raw string `"[SDD-018]"`, not a list. Both `schema_lint.check_depends_on` and the `state_builder` reader MUST parse the inline `[...]` syntax themselves (strip brackets, split on comma, trim). No PyYAML dependency is permitted (Article V).
- **New display-order overlay** `backlog/display-order.json`: an ordered list of feature IDs representing dashboard display rank. Absent = fall back to BACKLOG.md natural order. **BACKLOG.md is not mutated by reorder** -- it remains the PM-authoritative RICE-scored source; the overlay is the ad-hoc display order with full audit.
- **New audit artifact** `ledger/reorder-audit.jsonl`: append-only JSON Lines, one object per reorder (shape in Q-G / AC-6). No SQLite.

## API Changes

- No HTTP API change. The reorder operation is a stdlib CLI (`cli/backlog_reorder.py`) following CLI-PATTERN: `main(argv) -> int`, subcommand(s), exit codes 0 success / 1 blocked-or-validation-failure / 2 usage error, errors to stderr, UTC ISO-8601 `Z` timestamps.
- The dashboard's keyboard move control invokes this CLI operation; no JS framework, no new runtime dependency.

## Test Strategy

- Unit tests for `check_depends_on`: valid list, bad ID shape, duplicate, self-dependency (ERROR cases); non-existent reference (WARNING); absent field (zero findings).
- Unit tests for `backlog_reorder`: legal move succeeds + appends one audit row; dependency-violating move blocked with reason + no order change; cycle-creating move blocked; forced move records `force_override: true` + non-empty reason; audit file is append-only across two moves.
- Render tests for `state_builder`: pipeline nodes present with correct current-state emphasis; four-card docs row present with one disabled/missing card; reorder control present; display-order overlay respected.
- Full suite must hold at >= 349 passed + 2 skips plus the new tests (AC-10).
- One test per acceptance criterion per CLI-PATTERN.

## Validation Contract Pointer

See [`validation.md`](./validation.md). It is **LOCKED at F-24** and splits REQUIRED items into a **Strict (Article X)** block (schema/ledger correctness that cannot loosen) and a **UI-Variant (Article XII)** block (visual surfaces eligible for append-only `## Delta Entries` during F-25). At F-24 there are zero delta entries.

## Traceability Matrix

| Requirement | CLARIFY Q | AC | Validation Row | Task ID |
|-------------|-----------|----|----------------|---------|
| Lifecycle pipeline render | Q-A | AC-1 | R-1 (UI-Variant) | T-036-02 |
| Four-card docs row + missing state | Q-B | AC-2 | R-2 (UI-Variant) | T-036-03 |
| `depends_on` optional schema | Q-E | AC-3 | R-3 (Strict) | T-036-04 |
| `schema_lint` when-present validation | Q-F | AC-4 | R-4 (Strict) | T-036-05 |
| Dependency-lock behavior | Q-D | AC-5 | R-5 (Strict) | T-036-06 |
| Audit-trail append | Q-G | AC-6 | R-6 (Strict) | T-036-06 |
| Force-override governance | Q-H | AC-7 | R-7 (Strict) | T-036-07 |
| Reorder control on dashboard | Q-C | AC-8 | R-8 (UI-Variant) | T-036-08 |
| Schema lint clean | -- | AC-9 | R-9 (Strict) | T-036-09 |
| Test baseline preserved | -- | AC-10 | R-10 (Strict) | T-036-09 |

## Open Questions

- None blocking. All Q-A..Q-J are ANSWERED in [`clarify.md`](./clarify.md).
- **ADR required: yes** -- ADR-017 (`proposed`).

## Out of Scope

- True pointer drag/drop (v2).
- SDD-037 (Dispatches card + health pills), SDD-038 (aesthetic tokens), SDD-034 / SDD-039 / PI-4 housekeeping carryovers, SDD-035 (Azure decommission).
- Mutating `backlog/BACKLOG.md` ordering (the overlay is used instead; BACKLOG stays PM-authoritative).
- New SQLite ledger table; `depends_on` as a required field.

## Risks

- **R-A (Shared-file serialization).** `cli/state_builder.py` and `cli/schema_lint.py` are shared single files; concurrent worker edits would conflict. Mitigation: F-25 runs serially (see [`plan.md`](./plan.md) dependency graph).
- **R-B (Inline-list parsing).** The stdlib frontmatter parser yields a raw string for `depends_on`; a naive `for x in value` would iterate characters. Mitigation: explicit `[...]` parse documented in Data Model Changes and tested.
- **R-C (Overlay drift).** `display-order.json` could drift from BACKLOG IDs (renamed/closed features). Mitigation: reorder validates IDs against BACKLOG; unknown IDs surface a reason; existence is WARNING-level in lint.
- **R-D (Reorder writes a PM-owned concept).** Mitigation: reorder writes the overlay + audit, never BACKLOG.md; BACKLOG remains PM-authoritative.
- **R-E (UI over-specification).** Visual REQUIREDs are hard to pin pre-implementation. Mitigation: UI Lifecycle Variant lets visual REQUIREDs be refined via append-only deltas during F-25 while schema/ledger stays strict.

## Cross-Feature Notes

- **SDD-037** will add the Dispatches card + health pills on top of this dashboard; SDD-036 must not pre-empt those cards. The four-card docs row is fixed at Constitution/Spec/Sprint/ADRs.
- **SDD-018** (UI Lifecycle Variant) is the variant this spec opts into; `depends_on: [SDD-018]` is a natural demonstrator candidate.
- **SDD-038** owns the lifecycle color-token system; SDD-036 uses only minimal existing styles for readability.
