# ADR-026: Transactional, manifest-driven brownfield adoption

- Date: 2026-07-12
- Status: accepted (owner approved jointly with the SDD-058 SPEC on 2026-07-12;
  local ledger decision 5)
- Feature: SDD-058
- Decision authority: Principal Architect Level 1; owner ratified Option 1 at the
  Sprint 24 cross-cutting SPEC gate on 2026-07-12

## Context

The first real Node/Express brownfield adoption exposed four coupled defects in
`bootstrap.py brownfield`: apply regenerates and overwrites a reviewed proposal;
it copies broad framework trees and contaminates the host with framework identity
and operating history; it does not produce host-specific configuration; and the
framework doctor cannot truthfully establish generic host readiness.

The owner approved SDD058-PQ-01 through SDD058-PQ-08 as one product package on
2026-07-12. The corrected architecture must preserve human decisions, select only
dependency-closed reusable assets, initialize clean host state, generate truthful
host identity, survive failure on Windows and POSIX, migrate legacy adoptions
without deleting unknown work, and remain stdlib-only. No constitution change,
new dependency, or ledger schema change is authorized.

## Decision

### 1. Proposal refresh uses a generated baseline, not content heuristics

Each generated proposal MUST include a versioned baseline manifest. The manifest
records the framework source revision, archaeology/evidence digest, renderer and
schema versions, and the SHA-256 hash and byte length of every generated proposal
file. The generated baseline bytes, or an equivalently lossless baseline snapshot,
MUST remain available for three-way comparison.

Normal apply consumes the reviewed proposal exactly as found and MUST NOT run
archaeology or proposal generation. Refresh is a separate explicit operation. It
compares baseline, reviewed proposal, and newly generated candidate:

- reviewed equals baseline, candidate equals baseline: unchanged;
- reviewed equals baseline, candidate differs: safe upstream refresh;
- reviewed differs, candidate equals baseline: preserve human edit;
- reviewed and candidate are byte-identical: convergent change, preserve without
  conflict even if both differ from baseline;
- reviewed differs from both baseline and candidate, and candidate differs from
  baseline: conflict requiring explicit resolution.

This classification never infers edit state from `TODO` text or current content
alone. Refresh previews all outcomes and preserves the prior proposal and baseline
for recovery. Conflicted files are never overwritten by default.

### 2. Reusable assets are selected by a versioned, dependency-closed allowlist

Adopt the immutable versioned bundle membership in Appendix A, materialized by
implementation as `brownfield-core@1`. Every entry declares
a POSIX-relative destination, operation (`copy`, `render`, `seed`, `preserve`, or
`forbid`), source and SHA-256 when copied, renderer ID/version when generated,
dependencies, text policy, and managed/unmanaged ownership. Dependency closure,
source containment, duplicate destinations, and hashes MUST validate before a
preview is produced.

Default deny applies to framework-source selection and managed mutation
destinations: no unlisted framework source may be read for installation, and no
unlisted host destination may be created, replaced, deleted, or ownership-claimed.
Unlisted existing host paths are inventory-only and MUST be preserved; their mere
presence does not block adoption unless they collide with an enumerated
destination or violate a separately identified path-safety rule.

The minimum core profile consists of:

- **Rendered identity and governance:** host `.github/copilot-instructions.md`,
  `project.config.json`, host `spec-driven-development/README.md`, `CONTEXT.md`,
  six reviewed constitution files, and compact host seed documents required by
  installed commands.
- **Rendered core agents:** four Principal agents, Sprint Executive Manager,
  Developer, and QA Engineer. Their host stack, branch, test, path, and approval
  references come from the confirmed identity manifest. UX Designer and Data
  Scientist are optional profile entries, not core requirements.
- **Canonical lifecycle prompts:** `ask`, `triage`, `clarify`, `grill`, `spec`,
  `plan`, `tasks`, `analyze`, `fleet`, `implement`, `qa`, `retro`, `state`,
  `replan`, `evolve`, and `constitution`, with host command references rendered.
