#!/usr/bin/env python3
"""State builder -- derive a visual + textual executive dashboard from artifacts.

Reads:
    - constitution/roadmap.md         (current PI + commitments)
    - backlog/BACKLOG.md              (P1..P4 items with RICE)
    - specs/*/spec.md + plan.md + tasks.md + validation.md + RETRO.md
                                      (feature stage detection)
    - sprints/PI-{N}/lessons.md       (deferred / shipped lessons)
    - roster/agents.json              (fleet roster)
    - ledger/fleet.db (optional)      (dispatch + decision history)
    - git log (optional)              (recent activity)

Writes:
    - exec/state.md                   (refreshed textual briefing)
    - exec/state.html                 (single self-contained visual dashboard)

Style: pure Python stdlib (LESSON-001). No third-party dependencies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------- #
# Paths
# ---------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parents[1]          # spec-driven-development/
REPO_ROOT = ROOT.parent                              # repository root

ROADMAP = ROOT / "constitution" / "roadmap.md"
BACKLOG = ROOT / "backlog" / "BACKLOG.md"
SPECS_DIR = ROOT / "specs"
SPRINTS_DIR = ROOT / "sprints"
ROSTER = ROOT / "roster" / "agents.json"
LEDGER_DB = ROOT / "ledger" / "fleet.db"

EXEC_DIR = ROOT / "exec"
STATE_MD = EXEC_DIR / "state.md"
STATE_HTML = EXEC_DIR / "state.html"

# ---------------------------------------------------------------------------- #
# Stage detection
# ---------------------------------------------------------------------------- #

# Canonical SDD lifecycle stages, left-to-right.
STAGES = ["IDEA", "BACKLOG", "CLARIFY", "SPEC", "PLAN", "TASKS", "IMPLEMENT", "REVIEW", "DONE"]


@dataclass
class Feature:
    feature_dir: Path
    name: str
    stage: str
    created: str
    notes: str = ""


def detect_stage(feature_dir: Path) -> tuple[str, str]:
    """Return (stage, notes) for a feature directory based on which artifacts exist."""
    has_design = (feature_dir / "DESIGN.md").is_file()
    has_spec = (feature_dir / "spec.md").is_file()
    has_plan = (feature_dir / "plan.md").is_file()
    has_tasks = (feature_dir / "tasks.md").is_file()
    has_validation = (feature_dir / "validation.md").is_file()
    has_retro = (feature_dir / "RETRO.md").is_file()

    # Detect DONE: validation fully checked + RETRO present.
    if has_retro and has_validation:
        checks = (feature_dir / "validation.md").read_text(encoding="utf-8", errors="replace")
        unchecked = re.findall(r"^\s*- \[ \]", checks, re.MULTILINE)
        if not unchecked:
            return "DONE", "validation 100%, RETRO present"

    if has_validation:
        checks_text = (feature_dir / "validation.md").read_text(encoding="utf-8", errors="replace")
        unchecked = re.findall(r"^\s*- \[ \]", checks_text, re.MULTILINE)
        checked = re.findall(r"^\s*- \[x\]", checks_text, re.MULTILINE | re.IGNORECASE)
        total = len(unchecked) + len(checked)
        if total > 0:
            pct = round(len(checked) * 100 / total)
            stage = "REVIEW" if pct >= 80 else "IMPLEMENT"
            return stage, f"validation {pct}% ({len(checked)}/{total})"

    if has_tasks:
        return "TASKS", "tasks.md present"
    if has_plan:
        return "PLAN", "plan.md present"
    if has_spec:
        # Look at spec status frontmatter as override
        text = (feature_dir / "spec.md").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^status:\s*(.+?)$", text, re.MULTILINE)
        if m and "implement" in m.group(1).lower():
            return "IMPLEMENT", f"spec status: {m.group(1).strip()}"
        return "SPEC", "spec.md present"
    if has_design:
        return "CLARIFY", "DESIGN.md only (pre-spec design exploration)"
    return "BACKLOG", "directory exists, no artifacts yet"


def load_features() -> list[Feature]:
    if not SPECS_DIR.is_dir():
        return []
    features: list[Feature] = []
    for d in sorted(SPECS_DIR.iterdir()):
        if not d.is_dir():
            continue
        stage, notes = detect_stage(d)
        # Created date from the directory name prefix if it parses
        name = d.name
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", name)
        created = m.group(1) if m else ""
        display_name = m.group(2) if m else name
        features.append(Feature(feature_dir=d, name=display_name, stage=stage, created=created, notes=notes))
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
    def done(self) -> int:
        return sum(1 for c, _ in self.checkboxes if c)

    @property
    def total(self) -> int:
        return len(self.checkboxes)

    @property
    def pct(self) -> int:
        return round(self.done * 100 / self.total) if self.total else 0


def load_pis() -> list[PIBlock]:
    """Parse PI blocks from roadmap.md."""
    if not ROADMAP.is_file():
        return []
    text = ROADMAP.read_text(encoding="utf-8")
    blocks: list[PIBlock] = []
    # Match headings like "## PI-2: Fleet Maturity and CLI"
    header_re = re.compile(r"^##\s+(PI-\d+)\s*[:\-]\s*(.+?)\s*$", re.MULTILINE)
    matches = list(header_re.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1)
        title = m.group(2).strip()
        is_current = "(current)" in title.lower()
        title_clean = re.sub(r"\s*\(current\)\s*$", "", title, flags=re.IGNORECASE).strip()
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


def current_pi(pis: list[PIBlock]) -> PIBlock | None:
    for p in pis:
        if p.is_current:
            return p
    # Fallback: first PI with any unchecked item
    for p in pis:
        if any(not c for c, _ in p.checkboxes):
            return p
    return pis[0] if pis else None


# ---------------------------------------------------------------------------- #
# Backlog parsing
# ---------------------------------------------------------------------------- #

@dataclass
class BacklogItem:
    pid: str
    title: str
    priority: str
    rice: str
    status: str


def load_backlog() -> list[BacklogItem]:
    if not BACKLOG.is_file():
        return []
    text = BACKLOG.read_text(encoding="utf-8")
    items: list[BacklogItem] = []
    # Match table rows: | ID | Title | P1 | ... | RICE | ... | Status |
    row_re = re.compile(r"^\|\s*([A-Z]{2,}-\d{2,3})\s*\|\s*(.+?)\s*\|\s*(P[1-4])\s*\|.+?\|\s*([\d\.]+)\s*\|.+?\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)
    for m in row_re.finditer(text):
        items.append(BacklogItem(pid=m.group(1), title=m.group(2), priority=m.group(3), rice=m.group(4), status=m.group(5).strip()))
    return items


# ---------------------------------------------------------------------------- #
# Roster
# ---------------------------------------------------------------------------- #

def load_roster() -> dict:
    if not ROSTER.is_file():
        return {"principals": 0, "generic": 0, "specialist": 0, "by_kind": {}}
    agents = json.loads(ROSTER.read_text(encoding="utf-8"))
    by_kind: dict[str, int] = {}
    for a in agents:
        k = a.get("kind", "unknown")
        by_kind[k] = by_kind.get(k, 0) + 1
    return {
        "principals": by_kind.get("principal", 0),
        "generic": by_kind.get("generic", 0),
        "specialist": by_kind.get("specialist", 0),
        "total": len(agents),
        "by_kind": by_kind,
    }


# ---------------------------------------------------------------------------- #
# Ledger
# ---------------------------------------------------------------------------- #

def load_dispatches(limit: int = 10) -> list[dict]:
    if not LEDGER_DB.is_file():
        return []
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT dispatched_at, pi, sprint, feature_dir, task_id, task_title, agent_id, outcome "
                "FROM dispatches ORDER BY dispatched_at DESC LIMIT ?",
                [limit],
            ).fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error:
        return []


# ---------------------------------------------------------------------------- #
# Git log
# ---------------------------------------------------------------------------- #

def load_recent_commits(limit: int = 10) -> list[tuple[str, str]]:
    try:
        out = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h\x1f%s"],
            capture_output=True, text=True, check=True, cwd=str(REPO_ROOT),
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    commits = []
    for line in out.splitlines():
        if "\x1f" in line:
            sha, subj = line.split("\x1f", 1)
            commits.append((sha, subj))
    return commits


# ---------------------------------------------------------------------------- #
# Next-action heuristic
# ---------------------------------------------------------------------------- #

def derive_next_action(pi: PIBlock | None, features: list[Feature]) -> tuple[str, str]:
    """Return (action_title, why)."""
    # 1. Any feature in IMPLEMENT? finish it first.
    in_flight = [f for f in features if f.stage == "IMPLEMENT"]
    if in_flight:
        f = in_flight[0]
        return (
            f"Finish implementation of '{f.name}'",
            f"It is the only feature in IMPLEMENT stage ({f.notes}). Quality gate: do not start new work while a feature is in flight.",
        )
    # 2. Any feature in REVIEW? close it.
    in_review = [f for f in features if f.stage == "REVIEW"]
    if in_review:
        f = in_review[0]
        return (
            f"Close out '{f.name}' (currently in REVIEW)",
            f"Two-stage review then mark DONE. {f.notes}",
        )
    # 3. Otherwise pick first undone PI commitment.
    if pi:
        for done, label in pi.checkboxes:
            if not done:
                return (
                    f"Start: '{label}'",
                    f"Highest-priority unstarted commitment in {pi.name}: {pi.title}. Run /clarify to start the lifecycle.",
                )
    return ("Open PI-2 planning or pick from backlog", "No active in-flight work and no obvious next commitment.")


# ---------------------------------------------------------------------------- #
# Markdown renderer (state.md)
# ---------------------------------------------------------------------------- #

def render_markdown(*, pi: PIBlock | None, features: list[Feature], roster: dict,
                    commits: list[tuple[str, str]], dispatches: list[dict],
                    next_action: tuple[str, str], generated_at: str) -> str:
    lines: list[str] = []
    lines.append("# Executive State")
    lines.append("")
    lines.append(f"Generated date: {generated_at}")
    lines.append(f"Current PI: {pi.name + ' (' + pi.title + ')' if pi else 'none active'}")
    lines.append("Active sprint: Symbolic -- AI fleet compresses wall-clock time")
    if pi:
        lines.append(f"PI progress: {pi.done}/{pi.total} commitments complete ({pi.pct}%)")
    lines.append("")
    lines.append("## Next Action (recommended)")
    lines.append("")
    lines.append(f"**{next_action[0]}**")
    lines.append("")
    lines.append(next_action[1])
    lines.append("")
    lines.append("## Spec Pipeline")
    lines.append("")
    lines.append("| Feature | Stage | Notes |")
    lines.append("|---------|-------|-------|")
    for f in features:
        lines.append(f"| {f.name} | {f.stage} | {f.notes} |")
    lines.append("")
    lines.append("## Fleet")
    lines.append("")
    lines.append(f"- Principals: {roster['principals']}")
    lines.append(f"- Generic workers: {roster['generic']}")
    lines.append(f"- Specialists: {roster['specialist']}")
    lines.append(f"- Total agents: {roster['total']}")
    lines.append("")
    lines.append("## Recent Commits")
    lines.append("")
    for sha, subj in commits:
        lines.append(f"- `{sha}` {subj}")
    lines.append("")
    lines.append("## Recent Dispatches (fleet.db)")
    lines.append("")
    if not dispatches:
        lines.append("_No dispatches recorded yet._")
    else:
        lines.append("| When | PI | Feature | Task | Agent | Outcome |")
        lines.append("|------|----|---------|------|-------|---------|")
        for d in dispatches:
            lines.append(f"| {d['dispatched_at']} | {d['pi']} | {d.get('feature_dir','')} | {d['task_id']} | {d['agent_id']} | {d.get('outcome') or 'pending'} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_This file is auto-generated by `cli/state_builder.py`. To refresh: `python spec-driven-development/cli/state_builder.py`._")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------- #
# HTML renderer (state.html) -- Bridge design language
# ---------------------------------------------------------------------------- #

HTML_CSS = """
:root {
  --bg-carbon:       #0a0a0a;
  --bg-graphite:     #141413;
  --bg-graphite-2:   #1c1b18;
  --ink-paper:       #e8e4d8;
  --ink-paper-dim:   #a8a497;
  --ink-paper-faint: #6e6a5e;
  --accent-oxblood:  #ce2029;
  --accent-oxblood2: #a01820;
  --signal-amber:    #d29a3b;
  --signal-jade:     #6fa37a;
  --rule-line:       #2a2925;
  --focus-ring:      #e8e4d8;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg-carbon);
  color: var(--ink-paper);
  font-family: ui-monospace, "Berkeley Mono", "JetBrains Mono", Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.45;
}
a { color: var(--signal-amber); text-decoration: none; }
a:hover { text-decoration: underline; }
header.bridge-header {
  border-bottom: 2px solid var(--accent-oxblood);
  padding: 14px 22px 12px;
  display: flex; align-items: baseline; justify-content: space-between; gap: 18px; flex-wrap: wrap;
}
header.bridge-header h1 {
  margin: 0; font-size: 14px; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700;
}
header.bridge-header .meta {
  color: var(--ink-paper-dim); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
}
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 0;
  min-height: calc(100vh - 60px);
}
.main { padding: 20px 22px; min-width: 0; }
.side { padding: 20px 22px; border-left: 1px solid var(--rule-line); background: var(--bg-graphite); min-width: 0; }
section.panel { margin-bottom: 26px; }
section.panel h2 {
  margin: 0 0 10px;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink-paper-dim);
  border-bottom: 1px solid var(--rule-line);
  padding-bottom: 6px;
}
.next-action {
  background: var(--bg-graphite);
  border-left: 4px solid var(--accent-oxblood);
  padding: 14px 18px;
  margin-bottom: 24px;
}
.next-action .label {
  font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--accent-oxblood); margin-bottom: 6px;
}
.next-action .title { font-size: 17px; font-weight: 600; color: var(--ink-paper); margin-bottom: 4px; }
.next-action .why { color: var(--ink-paper-dim); font-size: 12px; }
.progress {
  margin-bottom: 18px;
}
.progress .bar {
  position: relative; height: 22px;
  background: var(--bg-graphite-2);
  border: 1px solid var(--rule-line);
  overflow: hidden;
}
.progress .fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  background: var(--signal-jade);
  transition: width 240ms ease;
}
.progress .label-row {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: 11px; color: var(--ink-paper-dim); margin-bottom: 4px;
  letter-spacing: 0.08em; text-transform: uppercase;
}
.progress .pct { color: var(--ink-paper); font-weight: 700; font-size: 14px; }
.commitments { list-style: none; padding: 0; margin: 10px 0 0; font-size: 12px; }
.commitments li {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 4px 0; border-bottom: 1px dashed var(--rule-line);
  color: var(--ink-paper-dim);
}
.commitments li.done { color: var(--signal-jade); }
.commitments li .mark {
  font-family: inherit; color: var(--ink-paper-faint);
  width: 18px; flex-shrink: 0;
}
.commitments li.done .mark { color: var(--signal-jade); }
.kanban {
  display: grid;
  grid-template-columns: repeat(9, minmax(110px, 1fr));
  gap: 6px;
  overflow-x: auto;
}
.kanban .col {
  background: var(--bg-graphite);
  border: 1px solid var(--rule-line);
  padding: 8px 8px 10px;
  min-height: 110px;
}
.kanban .col h3 {
  margin: 0 0 8px; font-size: 9px; letter-spacing: 0.18em;
  color: var(--ink-paper-dim); text-transform: uppercase;
  border-bottom: 1px solid var(--rule-line); padding-bottom: 4px;
}
.kanban .card {
  background: var(--bg-graphite-2);
  border-left: 3px solid var(--ink-paper-faint);
  padding: 6px 8px;
  margin-bottom: 6px;
  font-size: 11px;
  word-break: break-word;
}
.kanban .card.done   { border-left-color: var(--signal-jade); }
.kanban .card.review { border-left-color: var(--signal-amber); }
.kanban .card.impl   { border-left-color: var(--accent-oxblood); }
.kanban .card .name { color: var(--ink-paper); font-weight: 600; margin-bottom: 2px; }
.kanban .card .meta { color: var(--ink-paper-faint); font-size: 10px; }
table.dense {
  width: 100%; border-collapse: collapse; font-size: 11px;
}
table.dense th, table.dense td {
  padding: 5px 8px; text-align: left;
  border-bottom: 1px solid var(--rule-line);
  vertical-align: top;
}
table.dense th {
  font-weight: 600; color: var(--ink-paper-dim);
  font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
}
.fleet-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 6px; }
.fleet-stats .stat {
  background: var(--bg-graphite-2);
  border: 1px solid var(--rule-line);
  padding: 10px 12px;
}
.fleet-stats .stat .n {
  font-size: 22px; color: var(--ink-paper); font-weight: 700; line-height: 1;
}
.fleet-stats .stat .l {
  font-size: 9px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-paper-dim); margin-top: 4px;
}
.activity { font-size: 11px; }
.activity .row { padding: 5px 0; border-bottom: 1px dashed var(--rule-line); display: flex; gap: 10px; }
.activity .sha { color: var(--signal-amber); flex-shrink: 0; }
.activity .subj { color: var(--ink-paper-dim); }
footer { padding: 14px 22px; border-top: 1px solid var(--rule-line); color: var(--ink-paper-faint); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; }
.empty { color: var(--ink-paper-faint); font-style: italic; font-size: 11px; }
@media (max-width: 1100px) {
  .layout { grid-template-columns: 1fr; }
  .side { border-left: none; border-top: 1px solid var(--rule-line); }
  .kanban { grid-template-columns: repeat(3, minmax(140px, 1fr)); }
}
"""


def h(s) -> str:
    return html.escape(str(s) if s is not None else "")


def stage_class(stage: str) -> str:
    if stage == "DONE": return "done"
    if stage == "REVIEW": return "review"
    if stage in ("IMPLEMENT", "TASKS"): return "impl"
    return ""


def render_html(*, pi: PIBlock | None, features: list[Feature], roster: dict,
                commits: list[tuple[str, str]], dispatches: list[dict],
                next_action: tuple[str, str], generated_at: str,
                all_pis: list[PIBlock]) -> str:
    # Group features by stage
    by_stage: dict[str, list[Feature]] = {s: [] for s in STAGES}
    for f in features:
        by_stage.setdefault(f.stage, []).append(f)

    pi_label = f"{pi.name} -- {h(pi.title)}" if pi else "no PI active"
    pi_progress_block = ""
    if pi:
        pi_progress_block = f"""
        <section class="panel">
          <h2>{h(pi.name)} Progress</h2>
          <div class="progress">
            <div class="label-row">
              <span>{h(pi.title)}</span>
              <span class="pct">{pi.done} / {pi.total} &nbsp; ({pi.pct}%)</span>
            </div>
            <div class="bar"><div class="fill" style="width:{pi.pct}%"></div></div>
          </div>
          <ul class="commitments">
            {"".join(f'<li class="{"done" if c else ""}"><span class="mark">{"[x]" if c else "[ ]"}</span><span>{h(label)}</span></li>' for c, label in pi.checkboxes)}
          </ul>
        </section>
        """

    kanban_html = '<div class="kanban">'
    for s in STAGES:
        cards = by_stage.get(s, [])
        kanban_html += f'<div class="col"><h3>{h(s)}</h3>'
        if not cards:
            kanban_html += '<div class="empty">—</div>'
        for f in cards:
            kanban_html += (
                f'<div class="card {stage_class(s)}">'
                f'<div class="name">{h(f.name)}</div>'
                f'<div class="meta">{h(f.created)} &middot; {h(f.notes)}</div>'
                f'</div>'
            )
        kanban_html += '</div>'
    kanban_html += '</div>'

    fleet_stats = f"""
    <div class="fleet-stats">
      <div class="stat"><div class="n">{roster['principals']}</div><div class="l">Principals</div></div>
      <div class="stat"><div class="n">{roster['generic']}</div><div class="l">Generic</div></div>
      <div class="stat"><div class="n">{roster['specialist']}</div><div class="l">Specialist</div></div>
      <div class="stat"><div class="n">{roster['total']}</div><div class="l">Total</div></div>
    </div>
    """

    commits_html = '<div class="activity">'
    if not commits:
        commits_html += '<div class="empty">No commits found.</div>'
    for sha, subj in commits:
        commits_html += f'<div class="row"><span class="sha">{h(sha)}</span><span class="subj">{h(subj)}</span></div>'
    commits_html += '</div>'

    if dispatches:
        rows = "".join(
            f"<tr><td>{h(d['dispatched_at'])}</td><td>{h(d['pi'])}</td>"
            f"<td>{h(d.get('feature_dir',''))}</td><td>{h(d['task_id'])}</td>"
            f"<td>{h(d['agent_id'])}</td><td>{h(d.get('outcome') or 'pending')}</td></tr>"
            for d in dispatches
        )
        dispatch_html = f"""
        <table class="dense">
          <thead><tr><th>When</th><th>PI</th><th>Feature</th><th>Task</th><th>Agent</th><th>Outcome</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """
    else:
        dispatch_html = '<div class="empty">Dispatch stream is empty. The fleet has not been formally dispatched through the ledger yet.</div>'

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bridge -- Executive State -- {h(generated_at)}</title>
<style>{HTML_CSS}</style>
</head><body>
<header class="bridge-header">
  <h1>Bridge &nbsp;//&nbsp; {pi_label}</h1>
  <div class="meta">Generated {h(generated_at)} &nbsp;//&nbsp; symbolic sprint</div>
</header>
<div class="layout">
  <main class="main">
    <div class="next-action">
      <div class="label">Recommended next action</div>
      <div class="title">{h(next_action[0])}</div>
      <div class="why">{h(next_action[1])}</div>
    </div>

    {pi_progress_block}

    <section class="panel">
      <h2>Lifecycle Kanban</h2>
      {kanban_html}
    </section>

    <section class="panel">
      <h2>Dispatch Stream (fleet.db)</h2>
      {dispatch_html}
    </section>
  </main>
  <aside class="side">
    <section class="panel">
      <h2>Fleet Roster</h2>
      {fleet_stats}
    </section>
    <section class="panel">
      <h2>Recent Commits</h2>
      {commits_html}
    </section>
  </aside>
</div>
<footer>Auto-generated by cli/state_builder.py &nbsp;//&nbsp; SDD-001 v0.1 &nbsp;//&nbsp; refresh: python spec-driven-development/cli/state_builder.py</footer>
</body></html>
"""


