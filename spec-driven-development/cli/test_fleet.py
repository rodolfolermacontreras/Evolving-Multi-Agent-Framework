"""Acceptance tests for cli/fleet.py (SDD-003).

Covers AC1-AC9 from spec-driven-development/specs/2026-05-16-fleet-cli/spec.md.
AC10 (--help) is validated manually.
"""

from __future__ import annotations

import ast
import gc
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
FLEET_PY = CLI_DIR / "fleet.py"
SCHEMA = SDD_ROOT / "ledger" / "schema.sql"

sys.path.insert(0, str(CLI_DIR))
sys.path.insert(0, str(SDD_ROOT / "ledger"))
import fleet  # noqa: E402


TASKS_MD = """\
| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet Dispatch Eligible | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------------------------|--------|
| T-001 | [S] | Wire the gizmo | `cli/gizmo.py` | Proves AC1 | S | None | AFK | Yes | pending |
| T-002 | [S] | Test the widget | `cli/widget.py` | Validates widget | S | T-001 | AFK | Yes | pending |
| T-003 | [M] | Build the frobulator | `cli/frob.py` | Frobulates correctly | M | None | AFK | No | pending |
"""


def make_env(tmp: Path, tasks_content: str = TASKS_MD):
    """Create (db_path, roster_path, feature_dir) under *tmp*."""
    db = tmp / "fleet.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    roster = tmp / "agents.json"
    roster.write_text(json.dumps([
        {"id": "developer-general", "kind": "generic", "role": "developer"},
        {"id": "qa-engineer-general", "kind": "generic", "role": "qa-engineer"},
    ]), encoding="utf-8")
    feature = tmp / "specs" / "2026-05-16-thingy"
    feature.mkdir(parents=True)
    (feature / "tasks.md").write_text(tasks_content, encoding="utf-8")
    return db, roster, feature


