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

_CLI_DIR = SDD_ROOT / "cli"
if str(_CLI_DIR) not in sys.path:
    sys.path.insert(0, str(_CLI_DIR))

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

# Article XI ratification cutover (SDD-019.R8 grandfather migration).
# Spec dirs whose CLARIFY/SPEC frontmatter `updated` field is strictly older
# than this date are treated as grandfathered lock holders and are not
# retroactively blocked. See specs/2026-06-09-sprint-6-completion/.
#
# SDD-048 C-3: the live cutover is sourced from `project.config.json`
# (`article_xi_cutover`) so a host-project owner can override it without
# editing CLI code. This constant is the FALLBACK used only when the config
# file or field is absent or unreadable; do not delete it.
ARTICLE_XI_CUTOVER = "2026-06-08"

# Repo-root config (sibling of SDD_ROOT) holding host-project identity + knobs.
_PROJECT_CONFIG = SDD_ROOT.parent / "project.config.json"


def _resolve_article_xi_cutover(config_path: Path | None = None) -> str:
    """Resolve the Article XI grandfather cutover (``YYYY-MM-DD``).

    Reads the ``article_xi_cutover`` field from ``project.config.json`` via the
    stdlib ``json`` module. Falls back to the :data:`ARTICLE_XI_CUTOVER`
    constant when the config file or field is missing or unreadable, so the
    scanner never crashes on a host project that has not set the field.
    """
    path = config_path if config_path is not None else _PROJECT_CONFIG
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return ARTICLE_XI_CUTOVER
    value = data.get("article_xi_cutover") if isinstance(data, dict) else None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return ARTICLE_XI_CUTOVER


# Config-sourced cutover used as the default everywhere the scanner runs.
RESOLVED_ARTICLE_XI_CUTOVER = _resolve_article_xi_cutover()


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


# File-overlap conflict detector (SDD-049) ---------------------------------- #

# File Scope cell values that name no real file (placeholders / "none").
_NON_FILE_SCOPE_TOKENS = frozenset(
    {"(see tasks.md)", "see tasks.md", "none", "n/a", "na", "-", "--", "tbd"}
)


def parse_file_scope(file_scope: str) -> set[str]:
    """Parse a tasks.md ``File Scope`` cell into a normalized set of file paths.

    Mirrors ``render_brief`` parsing: split on ``,`` or ``;``, strip whitespace
    and surrounding backticks, drop empties and placeholder/"none" tokens. The
    result is the task's declared IN-scope file set used for overlap detection.
    """
    items: set[str] = set()
    for raw in re.split(r"[,;]", file_scope or ""):
        item = raw.strip().strip("`").strip()
        if not item:
            continue
        if item.lower() in _NON_FILE_SCOPE_TOKENS:
            continue
        items.add(item)
    return items


def detect_file_overlaps(batch: list[tuple[str, str]]) -> list[dict]:
    """Detect pairwise IN-scope file overlaps across a dispatch *batch*.

    *batch* is a list of ``(task_id, file_scope_string)`` pairs. Returns one
    conflict dict per overlapping unordered task pair, in stable order:
    ``{"task_a": str, "task_b": str, "shared": [sorted file paths]}``.
    Tasks with empty or placeholder scopes never conflict (the tool cannot
    know their real footprint).
    """
    scopes = [(tid, parse_file_scope(scope)) for tid, scope in batch]
    conflicts: list[dict] = []
    for i in range(len(scopes)):
        tid_a, set_a = scopes[i]
        for j in range(i + 1, len(scopes)):
            tid_b, set_b = scopes[j]
            shared = set_a & set_b
            if shared:
                conflicts.append(
                    {"task_a": tid_a, "task_b": tid_b, "shared": sorted(shared)}
                )
    return conflicts


def format_overlap_report(conflicts: list[dict]) -> str:
    """Render *conflicts* (from ``detect_file_overlaps``) as an indented list."""
    return "\n".join(
        f"  - {c['task_a']} and {c['task_b']} both declare: "
        f"{', '.join(c['shared'])}"
        for c in conflicts
    )



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

    # SDD-049: pre-dispatch file-overlap conflict detector. Runs BEFORE any
    # brief or ledger row is written, so a blocked batch leaves no side effects.
    conflicts = detect_file_overlaps(
        [(tid, task.get("file_scope", "")) for tid, task in resolved]
    )
    if conflicts:
        report = format_overlap_report(conflicts)
        if getattr(args, "allow_overlap", False):
            print(
                "WARNING: file-overlap conflict(s) detected in this dispatch "
                "batch; proceeding because --allow-overlap was set:\n"
                f"{report}",
                file=sys.stderr,
            )
        else:
            raise FleetError(
                "file-overlap conflict(s) detected in this dispatch batch -- "
                "two or more tasks declare the same IN-scope file. Dispatch "
                "blocked before any brief or ledger row was written:\n"
                f"{report}\n"
                "Split the overlapping file(s) into serial tasks, or pass "
                "--allow-overlap to dispatch anyway (deliberate override)."
            )

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


