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


if __name__ == "__main__":
    unittest.main()