- **Core skills:** only the individually enumerated skills in Appendix A.
  Host-specific variants MUST be rendered where the source contains framework
  paths or stack.
- **Instructions:** `sdd-workflow.instructions.md`; the fleet-worker instruction
  only when a confirmed worktree profile is enabled, and then rendered from the
  host branch/environment contract.
- **Templates/docs:** all general lifecycle templates except the worked Level-2
  example and model-upgrade JSON fixtures; `docs/ADR/TEMPLATE.md`; and
  `docs/CLI-PATTERN.md`.
- **Lifecycle CLI/ledger subset:** only the individually enumerated Appendix A
  sources and approved new SDD-058 modules; generated rosters contain exactly the
  installed agents and skills. PLAN MUST prove closure but cannot change bundle
  membership.

Explicitly forbidden in the core bundle are framework Copilot instructions and
`project.config.json`; framework backlog, specs, sprints, dispatches, sessions,
fleet history, generated exec snapshots, feature prompts, PI/management/status
history, historical ADRs, scorecards, archetypes, domain skills, specialist or
template agents, optional cloud/UI/symlink/role-creation/status-report skills,
workflows, git hooks, source tests/caches, `fleet.db`, and reorder history.
Whole-tree copy followed by cleanup is prohibited even inside staging: source
selection itself MUST be allowlisted.

### 3. Host identity is explicit, provenance-bearing, and deterministic

A versioned host-identity manifest is the sole input to host identity rendering.
Each field records value, classification (`evidence`, `default`, or `human`),
provenance/evidence path, confidence or ambiguity, confirmation state, and schema
version. It includes at minimum `project_name`, `repo_url`, `default_branch`,
`owner`, `team`, `mission`, adoption date/`article_xi_cutover`, stack and quality
commands, branch/commit conventions, source-of-truth documents, and approval
boundaries.

`project_name`, `repo_url`, and `default_branch` may be evidence-derived but MUST
be human-confirmed. `owner` and `mission` are human-required; `team` is required
unless the human explicitly confirms null. The adoption date is a safe generated
default. Ambiguous evidence and missing required confirmation block apply.
Renderers produce deterministic UTF-8/LF `project.config.json` and host Copilot
instructions. They MUST not emit framework identity, fabricated facts, unresolved
required placeholders, absolute temporary paths, or nondeterministic ordering.

### 4. Apply is a preview-bound, journaled transaction

Dry-run is the default. It emits a stable machine-readable manifest plus a
human-readable preview with exactly these categories: `create`, `replace`,
`preserve`, `conflict`, `forbidden`, and `runtime-initialize`. Preview performs no
host or proposal mutation. Real apply requires explicit approval bound to the
cryptographic hash of that exact preview; any changed input invalidates approval.
A conflict blocks apply.

Apply validates a complete candidate in same-volume staging, including structural
host-readiness checks against the staged view. Configured host quality commands
are not run during apply. Before promotion it creates a complete,
restorable backup of every affected destination and the reviewed proposal, then
writes a durable transaction journal containing the preview hash, original and
candidate hashes, backup paths, ordered operations, and transaction state. The
journal is write-ahead: journal/preimage metadata is flushed before each mutation;
every operation progresses through `prepared`, `applied`, and `verified`; startup
treats an unconfirmed operation as unknown and compares both preimage and candidate
before choosing completion or rollback. Promotion uses atomic same-volume file
replacement for supported regular files. Because whole-repository atomic rename
is not portable around `.git`, Windows
open handles, and existing host content, the guarantee is atomic per-path
promotion plus verified all-or-nothing rollback.

On failure, completed operations are reversed and every original hash is verified.
A verified rollback leaves the original host byte-identical and returns nonzero.
If rollback cannot be verified, staging, backup, and journal are retained; status
becomes `recovery-required`; the command returns the dedicated recovery exit code
and prints deterministic recovery instructions. Backups are removed only by a
later explicit cleanup. There is no `--force` or other path that bypasses preview,
conflict handling, backup, approval, or recovery.

