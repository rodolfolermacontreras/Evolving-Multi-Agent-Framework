"""Acceptance tests for cli/fleet.py (SDD-003).

Covers AC1-AC9 from spec-driven-development/specs/2026-05-16-fleet-cli/spec.md.
AC10 (--help) is validated manually.
"""

from __future__ import annotations

import ast
import gc
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
FLEET_PY = CLI_DIR / "fleet.py"
SCHEMA = SDD_ROOT / "ledger" / "schema.sql"

sys.path.insert(0, str(CLI_DIR))
sys.path.insert(0, str(SDD_ROOT / "ledger"))
import fleet  # noqa: E402


TASKS_MD = """\
| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------------------------|--------|
| T-001 | [S] | Wire the gizmo | `cli/gizmo.py` | Proves AC1 | S | None | AFK | Yes | pending |
| T-002 | [S] | Test the widget | `cli/widget.py` | Validates widget | S | T-001 | AFK | Yes | pending |
| T-003 | [M] | Build the frobulator | `cli/frob.py` | Frobulates correctly | M | None | AFK | No | pending |
"""


def make_env(tmp: Path, tasks_content: str = TASKS_MD):
    """Create (db_path, roster_path, feature_dir) under *tmp*."""
    db = tmp / "fleet.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    roster = tmp / "agents.json"
    roster.write_text(json.dumps([
        {"id": "developer-general", "kind": "generic", "role": "developer"},
        {"id": "qa-engineer-general", "kind": "generic", "role": "qa-engineer"},
    ]), encoding="utf-8")
    feature = tmp / "specs" / "2026-05-16-thingy"
    feature.mkdir(parents=True)
    (feature / "tasks.md").write_text(tasks_content, encoding="utf-8")
    return db, roster, feature


