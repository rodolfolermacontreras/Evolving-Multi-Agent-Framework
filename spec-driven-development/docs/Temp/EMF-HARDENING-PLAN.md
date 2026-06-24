---
title: EMF Hardening Plan — Make the Framework Practical and Team-Portable
status: proposed
owner: principal-executive-manager
audience: developers and agents working on the Evolving Multi-Agent Framework
created: 2026-06-24
source-review: external principal-level repo audit (master branch)
---

# EMF Hardening Plan

This is the work plan to take the Evolving Multi-Agent Framework from "works for
its author" to "a teammate clones the repo, runs one command, and is building
their own project with it the same day." It is written for both the humans and
the agents who will execute it. No emojis (Rule 1).

It is grounded in a file-by-file audit of `master`. Every claim below cites real
evidence (file, line count, row count) so nobody has to take it on faith.

---

## 1. Bottom line up front

The framework is real and well-tested (353 tests, a working CLI suite, a genuine
validation-first habit). Two things hold it back:

1. **It promises more than it delivers, and the proof is empty.** The headline
   promise — "every dispatch is a ledger row; who did what and when is always a
   ledger row" (Article VII) — is contradicted by the ledger itself: `fleet.db`
   holds **11 dispatch rows and 2 decision rows, none after PI-2**. Four whole
   PIs logged nothing. The most-advertised audit trail is near-empty.

2. **Almost nothing is enforced, and the repo is glued to one person.** Only
   frontmatter validation is real code, and even that only runs when invoked by
   hand (there is **no `.github/workflows/` and no CI**). The personal ledger
   `fleet.db` is committed, so a teammate inherits the author's rows. There are
   **93 "Rodolfo" references**, `author: rodolfolermacontreras` in nearly every
   skill, and origin-project leakage (`engine.py`, FastAPI, Day-to-Day) in 22
   framework files. A teammate clones the author's fingerprints, not a clean
   tool.

Neither requires a rebuild. The bones are solid. This plan makes the framework
keep its own promises and detach from its author's machine and identity.

---

## 2. Definition of done for this effort

This plan is complete when both statements are true and provable:

- **Truly practical:** the rules the framework claims to follow are either
  enforced by code that blocks on violation, or the claim is downgraded to match
  reality. No promise in the constitution is contradicted by the data in the
  repo. The ledger is populated by real work.
- **Truly team-portable (our definition):** a teammate on VS Code + Copilot CLI
  runs `git clone` then one setup command and gets a clean, personalized,
  self-checking working copy with no trace of the author's identity, ledger
  history, or origin project. "Portable" here means *pull-and-run for the team*,
  not cross-runtime.

---

## 3. How to read the work items

Each item has the same shape so agents can route it straight into the lifecycle:

- **ID / Title**
- **Problem** — what is wrong, in one line.
- **Evidence** — the file, count, or line that proves it. Verify before acting.
- **Change** — what to do.
- **Acceptance** — checkable criteria. These become the `validation.md` contract
  (Article X). Write them before implementing.
- **Effort** — S (<half day), M (1-2 days), L (a dedicated sprint).
- **Risk** — what could go wrong doing it.
- **Lock it in** — the check or test that stops this regressing. If an item has
  no "lock it in," it will rot.

Items are grouped: **Part A** detaches the repo from the author (portability),
**Part B** makes promises true (practical leverage), **Part C** maintainability,
**Part D** cleanup. Suggested sequencing is in Section 8.

---

## Part A — Team portability (pull-and-run, no author fingerprints)

### A-1. Stop committing the personal ledger
- **Problem:** a teammate clones the author's `fleet.db` instead of starting
  clean.
- **Evidence:** `git ls-files` lists `spec-driven-development/ledger/fleet.db`;
  `.gitignore` does not exclude it. The committed DB has 11 author rows.
- **Change:** add `spec-driven-development/ledger/fleet.db` (and `*.db`,
  `*.db-wal`, `*.db-shm`) to `.gitignore`; `git rm --cached` the file; have setup
  (A-4) create a fresh DB from `ledger/schema.sql` via `init_ledger.py` on first
  run.
