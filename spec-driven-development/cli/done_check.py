#!/usr/bin/env python3
"""DONE-completeness check (SDD-046 / B-2 rule 2).

FAILS (exit 1) when a feature directory that claims DONE is missing a required
artifact (``spec.md``, ``validation.md``, or a RETRO file) or has an unchecked
REQUIRED checkbox in ``validation.md``.

Two modes:
  - explicit dirs: every named directory must be complete. Used at feature
    close and by the unit tests.
  - ``--pi PI-N``: audit ``specs/*`` directories that claim DONE (have a RETRO
    file) AND reference ``PI-N``. Used by ``run_doctor`` so that historical PIs
    and in-flight (not-yet-done) features are not flagged.

Only checkboxes under the ``## Required Items`` heading are enforced; the
``## Optional Items`` section is ignored.

Enforced by: this module is wired into ``bootstrap.py run_doctor`` as the
``DONE completeness`` check.

Stdlib-only (Article V): argparse, pathlib, re, sys.
"""

from pathlib import Path
import argparse
import re
import sys

CHECKBOX = re.compile(r"-\s*\[( |x|X)\]\s*(.*)")


def find_retro(feature_dir: Path) -> Path | None:
    """Return a RETRO file in ``feature_dir`` (case-insensitive), or None."""
    if not feature_dir.is_dir():
        return None
    for path in sorted(feature_dir.iterdir()):
        if path.is_file() and path.name.lower().startswith("retro"):
            return path
    return None


def required_unchecked(validation_path: Path) -> list[str]:
    """Return labels of unchecked checkboxes under ``## Required Items``."""
    text = validation_path.read_text(encoding="utf-8", errors="replace")
    unchecked: list[str] = []
    in_required = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            in_required = heading.startswith("required items")
            continue
        if not in_required:
            continue
        match = CHECKBOX.match(stripped)
        if match and match.group(1) == " ":
            label = match.group(2).strip() or "(unlabeled item)"
            unchecked.append(label.split(":", 1)[0].strip())
    return unchecked


def check_feature_dir(feature_dir: Path) -> list[str]:
    """Return a list of completeness problems for ``feature_dir`` (empty == DONE)."""
    problems: list[str] = []
    name = feature_dir.name
    spec = feature_dir / "spec.md"
    validation = feature_dir / "validation.md"
    if not spec.is_file():
        problems.append(f"{name}: missing spec.md")
    if not validation.is_file():
        problems.append(f"{name}: missing validation.md")
    if find_retro(feature_dir) is None:
        problems.append(f"{name}: missing RETRO file")
    if validation.is_file():
        for item in required_unchecked(validation):
            problems.append(f"{name}: unchecked REQUIRED box {item}")
    return problems


def discover_pi_dirs(specs_root: Path, pi: str) -> list[Path]:
    """Return ``specs_root`` subdirs that claim DONE and reference ``pi``."""
    found: list[Path] = []
    if not specs_root.is_dir():
        return found
    for feature_dir in sorted(specs_root.iterdir()):
        if not feature_dir.is_dir():
            continue
        if find_retro(feature_dir) is None:
            continue
        haystack = ""
        for filename in ("validation.md", "spec.md"):
            candidate = feature_dir / filename
            if candidate.is_file():
                haystack += candidate.read_text(encoding="utf-8", errors="replace")
        if pi in haystack:
            found.append(feature_dir)
    return found


def audit_pi(specs_root: Path, pi: str) -> list[str]:
    """Return all completeness problems for DONE dirs of ``pi`` (empty == clean)."""
    problems: list[str] = []
    for feature_dir in discover_pi_dirs(specs_root, pi):
        problems.extend(check_feature_dir(feature_dir))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DONE-completeness check (SDD-046).")
    parser.add_argument("dirs", nargs="*", help="Feature directories to check.")
    parser.add_argument("--pi", help="Audit DONE dirs of this PI under --specs-root.")
    parser.add_argument(
        "--specs-root",
        default="spec-driven-development/specs",
        help="Specs root for --pi mode.",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    problems: list[str] = []
    if args.pi:
        problems.extend(audit_pi(Path(args.specs_root), args.pi))
    for raw in args.dirs:
        problems.extend(check_feature_dir(Path(raw)))

    if not problems:
        print("[PASS] DONE completeness: all checked feature dirs are complete.")
        return 0
    print("[FAIL] DONE completeness: incomplete feature dir(s):")
    for problem in problems:
        print(f"  - {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
