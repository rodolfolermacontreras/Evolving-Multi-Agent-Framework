#!/usr/bin/env python3
"""State builder -- generate exec/state.md (SDD-002) and live state.html dashboard.

Two feature contracts satisfied by this single CLI:

  * SDD-002 (`specs/2026-05-16-state-builder/`): produce `exec/state.md` in the
    canonical 7-section format derived from fleet.db + artifact directories.
  * SDD state-dashboard (`specs/2026-05-16-state-dashboard/`): produce a visual
    Bridge-style `exec/state.html` and optionally serve it live over HTTP.

Usage:

  # SDD-002 default behaviour: write state.md (and state.html as a side output)
  python state_builder.py --sdd-root spec-driven-development

  # SDD-002 dry-run: print state.md to stdout, write nothing
  python state_builder.py --sdd-root spec-driven-development --dry-run

  # SDD state-dashboard live mode: serve state.html, rebuild on each request
  python state_builder.py serve [--port 8765] [--no-open]

Style: pure Python stdlib (LESSON-001). No third-party dependencies at runtime.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import re
import socket
import sqlite3
import subprocess
import sys
import webbrowser
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------- #
# Shared-parser boundary (ADR-012 / SDD-FDC-001)
#
# Import the frontmatter parser and the contract enums from schema_lint via
# the established sys.path bootstrap. Single source of truth: do NOT duplicate
# the parser. If this import fails, the environment is broken and we surface
# the error rather than silently fall back.
# ---------------------------------------------------------------------------- #

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))
from schema_lint import (  # noqa: E402  -- module-bootstrap import per ADR-012
    parse_frontmatter,
    ARTIFACT_TYPE_ENUM,
    ARTIFACT_STATUS_ENUM,
    ARTIFACT_SKIP_NAMES,
    ARTIFACT_SKIP_PREFIXES,
    UserGate,
    load_user_gates,
    check_skill,
    _has_unquoted_version,
    Finding,
)

# ---------------------------------------------------------------------------- #
# Reorder write path (SDD-041 / ADR-019)
#
# The dashboard POST /reorder endpoint delegates to the SDD-036 safeguarded
# overlay mutator. We reuse backlog_reorder.move verbatim -- it enforces the
# dependency-lock, appends the audit row, and never auto-applies force. The
# import follows the same in-tree sibling bootstrap as schema_lint (ADR-012).
# ---------------------------------------------------------------------------- #

from backlog_reorder import move as _reorder_move, ReorderError as _ReorderError

# ---------------------------------------------------------------------------- #
# SDD root + path helpers
# ---------------------------------------------------------------------------- #

DEFAULT_SDD_ROOT = Path(__file__).resolve().parents[1]   # spec-driven-development/


class StateBuilderError(Exception):
    """Expected state-builder failure with a human-readable message."""


def repo_root_for(sdd_root: Path) -> Path:
    return sdd_root.parent


# ---------------------------------------------------------------------------- #
# Project identity constants (header + context bar, from mockup)
# ---------------------------------------------------------------------------- #

PROJECT_TITLE = "BRIDGE"
PROJECT_SUBTITLE = "Evolving Multi-Agent Framework"
PROJECT_TYPE = "STANDALONE FRAMEWORK"
PROJECT_OWNER = "Rodolfo Lerma"
PROJECT_STACK = "Python stdlib | Plain HTML/CSS | SQLite | No runtime deps"
PROJECT_MISSION = (
    "A portable, replicable multi-agent development system. One human developer "
    "orchestrates a team of AI agents through a structured spec-driven lifecycle."
)

ABOUT_FALLBACK = "Current focus information is unavailable."


# ---------------------------------------------------------------------------- #
# Stage detection (used by HTML dashboard + as a fallback in MD pipeline)
# ---------------------------------------------------------------------------- #

STAGES = ["IDEA", "BACKLOG", "CLARIFY", "SPEC", "PLAN", "TASKS", "IMPLEMENT", "REVIEW", "DONE"]

STAGE_TONE = {
    "IDEA":      "tone-faint",
    "BACKLOG":   "tone-faint",
    "CLARIFY":   "tone-amber-soft",
    "SPEC":      "tone-amber-soft",
    "PLAN":      "tone-amber",
    "TASKS":     "tone-amber",
    "IMPLEMENT": "tone-oxblood",
    "REVIEW":    "tone-amber-bright",
    "DONE":      "tone-jade",
}


@dataclass
class Feature:
    feature_dir: Path
    name: str
    stage: str
    created: str
    status_line: str = ""
    notes: str = ""


_STATUS_RE = re.compile(r"^\s*(?:-\s+)?[Ss]tatus\s*:\s*(.+?)\s*$", re.MULTILINE)


def _normalize_status_to_stage(status: str) -> str | None:
    """Map a free-form spec.md Status line to a canonical lifecycle stage."""
    s = status.strip().lower()
    if not s:
        return None
    if "done" in s or "shipped" in s:
        return "DONE"
    if "review" in s:
        return "REVIEW"
    if "implement" in s:
        return "IMPLEMENT"
    if "task" in s:
        return "TASKS"
    if "plan" in s:
        return "PLAN"
    if "draft" in s or "spec" in s:
        return "SPEC"
    if "clarif" in s or "exploration" in s or "pre-spec" in s:
        return "CLARIFY"
    if "backlog" in s:
        return "BACKLOG"
    if "idea" in s:
        return "IDEA"
    return None


def detect_stage(feature_dir: Path) -> tuple[str, str, str]:
    """Return (stage, status_line, notes).

    Order of precedence (SDD-002 AC4):
      1. Explicit `Status:` line in spec.md frontmatter -> primary source
      2. validation.md checkbox ratio -> infer IMPLEMENT/REVIEW/DONE
      3. Artifact presence (tasks/plan/spec/design) -> coarse stage
    """
    has_design = (feature_dir / "DESIGN.md").is_file()
    has_spec = (feature_dir / "spec.md").is_file()
    has_plan = (feature_dir / "plan.md").is_file()
    has_tasks = (feature_dir / "tasks.md").is_file()
    has_validation = (feature_dir / "validation.md").is_file()
    has_retro = (feature_dir / "RETRO.md").is_file()

    status_line = ""
    if has_spec:
        text = (feature_dir / "spec.md").read_text(encoding="utf-8", errors="replace")
        m = _STATUS_RE.search(text)
        if m:
            status_line = m.group(1).strip()

    # 1. Evidence-first: RETRO.md + 100% validation == DONE, regardless of stale Status line.
    #    Prevents stale "status: implementing" from masking shipped features.
    if has_retro and has_validation:
        v = (feature_dir / "validation.md").read_text(encoding="utf-8", errors="replace")
        if not re.findall(r"^\s*- \[ \]", v, re.MULTILINE):
            return "DONE", status_line or "done", "validation 100%, RETRO present"

    explicit = _normalize_status_to_stage(status_line)
    if explicit:
        if explicit == "DONE":
            if has_retro:
                return "DONE", status_line, "Status: done, RETRO present"
            # Status says done but no RETRO -> fall back to REVIEW
            return "REVIEW", status_line, "Status: done but RETRO missing"
        # For all other explicit stages, trust the spec line
        return explicit, status_line, f"Status: {status_line}"

    # 2. Validation.md checkbox ratio
    if has_validation:
        v = (feature_dir / "validation.md").read_text(encoding="utf-8", errors="replace")
        unchecked = re.findall(r"^\s*- \[ \]", v, re.MULTILINE)
        checked = re.findall(r"^\s*- \[x\]", v, re.MULTILINE | re.IGNORECASE)
        total = len(unchecked) + len(checked)
        if total > 0:
            pct = round(len(checked) * 100 / total)
            if pct == 100 and has_retro:
                return "DONE", status_line, "validation 100%, RETRO present"
            stage = "REVIEW" if pct >= 80 else "IMPLEMENT"
            return stage, status_line, f"validation {pct}% ({len(checked)}/{total})"

    # 3. Artifact-presence fallback
    if has_tasks:    return "TASKS", status_line, "tasks.md present"
    if has_plan:     return "PLAN", status_line, "plan.md present"
    if has_spec:     return "SPEC", status_line, "spec.md present"
    if has_design:   return "CLARIFY", status_line, "DESIGN.md only (pre-spec design exploration)"
    return "BACKLOG", status_line, "directory exists, no artifacts yet"


def load_features(sdd_root: Path) -> list[Feature]:
    specs_dir = sdd_root / "specs"
    if not specs_dir.is_dir():
        return []
    features: list[Feature] = []
    for d in sorted(specs_dir.iterdir()):
        if not d.is_dir():
            continue
        stage, status_line, notes = detect_stage(d)
        name = d.name
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", name)
        created = m.group(1) if m else ""
        display_name = m.group(2) if m else name
        features.append(Feature(
            feature_dir=d, name=display_name, stage=stage,
            created=created, status_line=status_line, notes=notes,
        ))
    return features


# ---------------------------------------------------------------------------- #
# Roadmap parsing
# ---------------------------------------------------------------------------- #

@dataclass
class PIBlock:
    name: str
    title: str
    is_current: bool
    checkboxes: list[tuple[bool, str]] = field(default_factory=list)

    @property
    def done(self) -> int:    return sum(1 for c, _ in self.checkboxes if c)
    @property
    def total(self) -> int:   return len(self.checkboxes)
    @property
    def pct(self) -> int:     return round(self.done * 100 / self.total) if self.total else 0


def load_pis(sdd_root: Path) -> list[PIBlock]:
    p = sdd_root / "constitution" / "roadmap.md"
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8")
    blocks: list[PIBlock] = []
    header_re = re.compile(r"^##\s+(PI-\d+)\s*[:\-]\s*(.+?)\s*$", re.MULTILINE)
    matches = list(header_re.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1)
        title = m.group(2).strip()
        is_current = "(current" in title.lower()
        title_clean = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        checkboxes = []
        for line in body.splitlines():
            cm = re.match(r"\s*-\s+\[([ xX])\]\s+(.+?)\s*$", line)
            if cm:
                checkboxes.append((cm.group(1).lower() == "x", cm.group(2)))
        blocks.append(PIBlock(name=name, title=title_clean, is_current=is_current, checkboxes=checkboxes))
    return blocks


def current_pi(pis: list[PIBlock], override: str | None = None) -> PIBlock | None:
    if override:
        for p in pis:
            if p.name == override:
                return p
        # Override didn't match any existing PI -- create a synthetic one
        return PIBlock(name=override, title="", is_current=True)
    for p in pis:
        if p.is_current:
            return p
    for p in pis:
        if any(not c for c, _ in p.checkboxes):
            return p
    return pis[0] if pis else None


# ---------------------------------------------------------------------------- #
# Backlog parsing (RICE + Sprint column)
# ---------------------------------------------------------------------------- #

@dataclass
class BacklogItem:
    pid: str
    title: str
    priority: str
    rice: str
    sprint: str
    status: str


_BACKLOG_ROW = re.compile(
    r"^\|\s*([A-Z]{2,}-\d{2,3})\s*"
    r"\|\s*(.+?)\s*"
    r"\|\s*(P[1-4])\s*"
    r"\|\s*[^|]*\s*\|\s*[^|]*\s*\|\s*[^|]*\s*\|\s*[^|]*\s*"   # R / I / C / E
    r"\|\s*([\d\.]+)\s*"
    r"\|\s*([^|]*?)\s*"
    r"\|\s*([^|]*?)\s*\|\s*$",
    re.MULTILINE,
)


def load_backlog(sdd_root: Path) -> list[BacklogItem]:
    p = sdd_root / "backlog" / "BACKLOG.md"
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8")
    return [
        BacklogItem(pid=m.group(1), title=m.group(2), priority=m.group(3),
                    rice=m.group(4), sprint=m.group(5), status=m.group(6))
        for m in _BACKLOG_ROW.finditer(text)
    ]


# ---------------------------------------------------------------------------- #
# Roster (agents + skills, per SDD-002 AC6)
# ---------------------------------------------------------------------------- #

def load_roster(sdd_root: Path) -> dict:
    agents_path = sdd_root / "roster" / "agents.json"
    skills_path = sdd_root / "roster" / "skills.json"
    agents = json.loads(agents_path.read_text(encoding="utf-8")) if agents_path.is_file() else []
    skills = json.loads(skills_path.read_text(encoding="utf-8")) if skills_path.is_file() else []
    principals = 0
    generic = 0
    specialist = 0
    for a in agents:
        k = a.get("kind", "unknown")
        if k == "principal":
            principals += 1
        elif k == "specialist":
            specialist += 1
        elif k == "generic":
            if a.get("specialization"):
                specialist += 1
            else:
                generic += 1
        else:
            generic += 1
    categories = {s.get("category", "") for s in skills if s.get("category")}
    return {
        "principals": principals,
        "generic": generic,
        "specialist": specialist,
        "total_agents": len(agents),
        "total_skills": len(skills),
        "skill_categories": len(categories),
        "agents": agents,
        "skills": skills,
    }


# ---------------------------------------------------------------------------- #
# Ledger (SDD-002 AC2 + AC3)
# ---------------------------------------------------------------------------- #

@dataclass
class LedgerView:
    recent_success: list[dict]
    blockers: list[dict]
    recent: list[dict]
    available: bool
    # SDD-037 (F-28): additive widening -- all dispatch rows grouped by
    # feature_dir then sprint, populated inside load_ledger's single
    # connection. Has a default so existing constructions stay valid.
    grouped: list = field(default_factory=list)


def _group_dispatches(rows: list[dict]) -> list[dict]:
    """Group dispatch rows by ``feature_dir`` then ``sprint`` (SDD-037).

    Pure helper over a list of row dicts. Feature groups and sprint
    subgroups preserve first-appearance order; rows keep the order they
    arrive in (the SQL caller pre-orders most-recent-first within a sprint).
    Returns ``[{"feature_dir": str, "sprints": [{"sprint": str,
    "rows": [dict, ...]}, ...]}, ...]``.
    """
    groups: list[dict] = []
    by_feature: dict[str, dict] = {}
    for row in rows:
        fdir = (row.get("feature_dir") or "") if isinstance(row, dict) else ""
        sprint = (row.get("sprint") or "") if isinstance(row, dict) else ""
        grp = by_feature.get(fdir)
        if grp is None:
            grp = {"feature_dir": fdir, "sprints": [], "_by_sprint": {}}
            by_feature[fdir] = grp
            groups.append(grp)
        sub = grp["_by_sprint"].get(sprint)
        if sub is None:
            sub = {"sprint": sprint, "rows": []}
            grp["_by_sprint"][sprint] = sub
            grp["sprints"].append(sub)
        sub["rows"].append(row)
    for grp in groups:
        grp.pop("_by_sprint", None)
    return groups


def load_ledger(sdd_root: Path, now: dt.datetime | None = None,
                stale_hours: int = 24, recent_limit: int = 10) -> LedgerView:
    db_path = sdd_root / "ledger" / "fleet.db"
    if not db_path.is_file():
        return LedgerView(recent_success=[], blockers=[], recent=[],
                          available=False, grouped=[])
    now = now or dt.datetime.now(dt.timezone.utc)
    stale_cutoff = (now - dt.timedelta(hours=stale_hours)).isoformat().replace("+00:00", "Z")
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            recent_success = [dict(r) for r in conn.execute(
                "SELECT * FROM dispatches WHERE outcome='success' "
                "ORDER BY COALESCE(outcome_at, dispatched_at) DESC LIMIT 10"
            ).fetchall()]
            blockers = [dict(r) for r in conn.execute(
                "SELECT * FROM dispatches WHERE outcome IS NULL AND dispatched_at < ? "
                "ORDER BY dispatched_at ASC LIMIT 10", [stale_cutoff],
            ).fetchall()]
            recent = [dict(r) for r in conn.execute(
                "SELECT * FROM dispatches ORDER BY dispatched_at DESC LIMIT ?",
                [recent_limit],
            ).fetchall()]
            # SDD-037: full grouped view read in the SAME connection so the
            # Dispatches card adds zero new connections per build tick.
            grouped_rows = [dict(r) for r in conn.execute(
                "SELECT * FROM dispatches "
                "ORDER BY feature_dir, sprint, COALESCE(outcome_at, dispatched_at) DESC"
            ).fetchall()]
    except sqlite3.Error:
        return LedgerView(recent_success=[], blockers=[], recent=[],
                          available=False, grouped=[])
    return LedgerView(recent_success=recent_success, blockers=blockers,
                      recent=recent, available=True,
                      grouped=_group_dispatches(grouped_rows))


# ---------------------------------------------------------------------------- #
# Git log (HTML extra; not part of SDD-002)
# ---------------------------------------------------------------------------- #

def load_recent_commits(sdd_root: Path, limit: int = 10) -> list[tuple[str, str, str]]:
    try:
        out = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h\x1f%s\x1f%cr"],
            capture_output=True, text=True, check=True, cwd=str(repo_root_for(sdd_root)),
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [tuple(line.split("\x1f")) for line in out.splitlines() if line.count("\x1f") == 2]


# ---------------------------------------------------------------------------- #
# Live UI v2 data-layer functions (T-001 .. T-004)
# ---------------------------------------------------------------------------- #

def load_sprint_table(sdd_root: Path, pi_name: str) -> list[dict]:
    """Return enriched sprint dicts for *pi_name*, merged with ledger data.

    Each dict contains the keys produced by ``_discover_sprints`` plus
    ``dispatch_count`` (int) and ``last_outcome`` (str) from the fleet ledger.
    Returns ``[]`` if the PI directory doesn't exist or has no sprints.
    """
    pi_dir = sdd_root / "docs" / "Management" / pi_name
    if not pi_dir.is_dir():
        return []
    sprints = _discover_sprints(pi_dir)
    if not sprints:
        return []
    ledger_data = _query_ledger_for_pi(sdd_root, pi_name)
    for s in sprints:
        ld = ledger_data.get(s["num"], {"count": 0, "last_outcome": "--"})
        s["dispatch_count"] = ld["count"]
        s["last_outcome"] = ld["last_outcome"]
    return sprints


def load_sprint_goal(sdd_root: Path, pi_name: str, sprint_num: int) -> str:
    """Extract the sprint goal from SPEC.md for the given sprint number.

    Looks for a ``## 1. Sprint Goal`` heading first; falls back to the first
    ``##`` heading.  Returns the first non-empty paragraph under that heading.
    Returns ``"No sprint goal defined"`` when nothing can be extracted.
    """
    fallback = "No sprint goal defined"
    pi_dir = sdd_root / "docs" / "Management" / pi_name
    if not pi_dir.is_dir():
        return fallback

    # Find the sprint directory matching sprint_num
    target_dir: Path | None = None
    for child in pi_dir.iterdir():
        if not child.is_dir():
            continue
        m = _SPRINT_DIR_RE.match(child.name)
        if m and int(m.group(1)) == sprint_num:
            target_dir = child
            break
    if target_dir is None:
        return fallback

    spec_path = target_dir / "SPEC.md"
    if not spec_path.is_file():
        return fallback

    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError:
        return fallback

    lines = text.splitlines()

    # Try to find '## 1. Sprint Goal' heading first
    goal_idx: int | None = None
    first_h2_idx: int | None = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            if first_h2_idx is None:
                first_h2_idx = i
            if "1. Sprint Goal" in stripped:
                goal_idx = i
                break

    heading_idx = goal_idx if goal_idx is not None else first_h2_idx
    if heading_idx is None:
        return fallback

    # Extract first non-empty paragraph after the heading
    for line in lines[heading_idx + 1:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break  # hit next heading
        if stripped:
            return stripped

    return fallback


def detect_current_sprint(sprints: list[dict]) -> dict | None:
    """Return the current sprint from a list of sprint dicts.

    Returns the first sprint whose status is NOT ``"DONE"`` and NOT
    ``"Proposed"``.  Falls back to the first sprint if all are DONE or
    Proposed.  Returns ``None`` for an empty list.
    """
    if not sprints:
        return None
    for s in sprints:
        if s.get("status") not in ("DONE", "Proposed"):
            return s
    return sprints[0]


def load_decisions(sdd_root: Path, limit: int = 50) -> list[dict]:
    """Load recent decision records from fleet.db.

    Returns a list of dicts with keys ``timestamp``, ``decider``, ``level``,
    ``description``, ordered by timestamp descending.  Returns ``[]`` if the
    database or ``decisions`` table does not exist.
    """
    db_path = sdd_root / "ledger" / "fleet.db"
    if not db_path.is_file():
        return []
    try:
        conn = sqlite3.connect(db_path)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT decided_at, decider, level, description "
                "FROM decisions ORDER BY decided_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []
    return [
        {
            "timestamp": row["decided_at"],
            "decider": row["decider"],
            "level": row["level"],
            "description": row["description"],
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------- #
# Next-action heuristic (state-dashboard feature)
# ---------------------------------------------------------------------------- #

_SPRINT_LABEL_RE = re.compile(r"Sprint\s+(\d+)", re.IGNORECASE)
_BACKLOG_ID_RE = re.compile(r"\b[A-Z]{2,}-\d{2,3}\b")


def _feature_relpath(sdd_root: Path, feature: Feature) -> str:
    return str(feature.feature_dir.relative_to(repo_root_for(sdd_root))).replace("\\", "/")


def _first_current_pi_sprint_anchor(sdd_root: Path, pi: PIBlock | None) -> tuple[str, list[str]]:
    if not pi:
        return "", []
    current_pi_path = sdd_root / "sprints" / pi.name / "CURRENT_PI.md"
    if not current_pi_path.is_file():
        return "", []
    text = current_pi_path.read_text(encoding="utf-8", errors="replace")
    anchors: list[tuple[int, str, list[str]]] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        if pi.name not in line or "Sprint" not in line:
            continue
        ids = _BACKLOG_ID_RE.findall(line)
        sprint_match = _SPRINT_LABEL_RE.search(line)
        if not ids or not sprint_match:
            continue
        sprint_number = int(sprint_match.group(1))
        anchors.append((sprint_number, f"Sprint {sprint_number}", ids))
    if not anchors:
        return "", []
    _, sprint_label, ids = sorted(anchors, key=lambda item: item[0])[0]
    return sprint_label, ids


def _active_sprint_pi(sdd_root: Path) -> PIBlock | None:
    sprints_dir = sdd_root / "sprints"
    if not sprints_dir.is_dir():
        return None
    candidates: list[PIBlock] = []
    for current_pi_path in sprints_dir.glob("PI-*/CURRENT_PI.md"):
        try:
            text = current_pi_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"status:\s*active", text, re.IGNORECASE) or "Status: **ACTIVE**" in text:
            candidates.append(PIBlock(
                name=current_pi_path.parent.name,
                title="",
                is_current=True,
            ))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: int(item.name.split("-", 1)[1]), reverse=True)[0]


def _read_current_pi_title(sdd_root: Path, pi_name: str) -> str:
    """Read the PI title from sprints/<pi_name>/CURRENT_PI.md H1 line.

    Expects a heading of the form ``# PI-6: <title>``; returns the text after
    the colon with any trailing parenthetical stripped. Returns "" if the file
    or heading is missing.
    """
    current_pi_path = sdd_root / "sprints" / pi_name / "CURRENT_PI.md"
    if not current_pi_path.is_file():
        return ""
    try:
        text = current_pi_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    heading_re = re.compile(rf"^#\s+{re.escape(pi_name)}\s*:\s*(.+?)\s*$")
    for line in text.splitlines():
        m = heading_re.match(line)
        if m:
            title = re.sub(r"\s*\([^)]*\)\s*$", "", m.group(1).strip()).strip()
            return title
    return ""


def resolve_display_pi(
    sdd_root: Path,
    pis: list[PIBlock],
    override: str | None = None,
) -> PIBlock | None:
    """Resolve the PI to display in the dashboard header (SDD-042).

    An explicit override always wins (parity with current_pi). Otherwise prefer
    the highest-numbered ACTIVE sprint PI (from sprints/PI-*/CURRENT_PI.md),
    resolving its title in order: (a) reuse a roadmap PIBlock of the same name,
    (b) read the title from the PI's CURRENT_PI.md H1, (c) fall back to the
    active block as-is. When no sprint is ACTIVE, fall back to the
    roadmap-derived current_pi (no hard-coded PI).
    """
    if override:
        return current_pi(pis, override=override)
    active = _active_sprint_pi(sdd_root)
    if active is None:
        return current_pi(pis)
    # (a) reuse a roadmap block with the same name (carries title + checkboxes)
    for block in pis:
        if block.name == active.name:
            return block
    # (b) read the title from the PI's CURRENT_PI.md H1 line
    title = _read_current_pi_title(sdd_root, active.name)
    if title:
        return PIBlock(name=active.name, title=title, is_current=True)
    # (c) fall back to the active block as-is (empty title)
    return active


def _backlog_ids_for_sprint(sdd_root: Path, pi_name: str, sprint_label: str) -> list[str]:
    backlog_path = sdd_root / "backlog" / "BACKLOG.md"
    if not backlog_path.is_file() or not pi_name or not sprint_label:
        return []
    ids: list[str] = []
    for line in backlog_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        item_id = cells[0]
        sprint = cells[8]
        if _BACKLOG_ID_RE.fullmatch(item_id) and pi_name in sprint and sprint_label in sprint:
            ids.append(item_id)
    return ids


def _feature_for_backlog_id(sdd_root: Path, features: list[Feature], backlog_id: str) -> Feature | None:
    needle = backlog_id.lower()
    weak_match: Feature | None = None
    strong_re = re.compile(rf"(?:^# .*\b{re.escape(backlog_id)}\b|Spec ID:\s*{re.escape(backlog_id)}\b)", re.IGNORECASE | re.MULTILINE)
    for feature in features:
        if needle in feature.name.lower() or needle in feature.feature_dir.name.lower():
            return feature
        for artifact_name in ("clarify.md", "spec.md", "validation.md", "tasks.md", "plan.md"):
            artifact = feature.feature_dir / artifact_name
            if not artifact.is_file():
                continue
            try:
                text = artifact.read_text(encoding="utf-8", errors="replace")
                if strong_re.search(text):
                    return feature
                if weak_match is None and needle in text.lower():
                    weak_match = feature
            except OSError:
                continue
    return weak_match


def _unchecked_required_count(feature_dir: Path) -> int:
    validation_path = feature_dir / "validation.md"
    if not validation_path.is_file():
        return 0
    try:
        text = validation_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return len(re.findall(r"^\s*- \[ \]\s+\*\*R\d+\b", text, re.MULTILINE))


def _git_recency_timestamp(sdd_root: Path, feature_dir: Path) -> int:
    rel = str(feature_dir.relative_to(repo_root_for(sdd_root))).replace("\\", "/")
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(repo_root_for(sdd_root)),
            timeout=2,
        )
    except (subprocess.SubprocessError, OSError):
        return 0
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip().splitlines()[0])
    except (IndexError, ValueError):
        return 0


def _derive_current_sprint_focus(
    sdd_root: Path,
    pi: PIBlock | None,
    features: list[Feature],
) -> tuple[str, str, str | None] | None:
    anchor_pi = _active_sprint_pi(sdd_root) or pi
    sprint_label, current_pi_ids = _first_current_pi_sprint_anchor(sdd_root, anchor_pi)
    if not current_pi_ids or not anchor_pi:
        return None
    backlog_ids = set(_backlog_ids_for_sprint(sdd_root, anchor_pi.name, sprint_label))
    scoped_ids = [item_id for item_id in current_pi_ids if item_id in backlog_ids]
    if not scoped_ids:
        scoped_ids = current_pi_ids

    candidates: list[tuple[str, Feature, int]] = []
    for item_id in scoped_ids:
        feature = _feature_for_backlog_id(sdd_root, features, item_id)
        if feature is None:
            continue
        candidates.append((item_id, feature, _unchecked_required_count(feature.feature_dir)))
    if not candidates:
        return None

    required_candidates = [candidate for candidate in candidates if candidate[2] > 0]
    pool = required_candidates or candidates
    enriched = [
        (item_id, feature, unchecked_required, _git_recency_timestamp(sdd_root, feature.feature_dir))
        for item_id, feature, unchecked_required in pool
    ]
    item_id, feature, unchecked_required, _ = sorted(
        enriched,
        key=lambda candidate: (-candidate[3], scoped_ids.index(candidate[0])),
    )[0]
    if unchecked_required:
        action = f"Finish validation for '{feature.name}' ({item_id})"
        reason = (
            f"Current {anchor_pi.name} {sprint_label} anchor with {unchecked_required} "
            "unchecked REQUIRED validation item(s)."
        )
    else:
        action = f"Continue current sprint anchor '{feature.name}' ({item_id})"
        reason = f"Current {anchor_pi.name} {sprint_label} anchor from CURRENT_PI and BACKLOG."
    return action, reason, _feature_relpath(sdd_root, feature)


def _derive_next_action_fallback(
    sdd_root: Path,
    pi: PIBlock | None,
    features: list[Feature],
) -> tuple[str, str, str | None]:
    in_flight = [f for f in features if f.stage == "IMPLEMENT"]
    if in_flight:
        f = in_flight[0]
        return (
            f"Finish implementation of '{f.name}'",
            f"Only feature in IMPLEMENT stage ({f.notes}). Quality gate: do not start new work while a feature is in flight.",
            _feature_relpath(sdd_root, f),
        )
    in_review = [f for f in features if f.stage == "REVIEW"]
    if in_review:
        f = in_review[0]
        return (
            f"Close out '{f.name}' (currently in REVIEW)",
            f"Two-stage review then mark DONE. {f.notes}",
            _feature_relpath(sdd_root, f),
        )
    if pi:
        for done, label in pi.checkboxes:
            if not done:
                return (
                    f"Start: '{label}'",
                    f"Highest-priority unstarted commitment in {pi.name}. Run /clarify to start the lifecycle.",
                    "spec-driven-development/constitution/roadmap.md",
                )
    return ("Open PI-2 planning or pick from backlog", "No active in-flight work.",
            "spec-driven-development/backlog/BACKLOG.md")


def derive_next_action(sdd_root: Path, pi: PIBlock | None, features: list[Feature]) -> tuple[str, str, str | None]:
    sprint_focus = _derive_current_sprint_focus(sdd_root, pi, features)
    if sprint_focus:
        return sprint_focus
    return _derive_next_action_fallback(sdd_root, pi, features)


# ---------------------------------------------------------------------------- #
# Markdown renderer -- SDD-002 7-section format
# ---------------------------------------------------------------------------- #

def render_markdown(*, generated_date: str, pi: PIBlock | None, features: list[Feature],
                    backlog: list[BacklogItem], roster: dict, ledger: LedgerView,
                    next_action: tuple[str, str, str | None],
                    user_gates: list[UserGate] | None = None) -> str:
    """Produce state.md in the canonical 7-section format required by SDD-002.

    Sections (in order):
      1. Header
      2. Spec Pipeline
      3. Sprint Plan
      4. Fleet
      5. Recently Completed
      6. Blockers
      7. Next Milestones
    """
    out: list[str] = []

    # ---- 1. Header --------------------------------------------------------
    pi_label = f"{pi.name} ({pi.title})" if pi else "no PI active"
    sprint_label = "Symbolic -- AI fleet compresses wall-clock time"
    focus_line = next_action[0] if next_action else ""
    out += ["# Executive State", "",
            f"Generated date: {generated_date}",
            f"Current PI: {pi_label}",
            f"Active sprint: {sprint_label}",
            f"Active focus: {focus_line}", ""]
    if pi:
        out += [f"PI progress: {pi.done}/{pi.total} commitments complete ({pi.pct}%)", ""]

    # ---- 2. Spec Pipeline -------------------------------------------------
    out += ["## Spec Pipeline", "",
            "| Feature | Stage | Status | Notes |",
            "|---------|-------|--------|-------|"]
    if features:
        for f in features:
            out.append(f"| {f.name} | {f.stage} | {f.status_line or '-'} | {f.notes} |")
    else:
        out.append("| _(no features)_ | -- | -- | -- |")
    out.append("")

    # ---- 3. Sprint Plan ---------------------------------------------------
    out += ["## Sprint Plan", ""]
    if backlog:
        by_sprint: dict[str, list[BacklogItem]] = {}
        for item in backlog:
            key = item.sprint or "Unassigned"
            by_sprint.setdefault(key, []).append(item)
        for sprint_key in sorted(by_sprint.keys()):
            if sprint_key.lower() in ("unscheduled", "unassigned"):
                continue
            out.append(f"### {sprint_key}")
            out.append("")
            out.append("| ID | Title | Priority | RICE | Status |")
            out.append("|----|-------|----------|------|--------|")
            for it in by_sprint[sprint_key]:
                out.append(f"| {it.pid} | {it.title} | {it.priority} | {it.rice} | {it.status} |")
            out.append("")
    else:
        out += ["_no items_", ""]

    # ---- 4. Fleet ---------------------------------------------------------
    out += ["## Fleet", "",
            f"- Principals: {roster['principals']}",
            f"- Generic workers: {roster['generic']}",
            f"- Specialists: {roster['specialist']}",
            f"- Total agents: {roster['total_agents']}",
            f"- Skills: {roster['total_skills']} across {roster.get('skill_categories', 0)} categories", ""]

    # ---- 5. Recently Completed -------------------------------------------
    out += ["## Recently Completed", ""]
    if not ledger.available:
        out += ["_fleet.db not initialized; no ledger data to summarize_", ""]
    elif not ledger.recent_success:
        out += ["_no successful dispatches yet_", ""]
    else:
        out += ["| When | Feature | Task | Agent |",
                "|------|---------|------|-------|"]
        for d in ledger.recent_success:
            when = d.get("outcome_at") or d.get("dispatched_at") or ""
            out.append(f"| {when} | {d.get('feature_dir','')} | {d.get('task_title','')} | {d.get('agent_id','')} |")
        out.append("")

    # ---- 6. Blockers ------------------------------------------------------
    out += ["## Blockers", ""]
    blocking_gates = active_user_gates(user_gates or [])
    if blocking_gates:
        out += [
            "### Pending User Gates",
            "",
            "| Feature | Gate | Blocks | Evidence Need | Next Action |",
            "|---------|------|--------|---------------|-------------|",
        ]
        for gate in blocking_gates:
            out.append(
                f"| {gate.feature} | {gate.gate_id} (`{gate.gate_type}`) | "
                f"`{gate.blocking_scope}` | {gate.evidence_type or '-'} | "
                f"{gate.next_action or '-'} |"
            )
        out += [
            "",
            "_Generated executive surfaces are visibility only; they are not approval evidence._",
            "",
        ]
    if not ledger.available:
        out += ["_fleet.db not initialized; no blockers known_", ""]
    elif not ledger.blockers:
        out += ["_none -- no dispatches without outcome older than 24h_", ""]
    else:
        out += ["| Dispatched | Feature | Task | Agent | Age |",
                "|-----------|---------|------|-------|-----|"]
        for d in ledger.blockers:
            out.append(f"| {d.get('dispatched_at','')} | {d.get('feature_dir','')} | "
                       f"{d.get('task_title','')} | {d.get('agent_id','')} | stale |")
        out.append("")

    # ---- 7. Next Milestones ----------------------------------------------
    out += ["## Next Milestones", ""]
    if pi and pi.checkboxes:
        unstarted = [label for done, label in pi.checkboxes if not done]
        if unstarted:
            for label in unstarted[:5]:
                out.append(f"- {label}")
        else:
            out.append("_all PI commitments complete -- plan next PI_")
    else:
        out.append("_no PI commitments registered_")
    out += ["",
            "---",
            "",
            "_Auto-generated by `cli/state_builder.py`. SDD-002 contract: 7-section format. "
            "Visual dashboard: `python state_builder.py serve`._",
            ""]
    return "\n".join(out)


# ---------------------------------------------------------------------------- #
# HTML renderer (state-dashboard feature) -- Bridge tokens, v0.2 UX
# ---------------------------------------------------------------------------- #

# Cumulative completion weight per stage (UX feedback 2026-05-16):
# weights chosen so a feature in IMPLEMENT reads as ~80% complete, not 0%.
STAGE_WEIGHT = {
    "IDEA":       0,
    "BACKLOG":    0,
    "CLARIFY":   10,
    "SPEC":      30,
    "PLAN":      40,
    "TASKS":     50,
    "IMPLEMENT": 85,
    "REVIEW":    95,
    "DONE":     100,
}

# One-sentence human mission per PI; surfaced in the dashboard top bar.
# Editable here when a new PI opens. (Future: parse from roadmap.md frontmatter.)
PI_MISSION = {
    "PI-1": "Generalize the framework off the original host project and ship the first dogfood feature end-to-end.",
    "PI-2": "Build the CLI tools that let the fleet self-manage: dispatch, QA, retrospectives, and live state tracking.",
    "PI-3": "Validate portability by bootstrapping the framework onto a completely different second project.",
    "PI-4": "Ship the alpha release: Live UI v2 dashboard, root README, roadmap cleanup, team-ready packaging.",
}


HTML_CSS = """
:root {
  /* Backgrounds */
  --bg-carbon:        #0a0a0a;
  --bg-graphite:      #141413;
  --bg-graphite-2:    #1c1b18;
  --bg-graphite-3:    #232220;
  /* Ink */
  --ink-paper:        #e8e4d8;
  --ink-paper-dim:    #b8b4a8;
  --ink-paper-faint:  #8a8678;
  /* Accent */
  --accent-oxblood:       #ce2029;
  --accent-oxblood-2:     #a01820;
  --accent-oxblood-hover: #e02830;
  /* Signals */
  --signal-amber:     #d29a3b;
  --signal-amber-2:   #e8b85a;
  --signal-amber-3:   #8a6a2a;
  --signal-jade:      #6fa37a;
  --signal-jade-dim:  #486a52;
  /* Structure */
  --rule-line:        #2a2925;
  --focus-ring:       #e8e4d8;
  /* Semantic aliases */
  --color-text-primary:      var(--ink-paper);
  --color-text-secondary:    var(--ink-paper-dim);
  --color-text-tertiary:     var(--ink-paper-faint);
  --color-surface-base:      var(--bg-carbon);
  --color-surface-raised:    var(--bg-graphite);
  --color-surface-overlay:   var(--bg-graphite-2);
  --color-border-default:    var(--rule-line);
  --color-interactive:       var(--accent-oxblood);
  --color-interactive-hover: var(--accent-oxblood-hover);
  --color-status-success:    var(--signal-jade);
  --color-status-warning:    var(--signal-amber);
  --color-status-error:      var(--accent-oxblood);

  /* Type scale */
  --fs-xs: 10px;
  --fs-sm: 11px;
  --fs-base: 13px;
  --fs-md: 14px;
  --fs-lg: 16px;
  --fs-xl: 20px;
  --fs-2xl: 24px;
  --fs-3xl: 32px;
  /* Spacing */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 12px;
  --sp-4: 16px;
  --sp-5: 24px;
  --sp-6: 32px;
}

* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--color-surface-base); color: var(--color-text-primary);
  font-family: ui-monospace, "Berkeley Mono", "JetBrains Mono", Menlo, Consolas, "Courier New", monospace;
  font-size: var(--fs-base); line-height: 1.45;
}
.body-sans {
  font-family: -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
}
a { color: var(--signal-amber-2); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Focus indicators (WCAG AA) ------------------------------------ */
:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

/* Skip link ----------------------------------------------------- */
.skip-link {
  position: absolute; left: -9999px; top: auto;
  width: 1px; height: 1px; overflow: hidden;
}
.skip-link:focus {
  position: fixed; left: var(--sp-3); top: var(--sp-3);
  width: auto; height: auto; padding: var(--sp-2) var(--sp-3);
  background: var(--color-interactive); color: var(--ink-paper);
  z-index: 1000;
}

/* TOP BAR ------------------------------------------------------- */
header.topbar {
  display: flex; align-items: center;
  gap: var(--sp-5); min-height: 72px;
  padding: var(--sp-3) var(--sp-5);
  border-bottom: 2px solid var(--color-interactive);
  background: var(--color-surface-raised);
  position: sticky; top: 0; z-index: 100;
}
.topbar-title {
  font-size: var(--fs-3xl); letter-spacing: 0.12em;
  font-weight: 900; color: var(--color-text-primary);
  margin: 0; padding: 0; line-height: 1; flex-shrink: 0;
  text-transform: uppercase;
}
.topbar-mission {
  font-family: inherit;
  font-size: var(--fs-md); color: var(--color-text-secondary);
  flex-shrink: 1; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
  padding-left: var(--sp-3);
  border-left: 1px solid var(--color-border-default);
}
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); border: 0;
}
.pi-pills { display: flex; gap: var(--sp-1); flex-wrap: wrap; margin-left: auto; flex-shrink: 0; }
.pi-pills .pill {
  padding: var(--sp-1) var(--sp-3);
  border: 1px solid var(--color-border-default);
  background: var(--color-surface-raised);
  color: var(--color-text-secondary);
  font-size: var(--fs-xs); letter-spacing: 0.14em;
  text-transform: uppercase; border-radius: 2px;
}
.pi-pills .pill.current,
.pi-pills .pill.active {
  background: var(--color-interactive);
  border-color: var(--color-interactive);
  color: var(--ink-paper); font-weight: 700;
}
.pi-pills .pill.future { opacity: 0.45; }

