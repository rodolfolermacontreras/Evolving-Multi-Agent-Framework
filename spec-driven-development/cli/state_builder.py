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
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
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

from backlog_reorder import (
    move as _reorder_move,
    ReorderError as _ReorderError,
    load_order as _reorder_load_order,
    load_backlog_entries as _reorder_load_entries,
)

# ---------------------------------------------------------------------------- #
# Data layer (SDD-048 C-1 E4 / T-048-05)
#
# The pure data-acquisition layer (artifact/roadmap/backlog/roster/ledger
# parsing + next-action derivation) was extracted to state_builder_data.py to
# right-size this facade. It is a true leaf (stdlib-only, no facade imports), so
# we re-export every moved name here -- early, before any facade code (locked
# loaders, render_markdown, render_html, build) resolves these globals at call
# time. In-tree sibling re-export per ADR-012.
# ---------------------------------------------------------------------------- #

from state_builder_data import (  # noqa: E402  -- in-tree sibling re-export (ADR-012)
    repo_root_for,
    Feature,
    _STATUS_RE,
    _normalize_status_to_stage,
    detect_stage,
    load_features,
    PIBlock,
    load_pis,
    current_pi,
    BacklogItem,
    _BACKLOG_ROW,
    load_backlog,
    load_roster,
    LedgerView,
    _group_dispatches,
    load_ledger,
    load_recent_commits,
    _SPRINT_LABEL_RE,
    _BACKLOG_ID_RE,
    _feature_relpath,
    _first_current_pi_sprint_anchor,
    _active_sprint_pi,
    _read_current_pi_title,
    resolve_display_pi,
    _backlog_ids_for_sprint,
    _feature_for_backlog_id,
    _unchecked_required_count,
    _git_recency_timestamp,
    _derive_current_sprint_focus,
    _derive_next_action_fallback,
    derive_next_action,
)

# ---------------------------------------------------------------------------- #
# E5 (SDD-048): HTML render + DOM-injection helpers extracted to
# state_builder_html.py. Re-exported here so the Article X-locked render_html,
# render_markdown and build resolve them as module globals at call time.
# In-tree sibling re-export per ADR-012; stdlib-only per ADR-023.
# ---------------------------------------------------------------------------- #

from state_builder_html import (  # noqa: E402  -- in-tree sibling re-export (ADR-012)
    COMMIT_TYPE_TONE,
    split_commit_type,
    h,
    _pulse,
    _weighted_progress,
    _next_what,
    active_user_gates,
    _agents_for_feature,
    _stage_short,
    _next_for,
    inject_user_gates_html,
    _SPRINT_STAGE_MAP,
    _sprint_stage,
    render_lifecycle_pipeline,
    resolve_docs_cards,
    render_docs_row,
    _feature_display_id,
    load_display_order,
    order_features_for_display,
    _LIFECYCLE_STYLE,
    inject_lifecycle_html,
    _BACKLOG_REORDER_STYLE,
    _BACKLOG_META_PID_RE,
    _backlog_reorder_meta,
    _render_backlog_buttons,
    inject_backlog_reorder_html,
    _DRAG_SCRIPT_BODY,
    _DRAG_SCRIPT_HASH,
    _DRAG_SCRIPT_CSP,
    _CSP_META_RE,
    inject_drag_html,
    _DISPATCHES_STYLE,
    _HEALTH_PILLS_STYLE,
    _group_dispatch_status_class,
    inject_dispatches_html,
    constitution_semver_status,
    skill_validity_status,
    ledger_reachability_status,
    stale_tracker_status,
    inject_health_pills_html,
    render_work_index,
)

# ---------------------------------------------------------------------------- #
# SDD root + path helpers
# ---------------------------------------------------------------------------- #

DEFAULT_SDD_ROOT = Path(__file__).resolve().parents[1]   # spec-driven-development/


class StateBuilderError(Exception):
    """Expected state-builder failure with a human-readable message."""


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
    # SDD-036: lifecycle pipeline + four-card docs row (static; reorder moved
    # to the dedicated Backlog section below).
    htm = inject_lifecycle_html(
        htm, features=features, sdd_root=sdd_root, current_sprint=current_sprint)
    # SDD-037 (F-28): Dispatches card then health-pills strip. Both are
    # read-only indicators consuming the SAME LedgerView (zero new sqlite
    # connections). Pills injected LAST so they render at the top as a header
    # strip; neither can alter build()'s exit.
    htm = inject_dispatches_html(htm, ledger=ledger, sdd_root=sdd_root)
    htm = inject_health_pills_html(htm, sdd_root=sdd_root, ledger=ledger)
    # SDD-041 (F-31 rebuild): the real Backlog reorder surface, keyed by the
    # canonical SDD-xxx ids the POST /reorder endpoint accepts. Injected before
    # inject_drag_html so its draggable rows arm the drag + CSP layer.
    htm = inject_backlog_reorder_html(htm, sdd_root=sdd_root)
    # SDD-041 (F-31): native drag-and-drop layer. Injected LAST so it post-
    # processes the fully assembled doc -- appends one hash-pinned <script> and
    # widens the CSP for exactly that script. No-op when no draggable rows.
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

# ---------------------------------------------------------------------------- #
# HTTP server surface -- extracted to dashboard_server.py (SDD-048 C-1 E2).
#
# served_html_with_refresh / DashboardHandler / _port_available / serve and the
# pure handle_reorder_request now live in the dashboard_server sibling. They are
# re-exported here so `from cli.state_builder import serve, DashboardHandler, ...`
# (and main()'s `serve` subcommand dispatch) keep resolving unchanged. The
# server resolves the facade surfaces it needs (build, _DRAG_SCRIPT_CSP) lazily,
# so this re-import is non-circular.
# ---------------------------------------------------------------------------- #
from dashboard_server import (  # noqa: E402  -- in-tree sibling re-export (ADR-012)
    handle_reorder_request,
    served_html_with_refresh,
    DashboardHandler,
    _port_available,
    serve,
)


# ---------------------------------------------------------------------------- #
# build-index -- extracted to work_index.py (SDD-048 C-1 E3).
#
# build_index and its _discover_sprints / _detect_sprint_status /
# _query_ledger_for_pi / _render_sprint_table helpers (plus the _SPRINT_DIR_RE /
# _MARKER_BEGIN / _MARKER_END constants) now live in the work_index sibling.
# They are re-exported here so `from cli.state_builder import build_index` (and
# main()'s `build-index` subcommand dispatch) keep resolving unchanged. The
# module raises the facade-owned StateBuilderError lazily, so this re-import is
# non-circular.
# ---------------------------------------------------------------------------- #
from work_index import (  # noqa: E402  -- in-tree sibling re-export (ADR-012)
    _SPRINT_DIR_RE,
    _MARKER_BEGIN,
    _MARKER_END,
    _discover_sprints,
    _detect_sprint_status,
    _query_ledger_for_pi,
    _render_sprint_table,
    build_index,
)


# ---------------------------------------------------------------------------- #
# Doc-count rollup (SDD-FDC-001 / R3, R4)
#
# Extracted to doc_count.py under SDD-048 C-1 (T-048-02). Re-exported here so
# existing imports (`from cli.state_builder import build_doc_count`) keep
# resolving. The bodies are byte-identical to the pre-extraction originals.
# ---------------------------------------------------------------------------- #

from doc_count import (  # noqa: E402  -- in-tree sibling re-export (ADR-012)
    _iter_in_scope_artifacts,
    _resolve_sprint_id,
    build_doc_count,
    build_doc_count_by_sprint,
    render_count_table,
    cmd_count,
)


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
