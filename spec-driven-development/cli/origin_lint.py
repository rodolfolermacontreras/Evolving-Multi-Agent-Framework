#!/usr/bin/env python3
"""
Origin-token + identity lint for the SDD framework (SDD-045 / A-6).

Fails when a denylisted origin token leaks into a portable framework file
under ``.github/**`` or ``constitution/**``. The shipped default denylist
targets personal home-directory paths (an unambiguous identity leak in any
repo). A host adopting the framework extends the denylist (via ``--denylist``
JSON) with their own origin-project module names (``engine.py``), project-root
paths, the origin project name, and personal author names; see
``RECOMMENDED_DENYLIST`` for the stricter set a fully-generalized host enables.

An ``<!-- example: ... -->`` marker exempts intentionally-illustrative lines or
blocks so documented examples are not flagged.

This module also provides the tracked-database guard (SDD-045 / A-4) used by
``bootstrap.py doctor``: it fails if a ``*.db`` file under the ledger directory
is tracked by git.

Usage:
    python origin_lint.py [--root PATH] [--denylist denylist.json]
    python origin_lint.py --check-tracked-db [--root PATH]

Stdlib-only (Article V): argparse, json, pathlib, re, subprocess, sys.
"""

from pathlib import Path
import argparse
import json
import re
import subprocess
import sys

# Default denylist: regex patterns that must never appear in a portable
# framework file (under .github/** or constitution/**) regardless of which
# host adopts the framework. The shipped default targets only personal
# home-directory paths -- the one class of token that is an unambiguous
# identity leak in any repository and is never legitimately illustrative.
#
# Deliberately NOT in the default: origin-project module names (engine.py),
# project-root paths (e.g. C:\Training\, C:\Dev\), the origin project name,
# and personal author names. Those appear legitimately in this repo's own
# origin story, ownership metadata, and host-pattern examples (the framework
# is documented as not-yet-fully-generalized). A host that has finished
# generalizing opts into the stricter set below via the --denylist override.
DEFAULT_DENYLIST = (
    r"[A-Za-z]:\\Users\\",
    r"/home/[A-Za-z0-9_.-]+/",
    r"/Users/[A-Za-z0-9_.-]+/",
)

# Recommended stricter denylist for a fully-generalized host. Not shipped as
# the default (it would flag this repo's own origin-story examples); supplied
# here so a host can copy it into a --denylist JSON file once generalization
# is complete. Personal author names and the origin project name are added
# per-host.
RECOMMENDED_DENYLIST = DEFAULT_DENYLIST + (
    r"engine\.py",
    r"[A-Za-z]:\\Training\\",
    r"[A-Za-z]:\\Dev\\",
)

# Origin-project tokens (SDD-047 / A-3). These name the framework's origin
# project (Day-to-Day Agent) and its stack. They are legitimate only inside a
# labeled ``<!-- example: ... -->`` history block (exempt) or in the historical
# record (specs/**, sprints/**, docs/** -- not scanned). A fully-generalized
# host folds these into the tightened denylist so they cannot leak into a
# generic agent, skill, or constitution file.
ORIGIN_TOKENS = (
    r"Day-to-Day",
    r"FastAPI",
    r"HTMX",
    r"World State",
    r"Outlander",
    r"\b743\b",
)

# Relative directories scanned for origin tokens.
SCAN_DIRS = (
    Path(".github"),
    Path("spec-driven-development") / "constitution",
)

# Directories exempt from the origin-token scan (SDD-047 / A-3, "generic
# scope"). The domain skill library is a deliberately stack-specific set of
# EXAMPLE reference skills (their descriptions begin with "EXAMPLE"); they
# illustrate how a host wires its own stack and legitimately name a concrete
# framework (e.g. a web framework, a frontend library). Scrubbing their stack
# tokens would destroy the reference value (R-A3-4 no concept loss), so they
# are excluded from the generic-scope lint -- mirroring the orphan-skill
# exemption in schema_lint.
EXEMPT_DIRS = (
    Path(".github") / "skills" / "domain",
)

# Text file suffixes scanned. Binary and generated artifacts are skipped.
TEXT_SUFFIXES = (".md", ".txt", ".yml", ".yaml", ".json", ".cfg", ".ini")

_EXAMPLE_OPEN = re.compile(r"<!--\s*example:", re.IGNORECASE)
_EXAMPLE_CLOSE = re.compile(r"-->")


class OriginLintError(Exception):
    """Expected origin-lint failure with a human-readable remediation."""


def framework_root() -> Path:
    """Return the repository root containing this script."""
    return Path(__file__).resolve().parents[2]


