"""Tests for cli/origin_lint.py config-aware denylist (SDD-047 / A-2 R-5, A-3).

Covers:
- ``load_config_denylist`` reads the host owner name from ``project.config.json``
  and folds it into a tightened denylist (A-2 R-5).
- A re-added personal name in a generic file FAILS the lint (A-2 R-5).
- The tightened denylist scrubs origin-project tokens (A-3 R-1).
- A labeled ``<!-- example: -->`` block exempts otherwise-flagged content.

Stdlib only (LESSON-001 / Article V).
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import origin_lint  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_config(root: Path, owner: str) -> None:
    _write(
        root / "project.config.json",
        json.dumps({"owner": owner, "team": "Some Team",
                    "repo_url": "https://example.com/x"}),
    )


class TestLoadConfigDenylist(unittest.TestCase):
    def test_includes_owner_name_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            patterns = origin_lint.load_config_denylist(root)
            self.assertIn(re.escape("Jane Doe"), patterns)

    def test_missing_config_no_owner_no_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            patterns = origin_lint.load_config_denylist(root)
            # Still returns the tightened base patterns, no owner pattern.
            self.assertIn(r"engine\.py", patterns)
            self.assertNotIn("", patterns)

    def test_includes_origin_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            patterns = origin_lint.load_config_denylist(root)
            joined = "\n".join(patterns)
            for token in ("Day-to-Day", "FastAPI", "HTMX",
                          "World State", "Outlander"):
                self.assertIn(token, joined)


class TestReaddedNameFailsLint(unittest.TestCase):
    def test_personal_name_in_generic_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "agents" / "foo.agent.md",
                "# Agent\n\nOwner: Jane Doe builds the thing.\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertTrue(
                any("Jane Doe" in token for _p, _ln, token, _line in findings),
                msg=f"expected a Jane Doe finding, got {findings!r}",
            )

    def test_name_inside_example_block_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "agents" / "foo.agent.md",
                "# Agent\n\n<!-- example: history\n"
                "Originally authored by Jane Doe.\n"
                "-->\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertEqual(
                [], findings, msg=f"example block should exempt name: {findings!r}"
            )


class TestOriginTokensScrubbed(unittest.TestCase):
    def test_unwrapped_origin_token_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "skills" / "x" / "SKILL.md",
                "# Skill\n\nUse the FastAPI route helper here.\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertTrue(
                any("FastAPI" in token for _p, _ln, token, _line in findings)
            )

    def test_wrapped_origin_token_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "skills" / "x" / "SKILL.md",
                "# Skill\n\n<!-- example: history --> FastAPI <!-- /example -->\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertEqual([], findings)


class TestDomainExampleSkillsExempt(unittest.TestCase):
    def test_domain_skill_origin_token_not_flagged(self) -> None:
        # Domain skills are labeled EXAMPLE reference implementations; their
        # stack tokens (FastAPI/HTMX) are legitimate (R-A3-4 no concept loss).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "skills" / "domain" / "web" / "SKILL.md",
                "# EXAMPLE Skill\n\nUse the FastAPI route helper with HTMX.\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertEqual(
                [], findings,
                msg=f"domain example skills must be exempt: {findings!r}",
            )

    def test_non_domain_skill_origin_token_still_flagged(self) -> None:
        # The exemption is scoped to skills/domain/ only.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_config(root, "Jane Doe")
            _write(
                root / ".github" / "skills" / "core" / "x" / "SKILL.md",
                "# Skill\n\nUse the FastAPI route helper here.\n",
            )
            findings = origin_lint.scan_origin_tokens(
                root, origin_lint.load_config_denylist(root)
            )
            self.assertTrue(
                any("FastAPI" in token for _p, _ln, token, _line in findings)
            )


if __name__ == "__main__":
    unittest.main()
