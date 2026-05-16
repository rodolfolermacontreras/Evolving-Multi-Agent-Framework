# Ledger Migration Policy

Provenance: LESSON-004, source feature `specs/2026-05-12-fleet-ledger/`
Effective: 2026-05-16

---

## Scope

This policy governs schema changes to `spec-driven-development/ledger/fleet.db`.
It applies to the `dispatches` and `decisions` tables and any future tables
added to the fleet ledger.

## Current Schema Version

- Version: **1** (v0.1, established 2026-05-12)
- Defined in: `schema.sql`
- Tracked by: `schema_version` table (created by the first migration)

## Version Tracking

Add a `schema_version` table on the first migration. The initializer
(`init_ledger.py`) creates it if absent:

```sql
CREATE TABLE IF NOT EXISTS schema_version (
  version     INTEGER PRIMARY KEY,
  applied_at  TEXT NOT NULL,
  description TEXT NOT NULL
);
```

If the table is empty after creation, insert the baseline:

```sql
INSERT OR IGNORE INTO schema_version (version, applied_at, description)
VALUES (1, '2026-05-12T00:00:00Z', 'v0.1 baseline: dispatches + decisions');
```

## Migration File Naming

Migrations live in `spec-driven-development/ledger/migrations/` as numbered SQL
files:

```
migrations/
  002-add-column-example.sql
  003-add-table-example.sql
```

Rules:
- Files are named `NNN-short-description.sql` where NNN is the target version.
- Each file begins with a comment: `-- Migration NNN: short description`
- Each file ends with an INSERT into `schema_version`.
- Files are idempotent where possible (use `IF NOT EXISTS`, `IF NOT NULL` checks).
- Version numbers are sequential with no gaps.

## Applying Migrations

`init_ledger.py` applies migrations automatically:

1. Run `schema.sql` (idempotent baseline).
2. Ensure `schema_version` table exists.
3. Read the current version from `MAX(version)` in `schema_version`.
4. Apply each migration file with a version number greater than the current version,
   in order.
5. Each migration runs inside a transaction. If it fails, the transaction rolls back
   and the process stops with an error.

This logic is not yet implemented. When the first migration is needed, update
`init_ledger.py` to include this loop before applying the migration.

## Approval Requirements

| Change type | Approval level | Documentation |
|-------------|---------------|---------------|
| Add a nullable column | Level 1 (Principal Architect) | Migration file + task note |
| Add a new table | Level 1 (Principal Architect) | Migration file + ADR if cross-cutting |
| Rename or drop a column | Level 2 (Human) | Migration file + ADR required |
| Drop a table | Level 2 (Human) | Migration file + ADR required |
| Change a column type | Level 2 (Human) | Migration file + ADR required |
| Add an index | Level 0 (Worker) | Migration file only |

These levels align with `constitution/decision-policy.md`. The key rule:
**destructive changes (drop, rename, type change) always require Level 2 approval
and an ADR before the migration file is written.**

## Rollback Posture

- **Forward-only by default.** SQLite does not support `ALTER TABLE DROP COLUMN`
  in older versions, and rollback scripts add maintenance burden.
- If a migration must be reversed, write a new forward migration that undoes the
  change (e.g., migration 004 adds a column, migration 005 removes it).
- The `schema_version` table records what was applied. It is never rolled back --
  new entries only.
- Before applying a migration to the production `fleet.db`, back up the file:
  `cp fleet.db fleet.db.bak-$(date +%Y%m%d)`.

## Testing Migrations

- Every migration file must have a corresponding test in `test_ledger.py` that:
  1. Creates a fresh DB at the pre-migration version.
  2. Applies the migration.
  3. Asserts the schema change is present.
  4. Asserts existing data survives.
- Use pytest `tmp_path` for all migration tests. Never test against the committed
  `fleet.db`.

## What This Policy Does NOT Cover

- Application-level data migrations (backfilling values). Those are task-level
  scripts, not schema migrations.
- Non-SQLite backends. The framework uses SQLite only.
- Automated migration generation tools. Migrations are hand-written SQL.
