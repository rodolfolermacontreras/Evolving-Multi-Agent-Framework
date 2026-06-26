---
name: clarify
description: Run a structured clarification session for a spec or feature request.
argument-hint: "What spec or feature request should I clarify?"
---

You are running the **Clarify** command for the SDD workflow.

## Workflow Phase
- Primary phase: **Phase 4 - Clarify**
- Use before `/spec` when the request still has unresolved decisions.

## Goal
Produce a compact clarification log that removes critical ambiguity before specification or planning.

## Pre-Step: Dedup Scan (SDD-020.R8)

Before asking clarification questions, run the cross-feature deduplication scan to surface prior art that may already answer the question:

1. Run `python spec-driven-development/cli/dedup.py scan --scope all`.
   - If **HARD** overlap (exact SDD-NNN ID collision): stop and report the duplicate ID to the owner; do not open clarification.
   - If **SOFT** overlap (fuzzy title match): surface the candidate to the owner and wait for explicit direction before drafting questions.
   - If **ADVISORY** overlap (keyword similarity): note it in the clarification log, append to `backlog/DEDUP-LOG.md`, and continue.

## Clarification Rules
- Ask up to three formal questions before writing the log if major uncertainty remains.
- Ask one question at a time during interactive use.
- Every question must include a recommendation.
- Track status as `answered`, `deferred`, or `unresolved`.
- Critical unresolved items must block `/spec`.

## Focus Areas
Prioritize questions in this order:
1. Scope
2. Key decisions
3. Context and constraints
4. Validation expectations
5. Ownership or approvals

## Output Format
```markdown
# Clarification Log
- Proposed path: `spec-driven-development/specs/YYYY-MM-DD-feature-name/clarification-log.md`
- Status: draft | ready for spec | blocked

## Q1: <theme>
Question:
Recommended answer:
Why this matters:
Answer:
Status: answered | deferred | unresolved

## Q2: <theme>
...

## Summary
- Resolved:
- Deferred:
- Still blocking:
- Recommendation: proceed to /spec | continue clarification
```

## Working Method
1. Restate the request and current state of ambiguity.
2. Ask the most important unresolved question first.
3. Recommend the best default answer.
4. Capture what changes if a different answer is chosen.
5. Stop as soon as the work is ready for `/spec`.

## Guardrails
- Keep the questions decision-oriented.
- Do not drift into plan or task detail.
- If the work implies approval-required changes, call them out explicitly.


## Project Rules
- Read `.github/copilot-instructions.md` first when project context is needed.
- Respect the SDD lifecycle and do not skip gates without saying why.
- No emojis.
- Prefer concise, traceable output over generic brainstorming.
- Surface blockers, assumptions, and escalation triggers explicitly.
