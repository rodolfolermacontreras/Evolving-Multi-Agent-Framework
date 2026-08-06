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
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import venv
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

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

    def test_repo_local_venv_is_ignored(self) -> None:
        gitignore = (FRAMEWORK_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".venv/", gitignore.splitlines())

    def test_quick_start_documents_setup_environment_and_doctor(self) -> None:
        readme = (FRAMEWORK_ROOT / "README.md").read_text(encoding="utf-8")
        for promise in (
            "creates or reuses the repo-local `.venv`",
            "ensures `pytest` is installed",
            "initializes the local `fleet.db` ledger",
            "runs health checks and tests",
            "through that environment",
        ):
            self.assertIn(promise, readme)
        self.assertIn(
            "python spec-driven-development/cli/bootstrap.py doctor",
            readme,
        )

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


class TestSetupVenvContract(unittest.TestCase):
    """Fresh-clone setup installs and checks through its repo-local venv."""

    def test_venv_python_uses_windows_and_posix_conventions(self) -> None:
        root = Path("repo")
        self.assertEqual(
            bootstrap._venv_python(root, platform_name="nt"),
            root / ".venv" / "Scripts" / "python.exe",
        )
        self.assertEqual(
            bootstrap._venv_python(root, platform_name="posix"),
            root / ".venv" / "bin" / "python",
        )

    def test_setup_uses_newly_created_venv_for_install_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            venv_python = target / ".venv" / "bin" / "python"
            calls: list[tuple[list[str], Path | None]] = []

            def fake_run_check(
                _root: Path,
                args: list[str],
                *,
                executable: Path | None = None,
            ) -> tuple[int, str]:
                calls.append((args, executable))
                if args[:2] == ["-m", "venv"]:
                    venv_python.parent.mkdir(parents=True)
                    venv_python.touch()
                    return 0, ""
                if args[:1] == ["-c"]:
                    return 1, "pytest missing"
                return 0, "1 passed"

            with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                 mock.patch("bootstrap._run_check", side_effect=fake_run_check):
                code = bootstrap.run_setup(target)

            self.assertEqual(code, 0)
            self.assertEqual(calls[0][1], Path(sys.executable))
            self.assertTrue(all(executable == venv_python for _, executable in calls[1:]))

    def test_default_check_runner_prefers_existing_venv_for_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            venv_python = target / ".venv" / "bin" / "python"
            venv_python.parent.mkdir(parents=True)
            venv_python.touch()
            completed = subprocess.CompletedProcess([], 0, "ok", "")

            with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                 mock.patch("bootstrap.subprocess.run", return_value=completed) as run:
                code, output = bootstrap._run_check(target, ["-m", "pytest"])

            self.assertEqual((code, output), (0, "ok"))
            self.assertEqual(run.call_args.args[0][0], str(venv_python))

    def test_default_check_runner_uses_ambient_python_without_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            completed = subprocess.CompletedProcess([], 0, "ok", "")

            with mock.patch("bootstrap.subprocess.run", return_value=completed) as run:
                code, output = bootstrap._run_check(target, ["-m", "pytest"])

            self.assertEqual((code, output), (0, "ok"))
            self.assertEqual(run.call_args.args[0][0], sys.executable)

    def test_default_check_runner_rejects_existing_venv_without_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".venv").mkdir()

            with mock.patch("bootstrap.subprocess.run") as run:
                code, output = bootstrap._run_check(target, ["-m", "pytest"])

            self.assertNotEqual(code, 0)
            self.assertIn(".venv interpreter missing", output)
            run.assert_not_called()

    def test_default_check_runner_reports_corrupt_venv_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            venv_python = bootstrap._venv_python(target)
            venv_python.parent.mkdir(parents=True)
            venv_python.write_text("not an executable", encoding="utf-8")

            code, output = bootstrap._run_check(target, ["-m", "pytest"])

            self.assertNotEqual(code, 0)
            self.assertIn("unable to launch Python interpreter", output)
            self.assertIn(str(venv_python), output)

    def test_skip_venv_uses_current_interpreter_when_valid_venv_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            venv.EnvBuilder(with_pip=False).create(target / ".venv")
            calls: list[tuple[list[str], Path | None]] = []

            def fake_run_check(
                _root: Path,
                args: list[str],
                *,
                executable: Path | None = None,
            ) -> tuple[int, str]:
                calls.append((args, executable))
                return 0, "1 passed"

            with mock.patch("bootstrap._run_check", side_effect=fake_run_check):
                code = bootstrap.run_setup(target, make_venv=False)

            self.assertEqual(code, 0)
            self.assertTrue(calls)
            self.assertTrue(
                all(executable == Path(sys.executable) for _, executable in calls)
            )
            self.assertFalse(any(args[:3] == ["-m", "pip", "install"] for args, _ in calls))

    def test_setup_installs_pytest_and_runs_checks_with_venv_python(self) -> None:
        for relative_python in (
            Path(".venv/Scripts/python.exe"),
            Path(".venv/bin/python"),
        ):
            with self.subTest(relative_python=relative_python), \
                 tempfile.TemporaryDirectory() as tmp:
                target = _make_target(Path(tmp))
                venv_python = target / relative_python
                venv_python.parent.mkdir(parents=True)
                venv_python.touch()
                calls: list[tuple[list[str], Path | None]] = []

                def fake_run_check(
                    _root: Path,
                    args: list[str],
                    *,
                    executable: Path | None = None,
                ) -> tuple[int, str]:
                    calls.append((args, executable))
                    if args[:1] == ["-c"]:
                        return 1, "ModuleNotFoundError: No module named 'pytest'"
                    return 0, "1 passed"

                with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                     mock.patch("bootstrap._run_check", side_effect=fake_run_check):
                    code = bootstrap.run_setup(target)

                self.assertEqual(code, 0)
                self.assertIn(
                    (["-m", "pip", "install", "pytest>=8,<9"], venv_python),
                    calls,
                )
                self.assertTrue(calls)
                self.assertTrue(all(executable == venv_python for _, executable in calls))

    def test_setup_reports_pytest_install_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            venv_python = target / ".venv" / "bin" / "python"
            venv_python.parent.mkdir(parents=True)
            venv_python.touch()

            def fake_run_check(
                _root: Path,
                args: list[str],
                *,
                executable: Path | None = None,
            ) -> tuple[int, str]:
                if args[:1] == ["-c"]:
                    return 1, "pytest missing"
                if args[:3] == ["-m", "pip", "install"]:
                    return 1, "network unavailable"
                self.fail(f"unexpected command after install failure: {args}")

            stderr = io.StringIO()
            with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                 mock.patch("bootstrap._run_check", side_effect=fake_run_check), \
                 redirect_stderr(stderr):
                code = bootstrap.run_setup(target)

            self.assertEqual(code, 1)
            self.assertIn("failed to install pytest", stderr.getvalue())
            self.assertIn("network unavailable", stderr.getvalue())

    def test_setup_does_not_reinstall_available_pytest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            venv_python = target / ".venv" / "bin" / "python"
            venv_python.parent.mkdir(parents=True)
            venv_python.touch()
            installed = False
            install_count = 0

            def fake_run_check(
                _root: Path,
                args: list[str],
                *,
                executable: Path | None = None,
            ) -> tuple[int, str]:
                nonlocal installed, install_count
                self.assertEqual(executable, venv_python)
                if args[:1] == ["-c"]:
                    return (0, "") if installed else (1, "pytest missing")
                if args[:3] == ["-m", "pip", "install"]:
                    install_count += 1
                    installed = True
                return 0, "1 passed"

            with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                 mock.patch("bootstrap._run_check", side_effect=fake_run_check):
                self.assertEqual(bootstrap.run_setup(target), 0)
                self.assertEqual(bootstrap.run_setup(target), 0)

            self.assertEqual(install_count, 1)

    def test_setup_reinstalls_pytest_outside_supported_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            venv_python = target / ".venv" / "bin" / "python"
            venv_python.parent.mkdir(parents=True)
            venv_python.touch()
            calls: list[list[str]] = []

            def fake_run_check(
                _root: Path,
                args: list[str],
                *,
                executable: Path | None = None,
            ) -> tuple[int, str]:
                self.assertEqual(executable, venv_python)
                calls.append(args)
                if args[0] == "-c":
                    return 1, "pytest 9 is outside supported range"
                return 0, "1 passed"

            with mock.patch("bootstrap._venv_python", return_value=venv_python), \
                 mock.patch("bootstrap._run_check", side_effect=fake_run_check):
                code = bootstrap.run_setup(target)

            self.assertEqual(code, 0)
            self.assertTrue(any("importlib.metadata" in " ".join(args) for args in calls))
            self.assertIn(["-m", "pip", "install", "pytest>=8,<9"], calls)


