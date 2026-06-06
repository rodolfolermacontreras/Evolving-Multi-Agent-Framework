# Sprint Progress Ledger

Append-only. Each completed feature appends a result block (format defined in
[../feature-prompts/_SHARED_ONBOARDING.md](../feature-prompts/_SHARED_ONBOARDING.md)
section 8).

The latest test baseline lives in the most recent block. **Read from the bottom
up to find current state.**

Maintained by feature workers themselves. The Executive Manager and the
`state_builder.py` CLI consume this file; they do not edit prior entries.

---

## Baseline (2026-06-05, HEAD `ae603c4`)

- Tests passing: **152**
- Current PI: PI-4 (Alpha Release)
- Active sprint: Sprint 4 (Filesystem Data Contracts) -- at `/tasks` gate
- Worktrees: 0
- Origin sync: up to date

---

## Sprint 4 -- PI-4 / Filesystem Data Contracts (FDC) finish

- Sprint kickoff: [../feature-prompts/SPRINT-04-KICKOFF.prompt.md](../feature-prompts/SPRINT-04-KICKOFF.prompt.md)
- Prerequisite: HEAD at or descended from `ae603c4`; FDC plan + ADR-012 committed.
- Sequence: F-01 -> F-02
- Owner: Principal Software Developer (lead)

### F-01 -- fdc-tasks -- DONE

- Date: 2026-06-05
- Owner: Principal Software Developer
- Commits: <pending-sha>
- Files changed: 2
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/tasks.md (new)
  - spec-driven-development/exec/sprint-progress.md (this block)
- Tests: 152 -> 152 (docs-only; no code changes in F-01)
- Validation: tasks.md frontmatter present (id/type/status/owner/updated);
  traceability matrix complete (9 tasks -> R1..R7 + O1..O2 mapped, zero
  orphans); per-task allowed_files/blocked_files scoping recorded (AC-3); no
  locked-function modification implied (AC-4); no third-party dep references
  (AC-5).
- Notes: Decomposed FDC plan into 9 tasks across 5 phases. Sequence:
  T-FDC-01 (schema doc) -> T-FDC-02 (S1 lock guard test, pulled forward as
  tripwire) -> T-FDC-03 (lint extension) -> T-FDC-04 (rollup helpers) ->
  T-FDC-05 (cmd_count handler) -> T-FDC-06 (COMMIT-CONVENTION) -> T-FDC-07
  (opt-in hook) -> T-FDC-08 (backfill) -> T-FDC-09 (validation closeout).
  Lock-guard task = T-FDC-02. Backfill task = T-FDC-08. One deviation
  documented in tasks.md "Frontmatter contract note": AC-1 mandates literal
  `status: locked` in tasks.md frontmatter but the FDC status enum does not
  include `locked` -- T-FDC-08 reconciles during backfill (either change to
  `active` or extend enum). No spec/plan/ADR/validation edits made.
- Next: F-02 ready -- paste F-02-fdc-implement.prompt.md in a fresh session

### F-02 -- fdc-implement -- DONE

