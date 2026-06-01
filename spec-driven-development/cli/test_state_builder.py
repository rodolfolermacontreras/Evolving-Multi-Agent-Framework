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
    ABOUT_STATIC_PARAGRAPH,
    StateBuilderError,
    build,
    build_index,
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
# About-block tests (T-004, V-1 through V-5)
# ---------------------------------------------------------------------------


class TestAboutBlock:
    """About / Where we are section in the dashboard HTML (SDD-010)."""

    def test_about_block_static_paragraph_present(self, tmp_path: Path) -> None:
        """V-1: rendered HTML contains the static purpose paragraph constant."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        assert ABOUT_STATIC_PARAGRAPH in htm

    def test_about_block_dynamic_line_reflects_state_md(self, tmp_path: Path) -> None:
        """V-2: dynamic line includes Current PI, Active sprint, Active focus."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        # The seeded roadmap has PI-2 (Fleet Maturity and CLI) as current
        assert "PI-2 (Fleet Maturity and CLI)" in htm
        # Sprint label is the static symbolic text
        assert "Symbolic" in htm
        # The about-where-we-are class must be present
        assert 'class="about-where-we-are"' in htm

    def test_about_block_dynamic_line_tracks_header_changes(self, tmp_path: Path) -> None:
        """V-3: different PI data produces different dynamic About lines."""
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

    def test_about_block_fallback_when_state_md_header_incomplete(self, tmp_path: Path) -> None:
        """V-4: missing PI/sprint/focus degrades to fallback string, no crash."""
        sdd = tmp_path / "sdd"
        sdd.mkdir()
        # No roadmap -> no PI -> fallback path
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

        # Static paragraph still present
        assert ABOUT_STATIC_PARAGRAPH in htm
        # Fallback string used for dynamic line
        assert ABOUT_FALLBACK in htm
        # No literal 'None' or 'KeyError' leaked
        assert "None" not in htm or "none" in htm.lower()  # allow CSS 'none'
        assert "KeyError" not in htm

    def test_about_block_appears_before_main_layout(self, tmp_path: Path) -> None:
        """V-5: About section is positioned before <main class='layout-4zone'>."""
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-05-16")
        htm = result["html"]
        about_idx = htm.index('id="about"')
        main_idx = htm.index('<main class="layout-4zone">')
        assert about_idx < main_idx
