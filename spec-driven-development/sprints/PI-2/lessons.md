# PI-2 Lessons

Captured during PI-2. Curated via `/evolve` at PI close.

Format: ID, source, statement, candidate framework change (SHIP / DEFER / DISCARD decided at /evolve time).

---

## LESSON-005 -- EM should recommend, not present a menu

**Source:** state-dashboard RETRO + direct user feedback 2026-05-16: _"it is very easy to get lost into all the words, choices and verbage that this is giving me."_

**Statement:** When the Executive Manager needs human input on a decision, the default mode is "I recommend X, here's the one-line why, OK?" -- NOT "pick from A/B/C/D with these 4 tables and 3 sub-questions." Menus are a fallback for genuinely ambiguous strategic choices, not the default for routine sequencing.

**Why it matters:** The human has one cognitive budget; the framework spends it. Every "pick from a menu" interaction taxes that budget. Recommendations preserve it for actual judgment calls.

**Candidate change:** Add an `em-communication-discipline` skill or amend the existing Executive Manager agent definition with explicit rules:
1. Default mode: single recommendation with one-line reasoning and OK/veto prompt.
2. Menu mode: only when the choice is irreversible, expensive, or the EM lacks the information to recommend.
3. Never present more than 3 options. If you have 4+, you have not finished thinking.
4. Tables and matrices belong in deliverable artifacts (spec.md, plan.md), not in conversational briefings.

**Status:** SHIPPED IN PI-2 (this lesson). See `.github/skills/operational/em-communication-discipline/SKILL.md`.

---

## LESSON-006 -- Closure ceremonies must touch ALL "current" markers

**Source:** state-dashboard RETRO 2026-05-16. PI-1 was closed in exec/state.md but roadmap.md still said `## PI-1: ... (current)`. The generator faithfully reported stale state.

**Statement:** When a PI/sprint/feature closes, ceremony must update EVERY file that carries a "current" marker, not just state.md. Specifically: `constitution/roadmap.md`, `exec/state.md`, and any sprint-level CURRENT_PI.md.

**Candidate change:** Add a "closure checklist" to the `pi-planning` skill OR extend the `constitution-sync` propagation scan to flag stale `(current)` markers.

**Status:** SHIPPED in PI-3/S3. See `.github/skills/core/constitution-sync/SKILL.md` v1.1.

---

## LESSON-007 -- Pre-spec design exploration transfers cheaply

**Source:** state-dashboard RETRO 2026-05-16.

**Statement:** Even when a full DESIGN.md is not implemented to spec, its design tokens (palette, type scale, layout grid, panel system) transfer to v0.1 implementations at near-zero cost. Pre-spec design is not waste; it is a reservoir.

**Candidate change:** Document this pattern in the `gem-designer` skill / agent prompt -- "your DESIGN.md should produce reusable tokens, not just a finished implementation. Tokens survive scope cuts."

**Status:** DEFERRED to PI-3/S4 (Live UI v2 Spec). UI Designer authors `design-tokens` skill in spec phase. Curated in PI-3/S3.

---

## Carry-over from PI-1

- **LESSON-004 (ledger migration policy)** -- CLOSED. Shipped in PI-2 Sprint A via `ledger/MIGRATION-POLICY.md`. Retrospectively closed in PI-3/S3.

---

## LESSON-008 -- Two parallel specs for the same file: declare one canonical

**Source:** state-builder + state-dashboard converged on a single implementation file (`cli/state_builder.py`) (2026-05-16).

**Statement:** When two parallel specs target the same implementation file, declare one as canonical for the file's primary contract and treat the other as additive scope. Cross-reference both validation contracts from the implementation file's header docstring.

**Status:** SHIPPED in PI-3/S3. See `.github/skills/workflow/to-spec/SKILL.md` v1.1, "Canonical File Declaration" section.

---

## LESSON-009 -- Windows SQLite + tempdir tests need explicit cleanup

**Source:** fleet.py SDD-003 test development (2026-05-16). All 9 acceptance tests passed logically but `tearDown` errored on Windows because `sqlite3.Connection` keeps the db file open until GC, and `TemporaryDirectory.cleanup()` refuses to delete locked files.

**Statement:** Any unittest that opens SQLite databases inside `tempfile.TemporaryDirectory()` must use `TemporaryDirectory(ignore_cleanup_errors=True)` and call `gc.collect()` in `tearDown` to release file handles before cleanup runs. This is a Python stdlib behavior on Windows, not a project bug.

**Candidate change:** Add a "Windows test fixtures" section to the `testing-conventions` skill at `.github/skills/core/testing-conventions/SKILL.md`.

**Status:** SHIPPED in PI-3/S3. See `.github/skills/core/testing-conventions/SKILL.md` v1.1, "Windows Test Fixtures" section.

---

## LESSON-010 -- ACA Easy Auth needs companion app reg with id_token issuance enabled

**Source:** SDD-007 cloud-dashboard first sign-in attempt returned HTTP 401 (2026-05-16).

**Statement:** When configuring Microsoft Entra Easy Auth on Azure Container Apps via `az containerapp auth microsoft update`, the CLI does NOT automatically enable `enableIdTokenIssuance` on the companion app registration. The Easy Auth default flow uses `response_type=id_token&response_mode=form_post`. Without the implicit grant enabled, sign-in completes at Microsoft's end but token validation fails at the ACA edge, yielding 401 post-auth.

**Fix:** Pair these two commands every time:
1. `az ad app create --display-name ... --web-redirect-uris https://<app>/.auth/login/aad/callback`
2. `az ad app update --id <appId> --enable-id-token-issuance true`     <- the missing step

**Candidate change:** Update `.github/skills/operational/azure-deployment-architecture/SKILL.md` runbook section to include the id_token issuance step explicitly. Update PROVISIONED.md template.

**Status:** SHIPPED (already present in skill). See `.github/skills/operational/azure-deployment-architecture/SKILL.md` runbook step 4. Retrospectively closed in PI-3/S3.
