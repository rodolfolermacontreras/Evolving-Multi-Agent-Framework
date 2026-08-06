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

    def test_current_pi_claim_is_flagged_when_no_pi_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _seed_root(tmp, current_pi=8)
            marker = (
                root / "spec-driven-development" / "sprints" /
                "PI-8" / "CURRENT_PI.md"
            )
            marker.write_text(
                "---\nstatus: done\nsprint: PI-8\n---\n\n# PI-8\n",
                encoding="utf-8",
            )
            _write(_doc(root, 2), "### Current PI: PI-8 (closed)\n")

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(
                f.kind == "pi" and "no active PI" in f.detail
                for f in findings
            ))


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


class TestLeadershipZeroActiveTruth(unittest.TestCase):
    def _leadership(self, root: Path) -> Path:
        return (
            root / "spec-driven-development" / "docs" /
            "LEADERSHIP-ONE-PAGER.html"
        )

    def _zero_active_root(self, tmp: str) -> Path:
        root = _seed_root(tmp, current_pi=9)
        marker = (
            root / "spec-driven-development" / "sprints" /
            "PI-9" / "CURRENT_PI.md"
        )
        marker.write_text("---\nstatus: done\n---\n", encoding="utf-8")
        return root

    def test_false_active_pi_claim_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "<p>PI-10 is active.</p>\n")

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_now_building_claim_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "<h2>Now building</h2>\n")

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-work" for f in findings))

    def test_active_sdd_068_claim_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "<p>Active feature: SDD-068</p>\n")

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-unauthorized-id" for f in findings))

    def test_each_unauthorized_product_label_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "\n".join(f"<li>SDD-{number:03d} planned</li>" for number in range(60, 68)),
            )

            findings = staledoc_lint.scan(root)

            labels = {f"SDD-{number:03d}" for number in range(60, 68)}
            found = {label for finding in findings for label in labels if label in finding.line}
            self.assertEqual(found, labels)

    def test_dated_capability_brief_without_product_labels_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p>Evidence date: 2026-08-06.</p>\n"
                "<p>No active PI, sprint, feature, or scheduled work.</p>\n"
                "<p>Concept themes confer no backlog, PI, sprint, or implementation authority.</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertEqual(findings, [])

    def test_historical_pi_then_no_active_pi_on_same_line_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<footer>PI-9 closed July 30; no active PI</footer>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertEqual(findings, [])

    def test_same_clause_active_negations_are_clean(self) -> None:
        negations = (
            "PI-10 is not active.",
            "PI-10 is no longer active.",
            "PI-10 isn't active.",
            "PI-10 wasn't active.",
            "PI-10 was never active.",
            "PI-10 is inactive.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "\n".join(f"<p>{claim}</p>" for claim in negations),
            )

            findings = staledoc_lint.scan(root)

            self.assertFalse(any(f.kind == "leadership-active-pi" for f in findings))

    def test_mixed_clause_later_positive_active_claim_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p>PI-9 is no longer active; however, PI-10 is active.</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_candidate_clause_does_not_hide_later_positive_active_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p>PI-10 is only a candidate, but PI-11 is active.</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_marked_up_positive_active_claim_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p><strong>PI-10</strong> is <em>active</em></p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_marked_up_same_clause_negation_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p><strong>PI-10</strong> is <em>not</em> active</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertFalse(any(f.kind == "leadership-active-pi" for f in findings))

    def test_adjacent_blocks_without_punctuation_do_not_share_negation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p>PI-9 is not active</p><p>PI-10 is active</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_later_marked_positive_is_not_suppressed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<p><strong>PI-9</strong> is not active; "
                "<strong>PI-10</strong> is active</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-active-pi" for f in findings))

    def test_candidate_local_negation_keeps_later_positive(self) -> None:
        claims = (
            "PI-9 is not active but PI-10 is active",
            "PI-9 inactive; active PI PI-10",
            "<strong>PI-9</strong> is <em>not active</em> but "
            "<strong>PI-10</strong> is <em>active</em>",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            for claim in claims:
                with self.subTest(claim=claim):
                    _write(self._leadership(root), f"<p>{claim}</p>\n")

                    findings = staledoc_lint.scan(root)

                    self.assertTrue(any(
                        f.kind == "leadership-active-pi" for f in findings
                    ))

    def test_candidate_local_negation_keeps_earlier_positive(self) -> None:
        claims = (
            "PI-9 is active but PI-10 is not active",
            "active PI PI-9; PI-10 inactive",
            "<strong>PI-9</strong> is <em>active</em> but "
            "<strong>PI-10</strong> is <em>not active</em>",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            for claim in claims:
                with self.subTest(claim=claim):
                    _write(self._leadership(root), f"<p>{claim}</p>\n")

                    findings = staledoc_lint.scan(root)

                    self.assertTrue(any(
                        f.kind == "leadership-active-pi" for f in findings
                    ))

    def test_candidate_local_negation_all_negated_is_clean(self) -> None:
        claims = (
            "PI-9 is not active and PI-10 is not active",
            "PI-9 inactive; inactive PI PI-10",
            "<strong>PI-9</strong> is <em>not active</em> and "
            "<strong>PI-10</strong> is <em>not active</em>",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            for claim in claims:
                with self.subTest(claim=claim):
                    _write(self._leadership(root), f"<p>{claim}</p>\n")

                    findings = staledoc_lint.scan(root)

                    self.assertFalse(any(
                        f.kind == "leadership-active-pi" for f in findings
                    ))

    def test_script_style_comments_and_attributes_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(
                self._leadership(root),
                "<!-- PI-10 is active -->"
                "<script>PI-11 is active</script>"
                "<style>.x::after { content: 'PI-12 is active'; }</style>"
                "<p data-state='PI-13 is active'>No active PI.</p>\n",
            )

            findings = staledoc_lint.scan(root)

            self.assertFalse(any(f.kind == "leadership-active-pi" for f in findings))

    def test_leadership_html_input_overflow_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "<p>No active PI.</p>" + " " * 65536)

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-html-overflow" for f in findings))

    def test_leadership_visible_text_overflow_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "<p>" + "x" * 16385 + "</p>")

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-html-overflow" for f in findings))

    def test_leadership_clause_overflow_is_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._zero_active_root(tmp)
            _write(self._leadership(root), "".join("<p>clean</p>" for _ in range(513)))

            findings = staledoc_lint.scan(root)

            self.assertTrue(any(f.kind == "leadership-html-overflow" for f in findings))

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
            "__future__", "argparse", "dataclasses", "html", "pathlib", "re", "sys",
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
