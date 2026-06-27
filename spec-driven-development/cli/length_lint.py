#!/usr/bin/env python3
"""
Advisory max-function-length lint for the SDD framework (SDD-048 / Q-F).

Walks production modules under ``spec-driven-development/cli/`` and reports
functions whose source span exceeds an advisory threshold, so the team can
keep functions right-sized after the SDD-048 god-module split. It is a
deliberately NON-BLOCKING check: ``main`` always returns 0. No gate is gated
by this lint -- it informs, it does not fail the build.

The five Article X locked functions (``render_html``, ``load_sprint_table``,
``load_sprint_goal``, ``detect_current_sprint``, ``load_decisions``) are
EXEMPT: they are byte-locked by the Article X footprint guard and must not be
split, so flagging them would be noise. ``render_html`` in particular is the
documented Article X / M-3 length exception.

Test files (``test_*.py``) and ``__init__.py`` are skipped: test methods are
not production functions to right-size.

Usage:
    python length_lint.py [--root PATH] [--max N]

Stdlib-only (Article V): argparse, ast, dataclasses, pathlib, sys.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

# Advisory threshold (logical source lines, def line through last body line).
# Set above typical helper length so the report stays signal, not noise.
DEFAULT_MAX_LINES = 150

# Article X locked functions -- exempt from findings (must not be split).
LOCKED_EXEMPT = frozenset({
    "render_html",
    "load_sprint_table",
    "load_sprint_goal",
    "detect_current_sprint",
    "load_decisions",
})


@dataclass(frozen=True)
class LongFunction:
    """A function and its measured source span."""

    path: Path
    name: str
    lineno: int
    length: int


def framework_root() -> Path:
    """Repository root that contains the ``spec-driven-development`` tree."""
    here = Path(__file__).resolve()
    # cli/ -> spec-driven-development/ -> repo root
    return here.parent.parent.parent


def measure_functions(source: str, path: Path) -> list[LongFunction]:
    """Return every top-level-or-nested function in ``source`` with its span.

    Span = ``end_lineno - lineno + 1`` (the ``def`` line through the last body
    line). Returns an empty list for unparseable source.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    found: list[LongFunction] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", None) or node.lineno
            found.append(LongFunction(
                path=path,
                name=node.name,
                lineno=node.lineno,
                length=end - node.lineno + 1,
            ))
    return found


def _iter_cli_modules(root: Path):
    """Yield production ``*.py`` modules under ``spec-driven-development/cli``."""
    cli = root / "spec-driven-development" / "cli"
    if not cli.is_dir():
        return
    for path in sorted(cli.glob("*.py")):
        name = path.name
        if name.startswith("test_") or name == "__init__.py":
            continue
        yield path


def _all_functions(root: Path) -> list[LongFunction]:
    funcs: list[LongFunction] = []
    for path in _iter_cli_modules(root):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        funcs.extend(measure_functions(source, path))
    return funcs


def scan(root: Path, max_lines: int = DEFAULT_MAX_LINES) -> list[LongFunction]:
    """Return non-locked functions whose span exceeds ``max_lines``."""
    over = [
        f for f in _all_functions(root)
        if f.name not in LOCKED_EXEMPT and f.length > max_lines
    ]
    return sorted(over, key=lambda f: f.length, reverse=True)


def longest_non_locked(root: Path) -> LongFunction | None:
    """Return the single longest non-locked function, or None if none found."""
    candidates = [f for f in _all_functions(root) if f.name not in LOCKED_EXEMPT]
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.length)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="length_lint.py",
        description="Advisory (non-blocking) max-function-length lint over cli/.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root to scan (default: the framework checkout).",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=DEFAULT_MAX_LINES,
        help=f"Advisory max function length in lines (default: {DEFAULT_MAX_LINES}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).expanduser().resolve() if args.root else framework_root()

    longest = longest_non_locked(root)
    if longest is not None:
        rel = (longest.path.relative_to(root)
               if longest.path.is_relative_to(root) else longest.path)
        print(f"length-lint: longest non-locked function: {longest.name} "
              f"({rel}:{longest.lineno}) = {longest.length} lines")

    findings = scan(root, args.max)
    if not findings:
        print(f"length-lint: clean (no non-locked function over {args.max} lines).")
        return 0

    for f in findings:
        rel = f.path.relative_to(root) if f.path.is_relative_to(root) else f.path
        print(f"LONG FUNCTION (advisory): {rel}:{f.lineno}: {f.name} = "
              f"{f.length} lines (max {args.max})")
    print(f"length-lint: {len(findings)} advisory finding(s) "
          f"over {args.max} lines. (non-blocking)")
    # Advisory only -- never block a gate.
    return 0


if __name__ == "__main__":
    sys.exit(main())
