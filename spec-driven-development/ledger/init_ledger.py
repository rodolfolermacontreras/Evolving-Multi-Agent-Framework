#!/usr/bin/env python3
"""Initialize the Fleet Ledger SQLite database.

By default this creates or updates `fleet.db` next to this script. Pass
`--db PATH` to initialize a different database, such as a test database.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().with_name("fleet.db")
SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")


class LedgerInitError(Exception):
    """Expected ledger initialization failure."""


def init_ledger(db_path: str | Path = DEFAULT_DB, schema_path: str | Path = SCHEMA_PATH) -> Path:
    """Create or update a Fleet Ledger database from the idempotent schema."""
    db = Path(db_path).expanduser()
    schema = Path(schema_path)
    if not schema.is_file():
        raise LedgerInitError(f"Schema file not found: {schema}")
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.executescript(schema.read_text(encoding="utf-8"))
        conn.commit()
    return db


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="init_ledger.py",
        description="Initialize the Fleet Ledger SQLite database from schema.sql.",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="Path to the SQLite database to create or update. Defaults to spec-driven-development/ledger/fleet.db.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        db = init_ledger(args.db)
    except (LedgerInitError, OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Fleet ledger initialized: {db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
