#!/usr/bin/env python3
"""Command-line interface for the Fleet Ledger.

Use this stdlib-only CLI to record dispatches and decisions, mark outcomes,
and answer basic audit questions such as "what dispatches happened in this PI?".
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from init_ledger import DEFAULT_DB, init_ledger

OUTCOMES = ("success", "failed", "blocked")


def utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect_initialized(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection after ensuring the ledger schema exists."""
    db = init_ledger(db_path)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def record_dispatch(db_path: str | Path, values: dict[str, Any]) -> int:
    """Insert one dispatch row and return its id."""
    columns = (
        "dispatched_at",
        "pi",
        "sprint",
        "feature_dir",
        "task_id",
        "task_title",
        "agent_id",
        "agent_role",
        "outcome",
        "outcome_at",
        "notes",
    )
    with connect_initialized(db_path) as conn:
        placeholders = ", ".join("?" for _ in columns)
        conn.execute(
            f"INSERT INTO dispatches ({', '.join(columns)}) VALUES ({placeholders})",
            [values.get(column) for column in columns],
        )
        conn.commit()
        return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def record_decision(db_path: str | Path, values: dict[str, Any]) -> int:
    """Insert one decision row and return its id."""
    columns = ("decided_at", "level", "decider", "artifact", "description")
    with connect_initialized(db_path) as conn:
        conn.execute(
            "INSERT INTO decisions (decided_at, level, decider, artifact, description) VALUES (?, ?, ?, ?, ?)",
            [values.get(column) for column in columns],
        )
        conn.commit()
        return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])


def mark_outcome(db_path: str | Path, dispatch_id: int, outcome: str, outcome_at: str) -> bool:
    """Update outcome fields for a dispatch id. Return True when a row changed."""
    with connect_initialized(db_path) as conn:
        cursor = conn.execute(
            "UPDATE dispatches SET outcome = ?, outcome_at = ? WHERE id = ?",
            (outcome, outcome_at, dispatch_id),
        )
        conn.commit()
        return cursor.rowcount == 1


def fetch_dispatches(db_path: str | Path, where_clause: str, value: str) -> list[sqlite3.Row]:
    """Fetch dispatches matching one equality predicate."""
    query = f"""
        SELECT id, dispatched_at, pi, sprint, feature_dir, task_id, task_title, agent_id, agent_role, outcome, outcome_at
        FROM dispatches
        WHERE {where_clause} = ?
        ORDER BY dispatched_at, id
    """
    with connect_initialized(db_path) as conn:
        return list(conn.execute(query, (value,)).fetchall())


