#!/usr/bin/env python3
"""Tests for state_builder.py (SDD-002).

Proves AC1-AC8 and AC10 from the validation contract.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Ensure the cli package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cli.state_builder import (
    ABOUT_FALLBACK,
    PROJECT_MISSION,
    PROJECT_SUBTITLE,
    PROJECT_TYPE,
    PROJECT_OWNER,
    PROJECT_STACK,
    BacklogItem,
    Feature,
    LedgerView,
    PIBlock,
    StateBuilderError,
    build,
    build_index,
    detect_current_sprint,
    load_backlog,
    load_decisions,
    load_features,
    load_ledger,
    load_roster,
    load_sprint_goal,
    load_sprint_table,
    main,
    parse_args,
    render_html,
    render_markdown,
)

SCHEMA_SQL = (Path(__file__).resolve().parent.parent / "ledger" / "schema.sql").read_text(
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_sdd_root(tmp_path: Path) -> Path:
    """Create a minimal sdd-root directory structure for testing."""
    sdd = tmp_path / "sdd"
    sdd.mkdir()

    # constitution/roadmap.md (needed by load_pis for PI detection)
    const_dir = sdd / "constitution"
    const_dir.mkdir()
    (const_dir / "roadmap.md").write_text(
        "# Roadmap\n\n"
        "## PI-2: Fleet Maturity and CLI (current)\n\n"
        "- [x] Fleet Ledger v0.1\n"
        "- [ ] state_builder.py\n"
        "- [ ] fleet.py\n",
        encoding="utf-8",
    )

    # specs/
    spec_dir = sdd / "specs" / "2026-05-12-fleet-ledger"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Feature Spec: Fleet Ledger\n\n"
        "- Date: 2026-05-12\n"
        "- Status: Done\n",
        encoding="utf-8",
    )
    (spec_dir / "validation.md").write_text(
        "# Validation\n- [x] item1\n- [x] item2\n", encoding="utf-8"
    )
    (spec_dir / "RETRO.md").write_text("# Retro\nDone.\n", encoding="utf-8")

    spec_dir2 = sdd / "specs" / "2026-05-16-state-builder"
    spec_dir2.mkdir(parents=True)
    (spec_dir2 / "spec.md").write_text(
        "# Feature Spec: state_builder.py\n\n"
        "- Date: 2026-05-16\n"
        "- Status: Draft\n",
        encoding="utf-8",
    )

    # backlog/BACKLOG.md
    backlog_dir = sdd / "backlog"
    backlog_dir.mkdir()
    (backlog_dir / "BACKLOG.md").write_text(
        "# Product Backlog\n\n"
        "## P2 - Should Have\n\n"
        "| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |\n"
        "|----|-------|----------|-------|--------|------------|--------|------|--------|--------|\n"
        "| SDD-002 | state_builder.py | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 Sprint A | Approved |\n"
        "| SDD-003 | fleet.py | P2 | 8 | 3 | 0.8 | 3 | 6.4 | PI-2 Sprint A | Approved |\n"
        "| SDD-004 | qa.py | P2 | 6 | 2 | 0.8 | 2 | 4.8 | PI-2 Sprint B | Approved |\n"
        "\n## P3 - Could Have\n\n"
        "| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |\n"
        "|----|-------|----------|-------|--------|------------|--------|------|--------|--------|\n"
        "| SDD-001 | Dashboard | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design |\n",
        encoding="utf-8",
    )

    # roster/
    roster_dir = sdd / "roster"
    roster_dir.mkdir()
    agents = [
        {"id": "principal-exec", "kind": "principal", "role": "exec", "specialization": None},
        {"id": "principal-arch", "kind": "principal", "role": "arch", "specialization": None},
        {"id": "dev-general", "kind": "generic", "role": "dev", "specialization": None},
        {"id": "qa-general", "kind": "generic", "role": "qa", "specialization": None},
        {"id": "dev-fastapi", "kind": "generic", "role": "dev", "specialization": "fastapi"},
    ]
    (roster_dir / "agents.json").write_text(json.dumps(agents), encoding="utf-8")
    skills = [
        {"id": "s1", "category": "core", "description": "skill 1"},
        {"id": "s2", "category": "core", "description": "skill 2"},
        {"id": "s3", "category": "workflow", "description": "skill 3"},
        {"id": "s4", "category": "domain", "description": "skill 4"},
    ]
    (roster_dir / "skills.json").write_text(json.dumps(skills), encoding="utf-8")

    # exec/ directory
    (sdd / "exec").mkdir()

    # ledger/ directory with fleet.db
    ledger_dir = sdd / "ledger"
    ledger_dir.mkdir()
    db_path = ledger_dir / "fleet.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return sdd


def _seed_dispatches(sdd: Path) -> None:
    """Insert test dispatches into the fleet.db."""
    db_path = sdd / "ledger" / "fleet.db"
    now = datetime.now(timezone.utc)
    old = now - timedelta(hours=30)

    with sqlite3.connect(db_path) as conn:
        # A successful dispatch
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, "
            "task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                old.isoformat(),
                "PI-2",
                "Sprint A",
                "2026-05-12-fleet-ledger",
                "T-001",
                "Implement ledger schema",
                "dev-general",
                "developer",
                "success",
                now.isoformat(),
            ),
        )
        # A stale (stuck) dispatch -- NULL outcome, older than 24h
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, "
            "task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                old.isoformat(),
                "PI-2",
                "Sprint A",
                "2026-05-16-state-builder",
                "T-002",
                "Stuck task example",
                "dev-general",
                "developer",
                None,
                None,
            ),
        )
        # A recent dispatch -- NULL outcome but within 24h (not a blocker)
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, "
            "task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                now.isoformat(),
                "PI-2",
                "Sprint A",
                "2026-05-16-state-builder",
                "T-003",
                "Recent in-progress task",
                "dev-general",
                "developer",
                None,
                None,
            ),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFullBuild:
    """test_full_build_produces_all_sections: proves AC1."""

    def test_full_build_produces_all_sections(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # All 7 sections present
        assert "# Executive State" in state_md
        assert f"Generated date: {today}" in state_md
        assert "## Spec Pipeline" in state_md
        assert "Sprint Plan" in state_md
        assert "## Fleet" in state_md
        assert "## Recently Completed" in state_md
        assert "## Blockers" in state_md

    def test_full_build_surfaces_pending_user_gates(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        gate_feature = sdd / "specs" / "2026-05-16-state-builder"
        (gate_feature / "validation.md").write_text(
            "---\n"
            "id: SDD-GATE-validation\n"
            "type: validation\n"
            "status: active\n"
            "owner: principal-architect\n"
            "updated: 2026-06-08\n"
            "---\n\n"
            "# Validation\n\n"
            "## Required User Gates Declared By This Spec\n\n"
            "| gate_id | gate_type | blocking_scope | approver | evidence_type | evidence_ref | status | next_action |\n"
            "|---------|-----------|----------------|----------|---------------|--------------|--------|-------------|\n"
            "| GATE-001 | `push-approval` | `push` | owner | `owner-quote` |  | pending | Record owner approval before push. |\n",
            encoding="utf-8",
        )

        result = main(["--sdd-root", str(sdd)])

        assert result == 0
        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        state_html = (sdd / "exec" / "state.html").read_text(encoding="utf-8")
        work_index = (sdd / "exec" / "work-index.md").read_text(encoding="utf-8")
        assert "Pending User Gates" in state_md
        assert "GATE-001" in state_md
        assert "push-approval" in state_html
        assert "Generated dashboard state is visibility only, not approval evidence" in state_html
        assert "USER GATES" in work_index
        assert "Record owner approval before push" in work_index
        assert "Milestones" in state_md


class TestRecentlyCompleted:
    """test_recently_completed_from_dispatches: proves AC2."""

    def test_recently_completed_from_dispatches(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "Implement ledger schema" in state_md


class TestBlockers:
    """test_blockers_from_stale_dispatches: proves AC3."""

    def test_blockers_from_stale_dispatches(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        # The stuck task should appear in Blockers
        assert "Stuck task example" in state_md
        # The recent in-progress task should NOT appear in Blockers
        blockers_section = state_md.split("## Blockers")[1].split("## ")[0]
        assert "Recent in-progress task" not in blockers_section


class TestPipeline:
    """test_pipeline_from_spec_dirs: proves AC4."""

    def test_pipeline_from_spec_dirs(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "fleet-ledger" in state_md
        assert "state-builder" in state_md
        # Status values from spec.md should appear
        assert "Done" in state_md
        assert "Draft" in state_md


class TestSprintPlan:
    """test_sprint_plan_from_backlog: proves AC5."""

    def test_sprint_plan_from_backlog(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        # Sprint A and Sprint B items should be grouped
        assert "PI-2 Sprint A" in state_md
        assert "state_builder.py" in state_md
        assert "fleet.py" in state_md
        assert "PI-2 Sprint B" in state_md
        assert "qa.py" in state_md
        # Unscheduled items should NOT appear in sprint plan
        sprint_section = state_md.split("Sprint Plan")[1].split("## Fleet")[0]
        assert "Dashboard" not in sprint_section


class TestFleetCounts:
    """test_fleet_counts_from_roster: proves AC6."""

    def test_fleet_counts_from_roster(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "Principals: 2" in state_md
        assert "Generic workers: 2" in state_md
        assert "Specialists: 1" in state_md
        assert "Skills: 4 across 3 categories" in state_md


class TestDeterministic:
    """test_deterministic_output: proves AC7."""

    def test_deterministic_output(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)

        main(["--sdd-root", str(sdd)])
        run1 = (sdd / "exec" / "state.md").read_text(encoding="utf-8")

        main(["--sdd-root", str(sdd)])
        run2 = (sdd / "exec" / "state.md").read_text(encoding="utf-8")

        assert run1 == run2


class TestStdlibOnly:
    """test_runtime_imports_are_stdlib_only: proves AC8."""

    def test_runtime_imports_are_stdlib_only(self) -> None:
        import ast

        src = (Path(__file__).resolve().parent / "state_builder.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)

        stdlib_modules = {
            "__future__",
            "argparse",
            "dataclasses",
            "datetime",
            "html",
            "http",
            "json",
            "pathlib",
            "re",
            "socket",
            "sqlite3",
            "subprocess",
            "sys",
            "textwrap",
            "os",
            "typing",
            "webbrowser",
            # In-tree sibling module imported via the established sys.path
            # bootstrap (ADR-012 / SDD-FDC-001). Not a third-party dep.
            "schema_lint",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top in stdlib_modules, f"Non-stdlib import: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    assert top in stdlib_modules, f"Non-stdlib import: from {node.module}"


class TestDryRun:
    """test_dry_run_prints_to_stdout: proves AC10."""

    def test_dry_run_prints_to_stdout(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        sdd = _seed_sdd_root(tmp_path)

        result = main(["--sdd-root", str(sdd), "--dry-run"])
        assert result == 0

        captured = capsys.readouterr()
        assert "# Executive State" in captured.out
        # File should NOT have been written
        assert not (sdd / "exec" / "state.md").exists()


# ---------------------------------------------------------------------------
# Edge-case and unit tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Additional edge-case coverage for the validation contract."""

    def test_missing_fleet_db_graceful(self, tmp_path: Path) -> None:
        """Missing fleet.db produces graceful output with empty dispatch sections."""
        sdd = _seed_sdd_root(tmp_path)
        # Remove the db file (ensure no open handles from _seed_sdd_root)
        db_path = sdd / "ledger" / "fleet.db"
        db_path.unlink(missing_ok=True)

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "## Recently Completed" in state_md
        assert "## Blockers" in state_md

    def test_empty_specs_dir(self, tmp_path: Path) -> None:
        """Empty specs/ produces empty pipeline table."""
        sdd = _seed_sdd_root(tmp_path)
        import shutil
        shutil.rmtree(sdd / "specs")
        (sdd / "specs").mkdir()

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "## Spec Pipeline" in state_md

    def test_empty_backlog(self, tmp_path: Path) -> None:
        """Empty backlog produces sprint plan with no items note."""
        sdd = _seed_sdd_root(tmp_path)
        (sdd / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\nNo items.\n", encoding="utf-8"
        )

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "Sprint Plan" in state_md

    def test_invalid_sdd_root(self) -> None:
        """Non-existent --sdd-root produces an error."""
        result = main(["--sdd-root", "/nonexistent/path/to/sdd"])
        assert result != 0

    def test_pi_override(self, tmp_path: Path) -> None:
        """--pi flag overrides the PI label in header."""
        sdd = _seed_sdd_root(tmp_path)

        result = main(["--sdd-root", str(sdd), "--pi", "PI-99"])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert "PI-99" in state_md

    def test_help_flag(self) -> None:
        """--help shows usage."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_parse_args_basic(self) -> None:
        """parse_args handles basic arguments."""
        args = parse_args(["--sdd-root", "/some/path"])
        assert args.sdd_root == "/some/path"
        assert args.dry_run is False
        assert args.pi is None

    def test_parse_args_all_flags(self) -> None:
        """parse_args handles all flags."""
        args = parse_args(["--sdd-root", "/some/path", "--dry-run", "--pi", "PI-3"])
        assert args.sdd_root == "/some/path"
        assert args.dry_run is True
        assert args.pi == "PI-3"

    def test_load_roster_specialist_counting(self, tmp_path: Path) -> None:
        """load_roster correctly counts specialists (generic with specialization)."""
        sdd = _seed_sdd_root(tmp_path)
        roster = load_roster(sdd)
        assert roster["principals"] == 2
        assert roster["generic"] == 2
        assert roster["specialist"] == 1
        assert roster["total_agents"] == 5
        assert roster["total_skills"] == 4
        assert roster["skill_categories"] == 3

    def test_load_ledger_success_and_blockers(self, tmp_path: Path) -> None:
        """load_ledger returns correct success and blocker lists."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        ledger = load_ledger(sdd)
        assert ledger.available is True
        assert len(ledger.recent_success) == 1
        assert ledger.recent_success[0]["task_title"] == "Implement ledger schema"
        assert len(ledger.blockers) == 1
        assert ledger.blockers[0]["task_title"] == "Stuck task example"

    def test_load_features_detects_status(self, tmp_path: Path) -> None:
        """load_features picks up Status line from spec.md files."""
        sdd = _seed_sdd_root(tmp_path)
        features = load_features(sdd)
        names = {f.name: f for f in features}
        assert "fleet-ledger" in names
        assert "state-builder" in names
        # fleet-ledger has Status: Done + RETRO + 100% validation -> DONE
        assert names["fleet-ledger"].stage == "DONE"
        # state-builder has Status: Draft -> SPEC
        assert names["state-builder"].stage == "SPEC"

    def test_load_backlog_parses_items(self, tmp_path: Path) -> None:
        """load_backlog parses RICE table rows correctly."""
        sdd = _seed_sdd_root(tmp_path)
        items = load_backlog(sdd)
        assert len(items) == 4
        sprints = {i.sprint for i in items}
        assert "PI-2 Sprint A" in sprints
        assert "PI-2 Sprint B" in sprints
        assert "Unscheduled" in sprints