The guaranteed preimage covers existence, file bytes, line endings, and portable
mode/read-only metadata recorded by the implementation. Unsupported special files,
ACL/alternate-stream requirements, cross-volume destinations, or preflight
sharing/locking constraints fail before mutation. Abrupt power-loss atomicity is
not promised; process interruption is recovered from the flushed journal on the
next invocation.

### 5. Host readiness is a separate bounded profile

Introduce an explicitly named host-readiness command/profile (`host-doctor` at the
contract level). It does not reuse framework doctor output or claim framework
health. It checks:

- bundle/receipt schema, dependency closure, and managed-asset integrity/drift;
- valid host identity manifest, `project.config.json`, Copilot instructions, and
  six constitution files with no unresolved required placeholders;
- source frontmatter/schema for installed agents, skills, prompts, and lifecycle
  artifacts;
- clean runtime seed and forbidden-fingerprint absence;
- ledger tables/columns matching the existing schema and zero operational rows at
  adoption (recorded in the adoption receipt, not required forever);
- local DB/cache/backup/generated-output ignore safety and required source assets
  not ignored or tracked incorrectly;
- presence and validity of explicitly configured host test/lint/typecheck/build
  command tokens, when supplied.

Framework-only governance, current-PI dogfooding, framework test baseline,
framework stale-doc checks, and framework generated surfaces are reported `N/A`,
not PASS. Exit semantics are: `0` all required host checks pass; `1` readiness
failure; `2` usage or invalid configuration; `3` interrupted transaction or
recovery required. An installation message may say `installed; host readiness
PASS` only after exit 0; otherwise it reports the bounded failure state.

Quality commands execute only through an explicit post-install
`host-doctor --run-quality` action. Before execution, output MUST disclose the
working directory, tokenized argv, timeout, environment policy, network policy,
and that command filesystem/external side effects are outside bootstrap rollback.
Commands use argument arrays without a shell. An explicitly confirmed
`not-configured` command is `N/A`, not PASS.

### 6. Migration is inventory-first and non-destructive

Before preview, classify the installation as `fresh`, `proposal-only`,
`managed-current`, `managed-drift`, `legacy-broad-copy`, `partial-or-interrupted`,
`foreign-collision`, or `mixed-contaminated`. Each destination is classified as
absent, managed-unchanged, managed-modified, generated-stale, host-owned,
forbidden-contamination, or conflict.

Unknown, host-owned, and modified content is preserved unless the exact approved
preview replaces it. Contamination candidates are surfaced, not deleted. Existing
link/junction adoption is detached and inventoried only through an explicit
migration path; it is never mutated through the linked tree. Legacy `--apply`
remains parse-compatible but maps to corrected, non-refreshing, preview-first
semantics. Unsafe legacy options fail with migration guidance. An unchanged rerun
is a no-op with the same semantic manifest and no new backup or ledger rows.

SDD-058 migration does not delete contamination. It may replace an enumerated
managed destination after exact approval and backup; all other contamination is
reported and preserved for a separately approved cleanup feature.

A reviewed legacy proposal without the new baseline remains untouched. Apply
routes it to explicit baseline-adoption migration, which generates a candidate and
proposed baseline beside the reviewed proposal, previews every difference as
preserved/convergent/conflict, and establishes the baseline only after exact
approval and backup. Normal apply/refresh remain blocked until that migration
commits.

### 7. Cross-platform fixtures are realistic and isolated

Automated tests construct temporary committed git repositories for a realistic
Node/Express host and a materially different Python library/service host. They use
local bare remotes for deterministic offline remote/default-branch evidence,
deliberate LF/CRLF and permission variations, and host-owned `.github` content.
The Node fixture includes a partially edited proposal; the Python fixture includes
fresh and already-adopted/rerun scenarios.

Equivalent behavioral assertions run on Windows and POSIX CI. Manifest paths are
POSIX-relative and independent of temporary absolute roots. Preserved files remain
byte-identical, including line endings; new managed text is UTF-8/LF. Core behavior
MUST not depend on symlinks, junctions, POSIX executable bits, or case-only renames.
Injected filesystem failures prove rename, rollback, journal, and recovery states.
No test mutates a real host or the real framework ledger.

