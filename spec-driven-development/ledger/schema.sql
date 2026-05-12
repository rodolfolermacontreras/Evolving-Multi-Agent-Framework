CREATE TABLE IF NOT EXISTS dispatches (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  dispatched_at TEXT NOT NULL,
  pi            TEXT NOT NULL,
  sprint        TEXT,
  feature_dir   TEXT,
  task_id       TEXT NOT NULL,
  task_title    TEXT NOT NULL,
  agent_id      TEXT NOT NULL,
  agent_role    TEXT NOT NULL,
  outcome       TEXT,
  outcome_at    TEXT,
  notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_dispatches_pi ON dispatches(pi);
CREATE INDEX IF NOT EXISTS idx_dispatches_feature ON dispatches(feature_dir);
CREATE INDEX IF NOT EXISTS idx_dispatches_agent ON dispatches(agent_id);

CREATE TABLE IF NOT EXISTS decisions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  decided_at  TEXT NOT NULL,
  level       INTEGER NOT NULL,
  decider     TEXT NOT NULL,
  artifact    TEXT,
  description TEXT NOT NULL
);
