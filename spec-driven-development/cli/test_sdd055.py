"""Isolated contract tests for SDD-055 explicit doctor profiles."""

from __future__ import annotations

import io
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

CLI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CLI_DIR))

import bootstrap  # noqa: E402


def _minimal_root(tmp: Path, *, active_pi: bool = False, ledger: bool = False) -> Path:
    root = tmp / "repo"
    (root / "spec-driven-development" / "ledger").mkdir(parents=True)
    if active_pi:
        marker = root / "spec-driven-development" / "sprints" / "PI-9" / "CURRENT_PI.md"
        marker.parent.mkdir(parents=True)
        marker.write_text("---\nstatus: active\n---\n", encoding="utf-8")
    if ledger:
        connection = sqlite3.connect(root / "spec-driven-development" / "ledger" / "fleet.db")
        try:
            connection.execute("CREATE TABLE dispatches (pi TEXT NOT NULL)")
            connection.commit()
        finally:
            connection.close()
    return root


def _run_doctor(root: Path, *, mode: str) -> tuple[int, str]:
    stdout = io.StringIO()
    with mock.patch("governance_check.check_governance", return_value=(True, [])), \
         mock.patch("origin_lint.find_tracked_dbs", return_value=[]), \
         mock.patch("origin_lint.scan_origin_tokens", return_value=[]), \
         redirect_stdout(stdout):
        result = bootstrap.run_doctor(root, run_tests=False, mode=mode)
    return result, stdout.getvalue()


class TestExplicitDoctorMode(unittest.TestCase):
    def test_local_is_default_and_ci_is_explicit(self) -> None:
        local = bootstrap.parse_args(["doctor"])
        ci = bootstrap.parse_args(["doctor", "--mode", "ci"])
        self.assertEqual(local.mode, "local")
        self.assertEqual(ci.mode, "ci")

    def test_ambient_ci_variables_do_not_select_mode(self) -> None:
        with mock.patch.dict(os.environ, {"CI": "true", "GITHUB_ACTIONS": "true"}):
            args = bootstrap.parse_args(["doctor"])
        self.assertEqual(args.mode, "local")


class TestProfileLedgerBoundary(unittest.TestCase):
    def test_local_fails_when_ledger_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result, output = _run_doctor(Path(directory), mode="local")
        self.assertEqual(result, 1)
        self.assertIn("[FAIL] ledger reachable", output)

    def test_ci_reports_missing_local_ledger_checks_as_inapplicable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result, output = _run_doctor(Path(directory), mode="ci")
        self.assertEqual(result, 0)
        self.assertIn("[N/A] ledger reachable", output)
        self.assertIn("[N/A] current-PI dispatch rows", output)
        self.assertNotIn("[PASS] ledger reachable", output)

    def test_local_zero_rows_fails_then_matching_row_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = _minimal_root(Path(directory), active_pi=True, ledger=True)
            _, ok, detail = bootstrap.check_current_pi_dispatch_rows(root)
            self.assertFalse(ok, detail)
            connection = sqlite3.connect(root / "spec-driven-development" / "ledger" / "fleet.db")
            try:
                connection.execute("INSERT INTO dispatches (pi) VALUES (?)", ("PI-9",))
                connection.commit()
            finally:
                connection.close()
            _, ok, detail = bootstrap.check_current_pi_dispatch_rows(root)
            self.assertTrue(ok, detail)


class TestTrackedDatabaseGuard(unittest.TestCase):
    def test_tracked_database_fails_in_both_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = _minimal_root(Path(directory), ledger=True)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            tracked_db = root / "tracked.db"
            tracked_db.write_bytes(b"not sqlite")
            subprocess.run(["git", "-C", str(root), "add", "tracked.db"], check=True)
            for mode in ("local", "ci"):
                stdout = io.StringIO()
                with mock.patch("governance_check.check_governance", return_value=(True, [])), \
                     mock.patch("origin_lint.scan_origin_tokens", return_value=[]), \
                     redirect_stdout(stdout):
                    result = bootstrap.run_doctor(root, run_tests=False, mode=mode)
                self.assertEqual(result, 1, mode)
                self.assertIn("[FAIL] tracked databases absent", stdout.getvalue())


class TestCommonChecksRemainShared(unittest.TestCase):
    def test_both_modes_invoke_all_source_controlled_checks(self) -> None:
        for mode in ("local", "ci"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = _minimal_root(Path(directory), ledger=True)
                commands: list[list[str]] = []

                def fake_run_check(_root: Path, command: list[str]) -> tuple[int, str]:
                    commands.append(command)
                    return 0, "616 passed, 2 skipped"

                stdout = io.StringIO()
                with mock.patch("bootstrap.framework_root", return_value=root), \
                     mock.patch("bootstrap._run_check", side_effect=fake_run_check), \
                     mock.patch("governance_check.check_governance", return_value=(True, [])) as governance, \
                     mock.patch("origin_lint.find_tracked_dbs", return_value=[]), \
                     mock.patch("origin_lint.scan_origin_tokens", return_value=[]) as origin, \
                     mock.patch("staledoc_lint.scan", return_value=[]) as stale, \
                     mock.patch("tdd_gate_check.changed_files", return_value=[]) as changed, \
                     mock.patch("tdd_gate_check.evaluate", return_value=(True, [])) as tdd, \
                     mock.patch("done_check.audit_pi", return_value=[]) as done, \
                     mock.patch("bootstrap.current_pi_name", return_value="PI-9"), \
                     mock.patch("bootstrap.check_current_pi_dispatch_rows", return_value=("current-PI dispatch rows", True, "PI-9: 1 row")), \
                     redirect_stdout(stdout):
                    result = bootstrap.run_doctor(root, mode=mode)

                self.assertEqual(result, 0, stdout.getvalue())
                flattened = [" ".join(command) for command in commands]
                self.assertTrue(any("schema_lint.py --check-orphans" in command for command in flattened))
                self.assertTrue(any("-m pytest spec-driven-development" in command for command in flattened))
                governance.assert_called_once()
                origin.assert_called_once()
                stale.assert_called_once()
                changed.assert_called_once()
                tdd.assert_called_once()
                done.assert_called_once()


if __name__ == "__main__":
    unittest.main()
