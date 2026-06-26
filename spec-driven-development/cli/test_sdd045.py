#!/usr/bin/env python3
"""
Tests for SDD-045 (detach + clone-and-run hardening).

Covers:
- R-3  initialize_ledger creates a fresh ledger from schema.sql (tables present,
       zero dispatch rows) and is idempotent.
- R-4  find_tracked_dbs detects a git-tracked database file (tracked-db guard).
- R-5  run_setup succeeds (happy path) and is idempotent (R-6).
- R-8  run_doctor is green on the real framework checkout and red on a tree with
       a planted origin-token leak.
- R-10 origin_lint fails on a denylisted token in a portable file.
- R-11 origin_lint exempts tokens inside an <!-- example: ... --> block.
- R-13 governance_check fails when the article count drifts from RULES.md.
- Stdlib-only audit for the three new/edited modules.
"""

from pathlib import Path
import ast
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

import bootstrap  # noqa: E402
import origin_lint  # noqa: E402
import governance_check  # noqa: E402

FRAMEWORK_ROOT = bootstrap.framework_root()


def _make_target(root: Path) -> Path:
    """Create the spec-driven-development/ledger directory tree under root."""
    (root / "spec-driven-development" / "ledger").mkdir(parents=True, exist_ok=True)
    return root


class TestInitializeLedger(unittest.TestCase):
    """R-3: fresh ledger from schema.sql with the right tables and no rows."""

    def test_fresh_ledger_has_tables_and_zero_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            bootstrap.initialize_ledger(target)
            ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
            self.assertTrue(ledger.is_file())
            connection = sqlite3.connect(str(ledger))
            try:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                self.assertIn("dispatches", tables)
                self.assertIn("decisions", tables)
                count = connection.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
                self.assertEqual(count, 0)
            finally:
                connection.close()

    def test_idempotent_leaves_existing_nonempty_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            bootstrap.initialize_ledger(target)
            ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
            connection = sqlite3.connect(str(ledger))
            try:
                connection.execute(
                    "INSERT INTO dispatches (dispatched_at, pi, task_id, task_title, "
                    "agent_id, agent_role) VALUES ('2026-06-26T00:00:00Z', 'PI-7', "
                    "'T-1', 'seed', 'a1', 'dev')"
                )
                connection.commit()
            finally:
                connection.close()
            bootstrap.initialize_ledger(target)  # second call: must not wipe
            connection = sqlite3.connect(str(ledger))
            try:
                count = connection.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
                self.assertEqual(count, 1)
            finally:
                connection.close()


class TestTrackedDbGuard(unittest.TestCase):
    """R-4: find_tracked_dbs detects a git-tracked database file."""

    def test_detects_tracked_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            ledger_dir = root / "spec-driven-development" / "ledger"
            ledger_dir.mkdir(parents=True)
            db_path = ledger_dir / "fleet.db"
            db_path.write_bytes(b"SQLite format 3\x00")
            subprocess.run(["git", "-C", str(root), "add", str(db_path)], check=True)
            tracked = origin_lint.find_tracked_dbs(root)
            self.assertTrue(any(name.endswith("fleet.db") for name in tracked))

    def test_no_findings_when_not_a_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(origin_lint.find_tracked_dbs(Path(tmp)), [])


class TestOriginLint(unittest.TestCase):
    """R-10 / R-11: denylisted tokens fail; example blocks are exempt."""

    def _write(self, root: Path, body: str) -> None:
        gh = root / ".github"
        gh.mkdir(parents=True, exist_ok=True)
        (gh / "doc.md").write_text(body, encoding="utf-8")

    def test_planted_token_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Saved under C:\\Users\\someone\\notes.md.\n")
            findings = origin_lint.scan_origin_tokens(root, list(origin_lint.DEFAULT_DENYLIST))
            self.assertTrue(findings)

    def test_custom_denylist_token_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "Written by Some Person.\n")
            findings = origin_lint.scan_origin_tokens(root, ["Some Person"])
            self.assertTrue(findings)

    def test_recommended_denylist_flags_engine_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "See engine.py for the runtime entry point.\n")
            findings = origin_lint.scan_origin_tokens(
                root, list(origin_lint.RECOMMENDED_DENYLIST)
            )
            self.assertTrue(findings)

    def test_example_block_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "<!-- example: C:\\Users\\someone is illustrative -->\n")
            findings = origin_lint.scan_origin_tokens(root, list(origin_lint.DEFAULT_DENYLIST))
            self.assertEqual(findings, [])

    def test_default_denylist_clean_on_framework(self) -> None:
        findings = origin_lint.scan_origin_tokens(
            FRAMEWORK_ROOT, list(origin_lint.DEFAULT_DENYLIST)
        )
        self.assertEqual(findings, [], f"unexpected origin tokens: {findings}")


