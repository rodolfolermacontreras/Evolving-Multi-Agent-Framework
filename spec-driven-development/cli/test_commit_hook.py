"""Tests for spec-driven-development/cli/hooks/commit-msg (SDD-FDC-001 / O1).

The hook is a Python stdlib script invoked via subprocess. Tests pass a
scratch temp file containing a candidate commit message and assert exit codes.

Coverage:
  - Valid type(scope): subject -> exit 0
  - Valid type: subject (no scope) -> exit 0
  - Valid feat(fdc): subject with body and footers -> exit 0
  - Missing type -> exit 1
  - Unknown type -> exit 1
  - Missing colon -> exit 1
  - Missing space after colon -> exit 1
  - Empty message -> exit 1
  - First-line-after-comments validation (git commit -v style)
  - Stdlib-only imports (LESSON-001)
"""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
HOOK = CLI_DIR / "hooks" / "commit-msg"


def _run_hook(message: str) -> subprocess.CompletedProcess[str]:
    """Write `message` to a temp file and run the hook against it."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".COMMIT_EDITMSG",
        delete=False
    ) as fh:
        fh.write(message)
        msg_path = Path(fh.name)
    try:
        return subprocess.run(
            [sys.executable, str(HOOK), str(msg_path)],
            capture_output=True, text=True,
        )
    finally:
        try:
            msg_path.unlink()
        except OSError:
            pass


class CommitMsgHookAcceptance(unittest.TestCase):
    """O1 / AC-6 -- the opt-in hook accepts valid and rejects invalid messages."""

    # --- Valid messages (exit 0) -------------------------------------------

    def test_accepts_type_with_scope(self) -> None:
        r = _run_hook("feat(fdc): T-FDC-04 add build_doc_count rollup helper\n")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_accepts_type_without_scope(self) -> None:
        r = _run_hook("chore: regenerate exec/ state -- Sprint 4 close\n")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_accepts_subject_with_body_and_footer(self) -> None:
        msg = (
            "test(fdc): T-FDC-02 add S1 footprint lock guard against 257b081\n"
            "\n"
            "Pins sha256 of inspect.getsource for render_html and friends.\n"
            "\n"
            "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\n"
        )
        r = _run_hook(msg)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_accepts_each_allowed_type(self) -> None:
        allowed = [
            "feat", "fix", "refactor", "test", "docs", "chore",
            "spec", "plan", "tasks", "triage", "close", "ideas", "retro",
        ]
        for t in allowed:
            r = _run_hook(f"{t}: a valid description\n")
            self.assertEqual(
                r.returncode, 0,
                f"type '{t}' should be accepted; stderr={r.stderr}",
            )

    def test_first_non_comment_line_is_subject(self) -> None:
        """git commit -v prepends a comment block; the hook must skip it."""
        msg = (
            "# Please enter the commit message for your changes.\n"
            "# Lines starting with '#' will be ignored.\n"
            "\n"
            "feat(fdc): T-FDC-07 add opt-in commit-msg hook\n"
        )
        r = _run_hook(msg)
        self.assertEqual(r.returncode, 0, r.stderr)

    # --- Invalid messages (exit 1) -----------------------------------------

    def test_rejects_missing_type(self) -> None:
        r = _run_hook("Updated the rollup helper\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("COMMIT-CONVENTION.md", r.stderr)

    def test_rejects_unknown_type(self) -> None:
        r = _run_hook("update: something\n")
        self.assertEqual(r.returncode, 1)

    def test_rejects_missing_colon(self) -> None:
        r = _run_hook("feat add the rollup helper\n")
        self.assertEqual(r.returncode, 1)

    def test_rejects_missing_space_after_colon(self) -> None:
        r = _run_hook("feat(fdc):add the rollup helper\n")
        self.assertEqual(r.returncode, 1)

    def test_rejects_empty_subject(self) -> None:
        r = _run_hook("\n\n# only comments and blanks\n")
        self.assertEqual(r.returncode, 1)

    def test_rejects_truly_empty_file(self) -> None:
        r = _run_hook("")
        self.assertEqual(r.returncode, 1)

    # --- Defensive ---------------------------------------------------------

    def test_missing_message_file_does_not_block(self) -> None:
        """A missing file path is a defensive no-op (cannot validate)."""
        r = subprocess.run(
            [sys.executable, str(HOOK), str(CLI_DIR / "no-such-file.txt")],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)

    def test_no_args_does_not_block(self) -> None:
        r = subprocess.run(
            [sys.executable, str(HOOK)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)

    # --- Stdlib-only (LESSON-001) ------------------------------------------

    def test_stdlib_only_imports(self) -> None:
        tree = ast.parse(HOOK.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".", 1)[0]
                    self.assertIn(mod, stdlib, f"non-stdlib import: {mod}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split(".", 1)[0]
                self.assertIn(mod, stdlib, f"non-stdlib import: {mod}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
