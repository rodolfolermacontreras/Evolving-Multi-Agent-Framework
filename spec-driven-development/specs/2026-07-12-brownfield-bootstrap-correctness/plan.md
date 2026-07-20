---
id: SDD-20260712BROWNFIELD-plan
type: plan
status: active
owner: principal-architect
updated: 2026-07-12
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# PLAN: SDD-058 -- Brownfield bootstrap correctness

- Feature ID: SDD-058
- Sprint: PI-9 / Sprint 3 (overall Sprint 24)
- Spec: [spec.md](spec.md)
- Validation: [validation.md](validation.md) -- DRAFT / UNLOCKED until TASKS
- Architecture: [ADR-026](../../docs/ADR/026-transactional-brownfield-adoption.md) -- accepted
- Approval basis: owner-approved ADR-026 and SPEC package, 2026-07-12,
  local ledger decision 5
- Dispatch basis: local ledger dispatch 52
- Execution owner: Principal Software Developer after TASKS locks validation
- Plan status: ACTIVE; implementation, commit, push, and non-fixture mutation
  remain unauthorized

---

## 1. Requirements and fixed constraints

- **REQ-001:** Implement every normative requirement R-001 through R-044,
  including R-016A and R-028A, and prove AC-01 through AC-15.
- **REQ-002:** Preserve the exact immutable `brownfield-core@1` membership in
  ADR-026 Appendix A. Implementation may encode and validate that membership but
  may not add, remove, glob, substitute, or silently make an entry optional.
- **REQ-003:** Keep the eight ADR-named responsibilities in eight distinct
  stdlib modules: `brownfield_inventory.py`, `brownfield_proposal.py`,
  `brownfield_manifest.py`, `brownfield_identity.py`,
  `brownfield_migration.py`, `brownfield_transaction.py`,
  `host_readiness.py`, and `brownfield_compat.py`.
- **REQ-004:** Keep `bootstrap.py` as a thin parser/dispatcher and legacy
  compatibility surface. It may import `brownfield_compat` but may not retain an
  alternate broad-copy, auto-refresh, direct-write, or framework-doctor path.
- **REQ-005:** Use Python 3.12+ standard library only. Add no runtime or test
  dependency, package, lockfile, vendored code, network call, or shell command.
- **REQ-006:** Normal apply reads the existing reviewed proposal and baseline
  exactly as found. It does not invoke inventory-based proposal generation or
  refresh and does not rewrite proposal bytes.
- **REQ-007:** Dry-run is the default. Mutation requires an exact preview hash,
  conflict-free validated inputs, complete same-volume stage and backup, durable
  journal, and either a verified commit or verified rollback.
- **REQ-008:** A real-host apply additionally requires a target-specific owner
  approval receipt. Automated fixture mutation is allowed only through a direct
  test API after positive disposable-root verification; no public CLI flag may
  self-declare an arbitrary repository to be a fixture.
- **REQ-009:** Migration is inventory-first and non-destructive. SDD-058 reports
  contamination but never deletes it. Unknown, host-owned, and modified files
  remain preserved unless an enumerated managed destination is explicitly
  approved, backed up, and replaced.
- **REQ-010:** Generated managed text is deterministic UTF-8/LF; preserved host
  and proposal files remain byte-identical, including line endings and supported
  portable mode/read-only metadata.
- **REQ-011:** Windows and POSIX execute the same behavioral contract against a
  realistic Node/Express host and a materially different Python host. Tests use
  temporary committed repositories and local bare remotes only.
- **REQ-012:** Validation remains draft/unlocked during PLAN. TASKS must lock it
  before any production or test implementation edit.
- **SEC-001:** Normalize and containment-check every source, destination,
  proposal, stage, backup, and journal path before access. Reject absolute,
  traversal, `.git`, control/reserved, case-fold-colliding, ancestor/descendant,
  symlink, junction, and cross-volume unsafe paths before mutation.
- **SEC-002:** Treat manifests, identity values, and command tokens as data.
  Quality commands run only as token arrays with `shell=False`; preview,
  journals, receipts, errors, and generated files exclude raw credentials,
  environment dumps, and sensitive content.
- **CON-001:** Do not change the constitution, ledger schema, framework doctor
  local/CI behavior, greenfield behavior, generated executive surfaces, Sprint
  24/current-PI state, backlog, or unrelated feature artifacts.
- **CON-002:** Do not mutate a non-fixture host while implementing or validating
  SDD-058. Separate owner approval is still required after this feature ships.
- **PAT-001:** Follow `docs/CLI-PATTERN.md`: `pathlib`, explicit `parse_args`,
  testable `main(argv) -> int`, expected domain errors, stderr remediation, UTC
  timestamps, and argument-array subprocess execution.
- **PAT-002:** Use immutable dataclasses and plain JSON-compatible dictionaries at
  module boundaries. Serialize canonical JSON with sorted semantic collections,
  fixed schema key order where ADR-026 requires it, UTF-8/LF, and compact
  separators when bytes participate in a hash.
- **PAT-003:** Use one canonical orchestration path. Compatibility code translates
  legacy syntax into canonical requests; it contains no business logic that
  duplicates another module.

## 2. Selected architecture

### 2.1 Dependency direction

The dependency graph is acyclic. Lower-level modules never import the adapter or
`bootstrap.py`.

```text
brownfield_inventory     brownfield_manifest     brownfield_identity
          |                       |                       |
          v                       |                       |
brownfield_proposal               +------v----------------+
          |                         brownfield_migration
          |                                  |
          +----------------------------------+
                                             |
host_readiness <---- validated candidate ----+
       ^                                     |
       | callback/protocol                    v
       +----------------------- brownfield_transaction
                                             |
                                             v
                                    brownfield_compat
                                             |
                                             v
                                         bootstrap
```

Rules:

- `brownfield_inventory` has no SDD-058 internal dependency and owns read-only
  repository evidence and filesystem classification primitives.
- `brownfield_proposal` consumes an inventory snapshot as data; it may import
  inventory dataclasses but never starts inventory during apply.
- `brownfield_manifest` owns immutable bundle membership, dependency closure,
  renderer declarations, source hashes, operation ordering, path validation, and
  preview category schema.
- `brownfield_identity` consumes evidence data and owns identity validation,
  remote sanitization, confirmation, and deterministic renderers.
- `brownfield_migration` consumes inventory, receipt, bundle, and identity state
  and emits classifications/planned operations; it never writes or deletes.
- `host_readiness` consumes a root view plus manifest/identity/receipt data. It
  never imports transaction code and never calls framework doctor.
- `brownfield_transaction` consumes an already validated preview and callback for
  staged structural readiness. It owns stage, backup, journal, promotion,
  rollback, recovery, and cleanup mechanics but does not decide bundle content.
- `brownfield_compat` is the sole application service/orchestrator. It wires the
  modules, binds exit semantics, enforces real-host versus fixture authorization,
  and returns presentation-neutral results to `bootstrap.py`.
- `bootstrap.py` owns only argparse definitions, legacy argument adaptation,
  bounded stdout/stderr formatting, and `main(argv) -> int` dispatch.

