#!/usr/bin/env python3
"""State-builder data layer (SDD-048 C-1 E4 -- god-module split).

Pure data/loader/derive surface extracted verbatim from ``state_builder.py``
to right-size the historically oversized facade module. This module owns the
feature/PI/backlog/roster/ledger loaders, their dataclasses, the next-action
derivation heuristics, and the regexes those functions depend on.

Design notes (boundary plumbing only -- NO behaviour change):

  * This is a true LEAF module. None of these functions raise the
    facade-owned ``StateBuilderError`` nor call any of the Article X LOCKED
    loaders (``load_sprint_table``/``load_sprint_goal``/
    ``detect_current_sprint``/``load_decisions``), so no ``_facade()`` lazy
    bridge is required (cf. work_index.py / dashboard_server.py).
  * The facade (``state_builder.py``) re-exports every public name defined
    here so the LOCKED functions and the renderers continue to resolve these
    symbols through the facade module namespace at call time.
  * Stdlib-only (Article V / LESSON-001): no third-party imports.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# In-tree sibling bootstrap (ADR-012): make the cli/ directory importable so a
# bare ``from state_builder_data import ...`` resolves whether the package is
# imported as ``cli.state_builder_data`` or as a top-level module.
CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

# SDD-050 (Dashboard truth): share the DONE-completeness definition with the
# B-2 gate (done_check) so the dashboard and the gate never disagree on
# "is this dir DONE?". Dual-import (ADR-012) for package/bare import parity.
try:  # pragma: no cover - import shim
    from cli.done_check import (
        required_checked,
        required_unchecked,
        validation_complete,
        validation_files,
    )
except ImportError:  # pragma: no cover - import shim
    from done_check import (
        required_checked,
        required_unchecked,
        validation_complete,
        validation_files,
    )


def repo_root_for(sdd_root: Path) -> Path:
    return sdd_root.parent


# ---------------------------------------------------------------------------- #
# Feature parsing
# ---------------------------------------------------------------------------- #

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

    Order of precedence (SDD-002 AC4, reconciled by SDD-050 with the B-2 gate):
      1. REQUIRED-item completeness (shared ``done_check.validation_complete``)
         -> DONE, regardless of a stale Status line and WITHOUT requiring a
         per-dir RETRO.md. Only ``## Required Items`` count; optional items and
         split ``validation-*.md`` files are handled by the shared helper.
      2. Explicit ``Status:`` line in spec.md -> trusted, except a ``done``
         status with unchecked REQUIRED items is demoted to REVIEW (not truth).
      3. REQUIRED-item ratio -> infer IMPLEMENT/REVIEW (never DONE from a ratio).
      4. Artifact presence (tasks/plan/spec/design) -> coarse stage.
    """
    has_design = (feature_dir / "DESIGN.md").is_file()
    has_spec = (feature_dir / "spec.md").is_file()
    has_plan = (feature_dir / "plan.md").is_file()
    has_tasks = (feature_dir / "tasks.md").is_file()
    v_files = validation_files(feature_dir)
    has_validation = bool(v_files)
    has_retro = (feature_dir / "RETRO.md").is_file()

    status_line = ""
    if has_spec:
        text = (feature_dir / "spec.md").read_text(encoding="utf-8", errors="replace")
        m = _STATUS_RE.search(text)
        if m:
            status_line = m.group(1).strip()

    # 1. Evidence-first (SDD-050): all REQUIRED items checked == DONE, even if
    #    the Status line is stale and even with no RETRO.md. This is the shared
    #    truth used by the B-2 gate (done_check.validation_complete).
    if has_validation and validation_complete(feature_dir):
        note = "validation required-complete"
        if has_retro:
            note += ", RETRO present"
        return "DONE", status_line or "done", note

    explicit = _normalize_status_to_stage(status_line)
    if explicit:
        if explicit == "DONE":
            if not has_validation:
                # No validation file to contradict the claim -> trust the status.
                note = "Status: done (no validation file)"
                if has_retro:
                    note += ", RETRO present"
                return "DONE", status_line, note
            # Validation present but REQUIRED items still open -> not truthfully done.
            return "REVIEW", status_line, "Status: done but validation required items unchecked"
        # For all other explicit stages, trust the spec line.
        return explicit, status_line, f"Status: {status_line}"

    # 2. REQUIRED-item ratio (known incomplete here -> never DONE).
    if has_validation:
        unchecked = 0
        checked = 0
        for f in v_files:
            unchecked += len(required_unchecked(f))
            checked += len(required_checked(f))
        total = unchecked + checked
        if total > 0:
            pct = round(checked * 100 / total)
            stage = "REVIEW" if pct >= 80 else "IMPLEMENT"
            return stage, status_line, f"validation required {pct}% ({checked}/{total})"

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
    is_closed: bool = False

    @property
    def done(self) -> int:    return sum(1 for c, _ in self.checkboxes if c)
    @property
    def total(self) -> int:   return len(self.checkboxes)
    @property
    def pct(self) -> int:
        # A closed PI is complete by definition: the dashboard shows 100%
        # regardless of any stray unchecked roadmap boxes.
        if self.is_closed:
            return 100
        return round(self.done * 100 / self.total) if self.total else 0


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
        low = title.lower()
        # A PI header may read "(current, closed YYYY-MM-DD)". "closed" wins:
        # a closed PI is never treated as the live/current PI.
        is_closed = "closed" in low
        is_current = ("(current" in low) and not is_closed
        title_clean = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        checkboxes = []
        for line in body.splitlines():
            cm = re.match(r"\s*-\s+\[([ xX])\]\s+(.+?)\s*$", line)
            if cm:
                checkboxes.append((cm.group(1).lower() == "x", cm.group(2)))
        blocks.append(PIBlock(name=name, title=title_clean, is_current=is_current, checkboxes=checkboxes, is_closed=is_closed))
    return blocks


