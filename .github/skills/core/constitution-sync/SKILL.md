---
name: constitution-sync
description: "Use when a constitution file is being amended. Scans all skills, prompts, and templates for references to the amended content. Returns a structured list of references and an alignment verdict per reference."
argument-hint: "Which constitution file is being amended?"
license: MIT
metadata:
  author: emf-framework
  version: '1.1'
---

# Constitution Sync

Use this skill to perform the propagation check for a constitution amendment. It does not edit downstream artifacts. It finds references, evaluates likely alignment, and returns structured results for the Sync Impact Report.

## When to Use

Use when any file under `spec-driven-development/constitution/` is amended, including PATCH-only wording changes. The `/constitution` command invokes this skill after drafting the amendment and before landing it.

Do not use this skill for ordinary feature specs, sprint updates, or roadmap entry additions that do not amend constitution content.

## Inputs

Collect these inputs before scanning:

- Constitution file path being amended.
- Old version and proposed new version.
- Amendment bump type: MAJOR, MINOR, or PATCH.
- Article number, section heading, or principle name.
- Old text removed or changed.
- New text added or changed.
- Related ADR numbers, command names, template names, and gate names.

## Scan Scope

Search only these propagation surfaces:

- `.github/skills/**/SKILL.md`
- `.github/prompts/*.prompt.md`
- `spec-driven-development/templates/*.md`

Do not scan implementation code unless the caller explicitly extends scope. Do not modify any scanned file.

## Reference Detection Patterns

Build search keys from the amendment:

1. Article references: `Article III`, `Article 3`, `III`, and exact heading.
2. Principle names: article title, section title, and stable short names.
3. Quoted text: distinctive phrases from old and new text.
4. Policy nouns: commands, gates, approval levels, artifacts, and ADRs.
5. File references: exact constitution path and basename.

Search case-insensitively for prose references and case-sensitively for exact commands, paths, and identifiers.

## Alignment Verdicts

Return one verdict per reference:

- `ALIGNED`: downstream text remains correct after the amendment.
- `NEEDS-REVIEW`: downstream text may be correct, but requires human judgment.
- `NEEDS-UPDATE`: downstream text contradicts the amended constitution or quotes superseded wording.

Use `NEEDS-REVIEW` for broad summaries or partial references. Use `NEEDS-UPDATE` for explicit conflicts, stale quoted text, old version numbers, or obsolete commands.

## Output Format

Return Markdown in this structure:

```markdown
## Constitution Sync Results

- Constitution file: `spec-driven-development/constitution/principles.md`
- Bump: MINOR
- Search keys: `Article X`, `Validation Is a Pre-Implementation Contract`, `validation contract`

| Verdict | File | Line | Reference type | Matched text | Reason |
|---------|------|------|----------------|--------------|--------|
| ALIGNED | `.github/prompts/spec.prompt.md` | 42 | principle name | `Validation Contract` | The prompt already requires validation before implementation. |
| NEEDS-REVIEW | `.github/skills/core/example/SKILL.md` | 18 | article number | `Article X` | Mentions the article but does not restate the updated requirement. |
| NEEDS-UPDATE | `spec-driven-development/templates/feature-spec.md` | 12 | quoted text | `validation after implementation` | Contradicts the amended pre-implementation rule. |
```

If no references are found, return one table row with verdict `ALIGNED`, file `none`, line `n/a`, matched text `No references found`, and a reason stating no downstream artifact references the amended content.

## Quality Checks

Before returning results:

- Confirm all three scan scopes were checked.
- Confirm every search key was used or explain omissions.
- Confirm each finding includes file and line.
- Confirm no skill, prompt, or template was modified.
- Confirm the result can be pasted into a Sync Impact Report.

## Stale Marker Detection (LESSON-006)

When invoked during a PI or sprint **closure ceremony**, perform an additional scan for stale `(current)` markers:

### Files to scan

- `spec-driven-development/constitution/roadmap.md` -- look for `(current)` on PI headings
- `spec-driven-development/exec/state.md` -- look for PI/sprint indicators
- Any `CURRENT_PI.md` files in the repo

### Detection logic

1. Identify the PI and sprint being closed from the ceremony context.
2. Search scanned files for `(current)` markers that reference the closing PI/sprint.
3. If a `(current)` marker still references a PI or sprint that is closing, flag it as `NEEDS-UPDATE` with the reason: "Stale (current) marker -- this PI/sprint is closing."
4. Include stale-marker findings in the Sync Impact Report table alongside constitution reference findings.

### When NOT to use

This check is only relevant during closure ceremonies (`/replan`, sprint DONE, PI close). Do not flag `(current)` markers during mid-sprint constitution amendments -- they are expected to be present.
