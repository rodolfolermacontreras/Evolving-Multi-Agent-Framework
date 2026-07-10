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
    current_pi,
    detect_current_sprint,
    derive_next_action,
    load_backlog,
    load_decisions,
    load_features,
    load_ledger,
    load_pis,
    load_roster,
    load_sprint_goal,
    load_sprint_table,
    load_active_sprint_from_current_pi,
    main,
    parse_args,
    render_html,
    render_markdown,
    resolve_display_pi,
    served_html_with_refresh,
    inject_pi_pills_html,
)

# SDD-036: lifecycle pipeline + four-card docs row + reorder control surfaces.
from cli.state_builder import (
    STAGES,
    LIFECYCLE_TOKENS,
    LIFECYCLE_STATE_CLASSES,
    inject_lifecycle_html,
    inject_lifecycle_tokens_html,
    load_display_order,
    order_features_for_display,
    render_docs_row,
    render_lifecycle_pipeline,
    resolve_docs_cards,
    _feature_display_id,
    _sprint_stage,
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
        today = datetime.now().strftime("%Y-%m-%d")

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


class TestActiveFocusHeuristic:
    """SDD-040 R1: current sprint active-focus helper."""

    def _seed_pi6_focus_root(self, tmp_path: Path) -> Path:
        sdd = _seed_sdd_root(tmp_path)

        (sdd / "constitution" / "roadmap.md").write_text(
            "# Roadmap\n\n"
            "## PI-6: Dashboard Reinvestment (current)\n\n"
            "- [ ] Dashboard Parser Fix + Auto-Refresh (SDD-040)\n",
            encoding="utf-8",
        )
        pi_dir = sdd / "sprints" / "PI-6"
        pi_dir.mkdir(parents=True)
        (pi_dir / "CURRENT_PI.md").write_text(
            "# PI-6\n\n"
            "## Sprint Allocation\n\n"
            "| Sprint | Overall | Title | Items |\n"
            "|--------|---------|-------|-------|\n"
            "| PI-6 Sprint 1 | Sprint 10 | Parser fix | SDD-040 |\n"
            "| PI-6 Sprint 2 | Sprint 11 | Lifecycle | SDD-036 |\n",
            encoding="utf-8",
        )
        (sdd / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\n"
            "| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |\n"
            "|----|-------|----------|---|---|---|---|------|--------|--------|-------|\n"
            "| SDD-040 | state_builder.py parser fix + auto-refresh | P1 | H | H | H | S | -- | PI-6 Sprint 10 | Allocated | Anchor |\n"
            "| SDD-036 | lifecycle dashboard | P1 | H | H | M | L | -- | PI-6 Sprint 11 | Planned | Later |\n",
            encoding="utf-8",
        )

        stale = sdd / "specs" / "2026-06-08-azure-decommission"
        stale.mkdir(parents=True)
        (stale / "spec.md").write_text(
            "# Feature Spec: Azure Decommission\n\n- Status: Implementing\n\nSpec ID: SDD-035\n",
            encoding="utf-8",
        )
        (stale / "plan.md").write_text(
            "# Plan\n\nAny later-found reference filed as P3 docs bug (SDD-040+), not a spec re-open.\n",
            encoding="utf-8",
        )
        focused = sdd / "specs" / "2026-06-10-state-builder-fixes"
        focused.mkdir(parents=True)
        (focused / "spec.md").write_text(
            "# Feature Spec: SDD-040 -- state_builder.py parser fix + auto-refresh\n\n"
            "- Status: Approved\n\nSpec ID: SDD-040\n",
            encoding="utf-8",
        )
        (focused / "validation.md").write_text(
            "# Validation\n\n## Required Items\n\n- [ ] **R1 -- Active-focus combination rule.**\n",
            encoding="utf-8",
        )
        return sdd

    def test_scope_guard_prefers_current_sprint_sdd040_over_stale_frontmatter(
        self, tmp_path: Path
    ) -> None:
        sdd = self._seed_pi6_focus_root(tmp_path)
        pi = PIBlock(name="PI-6", title="Dashboard", is_current=True)
        action = derive_next_action(sdd, pi, load_features(sdd))

        assert "SDD-040" in action[0]
        assert "azure" not in action[0].lower()

    def test_prefers_unchecked_required_validation_in_scoped_candidates(
        self, tmp_path: Path
    ) -> None:
        sdd = self._seed_pi6_focus_root(tmp_path)
        second = sdd / "specs" / "2026-06-10-second-current-item"
        second.mkdir(parents=True)
        (second / "spec.md").write_text(
            "# Feature Spec: SDD-041\n\n- Status: Approved\n\nSpec ID: SDD-041\n",
            encoding="utf-8",
        )
        (second / "validation.md").write_text(
            "# Validation\n\n## Required Items\n\n- [ ] **R1 -- Still open.**\n",
            encoding="utf-8",
        )
        focused_validation = sdd / "specs" / "2026-06-10-state-builder-fixes" / "validation.md"
        focused_validation.write_text(
            "# Validation\n\n## Required Items\n\n- [x] **R1 -- Done.**\n",
            encoding="utf-8",
        )
        current_pi = sdd / "sprints" / "PI-6" / "CURRENT_PI.md"
        current_pi.write_text(
            current_pi.read_text(encoding="utf-8").replace("SDD-040", "SDD-040, SDD-041"),
            encoding="utf-8",
        )
        backlog = sdd / "backlog" / "BACKLOG.md"
        backlog.write_text(
            backlog.read_text(encoding="utf-8")
            + "| SDD-041 | second current item | P1 | H | H | H | S | -- | PI-6 Sprint 10 | Allocated | Anchor |\n",
            encoding="utf-8",
        )

        pi = PIBlock(name="PI-6", title="Dashboard", is_current=True)
        action = derive_next_action(sdd, pi, load_features(sdd))

        assert "SDD-041" in action[0]

    def test_git_recency_breaks_ties_with_bounded_subprocess(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sdd = self._seed_pi6_focus_root(tmp_path)
        newer = sdd / "specs" / "2026-06-10-newer-current-item"
        newer.mkdir(parents=True)
        (newer / "spec.md").write_text(
            "# Feature Spec: SDD-041\n\n- Status: Approved\n\nSpec ID: SDD-041\n",
            encoding="utf-8",
        )
        (newer / "validation.md").write_text(
            "# Validation\n\n## Required Items\n\n- [ ] **R1 -- Still open.**\n",
            encoding="utf-8",
        )
        current_pi = sdd / "sprints" / "PI-6" / "CURRENT_PI.md"
        current_pi.write_text(
            current_pi.read_text(encoding="utf-8").replace("SDD-040", "SDD-040, SDD-041"),
            encoding="utf-8",
        )
        backlog = sdd / "backlog" / "BACKLOG.md"
        backlog.write_text(
            backlog.read_text(encoding="utf-8")
            + "| SDD-041 | newer current item | P1 | H | H | H | S | -- | PI-6 Sprint 10 | Allocated | Anchor |\n",
            encoding="utf-8",
        )

        def fake_run(cmd, **kwargs):
            assert cmd[:4] == ["git", "log", "-1", "--format=%ct"]
            assert kwargs["timeout"] <= 2
            path_arg = cmd[-1]
            stamp = "200\n" if "newer-current-item" in path_arg else "100\n"
            return subprocess.CompletedProcess(cmd, 0, stdout=stamp, stderr="")

        monkeypatch.setattr("cli.state_builder.subprocess.run", fake_run)
        pi = PIBlock(name="PI-6", title="Dashboard", is_current=True)
        action = derive_next_action(sdd, pi, load_features(sdd))

        assert "SDD-041" in action[0]

    def test_falls_back_to_existing_chain_when_helper_returns_none(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        pi = PIBlock(
            name="PI-2",
            title="Fleet Maturity and CLI",
            is_current=True,
            checkboxes=[(True, "Fleet Ledger v0.1"), (False, "state_builder.py")],
        )

        action = derive_next_action(sdd, pi, load_features(sdd))

        assert action == (
            "Start: 'state_builder.py'",
            "Highest-priority unstarted commitment in PI-2. Run /clarify to start the lifecycle.",
            "spec-driven-development/constitution/roadmap.md",
        )


class TestSdd042PiLabel:
    """SDD-042: the dashboard header surfaces the ACTIVE sprint PI (from
    sprints/PI-*/CURRENT_PI.md), not the stale roadmap-derived PI."""

    def _seed_roadmap_pi1_to_pi5(self, sdd: Path) -> None:
        (sdd / "constitution" / "roadmap.md").write_text(
            "# Roadmap\n\n"
            "## PI-1: Bootstrap\n\n- [x] item\n\n"
            "## PI-2: Fleet Maturity\n\n- [x] item\n\n"
            "## PI-3: Adoption\n\n- [x] item\n\n"
            "## PI-4: Hardening\n\n- [x] item\n\n"
            "## PI-5: Brownfield Adoption (current)\n\n- [ ] item\n",
            encoding="utf-8",
        )

    def _add_active_pi6(self, sdd: Path, title: str) -> None:
        pi6 = sdd / "sprints" / "PI-6"
        pi6.mkdir(parents=True, exist_ok=True)
        (pi6 / "CURRENT_PI.md").write_text(
            "---\nstatus: active\nsprint: PI-6\n---\n\n"
            f"# PI-6: {title}\n\n- Status: **ACTIVE**\n",
            encoding="utf-8",
        )

    def test_resolve_display_pi_prefers_active_pi6_over_roadmap_pi5(
        self, tmp_path: Path
    ) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        self._add_active_pi6(sdd, "Dashboard Reinvestment + Carryover Cleanup")

        pis = load_pis(sdd)
        pi = resolve_display_pi(sdd, pis)

        assert pi is not None
        assert pi.name == "PI-6"
        assert pi.title == "Dashboard Reinvestment + Carryover Cleanup"

    def test_rendered_state_md_surfaces_active_pi6_not_pi5(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        self._add_active_pi6(sdd, "Dashboard Reinvestment + Carryover Cleanup")

        result = main(["--sdd-root", str(sdd)])
        assert result == 0

        state_md = (sdd / "exec" / "state.md").read_text(encoding="utf-8")
        assert (
            "Current PI: PI-6 (Dashboard Reinvestment + Carryover Cleanup)" in state_md
        )
        assert "Current PI: PI-5" not in state_md

    def test_title_pulled_from_current_pi_h1_when_roadmap_lacks_pi6(
        self, tmp_path: Path
    ) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        self._add_active_pi6(sdd, "Dashboard Reinvestment + Carryover Cleanup")

        pis = load_pis(sdd)
        assert all(block.name != "PI-6" for block in pis)

        pi = resolve_display_pi(sdd, pis)
        assert pi is not None
        assert pi.title == "Dashboard Reinvestment + Carryover Cleanup"
        # Guards against the degenerate "PI-6 ()" label.
        assert pi.title != ""

    def test_h1_trailing_parenthetical_is_stripped(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        self._add_active_pi6(sdd, "Dashboard Reinvestment (Sprint 14 in flight)")

        pis = load_pis(sdd)
        pi = resolve_display_pi(sdd, pis)

        assert pi is not None
        assert pi.title == "Dashboard Reinvestment"

    def test_falls_back_to_current_pi_when_no_active_sprint(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        # No sprints/PI-*/CURRENT_PI.md present -> no ACTIVE sprint.

        pis = load_pis(sdd)
        pi = resolve_display_pi(sdd, pis)
        expected = current_pi(pis)

        assert pi is not None and expected is not None
        assert pi.name == expected.name == "PI-5"

    def test_explicit_override_still_wins_over_active_sprint(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        self._seed_roadmap_pi1_to_pi5(sdd)
        self._add_active_pi6(sdd, "Dashboard Reinvestment + Carryover Cleanup")

        pis = load_pis(sdd)
        pi = resolve_display_pi(sdd, pis, override="PI-99")

        assert pi is not None
        assert pi.name == "PI-99"


class TestServeModeRefresh:
    """SDD-040 R3: served refresh is handler-side and static output stays static."""

    def test_served_html_includes_meta_refresh_with_default_5_seconds(self) -> None:
        htm = served_html_with_refresh(_render_html_with_features(live=True, port=8765), 5)
        assert '<meta http-equiv="refresh" content="5">' in htm
        assert '<meta http-equiv="refresh" content="20">' not in htm

    def test_served_html_uses_refresh_seconds_override(self) -> None:
        htm = served_html_with_refresh(_render_html_with_features(live=True, port=8765), 17)
        assert '<meta http-equiv="refresh" content="17">' in htm

    def test_static_html_written_without_meta_refresh(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        result = main(["--sdd-root", str(sdd)])
        assert result == 0
        htm = (sdd / "exec" / "state.html").read_text(encoding="utf-8")
        assert 'http-equiv="refresh"' not in htm

    def test_served_refresh_adds_no_script_tag(self) -> None:
        htm = served_html_with_refresh(_render_html_with_features(live=True, port=8765), 5)
        assert "<script" not in htm.lower()


class TestRefreshCadenceFlag:
    """SDD-040 R5: serve-only refresh cadence argparse contract."""

    def test_parse_args_serve_refresh_seconds_default_is_5(self) -> None:
        args = parse_args(["serve"])
        assert args.refresh_seconds == 5

    def test_parse_args_serve_refresh_seconds_accepts_positive_integer(self) -> None:
        args = parse_args(["serve", "--refresh-seconds", "12"])
        assert args.refresh_seconds == 12

    def test_parse_args_serve_refresh_seconds_rejects_zero(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["serve", "--refresh-seconds", "0"])
        assert exc_info.value.code == 2

    def test_parse_args_serve_refresh_seconds_rejects_negative(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["serve", "--refresh-seconds", "-1"])
        assert exc_info.value.code == 2


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
            "base64",
            "dataclasses",
            "datetime",
            "hashlib",
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
            # In-tree sibling modules imported via the established sys.path
            # bootstrap (ADR-012 / SDD-FDC-001). Not third-party deps.
            "schema_lint",
            "backlog_reorder",
            "doc_count",
            "dashboard_server",
            "work_index",
            "state_builder_data",
            "state_builder_html",
            "state_builder_markdown",
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
# SDD-057: CURRENT_PI active-sprint source truth (V57-1..V57-3)
# ---------------------------------------------------------------------------


def _write_current_pi(
    sdd: Path, pi_num: int, body: str, *, frontmatter_status: str = "active"
) -> Path:
    path = sdd / "sprints" / f"PI-{pi_num}" / "CURRENT_PI.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"status: {frontmatter_status}\n"
        f"sprint: PI-{pi_num}\n"
        "---\n\n"
        f"# PI-{pi_num}: Test PI\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    return path


class TestLoadActiveSprintFromCurrentPi:
    """V57-1/V57-2: explicit CURRENT_PI marker parsing and rejection."""

    @pytest.mark.parametrize(
        ("body", "expected_num", "expected_title"),
        [
            ("- Status: **ACTIVE; overall Sprint 23 ACTIVE (PI-9 Sprint 2).**", 23, ""),
            ("- Status: **ACTIVE**\n\n### Sprint 4 -- IN-PROGRESS", 4, ""),
            (
                "- Status: **ACTIVE**\n\n## Sprint Allocation\n\n"
                "| Sprint | Overall | Title | Status |\n"
                "|--------|---------|-------|--------|\n"
                "| PI-9 Sprint 2 | Sprint 23 | Dashboard polish | CURRENT |",
                23,
                "Dashboard polish",
            ),
        ],
    )
    def test_accepts_each_explicit_marker_form(
        self, tmp_path: Path, body: str, expected_num: int, expected_title: str
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(sdd, 9, body)

        result = load_active_sprint_from_current_pi(sdd)

        assert result == [{
            "num": expected_num,
            "title": expected_title,
            "status": "ACTIVE",
            "path": "sprints/PI-9/CURRENT_PI.md",
        }]

    def test_highest_active_pi_wins_and_overall_beats_local(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(sdd, 7, "- Status: **ACTIVE; overall Sprint 19 ACTIVE.**")
        _write_current_pi(
            sdd, 9,
            "- Status: **ACTIVE; PI-9 Sprint 2 ACTIVE, overall Sprint 23 ACTIVE.**",
        )
        _write_current_pi(sdd, 10, "- Status: **CLOSED; Sprint 24 DONE.**")

        result = load_active_sprint_from_current_pi(sdd)

        assert result[0]["num"] == 23
        assert result[0]["path"] == "sprints/PI-9/CURRENT_PI.md"

    @pytest.mark.parametrize("frontmatter_status", ["done", "draft"])
    def test_rejects_inactive_frontmatter(
        self, tmp_path: Path, frontmatter_status: str
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(
            sdd, 9, "- Status: **ACTIVE; Sprint 23 ACTIVE.**",
            frontmatter_status=frontmatter_status,
        )
        assert load_active_sprint_from_current_pi(sdd) == []

    def test_rejects_inactive_body_status(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(sdd, 9, "- Status: **PLANNED; Sprint 23 ACTIVE.**")
        assert load_active_sprint_from_current_pi(sdd) == []

    @pytest.mark.parametrize("marker_status", ["CLOSED", "DONE", "PROPOSED"])
    def test_rejects_non_active_sprint_semantics(
        self, tmp_path: Path, marker_status: str
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(
            sdd, 9,
            f"- Status: **ACTIVE**\n\n### Overall Sprint 23 -- {marker_status}",
        )
        assert load_active_sprint_from_current_pi(sdd) == []

    @pytest.mark.parametrize(
        "body",
        [
            "- Status: **ACTIVE**\n\n### Sprint TBD -- ACTIVE",
            "- Status: **ACTIVE**\n\n### Sprint 23.5 -- ACTIVE",
            "- Status: **ACTIVE; overall Sprint 23.5 ACTIVE (PI-9 Sprint 2).**",
            (
                "- Status: **ACTIVE**\n\n## Sprint Allocation\n\n"
                "| Sprint | Overall | Title | Status |\n"
                "|--------|---------|-------|--------|\n"
                "| PI-9 Sprint 2 | Sprint 23.5 | Dashboard polish | CURRENT |"
            ),
            (
                "- Status: **ACTIVE**\n\n## Sprint Allocation\n\n"
                "| Sprint | Overall | Title | Status |\n"
                "|--------|---------|-------|--------|\n"
                "| PI-9 Sprint 2.5 | Sprint 23 | Dashboard polish | CURRENT |"
            ),
            "- Status: **ACTIVE**\n\nNo sprint marker is declared.",
            (
                "- Status: **ACTIVE; overall Sprint 23 ACTIVE.**\n\n"
                "### Overall Sprint 24 -- CURRENT"
            ),
        ],
    )
    def test_rejects_malformed_absent_or_conflicting_marker(
        self, tmp_path: Path, body: str
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(sdd, 9, body)
        assert load_active_sprint_from_current_pi(sdd) == []

    def test_read_error_returns_no_candidate(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sdd = tmp_path / "sdd"
        target = _write_current_pi(
            sdd, 9, "- Status: **ACTIVE; overall Sprint 23 ACTIVE.**"
        )
        original_read_text = Path.read_text

        def unreadable(path: Path, *args, **kwargs):
            if path == target:
                raise OSError("unreadable")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", unreadable)
        assert load_active_sprint_from_current_pi(sdd) == []

    def test_accepts_active_marker_when_same_status_line_mentions_closed_history(
        self, tmp_path: Path
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(
            sdd, 9,
            "- Status: **ACTIVE; Sprint 22 CLOSED; overall Sprint 23 ACTIVE.**",
        )
        assert load_active_sprint_from_current_pi(sdd)[0]["num"] == 23

    @pytest.mark.parametrize(
        "body",
        [
            "- Status: **ACTIVE; overall Sprint 23 NOT ACTIVE.**",
            "- Status: **ACTIVE; Sprint 23 ACTIVE; Sprint 24 CURRENT.**",
            "- Status: **ACTIVE; Sprint 23x ACTIVE.**",
            "- Status: **ACTIVE**\n\n### Sprint 23-alpha -- ACTIVE",
            "- Status: **ACTIVE**\n\n### Sprint 23 -- CLOSED ACTIVE",
            (
                "- Status: **ACTIVE**\n\n## Sprint Allocation\n\n"
                "| Sprint | Overall | Title | Status |\n"
                "|--------|---------|-------|--------|\n"
                "| PI-9 Sprint 2 | Sprint 23 | Current dashboard | PLANNED |"
            ),
            (
                "- Status: **ACTIVE**\n\n## Sprint Allocation\n\n"
                "| Sprint | Overall | Title | Status |\n"
                "|--------|---------|-------|--------|\n"
                "| PI-9 Sprint 2 | Sprint 23 | Dashboard polish | CLOSED ACTIVE |"
            ),
        ],
    )
    def test_rejects_negated_conflicting_malformed_or_non_active_sources(
        self, tmp_path: Path, body: str
    ) -> None:
        sdd = tmp_path / "sdd"
        _write_current_pi(sdd, 9, body)
        assert load_active_sprint_from_current_pi(sdd) == []


class TestActiveSprintBuildIntegration:
    """V57-3: build selects live, legacy fallback, or the existing empty state."""

    def test_build_passes_live_list_and_skips_legacy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from cli import state_builder as sb

        sdd = _seed_sdd_root(tmp_path)
        _write_current_pi(sdd, 9, "- Status: **ACTIVE; overall Sprint 23 ACTIVE.**")
        seen: list[list[dict]] = []
        original_detect = sb.detect_current_sprint

        def detect_spy(sprints: list[dict]) -> dict | None:
            seen.append(sprints)
            return original_detect(sprints)

        def legacy_must_not_run(*args, **kwargs):
            raise AssertionError("legacy loader must not run when live truth exists")

        monkeypatch.setattr(sb, "detect_current_sprint", detect_spy)
        monkeypatch.setattr(sb, "load_sprint_table", legacy_must_not_run)

        result = sb.build(sdd_root=sdd, write=False, fixed_date="2026-07-10")

        assert seen and seen[0][0]["num"] == 23
        assert "Sprint 23" in result["html"]

    @pytest.mark.parametrize("legacy", [
        [{"num": 8, "title": "Legacy", "status": "In-Flight", "path": "legacy"}],
        [],
    ])
    def test_build_uses_legacy_only_when_live_is_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, legacy: list[dict]
    ) -> None:
        from cli import state_builder as sb

        sdd = _seed_sdd_root(tmp_path)
        seen: list[list[dict]] = []
        original_detect = sb.detect_current_sprint

        def detect_spy(sprints: list[dict]) -> dict | None:
            seen.append(sprints)
            return original_detect(sprints)

        monkeypatch.setattr(sb, "detect_current_sprint", detect_spy)
        monkeypatch.setattr(sb, "load_sprint_table", lambda *args, **kwargs: legacy)

        result = sb.build(sdd_root=sdd, write=False, fixed_date="2026-07-10")

        assert seen == [legacy]
        if legacy:
            assert "Sprint 8" in result["html"]
        else:
            assert "No active sprint found." in result["html"]


# ---------------------------------------------------------------------------
# SDD-056: PI pill-nav live truth (V56-1/V56-2)
# ---------------------------------------------------------------------------


class TestInjectPiPillsHtml:
    def test_renders_live_pis_in_numeric_order_with_one_escaped_current(self) -> None:
        source = (
            '<header><nav class="pi-pills" aria-label="Program Increments" '
            'data-owner="render">stale</nav></header>'
        )
        pis = [
            PIBlock(name=f"PI-{num}", title=f"Title {num}", is_current=num == 5)
            for num in range(9, 0, -1)
        ]
        pis[-1] = PIBlock(
            name="PI-1", title='Alpha <beta> & "truth"', is_current=False
        )

        result = inject_pi_pills_html(source, pis=pis, active_pi=pis[0])

        assert result.index(">PI-1<") < result.index(">PI-2<") < result.index(">PI-9<")
        assert all(result.count(f">PI-{num}<") == 1 for num in range(1, 10))
        assert result.count('class="pill current"') == 1
        assert result.count('aria-current="page"') == 1
        assert 'class="pill current" title="Title 9" aria-current="page">PI-9<' in result
        assert 'title="Alpha &lt;beta&gt; &amp; &quot;truth&quot;"' in result
        assert '<nav class="pi-pills" aria-label="Program Increments" data-owner="render">' in result

    def test_missing_nav_or_active_pi_returns_original(self) -> None:
        pis = [PIBlock(name="PI-1", title="One", is_current=False)]
        no_nav = "<header>plain</header>"
        nav = '<nav class="pi-pills" aria-label="Program Increments">old</nav>'

        assert inject_pi_pills_html(no_nav, pis=pis, active_pi=pis[0]) == no_nav
        assert inject_pi_pills_html(nav, pis=pis, active_pi=None) == nav

    def test_second_pass_is_byte_idempotent(self) -> None:
        pis = [
            PIBlock(name="PI-2", title="Two", is_current=True),
            PIBlock(name="PI-1", title="One", is_current=False),
        ]
        source = '<nav class="pi-pills" aria-label="Program Increments">old</nav>'

        once = inject_pi_pills_html(source, pis=pis, active_pi=pis[0])
        twice = inject_pi_pills_html(once, pis=pis, active_pi=pis[0])

        assert twice == once

    def test_build_injects_live_pills_without_writing_source_data(
        self, tmp_path: Path
    ) -> None:
        sdd = _seed_sdd_root(tmp_path)
        roadmap = sdd / "constitution" / "roadmap.md"
        roadmap.write_text(
            "# Roadmap\n\n"
            + "\n".join(
                f"## PI-{num}: Title {num}{' (current)' if num == 5 else ''}\n\n- [x] item\n"
                for num in range(1, 10)
            ),
            encoding="utf-8",
        )
        _write_current_pi(sdd, 9, "- Status: **ACTIVE; overall Sprint 23 ACTIVE.**")
        before = roadmap.read_bytes()

        result = build(sdd_root=sdd, write=False, fixed_date="2026-07-10")

        nav = result["html"].split('<nav class="pi-pills"', 1)[1].split("</nav>", 1)[0]
        assert nav.count('class="pill current"') == 1
        assert 'aria-current="page">PI-9<' in nav
        assert roadmap.read_bytes() == before


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
            "argparse", "base64", "datetime", "hashlib", "html", "json",
            "re", "socket", "sqlite3", "subprocess", "sys", "webbrowser",
            "dataclasses", "http.server", "http", "pathlib",
            "__future__",
            # In-tree sibling modules imported via the established sys.path
            # bootstrap (ADR-012 / SDD-FDC-001). Not third-party deps.
            "schema_lint",
            "backlog_reorder",
            "doc_count",
            "dashboard_server",
            "work_index",
            "state_builder_data",
            "state_builder_html",
            "state_builder_markdown",
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

    def test_single_drag_script_in_full_build(self, tmp_path: Path) -> None:
        # SDD-041 (F-31): the build now emits exactly ONE <script> -- the
        # hash-pinned drag layer -- and only when reorderable lifecycle cards
        # exist. No other inject path emits script markup. (Was previously a
        # zero-script assertion before the additive drag layer landed.)
        sdd = self._make_sdd(tmp_path)
        result = build(sdd_root=sdd, write=False, live_html=False,
                       fixed_date="2026-06-02")
        html_doc = result["html"]
        script_count = html_doc.lower().count("<script")
        has_cards = 'draggable="true"' in html_doc
        assert script_count <= 1, "drag layer must inject at most one <script>"
        assert script_count == (1 if has_cards else 0), (
            f"expected {'1' if has_cards else '0'} script, found {script_count}"
        )

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


# ---------------------------------------------------------------------------
# SDD-036: lifecycle pipeline (AC-1) + four-card docs row (AC-2)
#          + keyboard reorder control (AC-8)
# ---------------------------------------------------------------------------


class TestLifecyclePipeline:
    """AC-1: 9-node horizontal pipeline with current-state emphasis."""

    NODES = ["IDEA", "BACKLOG", "CLARIFY", "SPEC", "PLAN", "TASKS",
             "IMPLEMENT", "REVIEW", "DONE"]

    def test_stages_constant_is_the_nine_ac1_nodes(self) -> None:
        assert list(STAGES) == self.NODES

    def test_pipeline_renders_all_nine_nodes(self) -> None:
        out = render_lifecycle_pipeline("IMPLEMENT")
        for node in self.NODES:
            assert f">{node}</li>" in out
        assert out.count('<li class="pipe-node') == 9

    def test_current_active_feature_emphasis(self) -> None:
        out = render_lifecycle_pipeline("IMPLEMENT")
        # current node carries pipe-current + aria-current
        assert 'pipe-node pipe-current" aria-current="step">IMPLEMENT</li>' in out
        # earlier nodes complete, later nodes outlined
        assert 'pipe-node pipe-complete">SPEC</li>' in out
        assert 'pipe-node pipe-later">DONE</li>' in out

    def test_current_done_feature_marks_all_prior_complete(self) -> None:
        out = render_lifecycle_pipeline("DONE")
        assert 'pipe-node pipe-current" aria-current="step">DONE</li>' in out
        assert 'pipe-node pipe-complete">IDEA</li>' in out
        # nothing after DONE -> no pipe-later
        assert "pipe-later" not in out

    def test_first_node_current_marks_rest_later(self) -> None:
        out = render_lifecycle_pipeline("IDEA")
        assert 'pipe-node pipe-current" aria-current="step">IDEA</li>' in out
        assert "pipe-complete" not in out
        assert 'pipe-node pipe-later">DONE</li>' in out

    def test_unknown_stage_outlines_everything(self) -> None:
        out = render_lifecycle_pipeline("NOPE")
        assert "pipe-current" not in out
        assert "pipe-complete" not in out
        assert out.count("pipe-later") == 9

    def test_sprint_stage_mapping(self) -> None:
        assert _sprint_stage("Active") == "IMPLEMENT"
        assert _sprint_stage("Done") == "DONE"
        assert _sprint_stage("complete") == "DONE"
        assert _sprint_stage("Planned") == "PLAN"
        assert _sprint_stage("Queued") == "BACKLOG"
        assert _sprint_stage("Review") == "REVIEW"
        assert _sprint_stage(None) == "IMPLEMENT"
        assert _sprint_stage("something weird") == "IMPLEMENT"

    def test_sprint_pipeline_uses_mapped_stage(self) -> None:
        out = render_lifecycle_pipeline(_sprint_stage("Active"),
                                        aria_label="Sprint 1 lifecycle")
        assert 'aria-label="Sprint 1 lifecycle"' in out
        assert 'pipe-current" aria-current="step">IMPLEMENT</li>' in out


class TestDocsRow:
    """AC-2: four-card docs row with missing-state handling."""

    def _feature_root(self, tmp_path: Path) -> tuple[Path, Feature]:
        sdd = tmp_path / "sdd"
        (sdd / "constitution").mkdir(parents=True)
        (sdd / "constitution" / "principles.md").write_text("# P", encoding="utf-8")
        feat_dir = sdd / "specs" / "feat-a"
        feat_dir.mkdir(parents=True)
        (feat_dir / "spec.md").write_text("# spec", encoding="utf-8")
        # tasks.md (Sprint) intentionally omitted -> missing card
        (sdd / "docs" / "ADR").mkdir(parents=True)
        feature = Feature(feature_dir=Path("specs/feat-a"), name="feat-a",
                          stage="SPEC", created="2026-06-01")
        return sdd, feature

    def test_resolve_returns_four_cards(self, tmp_path: Path) -> None:
        sdd, feature = self._feature_root(tmp_path)
        cards = resolve_docs_cards(feature, sdd)
        labels = [c[0] for c in cards]
        assert labels == ["Constitution", "Spec", "Sprint", "ADRs"]

    def test_resolved_cards_have_relative_href(self, tmp_path: Path) -> None:
        sdd, feature = self._feature_root(tmp_path)
        cards = dict(resolve_docs_cards(feature, sdd))
        assert cards["Constitution"] == "../constitution/principles.md"
        assert cards["Spec"] == "../specs/feat-a/spec.md"
        assert cards["ADRs"] == "../docs/ADR"

    def test_missing_target_resolves_to_none(self, tmp_path: Path) -> None:
        sdd, feature = self._feature_root(tmp_path)
        cards = dict(resolve_docs_cards(feature, sdd))
        assert cards["Sprint"] is None

    def test_render_row_has_four_cards_one_disabled(self, tmp_path: Path) -> None:
        sdd, feature = self._feature_root(tmp_path)
        out = render_docs_row(feature, sdd)
        # `class="docs-card` prefixes both the 3 anchors and the 1 missing span.
        assert out.count('class="docs-card') == 4
        assert 'aria-disabled="true"' in out
        assert "Sprint (missing)" in out
        # resolved cards are anchors
        assert '<a class="docs-card" href="../specs/feat-a/spec.md">' in out


class TestDisplayOrderOverlay:
    """AC-8: display-order overlay reader + feature ordering."""

    def _features(self) -> list[Feature]:
        return [
            Feature(feature_dir=Path("specs/feat-a"), name="feat-a",
                    stage="IMPLEMENT", created="2026-06-01"),
            Feature(feature_dir=Path("specs/feat-b"), name="feat-b",
                    stage="DONE", created="2026-05-01"),
        ]

    def test_absent_overlay_returns_empty(self, tmp_path: Path) -> None:
        assert load_display_order(tmp_path) == []

    def test_malformed_overlay_returns_empty(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        (tmp_path / "backlog" / "display-order.json").write_text(
            "{ not json", encoding="utf-8")
        assert load_display_order(tmp_path) == []

    def test_valid_overlay_returns_order(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        (tmp_path / "backlog" / "display-order.json").write_text(
            json.dumps({"order": ["feat-b", "feat-a"], "updated": "2026-06-24Z"}),
            encoding="utf-8")
        assert load_display_order(tmp_path) == ["feat-b", "feat-a"]

    def test_no_overlay_yields_natural_order(self, tmp_path: Path) -> None:
        ordered = order_features_for_display(self._features(), tmp_path)
        names = [f.name for _, f in ordered]
        assert names == ["feat-a", "feat-b"]

    def test_overlay_order_respected(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        (tmp_path / "backlog" / "display-order.json").write_text(
            json.dumps({"order": ["feat-b", "feat-a"]}), encoding="utf-8")
        ordered = order_features_for_display(self._features(), tmp_path)
        names = [f.name for _, f in ordered]
        assert names == ["feat-b", "feat-a"]

    def test_overlay_leftover_features_appended(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        # overlay lists only feat-b; feat-a must still appear (no drop)
        (tmp_path / "backlog" / "display-order.json").write_text(
            json.dumps({"order": ["feat-b"]}), encoding="utf-8")
        ordered = order_features_for_display(self._features(), tmp_path)
        names = [f.name for _, f in ordered]
        assert names == ["feat-b", "feat-a"]

    def test_overlay_unknown_id_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        (tmp_path / "backlog" / "display-order.json").write_text(
            json.dumps({"order": ["ghost", "feat-a", "feat-b"]}), encoding="utf-8")
        ordered = order_features_for_display(self._features(), tmp_path)
        names = [f.name for _, f in ordered]
        assert names == ["feat-a", "feat-b"]

    def test_feature_display_id_reads_spec_line(self, tmp_path: Path) -> None:
        feat_dir = tmp_path / "specs" / "feat-x"
        feat_dir.mkdir(parents=True)
        (feat_dir / "spec.md").write_text(
            "# Spec\n\n- Feature ID: SDD-099\n", encoding="utf-8")
        feature = Feature(feature_dir=feat_dir, name="feat-x",
                          stage="SPEC", created="2026-06-01")
        assert _feature_display_id(feature) == "SDD-099"

    def test_feature_display_id_fallbacks_to_dir_name(self, tmp_path: Path) -> None:
        feat_dir = tmp_path / "specs" / "feat-y"
        feat_dir.mkdir(parents=True)
        (feat_dir / "spec.md").write_text("# Spec\n\nNo id here.\n", encoding="utf-8")
        feature = Feature(feature_dir=feat_dir, name="feat-y",
                          stage="SPEC", created="2026-06-01")
        assert _feature_display_id(feature) == "feat-y"


class TestInjectLifecycleHtml:
    """AC-1/AC-2/AC-8: integration of the lifecycle section into the doc."""

    DOC = ('<main id="main" role="main" class="grid-v3">'
           '<section class="zone-next" aria-labelledby="next-heading">'
           '<h2 id="next-heading">What Comes Next</h2></section></main>')

    def _features(self) -> list[Feature]:
        return [
            Feature(feature_dir=Path("specs/feat-a"), name="feat-a",
                    stage="IMPLEMENT", created="2026-06-01"),
            Feature(feature_dir=Path("specs/feat-b"), name="feat-b",
                    stage="DONE", created="2026-05-01"),
        ]

    def test_section_injected_after_main_open(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint={"num": 1, "title": "T", "status": "Active"})
        assert 'class="zone-lifecycle"' in out
        assert "Lifecycle &amp; Docs" in out
        # injected immediately after main open
        marker = '<main id="main" role="main" class="grid-v3">'
        assert out.index(marker) < out.index('class="zone-lifecycle"')

    def test_renders_pipeline_for_active_and_done_feature(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        # active feature current = IMPLEMENT; done feature current = DONE
        assert 'pipe-current" aria-current="step">IMPLEMENT</li>' in out
        assert 'pipe-current" aria-current="step">DONE</li>' in out

    def test_renders_sprint_card(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint={"num": 2, "title": "Build", "status": "Active"})
        assert "Sprint 2 -- Build" in out
        assert 'class="lifecycle-card lifecycle-sprint"' in out

    def test_each_feature_has_docs_row_and_reorder(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        assert out.count('class="docs-row"') == 2
        # SDD-041 rebuild: reorder moved to the dedicated Backlog section; the
        # lifecycle cards are static and carry no reorder control.
        assert 'class="reorder-control"' not in out

    def test_overlay_order_reflected_in_section(self, tmp_path: Path) -> None:
        (tmp_path / "backlog").mkdir()
        (tmp_path / "backlog" / "display-order.json").write_text(
            json.dumps({"order": ["feat-b", "feat-a"]}), encoding="utf-8")
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        # feat-b card appears before feat-a card
        assert out.index("feat-b") < out.index("feat-a")

    def test_empty_features_and_no_sprint_returns_unchanged(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=[], sdd_root=tmp_path, current_sprint=None)
        assert out == self.DOC

    def test_no_script_injected(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint={"num": 1, "title": "T", "status": "Active"})
        assert "<script" not in out.lower()


class TestLifecycleTokensHtml:
    """SDD-038 V38-1..V38-4: semantic tokens and accessible states."""

    TOKENS = {
        "IDEA": "#B39DDB",
        "BACKLOG": "#7FA8C9",
        "CLARIFY": "#58B8B0",
        "SPEC": "#82B57A",
        "PLAN": "#C2A85D",
        "TASKS": "#D48B52",
        "IMPLEMENT": "#D36F86",
        "REVIEW": "#B884C4",
        "DONE": "#6FA37A",
    }

    @staticmethod
    def _relative_luminance(hex_color: str) -> float:
        channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [
            value / 12.92 if value <= 0.04045
            else ((value + 0.055) / 1.055) ** 2.4
            for value in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    @classmethod
    def _contrast(cls, first: str, second: str) -> float:
        lighter, darker = sorted(
            (cls._relative_luminance(first), cls._relative_luminance(second)),
            reverse=True,
        )
        return (lighter + 0.05) / (darker + 0.05)

    def _lifecycle_doc(self) -> str:
        pipelines = "".join(
            '<article class="lifecycle-card">'
            f'<span class="lifecycle-stage">{stage}</span>'
            f'{render_lifecycle_pipeline(stage)}'
            '</article>'
            for stage in STAGES
        )
        return f'<main><section class="zone-lifecycle">{pipelines}</section></main>'

    def test_exact_nine_tokens_and_canonical_state_mapping(self) -> None:
        assert LIFECYCLE_TOKENS == self.TOKENS
        assert LIFECYCLE_STATE_CLASSES == {
            stage: f"lifecycle-state-{stage.lower()}" for stage in self.TOKENS
        }

    def test_every_node_and_current_stage_label_gets_matching_state_class(self) -> None:
        result = inject_lifecycle_tokens_html(self._lifecycle_doc())

        for stage in STAGES:
            state_class = f"lifecycle-state-{stage.lower()}"
            nodes = re.findall(
                rf'<li class="[^"]*\b{state_class}\b[^"]*"[^>]*>{stage}</li>',
                result,
            )
            assert len(nodes) == 9
            assert (
                f'class="lifecycle-stage {state_class}">{stage}</span>' in result
            )
            assert re.search(
                rf'<li class="[^"]*\bpipe-current\b[^"]*\b{state_class}\b[^"]*" '
                rf'aria-current="step">{stage}</li>',
                result,
            )

        assert result.count('aria-current="step"') == 9
        assert all(f'>{stage}</li>' in result for stage in STAGES)

    def test_sprint_status_label_maps_to_pipeline_current_state(self) -> None:
        source = (
            '<section class="zone-lifecycle"><article class="lifecycle-card">'
            '<span class="lifecycle-stage">Active</span>'
            f'{render_lifecycle_pipeline("IMPLEMENT")}</article></section>'
        )

        result = inject_lifecycle_tokens_html(source)

        assert (
            'class="lifecycle-stage lifecycle-state-implement">Active</span>'
            in result
        )
        assert 'aria-current="step">IMPLEMENT</li>' in result

    def test_css_is_injected_once_and_second_pass_is_byte_idempotent(self) -> None:
        once = inject_lifecycle_tokens_html(self._lifecycle_doc())
        twice = inject_lifecycle_tokens_html(once)

        assert once.count('id="sdd-lifecycle-tokens"') == 1
        assert twice == once
        for stage, color in self.TOKENS.items():
            assert once.count(f"--lifecycle-{stage.lower()}:{color}") == 1

    def test_non_lifecycle_html_is_unchanged(self) -> None:
        source = "<main><p>No lifecycle surface.</p></main>"
        assert inject_lifecycle_tokens_html(source) == source

    def test_locked_tokens_meet_wcag_contrast_thresholds(self) -> None:
        surface_ratios = {
            stage: self._contrast(color, "#1C1B18")
            for stage, color in self.TOKENS.items()
        }
        fill_text_ratios = {
            stage: self._contrast(color, "#0A0A0A")
            for stage, color in self.TOKENS.items()
        }

        assert all(ratio >= 4.5 for ratio in surface_ratios.values())
        assert all(ratio >= 3.0 for ratio in surface_ratios.values())
        assert all(ratio >= 4.5 for ratio in fill_text_ratios.values())

    def test_css_preserves_non_color_meaning_and_accessibility_modes(self) -> None:
        result = inject_lifecycle_tokens_html(self._lifecycle_doc())
        token_css = result.split('<style id="sdd-lifecycle-tokens">', 1)[1].split(
            "</style>", 1
        )[0]

        assert "color:#0A0A0A" in token_css
        assert (
            ".zone-lifecycle .pipe-node,.zone-lifecycle .lifecycle-stage{opacity:1}"
            in token_css
        )
        assert "opacity:." not in token_css
        assert (
            ".zone-lifecycle .pipe-current{font-weight:700;"
            "outline:2px solid var(--lifecycle-state);outline-offset:1px}"
            in token_css
        )
        assert (
            ".zone-lifecycle :focus-visible{outline:3px solid "
            "var(--focus-ring,#E8E4D8);outline-offset:3px}"
            in token_css
        )
        assert (
            "@media (max-width:640px){.zone-lifecycle .lifecycle-pipeline{"
            "display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}"
            ".zone-lifecycle .pipe-node{text-align:center;"
            "overflow-wrap:anywhere}}"
            in token_css
        )
        assert (
            "@media (forced-colors:active){"
            ".zone-lifecycle .pipe-node[class*=\"lifecycle-state-\"],"
            ".zone-lifecycle .lifecycle-stage[class*=\"lifecycle-state-\"]{"
            "forced-color-adjust:auto;background:Canvas;color:CanvasText;"
            "border:1px solid CanvasText}"
            ".zone-lifecycle .pipe-current{outline:3px double Highlight}}"
            in token_css
        )

    def test_build_calls_token_injector_immediately_after_lifecycle_injector(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from cli import state_builder as sb

        sdd = _seed_sdd_root(tmp_path)
        calls: list[str] = []

        def lifecycle_spy(html_doc: str, **kwargs) -> str:
            calls.append("lifecycle")
            return html_doc

        def tokens_spy(html_doc: str) -> str:
            calls.append("tokens")
            return html_doc

        monkeypatch.setattr(sb, "inject_lifecycle_html", lifecycle_spy)
        monkeypatch.setattr(sb, "inject_lifecycle_tokens_html", tokens_spy)

        sb.build(sdd_root=sdd, write=False, fixed_date="2026-07-10")

        lifecycle_index = calls.index("lifecycle")
        assert calls[lifecycle_index:lifecycle_index + 2] == ["lifecycle", "tokens"]


# ===========================================================================
# SDD-037 (F-28): Dispatches card + dashboard health pills
# Tests-first. Surfaces are additive, read-only indicators -- never gates,
# never raise, open zero new sqlite connections, emit zero <script> tags.
# ===========================================================================

from cli.state_builder import (  # noqa: E402  -- SDD-037 surfaces under test
    _group_dispatches,
    inject_dispatches_html,
    inject_health_pills_html,
    constitution_semver_status,
    skill_validity_status,
    ledger_reachability_status,
    stale_tracker_status,
)

# Marker doc mirroring the real dashboard <main> open used by the injectors.
_MAIN_DOC = (
    '<main id="main" role="main" class="grid-v3">'
    '<section class="zone-next"><h2>What Comes Next</h2></section></main>'
)


def _grouped_ledger() -> LedgerView:
    """A populated LedgerView with the SDD-037 grouped widening field."""
    return LedgerView(
        recent_success=[],
        blockers=[],
        recent=[{"agent_id": "dev-1", "outcome": "success",
                 "dispatched_at": "2026-06-01T09:00:00Z"}],
        available=True,
        grouped=[
            {"feature_dir": "specs/2026-06-24-alpha", "sprints": [
                {"sprint": "Sprint A", "rows": [
                    {"agent_id": "dev-1", "agent_role": "developer",
                     "task_id": "T-1", "task_title": "Build <widget>",
                     "outcome": "success", "outcome_at": "2026-06-01T10:00:00Z",
                     "dispatched_at": "2026-06-01T09:00:00Z"},
                    {"agent_id": "dev-2", "agent_role": "developer",
                     "task_id": "T-2", "task_title": "Stuck task",
                     "outcome": None, "outcome_at": None,
                     "dispatched_at": "2026-06-01T08:00:00Z"},
                ]},
            ]},
            {"feature_dir": "specs/2026-06-25-beta", "sprints": [
                {"sprint": "Sprint B", "rows": [
                    {"agent_id": "qa-1", "agent_role": "qa",
                     "task_id": "T-9", "task_title": "Validate",
                     "outcome": "success", "outcome_at": "2026-06-02T10:00:00Z",
                     "dispatched_at": "2026-06-02T09:00:00Z"},
                ]},
            ]},
        ],
    )


class TestLedgerGrouping:
    """T-037-02: LedgerView widened additively; grouping by feature_dir -> sprint."""

    def test_ledger_view_has_grouped_field_default_empty(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=False)
        assert lv.grouped == []

    def test_group_dispatches_groups_feature_then_sprint(self) -> None:
        rows = [
            {"feature_dir": "f-a", "sprint": "S1", "agent_id": "d1"},
            {"feature_dir": "f-a", "sprint": "S1", "agent_id": "d2"},
            {"feature_dir": "f-a", "sprint": "S2", "agent_id": "d3"},
            {"feature_dir": "f-b", "sprint": "S1", "agent_id": "d4"},
        ]
        grouped = _group_dispatches(rows)
        assert [g["feature_dir"] for g in grouped] == ["f-a", "f-b"]
        fa = grouped[0]
        assert [s["sprint"] for s in fa["sprints"]] == ["S1", "S2"]
        assert len(fa["sprints"][0]["rows"]) == 2
        assert grouped[1]["sprints"][0]["rows"][0]["agent_id"] == "d4"

    def test_load_ledger_populates_grouped(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        lv = load_ledger(sdd)
        assert lv.available is True
        dirs = {g["feature_dir"] for g in lv.grouped}
        assert "2026-05-12-fleet-ledger" in dirs
        assert "2026-05-16-state-builder" in dirs
        # recent contract preserved (build() uses len(ledger.recent))
        assert isinstance(lv.recent, list)

    def test_load_ledger_unavailable_has_empty_grouped(self, tmp_path: Path) -> None:
        sdd = tmp_path / "empty"
        (sdd / "ledger").mkdir(parents=True)
        lv = load_ledger(sdd)
        assert lv.available is False
        assert lv.grouped == []


class TestInjectDispatchesHtml:
    """T-037-03: grouped dispatches card; empty + disabled states; escaping."""

    def test_card_injected_after_main_marker(self) -> None:
        out = inject_dispatches_html(_MAIN_DOC, ledger=_grouped_ledger(),
                                     sdd_root=Path("."))
        marker = '<main id="main" role="main" class="grid-v3">'
        assert 'class="zone-dispatches"' in out
        assert out.index(marker) < out.index('class="zone-dispatches"')

    def test_card_groups_feature_then_sprint_with_rows(self) -> None:
        out = inject_dispatches_html(_MAIN_DOC, ledger=_grouped_ledger(),
                                     sdd_root=Path("."))
        assert "specs/2026-06-24-alpha" in out
        assert "Sprint A" in out
        assert "dev-1" in out and "developer" in out
        assert "T-1" in out
        # alpha feature group renders before beta group
        assert out.index("2026-06-24-alpha") < out.index("2026-06-25-beta")

    def test_null_outcome_renders_pending(self) -> None:
        out = inject_dispatches_html(_MAIN_DOC, ledger=_grouped_ledger(),
                                     sdd_root=Path("."))
        assert "pending" in out.lower()
        assert "success" in out.lower()

    def test_values_html_escaped(self) -> None:
        out = inject_dispatches_html(_MAIN_DOC, ledger=_grouped_ledger(),
                                     sdd_root=Path("."))
        assert "Build &lt;widget&gt;" in out
        assert "<widget>" not in out

    def test_empty_state_when_reachable_no_rows(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[],
                        available=True, grouped=[])
        out = inject_dispatches_html(_MAIN_DOC, ledger=lv, sdd_root=Path("."))
        assert 'class="zone-dispatches"' in out
        assert "No dispatches recorded yet." in out

    def test_disabled_state_when_unavailable(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[],
                        available=False, grouped=[])
        out = inject_dispatches_html(_MAIN_DOC, ledger=lv, sdd_root=Path("."))
        assert 'class="zone-dispatches"' in out
        assert "unavailable" in out.lower()

    def test_no_script_injected(self) -> None:
        out = inject_dispatches_html(_MAIN_DOC, ledger=_grouped_ledger(),
                                     sdd_root=Path("."))
        assert "<script" not in out.lower()

    def test_never_raises_on_malformed_rows(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True,
                        grouped=[{"feature_dir": "x", "sprints": [
                            {"sprint": "S", "rows": [{}]}]}])
        out = inject_dispatches_html(_MAIN_DOC, ledger=lv, sdd_root=Path("."))
        assert 'class="zone-dispatches"' in out


class TestHealthCheckHelpers:
    """T-037-04: four read-only status helpers; thresholds; degrade-safe; no writes."""

    def _const(self, tmp_path: Path, versions: dict[str, str]) -> Path:
        sdd = tmp_path / "sdd"
        (sdd / "constitution").mkdir(parents=True)
        for fname, ver in versions.items():
            (sdd / "constitution" / fname).write_text(
                f"---\nname: {fname}\nversion: {ver}\n---\n# Body\n",
                encoding="utf-8")
        return sdd

    def test_constitution_green_when_all_quoted_valid(self, tmp_path: Path) -> None:
        sdd = self._const(tmp_path, {"a.md": "'1.0.0'", "b.md": "'2.3.4'"})
        status, _reason, _detail = constitution_semver_status(sdd)
        assert status == "green"

    def test_constitution_yellow_when_unquoted(self, tmp_path: Path) -> None:
        sdd = self._const(tmp_path, {"a.md": "'1.0.0'", "b.md": "1.0.0"})
        status, _reason, detail = constitution_semver_status(sdd)
        assert status == "yellow"
        assert any("b.md" in d for d in detail)

    def test_constitution_red_when_missing_version(self, tmp_path: Path) -> None:
        sdd = tmp_path / "sdd"
        (sdd / "constitution").mkdir(parents=True)
        (sdd / "constitution" / "a.md").write_text(
            "---\nname: a\n---\n# Body\n", encoding="utf-8")
        status, _reason, detail = constitution_semver_status(sdd)
        assert status == "red"
        assert detail

    def test_constitution_never_writes(self, tmp_path: Path) -> None:
        sdd = self._const(tmp_path, {"a.md": "1.0.0"})
        before = (sdd / "constitution" / "a.md").read_text(encoding="utf-8")
        constitution_semver_status(sdd)
        after = (sdd / "constitution" / "a.md").read_text(encoding="utf-8")
        assert before == after

    def test_skill_validity_green_when_no_skills(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        repo.mkdir()
        status, _reason, _detail = skill_validity_status(repo)
        assert status == "green"

    def test_skill_validity_red_on_bad_skill(self, tmp_path: Path) -> None:
        repo = tmp_path / "repo"
        sk = repo / ".github" / "skills" / "my-skill"
        sk.mkdir(parents=True)
        # Missing license + metadata -> check_skill findings
        (sk / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: x\n---\n# Skill\n",
            encoding="utf-8")
        status, _reason, detail = skill_validity_status(repo)
        assert status == "red"
        assert detail

    def test_ledger_reachability_green_when_available(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True)
        status, _reason, _detail = ledger_reachability_status(lv)
        assert status == "green"

    def test_ledger_reachability_red_when_unavailable(self) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=False)
        status, _reason, _detail = ledger_reachability_status(lv)
        assert status == "red"

    def _tracker(self, tmp_path: Path, date_str: str | None) -> Path:
        sdd = tmp_path / "sdd"
        (sdd / "exec").mkdir(parents=True)
        body = "# Progress\n"
        if date_str:
            body += f"## F-99 ({date_str})\n- done\n"
        (sdd / "exec" / "sprint-progress.md").write_text(body, encoding="utf-8")
        return sdd

    def test_stale_tracker_green_at_7_days(self, tmp_path: Path) -> None:
        now = datetime(2026, 6, 30)
        sdd = self._tracker(tmp_path, "2026-06-23")  # exactly 7 days
        status, _reason, _detail = stale_tracker_status(sdd, now=now, stale_days=7)
        assert status == "green"

    def test_stale_tracker_yellow_at_8_days(self, tmp_path: Path) -> None:
        now = datetime(2026, 6, 30)
        sdd = self._tracker(tmp_path, "2026-06-22")  # 8 days
        status, _reason, _detail = stale_tracker_status(sdd, now=now, stale_days=7)
        assert status == "yellow"

    def test_stale_tracker_yellow_at_14_days(self, tmp_path: Path) -> None:
        now = datetime(2026, 6, 30)
        sdd = self._tracker(tmp_path, "2026-06-16")  # 14 days
        status, _reason, _detail = stale_tracker_status(sdd, now=now, stale_days=7)
        assert status == "yellow"

    def test_stale_tracker_red_at_15_days(self, tmp_path: Path) -> None:
        now = datetime(2026, 6, 30)
        sdd = self._tracker(tmp_path, "2026-06-15")  # 15 days
        status, _reason, _detail = stale_tracker_status(sdd, now=now, stale_days=7)
        assert status == "red"

    def test_stale_tracker_yellow_when_undatable(self, tmp_path: Path) -> None:
        now = datetime(2026, 6, 30)
        sdd = self._tracker(tmp_path, None)
        status, _reason, _detail = stale_tracker_status(sdd, now=now, stale_days=7)
        assert status == "yellow"

    def test_helpers_degrade_safe_on_missing_paths(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope"
        # None of these may raise on a non-existent sdd/repo root.
        constitution_semver_status(missing)
        skill_validity_status(missing)
        stale_tracker_status(missing, now=datetime(2026, 6, 30))


class TestInjectHealthPillsHtml:
    """T-037-05: exactly four pills; colours; server-side anchors for non-green."""

    def _green_sdd(self, tmp_path: Path) -> Path:
        sdd = tmp_path / "sdd"
        (sdd / "constitution").mkdir(parents=True)
        (sdd / "constitution" / "a.md").write_text(
            "---\nname: a\nversion: '1.0.0'\n---\n# B\n", encoding="utf-8")
        (sdd / "exec").mkdir()
        (sdd / "exec" / "sprint-progress.md").write_text(
            "# P\n## F (2026-06-29)\n- x\n", encoding="utf-8")
        return sdd

    def test_exactly_four_pills(self, tmp_path: Path) -> None:
        sdd = self._green_sdd(tmp_path)
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=sdd, ledger=lv, now=datetime(2026, 6, 30))
        assert out.count('class="pill') == 4

    def test_pills_injected_after_main_marker(self, tmp_path: Path) -> None:
        sdd = self._green_sdd(tmp_path)
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=sdd, ledger=lv, now=datetime(2026, 6, 30))
        marker = '<main id="main" role="main" class="grid-v3">'
        assert out.index(marker) < out.index('class="zone-health"')

    def test_all_green_has_no_anchor_links(self, tmp_path: Path) -> None:
        sdd = self._green_sdd(tmp_path)
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=sdd, ledger=lv, now=datetime(2026, 6, 30))
        assert "#health-detail-" not in out

    def test_non_green_pill_links_to_detail_section(self, tmp_path: Path) -> None:
        sdd = self._green_sdd(tmp_path)
        # Unavailable ledger -> reachability pill red -> anchor + detail.
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=False)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=sdd, ledger=lv, now=datetime(2026, 6, 30))
        assert 'href="#health-detail-ledger"' in out
        assert 'id="health-detail-ledger"' in out

    def test_no_script_injected(self, tmp_path: Path) -> None:
        sdd = self._green_sdd(tmp_path)
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=False)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=sdd, ledger=lv, now=datetime(2026, 6, 30))
        assert "<script" not in out.lower()

    def test_never_raises_when_paths_missing(self, tmp_path: Path) -> None:
        lv = LedgerView(recent_success=[], blockers=[], recent=[], available=True)
        out = inject_health_pills_html(
            _MAIN_DOC, sdd_root=tmp_path / "nope", ledger=lv,
            now=datetime(2026, 6, 30))
        assert 'class="zone-health"' in out


class TestSdd037NoNewConnections:
    """T-037-02/AC-4: the new surfaces open ZERO sqlite connections."""

    def test_new_surfaces_open_no_connections(self, tmp_path: Path, monkeypatch) -> None:
        import cli.state_builder as sb
        calls = {"n": 0}
        real = sqlite3.connect

        def counting(*a, **k):
            calls["n"] += 1
            return real(*a, **k)

        monkeypatch.setattr(sb.sqlite3, "connect", counting)

        sdd = self._green(tmp_path)
        lv = _grouped_ledger()
        sb.inject_dispatches_html(_MAIN_DOC, ledger=lv, sdd_root=sdd)
        sb.inject_health_pills_html(_MAIN_DOC, sdd_root=sdd, ledger=lv,
                                    now=datetime(2026, 6, 30))
        sb.constitution_semver_status(sdd)
        sb.skill_validity_status(sdd.parent)
        sb.ledger_reachability_status(lv)
        sb.stale_tracker_status(sdd, now=datetime(2026, 6, 30))
        assert calls["n"] == 0

    def test_load_ledger_opens_exactly_one_connection(
            self, tmp_path: Path, monkeypatch) -> None:
        import cli.state_builder as sb
        calls = {"n": 0}
        real = sqlite3.connect

        def counting(*a, **k):
            calls["n"] += 1
            return real(*a, **k)

        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        monkeypatch.setattr(sb.sqlite3, "connect", counting)
        sb.load_ledger(sdd)
        assert calls["n"] == 1

    def _green(self, tmp_path: Path) -> Path:
        sdd = tmp_path / "sdd"
        (sdd / "constitution").mkdir(parents=True)
        (sdd / "constitution" / "a.md").write_text(
            "---\nname: a\nversion: '1.0.0'\n---\n# B\n", encoding="utf-8")
        (sdd / "exec").mkdir()
        (sdd / "exec" / "sprint-progress.md").write_text(
            "# P\n## F (2026-06-29)\n- x\n", encoding="utf-8")
        return sdd


class TestSdd037IndicatorsNotGates:
    """T-037-06: Q-F/FR-14/R-12 -- health checks never raise, never gate build()."""

    def test_build_succeeds_with_unreachable_ledger(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        # Remove the ledger db so reachability pill goes red -- build must still pass.
        (sdd / "ledger" / "fleet.db").unlink()
        result = build(sdd_root=sdd, write=False)
        assert "html" in result
        assert 'class="zone-health"' in result["html"]

    def test_full_build_has_dispatches_card_and_pills(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False)
        htm = result["html"]
        assert 'class="zone-dispatches"' in htm
        assert 'class="zone-health"' in htm
        # The four-pill invariant is scoped to the health strip. The PI
        # top-bar reuses a plain `class="pill"`; health pills are uniquely
        # `class="pill pill-<color>"`, so count those to isolate the strip.
        assert htm.count('class="pill pill-') == 4

    def test_build_html_has_single_drag_script_tag(self, tmp_path: Path) -> None:
        # SDD-037 surfaces (dispatches card + health pills) remain script-free.
        # The only <script> in a full build is the additive SDD-041 (F-31) drag
        # layer, injected last by inject_drag_html.
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False)
        html_doc = result["html"]
        assert html_doc.lower().count("<script") == 1
        assert "fetch('/reorder'" in html_doc

    def test_dispatches_result_key_unchanged(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        _seed_dispatches(sdd)
        result = build(sdd_root=sdd, write=False)
        lv = load_ledger(sdd)
        assert result["dispatches"] == len(lv.recent)


# ===========================================================================
# SDD-041 (F-31): true browser drag-and-drop reorder
# Rebuild: the drag surface and reorder buttons live in the dedicated Backlog
# section (inject_backlog_reorder_html), keyed by canonical SDD-xxx ids -- the
# exact ids the POST /reorder endpoint accepts. The lifecycle cards are now
# static. Force is never auto-applied by a drag/button gesture (ADR-017 /
# ADR-019).
# ===========================================================================

import io  # noqa: E402
import re  # noqa: E402

import cli.state_builder as _sb  # noqa: E402  -- module handle for monkeypatch
from cli.state_builder import (  # noqa: E402
    DashboardHandler,
    Feature,
    handle_reorder_request,
    inject_backlog_reorder_html,
    inject_drag_html,
    inject_lifecycle_html,
    _DRAG_SCRIPT_BODY,
    _DRAG_SCRIPT_CSP,
)
from cli.backlog_reorder import load_order  # noqa: E402

# handle_reorder_request now lives in the dashboard_server sibling (SDD-048
# C1-E2). Patch its source module -- the bare module the facade re-exports
# from -- not the facade ("patch at source, not import site").
import sys as _sys  # noqa: E402
_ds = _sys.modules[handle_reorder_request.__module__]  # noqa: E402


class TestSdd041DragAffordance:
    """AC: lifecycle cards are static; the drag surface is the Backlog section."""

    DOC = ('<main id="main" role="main" class="grid-v3">'
           '<section class="zone-next"><h2>Next</h2></section></main>')

    def _features(self) -> list[Feature]:
        return [
            Feature(feature_dir=Path("specs/feat-a"), name="feat-a",
                    stage="IMPLEMENT", created="2026-06-01"),
            Feature(feature_dir=Path("specs/feat-b"), name="feat-b",
                    stage="DONE", created="2026-05-01"),
        ]

    def test_feature_cards_are_draggable(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        # SDD-041 rebuild: lifecycle cards no longer drag (the Backlog section
        # owns the SDD-xxx-keyed drag surface). Cards must be static here.
        assert 'draggable="true"' not in out
        assert 'class="drag-handle"' not in out
        assert 'data-pid="' not in out

    def test_keyboard_reorder_control_survives(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        # SDD-041 rebuild: the lifecycle reorder control is retired; reorder is
        # the Backlog section's job.
        assert 'class="reorder-control"' not in out
        assert "reorder-btn" not in out

    def test_lifecycle_injector_stays_script_free(self, tmp_path: Path) -> None:
        out = inject_lifecycle_html(
            self.DOC, features=self._features(), sdd_root=tmp_path,
            current_sprint=None)
        assert "<script" not in out.lower()


class TestSdd041DragScript:
    """AC: exactly one hash-pinned script; CSP widened only for it; inert static."""

    _CARD_DOC = (
        '<html><head>'
        '<meta http-equiv="Content-Security-Policy" '
        'content="default-src \'none\'; style-src \'unsafe-inline\'; img-src \'self\'">'
        '</head><body>'
        '<article class="lifecycle-card" draggable="true" data-pid="SDD-041" '
        'data-rank="0">x</article>'
        '</body></html>'
    )

    def test_injects_exactly_one_script(self) -> None:
        out = inject_drag_html(self._CARD_DOC)
        assert out.lower().count("<script") == 1

    def test_widens_csp_with_script_hash_and_connect(self) -> None:
        out = inject_drag_html(self._CARD_DOC)
        assert "script-src 'sha256-" in out
        assert "connect-src 'self'" in out
        # never relaxes to unsafe-inline scripts
        assert "script-src 'unsafe-inline'" not in out

    def test_csp_hash_matches_script_body(self) -> None:
        import base64
        import hashlib
        digest = base64.b64encode(
            hashlib.sha256(_DRAG_SCRIPT_BODY.encode("utf-8")).digest()
        ).decode("ascii")
        assert _DRAG_SCRIPT_CSP == f"'sha256-{digest}'"

    def test_script_guarded_to_http_only(self) -> None:
        # Static file:// state.html stays inert -- the handler no-ops unless
        # served over http(s).
        assert "location.protocol!=='http:'" in _DRAG_SCRIPT_BODY
        assert "location.protocol!=='https:'" in _DRAG_SCRIPT_BODY

    def test_script_never_sends_force(self) -> None:
        # ADR-017: a drag gesture must never force past a dependency lock. The
        # POST body carries only {item, to_rank} -- no force key. (The word
        # "force" appears only in the user-facing rejection hint text.)
        assert "JSON.stringify({item:item,to_rank:toRank})" in _DRAG_SCRIPT_BODY
        assert "force:" not in _DRAG_SCRIPT_BODY

    def test_noop_without_draggable_cards(self) -> None:
        plain = "<html><body><p>no cards</p></body></html>"
        assert inject_drag_html(plain) == plain


def test_repo_backlog_has_no_cross_project_iai_ids() -> None:
    """Change 1: insights_ai (IAI-xx) rows must not contaminate the SDD backlog.

    The framework backlog is SDD-only; cross-project intake belongs in its own
    project, not here. This guard reads the real repo BACKLOG.md.
    """
    backlog = Path(__file__).resolve().parent.parent / "backlog" / "BACKLOG.md"
    text = backlog.read_text(encoding="utf-8")
    assert "IAI-" not in text
    assert "insights_ai" not in text


class TestSdd041BacklogReorderSection:
    """AC (rebuild): the Backlog section is the real, working reorder surface.

    DA-Evidence Discipline: every claim below is tied to the production
    pipeline -- the ids rendered into the section are fed straight into the
    real ``handle_reorder_request`` (no monkeypatch), and we read the audit /
    display-order artefacts off disk to prove the write happened.
    """

    _OPEN_ROW = re.compile(
        r'<div class="backlog-row" draggable="true" '
        r'data-pid="([A-Z]+-\d+)" data-rank="(\d+)"'
    )
    _DONE_ROW = re.compile(
        r'<div class="backlog-row backlog-done" data-pid="([A-Z]+-\d+)"'
    )

    def _build_html(self, sdd: Path) -> str:
        return _sb.build(sdd_root=sdd, write=False)["html"]

    def test_section_heading_present(self, tmp_path: Path) -> None:
        html_doc = self._build_html(_seed_sdd_root(tmp_path))
        assert 'id="backlog-reorder-heading"' in html_doc
        assert "Backlog" in html_doc

    def test_rendered_ids_are_accepted_by_the_real_endpoint(
            self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        html_doc = self._build_html(sdd)
        rows = self._OPEN_ROW.findall(html_doc)
        # The seed backlog has 4 OPEN SDD-xxx items -> 4 draggable rows.
        assert len(rows) == 4
        order = load_order(sdd)
        for pid, rank in rows:
            assert pid in order
            status, body = handle_reorder_request(
                sdd, {"item": pid, "to_rank": int(rank)})
            assert status == 200, f"{pid} rejected: {body}"
            assert body["status"] == "ok"

    def test_drag_move_persists_to_disk(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        html_doc = self._build_html(sdd)
        rows = self._OPEN_ROW.findall(html_doc)
        first_pid = rows[0][0]
        # Move the top item down one rank via the real endpoint.
        status, _ = handle_reorder_request(sdd, {"item": first_pid, "to_rank": 1})
        assert status == 200
        # Artefacts exist on disk (real pipeline, not a prediction).
        assert (sdd / "backlog" / "display-order.json").exists()
        assert (sdd / "ledger" / "reorder-audit.jsonl").exists()
        # And the canonical order now reflects the move.
        assert load_order(sdd).index(first_pid) == 1

    def test_updown_buttons_carry_adjacent_ranks(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        html_doc = self._build_html(sdd)
        # SDD-003 is rank 1 in the seed natural order: up -> 0, down -> 2.
        assert 'data-item="SDD-003" data-to-rank="0"' in html_doc
        assert 'data-item="SDD-003" data-to-rank="2"' in html_doc
        # The down-button target is a real, accepted move.
        status, body = handle_reorder_request(sdd, {"item": "SDD-003", "to_rank": 2})
        assert status == 200 and body["status"] == "ok"

    def test_done_rows_are_not_rendered(self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        # Append a DONE row to the P2 table.
        backlog = sdd / "backlog" / "BACKLOG.md"
        text = backlog.read_text(encoding="utf-8")
        done_row = (
            "| SDD-009 | shipped thing | P2 | 8 | 3 | 0.9 | 2 | 10.8 "
            "| PI-2 Sprint A | DONE |\n"
        )
        text = text.replace(
            "| SDD-004 | qa.py | P2 | 6 | 2 | 0.8 | 2 | 4.8 | PI-2 Sprint B | Approved |\n",
            "| SDD-004 | qa.py | P2 | 6 | 2 | 0.8 | 2 | 4.8 | PI-2 Sprint B | Approved |\n"
            + done_row,
        )
        backlog.write_text(text, encoding="utf-8")

        html_doc = self._build_html(sdd)
        # Option A: DONE rows are not shown at all -- not as a done div, not as
        # a draggable open row.
        assert self._DONE_ROW.findall(html_doc) == []
        open_ids = [pid for pid, _ in self._OPEN_ROW.findall(html_doc)]
        assert "SDD-009" not in open_ids
        # The four OPEN seed rows remain the complete visible set.
        assert len(open_ids) == 4

    def test_open_rows_all_carry_non_empty_titles(self, tmp_path: Path) -> None:
        # Owner acceptance: ONLY open items, each with a NON-EMPTY title (never
        # a bare duplicated id).
        sdd = _seed_sdd_root(tmp_path)
        html_doc = self._build_html(sdd)
        for pid, _ in self._OPEN_ROW.findall(html_doc):
            # The title span for this row must not be the id itself.
            assert f'<span class="backlog-title">{pid}</span>' not in html_doc
        # Every seed row's real title is present.
        for title in ("state_builder.py", "fleet.py", "qa.py", "Dashboard"):
            assert f'<span class="backlog-title">{title}</span>' in html_doc

    def test_dash_rice_open_row_shows_real_title(self, tmp_path: Path) -> None:
        # Real-shape OPEN row: '--' RICE placeholder AND a trailing notes column
        # (11 cells). load_backlog cannot parse it; the tolerant meta pass must,
        # so the row renders with its real title + status rather than a bare id.
        sdd = _seed_sdd_root(tmp_path)
        backlog = sdd / "backlog" / "BACKLOG.md"
        text = backlog.read_text(encoding="utf-8")
        dash_row = (
            "| SDD-099 | tolerant title row | P1 | H | H | H | M | -- "
            "| Out-of-band | Pending Level-2 approval | extra notes column |\n"
        )
        text = text.replace(
            "| SDD-001 | Dashboard | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design |\n",
            "| SDD-001 | Dashboard | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design |\n"
            + dash_row,
        )
        backlog.write_text(text, encoding="utf-8")

        html_doc = self._build_html(sdd)
        assert 'data-pid="SDD-099"' in html_doc
        assert '<span class="backlog-title">tolerant title row</span>' in html_doc
        # Status comes from col 9 (the Status column), not the trailing notes.
        assert "Pending Level-2 approval" in html_doc
        assert "extra notes column" not in html_doc
        # No bare-id regression for this row.
        assert '<span class="backlog-title">SDD-099</span>' not in html_doc

    def test_done_interleave_preserves_full_order_ranks_and_drag(
            self, tmp_path: Path) -> None:
        sdd = _seed_sdd_root(tmp_path)
        backlog = sdd / "backlog" / "BACKLOG.md"
        text = backlog.read_text(encoding="utf-8")
        # Interleave a DONE row between SDD-002 and SDD-003.
        done_row = (
            "| SDD-009 | shipped | P2 | 8 | 3 | 0.9 | 2 | 10.8 "
            "| PI-2 Sprint A | DONE |\n"
        )
        text = text.replace(
            "| SDD-002 | state_builder.py | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 Sprint A | Approved |\n",
            "| SDD-002 | state_builder.py | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 Sprint A | Approved |\n"
            + done_row,
        )
        backlog.write_text(text, encoding="utf-8")

        order = load_order(sdd)
        assert order == ["SDD-002", "SDD-009", "SDD-003", "SDD-004", "SDD-001"]

        html_doc = self._build_html(sdd)
        # DONE row is hidden; the four open rows remain, in full-order sequence.
        assert self._DONE_ROW.findall(html_doc) == []
        open_rows = self._OPEN_ROW.findall(html_doc)
        assert [pid for pid, _ in open_rows] == [
            "SDD-002", "SDD-003", "SDD-004", "SDD-001"]
        # data-rank is the FULL load_order index (SDD-003 sits at index 2).
        assert dict(open_rows)["SDD-003"] == "2"
        # Buttons target adjacent OPEN items' full-order indices, skipping DONE.
        assert 'data-item="SDD-003" data-to-rank="0"' in html_doc  # up -> 002
        assert 'data-item="SDD-003" data-to-rank="3"' in html_doc  # down -> 004
        # Real drag round-trip: drop SDD-004 (after SDD-003) onto SDD-003's full
        # index -> SDD-004 lands immediately before SDD-003 in the new order.
        status, body = handle_reorder_request(
            sdd, {"item": "SDD-004", "to_rank": 2})
        assert status == 200 and body["status"] == "ok"
        new_order = load_order(sdd)
        assert new_order.index("SDD-004") < new_order.index("SDD-003")

    def test_dependency_blocked_move_returns_409(self, tmp_path: Path) -> None:
        # A real dependency lock: SDD-100 depends_on SDD-101. Natural order is
        # [SDD-101, SDD-100]; moving SDD-100 above its blocker must 409.
        sdd = tmp_path / "dep"
        (sdd / "backlog").mkdir(parents=True)
        (sdd / "ledger").mkdir(parents=True)
        (sdd / "backlog" / "BACKLOG.md").write_text(
            "# Product Backlog\n\n## P2 - Should Have\n\n"
            "| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |\n"
            "|----|-------|----------|-------|--------|------------|--------|------|--------|--------|\n"
            "| SDD-101 | base | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 | Approved |\n"
            "| SDD-100 | dependent | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 | Approved |\n",
            encoding="utf-8",
        )
        for name, fid, dep in (
            ("dep-101", "SDD-101", None),
            ("dep-100", "SDD-100", "SDD-101"),
        ):
            spec = sdd / "specs" / name
            spec.mkdir(parents=True)
            front = "---\n"
            if dep:
                front += f"depends_on: [{dep}]\n"
            front += "---\n"
            (spec / "spec.md").write_text(
                f"{front}# Feature Spec\n\n- Feature ID: {fid}\n",
                encoding="utf-8",
            )
        assert load_order(sdd) == ["SDD-101", "SDD-100"]
        status, body = handle_reorder_request(sdd, {"item": "SDD-100", "to_rank": 0})
        assert status == 409
        assert body["status"] == "blocked"
        assert "SDD-101" in body["reason"]


class TestSdd041HandleReorder:
    """AC: pure validation + delegation contract for POST /reorder."""

    def test_non_dict_payload_is_400(self, tmp_path: Path) -> None:
        status, body = handle_reorder_request(tmp_path, ["not", "a", "dict"])
        assert status == 400
        assert body["status"] == "error"

    def test_invalid_item_is_400(self, tmp_path: Path, monkeypatch) -> None:
        calls = []
        monkeypatch.setattr(_ds, "_reorder_move",
                            lambda *a, **k: calls.append(k) or {})
        status, body = handle_reorder_request(tmp_path, {"item": "nope", "to_rank": 0})
        assert status == 400
        assert calls == []  # mutator never invoked on bad input

    def test_negative_rank_is_400(self, tmp_path: Path, monkeypatch) -> None:
        calls = []
        monkeypatch.setattr(_ds, "_reorder_move",
                            lambda *a, **k: calls.append(k) or {})
        status, _ = handle_reorder_request(tmp_path, {"item": "SDD-041", "to_rank": -1})
        assert status == 400
        assert calls == []

    def test_bool_rank_is_rejected(self, tmp_path: Path, monkeypatch) -> None:
        # bool is an int subclass -- must not slip through as rank 1/0.
        calls = []
        monkeypatch.setattr(_ds, "_reorder_move",
                            lambda *a, **k: calls.append(k) or {})
        status, _ = handle_reorder_request(tmp_path, {"item": "SDD-041", "to_rank": True})
        assert status == 400
        assert calls == []

    def test_happy_path_returns_200_with_audit(self, tmp_path: Path, monkeypatch) -> None:
        recorded = {}
        fake_row = {"item": "SDD-041", "to_rank": 2, "actor": "human"}

        def fake_move(sdd_root, *, item, to_rank, force):
            recorded.update(sdd_root=sdd_root, item=item, to_rank=to_rank, force=force)
            return fake_row

        monkeypatch.setattr(_ds, "_reorder_move", fake_move)
        status, body = handle_reorder_request(tmp_path, {"item": "SDD-041", "to_rank": 2})
        assert status == 200
        assert body == {"status": "ok", "audit": fake_row}
        assert recorded["item"] == "SDD-041"
        assert recorded["to_rank"] == 2
        assert recorded["force"] is False  # ADR-017: force never auto-applied

    def test_blocked_returns_409_without_force(self, tmp_path: Path, monkeypatch) -> None:
        seen = {}

        def fake_move(sdd_root, *, item, to_rank, force):
            seen["force"] = force
            raise _sb._ReorderError("SDD-041 depends on SDD-040")

        monkeypatch.setattr(_ds, "_reorder_move", fake_move)
        status, body = handle_reorder_request(tmp_path, {"item": "SDD-041", "to_rank": 0})
        assert status == 409
        assert body["status"] == "blocked"
        assert "SDD-040" in body["reason"]
        assert seen["force"] is False  # never retried with force

    def test_out_of_range_rank_returns_400(self, tmp_path: Path, monkeypatch) -> None:
        def fake_move(sdd_root, *, item, to_rank, force):
            raise ValueError("to_rank 99 out of range")

        monkeypatch.setattr(_ds, "_reorder_move", fake_move)
        status, body = handle_reorder_request(tmp_path, {"item": "SDD-041", "to_rank": 99})
        assert status == 400
        assert "out of range" in body["reason"]


class _CapturingHandler(DashboardHandler):
    """DashboardHandler with HTTP plumbing bypassed for unit testing do_POST."""

    def __init__(self, sdd_root: Path, body: bytes, path: str = "/reorder",
                 headers: dict | None = None) -> None:  # noqa: D401
        # Deliberately skip BaseHTTPRequestHandler.__init__ (needs a socket).
        self.sdd_root = sdd_root
        self.path = path
        self.rfile = io.BytesIO(body)
        self.headers = headers or {"Content-Length": str(len(body))}
        self.captured: tuple[int, dict] | None = None

    def _send_json(self, status: int, payload: dict) -> None:  # capture, don't write
        self.captured = (status, payload)


class TestSdd041DoPost:
    """AC: do_POST routes only /reorder, validates body, delegates; do_GET intact."""

    def test_non_reorder_path_is_404(self, tmp_path: Path) -> None:
        h = _CapturingHandler(tmp_path, b"{}", path="/elsewhere")
        h.do_POST()
        assert h.captured[0] == 404

    def test_malformed_json_is_400(self, tmp_path: Path) -> None:
        body = b"{not valid json"
        h = _CapturingHandler(tmp_path, body,
                              headers={"Content-Length": str(len(body))})
        h.do_POST()
        assert h.captured[0] == 400
        assert "malformed" in h.captured[1]["reason"]

    def test_valid_post_delegates_and_returns_200(
            self, tmp_path: Path, monkeypatch) -> None:
        fake_row = {"item": "SDD-041", "to_rank": 1}
        monkeypatch.setattr(_ds, "_reorder_move",
                            lambda sdd_root, *, item, to_rank, force: fake_row)
        body = json.dumps({"item": "SDD-041", "to_rank": 1}).encode("utf-8")
        h = _CapturingHandler(tmp_path, body,
                              headers={"Content-Length": str(len(body))})
        h.do_POST()
        assert h.captured == (200, {"status": "ok", "audit": fake_row})

    def test_do_get_still_present(self) -> None:
        # do_GET must remain on the handler (unchanged contract).
        assert hasattr(DashboardHandler, "do_GET")
        assert hasattr(DashboardHandler, "do_POST")


# ===========================================================================
# SDD-050 (Dashboard truth): detect_stage reconciled with done_check.
#   Defect 1: DONE is driven by REQUIRED-item completeness (via the shared
#   done_check.validation_complete helper), not by an all-boxes ratio that
#   also counts optional items, and not gated on a per-dir RETRO.md.
#   Split validation-*.md files must be recognized like done_check does.
# ===========================================================================

from cli.state_builder import detect_stage  # noqa: E402


def _write_feature(root: Path, name: str, *, spec_status=None,
                   validation_files=None, retro=False, extra=None):
    """Seed a specs/<name> dir for detect_stage.

    validation_files: dict of {filename: contents} (supports split validation).
    """
    feat = root / name
    feat.mkdir(parents=True)
    spec_body = "# Feature Spec: demo\n\n"
    if spec_status is not None:
        spec_body += f"- Status: {spec_status}\n"
    (feat / "spec.md").write_text(spec_body, encoding="utf-8")
    for fname, contents in (validation_files or {}).items():
        (feat / fname).write_text(contents, encoding="utf-8")
    if retro:
        (feat / "RETRO.md").write_text("# retro\n", encoding="utf-8")
    for fname, contents in (extra or {}).items():
        (feat / fname).write_text(contents, encoding="utf-8")
    return feat


_REQ_COMPLETE = (
    "# VALIDATION: demo\n\n## Required Items\n\n"
    "- [x] R-1: first item.\n- [x] R-2: second item.\n"
)
_REQ_COMPLETE_WITH_OPTIONAL = (
    _REQ_COMPLETE + "\n## Optional Items\n\n- [ ] O-1: optional, still open.\n"
)
_REQ_UNCHECKED = (
    "# VALIDATION: demo\n\n## Required Items\n\n"
    "- [x] R-1: first item.\n- [ ] R-2: second item still open.\n"
)


class TestSdd050DetectStage:
    """Defect 1: detect_stage renders truth for shipped/carryover features."""

    def test_validation_required_complete_is_done_without_retro(
        self, tmp_path: Path
    ) -> None:
        # Stale status + all REQUIRED items checked + NO RETRO -> DONE.
        feat = _write_feature(
            tmp_path, "2026-06-26-shipped",
            spec_status="Implementing",
            validation_files={"validation.md": _REQ_COMPLETE},
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage == "DONE"

    def test_explicit_done_no_validation_file_is_done(self, tmp_path: Path) -> None:
        # Status: done, no validation file, no RETRO -> trust the status -> DONE.
        feat = _write_feature(
            tmp_path, "2026-06-26-de-author",
            spec_status="done",
            validation_files=None,
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage == "DONE"

    def test_done_status_with_incomplete_required_is_review(
        self, tmp_path: Path
    ) -> None:
        # Status: done but REQUIRED items still unchecked -> not truthfully DONE.
        feat = _write_feature(
            tmp_path, "2026-06-26-carryover",
            spec_status="done",
            validation_files={"validation.md": _REQ_UNCHECKED},
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage == "REVIEW"

    def test_split_validation_required_complete_is_done(self, tmp_path: Path) -> None:
        # Split validation files, all REQUIRED complete, stale status, no RETRO.
        feat = _write_feature(
            tmp_path, "2026-06-26-split",
            spec_status="Implementing",
            validation_files={
                "validation-a.md": _REQ_COMPLETE,
                "validation-b.md": _REQ_COMPLETE,
            },
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage == "DONE"

    def test_optional_unchecked_still_done(self, tmp_path: Path) -> None:
        # REQUIRED complete, OPTIONAL unchecked, stale status -> DONE
        # (optional boxes must not demote a required-complete feature).
        feat = _write_feature(
            tmp_path, "2026-06-26-optional",
            spec_status="Implementing",
            validation_files={"validation.md": _REQ_COMPLETE_WITH_OPTIONAL},
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage == "DONE"

    def test_carryover_unchecked_required_stays_in_progress(
        self, tmp_path: Path
    ) -> None:
        # No explicit status; many REQUIRED unchecked -> IMPLEMENT/REVIEW, never DONE.
        feat = _write_feature(
            tmp_path, "2026-06-26-real-carryover",
            spec_status=None,
            validation_files={"validation.md": _REQ_UNCHECKED},
            retro=False,
        )
        stage, _status, _notes = detect_stage(feat)
        assert stage in {"IMPLEMENT", "REVIEW"}
        assert stage != "DONE"


class TestSdd050PiClosed:
    """Defect 2: closed PIs render at 100% and never masquerade as current;
    the header falls back to the newest PI, not the oldest."""

    def _write_roadmap(self, tmp_path: Path, body: str) -> Path:
        sdd = _seed_sdd_root(tmp_path)
        (sdd / "constitution" / "roadmap.md").write_text(body, encoding="utf-8")
        return sdd

    def test_load_pis_marks_closed_pi(self, tmp_path: Path) -> None:
        sdd = self._write_roadmap(
            tmp_path,
            "# Roadmap\n\n## PI-1: Bootstrap (closed 2026-05-13)\n\n- [x] a\n",
        )
        pis = load_pis(sdd)
        assert pis[0].is_closed is True

    def test_closed_and_current_title_closed_wins(self, tmp_path: Path) -> None:
        # PI-7 header says "(current, closed ...)" -> closed wins; not current.
        sdd = self._write_roadmap(
            tmp_path,
            "# Roadmap\n\n## PI-7: Hardening (current, closed 2026-07-07)\n\n- [ ] a\n",
        )
        pis = load_pis(sdd)
        assert pis[0].is_closed is True
        assert pis[0].is_current is False

    def test_closed_pi_pct_is_100_even_with_unchecked(self, tmp_path: Path) -> None:
        pi = PIBlock(
            name="PI-1", title="Bootstrap", is_current=False,
            checkboxes=[(True, "a"), (False, "b")], is_closed=True,
        )
        assert pi.pct == 100

    def test_current_pi_fallback_returns_newest_when_all_closed(
        self, tmp_path: Path
    ) -> None:
        # PI-1..PI-5 closed, PI-6 absent, PI-7 closed -> header = PI-7 (newest).
        sdd = self._write_roadmap(
            tmp_path,
            "# Roadmap\n\n"
            "## PI-1: Bootstrap (closed 2026-05-13)\n\n- [x] a\n\n"
            "## PI-5: Adoption (closed 2026-06-09)\n\n- [x] a\n\n"
            "## PI-7: Hardening (current, closed 2026-07-07)\n\n- [ ] a\n",
        )
        pis = load_pis(sdd)
        picked = current_pi(pis)
        assert picked is not None
        assert picked.name == "PI-7"

    def test_current_pi_unchecked_fallback_skips_closed(self, tmp_path: Path) -> None:
        # A closed PI with unchecked boxes must NOT be picked by the
        # unchecked-fallback branch; an open PI wins.
        pis = [
            PIBlock(name="PI-1", title="Old", is_current=False,
                    checkboxes=[(False, "a")], is_closed=True),
            PIBlock(name="PI-2", title="Open", is_current=False,
                    checkboxes=[(False, "b")], is_closed=False),
        ]
        picked = current_pi(pis)
        assert picked is not None
        assert picked.name == "PI-2"

