---
id: SDD-20260712BROWNFIELD-validation
type: validation
status: active
owner: principal-architect
updated: 2026-07-12
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# VALIDATION: SDD-058 -- Brownfield bootstrap correctness

- Feature ID: SDD-058
- Spec: [spec.md](spec.md)
- ADR: [ADR-026](../../docs/ADR/026-transactional-brownfield-adoption.md)
- Contract date: 2026-07-12
- Lock point: `/tasks`; locked by
  [tasks.md](tasks.md) on 2026-07-12 after joint ADR/SPEC owner approval and
  before any implementation or test edit
- Lock authority: Article X; TASKS preserves all 70 REQUIRED identifiers,
  including V-17A, V-21A, V-31A, V-38A, and V-54A
- Lock evidence: accepted ADR-026; approved active SPEC; active PLAN; TASKS exact
  traceability totals of 46 requirements, 15 acceptance criteria, and 70
  validation items; no implementation, worker dispatch, commit, push, or
  non-fixture mutation occurred during the lock transition
- Status: **LOCKED / ACTIVE AT IMPLEMENTATION -- local evidence and independent review recorded; owner approval and public CI pending**

This contract was authored before implementation and locked at TASKS under
Article X. Every REQUIRED item below must be proven; no item may be weakened,
waived, or silently deferred. Only V-01 through V-04 are checked at lock because
their design and sequencing evidence already exists. Every implementation,
fixture, review, owner-package, push, CI, and close item remains unchecked until
its real evidence exists.

---

## A. Design and gate evidence (REQUIRED)

- [x] **V-01 -- product decisions fixed.** PQ-01 through PQ-08 are recorded as one
  owner-approved package dated 2026-07-12; implementation does not weaken or
  substitute any approved default. Proves R-043, AC-13.
- [x] **V-02 -- Architect decisions closed.** AQ-01 through AQ-08 are answered in
  CLARIFY and represented consistently in proposed ADR-026, SPEC, PLAN, TASKS,
  and this contract. Proves R-043, AC-13.
- [x] **V-03 -- joint ADR/SPEC approval before downstream work.** Recorded owner
  evidence shows ADR-026 and SPEC were approved together before PLAN or TASKS
  existed; ADR status changes only after that approval. Approval evidence:
  Rodolfo Lerma (owner) selected Option 1 on 2026-07-12, jointly approving
  ADR-026 and the SDD-058 SPEC; Sprint Executive Manager recorded it as local
  ledger decision 5. The accepted ADR and approved SPEC existed before the PLAN
  and TASKS artifacts in this same uncommitted SDD-058 unit; TASKS records that
  chronology before implementation. Proves R-043, AC-13.
- [x] **V-04 -- validation lock timing.** This contract was approved during SPEC,
  remained draft/unlocked through PLAN, and is marked LOCKED / ACTIVE only at
  TASKS before any implementation or production-test edit. Proves R-043, AC-13.

## B. B1 proposal preservation and refresh (REQUIRED)

- [x] **V-05 -- apply preserves reviewed proposal exactly.** Node and Python
  fixtures contain human-edited/partially edited proposal bytes; normal apply
  preview and real fixture apply leave every proposal byte and baseline byte
  unchanged, and spies prove archaeology/proposal generation/refresh were not
  called. Proves R-001, AC-01.
- [x] **V-06 -- baseline manifest completeness.** Generated baseline records
  schema/bundle/source/evidence/renderer versions and per-file POSIX path,
  SHA-256, byte length, dependencies, and text policy; lossless baseline data is
  available and validated. Proves R-002, AC-02.
- [x] **V-07 -- five-outcome refresh classification.** Parameterized tests prove
  unchanged, upstream-only, user-only, convergent, and dual-change conflict from
  baseline/reviewed/candidate hashes, including multiple files and deterministic
  ordering. Proves R-003, R-004, AC-02.
- [x] **V-08 -- refresh preservation/conflicts.** User-only edits are preserved;
  convergent dual changes are preserved; non-convergent dual changes conflict; no
  conflict is overwritten; prior proposal and baseline remain recoverable;
  explicit per-file resolution is required. Proves R-003, R-004, AC-02.
- [x] **V-09 -- invalid and legacy baseline behavior.** Malformed, hash-mismatched,
  unsupported-version, or path-escaping baselines return nonzero with guidance and
  cause zero mutation. A missing legacy baseline routes to explicit baseline-
  adoption migration, preserves proposal bytes, previews differences, and records
  a baseline only after exact approval/backup. Proves R-005, AC-02.

## C. B2 exact allowlist, default deny, and clean runtime state (REQUIRED)

- [x] **V-10 -- exact versioned allowlist.** A structural test enumerates every
  immutable ADR-026 Appendix A `brownfield-core@1` entry and proves only approved,
  agents, prompts, skills, instructions, templates/docs, CLI/ledger dependencies,
  generated rosters, and seeds are included. Proves R-006, R-009, AC-03.
