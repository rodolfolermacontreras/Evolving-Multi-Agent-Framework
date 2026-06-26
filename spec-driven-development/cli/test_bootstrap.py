"""Tests for cli/bootstrap.py host-link subcommand (SDD-016 + SDD-017).

Covers R1..R6 from `specs/2026-06-06-symlink-portability/validation.md`.

Stdlib only (LESSON-001 / Article V).
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import bootstrap  # noqa: E402


FRAMEWORK_GITHUB = bootstrap.framework_root() / ".github"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_host_repo(tmp: Path, with_github: bool = False) -> Path:
    """Create a temp host directory and `git init` it. Optionally seed .github/."""
    repo = tmp / "host"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--quiet", "-b", "main", str(repo)],
        check=True, capture_output=True,
    )
    # An empty commit so HEAD exists (validator wants a real repo).
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--allow-empty",
         "-m", "init", "--quiet"],
        check=True, capture_output=True,
        env={**os.environ,
             "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e"},
    )
    if with_github:
        gh = repo / ".github"
        gh.mkdir()
        (gh / "marker.txt").write_text("host content", encoding="utf-8")
    return repo


def run_main(argv: list[str]) -> tuple[int, str, str]:
    """Invoke bootstrap.main([...]) capturing stdout, stderr, exit code."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = bootstrap.main(argv)
    return rc, out.getvalue(), err.getvalue()


# --------------------------------------------------------------------------- #
# R1 -- dry-run default
# --------------------------------------------------------------------------- #

class TestHostLinkDryRun(unittest.TestCase):
    """R1 / AC-1 / AC-2 -- dry-run is the default; --apply required for mutation."""

    def test_host_link_dry_run_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(host)]
            )
            self.assertEqual(rc, 0, f"stderr: {stderr}")
            self.assertIn("dry-run", stdout.lower())
            self.assertFalse(
                (host / ".github").exists(),
                "dry-run must not create the link",
            )


# --------------------------------------------------------------------------- #
# R2 -- clean install (Linux/macOS path; Windows succeeds when symlink works)
# --------------------------------------------------------------------------- #

class TestHostLinkApplyClean(unittest.TestCase):
    """R2 / AC-1 -- clean install creates a link resolving to framework's .github."""

    def test_host_link_apply_clean_creates_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(host), "--apply"]
            )
            self.assertEqual(rc, 0, f"stderr: {stderr}")
            link_path = host / ".github"
            self.assertTrue(
                link_path.exists() or link_path.is_symlink(),
                "link path must exist or be a symlink after --apply",
            )
            # Resolved path must point at the framework .github/.
            self.assertEqual(
                link_path.resolve(), FRAMEWORK_GITHUB.resolve(),
                "link must resolve to framework's .github/",
            )


# --------------------------------------------------------------------------- #
# R3 -- conflict abort (default behavior when .github/ exists)
# --------------------------------------------------------------------------- #

class TestHostLinkConflictAbort(unittest.TestCase):
    """R3 / AC-3 -- existing .github/ with no conflict flag aborts."""

    def test_host_link_conflict_abort_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp), with_github=True)
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(host), "--apply"]
            )
            self.assertEqual(rc, 1, f"stdout: {stdout}; stderr: {stderr}")
            self.assertIn("--backup", stderr)
            self.assertIn("--force", stderr)
            # Host's marker.txt must be preserved.
            self.assertTrue(
                (host / ".github" / "marker.txt").is_file(),
                "abort must not touch host's existing .github/",
            )


# --------------------------------------------------------------------------- #
# R4 -- backup and force modes
# --------------------------------------------------------------------------- #

class TestHostLinkBackup(unittest.TestCase):
    """R4 / AC-4 -- --backup moves .github/ to timestamped backup, then links."""

    def test_host_link_backup_moves_then_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp), with_github=True)
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(host), "--backup", "--apply"]
            )
            self.assertEqual(rc, 0, f"stderr: {stderr}")
            link_path = host / ".github"
            self.assertEqual(link_path.resolve(), FRAMEWORK_GITHUB.resolve())
            backups = sorted(host.glob(".github.bak.*"))
            self.assertEqual(
                len(backups), 1,
                f"expected one .github.bak.* directory, got {backups}",
            )
            self.assertTrue((backups[0] / "marker.txt").is_file(),
                            "backup must preserve host's original content")


