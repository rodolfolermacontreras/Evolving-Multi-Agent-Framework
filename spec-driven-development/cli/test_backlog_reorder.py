"""Tests for cli/backlog_reorder.py (SDD-036 / F-25): AC-5, AC-6, AC-7, AC-8 plumbing."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CLI_DIR))
import backlog_reorder  # noqa: E402


BACKLOG_TEXT = """# Backlog

| ID | Title | Priority | RICE | Sprint | Status |
|----|-------|----------|------|--------|--------|
| SDD-100 | Foundation | P1 | -- | PI-6 | **DONE** 2026-06-10 |
| SDD-101 | Incomplete dep | P1 | -- | PI-6 | Backlog |
| SDD-102 | Free agent | P1 | -- | PI-6 | Backlog |
| SDD-103 | Depends on 101 | P1 | -- | PI-6 | Backlog |
| SDD-200 | Cycle A | P1 | -- | PI-6 | Backlog |
| SDD-201 | Cycle B | P1 | -- | PI-6 | Backlog |
"""


def _spec(feature_id: str, deps: str) -> str:
    return (
        "---\n"
        f"id: {feature_id}-spec\n"
        "type: spec\n"
        "status: active\n"
        "owner: principal-architect\n"
        "updated: 2026-06-11\n"
        f"depends_on: {deps}\n"
        "---\n\n"
        f"# Spec\n\n- Feature ID: {feature_id}\n"
    )


class BacklogReorderBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self._tmp.name)
        (self.root / "backlog").mkdir()
        (self.root / "ledger").mkdir()
        (self.root / "backlog" / "BACKLOG.md").write_text(BACKLOG_TEXT, encoding="utf-8")
        # SDD-103 depends on incomplete SDD-101; SDD-200<->SDD-201 form a cycle.
        for fid, deps in (("SDD-103", "[SDD-101]"),
                          ("SDD-200", "[SDD-201]"),
                          ("SDD-201", "[SDD-200]")):
            d = self.root / "specs" / f"feat-{fid.lower()}"
            d.mkdir(parents=True)
            (d / "spec.md").write_text(_spec(fid, deps), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _audit_rows(self) -> list[dict]:
        path = backlog_reorder.audit_path(self.root)
        if not path.is_file():
            return []
        return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = backlog_reorder.main(["--sdd-root", str(self.root)] + argv)
        return code, out.getvalue(), err.getvalue()


class OverlayBasics(BacklogReorderBase):
    def test_absent_overlay_uses_backlog_natural_order(self):
        order = backlog_reorder.load_order(self.root)
        self.assertEqual(
            order,
            ["SDD-100", "SDD-101", "SDD-102", "SDD-103", "SDD-200", "SDD-201"],
        )

    def test_present_overlay_is_respected(self):
        backlog_reorder.write_order(self.root, ["SDD-103", "SDD-100"])
        order = backlog_reorder.load_order(self.root)
        # Overlay order first, then any backlog IDs missing from the overlay.
        self.assertEqual(order[:2], ["SDD-103", "SDD-100"])
        self.assertIn("SDD-201", order)


class LegalMove(BacklogReorderBase):
    def test_legal_move_reorders_and_exits_zero(self):
        code, out, _ = self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        self.assertEqual(code, 0)
        self.assertEqual(backlog_reorder.load_order(self.root)[0], "SDD-102")

    def test_legal_move_appends_exactly_one_audit_row(self):
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        rows = self._audit_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(tuple(rows[0].keys()), backlog_reorder.AUDIT_FIELDS)
        self.assertEqual(rows[0]["item_id"], "SDD-102")
        self.assertEqual(rows[0]["dependency_check"], "pass")
        self.assertFalse(rows[0]["force_override"])
        self.assertTrue(rows[0]["timestamp"].endswith("Z"))

    def test_audit_is_append_only_across_two_moves(self):
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        first = self._audit_rows()[0]
        self._run(["move", "--item", "SDD-100", "--to-rank", "5"])
        rows = self._audit_rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], first)  # earlier row untouched


class BlockedMove(BacklogReorderBase):
    def test_move_above_incomplete_dependency_is_blocked(self):
        before = backlog_reorder.load_order(self.root)
        code, _, err = self._run(["move", "--item", "SDD-103", "--to-rank", "0"])
        self.assertEqual(code, 1)
        self.assertIn("SDD-101", err)
        self.assertIn("BLOCKED", err)
        # No overlay written -> order unchanged.
        self.assertEqual(backlog_reorder.load_order(self.root), before)
        self.assertEqual(self._audit_rows(), [])

    def test_cycle_move_is_blocked(self):
        code, _, err = self._run(["move", "--item", "SDD-200", "--to-rank", "0"])
        self.assertEqual(code, 1)
        self.assertIn("cycle", err.lower())
        self.assertEqual(self._audit_rows(), [])

    def test_unknown_item_exits_one_with_reason(self):
        code, _, err = self._run(["move", "--item", "SDD-999", "--to-rank", "0"])
        self.assertEqual(code, 1)
        self.assertIn("unknown item", err.lower())


class ForceGovernance(BacklogReorderBase):
    def test_force_with_reason_lands_blocked_move(self):
        code, _, _ = self._run([
            "move", "--item", "SDD-103", "--to-rank", "0",
            "--force", "--reason", "owner override: re-sequencing for demo",
        ])
        self.assertEqual(code, 0)
        self.assertEqual(backlog_reorder.load_order(self.root)[0], "SDD-103")
        rows = self._audit_rows()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["force_override"])
        self.assertEqual(rows[0]["dependency_check"], "override")
        self.assertTrue(rows[0]["reason"])

    def test_force_without_reason_exits_two(self):
        code, _, err = self._run([
            "move", "--item", "SDD-103", "--to-rank", "0", "--force",
        ])
        self.assertEqual(code, 2)
        self.assertIn("never silently forces", err.lower())
        # Governance rejection must not mutate state.
        self.assertEqual(self._audit_rows(), [])

    def test_violation_without_force_is_blocked(self):
        code, _, err = self._run(["move", "--item", "SDD-103", "--to-rank", "0"])
        self.assertEqual(code, 1)
        self.assertEqual(self._audit_rows(), [])


class UsageErrors(BacklogReorderBase):
    def test_missing_required_arg_exits_two(self):
        code, _, _ = self._run(["move", "--item", "SDD-102"])  # no --to-rank
        self.assertEqual(code, 2)

    def test_out_of_range_rank_exits_two(self):
        code, _, err = self._run(["move", "--item", "SDD-102", "--to-rank", "99"])
        self.assertEqual(code, 2)
        self.assertIn("out of range", err.lower())

    def test_no_subcommand_exits_two(self):
        code, _, _ = self._run([])
        self.assertEqual(code, 2)


# SDD-054 (Option B) -- reorder -> backend re-optimization ------------------ #


class EffectivePriority(BacklogReorderBase):
    def test_backlog_entries_parse_rice_priority(self):
        entries = backlog_reorder.load_backlog_entries(self.root)
        by_id = {e.id: e for e in entries}
        self.assertEqual(by_id["SDD-100"].priority, "P1")
        self.assertTrue(by_id["SDD-100"].done)
        self.assertFalse(by_id["SDD-101"].done)

    def test_compute_blends_manual_and_rice_into_scored_ranking(self):
        entries = backlog_reorder.load_backlog_entries(self.root)
        order = ["SDD-102", "SDD-100", "SDD-101"]
        ranking = backlog_reorder.compute_effective_priority(order, entries, {})
        # Scored, descending priority_score; RICE annotated.
        self.assertEqual([r["id"] for r in ranking], order)
        self.assertEqual(ranking[0]["priority_score"], 3)
        self.assertEqual(ranking[-1]["priority_score"], 1)
        self.assertEqual(ranking[0]["rice_priority"], "P1")
        self.assertEqual(ranking[0]["manual_rank"], 0)

    def test_dependency_correction_demotes_below_incomplete_dep(self):
        entries = backlog_reorder.load_backlog_entries(self.root)
        depends_map = backlog_reorder.load_depends_map(self.root)
        # Manual order illegally puts SDD-103 above its incomplete dep SDD-101.
        order = ["SDD-103", "SDD-101", "SDD-102"]
        ranking = backlog_reorder.compute_effective_priority(order, entries, depends_map)
        eff = [r["id"] for r in ranking]
        self.assertLess(eff.index("SDD-101"), eff.index("SDD-103"))

    def test_move_writes_effective_priority_artifact(self):
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        path = backlog_reorder.effective_priority_path(self.root)
        self.assertTrue(path.is_file())
        ranking = backlog_reorder.load_effective_priority(self.root)
        self.assertEqual(ranking[0]["id"], "SDD-102")
        self.assertEqual(ranking[0]["effective_rank"], 0)

    def test_move_still_appends_exactly_one_audit_row(self):
        # Option B must not double-log: reoptimize writes the artifact, not audit.
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        self.assertEqual(len(self._audit_rows()), 1)

    def test_effective_priority_order_reads_persisted_ranking(self):
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        self.assertEqual(
            backlog_reorder.effective_priority_order(self.root)[0], "SDD-102"
        )

    def test_reoptimize_subcommand_exits_zero_and_writes_artifact(self):
        code, out, _ = self._run(["reoptimize"])
        self.assertEqual(code, 0)
        self.assertIn("Re-optimized", out)
        self.assertTrue(backlog_reorder.effective_priority_path(self.root).is_file())

    def test_backlog_md_not_mutated_by_reoptimization(self):
        before = backlog_reorder.backlog_path(self.root).read_text(encoding="utf-8")
        self._run(["move", "--item", "SDD-102", "--to-rank", "0"])
        after = backlog_reorder.backlog_path(self.root).read_text(encoding="utf-8")
        self.assertEqual(before, after)  # ADR-017: RICE source untouched


if __name__ == "__main__":
    unittest.main()
