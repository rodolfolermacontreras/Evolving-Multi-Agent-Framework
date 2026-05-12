---
name: constitution
description: "Amend a constitution file with semantic version bump (MAJOR for principle change, MINOR for new principle/article, PATCH for clarification). Runs propagation check across skills, prompts, and templates; emits Sync Impact Report. Inspired by Spec-Kit /speckit.constitution."
argument-hint: "Which constitution file are you amending and what is the change?"
---

You are running the **Constitution Amendment** workflow for the Evolving Multi-Agent Framework.

## Purpose

Use this command when any file in `spec-driven-development/constitution/` must change. The goal is to amend governance deliberately, apply semantic versioning, run a downstream propagation check, and emit a Sync Impact Report. Design source: Spec-Kit `/speckit.constitution`.

## Input

The user argument should identify the constitution file, proposed change, rationale, and any known downstream references. If ambiguous, choose the closest matching constitution file, state the assumption, and continue.

## Required Reading

Read these artifacts before drafting an amendment:

1. The constitution file being amended.
2. All `.github/skills/**/SKILL.md` files.
3. All `.github/prompts/*.prompt.md` files.
4. All `spec-driven-development/templates/*.md` files.
5. Relevant ADRs in `spec-driven-development/docs/ADR/`.

Do not rely on memory for current article wording. Quote only repository state you have read.

## Amendment Classification

Select exactly one semantic version bump before editing.

### MAJOR

Use MAJOR when a principle, article, invariant, authority boundary, or decision rule changes or is removed. Examples: Article III review order is rewritten, Article VIII ADR requirements are weakened, or Level 2 approval scope changes. A MAJOR amendment means downstream artifacts may be wrong, not merely stale.

### MINOR

Use MINOR when a new article, principle, required section, or governance capability is added without weakening an existing rule. Examples: Article XI is added, a Governance section is appended, or a new required command or quality gate is introduced. A MINOR amendment means downstream artifacts may need expansion.

### PATCH

Use PATCH when the amendment clarifies existing meaning without changing the rule. Examples: typo fix, non-normative example, readability improvement, or broken reference correction. A PATCH amendment still requires the propagation scan.

## Frontmatter Rules

Every constitution file must begin with:

```yaml
---
version: 'MAJOR.MINOR.PATCH'
ratified: YYYY-MM-DD
last_amended: YYYY-MM-DD
---
```

When amending:

1. Preserve `ratified` unless first ratifying a file.
2. Update `version` with the selected semver bump.
3. Update `last_amended` to today's `YYYY-MM-DD` date.
4. Keep frontmatter at lines 1-5.
5. Keep `version` quoted.
6. Add no unrelated frontmatter fields.

## Drafting Protocol

1. Identify the exact current text to change.
2. Explain MAJOR, MINOR, or PATCH classification.
3. Draft the smallest constitution edit that satisfies the request.
4. Update only the amended constitution file.
5. Do not modify skills, prompts, or templates.
6. Produce a draft unified `git diff` for the constitution file.

## Propagation Scan

Invoke the `constitution-sync` skill after drafting the change. Search only:

- `.github/skills/**/SKILL.md`
- `.github/prompts/*.prompt.md`
- `spec-driven-development/templates/*.md`

Search for references by article number, article title, principle name, stable old phrases, stable new phrases, quoted requirements, commands, filenames, gates, examples, and related ADR identifiers. For each hit, record file, line, matched text, reference type, and alignment verdict.

## Alignment Verdicts

Use exactly these verdicts:

- `ALIGNED`: reference remains correct after the amendment.
- `NEEDS-REVIEW`: reference may still be correct, but human judgment is needed.
- `NEEDS-UPDATE`: reference contradicts the amendment or quotes superseded text.

Prefer `NEEDS-REVIEW` when downstream wording is broad or ambiguous. Use `NEEDS-UPDATE` only for explicit conflict or stale quoted text.

## Sync Impact Report

After the draft diff, emit this report:

```markdown
# Sync Impact Report: {constitution file}

## 1. Amendment summary
- File: `spec-driven-development/constitution/{file}`
- Version: `{old_version}` -> `{new_version}`
- Bump: MAJOR | MINOR | PATCH
- Last amended: `{date}`
- Rationale: ...

## 2. Changed content
- Added: ...
- Changed: ...
- Removed: ...

## 3. Propagation scan scope
- Skills scanned: ...
- Prompts scanned: ...
- Templates scanned: ...
- Search keys: ...

## 4. References found
| Verdict | File | Line | Reference | Reason |
|---------|------|------|-----------|--------|
| ALIGNED | ... | ... | ... | ... |

## 5. Auto-updates performed
- Constitution file: ...
- Skills/prompts/templates: none; guardrail prohibits automatic modification.

## 6. Manual review required
- NEEDS-REVIEW: ...
- NEEDS-UPDATE: ...
- Architect owner: principal-architect

## 7. Commit notes
- ADR required: yes/no
- Suggested commit message: `type(scope): summary`
```

If no references are found, include one `ALIGNED` row stating `No references found`.

## Output Format

Return exactly two top-level sections:

1. `# Draft Git Diff`
2. `# Sync Impact Report: {constitution file}`

The diff section must contain a unified diff. The report section must follow the template above.

## Guardrails

- Never auto-modify a skill, prompt, or template.
- Always surface downstream references for human review.
- Never skip the propagation scan, even for PATCH amendments.
- Never amend without updating `version` and `last_amended`.
- Never alter `ratified` unless first ratifying a file.
- Never invent article numbers or titles.
- Never downgrade a MAJOR change to MINOR.
- Never claim alignment without file and line evidence.
- Do not commit unless explicitly asked to land the amendment.
- Use `YYYY-MM-DD` dates.
- No emojis.

## Escalation Rules

Escalate to Architect review when the amendment changes articles, principles, approval boundaries, required lifecycle gates, artifact ownership, TDD, validation, review, or ADR policy, or when any reference is `NEEDS-UPDATE`.

Escalate to human approval when the amendment changes Level 2 approval, production merge, dependency, data retention, or irreversible governance policy.

## Project Rules

- Respect Article VIII: constitution changes require an ADR unless explicitly exempted.
- Treat the constitution as the root governance source.
- Keep amendments narrow and traceable.
- Attach the Sync Impact Report to the amending commit or PR description.
