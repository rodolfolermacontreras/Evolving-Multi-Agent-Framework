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

HTML_CSS = """
:root {
  --bg-carbon:       #0a0a0a;
  --bg-graphite:     #141413;
  --bg-graphite-2:   #1c1b18;
  --ink-paper:       #e8e4d8;
  --ink-paper-dim:   #b8b4a8;
  --ink-paper-faint: #8a8678;
  --accent-oxblood:  #ce2029;
  --signal-amber:    #d29a3b;
  --signal-amber-2:  #e8b85a;
  --signal-amber-3:  #8a6a2a;
  --signal-jade:     #6fa37a;
  --rule-line:       #2a2925;
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
header.bridge-header {
  border-bottom: 2px solid var(--accent-oxblood);
  padding: 14px 22px 12px;
  display: flex; align-items: baseline; justify-content: space-between; gap: 18px; flex-wrap: wrap;
}
.brand { display: flex; align-items: baseline; gap: 14px; }
.brand .h-bridge { font-size: 14px; letter-spacing: 0.18em; font-weight: 700; text-transform: uppercase; color: var(--ink-paper); }
.brand .h-pi { font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--signal-amber-2); }
.brand .h-title { font-size: 12px; color: var(--ink-paper-dim); letter-spacing: 0.04em; }
.header-actions { display: flex; gap: 14px; align-items: center; font-size: 11px; }
.header-actions .meta { color: var(--ink-paper-dim); letter-spacing: 0.08em; text-transform: uppercase; }
.btn-refresh {
  border: 1px solid var(--rule-line); padding: 5px 12px;
  color: var(--ink-paper); background: var(--bg-graphite);
  font-family: inherit; font-size: 11px;
  letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
}
.btn-refresh:hover { border-color: var(--signal-amber-2); color: var(--signal-amber-2); }
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 0; min-height: calc(100vh - 62px); }
.main { padding: 22px 24px; min-width: 0; }
.side { padding: 22px 22px; border-left: 1px solid var(--rule-line); background: var(--bg-graphite); min-width: 0; }
section.panel { margin-bottom: 28px; }
section.panel h2 {
  margin: 0 0 12px; font-size: 11px;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-paper-dim);
  border-bottom: 1px solid var(--rule-line); padding-bottom: 6px;
}
.next-action {
  background: var(--bg-graphite); border-left: 4px solid var(--accent-oxblood);
  padding: 16px 20px; margin-bottom: 26px;
}
.next-action .label { font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--accent-oxblood); margin-bottom: 8px; }
.next-action .title { font-size: 19px; font-weight: 700; color: var(--ink-paper); margin-bottom: 6px; letter-spacing: -0.01em; }
.next-action .why { color: var(--ink-paper-dim); font-size: 13px; margin-bottom: 12px; }
.next-action .cta {
  display: inline-block; border: 1px solid var(--accent-oxblood);
  color: var(--ink-paper); background: rgba(206, 32, 41, 0.08);
  padding: 6px 14px; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
}
.next-action .cta:hover { background: rgba(206, 32, 41, 0.20); text-decoration: none; }
.progress { margin-bottom: 18px; }
.progress .label-row {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 11px; color: var(--ink-paper-dim); margin-bottom: 6px;
  letter-spacing: 0.08em; text-transform: uppercase;
}
.progress .pct { color: var(--ink-paper); font-weight: 700; font-size: 14px; }
.progress .seg-bar {
  height: 22px; display: flex;
  background: var(--bg-graphite-2); border: 1px solid var(--rule-line); overflow: hidden;
}
.progress .seg { transition: width 240ms ease; min-width: 0; }
.progress .seg.tone-faint        { background: var(--ink-paper-faint); }
.progress .seg.tone-amber-soft   { background: var(--signal-amber-3); }
.progress .seg.tone-amber        { background: var(--signal-amber); }
.progress .seg.tone-amber-bright { background: var(--signal-amber-2); }
.progress .seg.tone-oxblood      { background: var(--accent-oxblood); }
.progress .seg.tone-jade         { background: var(--signal-jade); }
.legend {
  display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px;
  font-size: 10px; color: var(--ink-paper-dim); letter-spacing: 0.06em; text-transform: uppercase;
}
.legend .item { display: flex; align-items: center; gap: 6px; }
.legend .swatch { width: 10px; height: 10px; display: inline-block; border: 1px solid var(--rule-line); }
.legend .swatch.tone-faint        { background: var(--ink-paper-faint); }
.legend .swatch.tone-amber-soft   { background: var(--signal-amber-3); }
.legend .swatch.tone-amber        { background: var(--signal-amber); }
.legend .swatch.tone-amber-bright { background: var(--signal-amber-2); }
.legend .swatch.tone-oxblood      { background: var(--accent-oxblood); }
.legend .swatch.tone-jade         { background: var(--signal-jade); }
.commitments {
  list-style: none; padding: 0; margin: 14px 0 0; font-size: 12px;
  border: 1px solid var(--rule-line); background: var(--bg-graphite);
}
.commitments li {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 7px 12px; border-bottom: 1px dashed var(--rule-line);
  color: var(--ink-paper-dim);
}
.commitments li:last-child { border-bottom: none; }
.commitments li.done { color: var(--signal-jade); background: rgba(111, 163, 122, 0.04); }
.commitments li .mark { font-family: inherit; color: var(--ink-paper-faint); width: 18px; flex-shrink: 0; }
.commitments li.done .mark { color: var(--signal-jade); }
.kanban { display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 6px; overflow-x: auto; }
.kanban .col {
  background: var(--bg-graphite); border: 1px solid var(--rule-line);
  padding: 8px 8px 10px; min-height: 130px;
  display: flex; flex-direction: column;
}
.kanban .col.empty { background: transparent; border-style: dashed; border-color: var(--rule-line); }
.kanban .col h3 {
  margin: 0 0 8px; font-size: 9px; letter-spacing: 0.18em;
  color: var(--ink-paper-dim); text-transform: uppercase;
  border-bottom: 1px solid var(--rule-line); padding-bottom: 5px;
  display: flex; justify-content: space-between; align-items: baseline; gap: 6px;
}
.kanban .col h3 .count {
  font-size: 10px; color: var(--ink-paper); font-weight: 700;
  background: var(--bg-graphite-2); padding: 1px 6px; border: 1px solid var(--rule-line);
}
.kanban .col.empty h3 .count { display: none; }
.kanban .col.empty h3 { color: var(--ink-paper-faint); }
.kanban .card {
  background: var(--bg-graphite-2); border-left: 3px solid var(--ink-paper-faint);
  padding: 7px 10px; margin-bottom: 7px; font-size: 11px; word-break: break-word;
}
.kanban .card.tone-faint        { border-left-color: var(--ink-paper-faint); }
.kanban .card.tone-amber-soft   { border-left-color: var(--signal-amber-3); }
.kanban .card.tone-amber        { border-left-color: var(--signal-amber); }
.kanban .card.tone-amber-bright { border-left-color: var(--signal-amber-2); }
.kanban .card.tone-oxblood      { border-left-color: var(--accent-oxblood); }
.kanban .card.tone-jade         { border-left-color: var(--signal-jade); }
.kanban .card .name { color: var(--ink-paper); font-weight: 600; margin-bottom: 3px; }
.kanban .card .meta { color: var(--ink-paper-dim); font-size: 10px; }
.kanban .col.empty .card-empty {
  color: var(--ink-paper-faint); font-size: 11px;
  display: flex; align-items: center; justify-content: center;
  flex: 1; padding: 12px 0;
}
table.dense { width: 100%; border-collapse: collapse; font-size: 11px; }
table.dense th, table.dense td {
  padding: 6px 8px; text-align: left;
  border-bottom: 1px solid var(--rule-line); vertical-align: top;
}
table.dense th {
  font-weight: 600; color: var(--ink-paper-dim);
  font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
}
.fleet-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px; }
.fleet-stats .stat {
  background: var(--bg-graphite-2); border: 1px solid var(--rule-line); padding: 12px 14px;
}
.fleet-stats .stat.zero { opacity: 0.55; }
.fleet-stats .stat .n { font-size: 24px; color: var(--ink-paper); font-weight: 700; line-height: 1; }
.fleet-stats .stat .l {
  font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-paper-dim); margin-top: 6px;
}
.fleet-stats .stat .hint { font-size: 9px; color: var(--ink-paper-faint); margin-top: 4px; }
.activity { font-size: 11px; }
.activity .row {
  padding: 6px 0; border-bottom: 1px dashed var(--rule-line);
  display: grid; grid-template-columns: 56px auto 1fr; gap: 8px; align-items: baseline;
}
.activity .sha { color: var(--signal-amber-2); font-weight: 600; }
.activity .type {
  display: inline-block; font-size: 9px; letter-spacing: 0.1em;
  padding: 1px 6px; border: 1px solid currentColor;
  text-transform: uppercase; line-height: 1.4;
}
.activity .type.t-jade         { color: var(--signal-jade); }
.activity .type.t-amber        { color: var(--signal-amber); }
.activity .type.t-amber-soft   { color: var(--signal-amber-3); }
.activity .type.t-amber-bright { color: var(--signal-amber-2); }
.activity .type.t-oxblood      { color: var(--accent-oxblood); }
.activity .type.t-faint        { color: var(--ink-paper-faint); }
.activity .subj { color: var(--ink-paper-dim); overflow: hidden; text-overflow: ellipsis; }
.activity .rel  { color: var(--ink-paper-faint); font-size: 10px; }
.empty-state {
  border: 1px dashed var(--rule-line); background: var(--bg-graphite-2);
  padding: 22px; text-align: center; color: var(--ink-paper-dim); font-size: 12px;
}
.empty-state .icon { font-size: 18px; color: var(--ink-paper-faint); margin-bottom: 8px; letter-spacing: 0.2em; }
.empty-state .hint { font-size: 10px; color: var(--ink-paper-faint); margin-top: 6px; letter-spacing: 0.06em; }
footer {
  padding: 14px 22px; border-top: 1px solid var(--rule-line);
  color: var(--ink-paper-faint); font-size: 10px;
  letter-spacing: 0.08em; text-transform: uppercase;
}
@media (max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
  .side { border-left: none; border-top: 1px solid var(--rule-line); }
  .kanban { grid-template-columns: repeat(3, minmax(140px, 1fr)); }
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


def render_html(*, generated_at: str, pi: PIBlock | None, features: list[Feature],
                roster: dict, ledger: LedgerView, commits: list[tuple[str, str, str]],
                next_action: tuple[str, str, str | None],
                live: bool = False, port: int | None = None) -> str:

    by_stage: dict[str, list[Feature]] = {s: [] for s in STAGES}
    for f in features:
        by_stage.setdefault(f.stage, []).append(f)

    # PI panel
    pi_block_html = ""
    if pi:
        counts = {s: len(by_stage.get(s, [])) for s in STAGES}
        total_features = sum(counts.values()) or 1
        seg_html = ""
        legend_html = ""
        for s in STAGES:
            n = counts.get(s, 0)
            if n == 0:
                continue
            tone = STAGE_TONE[s]
            pct = n * 100 / total_features
            seg_html += f'<div class="seg {tone}" style="width:{pct:.2f}%" title="{s}: {n}"></div>'
            legend_html += f'<span class="item"><span class="swatch {tone}"></span>{s} ({n})</span>'
        commitments_html = ""
        for c, label in pi.checkboxes:
            commitments_html += (
                f'<li class="{"done" if c else ""}">'
                f'<span class="mark">{"[x]" if c else "[ ]"}</span>'
                f'<span>{h(label)}</span></li>'
            )
        pi_block_html = f"""
        <section class="panel">
          <h2>{h(pi.name)} -- Feature Distribution</h2>
          <div class="progress">
            <div class="label-row">
              <span>{h(pi.title)}</span>
              <span class="pct">{pi.done} / {pi.total} commitments &nbsp; {pi.pct}%</span>
            </div>
            <div class="seg-bar">{seg_html or '<div class="seg tone-faint" style="width:100%"></div>'}</div>
            <div class="legend">{legend_html}</div>
          </div>
          <h2 style="margin-top:18px">{h(pi.name)} Commitments</h2>
          <ul class="commitments">{commitments_html}</ul>
        </section>
        """

    # Kanban
    kanban_html = '<div class="kanban">'
    for s in STAGES:
        cards = by_stage.get(s, [])
        col_class = "col" if cards else "col empty"
        count_badge = f'<span class="count">{len(cards)}</span>' if cards else ''
        kanban_html += f'<div class="{col_class}"><h3><span>{h(s)}</span>{count_badge}</h3>'
        if not cards:
            kanban_html += '<div class="card-empty">&mdash;</div>'
        for f in cards:
            tone = STAGE_TONE[s]
            kanban_html += (
                f'<div class="card {tone}">'
                f'<div class="name">{h(f.name)}</div>'
                f'<div class="meta">{h(f.created)} &middot; {h(f.notes)}</div>'
                f'</div>'
            )
        kanban_html += '</div>'
    kanban_html += '</div>'

    # Fleet stats
    def stat(n, label, hint=""):
        cls = "stat zero" if n == 0 else "stat"
        return (f'<div class="{cls}" title="{h(hint)}"><div class="n">{n}</div>'
                f'<div class="l">{h(label)}</div>' +
                (f'<div class="hint">{h(hint)}</div>' if hint else '') + '</div>')
    fleet_html = '<div class="fleet-stats">'
    fleet_html += stat(roster['principals'], "Principals", "EM, PM, Arch, SW Dev")
    fleet_html += stat(roster['generic'], "Generic", "developer, ux, qa, data-sci")
    fleet_html += stat(roster['specialist'], "Specialist", "none earned yet")
    fleet_html += stat(roster['total_skills'], "Skills", f"{roster['total_skills']} loadable")
    fleet_html += '</div>'

    # Commits with type tags
    commits_html = '<div class="activity">'
    if not commits:
        commits_html += '<div class="empty-state"><div class="icon">//</div>No commits found.</div>'
    for sha, subj, rel in commits:
        ctype, rest = split_commit_type(subj)
        if ctype:
            tone = COMMIT_TYPE_TONE.get(ctype, "faint")
            type_html = f'<span class="type t-{tone}">{h(ctype)}</span>'
            subj_html = h(rest)
        else:
            type_html = '<span></span>'
            subj_html = h(subj)
        commits_html += (
            f'<div class="row">'
            f'<span class="sha">{h(sha)}</span>{type_html}'
            f'<span class="subj">{subj_html}<div class="rel">{h(rel)}</div></span>'
            f'</div>'
        )
    commits_html += '</div>'

    # Dispatch stream (use ledger.recent)
    if ledger.recent:
        rows = "".join(
            f"<tr><td>{h(d['dispatched_at'])}</td><td>{h(d['pi'])}</td>"
            f"<td>{h(d.get('feature_dir',''))}</td><td>{h(d['task_id'])}</td>"
            f"<td>{h(d['agent_id'])}</td><td>{h(d.get('outcome') or 'pending')}</td></tr>"
            for d in ledger.recent
        )
        dispatch_html = (
            '<table class="dense">'
            '<thead><tr><th>When</th><th>PI</th><th>Feature</th><th>Task</th><th>Agent</th><th>Outcome</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
        )
    else:
        dispatch_html = (
            '<div class="empty-state"><div class="icon">// // //</div>'
            '<div>Dispatch stream is empty.</div>'
            '<div class="hint">The fleet has not yet been dispatched through the ledger. Record one with:<br>'
            '<code>python spec-driven-development/ledger/ledger_cli.py record-dispatch ...</code></div></div>'
        )

    action_title, why, link = next_action
    cta_html = f'<a class="cta" href="{h(link)}" target="_blank">Open &rarr; {h(link)}</a>' if link else ''

    refresh_meta = '<meta http-equiv="refresh" content="20">' if live else ''
    live_badge = (f'<span class="meta">live :: rebuilds on every request :: auto-refresh 20s</span>'
                  if live else '<span class="meta">static :: rerun state_builder.py to refresh</span>')
    refresh_btn = (
        '<a class="btn-refresh" href="/" title="Reload now">&#x21bb; refresh</a>' if live else
        '<a class="btn-refresh" href="state.html" title="Reload the static file">&#x21bb; reload</a>'
    )
    pi_label_html = (f'<span class="h-pi">{h(pi.name)}</span><span class="h-title">{h(pi.title)}</span>' if pi else '')

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{refresh_meta}
<title>Bridge -- {h(pi.name if pi else 'no PI')} -- {h(generated_at)}</title>
<style>{HTML_CSS}</style>
</head><body>
<header class="bridge-header">
  <div class="brand"><span class="h-bridge">Bridge</span>{pi_label_html}</div>
  <div class="header-actions">
    <span class="meta">generated {h(generated_at)}</span>
    {live_badge}
    {refresh_btn}
  </div>
</header>
<div class="layout">
  <main class="main">
    <div class="next-action">
      <div class="label">Recommended next action</div>
      <div class="title">{h(action_title)}</div>
      <div class="why">{h(why)}</div>
      {cta_html}
    </div>
    {pi_block_html}
    <section class="panel"><h2>Lifecycle Kanban</h2>{kanban_html}</section>
    <section class="panel"><h2>Dispatch Stream (fleet.db)</h2>{dispatch_html}</section>
  </main>
  <aside class="side">
    <section class="panel"><h2>Fleet Roster</h2>{fleet_html}</section>
    <section class="panel"><h2>Recent Commits</h2>{commits_html}</section>
  </aside>
</div>
<footer>Auto-generated by cli/state_builder.py &middot; {("live mode @ :" + str(port)) if (live and port) else "file mode"} &middot; SDD-002 + state-dashboard v0.2</footer>
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
        live=live_html, port=port,
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
