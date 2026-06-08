---
id: SDD-20260608MODELUPGRADE-spec
type: spec
status: done
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# Feature Spec: Model Upgrade Discipline (SDD-015)

- Date: 2026-06-08
- Authors: Principal Product Manager + Principal Architect
- Status: APPROVED for PLAN/TASKS/IMPLEMENT
- Priority: P1
- Sprint: PI-5 / Sprint 4 (= overall Sprint 8)
- Spec ID: SDD-015
- Parent objective: PI-5 Objective 4 -- ADO/GitHub Bridge + Model Upgrade Discipline
- Lifecycle: IDEA -> BACKLOG -> CLARIFY -> SPEC -> PLAN -> TASKS -> IMPLEMENT -> REVIEW -> DONE
- CLARIFY: Closed 2026-06-08 in `clarify.md`; Q-J through Q-O resolved by PM + Architect defaults from Sprint 8 kickoff.

---

## Problem Statement

The framework is built around specialized agents, prompts, and lifecycle gates. Those workflows do not port cleanly across model changes. A newer model can improve raw capability while also changing instruction-following behavior, cost, latency, output style, safety refusals, tool-use behavior, or compliance with the framework's artifact contracts.

Today the framework has a Level-2 decision policy and a Friction Analysis template, but it does not name model upgrades as a first-class Level-2 trigger and does not define the evidence required before a model swap is accepted. That creates three risks:

1. **Silent quality drift.** A model can be upgraded because it is newer, not because it performs better on SDD work.
2. **Unpriced complexity.** Cost-per-token, hosted availability, manual prompt rework, and maintenance burden can be hidden until after adoption.
3. **Weak stakeholder defense.** When a stakeholder pushes for a newer model or vendor, the framework lacks a citable process for answering "what is the real gain to overcome this friction?"

SDD-015 turns model upgrades into explicit Level-2 decisions backed by a regression-test branch, deterministic A/B evidence, cost analysis, quality deltas, and owner approval.

---

## Goals

1. Define what counts as a model upgrade and when minor patch changes can be logged without the full protocol.
2. Create `docs/MODEL-UPGRADE-PROTOCOL.md` as the operating procedure for model upgrade proposals.
3. Add a stdlib-only, no-network A/B harness for comparing old/new model outputs against committed representative fixtures.
4. Capture cost deltas with committed pricing assumptions and map the output into the Level-2 Friction Analysis brief.
5. Capture quality deltas with measurable rubric fields and explicit owner approval for ambiguous qualitative wins.
6. Require a per-upgrade regression branch named `model-upgrade/<old>-to-<new>` before implementation or adoption work proceeds.
7. Add the required `decision-policy.md` cross-reference only through an ADR-backed or owner-waived constitution edit.

---

## Non-Goals

- No live model API calls in the default A/B harness.
- No automatic model upgrade, model deployment, or hosted-model configuration change.
- No new third-party Python dependency.
- No change to current agent model assignments.
- No model-provider recommendation beyond the evidence protocol.
- No edits to `constitution/**` without ADR acceptance or explicit owner waiver.
- No replacement of the existing Level-2 Friction Analysis template.
- No F-12 `/taskstoissues` implementation work.

---

## Requirements

| ID | Requirement | Decision Source |
|----|-------------|-----------------|
| R1 | The protocol defines a model upgrade as a major version bump, vendor swap, model-family swap, or role-critical model assignment change. Minor patches are logged only unless material quality/cost/privacy/safety risk exists. | Q-J |
| R2 | Every in-scope model upgrade is a Level-2 decision and must use the existing Friction Analysis brief before adoption. | SDD-014, Q-M |
| R3 | Each model upgrade uses an ephemeral branch named `model-upgrade/<old>-to-<new>` and does not merge until owner approval is recorded. | Q-K |
| R4 | The representative workload is a committed canonical fixture based on recent sprint prompts and artifacts covering CLARIFY, SPEC, PLAN/TASKS, IMPLEMENT-report, and REVIEW-report scenarios. | Q-K |
| R5 | The A/B harness is stdlib-only, no-network by default, deterministic, and exposed through `cli/model_upgrade.py` with `main(argv)`. | Q-L |
| R6 | Cost-delta capture uses committed pricing inputs and produces values that can populate the Money Cost section of `templates/level-2-decision.md`. | Q-M |
| R7 | Quality-delta capture includes validation/test pass, spec-quality checklist score, commit/report quality deltas, and owner approval for ambiguous qualitative wins. | Q-N |
| R8 | `docs/MODEL-UPGRADE-PROTOCOL.md` describes trigger taxonomy, branch protocol, A/B workflow, cost capture, quality rubric, approval gate, and rejection path. | Q-J..Q-N |
| R9 | `constitution/decision-policy.md` references the protocol only after ADR-016 is accepted or an explicit owner waiver is recorded. | Q-O, Article VIII |
| R10 | Implementation remains portable and stdlib-only; no model SDK, benchmarking service, or provider dependency is introduced. | Article V |
| R11 | F-14 validates with targeted tests, schema_lint, and full pytest; no REQUIRED item can be deferred from Sprint 8 close. | Sprint 8 kickoff |

---

## Acceptance Criteria

