---
id: SDD-20260712BROWNFIELD-review-stage-2
type: validation
status: blocked
owner: principal-cloud-security-architect
updated: 2026-07-27
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# Stage-2 Review: SDD-058 Brownfield bootstrap correctness

- Review date: 2026-07-20
- Reviewer: Principal Cloud Security Architect reviewer B (independent; no implementation and not the Stage-1 reviewer)
- Exact reviewed implementation: `9e743e4bd6d7baa16debcc25ee5cad487dcf9782`
- Durable Stage-1 package: `a086ce6d583dae676e02bdff1ead656a8cff0aec`
- Stage-1 PASS evidence: **COMPLIANT** at `2026-07-20 08:24:24 -07:00`; the containing commit was authored at `2026-07-20 08:27:22 -07:00`
- Stage-2 completion time: `2026-07-20 09:03:58 -07:00`
- Verdict: **CHANGES REQUIRED**

---

## Strengths

- The manifest is an explicit, default-deny allowlist; the approved preview now binds the deterministic receipt mutation.
- Normal real-host apply requires a target/HEAD/preview/backup/recovery-bound owner receipt; fixture authority is in-memory and root-bound.
- Normal path validation rejects lexical escape, resolved escape, symlink, junction, and reparse traversal.
- Quality commands use token arrays, `shell=False`, a contained cwd, a reduced environment, and bounded direct-process timeouts.
- The transaction suite covers interruption boundaries, atomic per-path replacement, rollback verification, unknown third-state refusal, cleanup eligibility, and recovery-required retention.
- The Windows/POSIX workflow matrix and focused fixture coverage are substantial, and all Stage-2 test commands completed green.

## CRITICAL Findings

### CRITICAL-01: Recovery and cleanup trust mutable journal paths

- Evidence: `brownfield_transaction.py:728-805` reconstructs authority and absolute roots directly from journal JSON. `inspect_recovery`, `rollback`, and `cleanup` then read, replace, unlink, or recursively delete journal-selected paths. `brownfield_compat.py:950-959` exposes these operations through the public `recover` and `cleanup` actions.
- Failure scenario: a corrupted or attacker-written journal can select an unrelated target, backup, stage, lock, or operation destination and cause overwrite, unlink, or `shutil.rmtree` outside the authorized transaction workspace.
- Required Software Developer repair: define and validate a strict journal schema; derive trusted roots from the user-supplied workspace rather than journal absolutes; require journal/lock identity and authorization binding; revalidate every destination and backup path beneath trusted roots; reject links/reparse points; and add adversarial public-CLI tests for absolute, traversal, foreign-root, symlink/junction, and tampered-authorization journals.

### CRITICAL-02: Backup is declared complete without durable, verified preimages

- Evidence: `brownfield_transaction.py:325-343` silently ignores file/directory fsync errors and skips directory fsync on Windows. `backup` at lines 577-600 copies preimages and writes `BACKED_UP` without verifying copied hashes/modes or durably syncing backup files and directories first.
- Failure scenario: an interrupted or degraded write can leave a journal that authorizes promotion while the only rollback copy is absent, partial, or not durable.
- Required Software Developer repair: verify every copied backup against the recorded preimage before transition; durably flush backup files and parent directories using a supported cross-platform strategy; fail closed on durability errors; write `BACKED_UP` only after proof; and add corruption, short-write, fsync-failure, and interruption tests.

### CRITICAL-03: Mutation and recovery do not re-establish link/reparse safety

- Evidence: preflight path checks are not repeated in `backup`, `promote`, `rollback`, `inspect_recovery`, or `cleanup` (`brownfield_transaction.py:577-805`). These operations perform path-based opens, copies, replacements, unlinks, directory creation, and recursive deletion after a mutable interval.
- Failure scenario: a validated parent can be replaced with a symlink, junction, or reparse point after preflight, redirecting backup, promotion, rollback, recovery, or cleanup outside the host/workspace.
- Required Software Developer repair: introduce a single mutation-boundary resolver that verifies trusted root identity, lexical/resolved containment, and every ancestor immediately before each filesystem operation; reject link/reparse substitution; prefer handle-relative/no-follow primitives where available; and add deterministic race/substitution tests on Windows and POSIX.

## IMPORTANT Findings

### IMPORTANT-01: The receipt omits four managed executable modules

- Evidence: `brownfield_compat.py:589-598` explicitly excludes `bootstrap.py`, `brownfield_compat.py`, `brownfield_manifest.py`, and `host_readiness.py` from `managed_hashes` even though they are installed executable runtime assets.
- Risk: post-install tampering of these control-plane modules is not detected by managed-integrity readiness.
- Required repair: bind every installed managed executable to the receipt, or document and enforce an equivalent immutable trust mechanism; add tamper tests for each module.

### IMPORTANT-02: Apply does not compare approved HEAD with current Git HEAD

- Evidence: `brownfield_compat.py:653-668` passes `identity.target_head` into transaction authorization/preflight but does not collect and compare the target repository's current HEAD at apply time.
- Risk: commits can change after inventory/review while apply still accepts the stale identity value.
- Required repair: read current HEAD immediately before preflight and before first promotion, require equality with the approved receipt/identity, and test drift at both boundaries.

### IMPORTANT-03: Reviewed proposal descendants may be links/reparse points

- Evidence: `_reviewed_constitution` reads proposal children directly (`brownfield_compat.py:438-445`); refresh/adoption do the same (`brownfield_proposal.py:289-376`). `_read_snapshot` at lines 139-150 resolves and follows links rather than rejecting them.
- Risk: external or sensitive bytes can enter a proposal, preview, rendered output, or baseline through a linked descendant.
- Required repair: reject symlink/junction/reparse proposal roots, manifests, reviewed files, and snapshots; use the canonical safe-path primitive; add external-link tests on Windows and POSIX.

### IMPORTANT-04: `network_policy=deny` is claimed but not enforced

