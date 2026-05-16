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
    StateBuilderError,
    build,
    load_backlog,
    load_features,
    load_ledger,
    load_roster,
    main,
    parse_args,
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
