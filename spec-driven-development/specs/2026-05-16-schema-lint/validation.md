# Validation Contract: schema_lint.py (SDD-006)

- Date: 2026-05-16
- Spec: `spec-driven-development/specs/2026-05-16-schema-lint/spec.md`

## Automated tests

- [x] `test_agent_missing_description_fails` -- proves AC2
- [x] `test_skill_missing_required_fields_fails` -- proves AC3
- [x] `test_prompt_missing_description_fails` -- proves AC4
- [x] `test_unquoted_version_fails` -- proves AC5
- [x] `test_skill_name_dir_mismatch_fails` -- proves AC6
- [x] `test_json_flag_emits_findings` -- proves AC7
- [x] `test_repo_root_flag` -- proves AC8
- [x] `test_exit_codes` -- proves AC9
- [x] `test_runtime_imports_are_stdlib_only` -- proves AC10
- [x] `test_real_repo_passes_clean_or_findings_documented` -- AC1 against the live repo

## Manual checks

- [x] `python spec-driven-development/cli/schema_lint.py --help` shows usage.
- [x] `python spec-driven-development/cli/schema_lint.py` against the live repo runs and surfaces any findings.

## Definition of done

All 10 automated tests pass. Real-repo scan ran (findings documented in RETRO if any).