### 8. Responsibilities are separated behind compatibility adapters

`bootstrap.py` remains a thin parser and dispatcher. The implementation plan MUST
keep distinct stdlib-only responsibilities for inventory/evidence, proposal and
baseline refresh, reusable-asset manifest/dependency validation, identity
rendering, migration classification, transaction/recovery, and host readiness.
Legacy flags call these canonical paths through a compatibility adapter; they do
not retain alternate unsafe implementations. PLAN may assign filenames and tasks
for new SDD-058 modules but MUST NOT alter Appendix A membership or collapse
responsibilities back into broad copy/regenerate or framework-doctor code paths.

## Options considered

### Proposal tracking

- **Versioned generated baseline with three-way hashes (selected).** Pros: proves
  untouched versus edited without guessing; deterministic conflicts; recoverable.
  Cons: stores additional metadata/baseline bytes and requires schema versioning.
- **Infer edits from TODO markers or current text.** Pros: little metadata. Cons:
  cannot distinguish human edits from regenerated content; repeats the defect.
- **Never support refresh.** Pros: simplest safety model. Cons: prevents users
  from incorporating newly discovered evidence or renderer improvements.

### Asset selection

- **Dependency-closed allowlist at source (selected).** Pros: default-deny and
  auditable; contamination cannot enter staging. Cons: every reusable dependency
  must be curated and versioned.
- **Copy broad trees then delete denied paths.** Pros: easy initial implementation.
  Cons: selection is not default-deny; cleanup omissions recreate contamination.
- **Link the complete framework `.github/`.** Pros: live updates. Cons: imports
  workflows and framework assumptions, bypasses versioning, and conflicts with
  host identity and rollback guarantees.

### Transaction boundary

- **Complete staging, backup, journal, atomic per-path promote, verified rollback
  (selected).** Pros: realistic on Windows/POSIX; strong recovery evidence. Cons:
  extra disk I/O and transaction complexity.
- **Whole-repository atomic rename.** Pros: conceptual all-or-nothing swap. Cons:
  not portable around `.git`, open handles, volumes, and host-owned paths.
- **Per-file writes with best-effort backup.** Pros: simpler. Cons: can leave a
  mixed host after exceptional failure.

### Readiness

- **Separate bounded `host-doctor` profile (selected).** Pros: truthful name,
  check composition, and exit semantics; no confusion with ADR-025 local/CI
  framework profiles. Cons: another explicit command/profile to maintain.
- **Add host mode to framework doctor.** Pros: one entry point. Cons: risks
  conflating framework and host promises and complicates existing profile meaning.
- **Documentation-only fallback.** Pros: smaller implementation. Cons: owner
  approved the automated bounded profile; weaker user experience.

### Migration

- **Inventory, classify, preview, and preserve unknown work (selected).** Pros:
  safe for contaminated and locally modified hosts; supports idempotence. Cons:
  cannot automatically clean every legacy host.
- **Delete known framework-looking paths.** Pros: fast cleanup. Cons: appearance
  does not prove ownership; may delete host work.
- **Support only fresh hosts.** Pros: small scope. Cons: abandons users already
  exposed to the defective flow and violates PQ-06.

## Consequences

- Positive: reviewed proposal decisions cannot be silently regenerated by apply.
- Positive: contamination is prevented by construction rather than detected after
  broad copy.
- Positive: host identity and readiness claims become explicit, deterministic,
  and testable.
- Positive: failures have a portable recovery contract and legacy hosts retain
  unknown work.
- Negative: `brownfield-core@1` requires curation and compatibility rendering;
  optional framework capabilities are intentionally absent from the first bundle.
- Negative: staging, complete backup, journaling, and dual-platform fixtures add
  implementation and CI cost.
- Neutral: current greenfield behavior and framework doctor local/CI profiles are
  unchanged by this decision.