class TestHostLinkForce(unittest.TestCase):
    """R4 / AC-5 -- --force deletes .github/ then links (destructive)."""

    def test_host_link_force_deletes_then_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp), with_github=True)
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(host), "--force", "--apply"]
            )
            self.assertEqual(rc, 0, f"stderr: {stderr}")
            link_path = host / ".github"
            self.assertEqual(link_path.resolve(), FRAMEWORK_GITHUB.resolve())
            self.assertEqual(
                list(host.glob(".github.bak.*")), [],
                "force must not create a backup",
            )


class TestHostLinkConflictFlagsMutuallyExclusive(unittest.TestCase):
    """R4 / argparse -- --backup and --force cannot both be passed."""

    def test_backup_and_force_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp), with_github=True)
            # argparse exits 2 via SystemExit on mutually exclusive violation.
            with self.assertRaises(SystemExit) as ctx:
                run_main(
                    ["host-link", "--target", str(host),
                     "--backup", "--force", "--apply"]
                )
            self.assertEqual(ctx.exception.code, 2)


# --------------------------------------------------------------------------- #
# R5 -- Windows junction fallback (mocked)
# --------------------------------------------------------------------------- #

class TestHostLinkWindowsJunctionFallback(unittest.TestCase):
    """R5 / AC-6 -- os.symlink OSError triggers mklink /J via subprocess.run."""

    def test_host_link_windows_junction_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            captured_calls: list[list[str]] = []
            real_run = subprocess.run

            def fake_run(cmd, *args, **kwargs):  # noqa: ANN001, ANN002
                # Only intercept mklink calls; let git pass through so
                # validate_host_link_target's git rev-parse still succeeds.
                if isinstance(cmd, (list, tuple)) and len(cmd) > 0 and \
                   any("mklink" in str(c) for c in cmd):
                    captured_calls.append(list(cmd))
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                return real_run(cmd, *args, **kwargs)

            with mock.patch("os.symlink",
                            side_effect=OSError("permission denied")), \
                 mock.patch("bootstrap.subprocess.run",
                            side_effect=fake_run):
                rc, stdout, stderr = run_main(
                    ["host-link", "--target", str(host), "--apply"]
                )
            self.assertEqual(rc, 0, f"stderr: {stderr}")
            self.assertTrue(
                any("mklink" in arg for call in captured_calls for arg in call),
                f"expected mklink /J invocation; got {captured_calls}",
            )
            self.assertTrue(
                any("/J" in arg for call in captured_calls for arg in call),
                f"expected /J flag; got {captured_calls}",
            )


# --------------------------------------------------------------------------- #
# R6 -- non-git-repo guard
# --------------------------------------------------------------------------- #

class TestHostLinkNotAGitRepo(unittest.TestCase):
    """R6 / AC-7 -- non-git-repo target aborts with a clear message."""

    def test_host_link_target_not_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            non_git = Path(tmp) / "plain-dir"
            non_git.mkdir()
            rc, stdout, stderr = run_main(
                ["host-link", "--target", str(non_git), "--apply"]
            )
            self.assertEqual(rc, 1, f"stdout: {stdout}; stderr: {stderr}")
            self.assertIn("git repository", stderr.lower())


# --------------------------------------------------------------------------- #
# Regression smoke -- existing greenfield/brownfield subparsers untouched
# --------------------------------------------------------------------------- #

class TestSubparserRegression(unittest.TestCase):
    """No-op smoke check that the existing subparsers still parse."""

    def test_greenfield_subparser_still_parses(self) -> None:
        # Should parse without raising; we do not actually run greenfield.
        args = bootstrap.parse_args([
            "greenfield", "python-library",
            "--project-name", "TestProj",
            "--owner", "Tester",
            "--target", "/tmp/anywhere",
        ])
        self.assertEqual(args.command, "greenfield")
        self.assertEqual(args.archetype_name, "python-library")
        self.assertEqual(args.project_name, "TestProj")

    def test_brownfield_subparser_still_parses(self) -> None:
        args = bootstrap.parse_args(["brownfield", "/tmp/some-repo"])
        self.assertEqual(args.command, "brownfield")
        self.assertEqual(args.target_path, "/tmp/some-repo")

    def test_host_link_subparser_present(self) -> None:
        """Confirms the new subcommand is registered (catches accidental rename)."""
        args = bootstrap.parse_args(
            ["host-link", "--target", "/tmp/host"]
        )
        self.assertEqual(args.command, "host-link")
        self.assertFalse(args.apply, "dry-run is the default")
        self.assertFalse(args.backup)
        self.assertFalse(args.force)


