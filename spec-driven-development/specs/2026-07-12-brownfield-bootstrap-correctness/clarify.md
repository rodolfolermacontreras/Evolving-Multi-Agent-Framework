---
id: SDD-058-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-07-12
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# CLARIFY: SDD-058 Brownfield Bootstrap Correctness

- Date: 2026-07-12
- Phase: CLARIFY
- Product lead: Principal Product Manager
- Technical design owner: Principal Architect
- Status: **CLARIFY COMPLETE -- PRODUCT AND TECHNICAL QUESTIONS CLOSED; ADR/SPEC APPROVAL PENDING**
- Source: Sprint 24 kickoff, SDD-058 backlog row, preserved 2026-07-09
  Small-Business-Claude adoption evidence, prior brownfield bootstrap artifacts,
  and current `cli/bootstrap.py` behavior

---

## Problem and outcome boundary

The first real Node/Express brownfield adoption proved that the current apply flow
can erase reviewed proposal edits, copy this framework project's identity and
operating history into a host, omit host configuration, and present a
framework-shaped doctor as if it established host readiness.

SDD-058 must make brownfield apply safe, host-specific, clean, and truthful. The
product contract is default-deny: no source asset or mutable operation is allowed
unless the approved contract explicitly includes it. This artifact records
product recommendations, not implementation architecture.

## Evidence reviewed

- Current `run_brownfield()` always runs archaeology and
  `draft_constitution_proposal()` before checking `--apply`; proposal writes use
  `force=True`. Human edits can therefore be replaced before apply.
- Current `apply_brownfield_framework()` copies the complete `.github/` and
  `spec-driven-development/` trees with overwrite enabled, then replaces the six
  constitution files and initializes a ledger. This imports framework identity,
  backlog, specs, sprints, dispatches, generated exec state, ledger/reorder
  history, and other project-local state.
- The current brownfield parser exposes only `--draft-only` and `--apply`; there
  is no explicit refresh, dry-run diff, backup, restore, or migration mode.
- Current `run_doctor()` identifies itself as `framework health`; several checks
  run only when `root == framework_root()`, and governance checks assume framework
  structures. It is not evidence of generic host readiness.
- The completed 2026-05-26 Day-to-Day pilot expected broad copying and allowed
  manual fallback. It is useful prior art but does not satisfy SDD-058's stricter
  correctness, clean-state, migration, or cross-stack requirements.
- The mandatory `/clarify` dedup scan on 2026-07-12 scanned 83 entries and found
  7 unrelated existing overlaps: 4 SOFT and 3 ADVISORY. It found no HARD ID
  collision and no SDD-058 duplicate. The canonical scan recorded operational
  ledger evidence. Its three unrelated untracked per-spec advisory artifacts were
  removed to preserve this unit's authorized one-file scope.
- Article XI lock status immediately before authoring was: CLARIFY free; SPEC
  free. Creating this active artifact makes SDD-058 the sole CLARIFY holder.

---

## Product decisions requiring owner approval

### SDD058-PQ-01: Proposal preservation and refresh boundary

**Question:** When an edited proposal exists, which user-visible contract governs
normal apply, explicit refresh, and refresh conflicts?

**Facts/evidence:** Current apply regenerates every proposal file before reading
it. There is no reliable product distinction between generated text, human edits,
and partially completed `TODO(human)` fields, so silent regeneration is data loss.

**PM recommendation:** Normal apply must consume the reviewed proposal exactly as
found and must never refresh it. Refresh must be a separate explicit operation
that previews differences and refuses to overwrite any changed or partially
edited proposal file unless the user explicitly resolves each conflict. Keep the
existing proposal available for recovery.

**Options:**

1. Preserve on apply; explicit conflict-aware refresh -- safest default and clear
   user intent, with one extra refresh step when archaeology must be updated.
2. Auto-refresh only demonstrably untouched generated files -- less friction but
   requires a trustworthy untouched-file proof and can surprise users.