/* PROJECT CONTEXT BAR ------------------------------------------- */
.context-section {
  display: flex; align-items: baseline; gap: var(--sp-5); flex-wrap: wrap;
  padding: var(--sp-2) var(--sp-5);
  background: var(--color-surface-raised);
  border-bottom: 1px solid var(--color-border-default);
  font-size: var(--fs-sm); line-height: 20px;
}
.context-item { display: inline-flex; align-items: baseline; gap: var(--sp-2); white-space: nowrap; }
.context-label {
  color: var(--color-text-secondary); font-size: var(--fs-xs);
  text-transform: uppercase; letter-spacing: 0.14em; font-weight: 600;
}
.context-value { color: var(--color-text-primary); }
.context-mission { white-space: normal; max-width: 560px; }
.project-type-badge {
  display: inline-block; padding: 2px var(--sp-2);
  font-size: var(--fs-xs); font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.14em; line-height: 14px;
  color: var(--signal-jade); background: var(--color-surface-raised);
  border: 1px solid var(--signal-jade); border-radius: 2px;
}

.live-pulse {
  display: flex; align-items: center; gap: var(--sp-2);
  font-size: var(--fs-sm); color: var(--color-text-secondary);
  letter-spacing: 0.06em;
}
.live-pulse .dot {
  width: 10px; height: 10px; border-radius: 50%;
  display: inline-block; flex-shrink: 0;
}
.dot.dot-green { background: var(--signal-jade);    animation: pulse-green 1.6s ease-in-out infinite; }
.dot.dot-amber { background: var(--signal-amber);   animation: pulse-amber 2.2s ease-in-out infinite; }
.dot.dot-red   { background: var(--accent-oxblood); animation: pulse-red   1.0s ease-in-out infinite; }
.dot.dot-gray  { background: var(--ink-paper-faint); }
@keyframes pulse-green { 0%,100% { box-shadow: 0 0 0 0 rgba(111,163,122,0.55); } 50% { box-shadow: 0 0 0 8px rgba(111,163,122,0); } }
@keyframes pulse-amber { 0%,100% { box-shadow: 0 0 0 0 rgba(210,154,59,0.55); } 50% { box-shadow: 0 0 0 8px rgba(210,154,59,0); } }
@keyframes pulse-red   { 0%,100% { box-shadow: 0 0 0 0 rgba(206,32,41,0.55); } 50% { box-shadow: 0 0 0 8px rgba(206,32,41,0); } }

.freshness {
  font-size: var(--fs-sm); color: var(--color-text-tertiary);
  letter-spacing: 0.06em;
}

/* LIVE PULSE + FRESHNESS ---------------------------------------- */
main.grid-v3 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    "sprint sprint"
    "next   wip"
    "timeline timeline"
    "pi     pi"
    "agents agents"
    "feed   feed";
  gap: var(--sp-4);
  padding: var(--sp-5);
  opacity: 0;
  animation: fade-in 300ms ease forwards;
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

.zone-sprint   { grid-area: sprint; }
.zone-next     { grid-area: next; }
.zone-wip      { grid-area: wip; }
.zone-timeline { grid-area: timeline; }
.zone-pi       { grid-area: pi; }
.zone-agents   { grid-area: agents; }
.zone-feed     { grid-area: feed; }

main.grid-v3 > section {
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-default);
  padding: var(--sp-4);
}
main.grid-v3 > section h2 {
  margin: 0 0 var(--sp-3) 0;
  font-size: var(--fs-md); letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--color-text-primary);
  font-weight: 700;
  border-bottom: 1px solid var(--color-border-default);
  padding-bottom: var(--sp-2);
}
.empty-state {
  color: var(--color-text-tertiary);
  font-style: italic; padding: var(--sp-3) 0;
}

/* SECTION 1: Sprint --------------------------------------------- */
.sprint-goal {
  color: var(--color-text-secondary);
  font-size: var(--fs-md); margin: 0 0 var(--sp-3) 0;
}
dl.task-counters {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-3); margin: 0 0 var(--sp-3) 0;
}
dl.task-counters > div {
  background: var(--color-surface-overlay);
  padding: var(--sp-2);
  border-left: 3px solid var(--color-border-default);
}
dl.task-counters dt {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  letter-spacing: 0.1em; text-transform: uppercase;
}
dl.task-counters dd {
  margin: var(--sp-1) 0 0 0;
  font-size: var(--fs-xl); color: var(--color-text-primary);
  font-weight: 700;
}
dl.task-counters .c-todo  { border-left-color: var(--color-text-tertiary); }
dl.task-counters .c-doing { border-left-color: var(--signal-amber); }
dl.task-counters .c-done  { border-left-color: var(--signal-jade); }
dl.task-counters .c-block { border-left-color: var(--accent-oxblood); }

.progress-bar {
  height: 12px; background: var(--bg-graphite-3);
  border: 1px solid var(--color-border-default);
  display: flex; overflow: hidden;
}
.progress-bar .seg-done  { background: var(--signal-jade); }
.progress-bar .seg-doing { background: var(--signal-amber); }
.progress-bar .seg-block { background: var(--accent-oxblood); }
.progress-bar .seg-todo  { background: transparent; }

.blockers { margin: var(--sp-3) 0 0 0; padding: 0; list-style: none; }
.blockers li {
  padding: var(--sp-2);
  border-left: 3px solid var(--accent-oxblood);
  background: var(--color-surface-overlay);
  margin-bottom: var(--sp-1);
  color: var(--color-text-secondary);
}

/* SECTION 2: Next ----------------------------------------------- */
.next-action-card {
  background: var(--color-surface-overlay);
  border-left: 3px solid var(--color-interactive);
  padding: var(--sp-3); margin-bottom: var(--sp-3);
}
.next-action-card .label {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  letter-spacing: 0.12em; text-transform: uppercase;
  margin-bottom: var(--sp-1);
}
.next-action-card .title {
  font-size: var(--fs-md); color: var(--color-text-primary);
  font-weight: 700; margin-bottom: var(--sp-1);
}
.next-action-card .why {
  font-size: var(--fs-sm); color: var(--color-text-secondary);
}
.next-action-card .cta {
  display: inline-block; margin-top: var(--sp-2);
  padding: var(--sp-1) var(--sp-3);
  background: var(--color-interactive); color: var(--ink-paper);
  border: 1px solid var(--color-interactive);
  font-size: var(--fs-sm); letter-spacing: 0.1em;
  text-transform: uppercase; transition: background-color 150ms ease;
}
.next-action-card .cta:hover {
  background: var(--color-interactive-hover);
  text-decoration: none;
}
.next-gate, .next-sprint {
  font-size: var(--fs-sm); color: var(--color-text-secondary);
  padding: var(--sp-2) 0;
  border-top: 1px solid var(--color-border-default);
}
.next-gate .label, .next-sprint .label {
  color: var(--color-text-tertiary); letter-spacing: 0.1em;
  text-transform: uppercase; font-size: var(--fs-xs);
  margin-right: var(--sp-2);
}

/* SECTION 3: WIP ------------------------------------------------ */
.swim-lane {
  display: grid;
  grid-template-columns: 200px 1fr 100px;
  gap: var(--sp-3); align-items: center;
  padding: var(--sp-2) 0;
  border-bottom: 1px solid var(--color-border-default);
  transition: background-color 150ms ease;
}
.swim-lane:hover { background: var(--color-surface-overlay); }
.swim-lane:last-child { border-bottom: none; }
.swim-lane .feature-name {
  font-size: var(--fs-sm); color: var(--color-text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.stage-bar {
  display: grid; grid-template-columns: repeat(9, 1fr);
  gap: 2px; height: 14px;
}
.stage-cell {
  background: var(--bg-graphite-3);
  border: 1px solid var(--color-border-default);
}
.stage-cell.active     { background: var(--signal-amber); }
.stage-cell.complete   { background: var(--signal-jade); }
.stage-cell.tone-faint        { background: var(--ink-paper-faint); }
.stage-cell.tone-amber-soft   { background: var(--signal-amber-3); }
.stage-cell.tone-amber        { background: var(--signal-amber); }
.stage-cell.tone-amber-bright { background: var(--signal-amber-2); }
.stage-cell.tone-oxblood      { background: var(--accent-oxblood); }
.stage-cell.tone-jade         { background: var(--signal-jade); }
.swim-lane .stage-text {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  letter-spacing: 0.08em; text-transform: uppercase;
}
.overall-completion {
  margin-top: var(--sp-3); padding-top: var(--sp-2);
  border-top: 1px solid var(--color-border-default);
  font-size: var(--fs-sm); color: var(--color-text-secondary);
}
.overall-completion strong {
  color: var(--color-text-primary); font-size: var(--fs-md);
}

/* SECTION 4: PI Context (details/summary) ---------------------- */
.zone-pi details {
  margin-bottom: var(--sp-2);
  border: 1px solid var(--color-border-default);
  background: var(--color-surface-overlay);
}
.zone-pi summary {
  list-style: none;
  padding: var(--sp-2) var(--sp-3);
  cursor: pointer;
  font-size: var(--fs-sm); letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--color-text-primary);
  position: relative;
  transition: background-color 150ms ease;
}
.zone-pi summary::-webkit-details-marker { display: none; }
.zone-pi summary::marker { content: ""; }
.zone-pi summary::before {
  content: "\25B6";
  display: inline-block;
  margin-right: var(--sp-2);
  font-size: var(--fs-xs);
  color: var(--color-text-tertiary);
  transition: transform 150ms ease;
}
.zone-pi details[open] > summary::before { transform: rotate(90deg); }
.zone-pi summary:hover { background: var(--bg-graphite-3); }
.zone-pi .pi-body { padding: var(--sp-3); }
table.sprint-table {
  width: 100%; border-collapse: collapse;
  font-size: var(--fs-sm);
}
table.sprint-table th, table.sprint-table td {
  padding: var(--sp-1) var(--sp-2);
  text-align: left;
  border-bottom: 1px solid var(--color-border-default);
  color: var(--color-text-secondary);
}
table.sprint-table th {
  font-size: var(--fs-xs); letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--color-text-tertiary);
  font-weight: 400;
}
table.sprint-table tr {
  transition: background-color 150ms ease;
}
table.sprint-table tbody tr:hover {
  background: var(--bg-graphite-3);
}

/* SECTION 5: Agents -------------------------------------------- */
.fleet-summary {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--sp-3); margin-bottom: var(--sp-3);
}
.fleet-stat {
  background: var(--color-surface-overlay);
  padding: var(--sp-2); text-align: center;
}
.fleet-stat .n {
  font-size: var(--fs-xl); color: var(--color-text-primary);
  font-weight: 700;
}
.fleet-stat .l {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  letter-spacing: 0.1em; text-transform: uppercase;
}
.defer-notice {
  font-size: var(--fs-sm); color: var(--color-text-tertiary);
  font-style: italic; padding: var(--sp-2) 0;
}
/* Agent hierarchy tree */
.agent-tree {
  font-size: var(--type-label, var(--fs-sm));
  line-height: 24px;
  padding: var(--space-md, var(--sp-2)) var(--space-lg, var(--sp-3));
  background: var(--bg-graphite);
  border: 1px solid var(--rule-line);
  margin-bottom: var(--space-xl, var(--sp-3));
  overflow-x: auto;
  white-space: pre;
  font-family: var(--type-mono);
}
.agent-principal { color: var(--accent-oxblood); font-weight: 600; }
.agent-worker { color: var(--ink-paper-dim); }
.agent-tree-chrome { color: var(--ink-paper-faint); }
.agent-tree-action { color: var(--ink-paper-faint); font-weight: 400; }

/* Recent dispatch chain table */
.dispatch-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--type-label, var(--fs-sm));
}
.dispatch-table th {
  text-align: left;
  font-size: var(--type-micro, var(--fs-xs));
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-paper-dim);
  padding: var(--space-sm, var(--sp-1)) var(--space-md, var(--sp-2));
  border-bottom: 1px solid var(--rule-line);
  font-weight: 600;
  white-space: nowrap;
}
.dispatch-table td {
  padding: var(--space-sm, var(--sp-1)) var(--space-md, var(--sp-2));
  border-bottom: 1px solid var(--rule-line);
  color: var(--ink-paper-dim);
  line-height: 22px;
  white-space: nowrap;
}
.dispatch-table tbody tr:hover {
  background: var(--bg-graphite-2);
  transition: background var(--duration-fast, 150ms) var(--easing-default, ease);
}
.dispatch-chain { color: var(--ink-paper-faint); }

/* SECTION 6: Activity Feed ------------------------------------- */
.feed-container {
  max-height: 480px; overflow-y: auto;
  border: 1px solid var(--color-border-default);
  background: var(--bg-graphite-3);
}
.feed-event {
  display: grid;
  grid-template-columns: 90px 90px 1fr;
  gap: var(--sp-3); align-items: baseline;
  padding: var(--sp-2) var(--sp-3);
  border-bottom: 1px solid var(--color-border-default);
  font-size: var(--fs-sm);
  transition: background-color 150ms ease;
}
.feed-event:hover { background: var(--color-surface-overlay); }
.feed-event:last-child { border-bottom: none; }
.feed-event .when {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
}
.feed-event .badge {
  font-size: var(--fs-xs); letter-spacing: 0.1em;
  text-transform: uppercase; padding: 2px var(--sp-2);
  border: 1px solid var(--color-border-default);
  text-align: center;
}
.feed-event .badge.b-dispatch { color: var(--signal-amber-2); border-color: var(--signal-amber-3); }
.feed-event .badge.b-decision { color: var(--ink-paper); border-color: var(--color-text-secondary); }
.feed-event .badge.b-commit   { color: var(--signal-jade);   border-color: var(--signal-jade-dim); }
.feed-event .desc { color: var(--color-text-secondary); }

/* SECTION 7: Project Timeline ---------------------------------- */
.timeline-legend {
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  margin: 0 0 var(--sp-3) 0; letter-spacing: 0.06em;
}
.tl-key {
  display: inline-block; padding: 1px var(--sp-2);
  border: 1px solid var(--color-border-default); border-radius: 2px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;
}
.tl-key-done    { color: var(--signal-jade);   border-color: var(--signal-jade-dim); }
.tl-key-current { color: var(--signal-amber);  border-color: var(--signal-amber-3); }
.tl-key-future  { color: var(--color-text-tertiary); }

.timeline {
  list-style: none; padding: 0 0 0 var(--sp-4); margin: 0;
  position: relative; counter-reset: tl;
}
.timeline::before {
  content: ""; position: absolute; left: 7px; top: 6px; bottom: 6px;
  width: 2px; background: var(--color-border-default);
}
.tl-item {
  position: relative; display: grid;
  grid-template-columns: 1fr auto; align-items: baseline;
  padding: var(--sp-2) 0 var(--sp-2) var(--sp-3);
}
.tl-marker {
  position: absolute; left: -17px; top: 14px;
  width: 12px; height: 12px; border-radius: 50%;
  border: 2px solid var(--color-surface-raised);
}
.tl-marker-done    { background: var(--signal-jade); }
.tl-marker-current { background: var(--signal-amber); box-shadow: 0 0 0 4px rgba(210,154,59,0.18); }
.tl-marker-future  { background: var(--color-text-tertiary); opacity: 0.6; }