- **AC-1**: Given the model-upgrade protocol doc, when a reader searches for upgrade triggers, then the doc distinguishes full Level-2 triggers from minor patch log-only changes. (R1, R8)
- **AC-2**: Given a model-upgrade proposal, when it meets the trigger definition, then the protocol routes it through `templates/level-2-decision.md` before adoption. (R2, R6)
- **AC-3**: Given old and new model identifiers, when the branch name helper or protocol guidance is applied, then the branch name follows `model-upgrade/<old>-to-<new>` with safe slug components. (R3)
- **AC-4**: Given the committed workload fixture, when the harness reads it, then it includes CLARIFY, SPEC, PLAN/TASKS, IMPLEMENT-report, and REVIEW-report scenarios derived from recent sprint artifacts. (R4)
- **AC-5**: Given captured old/new outputs for the workload fixture, when the A/B harness runs, then it produces deterministic Markdown and JSON summaries without network access. (R5)
- **AC-6**: Given committed pricing inputs and output token/unit counts, when cost analysis runs, then one-time, recurring, per-run, and delta cost values are reported for Level-2 Friction Analysis. (R6)
- **AC-7**: Given old/new outputs, when quality analysis runs, then validation/test pass, spec-quality checklist score, commit/report quality deltas, and ambiguous-owner-approval fields appear in the report. (R7)
- **AC-8**: Given `decision-policy.md`, when SDD-015 is complete, then it references `docs/MODEL-UPGRADE-PROTOCOL.md`; because this touches constitution, ADR-016 acceptance or owner waiver evidence exists. (R9)
- **AC-9**: Given the implementation, when imports are scanned, then no third-party model, HTTP, benchmark, or data-analysis libraries are imported. (R10)
- **AC-10**: Given F-14 close, when `python spec-driven-development/cli/schema_lint.py` and full pytest run, then both exit 0 with test count at or above the Sprint 8 baseline plus new SDD-015 tests. (R11)

---

## Affected Modules

Approved F-14 implementation surfaces:

- `spec-driven-development/docs/MODEL-UPGRADE-PROTOCOL.md` -- new operating protocol.
- `spec-driven-development/templates/model-upgrade-workload.json` -- new canonical no-network workload fixture.
- `spec-driven-development/templates/model-upgrade-pricing.json` -- new committed pricing input fixture.
- `spec-driven-development/cli/model_upgrade.py` -- new stdlib CLI harness.
- `spec-driven-development/cli/test_model_upgrade.py` -- new tests for branch naming, fixture parsing, cost deltas, quality deltas, report output, and import guard.
- `spec-driven-development/docs/ADR/016-model-upgrade-protocol-cross-reference.md` -- new ADR if F-14 edits `decision-policy.md`.
- `spec-driven-development/constitution/decision-policy.md` -- conditional cross-reference edit; blocked unless ADR-016 is accepted or owner waiver is recorded.

Blocked surfaces unless separately approved:

- Dependency manifests or package lock files.
- Agent model assignment files or runtime model configuration.
- Any live provider API integration.
- `constitution/principles.md`.
- SDD-022 `/taskstoissues` files.

---

## API / CLI Contract

F-14 should implement a CLI compatible with this shape:

```powershell
python spec-driven-development/cli/model_upgrade.py branch-name --old claude-4-7 --new claude-5-0
python spec-driven-development/cli/model_upgrade.py compare --fixture spec-driven-development/templates/model-upgrade-workload.json --pricing spec-driven-development/templates/model-upgrade-pricing.json --old-output old.json --new-output new.json --out-dir .tmp/model-upgrade-report
python spec-driven-development/cli/model_upgrade.py summarize --report .tmp/model-upgrade-report/comparison.json
```

Required semantics:

- Exit code 0 = comparison complete with no malformed input.
- Exit code 1 = validation failure or quality/cost threshold requires owner review.
- Exit code 2 = usage error.
- No subcommand performs live model calls.
- Expected failures print to stderr.
- All file operations use `pathlib.Path`.

---

## Test Strategy

- Unit tests for trigger taxonomy text and protocol link sanity.
- Unit tests for safe branch-name slugging.
- Unit tests for workload fixture parsing and required scenario coverage.
- Unit tests for pricing input parsing and cost-delta calculation.
- Unit tests for quality rubric aggregation and owner-review recommendation when ambiguity is present.
- Unit tests for deterministic Markdown and JSON report generation.
- Import scan proving no third-party model, HTTP, or data-analysis dependency.
- Governance check proving `decision-policy.md` cross-reference has ADR-016 acceptance or owner-waiver evidence.
- Regression: `python spec-driven-development/cli/schema_lint.py` exit 0.
- Regression: full pytest suite exit 0 after F-14 code changes.

---

## Validation Contract

The binding validation contract lives in sibling file `validation.md` and is locked at F-13. F-14 implementation must check every REQUIRED item before SDD-015 can be marked DONE.

---

## Traceability Matrix

| Requirement | Acceptance Criteria | Validation Items | Implementation Surface |
|-------------|---------------------|------------------|------------------------|
| R1 | AC-1 | V-1 | protocol doc |
| R2 | AC-2 | V-2 | protocol doc, Level-2 template references |
| R3 | AC-3 | V-3 | protocol doc, CLI |
| R4 | AC-4 | V-4 | workload fixture, CLI tests |
| R5 | AC-5 | V-5 | `cli/model_upgrade.py` |
| R6 | AC-6 | V-6 | pricing fixture, CLI report |
| R7 | AC-7 | V-7 | CLI quality rubric |
| R8 | AC-1..AC-7 | V-1, V-2, V-8 | protocol doc |
| R9 | AC-8 | V-9 | ADR-016, `decision-policy.md` |
| R10 | AC-9 | V-10 | CLI import guard |
| R11 | AC-10 | V-11, V-12 | schema_lint, pytest |

---

## Open Questions

None. CLARIFY closed 2026-06-08.

---

## F-14 Caveats

- F-14 must not call live model APIs. The harness compares committed/captured fixture outputs only.
- F-14 must not edit `decision-policy.md` unless ADR-016 is accepted or an explicit owner waiver is recorded.
- If owner approval for the constitution cross-reference is unavailable, F-14 must stop as OWNER-ATTENTION rather than marking SDD-015 done.
- A future live model-runner integration would be a separate Level-2 decision.
