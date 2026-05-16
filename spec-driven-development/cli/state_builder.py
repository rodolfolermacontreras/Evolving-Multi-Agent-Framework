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

    # 1. Explicit status wins -- but DONE still requires RETRO + 100% validation as a check
    explicit = _normalize_status_to_stage(status_line)
    if explicit:
        if explicit == "DONE":
            if has_retro and has_validation:
                v = (feature_dir / "validation.md").read_text(encoding="utf-8", errors="replace")
                if not re.findall(r"^\s*- \[ \]", v, re.MULTILINE):
                    return "DONE", status_line, "validation 100%, RETRO present, Status: done"
            # Status says done but evidence missing -> fall back to REVIEW
            return "REVIEW", status_line, "Status: done but RETRO or validation incomplete"
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
        is_current = "(current)" in title.lower()
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
}


HTML_CSS = """
:root {
  --bg-carbon:        #0a0a0a;
  --bg-graphite:      #141413;
  --bg-graphite-2:    #1c1b18;
  --bg-graphite-3:    #232220;
  --ink-paper:        #e8e4d8;
  --ink-paper-dim:    #b8b4a8;
  --ink-paper-faint:  #8a8678;
  --accent-oxblood:   #ce2029;
  --accent-oxblood-2: #a01820;
  --signal-amber:     #d29a3b;
  --signal-amber-2:   #e8b85a;
  --signal-amber-3:   #8a6a2a;
  --signal-jade:      #6fa37a;
  --signal-jade-dim:  #486a52;
  --rule-line:        #2a2925;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg-carbon); color: var(--ink-paper);
  font-family: ui-monospace, "Berkeley Mono", "JetBrains Mono", Menlo, Consolas, monospace;
  font-size: 13px; line-height: 1.45;
}
.body-sans { font-family: -apple-system, "Segoe UI", Inter, system-ui, sans-serif; }
a { color: var(--signal-amber-2); text-decoration: none; }
a:hover { text-decoration: underline; }

/* TOP BAR --------------------------------------------------------------- */
header.topbar {
  display: grid; grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 24px; align-items: center;
  padding: 14px 22px; border-bottom: 2px solid var(--accent-oxblood);
}
.mission { display: flex; align-items: baseline; gap: 14px; min-width: 0; }
.mission .h-bridge {
  font-size: 14px; letter-spacing: 0.18em;
  text-transform: uppercase; font-weight: 700; color: var(--ink-paper);
  flex-shrink: 0;
}
.mission .mission-text {
  font-family: -apple-system, "Segoe UI", Inter, system-ui, sans-serif;
  font-size: 13px; color: var(--ink-paper-dim);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.sprint-pills { display: flex; gap: 4px; }
.sprint-pills .pill {
  padding: 4px 12px; border: 1px solid var(--rule-line);
  background: var(--bg-graphite); color: var(--ink-paper-dim);
  font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase;
  cursor: default;
}
.sprint-pills .pill.active {
  background: var(--accent-oxblood); border-color: var(--accent-oxblood);
  color: var(--ink-paper); font-weight: 700;
}
.sprint-pills .pill.future { opacity: 0.45; }
.live-pulse {
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; color: var(--ink-paper-dim); letter-spacing: 0.06em;
}
.live-pulse .dot {
  width: 10px; height: 10px; border-radius: 50%;
  display: inline-block; flex-shrink: 0;
}
.dot.dot-green { background: var(--signal-jade); animation: pulse-green 1.6s ease-in-out infinite; }
.dot.dot-amber { background: var(--signal-amber); animation: pulse-amber 2.2s ease-in-out infinite; }
.dot.dot-red   { background: var(--accent-oxblood); animation: pulse-red 1.0s ease-in-out infinite; }
.dot.dot-gray  { background: var(--ink-paper-faint); }
@keyframes pulse-green { 0%,100% { box-shadow: 0 0 0 0 rgba(111,163,122,0.55); } 50% { box-shadow: 0 0 0 8px rgba(111,163,122,0); } }
@keyframes pulse-amber { 0%,100% { box-shadow: 0 0 0 0 rgba(210,154,59,0.55); } 50% { box-shadow: 0 0 0 8px rgba(210,154,59,0); } }
@keyframes pulse-red   { 0%,100% { box-shadow: 0 0 0 0 rgba(206,32,41,0.55); } 50% { box-shadow: 0 0 0 8px rgba(206,32,41,0); } }
.live-pulse .meta { color: var(--ink-paper-faint); margin-left: 8px; }
.btn-refresh {
  border: 1px solid var(--rule-line); padding: 5px 12px;
  color: var(--ink-paper); background: var(--bg-graphite);
  font-family: inherit; font-size: 11px;
  letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
  margin-left: 12px;
}
.btn-refresh:hover { border-color: var(--signal-amber-2); color: var(--signal-amber-2); }

/* 4-ZONE LAYOUT --------------------------------------------------------- */
main.layout-4zone {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  grid-template-rows: auto auto;
  grid-template-areas:
    "a b"
    "c c"
    "d d";
  gap: 14px;
  padding: 18px 22px;
}
.zone { background: var(--bg-graphite); border: 1px solid var(--rule-line); padding: 16px 18px; min-width: 0; }
.zone-a { grid-area: a; }
.zone-b { grid-area: b; }
.zone-c { grid-area: c; }
.zone-d { grid-area: d; }
.zone h2 {
  margin: 0 0 12px; font-size: 10px;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--ink-paper-dim);
  border-bottom: 1px solid var(--rule-line); padding-bottom: 6px;
}
.zone h2 .sub { color: var(--ink-paper-faint); letter-spacing: 0.06em; margin-left: 8px; font-weight: normal; }
.zone .defer-note {
  margin: 12px 0 0; padding: 8px 10px;
  border-left: 2px solid var(--signal-amber-3);
  background: var(--bg-graphite-2);
  font-size: 10px; color: var(--ink-paper-faint);
  letter-spacing: 0.06em;
}
.zone .defer-note code { color: var(--signal-amber-2); }

/* ZONE A: Big picture ---------------------------------------------------- */
.big-picture { display: grid; grid-template-columns: 140px 1fr; gap: 18px; align-items: start; }
.progress-ring { position: relative; width: 140px; height: 140px; }
.progress-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.progress-ring .ring-bg { fill: none; stroke: var(--bg-graphite-3); stroke-width: 12; }
.progress-ring .ring-fg {
  fill: none; stroke: var(--signal-jade); stroke-width: 12; stroke-linecap: round;
  transition: stroke-dashoffset 700ms ease;
}
.progress-ring .ring-center {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.progress-ring .pct-big { font-size: 28px; font-weight: 700; color: var(--ink-paper); line-height: 1; }
.progress-ring .pct-sub { font-size: 9px; color: var(--ink-paper-dim); letter-spacing: 0.14em; margin-top: 4px; text-transform: uppercase; }
.feature-stack { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.feature-stack .row {
  display: grid; grid-template-columns: 14px minmax(0, 1fr) auto;
  gap: 10px; align-items: center;
  padding: 6px 0; border-bottom: 1px dashed var(--rule-line);
  font-size: 11px; color: var(--ink-paper-dim);
}
.feature-stack .row:last-child { border-bottom: none; }
.feature-stack .dot {
  width: 10px; height: 10px; border-radius: 50%; display: inline-block;
}
.feature-stack .dot.tone-faint        { background: var(--ink-paper-faint); }
.feature-stack .dot.tone-amber-soft   { background: var(--signal-amber-3); }
.feature-stack .dot.tone-amber        { background: var(--signal-amber); }
.feature-stack .dot.tone-amber-bright { background: var(--signal-amber-2); }
.feature-stack .dot.tone-oxblood      { background: var(--accent-oxblood); }
.feature-stack .dot.tone-jade         { background: var(--signal-jade); }
.feature-stack .name { color: var(--ink-paper); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feature-stack .meta { color: var(--ink-paper-faint); font-size: 10px; text-align: right; letter-spacing: 0.04em; }

.next-card {
  margin-top: 14px; padding: 12px 14px;
  background: var(--bg-graphite-2); border-left: 3px solid var(--accent-oxblood);
}
.next-card .label { font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent-oxblood); margin-bottom: 4px; }
.next-card .title { font-size: 14px; font-weight: 700; color: var(--ink-paper); margin-bottom: 4px; }
.next-card .why   { font-size: 11px; color: var(--ink-paper-dim); margin-bottom: 8px; }
.next-card .cta {
  display: inline-block; border: 1px solid var(--accent-oxblood);
  color: var(--ink-paper); background: rgba(206, 32, 41, 0.08);
  padding: 4px 12px; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase;
}
.next-card .cta:hover { background: rgba(206, 32, 41, 0.2); text-decoration: none; }

/* ZONE B: Agent activity (text-mode v2.1; D3 graph deferred to SDD-008) -- */
.feature-cluster {
  margin-bottom: 12px; padding: 10px 12px;
  background: var(--bg-graphite-2); border-left: 3px solid var(--ink-paper-faint);
}
.feature-cluster.tone-faint        { border-left-color: var(--ink-paper-faint); }
.feature-cluster.tone-amber-soft   { border-left-color: var(--signal-amber-3); }
.feature-cluster.tone-amber        { border-left-color: var(--signal-amber); }
.feature-cluster.tone-amber-bright { border-left-color: var(--signal-amber-2); }
.feature-cluster.tone-oxblood      { border-left-color: var(--accent-oxblood); }
.feature-cluster.tone-jade         { border-left-color: var(--signal-jade); }
.feature-cluster .feat-title { font-size: 11px; color: var(--ink-paper); font-weight: 700; margin-bottom: 6px; }
.feature-cluster .feat-title .stage-tag {
  font-size: 9px; letter-spacing: 0.14em; color: var(--ink-paper-faint); font-weight: normal;
  margin-left: 8px; text-transform: uppercase;
}
.feature-cluster .agents { display: flex; flex-wrap: wrap; gap: 6px; }
.agent-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 9px; background: var(--bg-graphite-3); border: 1px solid var(--rule-line);
  font-size: 10px; color: var(--ink-paper-dim);
}
.agent-chip .avatar {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--signal-jade-dim); color: var(--ink-paper);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 700;
}
.agent-chip.principal .avatar { background: var(--accent-oxblood-2); }
.agent-chip.active .avatar  { background: var(--signal-jade); }
.agent-chip.idle .avatar    { background: var(--ink-paper-faint); }

.fleet-summary {
  margin-top: 12px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
}
.fleet-summary .stat { background: var(--bg-graphite-3); padding: 8px 10px; border: 1px solid var(--rule-line); }
.fleet-summary .stat.zero { opacity: 0.55; }
.fleet-summary .stat .n { font-size: 18px; font-weight: 700; color: var(--ink-paper); line-height: 1; }
.fleet-summary .stat .l { font-size: 8px; letter-spacing: 0.18em; color: var(--ink-paper-dim); text-transform: uppercase; margin-top: 4px; }

/* ZONE C: Feature swim lanes -------------------------------------------- */
.swim-lanes { display: flex; flex-direction: column; gap: 8px; }
.swim-row {
  display: grid; grid-template-columns: 200px minmax(0, 1fr) 100px;
  gap: 12px; align-items: center;
}
.swim-row .label { font-size: 11px; color: var(--ink-paper); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.swim-track {
  position: relative; height: 18px;
  background: var(--bg-graphite-3); border: 1px solid var(--rule-line); overflow: hidden;
}
.swim-fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  background: var(--signal-amber-3);
  transition: width 700ms ease;
}
.swim-fill.tone-faint        { background: var(--ink-paper-faint); }
.swim-fill.tone-amber-soft   { background: var(--signal-amber-3); }
.swim-fill.tone-amber        { background: var(--signal-amber); }
.swim-fill.tone-amber-bright { background: var(--signal-amber-2); }
.swim-fill.tone-oxblood      { background: var(--accent-oxblood); }
.swim-fill.tone-jade         { background: var(--signal-jade); }
.swim-marker {
  position: absolute; top: 50%; transform: translate(-50%, -50%);
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--ink-paper); border: 2px solid var(--bg-carbon);
  z-index: 2;
}
.swim-stages {
  position: absolute; left: 0; right: 0; top: 0; bottom: 0;
  display: flex; pointer-events: none;
}
.swim-stages .tick {
  flex: 1; border-right: 1px dashed rgba(138,134,120,0.18);
}
.swim-stages .tick:last-child { border-right: none; }
.swim-row .stage-text {
  font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink-paper-dim); text-align: right;
}
.swim-axis {
  margin-top: 4px;
  display: grid; grid-template-columns: 200px minmax(0, 1fr) 100px; gap: 12px;
}
.swim-axis .stages {
  display: grid; grid-template-columns: repeat(9, 1fr);
  font-size: 8px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink-paper-faint);
}
.swim-axis .stages span { text-align: center; }
.swim-axis .stages span.active { color: var(--ink-paper); font-weight: 700; }

/* ZONE D: Unified activity feed ----------------------------------------- */
.activity-controls { display: flex; gap: 6px; align-items: center; margin-bottom: 8px; }
.activity-controls .toggle {
  font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--ink-paper-faint);
}
.activity-list { display: flex; flex-direction: column; }
.activity-row {
  display: grid; grid-template-columns: 70px 18px 60px minmax(0, 1fr) auto;
  gap: 10px; align-items: baseline;
  padding: 7px 0; border-bottom: 1px dashed var(--rule-line);
  font-size: 11px;
}
.activity-row:last-child { border-bottom: none; }
.activity-row .when { color: var(--ink-paper-faint); font-size: 10px; }
.activity-row .avatar {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--bg-graphite-3); color: var(--ink-paper-dim);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 8px; font-weight: 700; border: 1px solid var(--rule-line);
}
.activity-row .badge {
  font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 1px 6px; border: 1px solid currentColor;
  display: inline-block; text-align: center;
}
.badge.t-jade         { color: var(--signal-jade); }
.badge.t-amber        { color: var(--signal-amber); }
.badge.t-amber-soft   { color: var(--signal-amber-3); }
.badge.t-amber-bright { color: var(--signal-amber-2); }
.badge.t-oxblood      { color: var(--accent-oxblood); }
.badge.t-faint        { color: var(--ink-paper-faint); }
.activity-row .desc { color: var(--ink-paper-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.activity-row .feat-tag {
  font-size: 9px; color: var(--ink-paper-faint);
  border: 1px solid var(--rule-line); padding: 1px 6px;
  letter-spacing: 0.06em;
}

/* footer ---------------------------------------------------------------- */
footer {
  padding: 14px 22px; border-top: 1px solid var(--rule-line);
  color: var(--ink-paper-faint); font-size: 10px;
  letter-spacing: 0.08em; text-transform: uppercase;
}

@media (max-width: 1100px) {
  main.layout-4zone {
    grid-template-columns: 1fr;
    grid-template-areas: "a" "b" "c" "d";
  }
  .big-picture { grid-template-columns: 100px 1fr; }
  .progress-ring { width: 100px; height: 100px; }
  .swim-row, .swim-axis { grid-template-columns: 120px minmax(0, 1fr) 80px; }
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
                all_pis: list[PIBlock] | None = None) -> str:
    """Render the 4-zone v3 Bridge dashboard."""

    # ---- TOP BAR ---------------------------------------------------------
    pi_name = pi.name if pi else "no PI"
    mission_text = PI_MISSION.get(pi_name, pi.title if pi else "")
    pulse_class, pulse_text = _pulse(roster, ledger, features)

    sprint_pills_html = ""
    if all_pis:
        for p in all_pis:
            cls = "pill"
            if p.is_current or (pi and p.name == pi.name):
                cls += " active"
            elif p.pct < 100 and not p.is_current:
                cls += " future"
            sprint_pills_html += f'<span class="{cls}">{h(p.name)}</span>'

    refresh_meta = '<meta http-equiv="refresh" content="20">' if live else ''
    live_badge = ('live' if live else 'static')
    refresh_btn = (
        '<a class="btn-refresh" href="/" title="Reload now">&#x21bb; refresh</a>' if live else
        '<a class="btn-refresh" href="state.html" title="Reload the static file">&#x21bb; reload</a>'
    )

    # ---- ZONE A: Big Picture --------------------------------------------
    pct = _weighted_progress(features)
    circumference = 2 * 3.14159 * 60
    dash_offset = circumference * (1 - pct / 100)

    feature_stack_html = ""
    if features:
        # Order: in-flight first, then by stage descending, then alphabetical
        order_key = lambda f: (-STAGE_WEIGHT.get(f.stage, 0), f.name)
        for f in sorted(features, key=order_key):
            tone = STAGE_TONE[f.stage]
            nxt = _next_for(f)
            meta = f"next: {nxt}" if f.stage != "DONE" else "shipped"
            feature_stack_html += (
                f'<div class="row">'
                f'<span class="dot {tone}"></span>'
                f'<span class="name" title="{h(f.notes)}">{h(f.name)}</span>'
                f'<span class="meta">{h(_stage_short(f.stage))} -&gt; {h(meta)}</span>'
                f'</div>'
            )
    else:
        feature_stack_html = '<div class="row"><span class="meta">no features yet</span></div>'

    action_title, why, link = next_action
    nxt_summary = _next_what(features)
    cta_html = f'<a class="cta" href="{h(link)}" target="_blank">Open &rarr; {h(link)}</a>' if link else ''

    zone_a_html = f"""
    <section class="zone zone-a">
      <h2>Mission Progress <span class="sub">(weighted by stage)</span></h2>
      <div class="big-picture">
        <div class="progress-ring">
          <svg viewBox="0 0 140 140">
            <circle class="ring-bg" cx="70" cy="70" r="60"></circle>
            <circle class="ring-fg" cx="70" cy="70" r="60"
                    stroke-dasharray="{circumference:.2f}"
                    stroke-dashoffset="{dash_offset:.2f}"></circle>
          </svg>
          <div class="ring-center">
            <div class="pct-big">{pct}%</div>
            <div class="pct-sub">{len(features)} feat</div>
          </div>
        </div>
        <div class="feature-stack">{feature_stack_html}</div>
      </div>
      <div class="next-card">
        <div class="label">Recommended next action</div>
        <div class="title">{h(action_title)}</div>
        <div class="why">{h(why)} &middot; Trajectory: {h(nxt_summary)}.</div>
        {cta_html}
      </div>
    </section>
    """

    # ---- ZONE B: Agent activity (text-mode v2.1; D3 graph -> SDD-008) ----
    cluster_html = ""
    active_features = [f for f in features if f.stage not in ("DONE", "BACKLOG", "IDEA")]
    if not active_features:
        cluster_html = '<div class="defer-note">No active features. Fleet is idle.</div>'
    for f in active_features:
        agents = _agents_for_feature(roster, f, ledger)
        tone = STAGE_TONE[f.stage]
        chips_html = ""
        if agents:
            for a in agents:
                initials = "".join(p[0].upper() for p in a["id"].split("-")[:2])
                role_short = a["role"].split("-")[0]
                kind_cls = "active" if a["status"] == "active" else "idle"
                chips_html += (
                    f'<span class="agent-chip {kind_cls}" title="{h(a["id"])} - {h(a["role"])}">'
                    f'<span class="avatar">{h(initials)}</span>{h(role_short)}'
                    f'</span>'
                )
        else:
            chips_html = '<span class="agent-chip"><span class="avatar">??</span>no dispatch yet</span>'
        cluster_html += (
            f'<div class="feature-cluster {tone}">'
            f'<div class="feat-title">{h(f.name)}<span class="stage-tag">{h(_stage_short(f.stage))}</span></div>'
            f'<div class="agents">{chips_html}</div>'
            f'</div>'
        )

    fleet_summary_html = ""
    def _stat(n, label):
        cls = "stat zero" if n == 0 else "stat"
        return f'<div class="{cls}"><div class="n">{n}</div><div class="l">{label}</div></div>'
    fleet_summary_html = (
        f'<div class="fleet-summary">'
        f'{_stat(roster["principals"], "Principals")}'
        f'{_stat(roster["generic"], "Generic")}'
        f'{_stat(roster["specialist"], "Specialist")}'
        f'{_stat(roster["total_skills"], "Skills")}'
        f'</div>'
    )

    zone_b_html = f"""
    <section class="zone zone-b">
      <h2>Agent Activity <span class="sub">(by feature)</span></h2>
      {cluster_html}
      {fleet_summary_html}
      <div class="defer-note">Live force-directed network graph -&gt; <code>SDD-008</code> (deferred: requires JS deps + WebSocket).</div>
    </section>
    """

    # ---- ZONE C: Swim lanes ----------------------------------------------
    lanes_html = ""
    if features:
        # Active features first (descending by stage), DONE last (alphabetical)
        active = sorted([f for f in features if f.stage != "DONE"],
                        key=lambda f: (-STAGE_WEIGHT.get(f.stage, 0), f.name))
        done = sorted([f for f in features if f.stage == "DONE"], key=lambda f: f.name)
        ordered = active + done
        for f in ordered:
            tone = STAGE_TONE[f.stage]
            fill_pct = STAGE_WEIGHT.get(f.stage, 0)
            ticks = "".join('<div class="tick"></div>' for _ in STAGES)
            lanes_html += (
                f'<div class="swim-row">'
                f'<span class="label" title="{h(f.notes)}">{h(f.name)}</span>'
                f'<div class="swim-track">'
                f'<div class="swim-stages">{ticks}</div>'
                f'<div class="swim-fill {tone}" style="width:{fill_pct}%"></div>'
                f'<div class="swim-marker" style="left:{fill_pct}%"></div>'
                f'</div>'
                f'<span class="stage-text">{h(_stage_short(f.stage))}</span>'
                f'</div>'
            )
    else:
        lanes_html = '<div class="defer-note">No features registered yet.</div>'

    axis_html = (
        '<div class="swim-axis">'
        '<span></span>'
        '<div class="stages">'
        + "".join(f'<span>{s.title()}</span>' for s in STAGES) +
        '</div><span></span></div>'
    )

    zone_c_html = f"""
    <section class="zone zone-c">
      <h2>Feature Pipeline <span class="sub">(stage-weighted; bigger fill = closer to done)</span></h2>
      <div class="swim-lanes">{lanes_html}</div>
      {axis_html}
    </section>
    """

    # ---- ZONE D: Unified activity feed -----------------------------------
    # Merge commits and dispatches into one chronological feed.
    feed: list[tuple[str, dict]] = []
    for sha, subj, rel in commits:
        ctype, rest = split_commit_type(subj)
        feed.append((rel, {
            "kind": "commit", "when": rel, "actor": sha,
            "actor_short": sha[:5], "badge_type": ctype or "chore",
            "badge_tone": COMMIT_TYPE_TONE.get(ctype or "chore", "faint"),
            "desc": rest, "feat": "",
        }))
    if ledger.recent:
        for d in ledger.recent:
            actor = d.get("agent_id", "?")
            initials = "".join(p[0].upper() for p in actor.split("-")[:2]) or "??"
            outcome = d.get("outcome") or "pending"
            tone = {"success": "jade", "failed": "oxblood",
                    "blocked": "oxblood", "pending": "amber"}.get(outcome, "amber")
            feat = (d.get("feature_dir") or "").rsplit("/", 1)[-1] or ""
            feed.append((d.get("dispatched_at", ""), {
                "kind": "dispatch", "when": "ledger",
                "actor_short": initials,
                "badge_type": f"dispatch:{outcome}",
                "badge_tone": tone,
                "desc": f"{d.get('task_id','')} {d.get('task_title','')}",
                "feat": feat,
            }))
    # Sort: dispatches have ISO timestamps that sort lexicographically; commits use relative dates.
    # Show all dispatches first (most authoritative), then commits in repo order.
    dispatch_items = [item for ts, item in feed if item["kind"] == "dispatch"]
    commit_items = [item for ts, item in feed if item["kind"] == "commit"]
    feed_ordered = dispatch_items + commit_items

    feed_rows_html = ""
    for item in feed_ordered[:20]:
        feat_tag = f'<span class="feat-tag">{h(item["feat"])}</span>' if item["feat"] else '<span></span>'
        feed_rows_html += (
            f'<div class="activity-row">'
            f'<span class="when">{h(item["when"])}</span>'
            f'<span class="avatar" title="{h(item.get("actor", item["actor_short"]))}">{h(item["actor_short"])}</span>'
            f'<span class="badge t-{item["badge_tone"]}">{h(item["badge_type"])}</span>'
            f'<span class="desc">{h(item["desc"])}</span>'
            f'{feat_tag}'
            f'</div>'
        )
    if not feed_rows_html:
        feed_rows_html = '<div class="defer-note">No activity yet. Dispatches and commits will appear here.</div>'

    zone_d_html = f"""
    <section class="zone zone-d">
      <h2>Activity Feed <span class="sub">(dispatches + commits, newest first, top 20)</span></h2>
      <div class="activity-list">{feed_rows_html}</div>
    </section>
    """

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{refresh_meta}
<title>Bridge -- {h(pi_name)} -- {h(generated_at)}</title>
<style>{HTML_CSS}</style>
</head><body>
<header class="topbar">
  <div class="mission">
    <span class="h-bridge">Bridge</span>
    <span class="mission-text">{h(mission_text)}</span>
  </div>
  <div class="sprint-pills">{sprint_pills_html}</div>
  <div class="live-pulse">
    <span class="dot {pulse_class}"></span>
    <span>{h(pulse_text)}</span>
    <span class="meta">| {live_badge}</span>
    {refresh_btn}
  </div>
</header>
<main class="layout-4zone">
  {zone_a_html}
  {zone_b_html}
  {zone_c_html}
  {zone_d_html}
</main>
<footer>Auto-generated by cli/state_builder.py &middot; {("live mode @ :" + str(port)) if (live and port) else "file mode"} &middot; v2.1 (4-zone) &middot; v3 (D3 + WebSocket) tracked as SDD-008</footer>
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

    generated_date = fixed_date or dt.date.today().isoformat()        # MD: day precision = deterministic
    generated_at = fixed_date or dt.datetime.now().strftime("%Y-%m-%d %H:%M")  # HTML: more precise

    md = render_markdown(
        generated_date=generated_date, pi=pi, features=features, backlog=backlog,
        roster=roster, ledger=ledger, next_action=next_action,
    )
    htm = render_html(
        generated_at=generated_at, pi=pi, features=features, roster=roster,
        ledger=ledger, commits=commits, next_action=next_action,
        live=live_html, port=port, all_pis=pis,
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
