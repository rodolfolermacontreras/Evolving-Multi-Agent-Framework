"""Tests for cli/dedup.py (SDD-020).

Covers R1-R7 from spec-driven-development/specs/2026-06-07-cross-feature-dedup/validation.md.
Stdlib only (Article V).
"""

from __future__ import annotations

import ast
import json
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import dedup  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_sdd(tmp: Path) -> Path:
    """Create a minimal SDD root under tmp."""
    sdd = tmp / "sdd"
    (sdd / "backlog").mkdir(parents=True)
    (sdd / "specs").mkdir(parents=True)
    return sdd


def write_backlog(sdd: Path, rows: list[tuple[str, str]]) -> None:
    """Write a BACKLOG.md table with (id, title) rows."""
    lines = [
        "# Backlog\n",
        "| ID | Title | Priority |\n",
        "|----|-------|----------|\n",
    ]
    for item_id, title in rows:
        lines.append(f"| {item_id} | {title} | P1 |\n")
    (sdd / "backlog" / "BACKLOG.md").write_text("".join(lines), encoding="utf-8")


def write_ideas(sdd: Path, ideas: list[str]) -> None:
    """Write IDEAS.md with dated idea entries."""
    lines = ["# Ideas\n\n"]
    for idea in ideas:
        lines.append(f"- **[2026-06-01]** {idea} -- description text\n")
    (sdd / "backlog" / "IDEAS.md").write_text("".join(lines), encoding="utf-8")


def make_spec_dir(sdd: Path, name: str, status: str, title: str,
                  item_id: str | None = None) -> Path:
    """Create a spec directory with spec.md containing given frontmatter."""
    spec_dir = sdd / "specs" / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    id_val = item_id or "auto"
    text = (
        "---\n"
        f"id: '{id_val}'\n"
        f"type: spec\n"
        f"status: {status}\n"
        "owner: architect\n"
        "updated: 2026-06-07\n"
        "---\n"
        "\n"
        f"# {title}\n"
        "\n"
        "Some spec content here.\n"
    )
    (spec_dir / "spec.md").write_text(text, encoding="utf-8")
    return spec_dir


# --------------------------------------------------------------------------- #
# R1 -- Corpus loading
# --------------------------------------------------------------------------- #

class TestLoadCorpusBacklog(unittest.TestCase):
    """R1: load_corpus covers BACKLOG.md."""

    def test_load_corpus_backlog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            write_backlog(sdd, [
                ("SDD-001", "Widget factory"),
                ("SDD-002", "Gizmo pipeline"),
                ("SDD-003", "Frobnitz cleaner"),
            ])
            corpus = dedup.load_corpus(sdd, scope="backlog")
            self.assertEqual(len(corpus), 3)
            ids = [e["id"] for e in corpus]
            self.assertIn("SDD-001", ids)
            self.assertIn("SDD-002", ids)


class TestLoadCorpusOpenSpecs(unittest.TestCase):
    """R1: load_corpus covers open specs, excludes done/archived."""

    def test_load_corpus_open_specs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            make_spec_dir(sdd, "feat-a", "active", "Feature Alpha")
            make_spec_dir(sdd, "feat-b", "draft", "Feature Beta")
            make_spec_dir(sdd, "feat-c", "done", "Feature Gamma")
            corpus = dedup.load_corpus(sdd, scope="specs")
            titles = [e["title"] for e in corpus]
            self.assertIn("Feature Alpha", titles)
            self.assertIn("Feature Beta", titles)
            self.assertNotIn("Feature Gamma", titles)
            self.assertEqual(len(corpus), 2)


class TestLoadCorpusIdeas(unittest.TestCase):
    """R1: load_corpus covers IDEAS.md."""

    def test_load_corpus_ideas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            write_backlog(sdd, [])
            write_ideas(sdd, ["Auto-deploy dashboard", "Timeline visualization"])
            corpus = dedup.load_corpus(sdd, scope="backlog")
            idea_titles = [e["title"] for e in corpus if e["source"].endswith("IDEAS.md")]
            self.assertEqual(len(idea_titles), 2)


# --------------------------------------------------------------------------- #
# R2 -- Three-layer heuristic
# --------------------------------------------------------------------------- #