### 2.2 Module responsibilities and interfaces

#### `brownfield_inventory.py`

Own these immutable dataclasses and pure/read-only functions:

- `RepositoryEvidence(schema_version, target_head, project_name, remotes,
  default_branch, stack, quality_candidates, conventions, source_documents,
  evidence_digest)`; every path is sorted POSIX-relative and raw remote secrets
  are discarded before construction.
- `PathObservation(path, kind, ownership_hint, sha256, byte_length, portable_mode,
  link_kind, receipt_hash)` where `kind` contains only filesystem facts and no
  mutation decision.
- `InventorySnapshot(schema_version, target_head, evidence, observations,
  recovery_markers, fingerprint_hits)` with deterministic ordering.
- `validate_repository_root(target: Path) -> Path` requires the exact committed
  git root and rejects `.git` entry, links, and missing `HEAD`.
- `collect_repository_evidence(target: Path) -> RepositoryEvidence` uses
  tokenized read-only git commands and local files; it does not write an
  archaeology report.
- `inventory_target(target, managed_paths, forbidden_fingerprints) ->
  InventorySnapshot` performs one non-following scan and hashes only relevant
  managed/collision/fingerprint candidates.
- `safe_relative_path(raw, root, purpose, *, allow_missing) -> Path` and
  `validate_path_set(paths) -> tuple[str, ...]` provide the shared fail-closed
  containment, `.git`, special-file, reserved-name, case-fold, and
  ancestor/descendant checks used by all modules.

`RepositoryEvidence` supersedes the current side-effecting
`create_archaeology_report()` path for canonical brownfield operations. A
human-readable archaeology view is rendered by the proposal module from this
in-memory schema.

#### `brownfield_proposal.py`

Own proposal layout, generation, baseline validation, refresh classification,
legacy baseline adoption, and recoverable proposal updates:

- Proposal root remains `.sdd-proposal/` for compatibility.
- Reviewed files remain `.sdd-proposal/constitution/<name>`.
- Identity input is `.sdd-proposal/host-identity.json`.
- Baseline metadata is `.sdd-proposal/baseline-manifest.json`.
- Lossless generated bytes are stored under
  `.sdd-proposal/.baseline/constitution/<name>`; candidate refresh bytes are
  staged outside the proposal until an approved proposal transaction commits.
- `BaselineFile(path, sha256, byte_length, baseline_path, renderer_id,
  renderer_version, evidence_dependencies, text_policy)` and
  `BaselineManifest(schema_version="1", source_revision, evidence_digest,
  bundle_version="brownfield-core@1", generated_at, files)` are canonical.
- `generate_proposal(evidence, identity_draft, framework_root, date) ->
  ProposalCandidate` is used only by draft or explicit legacy-baseline adoption.
- `load_and_validate_baseline(proposal_root) -> BaselineManifest` validates
  version, sorted unique paths, containment, hashes, byte lengths, source
  revision, renderer data, and lossless snapshots.
- `classify_refresh(baseline: bytes, reviewed: bytes, candidate: bytes) ->
  RefreshOutcome` returns exactly `unchanged`, `upstream-only`, `user-only`,
  `convergent`, or `conflict` according to ADR-026.
- `plan_refresh(...) -> ProposalRefreshPlan` performs three-way classification
  without mutation and requires explicit resolution for each conflict.
- `plan_baseline_adoption(...) -> ProposalRefreshPlan` leaves a legacy reviewed
  proposal untouched and emits side-by-side candidate/baseline operations for
  exact transaction approval.

Normal apply is intentionally absent from this module. The adapter loads reviewed
proposal and baseline bytes through validation-only functions and passes those
bytes onward without invoking generation or refresh.

#### `brownfield_manifest.py`

Own the executable form of ADR-026 Appendix A without changing membership:

- `BundleEntry(destination, operation, source, source_sha256, renderer_id,
  renderer_version, dependencies, text_policy, ownership, enabled_condition)`.
- `BundleManifest(schema_version="1", bundle_id="brownfield-core@1",
  framework_revision, entries, forbidden_fingerprint_version)`.
- Operations are exactly `copy`, `render`, `seed`, `preserve`, and `forbid`.
- The disabled fleet-worker instruction is present as the Appendix A conditional
  entry and activates only when confirmed `worktree_profile == true`; this is an
  enabled condition, not a membership change.
- `build_core_manifest(framework_root, identity) -> BundleManifest` explicitly
  enumerates every Appendix A file. It does not use recursive tree selection or a
  future-facing glob. Directory notation in the ADR resolves only to the named
  current `SKILL.md`.
- `validate_manifest(manifest, framework_root, target_root,
  renderer_registry) -> ValidatedBundle` verifies exact membership against a
  frozen expected-destination set, source hashes, operation/version enums,
  renderer IDs, source/target containment, unique destinations, no
  ancestor/descendant conflicts, acyclic dependency closure, and stable
  topological order before preview.
- `build_preview(validated_bundle, inventory, rendered_bytes, seed_bytes,
  migration) -> Preview` emits exactly six category arrays in this order:
  `create`, `replace`, `preserve`, `conflict`, `forbidden`, and
  `runtime-initialize`. Each `PreviewItem` has one POSIX destination, reason,
  ownership, operation, before hash, after hash, and dependency IDs.
- `canonical_preview_bytes(preview) -> bytes` excludes absolute roots and volatile
  timestamps; `preview_hash(preview) -> str` is SHA-256 over those bytes.

Source selection copies only a validated entry's single source file. Forbidden
entries are assertions/reporting rules and never become a broad-copy cleanup list.

#### `brownfield_identity.py`

Own ADR-026 Appendix B exactly:

- `IdentityField(value, classification, evidence_paths, ambiguity, confidence,
  confirmed_by, confirmed_at)` and `HostIdentityManifest(schema_version="1",
  generated_at, target_head, fields, renderers)`.
- `draft_identity(evidence, adoption_date) -> HostIdentityManifest` supplies only
  approved evidence and date defaults; it never infers owner, team, or mission.
- `load_identity(path)`, `validate_identity(manifest)`, and
  `confirm_identity(manifest, confirmations)` reject unknown/missing fields,
  wrong types, invalid nullability, unconfirmed required values, unstable paths,
  unsupported renderer versions, and malformed quality policies.
- `sanitize_remote(raw) -> SanitizedRemote` removes HTTPS userinfo, credentials,
  query, fragment, and secret-bearing expansions before any operational object is
  created. Ambiguity or non-`git` SSH usernames require confirmation. Errors
  identify the field and remediation but never echo raw input.
- Renderer registry keys are exactly `project_config`, `copilot_instructions`,
  `constitution`, `rosters`, and `seeds`, each with a non-empty explicit version.
- `render_project_config(identity) -> bytes` emits exactly the Appendix B keys in
  the mandated order.
- `render_copilot_instructions(identity)`, `render_constitution(identity,
  reviewed_proposal)`, `render_rosters(identity, bundle)`, and
  `render_seeds(identity)` return deterministic UTF-8/LF bytes and reject
  framework identity, unresolved required markers, and absolute temporary paths.
