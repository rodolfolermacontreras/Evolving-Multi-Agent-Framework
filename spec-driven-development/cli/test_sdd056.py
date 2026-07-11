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
        "276c21e7d9bc61e9b815732a34b8c36f8708ed6fca39ed824c392de295e699c8",
        "66376e4e033859709fc9d482476c82b617b8659c8cf17a7f2056956da0ea90ad",
    ),
    (
        SPRINT_06,
        "Do NOT start Sprint 7 in this session. It runs in its own fresh session",
        "Do NOT start Sprint 7 in this context-isolated unit. Start it in a fresh session or through an EM-routed subagent dispatch",
        "4be177aa730ce1a685119b93cd696fe6690560fc764894eca87975c92b5820c1",
        "168e9e1b86940dabec0f496b888c54cc50675533e4633abdcb425cb41ea6e899",
    ),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_checkout_newlines(data: bytes) -> bytes:
    """Use repository-content newlines for platform-neutral scope hashes."""
    return data.replace(b"\r\n", b"\n")


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
                current = _normalize_checkout_newlines(path.read_bytes())
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