- **Acceptance:**
  - [ ] `fleet.db` is not tracked by git.
  - [ ] A fresh clone has no `fleet.db` until setup runs.
  - [ ] After setup, `fleet.db` exists with 0 dispatch rows and the correct schema.
- **Effort:** S. **Risk:** low — the schema and `init_ledger.py` already exist;
  only the seed data is lost, which is the point.
- **Lock it in:** a `schema_lint`/`doctor` check that fails if `fleet.db` is
  tracked.

### A-2. Make the owner/identity a config value, not a hardcoded name
- **Problem:** the framework is welded to one human as owner and "single user."
- **Evidence:** 93 "Rodolfo" hits across `.md`/`.py`; `INSTRUCTIONS.md` line 5
  ("Owner: Rodolfo Lerma"); `principal-product-manager.agent.md` ("a single
  user: Rodolfo Lerma"); `author: rodolfolermacontreras` in nearly every
  `SKILL.md` frontmatter.
- **Change:** introduce one `project.config.json` (or `constitution/owner.md`)
  holding `owner`, `team`, `repo_url`. Replace hardcoded names in agent files,
  `INSTRUCTIONS.md`, and the PM "single user" line with a reference to that
  value. Change skill `author:` frontmatter to a neutral value
  (`emf-framework`) or read it from config. Setup (A-4) prompts for owner and
  fills it in.
- **Acceptance:**
  - [ ] No framework file (agents, skills, constitution, INSTRUCTIONS) contains a
        hardcoded personal name; all owner references resolve to config.
  - [ ] The PM agent traces value to "the host project's owner," not a person.
  - [ ] A grep for the author's name across non-historical files returns 0 hits.
        (Historical `specs/`, `sprints/`, retros, ADRs may keep their record.)
- **Effort:** M. **Risk:** medium — easy to miss occurrences; the lock-in check
  is what makes it safe.
- **Lock it in:** A-6 origin-token lint, extended to personal-name tokens.

### A-3. Scrub origin-project leakage out of generic files
- **Problem:** the "generic" framework still teaches the Day-to-Day Agent project.
- **Evidence:** `Rodolfo Lerma|engine.py|Day-to-Day|Outlander|FastAPI|World State|743`
  hits **22 framework files** — all 8 agent definitions, 7 core/engineering/
  workflow skills, and 3 of 6 constitution files. `principal-architect.agent.md`
  still carries the "Lazy singleton | `agent/engine.py`" table; `README.md`
  recounts the FastAPI/HTMX origin as if it were framework guidance.
- **Change:** move origin-specific examples into either (a) the host-project
  archetype where they belong, or (b) a clearly labeled `examples/` section.
  Replace in-place examples in agents/skills/constitution with stack-neutral
  ones. Keep the origin story in `README` as history, clearly marked, not as
  instruction.
- **Acceptance:**
  - [ ] The 22 flagged files contain no origin tokens outside a labeled
        "example/history" block.
  - [ ] `principal-architect.agent.md` design examples are stack-neutral.
  - [ ] A new teammate reading any agent or core skill cannot tell which project
        the framework came from.
- **Effort:** M. **Risk:** medium — over-scrubbing can remove useful concrete
  examples; replace, do not just delete.
- **Lock it in:** A-6.

### A-4. One setup command: clone -> productive
- **Problem:** there is no single "you are ready" command. README points to
  "open the EM agent" plus a manual `bootstrap.py greenfield ...` aimed at *new
  host projects*, not at making *this repo* usable on a fresh machine.
- **Evidence:** `README.md` quickstart (lines 19-27); `bootstrap.py` personalizes
  new host projects but does nothing for a teammate who just cloned EMF itself.
- **Change:** add a `make setup` target (and a `bootstrap.py setup` subcommand it
  calls) that, idempotently: verifies Python version; creates `.venv` if absent;
  initializes a fresh `fleet.db` (A-1); installs the commit-msg hook (opt-in made
  one-step); prompts for and writes owner config (A-2); runs `schema_lint` and
  the test suite; prints a green "you are ready, here is your first command"
  message.
- **Acceptance:**
  - [ ] On a clean clone, a single command leaves the repo lint-clean,
        test-passing, with a fresh ledger and personalized owner.
  - [ ] Re-running it is safe (idempotent) and reports current health.
  - [ ] The README quickstart is reduced to: clone, run setup, talk to the EM
        agent.
- **Effort:** M. **Risk:** low-medium — keep it stdlib + make only; do not add a
  package manager dependency.
- **Lock it in:** this command *is* the lock-in for A-1, A-2, A-5; it should fail
  loudly if any of them regress.

### A-5. A `doctor` / health check teammates can trust
- **Problem:** nothing tells a teammate whether their checkout is healthy.
- **Evidence:** no CI, no health command; `state.html` can silently show stale
  data (the PI-6 anchor complaint).
- **Change:** add `bootstrap.py doctor` (or `make doctor`) that checks: ledger
  reachable and untracked; schema_lint clean; constitution semver consistent
  (B-3); RULES.md article range matches principles.md (B-3); no origin tokens
  (A-6); tests pass. Output a one-screen green/red report.
- **Acceptance:**
  - [ ] `doctor` exits non-zero on any failed check with a specific reason.
  - [ ] `doctor` is the same set of checks CI runs (B-4), so local == CI.
- **Effort:** M. **Risk:** low.
- **Lock it in:** wired into CI (B-4).

### A-6. Origin-token and identity lint
- **Problem:** scrubs (A-2, A-3) decay the moment someone pastes an old example.
- **Change:** add a `schema_lint` rule (or standalone `origin_lint.py`) that
  fails if any file under `.github/` or `constitution/` contains a configurable
  denylist (personal names, `engine.py`, origin project names, hardcoded host
  paths). Allow an explicit `<!-- example: ... -->` escape for labeled blocks.
- **Acceptance:**
  - [ ] Adding the author's name to an agent file fails the lint.
  - [ ] Labeled example blocks pass.
- **Effort:** S. **Risk:** low — tune the denylist to avoid false positives.
- **Lock it in:** itself, run in `doctor` and CI.

---

## Part B — Practical leverage (make the promises true or retract them)

### B-1. Make the ledger true — THE priority item
- **Problem:** the central audit-trail promise is contradicted by the data.
- **Evidence:** Article VII and RULES Rule 4 claim universal dispatch logging.
  `fleet.db`: 11 dispatch rows, all `outcome='success'`, only agents
  `developer-general` and `dedup-scanner`, only `pi` values `PI-2` and `N/A`;
  nothing from PI-3..PI-6. RULES Section 4 ("What counts as DONE") requires a
  ledger row, yet four PIs closed without one.
- **Change (pick one and commit):**
  - **Option 1 (make it real):** make `fleet.py mark` a required close step.
    A feature/sprint cannot be stamped DONE until its dispatch outcomes are in
    the ledger. The `/qa` and `/retro` flows write rows; `doctor` warns if the
    current PI has zero rows.
  - **Option 2 (right-size the claim):** rewrite Article VII and Rule 4 to
    "fleet-dispatched work is logged in the ledger" and remove the universal
    "who did this and when is always a ledger row" language; remove the ledger
    line from the DONE checklist.
- **Acceptance:**
  - [ ] If Option 1: closing a feature with unlogged dispatches fails a check;
        the current PI shows real rows in `state.html`.
  - [ ] If Option 2: no constitution/RULES sentence claims universal logging;
        `doctor` does not require ledger rows.
  - [ ] Either way: no promise about the ledger is contradicted by `fleet.db`.
- **Effort:** M. **Risk:** Option 1 adds friction (mitigate: make logging a
  one-liner in the close flow); Option 2 reduces an aspiration to honesty.
- **Lock it in:** the close-gate check (Opt 1) or `doctor` consistency check
  (Opt 2).

### B-2. Turn the rules you actually care about into blocking checks
- **Problem:** the methodology is honor-system prose; an agent under pressure can
  ignore it with no consequence.
- **Evidence:** `tdd-gate` is a prose `SKILL.md` referenced by **zero** agents or
  prompts; two-stage review order, file-scope (1-3 files), HITL gates, and the
  DONE checklist are all text, not code. Only `schema_lint.py` is enforcing.
- **Change:** pick the two or three rules with the highest payoff and make them
  real, fast checks (stdlib, runnable locally and in CI). Strong candidates:
  - **TDD gate:** a script that, given a diff/commit range, fails if production
    paths changed without a corresponding test change and no `[NO-TEST-NEEDED]`
    tag. (The prose logic already exists in `tdd-gate/SKILL.md` step "Mechanical
    Check"; turn it into code.)
  - **File-scope:** a check that flags a single dispatch/commit touching more
    than 3 production files without escalation.
  - **DONE completeness:** a check that a closed feature dir has spec, validation
    (all REQUIRED boxes checked), and RETRO.
- **Acceptance:**
  - [ ] At least two named rules now fail a command when violated.
  - [ ] The corresponding prose skills point at the enforcing script.
  - [ ] Each enforced rule has tests proving it catches a real violation.
- **Effort:** M-L. **Risk:** false positives erode trust; start with the TDD gate
  where the logic is already specified, tune thresholds, expand later.
- **Lock it in:** these checks run in `doctor` and CI.

### B-3. Make governance keep its own cross-references straight
- **Problem:** governance ceremony does not even hold itself consistent.
- **Evidence:** `principles.md` (v1.3.0) declares "Twelve binding articles"
  (I-XII); `RULES.md` (v1.1.0) still names the source as "Articles I-X." XI and
  XII were added without RULES.md following, despite Article VIII promising a
  `constitution-sync` propagation scan that flags NEEDS-UPDATE. The promised scan
  did not catch a file that literally enumerates the article range.
- **Change:** add a check that asserts (a) `RULES.md` article range == the article
  count in `principles.md`; (b) every `version:`/`last_amended:` pair across the
  six constitution files and RULES.md is internally consistent with the latest
  amendment. Fix the current RULES.md drift as part of this.
- **Acceptance:**
  - [ ] RULES.md references Articles I-XII.
  - [ ] Adding an article to `principles.md` without updating RULES.md fails the
        check.
- **Effort:** S. **Risk:** low.
- **Lock it in:** the check itself, in `doctor` and CI.

### B-4. Add CI so the checks fire for everyone, every push
- **Problem:** every enforceable check only runs when someone remembers to.
- **Evidence:** no `.github/workflows/` exists; `hooks/commit-msg` says it is
  "NEVER auto-installed and NOT enforced by CI"; `ADR-009` references CI that is
  not present in the repo.
- **Change:** add one GitHub Actions workflow that runs the exact `doctor` set
  (tests + schema_lint + B-2 checks + B-3 consistency + A-6 origin lint) on push
  and PR. Local `doctor` and CI must run the identical command so they never
  diverge.
- **Acceptance:**
  - [ ] A PR that breaks any enforced rule is red.
  - [ ] CI and `make doctor` invoke the same entrypoint.
  - [ ] ADR-009 either reflects the real workflow or is superseded.
- **Effort:** M. **Risk:** low; keep the workflow minimal and stdlib-friendly.
- **Lock it in:** this is the team-wide lock-in for Part B.

---

## Part C — Maintainability

### C-1. Break up the `state_builder.py` god-module
- **Problem:** the dashboard generator is unmaintainable and will cost future
  hours.
- **Evidence:** 3082 lines, 56 top-level functions; `render_markdown` is 762
  lines and `render_html` is 658 lines (46% of the file in two functions); 186
  lines of hand-concatenated HTML f-strings; the file also contains an HTTP
  server (`DashboardHandler`, `serve`), a doc-counter, and a work-index builder.
- **Change:** split into modules: data assembly (load_* functions), markdown
  render, html render, http server, doc-count, work-index. Decompose the two
  giant render functions into per-section functions. Keep behavior identical;
  the 135 existing `test_state_builder` tests are the safety net.
- **Acceptance:**
  - [ ] No function exceeds ~120 lines.
  - [ ] HTTP server and doc-counter live in their own modules.
  - [ ] All existing tests still pass with no assertion changes.
- **Effort:** L. **Risk:** medium — pure refactor; do it behind the test suite,
  one section at a time, commit per extraction.
- **Lock it in:** a simple max-function-length lint (optional) and the test suite.

### C-2. Right-size the stdlib-only rule where it hurts
- **Problem:** the stdlib-only constraint is producing worse code inside the
  renderer, not leaner code.
- **Evidence:** the 1420 lines of hand-rolled rendering exist largely to avoid a
  templating dependency; PI-6 ROAM already concedes the auto-refresh awkwardness
  ("polling wastes CPU and file-watch needs `watchdog`").
- **Change:** keep stdlib-only as the *distribution* guarantee, but allow a
  factored-out `string.Template`-based (still stdlib) rendering layer, or
  formally decide via ADR whether a single templating dependency is worth it for
  the dashboard only. Document the decision either way.
- **Acceptance:**
  - [ ] An ADR records the decision and its trade-off.
  - [ ] If kept stdlib: rendering is factored so it is no longer one 700-line
        f-string wall.
- **Effort:** S (decision) + folds into C-1. **Risk:** low.
- **Lock it in:** ADR + C-1.

### C-3. Replace the hardcoded grandfather date
- **Problem:** a hardcoded cutover date is an env/time coupling.
- **Evidence:** `fleet.py` `ARTICLE_XI_CUTOVER = "2026-06-08"`.
- **Change:** move the cutover to config or derive it; document why it exists.
- **Acceptance:** [ ] no hardcoded calendar dates in CLI logic without a config
  source and comment.
- **Effort:** S. **Risk:** low.

---

## Part D — Cleanup and kill list

### D-1. Delete or wire the 10 dead skills
- **Problem:** a quarter of the skill library is referenced by nothing, which
  implies capability/enforcement that does not exist.
- **Evidence:** zero references from any agent/prompt/instruction for: `diagnose`,
  `grill-with-docs`, `host-integration-symlink`, `lesson-capture`,
  `respect-existing`, `session-self-review`, `stakeholder-pressure-defense`,
  `to-plan`, `weekly-status-report`, and `tdd-gate`.
- **Change:** for each, either wire it into the agent/prompt that should use it,
  or delete it. Start with `tdd-gate` — once B-2 turns it into a real check,
  reference it from the SW Dev review flow; an unreferenced enforcement skill is
  worse than none.
- **Acceptance:** [ ] every shipped skill is referenced by at least one agent or
  prompt, or is removed.
- **Effort:** S-M. **Risk:** low. **Lock it in:** a `schema_lint` rule that flags
  unreferenced skills.

### D-2. Add a lightweight-spec path for small features
- **Problem:** the four-document lifecycle is too heavy for small changes; the
  project's own RETRO says so.
- **Evidence:** `specs/2026-05-12-fleet-ledger/RETRO.md`: "Lifecycle artifact
  volume is high for a small CLI ... spec, plan, tasks, and validation each
  needed similar references" (LESSON-001/003). Article VI already authorizes
  lighter ceremony for <5-file features.
- **Change:** implement the lightweight path Article VI promises: one combined
  doc (story + requirements + validation contract) for small features, with
  cross-links instead of four near-duplicate files.
- **Acceptance:** [ ] a <5-file feature can complete the lifecycle with one
  combined artifact and still satisfy Article X (validation before
  implementation).
- **Effort:** M. **Risk:** low — do not weaken the validation lock, only collapse
  duplication.

### D-3. Rename "parallel dispatch with conflict detection"
- **Problem:** the words over-claim the code.
- **Evidence:** `fleet.py` conflict handling is `_scan_lock_state` deriving a
  single CLARIFY holder and single SPEC holder (a serial per-phase lock); there
  is no file-dependency graph. `roadmap.md` admits "Conflict-detection workflow
  validated against a real two-worker collision (deferred)."
- **Change:** rename to "serial CLARIFY/SPEC gate" everywhere; if a true
  file-overlap detector is wanted, file it as an honest backlog item.
- **Acceptance:** [ ] no doc claims conflict detection the code does not perform.
- **Effort:** S. **Risk:** low.

---

## 4. Enforced vs aspirational (reference table)

Keep this table honest as the plan lands. Today:

| Promise | Source | Status today | After this plan |
|---|---|---|---|
| Frontmatter contract valid | Article VII / FDC-001 | Enforced (manual) | Enforced in CI (B-4) |
| Agent/skill/prompt frontmatter | schema_lint | Enforced (manual) | Enforced in CI |
| Article XII ui-variant deltas | Article XII | Enforced (manual) | Enforced in CI |
| Serial CLARIFY/SPEC lock | Article XI | Partial (fleet.py only) | Documented honestly (D-3) |
| Conventional commits | Rule 6 | Opt-in only | One-step install via setup (A-4) |
| TDD gate / test-first | Article X, Rule 2 | Honor system | Enforced check (B-2) |
| File-scope 1-3 files | Article IV | Honor system | Enforced check (B-2) |
| DONE completeness | RULES Section 4 | Honor system | Enforced check (B-2) |
| Dispatch logged to ledger | Article VII | Falsified in practice | True or retracted (B-1) |
| Constitution self-consistency | Article VIII | Aspirational (RULES drift) | Enforced check (B-3) |
| Conflict detection | roadmap | Over-claimed | Renamed to match code (D-3) |
| CI enforcement | ADR-009 | Absent | Present (B-4) |

---

## 5. What "good" looks like at the end

- A teammate runs `git clone` + `make setup` and within minutes has a clean,
  personalized, lint-clean, test-passing checkout with their own empty ledger and
  no trace of anyone else.
- `make doctor` (and CI) is green, and a teammate can break a rule on purpose and
  watch it go red.
- The dashboard reads a ledger that is actually being filled by the work.
- The constitution says nothing the repo contradicts.
- No file teaches the origin project as if it were the framework.

---

## 6. The single most important move

If only one thing gets done first, do **B-1 (make the ledger true or retract the
claim)**. It is the clearest case of the framework promising what it does not
deliver, it is a few hours of work, and it is the difference between a teammate
trusting the framework in the first hour and quietly concluding the process is
paperwork. Everything else is refactor or cleanup; B-1 is credibility.

If you want the fastest visible "this is a team tool now" win in parallel, ship
**A-1 + A-4** (gitignore the ledger, one setup command) — that is the literal
clone-and-run experience your team will judge it by.

---

## 7. Suggested sequencing (one PI, four sprints)

- **Sprint 1 — Detach (smallest, highest trust):** A-1, A-4, A-5, A-6, B-3.
  Outcome: a teammate can clone-and-run on a clean machine; governance is
  self-consistent. This is the slice to demo first.
- **Sprint 2 — Make promises true:** B-1, B-2 (start with TDD gate), B-4 (CI).
  Outcome: the ledger is real and the rules you care about block on violation,
  for everyone, on every push.
- **Sprint 3 — De-author the content:** A-2, A-3, D-1, D-3. Outcome: no personal
  fingerprints, no dead skills, no over-claims.
- **Sprint 4 — Maintainability and right-sizing:** C-1, C-2, C-3, D-2. Outcome:
  the god-module is gone and small features stop drowning in ceremony.

Each sprint follows the framework's own lifecycle: CLARIFY -> SPEC (with the
`validation.md` contract built from the Acceptance boxes above) -> PLAN -> TASKS
-> IMPLEMENT -> REVIEW -> DONE, with a ledger row per dispatch (which, after
B-1, is mandatory and dogfoods the fix).

---

## 8. Note to the agents executing this

- Treat every "Acceptance" block above as the seed of that feature's
  `validation.md`. Write it before implementing; lock it at `/tasks` (Article X).
- Do not silently drop an item. If an item is wrong on closer inspection, file a
  clarification and surface it, do not skip it.
- Verify each "Evidence" line against the live repo before acting; this plan was
  written against `master` at review time and the tree may have moved.
- This plan is itself an exercise in the framework keeping its promises. If a
  step here cannot be made true, that is a finding, not a footnote.