- Date: 2026-06-06
- Owner: Principal Software Developer (no fleet dispatch; linear single-session execution per dispatch policy)
- Commits (sprint chain, in order):
  - `2335a2a` spec(fdc): amend R5/AC-5 anchor b7ce642 -> 257b081 (Article X) -- pre-F-02 amendment ratified by owner
  - `e96f849` docs(fdc): log Q5 amendment of R5 anchor in clarification-log -- pre-F-02 amendment ratified
  - `c2e5871` test(fdc): T-FDC-02 add S1 footprint lock guard against 257b081
  - `405c332` docs(fdc): T-FDC-01 + T-FDC-06 frontmatter schema and commit convention
  - `62006f4` feat(fdc): T-FDC-03 extend schema_lint with artifact contract validator
  - `99499ac` feat(fdc): T-FDC-07 add opt-in commit-msg hook + tests
  - `47b1568` feat(fdc): T-FDC-04 + T-FDC-05 add count subcommand (rollup + handler)
  - `b2586dc` docs(fdc): T-FDC-08 backfill frontmatter across specs/** and sprints/**
  - `20c16dc` spec(fdc): T-FDC-09 close validation -- R1..R7 + O1/O2 all checked
- Files changed (F-02 only, excluding pre-F-02 amendment commits): ~95 files
  - cli/schema_lint.py (extended additively)
  - cli/test_schema_lint.py (+12 artifact contract tests)
  - cli/state_builder.py (additive: bootstrap import, build_doc_count, build_doc_count_by_sprint, render_count_table, cmd_count, count subparser; locked S1 functions UNTOUCHED)
  - cli/test_state_builder.py (+18 count subsystem tests + 3 lock guard tests; stdlib-allowlist updated for schema_lint sibling import)
  - cli/hooks/commit-msg (new)
  - cli/test_commit_hook.py (new, 14 tests)
  - spec-driven-development/docs/COMMIT-CONVENTION.md (new)
  - spec-driven-development/specs/2026-06-04-filesystem-data-contracts/frontmatter-schema.md (new)
  - 77 frontmatter backfills across spec-driven-development/specs/** + sprints/** (68 prepends + 9 legacy-frontmatter patches)
  - validation.md (checkbox state R1..R7 + O1/O2 ticked; Article X statement bodies untouched)
  - tasks.md (status fields flipped pending -> done; status: locked -> status: active)
  - FDC artifact frontmatter (spec/plan/clarification-log/handoff-to-plan/frontmatter-schema): status: active -> done
- Tests: 152 -> 200 (+48). +47 new (12 schema_lint artifact, 18 count subsystem, 3 lock guard, 14 commit-msg hook) + 1 from previously-skipped real-repo lint test that now passes because the in-scope tree is clean.
- Validation: 7/7 REQUIRED checked; 2/2 OPTIONAL checked.
  - R1 PASS, R2 PASS, R3 PASS, R4 PASS, R5 PASS (against 257b081 goldens), R6 PASS, R7 PASS, O1 PASS, O2 PASS
- Lock guard (R5): PASS. Five locked function sha256 digests are byte-identical to 257b081 (also matches the pre-amendment HEAD `b7ce642` for `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`; `render_html` + `load_decisions` were re-anchored to current HEAD via Article X because they had legitimately evolved during Sprint 3).
- Schema-lint full scan (R6): `python spec-driven-development/cli/schema_lint.py spec-driven-development/specs/ spec-driven-development/sprints/` exits 0; "Schema lint clean."
- Backfill (T-FDC-08): 77 files received or had frontmatter completed (68 fresh prepends + 9 legacy-frontmatter patches). Total in-scope artifact count surfaced by `state_builder.py count`: 80 (5 active + 68 done + 1 superseded + 1 active FDC-residual + extras = 80, invariant holds).
- Notes: Single-session linear execution with no fleet dispatch (per EM policy for additive well-scoped tasks). Day-1 anchor drift caught BY the lock guard, resolved BEFORE F-02 implementation via Article X amendment (commits `2335a2a` + `e96f849`); F-02 itself never touched a locked function. Friction-analysis-template state_builder display gap documented as PI-5 P3 cleanup candidate (see "PI-5 cleanup candidates" section below); not fixed in this session per 5-min cap.
- Next: Sprint 4 close block below.

### Sprint 4 -- CLOSED

- Date: 2026-06-06
- Owner: Principal Software Developer (closing); Principal Executive Manager (routing); Owner Rodolfo Lerma (ratified Level-2, 2026-06-06)
- Features completed: F-01 (fdc-tasks DONE 2026-06-05), F-02 (fdc-implement DONE 2026-06-06)
- Final SHA: (this commit's parent will be the sprint-close commit -- see commit log)
- Sprint chain (chronological, in master): `2bf2e96` (F-01) -> `257b081` -> `2335a2a` -> `e96f849` -> `c2e5871` -> `405c332` -> `62006f4` -> `99499ac` -> `47b1568` -> `b2586dc` -> `20c16dc` -> sprint-close commit
- Tests: 152 -> 200
- Validation: 7/7 REQUIRED, 2/2 OPTIONAL (FDC validation contract fully checked)
- PI-4 status decision: **DONE-WITH-DEFERRED** (pending owner ratification). Three of five PI-4 commitments shipped (Live UI v2 dashboard, root README + roadmap, filesystem data contracts). Two cosmetic / maintenance commitments deferred explicitly to PI-5: (1) annotate Day-to-Day-specific domain skills as examples; (2) bump GitHub Actions to resolve Node.js deprecation. No PI-4 commitment was loosened.
- Notes: PI-4 shipped two pieces of structural infrastructure (the Live UI v2 dashboard in Sprints 1-3 and the filesystem data contract in Sprint 4) plus the README/roadmap housekeeping. The 257b081 -> 200-test trajectory ratifies both the lock-guard discipline (caught a real anchor drift on Day 1) and the validation-contract discipline (zero loosening, even when literal anchors had to be amended by formal process). Two PI-4 commitments deferred to PI-5; both are P1/P2 cosmetic items, not blockers for alpha-release readiness.
- Next: Sprint 5 unblocked. Paste `spec-driven-development/feature-prompts/SPRINT-05-KICKOFF.prompt.md` in a fresh session.

### PI-5 cleanup candidates (carry-over from PI-4)

These items surfaced during F-02 but were intentionally not fixed in-session per the 5-min cap rule. They are NOT blockers; they go to the PI-5 grooming pass.

- **state_builder feature-stage cosmetic nit (P3)**: The IMPLEMENT 0/12 false signal for `friction-analysis-template` flagged by EM was **resolved as a side effect of the T-FDC-08 backfill** -- once `status: done` was prepended to that feature's `spec.md` and `validation.md` frontmatter, state_builder.py correctly reports it as `REVIEW done` in `exec/state.md`. A smaller residual nit remains: the same row now reports "Status: done but RETRO missing" because the feature legitimately closed without a `RETRO.md` (it was a skip-to-implement, single-spec change). Teaching state_builder to suppress the RETRO-missing warning for features whose tasks.md is absent (or whose frontmatter explicitly marks them as no-retro) is a P3 cosmetic improvement. Not a blocker; not in Sprint 4 scope.
- **Domain-skill annotation (P1, PI-4 deferred)**: Day-to-Day-specific domain skills (fastapi-routes, htmx-frontend, pytest-runner) need to be marked as reference examples in `.github/skills/domain/`. No code change, doc-only.
- **GitHub Actions Node.js deprecation (P2, PI-4 deferred)**: bump `actions/checkout` and `azure/login` (and any other actions still on Node 16/18) to current versions in `.github/workflows/`.

---

## Sprint 5 -- PI-5 kickoff + Brownfield-portability bundle (SDD-016 + SDD-017)

- Sprint kickoff: [../feature-prompts/SPRINT-05-KICKOFF.prompt.md](../feature-prompts/SPRINT-05-KICKOFF.prompt.md)
- Prerequisite: **Sprint 4 closed DONE.** Full suite green. FDC merged.
- Sequence: F-03 -> F-04 -> F-05
- Owner: Principal Executive Manager (lead); PM and Architect for planning;
  SW Dev + workers for implementation.

### F-03 -- pi5-kickoff -- NOT STARTED

(append block here on completion)

### F-04 -- symlink-portability-clarify-spec -- NOT STARTED

(append block here on completion)

### F-05 -- symlink-portability-implement -- NOT STARTED

(append block here on completion)
