---
id: SDD-20260611DASHREORDER-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-11
feature: 2026-06-24-dashboard-lifecycle-reorder
---

# CLARIFY: SDD-036 -- Lifecycle pipeline + 4-card docs row + drag-to-reorder safeguards

- Date: 2026-06-11
- Authors: Principal Product Manager + Principal Architect (jointly, with Software Developer task input), at F-24
- Status: **DONE** -- Q-A through Q-J answered; validation contract locked in [`validation.md`](./validation.md)
- Spec ID: SDD-036
- Sprint: PI-6 / Sprint 2 (= overall Sprint 11), feature slot F-24 (CLARIFY + SPEC + PLAN + TASKS; IMPLEMENT is F-25)
- Decision source: SDD-036 design surfaces resolved at F-24 against the locked owner direction recorded in [`SPRINT-11-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-11-KICKOFF.prompt.md) section 3 and the BACKLOG SDD-036 row owner correction (2026-06-08).

---

## Ground Rules

- This file is the source of truth for SDD-036 design decisions.
- Default recommendations are taken from [`SPRINT-11-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-11-KICKOFF.prompt.md) section 3 (Q-A..Q-J). Each question records the question, the options, the recommendation, and the **locked decision + rationale**.
- Article V (stdlib-only CLI), Article VII (context isolation / every artifact is a file), Article X (validation pre-implementation contract), and Article XII (UI Lifecycle Variant) all remain binding.
- F-24 is design-only. **No implementation, no production code, no commit, no push** is authorized by this file. Implementation is F-25.
- The two Level-2 triggers the kickoff flagged -- a new SQLite ledger table and making `depends_on` required across historical specs -- are **deliberately avoided** by the decisions below, keeping the common path at Level-1.

---

## Decision Summary (Q-A..Q-J)

| Q | Topic | Locked Decision | Level |
|---|-------|-----------------|-------|
| Q-A | Lifecycle pipeline scope + state source | Render the 9-state pipeline from existing `detect_stage` signals + backlog/sprint allocation; no new state registry | Level-1 |
| Q-B | Four-card documentation row | Constitution / Spec / Sprint / ADRs; each resolves to existing local artifacts; missing target -> disabled card | Level-1 |
| Q-C | Drag-to-reorder interaction model | Keyboard-accessible / no-JS-framework move controls backed by a stdlib reorder CLI; true pointer drag/drop deferred to v2 | Level-1 |
| Q-D | Dependency-lock semantics | Item cannot outrank an incomplete item it depends on; cycle-creating moves blocked; blocked moves give a human-readable reason; deps are feature IDs only | Level-1 |
| Q-E | `depends_on` frontmatter field | Optional inline-list field on `spec.md`; absent = empty; no flag-day backfill | Level-1 |
| Q-F | `schema_lint.py` extension | Validate `depends_on` only when present: list shape, ID shape, no duplicates, no self-dependency; existence = WARNING; field NOT added to REQUIRED_CONTRACT_FIELDS | Level-1 |
| Q-G | Audit-trail ledger row | Append-only JSON Lines artifact `ledger/reorder-audit.jsonl`; NOT a new SQLite table | Level-1 |
| Q-H | Force override | Blocked by default; design the governance now (Level-1); each force *use* at runtime is Level-2 with Friction Analysis + owner approval; UI never silently forces | Level-1 design / **Level-2 per use** |
| Q-I | UI Lifecycle Variant applicability | `ui-variant: true`; variant covers visual surfaces only; schema/ledger surfaces stay strict Article X; split made explicit in validation.md | Level-1 |
| Q-J | ADR requirement | **ADR-017 required** (Level-1, status `proposed`) -- new frontmatter field + new audit artifact + dependency-lock governance + new lint validator | Level-1 |

---

## Scope

### Q-A: Lifecycle pipeline scope and state source

**Context.** SDD-036 imports Scott's highest-value pattern: a horizontal lifecycle status pipeline on every feature card and sprint card (see [`docs/Scott_Example/UI_LEARNINGS_FROM_SCOTT.md`](../../docs/Scott_Example/UI_LEARNINGS_FROM_SCOTT.md), learning 1). The open question is which states render and where the source of truth comes from.

**Options.**

- Option A: Render the full lifecycle `IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE` from signals `state_builder.py` already computes (`detect_stage()` + backlog/sprint allocation). No new data.
- Option B: Add a new per-feature `lifecycle_state` frontmatter field and a state registry; backfill all spec dirs. (Flag-day; new schema surface.)

