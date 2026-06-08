# Stakeholder Pressure Response

Use this as a communication wrapper for stakeholder-pressure cases. It does not replace `spec-driven-development/templates/level-2-decision.md`; Level-2 or irreversible decisions still require the Friction Analysis brief.

---

## Request Summary

- Request:
- Stakeholder / source:
- Date:
- Urgency:

## Trigger Classification

- Trigger: `speed-over-validation | skip-owner-approval | scope-reduction-without-traceability | push-before-approval | unverified-external-claim | novelty-or-prestige-pressure | external-write-pressure | silent-exception-pressure`
- Principal route: `EM | PM | Architect | SW Dev | QA | owner`
- Level-2 pressure present: `yes | no`

## Affected Gate Or Requirement

- gate_id:
- gate_type:
- blocking_scope:
- approver:
- evidence_type:
- evidence_ref:
- status:
- next_action:
- Requirement / validation item, if no gate applies:

## Missing Evidence

Name the missing approval, validation result, source-system output, issue comment, commit stamp, accepted ADR, or other SDD-023 evidence.

Invalid approval evidence includes green tests, schema-lint success, elapsed time, generated executive surfaces, stakeholder silence, task status, and agent confidence.

## Risk Of Proceeding Without It

State the delivery, governance, traceability, security, privacy, or quality risk in plain language.

## Options

- Fastest compliant path:
- Safer full path:
- Explicit owner decision path:

## Recommendation

- Recommended option:
- Next action:
- Owner / principal responsible:

## Friction Analysis Handoff

If Level-2 or irreversible shortcut pressure exists, instantiate `spec-driven-development/templates/level-2-decision.md` before implementation, push, external write, schema migration, dependency addition, model/tool upgrade, M365 permission change, privacy-sensitive logging change, or constitution edit.

## Response Checklist

- [ ] Acknowledges the stakeholder goal or urgency.
- [ ] Names the blocked transition or decision surface.
- [ ] Names the missing evidence, approval, validation result, or traceability update.
- [ ] Explains the risk of proceeding without it.
- [ ] Offers options.
- [ ] Recommends one path.
- [ ] Routes Level-2 pressure to `spec-driven-development/templates/level-2-decision.md`.
- [ ] Preserves unchecked REQUIRED items until owner evidence exists.
