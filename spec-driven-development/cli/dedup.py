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
import sqlite3
import sys
from datetime import datetime, timezone
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
# SDD-020.R6 -- triple-destination log writers (SDD-032 / 2026-06-09)
#
# Three thin writers fire from cmd_scan when --emit-logs is set (default).
# Log artifact schemas (frozen; reused by downstream dashboard consumers):
#
#   1. Ledger rows (sqlite3 -> ledger/fleet.db.dispatches):
#      - one row per scan with task_id="DEDUP-SCAN-RUN",
#        notes='{"scope":..., "candidate_count":N, "overlap_count":M, "exit":X}'
#      - one row per overlap with task_id="DEDUP-OVERLAP-FLAGGED",
#        notes='{"tier":..., "score":..., "corpus_title":..., "candidate_title":...}'
#      Both use agent_id="dedup-scanner", agent_role="scanner", pi="N/A".
#
#   2. Per-spec dedup-scan.md (one file per candidate spec dir flagged):
#      - frontmatter: id, type=session, status=active, owner=dedup-scanner, updated
#      - body: "# Dedup Scan" + one bulleted overlap entry per flagged overlap
#
#   3. Rolling backlog/DEDUP-LOG.md (single file; appended one line per scan):
#      - header (first call only): "# Dedup Scan Log" + pipe-delimited columns
#      - line format: "| ISO-DATETIME | scope | candidate_count | overlap_count | exit |"
# --------------------------------------------------------------------------- #


_DEDUP_SCANNER_AGENT = ("dedup-scanner", "scanner")
_DEDUP_LOG_HEADER = (
    "# Dedup Scan Log\n"
    "\n"
    "Rolling log of cross-feature deduplication scans (SDD-020.R6).\n"
    "One line per `cli/dedup.py scan` invocation.\n"
    "\n"
    "| timestamp_utc | scope | candidates | overlaps | exit |\n"
    "|---------------|-------|------------|----------|------|\n"
)


def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 string (no microseconds)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_ledger_rows(
    db_path: Path,
    scan_run: dict,
    overlaps: list[tuple[str, dict, dict, float]],
) -> int:
    """Insert one DEDUP-SCAN-RUN row + N DEDUP-OVERLAP-FLAGGED rows.

    *scan_run* keys: scope, candidate_count, overlap_count, exit_code.
    Returns the number of rows inserted (1 + len(overlaps)).
    Silent on missing DB file (returns 0); writes nothing if the schema
    is not present.
    """
    if not db_path.is_file():
        return 0
    inserted = 0
    now = _utc_now_iso()
    agent_id, agent_role = _DEDUP_SCANNER_AGENT
    try:
        with sqlite3.connect(db_path) as conn:
            scan_notes = json.dumps({
                "scope": scan_run.get("scope", ""),
                "candidate_count": int(scan_run.get("candidate_count", 0)),
                "overlap_count": int(scan_run.get("overlap_count", 0)),
                "exit": int(scan_run.get("exit_code", 0)),
            })
            conn.execute(
                "INSERT INTO dispatches "
                "(dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
                " agent_id, agent_role, outcome, outcome_at, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    now, "N/A", None, None,
                    "DEDUP-SCAN-RUN",
                    f"Dedup scan ({scan_run.get('scope', '?')})",
                    agent_id, agent_role,
                    "success", now, scan_notes,
                ),
            )
            inserted += 1
            for tier, corpus_entry, candidate, score in overlaps:
                ov_notes = json.dumps({
                    "tier": tier,
                    "score": round(score, 4),
                    "corpus_title": corpus_entry.get("title", ""),
                    "corpus_source": corpus_entry.get("source", ""),
                    "candidate_title": candidate.get("title", ""),
                    "candidate_source": candidate.get("source", ""),
                })
                conn.execute(
                    "INSERT INTO dispatches "
                    "(dispatched_at, pi, sprint, feature_dir, task_id, task_title, "
                    " agent_id, agent_role, outcome, outcome_at, notes) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        now, "N/A", None, None,
                        "DEDUP-OVERLAP-FLAGGED",
                        f"[{tier}] {candidate.get('title', '?')}",
                        agent_id, agent_role,
                        "success", now, ov_notes,
                    ),
                )
                inserted += 1
            conn.commit()
    except sqlite3.DatabaseError:
        # Corrupt or schema-missing DB -- skip silently rather than break a scan.
        return 0
    return inserted


