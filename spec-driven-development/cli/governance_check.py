#!/usr/bin/env python3
"""
Governance-consistency check for the SDD framework (SDD-045 / B-3).

Asserts two properties:

1. **Article-range coherence.** The upper bound of the article range cited in
   ``docs/RULES.md`` (e.g. "Articles I-XII") equals the number of articles
   actually defined in ``constitution/principles.md`` (``## Article {ROMAN}:``
   headers). Adding a thirteenth article to principles.md without updating
   RULES.md makes this check FAIL.

2. **Frontmatter well-formedness.** Each of the six constitution files plus
   RULES.md carries a quoted semver ``version:`` and an ISO ``last_amended:``
   (and ``ratified:`` where present). This is a well-formedness check, NOT an
   equality check: the files legitimately carry different versions.

Stdlib-only (Article V): argparse, pathlib, re, sys.
"""

from pathlib import Path
import argparse
import re
import sys

# The six constitution files (mirrors bootstrap.py:CONSTITUTION_FILES).
CONSTITUTION_FILES = (
    "mission.md",
    "tech-stack.md",
    "principles.md",
    "roadmap.md",
    "decision-policy.md",
    "quality-policy.md",
)

_ARTICLE_RE = re.compile(r"^##\s+Article\s+([IVXLCDM]+)\s*:", re.MULTILINE)
_RULES_RANGE_RE = re.compile(r"Articles\s+I-([IVXLCDM]+)|\(I-([IVXLCDM]+)\)")
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_VERSION_RE = re.compile(r"^version:\s*'(\d+\.\d+\.\d+)'\s*$", re.MULTILINE)
_DATE_FIELD_RE = re.compile(r"^(last_amended|ratified):\s*(\S+)\s*$", re.MULTILINE)
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


class GovernanceError(Exception):
    """Expected governance-check failure with a human-readable remediation."""


def framework_root() -> Path:
    """Return the repository root containing this script."""
    return Path(__file__).resolve().parents[2]


def roman_to_int(roman: str) -> int:
    """Convert an uppercase Roman numeral to an integer."""
    total = 0
    previous = 0
    for char in reversed(roman.upper()):
        value = _ROMAN_VALUES.get(char)
        if value is None:
            raise GovernanceError(f"Invalid Roman numeral: {roman}")
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total


def count_articles(principles_text: str) -> int:
    """Return the highest article number defined in principles.md text."""
    numbers = [roman_to_int(match.group(1)) for match in _ARTICLE_RE.finditer(principles_text)]
    if not numbers:
        raise GovernanceError(
            "No '## Article {ROMAN}:' headers found in principles.md.\n"
            "Remediation: confirm principles.md article headers are well-formed."
        )
    return max(numbers)


def rules_upper_bound(rules_text: str) -> int:
    """Return the highest article-range upper bound cited in RULES.md text."""
    bounds: list[int] = []
    for match in _RULES_RANGE_RE.finditer(rules_text):
        roman = match.group(1) or match.group(2)
        if roman:
            bounds.append(roman_to_int(roman))
    if not bounds:
        raise GovernanceError(
            "No 'Articles I-{ROMAN}' range citation found in RULES.md.\n"
            "Remediation: confirm RULES.md cites the article range."
        )
    return max(bounds)


def check_frontmatter(name: str, text: str) -> list[str]:
    """Return findings for malformed version/date frontmatter in one file."""
    findings: list[str] = []
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return [f"{name}: missing YAML frontmatter block."]
    frontmatter = match.group(1)
    if not _VERSION_RE.search(frontmatter):
        findings.append(
            f"{name}: missing or malformed quoted semver version (expected version: 'X.Y.Z')."
        )
    date_fields = _DATE_FIELD_RE.findall(frontmatter)
    if not date_fields:
        findings.append(f"{name}: missing last_amended/ratified date field.")
    for field_name, value in date_fields:
        if not _ISO_DATE_RE.match(value):
            findings.append(f"{name}: {field_name} is not an ISO YYYY-MM-DD date: {value}")
    return findings


def check_governance(root: Path) -> tuple[bool, list[str]]:
    """Run all governance checks against a framework checkout.

    Returns (ok, findings). ok is True only when every check passes.
    """
    findings: list[str] = []
    constitution_dir = root / "spec-driven-development" / "constitution"
    principles_path = constitution_dir / "principles.md"
    rules_path = root / "spec-driven-development" / "docs" / "RULES.md"

    if not principles_path.is_file():
        return False, [f"principles.md not found at {principles_path}"]
    if not rules_path.is_file():
        return False, [f"RULES.md not found at {rules_path}"]

    principles_text = principles_path.read_text(encoding="utf-8")
    rules_text = rules_path.read_text(encoding="utf-8")

    try:
        article_count = count_articles(principles_text)
        range_upper = rules_upper_bound(rules_text)
        if article_count != range_upper:
            findings.append(
                f"Article-range drift: principles.md defines {article_count} articles "
                f"but RULES.md cites Articles I-{range_upper}. "
                f"Update RULES.md to cite Articles I-{article_count}."
            )
    except GovernanceError as exc:
        findings.append(str(exc))

    for name in CONSTITUTION_FILES:
        path = constitution_dir / name
        if not path.is_file():
            findings.append(f"{name}: constitution file not found at {path}")
            continue
        findings.extend(check_frontmatter(name, path.read_text(encoding="utf-8")))
    findings.extend(check_frontmatter("RULES.md", rules_text))

    return (not findings), findings


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="governance_check.py",
        description="Assert RULES.md article range matches principles.md and frontmatter is well-formed.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root to check (default: the framework checkout).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).expanduser().resolve() if args.root else framework_root()
    ok, findings = check_governance(root)
    if ok:
        print("governance-check: clean (article range and frontmatter coherent).")
        return 0
    for finding in findings:
        print(f"GOVERNANCE: {finding}", file=sys.stderr)
    print(f"governance-check: FAIL ({len(findings)} issue(s)).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