**PM recommendation:** Option A. The lifecycle is already derivable; a registry adds backfill cost for zero new information.

**Architect recommendation:** Option A. `detect_stage()` already returns one of `DONE/REVIEW/IMPLEMENT/TASKS/PLAN/SPEC/CLARIFY/BACKLOG` (8 of the 9 states; `IDEA` lives pre-spec-dir in `backlog/IDEAS.md`). The pipeline is a pure rendering of `Feature.stage`; sprint cards map the sprint's own status. No new registry, no new frontmatter, no schema migration.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Render the 9-state pipeline horizontally on each feature card and each sprint card. The current state is emphasized; prior states are marked complete; later states are outlined/pending. Source of truth is the existing `detect_stage()` result plus backlog/sprint allocation already parsed by `state_builder.py`. `IDEA` renders as the implicit pre-BACKLOG state (no spec dir yet) and is shown only as the leading pipeline node, never as a feature-card state. **No new state registry or frontmatter state field is introduced.**
**Rationale:** Reuses existing derivation (convention over configuration, Article-adjacent design heuristic), avoids a backfill flag-day, keeps the change to rendering only.

---

### Q-B: Four-card documentation row

**Context.** Scott's learning 2: replace scattered per-feature links with a fixed documentation row whose empty cards make missing artifacts visible.

**Options.**

- Option A: Constitution / Spec / Sprint / ADRs, each resolving to existing local artifacts; absent target renders a disabled "missing" card.
- Option B: Add ledger/dispatch cards now. (Rejected -- that is SDD-037 / Sprint 12 scope.)

**PM recommendation:** Option A. Four cards, no SDD-037 leakage.

**Architect recommendation:** Option A. Each card resolves to an artifact that already exists in the repo:
- **Constitution** -> the constitution articles/files referenced by the feature's `spec.md` (link into `constitution/`).
- **Spec** -> the feature's `specs/<dir>/spec.md`.
- **Sprint** -> the owning `sprints/PI-N/CURRENT_PI.md` sprint detail.
- **ADRs** -> the ADR(s) referenced by the feature's `spec.md` (link into `docs/ADR/`).
An absent or unresolved target renders a disabled/"missing" card; an empty card is an intentional signal, not an error.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Render a four-card documentation row -- **Constitution / Spec / Sprint / ADRs** -- on each feature card. Each card deep-links to the existing local artifact; missing targets render a disabled card with a "missing" affordance. **No SDD-037 ledger or dispatch cards are added under SDD-036.**
**Rationale:** Operationalizes the layered-documentation discipline, removes "where is the spec?" friction, and makes missing artifacts glaringly visible -- all from existing files.

---

### Q-C: Drag-to-reorder interaction model

**Context.** Scott's drag-to-reorder backlog pattern, adopted WITH safeguards. Owner correction (2026-06-08, BACKLOG SDD-036 row): "leadership meetings happen without the PM; drag-to-reorder must be possible without ceremony -- the framework value-add is the audit trail, not blocking the human." Article V forbids new third-party runtime deps; the kickoff section 7 forbids "new JavaScript frameworks."

**Options.**

- Option A: True browser pointer drag/drop using a JS drag library. (Rejected -- new JS framework dependency; raises validation ambiguity; the served dashboard is a stdlib-generated, mostly-read surface.)
- Option B: Keyboard-accessible / button-based move controls (move-up / move-down) on the dashboard, backed by a stdlib reorder CLI operation that performs the move, runs dependency-lock validation, and appends the audit row. True pointer drag/drop deferred to a possible v2.
- Option C: CLI-only reorder with no dashboard control. (Rejected -- loses the "without ceremony in a leadership meeting" affordance.)

**PM recommendation:** Option B. Preserves the no-ceremony intent and the audit trail without a JS framework.

**Architect recommendation:** Option B. The authoritative reorder mechanism is a stdlib CLI operation (`cli/backlog_reorder.py`, CLI-PATTERN compliant) that validates dependency-lock and appends an audit row. The dashboard exposes keyboard-accessible move controls that invoke that operation. True pointer drag/drop is explicitly deferred to v2 so SDD-036 introduces no JS framework and no validation ambiguity.

**SW Dev input:** A new stdlib module keeps the reorder logic unit-testable (`main(argv)`, exit codes 0/1/2) independent of any browser interaction, which the dashboard surface cannot provide.

**Joint recommendation:** **Option B.**

