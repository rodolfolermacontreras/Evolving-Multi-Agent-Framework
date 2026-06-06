---
id: SDD-PI-5-S1-plan
type: plan
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: symlink-portability
sprint: PI-5 / Sprint 1
spec: spec.md
validation: validation.md
---

# Plan: Brownfield Portability Bundle (SDD-016 + SDD-017)

- Date: 2026-06-06
- Author: Principal Software Developer (consolidated worker session)
- Phases: 5 (DOCS first, then TESTS, then IMPL, then HOST-INTEGRATION docs, then INTEGRATION)
- Pattern: Linear single-session implementation. No fleet split. Precedent: PI-4 Sprint 4 (F-02 same pattern).

---

## 1. Locked Decisions (from clarification-log + spec)

| # | Decision | Source |
|---|----------|--------|
| D1 | `host-link` is a new third subcommand on `bootstrap.py`, alongside `greenfield` and `brownfield`. | C1 / Spec |
| D2 | Dry-run is the default; `--apply` is required for any filesystem mutation. | C1 / Spec |
| D3 | Cross-platform link strategy: try `os.symlink` first; on OSError, fall back to `mklink /J` (junction) via `subprocess.run(["cmd", "/c", "mklink", "/J", ...])`. | C2 / Spec |
| D4 | Conflict handling: abort by default; `--backup` (timestamped) or `--force` (destructive) opt-in; mutually exclusive. | C3 / Spec |
| D5 | No host-context auto-detection; `--target` is always explicit. | C4 / Spec |
| D6 | Live link in v1; no version pinning. | C5 / Spec |
| D7 | New agent rostered as `kind: generic`, `role: dev-env-manager`. | C7 / Spec |
| D8 | New skill: `host-integration-symlink`, category `operational`. | C8 / Spec |
| D9 | Stdlib only. No PyYAML, no requests, nothing external. (Article V). | _SHARED_ONBOARDING |
| D10 | Test platform: any. Windows-specific code path is mocked via `unittest.mock.patch(os.symlink)`. | R5 |

These are immutable for this sprint. Loosening any requires an Article X
amendment.

---

## 2. Phases

### Phase 1 -- TASKS scaffold (T-01)
Produce `tasks.md` listing 9 tasks with file scopes and traceability to
R1..R7 + O1..O2.

### Phase 2 -- TESTS first (T-02)
Author `cli/test_bootstrap.py` with the seven failing tests for R1..R6 plus
the regression smoke test for greenfield/brownfield argparse. Confirm they
fail for the right reason.

### Phase 3 -- IMPLEMENT bootstrap.py extension (T-03 through T-05)
- T-03: add `host-link` subparser to `parse_args()`.
- T-04: add helpers (`resolve_framework_github`, `validate_host_link_target`,
  `install_link`, `handle_existing_github`, `format_dry_run_report`).
- T-05: add `run_host_link(args)` dispatcher; wire into `main()`.

After each task, run the targeted tests and full suite.

### Phase 4 -- Roster + agent + skill (T-06 through T-08)
- T-06: write `.github/agents/dev-env-manager-general.agent.md`.
- T-07: write `.github/skills/operational/host-integration-symlink/SKILL.md`.
- T-08: add roster rows to `roster/agents.json` and `roster/skills.json`.

After T-08, run `schema_lint.py` full scan.

### Phase 5 -- Docs + sprint close (T-09 through T-11)
- T-09: write `docs/HOST-INTEGRATION.md`.
- T-10: update `BACKLOG.md` rows for SDD-016 + SDD-017 to DONE with SHA.
- T-11: append F-05 + Sprint 5 close blocks; regenerate exec state.

---

## 3. Risks + Mitigations

| Risk | Mitigation |
|------|------------|
| Windows symlink fallback test cannot run on Linux/macOS CI | Mock both `os.symlink` (raises OSError) and `subprocess.run` (capture call args); assert `mklink /J` invocation pattern. Test runs on any platform. |
| `.github/` symlink in a host could be picked up by host git and committed | Document in HOST-INTEGRATION.md (host operator decides whether to commit the link). Tool does not modify host's `.gitignore`. |
| Existing `bootstrap.py` regression (greenfield/brownfield broken) | Phase 2 includes a smoke test that asserts both subparsers still parse and the existing `parse_args` accepts both. |
| Schema lint regression: new agent/skill files miss frontmatter | T-06 and T-07 each follow the documented template; T-08 lint is the gate. |
| `os.symlink` on Linux requires the target to exist as a directory | The framework's `.github/` always exists in the framework checkout; helper validates this before calling `os.symlink`. |

---

## 4. Definition of Done (mirrors validation.md)

All R1..R7 REQUIRED checked. O1..O2 treated as REQUIRED for this feature.
Full test suite >= 200 + new tests for R1..R6. Schema lint full scan exits 0.
Sprint 5 close block + state regeneration committed.

---

## 5. Out of scope (per spec section "Out of Scope")

- Auto-detection of host context (C4).
- Version pinning (C5).
- Per-subdirectory link granularity (C6 mitigation 2).
- New `/env` slash command (C9).
- Live demo against Day-to-Day Agent. The validation harness is `tmp_path`
  only in this sprint.

---

## 6. Worker dispatch

This is a linear single-session execution. No fleet split. The
Principal Software Developer (this session) authors all artifacts. The
`dev-env-manager-general` worker is HIRED in this sprint via the roster
row in T-08, but is not dispatched on a task yet -- its first dispatch
becomes one of the post-PI-5-Sprint-1 work items (likely the first
real-host demo in a follow-on session).

This is consistent with PI-4 Sprint 4's F-02 pattern: hire the role, prove
the skill exists, defer first dispatch to the natural follow-on context.