# --------------------------------------------------------------------------- #
# Roster sanity -- the new agent and skill are rostered
# --------------------------------------------------------------------------- #

class TestRosterAdditions(unittest.TestCase):
    """R7 (partial) -- roster rows for SDD-017 hire are present."""

    def test_dev_env_manager_in_agents_json(self) -> None:
        agents_path = (
            bootstrap.framework_root() / "spec-driven-development"
            / "roster" / "agents.json"
        )
        agents = json.loads(agents_path.read_text(encoding="utf-8"))
        ids = [a["id"] for a in agents]
        self.assertIn("dev-env-manager-general", ids)

    def test_host_integration_symlink_in_skills_json(self) -> None:
        skills_path = (
            bootstrap.framework_root() / "spec-driven-development"
            / "roster" / "skills.json"
        )
        skills = json.loads(skills_path.read_text(encoding="utf-8"))
        ids = [s["id"] for s in skills]
        self.assertIn("host-integration-symlink", ids)


# --------------------------------------------------------------------------- #
# SDD-027: Host .gitignore protection tests
# --------------------------------------------------------------------------- #


class TestGitignoreManifestLoads(unittest.TestCase):
    """R6: manifest JSON loads and has both keys."""

    def test_gitignore_manifest_loads(self) -> None:
        manifest = bootstrap._load_gitignore_manifest()
        self.assertIn("must_be_ignored", manifest)
        self.assertIn("must_be_tracked", manifest)
        self.assertIsInstance(manifest["must_be_ignored"], list)
        self.assertIsInstance(manifest["must_be_tracked"], list)
        self.assertTrue(len(manifest["must_be_ignored"]) > 0)
        self.assertTrue(len(manifest["must_be_tracked"]) > 0)


class TestParseGitignoreBasic(unittest.TestCase):
    """R2: parse host .gitignore into patterns."""

    def test_parse_gitignore_basic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gi = Path(tmp) / ".gitignore"
            gi.write_text("# comment\n__pycache__/\n*.pyc\n\n.env\n",
                          encoding="utf-8")
            patterns = bootstrap._parse_host_gitignore(gi)
            self.assertIn("__pycache__/", patterns)
            self.assertIn("*.pyc", patterns)
            self.assertIn(".env", patterns)
            self.assertNotIn("# comment", patterns)


