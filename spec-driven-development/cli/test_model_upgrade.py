"""Tests for cli/model_upgrade.py (SDD-015)."""

from __future__ import annotations

import ast
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
SDD_ROOT = THIS.parents[1]
sys.path.insert(0, str(CLI_DIR))

import model_upgrade  # noqa: E402


def output_fixture(path: Path, validation: bool = True, ambiguous: bool = False, quality: float = 4.0) -> Path:
    data = {
        "model": path.stem,
        "usage": {"input_tokens": 1000, "output_tokens": 500},
        "outputs": [
            {"scenario_id": "clarify-sdd-018", "validation_pass": validation, "spec_quality": quality, "commit_quality": quality, "report_quality": quality, "ambiguous_win": ambiguous},
            {"scenario_id": "spec-sdd-022", "validation_pass": validation, "spec_quality": quality, "commit_quality": quality, "report_quality": quality, "ambiguous_win": False},
        ],
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


class TestBranchName(unittest.TestCase):
    def test_branch_name_slugging(self) -> None:
        self.assertEqual(
            model_upgrade.branch_name("Claude 4.7", "GPT/5.5"),
            "model-upgrade/claude-4-7-to-gpt-5-5",
        )

    def test_empty_identifier_rejected(self) -> None:
        with self.assertRaises(model_upgrade.ModelUpgradeError):
            model_upgrade.branch_name("!!!", "new")

    def test_main_prints_branch_name(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = model_upgrade.main(["branch-name", "--old", "old model", "--new", "new model"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertEqual(out.getvalue().strip(), "model-upgrade/old-model-to-new-model")


class TestFixtures(unittest.TestCase):
    def test_workload_fixture_has_required_scenarios(self) -> None:
        data = json.loads((SDD_ROOT / "templates" / "model-upgrade-workload.json").read_text(encoding="utf-8"))
        scenarios = model_upgrade.validate_workload(data)
        self.assertEqual({item["kind"] for item in scenarios}, model_upgrade.REQUIRED_KINDS)

    def test_pricing_fixture_has_required_fields(self) -> None:
        data = json.loads((SDD_ROOT / "templates" / "model-upgrade-pricing.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertIn("old", data["models"])
        self.assertIn("new", data["models"])
        self.assertIn("source_notes", data)


class TestCompare(unittest.TestCase):
    def test_compare_writes_json_and_markdown_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_output = output_fixture(root / "old.json", quality=3.0)
            new_output = output_fixture(root / "new.json", ambiguous=True, quality=4.0)
            out_dir = root / "report"
            result = model_upgrade.compare(
                SDD_ROOT / "templates" / "model-upgrade-workload.json",
                SDD_ROOT / "templates" / "model-upgrade-pricing.json",
                old_output,
                new_output,
                out_dir,
            )
            self.assertEqual(result["recommendation"], "owner-review")
            self.assertTrue((out_dir / "comparison.json").is_file())
            self.assertTrue((out_dir / "comparison.md").is_file())
            markdown = (out_dir / "comparison.md").read_text(encoding="utf-8")
            self.assertIn("Ambiguous owner approval required: True", markdown)
            self.assertIn("Delta per-run", markdown)

    def test_cost_report_contains_required_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = model_upgrade.compare(
                SDD_ROOT / "templates" / "model-upgrade-workload.json",
                SDD_ROOT / "templates" / "model-upgrade-pricing.json",
                output_fixture(root / "old.json", quality=3.0),
                output_fixture(root / "new.json", quality=3.0),
                root / "report",
            )
            costs = result["costs"]
            self.assertIn("one_time", costs)
            self.assertIn("recurring_monthly", costs)
            self.assertIn("per_run", costs["old_model"])
            self.assertIn("per_run", costs["new_model"])
            self.assertIn("delta_per_run", costs)

    def test_compare_main_returns_owner_review_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = model_upgrade.main([
                    "compare",
                    "--fixture", str(SDD_ROOT / "templates" / "model-upgrade-workload.json"),
                    "--pricing", str(SDD_ROOT / "templates" / "model-upgrade-pricing.json"),
                    "--old-output", str(output_fixture(root / "old.json", quality=3.0)),
                    "--new-output", str(output_fixture(root / "new.json", ambiguous=True, quality=4.0)),
                    "--out-dir", str(root / "report"),
                ])
            self.assertEqual(rc, 1)
            self.assertIn("owner-review", out.getvalue())


class TestProtocolAndGuards(unittest.TestCase):
    def test_protocol_mentions_required_governance_terms(self) -> None:
        text = (SDD_ROOT / "docs" / "MODEL-UPGRADE-PROTOCOL.md").read_text(encoding="utf-8")
        for term in ["major version", "vendor swap", "model-family", "role-critical", "templates/level-2-decision.md", "model-upgrade/"]:
            self.assertIn(term, text)

    def test_imports_are_stdlib_only(self) -> None:
        tree = ast.parse(Path(model_upgrade.__file__).read_text(encoding="utf-8"))
        forbidden = {"requests", "httpx", "openai", "anthropic", "pandas", "numpy", "azure", "benchmark"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".", 1)[0]]
            else:
                continue
            self.assertFalse(forbidden.intersection(names), f"forbidden import: {names}")

    def test_no_network_imports_or_behavior(self) -> None:
        text = Path(model_upgrade.__file__).read_text(encoding="utf-8")
        self.assertNotIn("urllib", text)
        self.assertNotIn("socket", text)


if __name__ == "__main__":
    unittest.main()