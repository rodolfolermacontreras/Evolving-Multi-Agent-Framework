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
import subprocess
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
# SDD-018 UI Lifecycle Variant (Article XII candidate; ADR-014)
#
# Opt-in via `ui-variant: true` on a spec dir's spec.md. Triggers a sibling
# validator (check_validation_variant) that accepts a `## Delta Entries`
# section in that spec dir's validation.md. All delta-originated findings
# carry the `[delta]` prefix in both human and JSON output. Append-only
# enforcement is always-on (parse-time heuristic + git-show comparison
# against the last-committed file state). Non-variant spec dirs are
# byte-identical to pre-SDD-018 lint output.
# ---------------------------------------------------------------------------- #

UI_VARIANT_MARKER_KEY = "ui-variant"

DELTA_REQUIRED_FIELDS = ("timestamp", "author", "rationale", "item-type")

DELTA_ITEM_TYPE_ENUM = {
    "add",
    "wontfix",
    "re-check",
    "retroactive-demo",
}

# Forward-only allow-list per AC-5/R-5: only this spec dir may use
# `item-type: retroactive-demo`. Match by endswith() so the rule fires
# correctly both in the real repo (path prefix `spec-driven-development/`)
# and in test tempdirs (path prefix absent). Hard-coded length 1 per
# clarify.md Q8.
RETROACTIVE_DEMO_ALLOWLIST = (
    "specs/2026-05-16-state-dashboard/",
)

DELTA_FINDING_KIND = "delta"
DELTA_PREFIX = "[delta]"

# ISO 8601 UTC: YYYY-MM-DDTHH:MMZ or YYYY-MM-DDTHH:MM:SSZ
_ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z$"
)

_DELTA_HEADING_RE = re.compile(
    r"^###\s+Delta\s+DE-(\d{2,})(?:\s+--\s+(.*))?\s*$"
)
_DELTA_FIELD_RE = re.compile(
    r"^-\s+([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$"
)


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


# ---------------------------------------------------------------------------- #
# SDD-018 UI Lifecycle Variant: marker recognition, delta-entry validator,
# retroactive-demo allow-list, append-only enforcement.
# ---------------------------------------------------------------------------- #

def _spec_has_ui_variant(spec_dir: Path) -> bool:
    """Return True iff `spec.md` in `spec_dir` carries `ui-variant: true`."""
    spec_path = spec_dir / "spec.md"
    if not spec_path.is_file():
        return False
    fm = parse_frontmatter(spec_path.read_text(encoding="utf-8", errors="replace"))
    val = fm.get(UI_VARIANT_MARKER_KEY)
    if not isinstance(val, str):
        return False
    return val.strip().lower() == "true"


def _ui_variant_marker_shape_findings(spec_path: Path) -> list[Finding]:
    """If `spec.md` has a `ui-variant` key, its value must be exactly
    `true` or `false`. Anything else (`yes`, `1`, empty, etc.) is a
    `[delta]` lint error. Absent key returns []."""
    findings: list[Finding] = []
    fm = parse_frontmatter(spec_path.read_text(encoding="utf-8", errors="replace"))
    if UI_VARIANT_MARKER_KEY not in fm:
        return findings
    val = fm.get(UI_VARIANT_MARKER_KEY)
    if not isinstance(val, str) or val.strip().lower() not in ("true", "false"):
        shown = repr(val) if not isinstance(val, str) else f"'{val}'"
        findings.append(Finding(
            str(spec_path), DELTA_FINDING_KIND,
            f"{DELTA_PREFIX} ui-variant marker must be 'true' or 'false'; "
            f"saw {shown}",
        ))
    return findings


def _parse_delta_entries(text: str) -> list[dict]:
    """Extract delta entries from a `## Delta Entries` section.

    Returns a list of dicts with keys: de_num (int), de_id (str like
    `DE-01`), title (str), start_line (1-based int), raw_fields (dict
    of `key -> value` from `- key: value` lines BEFORE the first body
    line), body_present (bool).

    Returns [] when the section is absent. Tolerates an empty section
    (zero entries is a valid state per R-16 edge case).
    """
    lines = text.splitlines()

    section_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## Delta Entries":
            section_start = i + 1
            break
    if section_start is None:
        return []

    section_end = len(lines)
    for i in range(section_start, len(lines)):
        if lines[i].startswith("## ") and not lines[i].startswith("### "):
            section_end = i
            break

    entries: list[dict] = []
    i = section_start
    while i < section_end:
        m = _DELTA_HEADING_RE.match(lines[i])
        if not m:
            i += 1
            continue
        de_num_str = m.group(1)
        title = (m.group(2) or "").strip()
        de_num = int(de_num_str)

        # Locate this entry's block
        block_start = i + 1
        block_end = section_end
        for j in range(block_start, section_end):
            if lines[j].startswith("### "):
                block_end = j
                break
        block = lines[block_start:block_end]

        entry: dict = {
            "de_num": de_num,
            "de_id": f"DE-{de_num_str.zfill(2)}",
            "title": title,
            "start_line": i + 1,
            "raw_fields": {},
            "body_present": False,
        }
        seen_body = False
        for bl in block:
            stripped = bl.strip()
            if not stripped:
                continue
            field_match = _DELTA_FIELD_RE.match(bl)
            if field_match and not seen_body:
                key = field_match.group(1)
                value = field_match.group(2)
                entry["raw_fields"][key] = value
            else:
                seen_body = True
                entry["body_present"] = True
        entries.append(entry)
        i = block_end

    return entries


