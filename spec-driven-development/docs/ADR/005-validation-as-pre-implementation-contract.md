# ADR-0005: Validation as a Pre-Implementation Contract

- Status: Accepted
- Date: 2026-05-12
- Deciders: Rodolfo Lerma (project owner)
- Supersedes: validation checklist as post-implementation review artifact
- Related: ADR-0001 (SDD framework), ADR-0004 (Executive Manager orchestration), Article X in `constitution/principles.md`

---

## Context

The framework already values spec-driven development, TDD, and two-stage review,
but its validation template was positioned as a post-implementation checklist.
That made validation reactive: an implementer could start work before acceptance
criteria, required tests, manual checks, and Definition of Done were written down
as a binding target.

Cross-source inspiration research found the same pattern independently in three
code-based references:

1. Spec-Kit treats `/checklist` as a requirements-quality gate and explicitly
   checks whether requirements have unit-test coverage.
2. The DeepLearning.AI SDD course uses a Validation Scorecard to define how a
   specification will be judged before implementation proceeds.
3. The sc-spec companion keeps `validation.md` beside the spec and includes a
   Definition of Done that makes completion measurable.

The convergence is stronger than a stylistic preference: validation criteria are
most useful when they constrain implementation before code exists. If they are
written afterward, they can become a narrative of what happened rather than a
contract for what must happen.

## Decision

Promote validation from a post-implementation review artifact to a
**pre-implementation binding contract**.

Concretely:

1. Add Article X to `constitution/principles.md`: Validation Is a
   Pre-Implementation Contract.
2. Require every spec-governed feature to include both `spec.md` and sibling
   `validation.md` during `/spec`.
3. Require acceptance criteria to be phrased as testable assertions.
4. Lock the validation contract when `/tasks` is invoked, so task decomposition
   cannot silently weaken validation after implementation begins.
5. Require `/implement` to verify `validation.md` exists before code changes.
6. Require at least one automated-test checkbox or an explicit
   `[NO-TEST-NEEDED]` task justification accepted by the spec-compliance
   reviewer.
7. Treat implementation as complete only when every relevant validation checkbox
   is satisfied with passing tests, confirmed manual checks, or accepted written
   justification.
8. Add an optional `tdd-gate` skill so spec-compliance reviewers can mechanically
   compare production-code changes against test-file changes.

We considered leaving `validation.md` as a QA-only artifact and merely improving
its wording. We rejected that because it preserves the core weakness: validation
would still be discovered after implementation rather than binding the work
before implementation.

## Consequences

### Positive

- Specs become more executable because acceptance criteria and validation checks
  are written before implementation.
- TDD becomes enforceable at the IMPLEMENT gate rather than merely recommended in
  worker guidance.
- Spec-compliance review has a concrete artifact to check instead of inferring
  test obligations from prose.
- QA becomes faster and less subjective because the Definition of Done is already
  explicit.
- The framework now aligns with the strongest convergent finding from Spec-Kit,
  the DeepLearning.AI SDD course, and sc-spec.

### Negative or risky

- Existing specs that were created before this ADR may not have sibling
  `validation.md` files and are technically out of compliance with Article X.
  Mitigation: grandfather already-accepted specs or add a lightweight migration
  pass before their next `/tasks` invocation.
- Small changes may feel heavier if agents over-apply the rule. Mitigation:
  Article VI still allows spec-exempt work for tiny bug fixes, and Article X
  allows `[NO-TEST-NEEDED]` with reviewer-accepted justification.
- Validation contracts can become checkbox theater if written generically.
  Mitigation: `/spec` now requires acceptance criteria as testable assertions
  and `validation.md` requires specific test coverage, manual checks, and a
  Definition of Done.

### Process changes

- `templates/feature-spec.md` now requires testable Acceptance Criteria and a
  Validation Contract reference.
- `templates/validation.md` is rewritten as a pre-implementation contract using
  checkbox sections and an explicit Definition of Done.
- `.github/prompts/spec.prompt.md` requires `/spec` to produce both `spec.md`
  and `validation.md`.
- `.github/prompts/implement.prompt.md` gains pre-execution and post-execution
  validation gates.
- `.github/skills/engineering/tdd-gate/SKILL.md` documents a mechanical diff
  check for TDD compliance.
- `constitution/roadmap.md` records the PI-1 deliverable.

## Status

Accepted. Implemented in commit that introduces this ADR.
