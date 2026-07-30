---
id: SDD-20260712BROWNFIELD-spec
type: spec
status: done
owner: principal-architect
updated: 2026-07-29
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# SPEC: SDD-058 -- Brownfield bootstrap correctness

- Feature ID: SDD-058
- Sprint: PI-9 / Sprint 3 (overall Sprint 24)
- Priority: P1; RICE 8.0
- CLARIFY: [clarify.md](clarify.md)
- Validation: [validation.md](validation.md)
- Architecture decision: [ADR-026](../../docs/ADR/026-transactional-brownfield-adoption.md)
- Status: **DONE -- 70/70 validation IDs checked; exact repaired package green on public Windows/POSIX CI**
- Approval: Rodolfo Lerma (owner) selected Option 1 on 2026-07-12, jointly
  approving ADR-026 and this SPEC; recorded as local ledger decision 5.

---

## 1. Problem statement

The first real Node/Express brownfield adoption proved four coupled correctness
defects. Applying a reviewed proposal regenerates it first and can erase human
answers (B1). Apply copies broad framework trees and imports framework identity,
backlog, specs, sprints, dispatches, executive snapshots, and ledger history into
the host (B2). It does not generate truthful host-specific Copilot instructions
or `project.config.json` (B3). The existing doctor validates this framework and
cannot honestly establish generic host readiness (B4).

A corrected brownfield flow must make user intent and ownership explicit. Normal
apply consumes the reviewed proposal without refresh. Reusable assets are selected
from a dependency-closed allowlist. Host identity is generated from confirmed
provenance-bearing values. Every mutation is previewed, backed up, staged, and
recoverable. Host readiness has bounded semantics distinct from framework health.
Legacy and contaminated hosts are classified and preserved rather than blindly
cleaned.

## 2. Goals

- **G-01 (B1):** Preserve reviewed proposal bytes during normal apply and provide
  separate, explicit, conflict-aware refresh based on a generated baseline.
- **G-02 (B2):** Install only a versioned dependency-closed reusable-asset bundle;
  initialize clean host-owned runtime state with no framework history.
- **G-03 (B3):** Generate deterministic host Copilot instructions and
  `project.config.json` from a confirmed identity manifest with explicit
  evidence/default/human provenance.
- **G-04 (B4):** Provide a truthful bounded host-readiness profile that cannot be
  confused with framework doctor health.
- **G-05:** Make dry-run the default and guarantee complete staging, backup,
  preview-bound approval, atomic per-path promotion, and verified rollback or an
  explicit recovery-required state.
- **G-06:** Preserve safe legacy invocations, classify existing adoptions and
  contamination, protect unknown host work, and make unchanged reruns idempotent.
- **G-07:** Prove behavior using realistic Node/Express and materially different
  Python hosts on Windows and POSIX without mutating a real host.

## 3. Non-goals and explicit exclusions

- No greenfield bootstrap redesign unless a shared primitive is unavoidable for
  SDD-058 correctness; greenfield behavior is not acceptance scope.
- No real-host mutation during SPEC, PLAN, TASKS, or automated validation. A later
  destructive real-host apply requires separate recorded owner approval.
- No deletion or wholesale replacement of unknown host `.github/`, SDD artifacts,
  backlog, specs, sprints, dispatches, sessions, or ledger data.
- No broad framework-tree copy followed by cleanup.
- No redesign of framework doctor local/CI profiles established by ADR-025.
- No dashboard, Azure decommission, SDD-034, Sprint 23 retro reconciliation,
  unrelated backlog/housekeeping, agent hiring, cloud work, or historical cleanup.
- No new dependency, ledger schema migration, constitution change, or framework
  project-config schema migration outside the generated host contract.
- No optional domain skills, specialist agents, workflows, git hooks, issue
  integration, cloud/UI tooling, or model-upgrade tooling in `brownfield-core@1`.

## 4. Actors and user flows

### UF-01: Draft and review a proposal

1. The operator targets an existing committed git repository.
2. The tool inventories repository evidence and creates a proposal, host-identity
   manifest, and immutable generated baseline manifest.
3. The operator edits the proposal and supplies/confirms required host identity.
4. No live SDD installation is mutated.

### UF-02: Apply an existing reviewed proposal

1. The operator invokes brownfield apply; legacy `--apply` maps here.
2. The tool reads the existing proposal and baseline without running archaeology
   or proposal generation.
