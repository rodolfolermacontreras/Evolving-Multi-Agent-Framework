#!/usr/bin/env python3
"""
Tests for SDD-053 (decision-request format for human-facing agents).

Covers:
- R-1  The em-communication-discipline skill carries the DECISION-REQUEST FORMAT
       section with all required tokens/rules (case-insensitive).
- R-2  Both EM charters bind to the skill as single source of truth: each names
       em-communication-discipline AND the phrase "decision-request format", and
       neither restates the full block (no duplicated fenced block).
- R-3  Stdlib-only audit of this new test module (no third-party imports),
       mirroring test_sdd045.py's stdlib audit.
"""

from pathlib import Path
import ast
import sys
import unittest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

import bootstrap  # noqa: E402

FRAMEWORK_ROOT = bootstrap.framework_root()

SKILL_PATH = (
    FRAMEWORK_ROOT
    / ".github"
    / "skills"
    / "operational"
    / "em-communication-discipline"
    / "SKILL.md"
)
SPRINT_EM_PATH = (
    FRAMEWORK_ROOT / ".github" / "agents" / "sprint-executive-manager.agent.md"
)
PROJECT_EM_PATH = (
    FRAMEWORK_ROOT / ".github" / "agents" / "principal-executive-manager.agent.md"
)


def _read_lower(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


class TestSkillCarriesFormat(unittest.TestCase):
    """R-1: the skill contains every required format token/rule."""

    REQUIRED_TOKENS = (
        "decision-request format",
        "decision needed:",
        "options:",
        "impact:",
        "recommendation:",
        "one decision block per message",
        "at the very end",
        "no decision",
    )

    def setUp(self) -> None:
        self.assertTrue(SKILL_PATH.is_file(), f"missing skill: {SKILL_PATH}")
        self.text = _read_lower(SKILL_PATH)

    def test_all_required_tokens_present(self) -> None:
        for token in self.REQUIRED_TOKENS:
            self.assertIn(
                token,
                self.text,
                f"skill is missing required token/rule: {token!r}",
            )

    def test_recommendation_stays_mandatory_container(self) -> None:
        # U-1: the format is the container for the recommendation, not a menu.
        self.assertIn("recommend, do not menu", self.text)
        self.assertIn("recommendation:", self.text)


class TestChartersBindToSkill(unittest.TestCase):
    """R-2: both charters name the skill + the decision-request format (SSOT)."""

    def _assert_binds(self, path: Path) -> None:
        self.assertTrue(path.is_file(), f"missing charter: {path}")
        text = _read_lower(path)
        self.assertIn(
            "em-communication-discipline",
            text,
            f"{path.name} does not name em-communication-discipline",
        )
        self.assertIn(
            "decision-request format",
            text,
            f"{path.name} does not reference the decision-request format",
        )

    def test_sprint_em_binds(self) -> None:
        self._assert_binds(SPRINT_EM_PATH)

    def test_project_em_binds(self) -> None:
        self._assert_binds(PROJECT_EM_PATH)

    def test_charters_do_not_restate_full_block(self) -> None:
        # M-2: no duplication drift. The full block lives ONLY in the skill.
        # A charter that restated it would carry the "DECISION NEEDED:" line.
        for path in (SPRINT_EM_PATH, PROJECT_EM_PATH):
            text = _read_lower(path)
            self.assertNotIn(
                "decision needed:",
                text,
                f"{path.name} appears to restate the full format block",
            )


class TestStdlibOnly(unittest.TestCase):
    """R-3: this test module imports stdlib + sibling modules only."""

    LOCAL_OK = {"bootstrap"}

    def _assert_stdlib_only(self, path: Path, module_name: str) -> None:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(
                        top in stdlib or top in self.LOCAL_OK,
                        f"non-stdlib import in {module_name}: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(
                    top in stdlib or top in self.LOCAL_OK,
                    f"non-stdlib import in {module_name}: {node.module}",
                )

    def test_this_module_stdlib_only(self) -> None:
        self._assert_stdlib_only(Path(__file__).resolve(), "test_sdd053")


if __name__ == "__main__":
    unittest.main()
