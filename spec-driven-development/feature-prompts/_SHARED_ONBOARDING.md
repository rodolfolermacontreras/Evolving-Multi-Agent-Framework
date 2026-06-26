# Shared Onboarding -- Read this first

Every `F-##-*.prompt.md` and `SPRINT-##-KICKOFF.prompt.md` in this folder begins
by pointing you here. Load these rules once, then go execute your feature.

You are working on the **Evolving Multi-Agent Framework** -- the meta-recursive
spec-driven framework that builds itself.

- Repo root: `C:\Training\Projects\Evolving-Multi-Agent-Framework`
- Default branch: `master` (we work directly on `master`; **no `integration/`
  branch, no PR workflow** -- single-developer convention)
- GitHub: <https://github.com/rodolfolermacontreras/Evolving-Multi-Agent-Framework>
- Owner: Rodolfo Lerma (Senior Data Scientist, L63, Microsoft WWIC Central Analytics)

---

## 1. Required reading (in this order, every session)

1. [.github/copilot-instructions.md](../../.github/copilot-instructions.md) --
   session-start authority. Project identity, history, conventions, structure.
2. [spec-driven-development/CONTEXT.md](../CONTEXT.md) -- shared vocabulary.
3. [spec-driven-development/constitution/principles.md](../constitution/principles.md)
   -- the 10 binding articles. Article VII has the "one feature, one session"
   corollary; live it.
4. [spec-driven-development/constitution/decision-policy.md](../constitution/decision-policy.md)
   -- Level 0/1/2 authority + Friction Analysis requirement for Level-2.
5. [spec-driven-development/constitution/quality-policy.md](../constitution/quality-policy.md)
   -- the test, lint, and review gates.
6. [spec-driven-development/sessions/SESSION-MEMORY.md](../sessions/SESSION-MEMORY.md)
   -- latest durable checkpoint. **Verify against git -- the EM has caught stale
   checkpoints (e.g. 2026-06-05 false "62 failing tests" flag from a 2026-06-03
   checkpoint).**
7. [spec-driven-development/exec/state.md](../exec/state.md) -- DERIVED snapshot.
   Treat as descriptive, not authoritative. Regenerate before trusting:
   `python spec-driven-development/cli/state_builder.py`.
8. [spec-driven-development/exec/sprint-progress.md](../exec/sprint-progress.md)
   -- append-only worker ledger. **Real test baseline lives here.**