- Evidence: `host_readiness.py:376-394` validates the string value, while lines 465-482 invoke the command without a sandbox or network-isolation mechanism; disclosure states `network=deny`.
- Risk: approved host commands can access the network despite the reported policy.
- Required repair: either enforce denial with a supported platform boundary or rename the field/disclosure to an accurate non-enforced declaration and require explicit owner consent for network-capable commands. Add a behavioral policy test.

### IMPORTANT-05: Quality-command evidence lacks complete secret redaction

- Evidence: `brownfield_identity.py:92-94,211-240` catches expansions and assignment-like tokens but does not bind flag/value pairs such as `--token literal`; `host_readiness.py:465-489` emits raw argv, stdout/stderr, and exception text.
- Risk: credentials in argv or command output can be written to review evidence or console output.
- Required repair: reject credential-bearing flag/value patterns, redact argv before disclosure, redact bounded stdout/stderr/exception evidence, and test common token/password/API-key forms without persisting test secrets.

### IMPORTANT-06: Fatal Git ignore checks can falsely PASS

- Evidence: `host_readiness.py:343-353` inspects stdout but does not reject unexpected nonzero `git check-ignore` return codes.
- Risk: Git failure or repository corruption can be reported as managed paths being safe.
- Required repair: accept only documented success/no-match return codes, fail closed on all others, preserve sanitized diagnostics, and add return-code tests including 128.

### IMPORTANT-07: Timeout does not bound descendant processes

- Evidence: `host_readiness.py:475-482` uses `subprocess.run(timeout=...)` for the direct process only and does not establish or terminate a process group/job.
- Risk: a timed-out quality command can leave children running with filesystem or network side effects.
- Required repair: launch commands in an isolated process group/job, terminate the full tree on timeout, verify cleanup, and add a child-process timeout test for Windows and POSIX.

## SUGGESTIONS

- Require candidate materialization to consume only a validated bundle type rather than structurally compatible caller objects.
- Pin GitHub Actions by immutable SHA and constrain the pytest version in `.github/workflows/doctor.yml` to improve CI supply-chain reproducibility.

## Commands and Results

- Nine-file SDD-058 workflow suite: the VS Code task progressed through 74% without a failure but did not return its final summary; a duplicate synchronous run was stopped after green progress because the fully captured security-sensitive slice below already exercised the reviewed risk surface.
- Security-sensitive transaction/readiness/identity/inventory slice: `233 passed in 789.54s`.
- Schema lint: `Schema lint clean.`
- `git diff --check` before review artifacts: clean.
- Reviewed package confirmation: clean worktree at `a086ce6d583dae676e02bdff1ead656a8cff0aec`; implementation `9e743e4bd6d7baa16debcc25ee5cad487dcf9782`.

Green tests demonstrate normal and injected-failure stability, but the current suite does not cover hostile journal metadata, post-preflight link substitution, current-HEAD drift, proposal descendants backed by links/reparse points, or enforced network denial.

## Gate and Handoff

T-058-022 is **blocked** and V-61 remains unchecked. Route CRITICAL-01 through CRITICAL-03 and IMPORTANT-01 through IMPORTANT-07 to the Principal Software Developer as explicit repair tasks with RED-before-GREEN evidence. After repairs, rerun Stage 1 only if a concrete requirement mapping changes; otherwise repeat independent Stage 2 on the repaired commit.

Owner approval, push, public Windows/POSIX CI, SDD-058 DONE, Sprint 24 close, and executive-surface regeneration remain unauthorized and ineligible.

---

## Independent Re-review (2026-07-27)

- Reviewer: Principal Cloud Security Architect reviewer B (independent; did not implement the repair)
- Base and current Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed state: current dirty diff on `feature/f7.5-sdd-058-stage-2-security`
- Scope: Stage-2 code quality, security, and maintainability only; Stage 1 was not repeated
- Verdict: **CHANGES REQUIRED**

The repair materially improves journal validation, durable backups, receipt integrity, Git-HEAD binding, proposal path safety, quality-command disclosure, Git error handling, and process containment. Three original findings remain open because their required adversarial boundary evidence or implementation is incomplete.

### Original Finding Disposition

#### CRITICAL-01: OPEN

- The transaction engine now derives target/workspace trust from caller-supplied roots, requires the exact `workspace/transaction.json`, validates a strict top-level and nested journal schema, derives stage/lock paths from the transaction ID, constrains backup/proposal paths, binds lock identity, and requires a registered authorization whose target fingerprint, HEAD, preview hash, backup root, and recovery command match the journal (`brownfield_transaction.py::_validated_journal`, `_validate_journal_authorization`, `_context_from_journal`).
- Direct engine tests reject a journal-selected foreign target, forged-equal authorization, authorization-field tampering, malformed nested operation records, and forged cleanup authorization without mutation (`test_brownfield_transaction.py::test_recovery_rejects_journal_selected_foreign_target_without_mutation`, `test_recovery_rejects_forged_equal_authorization_without_mutation`, `test_recovery_rejects_journal_authorization_field_tampering_without_mutation`, `test_recovery_rejects_malformed_nested_operation_records`, `test_cleanup_rejects_forged_equal_authorization_without_deleting_evidence`).
- Closure is incomplete at the public boundary. `brownfield_compat.py::execute` correctly routes caller-provided target/workspace and a loaded owner receipt into the validated engine, but `test_brownfield_cli.py::test_canonical_recover_and_cleanup_route_to_transaction_engine` replaces authorization loading and both transaction operations with mocks. There is no public `execute` adversarial test proving tampered roots, journal fields, links/reparse points, or authorization fail closed without mutation. That public recovery/cleanup evidence was an explicit CRITICAL-01 closure condition.

#### CRITICAL-02: CLOSED