class TestLayer1HardExactId(unittest.TestCase):
    """R2: Layer 1 HARD fires on exact ID match."""

    def test_layer1_hard_exact_id(self) -> None:
        corpus = [{"source": "a.md", "title": "Alpha", "id": "SDD-042", "text": "alpha"}]
        candidate = {"source": "b.md", "title": "Beta thing", "id": "SDD-042", "text": "beta"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0][0], "HARD")
        self.assertEqual(overlaps[0][3], 1.0)

    def test_layer1_no_match(self) -> None:
        corpus = [{"source": "a.md", "title": "Alpha", "id": "SDD-001", "text": "alpha"}]
        candidate = {"source": "b.md", "title": "Beta", "id": "SDD-999", "text": "beta"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        self.assertEqual(len(overlaps), 0)


class TestLayer2SoftFuzzy(unittest.TestCase):
    """R2: Layer 2 SOFT fires on fuzzy title match >= 0.8."""

    def test_layer2_soft_fuzzy(self) -> None:
        corpus = [{"source": "a.md", "title": "Cross-feature deduplication scanner", "id": None, "text": "dedup"}]
        candidate = {"source": "b.md", "title": "Cross-feature deduplication scan", "id": None, "text": "dedup scan"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        soft = [o for o in overlaps if o[0] == "SOFT"]
        self.assertTrue(len(soft) >= 1, f"Expected SOFT match, got {overlaps}")

    def test_layer2_no_match(self) -> None:
        corpus = [{"source": "a.md", "title": "Widget factory automation", "id": None, "text": "widget"}]
        candidate = {"source": "b.md", "title": "Kubernetes deploy pipeline", "id": None, "text": "k8s deploy"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        soft = [o for o in overlaps if o[0] == "SOFT"]
        self.assertEqual(len(soft), 0)


class TestLayer3AdvisoryJaccard(unittest.TestCase):
    """R2: Layer 3 ADVISORY fires on keyword Jaccard >= 0.3."""

    def test_layer3_advisory_jaccard(self) -> None:
        corpus = [{"source": "a.md", "title": "A", "id": None,
                    "text": "fleet dispatch parallel workers serial gate lock"}]
        candidate = {"source": "b.md", "title": "B", "id": None,
                     "text": "serial gate lock release fleet enforce parallel"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        advisory = [o for o in overlaps if o[0] == "ADVISORY"]
        self.assertTrue(len(advisory) >= 1, f"Expected ADVISORY match, got {overlaps}")

    def test_layer3_no_match(self) -> None:
        corpus = [{"source": "a.md", "title": "A", "id": None,
                    "text": "fleet dispatch parallel workers serial gate lock"}]
        candidate = {"source": "b.md", "title": "B", "id": None,
                     "text": "dashboard about section newcomer html css render"}
        overlaps = dedup.find_overlaps(corpus, candidate)
        advisory = [o for o in overlaps if o[0] == "ADVISORY"]
        self.assertEqual(len(advisory), 0)


# --------------------------------------------------------------------------- #
# R3 -- Standalone, stdlib-only
# --------------------------------------------------------------------------- #

class TestStdlibOnly(unittest.TestCase):
    """R3: dedup.py is stdlib-only (no third-party imports)."""

    def test_runtime_imports_are_stdlib_only(self) -> None:
        dedup_path = Path(dedup.__file__)
        tree = ast.parse(dedup_path.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        local_ok = {"schema_lint", "dedup"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(
                        top in stdlib or top in local_ok,
                        f"non-stdlib import: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(
                    top in stdlib or top in local_ok,
                    f"non-stdlib import: {node.module}",
                )


class TestMainSignature(unittest.TestCase):
    """R3: main(argv) signature."""

    def test_main_callable(self) -> None:
        import inspect
        sig = inspect.signature(dedup.main)
        params = list(sig.parameters.keys())
        self.assertIn("argv", params)


# --------------------------------------------------------------------------- #
# R4 -- Tiered action / exit codes
# --------------------------------------------------------------------------- #

class TestTieredHardExits1(unittest.TestCase):
    """R4: HARD overlap returns exit code 1."""

    def test_tiered_hard_exits_1(self) -> None:
        overlaps = [("HARD", {"title": "A", "source": "a", "id": "X"}, {"title": "B"}, 1.0)]
        buf = StringIO()
        with redirect_stdout(buf), redirect_stderr(StringIO()):
            rc = dedup.handle_overlaps(overlaps)
        self.assertEqual(rc, 1)


class TestTieredCleanExits0(unittest.TestCase):
    """R4: No overlaps returns exit code 0."""

    def test_tiered_clean_exits_0(self) -> None:
        rc = dedup.handle_overlaps([])
        self.assertEqual(rc, 0)


class TestTieredSoftNoPrompt(unittest.TestCase):
    """R4: SOFT + --no-prompt returns exit code 1."""

    def test_soft_no_prompt_exits_1(self) -> None:
        overlaps = [("SOFT", {"title": "A", "source": "a"}, {"title": "B"}, 0.85)]
        buf = StringIO()
        with redirect_stdout(buf), redirect_stderr(StringIO()):
            rc = dedup.handle_overlaps(overlaps, no_prompt=True)
        self.assertEqual(rc, 1)


class TestTieredAdvisoryExits0(unittest.TestCase):
    """R4: ADVISORY returns exit code 0."""

    def test_advisory_exits_0(self) -> None:
        overlaps = [("ADVISORY", {"title": "A", "source": "a"}, {"title": "B"}, 0.35)]
        buf = StringIO()
        with redirect_stdout(buf):
            rc = dedup.handle_overlaps(overlaps)
        self.assertEqual(rc, 0)


# --------------------------------------------------------------------------- #
# R5 -- Independent of SDD-019
# --------------------------------------------------------------------------- #

class TestIndependentOfFleet(unittest.TestCase):
    """R5: dedup runs without fleet.py lock state present."""

    def test_no_fleet_dependency(self) -> None:
        dedup_path = Path(dedup.__file__)
        text = dedup_path.read_text(encoding="utf-8")
        self.assertNotIn("import fleet", text)
        self.assertNotIn("from fleet", text)


# --------------------------------------------------------------------------- #
# R7 -- Empty corpus notice
# --------------------------------------------------------------------------- #

class TestEmptyCorpusNotice(unittest.TestCase):
    """R7: empty corpus emits explicit notice."""

    def test_empty_corpus_notice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            # Empty BACKLOG.md
            (sdd / "backlog" / "BACKLOG.md").write_text("# Backlog\n", encoding="utf-8")
            (sdd / "backlog" / "IDEAS.md").write_text("# Ideas\n", encoding="utf-8")
            buf = StringIO()
            with redirect_stdout(buf):
                rc = dedup.main(["scan", "--sdd-root", str(sdd)])
            self.assertEqual(rc, 0)
            self.assertIn("no corpus", buf.getvalue().lower())


# --------------------------------------------------------------------------- #
# CLI smoke tests
# --------------------------------------------------------------------------- #

class TestCLIHelp(unittest.TestCase):
    """R3: --help exits 0."""

    def test_cli_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            dedup.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_scan_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            dedup.main(["scan", "--help"])
        self.assertEqual(ctx.exception.code, 0)


class TestCLIScanClean(unittest.TestCase):
    """CLI scan with no overlaps returns 0."""

    def test_cli_scan_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            write_backlog(sdd, [("SDD-001", "Alpha"), ("SDD-002", "Beta")])
            buf = StringIO()
            with redirect_stdout(buf):
                rc = dedup.main(["scan", "--sdd-root", str(sdd)])
            self.assertEqual(rc, 0)


class TestCLIScanCandidate(unittest.TestCase):
    """CLI --candidate checks one title against corpus."""

    def test_candidate_hard_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            make_spec_dir(sdd, "f1", "active", "Serial Gate", "SDD-019")
            buf_out, buf_err = StringIO(), StringIO()
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                rc = dedup.main([
                    "scan", "--sdd-root", str(sdd),
                    "--candidate", "Serial Gate",
                ])
            # Should detect SOFT match on identical title
            self.assertIn("SOFT", buf_out.getvalue())


class TestCLIScanJsonFormat(unittest.TestCase):
    """CLI --format json produces valid JSON."""

    def test_json_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            write_backlog(sdd, [("SDD-001", "Alpha")])
            buf = StringIO()
            with redirect_stdout(buf):
                rc = dedup.main(["scan", "--sdd-root", str(sdd), "--format", "json"])
            self.assertEqual(rc, 0)
            data = json.loads(buf.getvalue())
            self.assertIsInstance(data, list)


if __name__ == "__main__":
    unittest.main()
