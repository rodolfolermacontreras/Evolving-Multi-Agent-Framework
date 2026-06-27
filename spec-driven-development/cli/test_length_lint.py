"""Tests for cli/length_lint.py (SDD-048 / Q-F).

Covers the optional, advisory max-function-length lint over ``cli/**``:
- ``measure_functions`` computes each function's line span from source.
- The five Article X locked functions are exempt from findings.
- ``scan`` reports functions exceeding the threshold and respects ``--max``.
- ``longest_non_locked`` identifies the longest non-exempt function.
- ``main`` is NON-BLOCKING: it always returns 0 (advisory only), even when
  long functions are found, so no gate is gated by the lint.

Stdlib only (LESSON-001 / Article V).
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import length_lint  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _func(name: str, body_lines: int) -> str:
    """Build a function source whose total span is body_lines + 1 (def line)."""
    body = "\n".join(f"    x{i} = {i}" for i in range(body_lines))
    return f"def {name}():\n{body}\n"


class MeasureFunctionsTests(unittest.TestCase):
    def test_measures_span_including_def_line(self) -> None:
        # def line + 3 body lines => span 4
        src = _func("short", 3)
        funcs = length_lint.measure_functions(src, Path("m.py"))
        self.assertEqual(len(funcs), 1)
        self.assertEqual(funcs[0].name, "short")
        self.assertEqual(funcs[0].length, 4)

    def test_measures_async_functions(self) -> None:
        src = "async def a():\n    x = 1\n    y = 2\n"
        funcs = length_lint.measure_functions(src, Path("m.py"))
        self.assertEqual(funcs[0].name, "a")
        self.assertEqual(funcs[0].length, 3)

    def test_syntax_error_returns_empty(self) -> None:
        funcs = length_lint.measure_functions("def broken(:\n", Path("m.py"))
        self.assertEqual(funcs, [])


class LockedExemptTests(unittest.TestCase):
    def test_locked_functions_not_flagged(self) -> None:
        # A long function named like a locked one must be exempt from findings.
        long_locked = _func("render_html", 200)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "spec-driven-development" / "cli" / "mod.py", long_locked)
            findings = length_lint.scan(root, max_lines=50)
        self.assertEqual(findings, [])

    def test_five_locked_names_are_exempt(self) -> None:
        expected = {
            "render_html",
            "load_sprint_table",
            "load_sprint_goal",
            "detect_current_sprint",
            "load_decisions",
        }
        self.assertEqual(set(length_lint.LOCKED_EXEMPT), expected)


class ScanTests(unittest.TestCase):
    def _make_cli(self, files: dict[str, str]) -> Path:
        td = tempfile.mkdtemp()
        root = Path(td)
        cli = root / "spec-driven-development" / "cli"
        for name, text in files.items():
            _write(cli / name, text)
        return root

    def test_flags_function_over_threshold(self) -> None:
        root = self._make_cli({"mod.py": _func("big", 200)})
        findings = length_lint.scan(root, max_lines=50)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].name, "big")
        self.assertGreater(findings[0].length, 50)

    def test_respects_max_override(self) -> None:
        root = self._make_cli({"mod.py": _func("mid", 60)})
        # span ~61; above 50 (flagged) but below 100 (not flagged)
        self.assertEqual(len(length_lint.scan(root, max_lines=50)), 1)
        self.assertEqual(len(length_lint.scan(root, max_lines=100)), 0)

    def test_skips_test_files(self) -> None:
        root = self._make_cli({"test_mod.py": _func("big", 200)})
        findings = length_lint.scan(root, max_lines=50)
        self.assertEqual(findings, [])

    def test_longest_non_locked_ignores_locked(self) -> None:
        root = self._make_cli({
            "mod.py": _func("small", 5) + _func("render_html", 300),
        })
        longest = length_lint.longest_non_locked(root)
        self.assertIsNotNone(longest)
        self.assertEqual(longest.name, "small")


class MainNonBlockingTests(unittest.TestCase):
    def test_main_returns_zero_when_clean(self) -> None:
        td = tempfile.mkdtemp()
        root = Path(td)
        _write(root / "spec-driven-development" / "cli" / "mod.py", _func("ok", 3))
        self.assertEqual(length_lint.main(["--root", str(root), "--max", "50"]), 0)

    def test_main_returns_zero_even_with_findings(self) -> None:
        td = tempfile.mkdtemp()
        root = Path(td)
        _write(root / "spec-driven-development" / "cli" / "mod.py", _func("big", 200))
        # Advisory: long functions present but main MUST NOT block (return 0).
        self.assertEqual(length_lint.main(["--root", str(root), "--max", "50"]), 0)


if __name__ == "__main__":
    unittest.main()
