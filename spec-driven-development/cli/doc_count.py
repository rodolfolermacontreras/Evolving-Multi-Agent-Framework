#!/usr/bin/env python3
"""Doc-count rollup (SDD-FDC-001 / R3, R4).

Walks spec-driven-development/specs and sprints, parses YAML frontmatter via
the shared schema_lint.parse_frontmatter, and rolls counts up by status and by
type. Pure, additive, never touches the locked S1 functions.

Extracted from state_builder.py under SDD-048 C-1 (T-048-02). The function
bodies are byte-identical to the originals; state_builder.py re-exports the
public names so existing imports (`from cli.state_builder import build_doc_count`)
keep resolving. Style: pure Python stdlib (LESSON-001).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Shared-parser boundary (ADR-012): reuse the schema_lint frontmatter parser
# and contract enums via the established in-tree sibling bootstrap.
CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))
from schema_lint import (  # noqa: E402  -- module-bootstrap import per ADR-012
    parse_frontmatter,
    ARTIFACT_TYPE_ENUM,
    ARTIFACT_STATUS_ENUM,
    ARTIFACT_SKIP_NAMES,
    ARTIFACT_SKIP_PREFIXES,
)


def _iter_in_scope_artifacts(sdd_root: Path):
    """Yield in-scope *.md files under specs/** and sprints/**, applying the
    schema_lint skip list (templates, _-prefixed files).
    """
    for sub in ("specs", "sprints"):
        base = sdd_root / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name in ARTIFACT_SKIP_NAMES:
                continue
            if any(p.name.startswith(prefix) for prefix in ARTIFACT_SKIP_PREFIXES):
                continue
            yield p


def _resolve_sprint_id(path: Path, sdd_root: Path) -> str | None:
    """Infer the sprint id from an artifact path.

    Returns the path segment under spec-driven-development/sprints/<sprint-id>/...
    when the artifact lives under sprints/, otherwise None. Spec artifacts are
    not associated with a sprint by this helper.
    """
    try:
        rel = path.resolve().relative_to(sdd_root.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "sprints":
        return parts[1]
    return None


def build_doc_count(sdd_root: Path, sprint: str | None = None) -> dict:
    """Walk specs/** + sprints/**, parse frontmatter, return the rollup.

    Stable contract (R3):
        {
            "by_status": {<status>: int, ...},
            "by_type":   {<type>: int, ...},
            "total":     int,
        }

    Zero-count policy: every key from ARTIFACT_STATUS_ENUM and ARTIFACT_TYPE_ENUM
    is seeded with 0 before counting. This makes the output shape stable for
    dashboard consumers regardless of which values appear in the tree.

    When `sprint` is supplied, only artifacts whose resolved sprint matches are
    counted; the top-level shape is unchanged.

    A frontmatter parse that yields {} (no YAML delimiters or unparseable) is
    SKIPPED rather than crashing -- it is the lint's job to flag such files.
    Out-of-enum `type` or `status` values are also skipped (lint flags them).
    """
    by_status = {k: 0 for k in sorted(ARTIFACT_STATUS_ENUM)}
    by_type = {k: 0 for k in sorted(ARTIFACT_TYPE_ENUM)}

    for path in _iter_in_scope_artifacts(sdd_root):
        if sprint is not None:
            path_sprint = _resolve_sprint_id(path, sdd_root)
            if path_sprint != sprint:
                continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = parse_frontmatter(text)
        if not fm:
            continue  # missing/unparseable: lint reports it, count skips it
        t = fm.get("type")
        s = fm.get("status")
        # Count each artifact at most once on each axis. An artifact missing
        # either field, or carrying out-of-enum values, is silently skipped
        # (the lint already reports it). Without this guard the
        # total == sum(by_status) == sum(by_type) invariant could break.
        if not (isinstance(t, str) and t.strip() in ARTIFACT_TYPE_ENUM):
            continue
        if not (isinstance(s, str) and s.strip() in ARTIFACT_STATUS_ENUM):
            continue
        by_type[t.strip()] += 1
        by_status[s.strip()] += 1

    total = sum(by_status.values())
    # Invariant check: each counted artifact contributes exactly one of each axis.
    assert total == sum(by_type.values()), (
        f"build_doc_count invariant violated: "
        f"sum(by_status)={total} sum(by_type)={sum(by_type.values())}"
    )
    return {"by_status": by_status, "by_type": by_type, "total": total}


def build_doc_count_by_sprint(sdd_root: Path) -> dict:
    """Return {<sprint_id>: <flat contract>} for each sprint directory under sprints/.

    Sprint directories are immediate children of spec-driven-development/sprints/.
    Spec artifacts (under specs/) are not associated with a sprint and are
    excluded from this view.
    """
    sprints_dir = sdd_root / "sprints"
    if not sprints_dir.is_dir():
        return {}
    out: dict = {}
    for child in sorted(sprints_dir.iterdir()):
        if not child.is_dir():
            continue
        sprint_id = child.name
        out[sprint_id] = build_doc_count(sdd_root, sprint=sprint_id)
    return out


def render_count_table(rollup: dict) -> str:
    """Render a flat rollup dict as a human-readable table.

    Format (stdlib only, no third-party tabulate dependency):

        BY STATUS                BY TYPE
          status         count     type            count
          -------------- -----     --------------- -----
          active             3     spec                4
          ...                       ...
                                  TOTAL             N

    The leading two-space indent is for stable alignment under section headers.
    """
    by_status = rollup.get("by_status", {})
    by_type = rollup.get("by_type", {})
    total = rollup.get("total", 0)

    status_rows = [(k, by_status[k]) for k in sorted(by_status.keys())]
    type_rows = [(k, by_type[k]) for k in sorted(by_type.keys())]

    lines: list[str] = []
    lines.append("Document count rollup")
    lines.append("")
    lines.append("BY STATUS")
    lines.append(f"  {'status':<16}{'count':>6}")
    lines.append(f"  {'-' * 16}{'-' * 6}")
    for name, count in status_rows:
        lines.append(f"  {name:<16}{count:>6}")
    lines.append("")
    lines.append("BY TYPE")
    lines.append(f"  {'type':<16}{'count':>6}")
    lines.append(f"  {'-' * 16}{'-' * 6}")
    for name, count in type_rows:
        lines.append(f"  {name:<16}{count:>6}")
    lines.append("")
    lines.append(f"TOTAL: {total}")
    return "\n".join(lines) + "\n"


def cmd_count(args: argparse.Namespace, sdd_root: Path) -> int:
    """Handler for `state_builder.py count`. CLI-PATTERN rule 9 (own handler)."""
    sprint = getattr(args, "sprint", None)
    by_sprint_flag = getattr(args, "by_sprint", False)
    fmt = getattr(args, "format", "json")

    rollup = build_doc_count(sdd_root, sprint=sprint)

    if by_sprint_flag:
        rollup["by_sprint"] = build_doc_count_by_sprint(sdd_root)

    if fmt == "table":
        # Tables suppress the by_sprint nested map (would be a wall of text).
        # JSON output remains the source of truth for the nested view.
        print(render_count_table(rollup), end="")
    else:
        print(json.dumps(rollup, indent=2, default=str))
    return 0