- Generic source agents/prompts/skills containing framework paths, branch names,
  commands, or stack assumptions are rendered through a bounded token
  substitution registry. Unknown required tokens fail; no free-form replacement
  scans are allowed.

#### `brownfield_migration.py`

Own classification and migration planning, never mutation:

- `InstallationClass` is exactly `fresh`, `proposal-only`, `managed-current`,
  `managed-drift`, `legacy-broad-copy`, `partial-or-interrupted`,
  `foreign-collision`, or `mixed-contaminated`.
- `PathClass` is exactly `absent`, `managed-unchanged`, `managed-modified`,
  `generated-stale`, `host-owned`, `forbidden-contamination`, or `conflict`.
- `classify_path(observation, bundle_entry, prior_receipt) -> PathClassification`
  uses receipt/baseline hashes before appearance-based evidence and applies a
  documented deterministic precedence table.
- `classify_installation(inventory, path_classes, proposal_state) ->
  InstallationClassification` returns one class plus stable reasons.
- `plan_migration(classification, validated_bundle, identity, prior_receipt) ->
  MigrationPlan` is read-only, preserves all unlisted/unknown content, identifies
  contamination without delete operations, and allows replacement only for an
  enumerated managed destination.
- Existing SDD state blocks normal fresh apply and requires explicit migration.
  A linked/junction adoption returns `foreign-collision` or
  `partial-or-interrupted` with detach/inventory guidance and no traversal.
- Unchanged `managed-current` inputs produce an empty semantic operation set;
  the adapter returns no-op without creating a backup, journal, receipt rewrite,
  or ledger row.

#### `host_readiness.py`

Own bounded host readiness, separate from `run_doctor()`:

- `CheckResult(id, label, status, detail)` where status is only `PASS`, `FAIL`,
  or `N/A`; `ReadinessReport(schema_version, mode, checks, exit_code)`.
- `run_structural_checks(root_view, bundle, identity, receipt, *, staged) ->
  ReadinessReport` checks bundle/receipt/dependencies, managed integrity, identity,
  config/instructions, six constitution files, installed frontmatter, unresolved
  markers, runtime seeds/fingerprints, ledger schema and adoption zero-row
  receipt, gitignore/tracked safety, and configured quality token validity.
- The report always contains explicit `N/A` rows for framework governance,
  stale-doc, current PI, framework test baseline, and generated framework
  surfaces. It never imports or invokes framework doctor.
- `run_quality_checks(root, identity, disclosure_sink) -> ReadinessReport` runs
  only explicitly configured commands, after disclosing cwd, argv, timeout,
  environment policy, network policy, and outside-rollback side effects. It uses
  `subprocess.run(argv, cwd=..., shell=False, timeout=..., env=...)`.
- `not-configured` commands are `N/A`. Apply invokes structural staged/final
  checks only and never quality execution.
- `main(argv) -> int` provides the distinct `host-doctor` CLI when this copied
  module runs in a host. Exit mapping is exactly 0/1/2/3 from the SPEC.

#### `brownfield_transaction.py`

Own mutation mechanics and no policy shortcuts:

- `ApplyAuthorization(kind, target_fingerprint, target_head, preview_hash,
  backup_location, recovery_command, approved_by, approved_at, fixture_root)`.
  `kind` is `owner-receipt` or internal `verified-fixture`.
- `TransactionOperation(sequence, destination, operation, preimage,
  candidate, backup, state)`; state transitions are exactly `prepared`,
  `applied`, and `verified`.
- `TransactionJournal(schema_version="1", transaction_id, target_fingerprint,
  target_head, preview_hash, state, stage_root, backup_root, operations)` with
  states `staging`, `staged`, `backed-up`, `promoting`, `committed`,
  `rolling-back`, `rolled-back`, and `recovery-required`.
- Transaction workspace is a caller-approved, same-volume sibling of the target,
  never an installed host asset and never inside `.git`. Stage, backup, and
  journal locations are containment-checked against this dedicated workspace.
- `preflight(preview, authorization, target, workspace) -> TransactionContext`
  re-hashes all inputs, validates owner receipt or internal fixture proof, checks
  same volume/capacity/special files/links/locks, and rejects active journals.
- `stage_candidate(context, materializer, structural_check) -> StagedCandidate`
  builds only enumerated destinations, validates complete hashes and structural
  readiness, and does not mutate host/proposal.
- `backup(context)` saves every replacement/deletion preimage, reviewed proposal,
  existence state, line endings as bytes, and supported portable metadata before
  first promotion. Creates are recorded for rollback removal.
- `promote(context)` flushes journal and containing directory metadata where the
  platform supports it before each mutation, uses same-volume temporary files and
  `Path.replace()`/`os.replace()` for regular-file atomic replacement, and records
  each state transition durably.
- `rollback(context)` reverses operations and verifies original existence, hashes,
  bytes, and supported metadata. Verified rollback exits domain failure 1;
  uncertainty retains all evidence and exits recovery-required 3.
- `recover(journal_path, action)` resolves an unknown operation by comparing both
  preimage and candidate hashes, then safely completes or rolls back. `cleanup`
  is separate and rejects active/recovery-required journals.
- Abrupt power-loss atomicity is not claimed. Tests inject process interruption at
  every journal boundary; implementation guarantees restart recovery from the
  last flushed state.

#### `brownfield_compat.py`

Own canonical commands and backward compatibility:

- `BrownfieldRequest(action, target, proposal_root, identity_path,
  migration, run_quality, preview_approval, owner_approval_path,
  transaction_workspace)` where action is `draft`, `preview`, `apply`,
  `refresh`, `adopt-baseline`, `migrate`, `recover`, `cleanup`, or
  `host-doctor`.
- `BrownfieldResult(exit_code, status, message, preview, receipt_path,
  readiness, recovery_command)` contains no presentation side effects.
- `execute(request, *, fixture_authorization=None) -> BrownfieldResult` is the one
  orchestration entry point.
- `adapt_legacy_brownfield(args) -> BrownfieldRequest` maps bare brownfield and
  `--draft-only` to non-overwriting draft/preview behavior and `--apply` to
  existing-proposal, non-refreshing preview-first apply. Existing installations
  route to migration; unsafe flags fail with guidance.
- Domain exceptions from all modules expose `exit_code` and redacted remediation.
  The adapter maps invalid usage/configuration to 2, conflict/readiness/verified-
  rollback failures to 1, and interrupted/unverified recovery to 3. Unexpected
  errors become concise exit 1 unless an active journal cannot be proven safe,
  in which case evidence is retained and exit 3 is returned.
- Successful apply writes the Appendix A adoption receipt only after committed
  promotion and final structural readiness 0. The receipt records bundle and
  identity versions, target/preview/managed hashes, adoption-time zero ledger
  rows, transaction ID, and readiness result. It never writes an operational
  fleet-ledger row.

#### Thin `bootstrap.py` adapter

- Extend brownfield parsing without changing greenfield, host-link, setup, or
  framework-doctor contracts.