3. Always regenerate with a confirmation -- simplest conceptually but retains an
   avoidable data-loss path and is not recommended.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: preserve
the reviewed proposal on normal apply and require a separate, conflict-aware
explicit refresh.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-02: Reusable-asset allowlist

**Question:** What exact product allowlist may brownfield apply install, with all
unlisted paths denied by default?

**Facts/evidence:** Whole-tree copying imported framework project state. The
prior pilot's broad directory list included project-specific docs, roster state,
and runtime directories that are not all reusable assets.

**PM recommendation:** Approve this minimum reusable set, subject to Architect
validation of dependencies between assets:

- `.github/agents/*.agent.md`, excluding `_TEMPLATE-worker.agent.md` and excluding
  any specialist whose charter is not portable to a generic host.
- `.github/prompts/*.prompt.md` required for the canonical lifecycle.
- `.github/skills/core/**`, `.github/skills/workflow/**`,
  `.github/skills/engineering/**`, and only portable `.github/skills/operational/**`.
- `.github/instructions/sdd-workflow.instructions.md`; include
  `fleet-workers.instructions.md` only if its referenced host paths/assets are
  also installed.
- Generated host `.github/copilot-instructions.md`; never copy the framework
  file verbatim.
- `spec-driven-development/README.md`, `CONTEXT.md`, reusable `templates/**`,
  reusable `docs/ADR/TEMPLATE.md`, and the approved CLI/ledger schema subset
  needed for the installed lifecycle.
- Six reviewed proposal constitution files as host constitution content.
- Empty host runtime directories and seed files explicitly defined in
  SDD058-PQ-04; these are initialized, not copied from framework state.

Default-denied examples include framework `backlog/**`, `specs/**`, `sprints/**`,
`dispatches/**`, `exec/**`, `sessions/**`, `fleet/**` history,
`ledger/fleet.db`, `ledger/reorder-audit.jsonl`, PI documents, generated executive
surfaces, framework `project.config.json`, framework Copilot instructions,
framework roadmap/status reports, feature prompts, caches, and test artifacts.
Domain skills, roster files, archetypes, non-template docs, optional operational
skills, CLI files, workflows, and git hooks remain denied until the Architect
proves each is portable and required by the approved host contract.

**Options:**

1. Minimum explicit allowlist above plus Architect dependency validation -- least
   contamination risk; optional capabilities require later opt-in.
2. Broader curated profile containing every currently portable tool -- richer
   first install but increases review and migration surface.
3. Copy broad trees and remove denied paths -- easier implementation but violates
   the default-deny product requirement and is not acceptable.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: use the
minimum explicit allowlist above, subject to Architect dependency validation,
with every unlisted path denied by default.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-03: Host identity and configuration contract

**Question:** Which generated host identity/configuration values may come from
repository evidence or defaults, and which must be confirmed by a human before
apply?

**Facts/evidence:** Archaeology can observe repository name/path, branch, stack,
quality signals, and some remote metadata. It cannot reliably establish the
accountable human, team, mission, permission boundaries, or whether a detected
remote is authoritative. Current apply generates no host `project.config.json`
and copies framework Copilot instructions.

**PM recommendation:** Classify values as follows:

| Output | Field/content | Classification | Product rule |
|--------|---------------|----------------|--------------|
| `project.config.json` | `project_name` | evidence-derived, human-confirmed | Derive from repository metadata/name; show before apply. |
| `project.config.json` | `repo_url` | evidence-derived, human-confirmed | Use a normalized configured git remote only when unambiguous. |
| `project.config.json` | `default_branch` | evidence-derived, human-confirmed | Use repository evidence; never assume `master` or `main`. |
| `project.config.json` | `owner` | human-required | No personal-name inference from commit history. |
| `project.config.json` | `team` | human-required, nullable only by explicit choice | Do not infer organization ownership from a remote URL. |
| `project.config.json` | `article_xi_cutover` | safe generated default | Set to the adoption date for a new host installation. |
| Copilot instructions | project identity, purpose, source-of-truth docs, stack/quality commands, branch/commit conventions | evidence-derived draft plus human-required gaps | Generate host wording; cite observed files; mark unresolved facts explicitly. |
| Copilot instructions | owner/team/mission/approval boundaries | human-required | Apply blocks until required values are supplied and reviewed. |