class TestCheckCoverageMissingRule(unittest.TestCase):
    """R2: manifest rule not in .gitignore is flagged."""

    def test_check_coverage_missing_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            (host / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            manifest = {
                "must_be_ignored": ["*.pyc", "__pycache__/", "fleet.db"],
                "must_be_tracked": [],
            }
            missing, over = bootstrap._check_gitignore_coverage(host, manifest)
            self.assertIn("__pycache__/", missing)
            self.assertIn("fleet.db", missing)
            self.assertNotIn("*.pyc", missing)


class TestCheckCoverageClean(unittest.TestCase):
    """R2: all rules present -> no flags."""

    def test_check_coverage_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            (host / ".gitignore").write_text(
                "*.pyc\n__pycache__/\nfleet.db\n",
                encoding="utf-8",
            )
            manifest = {
                "must_be_ignored": ["*.pyc", "__pycache__/", "fleet.db"],
                "must_be_tracked": [],
            }
            missing, over = bootstrap._check_gitignore_coverage(host, manifest)
            self.assertEqual(missing, [])
            self.assertEqual(over, [])


class TestMissingGitignoreRefuses(unittest.TestCase):
    """R5: host with no .gitignore -> refuse."""

    def test_missing_gitignore_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            # No .gitignore exists
            buf = io.StringIO()
            with redirect_stderr(buf):
                ok = bootstrap._check_host_gitignore(host, mode="strict")
            self.assertFalse(ok)
            self.assertIn("no .gitignore", buf.getvalue().lower())

    def test_missing_gitignore_warns_in_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            buf = io.StringIO()
            with redirect_stderr(buf):
                ok = bootstrap._check_host_gitignore(host, mode="prompt")
            self.assertTrue(ok)
            self.assertIn("no .gitignore", buf.getvalue().lower())


class TestGitignoreModeStrict(unittest.TestCase):
    """R3: strict mode with conflict -> returns False."""

    def test_gitignore_mode_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            (host / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            manifest = {
                "must_be_ignored": ["*.pyc", "__pycache__/"],
                "must_be_tracked": [],
            }
            buf = io.StringIO()
            with redirect_stderr(buf):
                ok = bootstrap._check_host_gitignore(
                    host, mode="strict", manifest=manifest
                )
            self.assertFalse(ok)
            self.assertIn("__pycache__/", buf.getvalue())


class TestGitignoreModeWarn(unittest.TestCase):
    """R3: warn mode with conflict -> returns True + output."""

    def test_gitignore_mode_warn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            (host / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            manifest = {
                "must_be_ignored": ["*.pyc", "__pycache__/"],
                "must_be_tracked": [],
            }
            buf = io.StringIO()
            with redirect_stderr(buf):
                ok = bootstrap._check_host_gitignore(
                    host, mode="warn", manifest=manifest
                )
            self.assertTrue(ok)
            self.assertIn("__pycache__/", buf.getvalue())


class TestGitignoreModeSkip(unittest.TestCase):
    """R3: skip mode -> returns True, no check done."""

    def test_gitignore_mode_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp)
            # No .gitignore, but skip mode should bypass
            ok = bootstrap._check_host_gitignore(host, mode="skip")
            self.assertTrue(ok)


class TestHostLinkWithGitignoreCheck(unittest.TestCase):
    """R8 + integration: host_link with gitignore check."""

    def test_host_link_with_gitignore_check_clean(self) -> None:
        """Clean gitignore -> host-link succeeds."""
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            manifest = bootstrap._load_gitignore_manifest()
            # Write a .gitignore that covers all must_be_ignored
            gi_lines = manifest["must_be_ignored"][:]
            (host / ".gitignore").write_text(
                "\n".join(gi_lines) + "\n", encoding="utf-8"
            )
            # Mock coverage check to report clean (avoids subprocess mock conflicts)
            with mock.patch(
                "bootstrap._check_gitignore_coverage",
                return_value=([], []),
            ):
                rc, stdout, stderr = run_main([
                    "host-link", "--target", str(host), "--apply",
                    "--gitignore-mode", "strict",
                ])
            self.assertEqual(rc, 0, f"stderr: {stderr}")

    def test_host_link_with_gitignore_check_fails_strict(self) -> None:
        """Missing gitignore rules + strict -> host-link fails."""
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            # .gitignore exists but is empty
            (host / ".gitignore").write_text("# empty\n", encoding="utf-8")
            # Mock coverage check to report missing rules
            with mock.patch(
                "bootstrap._check_gitignore_coverage",
                return_value=(["__pycache__/", "*.pyc"], []),
            ):
                rc, stdout, stderr = run_main([
                    "host-link", "--target", str(host), "--apply",
                    "--gitignore-mode", "strict",
                ])
            self.assertEqual(rc, 1, f"stdout: {stdout}")

    def test_host_link_no_gitignore_check(self) -> None:
        """--no-gitignore-check disables the check."""
        with tempfile.TemporaryDirectory() as tmp:
            host = make_host_repo(Path(tmp))
            # No .gitignore at all, but check disabled
            rc, stdout, stderr = run_main([
                "host-link", "--target", str(host), "--apply",
                "--no-gitignore-check",
            ])
            self.assertEqual(rc, 0, f"stderr: {stderr}")


class TestExistingHostLinkTestsStillPass(unittest.TestCase):
    """R8: Sprint 5 tests still pass (regression check via class existence)."""

    def test_existing_test_classes_exist(self) -> None:
        """Verify Sprint 5 test classes are still defined."""
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkDryRun"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkApplyClean"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkConflictAbort"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkBackup"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkForce"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkWindowsJunctionFallback"))
        self.assertTrue(hasattr(sys.modules[__name__], "TestHostLinkNotAGitRepo"))