class TestFleetCLI(unittest.TestCase):
    """Acceptance tests for fleet.py (SDD-003)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.db, self.roster, self.feature = make_env(self.tmp)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _dispatch_args(self, tasks="T-001", agent="developer-general"):
        return [
            "dispatch",
            "--feature", str(self.feature),
            "--tasks", tasks,
            "--agent", agent,
            "--pi", "PI-2",
            "--db", str(self.db),
            "--roster", str(self.roster),
        ]

    # ------------------------------------------------------------------ AC1
    def test_dispatch_prints_brief_to_stdout(self):
        """AC1: dispatch prints markdown brief with task ID, description,
        file scope, acceptance test, and agent role."""
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main(self._dispatch_args())
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("Wire the gizmo", out)
        self.assertIn("cli/gizmo.py", out)
        self.assertIn("Proves AC1", out)
        self.assertIn("developer", out)

    # ------------------------------------------------------------------ AC2
    def test_dispatch_writes_ledger_row(self):
        """AC2: dispatch writes a row to fleet.db with correct fields."""
        with redirect_stdout(StringIO()):
            rc = fleet.main(self._dispatch_args())
        self.assertEqual(rc, 0)
        with sqlite3.connect(self.db) as conn:
            conn.row_factory = sqlite3.Row
            rows = list(conn.execute("SELECT * FROM dispatches"))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r["task_id"], "T-001")
        self.assertEqual(r["pi"], "PI-2")
        self.assertEqual(r["agent_id"], "developer-general")
        self.assertEqual(r["agent_role"], "developer")
        self.assertIsNotNone(r["dispatched_at"])
        self.assertIsNotNone(r["feature_dir"])

    # ------------------------------------------------------------------ AC3
    def test_batch_dispatch_multiple_tasks(self):
        """AC3: --tasks T-001,T-002 produces one brief + one row per task."""
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main(self._dispatch_args(tasks="T-001,T-002"))
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("T-002", out)
        self.assertIn("Wire the gizmo", out)
        self.assertIn("Test the widget", out)
        with sqlite3.connect(self.db) as conn:
            rows = conn.execute("SELECT * FROM dispatches ORDER BY id").fetchall()
        self.assertEqual(len(rows), 2)

    # ------------------------------------------------------------------ AC4
    def test_dispatch_saves_briefs_to_output_dir(self):
        """AC4: --output-dir saves briefs as dispatch-<id>-<task_id>.md."""
        out_dir = self.tmp / "briefs"
        out_dir.mkdir()
        with redirect_stdout(StringIO()):
            rc = fleet.main(self._dispatch_args() + ["--output-dir", str(out_dir)])
        self.assertEqual(rc, 0)
        files = sorted(out_dir.iterdir())
        self.assertEqual(len(files), 1)
        f = files[0]
        self.assertTrue(f.name.startswith("dispatch-"), f"unexpected name: {f.name}")
        self.assertIn("T-001", f.name)
        self.assertTrue(f.name.endswith(".md"))
        content = f.read_text(encoding="utf-8")
        self.assertIn("T-001", content)
        self.assertIn("Wire the gizmo", content)

    # ------------------------------------------------------------------ AC5
    def test_mark_outcome_updates_dispatch(self):
        """AC5: mark --dispatch-id <id> --outcome success updates outcome + outcome_at."""
        with redirect_stdout(StringIO()):
            fleet.main(self._dispatch_args())
        with sqlite3.connect(self.db) as conn:
            did = conn.execute("SELECT id FROM dispatches").fetchone()[0]
        with redirect_stdout(StringIO()):
            rc = fleet.main([
                "mark", "--dispatch-id", str(did),
                "--outcome", "success",
                "--db", str(self.db),
            ])
        self.assertEqual(rc, 0)
        with sqlite3.connect(self.db) as conn:
            row = conn.execute(
                "SELECT outcome, outcome_at FROM dispatches WHERE id=?", [did],
            ).fetchone()
        self.assertEqual(row[0], "success")
        self.assertIsNotNone(row[1])

    # ------------------------------------------------------------------ AC6
    def test_status_lists_feature_dispatches(self):
        """AC6: status --feature <dir> lists dispatches in readable table."""
        with redirect_stdout(StringIO()):
            fleet.main(self._dispatch_args())
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main([
                "status",
                "--feature", str(self.feature),
                "--db", str(self.db),
            ])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("T-001", out)
        self.assertIn("developer-general", out)

    # ------------------------------------------------------------------ AC7
    def test_ineligible_task_rejected(self):
        """AC7: task with Fleet Dispatch Eligible = No is rejected with error."""
        buf = StringIO()
        with redirect_stderr(buf):
            rc = fleet.main(self._dispatch_args(tasks="T-003"))
        self.assertNotEqual(rc, 0)
        self.assertIn("not eligible", buf.getvalue().lower())
        # No ledger row should exist
        with sqlite3.connect(self.db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
        self.assertEqual(count, 0)

    # ------------------------------------------------------------------ AC8
    def test_missing_tasks_md_error(self):
        """AC8: missing tasks.md exits with clear error."""
        empty_feature = self.tmp / "no-tasks"
        empty_feature.mkdir()
        buf = StringIO()
        with redirect_stderr(buf):
            rc = fleet.main([
                "dispatch",
                "--feature", str(empty_feature),
                "--tasks", "T-001",
                "--agent", "developer-general",
                "--pi", "PI-2",
                "--db", str(self.db),
                "--roster", str(self.roster),
            ])
        self.assertNotEqual(rc, 0)
        self.assertIn("tasks.md", buf.getvalue())

    # ------------------------------------------------------------------ AC9
    def test_runtime_imports_are_stdlib_only(self):
        """AC9: only stdlib + local ledger modules imported at runtime."""
        tree = ast.parse(FLEET_PY.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        local_ok = {"ledger_cli", "init_ledger", "fleet", "schema_lint"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    self.assertTrue(
                        top in stdlib or top in local_ok,
                        f"non-stdlib/non-local import: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                top = node.module.split(".", 1)[0]
                self.assertTrue(
                    top in stdlib or top in local_ok,
                    f"non-stdlib/non-local import: {node.module}",
                )


# --------------------------------------------------------------------------- #
# SDD-019: Serial Gate Tests
# --------------------------------------------------------------------------- #


def make_spec_dir(parent: Path, name: str, clarify_status: str | None = None,
                  spec_status: str | None = None) -> Path:
    """Create a spec dir with optional clarify.md and spec.md frontmatter."""
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    if clarify_status is not None:
        (d / "clarify.md").write_text(
            f"---\nid: '{name}-clarify'\ntype: clarification\n"
            f"status: {clarify_status}\nowner: pm\nupdated: 2026-06-07\n---\n",
            encoding="utf-8",
        )
    if spec_status is not None:
        (d / "spec.md").write_text(
            f"---\nid: '{name}-spec'\ntype: spec\n"
            f"status: {spec_status}\nowner: arch\nupdated: 2026-06-07\n---\n"
            f"# {name}\n",
            encoding="utf-8",
        )
    return d


class TestScanLockState(unittest.TestCase):
    """SDD-019 R3: lock state derived from frontmatter."""

    def test_scan_lock_state_clarify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-a", clarify_status="draft", spec_status="done")
            state = fleet._scan_lock_state(specs)
            self.assertEqual(state["clarify_holder"], "feat-a")

    def test_scan_lock_state_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-b", clarify_status="done", spec_status="draft")
            state = fleet._scan_lock_state(specs)
            self.assertEqual(state["spec_holder"], "feat-b")
            self.assertIsNone(state["clarify_holder"])

    def test_scan_lock_state_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-c", clarify_status="done", spec_status="done")
            state = fleet._scan_lock_state(specs)
            self.assertIsNone(state["clarify_holder"])
            self.assertIsNone(state["spec_holder"])

    def test_scan_lock_state_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-x", clarify_status="active")
            make_spec_dir(specs, "feat-y", spec_status="draft")
            state = fleet._scan_lock_state(specs)
            self.assertEqual(state["clarify_holder"], "feat-x")
            self.assertEqual(state["spec_holder"], "feat-y")


class TestLockStatusSubcommand(unittest.TestCase):
    """SDD-019 R1: lock status subcommand runs cleanly."""

    def test_lock_status_subcommand(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            rc = fleet.main(["lock", "status"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("CLARIFY lock:", out)
        self.assertIn("SPEC lock:", out)


class TestLockForceRelease(unittest.TestCase):
    """SDD-019 R4: force-release writes ledger row."""

    def test_lock_force_release(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = Path(tmp) / "fleet.db"
            with sqlite3.connect(db) as conn:
                conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            buf = StringIO()
            with redirect_stdout(buf):
                rc = fleet.main([
                    "lock", "force-release", "test-feature",
                    "--reason", "testing force release",
                    "--db", str(db),
                ])
            self.assertEqual(rc, 0)
            self.assertIn("force-released", buf.getvalue())
            with sqlite3.connect(db) as conn:
                rows = conn.execute("SELECT * FROM dispatches WHERE task_id='LOCK-FORCE-RELEASE'").fetchall()
            self.assertEqual(len(rows), 1)


class TestSerialGateBlocks(unittest.TestCase):
    """SDD-019 R1/R6: gate blocks second feature in same phase."""

    def test_gate_blocks_second_clarify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-a", clarify_status="active")
            feat_b = make_spec_dir(specs, "feat-b", clarify_status="active")

            # Monkey-patch SDD_ROOT for this test
            original = fleet.SDD_ROOT
            try:
                fleet.SDD_ROOT = Path(tmp)
                buf = StringIO()
                with redirect_stderr(buf):
                    rc = fleet._check_serial_gate(feat_b, phase="clarify")
                self.assertEqual(rc, 1)
                self.assertIn("feat-a", buf.getvalue())
            finally:
                fleet.SDD_ROOT = original

    def test_gate_allows_post_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            make_spec_dir(specs, "feat-a", clarify_status="active")
            feat_b = make_spec_dir(specs, "feat-b", clarify_status="done", spec_status="active")

            original = fleet.SDD_ROOT
            try:
                fleet.SDD_ROOT = Path(tmp)
                rc = fleet._check_serial_gate(feat_b, phase="implement")
                self.assertEqual(rc, 0)
            finally:
                fleet.SDD_ROOT = original

    def test_gate_allows_same_feature(self) -> None:
        """R6: intra-feature parallel workers proceed."""
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp) / "specs"
            specs.mkdir()
            feat_a = make_spec_dir(specs, "feat-a", clarify_status="active")

            original = fleet.SDD_ROOT
            try:
                fleet.SDD_ROOT = Path(tmp)
                rc = fleet._check_serial_gate(feat_a, phase="clarify")
                self.assertEqual(rc, 0)
            finally:
                fleet.SDD_ROOT = original


# --------------------------------------------------------------------------- #
# SDD-019.R7 -- priority-weighted FIFO queue ordering (SDD-032)
# --------------------------------------------------------------------------- #


class TestQueueOrdering(unittest.TestCase):
    """SDD-019.R7 (SDD-032 R1): priority-weighted FIFO queue."""

    def test_priority_wins(self) -> None:
        """Highest priority queued feature acquires next."""
        entries = [
            ("feat-c", "P3", "2026-06-01"),
            ("feat-a", "P1", "2026-06-09"),  # latest timestamp but highest priority
            ("feat-b", "P2", "2026-06-05"),
        ]
        ordered = fleet._compute_queue_order(entries)
        self.assertEqual([e[0] for e in ordered], ["feat-a", "feat-b", "feat-c"])

    def test_fifo_tiebreak(self) -> None:
        """Equal priorities break ties by earliest updated timestamp (FIFO)."""
        entries = [
            ("feat-late", "P2", "2026-06-09"),
            ("feat-mid", "P2", "2026-06-05"),
            ("feat-early", "P2", "2026-06-01"),
        ]
        ordered = fleet._compute_queue_order(entries)
        self.assertEqual([e[0] for e in ordered], ["feat-early", "feat-mid", "feat-late"])

    def test_empty_queue(self) -> None:
        """Empty input yields empty output (no acquirer)."""
        self.assertEqual(fleet._compute_queue_order([]), [])

    def test_priority_lookup_fallback(self) -> None:
        """Unknown feature_id falls back to P3 (least-urgent default)."""
        with tempfile.TemporaryDirectory() as tmp:
            backlog = Path(tmp) / "BACKLOG.md"
            backlog.write_text(
                "| ID | Title | Priority |\n"
                "|----|-------|----------|\n"
                "| SDD-100 | Known feature | P1 |\n",
                encoding="utf-8",
            )
            self.assertEqual(fleet._lookup_backlog_priority("SDD-100", backlog), "P1")
            self.assertEqual(fleet._lookup_backlog_priority("SDD-999", backlog), "P3")
            self.assertEqual(fleet._lookup_backlog_priority("", backlog), "P3")


# --------------------------------------------------------------------------- #
# SDD-019.R8 -- cutover-commit grandfather migration (SDD-032)
# --------------------------------------------------------------------------- #


def _grandfather_spec_dir(
    parent: Path,
    name: str,
    updated: str,
    *,
    file: str = "clarify.md",
    status: str = "active",
) -> Path:
    """Helper: create a spec dir with a single file carrying *updated* frontmatter."""
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    body = "# stub\n" if file == "spec.md" else ""
    (d / file).write_text(
        f"---\nid: '{name}-stub'\ntype: clarification\n"
        f"status: {status}\nowner: pm\nupdated: {updated}\n---\n{body}",
        encoding="utf-8",
    )
    return d


class TestGrandfather(unittest.TestCase):
    """SDD-019.R8 (SDD-032 R2): cutover-commit grandfather."""

    def test_pre_cutover_not_blocked(self) -> None:
        """Spec dir whose updated date is strictly older than cutover is grandfathered."""
        with tempfile.TemporaryDirectory() as tmp:
            sd = _grandfather_spec_dir(Path(tmp), "feat-old", "2026-06-01")
            self.assertTrue(fleet._is_grandfathered(sd))
            # Custom cutover honored
            self.assertFalse(fleet._is_grandfathered(sd, cutover="2026-05-01"))

    def test_post_cutover_blocked(self) -> None:
        """Spec dir created on/after cutover is NOT grandfathered."""
        with tempfile.TemporaryDirectory() as tmp:
            sd_eq = _grandfather_spec_dir(Path(tmp), "feat-cutover", "2026-06-08")
            self.assertFalse(fleet._is_grandfathered(sd_eq))
            sd_new = _grandfather_spec_dir(Path(tmp), "feat-new", "2026-06-09")
            self.assertFalse(fleet._is_grandfathered(sd_new))

    def test_mixed_pre_and_post(self) -> None:
        """Two spec dirs, one pre and one post -- grandfather is per-dir."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            sd_pre = _grandfather_spec_dir(tmp_p, "feat-pre", "2026-05-15")
            sd_post = _grandfather_spec_dir(tmp_p, "feat-post", "2026-06-09")
            self.assertTrue(fleet._is_grandfathered(sd_pre))
            self.assertFalse(fleet._is_grandfathered(sd_post))
            # Missing dir -> False (not an error)
            missing = tmp_p / "feat-missing"
            self.assertFalse(fleet._is_grandfathered(missing))


