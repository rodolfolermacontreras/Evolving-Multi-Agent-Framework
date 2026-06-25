---
id: ADR-018
type: spec
status: accepted
owner: principal-architect
updated: 2026-06-25
feature: SDD-039
---

# ADR-018: Article VII context-isolation wording -- subagent dispatch as a first-class alternative to a fresh session

- Date: 2026-06-25
- Status: **Accepted** (owner approval recorded 2026-06-25 via Executive Manager: "item 1, yes approved")
- Authors: Principal Architect (SDD-039 design slot)
- Feature: SDD-039 (Article VII "one feature, one session" wording clarification)

> **Frontmatter note:** `status: draft` is the schema-lint carrier value for a not-yet-accepted ADR (the frontmatter status enum has no `proposed`). The body Status is the authoritative ADR lifecycle state: **Proposed**, pending owner acceptance. This ADR is DRAFT-ONLY; nothing it describes has been applied.

## Context

Article VII of `constitution/principles.md` carries the "one feature, one session" corollary. Its current wording (lines 94-101) says each in-flight feature "SHOULD use its own dedicated Copilot session." Read literally, the only sanctioned context-isolation mechanism is a fresh chat session. In practice this produces repeated, unnecessary "please open another session" requests even when an EM-routed subagent dispatch already provides equivalent context isolation -- the subagent runs in its own isolated context window, returns a single report, and cannot leak feature depth back into the routing session.

The intent of Article VII has always been **context isolation**, not the chat-session mechanism specifically. SDD-039 makes that intent explicit: a subagent dispatch is a first-class alternative to a fresh session, because both satisfy the same property -- context from one feature does not contaminate work on another.

This is a clarification of existing intent, not a change of intent. Per `decision-policy.md`, a constitution edit requires an ADR (Article VIII) and recorded owner (Level-2) approval. Per `006-constitution-semantic-versioning.md`, a clarification that does not change a binding rule is a MINOR bump: `principles.md` moves `1.3.0 -> 1.4.0` only when the change is applied. The owner is currently away and has not given the recorded approval Article VIII requires, so this ADR records the proposed decision and the exact apply-plan and stops at the approval boundary.

## Decision

1. **Article VII corollary wording (proposed replacement).** When approved, the apply step replaces the current corollary in `constitution/principles.md` (lines 94-101) with the paragraph below. It makes "context-isolated unit" the governed concept and names both a fresh Copilot chat session and an EM-routed subagent dispatch as equally valid, while preserving every existing guarantee (EM stays high-level; this is not a license to merge features; durable artifacts carry state forward).

   EXACT proposed replacement paragraph:

   ```markdown
   **One feature, one session.** A direct corollary of the rule above: chat
   sessions are ephemeral context, not project state. Each in-flight feature
   SHOULD run in its own context-isolated unit -- either a fresh Copilot chat
   session OR an EM-routed subagent dispatch. Both satisfy the
   context-isolation property: they keep context from one feature from
   contaminating work on another. Neither is privileged over the other; pick
   whichever fits the work. The Principal Executive Manager session stays
   high-level (routing, status, synthesis) and never absorbs feature
   implementation depth -- and this corollary is not a license to cram
   multiple features into one undifferentiated session. When a session ends,
   the durable artifacts (specs, tasks, validation, ledger rows, session
   checkpoints under `spec-driven-development/sessions/`) carry the state
   forward -- not the chat history.
   ```

2. **MINOR version bump.** When applied, `principles.md` frontmatter `version` bumps `'1.3.0' -> '1.4.0'` and `last_amended` is set to the apply date. The bump is MINOR because the change clarifies existing intent and loosens no binding rule (a subagent dispatch was never prohibited; it simply was not named).

3. **Echo the same clarification in the kickoff surfaces.** The shared "one feature, one session" boilerplate that every sprint kickoff inherits, and each kickoff prompt's own restatement of it, are amended to read "fresh chat session OR subagent dispatch -- both satisfy the context-isolation property," so the operational prompts match the constitution. The exact current snippets are enumerated in the Apply plan below.

4. **Nothing is applied by this ADR.** This ADR is the recorded proposal only. The constitution edit, the version bump, and the prompt/template edits happen in a separate, owner-approved apply step.

## Apply plan (executed only after recorded owner approval)

The approved apply step touches the following files. Each entry lists the EXACT current snippet (file + line) the apply step will change. No file outside this list is in scope.

1. **`spec-driven-development/constitution/principles.md`** -- replace the Article VII corollary at lines 94-101 with the proposed paragraph in Decision item 1, AND bump frontmatter `version: '1.3.0' -> '1.4.0'` and update `last_amended`. Current corollary (lines 94-101):

   ```
   **One feature, one session.** A direct corollary of the rule above: chat
   sessions are ephemeral context, not project state. Each in-flight feature
   SHOULD use its own dedicated Copilot session so context from one feature does
   not contaminate work on another. The Principal Executive Manager session
   stays high-level (routing, status, synthesis) and never absorbs feature
   implementation depth. When a session ends, the durable artifacts (specs,
   tasks, validation, ledger rows, session checkpoints under
   `spec-driven-development/sessions/`) carry the state forward -- not the chat
   history.
   ```