# ---------------------------------------------------------------------------- #
# Build orchestration
# ---------------------------------------------------------------------------- #

def build(write: bool = True) -> dict:
    """Build state outputs. Returns a dict of (path, char_count) actually written."""
    pis = load_pis()
    pi = current_pi(pis)
    features = load_features()
    roster = load_roster()
    dispatches = load_dispatches()
    commits = load_recent_commits()
    next_action = derive_next_action(pi, features)
    generated_at = dt.date.today().isoformat()

    md = render_markdown(
        pi=pi, features=features, roster=roster, commits=commits,
        dispatches=dispatches, next_action=next_action, generated_at=generated_at,
    )
    htm = render_html(
        pi=pi, features=features, roster=roster, commits=commits,
        dispatches=dispatches, next_action=next_action, generated_at=generated_at,
        all_pis=pis,
    )

    result = {"markdown_chars": len(md), "html_chars": len(htm), "features": len(features),
              "commits": len(commits), "dispatches": len(dispatches),
              "pi": pi.name if pi else None}
    if write:
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        STATE_MD.write_text(md, encoding="utf-8")
        STATE_HTML.write_text(htm, encoding="utf-8")
        result["wrote"] = [str(STATE_MD), str(STATE_HTML)]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild exec/state.md and exec/state.html from artifacts.")
    parser.add_argument("--no-write", action="store_true", help="Compute but do not write outputs (dry run).")
    parser.add_argument("--json", action="store_true", help="Print a JSON summary instead of human text.")
    args = parser.parse_args(argv)

    info = build(write=not args.no_write)
    if args.json:
        print(json.dumps(info, indent=2, default=str))
    else:
        print(f"PI: {info['pi']}")
        print(f"Features: {info['features']}")
        print(f"Commits scanned: {info['commits']}")
        print(f"Dispatches in ledger: {info['dispatches']}")
        if "wrote" in info:
            for p in info["wrote"]:
                print(f"Wrote: {p}")
        else:
            print("Dry run -- nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
