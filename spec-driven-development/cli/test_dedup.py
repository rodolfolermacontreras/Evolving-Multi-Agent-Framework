"""Tests for cli/dedup.py (SDD-020).

Covers R1-R7 from spec-driven-development/specs/2026-06-07-cross-feature-dedup/validation.md.
Stdlib only (Article V).
"""

from __future__ import annotations

import ast
import json
import sqlite3
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
SDD_ROOT = THIS.parents[1]
SCHEMA = SDD_ROOT / "ledger" / "schema.sql"
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


# --------------------------------------------------------------------------- #
# SDD-020.R6 -- triple-destination log writers (SDD-032 / R3)
# --------------------------------------------------------------------------- #


def _init_ledger_db(tmp: Path) -> Path:
    """Create an empty fleet.db under tmp using the real schema."""
    db = tmp / "fleet.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    return db


def _stub_overlap(
    candidate_source: str = "<cli-candidate>",
    tier: str = "HARD",
    score: float = 1.0,
) -> tuple[str, dict, dict, float]:
    return (
        tier,
        {"title": "Corpus Item", "source": "backlog/BACKLOG.md", "id": "SDD-001"},
        {"title": "Candidate Item", "source": candidate_source, "id": "SDD-001"},
        score,
    )


class TestDedupLogWriters(unittest.TestCase):
    """SDD-020.R6 (SDD-032 R3): triple-destination log writers."""

    def test_ledger_rows_written(self) -> None:
        """One DEDUP-SCAN-RUN row + N DEDUP-OVERLAP-FLAGGED rows inserted."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = _init_ledger_db(Path(tmp))
            overlaps = [_stub_overlap(), _stub_overlap(tier="SOFT", score=0.85)]
            inserted = dedup._write_ledger_rows(
                db,
                {"scope": "all", "candidate_count": 5, "overlap_count": 2, "exit_code": 1},
                overlaps,
            )
            self.assertEqual(inserted, 3)  # 1 scan-run + 2 overlap-flagged
            with sqlite3.connect(db) as conn:
                conn.row_factory = sqlite3.Row
                rows = list(conn.execute(
                    "SELECT task_id, agent_id, agent_role, notes FROM dispatches "
                    "ORDER BY id"
                ))
            self.assertEqual(rows[0]["task_id"], "DEDUP-SCAN-RUN")
            self.assertEqual(rows[0]["agent_id"], "dedup-scanner")
            self.assertEqual(rows[0]["agent_role"], "scanner")
            scan_notes = json.loads(rows[0]["notes"])
            self.assertEqual(scan_notes["scope"], "all")
            self.assertEqual(scan_notes["overlap_count"], 2)
            self.assertEqual(scan_notes["exit"], 1)
            self.assertEqual(rows[1]["task_id"], "DEDUP-OVERLAP-FLAGGED")
            self.assertEqual(rows[2]["task_id"], "DEDUP-OVERLAP-FLAGGED")
            ov_notes = json.loads(rows[1]["notes"])
            self.assertIn("tier", ov_notes)
            self.assertIn("score", ov_notes)
            # Missing DB silently no-ops (returns 0) rather than crashing.
            missing = Path(tmp) / "nonexistent.db"
            self.assertEqual(
                dedup._write_ledger_rows(
                    missing,
                    {"scope": "all", "candidate_count": 0, "overlap_count": 0, "exit_code": 0},
                    [],
                ),
                0,
            )

    def test_per_spec_file_written(self) -> None:
        """dedup-scan.md is written inside the candidate spec dir with valid frontmatter."""
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = Path(tmp) / "spec-1"
            spec_dir.mkdir()
            overlaps = [_stub_overlap(candidate_source=str(spec_dir / "spec.md"))]
            out = dedup._write_per_spec_dedup_scan(spec_dir, overlaps)
            self.assertIsNotNone(out)
            self.assertTrue(out.is_file())
            content = out.read_text(encoding="utf-8")
            self.assertIn("---", content)
            self.assertIn("type: session", content)
            self.assertIn("status: active", content)
            self.assertIn("owner: dedup-scanner", content)
            self.assertIn("# Dedup Scan", content)
            self.assertIn("[HARD]", content)
            self.assertIn("Candidate Item", content)
            # Missing dir -> None (silent no-op for pure-backlog scans)
            self.assertIsNone(
                dedup._write_per_spec_dedup_scan(Path(tmp) / "no-such", overlaps)
            )
            # Empty overlap list -> None (nothing to flag)
            empty_dir = Path(tmp) / "spec-2"
            empty_dir.mkdir()
            self.assertIsNone(dedup._write_per_spec_dedup_scan(empty_dir, []))

    def test_rolling_log_appended(self) -> None:
        """First call creates header + line; second call appends only the line."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "backlog" / "DEDUP-LOG.md"
            summary = {"scope": "all", "candidate_count": 3, "overlap_count": 1, "exit_code": 0}
            dedup._append_rolling_log(log_path, summary)
            self.assertTrue(log_path.is_file())
            first = log_path.read_text(encoding="utf-8")
            self.assertIn("# Dedup Scan Log", first)
            self.assertIn("| timestamp_utc | scope | candidates | overlaps | exit |", first)
            first_lines = first.count("\n")
            # Second call appends one more row, no duplicated header.
            dedup._append_rolling_log(log_path, summary)
            second = log_path.read_text(encoding="utf-8")
            self.assertEqual(second.count("# Dedup Scan Log"), 1)
            self.assertGreater(second.count("\n"), first_lines)

    def test_no_emit_logs_flag(self) -> None:
        """--no-emit-logs suppresses all three writes; scan still exits cleanly."""
        with tempfile.TemporaryDirectory() as tmp:
            sdd = make_sdd(Path(tmp))
            write_backlog(sdd, [("SDD-001", "Widget factory")])
            buf = StringIO()
            with redirect_stdout(buf):
                rc = dedup.main([
                    "scan",
                    "--sdd-root", str(sdd),
                    "--scope", "backlog",
                    "--no-emit-logs",
                ])
            self.assertEqual(rc, 0)
            self.assertFalse((sdd / "backlog" / "DEDUP-LOG.md").is_file())
            self.assertFalse((sdd / "ledger" / "fleet.db").is_file())


