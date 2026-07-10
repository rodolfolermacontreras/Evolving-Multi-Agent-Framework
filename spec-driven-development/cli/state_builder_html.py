"""SDD-048 C-1 E5 (T-048-06): HTML rendering + DOM-injection helpers.

Extracted verbatim from state_builder.py to right-size the facade. Owns the
post-render HTML fragment builders and injection passes that run *after* the
Article X-locked render_html (which stays in state_builder.py). Near-leaf:
imports stdlib, the pure data layer (state_builder_data) and the shared
frontmatter contract (schema_lint). Two facade-owned rendering constants
(STAGES, STAGE_WEIGHT) are resolved lazily via _facade() to avoid an import
cycle. The facade re-exports every moved name early so locked loaders,
render_markdown, render_html and build resolve them as module globals at call
time. In-tree sibling per ADR-012; stdlib-only per ADR-023 / Article V.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import html
import json
import re
import sys
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from state_builder_data import (  # noqa: E402  -- in-tree sibling import (ADR-012)
    BacklogItem,
    Feature,
    LedgerView,
    PIBlock,
    load_backlog,
    repo_root_for,
)
from schema_lint import (  # noqa: E402  -- shared contract / in-tree sibling (ADR-012)
    UserGate,
    Finding,
    parse_frontmatter,
    check_skill,
    _has_unquoted_version,
)
from backlog_reorder import (  # noqa: E402  -- in-tree sibling (ADR-012)
    load_order as _reorder_load_order,
    load_backlog_entries as _reorder_load_entries,
)


def _facade():
    """Lazily resolve the state_builder facade for facade-owned rendering
    constants (STAGES, STAGE_WEIGHT). Runtime-only; never called at import, so
    the facade <-> state_builder_html cycle never materializes."""
    import state_builder as _sb
    return _sb


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
    total = sum(_facade().STAGE_WEIGHT.get(f.stage, 0) for f in features)
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


_PI_PILLS_NAV_RE = re.compile(
    r'(<nav\b(?=[^>]*\bclass="[^"]*\bpi-pills\b[^"]*")[^>]*>).*?</nav>',
    re.DOTALL,
)


def inject_pi_pills_html(
    html_doc: str, *, pis: list[PIBlock], active_pi: PIBlock | None
) -> str:
    """Replace only the rendered PI pill nav with sorted live PI truth."""
    if active_pi is None or not _PI_PILLS_NAV_RE.search(html_doc):
        return html_doc

    numbered: dict[int, PIBlock] = {}
    for pi in pis:
        match = re.fullmatch(r"PI-(\d+)", pi.name)
        if match:
            numbered.setdefault(int(match.group(1)), pi)
    active_match = re.fullmatch(r"PI-(\d+)", active_pi.name)
    if not active_match or int(active_match.group(1)) not in numbered:
        return html_doc

    pills: list[str] = []
    active_number = int(active_match.group(1))
    for number in sorted(numbered):
        pi = numbered[number]
        current = number == active_number
        current_attrs = ' current"' if current else '"'
        aria = ' aria-current="page"' if current else ""
        title = f' title="{h(pi.title)}"' if pi.title else ""
        pills.append(
            f'<span class="pill{current_attrs}{title}{aria}>{h(pi.name)}</span>'
        )

    def replace_nav(match: re.Match) -> str:
        return match.group(1) + "".join(pills) + "</nav>"

    return _PI_PILLS_NAV_RE.sub(replace_nav, html_doc, count=1)


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
        current_idx = _facade().STAGES.index(current_stage)
    except ValueError:
        current_idx = -1
    nodes: list[str] = []
    for i, stage in enumerate(_facade().STAGES):
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
    overlay), a card containing the lifecycle pipeline and the four-card docs
    row. The section is appended after the user-gates marker / main open,
    mirroring inject_user_gates_html. Kept outside render_html because that
    function has an Article X footprint lock from SDD-FDC-001.

    SDD-041 rebuild: the reorder surface lives in the dedicated Backlog section
    (inject_backlog_reorder_html), keyed by canonical SDD-xxx ids. Lifecycle
    cards are therefore static here -- no drag affordances, no reorder control.
    """
    ordered = order_features_for_display(features, sdd_root)

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
    for fid, feature in ordered:
        pipeline = render_lifecycle_pipeline(
            feature.stage, aria_label=f"{feature.name} lifecycle")
        docs = render_docs_row(feature, sdd_root)
        feature_blocks.append(
            f'<article class="lifecycle-card" '
            f'aria-label="{h(feature.name)} lifecycle">'
            f'<div class="lifecycle-head">'
            f'<span class="lifecycle-id">{h(fid)}</span>'
            f'<span class="lifecycle-name">{h(feature.name)}</span>'
            f'<span class="lifecycle-stage">{h(feature.stage)}</span></div>'
            f'{pipeline}{docs}</article>'
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


LIFECYCLE_TOKENS = {
    "IDEA": "#B39DDB",
    "BACKLOG": "#7FA8C9",
    "CLARIFY": "#58B8B0",
    "SPEC": "#82B57A",
    "PLAN": "#C2A85D",
    "TASKS": "#D48B52",
    "IMPLEMENT": "#D36F86",
    "REVIEW": "#B884C4",
    "DONE": "#6FA37A",
}

LIFECYCLE_STATE_CLASSES = {
    stage: f"lifecycle-state-{stage.lower()}" for stage in LIFECYCLE_TOKENS
}

_LIFECYCLE_TOKENS_STYLE_ID = "sdd-lifecycle-tokens"
_LIFECYCLE_TOKENS_STYLE = (
    f'<style id="{_LIFECYCLE_TOKENS_STYLE_ID}">'
    ":root{"
    + "".join(
        f"--lifecycle-{stage.lower()}:{color};"
        for stage, color in LIFECYCLE_TOKENS.items()
    )
    + "}"
    ".zone-lifecycle .pipe-node,.zone-lifecycle .lifecycle-stage{opacity:1}"
    + "".join(
        f".zone-lifecycle .{state_class}{{"
        f"--lifecycle-state:var(--lifecycle-{stage.lower()});}}"
        for stage, state_class in LIFECYCLE_STATE_CLASSES.items()
    )
    + ".zone-lifecycle .pipe-node[class*=\"lifecycle-state-\"],"
    ".zone-lifecycle .lifecycle-stage[class*=\"lifecycle-state-\"]{"
    "background:var(--lifecycle-state);color:#0A0A0A;"
    "border-color:var(--lifecycle-state);opacity:1}"
    ".zone-lifecycle .pipe-current{font-weight:700;outline:2px solid var(--lifecycle-state);"
    "outline-offset:1px}"
    ".zone-lifecycle :focus-visible{outline:3px solid var(--focus-ring,#E8E4D8);"
    "outline-offset:3px}"
    "@media (max-width:640px){.zone-lifecycle .lifecycle-pipeline{"
    "display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}"
    ".zone-lifecycle .pipe-node{text-align:center;overflow-wrap:anywhere}"
    "main.grid-v3{grid-template-columns:minmax(0,1fr)}"
    "main.grid-v3>section{min-width:0;overflow-x:auto}"
    "header.topbar{flex-wrap:wrap;min-width:0}"
    ".topbar-mission{min-width:0}"
    ".pi-pills{margin-left:0;min-width:0;max-width:100%;flex-shrink:1}"
    ".context-item{white-space:normal;overflow-wrap:anywhere}}"
    "@media (forced-colors:active){"
    ".zone-lifecycle .pipe-node[class*=\"lifecycle-state-\"],"
    ".zone-lifecycle .lifecycle-stage[class*=\"lifecycle-state-\"]{"
    "forced-color-adjust:auto;background:Canvas;color:CanvasText;"
    "border:1px solid CanvasText}"
    ".zone-lifecycle .pipe-current{outline:3px double Highlight}}"
    "</style>"
)

_LIFECYCLE_NODE_RE = re.compile(
    r'(<li\b[^>]*\bclass=")([^"]*\bpipe-node\b[^"]*)("[^>]*>)([^<]+)(</li>)'
)
_LIFECYCLE_ARTICLE_RE = re.compile(
    r'<article\b(?=[^>]*\bclass="[^"]*\blifecycle-card\b)[^>]*>.*?</article>',
    re.DOTALL,
)
_LIFECYCLE_STAGE_RE = re.compile(
    r'(<span\b[^>]*\bclass=")([^"]*\blifecycle-stage\b[^"]*)("[^>]*>)([^<]+)(</span>)'
)


def _with_state_class(classes: str, stage: str) -> str:
    """Append one canonical lifecycle state class without disturbing others."""
    state_class = LIFECYCLE_STATE_CLASSES[stage]
    values = classes.split()
    if state_class not in values:
        values.append(state_class)
    return " ".join(values)


def inject_lifecycle_tokens_html(html_doc: str) -> str:
    """Add SDD-038 semantic state classes and token CSS to lifecycle HTML.

    The pass is additive, marker-bounded, and byte-idempotent. Existing labels,
    structural state classes, and ``aria-current=step`` attributes are retained.
    """
    if (
        'class="zone-lifecycle"' not in html_doc
        or f'id="{_LIFECYCLE_TOKENS_STYLE_ID}"' in html_doc
    ):
        return html_doc

    def decorate_node(match: re.Match) -> str:
        stage = match.group(4).strip().upper()
        if stage not in LIFECYCLE_STATE_CLASSES:
            return match.group(0)
        classes = _with_state_class(match.group(2), stage)
        return match.group(1) + classes + "".join(match.groups()[2:])

    def decorate_article(match: re.Match) -> str:
        article = _LIFECYCLE_NODE_RE.sub(decorate_node, match.group(0))
        current = re.search(
            r'<li\b[^>]*\bclass="[^"]*\bpipe-current\b[^"]*"[^>]*>'
            r'([^<]+)</li>',
            article,
        )
        current_stage = current.group(1).strip().upper() if current else ""

        def decorate_label(label_match: re.Match) -> str:
            label = label_match.group(4).strip().upper()
            stage = label if label in LIFECYCLE_STATE_CLASSES else current_stage
            if stage not in LIFECYCLE_STATE_CLASSES:
                return label_match.group(0)
            classes = _with_state_class(label_match.group(2), stage)
            return label_match.group(1) + classes + "".join(label_match.groups()[2:])

        return _LIFECYCLE_STAGE_RE.sub(decorate_label, article)

    decorated = _LIFECYCLE_ARTICLE_RE.sub(decorate_article, html_doc)
    if "</head>" in decorated:
        return decorated.replace("</head>", _LIFECYCLE_TOKENS_STYLE + "</head>", 1)
    marker = '<section class="zone-lifecycle"'
    return decorated.replace(marker, _LIFECYCLE_TOKENS_STYLE + marker, 1)


# ---------------------------------------------------------------------------- #
# SDD-041 (F-31 rebuild): the Backlog reorder surface
#
# The original SDD-041 attached drag affordances to the lifecycle cards, keyed
# by feature DIRECTORY names. Those names are not the SDD-xxx ids the POST
# /reorder endpoint (and backlog_reorder.move) accept, so every drop 400'd; the
# cards also pointed at whatever features happened to have specs, including
# DONE work. This section replaces that surface with a dedicated, visible
# Backlog list keyed by the canonical SDD-xxx ids.
#
# Ordering is taken VERBATIM from backlog_reorder.load_order (overlay-aware,
# includes DONE rows so ranks line up with the mutator's index space). The
# done-flag for each row is the same one the mutator uses
# (backlog_reorder.load_backlog_entries); title/priority are enriched from
# load_backlog when the row is in a numeric-RICE table, else fall back to the
# id. We never fork load_order.
#
# OPEN rows (the backlog row does not contain the token DONE -- the exact rule
# backlog_reorder uses) are draggable and carry working up/down buttons. DONE
# rows are shown de-emphasized for rank-correctness but are not draggable.
# ---------------------------------------------------------------------------- #

_BACKLOG_REORDER_STYLE = (
    "<style>"
    ".zone-backlog-reorder{grid-column:1/-1;margin-top:1rem}"
    ".backlog-list{display:flex;flex-direction:column;gap:.35rem;margin:.5rem 0}"
    ".backlog-row{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;"
    "border:1px solid var(--line,#333);border-radius:6px;padding:.4rem .6rem}"
    ".backlog-row[draggable=\"true\"]{cursor:grab}"
    ".backlog-row.backlog-done{opacity:.5}"
    ".backlog-handle{font-size:.85em;opacity:.45;cursor:grab;user-select:none}"
    ".backlog-id{font-weight:700;letter-spacing:.03em}"
    ".backlog-title{flex:1 1 12rem;min-width:8rem}"
    ".backlog-priority{font-size:.78em;opacity:.7}"
    ".backlog-status{font-size:.78em;opacity:.7}"
    ".backlog-rank{font-size:.72em;opacity:.55}"
    ".backlog-btns{display:flex;gap:.3rem;margin-left:auto}"
    ".backlog-btn{font-size:.8em;padding:.1rem .45rem;cursor:pointer}"
    ".backlog-btn[disabled]{opacity:.4;cursor:not-allowed}"
    ".backlog-row.drag-over{border-color:currentColor;"
    "box-shadow:0 0 0 2px var(--line,#444) inset}"
    ".backlog-row.drag-rejected{border-color:#f08a8a}"
    "</style>"
)


_BACKLOG_META_PID_RE = re.compile(r"[A-Z]{2,}-\d{2,3}")


def _backlog_reorder_meta(sdd_root: Path) -> dict[str, dict[str, str]]:
    """Best-effort ``{pid: {title, priority, status}}`` for the reorder view.

    ``load_backlog`` only parses numeric-RICE rows; many OPEN rows use a ``--``
    RICE placeholder (and some carry an extra trailing notes column), so they
    would render with a bare, duplicated id. This tolerant pass splits every
    ID row positionally on ``|`` -- title = col 1, priority = col 2, status =
    col 9 (the Status column in both 10- and 11-column rows) -- so every shown
    row has a real description. Canonical ``BacklogItem`` values from
    ``load_backlog`` take precedence; this only fills rows it missed.
    """
    meta: dict[str, dict[str, str]] = {
        b.pid: {"title": b.title, "priority": b.priority, "status": b.status}
        for b in load_backlog(sdd_root)
    }
    path = sdd_root / "backlog" / "BACKLOG.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return meta
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        pid = cells[0]
        if not _BACKLOG_META_PID_RE.fullmatch(pid) or pid in meta:
            continue
        title = cells[1] if len(cells) > 1 else pid
        priority = cells[2] if len(cells) > 2 else ""
        status = cells[9] if len(cells) > 9 else (cells[-1] if cells else "")
        meta[pid] = {"title": title or pid, "priority": priority,
                     "status": status}
    return meta


def _render_backlog_buttons(item_id: str, *, up_rank: int | None,
                            down_rank: int | None) -> str:
    """Render JS-driven up/down reorder buttons for one OPEN backlog row.

    ``up_rank`` / ``down_rank`` are the absolute indices in the FULL
    ``load_order`` of the previous / next OPEN item -- the value ``move()``
    expects. They are ``None`` when there is no adjacent OPEN item (first / last
    open row), which renders the button disabled. DONE rows are hidden, so
    adjacency is computed over OPEN items only while the POSTed rank stays in
    full-order space, keeping button and drag moves consistent with ``move()``.
    CSP blocks inline ``onclick``; click wiring is done in the single
    hash-pinned script.
    """
    def _btn(direction: str, glyph: str, label: str,
             to_rank: int | None) -> str:
        if to_rank is None:
            return (
                f'<button type="button" class="backlog-btn backlog-{direction}" '
                f'aria-label="{h(label)}" disabled>{glyph}</button>'
            )
        return (
            f'<button type="button" class="backlog-btn backlog-{direction}" '
            f'aria-label="{h(label)}" data-item="{h(item_id)}" '
            f'data-to-rank="{to_rank}">{glyph}</button>'
        )

    up_btn = _btn("up", "&#9650;", f"Move {item_id} up", up_rank)
    down_btn = _btn("down", "&#9660;", f"Move {item_id} down", down_rank)
    return f'<span class="backlog-btns">{up_btn}{down_btn}</span>'


def inject_backlog_reorder_html(html_doc: str, *, sdd_root: Path) -> str:
    """Inject the SDD-041 Backlog reorder section (OPEN-only priorities view).

    Renders ONLY OPEN backlog ids (a row is OPEN when its BACKLOG.md line does
    not contain the token ``DONE`` -- the exact rule ``backlog_reorder`` uses).
    DONE rows are not shown at all. Each open row carries ``data-pid`` and
    ``data-rank`` (its index in the FULL ``load_order``, so the value
    ``move()`` expects survives the DONE rows being hidden). Up/down buttons
    target the adjacent OPEN item's full-order index. Every row shows a real
    id + title + priority + status via ``_backlog_reorder_meta`` (so no row
    renders as a bare duplicated id). No-op when there are no open items.
    Article X safe -- post-processes render_html output.
    """
    order = _reorder_load_order(sdd_root)
    if not order:
        return html_doc

    done_map = {e.id: e.done for e in _reorder_load_entries(sdd_root)}
    meta = _backlog_reorder_meta(sdd_root)

    open_ids = [pid for pid in order if not done_map.get(pid, False)]
    if not open_ids:
        return html_doc
    open_total = len(open_ids)
    full_rank = {pid: i for i, pid in enumerate(order)}

    rows: list[str] = []
    for pos, pid in enumerate(open_ids):
        info = meta.get(pid, {})
        title = info.get("title") or pid
        priority = info.get("priority", "")
        status_text = info.get("status") or "OPEN"
        rank_label = f"rank {pos + 1} of {open_total}"

        up_rank = full_rank[open_ids[pos - 1]] if pos > 0 else None
        down_rank = (full_rank[open_ids[pos + 1]]
                     if pos < open_total - 1 else None)
        buttons = _render_backlog_buttons(pid, up_rank=up_rank,
                                          down_rank=down_rank)
        rows.append(
            f'<div class="backlog-row" draggable="true" '
            f'data-pid="{h(pid)}" data-rank="{full_rank[pid]}" '
            f'aria-label="{h(pid)} {h(title)} (drag or use buttons to '
            f'reorder)">'
            f'<span class="backlog-handle" aria-hidden="true" '
            f'title="Drag to reorder">\u2630</span>'
            f'<span class="backlog-id">{h(pid)}</span>'
            f'<span class="backlog-title">{h(title)}</span>'
            f'<span class="backlog-priority">{h(priority)}</span>'
            f'<span class="backlog-status">{h(status_text)}</span>'
            f'<span class="backlog-rank">{h(rank_label)}</span>'
            f'{buttons}'
            f'</div>'
        )

    section = (
        '<section class="zone-backlog-reorder" '
        'aria-labelledby="backlog-reorder-heading">'
        + _BACKLOG_REORDER_STYLE
        + '<h2 id="backlog-reorder-heading">Backlog &mdash; drag to '
        'reprioritize</h2>'
        + '<div class="backlog-list">'
        + "".join(rows)
        + '</div></section>'
    )
    marker = '<main id="main" role="main" class="grid-v3">'
    if marker in html_doc:
        return html_doc.replace(marker, marker + section, 1)
    return html_doc + section


# ---------------------------------------------------------------------------- #
# SDD-041 (F-31): true browser drag-and-drop reorder
#
# A single, hash-pinned vanilla-JS block turns the Backlog rows into a native
# HTML5 drag surface AND wires the per-row up/down buttons. The script is:
#   - additive: emitted only when draggable rows exist; injected by
#     inject_drag_html AFTER inject_backlog_reorder_html so the locked
#     render_html footprint (Article X) is untouched.
#   - inert as a static file: it no-ops unless location.protocol is http(s),
#     so the file:// state.html stays read-only.
#   - CSP-pinned: we widen ONLY for this exact script via its sha256 hash --
#     never 'unsafe-inline'. The hash is computed at import time over the exact
#     body, so editing the body re-pins automatically (and a mismatch fails
#     closed by browser CSP enforcement).
#   - force-free: the handlers post {item, to_rank} only. Forcing past a
#     dependency lock is a Level-2 human decision (ADR-017) and is NEVER sent
#     by a drag or button gesture; a 409 surfaces the reason.
# ---------------------------------------------------------------------------- #

_DRAG_SCRIPT_BODY = (
    "(function(){"
    "if(location.protocol!=='http:'&&location.protocol!=='https:')return;"
    "function postReorder(item,toRank,el){"
    "if(!item||isNaN(toRank))return;"
    "fetch('/reorder',{method:'POST',"
    "headers:{'Content-Type':'application/json'},"
    "body:JSON.stringify({item:item,to_rank:toRank})})"
    ".then(function(r){return r.json().then(function(d){"
    "return {s:r.status,d:d};});})"
    ".then(function(res){if(res.s===200){location.reload();return;}"
    "var reason=(res.d&&res.d.reason)?res.d.reason:'reorder rejected';"
    "if(el){el.classList.add('drag-rejected');"
    "el.setAttribute('title','blocked: '+reason+"
    "' -- forcing is a Level-2 decision; use the CLI with --force');}})"
    ".catch(function(){});}"
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
    "postReorder(item,toRank,t);}"
    "var rows=document.querySelectorAll('.backlog-row[draggable=\"true\"]');"
    "for(var i=0;i<rows.length;i++){var c=rows[i];"
    "c.addEventListener('dragstart',onStart);"
    "c.addEventListener('dragover',onOver);"
    "c.addEventListener('dragleave',onLeave);"
    "c.addEventListener('drop',onDrop);}"
    "function onBtn(e){var el=e.currentTarget;"
    "var item=el.getAttribute('data-item');"
    "var toRank=parseInt(el.getAttribute('data-to-rank'),10);"
    "var row=el.closest?el.closest('.backlog-row'):null;"
    "postReorder(item,toRank,row);}"
    "var btns=document.querySelectorAll('.backlog-up,.backlog-down');"
    "for(var j=0;j<btns.length;j++){"
    "btns[j].addEventListener('click',onBtn);}"
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
