"""Smoke + acceptance tests for cli/fleet.py (SDD-003)."""

from __future__ import annotations

import gc
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
FLEET = CLI_DIR / "fleet.py"
SCHEMA = SDD_ROOT / "ledger" / "schema.sql"

sys.path.insert(0, str(CLI_DIR))
sys.path.insert(0, str(SDD_ROOT / "ledger"))
import fleet  # noqa: E402


def make_env(tmp: Path):
    """Return (db_path, roster_path, dispatches_dir, feature_dir) all under tmp."""
    db = tmp / "fleet.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    roster = tmp / "agents.json"
    roster.write_text(json.dumps([
        {"id": "developer-general", "kind": "generic", "role": "developer"},
        {"id": "qa-engineer-general", "kind": "generic", "role": "qa-engineer"},
    ]), encoding="utf-8")
    dispatches_dir = tmp / "dispatches"
    dispatches_dir.mkdir()
    feature = tmp / "specs" / "2026-05-16-thingy"
    feature.mkdir(parents=True)
    (feature / "tasks.md").write_text(
        "| Task ID | Tag | Description | File Scope | Acceptance Test |\n"
        "|---------|-----|-------------|------------|-----------------|\n"
        "| T-001 | [S] | Wire the gizmo | cli/gizmo.py | Proves AC1 |\n",
        encoding="utf-8",
    )
    return db, roster, dispatches_dir, feature


class FleetSDD003(unittest.TestCase):

    def setUp(self):
        # ignore_cleanup_errors needed on Windows: sqlite3.Connection holds the
        # db file open until GC, which races with TemporaryDirectory cleanup.
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.db, self.roster, self.dispatches_dir, self.feature = make_env(self.tmp)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _dispatch_args(self, task="T-001", agent="developer-general"):
        return ["dispatch", "--db", str(self.db),
                "--roster", str(self.roster),
                "--dispatches-dir", str(self.dispatches_dir),
                "--task", task, "--agent", agent,
                "--feature", str(self.feature),
                "--pi", "PI-2", "--sprint", "A"]

    def test_dispatch_inserts_row_and_writes_packet(self):
        """AC1."""
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
        # Packet file exists
        packet = self.dispatches_dir / "PI-2" / f"{r['id']:06d}.md"
        self.assertTrue(packet.is_file(), f"packet not written: {packet}")

    def test_mark_outcome_updates_row(self):
        """AC2."""
        fleet.main(self._dispatch_args())
        with sqlite3.connect(self.db) as conn:
            did = conn.execute("SELECT id FROM dispatches").fetchone()[0]
        rc = fleet.main(["mark-outcome", str(did), "--outcome", "success", "--db", str(self.db)])
        self.assertEqual(rc, 0)
        with sqlite3.connect(self.db) as conn:
            row = conn.execute("SELECT outcome, outcome_at FROM dispatches WHERE id=?", [did]).fetchone()
        self.assertEqual(row[0], "success")
        self.assertIsNotNone(row[1])

    def test_mark_outcome_unknown_id_fails_cleanly(self):
        """AC2 edge."""
        rc = fleet.main(["mark-outcome", "9999", "--outcome", "failed", "--db", str(self.db)])
        self.assertNotEqual(rc, 0)

    def test_status_lists_in_flight_only(self):
        """AC3."""
        fleet.main(self._dispatch_args())
        # Pipe stdout
        from io import StringIO
        buf = StringIO()
        orig = sys.stdout
        sys.stdout = buf
        try:
            rc = fleet.main(["status", "--db", str(self.db)])
        finally:
            sys.stdout = orig
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("developer-general", out)

    def test_status_empty_message(self):
        """AC3 edge."""
        from io import StringIO
        buf = StringIO()
        orig = sys.stdout
        sys.stdout = buf
        try:
            rc = fleet.main(["status", "--db", str(self.db)])
        finally:
            sys.stdout = orig
        self.assertEqual(rc, 0)
        self.assertIn("no in-flight dispatches", buf.getvalue())

    def test_list_by_pi_and_feature(self):
        """AC4."""
        fleet.main(self._dispatch_args())
        from io import StringIO
        buf = StringIO()
        orig = sys.stdout
        sys.stdout = buf
        try:
            rc1 = fleet.main(["list", "--pi", "PI-2", "--db", str(self.db)])
        finally:
            sys.stdout = orig
        self.assertEqual(rc1, 0)
        self.assertIn("T-001", buf.getvalue())

    def test_dispatch_unknown_agent_fails(self):
        """AC5."""
        rc = fleet.main(self._dispatch_args(agent="ghost-agent-9000"))
        self.assertNotEqual(rc, 0)

    def test_packet_contains_required_fields(self):
        """AC6."""
        fleet.main(self._dispatch_args())
        packet = next((self.dispatches_dir / "PI-2").iterdir())
        text = packet.read_text(encoding="utf-8")
        # Task id, feature ref, agent role, file scope from tasks.md
        self.assertIn("T-001", text)
        self.assertIn("developer", text)        # role mentioned somewhere
        self.assertIn("cli/gizmo.py", text)      # File Scope scraped from tasks.md

    def test_help_shows_all_subcommands(self):
        """AC7."""
        result = subprocess.run(
            [sys.executable, str(FLEET), "--help"],
            capture_output=True, text=True, check=True,
        )
        for sub in ("dispatch", "mark-outcome", "status", "list"):
            self.assertIn(sub, result.stdout, f"--help missing subcommand: {sub}")

    def test_runtime_imports_are_stdlib_plus_local_only(self):
        """AC8."""
        import ast
        tree = ast.parse(FLEET.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        local_ok = {"ledger_cli", "fleet"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(top in stdlib or top in local_ok,
                                    f"non-stdlib/non-local import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module is None: continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(top in stdlib or top in local_ok,
                                f"non-stdlib/non-local import: {node.module}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