Missing or ambiguous required identity must stop apply with an actionable message;
it must not silently emit framework identity, fabricated facts, or unresolved
placeholders into a supposedly ready host.

**Options:**

1. Require human confirmation of the classified manifest before apply -- strongest
   identity truth with a deliberate review step.
2. Apply evidence-derived values and leave unresolved markers -- faster adoption
   but produces an incomplete host contract and is not recommended.
3. Require every field manually -- maximally explicit but discards useful,
   reviewable archaeology evidence.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: require
human confirmation of the classified host identity/configuration manifest before
apply.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-04: Clean runtime-state contract

**Question:** What is the acceptable initial mutable state of a newly adopted
host, and what contamination proof is required?

**Facts/evidence:** The first real adoption inherited PI-9 names, dozens of specs,
framework dispatch rows, generated state, backlog content, and reorder history.
Manual cleanup was necessary.

**PM recommendation:** Initialize only empty/seed host-owned state:

- `backlog/IDEAS.md` and `backlog/BACKLOG.md`: host-specific headings and no
  framework items, SDD IDs, RICE rows, or PI allocations.
- `specs/`, `sprints/`, `dispatches/`, `sessions/`, and `fleet/`: empty except
  approved tracked placeholders or host-generic README files.
- `ledger/fleet.db`: newly created from the approved schema with zero operational
  rows; `reorder-audit.jsonl`: absent or empty by explicit contract.
- `exec/`: no copied/generated framework snapshot. If required for tool startup,
  create a clearly labeled host seed that contains no PI/sprint/feature claims and
  is regenerated only after host source artifacts exist.
- Ignore rules: local databases, caches, backups, and generated outputs follow the
  approved host manifest; source artifacts required by lifecycle remain tracked.

Proof must compare both fixtures against a forbidden fingerprint set: no
framework owner/repo identity, `PI-9`, Sprint 24, SDD-058 or prior framework SDD
rows, framework backlog titles, framework spec/sprint/dispatch paths, nonzero
ledger dispatches, reorder entries, or framework-generated exec content. Also
assert the positive seed contract and zero-row ledger query.

**Options:**

1. Empty/seed contract with positive and forbidden-fingerprint assertions --
   strongest proof and deterministic host start.
2. Empty directories only, with no generated seed files -- cleanest state but may
   require tools to tolerate absent artifacts.
3. Copy generic-looking framework placeholders and sanitize them -- higher
   contamination risk and not recommended.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: enforce
the empty/seed runtime-state contract with positive assertions and
forbidden-fingerprint assertions.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-05: Truthful host-readiness promise

**Question:** What product promise may apply make about host readiness if a
portable host-mode doctor cannot be completed in SDD-058?

**Facts/evidence:** The current doctor is explicitly a framework-health command.
Some checks are source-controlled and potentially portable, while others depend
on framework self-tests, Article ranges, current PI rows, framework governance,
and framework-only generated surfaces.

**PM recommendation:** Prefer a separate, explicitly named host-readiness profile
whose PASS means only approved portable checks passed: required installed assets,
valid host config and instructions, no unresolved required placeholders, clean
runtime state, ledger schema/zero-row health at adoption, source-artifact schema,
gitignore safety, and configured quality-command validity. Quality execution is a
separate explicit post-install action. Framework-only checks must be labeled N/A,
not silently omitted. If that truthful profile
cannot ship, apply must end as `installed; readiness not verified`, must not print
success language implying readiness, and must direct the user to documented manual
verification. Existing framework doctor must reject or clearly identify host use.

**Options:**

1. Ship an explicit host-readiness profile with bounded PASS semantics -- best
   user experience but larger verified scope.