- Preserve `brownfield <target>`, `--draft-only`, and `--apply` parsing.
- Add explicit actions/options for refresh, baseline adoption, migration,
  recovery, cleanup, identity manifest, preview hash, owner approval receipt,
  transaction workspace, and host readiness. Mutually exclusive modes and
  argparse usage errors exit 2.
- Remove canonical calls to `create_archaeology_report()`,
  `draft_constitution_proposal()`, and `apply_brownfield_framework()` from
  `run_brownfield()`. Delete or leave unreachable compatibility helpers only
  after tests prove no alternate unsafe route; final production code must contain
  no whole-tree brownfield copy.
- Convert `BrownfieldResult` to deterministic stdout/stderr and return its exit
  code. Do not catch `SystemExit` from argparse; expected domain errors print no
  traceback.

### 2.3 Canonical data and persistence schemas

| Artifact | Location | Required content and canonicalization |
|----------|----------|----------------------------------------|
| Evidence | `.sdd-proposal/archaeology.json` | Schema 1, target HEAD, sanitized evidence, sorted POSIX paths, evidence digest; no absolute target or raw remote. |
| Baseline manifest | `.sdd-proposal/baseline-manifest.json` | Schema 1, source revision, evidence digest, bundle/renderer versions, sorted per-file path/hash/length/dependencies/text policy. |
| Baseline bytes | `.sdd-proposal/.baseline/constitution/**` | Lossless generated bytes matching the baseline manifest; never inferred from reviewed content. |
| Host identity | `.sdd-proposal/host-identity.json`, then managed `.adoption/host-identity.json` | Exact ADR-026 Appendix B field/type/null/confirmation schema and fixed renderer keys. |
| Bundle manifest | Managed `.adoption/bundle-manifest.json` | Schema 1, `brownfield-core@1`, exact Appendix A entries, stable topological order, source/renderer hashes. |
| Preview | stdout plus caller-selected read-only export | Exactly six ordered category arrays; stable reasons and hashes; no timestamps/absolute roots in hashed semantic body. |
| Owner approval receipt | Operator-supplied outside generated host state | Schema 1, canonical target fingerprint and HEAD, exact preview hash, backup location, recovery command, owner identity/time. Never auto-created by the tool. |
| Transaction journal | Same-volume transaction workspace | Schema 1, target/HEAD/preview, operation preimage/candidate/backup hashes, ordered write-ahead states, recovery status. |
| Adoption receipt | `spec-driven-development/.adoption/receipt.json` | Schema 1, committed transaction, bundle/identity/managed hashes, adoption-time ledger zero-row evidence, structural readiness result. |
| Runtime ledger | `spec-driven-development/ledger/fleet.db` | Initialized from the unchanged copied `schema.sql`; dispatches and decisions both zero at adoption. Database remains ignored/untracked. |

All JSON writers append one LF. Hash-bearing JSON uses one canonical serializer.
Human-readable output may include the target supplied by the operator, but no
machine preview, receipt, journal, or generated managed file contains temporary
absolute roots or secrets.

### 2.4 End-to-end sequencing and exit propagation

#### Draft

1. Validate committed target and prove no active transaction.
2. Collect sanitized evidence without writing.
3. Draft identity with required human values unconfirmed.
4. Render proposal candidate and baseline in a transaction workspace.
5. Preview proposal creates/replacements; existing reviewed files are conflicts,
   never implicit replacements.
6. On exact proposal-preview approval, back up affected proposal files and commit
   proposal/baseline/evidence through the transaction engine.
7. Return 0 only after hashes verify; 1 for conflicts/verified rollback, 2 for
   invalid input, 3 for unresolved recovery.

#### Normal preview/apply

1. Validate target, baseline, reviewed proposal, and confirmed identity without
   running archaeology, proposal generation, or refresh.
2. Inventory the target and classify installation/path state.
3. Validate exact bundle membership, source hashes, renderer closure, and all
   path boundaries.
4. Render candidate bytes from identity/reviewed constitution and produce the
   deterministic six-category preview.
5. If no operation is required, return no-op 0 without backup/journal/receipt or
   ledger change.
6. For apply, verify exact preview hash and owner approval receipt; no public
   fixture bypass exists.
7. Preflight, stage complete candidate, run staged structural readiness, back up
   every affected destination plus reviewed proposal, and flush journal.
8. Promote in stable dependency order with per-path prepared/applied/verified
   journal states.
9. Run final structural host readiness. If it fails, roll back and return 1 when
   verified or 3 when not verifiable.
10. Commit receipt and report `installed; host readiness PASS` only after
    readiness exit 0. Retain backup until explicit cleanup.

#### Refresh/baseline adoption

1. Refresh is an explicit action; only it collects new evidence and renders a
   new candidate.
2. Validate baseline and classify every file with the five-outcome truth table.
3. Emit proposal-only preview; conflicts block and require explicit per-file
   resolution.
4. Exact approval uses the same backup/journal engine and never applies the SDD
   bundle.
5. Legacy no-baseline adoption follows the same path with candidate/baseline
   beside the untouched reviewed proposal; normal refresh/apply remains blocked
   until adoption commits.

#### Migration/recovery

1. Any existing installation requires explicit migration and inventory class.
2. Migration preview contains only enumerated managed creates/replacements;
   contamination and unknown work are preserved/reported.
3. Approved migration uses the same transaction path. It never deletes
   contamination or traverses an existing host link/junction.
4. Startup detects an active/unknown journal before other mutable work. Recovery
   compares preimage and candidate, completes or rolls back, verifies, and exits
   0/1/3 according to certainty. Cleanup is separately explicit.

### 2.5 No-real-host proof

The implementation must make fixture mutation distinguishable by construction:

- The public CLI accepts only an owner approval receipt for apply/migration.
- Test helpers create a fresh temporary parent, write a random fixture sentinel
  known only to the test process, initialize the host beneath that parent, and
  pass an in-memory `verified-fixture` authorization directly to
  `brownfield_compat.execute()`.
- Transaction preflight resolves both target and fixture root without following
  links, requires target to be a strict descendant of the verified temporary
  root, requires sentinel identity to match, rejects the real framework root and
  all ancestors, and requires the host's git directory to be under that target.
- Fixture authorization is not serializable to an accepted owner receipt and is
  not exposed by argparse or environment variables.
- A dedicated negative test passes the real checkout, a sibling, an ancestor,
  a linked target, a copied sentinel, and a temp-looking name; every case must
  fail before stage/backup/journal creation.
- Test snapshots assert the real framework git status, local ledger hash/size,
  generated exec hashes, and feature proposal bytes are unchanged by all fixture
  suites. This is the explicit proof for R-041, R-044, V-51, V-64, and V-65.

## 3. Implementation phases

