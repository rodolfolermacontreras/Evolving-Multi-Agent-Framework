"""Smoke + acceptance tests for cli/state_builder.py.

Covers TWO feature contracts:

* SDD-002 (state_builder spec): nine named acceptance tests AC1-AC10 (AC9 manual).
* state-dashboard (live HTML + Bridge UX): server liveness, self-contained HTML,
  Kanban contents, multi-segment progress, color-coded commit tags.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import sqlite3
import tempfile
import time
import unittest
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
BUILDER = CLI_DIR / "state_builder.py"
EXEC_DIR = SDD_ROOT / "exec"

sys.path.insert(0, str(CLI_DIR))
import state_builder  # noqa: E402


def make_minimal_sdd_root(tmp: Path) -> Path:
    """Create a minimal but valid SDD root in tmp, return its path."""
    root = tmp / "sdd"
    (root / "constitution").mkdir(parents=True)
    (root / "specs").mkdir()
    (root / "backlog").mkdir()
    (root / "roster").mkdir()
    (root / "ledger").mkdir()
    (root / "exec").mkdir()

    (root / "constitution" / "roadmap.md").write_text(
        "## PI-1: First (closed 2026-01-01)\n\n"
        "- [x] All commitments shipped\n\n"
        "## PI-2: Second (current)\n\n"
        "- [ ] Build state_builder\n"
        "- [ ] Build fleet.py\n"
        "- [x] Approve plan\n", encoding="utf-8",
    )
    (root / "backlog" / "BACKLOG.md").write_text(
        "# Backlog\n\n"
        "| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |\n"
        "|----|-------|----------|-------|--------|------------|--------|------|--------|--------|\n"
        "| SDD-002 | state_builder | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 Sprint A | Approved |\n"
        "| SDD-003 | fleet.py | P2 | 8 | 3 | 0.8 | 3 | 6.4 | PI-2 Sprint A | Approved |\n"
        "| SDD-004 | qa.py | P2 | 6 | 2 | 0.8 | 2 | 4.8 | PI-2 Sprint B | Approved |\n",
        encoding="utf-8",
    )
    (root / "roster" / "agents.json").write_text(json.dumps([
        {"id": "principal-em", "kind": "principal", "role": "executive-manager"},
        {"id": "developer-general", "kind": "generic", "role": "developer"},
        {"id": "qa-engineer-general", "kind": "generic", "role": "qa-engineer"},
    ]), encoding="utf-8")
    (root / "roster" / "skills.json").write_text(json.dumps([
        {"id": "sdd-constitution", "category": "core"},
        {"id": "tdd", "category": "engineering"},
        {"id": "handoff", "category": "operational"},
        {"id": "code-review", "category": "engineering"},
        {"id": "pytest-runner", "category": "domain"},
    ]), encoding="utf-8")

    # A done feature with status line
    f1 = root / "specs" / "2026-01-01-feature-one"
    f1.mkdir()
    (f1 / "spec.md").write_text("---\nstatus: done\n---\n# Feature One\n", encoding="utf-8")
    (f1 / "validation.md").write_text("# Validation\n\n- [x] All checks pass\n", encoding="utf-8")
    (f1 / "RETRO.md").write_text("# Retro\n", encoding="utf-8")

    # An in-progress feature
    f2 = root / "specs" / "2026-02-01-feature-two"
    f2.mkdir()
    (f2 / "spec.md").write_text("---\nstatus: implementing\n---\n# Feature Two\n", encoding="utf-8")
    (f2 / "validation.md").write_text("# Validation\n\n- [x] one\n- [ ] two\n- [ ] three\n", encoding="utf-8")

    # A spec-only feature
    f3 = root / "specs" / "2026-03-01-feature-three"
    f3.mkdir()
    (f3 / "spec.md").write_text("# Feature Three\n", encoding="utf-8")

    # Seed fleet.db with one success and one stale-blocker dispatch
    db = root / "ledger" / "fleet.db"
    schema = (SDD_ROOT / "ledger" / "schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db) as conn:
        conn.executescript(schema)
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
            "agent_id, agent_role, outcome, outcome_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            ["2026-04-01T10:00:00Z", "PI-2", "A", "2026-01-01-feature-one",
             "T-001", "implement feature one", "developer-general", "developer",
             "success", "2026-04-01T12:00:00Z"],
        )
        old_iso = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat().replace("+00:00", "Z")
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
            "agent_id, agent_role, outcome) VALUES (?,?,?,?,?,?,?,?,?)",
            [old_iso, "PI-2", "A", "2026-02-01-feature-two",
             "T-009", "implement feature two", "developer-general", "developer", None],
        )
        conn.commit()
    return root


class SDD002Acceptance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = make_minimal_sdd_root(Path(cls._tmp.name))
        state_builder.build(sdd_root=cls.root, write=True, fixed_date="2026-05-16")
        cls.md = (cls.root / "exec" / "state.md").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_full_build_produces_all_sections(self) -> None:
        """AC1."""
        for header in ("# Executive State", "## Spec Pipeline", "## Sprint Plan",
                       "## Fleet", "## Recently Completed", "## Blockers", "## Next Milestones"):
            self.assertIn(header, self.md, f"missing section: {header}")
        self.assertIn("Generated date: 2026-05-16", self.md)

    def test_recently_completed_from_dispatches(self) -> None:
        """AC2."""
        block = self.md.split("## Recently Completed", 1)[1].split("##", 1)[0]
        self.assertIn("implement feature one", block)
        self.assertIn("developer-general", block)

    def test_blockers_from_stale_dispatches(self) -> None:
        """AC3."""
        block = self.md.split("## Blockers", 1)[1].split("##", 1)[0]
        self.assertIn("implement feature two", block)
        self.assertIn("developer-general", block)

    def test_pipeline_from_spec_dirs(self) -> None:
        """AC4."""
        block = self.md.split("## Spec Pipeline", 1)[1].split("##", 1)[0]
        self.assertIn("feature-one", block)
        self.assertIn("feature-two", block)
        self.assertIn("feature-three", block)
        self.assertIn("DONE", block)
        self.assertIn("IMPLEMENT", block)

    def test_sprint_plan_from_backlog(self) -> None:
        """AC5."""
        block = self.md.split("## Sprint Plan", 1)[1].split("## Fleet", 1)[0]
        self.assertIn("PI-2 Sprint A", block)
        self.assertIn("PI-2 Sprint B", block)
        self.assertIn("SDD-002", block)
        self.assertIn("SDD-004", block)

    def test_fleet_counts_from_roster(self) -> None:
        """AC6."""
        block = self.md.split("## Fleet", 1)[1].split("## Recently", 1)[0]
        self.assertIn("Principals: 1", block)
        self.assertIn("Generic workers: 2", block)
        self.assertIn("Specialists: 0", block)
        self.assertIn("Total agents: 3", block)
        self.assertIn("Skills registered: 5", block)

    def test_deterministic_output(self) -> None:
        """AC7."""
        info1 = state_builder.build(sdd_root=self.root, write=False, fixed_date="2026-05-16")
        info2 = state_builder.build(sdd_root=self.root, write=False, fixed_date="2026-05-16")
        self.assertEqual(info1["markdown"], info2["markdown"])

    def test_runtime_imports_are_stdlib_only(self) -> None:
        """AC8."""
        import ast
        tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertIn(top, stdlib, f"non-stdlib import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertIn(top, stdlib, f"non-stdlib import: {node.module}")

    def test_dry_run_prints_to_stdout(self) -> None:
        """AC10."""
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--sdd-root", str(self.root), "--dry-run"],
            capture_output=True, text=True, check=True,
        )
        for header in ("# Executive State", "## Spec Pipeline", "## Sprint Plan",
                       "## Fleet", "## Recently Completed", "## Blockers", "## Next Milestones"):
            self.assertIn(header, result.stdout)


class StateDashboardVisual(unittest.TestCase):

    def test_html_is_self_contained_and_has_bridge_tokens(self) -> None:
        state_builder.build(sdd_root=SDD_ROOT, write=True)
        content = (EXEC_DIR / "state.html").read_text(encoding="utf-8")
        self.assertIn("<style>", content)
        self.assertNotIn('<link rel="stylesheet"', content)
        self.assertNotIn("<script src=", content)
        for token in ("--bg-carbon", "--accent-oxblood", "--signal-jade", "--signal-amber"):
            self.assertIn(token, content)

    def test_html_contains_multi_segment_progress_and_color_borders(self) -> None:
        state_builder.build(sdd_root=SDD_ROOT, write=True)
        content = (EXEC_DIR / "state.html").read_text(encoding="utf-8")
        self.assertIn("seg-bar", content)
        self.assertIn("tone-jade", content)
        self.assertIn('class="card tone-', content)
        self.assertIn('class="count"', content)

    def test_html_has_action_cta_and_refresh_button(self) -> None:
        state_builder.build(sdd_root=SDD_ROOT, write=True)
        content = (EXEC_DIR / "state.html").read_text(encoding="utf-8")
        self.assertIn('class="cta"', content)
        self.assertIn("btn-refresh", content)


class LiveServerSmoke(unittest.TestCase):

    @staticmethod
    def _free_port() -> int:
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def test_serve_responds_to_requests(self) -> None:
        port = self._free_port()
        proc = subprocess.Popen(
            [sys.executable, str(BUILDER), "serve", "--port", str(port), "--no-open"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            url = f"http://127.0.0.1:{port}/"
            healthz = f"http://127.0.0.1:{port}/healthz"
            ready = False
            for _ in range(40):
                if proc.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(healthz, timeout=1) as r:
                        if r.status == 200 and r.read() == b"ok":
                            ready = True
                            break
                except Exception:
                    time.sleep(0.2)
            self.assertTrue(ready, "server did not become ready in time")

            with urllib.request.urlopen(url, timeout=5) as r:
                self.assertEqual(r.status, 200)
                body = r.read().decode("utf-8")
                self.assertIn("Bridge", body)
                self.assertIn("Lifecycle Kanban", body)
                self.assertIn("Recommended next action", body)
                self.assertIn('http-equiv="refresh"', body)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    unittest.main(verbosity=2)