2. Enforce the honest fallback only -- smaller scope and truthful, but no single
   automated readiness PASS.
3. Reuse framework doctor with skipped checks -- misleading unless its name,
   output, and exit semantics are redesigned; not recommended.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: ship an
explicit host-readiness profile with bounded PASS semantics.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-06: Migration, rerun, and legacy behavior

**Question:** How should the corrected flow treat existing proposals,
already-adopted hosts, legacy flags, and repeated runs?

**Facts/evidence:** Existing users know `brownfield <target>`, `--draft-only`, and
`--apply`; some hosts may contain a mixture of copied framework assets and local
edits. Blind repair could delete host work, while leaving legacy behavior intact
would preserve the defect.

**PM recommendation:** Preserve command parsing where safe, but map legacy
`--apply` to the corrected non-refreshing, preview-first contract. Treat an
existing proposal as user-owned. Treat an existing SDD installation as migration,
not a fresh install: inventory and classify files, preserve unknown/modified host
content, surface contamination candidates, and require explicit approval before
repair. Rerunning against an unchanged approved input must be idempotent and
report no changes. Deprecated or unsafe legacy behavior must fail with migration
guidance rather than continue silently.

**Options:**

1. Backward-compatible flags with corrected semantics plus explicit migration mode
   for adopted hosts -- balanced compatibility and safety.
2. Break legacy flags and require new commands -- clearest contract but highest
   adoption friction.
3. Keep legacy unsafe behavior behind a warning -- preserves defect exposure and
   is not acceptable.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: preserve
safe legacy flags with corrected semantics and require explicit migration mode
for already-adopted hosts.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-07: Apply safety and approval boundary

**Question:** Which safety evidence and approvals are mandatory before any
filesystem mutation, and what recovery guarantee must apply provide?

**Facts/evidence:** Current apply prompts only for `yes`, after proposal mutation
has already occurred. It has no operation summary, diff, backup, rollback, or
atomicity promise. Sprint 24 forbids destructive real-host apply without owner
approval.

**PM recommendation:** Dry-run must be the default and produce a human-readable
manifest/diff grouped as create, replace, preserve, conflict, forbidden, and
runtime-initialize, with no mutation. A real apply requires explicit approval of
that exact preview. Before mutation, preserve every replaced host file and the
reviewed proposal in a restorable backup. Apply must validate/stage the complete
result before promotion; any failure must leave the original host intact or
perform verified rollback and return nonzero with recovery instructions. No
`--force` path may bypass conflicts, backup, or approval. Destructive apply to a
real host additionally requires recorded owner approval; fixture applies may be
automated when isolated and disposable.

**Options:**

1. Preview approval + complete backup + atomic promote/verified rollback --
   strongest safety with extra disk/time cost.
2. Preview approval + per-file backup and best-effort rollback -- simpler but may
   leave mixed state after exceptional failure.
3. Confirmation prompt only -- insufficient for informed approval and recovery.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: require
approval of the exact preview, complete backup, and atomic promotion or verified
rollback. This product decision does not authorize destructive real-host apply.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

### SDD058-PQ-08: Representative fixture and platform contract

**Question:** Which minimum fixture matrix is sufficient to claim generic
brownfield correctness across stacks and operating systems?

**Facts/evidence:** The defect was reproduced on a Node/Express Claude copilot
application. Existing framework tests cover almost no brownfield behavior. A
second fixture must be materially different, not another JavaScript variant.
Windows/POSIX differences include path separators, executable bits, symlink
behavior, newline conventions, case sensitivity, and replacement/rename behavior.

**PM recommendation:** Require two clean committed git fixtures:

1. A realistic Node/Express host with `package.json`, npm lockfile, Express source,
   JavaScript/TypeScript tests, README, existing `.github/` content, `.gitignore`,
   remote/default-branch evidence, and a partially human-edited proposal matching
   the original failure.
