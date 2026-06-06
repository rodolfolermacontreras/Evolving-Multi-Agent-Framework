---
id: SDD-20260603FRIC-spec
type: spec
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-06-03-friction-analysis-template
---

# Feature Spec: Friction Analysis Section in Level-2 Decision Template

- Date: 2026-06-03
- Author: principal-architect
- Status: APPROVED
- Priority: P1
- Sprint: PI-4 Sprint 3
- Spec ID: SDD-014

---

## Problem Statement

The framework's `constitution/decision-policy.md` defines three authority
levels and reserves Level 2 for irreversible / high-risk / privacy-sensitive
decisions (new dependencies, schema migrations, external integrations,
production merges, credential changes). The policy correctly requires
explicit human approval and an ADR for every Level 2 decision, but it does
not force a structured **cost-of-change conversation** before the human is
asked to approve.

Today a Level 2 request lands at the human in whatever shape the proposing
Principal happens to draft it. The Cloud-Security Architect performs this
friction analysis informally (see ADR-0008 / ADR-0009); other Principals do
not. This produces:

1. Inconsistent quality of Level 2 submissions (some have alternatives
   considered and cost estimates, some do not).
2. Easy approval-by-default when the human cannot quickly see the
   incremental complexity, maintenance burden, or recurring cost.
3. No citable, reusable artifact when a stakeholder later asks "why did we
   adopt X over the cheaper Y option?"

Scott Epperly framed this in the 2026-06-02 meeting as: *"what is the real
gain to overcome this friction?"* The framework needs an explicit template
that forces every Level 2 proposal to answer that question in the same five
dimensions, every time, in one page.

## Proposed Solution

Introduce one new template and one worked example, and amend the decision
policy to require both.

1. **`spec-driven-development/templates/level-2-decision.md`** -- a one-page
   form that a proposing Principal fills in and submits to the human BEFORE
   Level 2 approval is granted. The form is the input to the human approval
   gate. After approval, the decision is recorded as an ADR which links back
   to the submitted form (preserving the friction analysis as evidence).

2. **`spec-driven-development/templates/level-2-decision-EXAMPLE.md`** -- a
   retrospective fill-in for ADR-0008 (the Cloud-Security Architect hire)
   showing the five sections populated with the actual costs and benefits
   that decision carried. Serves as the reference any Principal can read
   when filling in their first form.

3. **`spec-driven-development/constitution/decision-policy.md`** amended
   (MINOR bump) to require the new template for every Level 2 submission and
   to reference both files.

## Five Required Sections

The template MUST contain these five sections in this order. No section may
be omitted; a section with no content must explicitly say "none" with a
one-sentence justification.

1. **Money cost (one-time + recurring)** -- dollar estimate of setup cost
   and ongoing monthly / annual cost. "None" is acceptable with justification.
2. **Complexity cost** -- new moving parts the decision introduces (new
   dependencies, new services, new agent roles, new failure modes).
3. **Maintenance burden** -- who maintains the added surface, at what
   cadence, and what happens to upkeep if the owner is unavailable.
4. **Expected benefit** -- concrete and measurable where possible (e.g.
   "removes X manual step per sprint", "unblocks Y stakeholder", "passes
   Z compliance gate"). Vague benefits are flagged at the approval gate.
5. **Alternatives considered** -- cheaper paths evaluated and the reason
   each was rejected. At least one alternative must be considered; "we
   considered no alternatives" is not an acceptable answer.

## Acceptance Criteria

Each criterion is phrased as a testable assertion an automated `grep` /
manual check can prove true or false.

1. Given the new template file at
   `spec-driven-development/templates/level-2-decision.md`, when a reader
   opens it, then the file MUST contain exactly five top-level section
   headings matching the five dimensions above, in order.
2. Given the worked example at
   `spec-driven-development/templates/level-2-decision-EXAMPLE.md`, when a
   reader opens it, then the file MUST be populated for ADR-0008
   (Cloud-Security Architect hire) and MUST contain all five sections with
   non-placeholder content.
3. Given the amended `constitution/decision-policy.md`, when a reader
   searches for the template path, then the file MUST reference
   `templates/level-2-decision.md` and MUST state that the template is
   required for every Level 2 submission.
4. Given `constitution/decision-policy.md`, when the frontmatter `version`
   is inspected, then it MUST be bumped from `1.0.0` to `1.1.0` (MINOR per
   ADR-0006: new required section reference added; no existing rule
   removed or weakened).
5. Given the new template file, when its rendered length is measured, then
   it MUST fit on one page when viewed at standard editor zoom
   (operational target: under 100 lines of Markdown, comments excluded).

## Affected Modules

- Files (new):
    - `spec-driven-development/templates/level-2-decision.md`
    - `spec-driven-development/templates/level-2-decision-EXAMPLE.md`
    - `spec-driven-development/specs/2026-06-03-friction-analysis-template/spec.md` (this file)
    - `spec-driven-development/specs/2026-06-03-friction-analysis-template/validation.md`
- Files (amended):
    - `spec-driven-development/constitution/decision-policy.md` (version bump + template reference)

## Data Model Changes

None. Pure documentation change.

## API Changes

None.

## Test Strategy

- Unit: not applicable (documentation).
- Integration: `grep`-based verification that the five required section
  headings exist in both the template and the example, that
  `decision-policy.md` references the template path, and that the version
  was bumped.
- End-to-end / manual: human review of the worked example to confirm the
  filled-in friction analysis for ADR-0008 is accurate and useful.
- Regression: constitution-sync scan over `.github/skills/`,
  `.github/prompts/`, and `spec-driven-development/templates/` to confirm
  no downstream artifact contradicts the new requirement.

## Validation Contract

The binding validation contract for this feature lives in the sibling file
`validation.md` in this directory. It is locked at `/tasks` and must have
zero unchecked required items before this spec is considered complete.

## Traceability Matrix

| Requirement | Acceptance Test | Module |
|-------------|-----------------|--------|
| AC1 -- five sections in template | grep for the five headings | `templates/level-2-decision.md` |
| AC2 -- worked example populated | grep + manual read | `templates/level-2-decision-EXAMPLE.md` |
| AC3 -- decision-policy references template | grep for template path | `constitution/decision-policy.md` |
| AC4 -- version bumped to 1.1.0 | grep for `version: '1.1.0'` | `constitution/decision-policy.md` |
| AC5 -- one-page template | line count under 100 | `templates/level-2-decision.md` |

## Open Questions

None. Scope was clarified in the EM brief that routed this work.

## Out of Scope

- Level 0 (worker autonomous) and Level 1 (Principal) decisions remain
  template-free; this template applies only to Level 2.
- Retroactively reformatting historical ADRs to add a Friction Analysis
  section. Past Level 2 decisions stand as recorded; the template applies
  going forward.
- SDD-015 (Model upgrades as Level-2) -- a separate spec that USES this
  template, deferred to PI-5.
- SDD-025 (Stakeholder-pressure defense pattern) -- a playbook that
  INVOKES this template, deferred to PI-5.
- Tooling automation (e.g. a `/level-2-decision` slash command). The
  template is human-fillable in plain Markdown; automation is a later
  iteration if needed.
