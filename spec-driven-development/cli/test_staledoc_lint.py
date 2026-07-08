"""Tests for cli/staledoc_lint.py -- the SDD-051B stale-doc guard.

Guard-first TDD (written before staledoc_lint.py). Covers:
- article count verified against principles.md (verify-against-source, R-B2)
- current PI verified against the active CURRENT_PI.md (R-B3)
- the roman article-range citation form
- the <!-- staledoc-ok --> marker exemption (R-B4)
- scope limited to the session-start docs (R-B4)
- main(argv) exit codes (R-B1/R-B6)
- stdlib-only imports (Article V)

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

import staledoc_lint  # noqa: E402

_ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
           "XI", "XII", "XIII", "XIV"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_root(tmp: str, *, articles: int = 12, current_pi: int = 8) -> Path:
    """Build a minimal framework-shaped root the guard can read."""
    root = Path(tmp)
    body = "\n".join(f"## Article {_ROMANS[i]}: Placeholder" for i in range(articles))
    _write(
        root / "spec-driven-development" / "constitution" / "principles.md",
        "---\ntitle: principles\n---\n\n" + body + "\n",
    )
    _write(
        root / "spec-driven-development" / "sprints" / f"PI-{current_pi}" / "CURRENT_PI.md",
        f"---\nstatus: active\nsprint: PI-{current_pi}\n---\n\n# PI-{current_pi}\n",
    )
    return root


def _doc(root: Path, index: int = 0) -> Path:
    """Absolute path to a chosen session-start doc under root."""
    return root / staledoc_lint.SESSION_START_DOCS[index]


class TestArticleCount(unittest.TestCase):
    def test_stale_article_count_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "The 10 binding articles govern the framework.\n")
            findings = staledoc_lint.scan(root)
            self.assertTrue(any(f.kind == "article" for f in findings))

    def test_correct_article_count_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "The 12 binding articles govern the framework.\n")
            findings = staledoc_lint.scan(root)
            self.assertEqual([f for f in findings if f.kind == "article"], [])

    def test_roman_range_mismatch_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "Constitution articles: the set (I-X).\n")
            findings = staledoc_lint.scan(root)
            self.assertTrue(any(f.kind == "article" for f in findings))

    def test_roman_range_match_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "Constitution articles: the set (I-XII).\n")
            findings = staledoc_lint.scan(root)
            self.assertEqual([f for f in findings if f.kind == "article"], [])

    def test_marker_exempts_stale_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(
                _doc(root),
                "History: PI-1 shipped 10 binding articles. <!-- staledoc-ok -->\n",
            )
            findings = staledoc_lint.scan(root)
            self.assertEqual(findings, [])


class TestCurrentPi(unittest.TestCase):
    def test_stale_current_pi_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, current_pi=8)
            _write(_doc(root, 2), "| **Current PI** | PI-3 (Portability) |\n")
            findings = staledoc_lint.scan(root)
            self.assertTrue(any(f.kind == "pi" for f in findings))

    def test_correct_current_pi_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, current_pi=8)
            _write(_doc(root, 2), "### Current PI: PI-8 (Truth in the Window)\n")
            findings = staledoc_lint.scan(root)
            self.assertEqual([f for f in findings if f.kind == "pi"], [])

    def test_marked_stale_current_pi_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, current_pi=8)
            _write(
                _doc(root, 2),
                "Historic note: Current PI: PI-3 back then. <!-- staledoc-ok -->\n",
            )
            findings = staledoc_lint.scan(root)
            self.assertEqual(findings, [])


class TestScope(unittest.TestCase):
    def test_non_session_start_doc_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(
                root / "spec-driven-development" / "docs" / "SOME_OTHER.md",
                "The 10 binding articles.\n",
            )
            findings = staledoc_lint.scan(root)
            self.assertEqual(findings, [])

    def test_missing_docs_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp)
            # No session-start docs written at all.
            self.assertEqual(staledoc_lint.scan(root), [])


class TestMain(unittest.TestCase):
    def test_main_nonzero_on_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "The 10 binding articles.\n")
            self.assertEqual(staledoc_lint.main(["--root", str(root)]), 1)

    def test_main_zero_on_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, articles=12)
            _write(_doc(root), "The 12 binding articles.\n")
            self.assertEqual(staledoc_lint.main(["--root", str(root)]), 0)


class TestStdlibOnly(unittest.TestCase):
    def test_imports_are_stdlib_or_sibling(self) -> None:
        import ast

        allowed = {
            "__future__", "argparse", "dataclasses", "pathlib", "re", "sys",
            "governance_check",  # in-tree sibling (ADR-012), not third-party
        }
        src = (CLI_DIR / "staledoc_lint.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name.split(".")[0], allowed)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertIn(node.module.split(".")[0], allowed)


if __name__ == "__main__":
    unittest.main()
