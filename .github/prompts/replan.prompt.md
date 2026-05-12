---
name: replan
description: "Run after every feature DONE. Reviews constitution, roadmap, skills, and lessons; surfaces what should change before the next feature begins. Slow down to run fast. Inspired by the DeepLearning.AI SDD course (Paul Everitt)."
argument-hint: "Which feature just completed (path or short name)?"
---

You are running the **Replan** ceremony for the Evolving Multi-Agent Framework.

## Workflow Phase

- Primary phase: **Post-DONE ceremony**
- Use after a feature reaches DONE and before selecting the next feature.
- Purpose: slow down to run fast by updating the operating model before more work starts.

## Input

The user argument is the completed feature path, short name, sprint deliverable, commit, or PR reference. If ambiguous, make the best reasonable match from nearby artifacts and state the assumption.

## Required Reading

Read these artifacts before producing the report:

1. Constitution files in `spec-driven-development/constitution/`
   - `mission.md`, `principles.md`, `tech-stack.md`
   - `roadmap.md`, `decision-policy.md`, `quality-policy.md`
2. Roadmap: `spec-driven-development/constitution/roadmap.md`
3. Skill catalog:
   - `.github/skills/`
   - `spec-driven-development/roster/skills.json`
4. Lessons file for the current PI:
   - `spec-driven-development/sprints/PI-{N}/lessons.md`
   - This file may not exist yet; if missing, recommend what should be captured there.
5. Completed feature artifacts, when available:
   - `spec.md`, `plan.md`, `tasks.md`, `validation.md`, `clarification-log.md`, optional `research.md`

## Ceremony Protocol

1. Identify what just changed.
   - Summarize the completed feature in 3 bullets or fewer.
   - Reference the feature directory or commit instead of duplicating content.
2. Review the constitution.
   - Check for missing principles, changed policy, or outdated technical assumptions.
   - Surface suggested updates only; do not edit constitution files.
3. Review the roadmap.
   - Check whether the next planned item still makes sense.
   - Consider dependencies, newly discovered risks, value, and sequence.
4. Review the skills.
   - Identify repeated behavior that should become a new skill.
   - Identify existing skills needing sharper triggers, guardrails, examples, or frontmatter.
5. Review lessons.
   - Read `spec-driven-development/sprints/PI-{N}/lessons.md` if present.
   - If absent, produce lessons that should be appended when created.
6. Recommend the next IDEA.
   - Use roadmap order as the default.
   - Override only when there is clear evidence.
   - Explain why the next IDEA is the highest-leverage next step.

## Output Format

Return exactly these five sections:

```markdown
# Replan Report: {completed feature}

## 1. Constitution updates suggested
- Recommendation: ...
- Evidence: ...
- Approval path: ADR required? yes/no

## 2. Roadmap reorder suggested
- Recommendation: ...
- Evidence: ...
- Next roadmap item still valid: yes/no

## 3. Skill changes suggested
- New skill candidates: ...
- Existing skill improvements: ...
- Roster updates needed: yes/no

## 4. Lessons captured
- Lesson: ...
- Suggested location: `spec-driven-development/sprints/PI-{N}/lessons.md`

## 5. Recommended next IDEA
- IDEA: ...
- Why now: ...
- Suggested next command: `/triage ...` or `/clarify ...`
```

## Guardrails

- Do not modify files unless the user explicitly asks for implementation after the report.
- Do not propose constitution changes as final decisions; policy-level changes require human approval and an ADR.
- Do not reorder the roadmap solely because a newer idea feels more interesting.
- Do not create a new skill for one-off knowledge; prefer skills for repeatable behavior.
- Do not duplicate full specs, plans, ADRs, or diffs in the report; reference paths.
- Keep the report evidence-based and concise.
- Use dates in `YYYY-MM-DD` format.
- No emojis.

## Decision Thresholds

Suggest a constitution update when a recurring rule, quality gate, approval boundary, or canonical technical convention is missing from the constitution.

Suggest roadmap reorder when the completed feature unlocks a dependency, blocks the next item, or reveals a risk that should be reduced first.

Suggest skill changes when agents repeated a multi-step protocol, needed missing role guidance, or found ambiguity in an existing skill.

## Project Rules

- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect SDD lifecycle gates.
- Surface assumptions and escalation triggers explicitly.
- Prefer traceable recommendations over broad brainstorming.
