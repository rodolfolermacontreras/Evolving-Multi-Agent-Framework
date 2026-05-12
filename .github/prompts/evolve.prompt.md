---
name: evolve
description: "Curate the lessons backlog. Reads sprints/PI-{N}/lessons.md, decides which candidates ship as framework changes, which defer, which discard. For ship decisions, drafts the actual file changes and a Sync Impact Report. Honors constitution-versioning rules (b5)."
argument-hint: "Which PI's lessons should I curate? (default: current PI)"
---

You are running the **Evolve** ceremony for the Evolving Multi-Agent Framework.

## Workflow Phase
- Primary phase: **Framework evolution curation**
- Use after `/retro`, `/replan`, or any period where lessons accumulated.
- Purpose: convert project experience into reviewed framework changes with provenance.
- The curator decides what should ship, defer, or discard, but never auto-commits.

## Input
The user argument is the PI to curate, such as `PI-1` or `sprints/PI-1/lessons.md`.
If omitted, read `spec-driven-development/constitution/roadmap.md`, identify the current PI, and use `spec-driven-development/sprints/PI-{N}/lessons.md`.
If ambiguous, make the best reasonable PI match and state the assumption.

## Required Reading
Read these artifacts before making decisions:
1. Lessons backlog for the target PI: `spec-driven-development/sprints/PI-{N}/lessons.md`
2. Roadmap, to confirm current PI and future PI targets: `spec-driven-development/constitution/roadmap.md`
3. The affected files named by each lesson's `Affects` field.
4. Constitution versioning guidance when available: `/constitution` command prompt and ADR-0006 propagation rules.
5. Source feature artifacts when evidence is unclear: `spec.md`, `plan.md`, `tasks.md`, `validation.md`, `RETRO.md`, `clarification-log.md`.
If an artifact is missing, continue with available evidence and record the gap in the Curator Report.

## Lesson Contract
Each candidate should include:
- `Date`
- `Source feature`
- `Tag`
- `Proposal`
- `Evidence`
- `Affects`
- `Estimated effort`
- `Status`
- `Curator decision`
- `PR / commit`
Accepted tags are `skill-update`, `new-skill`, `agent-update`, `constitution-amendment`, `template-update`, `prompt-update`, and `docs-update`.
Skip `shipped` lessons unless the user explicitly asks for an audit.

## Curation Protocol
For each non-shipped lesson:
1. Read `Proposal`, `Evidence`, and `Affects` together.
2. Inspect every affected file that exists.
3. Decide: `SHIP`, `DEFER`, `DISCARD`, or `needs-clarification`.
4. Record the decision in the original lesson entry.
5. Preserve the lesson ID and source feature as provenance for every proposed change.

## Decision Criteria
Choose `SHIP` when:
- Evidence is specific and credible.
- The affected change is small or medium.
- The change is low-risk and consistent with the constitution.
- The implementation can be drafted now without more stakeholder input.
- The proposal improves reusable framework behavior, not one feature only.
Choose `DEFER` when:
- The idea is promising but needs design discussion.
- The proposal depends on unfinished roadmap work.
- The change is large and should be planned in a future PI.
- The affected files are in active conflict or outside the current curation window.
Choose `DISCARD` when:
- The lesson is wrong, obsolete, redundant, or already addressed.
- The evidence does not support a framework change.
- The proposed change would weaken a constitution rule or lifecycle gate.
- The item is project backlog work rather than framework learning.
Choose `needs-clarification` when the lesson cannot be classified from available artifacts.
Route the question to the human via the Executive Manager.

## SHIP Procedure
For each `SHIP` lesson:
1. Draft the actual framework file changes as a unified diff in chat.
2. Do not apply the diff unless the human explicitly approves implementation.
3. Include a provenance line where appropriate: `Provenance: LESSON-{NN}, source feature {path}`.
4. If the lesson implies a constitution amendment:
   - Do not directly edit constitution files.
   - Reference `/constitution` as the required approval path.
   - Reference ADR-0006 propagation rules.
   - Include the expected semantic version bump category if clear.
5. Set status to `curated-ship` only after drafting the diff.
6. Leave `PR / commit` unchanged until the change ships.

## DEFER Procedure
For each `DEFER` lesson:
1. Choose a target PI, defaulting to the next PI in the roadmap.
2. Write a concise defer reason in `Curator decision`.
3. Set status to `curated-defer`.
4. Append or recommend appending the lesson to the target PI `lessons.md`.
5. If the target PI file does not exist, include a copy-ready lesson block in the report.

## DISCARD Procedure
For each `DISCARD` lesson:
1. Write the discard reason in `Curator decision`.
2. Set status to `curated-discard`.
3. Do not delete the lesson.
4. Mention any existing file, command, ADR, or prior lesson that already covers it.

## Needs-Clarification Procedure
For each unclear lesson:
1. Keep status as `open` unless the lessons file supports `needs-clarification`.
2. Write the missing information in `Curator decision`.
3. Route the focused question to the human via the Executive Manager.
4. Do not draft file changes.

## Sync Impact Report
For every curation run, compute aggregate impact across constitution, skills, prompts, agents, templates, and docs.
For each area, list candidate lesson IDs, files that would change, whether propagation is required, and whether `/constitution` is required.

## Output Format
Return exactly this structure at the end:
~~~markdown
# Curator Report: PI-{N}

## 1. Summary
- Total candidates curated: {count}
- Shipped drafts: {count}
- Deferred: {count}
- Discarded: {count}
- Needs clarification: {count}

## 2. SHIP decisions
| Lesson | Source feature | Affected files | Draft summary | Diff reference |
|--------|----------------|----------------|---------------|----------------|
| LESSON-... | ... | ... | ... | See Draft Diff ... |

## 3. DEFER decisions
| Lesson | Target PI | Reason |
|--------|-----------|--------|
| LESSON-... | PI-... | ... |

## 4. DISCARD decisions
| Lesson | Reason |
|--------|--------|
| LESSON-... | ... |

## 5. Needs clarification
| Lesson | Question | Route |
|--------|----------|-------|
| LESSON-... | ... | Executive Manager |

## 6. Draft diffs for SHIP candidates

### Draft Diff: LESSON-...
```diff
...
```

## 7. Aggregate Sync Impact
- Constitution: ...
- Skills: ...
- Prompts: ...
- Agents: ...
- Templates: ...
- Docs: ...

## 8. Follow-up commands
- `/constitution ...` when constitution amendments are required
- Human approval request for any drafted file changes
~~~

## Guardrails
- Do not auto-commit any change.
- Do not apply drafted diffs without explicit human approval.
- Constitution amendments must use `/constitution`; do not directly edit constitution files.
- Honor semantic versioning and propagation checks for constitution-affecting lessons.
- Reference ADR-0006 propagation rules when a constitution change is implicated.
- Every shipped change must reference its lesson ID and source feature.
- If a lesson cannot be classified, mark `needs-clarification` and route to the Executive Manager.
- Do not discard a lesson only because it is inconvenient.
- Keep all dates in `YYYY-MM-DD` format.
- No emojis.

## Project Rules
- Prefer small, auditable framework changes over broad rewrites.
- Preserve the original lessons ledger as an audit trail.
- If parallel agents own affected files, defer or route to the orchestrator instead of creating conflicts.
- For new skills, ensure valid SKILL.md frontmatter and clear trigger conditions.
- For prompt updates, match existing `.github/prompts/*.prompt.md` style.
- For docs updates, link to canonical artifacts instead of duplicating long content.
- For template updates, avoid changing lifecycle semantics without constitution review.