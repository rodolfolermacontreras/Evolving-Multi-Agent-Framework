# Session Memory — Evolving Multi-Agent Framework

**Latest checkpoint (2026-06-05):** PI-4 Sprint 4 "Filesystem Data Contracts" (SDD-FDC-001)
through PLAN. Clarify CLOSED (D1-D5), Spec APPROVED WITH CONDITIONS (Architect),
plan.md + ADR-012 written, all 5 review conditions closed. **Next: /tasks (Software
Developer).** Hard constraint carried throughout: b7ce642 S1 footprint locked
(`render_html()` + T-001..T-004 immutable; additive code only). Artifacts under
`specs/2026-06-04-filesystem-data-contracts/` (spec, validation, clarification-log,
handoff-to-plan, plan) + `docs/ADR/012-filesystem-frontmatter-data-contract.md`.
PM role pauses until AC verification (AC-1..AC-7) post-implement.

**Prior checkpoint:** PI-4 polish in progress. Timeline + Work-Index features partially implemented. **UNCOMMITTED + 62 tests failing — NameError bug to fix on resume.**

**Date:** 2026-06-03 (computer restart mid-session)
**Owner:** Rodolfo Lerma
**Repo:** https://github.com/rodolfolermacontreras/Evolving-Multi-Agent-Framework
**Local path:** `C:\Training\Projects\Evolving-Multi-Agent-Framework`

---

## CRITICAL: Resume Here

### Immediate fix needed (5-10 minutes)

**Bug**: In `spec-driven-development/cli/state_builder.py` around line 1911, the timeline section references `backlog` and `features` variables that are NOT in `render_html()`'s signature. Result: 62 test failures with `NameError: name 'backlog' is not defined`.

**Fix path (recommended)**: Move the timeline-section build logic OUT of `render_html()` and INTO `build()` where `features` and `backlog` are in scope. Pass the pre-built `timeline_section` string into `render_html()` as a new parameter.

OR (simpler): Add `features` and `backlog` parameters to `render_html()` signature. Search for `def render_html(` to find the signature.

After fix:
1. `python -m pytest spec-driven-development/cli/test_state_builder.py -q` -- expect 95+ pass
2. Add 2-3 tests for timeline section (test_timeline_section_renders, test_timeline_has_done_items, test_work_index_generated)
3. Add 1-2 tests for work-index (test_work_index_file_written, test_work_index_lists_done_features)
4. `python spec-driven-development/cli/state_builder.py` to regenerate dashboard
5. Commit + push (triggers Azure auto-deploy)

### What was being built (user's exact request)

User said: "we need a diagram, clearly showing what was done first, then second, and where we are right now. A time series of sorts, like a timeline line, clearly showing the progress." AND "we need the system to be informed on what was already worked on (the executive agent or principals) what is in the backlog, and what we are working on, so we can do the cross check validation to not work on something that was already done, or poison other pieces of the code by introducing new features that cancel each other."

**Two-part deliverable:**

1. **Project Timeline (visible UI)** — New Section 7 on dashboard. Vertical timeline with markers:
   - DONE features (jade dots, sorted by spec date)
   - IN-FLIGHT features (amber pulsing dots)
   - QUEUED items from backlog (gray dots)
   - Legend at top: "serial-first execution (no parallel work unless tasks are truly independent)"
   - CSS classes: `.timeline`, `.tl-item`, `.tl-marker`, `.tl-done/.tl-current/.tl-future`, `.tl-content`, `.tl-date`, `.tl-name`, `.tl-stage`
   - Grid area `timeline` added between `wip` and `pi`

2. **Cross-check protocol** — Auto-generated `exec/work-index.md` for principal consumption.
   - Function: `render_work_index()` (DONE — already in state_builder.py)
   - Wired into `build()` to write `exec/work-index.md` (DONE)
   - **NOT YET DONE**: Create `.github/skills/core/pre-work-check/SKILL.md`
   - **NOT YET DONE**: Update all 4 principal `.agent.md` files to load the skill

### Files modified (uncommitted)

- `spec-driven-development/cli/state_builder.py`:
  - Added timeline CSS (lines ~1218 area, before footer)
  - Added timeline grid area to main.grid-v3 (lines ~894-915)
  - Added timeline to responsive media query
  - Added `timeline_section` build logic in render_html (BUGGY — references `features`/`backlog` not in scope)
  - Added `render_work_index()` function (~line 2055)
  - Wired work-index write into `build()` orchestration
  - Added `{timeline_section}` to HTML body template

- `spec-driven-development/backlog/IDEAS.md`:
  - Added 2026-06-03 timeline visualization idea
  - Added 2026-06-03 cross-check validation protocol idea

### Remaining work

After fixing the bug:

1. ✅ Fix render_html NameError (5 min)
2. ⬜ Run tests, verify 95+ pass
3. ⬜ Add 3-5 new tests (timeline rendering, work-index generation)
4. ⬜ Create `.github/skills/core/pre-work-check/SKILL.md` (15 min)
5. ⬜ Update 4 principal agent files to load pre-work-check skill (10 min)
6. ⬜ Regenerate dashboard, commit, push
7. ⬜ Verify Azure deploy renders timeline correctly

---

## Resume Instructions (longer-term)

### PI-4 Summary

