"""Tests for cli/taskstoissues.py (SDD-022)."""

from __future__ import annotations

import ast
import io
import json
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
REPO = THIS.parents[2]
sys.path.insert(0, str(CLI_DIR))

import taskstoissues  # noqa: E402


class FakeProvider:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.updated: list[tuple[str, dict[str, object]]] = []
        self.remote_state = "open"
        self.remote_body = "human note\n"

    def create_issue(self, payload: dict[str, object]) -> dict[str, object]:
        self.created.append(payload)
        number = len(self.created)
        return {"number": number, "html_url": f"https://example.test/{number}", "state": payload["state"]}

    def update_issue(self, remote_id: str, payload: dict[str, object], existing_body: str = "") -> dict[str, object]:
        self.updated.append((remote_id, payload))
        return {"number": remote_id, "html_url": f"https://example.test/{remote_id}", "state": payload["state"]}

    def get_issue(self, remote_id: str) -> dict[str, object]:
        return {"number": remote_id, "html_url": f"https://example.test/{remote_id}", "state": self.remote_state, "body": self.remote_body}


def make_spec_dir(tmp: Path, task_status: str = "pending") -> Path:
    spec_dir = tmp / "spec-driven-development" / "specs" / "2026-06-08-demo"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# Demo\n\n- Spec ID: SDD-999\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(textwrap.dedent(f"""
        # Task List

        ## Task T-999-01: Build bridge

        **Story**: [R1] Demo story
        **Type**: [S] sequential
        **Execution**: [AFK] autonomous
        **Size**: S
        **Status**: {task_status}
        **Files**: `spec-driven-development/cli/taskstoissues.py`
        **Files Blocked**: `constitution/**`
        **Depends on**: NONE

        ### Description

        Parse local task records.

        ### Acceptance Criteria

        - [ ] Parses task ID.
        - [ ] Preserves tasks.md authority.

        ### Verification

        ```powershell
        python -m pytest spec-driven-development/cli/test_taskstoissues.py
        ```
        """).strip() + "\n", encoding="utf-8")
    return spec_dir


def run_main(argv: list[str]) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = taskstoissues.main(argv)
    return rc, stdout.getvalue(), stderr.getvalue()


class TestParser(unittest.TestCase):
    def test_parser_reads_task_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = taskstoissues.parse_tasks(make_spec_dir(Path(tmp)))[0]
            self.assertEqual(task["id"], "T-999-01")
            self.assertEqual(task["title"], "Build bridge")
            self.assertEqual(task["status"], "pending")
            self.assertIn("Parse local task records", task["description"])
            self.assertEqual(len(task["acceptance_criteria"]), 2)
            self.assertIn("pytest", task["verification"])

    def test_parser_reads_current_sdd022_tasks(self) -> None:
        spec_dir = REPO / "spec-driven-development" / "specs" / "2026-06-08-ado-github-bridge"
        tasks = taskstoissues.parse_tasks(spec_dir)
        self.assertGreaterEqual(len(tasks), 10)
        self.assertEqual(tasks[0]["id"], "T-022-01")

    def test_duplicate_task_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp))
            text = (spec_dir / "tasks.md").read_text(encoding="utf-8")
            (spec_dir / "tasks.md").write_text(text + text.split("## Task", 1)[1].join(["\n## Task", ""]), encoding="utf-8")
            with self.assertRaises(taskstoissues.TaskSyncError):
                taskstoissues.parse_tasks(spec_dir)


class TestRendering(unittest.TestCase):
    def test_payload_is_deterministic_and_limited(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp))
            task = taskstoissues.parse_tasks(spec_dir)[0]
            payload = taskstoissues.render_payload(task, spec_dir, "SDD-999", "github")
            self.assertEqual(payload["title"], "[T-999-01] Build bridge")
            self.assertIn(taskstoissues.GENERATED_START, str(payload["body"]))
            self.assertIn("File Scope", str(payload["body"]))
            self.assertIn("sdd", payload["labels"])
            self.assertNotIn("assignee", payload)
            self.assertNotIn("milestone", payload)
            self.assertNotIn("dependencies", payload)

    def test_generated_region_update_preserves_human_text(self) -> None:
        old = "human intro\n<!-- sdd-task:start -->old<!-- sdd-task:end -->\nhuman tail"
        new = "<!-- sdd-task:start -->new<!-- sdd-task:end -->\n"
        merged = taskstoissues.replace_generated_region(old, new)
        self.assertIn("human intro", merged)
        self.assertIn("new", merged)
        self.assertIn("human tail", merged)


class TestCliAndMapping(unittest.TestCase):
    def test_dry_run_default_no_network_and_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp))
            rc, stdout, stderr = run_main(["push", "--spec-dir", str(spec_dir), "--repo", "owner/repo"])
            self.assertEqual(rc, 0, stderr)
            self.assertIn('"mode": "dry-run"', stdout)
            self.assertFalse((spec_dir / "issue-map.json").exists())

    def test_apply_writes_deterministic_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp))
            provider = FakeProvider()
            result = taskstoissues.push_tasks(spec_dir, "github", "owner/repo", apply=True, provider=provider, now="2026-06-08T00:00:00Z")
            self.assertEqual(result["created"], ["T-999-01"])
            data = json.loads((spec_dir / "issue-map.json").read_text(encoding="utf-8"))
            row = data["tasks"]["T-999-01"]
            self.assertEqual(row["provider"], "github")
            self.assertEqual(row["remote_id"], "1")
            self.assertEqual(row["last_synced_at"], "2026-06-08T00:00:00Z")
            self.assertNotIn("token", json.dumps(data).lower())

    def test_existing_mapping_is_idempotent_for_unchanged_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp))
            provider = FakeProvider()
            taskstoissues.push_tasks(spec_dir, "github", "owner/repo", apply=True, provider=provider, now="2026-06-08T00:00:00Z")
            result = taskstoissues.push_tasks(spec_dir, "github", "owner/repo", apply=True, provider=provider, now="2026-06-08T00:01:00Z")
            self.assertEqual(result["unchanged"], ["T-999-01"])
            self.assertEqual(len(provider.created), 1)
            self.assertEqual(provider.updated, [])

    def test_missing_token_fails_before_write(self) -> None:
        with self.assertRaises(taskstoissues.TaskSyncError):
            taskstoissues.resolve_github_token({})

    def test_cli_help_is_clean(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            run_main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


class TestProviderBoundary(unittest.TestCase):
    def test_github_request_uses_urllib_request(self) -> None:
        calls = []

        class Response:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def read(self) -> bytes:
                return b'{"number": 12, "html_url": "https://example.test/12", "state": "open"}'

        def transport(req):
            calls.append(req)
            return Response()

        provider = taskstoissues.GitHubProvider("owner/repo", "secret-token", transport=transport)
        provider.create_issue({"title": "t", "body": "b", "labels": ["sdd"], "state": "open"})
        self.assertEqual(calls[0].get_method(), "POST")
        self.assertIn("/repos/owner/repo/issues", calls[0].full_url)
        self.assertIn("Bearer secret-token", calls[0].headers["Authorization"])

    def test_ado_dry_run_provider_contract(self) -> None:
        provider = taskstoissues.AdoDryRunProvider()
        response = provider.create_issue({"title": "t", "body": "b", "labels": [], "state": "open"})
        self.assertEqual(response["state"], "open")
        self.assertEqual(provider.required_env, ("ADO_PAT", "ADO_ORG_URL", "ADO_PROJECT"))


class TestConflictsAndGuards(unittest.TestCase):
    def test_conflict_report_written_without_mutating_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spec_dir = make_spec_dir(Path(tmp), task_status="done")
            provider = FakeProvider()
            taskstoissues.push_tasks(spec_dir, "github", "owner/repo", apply=True, provider=provider, now="2026-06-08T00:00:00Z")
            provider.remote_state = "open"
            before = (spec_dir / "tasks.md").read_bytes()
            conflicts = taskstoissues.detect_conflicts(spec_dir, "github", "owner/repo", provider=provider)
            after = (spec_dir / "tasks.md").read_bytes()
            self.assertEqual(before, after)
            self.assertEqual(conflicts[0]["task_id"], "T-999-01")
            report = (spec_dir / "issue-conflicts.md").read_text(encoding="utf-8")
            self.assertIn("recommended", report.lower())

    def test_path_guard_rejects_non_framework_spec_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host = Path(tmp) / "app" / "specs" / "demo"
            host.mkdir(parents=True)
            (host / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
            with self.assertRaises(taskstoissues.TaskSyncError):
                taskstoissues.ensure_spec_dir(host)

    def test_imports_do_not_use_third_party_tracker_libraries(self) -> None:
        tree = ast.parse(Path(taskstoissues.__file__).read_text(encoding="utf-8"))
        forbidden = {"requests", "httpx", "PyGithub", "github", "azure", "azure-devops"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".", 1)[0]]
            else:
                names = []
            self.assertFalse(forbidden.intersection(names), f"forbidden import: {names}")


if __name__ == "__main__":
    unittest.main()
