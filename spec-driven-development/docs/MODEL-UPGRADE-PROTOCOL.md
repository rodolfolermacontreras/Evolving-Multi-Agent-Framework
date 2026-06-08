# Model Upgrade Protocol

This protocol governs proposed model changes for the Evolving Multi-Agent Framework.
It specializes the existing Level-2 Friction Analysis process; it does not replace
`templates/level-2-decision.md`.

---

## Trigger Taxonomy

Treat a proposal as a full Level-2 model upgrade when it includes any of these
changes:

- Major version bump, such as `model-4` to `model-5`.
- Vendor swap, such as moving a role from one provider family to another.
- model-family swap, such as moving from a fast-mini family to a reasoning family.
- role-critical model assignment change for a Principal, reviewer, or worker whose
  behavior affects committed framework artifacts.

A minor patch is log-only when it has no material quality, cost, privacy, safety,
availability, hosted-capability, or tool-use risk. Escalate a minor patch to the
full Level-2 route when any of those risks are material or unclear.

---

## Required Branch Protocol

Every in-scope upgrade starts on an ephemeral regression branch:

```text
model-upgrade/<old>-to-<new>
```

Use `cli/model_upgrade.py branch-name --old <old> --new <new>` to produce safe
slug components. The branch must not merge until the owner approval evidence is
recorded in the Level-2 brief and the related ADR or waiver is committed.

---

## Evidence Workflow

1. Create the regression branch.
2. Fill `templates/level-2-decision.md` before adoption work begins.
3. Run the committed no-network workload in `templates/model-upgrade-workload.json`.
4. Capture old-model and new-model outputs in local or committed fixture files that
   contain no secrets.
5. Run `cli/model_upgrade.py compare` with the workload, pricing fixture, and both
   captured output files.
6. Review `comparison.json` and `comparison.md` for cost deltas, quality deltas,
   and the aggregate recommendation.
7. Owner approves, rejects, or requests another A/B pass before any model assignment
   changes land.

The harness is deterministic and no-network by design. It does not call model APIs,
HTTP endpoints, benchmark services, or provider SDKs.

---

## Friction Analysis Mapping

Map comparison evidence into `templates/level-2-decision.md` as follows:

| Brief section | Required model-upgrade evidence |
|---------------|---------------------------------|
| Money cost | One-time, recurring, per-run, old-model, new-model, and delta cost values from `comparison.json`. |
| Complexity cost | New hosted model surfaces, prompt rewrites, routing changes, and any provider-specific operational risk. |
| Maintenance burden | Who maintains prompts, fixtures, pricing assumptions, and re-runs; review cadence after provider price or capability changes. |
| Expected benefit | Measured quality delta, validation/test pass delta, review quality delta, and concrete workflow improvement. |
| Alternatives considered | Keep current model, use patch-only upgrade, restrict upgrade to one worker role, or defer until better evidence exists. |

Pricing assumptions live in `templates/model-upgrade-pricing.json` so cost changes are
reviewable diffs rather than hidden code changes.

---

## Quality Rubric

Each scenario output records these fields:

- `validation_pass`: whether the output satisfies task-specific validation.
- `spec_quality`: numeric checklist score for spec clarity and traceability.
- `commit_quality`: numeric score for implementation/report usefulness.
- `report_quality`: numeric score for executive readability and completeness.
- `ambiguous_win`: true when the new model appears better but the evidence is
  qualitative enough to require owner judgment.

The aggregate recommendation is:

- `approve` when the new model improves quality, does not fail validation, and has
  acceptable cost delta.
- `reject` when the A/B fails validation, weakens artifact quality, or has unclear
  cost benefit.
- `owner-review` when quality wins are ambiguous or the cost/benefit trade-off needs
  human judgment.

Ambiguous quality wins require explicit owner approval before merge.

---

## Rejection Path

If the A/B fails, cost benefit is unclear, or qualitative wins are ambiguous without
owner approval, keep the upgrade branch unmerged. Record `reject` or `owner-review`
in the comparison report, capture the reason in the Level-2 brief, and close or park
the branch without changing model assignments.

---

## Worked Example

Hypothetical vendor swap: `vendor-a-reasoner-4` to `vendor-b-reasoner-5`.

- Trigger: vendor swap and major version bump, so full Level-2 applies.
- Branch: `model-upgrade/vendor-a-reasoner-4-to-vendor-b-reasoner-5`.
- Money evidence: pricing fixture shows higher per-run cost but no recurring platform fee.
- Expected benefit: comparison report shows higher review-report quality and equal validation pass rate.
- Outcome: `owner-review` until Rodolfo approves the higher cost for the measured quality gain.