3. It inventories the host, validates identity and bundle dependency closure, and
   emits a no-mutation preview grouped by exact operation category.
4. Conflicts, missing confirmation, forbidden paths, or recovery state block apply.
5. The operator approves the exact preview hash.
6. The tool stages and validates the complete result, backs up all affected paths
   and proposal, promotes the transaction, then runs host readiness.
7. Success is reported only when the bounded readiness profile exits 0.

### UF-03: Explicitly refresh a proposal

1. The operator invokes refresh separately from apply.
2. The tool inventories new evidence and compares baseline, reviewed proposal,
   and candidate output.
3. Safe upstream-only changes may be previewed for adoption; user-only changes are
  preserved; convergent dual changes are preserved; non-convergent dual changes
  are conflicts.
4. Conflict resolution is explicit per file. The old proposal and baseline remain
   recoverable. Refresh never applies the framework.

### UF-04: Migrate an existing or contaminated adoption

1. The operator explicitly requests migration.
2. Inventory classifies the installation and every affected path.
3. The preview identifies managed drift, host-owned content, foreign collisions,
   and contamination candidates without deleting them.
4. Only the exact approved migration operations run through the same transaction.
5. A linked/junction adoption must be detached and inventoried before curated copy.

### UF-05: Rerun or recover

- An unchanged rerun reports no changes and creates no backup, transaction, or
  operational ledger row.
- An interrupted transaction blocks other mutations. Recovery either verifies
  commit completion or restores and verifies original hashes; uncertainty exits
  recovery-required and preserves all evidence.

## 5. Normative requirements

RFC-2119 terms MUST, MUST NOT, SHOULD, and MAY are normative.

### 5.1 Proposal preservation and refresh (B1)

- **R-001:** Normal apply MUST consume the existing reviewed proposal bytes and
  MUST NOT invoke archaeology, proposal generation, or refresh.
- **R-002:** Proposal generation MUST create a versioned baseline manifest that
  records source revision, evidence digest, schema/renderer versions, and each
  generated file's POSIX-relative path, SHA-256, and byte length. A lossless
  generated baseline MUST remain available.
- **R-003:** Refresh MUST be a separate explicit operation and MUST classify each
  file through a three-way comparison of baseline, reviewed proposal, and new
  candidate. It MUST NOT infer edit state from `TODO` markers or content patterns.
- **R-004:** Refresh MUST preserve user-only edits, MAY update only files proven
  unchanged from baseline, MUST preserve a convergent reviewed/candidate value
  without conflict, and MUST classify non-convergent concurrent user/upstream
  changes as conflicts requiring explicit resolution. The prior proposal and
  baseline MUST remain recoverable.
- **R-005:** A missing, invalid, path-escaping, or internally inconsistent baseline
  MUST stop normal refresh/apply with actionable guidance; no fallback
  regeneration is permitted. A legacy proposal with no baseline MUST remain
  untouched and route to explicit baseline-adoption migration that generates a
  candidate/baseline beside it, previews every difference, and establishes the
  baseline only after exact approval and backup.

### 5.2 Versioned reusable-asset allowlist and clean state (B2)

- **R-006:** Apply MUST use a versioned `brownfield-core@1` manifest with one
  explicit `copy`, `render`, `seed`, `preserve`, or `forbid` entry per destination,
  including dependencies and hashes/renderer versions. Default deny applies to
  source selection and managed mutation. Unlisted existing host paths are
  inventory-only and preserved unless they collide with an enumerated destination
  or violate a separate path-safety rule.
- **R-007:** Manifest validation MUST reject missing dependencies, duplicate or
  ancestor/descendant destination conflicts, source paths outside the framework
  root, target paths outside the host root, absolute paths, `..` traversal,
  unsupported operations, hash mismatch, and cyclic dependencies before preview.
- **R-008:** Source selection MUST itself be allowlisted. Implementations MUST NOT
  copy broad trees into staging or the host and then remove denied paths.
- **R-009:** The core bundle MUST include only the rendered identity/governance,
  core agents, canonical lifecycle prompts, approved core/workflow/engineering/
  portable operational skills, applicable instructions, lifecycle templates,
  ADR/CLI pattern docs, and dependency-closed lifecycle CLI/ledger membership
  recorded by ADR-026 Appendix A. Generated rosters MUST enumerate exactly
  installed assets. PLAN MUST NOT add, remove, or substitute bundle members;
  membership changes require ADR/SPEC amendment and renewed owner approval.