| Phase | Goal | Dependencies | Required deliverable/checkpoint |
|-------|------|--------------|---------------------------------|
| P0 | Freeze contract and baseline | Approved ADR/SPEC; TASKS must first lock validation | Locked validation; explicit file scopes; baseline >=668 passed/2 skipped; schema/origin/staledoc/governance, Article X, local doctor green; real checkout hash snapshot. |
| P1 | Build isolated fixture factory and focused RED tests | P0 | Node and Python committed temp repositories, local bare remotes, Windows/POSIX variants, real-host mutation guard; focused tests fail only because SDD-058 behavior is absent. |
| P2 | Implement read-only inventory and proposal/baseline core | P1 | Path/evidence inventory, proposal generation, five-way refresh, invalid/legacy baseline behavior; focused GREEN for V-05..V-09 and path subsets. |
| P3 | Implement immutable bundle and identity/rendering core | P1; may proceed parallel to P2 because files do not overlap | Exact Appendix A membership/closure and Appendix B schema/renderers; source default deny; clean seeds; focused GREEN for V-10..V-22. |
| P4 | Implement migration classification and deterministic preview | P2, P3 | All installation/path classes, exactly six categories, no-op rerun, legacy/link behavior; focused GREEN for V-23..V-27 and V-39..V-44. |
| P5 | Implement bounded host readiness | P3; may start in parallel with P4 in disjoint files | Structural and quality modes, N/A framework checks, exact 0/1/2/3 semantics; focused GREEN for V-34..V-38A. |
| P6 | Implement transaction, rollback, and recovery | P4, P5 | Same-volume stage/backup/journal, write-ahead states, per-path promotion, injected rollback/recovery, retained evidence; focused GREEN for V-28..V-33. |
| P7 | Wire canonical compatibility adapter and thin bootstrap CLI | P2-P6 | Safe legacy mapping, explicit modes, no old broad-copy/regeneration route, exact exit/error wording, owner receipt and fixture authorization boundaries. |
| P8 | Complete cross-stack/platform integration and CI matrix | P7 | Full SPEC Section 9.1 scenario matrix on Windows and POSIX, semantic manifest comparison, newline/permission/rename equivalence, no-real-host proof. |
| P9 | Stage-1 spec-compliance QA | P8 | Independent reviewer maps every R/AC/V item; missing/extra/wrong findings resolved and re-reviewed before Stage 2. |
| P10 | Stage-2 quality/security QA and close gates | P9 only | Different reviewer; full >=668/2 regression floor plus additions; all repository/Article X/B-1/B-2/local doctor checks; exact-package owner approval; authorized push and public B-4 CI before DONE. |

### RED/GREEN checkpoints

- **RED-1:** Fixture/authentication tests fail because no verified-fixture API or
  new modules exist; prove real checkout is unchanged.
- **GREEN-1:** Fixture factory and no-real-host guard pass without production
  mutation beyond disposable fixture roots.
- **RED-2/GREEN-2:** Proposal preservation, baseline schema, five refresh outcomes,
  invalid baseline, and legacy adoption (V-05..V-09).
- **RED-3/GREEN-3:** Exact bundle, dependency closure, source default deny, seeds,
  identity schema/rendering, and remote sanitization (V-10..V-22).
- **RED-4/GREEN-4:** Six-category preview, approval binding, migration classes,
  safe legacy behavior, idempotence, and link rejection (V-23..V-27,
  V-39..V-44).
- **RED-5/GREEN-5:** Host-readiness composition, explicit N/A checks, exits,
  bounded wording, and quality disclosure/no-shell behavior (V-34..V-38A).
- **RED-6/GREEN-6:** Complete stage/backup/journal, every write-ahead interruption
  boundary, verified rollback, recovery-required, and explicit cleanup
  (V-28..V-33).
- **RED-7/GREEN-7:** CLI/compatibility end-to-end flows and both stack fixtures.
- Each RED command and intended assertion failure must be recorded in unlocked
  validation evidence only after TASKS locks it. Production changes may follow
  only the corresponding focused RED.

## 4. File map and non-overlapping work packets

No worker is dispatched by this plan. TASKS must derive atomic packets from this
map with one to three mutable files each and run the SDD-049 overlap checker
before any parallel dispatch.

### Production file map

| Packet candidate | Files (maximum three) | Responsibility | Dependency/serialization |
|------------------|-----------------------|----------------|--------------------------|
| A | `cli/brownfield_inventory.py`, `cli/test_brownfield_inventory.py` | Evidence, safe paths, inventory facts | Foundational; serial before D/F integration. |
| B | `cli/brownfield_proposal.py`, `cli/test_brownfield_proposal.py` | Proposal/baseline/refresh/adoption | After A; parallel-safe with C. |
| C | `cli/brownfield_manifest.py`, `cli/test_brownfield_manifest.py` | Exact bundle, closure, preview schema | After fixture RED; parallel-safe with B and D. |
| D | `cli/brownfield_identity.py`, `cli/test_brownfield_identity.py` | Appendix B, sanitization, renderers | Reads A contracts; parallel-safe with B/C once A interface freezes. |
| E | `cli/brownfield_migration.py`, `cli/test_brownfield_migration.py` | Installation/path classes and no-op plan | Requires A/C/D; serial after their interfaces freeze. |
| F | `cli/host_readiness.py`, `cli/test_host_readiness.py` | Structural/quality readiness | Requires C/D schemas; parallel-safe with E in disjoint files. |
| G | `cli/brownfield_transaction.py`, `cli/test_brownfield_transaction.py` | Stage/backup/journal/promote/rollback/recovery | Requires C/E/F contracts; serialized because it consumes all mutation plans. |
| H | `cli/brownfield_compat.py`, `cli/bootstrap.py`, `cli/test_brownfield_cli.py` | Canonical orchestration and thin legacy CLI adapter | Final production integration; serial after B-G. |
| I | `.github/workflows/doctor.yml`, `cli/test_brownfield_cross_platform.py` | Windows/POSIX matrix and workflow wiring | After H; workflow remains read-only validation. |

`spec-driven-development/cli/` is abbreviated as `cli/` in the tables. The exact
repository-relative path is always `spec-driven-development/cli/<name>`.

### Test-only construction map

| File | Purpose | Mutation boundary |
|------|---------|-------------------|
| `cli/brownfield_test_fixtures.py` | Build disposable committed Node/Express and Python repositories, local bare remotes, identity/proposal variants, snapshots, failure injectors, and platform-normalized assertions. | May write only beneath a caller-created temporary root; imported by test files only; excluded from `brownfield-core@1`. |
| `cli/test_brownfield_inventory.py` | Evidence, path normalization, malicious paths, links, classifications input, secret redaction. | Read-only against real source; fixture writes only. |
| `cli/test_brownfield_proposal.py` | Baseline schema/hashes, apply non-invocation spies, five refresh outcomes, legacy adoption. | Proposal fixture only. |
| `cli/test_brownfield_manifest.py` | Exact Appendix A set, closure/order/hash/renderers, unlisted canary, positive seeds/fingerprints/schema hash. | Candidate fixture only. |
| `cli/test_brownfield_identity.py` | Exact Appendix B types/order, confirmations, remote secrets, deterministic Node/Python rendering. | Candidate fixture only. |
| `cli/test_brownfield_migration.py` | Eight installation and seven path classes, contamination preservation, no-op, link guidance. | Read-only plans plus approved disposable fixture integration. |
| `cli/test_brownfield_transaction.py` | Approval binding, stage/backup/journal, failure injection at every transition, rollback/recovery/cleanup. | Verified disposable fixture only. |
| `cli/test_host_readiness.py` | Exact check composition, N/A rows, exits, quality disclosure/no-shell, readiness wording. | Structural fixture reads; explicit harmless fixture quality commands only. |
| `cli/test_brownfield_cli.py` | Legacy/new parsing, adapter-only routing, no unsafe helpers, exit/stderr contracts, owner receipt and fixture non-exposure. | Default dry-run; direct fixture authorization only in integration cases. |
| `cli/test_brownfield_cross_platform.py` | Complete SPEC 9.1 Node/Python matrix, semantic expected manifests, newline/mode/rename equivalence, no-real-host snapshots. | Verified disposable fixture only. |