**Status:** ANSWERED.
**Decision:** Ship a **keyboard-accessible, no-JS-framework reorder control** backed by a stdlib reorder CLI. Reordering is possible without ceremony; the safeguard is the audit trail (Q-G) and the dependency lock (Q-D), not a modal block of the human. **True pointer drag/drop is deferred to a possible v2** and is OUT of SDD-036 scope.
**Rationale:** Honors Article V and the "no new JS framework" constraint, preserves the owner's no-ceremony intent, and keeps the reorder logic testable in isolation.

---

### Q-D: Dependency-lock semantics

**Context.** The reorder safeguard must prevent an item from being prioritized ahead of work it depends on, without blocking the human from ordinary moves.

**Decision.** A **dependency lock** means all of the following:

1. **Ordering constraint.** A backlog item `X` MAY NOT be moved to a higher display rank (more prioritized) than any item `Y` where `Y` is in `X.depends_on` and `Y` is not yet `DONE`. Moving `X` above an incomplete dependency is blocked.
2. **Cycle guard.** A move is blocked if honoring it would require a dependency cycle among the `depends_on` edges. (`depends_on` is static frontmatter, so cycles should already be rejected by schema lint per Q-F; the reorder tool re-checks defensively.)
3. **Human-readable reason.** Every blocked move surfaces a plain-language reason naming the blocking dependency and why (e.g. "SDD-036 cannot outrank SDD-018 -- SDD-018 is an incomplete dependency").
4. **Dependency identity.** Dependencies reference **feature IDs only** (e.g. `SDD-036`), matching the BACKLOG ID shape `[A-Z]{2,}-\d{2,3}`. Spec-dir slugs are NOT accepted (slugs are unstable across renames; IDs are the stable key already used by BACKLOG and state).

**Status:** ANSWERED.
**Decision:** As stated above. Deps are feature IDs only; ordering + cycle + human-readable-reason rules bind every reorder.
**Rationale:** Minimal, testable lock semantics that protect dependency order while leaving ordinary moves friction-free; feature-ID identity reuses the existing stable key.

---

### Q-E: `depends_on` frontmatter field

**Context.** Dependency-lock needs a declared dependency edge per feature. The kickoff and PI-6 risk register both default to **optional** to avoid a flag day.

**Options.**

- Option A: Optional inline-list field on `spec.md` frontmatter, e.g. `depends_on: [SDD-018]`; absent field = empty dependency list. No backfill.
- Option B: Required field on every spec dir, backfilled across all historical specs. (Level-2 flag-day; rejected per kickoff section 7 and PI-6 Risk row.)

**PM recommendation:** Option A.

**Architect recommendation:** Option A, with one parsing note for F-25: the stdlib frontmatter parser (`schema_lint.parse_frontmatter`) stores `depends_on: [SDD-018]` as the **raw string** `"[SDD-018]"`, not a Python list. The schema-lint validator and the state_builder reader MUST each parse the inline `[...]` list themselves. This is documented in [`plan.md`](./plan.md) so F-25 does not assume a structured list object.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** `depends_on` is an **optional** inline-list field on `spec.md` frontmatter. Absent = empty list. **No flag-day backfill.** At least one spec dir (the SDD-036 proof case) will carry a non-empty `depends_on` as the demonstrator. The raw-string parsing caveat is recorded for F-25.
**Rationale:** Keeping the field optional is precisely what keeps Q-F and the whole feature at Level-1 instead of Level-2; absent-means-empty is backward compatible with every existing spec dir.

---

### Q-F: `schema_lint.py` extension

**Context.** Lint must guard the new field without forcing a flag day.

**Decision.** Add a `check_depends_on` validator that runs **only when `depends_on` is present** on a `spec.md`. It validates:

- **List shape (ERROR).** The raw value parses as an inline list `[ID, ID, ...]`.
- **ID shape (ERROR).** Each entry matches `^[A-Z]{2,}-\d{2,3}$` (the BACKLOG ID shape).
- **No duplicates (ERROR).** No repeated IDs within the list.
- **No self-dependency (ERROR).** The spec's own feature ID is not in its own list.
- **Referenced-ID existence (WARNING).** Each referenced ID should exist in `backlog/BACKLOG.md`; absence is a WARNING (not ERROR), because historical artifacts may be incomplete.

`depends_on` is **NOT** added to `REQUIRED_CONTRACT_FIELDS`. No schema migration. No required-field rule.

**Status:** ANSWERED.
**Decision:** As stated. When-present validation only; ERROR for shape/duplicate/self-dependency; WARNING for non-existent reference; field stays optional.
**Rationale:** Guards data integrity for the new edge while avoiding the Level-2 flag-day a required field would impose; WARNING-level existence tolerates incomplete history.

