# Validation Contract: Dashboard About Section and Data Freshness

LOCKED 2026-05-16 -- modifications require human approval

- Spec Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/spec.md`
- Plan Reference: `spec-driven-development/specs/2026-05-16-dashboard-about-and-freshness/plan.md`
- Author: Principal Software Developer
- Constitution Article: X (TDD + pre-implementation validation contract)

This file is the binding pre-implementation test specification. Per
Article X, every test listed here MUST be written BEFORE the corresponding
implementation code, and every required item MUST be PASS before the feature
is considered complete. Modifications to this document after the lock date
require explicit human approval recorded in a follow-up commit.

---

## Definitions

- "Test file" refers to `spec-driven-development/cli/test_state_builder.py`
  unless otherwise stated.
- "Workflow file" refers to `.github/workflows/deploy-dashboard.yml`.
- "Live URL" refers to
  `https://state-dashboard.politehill-ac7984d9.westus2.azurecontainerapps.io/`.
- "Canonical fixture" refers to a synthetic `exec/state.md` written into
  `tmp_path` with the following header (used in unit tests):

  ```
  # Executive State

  Generated date: 2026-05-16
  Current PI: PI-3 (Validation Surface)
  Active sprint: PI-3 Sprint A -- About + Freshness
  Active focus: Land OIDC auto-deploy and About block
  ```

---

## Required Tests (write FIRST, then implement)

### V-1 -- About block static paragraph present (proves AC #4 part a)