The fixture helper is introduced in its own TASKS packet with one focused test
file (two-file scope). Subsequent tests may import it but do not edit it in
parallel. Any helper correction is a serialization point across all test tracks.

### Candidate parallel tracks

- After P1 freezes fixture helpers, B (proposal), C (manifest), and the identity
  portion of D can proceed in parallel only if A's public dataclasses are frozen
  and their mutable file sets remain disjoint.
- E (migration) and F (readiness) can proceed in parallel after C/D schemas are
  frozen; they share no mutable file.
- Security test expansion may proceed in the owning test file for each module;
  there is no shared catch-all test file.
- Workflow/cross-platform wiring waits until H and is serial.
- Transaction and compatibility integration are always serial because they
  consume all lower-level contracts.

### Mandatory serialization points

1. Validation lock and baseline evidence before any implementation/test edit.
2. Fixture-helper interface before parallel module test authoring.
3. Inventory dataclasses/path API before proposal/identity/migration integration.
4. Frozen manifest/identity schemas before migration/readiness.
5. Frozen preview and readiness callback before transaction implementation.
6. Transaction completion before compatibility/bootstrap integration.
7. All implementation integration before Stage-1 review.
8. Stage-1 PASS before Stage-2 review.
9. Stage-2 and all local gates before exact-package owner approval.
10. Owner approval before push; public CI before DONE/Sprint 24 close.

## 5. Fixture and Windows/POSIX CI design

### Node/Express fixture

Construct a repository on explicit branch `main` with local author identity,
baseline commit, and local bare `origin`. Include `package.json`, lockfile,
Express source, JavaScript test, TypeScript or JavaScript config evidence,
README, `.gitignore`, existing unrelated `.github/` file, CRLF host file,
host-owned content collision variants, and a generated proposal whose reviewed
constitution has partial human byte edits. Configure tokenized npm commands as
data but never execute them during apply.

### Python fixture

Construct a repository on explicit branch `trunk` (to prove no main/master
assumption) with local author identity, baseline commit, and local bare `origin`.
Include `pyproject.toml`, package source, stdlib/pytest-style test evidence,
different CI/convention evidence, README, `.gitignore`, LF host files, no initial
Copilot instructions in the fresh scenario, and managed-current, managed-drift,
legacy-broad-copy, mixed-contaminated, and rerun variants. Quality command values
are confirmed token arrays; test execution uses harmless interpreter commands
only in explicit `--run-quality` unit cases.

### Platform matrix

- Replace the single-OS workflow job with a matrix containing
  `ubuntu-latest` and `windows-latest`, Python 3.12, checkout, pytest install,
  focused SDD-058 tests, then the existing explicit CI doctor command.
- Keep permissions `contents: read`, no credentials, no cloud login, no network
  use after dependency setup, and no real-host apply.
- Tests compare parsed semantic previews rather than platform newlines in console
  capture. All manifest paths are POSIX-relative and hashes derive from canonical
  bytes.
- POSIX exercises symlink, read-only/mode variance, LF/CRLF, and atomic rename
  injection. Windows exercises symlink/junction/reparse detection without relying
  on privilege, read-only attributes, LF/CRLF, open-handle/replace injection, and
  drive/UNC/reserved-name rejection.
- An OS-inapplicable mechanism receives an explicit equivalent behavior test; it
  is not silently skipped. Existing repository-wide two platform-specific skips
  may remain, but SDD-058's matrix must satisfy every SPEC 9.1 cell.

## 6. Migration and backward compatibility strategy

- Keep legacy parser syntax, but change its semantics at the adapter boundary.
  Bare/draft invocation never overwrites a reviewed proposal; apply never drafts
  or refreshes.
- A proposal generated before baseline schema v1 remains user-owned. Apply and
  refresh exit 1 with an `adopt-baseline` remediation. Adoption creates candidate
  artifacts beside existing bytes and uses preview/backup/transaction approval.
- An existing SDD installation cannot enter fresh apply. It must use `migrate`,
  which classifies receipt-managed, modified, host-owned, forbidden, and linked
  content before planning.
- Existing broad-copy contamination is never interpreted as ownership solely by
  path/name. Receipt hashes establish managed state; absent proof defaults to
  host-owned/forbidden-contamination and preservation.
- Existing `fleet.db`, backlog, specs, sprints, dispatches, sessions, and other
  history remain byte-identical in migration. The new zero-row rule applies to a
  fresh installation and the adoption receipt, not to an established host.
- Existing host identity/config is preserved unless a managed replacement appears
  in the exact preview. Replacement always has preimage hash, backup, and rollback.
- Existing host-link/junction installations are detected without traversal and
  require the operator to detach the link before a new inventory. SDD-058 does
  not perform the detach or mutate the linked framework tree.
- An unchanged managed-current rerun returns the same semantic preview/no-op
  result and creates no transaction, backup, receipt churn, or fleet-ledger row.
- Greenfield, host-link, setup, and framework doctor remain behaviorally unchanged.

## 7. Security, error handling, and rollback

### Security/path handling

- Perform lexical validation before resolution, then component-wise containment
  checks with `lstat`/non-following traversal. Reject links/reparse points in every
  managed ancestor and re-check immediately before mutation to reduce TOCTOU risk.
- Reject NUL/control characters, Windows reserved components and trailing dot/
  space aliases, drive-relative/UNC/absolute inputs, mixed traversal, `.git` at
  any depth, case-fold collisions, and destination ancestor/descendant overlap.
- Require framework sources to be regular files beneath the resolved framework
  root and match manifest SHA-256 before reading for materialization.
- Never print a raw remote, identity secret candidate, host file content,
  environment value, or quality command environment. Redact at ingestion so
  downstream objects cannot accidentally serialize secrets.
- Quality command `cwd` is POSIX-relative and contained in host root; argv is a
  non-empty array when configured; timeout is 1..3600; environment is minimal or
  explicitly confirmed inherited; network policy is disclosed. No shell.
- Refuse non-fixture apply unless approval receipt target fingerprint, HEAD,
  preview hash, backup location, and recovery command all match current inputs.

### Error/exit propagation