- `brownfield_transaction.py::backup` now flushes and verifies each destination preimage by hash, size, and portable mode before recording it; verifies every reviewed-proposal file, including multi-file proposals; flushes copied files and directories; fails closed on OS/durability errors; and writes `BACKED_UP` only after verification.
- `fsync_file` no longer suppresses errors. `fsync_directory` uses `FlushFileBuffers` on a Windows directory handle and `os.fsync` on POSIX, propagating failures.
- Tests cover file and directory fsync failure, corrupt/short copies, mode mismatch, multi-file proposal corruption, interruption around durable journal transitions, and the rule that incomplete staging never creates backup or mutates the host (`test_brownfield_transaction.py::test_backup_fsync_failure_never_reaches_backed_up`, `test_multifile_proposal_backup_corruption_never_reaches_backed_up`, `test_backup_verification_failure_never_reaches_backed_up`, `test_each_prepared_applied_verified_interruption_is_startup_recoverable`, `test_failed_or_incomplete_stage_never_creates_backup_or_mutates_host`).
- The supplied TDD record confirms the multi-file corruption test was genuinely RED (`DID NOT RAISE`) before the per-file verification repair and GREEN afterward.

#### CRITICAL-03: OPEN

- `_mutation_destination` and `_evidence_deletion_path` now reject lexical/resolved escape and link/junction/reparse traversal. Backup source reads, promotion destinations, rollback destinations, recovery inspection reads, parent pruning, and cleanup deletion calls use one of these guards.
- The repair does not yet protect every immediate filesystem boundary. `stage_candidate` can `rmtree` and recreate `context.stage_root` without the evidence-path guard. `backup` creates and writes `context.backup_root`, `reviewed-proposal`, and descendant backup paths without an immediate trusted-root resolver. `promote` reads staged sources and writes predictable `.<name>.<transaction_id>.candidate` paths without rejecting linked/reparsed sources or temporary paths. `rollback` reads journal-bound backup paths and writes predictable rollback temporary paths without an immediate no-link/reparse check.
- Promotion also resolves the destination before `_transition` writes/flushed journal state and invokes the failure injector, then calls `_ATOMIC_DESTINATION_REPLACE` without re-resolving. Rollback resolves a destination before the `rollback-replace`/`rollback-remove` injector and mutates afterward. A parent substitution in those gaps is not rejected at the actual replace/unlink boundary.
- Existing tests mark paths unsafe before `_mutation_destination` runs or mock the resolver itself (`test_mutation_boundary_rejects_link_substitution_before_promotion`, `test_rollback_revalidates_link_substitution_before_destination_mutation`, `test_recovery_inspection_resolves_mutation_boundary_immediately_before_read`, `test_cleanup_revalidates_evidence_tree_immediately_before_deletion`). They do not substitute a stage, backup, temporary, or destination ancestor after resolution and before the concrete read/write/replace/unlink. The supplied RED-to-GREEN recovery-inspection test proves resolver routing, but not the remaining check/use gaps.

#### IMPORTANT-01: CLOSED

- `brownfield_manifest.py` includes `bootstrap.py`, `brownfield_compat.py`, `brownfield_manifest.py`, and `host_readiness.py` in the executable bundle.
- `brownfield_compat.py::_managed_candidate_hashes` now hashes every candidate except the self-referential receipt, removing the prior four-module exclusion. The resulting hashes are consumed by staged and final managed-integrity readiness checks.
- `test_brownfield_cli.py::test_adoption_receipt_manages_every_installed_executable_module` covers the four formerly omitted modules.

#### IMPORTANT-02: CLOSED

- `brownfield_compat.py::_execute_transaction` reads the validated repository HEAD and compares it with the approved identity HEAD immediately before preflight and again after staging/backup immediately before promotion.
- `test_brownfield_cli.py::test_apply_rejects_head_drift_before_preflight` and `test_apply_rejects_head_drift_immediately_before_first_promotion` prove neither protected boundary is entered on drift.

#### IMPORTANT-03: CLOSED

- `brownfield_inventory.py::safe_relative_path` rejects linked/reparsed roots, ancestors, and final descendants and enforces lexical and resolved containment.
- Reviewed constitution files, host identity, baseline manifest, baseline snapshots, refresh inputs, and baseline-adoption inputs now use that primitive (`brownfield_compat.py::_reviewed_inputs`, `_reviewed_constitution`; `brownfield_proposal.py::_read_snapshot`, `load_and_validate_baseline`, `plan_refresh`, `plan_baseline_adoption`).
- `test_brownfield_proposal.py::test_load_and_validate_baseline_rejects_linked_snapshot_outside_proposal` and the Windows/POSIX link/junction/reparse scenario matrix exercise the controlling primitive.

#### IMPORTANT-04: CLOSED

- `host_readiness.py::run_quality_checks` refuses `network_policy=deny` before process launch because this executor cannot enforce network isolation. Execution is permitted only for the explicit `allow-confirmed` value, and disclosure now accurately states that network and external side effects are outside rollback.
- Identity validation accepts only `deny` or `allow-confirmed`, and the quality-command field still requires human confirmation.
- `test_host_readiness.py::test_deny_policy_refuses_before_launch_when_enforcing_executor_is_unavailable` proves deny fails closed before launch; stale readiness tests now use explicit `allow-confirmed` for executable commands.

#### IMPORTANT-05: CLOSED

- `brownfield_identity.py::_validate_quality_commands` rejects secret expansions, assignment forms, exact credential flags followed by values, and inline credential flags before an executable identity is created.
- `host_readiness.py::run_quality_checks` never discloses raw argv and redacts credential forms in stdout, stderr, and exception evidence.
- `test_brownfield_identity.py::test_quality_commands_reject_credential_flag_value_pairs_without_disclosure` and `test_host_readiness.py::test_quality_evidence_redacts_argv_output_and_exception_canaries` cover flag/value, inline, output, and exception canaries without persisting them in evidence.

#### IMPORTANT-06: CLOSED

- `host_readiness.py::_check_gitignore` accepts only documented return codes `0` and `1`; every other code fails closed without exposing Git diagnostics.
- `test_host_readiness.py::test_gitignore_unexpected_return_code_fails_closed_and_redacts_diagnostics` covers return code `128` and a credential canary.

#### IMPORTANT-07: OPEN

