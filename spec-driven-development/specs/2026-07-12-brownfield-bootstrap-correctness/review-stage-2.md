---
id: SDD-20260712BROWNFIELD-review-stage-2
type: validation
status: blocked
owner: principal-cloud-security-architect
updated: 2026-07-20
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