def print_dispatch_table(rows: list[sqlite3.Row]) -> None:
    """Print dispatch rows as a compact readable table."""
    if not rows:
        print("No dispatches found.")
        return
    headers = ["id", "pi", "task", "title", "agent", "role", "outcome", "dispatched_at"]
    table = []
    for row in rows:
        table.append([
            str(row["id"]),
            row["pi"] or "",
            row["task_id"] or "",
            row["task_title"] or "",
            row["agent_id"] or "",
            row["agent_role"] or "",
            row["outcome"] or "in-flight",
            row["dispatched_at"] or "",
        ])
    widths = [len(header) for header in headers]
    for row in table:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print(" | ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in table:
        print(" | ".join(cell.ljust(width) for cell, width in zip(row, widths)))


def summary_counts(db_path: str | Path) -> dict[str, list[tuple[str, int]]]:
    """Return dispatch counts grouped by outcome, role, and PI."""
    with connect_initialized(db_path) as conn:
        outcome_rows = conn.execute(
            "SELECT COALESCE(outcome, 'in-flight') AS label, COUNT(*) AS count FROM dispatches GROUP BY label ORDER BY label"
        ).fetchall()
        role_rows = conn.execute(
            "SELECT agent_role AS label, COUNT(*) AS count FROM dispatches GROUP BY agent_role ORDER BY agent_role"
        ).fetchall()
        pi_rows = conn.execute(
            "SELECT pi AS label, COUNT(*) AS count FROM dispatches GROUP BY pi ORDER BY pi"
        ).fetchall()
    return {
        "outcome": [(row["label"], row["count"]) for row in outcome_rows],
        "role": [(row["label"], row["count"]) for row in role_rows],
        "pi": [(row["label"], row["count"]) for row in pi_rows],
    }


def print_summary(groups: dict[str, list[tuple[str, int]]]) -> None:
    """Print grouped summary counts."""
    titles = {"outcome": "By outcome", "role": "By role", "pi": "By PI"}
    for key in ("outcome", "role", "pi"):
        print(titles[key])
        rows = groups[key]
        if not rows:
            print("  (none)")
        for label, count in rows:
            print(f"  {label}: {count}")


def add_db_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="Path to the SQLite ledger database. Defaults to spec-driven-development/ledger/fleet.db.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger_cli.py",
        description="Record and query Fleet Ledger dispatch and decision rows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_dispatch_parser = subparsers.add_parser("record-dispatch", help="Record one fleet dispatch.")
    add_db_argument(record_dispatch_parser)
    record_dispatch_parser.add_argument("--dispatched-at", default=utc_now(), help="ISO 8601 dispatch timestamp. Defaults to current UTC time.")
    record_dispatch_parser.add_argument("--pi", required=True, help="Program increment, for example PI-1.")
    record_dispatch_parser.add_argument("--sprint", help="Sprint identifier, for example PI-1/sprint-2.")
    record_dispatch_parser.add_argument("--feature-dir", help="Feature directory associated with this dispatch.")
    record_dispatch_parser.add_argument("--task-id", required=True, help="Task id, for example T-001.")
    record_dispatch_parser.add_argument("--task-title", required=True, help="Human-readable task title.")
    record_dispatch_parser.add_argument("--agent-id", required=True, help="Dispatched agent id.")
    record_dispatch_parser.add_argument("--agent-role", required=True, help="Dispatched agent role.")
    record_dispatch_parser.add_argument("--outcome", choices=OUTCOMES, help="Optional outcome for already-completed dispatches.")
    record_dispatch_parser.add_argument("--outcome-at", help="ISO 8601 outcome timestamp.")
    record_dispatch_parser.add_argument("--notes", help="Optional notes.")

    decision_parser = subparsers.add_parser("record-decision", help="Record one decision-policy decision.")
    add_db_argument(decision_parser)
    decision_parser.add_argument("--decided-at", default=utc_now(), help="ISO 8601 decision timestamp. Defaults to current UTC time.")
    decision_parser.add_argument("--level", type=int, choices=(0, 1, 2), required=True, help="Decision level: 0, 1, or 2.")
    decision_parser.add_argument("--decider", required=True, help="Agent id or human.")
    decision_parser.add_argument("--artifact", help="Related artifact path or ADR id.")
    decision_parser.add_argument("--description", required=True, help="Decision description.")

    outcome_parser = subparsers.add_parser("mark-outcome", help="Mark a dispatch outcome by id.")
    add_db_argument(outcome_parser)
    outcome_parser.add_argument("dispatch_id", type=int, help="Dispatch id to update.")
    outcome_parser.add_argument("--outcome", choices=OUTCOMES, required=True, help="Final dispatch outcome.")
    outcome_parser.add_argument("--outcome-at", default=utc_now(), help="ISO 8601 outcome timestamp. Defaults to current UTC time.")

    list_pi_parser = subparsers.add_parser("list-pi", help="List dispatches for a PI.")
    add_db_argument(list_pi_parser)
    list_pi_parser.add_argument("pi", help="PI to list, for example PI-1.")

    list_feature_parser = subparsers.add_parser("list-feature", help="List dispatches for a feature directory.")
    add_db_argument(list_feature_parser)
    list_feature_parser.add_argument("feature_dir", help="Feature directory to list.")

    summary_parser = subparsers.add_parser("summary", help="Print counts by outcome, role, and PI.")
    add_db_argument(summary_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "record-dispatch":
            dispatch_id = record_dispatch(args.db, vars(args))
            print(f"Recorded dispatch {dispatch_id}")
            return 0
        if args.command == "record-decision":
            decision_id = record_decision(args.db, vars(args))
            print(f"Recorded decision {decision_id}")
            return 0
        if args.command == "mark-outcome":
            if mark_outcome(args.db, args.dispatch_id, args.outcome, args.outcome_at):
                print(f"Marked dispatch {args.dispatch_id} as {args.outcome}")
                return 0
            print(f"Dispatch not found: {args.dispatch_id}", file=sys.stderr)
            return 1
        if args.command == "list-pi":
            print_dispatch_table(fetch_dispatches(args.db, "pi", args.pi))
            return 0
        if args.command == "list-feature":
            print_dispatch_table(fetch_dispatches(args.db, "feature_dir", args.feature_dir))
            return 0
        if args.command == "summary":
            print_summary(summary_counts(args.db))
            return 0
    except (OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
