#!/usr/bin/env python3
"""TDD-gate mechanical check (SDD-046 / B-2 rule 1).

Ports the tdd-gate skill's Mechanical Check into an executable, blocking check.
FAILS (exit 1) when a production file changed with no corresponding test change
and no accepted ``[NO-TEST-NEEDED]`` justification.

Scope is deliberately narrow: only Python files under ``cli/`` are treated as
production. A ``test_*.py`` (or other test-named file) is a test. Docs, prompts,
ADRs, templates, and workflow config never trip the gate -- this avoids the
false positives that a broad "any source file" rule would generate.

Usage:
    python tdd_gate_check.py [--root PATH] [--base REF --head REF]
    python tdd_gate_check.py --files PATH [PATH ...] [--tag-text TEXT]

With no ``--files``, the working tree (staged + unstaged + untracked) is
inspected via git. ``--base``/``--head`` compare two refs instead.

Enforced by: this module is wired into ``bootstrap.py run_doctor`` as the
``tdd gate`` check, so CI (``make doctor``) blocks untested production changes.

Stdlib-only (Article V): argparse, pathlib, subprocess, sys.
"""

from pathlib import Path
import argparse
import subprocess
import sys

NO_TEST_TAG = "[NO-TEST-NEEDED]"


def _normalize(path: str) -> str:
    return path.replace("\\", "/")


def is_test_path(path: str) -> bool:
    """True when ``path`` names a test file."""
    norm = _normalize(path).lower()
    name = norm.rsplit("/", 1)[-1]
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
        or "/tests/" in norm
        or "/__tests__/" in norm
    )


def is_production_path(path: str) -> bool:
    """True when ``path`` is a production Python file the gate guards.

    Strict scope: only ``cli/**`` Python files (excluding test files).
    """
    norm = _normalize(path)
    if not norm.endswith(".py"):
        return False
    if is_test_path(norm):
        return False
    return "/cli/" in norm or norm.startswith("cli/")


def classify(paths: list[str]) -> tuple[list[str], list[str]]:
    """Split ``paths`` into (production, test) lists."""
    prod = [p for p in paths if is_production_path(p)]
    test = [p for p in paths if _normalize(p).endswith(".py") and is_test_path(p)]
    return prod, test


def evaluate(changed_files: list[str], tag_text: str = "") -> tuple[bool, list[str]]:
    """Return (ok, offending_production_paths).

    ok is True when there are no production changes, OR at least one test file
    changed, OR an accepted ``[NO-TEST-NEEDED]`` justification is present.
    """
    prod, test = classify(changed_files)
    if not prod:
        return True, []
    if test:
        return True, []
    if NO_TEST_TAG in (tag_text or ""):
        return True, []
    return False, prod


def _git_lines(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(root: Path, base: str | None = None, head: str | None = None) -> list[str]:
    """Return changed paths from git: ref-range when given, else working tree."""
    if base and head:
        return _git_lines(root, ["diff", "--name-only", f"{base}..{head}"])
    seen: set[str] = set()
    seen.update(_git_lines(root, ["diff", "--name-only"]))
    seen.update(_git_lines(root, ["diff", "--name-only", "--cached"]))
    seen.update(_git_lines(root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(seen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TDD-gate mechanical check (SDD-046).")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd).")
    parser.add_argument("--base", help="Base ref for a range comparison.")
    parser.add_argument("--head", help="Head ref for a range comparison.")
    parser.add_argument(
        "--files",
        nargs="*",
        help="Explicit changed-file list (bypasses git discovery).",
    )
    parser.add_argument("--tag-text", default="", help="Task text scanned for the escape hatch.")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.files is not None:
        paths = args.files
    else:
        paths = changed_files(Path(args.root).resolve(), args.base, args.head)

    ok, offenders = evaluate(paths, args.tag_text)
    if ok:
        print("[PASS] tdd gate: production changes are test-paired or justified.")
        return 0
    print(
        "[FAIL] tdd gate: production file(s) changed without a matching test "
        "change or an accepted [NO-TEST-NEEDED] justification:"
    )
    for path in offenders:
        print(f"  - {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