# --------------------------------------------------------------------------- #
# Lock-state scanner (SDD-019) -- serial gate at CLARIFY and SPEC
# --------------------------------------------------------------------------- #

def _scan_lock_state(specs_root: Path) -> dict:
    """Walk specs/ and derive lock holders from frontmatter.

    Returns {"clarify_holder": feature_name | None,
             "spec_holder": feature_name | None}.
    """
    from schema_lint import parse_frontmatter  # noqa: E402 -- sibling import

    clarify_holder: str | None = None
    spec_holder: str | None = None

    if not specs_root.is_dir():
        return {"clarify_holder": None, "spec_holder": None}

    for spec_dir in sorted(specs_root.iterdir()):
        if not spec_dir.is_dir():
            continue
        feature_name = spec_dir.name

        # Check clarify lock: clarify.md or clarification-log.md status != done
        if clarify_holder is None:
            for clarify_name in ("clarify.md", "clarification-log.md"):
                clarify_path = spec_dir / clarify_name
                if clarify_path.is_file():
                    text = clarify_path.read_text(encoding="utf-8")
                    fm = parse_frontmatter(text)
                    status = fm.get("status", "").strip("'\"" ).lower()
                    if status and status != "done":
                        clarify_holder = feature_name
                    break  # only check first found

        # Check spec lock: spec.md status == draft
        if spec_holder is None:
            spec_path = spec_dir / "spec.md"
            if spec_path.is_file():
                text = spec_path.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                status = fm.get("status", "").strip("'\"" ).lower()
                if status == "draft":
                    spec_holder = feature_name

    return {"clarify_holder": clarify_holder, "spec_holder": spec_holder}


def _check_serial_gate(feature_dir: Path, phase: str | None = None) -> int:
    """Pre-dispatch serial gate check.

    Returns 0 if dispatch is allowed, 1 if blocked.
    *phase* may be inferred from the feature's frontmatter or passed explicitly.
    """
    specs_root = SDD_ROOT / "specs"
    if not specs_root.is_dir():
        return 0

    feature_name = feature_dir.resolve().name

    # Infer phase from feature dir frontmatter if not given
    if phase is None:
        for clarify_name in ("clarify.md", "clarification-log.md"):
            clarify_path = feature_dir / clarify_name
            if clarify_path.is_file():
                from schema_lint import parse_frontmatter
                fm = parse_frontmatter(clarify_path.read_text(encoding="utf-8"))
                status = fm.get("status", "").strip("'\"").lower()
                if status and status != "done":
                    phase = "clarify"
                    break
        if phase is None:
            spec_path = feature_dir / "spec.md"
            if spec_path.is_file():
                from schema_lint import parse_frontmatter
                fm = parse_frontmatter(spec_path.read_text(encoding="utf-8"))
                status = fm.get("status", "").strip("'\"").lower()
                if status == "draft":
                    phase = "spec"

    # Post-SPEC phases are not gated
    if phase not in ("clarify", "spec"):
        return 0

    lock_state = _scan_lock_state(specs_root)

    if phase == "clarify":
        holder = lock_state["clarify_holder"]
        if holder and holder != feature_name:
            print(
                f"ERROR: CLARIFY lock held by '{holder}'. "
                f"Feature '{feature_name}' cannot enter CLARIFY concurrently. "
                f"Use `fleet.py lock force-release {holder} --reason ...` to override.",
                file=sys.stderr,
            )
            return 1
    elif phase == "spec":
        holder = lock_state["spec_holder"]
        if holder and holder != feature_name:
            print(
                f"ERROR: SPEC lock held by '{holder}'. "
                f"Feature '{feature_name}' cannot enter SPEC concurrently. "
                f"Use `fleet.py lock force-release {holder} --reason ...` to override.",
                file=sys.stderr,
            )
            return 1

    return 0


