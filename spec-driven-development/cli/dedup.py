#!/usr/bin/env python3
"""Cross-feature deduplication scanner (SDD-020).

Scans backlog, ideas, and open spec dirs for overlapping entries using a
three-layer heuristic: exact ID match (HARD), fuzzy title match (SOFT),
and keyword Jaccard similarity (ADVISORY).

Usage:
    python dedup.py scan [--scope backlog|specs|all] [--format table|json]
                         [--no-prompt] [--candidate "title text"]

Exit codes:
    0 - clean scan (or ADVISORY/SOFT in non-strict mode)
    1 - HARD overlap detected
    2 - usage error
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

# Framework layout ---------------------------------------------------------- #
SDD_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_LINT_DIR = SDD_ROOT / "cli"
if str(_SCHEMA_LINT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_LINT_DIR))

from schema_lint import parse_frontmatter  # noqa: E402


class DedupError(Exception):
    """Expected dedup CLI failure."""


# --------------------------------------------------------------------------- #
# Corpus loader
# --------------------------------------------------------------------------- #

def _parse_backlog_table(text: str, source: str) -> list[dict]:
    """Parse markdown table rows from BACKLOG.md.

    Extracts ID (first column) and title/description (second column).
    """
    entries: list[dict] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        # Detect header row
        if any(re.search(r"\bID\b", c, re.IGNORECASE) for c in cells):
            in_table = True
            continue
        # Skip separator rows
        if all(re.match(r"^[-:]+$", c) for c in cells if c):
            continue
        if not in_table:
            continue
        item_id = cells[0].strip()
        title = cells[1].strip() if len(cells) > 1 else ""
        if not item_id or not title:
            continue
        entries.append({
            "source": source,
            "title": title,
            "id": item_id,
            "text": title,
        })
    return entries


def _parse_ideas(text: str, source: str) -> list[dict]:
    """Parse idea entries from IDEAS.md.

    Entries start with `- **[YYYY-MM-DD]**` followed by a title.
    """
    entries: list[dict] = []
    pattern = re.compile(
        r"^-\s+\*\*\[\d{4}-\d{2}-\d{2}\]\*\*\s+(.+?)(?:\s+--\s+|$)"
    )
    for line in text.splitlines():
        m = pattern.match(line.strip())
        if m:
            title = m.group(1).strip().rstrip(" -")
            entries.append({
                "source": source,
                "title": title,
                "id": None,
                "text": line.strip(),
            })
    return entries


def _parse_spec_entry(spec_dir: Path) -> dict | None:
    """Parse a single spec.md, returning an entry if status is open."""
    spec_md = spec_dir / "spec.md"
    if not spec_md.is_file():
        return None
    text = spec_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    status = fm.get("status", "").strip("'\"").lower()
    if status in ("done", "archived"):
        return None
    item_id = fm.get("id", "").strip("'\"")
    # Extract title from first heading
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break
    return {
        "source": str(spec_dir / "spec.md"),
        "title": title or spec_dir.name,
        "id": item_id or None,
        "text": title or spec_dir.name,
    }


def load_corpus(sdd_root: Path, scope: str = "all") -> list[dict]:
    """Load deduplication corpus from backlog and/or open specs.

    Args:
        sdd_root: Path to `spec-driven-development/` root.
        scope: "backlog", "specs", or "all".

    Returns:
        List of dicts with keys: source, title, id (str or None), text.
    """
    entries: list[dict] = []

    if scope in ("backlog", "all"):
        backlog_path = sdd_root / "backlog" / "BACKLOG.md"
        if backlog_path.is_file():
            entries.extend(
                _parse_backlog_table(
                    backlog_path.read_text(encoding="utf-8"),
                    str(backlog_path),
                )
            )
        ideas_path = sdd_root / "backlog" / "IDEAS.md"
        if ideas_path.is_file():
            entries.extend(
                _parse_ideas(
                    ideas_path.read_text(encoding="utf-8"),
                    str(ideas_path),
                )
            )

    if scope in ("specs", "all"):
        specs_dir = sdd_root / "specs"
        if specs_dir.is_dir():
            for spec_dir in sorted(specs_dir.iterdir()):
                if spec_dir.is_dir():
                    entry = _parse_spec_entry(spec_dir)
                    if entry:
                        entries.append(entry)

    return entries


# --------------------------------------------------------------------------- #
# Three-layer heuristic
# --------------------------------------------------------------------------- #

def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words (3+ chars)."""
    return {w for w in re.findall(r"[a-z]{3,}", text.lower()) if w}


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_overlaps(
    corpus: list[dict],
    candidate: dict,
    fuzzy_threshold: float = 0.8,
    jaccard_threshold: float = 0.3,
) -> list[tuple[str, dict, dict, float]]:
    """Find overlaps between a candidate and the corpus.

    Returns list of (tier, corpus_entry, candidate, score).
    Tiers: "HARD", "SOFT", "ADVISORY".
    """
    results: list[tuple[str, dict, dict, float]] = []

    cand_id = candidate.get("id")
    cand_title = candidate.get("title", "")
    cand_tokens = _tokenize(candidate.get("text", ""))

    for entry in corpus:
        # Skip self-comparison (same source path)
        if entry.get("source") == candidate.get("source"):
            continue

        # Layer 1: HARD -- exact ID match
        if cand_id and entry.get("id") and cand_id == entry["id"]:
            results.append(("HARD", entry, candidate, 1.0))
            continue

        # Layer 2: SOFT -- fuzzy title match
        if cand_title and entry.get("title"):
            ratio = difflib.SequenceMatcher(
                None, cand_title.lower(), entry["title"].lower()
            ).ratio()
            if ratio >= fuzzy_threshold:
                results.append(("SOFT", entry, candidate, ratio))
                continue

        # Layer 3: ADVISORY -- keyword Jaccard
        entry_tokens = _tokenize(entry.get("text", ""))
        jac = _jaccard(cand_tokens, entry_tokens)
        if jac >= jaccard_threshold:
            results.append(("ADVISORY", entry, candidate, jac))

    return results