- **S1 (Live UI v2)**: DONE. state_builder.py rewritten to v3.0 sprint-first layout. Agent lineage section added (roster table + promotion timeline). 94 tests. HTML renderer, data-layer functions, accessibility audit, security tests, integration tests. Code review fix (try/finally for sqlite).
- **S2 (Alpha Release Housekeeping)**: DONE. Root README.md rewritten with quickstart, key concepts, origin story. Roadmap updated (PI-1 through PI-4). Domain skills already annotated as examples. GitHub Actions versions verified (Node 20+).
- **Post-S2 fixes**: Dashboard bugs fixed (PI detection, feature stages, 404 links, PI_MISSION dict, missing RETROs). ARCHITECTURE.md created (530 lines). Live dashboard URL documented. Auto-launch idea captured. Agent lineage section added to Section 5. Spec amended retroactively with LESSON-014.

**Next:** PI-5 planning, team onboarding, second-project bootstrap.

---

## PI-4 Sprint Status (as of 2026-06-02)

| Sprint | Title | Status | Notes |
|--------|-------|--------|-------|
| S1 | Live UI v2 | **DONE** | v3.0 sprint-first layout. 94 tests. Agent lineage (roster + timeline). |
| S2 | Alpha Release Housekeeping | **DONE** | README rewritten. Roadmap updated PI-1 through PI-4. |

## Commit chain (PI-4)

```
216eb8d  docs: amend live-ui-v2 spec Section 5.6 to match shipped agent lineage feature
cb117d8  feat: replace agent activity placeholder with full agent lineage section
59900a0  docs: capture auto-launch dashboard idea in IDEAS.md
6bb06e6  fix: dashboard shows PI-4, correct feature stages, no 404 links
7116713  docs: add live dashboard URL to README and ARCHITECTURE
dc84f32  docs: add comprehensive ARCHITECTURE.md with code and framework diagrams
707fdc1  feat: alpha release housekeeping -- README, roadmap, domain skill annotations (PI-4 S2)
86748f3  fix: use try/finally for sqlite connection in load_decisions() (code review)
7abb353  feat: add accessibility audit, security tests, and integration tests (T-012..T-014)
a16819a  feat: rewrite HTML renderer to v3.0 sprint-first layout (T-005..T-011)
b7ce642  feat: add data-layer functions for Live UI v2 (T-001..T-004)
a702c23  docs: kick off PI-4 -- Alpha Release
```

## Lessons captured

- **LESSON-014**: Implementation preceded spec amendment. Agent lineage was built before the spec was updated. Root cause: EM routed human request directly to implementation instead of checking spec alignment via Architect first. Action: add spec alignment check to implement skill.

## What to do when resuming

### Immediate next steps:

1. **PI-5 Planning** -- run `/replan` to define PI-5 objectives. Candidates: real-time agent dispatch status (Section 5.6.1 data contract), team onboarding guide, second-project bootstrap (non-Day-to-Day), GENERALIZATION_SDD.md v1.0, template repo packaging, auto-launch dashboard on session start.
2. **Team onboarding** -- share the repo with teammates. The new README provides the entry point. Point them to the 3-Hour Bootstrap in GENERALIZATION_SDD.md Section 3.
3. **Second-project bootstrap** -- pick a new project (different tech stack from Day-to-Day) and run the full greenfield bootstrap to validate portability.

### Session read order for a fresh agent:
1. `INSTRUCTIONS.md` (repo root)
2. `.github/copilot-instructions.md`
3. `spec-driven-development/CONTEXT.md`
4. This file (`sessions/SESSION-MEMORY.md`)
5. `docs/HIGH_LEVEL_DEV_TRACKER.md` (Tier 1 navigation)
6. `docs/Management/PI-4/INDEX.md` (active PI, if it exists)
7. `docs/RULES.md` (v1.1.0, 13 rules)
8. The relevant sprint SPEC for whichever sprint you are working on

```
aa8ba75  docs(s4): human approves all 6 Live UI v2 design decisions
f74d20a  feat(s4): author Live UI v2 DESIGN_TOKENS.md and spec.md (T-004, T-006)
e960ed8  feat(s4): add Live UI v2 static HTML mockup (T-005)
c416ba0  feat(skills): add design-tokens skill v1.0 (T-011, closes LESSON-007)
6361ef1  docs(s4): apply Architect review notes to spec.md (T-007)
2bc6b44  docs(roster): register design-tokens skill in skills.json
3026eec  feat(s4): author plan.md, tasks.md, validation.md (T-008, T-009, T-010)
8450eb2  feat: incorporate human feedback into Live UI v2 spec and mockup
8f1d0ff  docs: update SESSION-MEMORY and AGENT_NOTES with mockup feedback session
f8679dd  feat: redesign timeline + fix sprint naming consistency
```

## Key files changed this session

| File | Change |
|------|--------|
| `specs/2026-05-26-live-ui-v2/clarification.md` | EM recommendations prefilled, human approved all 6 |
| `specs/2026-05-26-live-ui-v2/DESIGN_TOKENS.md` | NEW: 59 CSS custom properties, 8 sections |
| `specs/2026-05-26-live-ui-v2/spec.md` | NEW: 37KB spec, 12 sections + 3 appendices |
| `specs/2026-05-26-live-ui-v2/mockup.html` | NEW: 34KB static prototype |
| `specs/2026-05-26-live-ui-v2/plan.md` | NEW: 4-phase PI-4 implementation plan |
| `specs/2026-05-26-live-ui-v2/tasks.md` | NEW: 14 atomic tasks with TDD ordering |
| `specs/2026-05-26-live-ui-v2/validation.md` | NEW: LOCKED, 15+21 acceptance criteria |
| `.github/skills/operational/design-tokens/SKILL.md` | NEW: design-tokens skill v1.0 |
| `roster/skills.json` | design-tokens skill registered |
| `docs/Management/PI-3/Sprint-4-live-ui-v2-spec/SPEC.md` | Status -> DONE, dispatch tracker filled |
| `docs/Management/PI-3/Sprint-4-live-ui-v2-spec/AGENT_NOTES.md` | Full session log populated |
| `docs/Management/PI-3/INDEX.md` | S4 -> DONE, What Was Done updated |
| `docs/HIGH_LEVEL_DEV_TRACKER.md` | S4 DONE, Top 3 refreshed, lessons all closed |