class TestFleetCLI(unittest.TestCase):
    """Acceptance tests for fleet.py (SDD-003)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.db, self.roster, self.feature = make_env(self.tmp)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _dispatch_args(self, tasks="T-001", agent="developer-general"):
        return [
            "dispatch",
            "--feature", str(self.feature),
            "--tasks", tasks,
            "--agent", agent,
            "--pi", "PI-2",
            "--db", str(self.db),
            "--roster", str(self.roster),
        ]

    # ------------------------------------------------------------------ AC1
    def test_dispatch_prints_brief_to_stdout(self):
        """AC1: dispatch prints markdown brief with task ID, description,
        file scope, acceptance test, and agent role."""
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main(self._dispatch_args())
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("Wire the gizmo", out)
        self.assertIn("cli/gizmo.py", out)
        self.assertIn("Proves AC1", out)
        self.assertIn("developer", out)

    # ------------------------------------------------------------------ AC2
    def test_dispatch_writes_ledger_row(self):
        """AC2: dispatch writes a row to fleet.db with correct fields."""
        with redirect_stdout(StringIO()):
            rc = fleet.main(self._dispatch_args())
        self.assertEqual(rc, 0)
        with sqlite3.connect(self.db) as conn:
            conn.row_factory = sqlite3.Row
            rows = list(conn.execute("SELECT * FROM dispatches"))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["task_id"], "T-001")
        self.assertEqual(r["pi"], "PI-2")
        self.assertEqual(r["agent_id"], "developer-general")
        self.assertEqual(r["agent_role"], "developer")
        self.assertIsNotNone(r["dispatched_at"])
        self.assertIsNotNone(r["feature_dir"])

    # ------------------------------------------------------------------ AC3
    def test_batch_dispatch_multiple_tasks(self):
        """AC3: --tasks T-001,T-002 produces one brief + one row per task."""
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main(self._dispatch_args(tasks="T-001,T-002"))
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("T-002", out)
        self.assertIn("Wire the gizmo", out)
        self.assertIn("Test the widget", out)
        with sqlite3.connect(self.db) as conn:
            rows = conn.execute("SELECT * FROM dispatches ORDER BY id").fetchall()
        self.assertEqual(len(rows), 2)

    # ------------------------------------------------------------------ AC4
    def test_dispatch_saves_briefs_to_output_dir(self):
        """AC4: --output-dir saves briefs as dispatch-<id>-<task_id>.md."""
        out_dir = self.tmp / "briefs"
        out_dir.mkdir()
        with redirect_stdout(StringIO()):
            rc = fleet.main(self._dispatch_args() + ["--output-dir", str(out_dir)])
        self.assertEqual(rc, 0)
        files = sorted(out_dir.iterdir())
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertTrue(f.name.startswith("dispatch-"), f"unexpected name: {f.name}")
        self.assertIn("T-001", f.name)
        self.assertTrue(f.name.endswith(".md"))
        content = f.read_text(encoding="utf-8")
        self.assertIn("T-001", content)
        self.assertIn("Wire the gizmo", content)

    # ------------------------------------------------------------------ AC5
    def test_mark_outcome_updates_dispatch(self):
        """AC5: mark --dispatch-id <id> --outcome success updates outcome + outcome_at."""
        with redirect_stdout(StringIO()):
            fleet.main(self._dispatch_args())
        with sqlite3.connect(self.db) as conn:
            did = conn.execute("SELECT id FROM dispatches").fetchone()[0]
        with redirect_stdout(StringIO()):
            rc = fleet.main([
                "mark", "--dispatch-id", str(did),
                "--outcome", "success",
                "--db", str(self.db),
            ])
        self.assertEqual(rc, 0)
        with sqlite3.connect(self.db) as conn:
            row = conn.execute(
                "SELECT outcome, outcome_at FROM dispatches WHERE id=?", [did],
            ).fetchone()
        self.assertEqual(row[0], "success")
        self.assertIsNotNone(row[1])

    # ------------------------------------------------------------------ AC6
    def test_status_lists_feature_dispatches(self):
        """AC6: status --feature <dir> lists dispatches in readable table."""
        with redirect_stdout(StringIO()):
            fleet.main(self._dispatch_args())
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main([
                "status",
                "--feature", str(self.feature),
                "--db", str(self.db),
            ])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("developer-general", out)

    # ------------------------------------------------------------------ AC7
    def test_ineligible_task_rejected(self):
        """AC7: task with Fleet Dispatch Eligible = No is rejected with error."""
        buf = StringIO()
        with redirect_stderr(buf):
            rc = fleet.main(self._dispatch_args(tasks="T-003"))
        self.assertNotEqual(rc, 0)
        self.assertIn("not eligible", buf.getvalue().lower())
        # No ledger row should exist
        with sqlite3.connect(self.db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
        self.assertEqual(count, 0)

    # ------------------------------------------------------------------ AC8
    def test_missing_tasks_md_error(self):
        """AC8: missing tasks.md exits with clear error."""
        empty_feature = self.tmp / "no-tasks"
        empty_feature.mkdir()
        buf = StringIO()
        with redirect_stderr(buf):
            rc = fleet.main([
                "dispatch",
                "--feature", str(empty_feature),
                "--tasks", "T-001",
                "--agent", "developer-general",
                "--pi", "PI-2",
                "--db", str(self.db),
                "--roster", str(self.roster),
            ])
        self.assertNotEqual(rc, 0)
        self.assertIn("tasks.md", buf.getvalue())

    # ------------------------------------------------------------------ AC9
    def test_runtime_imports_are_stdlib_only(self):
        """AC9: only stdlib + local ledger modules imported at runtime."""
        tree = ast.parse(FLEET_PY.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        local_ok = {"ledger_cli", "init_ledger", "fleet"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(
                        top in stdlib or top in local_ok,
                        f"non-stdlib/non-local import: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(
                    top in stdlib or top in local_ok,
                    f"non-stdlib/non-local import: {node.module}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