- **R-010:** The core bundle MUST forbid framework Copilot instructions/config,
  backlog/spec/sprint/dispatch/session/fleet/exec history, feature prompts,
  management/PI/status history, historical ADRs, scorecards, archetypes, domain or
  specialist assets, optional integrations, workflows/hooks, tests/caches,
  `fleet.db`, and reorder history.
- **R-011:** A fresh host MUST receive only host-owned seed state: empty host
  backlog headings, empty lifecycle directories or approved generic placeholders,
  a new ledger from the existing schema with zero operational rows, absent/empty
  reorder history, and no framework executive snapshot. Any required exec seed
  MUST make no PI/sprint/feature claim.
- **R-012:** Clean-state verification MUST combine a versioned forbidden-
  fingerprint set with positive seed assertions and a zero-row ledger query. No
  framework owner/repository identity, `PI-9`, Sprint 24, SDD-058/prior framework
  rows, framework backlog titles, historical paths, reorder entries, or generated
  executive claims may survive.

### 5.3 Host identity and deterministic rendering (B3)

- **R-013:** A versioned host-identity manifest MUST record, per field, value,
  classification (`evidence`, `default`, `human`), provenance/evidence path,
  confidence/ambiguity, confirmation state, and schema version.
- **R-014:** `project_name`, normalized `repo_url`, and `default_branch` MAY be
  evidence-derived but MUST be human-confirmed. `owner` and `mission` MUST be
  human-supplied. `team` MUST be human-supplied or explicitly confirmed null.
  Adoption date/`article_xi_cutover` MAY use the safe current-date default.
- **R-015:** The manifest MUST also capture confirmed stack/quality commands,
  branch/commit conventions, source-of-truth documents, and approval boundaries
  required to render host instructions. Ambiguous or missing required values MUST
  block preview/apply.
- **R-016:** Host `.github/copilot-instructions.md` and `project.config.json` MUST
  be rendered deterministically from the confirmed manifest as UTF-8/LF with
  stable ordering. They MUST NOT copy framework identity, fabricate facts, emit
  unresolved required placeholders, or include temporary absolute paths. Field
  types, nullability, provenance, confirmation metadata, renderer versions,
  quality-command states, and exact project-config keys MUST follow ADR-026
  Appendix B.
- **R-016A:** Remote normalization MUST strip HTTPS userinfo, passwords/tokens,
  query strings, fragments, and secret-bearing environment expansions. The
  conventional non-secret SSH username `git` MAY remain; another SSH username
  requires confirmation and MUST NOT contain a password/token. Ambiguous or
  credential-bearing remotes MUST block until a sanitized value is confirmed;
  raw remotes/secrets MUST NOT enter tracked files or operational evidence.
- **R-017:** Existing host identity files MUST be classified as host-owned or
  managed. Replacement requires exact preview approval and backup; unmanaged
  content MUST be preserved by default.

### 5.4 Preview, transaction, backup, and recovery

- **R-018:** Dry-run MUST be the default, MUST perform no mutation to host or
  proposal, and MUST produce machine-readable and human-readable previews with
  exactly these categories: `create`, `replace`, `preserve`, `conflict`,
  `forbidden`, and `runtime-initialize`.
- **R-019:** Preview output MUST be deterministic for equivalent inputs, use
  POSIX-relative paths, include reasons and before/after hashes where applicable,
  and produce a cryptographic preview hash. Real apply MUST require explicit
  approval bound to that exact hash; changed inputs invalidate approval.
- **R-020:** `conflict`, invalid identity/bundle, dirty recovery state, path-safety
  failure, insufficient backup/staging capacity, or unapproved replacement MUST
  block mutation. No force/skip/warn flag may bypass preview, conflicts, backup,
  approval, or recovery.
- **R-021:** Before promotion, apply MUST build and validate the complete candidate
  in same-volume staging and run the host-readiness checks that are meaningful on
  the staged view.
- **R-022:** Apply MUST create a complete restorable backup of every affected
  destination and the reviewed proposal, then durably record preview hash,
  original/candidate hashes, backup paths, ordered operations, and transaction
  state in a journal. Journal/preimage metadata MUST be flushed before each
  mutation; each operation MUST record `prepared`, `applied`, and `verified`.
