"""Acceptance tests for cli/retro.py (SDD-005).

Covers AC1-AC8 from spec-driven-development/specs/2026-05-16-retro-cli/spec.md.
AC9 (--help) is validated manually.
"""

from __future__ import annotations

import ast
import gc
import sqlite3
import sys
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
SCHEMA = SDD_ROOT / "ledger" / "schema.sql"

sys.path.insert(0, str(CLI_DIR))
sys.path.insert(0, str(SDD_ROOT / "ledger"))
import retro  # noqa: E402


def _seed_db(db: Path, rows: list[dict]) -> None:
    """Insert dispatch rows into the database."""
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        for r in rows:
            conn.execute(
                "INSERT INTO dispatches "
                "(dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
                "agent_id, agent_role, outcome, outcome_at, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    r.get("dispatched_at", "2026-05-16T10:00:00Z"),
                    r.get("pi", "PI-2"),
                    r.get("sprint"),
                    r.get("feature_dir"),
                    r.get("task_id", "T-001"),
                    r.get("task_title", "Test task"),
                    r.get("agent_id", "dev-general"),
                    r.get("agent_role", "developer"),
                    r.get("outcome"),
                    r.get("outcome_at"),
                    r.get("notes"),
                ),
            )
        conn.commit()


def _make_env(tmp: Path, dispatches: list[dict] | None = None,
              features: dict[str, str] | None = None,
              lessons_content: str | None = None) -> Path:
    """Build a minimal SDD root under *tmp*.

    Returns the sdd_root path.
    """
    sdd = tmp / "sdd"
    sdd.mkdir()

    # Ledger
    db = sdd / "ledger" / "fleet.db"
    db.parent.mkdir(parents=True)
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    if dispatches:
        _seed_db(db, dispatches)

    # Specs
    specs_dir = sdd / "specs"
    specs_dir.mkdir()
    if features:
        for name, status in features.items():
            feat = specs_dir / name
            feat.mkdir(parents=True)
            (feat / "spec.md").write_text(
                f"# Feature Spec: {name}\n\n- Status: {status}\n",
                encoding="utf-8",
            )

    # Sprints / lessons
    sprints = sdd / "sprints" / "PI-2"
    sprints.mkdir(parents=True)
    if lessons_content is not None:
        (sprints / "lessons.md").write_text(lessons_content, encoding="utf-8")

    return sdd


SAMPLE_DISPATCHES = [
    {"pi": "PI-2", "sprint": "Sprint A", "task_id": "T-001",
     "task_title": "Build widget", "agent_id": "dev-alpha",
     "agent_role": "developer", "outcome": "success",
     "feature_dir": "specs/2026-05-16-widget"},
    {"pi": "PI-2", "sprint": "Sprint A", "task_id": "T-002",
     "task_title": "Test widget", "agent_id": "qa-beta",
     "agent_role": "qa-engineer", "outcome": "success",
     "feature_dir": "specs/2026-05-16-widget"},
    {"pi": "PI-2", "sprint": "Sprint A", "task_id": "T-003",
     "task_title": "Deploy gadget", "agent_id": "dev-alpha",
     "agent_role": "developer", "outcome": "failed",
     "feature_dir": "specs/2026-05-16-gadget"},
    {"pi": "PI-2", "sprint": "Sprint B", "task_id": "T-004",
     "task_title": "Fix blocked", "agent_id": "dev-gamma",
     "agent_role": "developer", "outcome": "blocked",
     "feature_dir": "specs/2026-05-16-gadget"},
]

SAMPLE_LESSONS = """\
# PI-2 Lessons

---

### LESSON-005: EM should recommend, not present a menu

- Date: 2026-05-16
- Source feature: specs/2026-05-16-state-dashboard
- Tag: ux-improvement
- Status: shipped

### LESSON-006: Closure ceremonies must touch ALL current markers

- Date: 2026-05-16
- Source feature: specs/2026-05-16-state-dashboard
- Tag: process-gap
- Status: open
"""