# ---------------------------------------------------------------------------
# build-index tests (T-011)
# ---------------------------------------------------------------------------

_INDEX_TEMPLATE = """\
# PI-X -- Test PI

Some intro prose.

## Sprint List

<!-- BEGIN auto-generated:sprints (refreshed by `cli/state_builder.py build-index`) -->
<!-- END auto-generated:sprints -->

## Footer

Human prose that must survive regeneration.
"""


class TestBuildIndexEmpty:
    """build_index on a PI with no sprint folders produces an empty table."""

    def test_empty_pi_produces_empty_table(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-X"
        pi_dir.mkdir(parents=True)
        (pi_dir / "INDEX.md").write_text(_INDEX_TEMPLATE, encoding="utf-8")

        result = build_index(sdd_root=sdd, pi="PI-X", write=True)

        assert result["pi"] == "PI-X"
        assert result["sprints_found"] == 0
        assert result["wrote"] is not None

        updated = (pi_dir / "INDEX.md").read_text(encoding="utf-8")
        # Table header should still be present (even with 0 data rows)
        assert "| Sprint | Title |" in updated
        # No data rows (only header + separator)
        table_lines = [
            ln for ln in result["table_content"].splitlines()
            if ln.startswith("|") and not ln.startswith("| Sprint") and not ln.startswith("|--")
        ]
        assert len(table_lines) == 0


class TestBuildIndexPopulated:
    """build_index with sprint folders and ledger data produces correct rows."""

    def test_populated_pi_with_ledger(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-X"
        pi_dir.mkdir(parents=True)
        (pi_dir / "INDEX.md").write_text(_INDEX_TEMPLATE, encoding="utf-8")

        # Create two sprint folders with SPEC.md
        s1 = pi_dir / "Sprint-1-alpha"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "---\nstatus: In-Flight\n---\n# Sprint 1\n", encoding="utf-8"
        )

        s2 = pi_dir / "Sprint-2-beta"
        s2.mkdir()
        (s2 / "SPEC.md").write_text(
            "---\nstatus: DONE\n---\n# Sprint 2\n", encoding="utf-8"
        )

        # Create a temporary fleet.db with dispatch rows
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE dispatches ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  dispatched_at TEXT NOT NULL,"
            "  pi TEXT NOT NULL,"
            "  sprint TEXT,"
            "  feature_dir TEXT,"
            "  task_id TEXT NOT NULL,"
            "  task_title TEXT NOT NULL,"
            "  agent_id TEXT NOT NULL,"
            "  agent_role TEXT NOT NULL,"
            "  outcome TEXT,"
            "  outcome_at TEXT,"
            "  notes TEXT"
            ")"
        )
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, "
            "task_id, task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (now, "PI-X", "S1", "feat-1", "T-001", "Task A", "dev-1", "dev", "success", now),
        )
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, "
            "task_id, task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (now, "PI-X", "S1", "feat-1", "T-002", "Task B", "dev-1", "dev", "failure", now),
        )
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, "
            "task_id, task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (now, "PI-X", "S2", "feat-2", "T-003", "Task C", "dev-2", "dev", "success", now),
        )
        conn.commit()
        conn.close()

        import gc
        gc.collect()

        result = build_index(sdd_root=sdd, pi="PI-X", write=True)

        assert result["sprints_found"] == 2
        table = result["table_content"]
        # Sprint 1: 2 dispatches, last outcome = failure
        assert "| 1 | Alpha | In-Flight | 2 | failure |" in table
        # Sprint 2: 1 dispatch, last outcome = success
        assert "| 2 | Beta | DONE | 1 | success |" in table

        # Verify the written file has the table
        updated = (pi_dir / "INDEX.md").read_text(encoding="utf-8")
        assert "| 1 | Alpha |" in updated
        assert "| 2 | Beta |" in updated