- The executor now starts a POSIX session or Windows process group and, on timeout, calls `os.killpg(..., SIGKILL)` or `taskkill /T /F` before returning. This is a meaningful improvement over direct-process `subprocess.run(timeout=...)`.
- The Windows implementation does not use a Job Object or verify `taskkill` success, so it does not provide a durable containment boundary if the direct parent exits/reparents descendants or `taskkill` fails. POSIX containment is likewise limited to descendants that remain in the created process group.
- `test_host_readiness.py::test_quality_timeout_executor_terminates_descendant_boundary_before_return` uses a fake process and mocks `_terminate_process_tree`; it proves control flow only. No test launches a real child process, times out the parent, and verifies the descendant is gone on Windows and POSIX, which was an explicit IMPORTANT-07 closure condition.

### New Findings

- No new CRITICAL or IMPORTANT finding is raised independently of the still-open scope above.
- **SUGGESTION-03:** strengthen IMPORTANT-01 regression coverage by asserting, in the canonical fixture apply test, that each installed executable's on-disk SHA-256 equals its final on-disk receipt entry. The current focused test proves helper behavior, while the broader apply/readiness path proves integration indirectly.
- The two historical suggestions remain non-blocking and were not repaired by this diff: require a validated candidate-bundle type at materialization boundaries, and pin GitHub Actions plus pytest dependencies immutably.

### Validation Evidence Reviewed

- Transaction/readiness: `106 passed in 196.35s`
- Cross-platform: `26 passed in 68.25s`
- Focused workflow: `424 passed, 1 skipped in 474.94s`
- Workflow contracts: `11 passed, 2 subtests passed`
- Full repository: `1092 passed, 3 skipped, 6 subtests passed in 626.11s`
- Schema, origin, stale-document, and governance checks: clean
- Article X: `3 passed`
- `git diff --check`: clean
- TDD gate: PASS
- DONE gate: PASS
- Strict local doctor: still running; no result is claimed in this review

### Gate Implications

T-058-022 remains **blocked** and V-61 remains unchecked because CRITICAL-01, CRITICAL-03, and IMPORTANT-07 remain open. The repair is not Stage-2 approved.

This re-review does not mark or imply owner approval, push authorization, public Windows/POSIX CI, V-54, V-62, feature DONE, Sprint 24 close, or executive-surface regeneration. Those states remain outside this review and unauthorized.

---

## Independent Re-review After Additional Repairs (2026-07-27)

- Reviewer: Principal Cloud Security Architect reviewer B (independent; did not implement the repair)
- Base Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed state: current 15-file dirty package on `feature/f7.5-sdd-058-stage-2-security`
- Scope: security re-review of CRITICAL-01, CRITICAL-03, and IMPORTANT-07 only
- Verdict: **CHANGES REQUIRED**

This section supersedes the disposition of those three findings in the earlier 2026-07-27 re-review. The additional repair closes the missing public-entry evidence for CRITICAL-01 and materially narrows CRITICAL-03 and IMPORTANT-07, but it does not close every required containment boundary.

### Findings

#### CRITICAL-03: OPEN

- The repaired stage reset/create/read, backup root/destination/proposal, promotion staged/temporary/destination, and rollback backup/temporary/destination tests are real deterministic RED/GREEN checks. The implementation now repeats link/reparse and containment checks immediately before the tested `rmtree`, `mkdir`, source copy, atomic replace, rollback replace, and rollback unlink boundaries.
- Trusted-root identity is still not established. `_trusted_existing_path` recomputes containment against whichever ordinary directory currently occupies `root`; it does not compare a retained file identity, device/inode, Windows file ID, or open root handle. Renaming the validated root and replacing it with another non-link directory therefore passes the helper. The original CRITICAL-03 repair condition explicitly required trusted-root identity, not only rejection of links/reparse points.
- Concrete active-transaction boundaries remain outside immediate revalidation. `_write_journal` calls `_proposal_record`, reads proposal and backup descendants, creates the journal parent, writes the temporary journal, and replaces the journal without the trusted-path helper. Promotion exception cleanup calls `temporary.exists()` and `temporary.unlink()` without revalidating the temporary path. Rollback changes temporary and destination modes after copy/replace without revalidating those paths. Cleanup flushes the workspace after deletion without revalidating the workspace.
- The new substitution tests exercise link/reparse rejection at selected injected boundaries. They do not test ordinary-directory trusted-root replacement or the unguarded journal, promotion-cleanup, post-replace mode, and final workspace-flush boundaries above. The remaining gaps preserve a local check/use path-redirection risk, so this critical finding cannot close.

#### IMPORTANT-07: OPEN

- The new real parent-spawns-child test is valid evidence for the ordinary descendant case on the executing platform, and the Windows error path now fails closed when `taskkill /T /F` returns nonzero.
- The executor still treats a zero `taskkill` return code as proof that the tree is gone; production code does not enumerate or verify descendant termination before returning timeout status. The test performs that verification externally for one cooperative child only.
- `CREATE_NEW_PROCESS_GROUP` is not a Windows Job Object and does not prevent a descendant from escaping or being reparented before `taskkill` traverses the tree. On POSIX, `start_new_session` plus `killpg` does not contain a descendant that creates a new session/process group. The original repair condition required a contained process group/job and verified cleanup. Those cross-platform containment guarantees are not yet implemented.

#### CRITICAL-01: CLOSED

- `brownfield_compat.execute` now has real parameterized `recover` and `cleanup` adversarial coverage. Each action creates a genuine fixture transaction, obtains live valid fixture authorization through the canonical entry point, tampers the journal-selected target to a foreign directory, and proves exit code `3` / `recovery-required`, retained journal evidence, unchanged host receipt bytes, and unchanged foreign protected bytes.
- The canonical test complements the direct engine tests for strict journal schema, authorization binding, malformed nested records, forged authorization, and cleanup rejection. This satisfies the previously missing public-boundary closure condition without replacing the transaction engine with mocks.

### Independent Focused Validation

The exact public recovery/cleanup, five deterministic mutation-boundary, real descendant-timeout, and Windows `taskkill` failure tests completed with `9 passed in 119.32s`. This re-review also accepts the recorded repair-package evidence of transaction `93 passed`, public adversarial `2 passed`, timeout `3 passed`, prior full-repository `1092 passed`, and strict local doctor `All checks passed.` The separately running combined local regression is not claimed here.