class TestGovernanceCheck(unittest.TestCase):
    """R-13: article-count drift from RULES.md is detected."""

    def test_count_articles(self) -> None:
        text = "## Article I: A\n## Article II: B\n## Article III: C\n"
        self.assertEqual(governance_check.count_articles(text), 3)

    def test_rules_upper_bound(self) -> None:
        self.assertEqual(governance_check.rules_upper_bound("cites Articles I-XII here"), 12)
        self.assertEqual(governance_check.rules_upper_bound("an Article (I-X) ref"), 10)

    def test_real_repo_is_coherent(self) -> None:
        ok, findings = governance_check.check_governance(FRAMEWORK_ROOT)
        self.assertTrue(ok, f"governance findings: {findings}")

    def test_drift_detected(self) -> None:
        articles = "".join(
            f"## Article {r}: x\n"
            for r in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII",
                      "IX", "X", "XI", "XII", "XIII")
        )
        self.assertEqual(governance_check.count_articles(articles), 13)
        self.assertNotEqual(
            governance_check.count_articles(articles),
            governance_check.rules_upper_bound("Articles I-XII"),
        )


class TestSetup(unittest.TestCase):
    """R-5 / R-6: run_setup succeeds and is idempotent."""

    def test_setup_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            code = bootstrap.run_setup(target, make_venv=False, run_checks=False)
            self.assertEqual(code, 0)
            self.assertTrue(
                (target / "spec-driven-development" / "ledger" / "fleet.db").is_file()
            )

    def test_setup_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            self.assertEqual(bootstrap.run_setup(target, make_venv=False, run_checks=False), 0)
            self.assertEqual(bootstrap.run_setup(target, make_venv=False, run_checks=False), 0)
            ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
            connection = sqlite3.connect(str(ledger))
            try:
                count = connection.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(count, 0)


class TestDoctor(unittest.TestCase):
    """R-8: doctor green on the real repo, red on a tree with a leak."""

    def test_doctor_green_on_framework(self) -> None:
        code = bootstrap.run_doctor(FRAMEWORK_ROOT, run_tests=False)
        self.assertEqual(code, 0)

    def test_doctor_red_on_leak(self) -> None:
        # Plant a home-path origin token into the otherwise-green framework
        # tree so the origin check is the single isolated reason doctor flips
        # red. Temp file is removed in finally.
        leak = FRAMEWORK_ROOT / ".github" / "_sdd045_leak_probe.md"
        leak.write_text("Saved under C:\\Users\\someone\\notes.md.\n", encoding="utf-8")
        try:
            code = bootstrap.run_doctor(FRAMEWORK_ROOT, run_tests=False)
        finally:
            leak.unlink(missing_ok=True)
        self.assertEqual(code, 1)


class TestStdlibOnly(unittest.TestCase):
    """R-15: the new/edited modules import stdlib + sibling modules only."""

    LOCAL_OK = {
        "bootstrap",
        "origin_lint",
        "governance_check",
        "schema_lint",
        "tdd_gate_check",
        "done_check",
    }

    def _assert_stdlib_only(self, module) -> None:
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(
                        top in stdlib or top in self.LOCAL_OK,
                        f"non-stdlib import in {module.__name__}: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(
                    top in stdlib or top in self.LOCAL_OK,
                    f"non-stdlib import in {module.__name__}: {node.module}",
                )

    def test_bootstrap_stdlib_only(self) -> None:
        self._assert_stdlib_only(bootstrap)

    def test_origin_lint_stdlib_only(self) -> None:
        self._assert_stdlib_only(origin_lint)

    def test_governance_check_stdlib_only(self) -> None:
        self._assert_stdlib_only(governance_check)


if __name__ == "__main__":
    unittest.main()