- Neutral: no new dependency, constitution edit, ledger schema change, cloud
  integration, or real-host mutation is authorized.

## Approval and sequencing

This ADR is **accepted**. On 2026-07-12, Rodolfo Lerma (owner) selected Option 1
and approved ADR-026 and the SDD-058 SPEC together. Sprint Executive Manager
recorded the approval as local ledger decision 5. This joint approval releases
PLAN/TASKS only; validation remains unlocked until TASKS, and no implementation,
commit, push, or real-host apply is authorized. The later exact pre-push package
requires a separate owner approval.

No non-fixture host may be mutated until a separate recorded owner approval names
the target repository, exact preview hash, backup location, and recovery command.
Joint ADR/SPEC approval and pre-push approval do not satisfy that real-host gate.
Automated fixtures are exempt only when positively identified under the test
temporary root as disposable.

## Appendix A: Immutable `brownfield-core@1` membership

All listed entries use their repository-relative source and destination unless
marked render/seed. Directory notation means the named `SKILL.md`, not a future
glob. Any membership change requires ADR/SPEC amendment and renewed owner approval.

- **Render:** `.github/copilot-instructions.md`, `project.config.json`, host
  `spec-driven-development/{README.md,CONTEXT.md}`,
  `spec-driven-development/constitution/{mission,tech-stack,principles,roadmap,decision-policy,quality-policy}.md`,
  `spec-driven-development/roster/{agents,skills,skill_packs}.json`, and
  `spec-driven-development/.adoption/{bundle-manifest,host-identity,receipt}.json`.
- **Seed:** `spec-driven-development/backlog/{IDEAS,BACKLOG}.md` and
  `spec-driven-development/{dispatches,specs,sprints,sessions,fleet,exec}/.gitkeep`.
  Runtime-initialize `spec-driven-development/ledger/fleet.db` from the listed
  schema with zero operational rows; the database is not copied or tracked.
- **Agents (render):** `.github/agents/{principal-executive-manager,principal-product-manager,principal-architect,principal-software-developer,sprint-executive-manager,developer-general,qa-engineer-general}.agent.md`.
- **Prompts (render command references):** `.github/prompts/{ask,triage,clarify,grill,spec,plan,tasks,analyze,fleet,implement,qa,retro,state,replan,evolve,constitution}.prompt.md`.
- **Core skills:** `.github/skills/core/{sdd-constitution,project-context,constitution-sync,pre-work-check,git-workflow,testing-conventions}/SKILL.md`.
- **Workflow skills:** `.github/skills/workflow/{grill-me,grill-with-docs,triage,to-spec,to-plan,to-tasks,implement}/SKILL.md`.
- **Engineering skills:** `.github/skills/engineering/{tdd,tdd-gate,diagnose,code-review,improve-architecture}/SKILL.md`.
- **Operational skills:** `.github/skills/operational/{em-communication-discipline,fleet-coordinator,handoff,lesson-capture,pi-planning,respect-existing,session-self-review,stakeholder-pressure-defense}/SKILL.md`.
- **Instructions:** `.github/instructions/sdd-workflow.instructions.md`; rendered
  `fleet-workers.instructions.md` is a disabled entry activated only by a
  confirmed worktree profile.
- **Templates/docs:** `spec-driven-development/templates/{feature-spec,lightweight-feature,clarification-log,validation,plan,task-list,agent-brief,review-report,handoff,level-2-decision,stakeholder-pressure-response}.md`,
  `docs/ADR/TEMPLATE.md`, and `docs/CLI-PATTERN.md`.
- **CLI/ledger:** `spec-driven-development/cli/{__init__,bootstrap,dedup,fleet,qa,retro,schema_lint,done_check,tdd_gate_check}.py`,
  `spec-driven-development/ledger/{__init__,init_ledger,ledger_cli}.py`, and
  `spec-driven-development/ledger/schema.sql`.
