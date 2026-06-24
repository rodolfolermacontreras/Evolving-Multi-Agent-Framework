#!/usr/bin/env python3
"""backlog_reorder.py -- SDD-036 display-order overlay with dependency safeguards.

CLI-PATTERN compliant (docs/CLI-PATTERN.md), stdlib only (Article V).

The reorder operation mutates an *overlay* artifact `backlog/display-order.json`
(an ordered list of feature IDs) -- it NEVER mutates `backlog/BACKLOG.md`, which
remains the PM-authoritative RICE-scored source (ADR-017, R-B). Every order
change appends exactly one row to the append-only audit log
`ledger/reorder-audit.jsonl` (AC-6). Dependency-lock (AC-5) blocks a move that
would place an item above an incomplete item it depends on, or that participates
in a dependency cycle, unless `--force` with a non-empty reason is given (AC-7).

Exit codes (CLI-PATTERN): 0 success, 1 blocked / unknown item, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# ADR-012: reuse the single stdlib frontmatter parser. Do NOT duplicate it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema_lint import parse_frontmatter, parse_depends_on  # noqa: E402

DEFAULT_SDD_ROOT = Path(__file__).resolve().parents[1]

# Locked audit row shape (AC-6 / spec.md Q-G). Order is fixed for readability.
AUDIT_FIELDS = (
    "event_type",
    "actor",
    "timestamp",
    "item_id",
    "from_rank",
    "to_rank",
    "reason",
    "dependency_check",
    "force_override",
)

_FEATURE_ID_RE = re.compile(r"\b([A-Z]{2,}-\d{2,3})\b")
_BACKLOG_ROW_RE = re.compile(r"^\|\s*([A-Z]{2,}-\d{2,3})\s*\|", re.MULTILINE)


class ReorderError(Exception):
    """Raised for a blocked move or an unknown item (exit code 1)."""


# --------------------------------------------------------------------------- #
# Path helpers
# --------------------------------------------------------------------------- #
def display_order_path(sdd_root: Path) -> Path:
    return sdd_root / "backlog" / "display-order.json"


def backlog_path(sdd_root: Path) -> Path:
    return sdd_root / "backlog" / "BACKLOG.md"


def audit_path(sdd_root: Path) -> Path:
    return sdd_root / "ledger" / "reorder-audit.jsonl"


def specs_root(sdd_root: Path) -> Path:
    return sdd_root / "specs"


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
@dataclass
class BacklogEntry:
    id: str
    done: bool


def load_backlog_entries(sdd_root: Path) -> list[BacklogEntry]:
    """Parse BACKLOG.md table rows into (id, done) in natural (top-down) order.

    A row is considered complete when its row text contains the token ``DONE``
    (the BACKLOG status convention, e.g. ``DONE (PI-5 Sprint 3, ...)``).
    """
    path = backlog_path(sdd_root)
    if not path.is_file():
        return []
    entries: list[BacklogEntry] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _BACKLOG_ROW_RE.match(line)
        if not m:
            continue
        item_id = m.group(1)
        if item_id in seen:
            continue
        seen.add(item_id)
        entries.append(BacklogEntry(id=item_id, done="DONE" in line))
    return entries


def load_order(sdd_root: Path) -> list[str]:
    """Return the current display order.

    Uses the overlay `backlog/display-order.json` when present; otherwise falls
    back to BACKLOG.md natural order (ADR-017). Any backlog IDs missing from a
    present overlay are appended (in backlog order) so the order stays complete.
    """
    natural = [e.id for e in load_backlog_entries(sdd_root)]
    path = display_order_path(sdd_root)
    if not path.is_file():
        return natural
    data = json.loads(path.read_text(encoding="utf-8"))
    order = [str(x) for x in data.get("order", [])]
    for item_id in natural:
        if item_id not in order:
            order.append(item_id)
    return order


def write_order(sdd_root: Path, order: list[str]) -> None:
    path = display_order_path(sdd_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "order": order,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_depends_map(sdd_root: Path) -> dict[str, list[str]]:
    """Build a feature-ID -> [dependency feature IDs] map from `specs/*/spec.md`.

    The dependency list comes from the optional `depends_on` frontmatter field
    (parsed via the shared stdlib parser). The owning feature ID is read from
    the spec body line ``- Feature ID: SDD-NNN`` (falling back to the first
    artifact-ID-shaped token in the body).
    """
    mapping: dict[str, list[str]] = {}
    root = specs_root(sdd_root)
    if not root.is_dir():
        return mapping
    for spec in sorted(root.glob("*/spec.md")):
        text = spec.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        deps = parse_depends_on(fm)
        if not deps:
            continue
        feature_id = _extract_feature_id(text)
        if feature_id:
            mapping[feature_id] = deps
    return mapping


def _extract_feature_id(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("- feature id:"):
            m = _FEATURE_ID_RE.search(stripped)
            if m:
                return m.group(1)
    return None


# --------------------------------------------------------------------------- #
# Dependency-lock (AC-5)
# --------------------------------------------------------------------------- #
def _has_cycle_through(node: str, graph: dict[str, list[str]]) -> bool:
    """True if following dependency edges from `node` can return to `node`."""
    seen: set[str] = set()

    def dfs(current: str) -> bool:
        for dep in graph.get(current, []):
            if dep == node:
                return True
            if dep not in seen:
                seen.add(dep)
                if dfs(dep):
                    return True
        return False

    return dfs(node)


def dependency_violations(
    item: str,
    new_order: list[str],
    depends_map: dict[str, list[str]],
    done_map: dict[str, bool],
) -> list[str]:
    """Return human-readable reasons the proposed `new_order` is illegal.

    Two safeguard classes (AC-5):
      1. Incomplete-dependency outranking: `item` placed above an incomplete
         dependency present in the order.
      2. Dependency cycle through `item`.
    An empty list means the move is legal.
    """
    reasons: list[str] = []
    if _has_cycle_through(item, depends_map):
        reasons.append(
            f"{item} participates in a dependency cycle; reorder is blocked "
            f"until the cycle is resolved"
        )
    item_rank = new_order.index(item)
    for dep in depends_map.get(item, []):
        if dep not in new_order:
            continue
        if done_map.get(dep, False):
            continue
        if item_rank < new_order.index(dep):
            reasons.append(
                f"{item} cannot be ranked above {dep}: {item} depends on {dep} "
                f"and {dep} is not yet complete"
            )
    return reasons


# --------------------------------------------------------------------------- #
# Audit (AC-6)
# --------------------------------------------------------------------------- #
def append_audit_row(
    sdd_root: Path,
    *,
    actor: str,
    item_id: str,
    from_rank: int,
    to_rank: int,
    reason: str,
    dependency_check: str,
    force_override: bool,
) -> dict:
    """Append exactly one row (locked 9-field shape) to the audit JSONL log."""
    row = {
        "event_type": "reorder",
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "item_id": item_id,
        "from_rank": from_rank,
        "to_rank": to_rank,
        "reason": reason,
        "dependency_check": dependency_check,
        "force_override": force_override,
    }
    # Emit fields in the locked order for human-readable append-only history.
    ordered = {field: row[field] for field in AUDIT_FIELDS}
    path = audit_path(sdd_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ordered) + "\n")
    return ordered


# --------------------------------------------------------------------------- #
# Move operation (AC-5 + AC-6 + AC-7)
# --------------------------------------------------------------------------- #
def move(
    sdd_root: Path,
    *,
    item: str,
    to_rank: int,
    actor: str = "human",
    reason: str = "",
    force: bool = False,
) -> dict:
    """Move `item` to `to_rank` in the display-order overlay.

    Returns the appended audit row on success. Raises ReorderError for an
    unknown item or a blocked (unforced) dependency violation.
    """
    order = load_order(sdd_root)
    if item not in order:
        raise ReorderError(
            f"unknown item '{item}': not present in display order or BACKLOG.md"
        )
    if to_rank < 0 or to_rank >= len(order):
        # Out-of-range target is a usage error, surfaced by main() as exit 2.
        raise ValueError(
            f"--to-rank {to_rank} out of range (0..{len(order) - 1})"
        )

    from_rank = order.index(item)
    new_order = [x for x in order if x != item]
    new_order.insert(to_rank, item)

    depends_map = load_depends_map(sdd_root)
    done_map = {e.id: e.done for e in load_backlog_entries(sdd_root)}
    violations = dependency_violations(item, new_order, depends_map, done_map)

    if violations and not force:
        raise ReorderError("; ".join(violations))

    forced = bool(violations and force)
    if forced:
        dependency_check = "override"
    elif violations:  # unreachable: violations w/o force raises above
        dependency_check = "blocked"
    else:
        dependency_check = "pass"

    write_order(sdd_root, new_order)
    return append_audit_row(
        sdd_root,
        actor=actor,
        item_id=item,
        from_rank=from_rank,
        to_rank=to_rank,
        reason=reason,
        dependency_check=dependency_check,
        force_override=forced,
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="backlog_reorder",
        description="Reorder the dashboard display-order overlay with safeguards.",
    )
    parser.add_argument(
        "--sdd-root",
        type=Path,
        default=DEFAULT_SDD_ROOT,
        help="Path to the spec-driven-development root (default: this CLI's parent).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    mv = sub.add_parser("move", help="Move an item to a new display rank.")
    mv.add_argument("--item", required=True, help="Feature ID to move (e.g. SDD-037).")
    mv.add_argument(
        "--to-rank",
        required=True,
        type=int,
        help="Target 0-based rank (0 = top of the list).",
    )
    mv.add_argument("--actor", default="human", help="Who performed the move.")
    mv.add_argument(
        "--reason",
        default="",
        help="Reason for the move; REQUIRED when --force is used.",
    )
    mv.add_argument(
        "--force",
        action="store_true",
        help="Override a dependency-lock block (requires a non-empty --reason).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:  # argparse usage errors
        return int(exc.code) if exc.code is not None else 2

    if args.command == "move":
        # Governance: the tool never silently forces (AC-7).
        if args.force and not args.reason.strip():
            print(
                "ERROR: --force requires a non-empty --reason "
                "(the tool never silently forces a dependency-violating move)",
                file=sys.stderr,
            )
            return 2
        try:
            row = move(
                args.sdd_root,
                item=args.item,
                to_rank=args.to_rank,
                actor=args.actor,
                reason=args.reason,
                force=args.force,
            )
        except ValueError as exc:  # usage-level (bad rank)
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        except ReorderError as exc:  # blocked / unknown item
            print(f"BLOCKED: {exc}", file=sys.stderr)
            return 1
        print(
            f"Moved {row['item_id']} from rank {row['from_rank']} to "
            f"{row['to_rank']} (dependency_check={row['dependency_check']}, "
            f"force_override={row['force_override']})."
        )
        return 0

    print(f"ERROR: unknown command '{args.command}'", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