class TestBuildIndexMarkerPreservation:
    """Running build_index twice preserves human prose outside marker blocks."""

    def test_prose_survives_double_run(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-X"
        pi_dir.mkdir(parents=True)
        (pi_dir / "INDEX.md").write_text(_INDEX_TEMPLATE, encoding="utf-8")

        # Add one sprint folder
        s1 = pi_dir / "Sprint-1-gamma"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "---\nstatus: Proposed\n---\n# Sprint 1\n", encoding="utf-8"
        )

        # First run
        result1 = build_index(sdd_root=sdd, pi="PI-X", write=True)
        content_after_first = (pi_dir / "INDEX.md").read_text(encoding="utf-8")

        # Second run
        result2 = build_index(sdd_root=sdd, pi="PI-X", write=True)
        content_after_second = (pi_dir / "INDEX.md").read_text(encoding="utf-8")

        # Human prose before markers
        assert "Some intro prose." in content_after_second
        # Human prose after markers
        assert "Human prose that must survive regeneration." in content_after_second
        # The two runs produce identical content
        assert content_after_first == content_after_second
        # Table content is stable
        assert result1["table_content"] == result2["table_content"]


# ---------------------------------------------------------------------------
# T-001: load_sprint_table
# ---------------------------------------------------------------------------

class TestLoadSprintTable:
    """Tests for load_sprint_table(sdd_root, pi_name)."""

    def test_returns_empty_list_when_pi_dir_missing(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        result = load_sprint_table(sdd, "PI-99")
        assert result == []

    def test_returns_sprints_with_ledger_data(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        s1 = pi_dir / "Sprint-1-foundation"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "---\nstatus: DONE\n---\n# Sprint 1\n", encoding="utf-8"
        )
        # Create fleet.db with a dispatch for Sprint 1
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, task_id, "
            "task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("2026-06-01T00:00:00Z", "PI-3", "Sprint 1", "feat-dir",
             "T-001", "Task one", "dev-1", "dev", "success", "2026-06-01T01:00:00Z"),
        )
        conn.commit()
        conn.close()

        result = load_sprint_table(sdd, "PI-3")
        assert len(result) == 1
        assert result[0]["dispatch_count"] == 1
        assert result[0]["last_outcome"] == "success"

    def test_returns_sprints_with_no_ledger_data(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        s1 = pi_dir / "Sprint-1-alpha"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "---\nstatus: In-Flight\n---\n# Sprint 1\n", encoding="utf-8"
        )
        result = load_sprint_table(sdd, "PI-3")
        assert len(result) == 1
        assert result[0]["dispatch_count"] == 0
        assert result[0]["last_outcome"] == "--"

    def test_sprints_sorted_by_num_ascending(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        for n, name in [(3, "gamma"), (1, "alpha"), (2, "beta")]:
            s = pi_dir / f"Sprint-{n}-{name}"
            s.mkdir()
            (s / "SPEC.md").write_text(
                f"---\nstatus: Proposed\n---\n# Sprint {n}\n", encoding="utf-8"
            )
        result = load_sprint_table(sdd, "PI-3")
        nums = [s["num"] for s in result]
        assert nums == [1, 2, 3]


# ---------------------------------------------------------------------------
# T-002: load_sprint_goal
# ---------------------------------------------------------------------------

class TestLoadSprintGoal:
    """Tests for load_sprint_goal(sdd_root, pi_name, sprint_num)."""

    def test_returns_fallback_when_spec_missing(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        result = load_sprint_goal(sdd, "PI-3", 1)
        assert result == "No sprint goal defined"

    def test_extracts_goal_from_sprint_goal_heading(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        s1 = pi_dir / "Sprint-1-foundation"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "# Sprint 1\n\n"
            "## 1. Sprint Goal\n\n"
            "Deliver the data layer for the Live UI.\n\n"
            "## 2. Scope\n\nSome scope text.\n",
            encoding="utf-8",
        )
        result = load_sprint_goal(sdd, "PI-3", 1)
        assert result == "Deliver the data layer for the Live UI."

    def test_falls_back_to_first_heading_paragraph(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        s1 = pi_dir / "Sprint-1-foundation"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "# Sprint 1\n\n"
            "## Overview\n\n"
            "This sprint focuses on infrastructure.\n\n"
            "## Details\n\nMore info.\n",
            encoding="utf-8",
        )
        result = load_sprint_goal(sdd, "PI-3", 1)
        assert result == "This sprint focuses on infrastructure."

    def test_returns_fallback_when_no_headings(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        pi_dir = sdd / "docs" / "Management" / "PI-3"
        pi_dir.mkdir(parents=True)
        s1 = pi_dir / "Sprint-1-foundation"
        s1.mkdir()
        (s1 / "SPEC.md").write_text(
            "Just some text without any headings.\n",
            encoding="utf-8",
        )
        result = load_sprint_goal(sdd, "PI-3", 1)
        assert result == "No sprint goal defined"


# ---------------------------------------------------------------------------
# T-003: detect_current_sprint
# ---------------------------------------------------------------------------

class TestDetectCurrentSprint:
    """Tests for detect_current_sprint(sprints)."""

    def test_returns_none_for_empty_list(self) -> None:
        assert detect_current_sprint([]) is None

    def test_returns_first_non_done_non_proposed(self) -> None:
        sprints = [
            {"num": 1, "status": "DONE"},
            {"num": 2, "status": "In-Flight"},
            {"num": 3, "status": "Proposed"},
        ]
        result = detect_current_sprint(sprints)
        assert result["num"] == 2

    def test_returns_first_when_all_done(self) -> None:
        sprints = [
            {"num": 1, "status": "DONE"},
            {"num": 2, "status": "DONE"},
        ]
        result = detect_current_sprint(sprints)
        assert result["num"] == 1

    def test_returns_first_when_all_proposed(self) -> None:
        sprints = [
            {"num": 1, "status": "Proposed"},
            {"num": 2, "status": "Proposed"},
        ]
        result = detect_current_sprint(sprints)
        assert result["num"] == 1

    def test_skips_done_returns_in_flight(self) -> None:
        sprints = [
            {"num": 1, "status": "DONE"},
            {"num": 2, "status": "DONE"},
            {"num": 3, "status": "In-Flight"},
            {"num": 4, "status": "Proposed"},
        ]
        result = detect_current_sprint(sprints)
        assert result["num"] == 3


# ---------------------------------------------------------------------------
# T-004: load_decisions
# ---------------------------------------------------------------------------

class TestLoadDecisions:
    """Tests for load_decisions(sdd_root, limit)."""

    def test_returns_empty_when_db_missing(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        assert load_decisions(sdd) == []

    def test_returns_empty_when_table_missing(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE dummy (id INTEGER)")
        conn.commit()
        conn.close()
        assert load_decisions(sdd) == []

    def test_returns_decisions_ordered_desc(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE decisions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "decided_at TEXT NOT NULL, level INTEGER NOT NULL, "
            "decider TEXT NOT NULL, artifact TEXT, description TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO decisions (decided_at, level, decider, description) "
            "VALUES ('2026-06-01T00:00:00Z', 0, 'dev', 'First decision')"
        )
        conn.execute(
            "INSERT INTO decisions (decided_at, level, decider, description) "
            "VALUES ('2026-06-02T00:00:00Z', 1, 'arch', 'Second decision')"
        )
        conn.commit()
        conn.close()

        result = load_decisions(sdd)
        assert len(result) == 2
        assert result[0]["timestamp"] == "2026-06-02T00:00:00Z"
        assert result[0]["decider"] == "arch"
        assert result[1]["timestamp"] == "2026-06-01T00:00:00Z"

    def test_respects_limit(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE decisions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "decided_at TEXT NOT NULL, level INTEGER NOT NULL, "
            "decider TEXT NOT NULL, artifact TEXT, description TEXT NOT NULL)"
        )
        for i in range(10):
            conn.execute(
                "INSERT INTO decisions (decided_at, level, decider, description) "
                f"VALUES ('2026-06-{i+1:02d}T00:00:00Z', 0, 'dev', 'Decision {i}')"
            )
        conn.commit()
        conn.close()

        result = load_decisions(sdd, limit=3)
        assert len(result) == 3

    def test_default_limit_is_50(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir(parents=True)
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE decisions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "decided_at TEXT NOT NULL, level INTEGER NOT NULL, "
            "decider TEXT NOT NULL, artifact TEXT, description TEXT NOT NULL)"
        )
        for i in range(60):
            conn.execute(
                "INSERT INTO decisions (decided_at, level, decider, description) "
                f"VALUES ('2026-06-{(i % 28)+1:02d}T{i:02d}:00:00Z', 0, 'dev', 'D{i}')"
            )
        conn.commit()
        conn.close()

        result = load_decisions(sdd)
        assert len(result) == 50


# ---------------------------------------------------------------------------
# About-block tests (T-004, V-1 through V-5)
# ---------------------------------------------------------------------------


class TestAboutBlock:
    """Context bar section in the dashboard HTML (mockup lines 1380-1401)."""

    def test_context_bar_project_identity_present(self, tmp_path: Path) -> None:
        """V-1: rendered HTML contains project identity fields from the mockup."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        assert PROJECT_SUBTITLE in htm
        assert PROJECT_TYPE in htm
        assert PROJECT_OWNER in htm
        assert PROJECT_STACK in htm
        assert PROJECT_MISSION in htm

    def test_context_bar_dynamic_focus_reflects_state(self, tmp_path: Path) -> None:
        """V-2: dynamic Focus field includes Current PI."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        # The seeded roadmap has PI-2 (Fleet Maturity and CLI) as current
        assert "PI-2 (Fleet Maturity and CLI)" in htm
        # Sprint label is the static symbolic text
        assert "Symbolic" in htm

    def test_context_bar_dynamic_focus_tracks_header_changes(self, tmp_path: Path) -> None:
        """V-3: different PI data produces different dynamic Focus lines."""
        # Fixture A: PI-2 (default from _seed_sdd_root)
        base_a = tmp_path / "a"
        base_a.mkdir()
        sdd_a = _seed_sdd_root(base_a)
        _seed_dispatches(sdd_a)
        result_a = build(sdd_root=sdd_a, write=False, live_html=False,
                         fixed_date="2026-05-16")

        # Fixture B: PI-7 as current
        sdd_b = tmp_path / "b" / "sdd"
        sdd_b.mkdir(parents=True)
        const_dir = sdd_b / "constitution"
        const_dir.mkdir()
        (const_dir / "roadmap.md").write_text(
            "# Roadmap\n\n"
            "## PI-7: Quantum Leap (current)\n\n"
            "- [ ] quantum module\n",
            encoding="utf-8",
        )
        for d in ("specs", "backlog", "roster", "exec"):
            (sdd_b / d).mkdir(exist_ok=True)
        (sdd_b / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\nEmpty.\n", encoding="utf-8"
        )
        (sdd_b / "roster" / "agents.json").write_text("[]", encoding="utf-8")
        (sdd_b / "roster" / "skills.json").write_text("[]", encoding="utf-8")
        ledger_dir = sdd_b / "ledger"
        ledger_dir.mkdir()
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()

        result_b = build(sdd_root=sdd_b, write=False, live_html=False,
                         fixed_date="2026-05-16")

        htm_a = result_a["html"]
        htm_b = result_b["html"]

        # Fixture A sees PI-2, not PI-7
        assert "PI-2 (Fleet Maturity and CLI)" in htm_a
        assert "PI-7" not in htm_a

        # Fixture B sees PI-7, not PI-2
        assert "PI-7 (Quantum Leap)" in htm_b
        assert "PI-2" not in htm_b

    def test_context_bar_fallback_when_no_pi(self, tmp_path: Path) -> None:
        """V-4: missing PI/sprint/focus degrades to fallback string, no crash."""
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        for d in ("constitution", "specs", "backlog", "roster", "exec"):
            (sdd / d).mkdir(exist_ok=True)
        (sdd / "constitution" / "roadmap.md").write_text(
            "# Roadmap\n\nNothing here.\n", encoding="utf-8"
        )
        (sdd / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\nEmpty.\n", encoding="utf-8"
        )
        (sdd / "roster" / "agents.json").write_text("[]", encoding="utf-8")
        (sdd / "roster" / "skills.json").write_text("[]", encoding="utf-8")
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir()
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()

        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]

        # Project identity still present
        assert PROJECT_SUBTITLE in htm
        # Fallback string used for dynamic focus
        assert ABOUT_FALLBACK in htm
        # No literal 'None' or 'KeyError' leaked
        assert "None" not in htm or "none" in htm.lower()  # allow CSS 'none'
        assert "KeyError" not in htm

    def test_context_bar_appears_before_main_layout(self, tmp_path: Path) -> None:
        """V-5: Context bar is positioned before the main grid container."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        ctx_idx = htm.index("context-section")
        main_idx = htm.index('class="grid-v3"')
        assert ctx_idx < main_idx

    def test_topbar_has_title_and_subtitle(self, tmp_path: Path) -> None:
        """V-6: header has project title and subtitle matching mockup."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        assert 'class="topbar-title"' in htm
        assert "BRIDGE" in htm
        assert 'class="topbar-mission"' in htm
        assert PROJECT_SUBTITLE in htm


# ---------------------------------------------------------------------------
# v3 sprint-first layout tests (T-005..T-011)
# ---------------------------------------------------------------------------


class TestV3Layout:
    """Structural assertions for the v3.0 sprint-first dashboard."""

    def _build(self, tmp_path: Path) -> str:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        return result["html"]

    def test_skip_link_present(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'href="#main"' in htm
        assert 'class="skip-link"' in htm

    def test_top_bar_role_banner_with_brand(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'role="banner"' in htm
        assert "BRIDGE" in htm

    def test_main_has_grid_v3_class(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert '<main id="main" role="main" class="grid-v3">' in htm

    def test_sprint_section_renders_with_heading(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="sprint-heading"' in htm
        assert "class=\"zone-sprint\"" in htm

    def test_next_section_renders_with_heading(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="next-heading"' in htm
        assert "What Comes Next" in htm

    def test_wip_section_uses_9_stage_bars_with_aria(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="wip-heading"' in htm
        # Each stage bar must carry an aria-label for screen readers
        assert 'class="stage-bar"' in htm
        assert 'aria-label=' in htm

    def test_pi_context_uses_details_summary(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="pi-heading"' in htm
        assert "<details" in htm
        assert "<summary>" in htm

    def test_agents_heading_present(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="agents-heading"' in htm
        assert "Fleet -- Agent Traceability" in htm
        # Placeholder text must be gone
        assert "Per-agent real-time visibility planned for PI-5" not in htm

    def test_activity_feed_role_log(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'id="feed-heading"' in htm
        assert 'role="log"' in htm
        assert 'aria-live="off"' in htm
        assert 'tabindex="0"' in htm

    def test_footer_contains_version_and_stdlib(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert 'role="contentinfo"' in htm
        assert "v3.0 (sprint-first)" in htm
        assert "stdlib only" in htm


class TestV3CSS:
    """CSS-level assertions: tokens, breakpoints, motion, accessibility."""

    def _build(self, tmp_path: Path) -> str:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        return result["html"]

    def test_css_includes_design_tokens(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        # Spot-check a representative token from each tier
        assert "--bg-carbon: " in htm or "--bg-carbon:" in htm
        assert "--accent-oxblood:" in htm
        assert "--ink-paper:" in htm
        assert "--color-interactive:" in htm
        assert "--focus-ring:" in htm

    def test_css_grid_areas_define_v3_layout(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        # Desktop grid-template-areas must include "next   wip" together
        # (i.e. the desktop two-column row).  The exact whitespace may vary.
        assert '"next' in htm and 'wip"' in htm
        # Stacked tablet layout has next and wip on separate rows
        assert '"next"' in htm
        assert '"wip"' in htm

    def test_tablet_breakpoint_present(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "max-width: 1279px" in htm

    def test_prefers_reduced_motion_block_present(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "prefers-reduced-motion: reduce" in htm
        assert "transition-duration: 0s" in htm

    def test_feed_max_height_constraint(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "max-height: 480px" in htm

    def test_no_outline_none_in_css(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "outline: none" not in htm
        assert "outline:none" not in htm

    def test_focus_ring_outline_present(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "outline: 2px solid var(--focus-ring)" in htm

    def test_fade_in_animation_on_main(self, tmp_path: Path) -> None:
        htm = self._build(tmp_path)
        assert "@keyframes fade-in" in htm
        assert "animation: fade-in 300ms" in htm


class TestV3EmptyStates:
    """Each v3 section degrades gracefully when its data is missing."""

    def _empty_sdd(self, tmp_path: Path) -> Path:
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        for d in ("constitution", "specs", "backlog", "roster", "exec"):
            (sdd / d).mkdir(exist_ok=True)
        # Empty roadmap -> no PIs at all
        (sdd / "constitution" / "roadmap.md").write_text(
            "# Roadmap\n\nNothing here.\n", encoding="utf-8"
        )
        (sdd / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\nEmpty.\n", encoding="utf-8"
        )
        (sdd / "roster" / "agents.json").write_text("[]", encoding="utf-8")
        (sdd / "roster" / "skills.json").write_text("[]", encoding="utf-8")
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir()
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()
        return sdd

    def test_empty_sprint_renders_empty_state(self, tmp_path: Path) -> None:
        sdd = self._empty_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        assert "No active sprint found" in result["html"]

    def test_empty_features_render_wip_empty_state(self, tmp_path: Path) -> None:
        sdd = self._empty_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        assert "No features registered yet" in result["html"]

    def test_empty_pis_render_pi_empty_state(self, tmp_path: Path) -> None:
        sdd = self._empty_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        assert "No Program Increments found in roadmap" in result["html"]

    def test_empty_feed_renders_feed_empty_state(self, tmp_path: Path) -> None:
        sdd = self._empty_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        assert "No activity recorded yet" in result["html"]


# ---------------------------------------------------------------------------
# T-012: Accessibility Audit
# ---------------------------------------------------------------------------

def _render_html_with_features(**overrides) -> str:
    """Render HTML with realistic defaults; override any kwarg."""
    defaults = dict(
        generated_at="2026-06-02",
        pi=PIBlock(name="PI-4", title="Alpha Release",
                   checkboxes=[(True, "A"), (False, "B")], is_current=True),
        features=[
            Feature(feature_dir=Path("specs/feat-a"), name="feat-a",
                    stage="IMPLEMENT", created="2026-06-01", notes="wip"),
            Feature(feature_dir=Path("specs/feat-b"), name="feat-b",
                    stage="DONE", created="2026-05-01", notes="shipped"),
        ],
        roster={"principals": 4, "generic": 4, "specialist": 1,
                "total_agents": 9, "total_skills": 28, "skill_categories": 5,
                "agents": [
                    {"id": "principal-exec", "kind": "principal", "role": "exec",
                     "specialization": None, "created_at": "2026-05-07",
                     "provenance": None},
                    {"id": "principal-arch", "kind": "principal", "role": "arch",
                     "specialization": None, "created_at": "2026-05-07",
                     "provenance": None},
                    {"id": "dev-general", "kind": "generic", "role": "dev",
                     "specialization": None, "created_at": "2026-05-07",
                     "provenance": None},
                    {"id": "dev-cli-1", "kind": "specialist", "role": "dev",
                     "specialization": "cli", "created_at": "2026-05-16",
                     "provenance": "Promoted from dev-general via /hire specialist."},
                ]},
        ledger=LedgerView(available=True, recent=[
            {"agent_id": "dev-1", "outcome": "success",
             "dispatched_at": "2026-06-01T10:00:00Z",
             "task_id": "T-001", "task_title": "Build widget"}
        ], recent_success=[
            {"agent_id": "dev-1", "outcome": "success",
             "dispatched_at": "2026-06-01T10:00:00Z"}
        ], blockers=None),
        commits=[("abc1234", "feat: add widget", "2 hours ago")],
        next_action=("Write tests", "Coverage gap", None),
        all_pis=[
            PIBlock(name="PI-4", title="Alpha Release",
                    checkboxes=[(True, "A"), (False, "B")], is_current=True),
        ],
        sprint_table=[{"num": 1, "title": "Test Sprint", "status": "Active",
                       "dispatch_count": 3, "last_outcome": "success"}],
        current_sprint={"num": 1, "title": "Test Sprint", "status": "Active",
                        "dispatch_count": 3, "last_outcome": "success"},
        sprint_goal="Deliver the widget feature",
    )
    defaults.update(overrides)
    return render_html(**defaults)


class TestAccessibility:
    """T-012: Accessibility audit -- WCAG structural requirements."""

    def test_single_h1(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        matches = _re.findall(r"<h1[\s>]", htm, _re.IGNORECASE)
        assert len(matches) == 1, f"Expected exactly 1 <h1>, found {len(matches)}"

    def test_section_aria_labelledby(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        sections = _re.findall(r"<section\b[^>]*>", htm)
        assert len(sections) >= 6, f"Expected >= 6 sections, found {len(sections)}"
        for tag in sections:
            assert "aria-labelledby=" in tag or "aria-label=" in tag, (
                f"Section missing aria-labelledby or aria-label: {tag}"
            )

    def test_heading_hierarchy_no_skipped_levels(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        headings = _re.findall(r"<(h[1-6])[\s>]", htm, _re.IGNORECASE)
        levels = [int(h[1]) for h in headings]
        assert levels[0] == 1, "First heading must be h1"
        for i in range(1, len(levels)):
            # Each heading level can be same, lower (back up), or +1 deeper
            assert levels[i] <= levels[i - 1] + 1, (
                f"Skipped heading level: h{levels[i-1]} -> h{levels[i]} "
                f"at position {i}"
            )

    def test_landmark_roles_present(self) -> None:
        htm = _render_html_with_features()
        assert 'role="banner"' in htm, "Missing role=banner on header"
        assert 'role="main"' in htm, "Missing role=main on main"
        assert 'role="contentinfo"' in htm, "Missing role=contentinfo on footer"

    def test_activity_feed_role_log(self) -> None:
        htm = _render_html_with_features()
        assert 'role="log"' in htm, "Activity feed must have role=log"

    def test_skip_to_main_link(self) -> None:
        htm = _render_html_with_features()
        assert 'href="#main"' in htm, "Skip-to-main link missing"
        assert "Skip to main content" in htm

    def test_no_outline_none_in_css(self) -> None:
        htm = _render_html_with_features()
        assert "outline: none" not in htm
        assert "outline:none" not in htm

    def test_swim_lane_aria_label(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        bars = _re.findall(r'class="stage-bar"[^>]*aria-label="([^"]*)"', htm)
        assert len(bars) >= 1, "Expected at least one stage-bar with aria-label"
        for label in bars:
            assert "stage" in label.lower(), (
                f"Swim lane aria-label should describe the stage: {label}"
            )

    def test_freshness_aria_live_polite(self) -> None:
        htm = _render_html_with_features()
        assert 'aria-live="polite"' in htm, (
            "Freshness timestamp must have aria-live=polite"
        )


# ---------------------------------------------------------------------------
# T-013: No-JavaScript and Security Audit
# ---------------------------------------------------------------------------

class TestSecurityAudit:
    """T-013: Security audit -- CSP, no scripts, no external deps."""

    def test_no_script_tags(self) -> None:
        htm = _render_html_with_features()
        assert "<script" not in htm.lower(), "HTML must contain zero <script> tags"

    def test_no_import_in_css(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        style_match = _re.search(r"<style>(.*?)</style>", htm, _re.DOTALL)
        assert style_match, "No <style> block found"
        css = style_match.group(1)
        assert "@import" not in css, "CSS must not contain @import"

    def test_no_external_urls_in_css(self) -> None:
        htm = _render_html_with_features()
        import re as _re
        style_match = _re.search(r"<style>(.*?)</style>", htm, _re.DOTALL)
        assert style_match
        css = style_match.group(1)
        assert "http://" not in css, "CSS must not reference http:// URLs"
        assert "https://" not in css, "CSS must not reference https:// URLs"

    def test_no_link_stylesheet_tags(self) -> None:
        htm = _render_html_with_features()
        assert '<link rel="stylesheet"' not in htm.lower(), (
            "HTML must not contain external stylesheet links"
        )

    def test_csp_meta_tag_present(self) -> None:
        htm = _render_html_with_features()
        assert 'http-equiv="Content-Security-Policy"' in htm, (
            "CSP meta tag missing"
        )
        assert "default-src 'none'" in htm
        assert "style-src 'unsafe-inline'" in htm

    def test_stdlib_only_imports(self) -> None:
        src = Path(__file__).resolve().parent / "state_builder.py"
        text = src.read_text(encoding="utf-8")
        import re as _re
        approved = {
            "argparse", "datetime", "html", "json", "re", "socket",
            "sqlite3", "subprocess", "sys", "webbrowser", "dataclasses",
            "http.server", "http", "pathlib",
            "__future__",
            # In-tree sibling module imported via the established sys.path
            # bootstrap (ADR-012 / SDD-FDC-001). Not a third-party dep.
            "schema_lint",
        }
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                parts = stripped.split()
                mod = parts[1].split(".")[0]
                assert mod in approved, (
                    f"Non-stdlib import detected: {stripped}"
                )


# ---------------------------------------------------------------------------
# T-FDC-02: S1 footprint lock guard (SDD-FDC-001 R5 / AC-5)
#
# These five functions in state_builder.py are LOCKED to commit 257b081
# (re-anchored 2026-06-06 via Article X amendment -- see
# specs/2026-06-04-filesystem-data-contracts/clarification-log.md Q5).
#
# Any change to their source bodies that alters the sha256 of
# inspect.getsource(...) MUST fail this test. Repair: revert the locked
# function to its 257b081 form. Do NOT update the golden hashes without an
# Article X amendment ratified by the owner.
# ---------------------------------------------------------------------------

LOCKED_S1_FUNCTIONS = (
    "render_html",
    "load_sprint_table",
    "load_sprint_goal",
    "detect_current_sprint",
    "load_decisions",
)

GOLDEN_S1_HASHES = {
    "render_html":           "5b41283be94e5db1adfb99692b457d370b84fe100eeda7734c95cafe823a705b",
    "load_sprint_table":     "35ab5ad467970ec88709ef923ac608511d49408d31a7787cf2146fccb0e7248f",
    "load_sprint_goal":      "a50e52427f26b489b98f1030cb99f004127fc177d37dedc8de9c5f3e7de00716",
    "detect_current_sprint": "81af06480d402b032665be3d6a2a34c343be0a7005704dc096d52a7280263311",
    "load_decisions":        "98ba432c79d2a3c6e3c9eb84a69b07ea8af6d7deb7a5cf8fa3245692cd712eaf",
}


class TestS1FootprintLockGuard:
    """R5/AC-5: byte-identity of the five S1 functions vs commit 257b081 goldens."""

    def test_locked_function_set_is_exactly_five(self) -> None:
        # If this assertion ever needs to change, an Article X amendment is required.
        assert len(LOCKED_S1_FUNCTIONS) == 5
        assert set(LOCKED_S1_FUNCTIONS) == set(GOLDEN_S1_HASHES.keys())

    def test_s1_footprint_locked(self) -> None:
        """Each locked function's inspect.getsource sha256 must match its golden hash."""
        import hashlib
        import inspect

        from cli import state_builder as sb

        mismatches: list[str] = []
        for name in LOCKED_S1_FUNCTIONS:
            func = getattr(sb, name, None)
            assert func is not None, (
                f"Locked function '{name}' is missing from state_builder.py. "
                f"This is a contract violation -- restore the function or escalate."
            )
            src = inspect.getsource(func)
            actual = hashlib.sha256(src.encode("utf-8")).hexdigest()
            expected = GOLDEN_S1_HASHES[name]
            if actual != expected:
                mismatches.append(
                    f"{name}: expected sha256 {expected}, got {actual}"
                )

        assert not mismatches, (
            "S1 footprint lock violated -- the following functions drifted from "
            "commit 257b081 goldens:\n  " + "\n  ".join(mismatches) +
            "\nRepair: revert the function body to its 257b081 form. Do NOT update "
            "GOLDEN_S1_HASHES without an Article X amendment + owner ratification."
        )

    def test_footer_stdlib_badge(self) -> None:
        htm = _render_html_with_features()
        assert "stdlib only" in htm, "Footer must contain 'stdlib only' text"


# ---------------------------------------------------------------------------
# T-014: Final Integration
# ---------------------------------------------------------------------------

class TestIntegration:
    """T-014: End-to-end integration tests."""

    def _make_sdd(self, tmp_path: Path) -> Path:
        """Build a complete sdd-root for integration testing."""
        sdd = tmp_path / "sdd"
        sdd.mkdir()

        # constitution/roadmap.md with PI checkboxes
        const_dir = sdd / "constitution"
        const_dir.mkdir()
        (const_dir / "roadmap.md").write_text(
            "# Roadmap\n\n"
            "## PI-3: Live Visualization (current)\n\n"
            "- [x] Build renderer\n"
            "- [ ] Accessibility audit\n"
            "- [ ] Security hardening\n",
            encoding="utf-8",
        )

        # docs/Management/PI-3/Sprint-1-test-sprint/SPEC.md
        sprint_dir = sdd / "docs" / "Management" / "PI-3" / "Sprint-1-test-sprint"
        sprint_dir.mkdir(parents=True)
        (sprint_dir / "SPEC.md").write_text(
            "# Sprint 1: Test Sprint\n\n## Goal\n\nDeliver accessibility audit.\n",
            encoding="utf-8",
        )

        # specs/ with a feature
        spec_dir = sdd / "specs" / "2026-06-01-accessibility"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "# Feature Spec: Accessibility\n\n- Date: 2026-06-01\n- Status: Implement\n",
            encoding="utf-8",
        )

        # backlog
        backlog_dir = sdd / "backlog"
        backlog_dir.mkdir()
        (backlog_dir / "BACKLOG.md").write_text(
            "# Product Backlog\n\nEmpty.\n", encoding="utf-8"
        )

        # roster
        roster_dir = sdd / "roster"
        roster_dir.mkdir()
        agents = [
            {"id": "principal-exec", "kind": "principal", "role": "exec",
             "specialization": None},
            {"id": "dev-general", "kind": "generic", "role": "dev",
             "specialization": None},
        ]
        (roster_dir / "agents.json").write_text(
            json.dumps(agents), encoding="utf-8"
        )
        (roster_dir / "skills.json").write_text(
            json.dumps([{"id": "s1", "category": "core", "description": "skill 1"}]),
            encoding="utf-8",
        )

        # exec
        (sdd / "exec").mkdir()

        # ledger/fleet.db
        ledger_dir = sdd / "ledger"
        ledger_dir.mkdir()
        db_path = ledger_dir / "fleet.db"
        conn = sqlite3.connect(db_path)
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            "INSERT INTO dispatches (dispatched_at, pi, sprint, feature_dir, "
            "task_id, task_title, agent_id, agent_role, outcome, outcome_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "2026-06-01T10:00:00Z", "PI-3", "Sprint 1",
                "2026-06-01-accessibility", "T-012", "Accessibility audit",
                "dev-general", "developer", "success", "2026-06-01T12:00:00Z",
            ),
        )
        conn.commit()
        conn.close()
        return sdd

    def test_full_build_succeeds(self, tmp_path: Path) -> None:
        sdd = self._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=True, live_html=False,
                       fixed_date="2026-06-02")
        assert isinstance(result, dict)
        assert "html" in result
        assert "markdown" in result
        assert len(result["html"]) > 0
        assert len(result["markdown"]) > 0

    def test_html_has_all_seven_sections(self, tmp_path: Path) -> None:
        sdd = self._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-06-02")
        htm = result["html"]
        assert "Current Sprint" in htm or 'id="sprint-heading"' in htm
        assert "What Comes Next" in htm
        assert "WIP Summary" in htm
        assert "PI Context" in htm
        assert "Fleet -- Agent Traceability" in htm
        assert "Activity Feed" in htm
        assert "v3.0 (sprint-first)" in htm

    def test_markdown_seven_section_format(self, tmp_path: Path) -> None:
        sdd = self._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-06-02")
        md = result["markdown"]
        assert "# Executive State" in md
        assert "## Spec Pipeline" in md
        assert "## Sprint Plan" in md
        assert "## Fleet" in md
        assert "## Recently Completed" in md
        assert "## Blockers" in md
        assert "## Next Milestones" in md

    def test_no_script_tags_in_full_build(self, tmp_path: Path) -> None:
        sdd = self._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-06-02")
        assert "<script" not in result["html"].lower()

    def test_test_count_verification(self) -> None:
        src = Path(__file__).resolve()
        text = src.read_text(encoding="utf-8")
        import re as _re
        test_funcs = _re.findall(r"^\s+def (test_\w+)", text, _re.MULTILINE)
        # 69 original + new tests from T-012, T-013, T-014, T-015
        assert len(test_funcs) >= 89, (
            f"Expected >= 89 test functions, found {len(test_funcs)}"
        )


# ---------------------------------------------------------------------------
# T-015: Fleet -- Agent Traceability Section
# ---------------------------------------------------------------------------

class TestAgentLineage:
    """T-015: Fleet -- Agent Traceability section with hierarchy tree and dispatch table."""

    def test_load_roster_returns_agents_list(self, tmp_path: Path) -> None:
        """load_roster returns dict with agents key containing list of dicts."""
        sdd = _seed_sdd_root(tmp_path)
        roster = load_roster(sdd)
        assert "agents" in roster
        assert isinstance(roster["agents"], list)
        assert len(roster["agents"]) == 5
        for agent in roster["agents"]:
            assert "id" in agent
            assert "kind" in agent

    def test_agent_traceability_section_rendered(self, tmp_path: Path) -> None:
        """HTML output contains agent-tree with agent hierarchy."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        assert "Fleet -- Agent Traceability" in htm
        assert "agent-tree" in htm
        # Principals should appear
        assert "principal-exec" in htm
        assert "principal-arch" in htm
        # Workers should appear
        assert "dev-general" in htm

    def test_agent_hierarchy_tree(self) -> None:
        """Agent tree uses .agent-principal spans for principal agents."""
        htm = _render_html_with_features()
        assert "agent-tree" in htm
        assert "agent-principal" in htm
        assert "agent-worker" in htm
        assert "agent-tree-chrome" in htm

    def test_dispatch_chain_table(self) -> None:
        """Recent dispatches table has Task/Chain/Artifact/Status headers."""
        htm = _render_html_with_features()
        assert "dispatch-table" in htm
        assert "<th>Task</th>" in htm
        assert "<th>Chain</th>" in htm
        assert "<th>Artifact</th>" in htm
        assert "<th>Status</th>" in htm
        assert "dispatch-chain" in htm


# ---------------------------------------------------------------------------
# T-016: Project Timeline + Work Index (IDEA 2026-06-03)
# ---------------------------------------------------------------------------


from cli.state_builder import render_work_index  # noqa: E402


class TestProjectTimelineSection:
    """Timeline section renders chronological feature progression."""

    def test_timeline_section_renders_with_css_classes(self) -> None:
        htm = _render_html_with_features(
            backlog=[BacklogItem(pid="B1", title="Future thing", priority="P1",
                                 rice="", sprint="", status="NEW")]
        )
        assert 'class="timeline"' in htm, "Timeline <ol> missing"
        assert "tl-item" in htm, "Timeline item class missing"
        assert "tl-marker" in htm, "Timeline marker class missing"
        assert 'id="timeline-heading"' in htm, "Timeline heading missing"

    def test_timeline_shows_done_and_inflight_markers(self) -> None:
        htm = _render_html_with_features()
        # Defaults include feat-b (DONE) and feat-a (IMPLEMENT, in-flight)
        assert "tl-marker-done" in htm, "DONE marker missing (jade dot)"
        assert "tl-marker-current" in htm, "In-flight marker missing (amber dot)"
        assert "tl-done" in htm and "tl-current" in htm
        # DONE feature name and in-flight feature name both surface
        assert "feat-b" in htm
        assert "feat-a" in htm

    def test_timeline_handles_empty_backlog_without_error(self) -> None:
        # Regression for the NameError fix: render_html must not require backlog
        htm = _render_html_with_features()  # no backlog kwarg
        assert 'id="timeline-heading"' in htm


class TestWorkIndexGeneration:
    """exec/work-index.md is rendered by build() for principal cross-checks."""

    def test_render_work_index_lists_done_features(self) -> None:
        features = [
            Feature(feature_dir=Path("specs/done-one"), name="done-one",
                    stage="DONE", created="2026-05-01", notes=""),
            Feature(feature_dir=Path("specs/wip-one"), name="wip-one",
                    stage="IMPLEMENT", created="2026-06-01", notes=""),
        ]
        backlog = [BacklogItem(pid="B1", title="Queued idea", priority="P2",
                               rice="", sprint="", status="NEW")]
        pi = PIBlock(name="PI-4", title="Alpha Release",
                     checkboxes=[(True, "A")], is_current=True)
        md = render_work_index(generated_date="2026-06-03",
                               features=features, backlog=backlog, pi=pi)
        assert "# Work Index" in md
        assert "## 1. DONE" in md
        assert "done-one" in md, "DONE feature must appear in work-index"
        assert "wip-one" in md, "IN-FLIGHT feature must appear in work-index"
        assert "Queued idea" in md, "QUEUED backlog item must appear"
        assert "PI-4" in md

    def test_build_writes_work_index_file(self, tmp_path: Path) -> None:
        # Reuse the integration fixture to get a full sdd-root
        sdd = TestIntegration()._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=True, live_html=False,
                       fixed_date="2026-06-02")
        assert "work_index" in result, "build() must return work_index payload"
        work_index_path = sdd / "exec" / "work-index.md"
        assert work_index_path.exists(), "exec/work-index.md must be written"
        body = work_index_path.read_text(encoding="utf-8")
        assert "# Work Index" in body
        assert "DONE" in body


# ---------------------------------------------------------------------------
# T-FDC-04 + T-FDC-05: count subcommand (SDD-FDC-001 / R3, R4)
# ---------------------------------------------------------------------------

import subprocess  # noqa: E402  -- used by CLI subprocess tests below

from cli.state_builder import (  # noqa: E402
    build_doc_count,
    build_doc_count_by_sprint,
    render_count_table,
    cmd_count,
)


def _seed_doc_count_root(tmp_path: Path) -> Path:
    """Build a minimal sdd-root with frontmatter-bearing artifacts under
    specs/** and sprints/**.
    """
    sdd = tmp_path / "sdd"
    (sdd / "specs" / "feat-a").mkdir(parents=True)
    (sdd / "specs" / "feat-b").mkdir(parents=True)
    (sdd / "sprints" / "PI-9").mkdir(parents=True)

    def write(path: Path, kind: str, status: str) -> None:
        path.write_text(
            f"---\n"
            f"id: SDD-X-{path.stem}\n"
            f"type: {kind}\n"
            f"status: {status}\n"
            f"owner: principal-test\n"
            f"updated: 2026-06-06\n"
            f"---\n"
            f"# {path.stem}\n",
            encoding="utf-8",
        )

    write(sdd / "specs" / "feat-a" / "spec.md", "spec", "active")
    write(sdd / "specs" / "feat-a" / "plan.md", "plan", "active")
    write(sdd / "specs" / "feat-b" / "spec.md", "spec", "done")
    write(sdd / "sprints" / "PI-9" / "INDEX.md", "index", "active")
    write(sdd / "sprints" / "PI-9" / "retro.md", "retro", "done")

    # Files that should be SKIPPED: template + _-prefixed + bad frontmatter
    (sdd / "sprints" / "lessons-template.md").write_text(
        "# placeholder, intentionally no frontmatter\n", encoding="utf-8"
    )
    (sdd / "specs" / "feat-a" / "_template.md").write_text(
        "# skipped via _-prefix\n", encoding="utf-8"
    )
    (sdd / "specs" / "feat-b" / "scratch.md").write_text(
        "# no frontmatter -- silently skipped by count (lint flags it)\n",
        encoding="utf-8",
    )

    return sdd


class TestBuildDocCount:
    """T-FDC-04 R3 / AC-3: rollup helper contract + invariant."""

    def test_returns_stable_contract_shape(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        assert set(rollup.keys()) == {"by_status", "by_type", "total"}
        assert isinstance(rollup["by_status"], dict)
        assert isinstance(rollup["by_type"], dict)
        assert isinstance(rollup["total"], int)

    def test_invariant_total_equals_both_sums(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        assert rollup["total"] == sum(rollup["by_status"].values())
        assert rollup["total"] == sum(rollup["by_type"].values())

    def test_total_matches_seeded_artifact_count(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        # 5 frontmatter-bearing artifacts; 3 skipped (template, _-prefix, no fm)
        assert rollup["total"] == 5

    def test_zero_count_policy_seeds_all_enum_keys(self, tmp_path: Path) -> None:
        """Every enum key must appear with at least 0 (stable dashboard shape)."""
        from schema_lint import ARTIFACT_STATUS_ENUM, ARTIFACT_TYPE_ENUM
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        for key in ARTIFACT_STATUS_ENUM:
            assert key in rollup["by_status"], f"missing seeded status key: {key}"
        for key in ARTIFACT_TYPE_ENUM:
            assert key in rollup["by_type"], f"missing seeded type key: {key}"

    def test_per_status_counts_correct(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        # active: feat-a/spec + feat-a/plan + PI-9/INDEX = 3
        # done:   feat-b/spec + PI-9/retro = 2
        assert rollup["by_status"]["active"] == 3
        assert rollup["by_status"]["done"] == 2
        assert rollup["by_status"]["blocked"] == 0

    def test_per_type_counts_correct(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        # spec: 2 (feat-a, feat-b)
        # plan: 1
        # index: 1
        # retro: 1
        assert rollup["by_type"]["spec"] == 2
        assert rollup["by_type"]["plan"] == 1
        assert rollup["by_type"]["index"] == 1
        assert rollup["by_type"]["retro"] == 1
        assert rollup["by_type"]["tasks"] == 0

    def test_empty_tree_yields_all_zeros(self, tmp_path: Path) -> None:
        sdd = tmp_path / "empty-sdd"
        (sdd / "specs").mkdir(parents=True)
        (sdd / "sprints").mkdir()
        rollup = build_doc_count(sdd)
        assert rollup["total"] == 0
        assert all(v == 0 for v in rollup["by_status"].values())
        assert all(v == 0 for v in rollup["by_type"].values())

    def test_unparseable_frontmatter_skipped_no_crash(self, tmp_path: Path) -> None:
        sdd = tmp_path / "skip-sdd"
        spec_dir = sdd / "specs" / "x"
        spec_dir.mkdir(parents=True)
        (sdd / "sprints").mkdir()
        (spec_dir / "no-fm.md").write_text("# no frontmatter at all", encoding="utf-8")
        rollup = build_doc_count(sdd)  # must not raise
        assert rollup["total"] == 0

    def test_sprint_filter_narrows_results(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        # Add a second sprint with its own artifacts
        (sdd / "sprints" / "PI-8").mkdir()
        (sdd / "sprints" / "PI-8" / "INDEX.md").write_text(
            "---\nid: idx-pi8\ntype: index\nstatus: archived\nowner: x\nupdated: 2026-06-06\n---\nx\n",
            encoding="utf-8",
        )
        rollup_all = build_doc_count(sdd)
        rollup_pi8 = build_doc_count(sdd, sprint="PI-8")
        rollup_pi9 = build_doc_count(sdd, sprint="PI-9")
        # PI-8: just INDEX (archived). PI-9: INDEX (active) + retro (done) = 2
        assert rollup_pi8["total"] == 1
        assert rollup_pi9["total"] == 2
        # Top-level shape stays the same regardless of filter
        assert set(rollup_pi8.keys()) == set(rollup_all.keys())
        # PI-8 narrowing excludes specs/ artifacts
        assert rollup_pi8["by_type"]["spec"] == 0

    def test_out_of_enum_value_skipped(self, tmp_path: Path) -> None:
        """Lint flags out-of-enum values; count skips them to preserve invariant."""
        sdd = tmp_path / "bad-enum-sdd"
        spec_dir = sdd / "specs" / "x"
        spec_dir.mkdir(parents=True)
        (sdd / "sprints").mkdir()
        (spec_dir / "bad.md").write_text(
            "---\nid: x\ntype: not-a-real-type\nstatus: active\n"
            "owner: x\nupdated: 2026-06-06\n---\nbody\n",
            encoding="utf-8",
        )
        rollup = build_doc_count(sdd)
        assert rollup["total"] == 0
        # Invariant preserved even with out-of-enum input
        assert rollup["total"] == sum(rollup["by_status"].values())
        assert rollup["total"] == sum(rollup["by_type"].values())


class TestBuildDocCountBySprint:
    """T-FDC-04: per-sprint rollup helper."""

    def test_by_sprint_groups_correctly(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        per_sprint = build_doc_count_by_sprint(sdd)
        assert "PI-9" in per_sprint
        assert per_sprint["PI-9"]["total"] == 2

    def test_by_sprint_no_sprints_yields_empty(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd-empty"
        (sdd / "specs").mkdir(parents=True)
        # no sprints/ directory at all
        per_sprint = build_doc_count_by_sprint(sdd)
        assert per_sprint == {}


class TestRenderCountTable:
    """T-FDC-04: human-readable table renderer."""

    def test_table_contains_headers_and_total(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        rollup = build_doc_count(sdd)
        out = render_count_table(rollup)
        assert "BY STATUS" in out
        assert "BY TYPE" in out
        assert "TOTAL: 5" in out

    def test_table_lists_every_seeded_key(self, tmp_path: Path) -> None:
        from schema_lint import ARTIFACT_STATUS_ENUM, ARTIFACT_TYPE_ENUM
        sdd = _seed_doc_count_root(tmp_path)
        out = render_count_table(build_doc_count(sdd))
        for k in ARTIFACT_STATUS_ENUM:
            assert k in out, f"status key '{k}' missing from table"
        for k in ARTIFACT_TYPE_ENUM:
            assert k in out, f"type key '{k}' missing from table"


class TestCountSubcommand:
    """T-FDC-05 R3 / R4 / AC-3 / AC-4: CLI surface."""

    STATE_BUILDER = Path(__file__).resolve().parent / "state_builder.py"

    def test_count_default_json_shape(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        result = subprocess.run(
            [sys.executable, str(self.STATE_BUILDER), "--sdd-root", str(sdd), "count"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert set(payload.keys()) == {"by_status", "by_type", "total"}
        assert payload["total"] == 5
        assert payload["total"] == sum(payload["by_status"].values())
        assert payload["total"] == sum(payload["by_type"].values())

    def test_count_table_format_exits_zero_and_prints(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        result = subprocess.run(
            [sys.executable, str(self.STATE_BUILDER), "--sdd-root", str(sdd),
             "count", "--format", "table"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "BY STATUS" in result.stdout
        assert "BY TYPE" in result.stdout
        assert "TOTAL:" in result.stdout

    def test_count_sprint_filter_narrows_without_changing_top_shape(
        self, tmp_path: Path
    ) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        result = subprocess.run(
            [sys.executable, str(self.STATE_BUILDER), "--sdd-root", str(sdd),
             "count", "--sprint", "PI-9"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert set(payload.keys()) == {"by_status", "by_type", "total"}
        assert payload["total"] == 2  # only sprint artifacts
        assert payload["by_type"]["spec"] == 0  # specs/ excluded

    def test_count_by_sprint_flag_adds_nested_key(self, tmp_path: Path) -> None:
        sdd = _seed_doc_count_root(tmp_path)
        result = subprocess.run(
            [sys.executable, str(self.STATE_BUILDER), "--sdd-root", str(sdd),
             "count", "--by-sprint"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert "by_sprint" in payload
        assert "by_status" in payload  # top-level shape preserved
        assert "by_type" in payload
        assert "total" in payload
        assert "PI-9" in payload["by_sprint"]

    def test_count_no_subparser_breakage_serve_unchanged(self, tmp_path: Path) -> None:
        """Smoke: parser still accepts the legacy `build-index` subparser."""
        result = subprocess.run(
            [sys.executable, str(self.STATE_BUILDER), "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "serve" in result.stdout
        assert "build-index" in result.stdout
        assert "count" in result.stdout

    def test_count_handler_returns_zero(self, tmp_path: Path) -> None:
        """cmd_count returns 0 on success (CLI-PATTERN exit-code contract)."""
        sdd = _seed_doc_count_root(tmp_path)
        ns = argparse.Namespace(format="json", sprint=None, by_sprint=False)
        # Capture stdout to keep test output clean
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_count(ns, sdd)
        assert rc == 0
        payload = json.loads(buf.getvalue())
        assert payload["total"] == 5


import argparse  # noqa: E402  -- used by TestCountSubcommand.test_count_handler_returns_zero