2. **`spec-driven-development/feature-prompts/_SHARED_ONBOARDING.md`** (the kickoff template -- the shared boilerplate every `SPRINT-##-KICKOFF.prompt.md` loads "end to end" as step 1). Two occurrences:
   - Lines 95-99:
     ```
     - **Article VII -- One Feature, One Session.** Do not contaminate context.
       Reuse a session ONLY for the same feature, EM-level routing/status, or true
       one-off edits (<3 files). For a different feature, open a new session and
       paste its prompt.
     ```
   - Line 205:
     ```
     - Do NOT contaminate sessions. **One feature, one session.**
     ```

3. **`spec-driven-development/feature-prompts/SPRINT-04-KICKOFF.prompt.md`** -- NO canonical "one feature, one session (Article VII)" corollary snippet exists in this prompt (it predates the standardized boilerplate). The closest session-isolation language is:
   - Line 75: `session) load in a fresh chat.`
   - Line 164: `- Do NOT start Sprint 5 in this session. It runs in its own fresh session`
   See AMBIGUITY 1 below -- the apply step must decide whether SPRINT-04 is edited at all and, if so, which line, before touching it.

4. **`spec-driven-development/feature-prompts/SPRINT-05-KICKOFF.prompt.md`** -- lines 94-95:
   ```
   - **One feature, one session** (Article VII): F-03, F-04, F-05 each run in
     their own fresh chat session.
   ```

5. **`spec-driven-development/feature-prompts/SPRINT-06-KICKOFF.prompt.md`** -- two occurrences:
   - Lines 50-51:
     ```
     3. Execute the sprint sequence below. **Each F-## runs in its own fresh
        chat session** (Article VII: one feature, one session).
     ```
   - Lines 124-125:
     ```
     - **One feature, one session** (Article VII). F-06, F-07, F-08 each run in
       their own fresh chat session. Do not collapse them into a single session
     ```

6. **`spec-driven-development/feature-prompts/SPRINT-07-KICKOFF.prompt.md`** -- two occurrences:
   - Lines 59-60:
     ```
     3. Execute the sprint sequence below. **Each F-## runs in its own fresh
        chat session** (Article VII: one feature, one session).
     ```
   - Lines 161-162:
     ```
     - **One feature, one session** (Article VII). F-09, F-10, F-11 each run
       in their own fresh chat session. Do not collapse them into a single
     ```

## Consequences

- Positive: removes needless re-session friction -- a subagent dispatch becomes an explicitly sanctioned context-isolated unit, so EM routing no longer has to ask the owner to "open another session" when a dispatch already isolates context.
- Positive: the constitution and the operational kickoff prompts say the same thing, so workers and the EM read one consistent rule.
- Positive: MINOR bump (1.3.0 -> 1.4.0) keeps the semantic-versioning ledger honest -- a clarification, not a rule change.
- Negative / risk: the wording must NOT be read as license to cram multiple features into one undifferentiated session. The proposed paragraph keeps the explicit "not a license to cram multiple features into one undifferentiated session" clause to guard against that misreading.
- Neutral: this ADR changes no code and adds no dependency; the apply step edits Markdown only.

## Alternatives Considered

- **REJECTED -- Leave Article VII as-is and treat subagent dispatch as informally allowed.** Rejected because the literal wording ("its own dedicated Copilot session") keeps generating unnecessary re-session requests; informal allowance does not stop a literal reader from blocking a valid dispatch.
- **REJECTED -- Edit the kickoff prompts only, leave `principles.md` unchanged.** Rejected because Article VII is the authoritative source; prompts that contradict the constitution create a divergence the next reader must reconcile. The constitution must carry the clarification.
- **REJECTED -- MAJOR or PATCH version bump.** MAJOR is wrong because no binding rule is removed or reversed. PATCH is wrong because the change adds a newly named, governed alternative (subagent dispatch) to a binding article, which is a MINOR-level clarification under `006-constitution-semantic-versioning.md`.

---

APPLIED 2026-06-25 (owner approval recorded via Executive Manager: "item 1, yes approved"). `principles.md` bumped `1.3.0 -> 1.4.0` and its Article VII corollary replaced; the `_SHARED_ONBOARDING.md` boilerplate and the SPRINT-05/06/07 kickoff restatements were amended to name subagent dispatch as an equivalent context-isolated unit. Per owner/EM scope decision: `SPRINT-04-KICKOFF.prompt.md` was intentionally left untouched (it predates the canonical corollary), and `.github/copilot-instructions.md` was included so its Article VII "One Feature, One Session" section matches the constitution.