def load_denylist(path: Path | None) -> list[str]:
    """Return the denylist patterns, optionally overridden by a JSON file.

    The JSON file may be a list of patterns, or an object with a
    ``"denylist"`` key holding a list of patterns.
    """
    if path is None:
        return list(DEFAULT_DENYLIST)
    if not path.is_file():
        raise OriginLintError(
            f"Denylist file not found: {path}\n"
            "Remediation: pass --denylist pointing at an existing JSON file."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("denylist", [])
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise OriginLintError(
            f"Denylist JSON must be a list of strings (or an object with a "
            f"'denylist' list): {path}\n"
            "Remediation: fix the denylist file structure."
        )
    return data


def _read_owner_name(root: Path) -> str:
    """Return the ``owner`` field from ``project.config.json`` ('' if absent).

    Degrades silently to an empty string when the config file is missing,
    unreadable, malformed, or lacks a string ``owner`` value -- the lint must
    never crash on a host that has not populated the config surface.
    """
    config_path = root / "project.config.json"
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if isinstance(data, dict):
        owner = data.get("owner", "")
        if isinstance(owner, str):
            return owner.strip()
    return ""


def load_config_denylist(root: Path) -> list[str]:
    """Return a config-aware tightened denylist for a generalized host.

    Combines the recommended stricter patterns (home paths, project roots,
    ``engine.py``) with the origin-project tokens (A-3) and the host owner's
    personal name read from ``project.config.json`` (A-2 R-5). The owner name
    is regex-escaped so a re-added personal name in any generic file fails the
    lint. A missing or unreadable config degrades to the token denylist with
    no owner-name pattern (no crash).
    """
    patterns = list(RECOMMENDED_DENYLIST) + list(ORIGIN_TOKENS)
    owner = _read_owner_name(root)
    if owner:
        patterns.append(re.escape(owner))
    return patterns


def _iter_text_files(root: Path) -> list[Path]:
    """Return scanned text files under the framework's SCAN_DIRS.

    Files under EXEMPT_DIRS (the labeled EXAMPLE domain skill library) are
    excluded from the generic-scope scan.
    """
    exempt_bases = [root / rel for rel in EXEMPT_DIRS]

    def _is_exempt(path: Path) -> bool:
        return any(
            path == base or base in path.parents for base in exempt_bases
        )

    files: list[Path] = []
    for rel in SCAN_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                if _is_exempt(path):
                    continue
                files.append(path)
    return files


def scan_file(path: Path, patterns: list[re.Pattern[str]]) -> list[tuple[int, str, str]]:
    """Return (line_number, token, line) findings for one file.

    Lines inside an ``<!-- example: ... -->`` block are exempt.
    """
    findings: list[tuple[int, str, str]] = []
    in_example = False
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), start=1):
        opened = bool(_EXAMPLE_OPEN.search(line))
        closed = bool(_EXAMPLE_CLOSE.search(line))
        if in_example:
            # Inside a multi-line example block; skip until it closes.
            if closed:
                in_example = False
            continue
        if opened and not closed:
            # Block opens here and continues on later lines.
            in_example = True
            continue
        if opened and closed:
            # Self-contained example marker on this line; exempt the line.
            continue
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                findings.append((lineno, match.group(0), line.strip()))
    return findings


def scan_origin_tokens(root: Path, denylist: list[str]) -> list[tuple[Path, int, str, str]]:
    """Scan portable files under root for denylisted tokens.

    Returns a list of (path, line_number, token, line) findings.
    """
    patterns = [re.compile(token) for token in denylist]
    results: list[tuple[Path, int, str, str]] = []
    for path in _iter_text_files(root):
        for lineno, token, line in scan_file(path, patterns):
            results.append((path, lineno, token, line))
    return results


def find_tracked_dbs(root: Path) -> list[str]:
    """Return git-tracked database files under the ledger directory.

    Used by the tracked-database guard (A-4). Returns an empty list when git
    is unavailable or root is not a git repository (the guard is a no-op in
    that case rather than a false failure).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files",
             "spec-driven-development/ledger/*.db", "*.db"],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="origin_lint.py",
        description="Fail when origin/identity tokens leak into portable framework files.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root to scan (default: the framework checkout).",
    )
    parser.add_argument(
        "--denylist",
        default=None,
        help="Optional JSON file overriding the default denylist patterns.",
    )
    parser.add_argument(
        "--check-tracked-db",
        action="store_true",
        help="Also fail if a *.db file under the ledger is tracked by git.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).expanduser().resolve() if args.root else framework_root()
    try:
        denylist = load_denylist(Path(args.denylist) if args.denylist else None)
    except OriginLintError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings = scan_origin_tokens(root, denylist)
    tracked = find_tracked_dbs(root) if args.check_tracked_db else []

    if not findings and not tracked:
        print("origin-lint: clean (no origin tokens or tracked databases found).")
        return 0

    for path, lineno, token, line in findings:
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"ORIGIN TOKEN: {rel}:{lineno}: '{token}' in: {line}", file=sys.stderr)
    for tracked_path in tracked:
        print(f"TRACKED DATABASE: {tracked_path} is tracked by git "
              f"(run: git rm --cached {tracked_path})", file=sys.stderr)
    print(
        f"origin-lint: FAIL ({len(findings)} origin token(s), "
        f"{len(tracked)} tracked database(s)).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