# --------------------------------------------------------------------------- #
# SDD-020.R8 -- prompt hooks at /triage + /clarify (SDD-032 / R4)
# --------------------------------------------------------------------------- #


_PROMPTS_DIR = SDD_ROOT.parents[0] / ".github" / "prompts"
_TRIAGE_PROMPT = _PROMPTS_DIR / "triage.prompt.md"
_CLARIFY_PROMPT = _PROMPTS_DIR / "clarify.prompt.md"


class TestPromptHooks(unittest.TestCase):
    """SDD-020.R8 (SDD-032 R4): dedup invocation wired into /triage + /clarify."""

    def test_triage_invokes_dedup(self) -> None:
        """triage.prompt.md contains the literal dedup-scan invocation."""
        self.assertTrue(_TRIAGE_PROMPT.is_file(),
                        f"prompt file missing: {_TRIAGE_PROMPT}")
        content = _TRIAGE_PROMPT.read_text(encoding="utf-8").lower()
        self.assertIn("cli/dedup.py scan", content)

    def test_clarify_invokes_dedup(self) -> None:
        """clarify.prompt.md contains the literal dedup-scan invocation."""
        self.assertTrue(_CLARIFY_PROMPT.is_file(),
                        f"prompt file missing: {_CLARIFY_PROMPT}")
        content = _CLARIFY_PROMPT.read_text(encoding="utf-8").lower()
        self.assertIn("cli/dedup.py scan", content)

    def test_tier_action_guidance_present(self) -> None:
        """Both prompts document HARD / SOFT / ADVISORY tier-action responses."""
        for prompt in (_TRIAGE_PROMPT, _CLARIFY_PROMPT):
            content = prompt.read_text(encoding="utf-8").lower()
            for tier in ("hard", "soft", "advisory"):
                self.assertIn(tier, content,
                              f"tier keyword '{tier}' missing from {prompt.name}")


if __name__ == "__main__":
    unittest.main()