- [x] **V-11 -- dependency closure.** Tests prove all declared dependencies exist,
  graph order is stable, and missing dependency, cycle, duplicate destination,
  ancestor/descendant collision, hash mismatch, unknown operation/version, or
  renderer mismatch blocks before preview. Proves R-006, R-007, AC-03.
- [x] **V-12 -- source selection is allowlisted.** Spies/structural tests prove
  copying is invoked only for enumerated source files; no `.github` or
  `spec-driven-development` whole-tree copy occurs even in staging; an unlisted
  canary source never appears. Proves R-008, AC-03.
- [x] **V-13 -- default-denied assets absent.** Both fixtures contain none of the
  forbidden framework config/identity, backlog, specs, sprints, dispatches,
  sessions, fleet/exec history, feature prompts, PI/management/status documents,
  historical ADRs/scorecards, archetypes/domain/specialists/optional integrations,
  workflows/hooks, tests/caches, `fleet.db`, or reorder history. Proves R-010,
  AC-03, AC-04.
- [x] **V-14 -- positive seed contract.** Fresh fixtures contain host-specific
  backlog headings with no framework rows; approved empty/generic lifecycle
  placeholders; a new ledger from the existing schema with zero dispatch and
  decision rows; absent/empty reorder history; and no PI/sprint/feature claim in
  any required exec seed. Proves R-011, AC-04.
- [x] **V-15 -- contamination fingerprints plus positive proof.** A versioned
  forbidden-fingerprint test finds zero framework owner/repo identity, `PI-9`,
  Sprint 24, SDD-058/prior framework operational rows, framework backlog titles,
  copied historical paths, reorder records, or framework-generated exec content
  in either fixture; deliberately injected fingerprints are detected. Proves
  R-012, AC-04.
- [x] **V-16 -- no ledger schema change.** Installed `schema.sql` matches the
  approved existing schema hash/tables/columns and no migration alters it. The
  adoption receipt records zero operational rows. Proves R-011, R-026, AC-04,
  AC-08.

## D. B3 identity manifest and rendering (REQUIRED)

- [x] **V-17 -- provenance-bearing identity schema.** Tests validate field value,
  classification, evidence/default/human provenance, evidence path, confidence/
  ambiguity, confirmation, and schema version. Unknown/malformed fields and
  invalid classification fail. Proves R-013, AC-05.
- [x] **V-17A -- exact identity/project-config schema.** Every ADR-026 Appendix B
  field type, null rule, evidence cardinality, ambiguity/confidence value,
  confirmer/timestamp, renderer version, quality-command state, and exact ordered
  `project.config.json` key/type is tested. Proves R-013..R-016, AC-05.
- [x] **V-18 -- required versus derived fields.** `project_name`, normalized remote,
  and default branch are evidence-derived but require confirmation; owner and
  mission require human values; team requires a value or explicit null; adoption
  date is the only approved safe default. Commit history and remote organization
  never infer a person/team. Proves R-014, AC-05.
- [x] **V-19 -- missing/ambiguous identity blocks.** Missing owner/mission/team
  decision, multiple ambiguous remotes/default branches, unconfirmed evidence,
  or unresolved required quality/approval fields blocks preview/apply with exact
  remediation and zero mutation. Proves R-014, R-015, AC-05.
- [x] **V-20 -- deterministic host config.** Equivalent confirmed manifests render
  byte-identical UTF-8/LF `project.config.json` with stable key order and exact
  approved fields; no framework values, TODOs, temporary paths, or fabricated
  facts. Proves R-016, AC-05.
- [x] **V-21 -- deterministic Copilot instructions.** Node and Python manifests
  render materially host-specific, byte-stable instructions naming real source
  docs, stack/quality commands, branch/commit rules, owner/team/mission, and
  approval boundaries; framework identity and unresolved markers are absent.
  Proves R-015, R-016, AC-05.
- [x] **V-21A -- remote credential sanitization.** HTTPS userinfo, any password/
  token, query, fragment, or secret-bearing expansion is stripped and requires a
  confirmed sanitized value. Conventional SSH `git` usernames remain; other SSH
  usernames require confirmation. Raw secrets never enter output/evidence.
  Proves R-016A, AC-05, AC-10.
- [x] **V-22 -- existing identity ownership.** Existing host Copilot/config content
  is preserved by default; replacement appears under `replace`, requires exact
  approval and backup, and restores byte-identically on injected failure. Proves
  R-017, AC-05, AC-07.

## E. Dry-run, preview, transaction, backup, rollback, and recovery (REQUIRED)

- [x] **V-23 -- exact dry-run categories.** Machine and human previews expose
  exactly `create`, `replace`, `preserve`, `conflict`, `forbidden`, and
  `runtime-initialize`; every planned path appears once with reason and applicable
  hashes. Proves R-018, R-019, AC-06.