def _pi_number(pi: PIBlock) -> int:
    """Trailing integer from a PI name/title, for newest-PI selection."""
    m = re.search(r"(\d+)", pi.name or "") or re.search(r"(\d+)", pi.title or "")
    return int(m.group(1)) if m else -1


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
        if not p.is_closed and any(not c for c, _ in p.checkboxes):
            return p
    if not pis:
        return None
    # Every PI is closed (or fully checked): fall back to the NEWEST PI by
    # number, not the oldest (pis[0]), so the header never shows a stale PI-1.
    open_pis = [p for p in pis if not p.is_closed]
    return max(open_pis or pis, key=_pi_number)


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


_ACTIVE_SPRINT_WORD_RE = re.compile(
    r"\b(?:ACTIVE|CURRENT|IN[- ]PROGRESS)\b", re.IGNORECASE
)
_NEGATED_ACTIVE_RE = re.compile(
    r"\b(?:NOT|NO)\s+(?:ACTIVE|CURRENT|IN[- ]PROGRESS)\b", re.IGNORECASE
)
_TERMINAL_SPRINT_WORD_RE = re.compile(
    r"\b(?:CLOSED|DONE|PROPOSED)\b", re.IGNORECASE
)
_MALFORMED_SPRINT_TOKEN_RE = re.compile(
    r"\bSprint\s+(?:\d+[.\-][\w.-]+|\d+[A-Za-z]\w*|[A-Za-z]\w*)\b",
    re.IGNORECASE,
)
_ACTIVE_NUMBER_RE = re.compile(
    r"\b(?P<overall>overall\s+)?Sprint\s+(?P<num>\d+)(?![\w.])"
    r"(?:(?!\bSprint\b).){0,80}?"
    r"\b(?P<status>ACTIVE|CURRENT|IN[- ]PROGRESS)\b",
    re.IGNORECASE,
)


def _has_malformed_sprint_token(text: str) -> bool:
    """True when a Sprint marker's numeric token is not a whole integer."""
    return _MALFORMED_SPRINT_TOKEN_RE.search(text) is not None


def _active_numbers(text: str) -> tuple[set[int], set[int]] | None:
    """Return active ``(overall, local)`` numbers, or None for invalid text."""
    if _has_malformed_sprint_token(text):
        return None
    overall: set[int] = set()
    local: set[int] = set()
    for clause in re.split(r"[;|]", text):
        has_active = _ACTIVE_SPRINT_WORD_RE.search(clause) is not None
        if not has_active:
            continue
        if (_NEGATED_ACTIVE_RE.search(clause)
                or _TERMINAL_SPRINT_WORD_RE.search(clause)):
            return None
        for match in _ACTIVE_NUMBER_RE.finditer(clause):
            target = overall if match.group("overall") else local
            target.add(int(match.group("num")))
    return overall, local