- **New SDD-058 modules:**
  `spec-driven-development/cli/{brownfield_inventory,brownfield_proposal,brownfield_manifest,brownfield_identity,brownfield_migration,brownfield_transaction,host_readiness,brownfield_compat}.py`.

## Appendix B: Host identity schema v1

The manifest is a JSON object with `schema_version` (`"1"`), `generated_at`
(UTC ISO-8601), `target_head` (full commit SHA), `fields`, and `renderers`. Each
`fields` member has `value`, `classification` (`evidence`, `default`, or `human`),
`evidence_paths` (sorted POSIX-relative string array), `ambiguity` (`none`,
`multiple`, `missing`, or `conflict`), `confidence` (number from 0 through 1 or
null for human values), `confirmed_by` (non-empty string or null), and
`confirmed_at` (UTC ISO-8601 or null). `renderers` contains exactly the non-empty
string properties `project_config`, `copilot_instructions`, `constitution`,
`rosters`, and `seeds`.

Required fields and types are:

| Field | Value type | Classification/confirmation |
|-------|------------|-----------------------------|
| `project_name` | non-empty string | evidence or human; confirmation required |
| `repo_url` | sanitized HTTPS/SSH URL string or null | evidence/human; confirmation required, explicit null allowed |
| `default_branch` | non-empty string | evidence or human; confirmation required |
| `owner` | non-empty string | human; confirmation required |
| `team` | non-empty string or null | human; explicit confirmation required |
| `mission` | non-empty string | human; confirmation required |
| `article_xi_cutover` | `YYYY-MM-DD` string | default/human; confirmation required |
| `stack` | sorted string array | evidence/human; confirmation required |
| `quality_commands` | object with exactly `test`, `lint`, `typecheck`, `build`; each value is `{state, argv, cwd, timeout_seconds, environment_policy, network_policy}` | human-confirmed; see exact rules below |
| `branch_convention` | non-empty string | evidence/human; confirmation required |
| `commit_convention` | non-empty string | evidence/human; confirmation required |
| `source_documents` | sorted POSIX-relative string array | evidence/human; confirmation required |
| `approval_boundaries` | sorted non-empty string array | human; confirmation required |
| `worktree_profile` | boolean | human; confirmation required |

Rendered `project.config.json` contains exactly `schema_version`, `project_name`,
`repo_url`, `default_branch`, `owner`, `team`, `article_xi_cutover`,
`quality_commands`, `branch_convention`, `commit_convention`, and
`approval_boundaries`, in that order. Mission, stack, and source documents are
rendered into Copilot instructions/constitution and remain in the identity
manifest rather than duplicating prose into project config.

For each quality-command value, `state` is `configured` or `not-configured`;
`argv` is a string array; `cwd` is a POSIX-relative string or null;
`timeout_seconds` is an integer from 1 through 3600 or null;
`environment_policy` is `minimal` or `inherit-confirmed`; and `network_policy` is
`deny` or `allow-confirmed`. When configured, `argv` is non-empty, `cwd` is
non-null, and timeout is non-null. When not configured, `argv` is empty and
`cwd`/timeout are null; policy values remain explicit.

Remote normalization strips HTTPS userinfo, any URL password/token, query strings,
fragments, and secret-bearing environment expansions. The conventional non-secret
SSH username `git` MAY remain in `ssh://git@host/path` and SCP-like
`git@host:path`; any other SSH username requires human confirmation and MUST NOT
contain a password/token. Credential-bearing or ambiguous remotes block until a
sanitized value is human-confirmed. Raw remotes and secrets MUST NOT enter
preview, manifest, receipt, journal, or generated files.

## Compliance

- [x] Stdlib-only architecture; no new runtime or test dependency proposed.
- [x] Existing ledger schema retained; adoption receipt/manifest is file-based.
- [x] No constitution edit or semantic-version bump proposed.
- [x] Windows and POSIX behavior specified without symlink or executable-bit
      dependency.
- [x] Unknown host work is preserved by default.
- [ ] Owner approves ADR-026 and SDD-058 SPEC together.
- [ ] Status changed to accepted only after recorded owner approval.