2. A materially different Python library/service fixture with `pyproject.toml`,
   Python package/tests, different CI/convention evidence, no pre-existing
   `.github/copilot-instructions.md` in one scenario, and an already-adopted or
   rerun scenario.

Run equivalent behavioral assertions on Windows and POSIX CI or equivalent
platform runners. Assert path-independent manifests, normalized textual output,
preserved host line endings where files are preserved, intentional UTF-8/LF for
new framework text, no reliance on Windows-only junctions or POSIX executable
bits unless explicitly handled, and identical pass/fail/exit semantics.

**Options:**

1. Node/Express plus Python, both exercised on Windows and POSIX -- credible
   cross-stack/platform claim at manageable scope.
2. Node/Express plus a static non-code repo -- cheaper but does not materially
   test different build/test archaeology.
3. Node/Express only on both platforms -- tests OS portability but not generic
   cross-stack adoption.

**Owner answer (2026-07-12):** Option 1 approved exactly as recommended: require
Node/Express and Python fixtures exercised on Windows and POSIX.

**Status:** CLOSED/APPROVED -- owner package approval recorded as local ledger
decision 4 on 2026-07-12.

---

## Product constraints already fixed by authorization

These are not open implementation choices:

- B1: normal apply cannot silently overwrite an edited or partially edited
  proposal; refresh must be explicit and observable.
- B2: reusable assets use an exact allowlist; all unlisted source paths are denied
  by default. A newly adopted host contains no framework project/runtime/history
  state.
- B3: host Copilot instructions and `project.config.json` are generated for the
  host; framework identity is never copied as host identity.
- B4: framework self-checks cannot be represented as generic host readiness.
- No destructive apply against a real host without explicit owner approval.
- The CLI remains stdlib-only. No new runtime or test dependency is authorized.
- Windows/POSIX evidence and realistic Node/Express plus materially different
  cross-stack fixtures are mandatory.
- Existing host content and human decisions take precedence over generated
  defaults unless a reviewed, approved operation explicitly replaces them.

## Architect-owned technical design questions

The Principal Architect resolved these questions on 2026-07-12. ADR-026 and the
SDD-058 SPEC carry the normative detail; this section records the closure.

- **SDD058-AQ-01 -- CLOSED:** Each generated proposal records a versioned baseline
  manifest with SHA-256 hashes of generated bytes and evidence inputs. Refresh is
  an explicit three-way comparison among baseline, reviewed proposal, and newly
  generated candidate. Convergent dual changes are preserved; non-convergent dual
  changes conflict. Legacy proposals without a baseline use explicit baseline-
  adoption migration. Content is never guessed from `TODO` markers. Normal apply
  does not invoke refresh and preserves proposal bytes.
- **SDD058-AQ-02 -- CLOSED:** A versioned `brownfield-core@1` manifest enumerates
  every copy, render, seed, preserve, and forbidden destination plus dependencies
  and hashes. Dependency closure is validated before preview. Selection is
  allowlisted at source; managed mutation is default-denied; unrelated host paths
  are preserved. Whole-tree copy followed by deletion is forbidden. Exact
  membership is fixed in ADR-026 Appendix A.
- **SDD058-AQ-03 -- CLOSED:** A versioned host-identity manifest records each
  field's value, provenance (`evidence`, `default`, or `human`), confidence,
  evidence path, confirmation state, and renderer version. Required human facts
  block apply. Host Copilot instructions and `project.config.json` are rendered
  deterministically under ADR-026 Appendix B, never copied from the framework;
  credential-bearing remote evidence is sanitized or blocked.
- **SDD058-AQ-04 -- CLOSED:** Real apply validates a complete same-volume staging
  tree, binds approval to the preview hash, backs up every affected destination
  and the reviewed proposal, journals ordered operations, promotes paths with
  atomic replacement where supported, and verifies rollback hashes on failure.
  Write-ahead operation states support interruption recovery. An interrupted or
  unverifiable rollback exits recovery-required; no force path bypasses preview,
  conflicts, backup, or recovery. Abrupt power-loss atomicity is not claimed.