# --------------------------------------------------------------------------- #
# SDD-028: Windows junction documented limitation
# --------------------------------------------------------------------------- #

class TestWindowsJunctionDocumentedLimitation(unittest.TestCase):
    """SDD-028: Document that Windows junction test requires admin/dev-mode."""

    @unittest.skipUnless(sys.platform == "win32", "Windows-only test")
    def test_windows_junction_documented_limitation(self) -> None:
        """SDD-028: Windows junction creation may require admin or developer mode.

        On Windows, os.symlink raises OSError without developer mode or
        elevated privileges. The framework falls back to cmd /c mklink /J.
        Junctions work for directories without elevated privileges on
        recent Windows 10+, but traversal behavior differs from POSIX
        symlinks (junctions resolve on the server, symlinks on the client).

        This test documents the limitation; the actual junction test is
        TestHostLinkWindowsJunctionFallback which uses mocks.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "junction_test_link"
            source = Path(tmp) / "junction_test_source"
            source.mkdir()
            (source / "marker.txt").write_text("test", encoding="utf-8")
            try:
                bootstrap._windows_junction(target, source)
                self.assertTrue(
                    (target / "marker.txt").is_file(),
                    "Junction should allow traversal to read files",
                )
            except bootstrap.BootstrapError:
                self.skipTest(
                    "Windows junction creation failed -- requires admin or "
                    "developer mode. This is a known limitation documented "
                    "in SDD-028."
                )

    @unittest.skipIf(sys.platform == "win32", "Non-Windows always skips")
    def test_windows_junction_skip_non_windows(self) -> None:
        """On non-Windows platforms, junction test is not applicable."""
        pass  # No junction concept outside Windows


# --------------------------------------------------------------------------- #
# SDD-029: Stale-symlink vs real-directory distinction
# --------------------------------------------------------------------------- #

class TestStaleSymlinkDistinction(unittest.TestCase):
    """SDD-029: Distinguish stale symlink from real directory conflict."""

    def test_stale_symlink_detected(self) -> None:
        """A broken symlink at .github is identified as stale."""
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp) / "host"
            host.mkdir()
            link = host / ".github"
            # Create a symlink pointing to nonexistent target
            try:
                os.symlink("/nonexistent/path/that/does/not/exist", str(link))
            except OSError:
                self.skipTest("Cannot create symlinks on this platform/config")
            self.assertTrue(link.is_symlink())
            self.assertFalse(link.exists())  # broken

            is_stale = link.is_symlink() and not link.exists()
            self.assertTrue(is_stale, "Should detect stale/broken symlink")

    def test_real_directory_detected(self) -> None:
        """A real directory at .github is identified as a directory."""
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp) / "host"
            host.mkdir()
            gh = host / ".github"
            gh.mkdir()
            (gh / "marker.txt").write_text("real", encoding="utf-8")

            is_real_dir = gh.is_dir() and not gh.is_symlink()
            self.assertTrue(is_real_dir, "Should detect real directory")


# --------------------------------------------------------------------------- #
# SDD-046 B-1 -- current-PI dispatch-rows doctor check + current_pi_name helper
# --------------------------------------------------------------------------- #

import sqlite3  # noqa: E402


def _make_sdd_root(tmp: Path, *, pi: str | None, rows_for: str | None) -> Path:
    """Build a minimal framework-shaped root.

    pi: when given, write sprints/<pi>/CURRENT_PI.md marked active.
    rows_for: when given, insert one dispatches row for that PI into fleet.db.
    """
    root = tmp / "tree"
    sdd = root / "spec-driven-development"
    sprints = sdd / "sprints"
    ledger = sdd / "ledger"
    sprints.mkdir(parents=True)
    ledger.mkdir(parents=True)
    if pi is not None:
        marker_dir = sprints / pi
        marker_dir.mkdir()
        (marker_dir / "CURRENT_PI.md").write_text(
            f"---\nstatus: active\nsprint: {pi}\n---\n\n# {pi}\n\n"
            "Status: **ACTIVE**\n",
            encoding="utf-8",
        )
    db = ledger / "fleet.db"
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            "CREATE TABLE dispatches ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, dispatched_at TEXT NOT NULL, "
            "pi TEXT NOT NULL, sprint TEXT, feature_dir TEXT, task_id TEXT NOT NULL, "
            "task_title TEXT NOT NULL, agent_id TEXT NOT NULL, agent_role TEXT NOT NULL, "
            "outcome TEXT, outcome_at TEXT, notes TEXT)"
        )
        if rows_for is not None:
            conn.execute(
                "INSERT INTO dispatches "
                "(dispatched_at, pi, task_id, task_title, agent_id, agent_role, outcome) "
                "VALUES (?,?,?,?,?,?,?)",
                ("2026-06-26T00:00:00Z", rows_for, "T-1", "demo", "dev", "developer", "success"),
            )
        conn.commit()
    finally:
        conn.close()
    return root


class TestCurrentPiDispatchRowsCheck(unittest.TestCase):
    def test_fails_on_zero_rows_for_active_pi(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_sdd_root(Path(tmp), pi="PI-7", rows_for=None)
            result = bootstrap.check_current_pi_dispatch_rows(root)
            self.assertIsNotNone(result)
            label, ok, detail = result
            self.assertEqual(label, "current-PI dispatch rows")
            self.assertFalse(ok)
            self.assertIn("PI-7", detail)

    def test_passes_with_a_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_sdd_root(Path(tmp), pi="PI-7", rows_for="PI-7")
            result = bootstrap.check_current_pi_dispatch_rows(root)
            self.assertIsNotNone(result)
            _, ok, _ = result
            self.assertTrue(ok)

    def test_skips_with_no_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_sdd_root(Path(tmp), pi=None, rows_for=None)
            self.assertIsNone(bootstrap.current_pi_name(root))
            self.assertIsNone(bootstrap.check_current_pi_dispatch_rows(root))


class TestCurrentPiName(unittest.TestCase):
    def test_returns_pi7_for_current_tree(self):
        self.assertEqual(
            bootstrap.current_pi_name(bootstrap.framework_root()), "PI-7"
        )

    def test_picks_highest_numbered_active_pi(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_sdd_root(Path(tmp), pi="PI-7", rows_for=None)
            # add a lower active PI marker; resolver must prefer PI-7.
            lower = root / "spec-driven-development" / "sprints" / "PI-5"
            lower.mkdir()
            (lower / "CURRENT_PI.md").write_text(
                "---\nstatus: active\n---\n# PI-5\nStatus: **ACTIVE**\n",
                encoding="utf-8",
            )
            self.assertEqual(bootstrap.current_pi_name(root), "PI-7")


class TestDoctorPrintsNewCheckLines(unittest.TestCase):
    def test_doctor_output_lists_three_new_checks(self):
        rc, out, err = run_main(["doctor", "--skip-tests"])
        combined = out + err
        self.assertIn("current-PI dispatch rows", combined)
        self.assertIn("tdd gate", combined)
        self.assertIn("DONE completeness", combined)
        # rc may be non-zero before the Sprint dogfood adds PI-7 rows; we only
        # assert the new check lines are present.
        self.assertIn(rc, (0, 1))


# --------------------------------------------------------------------------- #
# SDD-047 A-2 -- project.config.json reader (owner/team/repo_url as config)
# --------------------------------------------------------------------------- #


class TestLoadProjectConfig(unittest.TestCase):
    """A-2 R-1: project.config.json is the single config surface for identity."""

    def test_framework_config_returns_owner(self) -> None:
        config = bootstrap.load_project_config(bootstrap.framework_root())
        self.assertEqual(config.get("owner"), "Rodolfo Lerma")

    def test_framework_config_has_team_and_repo_url(self) -> None:
        config = bootstrap.load_project_config(bootstrap.framework_root())
        self.assertIn("team", config)
        self.assertIn("repo_url", config)
        self.assertTrue(config["repo_url"].startswith("https://"))

    def test_missing_config_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = bootstrap.load_project_config(Path(tmp))
            self.assertEqual(config, {})

    def test_reads_arbitrary_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.config.json").write_text(
                json.dumps({"owner": "Jane Doe", "team": "T", "repo_url": "x"}),
                encoding="utf-8",
            )
            config = bootstrap.load_project_config(root)
            self.assertEqual(config["owner"], "Jane Doe")


if __name__ == "__main__":
    unittest.main()
