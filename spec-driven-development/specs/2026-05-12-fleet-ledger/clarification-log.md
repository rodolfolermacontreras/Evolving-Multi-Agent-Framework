# Clarification Log: Fleet Ledger v0.1

- Date: 2026-05-12
- Author: Agent INDIA
- Feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`

---

## Self-clarifications

### Q1. Should ledger track agent specialization packs or worker ids beyond `agent_id` and `agent_role`?

Answer: No for v0.1. The first ledger should prove Article VII dispatch logging with the minimum useful fields. Specialization tracking is a candidate for a later schema migration and is captured in `RETRO.md` / `sprints/PI-1/lessons.md`.

### Q2. Should this use SQLAlchemy or another ORM?

Answer: No. Use stdlib `sqlite3` to preserve framework portability and satisfy the no-third-party-runtime-dependency acceptance criterion.

### Q3. Should the schema include migration metadata now?

Answer: No for v0.1. The initializer is idempotent, but formal schema migrations are explicitly out of scope. A migration pattern should be designed when v0.2 needs its first change.

### Q4. Should the CLI output JSON for automation?

Answer: Not in v0.1. The requested output is a readable table and simple summaries. JSON can be added later if fleet automation needs machine-readable reports.

### Q5. Should `fleet.db` contain the dogfood dispatch rows from this pilot?

Answer: No. Commit an initialized empty database so the source-of-truth file exists from the start without baking transient pilot data into the baseline.

### Q6. Is pytest a runtime dependency?

Answer: No. pytest is accepted as a development dependency for the repository test suite only. Runtime scripts remain stdlib-only.
