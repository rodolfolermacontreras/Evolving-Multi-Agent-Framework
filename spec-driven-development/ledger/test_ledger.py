"""Tests for Fleet Ledger v0.1.

pytest is a development dependency for this repository test suite, not a runtime
Fleet Ledger dependency.
"""

from __future__ import annotations

import ast
import sqlite3
import sys
from pathlib import Path

import pytest

LEDGER_DIR = Path(__file__).resolve().parent
if str(LEDGER_DIR) not in sys.path:
    sys.path.insert(0, str(LEDGER_DIR))

import init_ledger
import ledger_cli


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def test_init_creates_database_file(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"

    init_ledger.init_ledger(db_path)

    assert db_path.is_file()


def test_init_creates_schema_objects(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"

    init_ledger.init_ledger(db_path)

    with connect(db_path) as conn:
        tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        indexes = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}

    assert {"dispatches", "decisions"}.issubset(tables)
    assert {"idx_dispatches_pi", "idx_dispatches_feature", "idx_dispatches_agent"}.issubset(indexes)


def test_schema_has_expected_dispatch_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"
    init_ledger.init_ledger(db_path)

    with connect(db_path) as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(dispatches)")}

    assert {
        "id",
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
    }.issubset(columns)


def test_init_is_idempotent_and_preserves_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"
    init_ledger.init_ledger(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO dispatches (dispatched_at, pi, task_id, task_title, agent_id, agent_role)
            VALUES ('2026-05-12T00:00:00Z', 'PI-1', 'T-001', 'Write tests', 'india', 'developer')
            """
        )
        conn.commit()

    init_ledger.init_ledger(db_path)

    with connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]

    assert count == 1


def test_record_dispatch_then_list_pi_round_trip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db_path = tmp_path / "fleet.db"

    result = ledger_cli.main([
        "record-dispatch",
        "--db",
        str(db_path),
        "--dispatched-at",
        "2026-05-12T12:00:00Z",
        "--pi",
        "PI-1",
        "--sprint",
        "PI-1/sprint-2",
        "--feature-dir",
        "specs/2026-05-12-fleet-ledger",
        "--task-id",
        "T-001",
        "--task-title",
        "Write schema test",
        "--agent-id",
        "india",
        "--agent-role",
        "developer",
        "--notes",
        "red first",
    ])
    assert result == 0

    result = ledger_cli.main(["list-pi", "--db", str(db_path), "PI-1"])
    output = capsys.readouterr().out

    assert result == 0
    assert "T-001" in output
    assert "Write schema test" in output
    assert "india" in output


def test_list_pi_empty_prints_no_dispatches(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db_path = tmp_path / "fleet.db"

    result = ledger_cli.main(["list-pi", "--db", str(db_path), "PI-404"])
    output = capsys.readouterr().out

    assert result == 0
    assert "No dispatches found" in output


def test_mark_outcome_updates_existing_dispatch(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"
    dispatch_id = ledger_cli.record_dispatch(
        db_path,
        {
            "dispatched_at": "2026-05-12T12:00:00Z",
            "pi": "PI-1",
            "sprint": None,
            "feature_dir": None,
            "task_id": "T-002",
            "task_title": "Implement schema",
            "agent_id": "india",
            "agent_role": "developer",
            "outcome": None,
            "outcome_at": None,
            "notes": None,
        },
    )

    result = ledger_cli.main([
        "mark-outcome",
        "--db",
        str(db_path),
        str(dispatch_id),
        "--outcome",
        "success",
        "--outcome-at",
        "2026-05-12T13:00:00Z",
    ])

    with connect(db_path) as conn:
        row = conn.execute("SELECT outcome, outcome_at FROM dispatches WHERE id = ?", (dispatch_id,)).fetchone()

    assert result == 0
    assert row["outcome"] == "success"
    assert row["outcome_at"] == "2026-05-12T13:00:00Z"


def test_mark_outcome_missing_dispatch_returns_nonzero(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"

    result = ledger_cli.main([
        "mark-outcome",
        "--db",
        str(db_path),
        "999",
        "--outcome",
        "failed",
        "--outcome-at",
        "2026-05-12T13:00:00Z",
    ])

    assert result == 1


def test_list_feature_filters_by_feature_dir(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db_path = tmp_path / "fleet.db"
    ledger_cli.record_dispatch(db_path, {
        "dispatched_at": "2026-05-12T12:00:00Z",
        "pi": "PI-1",
        "sprint": None,
        "feature_dir": "specs/2026-05-12-fleet-ledger",
        "task_id": "T-003",
        "task_title": "Implement init",
        "agent_id": "india",
        "agent_role": "developer",
        "outcome": "success",
        "outcome_at": "2026-05-12T13:00:00Z",
        "notes": None,
    })
    ledger_cli.record_dispatch(db_path, {
        "dispatched_at": "2026-05-12T12:05:00Z",
        "pi": "PI-1",
        "sprint": None,
        "feature_dir": "specs/other",
        "task_id": "T-999",
        "task_title": "Other",
        "agent_id": "alpha",
        "agent_role": "qa-engineer",
        "outcome": None,
        "outcome_at": None,
        "notes": None,
    })

    result = ledger_cli.main(["list-feature", "--db", str(db_path), "specs/2026-05-12-fleet-ledger"])
    output = capsys.readouterr().out

    assert result == 0
    assert "T-003" in output
    assert "T-999" not in output


def test_record_decision_writes_row(tmp_path: Path) -> None:
    db_path = tmp_path / "fleet.db"

    result = ledger_cli.main([
        "record-decision",
        "--db",
        str(db_path),
        "--decided-at",
        "2026-05-12T14:00:00Z",
        "--level",
        "1",
        "--decider",
        "india",
        "--artifact",
        "spec.md",
        "--description",
        "Use stdlib sqlite3",
    ])

    with connect(db_path) as conn:
        row = conn.execute("SELECT level, decider, description FROM decisions").fetchone()

    assert result == 0
    assert row["level"] == 1
    assert row["decider"] == "india"
    assert row["description"] == "Use stdlib sqlite3"


def test_summary_counts_by_outcome_role_and_pi(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db_path = tmp_path / "fleet.db"
    rows = [
        ("PI-1", "T-001", "developer", "success"),
        ("PI-1", "T-002", "developer", "blocked"),
        ("PI-2", "T-003", "qa-engineer", None),
    ]
    for pi, task_id, role, outcome in rows:
        ledger_cli.record_dispatch(db_path, {
            "dispatched_at": "2026-05-12T12:00:00Z",
            "pi": pi,
            "sprint": None,
            "feature_dir": None,
            "task_id": task_id,
            "task_title": task_id,
            "agent_id": f"agent-{task_id}",
            "agent_role": role,
            "outcome": outcome,
            "outcome_at": None,
            "notes": None,
        })

    result = ledger_cli.main(["summary", "--db", str(db_path)])
    output = capsys.readouterr().out

    assert result == 0
    assert "success" in output
    assert "blocked" in output
    assert "in-flight" in output
    assert "developer" in output
    assert "qa-engineer" in output
    assert "PI-1" in output
    assert "PI-2" in output


def test_help_lists_all_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        ledger_cli.main(["--help"])
    output = capsys.readouterr().out

    assert excinfo.value.code == 0
    for command in ["record-dispatch", "record-decision", "mark-outcome", "list-pi", "list-feature", "summary"]:
        assert command in output


def test_runtime_imports_are_stdlib_only() -> None:
    allowed = {
        "__future__",
        "argparse",
        "datetime",
        "pathlib",
        "sqlite3",
        "sys",
        "typing",
        "init_ledger",
    }
    for source_path in [LEDGER_DIR / "init_ledger.py", LEDGER_DIR / "ledger_cli.py"]:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert imports <= allowed, f"Unexpected runtime import in {source_path.name}: {imports - allowed}"