### Gate Implications

T-058-022 **may not pass** and V-61 **may not be checked** because CRITICAL-03 and IMPORTANT-07 remain open. Stage 2 remains blocked and is not APPROVED.

This verdict does not claim owner approval, commit, push, public CI, V-54, V-62, feature DONE, Sprint 24 close, or executive-surface regeneration.

---

## Independent Principal Cloud Security Architect Re-review (2026-07-27)

- Reviewer: Principal Cloud Security Architect (fresh independent Stage-2 reviewer; did not implement these repairs)
- Reviewed branch: `feature/f7.5-sdd-058-stage-2-security`
- Reviewed Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed dirty state: 15 modified tracked files and no untracked files
- Modified files present at review start: `spec-driven-development/cli/brownfield_compat.py`, `spec-driven-development/cli/brownfield_identity.py`, `spec-driven-development/cli/brownfield_inventory.py`, `spec-driven-development/cli/brownfield_proposal.py`, `spec-driven-development/cli/brownfield_transaction.py`, `spec-driven-development/cli/host_readiness.py`, `spec-driven-development/cli/test_brownfield_cli.py`, `spec-driven-development/cli/test_brownfield_cross_platform.py`, `spec-driven-development/cli/test_brownfield_identity.py`, `spec-driven-development/cli/test_brownfield_proposal.py`, `spec-driven-development/cli/test_brownfield_transaction.py`, `spec-driven-development/cli/test_host_readiness.py`, `spec-driven-development/docs/1_1_STATUS_REPORT_SDD.md`, this review artifact, and `spec-driven-development/specs/2026-07-12-brownfield-bootstrap-correctness/validation.md`
- Scope: latest open CRITICAL-03 and IMPORTANT-07 dispositions, repository-root scope preservation, and new CRITICAL/IMPORTANT regressions introduced by the repair
- Verdict: **CHANGES REQUIRED**

This section supersedes the prior open disposition for CRITICAL-03 and IMPORTANT-07. CRITICAL-01 remains closed and was not reopened.

### Dispositions

#### CRITICAL-03: OPEN

- The repair now captures stable target and workspace filesystem identities in the live transaction context and journal, checks the target identity at mutation and recovery inspection boundaries, and checks the workspace identity throughout staging and journal writes. The two real ordinary-directory target-root replacement tests pass and demonstrate fail-closed promotion and restart recovery for that root.
- Stable identity is not retained for the created backup root. `TransactionContext` and `TransactionJournal` retain only `backup_parent_identity`; `_backup_path` consequently accepts whichever ordinary directory currently occupies the authorized backup path as long as its parent identity is unchanged. Rollback can read substituted backup descendants before detecting a post-mutation hash mismatch.
- Restart trust for the workspace is not independently anchored. `_validated_journal` accepts `workspace_identity` from the mutable journal stored inside that workspace, and authorization does not bind the workspace identity. A replaced ordinary workspace can therefore present its own identity in a copied journal.
- Cleanup does not recheck retained workspace or backup-root identity immediately before deletion. `_evidence_deletion_path` provides lexical/resolved containment and link/reparse rejection only. A real disposable probe renamed the trusted backup root, created an ordinary replacement containing `protected.txt`, then called canonical cleanup with valid live authorization. Cleanup returned exit code `0`, deleted the replacement root and protected file, and left the renamed original backup intact. This is direct behavioral evidence that ordinary-directory backup-root substitution still crosses the cleanup mutation boundary.
- Required repair: retain and externally bind the created backup-root identity; bind restart workspace identity to authorization or another immutable capability outside the mutable workspace journal; require those identities immediately before rollback reads/mutations and every cleanup `rmtree`/`unlink`/final flush; and add real ordinary-directory replacement tests for backup and workspace roots across rollback, inspection, and cleanup.

#### IMPORTANT-07: OPEN

- Windows now uses a genuine Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. A paused broker is assigned before user code starts, timeout and normal completion terminate the Job Object, and active-process accounting verifies the contained boundary is empty. The live Windows Job Object and real parent-spawns-child timeout tests pass.
- Containment-unavailable and unverifiable-termination paths fail closed, and unsupported non-Windows/non-Linux platforms select the Linux boundary which rejects the platform before `Popen`; user code therefore does not launch on those paths.
- Linux creates a child cgroup v2 beneath the caller's delegated cgroup and moves the paused broker into it, but it does not prevent same-identity user code from writing itself back to the delegated parent `cgroup.procs`. Because the implementation must have delegation sufficient to create the child, the user command can potentially migrate outside the boundary that `cgroup.kill` and `_pids()` later terminate and verify. The Linux contract test proves cgroup creation/assignment or fail-before-launch, but it does not attempt parent migration or prove non-escape. It was skipped in this Windows review.
- Required repair: make the Linux containment boundary non-migratable by the admitted user process, or use a privileged supervisor/system boundary that user code cannot write out of; then add live timeout and normal-completion tests in which a descendant attempts cgroup escape and is still terminated and verified. Continue to fail before user code when that boundary is unavailable.

#### Repository-root scope: PRESERVED

- All canonical brownfield entry paths continue to call `validate_repository_root`, which requires Git's `--show-toplevel` result to equal the supplied target and requires a committed HEAD. Nested project targets remain rejected; no monorepo support was introduced.
- The real exact-root test was included in the independent validation below and passed.

### New Findings

No separate new CRITICAL or IMPORTANT finding was identified outside the residual CRITICAL-03 backup/workspace identity defect and IMPORTANT-07 Linux containment escape described above.

### Independent Validation Evidence

