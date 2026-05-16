#!/usr/bin/env python3
"""Schema lint for agent/skill/prompt YAML frontmatter (SDD-006).

Stdlib only. Walks `.github/agents/`, `.github/skills/**/SKILL.md`, and
`.github/prompts/` from the repo root and verifies required frontmatter fields.

Usage:
    python schema_lint.py [--repo-root PATH] [--json]

Exit codes:
    0 - clean scan
    1 - findings present
    2 - usage error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Finding:
    path: str
    kind: str          # "agent" | "skill" | "prompt"
    issue: str
    severity: str = "ERROR"


# ---------------------------------------------------------------------------- #
# Tiny frontmatter parser -- stdlib only, no PyYAML dependency.
#
# Supports our simple subset:
#   ---
#   key: value
#   key2: 'value2'
#   metadata:
#     author: foo
#     version: '1.0'
#   ---
# ---------------------------------------------------------------------------- #

_RAW_VERSION_RE = re.compile(r"^\s*version\s*:\s*([^\s#].*?)\s*$")


def parse_frontmatter(text: str) -> dict:
    """Return a dict with top-level keys; nested 'metadata' becomes a sub-dict.

    Returns {} when no frontmatter delimiter is present. Returns {"_raw_lines": [...]}
    when frontmatter is present, so callers can inspect raw lines for things like
    quoting (which a stricter parser would normalize away).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}

    body = lines[1:end_idx]
    out: dict = {"_raw_lines": list(body)}
    cur_section: str | None = None
    for line in body:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            # Nested under most recent top-level section
            if cur_section is None:
                continue
            m = re.match(r"^\s+([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
            if m:
                if not isinstance(out.get(cur_section), dict):
                    out[cur_section] = {}
                out[cur_section][m.group(1)] = m.group(2).strip()
            continue
        # Top-level key: value
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            cur_section = None
            continue
        key, value = m.group(1), m.group(2).strip()
        if value == "":
            # opening of a nested section
            cur_section = key
            out.setdefault(key, {})
        else:
            cur_section = None
            out[key] = value
    return out


def _has_unquoted_version(raw_lines: list[str]) -> tuple[bool, str | None]:
    """Return (is_unquoted, raw_value). True when `version:` exists with an
    unquoted, unquoted-looking value (e.g. `version: 1.0`)."""
    for line in raw_lines:
        m = _RAW_VERSION_RE.match(line)
        if not m:
            continue
        raw = m.group(1)
        # Strip trailing comments
        raw = raw.split("#", 1)[0].strip()
        if raw.startswith("'") or raw.startswith('"'):
            return False, raw
        # Accept booleans/null as still-not-a-version-string (also fails for our case)
        return True, raw
    return False, None


# ---------------------------------------------------------------------------- #
# Checkers
# ---------------------------------------------------------------------------- #

def check_agent(path: Path) -> list[Finding]:
    """Agent files require: description."""
    findings: list[Finding] = []
    fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if not fm:
        findings.append(Finding(str(path), "agent", "no YAML frontmatter delimiters"))
        return findings
    if not fm.get("description"):
        findings.append(Finding(str(path), "agent", "missing 'description'"))
    return findings


def check_skill(path: Path) -> list[Finding]:
    """Skill files require: name, description, license, metadata.author, metadata.version."""
    findings: list[Finding] = []
    fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if not fm:
        findings.append(Finding(str(path), "skill", "no YAML frontmatter delimiters"))
        return findings
    raw_lines = fm.get("_raw_lines", [])

    for field_name in ("name", "description", "license"):
        if not fm.get(field_name):
            findings.append(Finding(str(path), "skill", f"missing top-level '{field_name}'"))

    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        findings.append(Finding(str(path), "skill", "missing 'metadata' block"))
    else:
        if not meta.get("author"):
            findings.append(Finding(str(path), "skill", "missing 'metadata.author'"))
        if not meta.get("version"):
            findings.append(Finding(str(path), "skill", "missing 'metadata.version'"))

    # ADR-0006: version must be a quoted string at any nesting level
    unquoted, raw = _has_unquoted_version(raw_lines)
    if unquoted:
        findings.append(Finding(
            str(path), "skill",
            f"version must be a quoted string per ADR-0006; saw `version: {raw}`",
        ))

    # AC6: skill name must match its containing directory name
    declared_name = fm.get("name")
    if isinstance(declared_name, str) and declared_name:
        # Strip surrounding quotes if any
        declared_name = declared_name.strip().strip("'").strip('"')
        dir_name = path.parent.name
        if declared_name != dir_name:
            findings.append(Finding(
                str(path), "skill",
                f"skill name mismatch: declared '{declared_name}', directory '{dir_name}'",
            ))

    return findings


def check_prompt(path: Path) -> list[Finding]:
    """Prompt files require: description."""
    findings: list[Finding] = []
    fm = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if not fm:
        findings.append(Finding(str(path), "prompt", "no YAML frontmatter delimiters"))
        return findings
    if not fm.get("description"):
        findings.append(Finding(str(path), "prompt", "missing 'description'"))
    raw_lines = fm.get("_raw_lines", [])
    unquoted, raw = _has_unquoted_version(raw_lines)
    if unquoted:
        findings.append(Finding(
            str(path), "prompt",
            f"version must be a quoted string per ADR-0006; saw `version: {raw}`",
        ))
    return findings


# ---------------------------------------------------------------------------- #
# Walk + scan
# ---------------------------------------------------------------------------- #

def scan(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []

    agents_dir = repo_root / ".github" / "agents"
    skills_dir = repo_root / ".github" / "skills"
    prompts_dir = repo_root / ".github" / "prompts"

    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.agent.md")):
            if p.name.startswith("_"):
                continue
            findings.extend(check_agent(p))

    if skills_dir.is_dir():
        for p in sorted(skills_dir.rglob("SKILL.md")):
            findings.extend(check_skill(p))

    if prompts_dir.is_dir():
        for p in sorted(prompts_dir.rglob("*.prompt.md")):
            findings.extend(check_prompt(p))

    return findings


# ---------------------------------------------------------------------------- #
# Report renderer
# ---------------------------------------------------------------------------- #

def render_human(findings: list[Finding], scanned_root: Path) -> str:
    if not findings:
        return f"Schema lint clean. Scanned: {scanned_root}\n"
    by_path: dict[str, list[Finding]] = {}
    for f in findings:
        by_path.setdefault(f.path, []).append(f)
    lines = [f"Schema lint: {len(findings)} finding{'s' if len(findings) != 1 else ''} in {len(by_path)} file(s)."]
    for path, items in by_path.items():
        lines.append(f"  {path}")
        for it in items:
            lines.append(f"    [{it.severity}] ({it.kind}) {it.issue}")
    return "\n".join(lines) + "\n"


def render_json(findings: list[Finding]) -> str:
    return json.dumps(
        [{"path": f.path, "kind": f.kind, "issue": f.issue, "severity": f.severity}
         for f in findings],
        indent=2,
    )


# ---------------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="schema_lint.py",
        description="Validate YAML frontmatter on agent/skill/prompt files (SDD-006).",
    )
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT),
                        help="Repository root (default: detected from script location).")
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as JSON instead of human-readable text.")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: repo root not found: {root}", file=sys.stderr)
        return 2

    findings = scan(root)
    if args.json:
        print(render_json(findings))
    else:
        print(render_human(findings, root), end="")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
