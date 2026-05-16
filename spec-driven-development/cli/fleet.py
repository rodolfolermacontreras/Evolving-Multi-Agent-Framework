#!/usr/bin/env python3
"""Fleet CLI -- dispatch packet generation + ledger writes (SDD-003).

Subcommands:

    dispatch       Emit a markdown dispatch packet AND insert a fleet.db row.
    mark-outcome   Close a dispatch by id with outcome success | failed | blocked.
    status         List in-flight dispatches (outcome IS NULL).
    list           List dispatches by PI and/or feature directory.

Style: pure Python stdlib + the local ledger_cli module. No third-party deps.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = SDD_ROOT / "ledger"
DISPATCHES_DIR = SDD_ROOT / "dispatches"
ROSTER_PATH = SDD_ROOT / "roster" / "agents.json"
TEMPLATE_PATH = SDD_ROOT / "templates" / "agent-brief.md"
DEFAULT_DB = LEDGER_DIR / "fleet.db"

sys.path.insert(0, str(LEDGER_DIR))
import ledger_cli  # noqa: E402  (local module, executed for its helpers)

OUTCOMES = ledger_cli.OUTCOMES   # ('success', 'failed', 'blocked')


# ---------------------------------------------------------------------------- #
# Roster
# ---------------------------------------------------------------------------- #

def load_agents(roster_path: Path = ROSTER_PATH) -> list[dict]:
    if not roster_path.is_file():
        return []
    return json.loads(roster_path.read_text(encoding="utf-8"))


def resolve_agent(agent_id: str, agents: list[dict]) -> dict:
    """Return the roster entry for agent_id, raising KeyError with hint if missing."""
    for a in agents:
        if a.get("id") == agent_id:
            return a
    valid = ", ".join(a.get("id", "?") for a in agents) or "(roster empty)"
    raise KeyError(f"unknown agent '{agent_id}'. Valid agent ids: {valid}")


# ---------------------------------------------------------------------------- #
# Tasks.md scraping (best-effort)
# ---------------------------------------------------------------------------- #

def extract_task_row(feature_dir: Path, task_id: str) -> dict:
    """Return {'title': ..., 'file_scope': ..., 'acceptance': ...} for the given task id.

    Best-effort. If tasks.md is missing or the task row cannot be parsed, returns
    empty strings; the operator can always pass --title explicitly.
    """
    tasks_md = feature_dir / "tasks.md"
    if not tasks_md.is_file():
        return {"title": "", "file_scope": "", "acceptance": ""}
    text = tasks_md.read_text(encoding="utf-8", errors="replace")
    row_re = re.compile(
        rf"^\|\s*{re.escape(task_id)}\s*\|"
        r"\s*(?P<tag>[^|]*?)\s*\|"
        r"\s*(?P<desc>[^|]*?)\s*\|"
        r"\s*(?P<scope>[^|]*?)\s*\|"
        r"\s*(?P<accept>[^|]*?)\s*\|",
        re.MULTILINE,
    )
    m = row_re.search(text)
    if not m:
        return {"title": "", "file_scope": "", "acceptance": ""}
    return {
        "title": m.group("desc").strip(),
        "file_scope": m.group("scope").strip(),
        "acceptance": m.group("accept").strip(),
    }


# ---------------------------------------------------------------------------- #
# Dispatch packet rendering
# ---------------------------------------------------------------------------- #

def render_packet(*, dispatch_id: int, task_id: str, task_title: str,
                  worker_role: str, agent_id: str, feature_dir: str,
                  file_scope: str, acceptance: str, verification: str) -> str:
    """Render a self-contained dispatch packet (markdown).

    Loads `templates/agent-brief.md` if present, otherwise uses an inline default.
    Substitutes {TOKEN} placeholders. Unknown placeholders are left as the empty string.
    """
    if TEMPLATE_PATH.is_file():
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    else:
        template = (
            "# Agent Brief: {TASK_ID}\n\n"
            "- Task: {TASK_TITLE}\n"
            "- Worker: {WORKER_ROLE} ({AGENT_ID})\n"
            "- Dispatch ID: {DISPATCH_ID}\n"
            "- Feature: {FEATURE_DIR}\n\n"
            "## File Scope\n\n{FILE_SCOPE}\n\n"
            "## Acceptance\n\n{ACCEPTANCE}\n\n"
            "## Verification\n\n{VERIFICATION}\n"
        )

    repl = {
        "{TASK_ID}": task_id,
        "{TASK_REFERENCE}": f"{feature_dir} :: {task_id}",
        "{WORKER_ROLE}": worker_role,
        "{AGENT_ID}": agent_id,
        "{DISPATCH_ID}": str(dispatch_id),
        "{FEATURE_DIR}": feature_dir,
        "{TASK_TITLE}": task_title or "(see tasks.md)",
        "{FILE_SCOPE}": file_scope or "(see tasks.md File Scope column)",
        "{ACCEPTANCE}": acceptance or "(see spec.md acceptance criteria)",
        "{VERIFICATION}": verification or "Run the tests named in the validation contract.",
        "{ALLOWED_FILE_001}": file_scope or "(see tasks.md)",
        "{ALLOWED_FILE_002}": "",
        "{BLOCKED_FILE_001}": "",
        "{BLOCKED_FILE_002}": "",
        "{AC_001}": acceptance or "",
        "{AC_002}": "",
        "{AC_003}": "",
        "{CONSTRAINT_001}": "Do not modify files outside the allowed scope.",
        "{CONSTRAINT_002}": "Do not add new dependencies without escalating.",
        "{RELEVANT_SPEC_EXCERPT_ONLY}": f"See {feature_dir}/spec.md for full context.",
        "{WHAT_CHANGED}": "<fill in on completion>",
        "{FILE_001}": "<fill in on completion>",
        "{COMMAND}": verification or "<fill in on completion>",
        "{PASS_FAIL}": "<PASS|FAIL>",
        "{NONE_OR_ISSUE}": "<NONE or describe>",
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def write_packet(*, pi: str, dispatch_id: int, content: str,
                 dispatches_root: Path = DISPATCHES_DIR) -> Path:
    target_dir = dispatches_root / pi
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{dispatch_id:06d}.md"
    target.write_text(content, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------- #
# Subcommand: dispatch
# ---------------------------------------------------------------------------- #

def cmd_dispatch(args: argparse.Namespace) -> int:
    agents = load_agents(Path(args.roster) if args.roster else ROSTER_PATH)
    try:
        agent = resolve_agent(args.agent, agents)
    except KeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    feature_dir = Path(args.feature).resolve()
    feature_rel = (feature_dir.relative_to(SDD_ROOT.parent).as_posix()
                   if SDD_ROOT.parent in feature_dir.parents or feature_dir == SDD_ROOT.parent
                   else feature_dir.as_posix())

    scrape = extract_task_row(feature_dir, args.task)
    title = args.title or scrape["title"] or args.task
    file_scope = args.file_scope or scrape["file_scope"]
    acceptance = scrape["acceptance"]
    verification = args.verification or "Run the tests named in the validation contract."

    db_path = Path(args.db) if args.db else DEFAULT_DB
    values = {
        "dispatched_at": ledger_cli.utc_now(),
        "pi": args.pi,
        "sprint": args.sprint,
        "feature_dir": feature_rel,
        "task_id": args.task,
        "task_title": title,
        "agent_id": agent["id"],
        "agent_role": agent.get("role") or agent.get("kind") or "unknown",
        "outcome": None,
        "outcome_at": None,
        "notes": args.notes,
    }
    dispatch_id = ledger_cli.record_dispatch(db_path, values)

    packet = render_packet(
        dispatch_id=dispatch_id, task_id=args.task, task_title=title,
        worker_role=values["agent_role"], agent_id=agent["id"],
        feature_dir=feature_rel, file_scope=file_scope,
        acceptance=acceptance, verification=verification,
    )
    dispatches_root = Path(args.dispatches_dir) if args.dispatches_dir else DISPATCHES_DIR
    packet_path = write_packet(pi=args.pi, dispatch_id=dispatch_id,
                               content=packet, dispatches_root=dispatches_root)

    print(f"Dispatch #{dispatch_id} recorded.")
    print(f"Packet:  {packet_path}")
    print(f"Agent:   {agent['id']} ({values['agent_role']})")
    print(f"PI:      {args.pi}  Sprint: {args.sprint or '-'}")
    print(f"Feature: {feature_rel}")
    print(f"Task:    {args.task} -- {title}")
    return 0


# ---------------------------------------------------------------------------- #
# Subcommand: mark-outcome
# ---------------------------------------------------------------------------- #

def cmd_mark_outcome(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else DEFAULT_DB
    ok = ledger_cli.mark_outcome(db_path, args.dispatch_id, args.outcome, ledger_cli.utc_now())
    if not ok:
        print(f"ERROR: no dispatch with id {args.dispatch_id}", file=sys.stderr)
        return 3
    print(f"Dispatch #{args.dispatch_id} marked {args.outcome}.")
    return 0


# ---------------------------------------------------------------------------- #
# Subcommand: status
# ---------------------------------------------------------------------------- #

def cmd_status(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else DEFAULT_DB
    import sqlite3
    if not db_path.is_file():
        # No ledger yet -> behave as empty
        print("no in-flight dispatches")
        return 0
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = list(conn.execute(
            "SELECT id, dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
            "agent_id, agent_role, outcome, outcome_at FROM dispatches "
            "WHERE outcome IS NULL ORDER BY dispatched_at, id"
        ).fetchall())
    if not rows:
        print("no in-flight dispatches")
        return 0
    ledger_cli.print_dispatch_table(rows)
    return 0


# ---------------------------------------------------------------------------- #
# Subcommand: list
# ---------------------------------------------------------------------------- #

def cmd_list(args: argparse.Namespace) -> int:
    db_path = Path(args.db) if args.db else DEFAULT_DB
    if args.feature:
        rows = ledger_cli.fetch_dispatches(db_path, "feature_dir", args.feature)
    elif args.pi:
        rows = ledger_cli.fetch_dispatches(db_path, "pi", args.pi)
    else:
        print("ERROR: pass --pi PI-N and/or --feature <dir>", file=sys.stderr)
        return 2
    ledger_cli.print_dispatch_table(rows)
    return 0


# ---------------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------------- #

def _common_db(p: argparse.ArgumentParser) -> None:
    p.add_argument("--db", default=None, help="Path to fleet.db (default: ledger/fleet.db).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fleet.py",
        description="Fleet CLI: dispatch packet generation + ledger writes (SDD-003).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_disp = sub.add_parser("dispatch", help="Emit a packet and record a dispatch.")
    _common_db(p_disp)
    p_disp.add_argument("--task", required=True, help="Task id, e.g. T-001.")
    p_disp.add_argument("--agent", required=True, help="Agent id from roster (e.g. developer-general).")
    p_disp.add_argument("--feature", required=True, help="Feature dir path (relative or absolute).")
    p_disp.add_argument("--pi", required=True, help="Program increment, e.g. PI-2.")
    p_disp.add_argument("--sprint", default=None, help="Sprint label, e.g. A.")
    p_disp.add_argument("--title", default=None, help="Override task title (otherwise scraped from tasks.md).")
    p_disp.add_argument("--file-scope", default=None, help="Override allowed-files scope text.")
    p_disp.add_argument("--verification", default=None, help="Override verification command text.")
    p_disp.add_argument("--notes", default=None, help="Optional notes column.")
    p_disp.add_argument("--roster", default=None, help="Override roster JSON path (testing).")
    p_disp.add_argument("--dispatches-dir", default=None, help="Override dispatches output dir (testing).")

    p_mark = sub.add_parser("mark-outcome", help="Set outcome on a dispatch id.")
    _common_db(p_mark)
    p_mark.add_argument("dispatch_id", type=int)
    p_mark.add_argument("--outcome", choices=OUTCOMES, required=True)

    p_stat = sub.add_parser("status", help="List in-flight dispatches (no outcome yet).")
    _common_db(p_stat)

    p_list = sub.add_parser("list", help="List dispatches by --pi and/or --feature.")
    _common_db(p_list)
    p_list.add_argument("--pi", default=None)
    p_list.add_argument("--feature", default=None)

    return parser


HANDLERS = {
    "dispatch": cmd_dispatch,
    "mark-outcome": cmd_mark_outcome,
    "status": cmd_status,
    "list": cmd_list,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = HANDLERS[args.cmd]
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
