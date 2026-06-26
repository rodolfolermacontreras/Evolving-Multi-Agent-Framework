---
id: SDD-20260626PLAINLANG-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-plain-language-comms-discipline
---

# CLARIFY: SDD-044 -- Plain-language human-facing communication discipline

- Date: 2026-06-26
- Authors: Principal Product Manager + Principal Architect (jointly), at F-34
- Status: **DONE** -- Q-D and Q-E answered
- Spec ID: SDD-044
- Sprint: PI-7 / Sprint 1 (Sprint 14), design slot F-34 (paired with SDD-043); implementation F-36
- Decision source: BACKLOG SDD-044 row (filed 2026-06-26, owner requirement) + [`SPRINT-14-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-14-KICKOFF.prompt.md) + owner approval to start Sprint 14 (2026-06-26, "lets go").

---

## Ground Rules

- This file is the source of truth for SDD-044 design decisions.
- F-34 is design-only. **No skill body edit, no constitution edit, no commit, no push** is authorized here. The `em-communication-discipline` skill body change lands in F-36.
- SDD-044 amends a SKILL, not the constitution. The plain-language rule is a discipline binding human-facing outputs; it does not change any authority level or gate.

---

## Decision Summary (Q-D, Q-E)

| Q | Topic | Locked Decision | Level |
|---|-------|-----------------|-------|
| Q-D | Edit target | Amend the EXISTING `em-communication-discipline` skill's applicability/scope so it binds ALL human-facing principals/EMs, not EM only. Do NOT create a new skill. | Level-1 |
| Q-E | Rule boundary | Every human-facing output (status, progress, owner questions, recommendations) MUST be short, plain, and to the point. Agent-to-agent / internal engineering detail explicitly remains allowed. | Level-1 |

---

### Q-D: Edit target -- amend the existing skill vs create a new one

**Context.** The `em-communication-discipline` skill (`.github/skills/operational/em-communication-discipline/SKILL.md`, origin LESSON-005) currently scopes its rules to the Executive Manager. The owner's requirement is that the short-plain-language discipline apply to ALL human-facing principals/EMs.

**Options.**

- Option A: Amend the existing skill's applicability/scope section so it binds all human-facing principals/EMs (one skill, broadened scope).
- Option B: Create a new sibling skill for "all principals" and leave the EM skill EM-only.

**PM recommendation:** Option A. One skill, broadened scope, is less to maintain and avoids two near-duplicate skills drifting apart.

**Architect recommendation:** Option A. The rule is identical regardless of which human-facing agent emits the output; broadening the existing skill's applicability is the minimal, DRY change. A second skill (B) would duplicate the LESSON-005 guidance and create a consistency burden.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** Amend the EXISTING `em-communication-discipline` skill. F-36 edits its applicability/scope (and, where needed, the `description` frontmatter) so the discipline binds every human-facing principal/EM. No new skill is created. The skill `name` stays `em-communication-discipline` (it must keep matching its directory name per schema-lint / ADR-0006); only its stated scope broadens.
**Rationale:** DRY, minimal-surface, single source of truth for the comms discipline.

---

### Q-E: Rule boundary -- what the discipline covers

**Context.** The discipline must make human-facing outputs short and plain without starving agent-to-agent coordination of the technical detail it needs.

**Options.**

- Option A: Bind only human-facing outputs (status, progress, owner questions, recommendations) to short/plain; explicitly allow agent-to-agent / internal engineering detail.
- Option B: Apply short/plain to ALL outputs including agent-to-agent (would strip detail from internal routing).

**PM recommendation:** Option A. The owner reads human-facing surfaces; internal dispatches need full detail.

**Architect recommendation:** Option A. Plain-language is a human-readability rule; agent-to-agent traffic (dispatch briefs, tasks tables, validation contracts) must keep its precision. Option B would degrade internal coordination quality.

**Joint recommendation:** **Option A.**

**Status:** ANSWERED.
**Decision:** The discipline binds every HUMAN-FACING output -- status reports, progress updates, owner questions, and recommendations -- to be short, plain, and to the point (recommend, do not menu; lead with the answer; no long engineering detail unless asked). Agent-to-agent and internal engineering detail (dispatch briefs, tasks/validation tables, ADR bodies) explicitly remains allowed and unaffected.
**Rationale:** Protects owner readability without weakening internal coordination; matches the existing skill's "recommend, do not menu" intent, now extended to all human-facing principals.

---

## Open Questions

- None blocking. Q-D, Q-E answered.
- **ADR required: no.** SDD-044 is a skill applicability amendment; it does not change authority levels, gates, or any constitution article. (It rides alongside ADR-020, which is SDD-043's ADR.)

## Out of Scope

- The actual `em-communication-discipline` SKILL.md body/scope edit (F-36).
- Any `constitution/**` edit (SDD-044 amends a skill, not the constitution).
- SDD-043 agent design (paired but separate spec dir).
- SDD-045 Detach epic (F-35).