- [x] **V-24 -- dry-run is exact no-mutation.** Recursive byte/hash/stat snapshots
  before and after default dry-run prove zero host, proposal, baseline, ledger,
  journal, backup, staging, permission, mtime, and controlled metadata mutation.
  Read-induced access-time changes are explicitly excluded. Proves R-018, AC-06.
- [x] **V-25 -- deterministic preview and diff.** Equivalent Windows/POSIX fixture
  inputs produce semantically identical sorted previews with POSIX-relative paths,
  no absolute temp roots, stable reasons, before/after hashes, and the same preview
  hash. Proves R-019, AC-06, AC-11.
- [x] **V-26 -- approval binds exact preview.** Correct approval hash permits the
  fixture transaction; stale/wrong hash, changed proposal/evidence/host/bundle,
  missing approval, or interactive text not bound to the hash blocks with no
  mutation. Proves R-019, R-020, AC-06.
- [x] **V-27 -- no bypassing force path.** Parser and behavioral tests prove no
  force/skip/warn/legacy option can bypass conflict, identity, allowlist, staging,
  complete backup, exact approval, rollback, or recovery gates. Unsafe legacy
  options fail with guidance. Proves R-020, R-031, AC-06, AC-09.
- [x] **V-28 -- complete staging before mutation.** Candidate tree is built on the
  destination volume, includes every operation, passes staged manifest/identity/
  seed/structural-readiness validation without running host quality commands, and
  any staged failure leaves host/proposal unchanged. Proves R-021, R-028A, AC-07.
- [x] **V-29 -- complete backup and durable journal.** Before first promotion, all
  replaced destinations plus reviewed proposal are restorable; newly created
  destinations are recorded for rollback removal; journal
  records transaction ID/state, preview hash, original/candidate hashes, backup
  paths, and ordered operations. Proves R-022, AC-07.
- [x] **V-30 -- successful atomic promotion.** Node and Python fixture apply uses
  same-volume per-path replacement, commits all operations, writes a deterministic
  receipt, preserves unrelated bytes, and reaches host-doctor PASS. Proves R-021..
  R-023, AC-07, AC-08.
- [x] **V-31 -- verified rollback.** Failure injection before first promotion and
  after each representative create/replace/runtime-init operation returns nonzero;
  reverse operations restore every original hash/byte/permission and remove every
  newly created managed path. Proves R-023, AC-07.
- [x] **V-31A -- write-ahead interruption boundaries.** Failure/process-interrupt
  injection before/after journal flush and each `prepared`/`applied`/`verified`
  transition proves startup resolves unknown operations by preimage/candidate
  verification. Unsupported special metadata, cross-volume, or locking conditions
  fail preflight. Proves R-022..R-024, AC-07.
- [x] **V-32 -- rollback failure/recovery.** Injected rollback/rename/open-handle
  failure returns exit 3, preserves journal/stage/backup, blocks another apply,
  emits deterministic recovery instructions, and recovery later restores/verifies
  or completes safely. Proves R-024, R-028, AC-07, AC-08.
- [x] **V-33 -- backup retention and cleanup boundary.** Success/failure never
  silently deletes required recovery evidence; only explicit cleanup removes an
  eligible backup, and cleanup rejects active/recovery-required transactions.
  Proves R-024, AC-07.

## F. B4 truthful host readiness (REQUIRED)

- [x] **V-34 -- distinct truthful command/profile.** CLI help, heading, and output
  name host readiness and never framework health; framework `doctor --mode
  local|ci` remains unchanged and cannot produce a host-ready receipt. Proves
  R-025, AC-08.
- [x] **V-35 -- exact host check composition.** A checker-boundary spy proves host
  readiness invokes bundle/receipt/dependency integrity, managed drift, confirmed
  identity/config/instructions, constitution, source frontmatter, unresolved
  placeholders, runtime seed/fingerprints, ledger schema/adoption receipt,
  gitignore/tracked safety, and configured host quality-command token validity.
  Proves R-026,
  AC-08.
- [x] **V-36 -- framework-only checks are N/A.** Governance article range,
  framework stale-doc, current-PI rows, framework baseline tests, and dashboard/
  generated framework surfaces are visibly `N/A`, not PASS and not silently
  omitted. Proves R-027, AC-08.
- [x] **V-37 -- readiness exit semantics.** Isolated cases prove exit 0 only for all
  required structural PASS, exit 1 for readiness/drift/fingerprint failure (and
  quality failure when `--run-quality` is requested), exit 2 for usage/config
  error, and exit 3 for interrupted/recovery state. Proves R-028, R-028A, AC-08.
- [x] **V-38 -- success wording bounded.** Apply reports `installed; host readiness
  PASS` or equivalent only after exit 0; every failure uses truthful non-ready or
  recovery wording and never claims framework validation. Proves R-028, AC-08.
