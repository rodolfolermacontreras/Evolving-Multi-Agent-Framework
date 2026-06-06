---
id: SDD-20260603FRIC-validation
type: validation
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-06-03-friction-analysis-template
---

# Validation Contract: Friction Analysis Section in Level-2 Decision Template

- Spec Reference: `spec-driven-development/specs/2026-06-03-friction-analysis-template/spec.md`
- Contract Date: 2026-06-03
- Author: principal-architect
- Lock Point: `/tasks` (this spec is skip-to-implement; lock is at commit)

This contract is written DURING `/spec`, locked at commit time, and verified
before SDD-014 can be marked DONE in PI-4 Sprint 3.

---

## Automated Tests

> **Cross-reference rule:** Each check below maps to one or more AC
> identifiers from `spec.md`. Validation is `grep`-based because this is a
> documentation change; no production code is added.

- [ ] CHECK-001: `grep -c "^## " templates/level-2-decision.md` returns at
  least 5 second-level headings, and the five required headings -- money
  cost, complexity cost, maintenance burden, expected benefit, alternatives
  considered -- appear in that order: proves AC1.
- [ ] CHECK-002: `templates/level-2-decision-EXAMPLE.md` exists, contains
  all five required headings, and references ADR-0008 by name: proves AC2.
- [ ] CHECK-003: `grep "level-2-decision.md" constitution/decision-policy.md`
  returns at least one match AND the surrounding sentence states the
  template is required for Level 2 submissions: proves AC3.
- [ ] CHECK-004: `grep "version: '1.1.0'" constitution/decision-policy.md`
  returns one match in the YAML frontmatter: proves AC4.
- [ ] CHECK-005: `wc -l templates/level-2-decision.md` returns fewer than
  100 lines: proves AC5.

## Specific Test Coverage Required

- [ ] Unit coverage: `[NO-TEST-NEEDED]` -- documentation change, no
  production code introduced; verification is grep-based per the checks
  above.
- [ ] Integration coverage: covered by CHECK-001 through CHECK-005.
- [ ] Regression coverage: constitution-sync scan over `.github/skills/`,
  `.github/prompts/`, and `spec-driven-development/templates/` returns
  zero NEEDS-UPDATE findings.
- [ ] Error, empty, boundary, or permission cases: not applicable;
  documentation does not have runtime states.

## Manual Checks

- [ ] The worked example for ADR-0008 is accurate -- the populated cost,
  complexity, maintenance, benefit, and alternatives sections match the
  facts recorded in `docs/ADR/008-hire-cloud-security-architect.md`.
- [ ] The template fits on one page at standard editor zoom (visual
  confirmation in addition to CHECK-005's line count).
- [ ] The amended sentence in `decision-policy.md` reads naturally and
  does not contradict any other rule in the file.

## Tone / UX Check

`[NO-UX-CHECK-NEEDED]` -- this template is an internal artifact used by
Principal agents and the human owner; there is no end-user-facing UI copy.

## Definition of Done

SDD-014 is merge-ready only when all five automated checks pass, all three
manual checks are confirmed, the constitution-sync scan returns zero
NEEDS-UPDATE findings (NEEDS-REVIEW findings are acceptable and must be
listed in the commit message), the `decision-policy.md` version bump to
`1.1.0` is committed alongside the template files, and PI-4 Sprint 3's
SDD-014 row in `CURRENT_PI.md` is checked off.
