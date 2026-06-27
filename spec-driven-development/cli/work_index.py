"""PI INDEX.md sprint-table builder for the SDD state dashboard.

SDD-048 C-1 extraction E3: isolates the ``build-index`` subsystem
(``build_index`` plus its ``_discover_sprints`` / ``_detect_sprint_status`` /
``_query_ledger_for_pi`` / ``_render_sprint_table`` helpers) out of the
``state_builder`` god-module into a focused sibling (R-C1-3).

Behavior is preserved verbatim. The five Article X locked functions remain
physically in ``state_builder.py``. The only facade-owned surface this module
needs is the ``StateBuilderError`` exception type. It is resolved lazily via
``_facade()`` at RAISE time rather than imported at module top so that:
  - there is no circular import at module-load time (the facade re-exports this
    module partway through its own load), and
  - the raised exception is the SAME class object the facade exposes under
    whichever import name it was loaded (``cli.state_builder`` under pytest,
    ``state_builder`` when run as a script), so ``pytest.raises`` matches.
"""

from __future__ import annotations

import importlib
import re
import sqlite3
import sys
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))


def _facade():
    """Return the already-loaded ``state_builder`` facade module.

    This module raises the facade-owned ``StateBuilderError``. Resolving it
    lazily here -- rather than importing at module top -- avoids a circular
    import (the facade re-exports this module) and reuses whichever facade
    instance is already in ``sys.modules``, guaranteeing the raised exception
    is the same class object the caller caught. ``importlib.import_module`` is
    the stdlib fallback for the unusual case where neither name is loaded yet.
    """
    return (sys.modules.get("cli.state_builder")
            or sys.modules.get("state_builder")
            or importlib.import_module("state_builder"))


# ---------------------------------------------------------------------------- #
# build-index: regenerate sprint table in a PI INDEX.md
# ---------------------------------------------------------------------------- #

_SPRINT_DIR_RE = re.compile(r"^Sprint-(\d+)-(.+)$")
_MARKER_BEGIN = "<!-- BEGIN auto-generated:sprints"
_MARKER_END = "<!-- END auto-generated:sprints -->"


def _discover_sprints(pi_dir: Path) -> list[dict]:
    """Scan *pi_dir* for Sprint-N-title directories; return sorted list of dicts."""
    sprints: list[dict] = []
    if not pi_dir.is_dir():
        return sprints
    for child in sorted(pi_dir.iterdir()):
        if not child.is_dir():
            continue
        m = _SPRINT_DIR_RE.match(child.name)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).replace("-", " ").title()
        has_spec = (child / "SPEC.md").is_file()
        status = _detect_sprint_status(child) if has_spec else "Proposed"
        sprints.append({
            "num": num,
            "title": title,
            "folder": child.name,
            "has_spec": has_spec,
            "status": status,
        })
    sprints.sort(key=lambda s: s["num"])
    return sprints


def _detect_sprint_status(sprint_dir: Path) -> str:
    """Read SPEC.md frontmatter or first 20 lines for a status value."""
    spec_path = sprint_dir / "SPEC.md"
    if not spec_path.is_file():
        return "Proposed"
    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError:
        return "Unknown"
    lines = text.splitlines()

    # Check YAML frontmatter first (between --- markers)
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.lower().startswith("status:"):
                return line.split(":", 1)[1].strip()

    # Fallback: scan first 20 lines for status keywords
    head = "\n".join(lines[:20])
    for keyword in ("DONE", "BLOCKED", "In-Flight", "Proposed", "Draft"):
        if keyword in head:
            return keyword
    return "Unknown"


def _query_ledger_for_pi(sdd_root: Path, pi: str) -> dict[int, dict]:
    """Query fleet.db for dispatch counts and last outcome per sprint in *pi*.

    Returns {sprint_num: {"count": int, "last_outcome": str}}.
    """
    db_path = sdd_root / "ledger" / "fleet.db"
    result: dict[int, dict] = {}
    if not db_path.is_file():
        return result
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT sprint, outcome FROM dispatches WHERE pi = ? ORDER BY id",
            (pi,),
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        return result

    # Sprint column may be "Sprint A", "S5", "Sprint-5", etc.
    sprint_num_re = re.compile(r"(\d+)")
    for row in rows:
        sprint_val = row["sprint"] or ""
        m = sprint_num_re.search(sprint_val)
        if not m:
            continue
        snum = int(m.group(1))
        if snum not in result:
            result[snum] = {"count": 0, "last_outcome": "--"}
        result[snum]["count"] += 1
        if row["outcome"]:
            result[snum]["last_outcome"] = row["outcome"]
    return result


def _render_sprint_table(sprints: list[dict], ledger_data: dict[int, dict]) -> str:
    """Render the markdown table for sprint rows."""
    lines = [
        "| Sprint | Title | Status | Dispatches | Last Outcome | Detail |",
        "|--------|-------|--------|------------|--------------|--------|",
    ]
    for s in sprints:
        num = s["num"]
        ld = ledger_data.get(num, {"count": 0, "last_outcome": "--"})
        detail_link = f"[{s['folder']}]({s['folder']}/)"
        lines.append(
            f"| {num} | {s['title']} | {s['status']} "
            f"| {ld['count']} | {ld['last_outcome']} | {detail_link} |"
        )
    return "\n".join(lines)


def build_index(sdd_root: Path, pi: str, write: bool = True) -> dict:
    """Regenerate the sprint table in docs/Management/{pi}/INDEX.md.

    Returns a dict with keys: pi, sprints_found, wrote, table_content.
    Raises StateBuilderError on expected failures.
    """
    pi_dir = sdd_root / "docs" / "Management" / pi
    index_path = pi_dir / "INDEX.md"

    if not pi_dir.is_dir():
        raise _facade().StateBuilderError(f"PI directory not found: {pi_dir}")
    if not index_path.is_file():
        raise _facade().StateBuilderError(f"INDEX.md not found: {index_path}")

    # Discover sprints and query ledger
    sprints = _discover_sprints(pi_dir)
    ledger_data = _query_ledger_for_pi(sdd_root, pi)

    # Render the table
    table_content = _render_sprint_table(sprints, ledger_data)

    # Build the full marker block
    marker_header = f"{_MARKER_BEGIN} (refreshed by `cli/state_builder.py build-index`) -->"
    block = f"{marker_header}\n{table_content}\n{_MARKER_END}"

    # Read existing INDEX.md and replace the marker block
    original = index_path.read_text(encoding="utf-8")

    begin_idx = original.find(_MARKER_BEGIN)
    end_idx = original.find(_MARKER_END)

    if begin_idx == -1 or end_idx == -1:
        raise _facade().StateBuilderError(
            f"Marker block not found in {index_path}. "
            f"Expected {_MARKER_BEGIN!r} and {_MARKER_END!r}."
        )

    # end_idx points to the start of the END marker; include its full text
    end_idx += len(_MARKER_END)
    updated = original[:begin_idx] + block + original[end_idx:]

    wrote_path = None
    if write:
        index_path.write_text(updated, encoding="utf-8")
        wrote_path = str(index_path)

    return {
        "pi": pi,
        "sprints_found": len(sprints),
        "wrote": wrote_path,
        "table_content": table_content,
    }
