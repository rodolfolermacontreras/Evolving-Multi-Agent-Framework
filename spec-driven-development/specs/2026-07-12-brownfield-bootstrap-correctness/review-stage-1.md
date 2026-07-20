---
id: SDD-20260712BROWNFIELD-review-stage-1
type: validation
status: blocked
owner: qa-engineer-general
updated: 2026-07-20
feature: 2026-07-12-brownfield-bootstrap-correctness
---

# Stage-1 Review: SDD-058 Brownfield bootstrap correctness

- Review date: 2026-07-20
- Reviewer: QA Engineer reviewer A (no implementation)
- Verdict: **NOT COMPLIANT**

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

## Gate Result

T-058-021 remains blocked. Stage 1 may be marked PASS only after all three findings are corrected and independently re-reviewed; Stage 2 must not start before that PASS.