# --------------------------------------------------------------------------- #
# Tiered action
# --------------------------------------------------------------------------- #

def _format_overlap(tier: str, corpus_entry: dict, candidate: dict, score: float) -> str:
    """Format a single overlap for display."""
    lines = [
        f"  [{tier}] score={score:.2f}",
        f"    corpus : {corpus_entry.get('title', '?')}",
        f"             source={corpus_entry.get('source', '?')}",
        f"    candidate: {candidate.get('title', '?')}",
    ]
    if corpus_entry.get("id"):
        lines.insert(1, f"    corpus id: {corpus_entry['id']}")
    return "\n".join(lines)


def handle_overlaps(
    overlaps: list[tuple[str, dict, dict, float]],
    no_prompt: bool = False,
) -> int:
    """Process overlaps and return exit code.

    HARD: always exit 1.
    SOFT: exit 1 if no_prompt, else exit 0 (advisory).
    ADVISORY: always exit 0.
    """
    if not overlaps:
        return 0

    has_hard = False
    has_soft = False

    for tier, corpus_entry, candidate, score in overlaps:
        print(_format_overlap(tier, corpus_entry, candidate, score))
        if tier == "HARD":
            has_hard = True
        elif tier == "SOFT":
            has_soft = True

    if has_hard:
        print("\nHARD overlap(s) detected -- blocking.", file=sys.stderr)
        return 1
    if has_soft and no_prompt:
        print("\nSOFT overlap(s) detected -- blocking (--no-prompt).", file=sys.stderr)
        return 1

    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dedup.py",
        description="Cross-feature deduplication scanner (SDD-020).",
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_scan = sub.add_parser("scan", help="Scan corpus for overlapping entries.")
    p_scan.add_argument(
        "--scope",
        choices=("backlog", "specs", "all"),
        default="all",
        help="Scope of corpus to scan (default: all).",
    )
    p_scan.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        dest="output_format",
        help="Output format (default: table).",
    )
    p_scan.add_argument(
        "--no-prompt",
        action="store_true",
        help="Treat SOFT overlaps as blocking (exit 1).",
    )
    p_scan.add_argument(
        "--candidate",
        default=None,
        help="Check a single candidate title against the corpus.",
    )
    p_scan.add_argument(
        "--sdd-root",
        default=None,
        help="Override SDD root directory (for testing).",
    )

    return parser.parse_args(argv)


def cmd_scan(args: argparse.Namespace) -> int:
    """Run dedup scan."""
    sdd_root = Path(args.sdd_root) if args.sdd_root else SDD_ROOT

    corpus = load_corpus(sdd_root, scope=args.scope)

    if not corpus:
        print("No corpus to dedup against; 0 candidates scanned.")
        return 0

    all_overlaps: list[tuple[str, dict, dict, float]] = []

    if args.candidate:
        # Check a single candidate against the corpus
        candidate = {
            "source": "<cli-candidate>",
            "title": args.candidate,
            "id": None,
            "text": args.candidate,
        }
        all_overlaps = find_overlaps(corpus, candidate)
    else:
        # Cross-check all corpus entries against each other
        for i, candidate in enumerate(corpus):
            others = corpus[:i] + corpus[i + 1:]
            overlaps = find_overlaps(others, candidate)
            for overlap in overlaps:
                # Avoid duplicates: only report if corpus entry index < candidate index
                tier, corpus_entry, cand, score = overlap
                corpus_idx = None
                for j, e in enumerate(corpus):
                    if e is corpus_entry:
                        corpus_idx = j
                        break
                if corpus_idx is not None and corpus_idx < i:
                    all_overlaps.append(overlap)

    if args.output_format == "json":
        output = []
        for tier, corpus_entry, candidate, score in all_overlaps:
            output.append({
                "tier": tier,
                "score": round(score, 4),
                "corpus_title": corpus_entry.get("title", ""),
                "corpus_source": corpus_entry.get("source", ""),
                "candidate_title": candidate.get("title", ""),
            })
        print(json.dumps(output, indent=2))
    else:
        if all_overlaps:
            print(f"Found {len(all_overlaps)} overlap(s):\n")
        else:
            print(f"Scanned {len(corpus)} entries; 0 overlaps found.")

    return handle_overlaps(all_overlaps, no_prompt=args.no_prompt)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "scan":
            return cmd_scan(args)
        print(f"ERROR: Unknown command: {args.command}", file=sys.stderr)
        return 2
    except DedupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
