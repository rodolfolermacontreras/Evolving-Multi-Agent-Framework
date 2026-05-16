# Session Memory — Evolving Multi-Agent Framework

**Date:** 2026-05-12 to 2026-05-13
**Owner:** Rodolfo Lerma
**Repo:** https://github.com/rodolfolermacontreras/Evolving-Multi-Agent-Framework
**Local path:** `C:\Training\Projects\Evolving-Multi-Agent-Framework`
**Final state:** 29 commits on origin/master, 28/28 todos done, working tree clean

---

## How to resume in a new session

1. Open `C:\Training\Projects\Evolving-Multi-Agent-Framework` in VS Code or your terminal.
2. Read **`INSTRUCTIONS.md` at the repo root** first (entry point for any agent).
3. It will direct you to read in this order:
   - `.github/copilot-instructions.md` (session-start authority)
   - `spec-driven-development/CONTEXT.md` (shared vocabulary)
   - `spec-driven-development/sessions/SESSION-MEMORY.md` (this file — most recent checkpoint)
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
| `23156a0` | feat(ux): add archetype-recommender skill + visual workflow diagram in cheat sheet (g1) |
| `8729706` | feat(fleet): add /hire command + role-creation skill (h1, ADR-0007) |
| `691c7eb` | docs: add CHEAT-SHEET.html one-pager for sharing |
| `ba738f3` | chore: consolidator — bump skill count to 26 after Wave 3 (respect-existing) |
| `e8bf182` | feat(archetypes): expand archetype library to 5 (s6) |
| `fc18361` | feat(bootstrap): add brownfield subcommand with archaeology pass + respect-existing skill (s4) |
| `9ace815` | feat(ledger): fleet ledger v0.1 — first feature shipped through SDD lifecycle (p2 pilot) |
| `0773379` | chore: consolidator — register Wave 1+2 skills/prompts in roster, README table, copilot-instructions |
| `d36594e` | feat(constitution): add semantic versioning + propagation check (b5, ADR-0006) |
| `fbac302` | feat(bootstrap): add greenfield bootstrap script + python-library archetype (s3) |
| `e4ff074` | feat: project-to-framework evolution loop — lessons + /evolve + lesson-capture (s5) |
| `43115fd` | docs(skills): add argument-hint frontmatter field to skills and prompts (b3) |
| `c4e9956` | feat: add date-prefix feature dir convention + handoff skill + /replan ceremony |
| `2b1d272` | feat(constitution): bind TDD + pre-implementation validation contract (Article X, ADR-0005) |
| `6825943` | docs: fix inspirations attribution (Spec-Kit is GitHub; sc-spec is DLAI companion) |
| `946a224` | docs(constitution): rewrite principles.md as framework articles (closes PI-1 generalization) |
| `68d229a` | feat(agents): promote Executive Manager to orchestrator and single human entry point (ADR-0004) |
| `bafe0d5` | docs: add root README and annotate Day-to-Day domain skills as examples |
| `6dac9d7` | docs: generalize constitution and CONTEXT to describe framework, not Day-to-Day host |

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
    │   └── ADR/                            (7 ADRs)
    │       ├── 001-sdd-framework.md
    │       ├── 002-two-folder-split.md
    │       ├── 003-specialization-naming.md
    │       ├── 004-executive-manager-as-orchestrator.md
    │       ├── 005-validation-as-pre-implementation-contract.md
    │       ├── 006-constitution-semantic-versioning.md
    │       └── 007-hire-command-and-role-lifecycle.md
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

1. **No second-project portability test.** Framework claims to work on any project. Dogfood proved it works on its OWN project. PI-3 milestone: bootstrap onto a totally different stack to validate.
2. **No GitHub Issues integration.** Spec-Kit has `/taskstoissues`. Deferred.
3. **CLI scripts are stdlib-only and minimal.** Work but not pretty. Polish is PI-2 work.
4. **`fleet.db` schema is v0.1.** Just dispatches and decisions. Migration policy is LESSON-004 for /evolve.
5. **No web UI / dashboard.** Everything is files + Copilot Chat. Future feature.
6. **Brownfield archaeology is shallow heuristic.** Complex codebases still need human grilling for hidden conventions, undocumented agreements, deploy quirks.
7. **`/replan` and `/evolve` exist but never been run for real.** Framework's own retro on the dogfood is captured in PI-1 lessons.md but not yet curated.
8. **No `/hire` ever actually invoked.** Mechanism exists, never exercised.
9. **CLI scaffolds (fleet.py, qa.py, retro.py, state_builder.py) still empty.** Their functionality is provided through the agent/skill/prompt layer today; CLI implementations would be future polish.

---

## Strong recommendations for next session

In priority order:

### Highest value: actually use the framework on a real project
- Pick a small new internal tool (1-week scope) OR a focused refactor in an existing project
- Run `bootstrap.py greenfield` (with archetype-recommender) OR `bootstrap.py brownfield --draft-only`
- Walk one feature end-to-end through the lifecycle
- Run `/replan` after DONE
- File real frustrations as lessons via `lesson-capture` skill
- This is the second dogfood — proves portability

### Medium value: close the open loops on the dogfood
- Run `/replan` against the fleet-ledger pilot
- Curate the 4 LESSON-* candidates in `spec-driven-development/sprints/PI-1/lessons.md` via `/evolve`
- Mark PI-1 as DONE in roadmap.md, define PI-2 scope
- This validates the evolution loop end-to-end (project → framework feedback)

### Lower value: tactical polish
- Implement the CLI scaffolds (fleet.py, qa.py, retro.py, state_builder.py)
- Write more domain skills as projects demand them
- Consider GitHub Issues bridge (`/taskstoissues` from Spec-Kit)

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