class TestRetroCLI(unittest.TestCase):
    """Acceptance tests for retro.py (SDD-005)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    # ------------------------------------------------------------------ AC1
    def test_full_retro_produces_all_sections(self):
        """AC1: Full retro output contains header, Delivered, Signals, Lessons."""
        sdd = _make_env(
            self.tmp,
            dispatches=SAMPLE_DISPATCHES,
            features={"2026-05-16-widget": "Done"},
            lessons_content=SAMPLE_LESSONS,
        )
        buf = StringIO()
        with redirect_stdout(buf):
            rc = retro.main(["--sdd-root", str(sdd), "--pi", "PI-2"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("# Sprint Retrospective", out)
        self.assertIn("## Delivered", out)
        self.assertIn("## Signals and Evidence", out)
        self.assertIn("## Lessons Summary", out)
        self.assertIn("## Action Items", out)

    # ------------------------------------------------------------------ AC2
    def test_dispatch_metrics_from_ledger(self):
        """AC2: Signals section shows correct dispatch counts."""
        sdd = _make_env(self.tmp, dispatches=SAMPLE_DISPATCHES)
        buf = StringIO()
        with redirect_stdout(buf):
            retro.main(["--sdd-root", str(sdd), "--pi", "PI-2"])
        out = buf.getvalue()
        self.assertIn("Total dispatches: 4", out)
        self.assertIn("Successful: 2", out)
        self.assertIn("Failed: 1", out)
        self.assertIn("Blocked: 1", out)
        self.assertIn("Unique agents: 3", out)
        self.assertIn("Unique features: 2", out)

    # ------------------------------------------------------------------ AC3
    def test_delivered_features_from_specs(self):
        """AC3: Delivered section lists features with Status: Done."""
        sdd = _make_env(
            self.tmp,
            features={
                "2026-05-16-widget": "Done",
                "2026-05-16-gadget": "Draft",
            },
        )
        buf = StringIO()
        with redirect_stdout(buf):
            retro.main(["--sdd-root", str(sdd), "--pi", "PI-2"])
        out = buf.getvalue()
        self.assertIn("2026-05-16-widget", out)
        self.assertNotIn("2026-05-16-gadget", out)

    # ------------------------------------------------------------------ AC4
    def test_lessons_summary_from_file(self):
        """AC4: Lessons Summary lists lessons with status and tag."""
        sdd = _make_env(self.tmp, lessons_content=SAMPLE_LESSONS)
        buf = StringIO()
        with redirect_stdout(buf):
            retro.main(["--sdd-root", str(sdd), "--pi", "PI-2"])
        out = buf.getvalue()
        self.assertIn("LESSON-005", out)
        self.assertIn("shipped", out)
        self.assertIn("LESSON-006", out)
        self.assertIn("open", out)

    # ------------------------------------------------------------------ AC5
    def test_output_writes_to_file(self):
        """AC5: --output writes to file instead of stdout."""
        sdd = _make_env(self.tmp, dispatches=SAMPLE_DISPATCHES)
        out_path = self.tmp / "retro-output.md"
        buf = StringIO()
        with redirect_stdout(buf):
            rc = retro.main([
                "--sdd-root", str(sdd), "--pi", "PI-2",
                "--output", str(out_path),
            ])
        self.assertEqual(rc, 0)
        self.assertTrue(out_path.exists())
        content = out_path.read_text(encoding="utf-8")
        self.assertIn("# Sprint Retrospective", content)
        # stdout should be minimal (just a confirmation), not the full doc
        self.assertNotIn("## Signals and Evidence", buf.getvalue())

    # ------------------------------------------------------------------ AC6
    def test_sprint_filter(self):
        """AC6: --sprint filters dispatches to that sprint."""
        sdd = _make_env(self.tmp, dispatches=SAMPLE_DISPATCHES)
        buf = StringIO()
        with redirect_stdout(buf):
            retro.main([
                "--sdd-root", str(sdd), "--pi", "PI-2",
                "--sprint", "Sprint A",
            ])
        out = buf.getvalue()
        # Sprint A has 3 dispatches (T-001, T-002, T-003)
        self.assertIn("Total dispatches: 3", out)
        self.assertIn("Successful: 2", out)
        self.assertIn("Failed: 1", out)
        # T-004 (blocked, Sprint B) should not appear
        self.assertIn("Blocked: 0", out)

    # ------------------------------------------------------------------ AC7
    def test_empty_ledger_graceful(self):
        """AC7: Empty ledger shows zero counts with note."""
        sdd = _make_env(self.tmp)
        buf = StringIO()
        with redirect_stdout(buf):
            rc = retro.main(["--sdd-root", str(sdd), "--pi", "PI-2"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("Total dispatches: 0", out)
        self.assertIn("no dispatches recorded", out.lower())

    # ------------------------------------------------------------------ AC8
    def test_runtime_imports_are_stdlib_only(self):
        """AC8: Only stdlib + framework ledger modules imported at runtime."""
        source = (CLI_DIR / "retro.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        allowed_third_party = {"init_ledger"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    self.assertTrue(
                        top in sys.stdlib_module_names or top in allowed_third_party,
                        f"Non-stdlib import: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    self.assertTrue(
                        top in sys.stdlib_module_names or top in allowed_third_party,
                        f"Non-stdlib import-from: {node.module}",
                    )


if __name__ == "__main__":
    unittest.main()