- Exact combined command: `.venv\Scripts\python.exe -m pytest spec-driven-development/cli/test_brownfield_transaction.py spec-driven-development/cli/test_host_readiness.py::test_quality_command_fails_before_launch_when_containment_is_unavailable spec-driven-development/cli/test_host_readiness.py::test_quality_command_propagates_unverifiable_boundary_termination spec-driven-development/cli/test_host_readiness.py::test_quality_timeout_terminates_real_descendant_process_before_return spec-driven-development/cli/test_host_readiness.py::test_windows_quality_process_uses_genuine_job_object_containment spec-driven-development/cli/test_host_readiness.py::test_linux_quality_process_uses_cgroup_v2_or_fails_before_user_command spec-driven-development/cli/test_brownfield_inventory.py::test_validate_repository_root_requires_exact_committed_root -q --tb=short`
- Observed result: `101 passed, 1 skipped in 221.52s (0:03:41)`. The skipped case was the Linux-only cgroup contract on Windows.
- Disposable backup-root substitution probe: cleanup exit code `0`; cleanup success `True`; replacement backup root absent; protected replacement file absent; renamed original backup present. The probe used `TemporaryDirectory` and did not modify repository files.
- The main agent's separately reported `6 passed, 1 skipped in 16.65s` is not counted as this reviewer's independent result.

### Overall Stage-2 Verdict and Blocker

Stage 2 remains **CHANGES REQUIRED**. CRITICAL-03 and IMPORTANT-07 are open, so T-058-022 may not pass and V-61 may not be checked.

The exact blocking owner/action is the Principal Software Developer: retain and independently bind backup/workspace root identities through restart and cleanup, and provide a Linux cgroup boundary that admitted user code cannot migrate out of, with the behavioral tests specified above. This is an implementation blocker, not a new Level-2 human decision.

This verdict authorizes only repair work and another independent Stage-2 re-review. It does not authorize owner approval, commit, push, public CI, V-54, V-61, V-62, SDD-058 DONE, Sprint 24 close, or executive-surface regeneration.

---

## Fresh Independent Cloud-Security Re-review (2026-07-27)

- Reviewer: Principal Cloud Security Architect (fresh independent Stage-2 reviewer; did not implement these repairs)
- Reviewed Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed state: current dirty working tree on `feature/f7.5-sdd-058-stage-2-security`
- Scope: CRITICAL-03, IMPORTANT-07, exact repository-root enforcement, behavioral closure tests, owner-receipt schema v3, restart authorization binding, and new CRITICAL/IMPORTANT regressions
- Verdict: **CHANGES REQUIRED**

This section supersedes the immediately preceding CRITICAL-03 and IMPORTANT-07 dispositions. CRITICAL-03 remains open for one destructive cleanup boundary. IMPORTANT-07 is closed by the revised Windows-only containment contract, but a separate cross-platform test regression is newly IMPORTANT.

### Dispositions

#### CRITICAL-03: OPEN

- Stable identities now cover the target, workspace, and created backup root. `ApplyAuthorization` externally binds `target_identity`, `workspace_location`, `workspace_identity`, `backup_location`, and `backup_root_identity`; strict owner-receipt schema v3 loading registers the exact live authorization capability. Restart validation compares journal identities with live filesystem identities and then compares workspace and backup identities with the separately loaded authorization, so a copied journal cannot self-authorize a replaced workspace.
- Target, workspace, stage, backup, promotion, rollback, recovery inspection, journal-write, and final workspace-flush paths now repeatedly enforce ordinary-directory identity plus link/junction/reparse rejection. The ordinary target replacement, copied-journal workspace replacement, and pre-operation mutation tests are behavioral and passed independently.
- Cleanup still separates the backup-root identity check from the destructive boundary. In `brownfield_transaction.cleanup`, `_require_filesystem_identity(backup, authorization.backup_root_identity)` runs before `_evidence_deletion_path(workspace, path)`, and `shutil.rmtree(...)` runs after both. `_evidence_deletion_path` checks containment and links/reparse points but does not recheck the authorized backup-root identity. An ordinary directory can therefore replace the authorized backup root after the identity check but before `rmtree`; the replacement is not a link/reparse point and remains deletion-eligible.
- The existing ordinary-directory cleanup test replaces the backup root before cleanup starts, so `_validated_journal` rejects it. The immediate-deletion test mocks `_evidence_deletion_path` to raise and never performs an ordinary-directory swap after the identity check. Neither test exercises the residual check/use boundary.
- Required closure: make the authorization-bound backup identity part of the deletion resolver used immediately at each destructive call, revalidate it after any injectable/path-resolution boundary and directly before `rmtree`, and add a deterministic ordinary-directory swap test at that exact boundary proving the replacement and protected bytes survive while journal/lock evidence is retained. Apply the same combined identity/path primitive to cleanup unlink and final-flush boundaries where the workspace root is authoritative.

#### IMPORTANT-07: CLOSED

- Windows uses a genuine Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. A paused broker is assigned before the user argv is released, and timeout and normal completion terminate the Job Object and verify zero active processes before returning.
- `_spawn_contained_process` rejects every non-Windows platform before `subprocess.Popen`; the removed Linux cgroup implementation is not represented as supported containment. This is the required fail-closed contract.
- The real descendant timeout test and genuine Windows Job Object test passed independently. The dedicated non-Windows test monkeypatches `os.name` to `posix`, installs a `Popen` canary, and proves refusal before launch, so its security assertion is behavioral rather than prose-only.

#### Repository-root scope: PRESERVED

- `validate_repository_root` still requires a non-linked directory whose `git rev-parse --show-toplevel` result exactly equals the supplied target and whose `HEAD^{commit}` exists.
- Canonical brownfield entry paths continue to invoke this validator. Nested targets remain rejected and no monorepo support was introduced. The exact-root Node and Python parameterizations passed independently.

#### Owner-receipt schema v3 and restart binding: ACCEPTABLE

- `load_owner_authorization` accepts only the exact schema-v3 key set and deserializes target, workspace, and backup-root identities into a registered live capability.
- Preflight requires the authorization-bound workspace location and all three live identities. `_validate_journal_authorization` binds restart journal fields back to that authorization rather than trusting journal identities alone.
- The exact authorization contract, positive schema-v3 owner receipt, and copied-journal replaced-workspace rejection passed independently.

### New Findings

#### IMPORTANT-08: Removed Linux containment leaves a Linux-only test with a stale symbol

