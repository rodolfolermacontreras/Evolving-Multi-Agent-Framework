---
feature: state-dashboard
status: done
created: 2026-05-16
shipped: 2026-05-16
pi: PI-2
sprint: A
priority: P1
related_spec: SDD-002 (cli/state_builder.py shared implementation)
adjacent_backlog: SDD-001 (Fleet Bridge Dashboard, P3) -- this feature delivers ~70% of its operator-visibility value at v0.2 (live server + UX-polished Bridge dashboard)
id: SDD-STATEDASH-spec
type: spec
owner: principal-architect
updated: 2026-06-06
---

# Feature Spec -- State Dashboard v0.1

## Why this feature, in one sentence

The human gets lost in walls of text and choice prompts; the framework needs a single visual surface that answers "where am I, what is being built, what is next" without reading prose.

## Origin

User feedback on 2026-05-16: "when I am working with the system, it is confusing what is next exactly... it is very easy to lose track on where we are, that is why we need to develop a graphic user interface that shows exactly where we are in the project, what is being developed, and have some progress bar or something."

This is lived pain. It promotes SDD-001 (Fleet Bridge Dashboard, parked at P3 in backlog) to P1 because the dashboard is the missing piece that makes the rest of the framework usable, not a polish item.

## Scope of v0.1 (minimal, ship today)

In scope:
- One Python CLI: `cli/state_builder.py` that reads existing artifacts and produces both `exec/state.md` (refreshed from data) and `exec/state.html` (visual dashboard)
- Single self-contained HTML file (no external CSS, no JS dependencies beyond optional auto-refresh)
- Sections:
    1. Header: current PI + one-line focus + timestamp
    2. "What is next" -- ONE recommended action, prominently placed
    3. PI progress bar (commitments done / total) for the current PI
    4. Lifecycle Kanban: each feature placed in its current stage (IDEA, BACKLOG, CLARIFY, SPEC, PLAN, TASKS, IMPLEMENT, REVIEW, DONE)
    5. Fleet roster summary (principal count, generic count, specialist count, last role created)
    6. Recent activity: last 10 git commits + recent ledger dispatches (if any)
- Visual style follows the Bridge design language from SDD-001 DESIGN.md (carbon background, paper-cream text, oxblood/amber/jade signals, monospace)
- Generator runs in <2 seconds, stdlib only (LESSON-001)

Out of scope (deferred to SDD-001 v1.0+):
- Live auto-refresh / WebSocket / server-sent events
- Interactive controls (no buttons that mutate state)
- Light/dark mode toggle
- The full Dispatch Stream (will render whatever is in fleet.db; today that is empty -- show empty state cleanly)
- EM input drawer / command palette
- Real-time agent activity indicators

## Validation contract (Article X)

- [x] `python cli/state_builder.py` exits 0 and produces both `exec/state.md` and `exec/state.html`
- [x] HTML file is self-contained (no external network requests at render time) -- verified by `test_html_is_self_contained`
- [x] HTML displays current PI, current focus, and ONE next-action recommendation
- [x] Lifecycle Kanban shows the three existing features (fleet-ledger at DONE, fleet-bridge-dashboard at CLARIFY, state-dashboard at IMPLEMENT)
- [x] PI-2 progress bar reflects roadmap commitments (0 of 6 at start)
- [x] Fleet roster reflects roster/agents.json (4 principals + 4 generic, 0 specialists)
- [x] Recent activity shows last 10 commits via `git log`
- [x] Generator handles missing inputs gracefully (no ledger entries -- empty-state message rendered)
- [x] Smoke tests pass (4/4 in `cli/test_state_builder.py`)

## Success criteria (what "done" means to the human)

When the human opens `exec/state.html` in a browser, in under 5 seconds they can answer:
1. What PI/sprint are we in?
2. What was the last thing shipped?
3. What is the ONE recommended next action?
4. What features are in flight and at what stage?

If they cannot, v0.1 has failed and we iterate.