def load_active_sprint_from_current_pi(sdd_root: Path) -> list[dict]:
    """Load the one explicitly active sprint from the newest ACTIVE PI file.

    The highest numeric ``sprints/PI-*/CURRENT_PI.md`` with both active
    frontmatter and a body PI status beginning ACTIVE is authoritative. Any
    unreadable, malformed, absent, or conflicting sprint truth returns ``[]``.
    """
    sprints_dir = Path(sdd_root) / "sprints"
    if not sprints_dir.is_dir():
        return []

    active_pis: list[tuple[int, Path, str]] = []
    for path in sprints_dir.glob("PI-*/CURRENT_PI.md"):
        match = re.fullmatch(r"PI-(\d+)", path.parent.name)
        if not match:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []
        fm_match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
        if not fm_match or not re.search(
            r"^status\s*:\s*active\s*$", fm_match.group(1), re.IGNORECASE | re.MULTILINE
        ):
            continue
        body = text[fm_match.end():]
        status_match = re.search(
            r"^\s*-?\s*Status\s*:\s*(.+?)\s*$", body, re.IGNORECASE | re.MULTILINE
        )
        if not status_match:
            continue
        status_value = status_match.group(1).replace("**", "").strip()
        if not re.match(r"ACTIVE\b", status_value, re.IGNORECASE):
            continue
        active_pis.append((int(match.group(1)), path, body))

    if not active_pis:
        return []
    _, path, body = max(active_pis, key=lambda item: item[0])

    status_line = next(
        (line for line in body.splitlines()
         if re.match(r"^\s*-?\s*Status\s*:", line, re.IGNORECASE)),
        "",
    )
    source_lines = [status_line]
    source_lines.extend(
        line for line in body.splitlines()
        if re.match(r"^\s*#{1,6}\s+", line)
        and re.search(
            r"\bSprint\b.*\b(?:ACTIVE|CURRENT|IN[- ]PROGRESS|CLOSED|DONE|PROPOSED)\b",
            line,
            re.IGNORECASE,
        )
    )

    candidates: list[tuple[int, str, bool]] = []
    for line in source_lines:
        parsed = _active_numbers(line)
        if parsed is None:
            return []
        overall, local = parsed
        candidates.extend((number, "", True) for number in overall)
        candidates.extend((number, "", False) for number in local)

    for line in body.splitlines():
        if not line.lstrip().startswith("|") or "sprint" not in line.lower():
            continue
        cells = [cell.strip().strip("*") for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        status_text = " ".join(cells[3:])
        if not _ACTIVE_SPRINT_WORD_RE.search(status_text):
            continue
        if (_NEGATED_ACTIVE_RE.search(status_text)
            or _TERMINAL_SPRINT_WORD_RE.search(status_text)):
            return []
        marker_text = " ".join(cells[:2])
        if _has_malformed_sprint_token(marker_text):
            return []
        local_match = re.search(
            r"\bPI-\d+\s+Sprint\s+(\d+)\b", cells[0], re.IGNORECASE
        )
        overall_match = re.search(r"\bSprint\s+(\d+)\b", cells[1], re.IGNORECASE)
        if not local_match and not overall_match:
            return []
        number = int(overall_match.group(1) if overall_match else local_match.group(1))
        candidates.append((number, cells[2], overall_match is not None))

    overall_candidates = [candidate for candidate in candidates if candidate[2]]
    selected = overall_candidates or candidates
    unique_numbers = {number for number, _, _ in selected}
    if len(unique_numbers) != 1:
        return []
    number = unique_numbers.pop()
    titles = {
        title for candidate_num, title, _ in selected
        if candidate_num == number and title
    }
    if len(titles) > 1:
        return []
    title = next(iter(titles), "")
    return [{
        "num": number,
        "title": title,
        "status": "ACTIVE",
        "path": str(path.relative_to(sdd_root)).replace("\\", "/"),
    }]


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
