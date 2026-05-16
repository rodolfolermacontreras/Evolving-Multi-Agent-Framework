# Retro: QA CLI (SDD-004)

- Date: 2026-05-16
- Feature: `spec-driven-development/specs/2026-05-16-qa-cli/`
- Facilitator: Developer (dispatch retro-closure T-002)

---

## What worked

1. **Two-stage review directly maps to the constitution.** Article III requires spec compliance before code quality. Separating Stage 1 (validation.md checkbox parsing, AC cross-reference, task status check) from Stage 2 (mechanical code scans) made the constitutional requirement executable.
2. **Exit code 0/1 for COMPLIANT/NOT COMPLIANT integrates with CI and scripting.** A human or fleet coordinator can branch on the exit code without parsing output.
3. **Mechanical scans in Stage 2 are narrowly scoped by design.** Bare-except and debug-print detection handle the easy wins; human judgment handles the rest. This avoids false-positive noise from over-ambitious static analysis.
4. **validation.md checkbox parser is reusable.** The same parser could serve state_builder.py or any future tool that needs to read lifecycle progress.

## What did not work as smoothly

1. **Stage 1 depends on validation.md existing and being well-formed.** If a feature skips validation (e.g., a bug fix under the 3-file threshold), qa.py has nothing to parse. The tool should degrade gracefully for specs without validation artifacts.
2. **Stage 2 scans are minimal.** Only bare-except and debug-print are detected. Additional mechanical checks (unused imports, type-hint coverage) were deferred to avoid scope creep, but the gap is noticeable.
3. **AC cross-reference requires spec authors to use consistent requirement ID formats.** If an AC uses a different numbering convention, the cross-reference silently misses it. No warning is emitted for unmatched IDs.

## Framework change candidates filed

- LESSON candidate: qa.py should emit a clear warning (not a failure) when validation.md is absent, with guidance on whether the feature qualifies for the lightweight path.
- LESSON candidate: Define a minimal set of Stage 2 mechanical checks that every CLI module should pass, and document the extension point for project-specific scans.
- LESSON candidate: Standardize AC/requirement ID format in the spec template so cross-reference tools can rely on a single pattern.

## Honest assessment

QA CLI is the enforcement arm of Article III and it works well for the happy path: a feature with a properly formatted spec, validation.md, and tasks.md gets a meaningful compliance check. The weak spot is edge cases -- missing artifacts, inconsistent ID formats, or features that legitimately skip the full lifecycle. Hardening the tool for those cases is straightforward but was correctly deferred to keep the first implementation focused. The two-stage split is the right abstraction and should survive as the framework matures.