def _write_per_spec_dedup_scan(
    spec_dir: Path,
    overlaps_for_dir: list[tuple[str, dict, dict, float]],
) -> Path | None:
    """Write dedup-scan.md inside *spec_dir* summarizing the flagged overlaps.

    Skipped when *spec_dir* does not exist (pure-backlog scans). Returns the
    written path or None.
    """
    if not spec_dir.is_dir():
        return None
    if not overlaps_for_dir:
        return None
    now = _utc_now_iso()
    today = now.split("T", 1)[0]
    out = spec_dir / "dedup-scan.md"
    lines = [
        "---",
        f"id: '{spec_dir.name}-dedup-scan'",
        "type: session",
        "status: active",
        "owner: dedup-scanner",
        f"updated: {today}",
        "---",
        "",
        "# Dedup Scan",
        "",
        f"Generated by `cli/dedup.py scan` at {now}.",
        "",
        "## Flagged Overlaps",
        "",
    ]
    for tier, corpus_entry, candidate, score in overlaps_for_dir:
        lines.append(
            f"- [{tier}] score={score:.2f} -- "
            f"candidate `{candidate.get('title', '?')}` "
            f"vs corpus `{corpus_entry.get('title', '?')}` "
            f"(source: {corpus_entry.get('source', '?')})"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _append_rolling_log(log_path: Path, scan_summary: dict) -> Path:
    """Append a one-line row to *log_path* (creates with header if missing).

    *scan_summary* keys: scope, candidate_count, overlap_count, exit_code.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log_path.is_file()
    if is_new:
        log_path.write_text(_DEDUP_LOG_HEADER, encoding="utf-8")
    now = _utc_now_iso()
    line = (
        f"| {now} | {scan_summary.get('scope', '?')} | "
        f"{int(scan_summary.get('candidate_count', 0))} | "
        f"{int(scan_summary.get('overlap_count', 0))} | "
        f"{int(scan_summary.get('exit_code', 0))} |\n"
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return log_path


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
    # SDD-020.R6 (SDD-032) -- log writers gate. Default ON to match the
    # contract; tests and CI paths can opt out with --no-emit-logs.
    p_scan.add_argument(
        "--emit-logs",
        dest="emit_logs",
        action="store_true",
        default=True,
        help="Write ledger row + per-spec dedup-scan.md + rolling log (default).",
    )
    p_scan.add_argument(
        "--no-emit-logs",
        dest="emit_logs",
        action="store_false",
        help="Suppress all three log artifacts (used by test fixtures).",
    )
    p_scan.add_argument(
        "--db",
        default=None,
        help="Path to fleet.db (default: ledger/fleet.db). Used with --emit-logs.",
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

    exit_code = handle_overlaps(all_overlaps, no_prompt=args.no_prompt)

    # SDD-020.R6 (SDD-032) -- triple-destination log writers.
    # All three writes are guarded by --emit-logs (default True). Failures here
    # MUST NOT mask the dedup exit code; writers swallow their own I/O errors.
    if getattr(args, "emit_logs", True):
        scan_summary = {
            "scope": args.scope,
            "candidate_count": len(corpus),
            "overlap_count": len(all_overlaps),
            "exit_code": exit_code,
        }
        # (a) ledger row(s)
        db_path = Path(args.db) if getattr(args, "db", None) else (
            sdd_root / "ledger" / "fleet.db"
        )
        try:
            _write_ledger_rows(db_path, scan_summary, all_overlaps)
        except OSError:
            pass
        # (b) per-spec dedup-scan.md (group overlaps by candidate spec dir)
        per_dir: dict[Path, list[tuple[str, dict, dict, float]]] = {}
        for overlap in all_overlaps:
            _tier, _ce, cand, _s = overlap
            cand_src = cand.get("source", "")
            if not cand_src:
                continue
            cand_path = Path(cand_src)
            # spec-bound when path lives under sdd_root/specs/<feature>/spec.md
            try:
                rel = cand_path.relative_to(sdd_root / "specs")
            except ValueError:
                continue
            spec_feature = sdd_root / "specs" / rel.parts[0]
            per_dir.setdefault(spec_feature, []).append(overlap)
        for spec_feature, dir_overlaps in per_dir.items():
            try:
                _write_per_spec_dedup_scan(spec_feature, dir_overlaps)
            except OSError:
                pass
        # (c) rolling log
        log_path = sdd_root / "backlog" / "DEDUP-LOG.md"
        try:
            _append_rolling_log(log_path, scan_summary)
        except OSError:
            pass

    return exit_code


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