- `test_quality_command_fails_before_launch_when_containment_is_unavailable` selects `_LinuxCgroupV2` whenever `os.name != "nt"`, but production no longer defines that symbol. On Linux, `monkeypatch.setattr` therefore raises `AttributeError` before `_execute_quality_command` and before the `Popen` canary assertion.
- This does not reopen IMPORTANT-07 because the dedicated non-Windows no-`Popen` test covers the production contract. It is nevertheless an IMPORTANT cross-platform regression: the host-readiness suite cannot pass on Linux and the named containment-unavailable test does not test its claimed behavior there.
- Required closure: remove the stale `_LinuxCgroupV2` branch. Keep the Job Object construction-failure test Windows-only, and use the existing non-Windows refusal test for all unsupported platforms. Run the host-readiness suite on Linux to prove no user-code launch and no stale containment assumptions.

No other new CRITICAL or IMPORTANT finding was identified in the reviewed scope.

### Independent Evidence Reviewed and Run

- Reviewed the current dirty diff and controlling code in `brownfield_transaction.py`, `brownfield_compat.py`, `brownfield_inventory.py`, `host_readiness.py`, and their focused tests. Prior review prose was used only as history, not as implementation evidence.
- Focused closure selection: `8 passed in 10.89s`. It covered backup-root replacement cleanup, copied-journal workspace replacement, backup creation-boundary revalidation, non-Windows no-`Popen` refusal, genuine Windows Job Object containment, real descendant timeout cleanup, and both exact-root fixture parameterizations.
- Receipt and mutation-boundary selection: `7 passed in 11.98s`. It covered the exact authorization/journal contract, schema-v3 owner receipt, promotion replace revalidation, rollback replace/unlink revalidation, cleanup path-boundary rejection, and containment-unavailable refusal on this Windows host.
- `git diff --check`: clean during this review.
- The active full repository pytest run was not duplicated. Main-agent validation totals are not claimed as independent execution evidence.

### Gate Implications

Stage 2 remains **CHANGES REQUIRED**. CRITICAL-03 and IMPORTANT-08 block approval, so T-058-022 is not security-eligible and V-61 must remain unchecked.

The Principal Software Developer must close the cleanup identity/deletion boundary and remove the stale Linux containment test assumption, then route the repaired dirty tree to another independent Stage-2 cloud-security review.

This verdict does not claim or authorize owner approval, commit, push, public CI, feature DONE, Sprint 24 close, or executive regeneration.

---

## Superseding Fresh Independent Cloud-Security Re-review (2026-07-27)

- Reviewer: Principal Cloud Security Architect (new independent Stage-2 reviewer; did not implement the repair)
- Reviewed Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed state: current dirty working tree on `feature/f7.5-sdd-058-stage-2-security`; all pre-existing dirty changes preserved
- Scope: CRITICAL-03, IMPORTANT-07, IMPORTANT-08, owner-receipt schema v3 and restart binding, exact repository-root scope, and regressions introduced by the latest cleanup/helper changes
- Verdict: **APPROVED**

This section supersedes the immediately preceding `Fresh Independent Cloud-Security Re-review (2026-07-27)`. The current repair closes CRITICAL-03 and IMPORTANT-08 without reopening IMPORTANT-07.

### Dispositions

#### CRITICAL-03: CLOSED

- Stable external authorization binds the target, workspace location and identity, and backup-root location and identity. Strict journal validation independently checks the live target, workspace, backup parent, and backup root before restart operations, then `_validate_journal_authorization` binds journal fields back to the registered authorization capability.
- Cleanup now uses `_authorized_evidence_path`, which first resolves and validates the evidence path and then revalidates the authoritative root identity. Backup deletion passes the authorization-bound backup-root identity; stage deletion, journal and lock unlink, and final workspace `fsync` pass the authorization-bound workspace identity.
- The identity check occurs after evidence-path resolution and in the argument expression immediately before each `shutil.rmtree`, `unlink`, or final `fsync_directory` call. No injector, callback, or other application operation remains between the combined helper and the destructive call.
- `test_cleanup_rejects_backup_root_replacement_at_deletion_boundary` deterministically replaces the authorized backup root with an ordinary directory from inside the evidence-resolution boundary. Cleanup raises on the stale filesystem identity; the replacement's protected bytes survive, the renamed original backup remains, and the journal remains available. This directly covers the previously demonstrated deletion check/use failure.
- The changed cleanup path has no equivalent remaining destructive check/use gap: stage content is constrained beneath the still-authorized workspace root, while every externally bound root used by cleanup is revalidated at its concrete deletion, unlink, or flush boundary. Link, junction, reparse, lexical-escape, and resolved-escape checks remain in the same path-resolution chain.

#### IMPORTANT-07: CLOSED

- Windows uses a genuine Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. The broker is assigned before user argv is released; termination verifies the Job Object has zero active processes and fails closed when assignment, termination, or verification cannot be established.
- `_spawn_contained_process` rejects every non-Windows platform before `subprocess.Popen`, so unsupported platforms cannot launch the broker or user command. Linux cgroup containment has been removed and is not represented as supported.
- The Windows construction-failure test is Windows-only. On this Windows review host, both genuine Job Object containment and real descendant timeout cleanup executed and passed; the source-level non-Windows `Popen` canary also passed.

#### IMPORTANT-08: CLOSED

- No `_LinuxCgroupV2` or cgroup reference remains in the CLI production or test Python sources.
- The Job Object construction-failure test skips outside Windows. The dedicated non-Windows contract asserts `ContainmentUnavailableError` before `Popen`, and the Linux-only contract asserts refusal before the marker-writing user command.
- Linux collection is viable from source inspection: platform-specific `ctypes`/Win32 imports occur only inside `_WindowsJobObject.__init__`, the Windows behavioral test is guarded with `skipif`, and the Linux refusal test calls the platform-neutral fail-before-launch branch. Actual Linux execution and public Linux CI are not claimed.

#### Owner-receipt schema v3 and restart binding: PRESERVED