.tl-content { display: flex; align-items: baseline; gap: var(--sp-3); flex-wrap: wrap; }
.tl-date {
  font-family: var(--font-mono, monospace); font-size: var(--fs-xs);
  color: var(--color-text-tertiary); letter-spacing: 0.04em; min-width: 80px;
}
.tl-name { color: var(--color-text-primary); font-weight: 600; }
.tl-item.tl-future .tl-name { color: var(--color-text-secondary); font-weight: 400; }
.tl-stage {
  font-size: var(--fs-xs); padding: 1px var(--sp-2);
  border: 1px solid var(--color-border-default); border-radius: 2px;
  text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;
  color: var(--color-text-tertiary);
}
.tl-item.tl-done    .tl-stage { color: var(--signal-jade);  border-color: var(--signal-jade-dim); }
.tl-item.tl-current .tl-stage { color: var(--signal-amber); border-color: var(--signal-amber-3); }

/* FOOTER -------------------------------------------------------- */
footer[role="contentinfo"] {
  height: 32px;
  display: flex; align-items: center; justify-content: center;
  gap: var(--sp-3);
  border-top: 1px solid var(--color-border-default);
  background: var(--color-surface-raised);
  font-size: var(--fs-xs); color: var(--color-text-tertiary);
  letter-spacing: 0.1em; text-transform: uppercase;
}

/* RESPONSIVE: Tablet single-column ----------------------------- */
@media (max-width: 1279px) {
  main.grid-v3 {
    grid-template-columns: 1fr;
    grid-template-areas:
      "sprint"
      "next"
      "wip"
      "timeline"
      "pi"
      "agents"
      "feed";
  }
  dl.task-counters { grid-template-columns: repeat(2, 1fr); }
  .fleet-summary { grid-template-columns: repeat(2, 1fr); }
  .swim-lane { grid-template-columns: 140px 1fr 80px; }
}