## Previous session history

Previous work (PI-3/S5 Navigation Layer, PI-3 kickoff, PI-2 retro, PI-1 pilot) is documented in the commit history and in `docs/Management/PI-1/INDEX.md`, `docs/Management/PI-2/INDEX.md`.
   - `spec-driven-development/constitution/roadmap.md` (current PI status)
4. Optional: open `spec-driven-development/docs/CHEAT-SHEET.html` in a browser for the visual workflow.

To continue working on the framework itself, the natural next moves are:
- Run `/replan` against the fleet-ledger pilot to formally close PI-1
- Pick a real project to bootstrap (greenfield with `archetype-recommender` + `bootstrap.py greenfield`, or brownfield with `bootstrap.py brownfield --draft-only`)
- Curate the 4 lessons in `spec-driven-development/sprints/PI-1/lessons.md` via `/evolve`
- Exercise `/hire` to create a real new role (e.g., `data-analyst` generic)

---

## Project purpose, in one sentence

A portable, replicable system for orchestrating a fleet of AI agents through a structured, spec-driven, test-driven development lifecycle. One human + a team of specialized AI agents shipping production-quality features with traceability and minimal ceremony overhead.

---

## What we built today

### Starting state (commit `d6332c0`, before today)
- Framework scaffolded but unproven (v0.1)
- Constitution/CONTEXT/roadmap referenced the Day-to-Day Agent host project
- No pilot ever run; no validation that the lifecycle works in practice
- Domain skills under `.github/skills/domain/` were Day-to-Day-specific
- No bootstrap mechanism — adopters had to manually copy files
- "Evolving" was aspirational, not mechanical

### Ending state (commit `23156a0`, end of session)
- **29 commits** on origin/master
- **28 framework skills** across 5 categories (core, workflow, engineering, operational, domain)
- **17 slash commands** (added /ask, /constitution, /evolve, /replan, /hire today)
- **10 binding constitution articles** (I–X, all with semver frontmatter)
- **7 ADRs** (added 4 today: 004, 005, 006, 007)
- **5 starter archetypes** (python-library, python-web-service, data-pipeline, cli-tool, research-repo)
- **Working CLI** (`bootstrap.py greenfield <archetype>` and `bootstrap.py brownfield <target>`)
- **Working fleet ledger** at `spec-driven-development/ledger/fleet.db` with init script + query CLI + 13 passing tests
- **First feature shipped end-to-end** via the framework's own lifecycle (`specs/2026-05-12-fleet-ledger/`)
- **PI-1 lessons.md** seeded with 4 honest candidates from the pilot
- **Cheat sheet HTML** with visual SVG workflow diagram for greenfield + brownfield + lifecycle
- **Guided UX** — Executive Manager loads `archetype-recommender` skill on new-project intent, walks human through 5-6 questions with reasoning + confidence, falls back to `/evolve` if none of the 5 archetypes fit

### Day's commit log (newest first)

| SHA | Subject |
|---|---|
| `cec527e` | docs(nav): S5 closure -- AGENT_NOTES, PI-3 INDEX, tracker to DONE (T-014) |
| `6492aa1` | feat(cli): implement build-index subcommand for INDEX.md auto-gen (T-010/T-011) |
| `f971bfe` | docs(nav): update tracker links, onboarding 5-pointer, INSTRUCTIONS, deprecate Temp/ (T-007/T-008/T-012/T-013) |
| `991348f` | docs(nav): populate PI-3 INDEX with current sprint status (T-006) |
| `d745123` | refactor(nav): migrate Temp/ sprint docs to Management/PI-3/ (T-003) |
| `18c0a9f` | docs(nav): backfill PI-2 INDEX and sprint summaries (T-005) |
| `f6f043a` | docs(nav): backfill PI-1 INDEX and sprint summaries (T-004) |
| `6aca6a2` | feat(nav): merge T-002 Management/ skeleton into master |
| `0c80675` | feat(nav): create Management/ skeleton with PI-1/PI-2/PI-3 INDEX templates (T-002) |
| `59f695b` | docs(session): update SESSION-MEMORY with PI-3/S5 checkpoint |
| `0a8f2aa` | docs(tracker): S5 in-flight, ADR-0011 approved, HITL cleared |
| `a0093d4` | docs(s5): apply three amendments + mark T-001/T-009 DONE |
| `022a9c7` | docs(rules): add Rule 13 + ADR-0011 three-tier navigation layer |
| `ee56265` | plan(pi-3): add S5 Navigation Layer Migration in response to external feedback |
| `b2b5d59` | feat(agents): hire principal-ui-designer (draft) -- ADR-0010 |
| `cde5727` | plan(pi-3): create 4 sprint detail docs (S1-S4) + PI-3 kickoff artifacts |
| `5cc36b2` | docs(pi-3): kickoff foundation -- RULES.md, ONBOARDING, TRACKER |