- [x] **V-38A -- quality execution is explicit/outside rollback.** Apply never runs
  quality commands. `host-doctor --run-quality` discloses cwd, tokenized argv,
  timeout, environment/network policy, and side-effect boundary; uses no shell;
  confirmed `not-configured` is N/A. Proves R-028A, AC-08.

## G. Migration, legacy behavior, and idempotence (REQUIRED)

- [x] **V-39 -- installation classification matrix.** Isolated fixtures prove
  `fresh`, `proposal-only`, `managed-current`, `managed-drift`,
  `legacy-broad-copy`, `partial-or-interrupted`, `foreign-collision`, and
  `mixed-contaminated` classifications. Proves R-029, AC-09.
- [x] **V-40 -- per-path classification matrix.** Tests prove absent,
  managed-unchanged, managed-modified, generated-stale, host-owned,
  forbidden-contamination, and conflict with stable reasons and precedence.
  Proves R-029, AC-09.
- [x] **V-41 -- preserve unknown host work.** Migration against contaminated,
  already-adopted fixtures leaves unknown/host-owned/modified files and ledger
  history byte-identical unless exact approved operations replace them; no
  contamination candidate is auto-deleted; only enumerated managed destinations
  may be replaced. Proves R-030, AC-09.
- [x] **V-42 -- safe legacy flags.** `brownfield <target>`, `--draft-only`, and
  `--apply` continue parsing; apply consumes existing proposal and enters preview;
  draft does not overwrite reviewed files; unsafe semantics/options exit with
  migration guidance. Proves R-031, AC-09.
- [x] **V-43 -- idempotent rerun.** Repeating against unchanged approved inputs
  reports no changes and creates no mutation, backup, journal, receipt churn, or
  operational ledger row; drift is reported and preserved. Proves R-032, AC-09.
- [x] **V-44 -- host-link migration.** POSIX symlink and Windows-equivalent
  link/junction conditions are detected without traversing/mutating the linked
  framework tree; explicit detach/inventory guidance is required. Proves R-033,
  AC-09, AC-10.

## H. Security and path-boundary behavior (REQUIRED)

- [x] **V-45 -- malicious path matrix.** Absolute paths, `..`, mixed separators,
  drive/UNC forms, NUL/control/reserved names, `.git` entry, source/target escape,
  symlink/junction escape, case-fold collision, and ancestor/descendant collision
  fail before access/mutation on applicable platforms. Proves R-007, R-034,
  AC-10.
- [x] **V-46 -- manifest/identity injection.** Malformed JSON, oversized/duplicate
  fields, unknown operations/renderers, shell metacharacters, newline injection,
  and hostile quality-command values are treated as data or rejected; subprocess
  uses argument arrays and no shell. Proves R-035, AC-10.
- [x] **V-47 -- no sensitive disclosure.** Preview, errors, journal, receipt, and
  readiness output contain hashes/reasons but not secret values, environment
  dumps, or full sensitive file contents. Deliberate secret canaries are absent.
  Proves R-037, AC-10.
- [x] **V-48 -- expected failures are actionable.** Each domain error returns the
  specified exit, concise stderr remediation, no traceback, no success wording,
  and zero mutation or verified rollback. Proves R-037, AC-10.

## I. Realistic fixtures and Windows/POSIX behavior (REQUIRED)

- [x] **V-49 -- realistic Node/Express fixture.** Temporary committed repository
  includes `package.json`, npm lockfile, Express source, JS/TS tests, README,
  existing `.github` content, `.gitignore`, local bare origin/default-branch
  evidence, and a partially human-edited proposal reproducing B1. Proves R-039,
  AC-11.
- [x] **V-50 -- materially different Python fixture.** Temporary committed
  library/service includes `pyproject.toml`, package/tests, different CI/convention
  evidence, a no-Copilot-instructions scenario, and managed/contaminated/rerun
  variants. Proves R-039, AC-11.
- [x] **V-51 -- isolated deterministic git evidence.** Fixtures initialize explicit
  branches, local author identity, baseline commits, and local bare remotes; tests
  require no network and never read or mutate the real checkout ledger/host.
  Proves R-041, AC-11.
- [x] **V-52 -- path/newline/text assertions.** Windows and POSIX runs use
  semantically identical POSIX-relative manifests; preserved LF/CRLF files remain
  byte-identical; new managed text is intentional UTF-8/LF; absolute temp roots do
  not appear. Proves R-036, R-040, AC-11.
- [x] **V-53 -- permission/link/rename assertions.** Permission variance does not
  alter semantics; core requires no executable-bit or symlink/junction support;
  case-only renames are avoided/rejected; success and injected rename/open-handle
  failures produce identical exit-state contracts across platforms. Proves R-036,
  R-040, AC-07, AC-11.