- **SDD058-AQ-05 -- CLOSED:** A separate `host-doctor` profile reports bounded
  host readiness. It checks the installed manifest, identity/config, required
  assets, unresolved placeholders, runtime seeds, ledger schema/adoption receipt,
  gitignore safety, forbidden fingerprints, and configured quality-command token
  validity. Apply-time checks are structural; quality execution is explicit and
  post-install, outside rollback. Framework-only checks are `N/A`, never PASS.
- **SDD058-AQ-06 -- CLOSED:** Inventory classifies a target as fresh,
  proposal-only, managed-current, managed-drift, legacy-broad-copy,
  partial/interrupted, foreign-collision, or mixed-contaminated. Per-path
  classification preserves unknown or modified host work. Legacy `--apply` maps
  to corrected preview-first semantics; adopted hosts require explicit migration;
  unchanged reruns are no-op and idempotent. SDD-058 does not delete
  contamination.
- **SDD058-AQ-07 -- CLOSED:** Tests construct committed temporary Node/Express and
  Python hosts with local bare remotes, deliberate newline/permission variation,
  and deterministic branch evidence. Equivalent assertions run on Windows and
  POSIX. Manifests use POSIX-relative paths; preserved bytes remain byte-identical;
  new text is UTF-8/LF; failure injection proves rename and rollback behavior.
- **SDD058-AQ-08 -- CLOSED:** `bootstrap.py` remains a thin CLI/compatibility
  dispatcher. Inventory, proposal/baseline, asset manifest, identity rendering,
  migration, transaction/recovery, and host-readiness responsibilities are
  separate stdlib-only modules. Legacy flags are adapters, not alternate unsafe
  paths. No new dependency, constitution change, or ledger schema is introduced.

## Mandatory gate before SPEC approval

SDD-058 is cross-cutting. After the owner answers SDD058-PQ-01 through
SDD058-PQ-08, the Principal Architect must author the ADR and full SPEC from the
closed contract. The ADR and SPEC must be reviewed together and approved by both
the Architect and owner. No PLAN, TASKS, implementation, destructive real-host
apply, or validation lock may proceed before that approval. The later exact
pre-push package also requires separate owner approval. Any non-fixture host apply
requires an additional target- and preview-specific owner approval.

## Explicit exclusions

- SDD-035 Azure decommission remains out-of-band.
- Sprint 23 retro reconciliation remains separate cleanup.
- SDD-034 is excluded.
- Dashboard work is excluded.
- Greenfield bootstrap redesign is excluded except where the Architect proves a
  shared primitive is unavoidable for SDD-058 correctness.
- No unrelated backlog, housekeeping, constitution change, dependency, schema
  migration, cloud work, agent hiring, feature, or historical cleanup.
- No real-host mutation during CLARIFY, SPEC, PLAN, TASKS, or automated fixture
  proof.
- No wholesale rewrite or deletion of host-owned `.github/`, SDD artifacts,
  backlog history, specs, sprints, dispatches, or ledger data during migration.

## CLARIFY exit state

- Owner product decisions open: none. Product decision count: 0.
- Approved product contract: SDD058-PQ-01 through SDD058-PQ-08, exactly as
  recommended above, approved as one package on 2026-07-12 and recorded as local
  ledger decision 4.
- Architect route: SDD058-AQ-01 through SDD058-AQ-08 are closed above and carried
  into proposed ADR-026 plus the draft full SPEC.
- Routed Architect design question count: 8 closed; 0 open.
- Recommendation: CLARIFY remains complete. The CLARIFY lock is released; the
  draft SPEC now holds the repo-wide SPEC lock pending joint Architect-and-owner
  ADR/SPEC approval.
- Approval boundary: this handoff does not approve the future ADR/SPEC,
  PLAN/TASKS, implementation, commit, push, or destructive real-host apply. The
  ADR and SPEC require the separate joint Architect-and-owner approval gate
  before PLAN or TASKS.
