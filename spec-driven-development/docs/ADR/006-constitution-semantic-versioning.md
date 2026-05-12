# ADR-0006: Constitution Semantic Versioning and Propagation Check

- Status: Accepted
- Date: 2026-05-12
- Deciders: Rodolfo Lerma (project owner)
- Supersedes: unversioned constitution amendments with no propagation check
- Related: ADR-0001 (SDD framework), ADR-0005 (Validation as a Pre-Implementation Contract), Article VIII and Governance in `constitution/principles.md`

---

## Context

The framework constitution defines its mission, principles, technical posture,
roadmap, decision policy, and quality policy. Before this ADR, those six files
had no per-file version metadata. A constitution amendment could change a
principle while skills, prompts, and templates continued to encode the old rule.
That created a silent-drift risk: the framework's root governance could evolve
without any required check that downstream operating artifacts still aligned.

Spec-Kit's `/speckit.constitution` command provides a useful pattern for this
problem: constitution changes should carry explicit semantic-version impact and
produce a synchronization report that identifies affected artifacts. The pattern
fits this framework because governance is file-based, agent-readable, and
implemented through skills, slash prompts, and templates.

## Decision

Adopt per-file semantic versioning for the six constitution files and require a
propagation check for future amendments.

Concretely:

1. Add YAML frontmatter to all six files in `spec-driven-development/constitution/`:
   `version`, `ratified`, and `last_amended`.
2. Ratify the first framework constitution version as `1.0.0` on `2026-05-12`.
3. Add a `/constitution` slash command that classifies amendments as MAJOR,
   MINOR, or PATCH and updates `version` plus `last_amended`.
4. Require `/constitution` to scan `.github/skills/**/SKILL.md`,
   `.github/prompts/*.prompt.md`, and `spec-driven-development/templates/*.md`
   for downstream references to the amended content.
5. Add a `constitution-sync` skill that performs the lower-level reference scan
   and returns `ALIGNED`, `NEEDS-REVIEW`, or `NEEDS-UPDATE` verdicts.
6. Require a Sync Impact Report for every amendment, showing what changed, what
   was affected, what was auto-updated, and what still needs human review.
7. Guardrail the workflow so skills, prompts, and templates are never modified
   automatically by the scan; downstream changes must be reviewed explicitly.

Version bump semantics are:

- MAJOR: principle changed or removed.
- MINOR: new article or principle added, or new section appended.
- PATCH: clarification, example added, typo, or non-semantic edit.

We considered simply adding timestamps to the constitution files. We rejected
that because timestamps explain when a file changed but not whether the change
was semantic, additive, or editorial. We also considered allowing the command to
auto-update downstream prompts and skills. We rejected that because governance
changes require Architect judgment; automatic edits could spread a bad
interpretation faster than a human review can catch it.

## Consequences

### Positive

- Constitution files now expose machine-readable version, ratification, and last
  amendment metadata.
- Future amendments must classify semantic impact before landing.
- Skills, prompts, and templates are checked for drift whenever a constitution
  rule changes.
- The Sync Impact Report gives the Architect a concrete review queue instead of
  relying on memory.
- The framework aligns with Spec-Kit's constitution-amendment pattern while
  preserving this repository's file-based governance model.

### Negative or risky

- Constitution amendments now require more ceremony, even for small wording
  changes. Mitigation: PATCH changes remain lightweight but still run the scan.
- The propagation scan can produce false positives because references may be
  broad or indirect. Mitigation: the `NEEDS-REVIEW` verdict explicitly separates
  uncertain references from confirmed conflicts.
- Downstream artifacts can still remain stale if the Architect ignores the Sync
  Impact Report. Mitigation: Governance in `principles.md` makes resolution the
  Architect's responsibility before the amendment commit lands.

### Process changes

- All constitution files now begin with YAML frontmatter.
- `.github/prompts/constitution.prompt.md` defines the amendment workflow.
- `.github/skills/core/constitution-sync/SKILL.md` defines the propagation scan.
- `constitution/principles.md` includes a Governance section documenting version
  semantics, propagation checks, and Sync Impact Report expectations.
- `principal-architect` has an Amend Constitution handoff that triggers the
  workflow.

## Status

Accepted. Implemented in commit that introduces this ADR.