- [ ] **V-54 -- Windows and POSIX CI/equivalent runners.** The same focused fixture
  suite runs green on a Windows runner and a POSIX runner with recorded run IDs/
  output. Platform skips require explicit non-applicability and may not remove
  equivalent behavioral proof. Proves R-040, AC-11.
- [x] **V-54A -- minimum scenario matrix complete.** Every row in SPEC Section 9.1
  has evidence for the named stack/platform cells; all installation/path classes
  have platform-neutral unit coverage and OS-specific substitutions are named.
  Proves R-039, R-040, AC-11.

## J. Implementation boundaries and quality gates (REQUIRED)

- [x] **V-55 -- minimal responsibility boundaries.** Independent Stage-1 review
  at commit `9e743e4bd6d7baa16debcc25ee5cad487dcf9782` proves one canonical
  path with thin CLI dispatch and distinct inventory, proposal/baseline, manifest,
  identity, migration, transaction/recovery, and host-readiness responsibilities;
  legacy adapters contain no duplicate unsafe implementation. Proves ADR-026,
  R-038, AC-12.
- [x] **V-56 -- stdlib/no dependency.** Import/dependency diff shows no new runtime
  or test package, lockfile, vendored library, or network dependency. New CLI code
  follows `main(argv) -> int`, `pathlib`, custom expected errors, and stderr
  conventions. Proves R-038, AC-12.
- [x] **V-57 -- focused RED before GREEN.** Evidence records a focused test command
  failing for the intended missing SDD-058 behavior before production changes,
  then the same focused command passing after implementation. Proves R-042,
  AC-12.
- [x] **V-58 -- full regression baseline.** Full `spec-driven-development/` suite
  is at least **668 passed / 2 skipped**, with no removed or weakened
  baseline test. Proves R-042, AC-12.
- [x] **V-59 -- repository checks.** Schema lint, origin lint, stale-doc lint,
  governance check, `git diff --check`, and Article X FootprintLockGuard **3/3**
  are green. Proves R-042, AC-12.
- [x] **V-60 -- operational gates.** Strict local doctor is green; B-1 genuine PI-9
  dispatch/review/close outcomes exist in the local ledger without fabrication;
  B-2 TDD and DONE-completeness checks are green. Proves R-042, AC-12.
- [x] **V-61 -- two-stage QA ordering.** A Stage-1 reviewer independently proves
  every requirement/AC with no missing/extra/wrong behavior before a different
  Stage-2 reviewer evaluates quality/security/maintainability; timestamps and
  outcomes prove the order. Proves R-043, AC-13.
- [ ] **V-62 -- exact-package owner approval and public CI.** Owner approval names
  the exact pre-push diff/package; no push precedes it; public B-4 CI for that
  package is green with run ID/URL; only then are SDD-058 and Sprint 24 eligible
  for DONE/close. Proves R-043, AC-14.

## K. Scope integrity review (REQUIRED)

- [x] **V-63 -- sequencing and scope history.** Repository history through
  `9e743e4bd6d7baa16debcc25ee5cad487dcf9782` proves no
  PLAN/TASKS commit predates joint ADR/SPEC approval and no implementation commit
  predates TASKS validation lock. Implementation excludes real-host mutation,
  unproved greenfield redesign, dashboard/cloud/SDD-034/retro work, agent hiring,
  dependency, ledger schema change, and unrelated cleanup. Authorized lifecycle
  close updates occur only after implementation validation/approvals. Proves
  non-goals and R-043.
- [x] **V-64 -- no history or evidence fabrication.** Existing historical artifacts
  remain intact; ledger rows, approval timestamps, CI results, fixture outcomes,
  and validation checkmarks are backed by real evidence. Proves R-041..R-043.
- [x] **V-65 -- separate real-host approval.** No non-fixture host mutation occurs
  unless a distinct owner approval receipt matches target repository, exact
  preview hash, backup location, and recovery command. Fixture exemptions are
  accepted only under a positively identified disposable test temp root. Joint
  ADR/SPEC and pre-push approvals do not satisfy this gate. Proves R-044, AC-15.

---

## Evidence record (populate after implementation; do not pre-check)

### Pre-implementation baseline and protected preimage

- Exact baseline command: `C:\Training\Projects\Evolving-Multi-Agent-Framework\.venv\Scripts\python.exe -m pytest -q`
- Baseline output: `668 passed, 2 skipped, 6 subtests passed in 130.36s`; matches the Sprint 24 authority exactly.
- Checkout state before the first RED edit: `master...origin/master`; pre-existing owner/Sprint-EM change at `spec-driven-development/exec/sprint-progress.md`; accepted ADR-026 and the locked SDD-058 feature directory are untracked in the continuing feature-isolated unit. No implementation/test/workflow file existed or was edited.
- Protected hashes before fixture work:
  - local ledger: `9e836c887387a2900c91adcf473d52ad4ae84e56cbd4afef5244a863f8d835da` (57,344 bytes)
  - `exec/state.md`: `b2ddbde3ed99bc56bb68f1eadb9c8fffb1c8401eaa9131b385521e6f2452516b`
  - `exec/state.html`: `c82721c857f27a64d279f5e6e42df9471f8af6ada854b9c61ed7685719428f36`
  - `exec/work-index.md`: `4f793690b8d0f57697c7f44432a5648e697ed991812e9f76a4d22de6c0bef2d8`
  - `clarify.md`: `b320bc54181c3ec32340a3bc8643ce3befa32330dcb356b54d67acc5b6e84bce`
  - `plan.md`: `6f1a3b5d87eb7712d0821bc2e55f70fe05b0d90e1b1ed916935fdf39905441b8`
  - `spec.md`: `5d947bade122cff79d5c219a7017d2addb44998e17f68bc85001b5d63a5ef748`
