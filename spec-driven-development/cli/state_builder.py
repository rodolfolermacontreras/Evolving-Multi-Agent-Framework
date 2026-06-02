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
import datetime as dt
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
# SDD root + path helpers
# ---------------------------------------------------------------------------- #

DEFAULT_SDD_ROOT = Path(__file__).resolve().parents[1]   # spec-driven-development/


class StateBuilderError(Exception):
    """Expected state-builder failure with a human-readable message."""


def repo_root_for(sdd_root: Path) -> Path:
    return sdd_root.parent


# ---------------------------------------------------------------------------- #
# About-section constants (SDD-010)
# ---------------------------------------------------------------------------- #

ABOUT_STATIC_PARAGRAPH = (
    "The Evolving Multi-Agent Framework is an AI-powered software development "
    "system that uses coordinated specialist agents to deliver working code "
    "through a structured lifecycle. This dashboard is built by the framework "
    "whose progress it tracks."
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


def load_ledger(sdd_root: Path, now: dt.datetime | None = None,
                stale_hours: int = 24, recent_limit: int = 10) -> LedgerView:
    db_path = sdd_root / "ledger" / "fleet.db"
    if not db_path.is_file():
        return LedgerView(recent_success=[], blockers=[], recent=[], available=False)
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
    except sqlite3.Error:
        return LedgerView(recent_success=[], blockers=[], recent=[], available=False)
    return LedgerView(recent_success=recent_success, blockers=blockers, recent=recent, available=True)


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

def derive_next_action(sdd_root: Path, pi: PIBlock | None, features: list[Feature]) -> tuple[str, str, str | None]:
    in_flight = [f for f in features if f.stage == "IMPLEMENT"]
    if in_flight:
        f = in_flight[0]
        return (
            f"Finish implementation of '{f.name}'",
            f"Only feature in IMPLEMENT stage ({f.notes}). Quality gate: do not start new work while a feature is in flight.",
            str(f.feature_dir.relative_to(repo_root_for(sdd_root))).replace("\\", "/"),
        )
    in_review = [f for f in features if f.stage == "REVIEW"]
    if in_review:
        f = in_review[0]
        return (
            f"Close out '{f.name}' (currently in REVIEW)",
            f"Two-stage review then mark DONE. {f.notes}",
            str(f.feature_dir.relative_to(repo_root_for(sdd_root))).replace("\\", "/"),
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


# ---------------------------------------------------------------------------- #
# Markdown renderer -- SDD-002 7-section format
# ---------------------------------------------------------------------------- #

def render_markdown(*, generated_date: str, pi: PIBlock | None, features: list[Feature],
                    backlog: list[BacklogItem], roster: dict, ledger: LedgerView,
                    next_action: tuple[str, str, str | None]) -> str:
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
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto;
  gap: var(--sp-5); align-items: center;
  padding: var(--sp-3) var(--sp-5);
  border-bottom: 2px solid var(--color-interactive);
  background: var(--color-surface-raised);
}
.brand {
  font-size: var(--fs-md); letter-spacing: 0.18em;
  text-transform: uppercase; font-weight: 700; color: var(--color-text-primary);
  margin: 0;
}
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); border: 0;
}
.pi-pills { display: flex; gap: var(--sp-1); flex-wrap: wrap; }
.pi-pills .pill {
  padding: var(--sp-1) var(--sp-3);
  border: 1px solid var(--color-border-default);
  background: var(--color-surface-raised);
  color: var(--color-text-secondary);
  font-size: var(--fs-xs); letter-spacing: 0.14em;
  text-transform: uppercase;
}
.pi-pills .pill.current,
.pi-pills .pill.active {
  background: var(--color-interactive);
  border-color: var(--color-interactive);
  color: var(--ink-paper); font-weight: 700;
}
.pi-pills .pill.future { opacity: 0.45; }

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

/* ABOUT SECTION ------------------------------------------------- */
section#about {
  padding: var(--sp-3) var(--sp-5);
  border-bottom: 1px solid var(--color-border-default);
  background: var(--color-surface-raised);
}
section#about p { margin: 0 0 var(--sp-1) 0; color: var(--color-text-secondary); }
section#about p.about-where-we-are { color: var(--color-text-tertiary); font-size: var(--fs-sm); }

/* MAIN GRID (v3 sprint-first) ---------------------------------- */
main.grid-v3 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    "sprint sprint"
    "next   wip"
    "pi     pi"
    "agents agents"
    "feed   feed";
  gap: var(--sp-4);
  padding: var(--sp-5);
  opacity: 0;
  animation: fade-in 300ms ease forwards;
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