| Exit | Source conditions | Mutation guarantee |
|------|-------------------|--------------------|
| 0 | Successful read-only action; no-op rerun; committed apply plus structural host-readiness PASS; verified recovery | No overclaim; receipt/reference printed when applicable. |
| 1 | Conflict, missing confirmation, managed drift, readiness failure, contamination requiring migration/approval, or failed apply with verified rollback | Zero mutation or byte-verified restoration. |
| 2 | Argparse usage, unsupported mode/version, malformed schema/path/config, ambiguous required evidence, invalid/stale approval | No stage/backup/journal/host/proposal mutation. |
| 3 | Active interrupted transaction, unknown operation state, or unverified rollback/recovery | Preserve journal/stage/backup; block other mutation; print deterministic recovery command. |

Expected exceptions terminate at `brownfield_compat`/`bootstrap.main` with concise
stderr and no traceback. An unexpected exception before journal creation is exit
1 with no mutation; after a journal enters a mutable state it invokes rollback,
then returns 1 only after verification or 3 otherwise.

### Rollback strategy

- Code rollback before release is a normal revert of SDD-058 production/tests/
  workflow. No ledger or constitution migration is required.
- Host transaction rollback is data-first: reverse verified operations, restore
  backed-up bytes/metadata, remove only transaction-created managed paths, and
  verify all preimages. Never delete unlisted or contamination paths.
- A committed adoption is not automatically uninstalled by reverting framework
  code. Its retained receipt/journal/backup must be processed by the matching
  explicit recovery/cleanup version.
- Backups survive success and failure until explicit cleanup. Cleanup validates a
  terminal transaction, receipt, and hashes; it refuses active or recovery-
  required state.
- If public CI fails after an authorized push, do not mark DONE. Repair under the
  same locked contract or revert the code package; never use a host transaction to
  conceal a framework regression.

## 8. Testing and two-stage QA

### Automated test layers

1. Pure unit matrices: path handling, baseline truth table, graph closure,
   identity schema/sanitization, classifications, preview canonicalization,
   journal state machine, readiness exits.
2. Filesystem component tests: stage/backup/promote/rollback, byte/mode/newline
   preservation, injected errors, links/reparse points, zero-row SQLite.
3. CLI adapter tests: old/new syntax, no unsafe route, exact exits/stderr, no
   traceback/success wording, no public fixture bypass.
4. End-to-end fixture tests: every SPEC Section 9.1 row for Node and Python.
5. Repository regression: complete suite floor, lints, Article X 3/3, strict local
   doctor, B-1/B-2, and public cross-platform B-4 CI.

### Stage 1 -- spec compliance

A reviewer who did not implement the code must independently verify every
R-001..R-044 (including A suffixes), AC-01..AC-15, and V-01..V-65 (including A
suffixes). Findings use only `MISSING`, `EXTRA`, or `WRONG`. Stage 1 must inspect
the exact `brownfield-core@1` set, prove no alternate unsafe code path, review
real-host guard evidence, and compare Windows/POSIX run artifacts. Every finding
is fixed and re-reviewed before Stage 2.

### Stage 2 -- code quality/security

A different reviewer starts only after recorded Stage-1 PASS. Review domain
separation, dependency direction, path/secret handling, transaction durability,
TOCTOU controls, error redaction, test determinism, maintainability, performance,
and absence of dependencies/scope creep. Critical/important findings are fixed
and re-reviewed. Stage 2 cannot waive a Stage-1 requirement.

## 9. Traceability

### Requirements to plan and evidence

| Requirement | Plan ownership | Primary evidence |
|-------------|----------------|------------------|
| R-001 | Proposal + adapter; normal apply sequence | V-05; AC-01 |
| R-002 | Proposal baseline schema | V-06; AC-02 |
| R-003 | Proposal explicit refresh | V-07, V-08; AC-02 |
| R-004 | Five outcomes and conflict resolution | V-07, V-08; AC-02 |
| R-005 | Baseline validation/adoption | V-09; AC-02 |
| R-006 | Manifest exact versioned entries | V-10, V-11; AC-03 |
| R-007 | Manifest/path/graph validation | V-11, V-45; AC-03, AC-10 |
| R-008 | Per-entry source selection | V-12; AC-03 |
| R-009 | Frozen Appendix A set/rosters | V-10; AC-03 |
| R-010 | Explicit forbidden assets | V-13; AC-03, AC-04 |
| R-011 | Seed renderer/zero-row ledger | V-14, V-16; AC-04 |
| R-012 | Positive seed plus fingerprints | V-15; AC-04 |
| R-013 | Identity datamodel/validator | V-17, V-17A; AC-05 |
| R-014 | Confirmation classifications | V-18, V-19; AC-05 |
| R-015 | Stack/quality/conventions/boundaries | V-19, V-21; AC-05 |
| R-016 | Deterministic renderers | V-17A, V-20, V-21; AC-05 |
| R-016A | Remote sanitizer/redaction | V-21A; AC-05, AC-10 |
| R-017 | Identity ownership/backup | V-22; AC-05, AC-07 |
| R-018 | Preview exact categories/no mutation | V-23, V-24; AC-06 |
| R-019 | Canonical preview/hash approval | V-25, V-26; AC-06 |
| R-020 | Blocking gates/no bypass | V-26, V-27; AC-06 |
| R-021 | Complete stage + structural readiness | V-28, V-30; AC-07 |
| R-022 | Backup/durable write-ahead journal | V-29, V-31A; AC-07 |
| R-023 | Atomic per-path promote/verified rollback | V-30, V-31, V-31A; AC-07 |
| R-024 | Recovery-required/cleanup boundary | V-31A, V-32, V-33; AC-07 |
| R-025 | Separate host-doctor | V-34; AC-08 |
| R-026 | Exact host checks | V-16, V-35; AC-08 |
| R-027 | Explicit framework N/A | V-36; AC-08 |
| R-028 | Readiness exit/success wording | V-37, V-38; AC-08 |
| R-028A | Structural apply and explicit quality | V-28, V-38A; AC-08 |
| R-029 | Installation/path classes | V-39, V-40; AC-09 |
| R-030 | Preserve migration content | V-41; AC-09 |
| R-031 | Safe legacy adapter | V-27, V-42; AC-09 |
| R-032 | No-op rerun | V-43; AC-09 |
| R-033 | Link/junction migration | V-44; AC-09, AC-10 |
| R-034 | Full path matrix | V-45; AC-10 |
| R-035 | Data/no-shell execution | V-46; AC-10 |
| R-036 | UTF-8/LF and byte preservation | V-52, V-53; AC-10, AC-11 |
| R-037 | Redacted actionable failures | V-47, V-48; AC-10 |
| R-038 | Stdlib/main pattern/module boundaries | V-55, V-56; AC-12 |
| R-039 | Two realistic fixtures | V-49, V-50, V-54A; AC-11 |
| R-040 | Equivalent Windows/POSIX evidence | V-52, V-53, V-54, V-54A; AC-11 |
| R-041 | Isolated local git/no real mutation | V-51, V-64; AC-11 |
| R-042 | RED/GREEN and repository gates | V-57..V-60; AC-12 |
| R-043 | Gate ordering and exact package | V-01..V-04, V-61..V-64; AC-13, AC-14 |
| R-044 | Separate real-host approval | V-65; AC-15 |