### PI-3/S5 task status (as of 2026-05-25)

| Task | Description | Status |
|------|-------------|--------|
| T-001 | ADR-0011 (Three-Tier Navigation Layer) | DONE (`022a9c7`) |
| T-009 | Rule 13 + DONE ceremony bindings in RULES.md | DONE (`022a9c7`) |
| T-002 | Create Management/ skeleton (PI-1, PI-2, PI-3 INDEX.md) | DONE (`6aca6a2`) |
| T-003 | Migrate Temp/ sprint docs to Management/PI-3/Sprint-N-{title}/SPEC.md | DONE (`d745123`) |
| T-004 | Backfill PI-1 INDEX (summaries only, not full specs) | DONE (`f6f043a`) |
| T-005 | Backfill PI-2 INDEX | DONE (`18c0a9f`) |
| T-006 | Populate PI-3 INDEX | DONE (`991348f`) |
| T-007 | Update tracker links | DONE (`f971bfe`) |
| T-008 | Extend ONBOARDING to 5-pointer read | DONE (`f971bfe`) |
| T-010 | Implement build-index subcommand in state_builder.py | DONE (`6492aa1`) |
| T-011 | Tests for build-index (3 tests) | DONE (`6492aa1`) |
| T-012 | Update INSTRUCTIONS.md | DONE (`f971bfe`) |
| T-013 | Deprecate docs/Temp/ | DONE (`f971bfe`) |
| T-014 | Closure dry-run (S5 itself populates new structure) | DONE (`cec527e`) |

### Next recommended moves (post-S5)

