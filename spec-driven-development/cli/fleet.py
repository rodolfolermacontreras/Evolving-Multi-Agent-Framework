#!/usr/bin/env python3
"""Fleet CLI -- dispatch, mark, and status for the SDD fleet (SDD-003).

Subcommands:
    dispatch    Parse tasks.md, generate agent briefs, write ledger rows.
    mark        Update outcome on a dispatch by ID.
    status      List dispatches for a feature directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Framework layout ---------------------------------------------------------- #
SDD_ROOT = Path(__file__).resolve().parents[1]
_LEDGER_DIR = SDD_ROOT / "ledger"
if str(_LEDGER_DIR) not in sys.path:
    sys.path.insert(0, str(_LEDGER_DIR))

from ledger_cli import (  # noqa: E402
    OUTCOMES,
    connect_initialized,
    fetch_dispatches,
    mark_outcome,
    print_dispatch_table,
    record_dispatch,
    utc_now,
)

DEFAULT_DB = _LEDGER_DIR / "fleet.db"
ROSTER_PATH = SDD_ROOT / "roster" / "agents.json"


# Exception ----------------------------------------------------------------- #


class FleetError(Exception):
    """Expected fleet CLI failure."""


# Task parser --------------------------------------------------------------- #


def parse_tasks_md(feature_dir: Path) -> list[dict]:
    """Parse tasks.md from *feature_dir* into a list of task dicts.

    Handles both the full ``Fleet Dispatch Eligible`` column name and the
    abbreviated ``Fleet`` column name.
    """
    tasks_md = feature_dir / "tasks.md"
    if not tasks_md.is_file():
        raise FleetError(f"tasks.md not found in {feature_dir}")

    lines = tasks_md.read_text(encoding="utf-8").strip().splitlines()

    # Find the header row (contains "Task ID")
    header_idx: int | None = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and re.search(r"task\s*id", line, re.IGNORECASE):
            header_idx = i
            break
    if header_idx is None:
        raise FleetError(f"No task table header found in {tasks_md}")

    # Map column headers to logical names
    headers = [h.strip() for h in lines[header_idx].strip().strip("|").split("|")]
    col_map: dict[str, int] = {}
    for i, h in enumerate(headers):
        hl = h.lower().strip()
        if "task" in hl and "id" in hl:
            col_map["task_id"] = i
        elif "desc" in hl:
            col_map["description"] = i
        elif "file" in hl and "scope" in hl:
            col_map["file_scope"] = i
        elif "accept" in hl:
            col_map["acceptance"] = i
        elif "fleet" in hl:
            col_map["fleet_eligible"] = i
        elif hl == "status":
            col_map["status"] = i

    # Parse data rows
    tasks: list[dict] = []
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Skip separator rows (cells are only dashes / colons)
        if all(re.match(r"^[\-:]+$", c) for c in cells if c):
            continue
        task: dict[str, str] = {}
        for key, idx in col_map.items():
            task[key] = cells[idx].strip() if idx < len(cells) else ""
        if task.get("task_id"):
            tasks.append(task)

    return tasks


def find_task(tasks: list[dict], task_id: str) -> dict:
    """Return the task dict for *task_id* or raise FleetError."""
    for t in tasks:
        if t.get("task_id") == task_id:
            return t
    valid = ", ".join(t.get("task_id", "?") for t in tasks)
    raise FleetError(f"Task {task_id} not found in tasks.md. Available: {valid}")


def is_eligible(task: dict) -> bool:
    """Return True unless Fleet Dispatch Eligible is explicitly 'No'."""
    return task.get("fleet_eligible", "").strip().lower() != "no"


# Brief renderer ------------------------------------------------------------ #


def render_brief(
    *,
    dispatch_id: int,
    task_id: str,
    description: str,
    agent_role: str,
    feature_dir: str,
    file_scope: str,
    acceptance: str,
) -> str:
    """Render a Markdown agent brief matching templates/agent-brief.md."""
    items = [s.strip().strip("`") for s in re.split(r"[,;]", file_scope) if s.strip()]
    scope_lines = "\n".join(f"  - {item}" for item in items) if items else "  - (see tasks.md)"

    return (
        f"# Agent Brief: {task_id}\n"
        f"\n"
        f"- Task Reference: {feature_dir}/tasks.md\n"
        f"- Worker Role: {agent_role}\n"
        f"- Dispatch ID: {dispatch_id}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Task\n"
        f"\n"
        f"{description}\n"
        f"\n"
        f"## File Scope\n"
        f"\n"
        f"- Allowed files:\n"
        f"{scope_lines}\n"
        f"\n"
        f"## Acceptance Criteria\n"
        f"\n"
        f"{acceptance}\n"
        f"\n"
        f"## Constraints\n"
        f"\n"
        f"- Do not modify files outside the allowed scope.\n"
        f"- Do not add new dependencies.\n"
    )


# Roster -------------------------------------------------------------------- #


def load_roster(path: Path) -> list[dict]:
    """Load agent roster from JSON file."""
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_agent(agent_id: str, roster: list[dict]) -> dict:
    """Look up agent in roster; raise FleetError if roster exists but id missing."""
    for a in roster:
        if a.get("id") == agent_id:
            return a
    if roster:
        valid = ", ".join(a.get("id", "?") for a in roster)
        raise FleetError(f"Unknown agent '{agent_id}'. Valid: {valid}")
    return {"id": agent_id, "role": agent_id}


# Subcommands --------------------------------------------------------------- #


def cmd_dispatch(args: argparse.Namespace) -> int:
    """Parse tasks.md, validate eligibility, write briefs + ledger rows."""
    feature_path = Path(args.feature).resolve()
    feature_str = str(feature_path)

    tasks = parse_tasks_md(feature_path)

    roster_path = Path(args.roster) if args.roster else ROSTER_PATH
    agent = resolve_agent(args.agent, load_roster(roster_path))
    agent_role = agent.get("role") or agent.get("kind") or args.agent

    task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]

    # Validate all tasks before writing anything
    resolved: list[tuple[str, dict]] = []
    for tid in task_ids:
        task = find_task(tasks, tid)
        if not is_eligible(task):
            raise FleetError(f"Task {tid} is not eligible for fleet dispatch.")
        resolved.append((tid, task))

    db_path = Path(args.db) if args.db else DEFAULT_DB
    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    for tid, task in resolved:
        values = {
            "dispatched_at": utc_now(),
            "pi": args.pi,
            "sprint": getattr(args, "sprint", None),
            "feature_dir": feature_str,
            "task_id": tid,
            "task_title": task.get("description", tid),
            "agent_id": agent["id"],
            "agent_role": agent_role,
            "outcome": None,
            "outcome_at": None,
            "notes": getattr(args, "notes", None),
        }
        dispatch_id = record_dispatch(db_path, values)

        brief = render_brief(
            dispatch_id=dispatch_id,
            task_id=tid,
            description=task.get("description", ""),
            agent_role=agent_role,
            feature_dir=feature_str,
            file_scope=task.get("file_scope", ""),
            acceptance=task.get("acceptance", ""),
        )

        if output_dir:
            out_file = output_dir / f"dispatch-{dispatch_id}-{tid}.md"
            out_file.write_text(brief, encoding="utf-8")
            print(f"Brief saved: {out_file}")
        else:
            print(brief)

    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    """Update outcome on a dispatch."""
    db_path = Path(args.db) if args.db else DEFAULT_DB
    ok = mark_outcome(db_path, args.dispatch_id, args.outcome, utc_now())
    if not ok:
        print(f"ERROR: No dispatch with id {args.dispatch_id}.", file=sys.stderr)
        return 1
    if getattr(args, "notes", None):
        with connect_initialized(db_path) as conn:
            conn.execute(
                "UPDATE dispatches SET notes = ? WHERE id = ?",
                (args.notes, args.dispatch_id),
            )
            conn.commit()
    print(f"Dispatch #{args.dispatch_id} marked {args.outcome}.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """List dispatches for a feature directory."""
    db_path = Path(args.db) if args.db else DEFAULT_DB
    feature_str = str(Path(args.feature).resolve())
    rows = fetch_dispatches(db_path, "feature_dir", feature_str)
    if getattr(args, "pi", None):
        rows = [r for r in rows if r["pi"] == args.pi]
    if not rows:
        print("No dispatches found for this feature.")
        return 0
    print_dispatch_table(rows)
    return 0


# CLI parser ---------------------------------------------------------------- #


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="fleet.py",
        description="Fleet CLI: dispatch, mark, and status for the SDD fleet.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # dispatch
    p_disp = sub.add_parser("dispatch", help="Parse tasks.md, generate briefs, write ledger rows.")
    p_disp.add_argument("--feature", required=True, help="Feature directory path.")
    p_disp.add_argument("--tasks", required=True, help="Comma-separated task IDs (e.g. T-001,T-002).")
    p_disp.add_argument("--agent", required=True, help="Agent ID (e.g. developer-general).")
    p_disp.add_argument("--pi", required=True, help="Program increment (e.g. PI-2).")
    p_disp.add_argument("--sprint", default=None, help="Sprint label (e.g. A).")
    p_disp.add_argument("--output-dir", default=None, help="Save briefs to directory instead of stdout.")
    p_disp.add_argument("--notes", default=None, help="Optional notes for dispatch rows.")
    p_disp.add_argument("--db", default=None, help="Path to fleet.db.")
    p_disp.add_argument("--roster", default=None, help="Path to agents.json.")

    # mark
    p_mark = sub.add_parser("mark", help="Update outcome on a dispatch.")
    p_mark.add_argument("--dispatch-id", type=int, required=True, help="Dispatch ID to update.")
    p_mark.add_argument("--outcome", choices=OUTCOMES, required=True, help="Outcome: success, failed, or blocked.")
    p_mark.add_argument("--notes", default=None, help="Optional notes.")
    p_mark.add_argument("--db", default=None, help="Path to fleet.db.")

    # status
    p_stat = sub.add_parser("status", help="List dispatches for a feature directory.")
    p_stat.add_argument("--feature", required=True, help="Feature directory path.")
    p_stat.add_argument("--pi", default=None, help="Filter by program increment.")
    p_stat.add_argument("--db", default=None, help="Path to fleet.db.")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    handlers = {
        "dispatch": cmd_dispatch,
        "mark": cmd_mark,
        "status": cmd_status,
    }
    try:
        return handlers[args.command](args)
    except FleetError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