- V-01 through V-04 were already checked from durable owner/Architect/TASKS chronology. The contract remains `LOCKED / ACTIVE AT TASKS`; no wording was weakened.

### Focused RED

- Commands: focused module and canonical integration tests were added before their
  corresponding production behavior, using the mandated project Python executable.
- Expected failure: missing inventory, proposal, manifest, identity, migration,
  readiness, transaction, and canonical orchestration behavior.
- Output: the final transaction-integration RED packet produced 5 intended focused
  failures covering transactional draft persistence, complete staged-root
  readiness, receipt rollback safety, approved refresh/adoption persistence, and
  approved migration execution. Earlier packets likewise failed before each
  production module existed.

### Focused GREEN

- Command: `C:\Training\Projects\Evolving-Multi-Agent-Framework\.venv\Scripts\python.exe -m pytest spec-driven-development/cli/test_brownfield_cli.py spec-driven-development/cli/test_brownfield_cross_platform.py spec-driven-development/cli/test_brownfield_identity.py spec-driven-development/cli/test_brownfield_inventory.py spec-driven-development/cli/test_brownfield_manifest.py spec-driven-development/cli/test_brownfield_migration.py spec-driven-development/cli/test_brownfield_proposal.py spec-driven-development/cli/test_brownfield_transaction.py spec-driven-development/cli/test_host_readiness.py -q`
- Output: `383 passed in 557.15s`.

### Cross-platform fixture runs

- Windows run: local Windows 383-test focused suite PASS; scenario-matrix and
  platform-neutral/POSIX-substitution tests are included.
- POSIX run: not yet executed on a real POSIX runner; V-54 remains open. The
  workflow now defines both `ubuntu-latest` and `windows-latest`, but no public run
  is claimed.

### Full gates

- Full suite: `1051 passed, 2 skipped, 6 subtests passed in 603.71s`; baseline was
  `668 passed, 2 skipped, 6 subtests passed`, for a net increase of 383 passing
  tests and no baseline loss.
- Schema/origin/staledoc/governance: all clean; `git diff --check` clean.
- Article X 3/3: PASS in 0.38s.
- Local doctor / B-1 / B-2: strict local doctor PASS with the same 1051/2/6 test
  result, 16 genuine PI-9 dispatch rows, TDD gate PASS, and DONE completeness PASS
  for already-DONE features.
- Scope/protected state: no tracked database; generated exec surfaces and locked
  `clarify.md`, `plan.md`, and `spec.md` retained their preimage hashes. The local
  ledger changed only through genuine dispatch 53 and remains untracked. The
  pre-existing Sprint-EM edit to `exec/sprint-progress.md` was not touched.
- Fixture safety: all mutating tests required an in-memory capability bound to a
  positively identified sentinel temp root; local bare remotes avoided network;
  no serializable/public fixture bypass exists; no real-host authorization was
  issued or used.
- Stage-1 review: T-058-021 PASS / complete at 2026-07-20 08:24:24 -07:00
  for exact commit `9e743e4bd6d7baa16debcc25ee5cad487dcf9782`; all three
  returned WRONG findings are closed; V-55 and V-63 are evidenced. This PASS
  preceded every Stage-2 review recorded in `review-stage-2.md`.
- Stage-2 review: T-058-022 APPROVED / complete on 2026-07-27 by a different
  independent Principal Cloud Security Architect reviewer after all critical and
  important findings were closed. The superseding verdict satisfies V-61.
- Owner exact-package approval: not requested; V-62 remains open.
- Public CI run: not run; V-54 and V-62 remain open.
- Commit-history sequencing: no commit was permitted in this implementation unit;
  V-63 remains open until package/commit history exists.

### Stage-2 repair evidence (2026-07-27)

- Repair branch: `feature/f7.5-sdd-058-stage-2-security`, created from
  `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`. The binary diff hash before and
  after branch creation was
  `63bc0b1bb94529be2d73861837c19b90fc0a3f24`; porcelain status was identical,
  so every pre-existing dirty change was preserved.
