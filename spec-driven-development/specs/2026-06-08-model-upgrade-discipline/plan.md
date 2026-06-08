---
id: SDD-20260608MODELUPGRADE-plan
type: plan
status: blocked
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# Implementation Plan: Model Upgrade Discipline (SDD-015)

- Spec Reference: `./spec.md`
- Validation Reference: `./validation.md`
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Owners: Principal Architect + Principal Software Developer
- Status: APPROVED for TASKS / F-14 implementation

---

## Summary

Implement SDD-015 as a small governance-and-tooling slice:

1. Author the model-upgrade protocol doc.
2. Add committed no-network workload and pricing fixtures.
3. Add a stdlib-only `model_upgrade.py` comparison CLI with tests.
4. Draft ADR-016 and apply the `decision-policy.md` cross-reference only after ADR acceptance or owner waiver.
5. Close validation with schema_lint and full pytest.

The implementation must remain disjoint from SDD-022 except for shared validation commands. It must not introduce live model calls or third-party packages.

---

## Implementation Phases

### Phase 1 -- Protocol And Fixtures

- Create `docs/MODEL-UPGRADE-PROTOCOL.md` with trigger taxonomy, branch protocol, A/B workflow, cost capture, quality rubric, approval gate, rejection path, and evidence-to-Friction-Analysis mapping.
- Create `templates/model-upgrade-workload.json` with deterministic representative scenarios.
- Create `templates/model-upgrade-pricing.json` with placeholder owner-editable pricing inputs and source notes.

### Phase 2 -- Stdlib A/B Harness

- Create `cli/model_upgrade.py` following `docs/CLI-PATTERN.md`.
- Implement `branch-name`, `compare`, and `summarize` subcommands.
- Keep `compare` no-network by design: it reads fixture inputs and captured old/new outputs only.
- Write Markdown and JSON reports with stable ordering.

### Phase 3 -- Tests And Guards

- Create `cli/test_model_upgrade.py`.
- Cover branch slugging, fixture parsing, pricing calculations, quality rubric aggregation, deterministic report output, exit codes, and import guard.
- Include tests that fail on third-party model/HTTP/benchmark/data-analysis imports.

### Phase 4 -- Governance Cross-Reference

- Draft `docs/ADR/016-model-upgrade-protocol-cross-reference.md` if `decision-policy.md` will be edited.
- Apply the `decision-policy.md` cross-reference only after ADR-016 is accepted or owner waiver is recorded.
- If approval is unavailable, stop as OWNER-ATTENTION with V-9 unchecked.

### Phase 5 -- Validation Close

- Run targeted tests for `cli/test_model_upgrade.py`.
- Run `python spec-driven-development/cli/schema_lint.py`.
- Run full pytest because F-14 changes code.
- Check V-1 through V-12 only after evidence exists.

---

## Design Details

### Trigger Taxonomy

The protocol should classify model changes as:

- **Full Level-2 model upgrade**: major version bump, vendor swap, model-family swap, role-critical model assignment change.
- **Logged patch change**: minor patch with no material quality, cost, privacy, safety, or hosted capability risk.
- **Escalated patch change**: minor patch with material quality, cost, privacy, safety, or hosted capability risk; route as full Level-2.

### Branch Protocol

Branch names use:

```text
model-upgrade/<old>-to-<new>
```

The CLI should slug old/new identifiers to lowercase ASCII, collapse unsafe characters to `-`, trim duplicate separators, and reject empty slugs.

### A/B Fixture Model

The fixture is intentionally not a live benchmark. It is a committed representative workload containing prompt-like inputs and metadata derived from recent sprint artifacts. Captured old/new outputs are separate input files so the harness can be tested without network calls.

### Cost Model

The pricing fixture is owner-editable and committed. It should represent pricing assumptions explicitly rather than embedding vendor knowledge in code. The CLI calculates from the fixture and output usage numbers only.

### Quality Model

The quality rubric should be simple enough for repeat use:

- validation/test pass
- spec-quality checklist score
- commit/report quality delta
- required owner approval for ambiguous quality wins

The aggregate recommendation can be `approve`, `reject`, or `owner-review`.

---

## File Scope

### Allowed

- `spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md`
- `spec-driven-development/templates/model-upgrade-workload.json`
- `spec-driven-development/templates/model-upgrade-pricing.json`
- `spec-driven-development/cli/model_upgrade.py`
- `spec-driven-development/cli/test_model_upgrade.py`
- `spec-driven-development/docs/ADR/016-model-upgrade-protocol-cross-reference.md`
- `spec-driven-development/constitution/decision-policy.md` (only after ADR acceptance or owner waiver)
- `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/validation.md` (checkbox updates only at close)
- `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/spec.md` (status update only at close)
- `spec-driven-development/specs/2026-06-08-model-upgrade-discipline/tasks.md` (task status updates only at close)

### Blocked

- Any dependency manifest or package lock file.
- Any live model-provider integration.
- Any current agent model assignment or runtime model config.
- `spec-driven-development/constitution/principles.md`.
- SDD-022 files: `cli/taskstoissues.py`, `cli/test_taskstoissues.py`, `.github/prompts/taskstoissues.prompt.md`.
- Unrelated SDD-035 files.

---

## Validation Strategy

- Targeted tests: `python -m pytest spec-driven-development/cli/test_model_upgrade.py -v --tb=short`.
- Schema lint: `python spec-driven-development/cli/schema_lint.py`.
- Full suite: `python -m pytest spec-driven-development/ --tb=no -q`.
- Manual/HITL: ADR acceptance or owner waiver before `decision-policy.md` edit.

---

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Constitution edit lands without Article VIII evidence | V-9 requires ADR acceptance or explicit owner waiver before `decision-policy.md` edit. |
| Harness becomes a live benchmark | CLI contract forbids network calls; tests prove no provider SDK/HTTP dependency. |
| Pricing assumptions go stale | Pricing is committed data with source notes, not hidden code. Future updates are reviewable diffs. |
| Quality score becomes subjective | Rubric splits measurable checks from owner-approved ambiguous wins. |
| SDD-015 conflicts with SDD-022 in F-14 | File scopes are disjoint except shared validation commands. |

---

## Handoff To F-14

F-14 may start implementation after this plan and `tasks.md` are committed. The only known HITL point is V-9: before editing `constitution/decision-policy.md`, F-14 must have ADR-016 accepted or owner waiver recorded. If that approval is not available, F-14 stops as OWNER-ATTENTION and does not mark SDD-015 done.
