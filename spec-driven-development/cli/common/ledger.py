"""SQLite ledger scaffold for fleet.db.

Schema from the SDD plan:

```sql
-- Agent registry
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  name TEXT,
  specialized INTEGER DEFAULT 0,
  skills_json TEXT,
  born_at TEXT,
  last_used TEXT
);

-- Skill catalog
CREATE TABLE skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT DEFAULT '1.0',
  summary TEXT,
  applies_to TEXT,
  requires TEXT
);

-- Dispatch records
CREATE TABLE dispatches (
  id TEXT PRIMARY KEY,
  feature_id TEXT,
  worker_id TEXT REFERENCES agents(id),
  skills_json TEXT,
  prompt_hash TEXT,
  worktree TEXT,
  branch TEXT,
  status TEXT DEFAULT 'pending',
  started_at TEXT,
  finished_at TEXT
);

-- Artifacts produced by dispatches
CREATE TABLE artifacts (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  path TEXT NOT NULL,
  kind TEXT,
  sha TEXT
);

-- Blockers raised during dispatch
CREATE TABLE blockers (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  severity TEXT,
  summary TEXT,
  raised_at TEXT,
  resolved_at TEXT,
  resolved_by TEXT
);

-- Lessons learned from retrospectives
CREATE TABLE retro_lessons (
  id TEXT PRIMARY KEY,
  pi_id TEXT,
  sprint_id TEXT,
  lesson TEXT,
  applied_to_skill_id TEXT REFERENCES skills(id)
);
```
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  name TEXT,
  specialized INTEGER DEFAULT 0,
  skills_json TEXT,
  born_at TEXT,
  last_used TEXT
);

CREATE TABLE IF NOT EXISTS skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT DEFAULT '1.0',
  summary TEXT,
  applies_to TEXT,
  requires TEXT
);

CREATE TABLE IF NOT EXISTS dispatches (
  id TEXT PRIMARY KEY,
  feature_id TEXT,
  worker_id TEXT REFERENCES agents(id),
  skills_json TEXT,
  prompt_hash TEXT,
  worktree TEXT,
  branch TEXT,
  status TEXT DEFAULT 'pending',
  started_at TEXT,
  finished_at TEXT
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  path TEXT NOT NULL,
  kind TEXT,
  sha TEXT
);

CREATE TABLE IF NOT EXISTS blockers (
  id TEXT PRIMARY KEY,
  dispatch_id TEXT REFERENCES dispatches(id),
  severity TEXT,
  summary TEXT,
  raised_at TEXT,
  resolved_at TEXT,
  resolved_by TEXT
);

CREATE TABLE IF NOT EXISTS retro_lessons (
  id TEXT PRIMARY KEY,
  pi_id TEXT,
  sprint_id TEXT,
  lesson TEXT,
  applied_to_skill_id TEXT REFERENCES skills(id)
);
"""


def ledger_path() -> Path:
    """Return the default fleet ledger path."""
    return Path(__file__).resolve().parents[2] / "ledger" / "fleet.db"


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Create a SQLite connection for the fleet ledger."""
    target = path or ledger_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(target)


def ensure_schema(path: Path | None = None) -> None:
    """Create the base fleet schema if it does not exist."""
    with connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def main() -> int:
    """Initialize the fleet ledger schema."""
    ensure_schema()
    print(f"TODO: expand ledger operations beyond schema creation at {ledger_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