- **R-023:** Promotion MUST use atomic same-volume per-path replacement where
  supported. Any failure MUST reverse completed operations and verify every
  original hash. Startup MUST resolve unconfirmed operations by checking both
  preimage and candidate. Verified rollback MUST leave original host/proposal
  existence, bytes, line endings, and supported portable mode/read-only metadata
  intact.
- **R-024:** If rollback or interrupted-state resolution cannot be verified, the
  command MUST preserve stage/backup/journal, return recovery-required, print
  deterministic recovery instructions, and block further mutation. Backup cleanup
  MUST be a later explicit operation. Unsupported special metadata, cross-volume
  destinations, or preflight sharing/locking constraints MUST fail before
  mutation. Process interruption is recoverable; abrupt power-loss atomicity is
  not claimed.

### 5.5 Truthful host readiness (B4)

- **R-025:** The product MUST expose a separately named host-readiness command or
  profile whose heading and documentation identify host readiness, not framework
  health. It MUST NOT reuse a framework-doctor PASS as host evidence.
- **R-026:** Required host checks MUST cover bundle/receipt validity and dependency
  closure; managed asset integrity/drift; valid confirmed identity/config and
  Copilot instructions; six constitution files; installed source frontmatter;
  unresolved placeholders; positive runtime seed; forbidden fingerprints;
  existing ledger schema and adoption-time zero-row receipt; ignore/tracked-file
  safety; and validity/presence of configured host quality command tokens.
- **R-027:** Framework-only governance, stale-doc, current-PI dogfood, framework
  test-baseline, and generated-dashboard checks MUST be reported `N/A`, never PASS
  or silently omitted.
- **R-028:** Host readiness MUST exit `0` only when every required host check
  passes; `1` for readiness failure; `2` for usage/invalid configuration; and `3`
  for interrupted transaction or recovery required. Apply MUST not print ready or
  equivalent success wording unless readiness exits `0`.
- **R-028A:** Apply-time staged readiness MUST run structural checks only. Quality
  commands MAY execute only through explicit post-install
  `host-doctor --run-quality`, after disclosing working directory, tokenized argv,
  timeout, environment/network policies, and that external/filesystem side effects
  are outside rollback. Commands MUST use argument arrays without a shell;
  confirmed `not-configured` commands are `N/A`, not PASS.

### 5.6 Migration, compatibility, and idempotence

- **R-029:** Inventory MUST classify the installation as `fresh`, `proposal-only`,
  `managed-current`, `managed-drift`, `legacy-broad-copy`,
  `partial-or-interrupted`, `foreign-collision`, or `mixed-contaminated`, and each
  destination as absent, managed-unchanged, managed-modified, generated-stale,
  host-owned, forbidden-contamination, or conflict.
- **R-030:** Existing SDD installations MUST require explicit migration. Unknown,
  host-owned, or modified content MUST NOT be deleted automatically. Contamination
  candidates MUST be previewed and retained. SDD-058 MUST NOT delete
  contamination; it MAY replace only an enumerated managed destination after exact
  approval and backup. Other cleanup is a separate feature.
- **R-031:** Legacy `brownfield <target>`, `--draft-only`, and `--apply` parsing
  MUST remain compatible where safe. Legacy apply MUST map to corrected
  non-refreshing preview-first behavior. Unsafe options/semantics MUST fail with
  migration guidance rather than invoke old broad-copy/regeneration paths.
- **R-032:** An unchanged rerun against the same approved inputs MUST report no
  changes and MUST create no new backup, mutation journal, or operational ledger
  row. Managed drift MUST be reported, not silently overwritten.
- **R-033:** Existing symlink/junction host-link adoption MUST be detected and
  MUST require explicit detach/inventory migration before curated copy; the tool
  MUST NOT mutate through the linked tree.

### 5.7 Security, portability, and failure behavior

- **R-034:** Every source, proposal, stage, backup, and destination path MUST be
  normalized and containment-checked before access. Symlink/junction traversal,
  reserved/control names, absolute paths, `..`, case-fold collisions, and paths
  entering `.git` MUST fail closed.
- **R-035:** Manifest and identity text MUST be treated as data, not shell input.
  Subprocess calls MUST use argument arrays; no command interpolation or execution
  of host-provided quality commands may occur without explicit configured command
  tokens and the approved readiness contract.
- **R-036:** Newly generated managed text MUST be UTF-8/LF. Preserved host files
  MUST remain byte-identical, including line endings and content. Core correctness
  MUST not depend on POSIX executable bits, symlinks/junctions, case-only renames,
  or Windows-only behavior.