9. The spec dir for your feature (named in your prompt's section 3) -- full
   context.

Then run, to see live state:

```powershell
cd C:\Training\Projects\Evolving-Multi-Agent-Framework
git --no-pager log --oneline -10 --decorate
git status --short
git worktree list
python -m pytest spec-driven-development/ --tb=no -q 2>&1 | Select-Object -Last 3
```

If `git status --short` shows uncommitted work from a previous session, **stop
and surface it** before adding anything new.

---

## 2. The framework lifecycle (where your feature fits)

```
IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
```

Each phase has an owner:

| Phase | Owner | Slash command |
|-------|-------|---------------|
| IDEA | Executive Manager (captures verbatim) | -- |
| BACKLOG | Principal Product Manager | `/triage` |
| CLARIFY | PM + Architect | `/clarify` |
| SPEC | Principal Architect | `/spec` |
| PLAN | Architect + Software Developer | `/plan` |
| TASKS | Principal Software Developer | `/tasks` |
| IMPLEMENT | Workers (dispatched by SW Dev) | `/implement` or `cli/fleet.py dispatch` |
| REVIEW | PM (acceptance) + SW Dev (code review) | `/qa` |
| RETRO | Sprint lead | `/retro` |

Your prompt tells you which phase(s) you own. **Do not run a phase that is not
yours.** If you reach a phase boundary, hand off (label the handoff in
`sprint-progress.md`) and let the next session pick it up.

---

## 3. The Articles (load-bearing rules; full list in `principles.md`)

The ones most worker sessions touch:

- **Article I -- Validation Discipline.** Every feature has a
  `validation.md`. Zero unchecked REQUIRED items before DONE.
- **Article II -- Spec Sizing.** Bug fix <3 files = no spec, just task + test +
  review. Feature <5 files = lightweight spec. Feature >=5 files OR
  cross-cutting/schema = full spec + ADR + Level-2 Friction Analysis.
- **Article IV -- Test Discipline.** Full suite green before every commit.
  Baseline only goes up.
- **Article V -- Stdlib-Only CLI.** `cli/**` uses Python stdlib only. No
  third-party dependencies. (LESSON-001 / CLI-PATTERN rule 1.)
- **Article VII -- One Feature, One Session.** Do not contaminate context.
  Reuse a session ONLY for the same feature, EM-level routing/status, or true
  one-off edits (<3 files). For a different feature, run it in its own
  context-isolated unit -- a fresh chat session OR an EM-routed subagent
  dispatch (both satisfy the context-isolation property).
- **Article VIII -- Constitution Immutability.** No edits to `constitution/**`
  without an ADR. Route any constitution change to the Architect.
- **Article X -- Validation Contract.** Locked at `/tasks`; cannot be loosened
  during `/implement`.

---

## 4. Git workflow (this repo's convention)

- Work directly on `master`. There is no `integration/` branch.
- **Worktrees are optional.** They are only useful when two workers need to
  edit truly disjoint files in parallel. PI-4 has used zero worktrees. If your
  prompt does not call for one, do not create one.
- **Stage by explicit path.** **Never `git add -A`** while another session has
  uncommitted work in the tree. Always run `git status --short` first.
- **Commit message format**: `<type>(<scope>): <short>` then a body paragraph.
  Types in use: `feat`, `fix`, `docs`, `chore`, `plan`, `triage`, `close`,
  `ideas`, `retro`, `spec`, `tasks`.
- **Co-author trailer** when an agent participated:
  `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
- Push to `origin/master` when a logical unit closes (a feature, a sprint
  section). Do not push partial work.

---

## 5. Test discipline

- Run the full suite before every commit:
  `python -m pytest spec-driven-development/ --tb=no -q`
- Current baseline: **152 passing** as of HEAD `ae603c4` (2026-06-05). Verify
  before you start; the live number is what matters.
- If a test fails, fix it before moving on. Do not commit on red.
- If you add code, you add tests. New behaviour without new tests is a Level-1
  review fail.

---

## 6. CLI conventions (only if your feature touches `cli/**`)

Read [docs/CLI-PATTERN.md](../docs/CLI-PATTERN.md) before writing any CLI code.
Required pattern:

- Stdlib only (`argparse`, `sqlite3`, `pathlib`, `json`, `sys`, `os`).
- `main(argv)` signature for testability.
- Subcommands via `argparse` subparsers.
- Exit codes: 0 success, 1 validation failure, 2 usage error.
- Tests in `cli/test_<module>.py`, one test per acceptance criterion.

---

## 7. Definition of Done (every feature)

A feature is DONE when, in order:

1. All REQUIRED items in `validation.md` are checked.
2. Full test suite passes (>= baseline).
3. Files changed are committed with the proper commit message.
4. `sprint-progress.md` has a result block appended.
5. `state_builder.py` has been rerun and `exec/state.md` regenerated.
6. The sprint lead has been notified (or, if you are the sprint lead, the next
   feature in the sprint can start).

For a sprint to close DONE, every feature in it must be DONE, plus:

7. A retro block has been added to `sprints/PI-N/CURRENT_PI.md` (or a separate
   retro file under `sprints/PI-N/`).
8. Owner has explicitly approved the close.

---

## 8. Reporting format (append to `exec/sprint-progress.md`)

When your feature finishes (DONE or BLOCKED), append a block in this format:

```markdown
### F-NN -- {slug} -- {DONE|BLOCKED|IN-PROGRESS}

- Date: YYYY-MM-DD
- Owner: {principal-or-worker-name}
- Commits: {commit-sha-1}, {commit-sha-2}
- Files changed: {count}
  - {path-1}
  - {path-2}
- Tests: {before} -> {after} ({+/-N})
- Validation: {N/N REQUIRED checked} (or list which are open)
- Notes: {one paragraph -- anything the next session needs to know}
- Next: {what comes next, e.g. "Sprint 4 closes; Sprint 5 ready"}
```

Do not edit prior blocks. Append-only.

---

## 9. Hard rules (do NOT do these)

- Do NOT edit `constitution/**` without an ADR (Article VIII).
- Do NOT hand-edit `exec/state.md`, `exec/state.html`, `exec/work-index.md`.
  Regenerate via `cli/state_builder.py`.
- Do NOT add third-party Python dependencies in `cli/**` (Article V).
- Do NOT touch files outside your feature's `## File scope` section.
- Do NOT skip the spec phase for features >=5 files (Article II).
- Do NOT promote model upgrades, infra changes, or new dependencies without a
  Level-2 Friction Analysis (`templates/level-2-decision.md`).
- Do NOT use emojis in code, docs, commits, or filenames.
- Do NOT trust agent reports or session checkpoints without verifying in
  git/tests/files.
- Do NOT contaminate context across features. **One feature, one context-isolated unit** (fresh session OR subagent dispatch).

---

## 10. When you finish

- Append your block to `sprint-progress.md`.
- Commit your changes (including the ledger update) on `master` with the proper
  message and co-author trailer.
- Run `python spec-driven-development/cli/state_builder.py` to regenerate the
  executive surfaces.
- Commit that regeneration as a separate `chore: regenerate exec/ state` commit
  if it diffs.
- Push `origin/master`.
- Tell the owner (in chat) which feature finished, the commit SHA, and the next
  prompt to paste.

---

## 11. Sprint Executive Manager activation (forward-only, optional per kickoff)

From Sprint 14 onward, a sprint MAY run a delegated Sprint Executive Manager tier
(`.github/agents/sprint-executive-manager.agent.md`). This is **forward-only**: do
NOT retrofit any already-shipped `SPRINT-##-KICKOFF.prompt.md`. A NEW kickoff prompt
that wants the delegated tier copies the block below into its body.

```
### Sprint Executive Manager (this sprint only)

This sprint runs under the delegated Sprint Executive Manager
(`.github/agents/sprint-executive-manager.agent.md`). It coordinates ONLY this
sprint's committed features, summarizes sprint progress, and reports up to the
project Executive Manager at close. It operates at Level 0: it routes, summarizes,
and surfaces -- it does not decide, does not implement, and is NOT the human entry
point. The project Executive Manager remains the single human-facing entry point
per Article II. The Sprint EM cannot create a sprint or PI and cannot author the
next kickoff; it may only SUGGEST upward.
```

If a kickoff does not include this block, the project Executive Manager runs the
sprint directly, exactly as in Sprints 1-13. Nothing changes for shipped sprints.