def _check_delta_append_only(path: Path) -> list[Finding]:
    """Append-only enforcement (AC-3/R-3): compare `path`'s current
    content to its last-committed state via `git show HEAD:<rel>`. Any
    DE-NN entry whose mandatory fields changed, or that was deleted
    since the last commit, is a `[delta]` lint error.

    If `path` is not inside a git work tree, or git is unavailable, or
    the file is new (no prior commit), this check is silently skipped.
    The parse-time monotonic/dup checks in `check_validation_variant`
    catch in-memory shape violations independently.
    """
    findings: list[Finding] = []

    # Locate git work tree root
    repo_root = None
    for parent in [path.parent] + list(path.parents):
        if (parent / ".git").exists():
            repo_root = parent
            break
    if repo_root is None:
        return findings

    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return findings

    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel.as_posix()}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return findings

    if result.returncode != 0:
        # File is new (no HEAD version) or git ran into an error -- skip.
        return findings

    prior_text = result.stdout
    current_text = path.read_text(encoding="utf-8", errors="replace")

    prior_entries = _parse_delta_entries(prior_text)
    current_entries = _parse_delta_entries(current_text)

    prior_map = {e["de_id"]: e for e in prior_entries}
    current_map = {e["de_id"]: e for e in current_entries}

    for de_id, prior in prior_map.items():
        if de_id not in current_map:
            findings.append(Finding(
                str(path), DELTA_FINDING_KIND,
                f"{DELTA_PREFIX} {de_id} deleted (append-only violation: "
                f"delta entries from prior commits MUST remain)",
            ))
            continue
        current = current_map[de_id]
        for required in DELTA_REQUIRED_FIELDS:
            prior_val = prior["raw_fields"].get(required, "").strip()
            current_val = current["raw_fields"].get(required, "").strip()
            if prior_val and prior_val != current_val:
                findings.append(Finding(
                    str(path), DELTA_FINDING_KIND,
                    f"{DELTA_PREFIX} {de_id} field '{required}' modified "
                    f"(append-only violation: prior committed value "
                    f"'{prior_val}', current '{current_val}')",
                ))

    return findings


def _is_allowlisted_for_retroactive_demo(spec_dir_rel: str) -> bool:
    """True if `spec_dir_rel` (posix-style, trailing `/`) matches the
    hard-coded retroactive-demo allow-list (length 1; AC-5/R-5)."""
    if not spec_dir_rel:
        return False
    return any(spec_dir_rel.endswith(allowed) for allowed in RETROACTIVE_DEMO_ALLOWLIST)