# --------------------------------------------------------------------------- #
# SDD-019.R7 / R8 -- priority-weighted FIFO queue + grandfather migration
# (SDD-032 / 2026-06-09-sprint-6-completion)
# --------------------------------------------------------------------------- #


_PRIORITY_RANK = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}


def _lookup_backlog_priority(feature_id: str, backlog_path: Path | None = None) -> str:
    """Return the BACKLOG.md priority (`P1`/`P2`/`P3`/`P4`) for *feature_id*.

    Scans `backlog/BACKLOG.md` for a markdown table row whose first cell starts
    with *feature_id* (e.g. ``SDD-032``). Falls back to ``"P3"`` if not found
    or unparseable (the least-urgent default, per plan.md "Risk Assessment").
    """
    if backlog_path is None:
        backlog_path = SDD_ROOT / "backlog" / "BACKLOG.md"
    if not feature_id or not backlog_path.is_file():
        return "P3"
    try:
        text = backlog_path.read_text(encoding="utf-8")
    except OSError:
        return "P3"
    fid = feature_id.strip()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        # Match: first cell is exactly the feature_id, or starts with it followed
        # by whitespace/punctuation (e.g. "SDD-032" vs "SDD-032-foo" -- only the
        # exact-ID case wins).
        first = cells[0]
        if first == fid or first.startswith(fid + " ") or first.startswith(fid + ","):
            # Priority is the 4th column in the standard backlog layout
            # (| ID | Title | Priority | ... |). Find the first cell that matches
            # P1/P2/P3/P4 in the row to be robust against minor schema drift.
            for cell in cells[1:]:
                token = cell.strip()
                if token in _PRIORITY_RANK:
                    return token
            return "P3"
    return "P3"


def _compute_queue_order(
    entries: list[tuple[str, str, str]],
) -> list[tuple[str, str, str]]:
    """Order queued features by priority then FIFO submission timestamp.

    *entries* is a list of ``(feature_name, priority, updated)`` tuples where
    *priority* is one of ``P1`` / ``P2`` / ``P3`` / ``P4`` (unknown -> P3) and
    *updated* is an ISO-8601 date string (``YYYY-MM-DD``). Returns the same
    list sorted so the next-to-acquire feature is first: highest priority
    wins; equal-priority entries break ties by earliest *updated* (FIFO).
    """
    def _key(item: tuple[str, str, str]) -> tuple[int, str, str]:
        feature, priority, updated = item
        rank = _PRIORITY_RANK.get((priority or "").strip(), _PRIORITY_RANK["P3"])
        return (rank, updated or "", feature)
    return sorted(entries, key=_key)


def _is_grandfathered(
    spec_dir: Path,
    cutover: str = RESOLVED_ARTICLE_XI_CUTOVER,
) -> bool:
    """Return True if *spec_dir* predates the Article XI cutover.

    Reads the ``updated`` frontmatter field from ``clarify.md`` and ``spec.md``
    (whichever exist) and returns True if any value is strictly older than
    *cutover* (``YYYY-MM-DD``). Grandfathered spec dirs are treated as
    implicit lock holders by the scanner and are not retroactively blocked.
    Spec dirs created on or after the cutover get normal lock treatment.
    """
    from schema_lint import parse_frontmatter  # noqa: E402 -- sibling import

    if not spec_dir.is_dir():
        return False
    for name in ("clarify.md", "clarification-log.md", "spec.md"):
        path = spec_dir / name
        if not path.is_file():
            continue
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        updated = fm.get("updated", "").strip("'\" ").strip()
        # Compare as ISO-8601 date strings (lexical sort matches calendar sort).
        if updated and updated < cutover:
            return True
    return False