### Acceptance coverage

| Acceptance | Phases | Validation proof |
|------------|--------|------------------|
| AC-01 | P2, P7, P8 | V-05 |
| AC-02 | P2, P7, P8 | V-06..V-09 |
| AC-03 | P3, P8 | V-10..V-13 |
| AC-04 | P3, P8 | V-13..V-16 |
| AC-05 | P3, P8 | V-17, V-17A, V-18..V-22 |
| AC-06 | P4, P7, P8 | V-23..V-27 |
| AC-07 | P6, P8 | V-22, V-28..V-33, V-53 |
| AC-08 | P5, P6, P8 | V-16, V-34..V-38A |
| AC-09 | P4, P7, P8 | V-27, V-39..V-44 |
| AC-10 | P2..P8 | V-21A, V-45..V-48 |
| AC-11 | P1, P8 | V-49..V-54A |
| AC-12 | P0..P10 | V-55..V-60 |
| AC-13 | P0, P9 | V-01..V-04, V-61, V-63, V-64 |
| AC-14 | P10 | V-62 |
| AC-15 | P1, P7..P10 | V-65 |

### Complete validation-item allocation

| Validation items | Owning phase/file group |
|------------------|-------------------------|
| V-01, V-02, V-03, V-04 | P0/P9 governance and repository-history review; validation remains unlocked now and locks only at TASKS. |
| V-05, V-06, V-07, V-08, V-09 | P2 proposal tests. |
| V-10, V-11, V-12, V-13, V-14, V-15, V-16 | P3 manifest/seed tests. |
| V-17, V-17A, V-18, V-19, V-20, V-21, V-21A, V-22 | P3 identity tests plus P6 rollback integration for V-22. |
| V-23, V-24, V-25, V-26, V-27 | P4 preview and P7 CLI tests. |
| V-28, V-29, V-30, V-31, V-31A, V-32, V-33 | P6 transaction tests. |
| V-34, V-35, V-36, V-37, V-38, V-38A | P5 readiness tests and P7 wording integration. |
| V-39, V-40, V-41, V-42, V-43, V-44 | P4 migration and P7 legacy CLI tests. |
| V-45, V-46, V-47, V-48 | Module-owned security matrices, consolidated in P9 compliance review. |
| V-49, V-50, V-51, V-52, V-53, V-54, V-54A | P1 fixture construction and P8 cross-platform suite/workflow. |
| V-55, V-56, V-57, V-58, V-59, V-60 | P0 baseline, module review, RED/GREEN history, and P10 local gates. |
| V-61 | P9 PASS followed by P10 Stage-2 evidence. |
| V-62 | P10 exact-package owner approval and public CI evidence. |
| V-63, V-64 | P9/P10 history, scope, and evidence-integrity audit. |
| V-65 | P1/P7 no-real-host architecture and P9 independent negative proof. |

Every validation identifier, including V-17A, V-21A, V-31A, V-38A, V-54A,
is allocated above. TASKS must map each item to one or more atomic tasks without
changing its wording or checking it before evidence exists.

## 10. Alternatives rejected

- **ALT-001:** Keep brownfield logic in `bootstrap.py`. Rejected because it
  preserves coupled side effects and violates ADR-026's distinct responsibilities.
- **ALT-002:** Add a ninth shared production utility module. Rejected for v1;
  ownership remains with the eight approved modules and dataclass imports follow
  the declared DAG. A future common module would require ADR/SPEC amendment if it
  changed Appendix A membership.
- **ALT-003:** Store transaction work inside the host installation. Rejected
  because it creates unlisted managed destinations and complicates clean-state
  proof. Use an approved same-volume sibling workspace instead.
- **ALT-004:** Check in static fixture repositories. Rejected because nested git
  metadata is brittle and platform-dependent. Deterministic stdlib helpers create
  committed temporary repos and local bare remotes at test time.
- **ALT-005:** Expose `--fixture` on the public CLI. Rejected because a real host
  could self-declare fixture status and bypass R-044.
- **ALT-006:** Reuse framework doctor. Rejected because its checks and promise are
  framework-specific; host readiness remains separately named and composed.
- **ALT-007:** Auto-delete recognized contamination. Rejected because appearance
  is not ownership proof and SDD-058 explicitly preserves contamination.
- **ALT-008:** Whole-tree staging followed by denylist cleanup. Rejected because
  default-deny applies to source selection, including staging.

## 11. Risks and mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Exact Appendix A encoding omits a transitive dependency | Medium | High | Frozen structural expected set, per-source hashes, closure test, staged readiness on both stacks. |
| Shared dataclasses churn across parallel work | Medium | High | Freeze A/C/D interfaces at serialization checkpoints; no shared test file edits; overlap scan before dispatch. |
| Transaction failure leaves mixed host state | Medium | Critical | Complete preflight/stage/backup, write-ahead journal, injected boundary failures, reverse verification, exit 3 on uncertainty. |
| Windows open handles or metadata prevent replace/rollback | Medium | High | Preflight probes, supported metadata contract, open-handle injection, retained recovery assets, no whole-tree rename claim. |
| Path validation has platform alias gaps | Medium | Critical | Lexical plus resolved checks, Windows/POSIX malicious matrix, case-fold and reserved-name tests, no link traversal. |
| Remote credential reaches evidence | Low | Critical | Sanitize before object creation; secret canaries across every serializer/error channel. |
| Host quality command causes side effects | Medium | High | Never during apply; explicit disclosure and `--run-quality`; token arrays/no shell; policies and timeout; fixture-harmless commands only. |
| Fixture exemption can be forged | Low | Critical | In-memory sentinel-bound authorization, no CLI/env representation, strict descendant/repo checks, real-root negative tests. |
| Migration misclassifies host work | Medium | Critical | Receipt/hash evidence first, host-owned default, no contamination deletes, exact preview/backup for managed replacement. |
| CI matrix increases runtime/flakiness | Medium | Medium | Local bare remotes, no external network in tests, deterministic timestamps/branches, pure semantic comparisons, focused suite before full doctor. |
| Plan accidentally changes immutable bundle membership | Low | Critical | Structural Appendix A equality test and Stage-1 review; any difference routes back to ADR/SPEC owner approval. |

## 12. Completion and handoff criteria

This PLAN is ready for TASKS only when:

- schema lint accepts the artifact;
- `git diff --check` is clean;
- every ADR-026 responsibility and immutable Appendix A/B boundary is represented;
- every R-001..R-044, AC-01..AC-15, and V-01..V-65 identifier, including all
  letter-suffixed items, has explicit plan ownership;
- candidate task packets remain one to three mutable files and all overlap/
  serialization points are explicit;
- validation remains draft/unlocked and unchanged.

TASKS must then lock validation before authoring any implementation or test edit,
create atomic RED-first tasks from the packet map, preserve the exact dependency
sequence, and record separate Stage-1 and Stage-2 reviewers. This plan does not
authorize worker dispatch, implementation, commit, push, validation checkmarks,
or any non-fixture host mutation.