class TestDoctor(unittest.TestCase):
    """R-8: source health is green, then red when a tracked input leaks."""

    def test_doctor_reports_invalid_existing_venv_as_failed_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = _make_target(Path(tmp))
            (target / ".venv").mkdir()
            ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
            connection = sqlite3.connect(ledger)
            try:
                connection.execute("CREATE TABLE dispatches (pi TEXT NOT NULL)")
                connection.commit()
            finally:
                connection.close()

            stdout = io.StringIO()
            with mock.patch("bootstrap.framework_root", return_value=target), \
                 mock.patch("governance_check.check_governance", return_value=(True, [])), \
                 mock.patch("origin_lint.find_tracked_dbs", return_value=[]), \
                 mock.patch("origin_lint.scan_origin_tokens", return_value=[]), \
                 mock.patch("staledoc_lint.scan", return_value=[]), \
                 mock.patch("tdd_gate_check.changed_files", return_value=[]), \
                 mock.patch("tdd_gate_check.evaluate", return_value=(True, [])), \
                 mock.patch("bootstrap.current_pi_name", return_value=None), \
                 redirect_stdout(stdout):
                code = bootstrap.run_doctor(target, run_tests=False, mode="local")

            self.assertEqual(code, 1)
            self.assertIn("[FAIL] schema_lint clean", stdout.getvalue())
            self.assertIn(".venv interpreter missing", stdout.getvalue())

    def test_ci_doctor_green_on_framework_source(self) -> None:
        code = bootstrap.run_doctor(FRAMEWORK_ROOT, run_tests=False, mode="ci")
        self.assertEqual(code, 0)

    def test_ci_doctor_red_on_leak(self) -> None:
        # Plant a home-path origin token into the otherwise-green framework
        # tree so the origin check is the single isolated reason doctor flips
        # red. Temp file is removed in finally.
        leak = FRAMEWORK_ROOT / ".github" / "_sdd045_leak_probe.md"
        leak.write_text("Saved under C:\\Users\\someone\\notes.md.\n", encoding="utf-8")
        try:
            code = bootstrap.run_doctor(FRAMEWORK_ROOT, run_tests=False, mode="ci")
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
        "staledoc_lint",
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

    def test_staledoc_lint_stdlib_only(self) -> None:
        import staledoc_lint
        self._assert_stdlib_only(staledoc_lint)


if __name__ == "__main__":
    unittest.main()
