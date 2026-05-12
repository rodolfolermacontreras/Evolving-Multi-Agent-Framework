# Architectural Principles

Nine binding articles. All agents must honor these. Exceptions require a Level 1 or Level 2
decision and an ADR entry.

---

## Article I: Single Responsibility Engines

Each module in `agent/` owns exactly one domain. `engine.py` orchestrates but does not
implement business logic. If a module is doing two unrelated things, it must be split.

## Article II: Data Flows Through World State

All LLM prompts consume `world_state`. No prompt builder queries data sources directly.
Every piece of context reaches the LLM through `get_world_state()` in `agent/world_state.py`.
This is the single source of truth for what the agent knows.

## Article III: Testing Is Non-Negotiable

Every code change ships with tests. The test count must never decrease from its current
baseline (743 tests, 36 files). Isolation via `patched_settings`. LLM calls mocked via
`MockLLMClient`. There is no definition of "done" that does not include passing tests.

## Article IV: Security by Convention

User input touching file paths must use `safe_path()` (prevents path traversal).
User input rendered in HTML must use `esc()` (prevents XSS).
API mutations must use Pydantic validation via `agent/schemas.py` (returns 422 on failure).
No inline user content in templates without escaping.

## Article V: Git Discipline

`master` is production -- read-only. `integration/improvements` is the development trunk.
All work happens on feature branches via worktrees (`../wt-{shortname}`).
Merge direction: feature -> integration. Never merge integration -> master without human approval.
Failed experiments are deleted (worktree + branch), never merged.

## Article VI: Observability Is Built In

Every LLM call is logged with model, tokens, latency, and cost via `record_llm_call`.
No silent failures. Errors surface as structured responses, not bare exceptions.
The `_eval/` directory captures comparison artifacts -- delete when done.

## Article VII: Prefer Stdlib Over Dependencies

New dependencies require Architect approval + an ADR entry.
Approved production dependencies: FastAPI, SQLModel, Jinja2, MSAL, python-dotenv, httpx,
APScheduler, python-multipart, aiofiles.
When a stdlib module can do the job, use it.

## Article VIII: Configuration Is Explicit

All settings live in `agent/config.py` as frozen dataclasses, composed into a single
`settings` object. Secrets come from environment variables. No magic globals.
No runtime monkey-patching outside of tests. All paths derive from `REPO_ROOT`.

## Article IX: Incremental Migration

Legacy JSON dotfiles in `agent/` coexist with the SQLite database.
Migration is iterative, not big-bang. Each tech debt item (D1-D10) has its own spec.
Do not attempt to migrate all stores in one feature branch.

---

## Design Heuristics (not binding articles, but strong defaults)

- Convention over configuration: follow existing patterns before introducing new ones
- Existing patterns over new abstractions: read the codebase before deciding something is missing
- Small, frequent commits over large batches: each commit should be explainable in one sentence
- Read before modifying: open the file, understand the last-processed marker, show diffs before committing
- Clean as you go: no orphan code, no commented-out blocks, no unused variables, no stale scripts