---

### Q-G: Audit-trail ledger row

**Context.** Every reorder must be auditable (the owner's stated value-add). The kickoff flags that a **new SQLite schema requires explicit Architect review and owner-visible approval** (Level-2). The PI-6 risk register asks for the audit trail to be "append-only and visible-on-demand, not modal."

**Options.**

- Option A: New SQLite table in `ledger/fleet.db`. (**Level-2** -- schema migration; requires Friction Analysis + owner approval.)
- Option B: Append-only JSON Lines artifact `spec-driven-development/ledger/reorder-audit.jsonl`, one JSON object per reorder. (Level-1 -- a new file, stdlib `json`, Article VII compliant.)

**PM recommendation:** Option B. Append-only and visible-on-demand, no SQLite ceremony.

**Architect recommendation (binding architectural call):** **Option B.** A new SQLite table would be a Level-2 schema migration. The owner correction wants the audit trail without ceremony. An append-only JSONL artifact:
- honors Article VII ("every artifact is a file you can open");
- avoids a Level-2 migration entirely;
- stays stdlib (`json`, `pathlib`);
- keeps F-25 simpler and parallel-safer (a new file, not a shared DB schema).

**Audit row shape (locked).** Each appended JSON object MUST contain:

| Field | Type | Meaning |
|-------|------|---------|
| `event_type` | string | always `"reorder"` |
| `actor` | string | agent or human identifier performing the move |
| `timestamp` | string | ISO 8601 UTC, `YYYY-MM-DDTHH:MM:SSZ` |
| `item_id` | string | backlog feature ID moved (e.g. `SDD-036`) |
| `from_rank` | integer | display rank before the move |
| `to_rank` | integer | display rank after the move |
| `reason` | string | free text; MAY be empty for a no-ceremony move |
| `dependency_check` | string | `"pass"` or `"blocked:<reason>"` |
| `force_override` | boolean | `true` only when a Level-2-approved force occurred |

**Joint recommendation:** **Option B.**

**Status:** ANSWERED.
**Decision:** Append-only JSON Lines artifact `ledger/reorder-audit.jsonl` with the locked row shape above. **No new SQLite table; `ledger/fleet.db` schema is not modified.**
**Rationale:** Delivers the auditable, visible-on-demand trail the owner asked for while staying Level-1, stdlib-only, and Article VII compliant. This is the single decision that keeps Q-G off the Level-2 path.

---

### Q-H: Force override as a Level-2 decision

**Context.** A move that violates dependency-lock must not be silently forced, but the human must not be hard-blocked from an intentional, governed override.

**Decision.**

1. **Blocked by default.** A dependency-violating move is rejected with a human-readable reason.
2. **Governed force path.** The reorder tool MAY expose a `--force` path. **Using it requires a recorded Level-2 decision**: a Friction Analysis brief (`templates/level-2-decision.md`) plus explicit owner approval, before the forced move lands.
3. **Never silent.** The dashboard MAY surface the force affordance, but it MUST NEVER silently force a move. Every forced move records `force_override: true` and a non-empty `reason` in the audit artifact.
4. **Scope of the level.** **Designing** this governance is Level-1 (this decision). **Each force *use* at runtime is Level-2.** F-24 and F-25 do not themselves trigger a force; they only build and test the governed path.

**Status:** ANSWERED.
**Decision:** As stated. Force is blocked-by-default, governed by Level-2 per use, never silent.
**Rationale:** Preserves the no-ceremony default for legal moves while ensuring any dependency violation is a deliberate, owner-approved, audited exception -- never an accident.

---

### Q-I: UI Lifecycle Variant applicability

**Context.** SDD-036 has genuinely iterative visual surfaces (pipeline rendering, docs row, reorder control presentation) whose REQUIREDs may surface during F-25, alongside strict schema/ledger surfaces that must not loosen.

**Options.**

- Option A: Opt into the UI Lifecycle Variant (`ui-variant: true`) for the visual surfaces, while keeping schema/ledger surfaces under strict Article X. Make the split explicit in `validation.md`.
- Option B: Strict Article X across the whole feature. (Rejected -- forces visual over-specification or override ceremony, the exact friction Article XII was created to remove.)
- Option C: Variant across the whole feature. (Rejected -- would wrongly let schema/ledger REQUIREDs loosen post-lock.)

**PM recommendation:** Option A.

**Architect recommendation:** Option A. `spec.md` carries `ui-variant: true`; `validation.md` separates a **Strict (Article X)** REQUIRED block (schema/ledger items that cannot loosen) from a **UI-Variant (Article XII)** REQUIRED block whose post-lock changes go through append-only `## Delta Entries`. At F-24 lock there are zero deltas; deltas are appended only during F-25 as visual REQUIREDs surface.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** `ui-variant: true`. The variant applies to **visual dashboard surfaces only**; schema/ledger surfaces (`depends_on` schema, schema_lint extension, dependency-lock semantics, audit-trail shape, force-override governance) remain **strict Article X**. The split is explicit in [`validation.md`](./validation.md).
**Rationale:** Removes UI pre-lock guesswork while preserving strict, no-loosening discipline exactly where correctness depends on it.

---

### Q-J: ADR requirement

**Context.** The kickoff says an ADR is required only if SDD-036 introduces a new ledger schema/table, changes backlog-ordering governance, or makes `depends_on` required across historical specs -- and that CLARIFY must decide explicitly.

**Analysis.**
- New SQLite schema/table: **NO** (Q-G chose an append-only file).
- `depends_on` required across history: **NO** (Q-E kept it optional).
- Changes backlog-ordering governance: **YES** -- SDD-036 introduces dependency-lock + a force-override governance regime for display ordering, a new cross-cutting frontmatter field (`depends_on`), a new append-only audit artifact, and a new `schema_lint` validator. That is a new architectural pattern affecting more than one module.

**Decision.** **ADR-017 is REQUIRED** (Level-1, status `proposed`). It documents: the optional `depends_on` frontmatter field, the append-only `reorder-audit.jsonl` artifact (chosen over a SQLite table), the `check_depends_on` lint validator, the dependency-lock semantics, and the force-override-as-Level-2 governance. It does **NOT** propose any constitution edit and does **NOT** introduce a SQLite migration, so it stays Level-1 and needs no owner approval merely to draft. ADR-017 is referenced from [`spec.md`](./spec.md) and created at [`../../docs/ADR/017-backlog-reorder-safeguards.md`](../../docs/ADR/017-backlog-reorder-safeguards.md).

**Status:** ANSWERED.
**Decision:** ADR-017 required, Level-1, status `proposed`.
**Rationale:** The feature establishes a new, precedent-setting pattern across `state_builder.py`, `schema_lint.py`, a new reorder module, a new audit artifact, and the spec frontmatter contract -- exactly the "decision affects >1 module" trigger for an ADR.

---

## OWNER-ATTENTION Items (F-24 close)

- **Level-2 surfaces deferred to runtime, not triggered by F-24/F-25:**
  - **Force override use (Q-H).** Each actual forced reorder is a Level-2 decision requiring a Friction Analysis brief + owner approval at the time it is performed. Designing and testing the governed path is Level-1; no force is exercised during F-24 or F-25.
- **No Level-2 approval is required to proceed with F-25 implementation.** Both Level-2 triggers the kickoff named (new SQLite ledger schema; `depends_on` required across history) were deliberately avoided. The common path is entirely Level-1.
- **Pre-push approval remains mandatory at Sprint 11 close (F-26),** per the standing Sprint 7/8/9/10 owner direction. That gate is owned by F-26, not F-24.

## ADR Decision

- **ADR required: YES.** ADR-017 (`proposed`) created at [`../../docs/ADR/017-backlog-reorder-safeguards.md`](../../docs/ADR/017-backlog-reorder-safeguards.md). Level-1; no constitution edit; no SQLite migration.

## F-24 Close Checklist

1. Q-A through Q-J answered with locked decisions and rationale; zero open NEEDS-CLARIFICATION items.
2. This file frontmatter set to `status: done`, `updated: 2026-06-11`.
3. [`spec.md`](./spec.md) authored with goals, non-goals, requirements, acceptance criteria, file scope, traceability, `ui-variant: true`, and the `depends_on` schema.
4. [`plan.md`](./plan.md) authored with the F-25 file dependency graph and serialization analysis.
5. [`tasks.md`](./tasks.md) authored with atomic, verification-driven F-25 tasks honoring CLI-PATTERN.
6. [`validation.md`](./validation.md) authored, LOCKED at F-24, with the explicit Strict-vs-UI-Variant split; all REQUIRED items unchecked (implementation is F-25).
7. ADR-017 created (`proposed`) and referenced from spec.md + this file.
8. `python spec-driven-development/cli/schema_lint.py` exits 0.
9. No implementation, commit, or push performed in F-24.
