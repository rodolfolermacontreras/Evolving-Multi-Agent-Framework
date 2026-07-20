---
id: SDD-20260712BROWNFIELD-review-stage-1
type: validation
status: done
owner: qa-engineer-general
updated: 2026-07-20
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# Stage-1 Review: SDD-058 Brownfield bootstrap correctness

- Review date: 2026-07-20
- Reviewer: QA Engineer reviewer A (no implementation)
- Initial verdict: **NOT COMPLIANT**
- Re-review verdict: **COMPLIANT** at 2026-07-20 08:24:24 -07:00

---

## Findings

### WRONG-01: Required runtime modules remain preserved and unmanaged

- Requirement mapping: R-006, R-009; AC-03.
- Evidence mapping: V-10, V-11, V-12, V-28, V-30, V-34, V-35.
- Evidence: The five required SDD-058 runtime modules remain in `_PARALLEL_PENDING`, so the candidate manifest represents them as `preserve`/unmanaged rather than installable `copy` entries. A candidate installation therefore omits required implementation modules instead of installing the accepted runtime surface.
- Required correction: return to T-058-008 and move all five required runtime modules into the candidate installation as deterministic `copy` entries.

### WRONG-02: Approved preview does not bind the adoption receipt mutation

- Requirement mapping: R-018, R-019, R-020, R-044; AC-06, AC-15.
- Evidence mapping: V-23, V-26, V-27, V-65.
- Evidence: `brownfield_compat._apply` computes and approves the preview before `receipt_artifacts` is created. `brownfield_transaction.bind_commit_artifacts` then adds `spec-driven-development/.adoption/receipt.json` as a promoted operation that was not part of the approved semantic preview. The approved preview hash therefore does not bind every applied path and candidate byte.
- Required correction: return to T-058-016/T-058-018 and include the deterministic receipt mutation in the exact approved preview, or use an equivalent design in which every promoted receipt path and byte is cryptographically bound before authorization.

### WRONG-03: Canonical quality execution suppresses the required disclosure

- Requirement mapping: R-028A; AC-08.
- Evidence mapping: V-38A.
- Evidence: `brownfield_compat._host_doctor` invokes `host_readiness.run_quality_checks` with `lambda _text: None`. This discards the required pre-execution disclosure of cwd, tokenized argv, timeout, environment policy, network policy, and the outside-rollback side-effect boundary.
- Required correction: return to T-058-014/T-058-018 and preserve and present the disclosure through the canonical `host-doctor --run-quality` result before executing each configured quality command.

## Classification Summary

- MISSING: none.
- EXTRA: none.
- WRONG: 3 unresolved findings.

## Initial Gate Result

T-058-021 remains blocked. Stage 1 may be marked PASS only after all three findings are corrected and independently re-reviewed; Stage 2 must not start before that PASS.

---

## Re-review -- 2026-07-20

- Exact reviewed commit: `9e743e4bd6d7baa16debcc25ee5cad487dcf9782`.
- Reviewer: QA Engineer reviewer A (independent; did not implement repairs).
- PASS timestamp: `2026-07-20 08:24:24 -07:00`.
- Final verdict: **COMPLIANT**.

### Finding dispositions

#### WRONG-01 -- CLOSED

All eight SDD-058 runtime modules, including the five previously pending modules,
are explicit managed `copy` entries in `brownfield-core@1`, with source paths and
SHA-256 hashes bound by the manifest. The exact Appendix A membership test and
the nine-file workflow suite pass. R-006, R-009, AC-03, and V-10/V-11/V-12/V-28/
V-30/V-34/V-35 are satisfied.

#### WRONG-02 -- CLOSED

The deterministic adoption receipt candidate is now built before preview
construction. Its destination and candidate hash appear in the approved preview,
the transaction journal operation set exactly matches every mutable preview item,
and post-preview commit-artifact injection is rejected. Receipt promotion failure
is covered by verified rollback with no readiness-success claim. R-018, R-019,
R-020, R-044, AC-06, AC-15, and V-23/V-26/V-27/V-65 are satisfied.

#### WRONG-03 -- CLOSED

Canonical `host-doctor --run-quality` now forwards the disclosure sink, retains
the pre-execution disclosure, and returns it before the bounded readiness summary.
The canonical disclosure test proves cwd, tokenized argv, timeout, environment
policy, network policy, and the outside-rollback side-effect boundary are present.
R-028A, AC-08, and V-38A are satisfied.

### Independent evidence

- Finding-specific command: six targeted manifest/CLI/transaction tests;
	result `6 passed in 152.95s`.
- Nine-file SDD-058 workflow suite: `386 passed in 422.81s`.
- Full repository suite: `1054 passed, 2 skipped, 6 subtests passed in 496.01s`;
	the authoritative `668 passed / 2 skipped / 6 subtests` floor did not decrease.
- Schema lint: `Schema lint clean`.
- Repair diff check: clean for
	`669c07cbd857e9cd23ed6e600f304c101233c498..9e743e4bd6d7baa16debcc25ee5cad487dcf9782`.
- Independent identifier count: 46 requirement IDs, 15 acceptance criteria, and
	70 validation IDs.
- History order: implementation `2a1d096`, initial Stage-1 review `669c07c`,
	repair `9e743e4`; no Stage-2 artifact or public/push evidence was claimed.

### Complete compliance classification

- MISSING: none across all 46 R IDs, 15 ACs, and 70 V IDs.
- EXTRA: none. The repair commit is limited to the three returned compliance
	defects and their focused regression tests.
- WRONG: none remaining.
- Future-gated evidence remains correctly open and is not implementation
	noncompliance: V-54 public POSIX/Windows CI, V-61 completed two-stage ordering,
	V-62 owner/push/public-CI package evidence, and later DONE/Sprint close gates.

## Final Gate Result

T-058-021 is **PASS / complete**. Stage 2 may begin after the timestamp above with
a different reviewer. This verdict does not authorize owner approval, push,
public CI claims, non-fixture host mutation, feature DONE, or Sprint 24 close.