def check_validation_variant(path: Path, spec_dir_rel: str = "") -> list[Finding]:
    """Variant validator for `validation.md` in a `ui-variant: true` spec dir.

    Runs the strict base contract via `check_artifact()` first, then layers
    on variant-specific delta-entry checks. Findings originating in the
    delta layer carry the `[delta]` prefix and the `delta` kind so they are
    distinguishable in both human and JSON output (R-4).

    `spec_dir_rel` is the spec dir's path relative to the repo root,
    posix-style, with a trailing slash. Used for retroactive-demo
    allow-list matching.
    """
    findings: list[Finding] = list(check_artifact(path))

    text = path.read_text(encoding="utf-8", errors="replace")
    entries = _parse_delta_entries(text)

    seen_ids: set[str] = set()
    last_num = 0

    for entry in entries:
        de_id = entry["de_id"]
        de_num = entry["de_num"]

        if de_id in seen_ids:
            findings.append(Finding(
                str(path), DELTA_FINDING_KIND,
                f"{DELTA_PREFIX} {de_id} duplicated in this file "
                f"(IDs MUST be unique)",
            ))
        seen_ids.add(de_id)

        if de_num <= last_num:
            findings.append(Finding(
                str(path), DELTA_FINDING_KIND,
                f"{DELTA_PREFIX} {de_id} not monotonically increasing "
                f"(prior was DE-{last_num:02d})",
            ))
        if de_num > last_num:
            last_num = de_num

        # Mandatory field presence
        for required in DELTA_REQUIRED_FIELDS:
            val = entry["raw_fields"].get(required, "")
            if not isinstance(val, str) or not val.strip():
                findings.append(Finding(
                    str(path), DELTA_FINDING_KIND,
                    f"{DELTA_PREFIX} {de_id} missing mandatory field "
                    f"'{required}'",
                ))

        # Timestamp shape (only if present)
        ts = entry["raw_fields"].get("timestamp", "").strip()
        if ts and not _ISO_TIMESTAMP_RE.match(ts):
            findings.append(Finding(
                str(path), DELTA_FINDING_KIND,
                f"{DELTA_PREFIX} {de_id} timestamp '{ts}' is not ISO 8601 "
                f"UTC (expected YYYY-MM-DDTHH:MMZ or "
                f"YYYY-MM-DDTHH:MM:SSZ)",
            ))

        # item-type enum check (only if present and non-empty)
        item_type = entry["raw_fields"].get("item-type", "").strip()
        if item_type and item_type not in DELTA_ITEM_TYPE_ENUM:
            findings.append(Finding(
                str(path), DELTA_FINDING_KIND,
                f"{DELTA_PREFIX} {de_id} item-type '{item_type}' not in "
                f"enum {sorted(DELTA_ITEM_TYPE_ENUM)}",
            ))

        # Retroactive-demo allow-list (AC-5/R-5)
        if item_type == "retroactive-demo":
            if not _is_allowlisted_for_retroactive_demo(spec_dir_rel):
                findings.append(Finding(
                    str(path), DELTA_FINDING_KIND,
                    f"{DELTA_PREFIX} {de_id} retroactive-demo permitted only "
                    f"for SDD-018 proof case (spec dir '{spec_dir_rel}' not "
                    f"in allow-list)",
                ))

    # Append-only enforcement against last-committed file state
    findings.extend(_check_delta_append_only(path))

    return findings


def _should_skip_artifact(path: Path) -> bool:
    """Apply the skip list (templates, scratch fragments)."""
    if path.name in ARTIFACT_SKIP_NAMES:
        return True
    if any(path.name.startswith(prefix) for prefix in ARTIFACT_SKIP_PREFIXES):
        return True
    return False


def _walk_artifacts(base: Path) -> list[Finding]:
    """Walk one in-scope tree, applying check_artifact to every non-skipped *.md.

    SDD-018: for spec dirs whose spec.md carries `ui-variant: true`, the
    sibling `validation.md` is routed to `check_validation_variant` instead
    of the strict `check_artifact`. The variant validator still applies the
    full base contract internally; it only ADDS the delta-section checks.
    Non-variant spec dirs are byte-identical to pre-SDD-018 behavior.
    """
    findings: list[Finding] = []
    if not base.is_dir():
        return findings

    # Precompute which spec dirs are ui-variant so the per-spec-dir
    # dispatch decision happens exactly once (Authoring decision 2).
    variant_spec_dirs: set[Path] = set()
    for spec_path in sorted(base.rglob("spec.md")):
        if _should_skip_artifact(spec_path):
            continue
        if _spec_has_ui_variant(spec_path.parent):
            variant_spec_dirs.add(spec_path.parent.resolve())

    for p in sorted(base.rglob("*.md")):
        if _should_skip_artifact(p):
            continue
        # Marker-shape check on every spec.md (always-on; fires on
        # `ui-variant: yes` style typos even for non-variant spec dirs).
        if p.name == "spec.md":
            findings.extend(_ui_variant_marker_shape_findings(p))
        # Variant dispatch: validation.md inside a variant spec dir
        if p.name == "validation.md" and p.parent.resolve() in variant_spec_dirs:
            spec_dir_rel = _spec_dir_relative_path(p.parent.resolve())
            findings.extend(check_validation_variant(p, spec_dir_rel))
            continue
        findings.extend(check_artifact(p))
    return findings


def _spec_dir_relative_path(spec_dir: Path) -> str:
    """Return the spec dir's path relative to the nearest `specs/` ancestor,
    posix-style, with a trailing `/`. This anchors retroactive-demo
    allow-list matching to the framework convention `specs/<name>/`
    regardless of the absolute filesystem location (works in both the real
    repo and test tempdirs)."""
    parts = spec_dir.parts
    if "specs" not in parts:
        return ""
    idx = parts.index("specs")
    return "/".join(parts[idx:]) + "/"


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