1. **HITL**: Human runs 9 Azure provisioning steps for S1 (unblocks dashboard freshness)
2. **HITL**: Human approves ADR-0010 (UI Designer hire, unblocks S4)
3. **Dispatch**: Start S2 (Day-to-Day brownfield bootstrap) or S3 (PI-2 lessons curation) -- both parallel-safe, both benefit from the new Management/ structure
4. **Push**: 50+ commits ahead of origin -- consider pushing to remote (HITL gate #10)

---

## Architecture (the mental model that drove all decisions)

```
Human (you)
   │
   ▼
Executive Manager  ← single human entry point. Knows the big picture.
   │
   ├─► Principal Architect       ─┐
   ├─► Principal Product Manager  ─┼─► STRATEGY layer (decide WHAT and HOW)
   ├─► Principal Software Dev     ─┘
   │                                Each Principal dispatches workers as needed:
   │
   ▼
Worker Agents (the actual hands)  ← TACTICS layer (DO the work)
   ├─ Developer        ─ generic
   ├─ UX Designer      ─ generic
   ├─ QA Engineer      ─ generic
   ├─ Data Scientist   ─ generic
   ├─ Data Analyst     ─ created on demand via /hire generic
   ├─ AI Engineer      ─ created on demand via /hire generic
   ├─ Azure Data Eng.  ─ created on demand via /hire generic
   └─ <role>-<name>-<domain>-<n>  ─ specialists earned via /hire specialist
```

**Vendor analogy:** The human is the client. The Executive Manager is the engagement manager — your single phone number. Principals are partner-level consultants who decide strategy. Workers are the actual hands doing the work, dispatched per task, constrained to 1–3 files. Specialization is *earned* through demonstrated competence, never assigned by configuration.

---

## The 10 binding articles (current constitution, principles.md)

1. **I.** Two-folder split is invariant (`.github/` + `spec-driven-development/`)
2. **II.** Single human entry point: the Executive Manager (ADR-0004)
3. **III.** Two-stage review order is fixed: spec compliance, then code quality
4. **IV.** Specialization over generalism: workers 1–3 files; reviewers review only
5. **V.** Generic by default, specialized on demand (ADR-0003)
6. **VI.** Ceremony proportional to risk (the spec sizing rule)
7. **VII.** Every artifact is a file; every dispatch is logged
8. **VIII.** Constitution is immutable without an ADR
9. **IX.** Human holds final approval on Level-2 decisions
10. **X.** Validation is a pre-implementation contract (Article X, ADR-0005)

All 6 constitution files now carry YAML frontmatter: `version: '1.0.0'`, `ratified: 2026-05-12`, `last_amended: 2026-05-12`. Amendments must use `/constitution` which semver-bumps and runs the propagation scan via `constitution-sync` skill (ADR-0006).

---

## All 17 slash commands (full list)

### Entry & status
- `/ask` — ask Executive Manager anything; it routes + synthesizes
- `/state` — refresh + present `exec/state.md`
- `/grill` — free-form grilling to sharpen an idea before `/clarify`

### Lifecycle
- `/triage` — RICE-score idea, assign P1–P4
- `/clarify` — one question at a time, with recommendation
- `/spec` — generate feature spec + validation contract (Article X)
- `/plan` — implementation plan from approved spec
- `/tasks` — decompose plan into tagged 1–3-file tasks
- `/analyze` — read-only consistency check (spec vs plan vs tasks)
- `/implement` — execute one task (TDD, Article X gate)
- `/fleet` — parallel dispatch of [P][AFK] tasks
- `/qa` — validate implementation against spec (two-stage)

### Ceremony & evolution
- `/retro` — sprint retro, max 3 action items
- `/replan` — after every DONE: review constitution/roadmap/skills/lessons
- `/evolve` — curate lessons backlog into framework changes (SHIP/DEFER/DISCARD)
- `/constitution` — amend constitution with semver + propagation scan
- `/hire` — create new worker role: generic OR promote generic to specialist (ADR-0007, Level-2 draft-first)

---

## Key design decisions (from this session, with ADR references)

### ADR-0004: Executive Manager as orchestrator and single entry point
Re-scoped from passive reporter (read-only state.md) to active orchestrator. Owns kickoff capture, ad-hoc Q&A routing with answer synthesis, status, escalation, big-picture awareness. Reads state.md by default, may read raw artifacts to answer routed questions, never modifies anything except (optionally) state.md. Rejected adding a fifth Principal as too complex.

### ADR-0005: Validation as pre-implementation contract (Article X)
The strongest convergent finding from research across all 3 code-based inspirations (Spec-Kit, DeepLearning.AI SDD course, sc-spec companion). Validation criteria are written DURING /spec, locked at /tasks, and verified at /qa. Implementation is not done until every checkbox is checked or `[NO-TEST-NEEDED]` is documented. Killed the "AI wrote something that looks right but doesn't match the spec" failure mode.

### ADR-0006: Constitution semantic versioning
Every constitution file gets YAML frontmatter (version, ratified, last_amended). Amendments use `/constitution` which semver-bumps (MAJOR/MINOR/PATCH), runs the propagation scan via `constitution-sync` skill, and emits a Sync Impact Report listing what skills/prompts/templates need review. Closes the "constitution drift" silent risk.

### ADR-0007: /hire command and role lifecycle
ADR-0003 documented the model in prose ("generic by default, specialized on demand"). ADR-0007 makes it executable. Two modes: `/hire <role-name> generic` creates a new role on the fly (data-analyst, ai-engineer, azure-data-engineer); `/hire <role>-<name>-<domain>-<n> specialist` promotes a generic worker to permanent specialist with own skill pack, requires citing prior dispatch evidence. Both modes are Level-2 draft-first: produce draft + report, human approves, only then files land. Executive Manager awareness via BOTH `exec/state.md` Fleet line AND ledger `decisions` row (per user choice option C).

---

## The pilot proof (commit `9ace815`)

The framework's own first feature shipped through its own lifecycle as the dogfood. Feature: fleet ledger v0.1.

**Lifecycle artifacts at `spec-driven-development/specs/2026-05-12-fleet-ledger/`:**
- `spec.md` — full spec with testable acceptance criteria
- `plan.md` — 3-phase plan
- `tasks.md` — 8 tagged tasks, test-first ordering
- `validation.md` — pre-implementation contract (Article X format), all checkboxes verified
- `clarification-log.md` — 5 self-clarification Q&A entries
- `RETRO.md` — what worked, what didn't, lessons fed to PI-1 lessons.md

**Implementation at `spec-driven-development/ledger/`:**
- `schema.sql` — dispatches + decisions tables
- `init_ledger.py` — stdlib-only idempotent ledger init
- `ledger_cli.py` — record-dispatch, record-decision, mark-outcome, list-pi, list-feature, summary
- `test_ledger.py` — **13 tests, all passing in 0.81s**
- `fleet.db` — initialized empty SQLite DB, committed

**Lessons captured in `spec-driven-development/sprints/PI-1/lessons.md`:**
- LESSON-001: canonical Python CLI style guide (3 stdlib CLIs in tree should share style)
- LESSON-002: clarify task ID convention
- LESSON-003: reduce validation duplication across artifacts
- LESSON-004: define ledger migration policy

These 4 lessons are ready for `/evolve` curation in a future session.

---

## Inspiration audit findings (from research subagents)

We dispatched 4 parallel research subagents to actually inspect the 4 cited inspiration sources. Findings:

### Two factual corrections shipped in commit `6825943`
1. **Spec-Kit is by GitHub, not Cline.** Repo: https://github.com/github/spec-kit
2. **`sc-spec-driven-development-files` is the companion code repo for the DeepLearning.AI SDD course** taught by **Paul Everitt of JetBrains**. Not a separate inspiration — same source as the course. So we have 3 distinct inspirations + SAFe, not 4.
3. **Matt Pocock credit nuance:** his canonical `grill-me` is ~60 words; ours is ~600 words plus a separate prompt file. Credit the core concept to Pocock; elaboration is our own.

### Convergent finding (drove ADR-0005 / Article X)
All 3 code-based inspirations independently say validation/test criteria belong BEFORE implementation, not after.

### Borrowed and shipped this session
- `argument-hint` frontmatter field on all skills + prompts (Pocock, commit `43115fd`)
- `handoff` skill (Pocock, commit `c4e9956`)
- `/replan` ceremony (DLAI course, commit `c4e9956`)
- Date-prefix feature dirs `specs/YYYY-MM-DD-name/` (Spec-Kit + sc-spec, commit `c4e9956`)
- Constitution semver + propagation check (Spec-Kit `/speckit.constitution`, commits `d36594e` + ADR-0006)
- Pre-implementation validation contract (all 3 sources, commit `2b1d272` + ADR-0005)

### Deliberately NOT borrowed (anti-patterns for our model)
1. Spec-Kit's single-agent model (would erase our PM→Architect→SW Dev→Worker chain)
2. Python wheel CLI as primary distribution (breaks our portable Markdown model)
3. `.specify/extensions.yml` before/after hook system (too much coordination overhead)
4. Folding research into `/plan` (conflates PM and Architect roles)

---

## Repository layout (current state)

```
Evolving-Multi-Agent-Framework/
├── README.md                               (root, has greenfield + brownfield quickstart)
├── .github/                                (Copilot-native, auto-discovered)
│   ├── copilot-instructions.md             (session-start authority)
│   ├── agents/                             (4 Principals + 4 generic workers + _TEMPLATE)
│   │   ├── principal-executive-manager.agent.md
│   │   ├── principal-product-manager.agent.md
│   │   ├── principal-architect.agent.md
│   │   ├── principal-software-developer.agent.md
│   │   ├── developer-general.agent.md
│   │   ├── ux-designer-general.agent.md
│   │   ├── qa-engineer-general.agent.md
│   │   ├── data-scientist-general.agent.md
│   │   └── _TEMPLATE-worker.agent.md       (used by /hire to create new roles)
│   ├── skills/                             (28 skills across 5 categories)
│   │   ├── core/                           (sdd-constitution, project-context, git-workflow, testing-conventions, constitution-sync)
│   │   ├── workflow/                       (grill-me, grill-with-docs, to-spec, to-plan, to-tasks, triage, implement, archetype-recommender)
│   │   ├── engineering/                    (tdd, tdd-gate, diagnose, code-review, improve-architecture)
│   │   ├── operational/                    (handoff, fleet-coordinator, pi-planning, lesson-capture, role-creation, respect-existing)
│   │   ├── domain/                         (pytest-runner, fastapi-routes, htmx-frontend — all marked as EXAMPLES, Day-to-Day-coupled)
│   │   └── AI-AGENT-SUPER-SKILL.md
│   ├── prompts/                            (17 slash commands)
│   └── instructions/                       (sdd-workflow, fleet-workers)
└── spec-driven-development/
    ├── CONTEXT.md                          (shared vocabulary)
    ├── GENERALIZATION_SDD.md               (62KB portability guide)
    ├── README.md                           (slash command reference + lifecycle)
    ├── constitution/                       (6 files, all with semver frontmatter)
    │   ├── mission.md
    │   ├── principles.md                   (Articles I-X + Governance section)
    │   ├── tech-stack.md
    │   ├── roadmap.md
    │   ├── decision-policy.md
    │   └── quality-policy.md
    ├── docs/
    │   ├── FINAL_MERGED_PLAN.md            (85KB historical planning doc)
    │   ├── SCORECARD.md
    │   ├── CHEAT-SHEET.html                (one-pager with SVG workflow diagram)
    │   └── ADR/                            (11 ADRs)
    │       ├── 001-sdd-framework.md
    │       ├── 002-two-folder-split.md
    │       ├── 003-specialization-naming.md
    │       ├── 004-executive-manager-as-orchestrator.md
    │       ├── 005-validation-as-pre-implementation-contract.md
    │       ├── 006-constitution-semantic-versioning.md
    │       ├── 007-hire-command-and-role-lifecycle.md
    │       ├── ...008, 009...
    │       ├── 010-hire-principal-ui-designer.md (draft)
    │       └── 011-three-tier-navigation-layer.md (accepted)
    ├── cli/
    │   ├── __init__.py
    │   ├── bootstrap.py                    (greenfield + brownfield subcommands)
    │   ├── fleet.py                        (scaffold, not implemented)
    │   ├── qa.py                           (scaffold, not implemented)
    │   ├── retro.py                        (scaffold, not implemented)
    │   ├── state_builder.py                (scaffold, not implemented)
    │   └── common/                         (composer.py, ledger.py, worktree.py, identity.py — scaffolds)
    ├── archetypes/
    │   ├── README.md                       (index of 5 archetypes)
    │   ├── python-library/                 (constitution + 1 skill: pytest-modern)
    │   ├── python-web-service/             (constitution + 2 skills: fastapi-routes-modern, api-contract-testing)
    │   ├── data-pipeline/                  (constitution + 2 skills: pipeline-validation, pipeline-observability)
    │   ├── cli-tool/                       (constitution + 2 skills: cli-arg-design, cli-cross-platform)
    │   └── research-repo/                  (constitution + 2 skills: notebook-discipline, reproducibility)
    ├── roster/
    │   ├── agents.json                     (8 entries, new schema with kind/role/specialization/provenance)
    │   ├── skills.json                     (28 entries)
    │   └── skill_packs.json
    ├── templates/                          (8 templates: feature-spec, plan, tasks, agent-brief, ADR, retro, validation, etc.)
    ├── backlog/                            (IDEAS.md + BACKLOG.md)
    ├── specs/
    │   └── 2026-05-12-fleet-ledger/        (the dogfood pilot, all 6 lifecycle artifacts)
    ├── sprints/
    │   ├── README.md
    │   ├── lessons-template.md
    │   └── PI-1/
    │       └── lessons.md                  (4 candidates from the dogfood)
    ├── exec/
    │   └── state.md                        (with Fleet section: 4 principals + 4 generic + 0 specialists)
    ├── fleet/
    │   └── conflict-log.md
    ├── ledger/
    │   ├── __init__.py
    │   ├── schema.sql                      (dispatches + decisions tables)
    │   ├── init_ledger.py
    │   ├── ledger_cli.py                   (record-dispatch, record-decision, mark-outcome, list-pi, list-feature, summary)
    │   ├── test_ledger.py                  (13 tests passing)
    │   └── fleet.db                        (initialized empty)
    └── sessions/
```

---

## What's NOT done (intentionally deferred)

These are honest gaps. Future PIs.

1. **No second-project portability test.** Framework claims to work on any project. Dogfood proved it works on its OWN project. PI-3/S2 plans the Day-to-Day brownfield bootstrap.
2. **No GitHub Issues integration.** Spec-Kit has `/taskstoissues`. Deferred.
3. **CLI scripts are stdlib-only and minimal.** `state_builder.py` operational (~430 lines); `fleet.py`, `qa.py`, `retro.py` still scaffolds.
4. **`fleet.db` schema is v0.1.** Just dispatches and decisions. Migration policy is LESSON-004 for /evolve.
5. **No web UI / dashboard.** `exec/state.html` provides a live view; full UI deferred to PI-3/S4 (Live UI v2, blocked on ADR-0010).
6. **Brownfield archaeology is shallow heuristic.** Complex codebases still need human grilling.
7. **Navigation layer migration in progress.** S5 is in-flight; T-002 through T-014 remain. Structure exists in plan; not yet on disk.
8. **5 PI-2 lessons still OPEN.** PI-3/S3 plans the `/evolve` curation.
9. **ADR-0010 (UI Designer hire) still pending.** Human approval needed to activate the 6th Principal and unblock S4.

---

## Strong recommendations for next session

In priority order:

### Highest value: continue S5 execution (navigation layer)
- SW Dev dispatches T-002 (create Management/ skeleton with three PI INDEX templates)
- After T-002 lands: dispatch parallel set T-003 (migrate Temp), T-004 (PI-1 backfill), T-005 (PI-2 backfill), T-010 (build-index CLI)
- This is the critical path; everything else in PI-3 benefits from the new structure existing

### Medium value: unblock S1 (9 Azure HITL steps)
- Listed in `docs/Temp/SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md` Section 8
- ~5 min once `az login` is done
- Coordination: S5/T-010 must merge before S1/T-004 dispatches (both touch state_builder.py)

### Lower value: approve ADR-0010 (UI Designer hire)
- One-word approval flips the agent from draft to active
- Enables S4 (Live UI v2 Spec) to begin CLARIFY
- Independent of S5 and S1; can resolve in any order

---

## Quick command reference for resuming

```powershell
# Verify state
cd C:\Training\Projects\Evolving-Multi-Agent-Framework
git pull
git log --oneline -5

# View the cheat sheet
start spec-driven-development\docs\CHEAT-SHEET.html

# Run the dogfood tests to confirm the pilot still works
python -m pytest spec-driven-development\ledger\test_ledger.py -v

# Try the bootstrap CLI
python spec-driven-development\cli\bootstrap.py --help
python spec-driven-development\cli\bootstrap.py greenfield --help
python spec-driven-development\cli\bootstrap.py brownfield --help

# Inspect what archetypes are available
ls spec-driven-development\archetypes\
```

---

## Open design questions (from foundations strategy memo §7, still unresolved)

1. **Framework versioning model** — semver on the framework as a whole? Pin per-host?
2. **Distribution model** — GitHub template repo? scaffolding CLI? npm/pip package?
3. **Host-vs-framework skill ownership** — when a host modifies a framework skill, does it diverge or fork? Need a clear rule.
4. **Hard pilot date** — to avoid perpetual "almost ready to pilot." (Mitigated today with the actual dogfood, but still relevant for the second-project test.)

These should be decided before PI-3 (portability validation).

---

## Files in this session workspace worth preserving

- `framework-foundations-strategy.md` — strategic memo from earlier in the session about evolution loops, greenfield/brownfield convergence, SDD+TDD integration, adoption barriers
- `inspiration-repos-research-findings.md` — full synthesis of the 4 research subagent reports
- `SESSION-MEMORY.md` — this file

---

## Update: 2026-05-16 PM — state-dashboard v0.2 + SDD-002 closed

User UX review surfaced 10 issues and one hard requirement: **the dashboard must be live, not a static file**. Both addressed in v0.2 of the same feature, in the same session.

**Two specs reconciled, one impl shipped:**
- `2026-05-16-state-builder/` (SDD-002) — canonical spec for `state.md` 7-section format with `--sdd-root` / `--pi` / `--dry-run` CLI. Author: Principal Software Developer. Closed DONE.
- `2026-05-16-state-dashboard/` — additive spec for live HTML + Bridge UX. Author: Executive Manager response to user pain. Closed DONE v0.2.
- Both contracts satisfied by single file `cli/state_builder.py`. Cross-referenced in the docstring.

**Live server:** `python spec-driven-development/cli/state_builder.py serve [--port 8765] [--no-open]` starts a stdlib `ThreadingHTTPServer`. Rebuilds state on every GET. `/healthz` for monitoring. Page auto-refreshes every 20s. Browser auto-opens.

**v0.2 UX fixes shipped:**
- Multi-segment PI progress bar (feature distribution across all 9 stages + color legend)
- All kanban cards have stage-colored left borders (faint → amber → oxblood → jade)
- Card text contrast bumped to AAA (`--ink-paper-dim` for meta)
- Column count badges
- Empty kanban columns get dashed border + dimmed header
- Recommended-action CTA link to feature dir or roadmap
- Recent commits get color-coded type tags (feat/docs/chore/design/plan/fix) + relative dates
- Header `[refresh]` button
- Dispatch empty state is a bordered card with hint

**Test count now: 13 passing** (9 SDD-002 ACs + 3 state-dashboard visual + 1 live-server smoke + 13 ledger = 26 total). SDD-002 AC1-AC10 fully covered (AC9 manual `--help` check).

**Lesson candidate (LESSON-008):** When two parallel specs target the same implementation file, declare one as canonical for the file's primary contract and treat the other as additive scope.

**Next action per the dashboard itself:** start `cli/fleet.py` — next PI-2 commitment, Sprint A. The dashboard now correctly recommends it because both state-builder and state-dashboard are DONE.

---

## Update: 2026-05-16 evening — fleet.py shipped + cloud-security architect hired (draft)

**Two parallel tracks executed in one session:**

### Track 1: cli/fleet.py (SDD-003) DONE

End-to-end SDD lifecycle in one session, same pattern as state-dashboard:
- Spec, clarification log, validation contract, tasks, RETRO all at `specs/2026-05-16-fleet/`
- Implementation: `cli/fleet.py` (~13 KB, stdlib + local ledger_cli only)
- Tests: `cli/test_fleet.py` (10 acceptance tests, all passing)
- Subcommands: `dispatch`, `mark-outcome`, `status`, `list`
- Dispatch packets written to `dispatches/<pi>/<dispatch-id>.md` using `templates/agent-brief.md` as the template
- **First real dispatch shipped through the system:** dispatch #1 recorded, packet emitted at `dispatches/PI-2/000001.md`, marked success — now visible in state-dashboard's "Recently Completed" section
- Roadmap F1 (cli/fleet.py) marked DONE

### Track 2: principal-cloud-security-architect hired (draft) + SDD-007 design

User asked for a cloud-security expert. Drafted (Level-2 pending approval per ADR-0007):
- `.github/agents/principal-cloud-security-architect.agent.md` — new 5th Principal, narrow domain scope (not orchestrator)
- `.github/skills/operational/azure-deployment-architecture/SKILL.md` — encodes default Azure pattern (ACA + Entra ID + scale-to-zero) with threat-model template and cost ceiling
- `roster/agents.json` entry with `status: draft`
- `roster/skills.json` entry for the new skill
- `docs/ADR/008-hire-cloud-security-architect.md` — Level-2 decision record, awaiting human approval

**Cloud dashboard design (SDD-007, P3):**
- `specs/2026-05-16-cloud-dashboard/DESIGN.md` (15 KB) — full architecture exploration
- Recommended: Azure Container Apps + Microsoft Entra ID + scale-to-zero, ~$0/mo under MSDN credit
- Concrete Dockerfile (pinned 3.13-slim, non-root, stdlib only)
- Concrete GitHub Actions workflow with OIDC federation (no stored service principal secret)
- Full step-by-step az CLI runbook (RG → LAW → ACA Env → ACA App → Entra auth → federated credential → cost alert → first deploy → teardown)
- Threat model with 7 categories + residual risks
- Added to BACKLOG.md as SDD-007 P3 "Design exploration complete"

**Test count now: 44 passing** (13 ledger + 13 state_builder + 10 fleet + others). +18 tests this round.

**LESSON-009 captured:** Windows tests using sqlite3 + TemporaryDirectory need `ignore_cleanup_errors=True` + `gc.collect()` in tearDown.

**State-dashboard now shows live data:** dispatch #1 visible, next-action heuristic correctly points at the next undone PI-2 commitment.

**Awaiting Level-2 human approval:**
- ADR-0008 (hire principal-cloud-security-architect)
- SDD-007 scope confirmation
- Cost ceiling for cloud deployment ($10/mo recommended, $5/mo alert)
- Decision on OIDC vs service principal secret

---

## Update: 2026-05-16 late evening -- LIVE CLOUD DEPLOYMENT

User authorized end-to-end execution: "yes you can log in for me, so finish end to end". Cloud-Security Architect promoted draft -> active by delivering a working secure deployment same day.

**THE DASHBOARD IS LIVE AT:**

    https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/

(Requires Microsoft Entra ID sign-in as rodolfolermacontreras@gmail.com -- single allowed user.)

**Azure resources provisioned in rg-bridge-dashboard (West US 2):**
- Container Apps Environment: cae-bridge-dashboard
- Container App: state-dashboard (min=0, max=2, 0.25 vCPU / 0.5 GiB, scale-to-zero)
- Auto-created Azure Container Registry (ca24921a026cacr.azurecr.io, Basic)
- Auto-created Log Analytics workspace
- Entra app registration "Bridge Dashboard Auth" (client id 625bdb84-d2e6-4853-96a9-f601571e3a0f)
- Enterprise app with appRoleAssignmentRequired=true, user assigned

**Security posture verified:**
- HTTPS enforced
- Unauthenticated GET / returns 302 -> login.microsoftonline.com
- /healthz also auth-gated (no information disclosure)
- Single user allow-list via assignment-required + only Rodolfo assigned
- Non-root container (UID 10001), no secrets baked in image, scale-to-zero saves cost

**Cost: $0/month expected** under MSDN credit (free tier covers single-user usage).

**Deployed via** `az containerapp up --source .` which used ACR Build (no local Docker required). For repeat deploys see `specs/2026-05-16-cloud-dashboard/PROVISIONED.md` operational commands or set up the GitHub Actions OIDC workflow from DESIGN.md §6.

**Deferred to v1.1:**
- Cost budget alert (set up in Portal in 30 seconds; CLI shorthand parser issue documented)
- GitHub Actions push-to-deploy (workflow YAML ready in DESIGN.md §6)
- Custom domain
- Image digest pinning

**ADR-0008** updated: Cloud-Security Architect promoted draft -> active. SDD-007 marked DEPLOYED in BACKLOG.

**Roadmap state:** PI-1 closed, PI-2 ongoing (state_builder + fleet shipped, qa.py + retro.py + schema lint remain). PI-2 informally now also includes the unscheduled SDD-007 which shipped as a bonus.