- **R-037:** Expected operational failures MUST produce concise actionable stderr
  output and nonzero exit without traceback. Secrets, full environment values,
  and sensitive file contents MUST NOT appear in preview, journal, or errors.
- **R-038:** The CLI and all new test helpers MUST remain Python stdlib-only and
  preserve the testable `main(argv) -> int` pattern in `docs/CLI-PATTERN.md`.

### 5.8 Fixtures, validation, and governance

- **R-039:** Automated tests MUST create isolated committed temporary hosts: a
  realistic Node/Express repository with package/lock/Express/tests/README/
  existing `.github`/gitignore/remote/default-branch evidence and partially edited
  proposal; and a materially different Python library/service with `pyproject`,
  package/tests/CI conventions, missing Copilot instructions in one scenario, and
  already-adopted/rerun coverage.
- **R-040:** Equivalent behavioral assertions MUST run on Windows and POSIX CI or
  equivalent runners. Expected manifests MUST not contain absolute temp paths.
  Tests MUST exercise path separators, LF/CRLF preservation, permission variance,
  replacement/rename behavior, and injected rollback/recovery failures.
- **R-041:** Tests MUST NOT mutate a real host, real framework ledger, or generated
  executive surfaces. Fixture git remotes MUST be local/offline and deterministic.
- **R-042:** Implementation MUST begin with focused RED evidence, then focused
  GREEN evidence. The full suite MUST finish at least 668 passed / 2 skipped with
  no baseline regression; schema, origin, stale-doc, governance, Article X, local
  doctor, B-1, and B-2 gates MUST be green.
- **R-043:** ADR-026 and this SPEC MUST be approved together by the Architect and
  owner before PLAN/TASKS. Validation remains unlocked until TASKS. Stage-1 spec
  compliance MUST pass before Stage-2 code quality. Owner approval of the exact
  pre-push package and green public CI/B-4 are required before DONE.
- **R-044:** No command may mutate a non-fixture host until separate recorded owner
  approval names the target repository, exact preview hash, backup location, and
  recovery command. ADR/SPEC approval and pre-push approval do not satisfy this
  gate. Automated fixtures are exempt only when positively identified under the
  test temporary root as disposable.

## 6. Error and exit contract

| Exit | Meaning | Required behavior |
|------|---------|-------------------|
| `0` | Requested read-only operation succeeded, no-op rerun, transaction committed and host readiness passed, or recovery verified | Print bounded result and receipt/preview reference; never overclaim framework health. |
| `1` | Domain/readiness failure | Examples: conflict, missing required identity, contamination requiring approval, readiness check failure, managed drift, failed apply with verified rollback. Print actionable remediation; no mixed host state. |
| `2` | Usage or invalid configuration/input | Examples: unsupported mode, invalid manifest/schema, malformed path, ambiguous required evidence, invalid approval hash. No mutation. |
| `3` | Interrupted transaction or recovery required | Preserve journal/stage/backup; block other mutation; print recovery command/instructions. |

Unexpected exceptions MUST be converted at the CLI boundary into nonzero,
actionable errors while preserving recovery evidence. No failure may print a
successful installation/readiness claim.

## 7. Initial reusable bundle contract

The normative selection rule and exact membership are ADR-026 Appendix A plus
R-006 through R-010. PLAN may assign implementation modules/tasks for new SDD-058
responsibilities but MUST NOT change membership. The following boundaries are
fixed:

| Profile area | Required in `brownfield-core@1` | Excluded/default-denied |
|--------------|---------------------------------|-------------------------|
| Identity | Rendered Copilot instructions, host config, host SDD README/CONTEXT, six reviewed constitution files | Framework identity/config and framework roadmap/status content |
| Agents | Four Principals, Sprint EM, Developer, QA; host-rendered where assumptions exist | Template, specialist, cloud/UI/dev-env agents; UX/Data optional only |
| Prompts | Canonical lifecycle set through DONE/replan/evolve/constitution | `hire`, `taskstoissues`, feature kickoff prompts |
| Skills | Approved core, workflow, engineering, and portable operational set from ADR-026 | Domain, archetype, role creation, host-link, cloud/UI/status skills |
| Instructions | SDD workflow; rendered fleet-workers only with confirmed worktree profile | Unadapted framework branch/environment instructions |
| Templates/docs | General lifecycle templates, ADR template, CLI pattern, generated host README | Worked example, model fixtures, framework plans/status/history |
| CLI/ledger | Dependency-closed lifecycle commands, package initializers, schema/init/query, generated rosters | Dashboard/state builders, reorder, deployment/model/issues tooling, source tests/data |
| Runtime | Host seeds and a new zero-row ledger | Framework backlog/spec/sprint/dispatch/exec/session/fleet/ledger/reorder state |