.zone-sprint { grid-area: sprint; }
.zone-next   { grid-area: next; }
.zone-wip    { grid-area: wip; }
.zone-pi     { grid-area: pi; }
.zone-agents { grid-area: agents; }
.zone-feed   { grid-area: feed; }

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
    Comes Next, WIP Summary, PI Context, Agent Activity placeholder,
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

    # ---- SECTION 5: Agent Activity placeholder --------------------------
    def _stat(n: int, label: str) -> str:
        return (
            f'<div class="fleet-stat">'
            f'<div class="n">{n}</div><div class="l">{h(label)}</div>'
            f'</div>'
        )

    fleet_stats_html = (
        f'<div class="fleet-summary">'
        f'{_stat(roster.get("principals", 0), "Principals")}'
        f'{_stat(roster.get("generic", 0), "Generic")}'
        f'{_stat(roster.get("specialist", 0), "Specialist")}'
        f'{_stat(roster.get("total_skills", 0), "Skills")}'
        f'</div>'
    )
    agents_section = (
        f'<section class="zone-agents" aria-labelledby="agents-heading">'
        f'<h2 id="agents-heading">Agent Activity</h2>'
        f'{fleet_stats_html}'
        f'<p class="defer-notice">'
        f'Per-agent real-time visibility planned for PI-5.'
        f'</p>'
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

    # ---- ABOUT SECTION (SDD-010, retained) -------------------------------
    if about_pi and about_sprint and about_focus:
        about_dynamic = f'{h(about_pi)} | {h(about_sprint)} | {h(about_focus)}'
    else:
        about_dynamic = h(ABOUT_FALLBACK)
    about_section_html = (
        f'<section id="about" aria-labelledby="about-heading">'
        f'<h2 id="about-heading" class="sr-only">About this dashboard</h2>'
        f'<p>{h(ABOUT_STATIC_PARAGRAPH)}</p>'
        f'<p class="about-where-we-are">{about_dynamic}</p>'
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
  <h1 class="brand">BRIDGE</h1>
  <nav class="pi-pills" aria-label="Program Increments">{pi_pills_html}</nav>
  <div class="live-pulse">
    <span class="dot {pulse_class}" aria-hidden="true"></span>
    <span>{h(pulse_text)}</span>
  </div>
  <div class="freshness" aria-live="polite">{h(generated_at)}</div>
</header>
{about_section_html}
<main id="main" role="main" class="grid-v3">
  {sprint_section}
  {next_section}
  {wip_section}
  {pi_section}
  {agents_section}
  {feed_section}
</main>
{footer_html}
</body></html>
"""
# ---------------------------------------------------------------------------- #
# Build orchestration
# ---------------------------------------------------------------------------- #

def build(*, sdd_root: Path | None = None, write: bool = True,
          pi_override: str | None = None, live_html: bool = False,
          port: int | None = None, fixed_date: str | None = None) -> dict:
    sdd_root = sdd_root or DEFAULT_SDD_ROOT
    sdd_root = Path(sdd_root).resolve()

    pis = load_pis(sdd_root)
    pi = current_pi(pis, override=pi_override)
    features = load_features(sdd_root)
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
    )
    htm = render_html(
        generated_at=generated_at, pi=pi, features=features, roster=roster,
        ledger=ledger, commits=commits, next_action=next_action,
        live=live_html, port=port, all_pis=pis,
        about_pi=about_pi, about_sprint=about_sprint, about_focus=about_focus,
        sprint_table=sprint_table, current_sprint=current_sprint,
        sprint_goal=sprint_goal, decisions=decisions,
    )

    result = {
        "markdown_chars": len(md), "html_chars": len(htm),
        "features": len(features), "commits": len(commits),
        "dispatches": len(ledger.recent), "pi": pi.name if pi else None,
        "html": htm, "markdown": md,
    }
    if write:
        exec_dir = sdd_root / "exec"
        exec_dir.mkdir(parents=True, exist_ok=True)
        (exec_dir / "state.md").write_text(md, encoding="utf-8")
        (exec_dir / "state.html").write_text(htm, encoding="utf-8")
        result["wrote"] = [str(exec_dir / "state.md"), str(exec_dir / "state.html")]
    return result


# ---------------------------------------------------------------------------- #
# Live HTTP server (state-dashboard feature)
# ---------------------------------------------------------------------------- #

class DashboardHandler(BaseHTTPRequestHandler):
    server_port: int = 8765
    sdd_root: Path = DEFAULT_SDD_ROOT

    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write(f"[bridge] {self.address_string()} {format % args}\n")

    def _send(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Security headers (REC-2 from SECURITY-REVIEW.md)
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; "
                         "style-src 'unsafe-inline'; "
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

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            try:
                info = build(sdd_root=self.sdd_root, write=False, live_html=True, port=self.server_port)
                self._send(200, info["html"].encode("utf-8"))
            except Exception as exc:
                msg = f"<h1>Build failed</h1><pre>{html.escape(repr(exc))}</pre>"
                self._send(500, msg.encode("utf-8"))
            return
        if path == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8"); return
        if path == "/favicon.ico":
            self._send(204, b"", "image/x-icon"); return
        self._send(404, b"<h1>404</h1>not found")


def _port_available(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port)); return True
    except OSError:
        return False
    finally:
        s.close()


def serve(sdd_root: Path, host: str = "127.0.0.1", port: int = 8765,
          open_browser: bool = True) -> int:
    if not _port_available(host, port):
        for offset in range(1, 6):
            if _port_available(host, port + offset):
                port = port + offset; break
        else:
            print(f"ERROR: no available port near {port} on {host}", file=sys.stderr); return 1
    DashboardHandler.server_port = port
    DashboardHandler.sdd_root = sdd_root
    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    url = f"http://{host}:{port}/"
    print(f"Bridge dashboard live at {url}")
    print("Each request rebuilds state from artifacts. Page auto-refreshes every 20s.")
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
# CLI
# ---------------------------------------------------------------------------- #

def _resolve_sdd_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    return DEFAULT_SDD_ROOT


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
    sub_serve.add_argument("--no-open", action="store_true")

    sub_build_index = sub.add_parser("build-index",
                                     help="Regenerate the sprint table in a PI INDEX.md from the ledger.")
    sub_build_index.add_argument("--pi", required=True, help="PI identifier, e.g. PI-3")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    sdd_root = _resolve_sdd_root(args.sdd_root)

    if not sdd_root.is_dir():
        print(f"ERROR: --sdd-root directory does not exist: {sdd_root}", file=sys.stderr)
        return 1

    if args.cmd == "serve":
        return serve(sdd_root=sdd_root, host=args.host, port=args.port,
                     open_browser=not args.no_open)

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