- CRITICAL-02 RED: the focused multi-file proposal corruption test failed with
  `Failed: DID NOT RAISE TransactionError`. GREEN after per-file durability and
  content/mode verification: `1 passed, 86 deselected in 11.43s`.
- CRITICAL-03 RED: the recovery inspection boundary test failed with
  `Failed: DID NOT RAISE TransactionError`. GREEN after routing the destination
  read through the canonical mutation-boundary resolver: `2 passed, 86
  deselected in 8.07s`, including the neighboring link-substitution regression.
- Host-readiness execution-policy repair: explicit `allow-confirmed` tests use
  the contained `Popen` boundary, while `deny` still fails closed before launch;
  focused result `4 passed, 14 deselected in 9.64s`.
- Complete transaction/readiness security slice:
  `106 passed in 196.35s`.
- Focused cross-platform matrix: `26 passed in 68.25s`.
- Complete SDD-058 focused workflow suite:
  `424 passed, 1 skipped in 474.94s`.
- Workflow contracts: `11 passed, 2 subtests passed in 0.65s`.
- Full repository regression: `1092 passed, 3 skipped, 6 subtests passed in
  626.11s`; the pre-repair full-suite result was `1051 passed, 2 skipped, 6
  subtests passed`, so no passing-test baseline was lost.
- Schema lint, origin lint with tracked-database detection, stale-doc lint, and
  governance check all returned exit code 0. Article X FootprintLockGuard was
  `3 passed, 286 deselected in 0.27s`; `git diff --check` returned exit code 0.
- TDD gate and PI-9 DONE completeness both returned PASS. Strict local doctor
  was launched without `--skip-tests` and returned `All checks passed.` Its test
  result was `1092 passed, 3 skipped, 6 subtests passed in 625.77s`; the PI-9
  dispatch-row count was `21`.
- CRITICAL-01 public-boundary evidence: real canonical `recover` and `cleanup`
  calls with valid fixture authorization and a journal-selected foreign target
  both returned exit code 3 / `recovery-required`, retained the journal, and
  preserved host and foreign bytes. Focused result: `2 passed, 47 deselected in
  143.30s`.
- CRITICAL-03 additional RED evidence: deterministic stage-root, backup-root,
  promotion, rollback-replace, and rollback-unlink substitution tests failed
  before their immediate-boundary repairs. GREEN transaction regression:
  `93 passed in 229.63s`.
- IMPORTANT-07 RED: a failed Windows `taskkill /T /F` was silently accepted
  (`Failed: DID NOT RAISE RuntimeError`). GREEN after fail-closed handling, with
  a real parent-spawns-child timeout proving the descendant PID inactive before
  return: `3 passed, 17 deselected in 2.45s`.
- No commit or push occurred at this repair checkpoint. Stage 2 was still blocked
  then; the later superseding independent re-review in `review-stage-2.md`
  APPROVED the repaired package and closes T-058-022 and V-61.

### Stage-2 closure evidence (2026-07-27)

- Superseding independent reviewer: Principal Cloud Security Architect, distinct
  from the Stage-1 QA reviewer and not an implementer of the reviewed repairs.
- Reviewed branch and base/current HEAD:
  `feature/f7.5-sdd-058-stage-2-security` at
  `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`; the branch was created from that
  commit and no commit or push has occurred since.
- Superseding verdict: **APPROVED**. CRITICAL-03, IMPORTANT-07, and IMPORTANT-08
  are closed, no new critical or important regression was found, and the prior
  CHANGES REQUIRED findings remain preserved as review history.
- Live local validation on the exact dirty package: full repository
  `1109 passed, 4 skipped, 6 subtests passed`; transaction regression
  `98 passed`; strict local doctor `All checks passed.` with the same
  `1109 passed, 4 skipped, 6 subtests passed`; `git diff --check` clean.
- A later exact complete SDD-058 focused-workflow rerun did not reproduce the
  earlier `441 passed, 2 skipped` result: it returned `1 failed, 440 passed,
  2 skipped`. The failing forged-equal fixture-authorization test passed both
  alone (`1 passed`) and in the complete transaction module (`98 passed`),
  proving an order-dependent shared-state defect. The module-level fixture
  authorization registry retains raw object IDs, so allocator ID reuse can
  make an unregistered replacement authorization appear registered. The exact
  focused gate is therefore not currently green and pre-push approval must not
  proceed until the defect is repaired and the complete focused command passes.
- T-058-022 is complete and V-61 is satisfied. V-62 remains open: owner approval
  has not yet been recorded, no push or public CI is claimed, and SDD-058, Sprint
  24, and PI-9 remain open.

### Final authorization-registry closure evidence (2026-07-28)

- Preflight found and terminated only the stale workspace pytest parent/child
  pair before validation. A separate Second Brain pytest pair was observed and
  left untouched. No validation suites overlapped afterward.
- The fixture registry repair replaced persistent raw object IDs with weak live
  capabilities behind opaque UUID keys and exact object-identity checks. The
  exact nine-module workflow initially exposed the stale-ID order dependence.