- Test name: `test_about_block_static_paragraph_present`
- File: test file
- Setup: build dashboard HTML via `build(...)` with the canonical fixture in `tmp_path`.
- Assertion: rendered HTML contains a string that names the project ("Evolving Multi-Agent Framework" or the canonical short name agreed in the implementation) AND contains the meta caveat phrase (the dashboard tracks the framework's own progress). The exact static paragraph text is the developer's choice within T-004; the test pins whatever string is shipped.
- Implementation note: the test asserts substring presence on a constant defined in `state_builder.py`; both the constant and the test land in the same commit.

### V-2 -- About block dynamic line reflects state.md header (proves AC #4 part b, AC #5)

- Test name: `test_about_block_dynamic_line_reflects_state_md`
- File: test file
- Setup: build dashboard HTML via `build(...)` with the canonical fixture.
- Assertion: rendered HTML contains a single line that includes ALL THREE values verbatim: `PI-3 (Validation Surface)`, `PI-3 Sprint A -- About + Freshness`, `Land OIDC auto-deploy and About block`.

### V-3 -- About block dynamic line tracks header changes (proves AC #5)

- Test name: `test_about_block_dynamic_line_tracks_header_changes`
- File: test file
- Setup: parametrized -- two fixtures with different `Current PI` / `Active sprint` / `Active focus` triples.
- Assertion: each rendered HTML contains its own triple verbatim and does NOT contain the other fixture's values.

### V-4 -- About block fallback when state.md header missing fields (negative test, proves AC #4 graceful degradation)

- Test name: `test_about_block_fallback_when_state_md_header_incomplete`
- File: test file
- Setup: fixture with `# Executive State` heading only (no `Current PI`/`Active sprint`/`Active focus` lines).
- Assertion: `build(...)` does NOT raise; rendered HTML contains the static paragraph; rendered HTML contains a fallback string (e.g., `current focus unavailable` or equivalent constant defined in `state_builder.py`) in place of the dynamic line; rendered HTML does NOT contain the literal substrings `None` or `KeyError`.

### V-5 -- About block ordering: above the fold (proves AC #4 "above the fold")

- Test name: `test_about_block_appears_before_main_layout`
- File: test file
- Setup: build dashboard HTML with the canonical fixture.
- Assertion: index of the About-block opening marker (e.g., a `<section id="about">` or equivalent stable selector chosen in T-004) is LESS THAN the index of the `<main class="layout-4zone">` substring. The test pins the structural ordering, not the exact selector name.

### V-6 -- Workflow declares OIDC-only auth (proves AC #2)

- Test name: `test_deploy_workflow_oidc_only`
- File: new -- `spec-driven-development/cli/test_deploy_workflow.py` (stdlib only; uses a minimal YAML parser written ad hoc OR uses `actionlint` invoked as a subprocess if available; the test file's docstring documents which path was chosen)
- Setup: read `.github/workflows/deploy-dashboard.yml` from repo root via a relative path resolved from the test file.
- Assertion: parsed workflow contains `permissions.id-token: write`. Assertion: parsed workflow does NOT contain any of the substrings `client-secret`, `client_secret`, `AZURE_CLIENT_SECRET`, `password:`, `ARM_CLIENT_SECRET`. Assertion: `azure/login` step references `client-id`, `tenant-id`, `subscription-id` (the three public identifiers per ADR-009) and contains NO `client-secret` parameter.

### V-7 -- Workflow triggers cover state.md path (proves AC #1 trigger correctness)

- Test name: `test_deploy_workflow_triggers_cover_state_md`
- File: same as V-6
- Setup: read workflow file.
- Assertion: workflow declares `on.workflow_dispatch` AND `on.push.branches` includes `master`. Assertion: if `on.push.paths` is declared (path filter), it MUST include each of: `spec-driven-development/exec/state.md`, `spec-driven-development/cli/state_builder.py`, `.github/workflows/deploy-dashboard.yml`, `Dockerfile`. (If `on.push.paths` is omitted -- i.e., trigger on every push -- the test passes; the path filter is an optimization, not a requirement.)

### V-8 -- Workflow YAML parses cleanly (smoke test)

- Test name: `test_deploy_workflow_yaml_parses`
- File: same as V-6
- Setup: read workflow file; pass through the chosen parser.
- Assertion: parse does not raise. Workflow has `name`, `on`, `jobs` top-level keys.

### V-9 -- Federated credential present in Entra (proves AC #7) -- HITL

- Procedure: human runs
  `az ad app federated-credential list --id <DEPLOY_APP_OBJECT_ID>` and pastes
  the resulting JSON into the EVIDENCE section below.
- Assertion: at least one entry exists whose `subject` is exactly
  `repo:rodolfolermacontreras/Evolving-Multi-Agent-Framework:ref:refs/heads/master`,
  whose `issuer` is `https://token.actions.githubusercontent.com`, and whose
  `audiences` contains `api://AzureADTokenExchange`.

### V-10 -- Workflow visible and enabled (proves AC #6) -- HITL

- Procedure: human runs `gh workflow list --repo rodolfolermacontreras/Evolving-Multi-Agent-Framework`
  after merge to master.
- Assertion: a row with name `deploy-dashboard` (or whatever `name:` is set in the workflow file) appears with state `active`.

### V-11 -- Live freshness probe (proves AC #1) -- HITL

- Procedure:
  1. Confirm V-9 and V-10 PASS.
  2. Confirm the live URL currently serves a previous build (note the existing `Generated date` value).
  3. Trigger a benign change to `spec-driven-development/exec/state.md` by running the documented state regeneration command.
  4. Record `T0` = `git push` completion timestamp (UTC, second precision).
  5. Poll the live URL once every 15 seconds with `curl -fsSL <live URL> | grep -F "<new Generated date or About dynamic line content>"`.
  6. Record `T1` = timestamp of the first poll where the new content is present.
  7. Compute `elapsed = T1 - T0`.
- Assertion: `elapsed <= 300 seconds`.
- Record both timestamps and `elapsed` in the EVIDENCE section.

### V-12 -- Cold-start posture preserved (proves AC #8) -- HITL

- Procedure: after V-11 completes, wait at least 10 minutes (allow any non-min replicas to drain), then issue a single `curl -w "%{time_total}\n" -o /dev/null -s <live URL>` request.
- Assertion: response is HTTP 200 AND `time_total` is no worse than the cold-start figure recorded in the SDD-007 `PROVISIONED.md` baseline (or, if no baseline figure exists, no worse than 3.0 seconds, which is the implicit ceiling from SDD-007's accepted cold-start posture).

### V-13 -- Existing test suite green (regression guard)

- Procedure: `python -m unittest discover spec-driven-development/cli` (or the project's documented test entry point).
- Assertion: zero failures, zero errors. Baseline test count MUST NOT decrease.

### V-14 -- Workflow failure notification path verified (proves AC #3)

- Procedure: human confirms in GitHub repo settings that "Actions: Send notifications for failed workflows on the default branch" is enabled (default for repo owner).
- Assertion: confirmation pasted into EVIDENCE section. No code change.

---

## DONE Criteria per Task

| Task | DONE when |
|------|-----------|
| T-001 (human one-shot: federated credential) | V-9 PASS with `az` output pasted as evidence |
| T-002 (preconditions verification) | V-9 PASS AND V-14 PASS AND repository Actions variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` confirmed present (one-line evidence: `gh variable list` or screenshot reference); deploy SP role-scope confirmed minimum per ADR-009 |
| T-003 (workflow file) | Workflow file committed; V-6, V-7, V-8 PASS on the feature branch |
| T-004 (About block + unit tests) | V-1, V-2, V-3, V-4, V-5 PASS on the feature branch; V-13 PASS (no regression) |
| T-005 (live latency probe) | V-10, V-11, V-12 PASS with timestamps recorded in EVIDENCE |
| Feature DONE | All V-1 through V-14 PASS; this validation contract has zero unchecked required items |

---

## Required Item Checklist

- [ ] V-1 PASS
- [ ] V-2 PASS
- [ ] V-3 PASS
- [ ] V-4 PASS
- [ ] V-5 PASS
- [ ] V-6 PASS
- [ ] V-7 PASS
- [ ] V-8 PASS
- [ ] V-9 PASS (HITL)
- [ ] V-10 PASS (HITL)
- [ ] V-11 PASS (HITL) -- headline AC
- [ ] V-12 PASS (HITL)
- [ ] V-13 PASS
- [ ] V-14 PASS (HITL)

---

## EVIDENCE

(Populated during execution. Empty until T-001/T-002/T-005 run.)

### V-9 evidence

```
(paste `az ad app federated-credential list ...` output here)
```

### V-10 evidence

```
(paste `gh workflow list ...` output here)
```

### V-11 evidence

```
T0 (push completed at, UTC):
T1 (first poll observing new content, UTC):
elapsed (seconds):
PASS / FAIL vs. 300s SLO:
```

### V-12 evidence

```
curl time_total:
SDD-007 baseline cold-start:
PASS / FAIL:
```

### V-14 evidence

```
(paste confirmation that default GH failure notifications are enabled for repo owner)
```