/* MOTION REDUCTION --------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: 0s !important;
    animation-duration: 0s !important;
    animation-iteration-count: 1 !important;
  }
}
"""
COMMIT_TYPE_TONE = {
    "feat":     "jade",  "fix":      "oxblood", "docs":    "amber-soft",
    "chore":    "faint", "design":   "amber-bright", "plan":   "amber",
    "backlog":  "amber", "test":     "amber-soft", "refactor": "amber-soft",
    "spec":     "amber",
}


def split_commit_type(subject: str) -> tuple[str | None, str]:
    m = re.match(r"^([a-z]+)(\([^)]+\))?:\s*(.+)$", subject)
    if not m:
        return None, subject
    scope = m.group(2) or ""
    rest = m.group(3)
    return m.group(1), (f"{scope} {rest}".strip())


def h(s) -> str:
    return html.escape(str(s) if s is not None else "")


def _pulse(roster: dict, ledger: LedgerView, features: list[Feature]) -> tuple[str, str]:
    """Return (dot_class, text) for the live-pulse indicator in the top bar."""
    in_flight = [d for d in (ledger.recent or []) if d.get("outcome") is None]
    blocked = ledger.blockers or []
    impl_features = [f for f in features if f.stage in ("IMPLEMENT", "TASKS")]
    if blocked:
        return "dot-red", f"{len(blocked)} dispatch{'es' if len(blocked) != 1 else ''} blocked / stale"
    if in_flight:
        bits = [f"{len(in_flight)} dispatch{'es' if len(in_flight) != 1 else ''} in flight"]
        if impl_features:
            bits.append(f"{len(impl_features)} feature{'s' if len(impl_features) != 1 else ''} implementing")
        return "dot-green", " | ".join(bits)
    if impl_features:
        return "dot-amber", f"{len(impl_features)} feature{'s' if len(impl_features) != 1 else ''} implementing, no dispatch in flight"
    return "dot-gray", "fleet idle"


def _weighted_progress(features: list[Feature]) -> int:
    """Mission-level % complete weighted by lifecycle stage."""
    if not features:
        return 0
    total = sum(STAGE_WEIGHT.get(f.stage, 0) for f in features)
    return round(total / len(features))


def _next_what(features: list[Feature]) -> str:
    """One-line forward-looking trajectory for the next-action card."""
    impl = [f for f in features if f.stage == "IMPLEMENT"]
    review = [f for f in features if f.stage == "REVIEW"]
    spec = [f for f in features if f.stage == "SPEC"]
    bits = []
    if impl:
        bits.append(f"finish {len(impl)} in implementation")
    if review:
        bits.append(f"close {len(review)} in review")
    if spec:
        bits.append(f"advance {len(spec)} to plan")
    return "; then ".join(bits) if bits else "open the next backlog item"


def active_user_gates(gates: list[UserGate]) -> list[UserGate]:
    """Return user gates that currently block or require visible action."""
    return [gate for gate in gates if gate.status in ("pending", "blocked")]


def _agents_for_feature(roster: dict, feature: Feature, ledger: LedgerView) -> list[dict]:
    """Best-effort: which agents have been dispatched to this feature recently?"""
    if not ledger.recent:
        return []
    seen: dict[str, dict] = {}
    for d in ledger.recent:
        if (d.get("feature_dir") or "").endswith(feature.feature_dir.name):
            aid = d.get("agent_id", "")
            if aid and aid not in seen:
                role = d.get("agent_role", "?")
                status = "active" if d.get("outcome") is None else "idle"
                seen[aid] = {"id": aid, "role": role, "status": status}
    return list(seen.values())


def _stage_short(stage: str) -> str:
    return {"IDEA": "Idea", "BACKLOG": "Backlog", "CLARIFY": "Clarifying",
            "SPEC": "Specifying", "PLAN": "Planning", "TASKS": "Task breakdown",
            "IMPLEMENT": "Implementing", "REVIEW": "In review", "DONE": "Done"}.get(stage, stage)


def _next_for(feature: Feature) -> str:
    nxt = {"IDEA": "triage to backlog", "BACKLOG": "clarify",
           "CLARIFY": "draft spec", "SPEC": "plan", "PLAN": "decompose tasks",
           "TASKS": "implement", "IMPLEMENT": "review", "REVIEW": "close",
           "DONE": "shipped"}
    return nxt.get(feature.stage, "")


def render_html(*, generated_at: str, pi: PIBlock | None, features: list[Feature],
                roster: dict, ledger: LedgerView, commits: list[tuple[str, str, str]],
                next_action: tuple[str, str, str | None],
                backlog: list[BacklogItem] | None = None,
                live: bool = False, port: int | None = None,
                all_pis: list[PIBlock] | None = None,
                about_pi: str = "", about_sprint: str = "",
                about_focus: str = "",
                sprint_table: list[dict] | None = None,
                current_sprint: dict | None = None,
                sprint_goal: str | None = None,
                decisions: list[dict] | None = None) -> str:
    """Render the v3.0 sprint-first dashboard.

    The page has a fixed 7-section grid: top bar + Current Sprint, What
    Comes Next, WIP Summary, PI Context, Fleet -- Agent Traceability,
    Activity Feed, and a footer.  Each section degrades to an explicit
    empty-state message when its data is missing.
    """

    pi_name = pi.name if pi else "no PI"
    pulse_class, pulse_text = _pulse(roster, ledger, features)

    # ---- TOP BAR pills ---------------------------------------------------
    pi_pills_html = ""
    if all_pis:
        for p in all_pis:
            cls = "pill"
            if p.is_current or (pi and p.name == pi.name):
                cls += " current"
            elif p.pct < 100 and not p.is_current:
                cls += " future"
            pi_pills_html += f'<span class="{cls}">{h(p.name)}</span>'

    refresh_meta = '<meta http-equiv="refresh" content="20">' if live else ""
    live_badge = "live" if live else "static"

    # ---- SECTION 1: Current Sprint --------------------------------------
    if current_sprint:
        sprint_label = f"Sprint {current_sprint.get('num', '?')}: {current_sprint.get('title', '')}"
        status_text = current_sprint.get("status", "Unknown")
        dispatch_count = current_sprint.get("dispatch_count", 0)
        last_outcome = current_sprint.get("last_outcome", "--")

        # Best-effort task-status counters: use feature stages as a proxy
        c_done = sum(1 for f in features if f.stage == "DONE")
        c_doing = sum(1 for f in features if f.stage in ("IMPLEMENT", "REVIEW", "TASKS"))
        c_block = len(ledger.blockers or [])
        c_todo = sum(1 for f in features
                     if f.stage in ("IDEA", "BACKLOG", "CLARIFY", "SPEC", "PLAN"))
        total = max(1, c_done + c_doing + c_block + c_todo)
        seg_done_pct = 100 * c_done / total
        seg_doing_pct = 100 * c_doing / total
        seg_block_pct = 100 * c_block / total
        seg_todo_pct = 100 * c_todo / total

        counters_html = (
            f'<dl class="task-counters" aria-label="Task status counters">'
            f'<div class="c-todo"><dt>To do</dt><dd>{c_todo}</dd></div>'
            f'<div class="c-doing"><dt>Doing</dt><dd>{c_doing}</dd></div>'
            f'<div class="c-done"><dt>Done</dt><dd>{c_done}</dd></div>'
            f'<div class="c-block"><dt>Blocked</dt><dd>{c_block}</dd></div>'
            f'</dl>'
        )
        progress_html = (
            f'<div class="progress-bar" role="img" '
            f'aria-label="Sprint progress: {c_done} done, {c_doing} in progress, '
            f'{c_block} blocked, {c_todo} remaining">'
            f'<div class="seg-done"  style="width:{seg_done_pct:.1f}%"></div>'
            f'<div class="seg-doing" style="width:{seg_doing_pct:.1f}%"></div>'
            f'<div class="seg-block" style="width:{seg_block_pct:.1f}%"></div>'
            f'<div class="seg-todo"  style="width:{seg_todo_pct:.1f}%"></div>'
            f'</div>'
        )

        blockers_html = ""
        if ledger.blockers:
            items = "".join(
                f'<li>{h(b.get("agent_id", "?"))} -- '
                f'{h(b.get("task_title") or b.get("task_id") or "blocked dispatch")}</li>'
                for b in ledger.blockers
            )
            blockers_html = f'<ul class="blockers" aria-label="Active blockers">{items}</ul>'

        goal_text = sprint_goal if sprint_goal else "No sprint goal defined"
        sprint_meta = (
            f'<p class="sprint-meta">'
            f'<span class="status">Status: {h(status_text)}</span> &middot; '
            f'<span>{dispatch_count} dispatches</span> &middot; '
            f'<span>last outcome: {h(last_outcome)}</span>'
            f'</p>'
        )
        sprint_body = (
            f'<p class="sprint-goal">{h(goal_text)}</p>'
            f'{sprint_meta}'
            f'{counters_html}'
            f'{progress_html}'
            f'{blockers_html}'
        )
    else:
        sprint_label = "Current Sprint"
        sprint_body = '<p class="empty-state">No active sprint found.</p>'

    sprint_section = (
        f'<section class="zone-sprint" aria-labelledby="sprint-heading">'
        f'<h2 id="sprint-heading">{h(sprint_label)}</h2>'
        f'{sprint_body}'
        f'</section>'
    )

    # ---- SECTION 2: What Comes Next -------------------------------------
    if next_action and (next_action[0] or next_action[1]):
        action_title, why, link = next_action
        nxt_summary = _next_what(features)
        cta_html = (
            f'<span class="cta">'
            f'Open &rarr; {h(link)}</span>'
            if link else ""
        )
        next_card_html = (
            f'<div class="next-action-card">'
            f'<div class="label">Recommended next action</div>'
            f'<div class="title">{h(action_title)}</div>'
            f'<div class="why">{h(why)} &middot; Trajectory: {h(nxt_summary)}.</div>'
            f'{cta_html}'
            f'</div>'
        )
        # Best-effort next gate / next sprint: use trajectory + sprint table
        next_gate_html = (
            f'<div class="next-gate"><span class="label">Next gate</span>'
            f'{h(_next_what(features))}</div>'
        )
        next_sprint_text = "--"
        if sprint_table and current_sprint:
            cur_num = current_sprint.get("num")
            for s in sprint_table:
                if s.get("num", 0) > (cur_num or 0):
                    next_sprint_text = f"Sprint {s['num']}: {s.get('title', '')}"
                    break
        next_sprint_html = (
            f'<div class="next-sprint"><span class="label">Next sprint</span>'
            f'{h(next_sprint_text)}</div>'
        )
        next_body = next_card_html + next_gate_html + next_sprint_html
    else:
        next_body = '<p class="empty-state">No recommended action available.</p>'

    next_section = (
        f'<section class="zone-next" aria-labelledby="next-heading">'
        f'<h2 id="next-heading">What Comes Next</h2>'
        f'{next_body}'
        f'</section>'
    )

    # ---- SECTION 3: WIP Summary -----------------------------------------
    if features:
        active = sorted([f for f in features if f.stage != "DONE"],
                        key=lambda f: (-STAGE_WEIGHT.get(f.stage, 0), f.name))
        done = sorted([f for f in features if f.stage == "DONE"], key=lambda f: f.name)
        ordered = active + done

        lanes_html_parts: list[str] = []
        for f in ordered:
            tone = STAGE_TONE.get(f.stage, "tone-faint")
            try:
                cur_idx = STAGES.index(f.stage)
            except ValueError:
                cur_idx = 0
            cells = []
            for i, stage in enumerate(STAGES):
                if i < cur_idx:
                    cls = "stage-cell complete"
                elif i == cur_idx:
                    cls = f"stage-cell active {tone}"
                else:
                    cls = "stage-cell"
                cells.append(f'<div class="{cls}" aria-hidden="true"></div>')
            cells_html = "".join(cells)
            aria = (
                f"{f.name}: stage {h(_stage_short(f.stage))} "
                f"({cur_idx + 1} of {len(STAGES)})"
            )
            lanes_html_parts.append(
                f'<div class="swim-lane">'
                f'<span class="feature-name" title="{h(f.notes)}">{h(f.name)}</span>'
                f'<div class="stage-bar" role="img" aria-label="{h(aria)}">{cells_html}</div>'
                f'<span class="stage-text">{h(_stage_short(f.stage))}</span>'
                f'</div>'
            )
        lanes_html = "".join(lanes_html_parts)
        pct = _weighted_progress(features)
        wip_body = (
            f'{lanes_html}'
            f'<div class="overall-completion">'
            f'Overall completion: <strong>{pct}%</strong> '
            f'across {len(features)} feature{"s" if len(features) != 1 else ""}'
            f'</div>'
        )
    else:
        wip_body = '<p class="empty-state">No features registered yet.</p>'

    wip_section = (
        f'<section class="zone-wip" aria-labelledby="wip-heading">'
        f'<h2 id="wip-heading">WIP Summary</h2>'
        f'{wip_body}'
        f'</section>'
    )

    # ---- SECTION 4: PI Context ------------------------------------------
    if all_pis:
        details_parts: list[str] = []
        for p in all_pis:
            is_open = p.is_current or (pi and p.name == pi.name)
            open_attr = " open" if is_open else ""
            # Sprint table: only render rich table for the current PI
            table_html = ""
            if is_open and sprint_table:
                rows = "".join(
                    f"<tr>"
                    f"<td>{s.get('num', '?')}</td>"
                    f"<td>{h(s.get('title', ''))}</td>"
                    f"<td>{h(s.get('status', ''))}</td>"
                    f"<td>{s.get('dispatch_count', 0)}</td>"
                    f"<td>{h(s.get('last_outcome', '--'))}</td>"
                    f"</tr>"
                    for s in sprint_table
                )
                table_html = (
                    f'<table class="sprint-table">'
                    f'<thead><tr>'
                    f'<th>Sprint</th><th>Title</th><th>Status</th>'
                    f'<th>Dispatches</th><th>Last Outcome</th>'
                    f'</tr></thead>'
                    f'<tbody>{rows}</tbody>'
                    f'</table>'
                )
            else:
                table_html = (
                    f'<p class="empty-state">'
                    f'{h(p.title)} &middot; {p.pct}% complete'
                    f'</p>'
                )
            details_parts.append(
                f'<details{open_attr}>'
                f'<summary>{h(p.name)} -- {h(p.title)}</summary>'
                f'<div class="pi-body">{table_html}</div>'
                f'</details>'
            )
        pi_body = "".join(details_parts)
    else:
        pi_body = '<p class="empty-state">No Program Increments found in roadmap.</p>'

    pi_section = (
        f'<section class="zone-pi" aria-labelledby="pi-heading">'
        f'<h2 id="pi-heading">PI Context</h2>'
        f'{pi_body}'
        f'</section>'
    )

    # ---- SECTION 5: Fleet -- Agent Traceability ------------------------------
    def _stat(n: int, label: str) -> str:
        return (
            f'<div class="fleet-stat">'
            f'<div class="n">{n}</div><div class="l">{h(label)}</div>'
            f'</div>'
        )

    # Workers = generic + specialist
    worker_count = roster.get("generic", 0) + roster.get("specialist", 0)
    # Active = dispatches with outcome IS NULL
    active_count = sum(
        1 for d in (ledger.recent or []) if d.get("outcome") is None
    )
    # Total dispatches
    total_dispatches = len(ledger.recent or [])

    fleet_stats_html = (
        f'<div class="fleet-summary">'
        f'{_stat(roster.get("principals", 0), "Principals")}'
        f'{_stat(worker_count, "Workers")}'
        f'{_stat(active_count, "Active")}'
        f'{_stat(total_dispatches, "Total Dispatches")}'
        f'</div>'
    )

    # -- Agent hierarchy tree --
    agents_list = roster.get("agents") or []

    # Build dispatch map: agent_id -> list of dispatches
    _dispatch_map: dict[str, list[dict]] = {}
    for d in (ledger.recent or []):
        aid = d.get("agent_id", "")
        _dispatch_map.setdefault(aid, []).append(d)

    # Separate principals and workers
    principals = [a for a in agents_list if a.get("kind") == "principal"]
    workers = [a for a in agents_list if a.get("kind") != "principal"]

    # Build worker -> principal mapping based on dispatches
    # Workers are shown under the principal that dispatched them (heuristic:
    # if the worker has dispatches, show under SW Dev; otherwise under EM)
    worker_by_principal: dict[str, list[dict]] = {}
    for p in principals:
        worker_by_principal[p["id"]] = []

    # Assign workers with dispatches under SW Dev-like principals, others under EM
    sw_dev_id = ""
    em_id = ""
    for p in principals:
        role_lower = (p.get("role") or "").lower()
        if "sw" in role_lower or "software" in role_lower or "dev" in role_lower:
            sw_dev_id = p["id"]
        if "exec" in role_lower or "em" in role_lower or "manager" in role_lower:
            em_id = p["id"]
    # Fallback: use first principal as EM, second with dev role as SW Dev
    if not em_id and principals:
        em_id = principals[0]["id"]
    if not sw_dev_id and len(principals) > 1:
        sw_dev_id = principals[1]["id"]
    elif not sw_dev_id and principals:
        sw_dev_id = principals[0]["id"]

    for w in workers:
        wid = w.get("id", "")
        if wid in _dispatch_map:
            worker_by_principal.setdefault(sw_dev_id, []).append(w)
        else:
            worker_by_principal.setdefault(em_id, []).append(w)

    def _status_dot(agent_id: str) -> str:
        """Return jade dot if idle, oxblood if has active dispatch."""
        has_active = any(
            d.get("outcome") is None
            for d in _dispatch_map.get(agent_id, [])
        )
        if has_active:
            return '<span class="status-dot dot-oxblood" aria-label="active"></span>'
        return '<span class="status-dot dot-jade" aria-label="idle"></span>'

    tree_lines: list[str] = []
    for pi_idx, p in enumerate(principals):
        is_last_principal = (pi_idx == len(principals) - 1)
        branch = "\u2514\u2500\u2500 " if is_last_principal else "\u251c\u2500\u2500 "
        continuation = "    " if is_last_principal else "\u2502   "
        p_role = h(p.get("role", p.get("id", "")))
        p_id = h(p.get("id", ""))
        dot = _status_dot(p.get("id", ""))
        tree_lines.append(
            f'<span class="agent-tree-chrome">{branch}</span>'
            f'<span class="agent-principal">{p_role} ({p_id})</span>  {dot}'
        )
        # Show workers assigned to this principal
        assigned_workers = worker_by_principal.get(p["id"], [])
        # Also show dispatches for this principal's workers
        for wi, w in enumerate(assigned_workers):
            is_last_worker = (wi == len(assigned_workers) - 1)
            w_branch = "\u2514\u2500\u2500 " if is_last_worker else "\u251c\u2500\u2500 "
            wid = w.get("id", "")
            dispatches = _dispatch_map.get(wid, [])
            if dispatches:
                for di, d in enumerate(dispatches):
                    is_last_d = (di == len(dispatches) - 1) and is_last_worker
                    d_branch = "\u2514\u2500\u2500 " if is_last_d else "\u251c\u2500\u2500 "
                    task_ref = h(d.get("task_id", ""))
                    task_title = h(d.get("task_title", ""))
                    tree_lines.append(
                        f'<span class="agent-tree-chrome">{continuation}{d_branch}</span>'
                        f'<span class="agent-tree-action">dispatched: </span>'
                        f'<span class="agent-worker">{h(wid)}</span>'
                        f'<span class="agent-tree-action"> &rarr; {task_ref} {task_title}</span>'
                    )
            else:
                tree_lines.append(
                    f'<span class="agent-tree-chrome">{continuation}{w_branch}</span>'
                    f'<span class="agent-worker">{h(wid)}</span>'
                    f'<span class="agent-tree-action"> (idle)</span>'
                )

    # Build the EM root line
    em_agent = next((a for a in principals if a.get("id") == em_id), None)
    em_label = ""
    if em_agent:
        em_role = h(em_agent.get("role", "EM"))
        em_label = f'<span class="agent-principal">{em_role} ({h(em_id)})</span>  {_status_dot(em_id)}'
    elif principals:
        em_label = f'<span class="agent-principal">{h(principals[0].get("role", "EM"))}</span>'

    agent_tree_html = (
        f'<div class="agent-tree" role="img" aria-label="Agent hierarchy tree">'
        f'{em_label}\n'
        + "\n".join(tree_lines)
        + f'</div>'
    ) if agents_list else ""

    # -- Recent dispatches table --
    dispatch_rows = ""
    for d in (ledger.recent or []):
        task_id = h(d.get("task_id", ""))
        agent_id = h(d.get("agent_id", ""))
        task_title = h(d.get("task_title", ""))
        outcome = d.get("outcome") or "pending"
        outcome_label = h(outcome.upper() if outcome else "PENDING")
        dot_cls = "dot-jade" if outcome == "success" else (
            "dot-oxblood" if outcome == "failed" else "dot-amber"
        )
        # Chain: SW Dev -> worker (simplified; real chain from ledger)
        chain = f'SW Dev &rarr; {agent_id}'
        dispatch_rows += (
            f'<tr>'
            f'<td>{task_id}</td>'
            f'<td><span class="dispatch-chain">{chain}</span></td>'
            f'<td>{task_title}</td>'
            f'<td><span class="status-dot {dot_cls}" aria-hidden="true"></span> {outcome_label}</td>'
            f'</tr>'
        )

    dispatch_table_html = ""
    if dispatch_rows:
        dispatch_table_html = (
            f'<table class="dispatch-table">'
            f'<thead><tr>'
            f'<th>Task</th><th>Chain</th><th>Artifact</th><th>Status</th>'
            f'</tr></thead>'
            f'<tbody>{dispatch_rows}</tbody>'
            f'</table>'
        )

    agents_section = (
        f'<section class="zone-agents" aria-labelledby="agents-heading">'
        f'<h2 id="agents-heading">Fleet -- Agent Traceability</h2>'
        f'{fleet_stats_html}'
        f'{agent_tree_html}'
        f'{dispatch_table_html}'
        f'</section>'
    )

    # ---- SECTION 6: Activity Feed ---------------------------------------
    feed: list[dict] = []
    if ledger.recent:
        for d in ledger.recent:
            actor = d.get("agent_id", "?")
            outcome = d.get("outcome") or "pending"
            feed.append({
                "ts": d.get("dispatched_at", ""),
                "kind": "DISPATCH",
                "actor": actor,
                "desc": (
                    f"{d.get('task_id', '')} {d.get('task_title', '')}"
                    f" [{outcome}]"
                ),
            })
    if decisions:
        for dec in decisions:
            feed.append({
                "ts": dec.get("timestamp", ""),
                "kind": "DECISION",
                "actor": dec.get("decider", "?"),
                "desc": (
                    f"L{dec.get('level', '?')}: "
                    f"{dec.get('description', '')}"
                ),
            })
    for sha, subj, rel in commits:
        feed.append({
            "ts": rel,
            "kind": "COMMIT",
            "actor": sha[:7],
            "desc": subj,
        })

    if feed:
        # Sort heuristically: dispatches/decisions have ISO timestamps, commits
        # use relative date strings.  Prefer ISO timestamps first.
        def _key(e: dict) -> tuple[int, str]:
            ts = e["ts"] or ""
            return (0 if "T" in ts or "-" in ts else 1, ts)
        feed.sort(key=_key, reverse=True)
        rows = []
        for ev in feed[:50]:
            tone = ev["kind"].lower()
            rows.append(
                f'<div class="feed-event">'
                f'<span class="when">{h(ev["ts"]) or "--"}</span>'
                f'<span class="badge b-{tone}">{ev["kind"]}</span>'
                f'<span class="desc">'
                f'<strong>{h(ev["actor"])}</strong> {h(ev["desc"])}'
                f'</span>'
                f'</div>'
            )
        feed_html = "".join(rows)
    else:
        feed_html = '<div class="empty-state">No activity recorded yet.</div>'

    feed_section = (
        f'<section class="zone-feed" aria-labelledby="feed-heading">'
        f'<h2 id="feed-heading">Activity Feed</h2>'
        f'<div class="feed-container" role="log" aria-live="off" tabindex="0">'
        f'{feed_html}'
        f'</div>'
        f'</section>'
    )

    # ---- TIMELINE SECTION (chronological progression, IDEA 2026-06-03) ---
    # Group features by stage; sort DONE by date; show current + next
    done_feats = sorted(
        [f for f in features if f.stage == "DONE"],
        key=lambda x: x.created,
    )
    inflight_feats = [
        f for f in features
        if f.stage in ("IMPLEMENT", "TASKS", "PLAN", "SPEC", "CLARIFY")
    ]
    inflight_feats.sort(key=lambda x: x.created)
    # Next from backlog (top 3 P1/P2)
    _backlog = backlog or []
    next_backlog = [b for b in _backlog if b.priority in ("P1", "P2")][:3]

    timeline_items_html: list[str] = []
    # Past: DONE
    for f in done_feats:
        timeline_items_html.append(
            f'<li class="tl-item tl-done">'
            f'<div class="tl-marker tl-marker-done" aria-hidden="true"></div>'
            f'<div class="tl-content">'
            f'<span class="tl-date">{h(f.created)}</span>'
            f'<span class="tl-name">{h(f.name)}</span>'
            f'<span class="tl-stage">DONE</span>'
            f'</div>'
            f'</li>'
        )
    # Present: in-flight
    for f in inflight_feats:
        stage_class = f.stage.lower()
        timeline_items_html.append(
            f'<li class="tl-item tl-current">'
            f'<div class="tl-marker tl-marker-current" aria-hidden="true"></div>'
            f'<div class="tl-content">'
            f'<span class="tl-date">{h(f.created)}</span>'
            f'<span class="tl-name">{h(f.name)}</span>'
            f'<span class="tl-stage tl-stage-{stage_class}">{h(f.stage)}</span>'
            f'</div>'
            f'</li>'
        )
    # Future: next from backlog
    for b in next_backlog:
        timeline_items_html.append(
            f'<li class="tl-item tl-future">'
            f'<div class="tl-marker tl-marker-future" aria-hidden="true"></div>'
            f'<div class="tl-content">'
            f'<span class="tl-date">{h(b.priority)}</span>'
            f'<span class="tl-name">{h(b.title)}</span>'
            f'<span class="tl-stage">QUEUED</span>'
            f'</div>'
            f'</li>'
        )

    timeline_body = (
        f'<ol class="timeline" aria-label="Project timeline">'
        f'{"".join(timeline_items_html)}'
        f'</ol>'
        if timeline_items_html else
        '<div class="empty-state">No timeline data yet.</div>'
    )
    timeline_section = (
        f'<section class="zone-timeline" aria-labelledby="timeline-heading">'
        f'<h2 id="timeline-heading">Project Timeline</h2>'
        f'<p class="timeline-legend">'
        f'<span class="tl-key tl-key-done">Done</span> &middot; '
        f'<span class="tl-key tl-key-current">In Progress</span> &middot; '
        f'<span class="tl-key tl-key-future">Next</span> &middot; '
        f'serial-first execution (no parallel work unless tasks are truly independent)'
        f'</p>'
        f'{timeline_body}'
        f'</section>'
    )

    # ---- CONTEXT BAR (mockup lines 1380-1401) ----------------------------
    if about_pi and about_sprint and about_focus:
        about_dynamic = f'{h(about_pi)} | {h(about_sprint)} | {h(about_focus)}'
    else:
        about_dynamic = h(ABOUT_FALLBACK)

    context_section_html = (
        f'<section class="context-section" aria-label="Project context">'
        f'<div class="context-item">'
        f'<span class="context-label">Project</span>'
        f'<span class="context-value">{h(PROJECT_SUBTITLE)}</span>'
        f'</div>'
        f'<div class="context-item">'
        f'<span class="context-label">Type</span>'
        f'<span class="project-type-badge">{h(PROJECT_TYPE)}</span>'
        f'</div>'
        f'<div class="context-item">'
        f'<span class="context-label">Owner</span>'
        f'<span class="context-value">{h(PROJECT_OWNER)}</span>'
        f'</div>'
        f'<div class="context-item">'
        f'<span class="context-label">Stack</span>'
        f'<span class="context-value">{h(PROJECT_STACK)}</span>'
        f'</div>'
        f'<div class="context-item">'
        f'<span class="context-label">Mission</span>'
        f'<span class="context-value context-mission">{h(PROJECT_MISSION)}</span>'
        f'</div>'
        f'<div class="context-item">'
        f'<span class="context-label">Focus</span>'
        f'<span class="context-value">{about_dynamic}</span>'
        f'</div>'
        f'</section>'
    )

    # ---- FOOTER ----------------------------------------------------------
    mode_text = f"live mode @ :{port}" if (live and port) else "file mode"
    footer_html = (
        f'<footer role="contentinfo">'
        f'<span>{h(generated_at)}</span> &middot; '
        f'<span>v3.0 (sprint-first)</span> &middot; '
        f'<span>stdlib only</span> &middot; '
        f'<span>{h(mode_text)}</span> &middot; '
        f'<span>{h(live_badge)}</span>'
        f'</footer>'
    )

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'self'">
{refresh_meta}
<title>Bridge -- {h(pi_name)} -- {h(generated_at)}</title>
<style>{HTML_CSS}</style>
</head><body>
<a href="#main" class="skip-link">Skip to main content</a>
<header role="banner" class="topbar">
  <h1 class="topbar-title">{h(PROJECT_TITLE)}</h1>
  <span class="topbar-mission">{h(PROJECT_SUBTITLE)}</span>
  <nav class="pi-pills" aria-label="Program Increments">{pi_pills_html}</nav>
  <div class="live-pulse">
    <span class="dot {pulse_class}" aria-hidden="true"></span>
    <span>{h(pulse_text)}</span>
  </div>
  <div class="freshness" aria-live="polite">{h(generated_at)}</div>
</header>
{context_section_html}
<main id="main" role="main" class="grid-v3">
  {sprint_section}
  {next_section}
  {wip_section}
  {timeline_section}
  {pi_section}
  {agents_section}
  {feed_section}
</main>
{footer_html}
</body></html>
"""


def inject_user_gates_html(html_doc: str, user_gates: list[UserGate]) -> str:
    """Inject pending user-gate visibility into the generated dashboard HTML.

    Kept outside render_html because that function has an Article X footprint
    lock from SDD-FDC-001.
    """
    blocking_gates = active_user_gates(user_gates)
    if not blocking_gates:
        return html_doc
    gate_items = "".join(
        f'<li><strong>{h(gate.feature)} / {h(gate.gate_id)}</strong> '
        f'(<code>{h(gate.gate_type)}</code>) blocks '
        f'<code>{h(gate.blocking_scope)}</code>; needs '
        f'{h(gate.evidence_type or "approval evidence")}; next: '
        f'{h(gate.next_action or "record approval evidence")}</li>'
        for gate in blocking_gates
    )
    gates_html = (
        f'<div class="next-action-card user-gates-card">'
        f'<div class="label">Pending user gates</div>'
        f'<ul>{gate_items}</ul>'
        f'<div class="why">Generated dashboard state is visibility only, not approval evidence.</div>'
        f'</div>'
    )
    marker = '<section class="zone-next" aria-labelledby="next-heading"><h2 id="next-heading">What Comes Next</h2>'
    if marker not in html_doc:
        return html_doc.replace('<main id="main" role="main" class="grid-v3">',
                                '<main id="main" role="main" class="grid-v3">' + gates_html,
                                1)
    return html_doc.replace(marker, marker + gates_html, 1)


# ---------------------------------------------------------------------------- #
# SDD-036: Lifecycle pipeline + four-card docs row + reorder control.
#
# These surfaces are rendered by post-processor injectors that run in build()
# AFTER render_html, mirroring the inject_user_gates_html precedent. They are
# kept OUTSIDE render_html on purpose: render_html carries an Article X
# footprint lock (SDD-FDC-001) whose source body must remain byte-identical.
# No new state registry or frontmatter state field is introduced; the current
# lifecycle stage is taken from the existing detect_stage() result (features)
# or a coarse mapping of sprint status (_sprint_stage).
# ---------------------------------------------------------------------------- #

_SPRINT_STAGE_MAP = {
    "done":        "DONE",
    "complete":    "DONE",
    "completed":   "DONE",
    "closed":      "DONE",
    "active":      "IMPLEMENT",
    "in progress": "IMPLEMENT",
    "in-progress": "IMPLEMENT",
    "review":      "REVIEW",
    "planned":     "PLAN",
    "planning":    "PLAN",
    "queued":      "BACKLOG",
    "not started": "BACKLOG",
}


def _sprint_stage(status: str | None) -> str:
    """Map a free-form sprint status to a canonical lifecycle stage (AC-1).

    Unknown statuses fall back to IMPLEMENT (an in-flight sprint). No new state
    registry is introduced; this only reuses the existing STAGES vocabulary.
    """
    return _SPRINT_STAGE_MAP.get((status or "").strip().lower(), "IMPLEMENT")


def render_lifecycle_pipeline(current_stage: str, *, aria_label: str = "Lifecycle pipeline") -> str:
    """Render the 9-node horizontal lifecycle pipeline (AC-1).

    The node matching ``current_stage`` is emphasized (class ``pipe-current``
    + ``aria-current="step"``); earlier nodes are marked complete
    (``pipe-complete``); later nodes are outlined (``pipe-later``). The stage
    vocabulary is the existing module-level ``STAGES`` constant -- no new
    registry is added.
    """
    try:
        current_idx = STAGES.index(current_stage)
    except ValueError:
        current_idx = -1
    nodes: list[str] = []
    for i, stage in enumerate(STAGES):
        if i == current_idx:
            state_cls, aria = "pipe-current", ' aria-current="step"'
        elif current_idx >= 0 and i < current_idx:
            state_cls, aria = "pipe-complete", ""
        else:
            state_cls, aria = "pipe-later", ""
        nodes.append(f'<li class="pipe-node {state_cls}"{aria}>{h(stage)}</li>')
    return (
        f'<ol class="lifecycle-pipeline" aria-label="{h(aria_label)}">'
        + "".join(nodes)
        + "</ol>"
    )


def resolve_docs_cards(feature: Feature, sdd_root: Path) -> list[tuple[str, str | None]]:
    """Resolve the four governing-doc targets for a feature card (AC-2).

    Returns (label, href) pairs for Constitution / Spec / Sprint / ADRs. ``href``
    is a path relative to the exec/ output directory (``../<rel>``) when the
    local artifact exists, or ``None`` when it does not (rendered as a disabled
    "missing" card). No SDD-037 cards are added.
    """
    name = feature.feature_dir.name
    candidates: list[tuple[str, Path]] = [
        ("Constitution", Path("constitution") / "principles.md"),
        ("Spec",         Path("specs") / name / "spec.md"),
        ("Sprint",       Path("specs") / name / "tasks.md"),
        ("ADRs",         Path("docs") / "ADR"),
    ]
    cards: list[tuple[str, str | None]] = []
    for label, rel in candidates:
        if (sdd_root / rel).exists():
            cards.append((label, "../" + rel.as_posix()))
        else:
            cards.append((label, None))
    return cards


def render_docs_row(feature: Feature, sdd_root: Path) -> str:
    """Render the four-card docs row (AC-2). Unresolved targets are disabled."""
    items: list[str] = []
    for label, href in resolve_docs_cards(feature, sdd_root):
        if href:
            items.append(f'<a class="docs-card" href="{h(href)}">{h(label)}</a>')
        else:
            items.append(
                f'<span class="docs-card docs-card-missing" aria-disabled="true" '
                f'title="No local artifact resolved">{h(label)} (missing)</span>'
            )
    return (
        '<div class="docs-row" role="group" aria-label="Feature documents">'
        + "".join(items)
        + "</div>"
    )


def render_reorder_control(item_id: str, rank: int, total: int) -> str:
    """Render the keyboard-accessible reorder control (AC-8, no JS framework).

    Up/down are native ``<button>`` elements (keyboard-focusable by default).
    Each carries the exact ``backlog_reorder.py move`` command the operator
    runs (``data-cmd``); the up control is disabled at rank 0 and the down
    control at the last rank. Display order itself reflects the overlay (see
    ``order_features_for_display``).
    """
    up_disabled = rank <= 0
    down_disabled = rank >= total - 1
    up_cmd = f"python cli/backlog_reorder.py move --item {item_id} --to-rank {rank - 1}"
    down_cmd = f"python cli/backlog_reorder.py move --item {item_id} --to-rank {rank + 1}"

    def _btn(direction: str, glyph: str, label: str, cmd: str, disabled: bool) -> str:
        if disabled:
            return (
                f'<button type="button" class="reorder-btn reorder-{direction}" '
                f'aria-label="{h(label)}" disabled>{glyph}</button>'
            )
        return (
            f'<button type="button" class="reorder-btn reorder-{direction}" '
            f'aria-label="{h(label)}" data-cmd="{h(cmd)}">{glyph}</button>'
        )

    up_btn = _btn("up", "&#9650;", f"Move {item_id} up to rank {rank - 1}",
                  up_cmd, up_disabled)
    down_btn = _btn("down", "&#9660;", f"Move {item_id} down to rank {rank + 1}",
                    down_cmd, down_disabled)
    return (
        f'<div class="reorder-control" role="group" '
        f'aria-label="Reorder {h(item_id)} (current rank {rank})">'
        f'{up_btn}{down_btn}'
        f'<span class="reorder-rank">rank {rank + 1} of {total}</span>'
        f'</div>'
    )


def _feature_display_id(feature: Feature) -> str:
    """Best-effort SDD feature ID for a feature.

    Reads a ``- Feature ID: SDD-NNN`` line from the feature's spec.md when
    present; otherwise falls back to the feature directory name. Used to key the
    display-order overlay and the reorder control.
    """
    spec = feature.feature_dir / "spec.md"
    if spec.is_file():
        try:
            text = spec.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("- feature id:"):
                m = re.search(r"\b([A-Z]{2,}-\d{2,3})\b", stripped)
                if m:
                    return m.group(1)
    return feature.feature_dir.name


def load_display_order(sdd_root: Path) -> list[str]:
    """Read the display-order overlay (backlog/display-order.json), read-only.

    Returns the explicit ``order`` list of feature IDs, or [] when the overlay
    is absent or malformed. BACKLOG.md remains PM-authoritative; this overlay is
    presentation-only (Q-C) and never feeds RICE scoring.
    """
    overlay = sdd_root / "backlog" / "display-order.json"
    if not overlay.is_file():
        return []
    try:
        data = json.loads(overlay.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    order = data.get("order") if isinstance(data, dict) else None
    if not isinstance(order, list):
        return []
    return [str(x) for x in order]


def order_features_for_display(
    features: list[Feature], sdd_root: Path
) -> list[tuple[str, Feature]]:
    """Order features by the display-order overlay (AC-8).

    Returns (feature_id, feature) pairs. Features whose ID appears in the
    overlay come first, in overlay order; the remainder follow in natural (load)
    order. Overlay IDs with no matching feature are skipped; no feature is
    dropped.
    """
    pairs = [(_feature_display_id(f), f) for f in features]
    overlay = load_display_order(sdd_root)
    if not overlay:
        return pairs
    by_id: dict[str, tuple[str, Feature]] = {}
    for fid, f in pairs:
        by_id.setdefault(fid, (fid, f))
    ordered: list[tuple[str, Feature]] = []
    used_ids: set[str] = set()
    for fid in overlay:
        if fid in by_id and fid not in used_ids:
            ordered.append(by_id[fid])
            used_ids.add(fid)
    appended = {id(pair[1]) for pair in ordered}
    for fid, f in pairs:
        if id(f) not in appended:
            ordered.append((fid, f))
            appended.add(id(f))
    return ordered


_LIFECYCLE_STYLE = (
    "<style>"
    ".zone-lifecycle{grid-column:1/-1;margin-top:1rem}"
    ".lifecycle-card{border:1px solid var(--line,#333);border-radius:6px;"
    "padding:.6rem .8rem;margin:.5rem 0}"
    ".lifecycle-head{display:flex;gap:.5rem;align-items:baseline;flex-wrap:wrap;"
    "margin-bottom:.4rem}"
    ".lifecycle-id{font-weight:700;letter-spacing:.03em}"
    ".lifecycle-stage{margin-left:auto;opacity:.7;font-size:.85em}"
    ".lifecycle-pipeline{display:flex;flex-wrap:wrap;gap:.25rem;list-style:none;"
    "padding:0;margin:.2rem 0}"
    ".pipe-node{font-size:.72em;padding:.15rem .4rem;border-radius:3px;"
    "border:1px solid transparent}"
    ".pipe-complete{opacity:.55}"
    ".pipe-current{font-weight:700;border-color:currentColor}"
    ".pipe-later{opacity:.35;border-color:var(--line,#333)}"
    ".docs-row{display:flex;gap:.4rem;flex-wrap:wrap;margin:.4rem 0}"
    ".docs-card{font-size:.78em;padding:.2rem .55rem;border:1px solid "
    "var(--line,#333);border-radius:4px;text-decoration:none}"
    ".docs-card-missing{opacity:.4;border-style:dashed}"
    ".reorder-control{display:flex;gap:.3rem;align-items:center;margin-top:.3rem}"
    ".reorder-btn{font-size:.8em;padding:.1rem .45rem;cursor:pointer}"
    ".reorder-btn[disabled]{opacity:.4;cursor:not-allowed}"
    ".reorder-rank{font-size:.72em;opacity:.6}"
    ".lifecycle-card[draggable=\"true\"]{cursor:grab}"
    ".drag-handle{font-size:.85em;opacity:.45;cursor:grab;user-select:none;"
    "margin-right:.1rem}"
    ".lifecycle-card.drag-over{border-color:currentColor;"
    "box-shadow:0 0 0 2px var(--line,#444) inset}"
    ".lifecycle-card.drag-rejected{border-color:#f08a8a}"
    "</style>"
)


def inject_lifecycle_html(
    html_doc: str,
    *,
    features: list[Feature],
    sdd_root: Path,
    current_sprint: dict | None,
) -> str:
    """Inject the SDD-036 lifecycle section into the dashboard (AC-1/AC-2/AC-8).

    Builds, for the current sprint and each feature (ordered by the display
    overlay), a card containing the lifecycle pipeline, the four-card docs row,
    and -- for features -- the keyboard reorder control. The section is appended
    after the user-gates marker / main open, mirroring inject_user_gates_html.
    Kept outside render_html because that function has an Article X footprint
    lock from SDD-FDC-001.
    """
    ordered = order_features_for_display(features, sdd_root)
    total = len(ordered)

    sprint_block = ""
    if current_sprint:
        s_num = current_sprint.get("num", "")
        s_title = current_sprint.get("title", "")
        s_status = current_sprint.get("status", "")
        s_pipe = render_lifecycle_pipeline(
            _sprint_stage(s_status), aria_label=f"Sprint {s_num} lifecycle")
        sprint_block = (
            f'<article class="lifecycle-card lifecycle-sprint" '
            f'aria-label="Sprint {h(s_num)} lifecycle">'
            f'<div class="lifecycle-head">'
            f'<span class="lifecycle-name">Sprint {h(s_num)} -- {h(s_title)}</span>'
            f'<span class="lifecycle-stage">{h(s_status)}</span></div>'
            f'{s_pipe}</article>'
        )

    feature_blocks: list[str] = []
    for rank, (fid, feature) in enumerate(ordered):
        pipeline = render_lifecycle_pipeline(
            feature.stage, aria_label=f"{feature.name} lifecycle")
        docs = render_docs_row(feature, sdd_root)
        control = render_reorder_control(fid, rank, total)
        feature_blocks.append(
            f'<article class="lifecycle-card" '
            f'draggable="true" data-pid="{h(fid)}" data-rank="{rank}" '
            f'aria-label="{h(feature.name)} lifecycle">'
            f'<div class="lifecycle-head">'
            f'<span class="drag-handle" aria-hidden="true" title="Drag to reorder">'
            f'\u2630</span>'
            f'<span class="lifecycle-id">{h(fid)}</span>'
            f'<span class="lifecycle-name">{h(feature.name)}</span>'
            f'<span class="lifecycle-stage">{h(feature.stage)}</span></div>'
            f'{pipeline}{docs}{control}</article>'
        )

    body = sprint_block + "".join(feature_blocks)
    if not body:
        return html_doc
    section = (
        '<section class="zone-lifecycle" aria-labelledby="lifecycle-heading">'
        + _LIFECYCLE_STYLE
        + '<h2 id="lifecycle-heading">Lifecycle &amp; Docs</h2>'
        + body
        + '</section>'
    )
    marker = '<main id="main" role="main" class="grid-v3">'
    if marker in html_doc:
        return html_doc.replace(marker, marker + section, 1)
    return html_doc + section


# ---------------------------------------------------------------------------- #
# SDD-041 (F-31): true browser drag-and-drop reorder
#
# A single, hash-pinned vanilla-JS block turns the lifecycle cards into a
# native HTML5 drag surface. The script is:
#   - additive: emitted only when draggable cards exist; injected by
#     inject_drag_html AFTER inject_lifecycle_html so the locked render_html
#     footprint (Article X) is untouched.
#   - inert as a static file: it no-ops unless location.protocol is http(s),
#     so the file:// state.html stays keyboard-only (render_reorder_control).
#   - CSP-pinned: we widen ONLY for this exact script via its sha256 hash --
#     never 'unsafe-inline'. The hash is computed at import time over the exact
#     body, so editing the body re-pins automatically (and a mismatch fails
#     closed by browser CSP enforcement).
#   - force-free: the drop handler posts {item, to_rank} only. Forcing past a
#     dependency lock is a Level-2 human decision (ADR-017) and is NEVER sent
#     by a drag gesture; a 409 surfaces the reason and tells the user to use
#     the CLI with --force.
# ---------------------------------------------------------------------------- #

_DRAG_SCRIPT_BODY = (
    "(function(){"
    "if(location.protocol!=='http:'&&location.protocol!=='https:')return;"
    "var dragId=null;"
    "function onStart(e){dragId=e.currentTarget.getAttribute('data-pid');"
    "e.dataTransfer.effectAllowed='move';}"
    "function onOver(e){e.preventDefault();"
    "e.currentTarget.classList.add('drag-over');e.dataTransfer.dropEffect='move';}"
    "function onLeave(e){e.currentTarget.classList.remove('drag-over');}"
    "function onDrop(e){e.preventDefault();var t=e.currentTarget;"
    "t.classList.remove('drag-over');"
    "var toRank=parseInt(t.getAttribute('data-rank'),10);"
    "var item=dragId;dragId=null;"
    "if(!item||isNaN(toRank))return;"
    "fetch('/reorder',{method:'POST',"
    "headers:{'Content-Type':'application/json'},"
    "body:JSON.stringify({item:item,to_rank:toRank})})"
    ".then(function(r){return r.json().then(function(d){"
    "return {s:r.status,d:d};});})"
    ".then(function(res){if(res.s===200){location.reload();return;}"
    "var reason=(res.d&&res.d.reason)?res.d.reason:'reorder rejected';"
    "t.classList.add('drag-rejected');"
    "t.setAttribute('title','blocked: '+reason+"
    "' -- forcing is a Level-2 decision; use the CLI with --force');})"
    ".catch(function(){});}"
    "var cards=document.querySelectorAll('.lifecycle-card[draggable=\"true\"]');"
    "for(var i=0;i<cards.length;i++){var c=cards[i];"
    "c.addEventListener('dragstart',onStart);"
    "c.addEventListener('dragover',onOver);"
    "c.addEventListener('dragleave',onLeave);"
    "c.addEventListener('drop',onDrop);}"
    "})();"
)

_DRAG_SCRIPT_HASH = base64.b64encode(
    hashlib.sha256(_DRAG_SCRIPT_BODY.encode("utf-8")).digest()
).decode("ascii")

_DRAG_SCRIPT_CSP = f"'sha256-{_DRAG_SCRIPT_HASH}'"

_CSP_META_RE = re.compile(
    r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)'
)


def inject_drag_html(html_doc: str) -> str:
    """Append the SDD-041 drag script and widen the CSP for exactly that script.

    No-op when no draggable cards are present (e.g. empty backlog). Widens the
    locked render_html meta CSP -- which is ``default-src 'none'`` with no
    ``script-src``/``connect-src`` -- by appending a hash-pinned ``script-src``
    and ``connect-src 'self'`` so the inline drag handler and its same-origin
    POST /reorder fetch are permitted. The locked render_html body is never
    modified; this is post-processing of its output (Article X compliant).
    """
    if 'draggable="true"' not in html_doc:
        return html_doc

    def _widen(match: re.Match) -> str:
        policy = match.group(2)
        if "script-src" not in policy:
            policy = f"{policy}; script-src {_DRAG_SCRIPT_CSP}"
        if "connect-src" not in policy:
            policy = f"{policy}; connect-src 'self'"
        return match.group(1) + policy + match.group(3)

    new_doc = _CSP_META_RE.sub(_widen, html_doc, count=1)
    script_tag = f"<script>{_DRAG_SCRIPT_BODY}</script>"
    if "</body>" in new_doc:
        return new_doc.replace("</body>", script_tag + "</body>", 1)
    return new_doc + script_tag


_REORDER_ITEM_RE = re.compile(r"^[A-Z]{2,}-\d{2,3}$")


def handle_reorder_request(sdd_root: Path, payload: object) -> tuple[int, dict]:
    """Validate a drag-drop reorder payload and apply it via the safeguarded mutator.

    Pure function (no HTTP): returns ``(status_code, body_dict)`` so it can be
    unit-tested without a live server. Contract:
      - 400 when the payload is malformed (not a dict, bad ``item`` id, or a
        ``to_rank`` that is not a non-negative int -- bool is rejected).
      - 200 ``{"status":"ok","audit":<row>}`` on a successful move.
      - 409 ``{"status":"blocked","reason":<msg>}`` when a dependency lock
        rejects the move. Force is NEVER auto-applied (ADR-017): the drag layer
        does not pass force, and a block is surfaced, not retried.
      - 400 ``{"status":"error","reason":<msg>}`` for an out-of-range rank.
    """
    if not isinstance(payload, dict):
        return 400, {"status": "error", "reason": "body must be a JSON object"}

    item = payload.get("item")
    if not isinstance(item, str) or not _REORDER_ITEM_RE.match(item):
        return 400, {"status": "error", "reason": "invalid 'item' feature id"}

    to_rank = payload.get("to_rank")
    if isinstance(to_rank, bool) or not isinstance(to_rank, int) or to_rank < 0:
        return 400, {"status": "error", "reason": "'to_rank' must be a non-negative integer"}

    # The drag gesture never forces past a dependency lock (ADR-017). We accept
    # an explicit force only from a deliberate non-drag client; the injected JS
    # omits it entirely.
    force = bool(payload.get("force", False))

    try:
        row = _reorder_move(sdd_root, item=item, to_rank=to_rank, force=force)
    except _ReorderError as exc:
        return 409, {"status": "blocked", "reason": str(exc)}
    except ValueError as exc:
        return 400, {"status": "error", "reason": str(exc)}
    return 200, {"status": "ok", "audit": row}


# ---------------------------------------------------------------------------- #
# SDD-037 (F-28): Dispatches card + dashboard health pills
#
# All surfaces below are ADDITIVE, READ-ONLY INDICATORS. They never raise out
# of build(), never alter build()'s exit, never become gates (Q-F / FR-14 /
# R-12). They consume the LedgerView passed in by build() and open ZERO new
# sqlite connections. No JavaScript is emitted; non-green pills link to
# server-rendered same-page anchors.
# ---------------------------------------------------------------------------- #

_DISPATCHES_STYLE = (
    "<style>"
    ".zone-dispatches{margin-top:1rem}"
    ".zone-dispatches h2{font-size:1.05rem;margin:.4rem 0}"
    ".dispatch-feature{border:1px solid var(--line,#2a2a33);border-radius:6px;"
    "padding:.5rem .7rem;margin:.4rem 0}"
    ".dispatch-feature-name{font-size:.9rem;margin:.1rem 0 .3rem;font-weight:600}"
    ".dispatch-sprint-name{font-size:.8rem;margin:.3rem 0 .15rem;opacity:.85}"
    ".dispatch-rows{list-style:none;margin:0;padding:0}"
    ".dispatch-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline;"
    "padding:.15rem 0;font-size:.8rem;border-top:1px solid var(--line,#23232b)}"
    ".dispatch-agent{font-weight:600}"
    ".dispatch-role{opacity:.7}"
    ".dispatch-task{flex:1 1 12rem}"
    ".dispatch-status-ok{color:#5fd17a}"
    ".dispatch-status-pending{color:#e0b341}"
    ".dispatch-when{opacity:.6;font-variant-numeric:tabular-nums}"
    ".dispatch-note{font-size:.85rem;opacity:.75;font-style:italic}"
    "</style>"
)

_HEALTH_PILLS_STYLE = (
    "<style>"
    ".zone-health{margin-top:1rem}"
    ".zone-health h2{font-size:1.05rem;margin:.4rem 0}"
    ".health-pills{display:flex;flex-wrap:wrap;gap:.4rem}"
    ".pill{display:inline-block;padding:.2rem .55rem;border-radius:999px;"
    "font-size:.75rem;text-decoration:none;border:1px solid transparent}"
    ".pill-green{background:#13351f;color:#7fe39a;border-color:#1f5230}"
    ".pill-yellow{background:#3a3110;color:#e7c65c;border-color:#5a4c19}"
    ".pill-red{background:#3a1414;color:#f08a8a;border-color:#5a1f1f}"
    "a.pill:hover{filter:brightness(1.15)}"
    ".health-detail{margin-top:.5rem;font-size:.8rem;border-top:1px solid "
    "var(--line,#23232b);padding-top:.4rem}"
    ".health-detail h3{font-size:.85rem;margin:.3rem 0}"
    "</style>"
)


def _group_dispatch_status_class(outcome: object) -> str:
    if outcome == "success":
        return "ok"
    if not outcome:
        return "pending"
    return "other"


def inject_dispatches_html(html_doc: str, *, ledger: LedgerView, sdd_root: Path) -> str:
    """Inject the SDD-037 Dispatches card grouped by feature_dir then sprint.

    Consumes ``ledger.grouped`` (populated once by load_ledger). Renders an
    empty-state when the ledger is reachable but has no rows, and a disabled
    note when the ledger is unavailable. Never raises; opens no connection.
    Injected after the lifecycle section at the ``<main>`` marker.
    """
    try:
        available = getattr(ledger, "available", False)
        grouped = getattr(ledger, "grouped", []) or []
        if not available:
            body = ('<p class="dispatch-note">Fleet ledger unavailable '
                    '(fleet.db missing or unreadable).</p>')
        elif not grouped:
            body = '<p class="dispatch-note">No dispatches recorded yet.</p>'
        else:
            parts: list[str] = []
            for grp in grouped:
                fdir = h(grp.get("feature_dir") or "(unassigned)")
                parts.append(
                    '<article class="dispatch-feature">'
                    f'<h3 class="dispatch-feature-name">{fdir}</h3>'
                )
                for sub in grp.get("sprints", []):
                    parts.append(
                        '<div class="dispatch-sprint">'
                        f'<h4 class="dispatch-sprint-name">'
                        f'{h(sub.get("sprint") or "(no sprint)")}</h4>'
                        '<ul class="dispatch-rows">'
                    )
                    for row in sub.get("rows", []):
                        outcome = row.get("outcome")
                        status_txt = h(outcome) if outcome else "pending"
                        status_cls = _group_dispatch_status_class(outcome)
                        when = h(row.get("outcome_at") or row.get("dispatched_at") or "")
                        task = (f'{h(row.get("task_id") or "")} '
                                f'{h(row.get("task_title") or "")}').strip()
                        parts.append(
                            '<li class="dispatch-row">'
                            f'<span class="dispatch-agent">{h(row.get("agent_id") or "?")}</span>'
                            f'<span class="dispatch-role">{h(row.get("agent_role") or "")}</span>'
                            f'<span class="dispatch-task">{task}</span>'
                            f'<span class="dispatch-status dispatch-status-{status_cls}">'
                            f'{status_txt}</span>'
                            f'<span class="dispatch-when">{when}</span></li>'
                        )
                    parts.append('</ul></div>')
                parts.append('</article>')
            body = "".join(parts)
    except Exception as exc:  # indicators never raise out of build()
        body = f'<p class="dispatch-note">Dispatches unavailable: {h(exc)}</p>'

    section = (
        '<section class="zone-dispatches" aria-labelledby="dispatches-heading">'
        + _DISPATCHES_STYLE
        + '<h2 id="dispatches-heading">Dispatches</h2>'
        + body
        + '</section>'
    )
    marker = '<main id="main" role="main" class="grid-v3">'
    if marker in html_doc:
        return html_doc.replace(marker, marker + section, 1)
    return html_doc + section


def constitution_semver_status(sdd_root: Path) -> tuple[str, str, list[str]]:
    """Health check: constitution version frontmatter is present, quoted, valid.

    Returns ``(status, reason, detail)`` with status in {green,yellow,red}.
    GREEN: every ``constitution/*.md`` has a quoted, valid ``X.Y.Z`` version.
    YELLOW: at least one version is present and valid but unquoted.
    RED: a version is missing or unparseable. Read-only; never writes; never
    raises (internal failure degrades to RED).
    """
    try:
        cdir = Path(sdd_root) / "constitution"
        files = sorted(cdir.glob("*.md")) if cdir.is_dir() else []
        if not files:
            return ("red", "no constitution files found",
                    ["constitution/ missing or empty"])
        reds: list[str] = []
        yellows: list[str] = []
        for f in files:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                reds.append(f"{f.name}: unreadable")
                continue
            fm = parse_frontmatter(text)
            raw_lines = fm.get("_raw_lines", []) if isinstance(fm, dict) else []
            is_unq, raw_val = _has_unquoted_version(raw_lines)
            ver = fm.get("version") if isinstance(fm, dict) else None
            present = (ver is not None) or is_unq or (raw_val is not None)
            if not present:
                reds.append(f"{f.name}: missing version field")
                continue
            candidate = str(ver if ver is not None else raw_val).strip().strip("'\"")
            valid = bool(re.match(r"^\d+\.\d+\.\d+$", candidate))
            if not valid:
                reds.append(f"{f.name}: unparseable version '{candidate}'")
            elif is_unq:
                yellows.append(f"{f.name}: unquoted version '{candidate}'")
        if reds:
            return ("red", f"{len(reds)} version issue(s)", reds + yellows)
        if yellows:
            return ("yellow", f"{len(yellows)} unquoted version(s)", yellows)
        return ("green", "all versions valid", [])
    except Exception as exc:  # indicators never raise
        return ("red", f"check failed: {exc}", [str(exc)])


def skill_validity_status(repo_root: Path) -> tuple[str, str, list[str]]:
    """Health check: every ``.github/skills/**/SKILL.md`` passes ``check_skill``.

    Reuses the schema_lint validator. GREEN when there are no findings (or no
    skills directory); RED with concrete detail otherwise. Read-only; never
    raises.
    """
    try:
        skills_dir = Path(repo_root) / ".github" / "skills"
        if not skills_dir.is_dir():
            return ("green", "no skills directory", [])
        findings: list[Finding] = []
        for p in sorted(skills_dir.rglob("SKILL.md")):
            findings.extend(check_skill(p))
        if findings:
            detail = [f"{Path(fd.path).parent.name}: {fd.issue}" for fd in findings]
            return ("red", f"{len(findings)} skill issue(s)", detail)
        return ("green", "all skills valid", [])
    except Exception as exc:  # indicators never raise
        return ("red", f"check failed: {exc}", [str(exc)])


def ledger_reachability_status(ledger: LedgerView) -> tuple[str, str, list[str]]:
    """Health check: the fleet ledger was reachable for this build tick."""
    try:
        if getattr(ledger, "available", False):
            return ("green", "fleet ledger reachable", [])
        return ("red", "fleet ledger unreachable",
                ["ledger/fleet.db missing or unreadable"])
    except Exception as exc:  # indicators never raise
        return ("red", f"check failed: {exc}", [str(exc)])


def stale_tracker_status(sdd_root: Path, now: dt.datetime | None = None,
                         stale_days: int = 7) -> tuple[str, str, list[str]]:
    """Health check: ``exec/sprint-progress.md`` was updated recently.

    GREEN when the latest dated entry is <= ``stale_days`` old, YELLOW when
    within ``2*stale_days`` (or no parseable date), RED beyond that. Read-only;
    never raises.
    """
    try:
        now = now or dt.datetime.now()
        path = Path(sdd_root) / "exec" / "sprint-progress.md"
        if not path.is_file():
            return ("yellow", "sprint-progress.md not found",
                    ["exec/sprint-progress.md missing"])
        text = path.read_text(encoding="utf-8", errors="replace")
        dates: list[dt.date] = []
        for m in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", text):
            try:
                dates.append(dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
            except ValueError:
                continue
        if not dates:
            return ("yellow", "no dated entries", ["could not parse any ISO date"])
        latest = max(dates)
        now_date = now.date() if hasattr(now, "date") else now
        age = (now_date - latest).days
        warn = stale_days * 2
        if age <= stale_days:
            return ("green", f"fresh ({age}d)", [])
        if age <= warn:
            return ("yellow", f"aging ({age}d)",
                    [f"latest entry {latest.isoformat()} is {age}d old"])
        return ("red", f"stale ({age}d)",
                [f"latest entry {latest.isoformat()} is {age}d old"])
    except Exception as exc:  # indicators never raise
        return ("red", f"check failed: {exc}", [str(exc)])


def inject_health_pills_html(html_doc: str, *, sdd_root: Path,
                             ledger: LedgerView,
                             now: dt.datetime | None = None) -> str:
    """Inject the SDD-037 four-pill health strip after the Dispatches card.

    Pills: constitution semver, skill frontmatter validity, ledger
    reachability, stale-tracker (N=7). GREEN pills are plain ``<span>``;
    non-green pills are ``<a>`` links to server-rendered same-page detail
    sections (no JavaScript). Read-only; never raises.
    """
    try:
        repo_root = repo_root_for(Path(sdd_root))
        checks = [
            ("constitution", "Constitution",
             constitution_semver_status(Path(sdd_root))),
            ("skills", "Skills", skill_validity_status(repo_root)),
            ("ledger", "Ledger", ledger_reachability_status(ledger)),
            ("tracker", "Tracker", stale_tracker_status(Path(sdd_root), now=now)),
        ]
        pills: list[str] = []
        details: list[str] = []
        for key, label, result in checks:
            status, reason, detail = result
            cls = f"pill pill-{h(status)}"
            text = f"{h(label)}: {h(reason)}"
            if status == "green":
                pills.append(f'<span class="{cls}">{text}</span>')
            else:
                pills.append(f'<a class="{cls}" href="#health-detail-{key}">{text}</a>')
                items = "".join(f"<li>{h(d)}</li>" for d in (detail or [reason]))
                details.append(
                    f'<section id="health-detail-{key}" class="health-detail">'
                    f'<h3>{h(label)}</h3><ul>{items}</ul></section>'
                )
        body = (
            '<div class="health-pills">' + "".join(pills) + '</div>'
            + "".join(details)
        )
    except Exception as exc:  # indicators never raise out of build()
        body = f'<p class="dispatch-note">Health checks unavailable: {h(exc)}</p>'

    section = (
        '<section class="zone-health" aria-labelledby="health-heading">'
        + _HEALTH_PILLS_STYLE
        + '<h2 id="health-heading">Health</h2>'
        + body
        + '</section>'
    )
    marker = '<main id="main" role="main" class="grid-v3">'
    if marker in html_doc:
        return html_doc.replace(marker, marker + section, 1)
    return html_doc + section


# ---------------------------------------------------------------------------- #
# Work index generator (for principal pre-work checks, IDEA 2026-06-03)
# ---------------------------------------------------------------------------- #

def render_work_index(
    *, generated_date: str, features: list[Feature],
    backlog: list[BacklogItem], pi: PIBlock | None,
    user_gates: list[UserGate] | None = None,
) -> str:
    """Render exec/work-index.md -- canonical reference for principals before
    authorizing new work. Lists DONE, IN-FLIGHT, and QUEUED items so principals
    can cross-check that proposed work is not duplicate or conflicting.
    """
    done = sorted([f for f in features if f.stage == "DONE"], key=lambda x: x.created)
    inflight = sorted(
        [f for f in features if f.stage in ("IMPLEMENT", "TASKS", "PLAN", "SPEC", "CLARIFY")],
        key=lambda x: x.created,
    )
    queued = [b for b in backlog if b.priority in ("P1", "P2", "P3")]

    lines = [
        "# Work Index",
        "",
        f"_Auto-generated by `state_builder.py` on {generated_date}._",
        "",
        "**Purpose**: Authoritative reference for principals before authorizing",
        "any new work. Consult this file BEFORE writing a spec, planning a sprint,",
        "or dispatching a worker, to ensure you are not duplicating completed work",
        "or introducing conflicts with in-flight work.",
        "",
        f"Current PI: **{pi.name} ({pi.title})**" if pi else "No active PI.",
        "",
        "---",
        "",
        "## 1. DONE -- Already shipped (do not re-implement)",
        "",
    ]
    if done:
        lines.append("| Date | Feature | Spec dir |")
        lines.append("|------|---------|----------|")
        for f in done:
            lines.append(f"| {f.created} | {f.name} | `specs/{f.feature_dir.name}/` |")
    else:
        lines.append("_No completed features yet._")

    lines += [
        "",
        "## 2. IN-FLIGHT -- Currently being worked on (coordinate before touching)",
        "",
    ]
    if inflight:
        lines.append("| Started | Feature | Stage | Spec dir |")
        lines.append("|---------|---------|-------|----------|")
        for f in inflight:
            lines.append(f"| {f.created} | {f.name} | {f.stage} | `specs/{f.feature_dir.name}/` |")
    else:
        lines.append("_Nothing in flight._")

    lines += [
        "",
        "## 2A. USER GATES -- Human approvals and blocked transitions",
        "",
    ]
    blocking_gates = active_user_gates(user_gates or [])
    if blocking_gates:
        lines.append("| Feature | Gate | Blocks | Evidence Need | Next Action |")
        lines.append("|---------|------|--------|---------------|-------------|")
        for gate in blocking_gates:
            lines.append(
                f"| {gate.feature} | {gate.gate_id} (`{gate.gate_type}`) | "
                f"`{gate.blocking_scope}` | {gate.evidence_type or '-'} | "
                f"{gate.next_action or '-'} |"
            )
        lines.append("")
        lines.append("Generated state is visibility only; approvals require durable SDD-023 evidence.")
    else:
        lines.append("_No pending or blocked user gates declared._")

    lines += [
        "",
        "## 3. QUEUED -- Backlog (next candidates for triage)",
        "",
    ]
    if queued:
        lines.append("| ID | Priority | Title | Sprint |")
        lines.append("|----|----------|-------|--------|")
        for b in queued[:20]:
            lines.append(f"| {b.pid} | {b.priority} | {b.title} | {b.sprint or '--'} |")
    else:
        lines.append("_Backlog is empty._")

    lines += [
        "",
        "---",
        "",
        "## Cross-check protocol (for principals)",
        "",
        "Before authorizing new work, verify ALL of:",
        "",
        "1. **Not in DONE**: the proposed work is not already shipped above.",
        "2. **No conflict with IN-FLIGHT**: the proposed work does not touch the",
        "   same files or contradict the design of any in-flight feature.",
        "3. **Not a duplicate of QUEUED**: the idea is not already in backlog.",
        "4. **Aligns with current PI objective**: the work supports the active PI.",
        "",
        "If ANY check fails, surface as an escalation to the Executive Manager",
        "instead of proceeding. See `.github/skills/core/pre-work-check/SKILL.md`",
        "for the full protocol.",
        "",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------- #
# Build orchestration
# ---------------------------------------------------------------------------- #

def build(*, sdd_root: Path | None = None, write: bool = True,
          pi_override: str | None = None, live_html: bool = False,
          port: int | None = None, fixed_date: str | None = None) -> dict:
    sdd_root = sdd_root or DEFAULT_SDD_ROOT
    sdd_root = Path(sdd_root).resolve()

    pis = load_pis(sdd_root)
    pi = resolve_display_pi(sdd_root, pis, override=pi_override)
    features = load_features(sdd_root)
    user_gates = load_user_gates(sdd_root)
    backlog = load_backlog(sdd_root)
    roster = load_roster(sdd_root)
    ledger = load_ledger(sdd_root)
    commits = load_recent_commits(sdd_root)
    next_action = derive_next_action(sdd_root, pi, features)

    # v3 data-layer additions (Phase 1 functions)
    pi_name_val = pi.name if pi else ""
    sprint_table = load_sprint_table(sdd_root, pi_name_val) if pi_name_val else []
    current_sprint = detect_current_sprint(sprint_table)
    sprint_num = current_sprint["num"] if current_sprint else 1
    sprint_goal = (
        load_sprint_goal(sdd_root, pi_name_val, sprint_num)
        if pi_name_val else "No sprint goal defined"
    )
    decisions = load_decisions(sdd_root)

    generated_date = fixed_date or dt.date.today().isoformat()        # MD: day precision = deterministic
    generated_at = fixed_date or dt.datetime.now().strftime("%Y-%m-%d %H:%M")  # HTML: more precise

    # About-section values (SDD-010): reuse the same header values as state.md
    about_pi = f"{pi.name} ({pi.title})" if pi else ""
    about_sprint = "Symbolic -- AI fleet compresses wall-clock time"
    about_focus = next_action[0] if next_action else ""

    md = render_markdown(
        generated_date=generated_date, pi=pi, features=features, backlog=backlog,
        roster=roster, ledger=ledger, next_action=next_action,
        user_gates=user_gates,
    )
    htm = render_html(
        generated_at=generated_at, pi=pi, features=features, backlog=backlog,
        roster=roster, ledger=ledger, commits=commits, next_action=next_action,
        live=live_html, port=port, all_pis=pis,
        about_pi=about_pi, about_sprint=about_sprint, about_focus=about_focus,
        sprint_table=sprint_table, current_sprint=current_sprint,
        sprint_goal=sprint_goal, decisions=decisions,
    )
    htm = inject_user_gates_html(htm, user_gates)
    # SDD-036: lifecycle pipeline + four-card docs row + reorder control.
    htm = inject_lifecycle_html(
        htm, features=features, sdd_root=sdd_root, current_sprint=current_sprint)
    # SDD-037 (F-28): Dispatches card then health-pills strip. Both are
    # read-only indicators consuming the SAME LedgerView (zero new sqlite
    # connections). Pills injected LAST so they render at the top as a header
    # strip; neither can alter build()'s exit.
    htm = inject_dispatches_html(htm, ledger=ledger, sdd_root=sdd_root)
    htm = inject_health_pills_html(htm, sdd_root=sdd_root, ledger=ledger)
    # SDD-041 (F-31): native drag-and-drop layer. Injected LAST so it post-
    # processes the fully assembled doc -- appends one hash-pinned <script> and
    # widens the CSP for exactly that script. No-op when no draggable cards.
    htm = inject_drag_html(htm)

    result = {
        "markdown_chars": len(md), "html_chars": len(htm),
        "features": len(features), "commits": len(commits),
        "dispatches": len(ledger.recent), "pi": pi.name if pi else None,
        "html": htm, "markdown": md, "user_gates": len(user_gates),
    }
    # Work index for principal pre-work checks (IDEA 2026-06-03)
    work_index_md = render_work_index(
        generated_date=generated_date, features=features, backlog=backlog, pi=pi,
        user_gates=user_gates,
    )
    result["work_index"] = work_index_md
    if write:
        exec_dir = sdd_root / "exec"
        exec_dir.mkdir(parents=True, exist_ok=True)
        (exec_dir / "state.md").write_text(md, encoding="utf-8")
        (exec_dir / "state.html").write_text(htm, encoding="utf-8")
        (exec_dir / "work-index.md").write_text(work_index_md, encoding="utf-8")
        result["wrote"] = [
            str(exec_dir / "state.md"),
            str(exec_dir / "state.html"),
            str(exec_dir / "work-index.md"),
        ]
    return result


# ---------------------------------------------------------------------------- #
# Live HTTP server (state-dashboard feature)
# ---------------------------------------------------------------------------- #

def served_html_with_refresh(html_doc: str, refresh_seconds: int) -> str:
    if refresh_seconds < 1:
        raise ValueError("refresh_seconds must be positive")
    meta = f'<meta http-equiv="refresh" content="{refresh_seconds}">'
    if re.search(r'<meta http-equiv="refresh" content="\d+">', html_doc):
        return re.sub(r'<meta http-equiv="refresh" content="\d+">', meta, html_doc, count=1)
    return html_doc.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + meta,
        1,
    )

class DashboardHandler(BaseHTTPRequestHandler):
    server_port: int = 8765
    sdd_root: Path = DEFAULT_SDD_ROOT
    refresh_seconds: int = 5

    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write(f"[bridge] {self.address_string()} {format % args}\n")

    def _send(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Security headers (REC-2 from SECURITY-REVIEW.md). script-src is
        # pinned to the SDD-041 drag script hash only -- never 'unsafe-inline'
        # (ADR-019). The served HTML carries the same hash in its meta CSP.
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; "
                         "style-src 'unsafe-inline'; "
                         f"script-src {_DRAG_SCRIPT_CSP}; "
                         "img-src 'self' data:; "
                         "font-src 'self'; "
                         "connect-src 'self'; "
                         "frame-ancestors 'none'; "
                         "base-uri 'none'; "
                         "form-action 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                info = build(sdd_root=self.sdd_root, write=False, live_html=True, port=self.server_port)
                html_doc = served_html_with_refresh(info["html"], self.refresh_seconds)
                self._send(200, html_doc.encode("utf-8"))
            except Exception as exc:
                msg = f"<h1>Build failed</h1><pre>{html.escape(repr(exc))}</pre>"
                self._send(500, msg.encode("utf-8"))
            return
        if path == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8"); return
        if path == "/favicon.ico":
            self._send(204, b"", "image/x-icon"); return
        self._send(404, b"<h1>404</h1>not found")

    def do_POST(self) -> None:  # noqa: N802
        # SDD-041 (F-31): the ONLY write endpoint. Localhost-bound (serve()
        # binds 127.0.0.1), input-validated, and delegates to the safeguarded
        # backlog_reorder.move via handle_reorder_request. do_GET is unchanged.
        path = self.path.split("?", 1)[0]
        if path != "/reorder":
            self._send_json(404, {"status": "error", "reason": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except (TypeError, ValueError):
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"status": "error", "reason": "malformed JSON body"})
            return
        try:
            status, body = handle_reorder_request(self.sdd_root, payload)
        except Exception as exc:  # fail closed; never 500 the dashboard write path silently
            self._send_json(500, {"status": "error", "reason": repr(exc)})
            return
        self._send_json(status, body)


def _port_available(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port)); return True
    except OSError:
        return False
    finally:
        s.close()


def serve(sdd_root: Path, host: str = "127.0.0.1", port: int = 8765,
          open_browser: bool = True, refresh_seconds: int = 5) -> int:
    if refresh_seconds < 1:
        print("ERROR: --refresh-seconds must be a positive integer", file=sys.stderr)
        return 1
    if not _port_available(host, port):
        for offset in range(1, 6):
            if _port_available(host, port + offset):
                port = port + offset; break
        else:
            print(f"ERROR: no available port near {port} on {host}", file=sys.stderr); return 1
    DashboardHandler.server_port = port
    DashboardHandler.sdd_root = sdd_root
    DashboardHandler.refresh_seconds = refresh_seconds
    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    url = f"http://{host}:{port}/"
    print(f"Bridge dashboard live at {url}")
    print(f"Each request rebuilds state from artifacts. Page auto-refreshes every {refresh_seconds}s.")
    print("Press Ctrl+C to stop.")
    if open_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try: httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping...")
    finally:
        httpd.server_close()
    return 0


# ---------------------------------------------------------------------------- #
# build-index: regenerate sprint table in a PI INDEX.md
# ---------------------------------------------------------------------------- #

_SPRINT_DIR_RE = re.compile(r"^Sprint-(\d+)-(.+)$")
_MARKER_BEGIN = "<!-- BEGIN auto-generated:sprints"
_MARKER_END = "<!-- END auto-generated:sprints -->"


def _discover_sprints(pi_dir: Path) -> list[dict]:
    """Scan *pi_dir* for Sprint-N-title directories; return sorted list of dicts."""
    sprints: list[dict] = []
    if not pi_dir.is_dir():
        return sprints
    for child in sorted(pi_dir.iterdir()):
        if not child.is_dir():
            continue
        m = _SPRINT_DIR_RE.match(child.name)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).replace("-", " ").title()
        has_spec = (child / "SPEC.md").is_file()
        status = _detect_sprint_status(child) if has_spec else "Proposed"
        sprints.append({
            "num": num,
            "title": title,
            "folder": child.name,
            "has_spec": has_spec,
            "status": status,
        })
    sprints.sort(key=lambda s: s["num"])
    return sprints


def _detect_sprint_status(sprint_dir: Path) -> str:
    """Read SPEC.md frontmatter or first 20 lines for a status value."""
    spec_path = sprint_dir / "SPEC.md"
    if not spec_path.is_file():
        return "Proposed"
    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError:
        return "Unknown"
    lines = text.splitlines()

    # Check YAML frontmatter first (between --- markers)
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.lower().startswith("status:"):
                return line.split(":", 1)[1].strip()

    # Fallback: scan first 20 lines for status keywords
    head = "\n".join(lines[:20])
    for keyword in ("DONE", "BLOCKED", "In-Flight", "Proposed", "Draft"):
        if keyword in head:
            return keyword
    return "Unknown"


def _query_ledger_for_pi(sdd_root: Path, pi: str) -> dict[int, dict]:
    """Query fleet.db for dispatch counts and last outcome per sprint in *pi*.

    Returns {sprint_num: {"count": int, "last_outcome": str}}.
    """
    db_path = sdd_root / "ledger" / "fleet.db"
    result: dict[int, dict] = {}
    if not db_path.is_file():
        return result
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT sprint, outcome FROM dispatches WHERE pi = ? ORDER BY id",
            (pi,),
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        return result

    # Sprint column may be "Sprint A", "S5", "Sprint-5", etc.
    sprint_num_re = re.compile(r"(\d+)")
    for row in rows:
        sprint_val = row["sprint"] or ""
        m = sprint_num_re.search(sprint_val)
        if not m:
            continue
        snum = int(m.group(1))
        if snum not in result:
            result[snum] = {"count": 0, "last_outcome": "--"}
        result[snum]["count"] += 1
        if row["outcome"]:
            result[snum]["last_outcome"] = row["outcome"]
    return result


def _render_sprint_table(sprints: list[dict], ledger_data: dict[int, dict]) -> str:
    """Render the markdown table for sprint rows."""
    lines = [
        "| Sprint | Title | Status | Dispatches | Last Outcome | Detail |",
        "|--------|-------|--------|------------|--------------|--------|",
    ]
    for s in sprints:
        num = s["num"]
        ld = ledger_data.get(num, {"count": 0, "last_outcome": "--"})
        detail_link = f"[{s['folder']}]({s['folder']}/)"
        lines.append(
            f"| {num} | {s['title']} | {s['status']} "
            f"| {ld['count']} | {ld['last_outcome']} | {detail_link} |"
        )
    return "\n".join(lines)


def build_index(sdd_root: Path, pi: str, write: bool = True) -> dict:
    """Regenerate the sprint table in docs/Management/{pi}/INDEX.md.

    Returns a dict with keys: pi, sprints_found, wrote, table_content.
    Raises StateBuilderError on expected failures.
    """
    pi_dir = sdd_root / "docs" / "Management" / pi
    index_path = pi_dir / "INDEX.md"

    if not pi_dir.is_dir():
        raise StateBuilderError(f"PI directory not found: {pi_dir}")
    if not index_path.is_file():
        raise StateBuilderError(f"INDEX.md not found: {index_path}")

    # Discover sprints and query ledger
    sprints = _discover_sprints(pi_dir)
    ledger_data = _query_ledger_for_pi(sdd_root, pi)

    # Render the table
    table_content = _render_sprint_table(sprints, ledger_data)

    # Build the full marker block
    marker_header = f"{_MARKER_BEGIN} (refreshed by `cli/state_builder.py build-index`) -->"
    block = f"{marker_header}\n{table_content}\n{_MARKER_END}"

    # Read existing INDEX.md and replace the marker block
    original = index_path.read_text(encoding="utf-8")

    begin_idx = original.find(_MARKER_BEGIN)
    end_idx = original.find(_MARKER_END)

    if begin_idx == -1 or end_idx == -1:
        raise StateBuilderError(
            f"Marker block not found in {index_path}. "
            f"Expected {_MARKER_BEGIN!r} and {_MARKER_END!r}."
        )

    # end_idx points to the start of the END marker; include its full text
    end_idx += len(_MARKER_END)
    updated = original[:begin_idx] + block + original[end_idx:]

    wrote_path = None
    if write:
        index_path.write_text(updated, encoding="utf-8")
        wrote_path = str(index_path)

    return {
        "pi": pi,
        "sprints_found": len(sprints),
        "wrote": wrote_path,
        "table_content": table_content,
    }


# ---------------------------------------------------------------------------- #
# Doc-count rollup (SDD-FDC-001 / R3, R4)
#
# Walks spec-driven-development/specs and sprints, parses YAML frontmatter via
# the shared schema_lint.parse_frontmatter, and rolls counts up by status and
# by type. Pure, additive, never touches the locked S1 functions.
# ---------------------------------------------------------------------------- #


def _iter_in_scope_artifacts(sdd_root: Path):
    """Yield in-scope *.md files under specs/** and sprints/**, applying the
    schema_lint skip list (templates, _-prefixed files).
    """
    for sub in ("specs", "sprints"):
        base = sdd_root / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name in ARTIFACT_SKIP_NAMES:
                continue
            if any(p.name.startswith(prefix) for prefix in ARTIFACT_SKIP_PREFIXES):
                continue
            yield p


def _resolve_sprint_id(path: Path, sdd_root: Path) -> str | None:
    """Infer the sprint id from an artifact path.

    Returns the path segment under spec-driven-development/sprints/<sprint-id>/...
    when the artifact lives under sprints/, otherwise None. Spec artifacts are
    not associated with a sprint by this helper.
    """
    try:
        rel = path.resolve().relative_to(sdd_root.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "sprints":
        return parts[1]
    return None


def build_doc_count(sdd_root: Path, sprint: str | None = None) -> dict:
    """Walk specs/** + sprints/**, parse frontmatter, return the rollup.

    Stable contract (R3):
        {
            "by_status": {<status>: int, ...},
            "by_type":   {<type>: int, ...},
            "total":     int,
        }

    Zero-count policy: every key from ARTIFACT_STATUS_ENUM and ARTIFACT_TYPE_ENUM
    is seeded with 0 before counting. This makes the output shape stable for
    dashboard consumers regardless of which values appear in the tree.

    When `sprint` is supplied, only artifacts whose resolved sprint matches are
    counted; the top-level shape is unchanged.

    A frontmatter parse that yields {} (no YAML delimiters or unparseable) is
    SKIPPED rather than crashing -- it is the lint's job to flag such files.
    Out-of-enum `type` or `status` values are also skipped (lint flags them).
    """
    by_status = {k: 0 for k in sorted(ARTIFACT_STATUS_ENUM)}
    by_type = {k: 0 for k in sorted(ARTIFACT_TYPE_ENUM)}

    for path in _iter_in_scope_artifacts(sdd_root):
        if sprint is not None:
            path_sprint = _resolve_sprint_id(path, sdd_root)
            if path_sprint != sprint:
                continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = parse_frontmatter(text)
        if not fm:
            continue  # missing/unparseable: lint reports it, count skips it
        t = fm.get("type")
        s = fm.get("status")
        # Count each artifact at most once on each axis. An artifact missing
        # either field, or carrying out-of-enum values, is silently skipped
        # (the lint already reports it). Without this guard the
        # total == sum(by_status) == sum(by_type) invariant could break.
        if not (isinstance(t, str) and t.strip() in ARTIFACT_TYPE_ENUM):
            continue
        if not (isinstance(s, str) and s.strip() in ARTIFACT_STATUS_ENUM):
            continue
        by_type[t.strip()] += 1
        by_status[s.strip()] += 1

    total = sum(by_status.values())
    # Invariant check: each counted artifact contributes exactly one of each axis.
    assert total == sum(by_type.values()), (
        f"build_doc_count invariant violated: "
        f"sum(by_status)={total} sum(by_type)={sum(by_type.values())}"
    )
    return {"by_status": by_status, "by_type": by_type, "total": total}


def build_doc_count_by_sprint(sdd_root: Path) -> dict:
    """Return {<sprint_id>: <flat contract>} for each sprint directory under sprints/.

    Sprint directories are immediate children of spec-driven-development/sprints/.
    Spec artifacts (under specs/) are not associated with a sprint and are
    excluded from this view.
    """
    sprints_dir = sdd_root / "sprints"
    if not sprints_dir.is_dir():
        return {}
    out: dict = {}
    for child in sorted(sprints_dir.iterdir()):
        if not child.is_dir():
            continue
        sprint_id = child.name
        out[sprint_id] = build_doc_count(sdd_root, sprint=sprint_id)
    return out


def render_count_table(rollup: dict) -> str:
    """Render a flat rollup dict as a human-readable table.

    Format (stdlib only, no third-party tabulate dependency):

        BY STATUS                BY TYPE
          status         count     type            count
          -------------- -----     --------------- -----
          active             3     spec                4
          ...                       ...
                                  TOTAL             N

    The leading two-space indent is for stable alignment under section headers.
    """
    by_status = rollup.get("by_status", {})
    by_type = rollup.get("by_type", {})
    total = rollup.get("total", 0)

    status_rows = [(k, by_status[k]) for k in sorted(by_status.keys())]
    type_rows = [(k, by_type[k]) for k in sorted(by_type.keys())]

    lines: list[str] = []
    lines.append("Document count rollup")
    lines.append("")
    lines.append("BY STATUS")
    lines.append(f"  {'status':<16}{'count':>6}")
    lines.append(f"  {'-' * 16}{'-' * 6}")
    for name, count in status_rows:
        lines.append(f"  {name:<16}{count:>6}")
    lines.append("")
    lines.append("BY TYPE")
    lines.append(f"  {'type':<16}{'count':>6}")
    lines.append(f"  {'-' * 16}{'-' * 6}")
    for name, count in type_rows:
        lines.append(f"  {name:<16}{count:>6}")
    lines.append("")
    lines.append(f"TOTAL: {total}")
    return "\n".join(lines) + "\n"


def cmd_count(args: argparse.Namespace, sdd_root: Path) -> int:
    """Handler for `state_builder.py count`. CLI-PATTERN rule 9 (own handler)."""
    sprint = getattr(args, "sprint", None)
    by_sprint_flag = getattr(args, "by_sprint", False)
    fmt = getattr(args, "format", "json")

    rollup = build_doc_count(sdd_root, sprint=sprint)

    if by_sprint_flag:
        rollup["by_sprint"] = build_doc_count_by_sprint(sdd_root)

    if fmt == "table":
        # Tables suppress the by_sprint nested map (would be a wall of text).
        # JSON output remains the source of truth for the nested view.
        print(render_count_table(rollup), end="")
    else:
        print(json.dumps(rollup, indent=2, default=str))
    return 0


# ---------------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------------- #

def _resolve_sdd_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    return DEFAULT_SDD_ROOT


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments (separated per CLI-PATTERN.md)."""
    parser = argparse.ArgumentParser(
        prog="state_builder.py",
        description="Build (or live-serve) the executive state dashboard. "
                    "Default action: write exec/state.md and exec/state.html.",
    )
    parser.add_argument("--sdd-root", default=None,
                        help="Path to the spec-driven-development root. Defaults to the script's parent dir.")
    parser.add_argument("--pi", default=None,
                        help="Override the current PI label (e.g., PI-2).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print state.md to stdout instead of writing files. (SDD-002 AC10)")
    parser.add_argument("--json", action="store_true",
                        help="Print a JSON summary instead of human-readable text.")

    sub = parser.add_subparsers(dest="cmd")
    sub_serve = sub.add_parser("serve", help="Run a local HTTP server that rebuilds on every request.")
    sub_serve.add_argument("--host", default="127.0.0.1")
    sub_serve.add_argument("--port", type=int, default=8765)
    sub_serve.add_argument("--refresh-seconds", type=_positive_int, default=5,
                           help="Positive meta-refresh cadence in seconds for serve mode. Default: 5.")
    sub_serve.add_argument("--no-open", action="store_true")

    sub_build_index = sub.add_parser("build-index",
                                     help="Regenerate the sprint table in a PI INDEX.md from the ledger.")
    sub_build_index.add_argument("--pi", required=True, help="PI identifier, e.g. PI-3")

    sub_count = sub.add_parser("count",
                               help="Roll up in-scope artifact counts by status and type "
                                    "(SDD-FDC-001).")
    sub_count.add_argument("--format", choices=("json", "table"), default="json",
                           help="Output format. Default: json (R3 stable contract).")
    sub_count.add_argument("--sprint", default=None,
                           help="Narrow rollup to artifacts under this sprint id "
                                "(e.g. PI-4). Top-level shape unchanged.")
    sub_count.add_argument("--by-sprint", action="store_true",
                           help="Additionally include a 'by_sprint' key with per-sprint "
                                "rollups. Top-level keys unchanged.")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    sdd_root = _resolve_sdd_root(args.sdd_root)

    if not sdd_root.is_dir():
        print(f"ERROR: --sdd-root directory does not exist: {sdd_root}", file=sys.stderr)
        return 1

    if args.cmd == "serve":
        return serve(sdd_root=sdd_root, host=args.host, port=args.port,
                     open_browser=not args.no_open,
                     refresh_seconds=args.refresh_seconds)

    if args.cmd == "count":
        return cmd_count(args, sdd_root)

    if args.cmd == "build-index":
        write = not args.dry_run
        try:
            info = build_index(sdd_root=sdd_root, pi=args.pi, write=write)
        except (StateBuilderError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        if args.dry_run:
            print(info["table_content"])
        elif args.json:
            print(json.dumps(info, indent=2, default=str))
        else:
            print(f"PI: {info['pi']}")
            print(f"Sprints found: {info['sprints_found']}")
            if info['wrote']:
                print(f"Wrote: {info['wrote']}")
        return 0

    write = not args.dry_run
    try:
        info = build(sdd_root=sdd_root, write=write, pi_override=args.pi)
    except (StateBuilderError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        # SDD-002 AC10: dry-run prints the markdown to stdout
        sys.stdout.write(info["markdown"])
        return 0
    info_for_print = {k: v for k, v in info.items() if k not in ("html", "markdown")}
    if args.json:
        print(json.dumps(info_for_print, indent=2, default=str))
    else:
        print(f"PI: {info['pi']}")
        print(f"Features: {info['features']}")
        print(f"Commits scanned: {info['commits']}")
        print(f"Dispatches in ledger: {info['dispatches']}")
        if "wrote" in info:
            for p in info["wrote"]:
                print(f"Wrote: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
