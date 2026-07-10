"""Exact-scope regression guard for SDD-056 historical wording."""

from __future__ import annotations

import ast
import hashlib
import sys
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = CLI_DIR.parents[1]

SPRINT_05 = FRAMEWORK_ROOT / "spec-driven-development" / "feature-prompts" / "SPRINT-05-KICKOFF.prompt.md"
SPRINT_06 = FRAMEWORK_ROOT / "spec-driven-development" / "feature-prompts" / "SPRINT-06-KICKOFF.prompt.md"

REPLACEMENTS = (
    (
        SPRINT_05,
        "Each F-## runs in its own fresh session.",
        "Each F-## runs in its own context-isolated unit: a fresh session or an EM-routed subagent dispatch.",
        "028607f95aeb8161bf5a4dc56ef336c9bcbd4a7f75331071a6b0c4297e2f2723",
        "9d6b782e08615f9301d485d11950e00eb85c7291e55d37452ba28c470a436c14",
    ),
    (
        SPRINT_06,
        "Do NOT start Sprint 7 in this session. It runs in its own fresh session",
        "Do NOT start Sprint 7 in this context-isolated unit. Start it in a fresh session or through an EM-routed subagent dispatch",
        "e7f1654f5f6216a1ddd5f5daac975bf3eb159a2330df4aed5547bc6468a69a26",
        "8525319e6f521cf17aa6bb7fac0bf45b05e94a6a7a49281067faf566ae13dd97",
    ),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestExactScopeWordingGuard(unittest.TestCase):
    """V56-3: only the two approved byte substitutions are permitted."""

    def test_old_phrases_absent_and_replacements_present(self) -> None:
        for path, old, new, _before_hash, _after_hash in REPLACEMENTS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(old, text)
                self.assertEqual(text.count(new), 1)

    def test_all_other_bytes_unchanged(self) -> None:
        for path, old, new, before_hash, after_hash in REPLACEMENTS:
            with self.subTest(path=path.name):
                current = path.read_bytes()
                old_bytes = old.encode("utf-8")
                new_bytes = new.encode("utf-8")
                self.assertEqual(_sha256(current), after_hash)
                self.assertEqual(current.count(new_bytes), 1)
                reconstructed = current.replace(new_bytes, old_bytes, 1)
                self.assertEqual(_sha256(reconstructed), before_hash)


class TestStdlibOnly(unittest.TestCase):
    """The guard imports only Python standard-library modules."""

    def test_this_module_is_stdlib_only(self) -> None:
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = (node.module,)
            else:
                continue
            for module in modules:
                top_level = module.split(".", 1)[0]
                self.assertIn(top_level, sys.stdlib_module_names)


if __name__ == "__main__":
    unittest.main()