def cmd_lock_status(args: argparse.Namespace) -> int:
    """Print current lock holders."""
    specs_root = Path(args.specs_root) if getattr(args, "specs_root", None) else SDD_ROOT / "specs"
    state = _scan_lock_state(specs_root)
    clarify = state["clarify_holder"]
    spec = state["spec_holder"]
    print(f"CLARIFY lock: {clarify or '(free)'}")
    print(f"SPEC lock:    {spec or '(free)'}")

    # SDD-019.R7 + R8 -- additive surface (SDD-032 / O2 close).
    # Existing prints above stay byte-identical; the queue + grandfather
    # sections are appended after, never inline.
    if specs_root.is_dir():
        from schema_lint import parse_frontmatter  # noqa: E402 -- sibling

        for phase, holder, status_check in (
            ("CLARIFY", clarify, lambda s: bool(s) and s != "done"),
            ("SPEC", spec, lambda s: s == "draft"),
        ):
            queued: list[tuple[str, str, str]] = []
            for sd in sorted(specs_root.iterdir()):
                if not sd.is_dir() or sd.name == holder:
                    continue
                fm: dict = {}
                for name in (
                    ("clarify.md", "clarification-log.md") if phase == "CLARIFY"
                    else ("spec.md",)
                ):
                    p = sd / name
                    if p.is_file():
                        try:
                            fm = parse_frontmatter(p.read_text(encoding="utf-8"))
                        except OSError:
                            fm = {}
                        break
                status = fm.get("status", "").strip("'\" ").lower()
                if not status_check(status):
                    continue
                feature_id = _extract_feature_id(sd)
                priority = _lookup_backlog_priority(feature_id) if feature_id else "P3"
                updated = fm.get("updated", "").strip("'\" ").strip()
                queued.append((sd.name, priority, updated))
            if queued:
                ordered = _compute_queue_order(queued)
                print(f"{phase} queue:")
                for feature, priority, updated in ordered:
                    print(f"  - {feature} ({priority}, updated={updated or 'n/a'})")

        grandfathered = [
            sd.name for sd in sorted(specs_root.iterdir())
            if sd.is_dir() and _is_grandfathered(sd)
        ]
        if grandfathered:
            print("Grandfathered (pre-Article-XI; not retroactively blocked):")
            for name in grandfathered:
                print(f"  - {name}")

    return 0


def _extract_feature_id(spec_dir: Path) -> str | None:
    """Best-effort extraction of an SDD-NNN backlog ID from *spec_dir*.

    Reads spec.md body text for a line containing ``Spec ID: SDD-NNN`` or
    falls back to scanning for any ``SDD-\\d+`` token in the spec body.
    Returns the matched token (e.g. ``SDD-032``) or None.
    """
    spec_md = spec_dir / "spec.md"
    if not spec_md.is_file():
        return None
    try:
        text = spec_md.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"Spec ID:\s*(SDD-\d+)", text)
    if m:
        return m.group(1)
    m = re.search(r"\bSDD-\d{3}\b", text)
    if m:
        return m.group(0)
    return None


def cmd_lock_force_release(args: argparse.Namespace) -> int:
    """Force-release a lock for a feature with a mandatory reason."""
    db_path = Path(args.db) if args.db else DEFAULT_DB
    feature = args.feature
    reason = args.reason

    if not reason or not reason.strip():
        print("ERROR: --reason is mandatory for force-release.", file=sys.stderr)
        return 1

    # Write ledger row
    try:
        values = {
            "dispatched_at": utc_now(),
            "pi": "N/A",
            "sprint": None,
            "feature_dir": feature,
            "task_id": "LOCK-FORCE-RELEASE",
            "task_title": f"Force-release lock for {feature}",
            "agent_id": "human",
            "agent_role": "operator",
            "outcome": "success",
            "outcome_at": utc_now(),
            "notes": f"force-release reason: {reason}",
        }
        record_dispatch(db_path, values)
    except Exception as exc:
        print(f"WARNING: Could not write ledger row: {exc}", file=sys.stderr)

    print(f"Lock force-released for '{feature}'. Reason: {reason}")
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
    p_disp.add_argument(
        "--allow-overlap",
        action="store_true",
        help="Dispatch even if tasks in the batch declare the same IN-scope "
             "file (deliberate override; default blocks on overlap, SDD-049).",
    )

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

    # lock (SDD-019)
    p_lock = sub.add_parser("lock", help="Serial gate lock management (SDD-019).")
    lock_sub = p_lock.add_subparsers(dest="lock_command", required=True)

    lock_sub.add_parser("status", help="Show current CLARIFY/SPEC lock holders.")

    p_force = lock_sub.add_parser(
        "force-release",
        help="Force-release a lock with mandatory --reason.",
    )
    p_force.add_argument("feature", help="Feature name to release lock for.")
    p_force.add_argument("--reason", required=True, help="Mandatory reason for force-release.")
    p_force.add_argument("--db", default=None, help="Path to fleet.db.")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    handlers = {
        "dispatch": cmd_dispatch,
        "mark": cmd_mark,
        "status": cmd_status,
    }
    if args.command == "lock":
        lock_handlers = {
            "status": cmd_lock_status,
            "force-release": cmd_lock_force_release,
        }
        try:
            return lock_handlers[args.lock_command](args)
        except FleetError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    try:
        return handlers[args.command](args)
    except FleetError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
