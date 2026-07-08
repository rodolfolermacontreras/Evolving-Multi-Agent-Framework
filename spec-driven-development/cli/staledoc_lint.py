#!/usr/bin/env python3
"""
Stale-doc guard for the SDD framework (SDD-051B / PI-8 "Truth in the Window").

The four session-start docs a teammate reads first drift out of agreement with
the live repo (the audit found "10 articles" when it was 12, and a tracker frozen
at "Current PI: PI-3"). This guard catches that drift mechanically so it cannot
return silently.

It verifies two cheap, exact counts against their live source (verify-against-
source, the mechanism the audit recommends where the source is cheap to read):

- **Article count** -- a hardcoded "N articles" or roman range "(I-ROMAN)" in a
  session-start doc must equal the number of ``## Article {ROMAN}:`` headers in
  ``constitution/principles.md``.
- **Current PI** -- a hardcoded ``Current PI: PI-N`` must equal the active PI read
  from ``sprints/PI-*/CURRENT_PI.md``.

Moving counts (test totals) are deliberately NOT regex-scanned: they change every
sprint and per-file code-map counts are granular, so flagging them would
false-positive on legitimate origin-story and code-map lines. Stale test totals
are handled by the doc-refresh durable fix (drop the number, point at the live
source) instead. An inline ``<!-- staledoc-ok -->`` marker on a line exempts it,
so a legitimate historical count reference does not trip the guard.

Usage:
    python staledoc_lint.py [--root PATH]

Exit 0 when clean, 1 when a stale count is found, 2 on a usage error.

Stdlib-only (Article V): argparse, pathlib, re, sys. Reuses the in-tree sibling
``governance_check`` (ADR-012) for the article-count / roman helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re
import sys

# The session-start docs a teammate reads first (audit Section 4). Relative to
# the repository root. RULES.md and root README.md are intentionally excluded --
# the audit marks them clean and they carry no rotting hardcoded count.
SESSION_START_DOCS = (
    Path("INSTRUCTIONS.md"),
    Path("spec-driven-development") / "CONTEXT.md",
    Path("spec-driven-development") / "docs" / "HIGH_LEVEL_DEV_TRACKER.md",
    Path("spec-driven-development") / "docs" / "ONBOARDING_KICK_OFF.md",
)

# Inline marker exempting a line from the guard (for a legitimate historical
# count reference, mirroring origin_lint's <!-- example: --> marker).
_MARKER_RE = re.compile(r"<!--\s*staledoc-ok", re.IGNORECASE)

# "N articles" / "N binding articles" (number precedes the word).
_ARTICLE_DECIMAL_RE = re.compile(r"(\d+)\s+(?:binding\s+)?articles?\b", re.IGNORECASE)
# A roman article-range citation like "articles ... (I-XII)".
_ARTICLE_ROMAN_RE = re.compile(
    r"articles?\b[^\n]*?\(\s*I-([IVXLCDM]+)\s*\)", re.IGNORECASE
)
# "Current PI: PI-N" / "**Current PI** | PI-N" (tolerant of markdown between).
_CURRENT_PI_RE = re.compile(r"current\s+pi\b[^\n]*?PI-(\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    """One stale-count finding in a session-start doc."""

    path: Path
    lineno: int
    kind: str  # "article" | "pi"
    detail: str
    line: str


class StaleDocError(Exception):
    """Expected guard failure with a human-readable remediation."""


def framework_root() -> Path:
    """Return the repository root containing this script."""
    return Path(__file__).resolve().parents[2]


def live_article_count(root: Path) -> int | None:
    """Return the number of articles defined in principles.md, or None.

    Reuses ``governance_check.count_articles`` (the same source ``doctor`` uses
    for its article-range coherence check). Returns None when principles.md is
    absent or malformed so the guard degrades to a no-op rather than crashing.
    """
    principles = (
        root / "spec-driven-development" / "constitution" / "principles.md"
    )
    if not principles.is_file():
        return None
    try:
        import governance_check
        return governance_check.count_articles(
            principles.read_text(encoding="utf-8")
        )
    except Exception:
        return None


def _roman_to_int(roman: str) -> int | None:
    """Convert a roman numeral to int via the sibling helper; None on error."""
    try:
        import governance_check
        return governance_check.roman_to_int(roman)
    except Exception:
        return None


def live_current_pi(root: Path) -> int | None:
    """Return the active PI number from ``sprints/PI-*/CURRENT_PI.md``, or None.

    Mirrors ``bootstrap.current_pi_name``: the highest-numbered PI whose
    CURRENT_PI.md marks status active.
    """
    sprints = root / "spec-driven-development" / "sprints"
    if not sprints.is_dir():
        return None
    numbers: list[int] = []
    for marker in sprints.glob("PI-*/CURRENT_PI.md"):
        text = marker.read_text(encoding="utf-8", errors="replace")
        if re.search(r"status:\s*active", text, re.IGNORECASE) or "Status: **ACTIVE**" in text:
            name = marker.parent.name  # "PI-8"
            try:
                numbers.append(int(name.split("-", 1)[1]))
            except (IndexError, ValueError):
                continue
    return max(numbers) if numbers else None


def scan_file(
    path: Path,
    rel: Path,
    *,
    article_count: int | None,
    current_pi: int | None,
) -> list[Finding]:
    """Return stale-count findings for one session-start doc."""
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _MARKER_RE.search(line):
            continue

        if article_count is not None:
            for match in _ARTICLE_DECIMAL_RE.finditer(line):
                if int(match.group(1)) != article_count:
                    findings.append(Finding(
                        rel, lineno, "article",
                        f"says {match.group(1)} articles; live is {article_count}",
                        line.strip(),
                    ))
            for match in _ARTICLE_ROMAN_RE.finditer(line):
                value = _roman_to_int(match.group(1))
                if value is not None and value != article_count:
                    findings.append(Finding(
                        rel, lineno, "article",
                        f"cites (I-{match.group(1)}); live is {article_count}",
                        line.strip(),
                    ))

        if current_pi is not None:
            for match in _CURRENT_PI_RE.finditer(line):
                if int(match.group(1)) != current_pi:
                    findings.append(Finding(
                        rel, lineno, "pi",
                        f"says Current PI PI-{match.group(1)}; live is PI-{current_pi}",
                        line.strip(),
                    ))
    return findings


def scan(root: Path) -> list[Finding]:
    """Scan the session-start docs under root for stale counts."""
    article_count = live_article_count(root)
    current_pi = live_current_pi(root)
    results: list[Finding] = []
    for rel in SESSION_START_DOCS:
        path = root / rel
        if not path.is_file():
            continue
        results.extend(scan_file(
            path, rel, article_count=article_count, current_pi=current_pi
        ))
    return results


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="staledoc_lint.py",
        description="Fail when a session-start doc carries a stale hardcoded "
                    "article or current-PI count.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root to scan (default: the framework checkout).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).expanduser().resolve() if args.root else framework_root()

    findings = scan(root)
    if not findings:
        print("staledoc-lint: clean (session-start docs match the live repo).")
        return 0

    for finding in findings:
        print(
            f"STALE DOC: {finding.path}:{finding.lineno}: {finding.detail} "
            f"in: {finding.line}",
            file=sys.stderr,
        )
    print(
        f"staledoc-lint: FAIL ({len(findings)} stale count(s)). "
        "Refresh the doc to the live count, or mark a legitimate historical "
        "line with <!-- staledoc-ok -->.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
