---
id: SDD-20260608SELFREVIEW-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-08
feature: 2026-06-08-end-of-session-self-review
---

# CLARIFY: End-of-Session Self-Review Loop (SDD-021)

- Date: 2026-06-08
- Owners: Principal Product Manager + Principal Architect
- Sprint: PI-5 Sprint 5 (= overall Sprint 9)
- Source item: SDD-021 -- End-of-session self-review loop
- Status: CLOSED for SPEC/PLAN/TASKS

---

## Context Verified

- Sprint 8 ratification is recorded in commit `8b7d5b9` with owner evidence: "yes Sprint 8 was ratified, we are good".
- Sprint 9 F-16 / SDD-023 is complete in commit `6345366` and defines the reusable User Gate vocabulary.
- SDD-021 originated from the 2026-06-03 Scott feedback bundle: after a feature session, review the session for repeated tool failures, missing instructions, redundant calls, and candidate agent or skill deltas.
- The existing framework already has `lesson-capture` and `/evolve`; SDD-021 should feed those rails instead of silently editing agent or skill files.
- This F-17 pass is design-only. It does not edit `.github/skills/**`, `.github/agents/**`, `constitution/**`, `cli/**`, generated executive state, or external systems.

---

## Q-F: Trigger

Question: Should self-review run at the end of every feature session, every sprint close, only when friction is detected, or only through explicit `/evolve`?

Recommended answer: Make the self-review required at two lifecycle moments and available on demand:

- Required after every feature session that reaches a handoff, DONE, BLOCKED, or OWNER-ATTENTION state.
- Required during sprint close, summarizing feature-session review outputs into sprint-level lessons.
- Optional when an agent detects material friction mid-session, such as repeated tool failures, blocked approval gates, duplicated work, or instruction ambiguity.
- Explicit `/evolve` remains the curation path, not the initial review trigger.

Why this matters: Waiting until `/evolve` loses evidence. Running on every tiny message creates ceremony noise. The required feature-session and sprint-close triggers capture real learning while keeping `/evolve` as the reviewed promotion ceremony.

Answer: Adopt the recommendation. The self-review loop is mandatory at feature handoff/close and sprint close, optional for material friction, and never a license to bypass validation or approval gates.

Status: CLOSED.

---

## Q-G: Output Shape

Question: Should output be a skill output, `RETRO.md` section, session memory entry, ledger event, or backlog candidate?

Recommended answer: Use a small structured self-review record with multiple durable destinations depending on severity:

- Primary output: `session-self-review` skill output in the active chat or handoff block.
- Feature close: append a concise self-review note to `exec/sprint-progress.md` and, when a feature has a `RETRO.md`, include the same finding there.
- Sprint close: summarize open findings in the sprint retro or current PI lessons file.
- Durable framework-learning candidates: append to `spec-driven-development/sprints/PI-{N}/lessons.md` through `lesson-capture`.
- Product or process work: route to `BACKLOG.md` through PM triage, not directly to implementation.
- Gate-related friction: cite SDD-023 fields (`gate_id`, `gate_type`, `blocking_scope`, `approver`, `evidence_type`, `evidence_ref`, `status`, `next_action`) so missing approvals and approval pressure are visible.

Why this matters: One output shape is easy to author, but not every finding deserves the same destination. A lesson candidate, backlog item, gate blocker, and no-op observation have different owners.

Answer: Adopt the recommendation. The skill emits one structured record; the destination is selected by finding category and severity.

Status: CLOSED.

---

## Q-H: Transcript Access

Question: What may the self-review use when raw transcripts are unavailable or privacy-sensitive?

Recommended answer: The self-review MUST be useful without raw transcript access. It may use only available, appropriate evidence:

- Committed artifacts changed in the feature session.
- `git status`, `git diff --stat`, and commit metadata.
- Commands run and validation results that the agent reports in final or progress blocks.
- The feature's `clarification-log.md`, `spec.md`, `validation.md`, `plan.md`, `tasks.md`, and any `RETRO.md`.
- `exec/sprint-progress.md`, `sprints/PI-{N}/lessons.md`, and `sessions/SESSION-MEMORY.md` when relevant.
- Raw chat transcripts only when the tool environment exposes them and no privacy boundary is crossed.

The self-review MUST NOT require M365, WorkIQ, ADO, GitHub issue comments, raw terminal scrollback, or private transcript export to run. It MUST NOT copy sensitive user text into lessons when a sanitized summary is enough.

Why this matters: The feature exists to make learning durable, not to create a privacy-sensitive transcript-mining requirement. Artifact-first review also keeps the loop portable to host projects.

Answer: Adopt the recommendation. Transcript access is optional enrichment only. Artifact evidence is the portable baseline.

Status: CLOSED.

---

## Q-I: Promotion Path

Question: Which findings become agent deltas, skill updates, backlog items, or no-op lessons?

Recommended answer: Classify each finding before promotion:

- `no-op`: one-off issue, already handled, or no reusable framework change.
- `session-note`: useful handoff detail for the next session, but not a framework change.
- `lesson-candidate`: reusable process learning; append through `lesson-capture` for `/evolve`.
- `backlog-candidate`: new feature or larger process improvement; route to PM triage before scheduling.
- `gate-friction`: missing approval, ambiguous evidence, or pressure to proceed without evidence; express using SDD-023 gate fields.
- `agent-skill-delta`: proposed change to `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, templates, or instructions; record as a lesson candidate and let `/evolve` curate it.

Durable changes MUST NOT be applied directly by self-review. `/evolve`, PM triage, `/constitution`, or an approved implementation task owns promotion.

Why this matters: Self-review should improve the framework without becoming an unreviewed self-modification loop. The loop proposes; existing governance disposes.

Answer: Adopt the recommendation. Agent and skill edits are never silent self-review side effects.

Status: CLOSED.

---

## Clarify Close

- Q-F through Q-I are CLOSED.
- SDD-021 reuses SDD-023 gate vocabulary for approval-related findings and gate friction.
- F-17 does not perform constitution edits, ADR creation, new dependencies, schema migrations, M365 permission changes, production-branch changes, external writes, or direct agent/skill modifications.
- F-19 implementation must stop for owner approval if it discovers any Level-2 trigger.