## 8. Acceptance criteria

- **AC-01 (R-001):** Given a reviewed proposal containing human byte changes, when
  normal apply is previewed and executed in a fixture, then proposal bytes are
  unchanged and no archaeology/proposal renderer is invoked.
- **AC-02 (R-002..R-005):** Given baseline/reviewed/candidate combinations, refresh
  deterministically classifies unchanged, upstream-only, user-only, convergent,
  and conflict; preserves prior proposal/baseline; safely adopts a baseline for a
  legacy proposal; and blocks an invalid baseline.
- **AC-03 (R-006..R-010):** The versioned bundle passes dependency closure and
  installs only enumerated sources. A malicious/unlisted source cannot enter even
  staging; broad-copy-then-clean is absent.
- **AC-04 (R-011..R-012):** Fresh Node and Python installations satisfy every
  positive seed assertion, zero-row ledger query, and forbidden-fingerprint check.
- **AC-05 (R-013..R-017):** Evidence/default/human identity fields retain
  provenance and confirmation. Missing/ambiguous required values block; confirmed
  inputs render deterministic host config/instructions with no framework identity
  or unresolved required marker; credential-bearing remote evidence is sanitized
  or blocked.
- **AC-06 (R-018..R-020):** Default dry-run performs zero mutation and emits exactly
  six categories with deterministic paths/reasons/hashes. Apply rejects stale
  approval hashes, conflicts, and every attempted bypass.
- **AC-07 (R-021..R-024):** Complete staging and backup precede promotion. Injected
  failures at preparation and promotion leave original bytes intact after verified
  rollback; injected rollback failure returns exit 3 and preserves recovery assets.
- **AC-08 (R-025..R-028):** Host readiness runs the exact portable checks, labels
  framework-only checks N/A, uses exits 0/1/2/3 correctly, and framework doctor
  output cannot be mistaken for host readiness; quality execution is explicit and
  disclosed outside apply rollback.
- **AC-09 (R-029..R-033):** Fixtures cover all installation classes and path
  classes. Unknown/modified work survives migration; legacy flags map safely;
  host-link is detected; unchanged reruns are no-op with no new side effects.
- **AC-10 (R-034..R-037):** Traversal, absolute/out-of-root, `.git`, symlink/
  junction, case-collision, control/reserved-name, malformed manifest, and command-
  injection inputs fail closed without mutation or sensitive output.
- **AC-11 (R-036, R-039..R-041):** Realistic Node/Express and materially different
  Python fixtures pass equivalent Windows/POSIX assertions for normalized paths,
  byte/newline preservation, UTF-8/LF generation, permissions, and rename behavior.
- **AC-12 (R-038, R-042):** No new runtime/test dependency exists; focused RED then
  GREEN is recorded; full suite is >=668 passed/2 skipped; lints, governance,
  Article X 3/3, local doctor, B-1, and B-2 are green.
- **AC-13 (R-043):** Recorded evidence proves ADR-026/SPEC owner approval preceded
  PLAN/TASKS, validation lock occurred only at TASKS, and two-stage QA ran Stage 1
  before Stage 2.
- **AC-14 (R-043):** Owner approves the exact pre-push package; public CI/B-4 is
  green; only then may SDD-058 be DONE and Sprint 24 close.
- **AC-15 (R-044):** A non-fixture apply is impossible without a separate approval
  receipt matching target, preview hash, backup location, and recovery command;
  fixture exemption is accepted only under a positively identified temp root.

## 9. Traceability

