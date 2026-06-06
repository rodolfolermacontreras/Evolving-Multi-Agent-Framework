---
id: SDD-20260512FLEE-retro
type: retro
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-12-fleet-ledger
---

# Retro: Fleet Ledger v0.1 First SDD Pilot

- Date: 2026-05-12
- Feature: `spec-driven-development/specs/2026-05-12-fleet-ledger/`
- Facilitator: Agent INDIA

---

## What worked

1. **Validation-first clarified the implementation.** Writing `validation.md` before code turned the vague goal "make a ledger" into concrete checks: schema objects, idempotency, round trip, outcome update, help text, and dependency boundaries.
2. **The date-prefixed feature directory made traceability obvious.** Spec, plan, tasks, validation, clarification log, and retro stayed together and were easy to audit.
3. **TDD fit the feature well.** The initial red test proved the package did not exist; implementation then moved directly toward green without debating scope.

## What did not work as smoothly

1. **Lifecycle artifact volume is high for a small CLI.** The full lifecycle proved useful, but many sections repeated the same acceptance criteria in slightly different formats.
2. **Task IDs have two competing conventions.** The template suggests `T-{spec-date}-{NNN}`, while the pilot requested `T-001`. The framework should clarify whether local short ids are acceptable inside a feature directory.
3. **The framework lacks a canonical Python CLI style guide.** ECHO's bootstrap helped, but a small reusable pattern for argparse + pathlib + sqlite would reduce reinvention.

## Framework change candidates filed

- LESSON-001: Add a compact Python stdlib CLI pattern for framework utilities.
- LESSON-002: Clarify task id conventions for date-prefixed feature directories.
- LESSON-003: Add a validation contract quick-fill guide to reduce duplicated prose across spec/plan/tasks/validation.
- LESSON-004: Define a future ledger migration policy before v0.2 schema changes.

## Honest assessment

The framework helped more than it hurt for this first dogfood because it forced testable acceptance criteria before implementation and created durable evidence that Article VII is now real. The friction was mostly documentation duplication: spec, plan, tasks, and validation each needed similar references. For riskier or multi-agent features that duplication may be worth it; for small utilities the framework should provide a lighter artifact path or better cross-linking conventions.
