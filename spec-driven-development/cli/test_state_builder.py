"""Smoke tests for cli/state_builder.py -- stdlib + unittest only."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
BUILDER = SDD_ROOT / "cli" / "state_builder.py"
EXEC_DIR = SDD_ROOT / "exec"


class StateBuilderSmoke(unittest.TestCase):

    def test_module_imports_and_build_runs_dry(self) -> None:
        # Add cli/ to sys.path and call build() directly with write=False
        sys.path.insert(0, str(SDD_ROOT / "cli"))
        try:
            import state_builder
            info = state_builder.build(write=False)
        finally:
            sys.path.pop(0)
        self.assertIn("markdown_chars", info)
        self.assertIn("html_chars", info)
        self.assertGreater(info["markdown_chars"], 200)
        self.assertGreater(info["html_chars"], 2000)
        self.assertGreaterEqual(info["features"], 1)
        self.assertGreaterEqual(info["commits"], 1)

    def test_cli_json_mode_writes_outputs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--json"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("wrote", payload)
        for p in payload["wrote"]:
            self.assertTrue(Path(p).is_file(), f"output not written: {p}")

    def test_html_is_self_contained(self) -> None:
        html_path = EXEC_DIR / "state.html"
        # Ensure file exists (may have been written by previous test)
        if not html_path.is_file():
            subprocess.run([sys.executable, str(BUILDER), "--json"], check=True, capture_output=True)
        content = html_path.read_text(encoding="utf-8")
        self.assertIn("<style>", content, "HTML must inline its CSS")
        # No external CSS/JS links
        for forbidden in ('<link rel="stylesheet"', "<script src="):
            self.assertNotIn(forbidden, content, f"HTML must be self-contained: found {forbidden}")
        # Bridge design tokens present
        self.assertIn("--bg-carbon", content)
        self.assertIn("--accent-oxblood", content)
        # Core sections present
        self.assertIn("Recommended next action", content)
        self.assertIn("Lifecycle Kanban", content)
        self.assertIn("Fleet Roster", content)

    def test_kanban_contains_known_features(self) -> None:
        html_path = EXEC_DIR / "state.html"
        if not html_path.is_file():
            subprocess.run([sys.executable, str(BUILDER), "--json"], check=True, capture_output=True)
        content = html_path.read_text(encoding="utf-8")
        # The three features we know exist on disk
        self.assertIn("fleet-ledger", content)
        self.assertIn("fleet-bridge-dashboard", content)
        self.assertIn("state-dashboard", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