| Boundary | Product decisions | Architect decisions | Requirements | Acceptance |
|----------|-------------------|---------------------|--------------|------------|
| B1 proposal preservation | PQ-01 | AQ-01 | R-001..R-005 | AC-01, AC-02 |
| B2 allowlist/clean state | PQ-02, PQ-04 | AQ-02 | R-006..R-012 | AC-03, AC-04 |
| B3 host identity/config | PQ-03 | AQ-03 | R-013..R-017 | AC-05 |
| Apply safety | PQ-07 | AQ-04 | R-018..R-024, R-044 | AC-06, AC-07, AC-15 |
| B4 truthful readiness | PQ-05 | AQ-05 | R-025..R-028 | AC-08 |
| Migration/compatibility | PQ-06 | AQ-06 | R-029..R-033 | AC-09 |
| Security/cross-platform fixtures | PQ-08 | AQ-07 | R-034..R-041 | AC-10, AC-11 |
| Boundaries/governance | PQ-01..PQ-08 | AQ-08 | R-038, R-042..R-044 | AC-12..AC-15 |

## 9.1 Minimum fixture scenario matrix

| Scenario | Node/Express Windows | Node/Express POSIX | Python Windows | Python POSIX |
|----------|----------------------|--------------------|----------------|--------------|
| Draft + baseline + identity | required | required | required | required |
| Reviewed proposal apply + exact dry-run | required | required | required | required |
| Refresh outcomes, including convergence/conflict | required | required | required | required |
| Clean allowlist/seed/readiness | required | required | required | required |
| Unchanged idempotent rerun | required | required | required | required |
| Representative promotion failure + verified rollback | required | required | required | required |
| Interrupted/recovery-required state | required | required | required | required |
| Legacy no-baseline adoption | required | required | required | required |
| Managed drift / contaminated migration | unit matrix + one fixture | unit matrix + one fixture | required | required |
| OS-specific link/permission/rename case | Windows equivalent required | POSIX equivalent required | Windows equivalent required | POSIX equivalent required |

All installation/path classifications require platform-neutral unit coverage.
An OS-inapplicable mechanism may use its named equivalent but may not be skipped
without equivalent behavioral proof.

## 10. Non-functional requirements

- **NFR-01 Security:** Default deny, path containment, no shell interpolation, no
  secret/content disclosure, and no mutation through links or `.git`.
- **NFR-02 Data integrity:** Proposal and unknown host bytes survive by default;
  every replacement is previewed, backed up, journaled, and recoverable.
- **NFR-03 Determinism:** Equivalent inputs produce semantically identical sorted
  manifests, rendered identity, preview categories, hashes, and exit semantics on
  Windows and POSIX.
- **NFR-04 Performance:** Inventory and preview SHOULD be linear in enumerated host
  files and bundle entries; no network access or package installation is allowed.
- **NFR-05 Observability:** Preview, transaction journal, receipt, readiness output,
  and recovery state provide enough hashes/reasons to audit without storing
  sensitive file content.
- **NFR-06 Compatibility:** Python 3.12+ stdlib; safe legacy flags preserved;
  framework doctor and greenfield behavior remain backward-compatible.
- **NFR-07 Maintainability:** Responsibilities remain separated behind one canonical
  path; compatibility adapters contain no alternate broad-copy/regeneration logic.

## 11. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Allowlist omits a transitive asset | Installed lifecycle fails | Versioned dependency graph; closure validation; staged host-doctor; both fixtures. |
| Host file ownership is misclassified | Host work loss | Receipt/baseline hashes; host-owned default; conflict + approval + backup. |
| Windows replacement/open handles fail | Partial install | Same-volume staging, journal, injected failure tests, verified rollback/recovery exit. |
| Identity evidence is plausible but wrong | Misoriented agents | Provenance and human confirmation; no owner/team inference; missing facts block. |
| Host quality commands execute unsafe text | Command injection | Tokenized confirmed commands only; no shell; explicit readiness configuration. |
| Fingerprint check becomes the only contamination guard | False confidence | Prevention by source allowlist plus positive seed and forbidden fingerprints. |
| Legacy host contains mixed framework and host data | Automated cleanup deletes work | Explicit mixed classification; no automatic deletion; exact migration preview. |

## 12. Approval gate

Architect review verdict: **APPROVED**. The technical questions AQ-01 through
AQ-08 are resolved, and ADR-026 plus this SPEC are internally aligned. On
2026-07-12, Rodolfo Lerma (owner) selected Option 1 and approved ADR-026 and this
SPEC together; Sprint Executive Manager recorded the approval as local ledger
decision 5.

This approval authorizes PLAN/TASKS only and releases the Article XI SPEC lock.
Validation remains draft/unlocked until TASKS. Implementation, commit, push, and
destructive real-host apply remain unauthorized. The exact pre-push package and
any non-fixture real-host apply each retain their separate owner approval gates.
