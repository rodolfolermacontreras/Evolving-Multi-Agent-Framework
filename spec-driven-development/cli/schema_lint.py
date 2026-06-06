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
    kind: str          # "agent" | "skill" | "prompt" | "artifact"
    issue: str
    severity: str = "ERROR"


# ---------------------------------------------------------------------------- #
# Filesystem data contract (SDD-FDC-001 / ADR-012)
#
# Every in-scope `*.md` under spec-driven-development/specs/** and
# spec-driven-development/sprints/** MUST carry these five frontmatter fields.
# The enums for `type` and `status` are CLOSED -- adding a value requires an
# Architect decision recorded in plan.md or an ADR amendment.
# ---------------------------------------------------------------------------- #

REQUIRED_CONTRACT_FIELDS = ("id", "type", "status", "owner", "updated")

ARTIFACT_TYPE_ENUM = {
    "spec",
    "plan",
    "tasks",
    "validation",
    "clarification",
    "sprint",
    "retro",
    "lessons",
    "index",
    "session",
}

ARTIFACT_STATUS_ENUM = {
    "draft",
    "active",
    "blocked",
    "done",
    "superseded",
    "archived",
}

# Skip list -- in-scope markdown that intentionally has no contract because
# it is a template or scratch fragment, not a live artifact. Documented per
# ADR-012; do not extend without justification.
ARTIFACT_SKIP_NAMES = {
    "lessons-template.md",  # sprint retros use it as a starter, body is placeholder
}

# Skip files whose basename starts with one of these prefixes (template convention).
ARTIFACT_SKIP_PREFIXES = ("_",)

# Best-effort ISO date pattern for the `updated` field.
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def check_artifact(path: Path) -> list[Finding]:
    """Artifact files (in-scope specs/** + sprints/** markdown) require the
    SDD-FDC-001 frontmatter contract: id, type, status, owner, updated, with
    `type` and `status` drawn from the locked enums.

    A {} parse result (no YAML delimiters) produces a single finding and
    short-circuits -- never crashes (ADR-012 / FDC plan section 1).
    """
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    if not fm:
        findings.append(Finding(str(path), "artifact", "no YAML frontmatter delimiters"))
        return findings

    for field_name in REQUIRED_CONTRACT_FIELDS:
        val = fm.get(field_name)
        if val is None or (isinstance(val, str) and not val.strip()):
            findings.append(Finding(str(path), "artifact",
                                    f"missing '{field_name}'"))

    type_val = fm.get("type")
    if isinstance(type_val, str) and type_val.strip():
        if type_val.strip() not in ARTIFACT_TYPE_ENUM:
            findings.append(Finding(
                str(path), "artifact",
                f"type '{type_val.strip()}' not in enum "
                f"{sorted(ARTIFACT_TYPE_ENUM)}",
            ))

    status_val = fm.get("status")
    if isinstance(status_val, str) and status_val.strip():
        if status_val.strip() not in ARTIFACT_STATUS_ENUM:
            findings.append(Finding(
                str(path), "artifact",
                f"status '{status_val.strip()}' not in enum "
                f"{sorted(ARTIFACT_STATUS_ENUM)}",
            ))

    updated_val = fm.get("updated")
    if isinstance(updated_val, str) and updated_val.strip():
        if not _ISO_DATE_RE.match(updated_val.strip()):
            findings.append(Finding(
                str(path), "artifact",
                f"updated '{updated_val.strip()}' is not ISO YYYY-MM-DD",
                severity="WARNING",
            ))

    return findings


def _should_skip_artifact(path: Path) -> bool:
    """Apply the skip list (templates, scratch fragments)."""
    if path.name in ARTIFACT_SKIP_NAMES:
        return True
    if any(path.name.startswith(prefix) for prefix in ARTIFACT_SKIP_PREFIXES):
        return True
    return False


def _walk_artifacts(base: Path) -> list[Finding]:
    """Walk one in-scope tree, applying check_artifact to every non-skipped *.md."""
    findings: list[Finding] = []
    if not base.is_dir():
        return findings
    for p in sorted(base.rglob("*.md")):
        if _should_skip_artifact(p):
            continue
        findings.extend(check_artifact(p))
    return findings


# ---------------------------------------------------------------------------- #
# Walk + scan
# ---------------------------------------------------------------------------- #

def scan(repo_root: Path, paths: list[Path] | None = None) -> list[Finding]:
    """Scan for findings.

    If `paths` is provided (non-empty), walk each path as an artifact tree
    (SDD-FDC-001 contract) and ignore the default .github/ checkers. This is
    the explicit-invocation mode used by R6 verification:
        python schema_lint.py spec-driven-development/specs/ spec-driven-development/sprints/

    If `paths` is None/empty, run the legacy SDD-006 walk (.github/agents,
    .github/skills, .github/prompts) AND additionally walk the in-scope SDD
    artifact trees rooted at `repo_root/spec-driven-development/{specs,sprints}`.
    """
    findings: list[Finding] = []

    if paths:
        for base in paths:
            findings.extend(_walk_artifacts(base))
        return findings

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

    # In-scope artifact trees (SDD-FDC-001 / R6). Silently skipped if absent
    # (e.g. when scanning a fake-repo fixture in tests).
    sdd_root = repo_root / "spec-driven-development"
    findings.extend(_walk_artifacts(sdd_root / "specs"))
    findings.extend(_walk_artifacts(sdd_root / "sprints"))

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
        description="Validate YAML frontmatter on agent/skill/prompt files (SDD-006) "
                    "and the SDD-FDC-001 filesystem data contract for specs/** + sprints/**.",
    )
    parser.add_argument(
        "paths", nargs="*",
        help="Optional positional paths to walk as artifact trees (SDD-FDC-001 mode). "
             "When supplied, only these paths are scanned and the .github/ checkers "
             "are skipped. Example: schema_lint.py specs/ sprints/",
    )
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT),
                        help="Repository root (default: detected from script location). "
                             "Ignored when positional paths are supplied.")
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as JSON instead of human-readable text.")
    args = parser.parse_args(argv)

    explicit_paths: list[Path] = []
    if args.paths:
        for raw in args.paths:
            p = Path(raw).expanduser().resolve()
            if not p.exists():
                print(f"ERROR: path not found: {p}", file=sys.stderr)
                return 2
            if not p.is_dir():
                print(f"ERROR: path is not a directory: {p}", file=sys.stderr)
                return 2
            explicit_paths.append(p)
        findings = scan(Path(args.repo_root).expanduser().resolve(), paths=explicit_paths)
        scanned_root = Path(args.paths[0]).expanduser().resolve()
    else:
        root = Path(args.repo_root).expanduser().resolve()
        if not root.is_dir():
            print(f"ERROR: repo root not found: {root}", file=sys.stderr)
            return 2
        findings = scan(root)
        scanned_root = root

    if args.json:
        print(render_json(findings))
    else:
        print(render_human(findings, scanned_root), end="")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