- Independent targeted security review then found the equivalent owner-receipt
  `id -> values` ABA path. The owner lifetime regression was RED with `Failed:
  DID NOT RAISE AuthorizationError` (`1 failed in 45.82s`) before production
  repair and GREEN (`1 passed in 1.79s`) after owner receipts moved to their own
  weak exact-identity registry.
- Complete transaction regression: `100 passed in 272.13s (0:04:32)`.
- Exact nine-module SDD-058 workflow: `443 passed, 2 skipped in 771.20s
  (0:12:51)`.
- Full repository regression after both registry repairs: `1111 passed, 4
  skipped, 6 subtests passed in 1085.72s (0:18:05)`.
- Strict local doctor after both registry repairs: `All checks passed.` Internal
  tests were `1111 passed, 4 skipped, 6 subtests passed in 1113.30s (0:18:33)`;
  schema, governance, origin, stale-document, tracked-database, ledger, TDD, and
  DONE-completeness checks passed; PI-9 had `21` genuine dispatch rows.
- Article X FootprintLockGuard: `3 passed, 286 deselected in 0.21s`.
- Independent Principal Cloud Security Architect final verdict: **APPROVED**;
  no CRITICAL or IMPORTANT issue remains. T-058-022 and V-61 remain satisfied.
- Owner exact-package approval, push, public Windows/POSIX CI, V-62, SDD-058
  DONE, Sprint 24 close, PI-9 close, and executive regeneration remain open and
  unclaimed. Final evidence-byte gates and binary-diff fingerprint follow this
  append and must identify the exact package presented for approval.

### Failed public matrix and portability repair evidence (2026-07-29)

- Public run `30469954928` tested master SHA
  `8c942c881f4f31cbc5133f8098658f8633ce1362`. Ubuntu job `90637291129`
  failed `Run focused SDD-058 suite` with
  `test_brownfield_inventory.py::test_inventory_target_rejects_link_without_reading_external_or_unrelated_bytes`:
  `assert [] == [PosixPath(.../README.md)]`; summary
  `1 failed, 441 passed, 4 skipped in 44.06s`.
- Windows job `90637291287` later failed the same test and assertion with
  `assert [] == [WindowsPath(.../README.md)]`; summary
  `1 failed, 444 passed, 1 skipped in 339.95s`. Both jobs skipped `Run doctor`
  after the focused-suite failure. The failed matrix invalidates the prior exact
  package approval for any further push; V-54 and V-62 remain unchecked.
- Root cause: `validate_path_set()` deterministically sorts `linked-outside`
  before `README.md`. On runners capable of creating the directory link,
  `safe_relative_path()` rejects that first managed path before `_observe()` can
  read any file. The test incorrectly expected `README.md` to be read first;
  local Windows had hidden the defect by skipping when link creation was
  unavailable.
- Repair: the test-only assertion now requires `read_paths == []`. This matches
  both public traces and strengthens the locked security contract: link
  rejection occurs before managed, external, or unrelated bytes are read. No
  production code, requirement mapping, trust boundary, dependency, or real host
  changed, so the existing independent Stage-2 APPROVED verdict remains valid
  and no Stage-2 re-review is required.
- Structural POSIX-equivalent reproduction, used because Docker was absent and
  WSL was not installed, returned normalized order
  `['linked-outside', 'README.md']`; direct code inspection proves the link error
  precedes `_observe()` and `Path.read_bytes()`. The affected test skips on this
  non-link-capable checkout, while the exact nine-module workflow is green at
  `443 passed, 3 skipped in 1099.87s`.
- Full `spec-driven-development/` regression:
  `1111 passed, 5 skipped, 6 subtests passed in 852.37s`. Schema lint with orphan
  checking, origin lint with tracked-database detection, stale-doc lint,
  governance check, and `git diff --check` are green. Article X
  FootprintLockGuard is `3 passed, 286 deselected in 0.31s`.
- Strict local doctor and the final explicit-path checkpoint commit follow this
  evidence update. A new owner approval must name that exact checkpoint SHA
  before any push; no push is authorized by the prior approval.
- Strict local doctor subsequently passed all 9 checks. The explicit-path repair
  checkpoint is commit `32d33ae`; it contains only the test portability change
  and this SDD-058 evidence. V-54 and V-62 remain unchecked until a newly
  approved push of this exact repaired package produces green public jobs.

## Definition of Done

All V-01 through V-65, including letter-suffixed items, MUST be checked with real
evidence. No REQUIRED item may be
silently deferred, converted to optional, or checked by assertion alone. ADR-026
and SPEC approval must precede PLAN/TASKS; validation must lock at TASKS before
implementation; two-stage QA must run in order; owner exact-package approval must
precede push; public CI/B-4 must be green before SDD-058 or Sprint 24 is DONE.