- `load_owner_authorization` accepts only the exact schema-v3 key set and binds target fingerprint/identity, workspace location/identity, target HEAD, preview hash, backup location/root identity, recovery command, approver, and approval time into a registered live capability.
- Preflight checks those live identities and reviewed values. Restart journal validation cannot self-authorize a copied workspace because journal workspace and backup identities must match the separately loaded registered authorization.
- The exact public authorization contract, positive schema-v3 owner receipt, and copied-journal replaced-workspace rejection passed in the independent focused run.

#### Repository-root scope: PRESERVED

- `validate_repository_root` still requires a non-linked exact Git top-level directory and a committed `HEAD^{commit}`. Subdirectories, `.git`, the disposable parent, and the bare remote fixture remain invalid targets.
- Canonical entry paths retain exact-root enforcement. Nested targets and monorepo subproject targeting remain unsupported; no monorepo support was introduced. Both Node and Python exact-root parameterizations passed independently.

### New Findings

No new CRITICAL or IMPORTANT regression was identified in the latest helper or cleanup changes.

Residual risk is limited to the unavoidable local filesystem scheduling interval between a final path-based identity check and the immediately following OS call. There is no application-controlled yield in that interval, and the deterministic replacement boundary that previously deleted substituted bytes now fails closed. Handle-relative deletion would further reduce this residual risk but is not required to close the demonstrated finding.

### Independent Evidence Reviewed and Run

- Independently reviewed the current dirty diff and controlling implementations/tests in `brownfield_transaction.py`, `host_readiness.py`, `brownfield_inventory.py`, `test_brownfield_transaction.py`, `test_host_readiness.py`, and `test_brownfield_inventory.py`.
- Focused security selection: `13 passed, 1 skipped in 38.48s`. It covered cleanup path revalidation, pre-existing backup substitution, exact deletion-boundary ordinary-directory substitution, copied-journal workspace replacement, authorization/journal field contracts, positive schema-v3 authorization, Windows construction failure, non-Windows no-`Popen` refusal, unverifiable termination propagation, real descendant timeout cleanup, genuine Windows Job Object containment, Linux fail-before-user-command collection contract, and both exact-root fixture parameterizations. The one skip was the Linux-only behavioral test on Windows.
- Source search found no stale `_LinuxCgroupV2` or cgroup reference in the CLI Python surface.
- `git diff --check` passed independently before this appended review section.
- The main agent's recorded transaction, host-readiness, workflow, workflow-contract, cross-platform, full-repository, doctor, and diagnostics totals are acknowledged as package evidence only; they were not rerun or represented as this reviewer's independent execution.

### Gate Implications

Stage 2 is **APPROVED**. T-058-022 and V-61 are **security-eligible only**.

This review does not modify `tasks.md` or `validation.md` and does not claim owner approval, commit, push, public Linux or Windows CI, V-54, V-62, feature DONE, Sprint close, or executive regeneration.

---

## Final Authorization-Registry Re-review (2026-07-28)

- Reviewer: Principal Cloud Security Architect (independent; did not implement the repair)
- Reviewed Git HEAD: `7c6ebd2e9362832f9afbedc28d489fe14601e6e5`
- Reviewed state: current dirty working tree on `feature/f7.5-sdd-058-stage-2-security`
- Scope: owner and fixture capability lifetime, identity reuse, weak-reference behavior, authorization binding, current thread/process model, test isolation, and canonical transaction regressions
- Verdict: **APPROVED**

This section supersedes only the authorization-registry blocker discovered after the 2026-07-27 approval. All earlier findings and dispositions remain preserved as history.

### Disposition

- The original fixture registry stored raw object IDs after capability death. Allocator identity reuse could therefore make an equal but unregistered replacement appear registered. `_LiveCapabilityRegistry` now stores weak values behind opaque UUID keys and accepts only the exact live object by `is` comparison.
- The first targeted re-review found the same stale-ID/value defect in owner-receipt registration. A new owner lifetime test reproduced the defect as RED: `Failed: DID NOT RAISE AuthorizationError`. Owner receipts now use a separate `_LiveCapabilityRegistry`; the same test is GREEN and proves the loaded capability is collectible while an equal replacement remains unauthorized under forced stale-ID conditions.
- Separate owner and fixture registries prevent cross-kind confusion. Owner schema-v3 parsing remains exact, and preflight plus journal validation still bind target fingerprint and identity, workspace location and identity, HEAD, preview hash, backup location and identity, recovery command, approver, and approval time to the exact live capability.
- The current CLI is single-threaded and single-process. Unsynchronized process-local registries and post-fork inheritance are residual future concerns, not current blocking defects. Transaction-map retention can extend fixture-capability lifetime but cannot authorize equal replacements or reused addresses.
- No security check was weakened and no new CRITICAL or IMPORTANT finding remains. Suggestions are limited to revoking completed transaction-map entries and adding synchronization/post-fork policy if the architecture later introduces concurrency.

### Evidence

- Owner lifetime RED: `1 failed in 45.82s`; expected `AuthorizationError` was not raised.
- Owner lifetime GREEN: `1 passed in 1.79s`.
- Complete transaction module: `100 passed in 272.13s (0:04:32)`.
- Exact nine-module SDD-058 workflow: `443 passed, 2 skipped in 771.20s (0:12:51)`.
- Full repository: `1111 passed, 4 skipped, 6 subtests passed in 1085.72s (0:18:05)`.
- Strict local doctor: all checks passed; internal tests `1111 passed, 4 skipped, 6 subtests passed in 1113.30s (0:18:33)`; PI-9 ledger `21` rows; TDD and DONE completeness PASS.
- Article X FootprintLockGuard: `3 passed, 286 deselected in 0.21s`.
- `git diff --check`: clean before this evidence append; rerun is required on the final evidence bytes.
- The reviewer independently inspected the current source and tests but did not duplicate executable validation while doctor was active.

### Gate Implications

Stage 2 is **APPROVED** for the repaired exact dirty package. T-058-022 and V-61 remain satisfied. Owner approval and V-62 are still open; no commit, push, public Windows/POSIX CI, feature DONE, Sprint close, PI close, or executive regeneration is claimed.