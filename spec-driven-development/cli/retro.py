#!/usr/bin/env python3
"""Sprint retrospective generator.

Collects dispatch metrics from fleet.db, scans completed features,
reads lessons, and produces a structured Markdown retrospective document.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_LEDGER_DIR = Path(__file__).resolve().parents[1] / "ledger"
if str(_LEDGER_DIR) not in sys.path:
    sys.path.insert(0, str(_LEDGER_DIR))
from init_ledger import init_ledger  # noqa: E402


class RetroError(Exception):
    """Expected retro generation failure."""


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _query_dispatch_metrics(db_path: Path, pi: str,
                            sprint: str | None = None) -> dict:
    """Return dispatch aggregate metrics for the given PI (and optional sprint)."""
    if not db_path.is_file():
        return _empty_metrics()

    with sqlite3.connect(db_path) as conn:
        where = "WHERE pi = ?"
        params: list[str] = [pi]
        if sprint:
            where += " AND sprint = ?"
            params.append(sprint)

        row = conn.execute(
            f"SELECT COUNT(*) FROM dispatches {where}", params,
        ).fetchone()
        total = row[0] if row else 0

        if total == 0:
            return _empty_metrics()

        success = conn.execute(
            f"SELECT COUNT(*) FROM dispatches {where} AND outcome = 'success'",
            params,
        ).fetchone()[0]
        failed = conn.execute(
            f"SELECT COUNT(*) FROM dispatches {where} AND outcome = 'failed'",
            params,
        ).fetchone()[0]
        blocked = conn.execute(
            f"SELECT COUNT(*) FROM dispatches {where} AND outcome = 'blocked'",
            params,
        ).fetchone()[0]
        agents = conn.execute(
            f"SELECT COUNT(DISTINCT agent_id) FROM dispatches {where}",
            params,
        ).fetchone()[0]
        features = conn.execute(
            f"SELECT COUNT(DISTINCT feature_dir) FROM dispatches {where}",
            params,
        ).fetchone()[0]

    rate = round(success / total * 100) if total else 0
    return {
        "total": total,
        "success": success,
        "failed": failed,
        "blocked": blocked,
        "agents": agents,
        "features": features,
        "rate": rate,
    }


def _empty_metrics() -> dict:
    return {
        "total": 0, "success": 0, "failed": 0, "blocked": 0,
        "agents": 0, "features": 0, "rate": 0,
    }


def _scan_delivered_features(specs_dir: Path) -> list[dict]:
    """Return list of features whose spec.md has Status: Done."""
    delivered: list[dict] = []
    if not specs_dir.is_dir():
        return delivered
    for feat_dir in sorted(specs_dir.iterdir()):
        if not feat_dir.is_dir():
            continue
        spec_file = feat_dir / "spec.md"
        if not spec_file.is_file():
            continue
        text = spec_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("- status:"):
                status = stripped.split(":", 1)[1].strip()
                if status.lower() == "done":
                    has_retro = (feat_dir / "RETRO.md").is_file()
                    evidence = "RETRO.md present" if has_retro else "Status: Done"
                    delivered.append({
                        "name": feat_dir.name,
                        "stage": "DONE",
                        "evidence": evidence,
                    })
                break
    return delivered


_LESSON_RE = re.compile(
    r"^#{2,3}\s+(LESSON-\d+)\s*[:\-\-]+\s*(.+)$", re.IGNORECASE,
)


def _parse_lessons(lessons_path: Path) -> list[dict]:
    """Parse lesson entries from a lessons.md file."""
    lessons: list[dict] = []
    if not lessons_path.is_file():
        return lessons

    text = lessons_path.read_text(encoding="utf-8")
    current: dict | None = None

    for line in text.splitlines():
        m = _LESSON_RE.match(line.strip())
        if m:
            if current:
                lessons.append(current)
            current = {"id": m.group(1), "title": m.group(2).strip(),
                       "status": "unknown", "tag": ""}
            continue
        if current:
            stripped = line.strip()
            if stripped.lower().startswith("- status:"):
                current["status"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("**status:**"):
                raw = stripped.split(":**", 1)[1].strip()
                # Normalize verbose status to canonical token
                lower = raw.lower()
                if "shipped" in lower or "ship" in lower:
                    current["status"] = "shipped"
                elif "open" in lower:
                    current["status"] = "open"
                elif "defer" in lower:
                    current["status"] = "deferred"
                else:
                    current["status"] = raw
            elif stripped.lower().startswith("- tag:"):
                current["tag"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("**tag:**"):
                current["tag"] = stripped.split(":**", 1)[1].strip()

    if current:
        lessons.append(current)
    return lessons


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def _generate_retro(pi: str, sprint: str | None, metrics: dict,
                    delivered: list[dict], lessons: list[dict]) -> str:
    """Build the retrospective Markdown document."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title_parts = [pi]
    if sprint:
        title_parts.append(sprint)
    title = " ".join(title_parts)

    lines: list[str] = []
    lines.append(f"# Sprint Retrospective: {title}")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    # -- Delivered
    lines.append("## Delivered")
    lines.append("")
    if delivered:
        lines.append("| Feature | Stage | Evidence |")
        lines.append("|---------|-------|----------|")
        for f in delivered:
            lines.append(f"| {f['name']} | {f['stage']} | {f['evidence']} |")
    else:
        lines.append("_No features reached DONE in this period._")
    lines.append("")

    # -- Signals and Evidence
    lines.append("## Signals and Evidence")
    lines.append("")
    if metrics["total"] == 0:
        lines.append("_No dispatches recorded._")
        lines.append("")
    lines.append(f"- Total dispatches: {metrics['total']}")
    lines.append(f"- Successful: {metrics['success']}")
    lines.append(f"- Failed: {metrics['failed']}")
    lines.append(f"- Blocked: {metrics['blocked']}")
    lines.append(f"- Unique agents: {metrics['agents']}")
    lines.append(f"- Unique features: {metrics['features']}")
    lines.append(f"- Dispatch success rate: {metrics['rate']}%")
    lines.append("")

    # -- Lessons Summary
    lines.append("## Lessons Summary")
    lines.append("")
    if lessons:
        lines.append("| Lesson | Status | Tag |")
        lines.append("|--------|--------|-----|")
        for le in lessons:
            lines.append(f"| {le['id']}: {le['title']} | {le['status']} | {le['tag']} |")
    else:
        lines.append("_No lessons found for this PI._")
    lines.append("")

    # -- Action Items
    lines.append("## Action Items")
    lines.append("")
    lines.append("_(to be filled by human during retro review)_")
    lines.append("")
    lines.append("1. ")
    lines.append("2. ")
    lines.append("3. ")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="retro.py",
        description="Generate a sprint retrospective from fleet ledger data, "
                    "delivered features, and lessons.",
    )
    parser.add_argument(
        "--sdd-root", required=True,
        help="Path to the spec-driven-development directory.",
    )
    parser.add_argument(
        "--pi", required=True,
        help="Program Increment identifier (e.g. PI-2).",
    )
    parser.add_argument(
        "--sprint", default=None,
        help="Sprint name to filter dispatches (e.g. 'Sprint A').",
    )
    parser.add_argument(
        "--output", default=None,
        help="Write the retro document to this file instead of stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    sdd_root = Path(args.sdd_root).resolve()

    if not sdd_root.is_dir():
        print(f"ERROR: SDD root not found: {sdd_root}", file=sys.stderr)
        return 1

    try:
        db_path = sdd_root / "ledger" / "fleet.db"
        metrics = _query_dispatch_metrics(db_path, args.pi, args.sprint)
        delivered = _scan_delivered_features(sdd_root / "specs")
        lessons_path = sdd_root / "sprints" / args.pi / "lessons.md"
        lessons = _parse_lessons(lessons_path)
        doc = _generate_retro(args.pi, args.sprint, metrics, delivered, lessons)
    except (RetroError, OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"Retro written to: {out}")
    else:
        print(doc)

    return 0


if __name__ == "__main__":
    sys.exit(main())