# --------------------------------------------------------------------------- #
# SDD-048 C-3 -- config-sourced Article XI cutover (replaces hardcoded date)
# --------------------------------------------------------------------------- #


class TestArticleXICutoverConfig(unittest.TestCase):
    """C-3: cutover resolved from project.config.json with a constant fallback."""

    def _write_config(self, parent: Path, payload: dict) -> Path:
        cfg = parent / "project.config.json"
        cfg.write_text(json.dumps(payload), encoding="utf-8")
        return cfg

    def test_resolve_from_config_field(self) -> None:
        """R-1: a present config field is used verbatim."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._write_config(Path(tmp), {"article_xi_cutover": "2030-01-15"})
            self.assertEqual(fleet._resolve_article_xi_cutover(cfg), "2030-01-15")

    def test_fallback_when_field_absent(self) -> None:
        """R-2: a config lacking the field falls back to the module constant."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self._write_config(Path(tmp), {"owner": "Someone"})
            self.assertEqual(
                fleet._resolve_article_xi_cutover(cfg), fleet.ARTICLE_XI_CUTOVER
            )

    def test_fallback_when_file_missing(self) -> None:
        """R-2: a nonexistent config path falls back to the constant (no crash)."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.json"
            self.assertEqual(
                fleet._resolve_article_xi_cutover(missing), fleet.ARTICLE_XI_CUTOVER
            )

    def test_fallback_when_malformed_json(self) -> None:
        """R-2: malformed JSON falls back to the constant rather than raising."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "project.config.json"
            cfg.write_text("{ not json", encoding="utf-8")
            self.assertEqual(
                fleet._resolve_article_xi_cutover(cfg), fleet.ARTICLE_XI_CUTOVER
            )

    def test_resolved_constant_matches_project_config(self) -> None:
        """R-1: the module-level resolved cutover equals the shipped config value."""
        self.assertEqual(fleet.RESOLVED_ARTICLE_XI_CUTOVER, "2026-06-08")
        self.assertEqual(fleet.ARTICLE_XI_CUTOVER, "2026-06-08")

    def test_grandfather_verdict_unchanged_config_vs_fallback(self) -> None:
        """R-4: config-sourced default and explicit fallback agree on verdicts."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            sd_pre = _grandfather_spec_dir(tmp_p, "feat-pre", "2026-06-01")
            sd_post = _grandfather_spec_dir(tmp_p, "feat-post", "2026-06-09")
            # Default uses config-sourced RESOLVED_ARTICLE_XI_CUTOVER.
            self.assertTrue(fleet._is_grandfathered(sd_pre))
            self.assertFalse(fleet._is_grandfathered(sd_post))
            # Explicit fallback constant -- identical verdicts.
            self.assertEqual(
                fleet._is_grandfathered(sd_pre),
                fleet._is_grandfathered(sd_pre, cutover=fleet.ARTICLE_XI_CUTOVER),
            )
            self.assertEqual(
                fleet._is_grandfathered(sd_post),
                fleet._is_grandfathered(sd_post, cutover=fleet.ARTICLE_XI_CUTOVER),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
