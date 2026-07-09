---
id: SDD-20260708DECREQ-clarification
type: clarification
status: done
owner: principal-architect
updated: 2026-07-08
feature: 2026-07-08-decision-request-format
---

# CLARIFY: SDD-053 -- Decision-request format for human-facing agents

- Date: 2026-07-08
- Author: Principal Architect, at F-56 (design slot)
- Status: **DONE** -- Q-A, Q-B, Q-C answered
- Spec ID: SDD-053
- Sprint: PI-8 / Sprint 4 (Sprint 21), design slot F-56; implementation F-57
- Decision source: owner requirement filed 2026-07-08 (BACKLOG SDD-053 row, "go for the recommendation") + Sprint 21 kickoff. Builds on SDD-044 (PI-7), which made human-facing language plainer but did not fix HOW a decision is surfaced.

---

## Ground Rules

- This file is the source of truth for SDD-053 design decisions.
- F-56 is design-only. **No skill edit, no charter edit, no code, no commit, no push** is authorized here. The `em-communication-discipline` skill edit, the two charter bindings, and the structural test land in F-57.
- SDD-053 amends a SKILL and two agent charters, not the constitution. The decision-request format is a discipline binding human-facing outputs; it does not change any authority level or gate.

---

## Decision Summary (Q-A, Q-B, Q-C)

| Q | Topic | Locked Decision | Level |
|---|-------|-----------------|-------|
| Q-A | Change level | Level-1 documentation/behavior change under `.github/` (skill + two charters + one test). No `constitution/**` edit, no ADR, no version bump. Owner pre-push approval still required as house discipline. | Level-1 |
| Q-B | Exact wording | Lock the DECISION-REQUEST FORMAT once, in the skill. Both charters reference the skill by name as single source of truth -- no duplicated spec that can drift. | Level-1 |
| Q-C | Enforcement depth | Add a small stdlib-only STRUCTURAL test that asserts (a) the skill contains the required format tokens and rules, and (b) BOTH EM charters reference the skill by name for the decision-request format. No brittle prose-quality linter. | Level-1 |

---

### Q-A: Change level -- Level-1 vs Level-2

**Context.** F-57 edits `.github/skills/operational/em-communication-discipline/SKILL.md`, binds two agent charters, and adds one stdlib structural test. The question is whether this is a Level-1 documentation/behavior change (no ADR, no version bump) or a Level-2 change (constitution / authority / gate impact).

**Options.**

- Option A: Treat as Level-1. Skill + charter text + a test are behavioral documentation under `.github/`; no authority level, gate, or constitution article changes. No ADR, no version bump. Owner pre-push approval still required.
- Option B: Treat as Level-2. Write an ADR and/or bump a version because the format is a new mandatory rule.

**Architect recommendation:** Option A. Precedent SDD-044 broadened the exact same skill's applicability without a constitution edit and without an ADR (see `specs/2026-06-26-plain-language-comms-discipline/clarify.md`, "ADR required: no"). SDD-053 is strictly smaller in surface: it adds a container/format for the recommendation the skill already mandates. It changes no authority level, no gate, no constitution article, and adds no dependency. Level-1 is the correct and expected path.

**Status:** ANSWERED.
**Decision:** **Level-1.** No `constitution/**` edit, no ADR, no version bump, no third-party dependency (stdlib-only, Article V). Owner pre-push approval before any push remains mandatory house discipline (not a Level-2 trigger). No genuine constitution impact was found; STOP/Level-2 is NOT raised.
**Rationale:** Minimal-surface behavioral amendment to an existing skill plus two charter cross-references and a cheap test; matches the SDD-044 precedent exactly.

---

### Q-B: Exact wording -- lock the format once, reference it twice

**Context.** The skill and both EM charters must be byte-consistent about the format. If each charter re-states the full spec, the three copies will drift.

**Options.**

- Option A: Define the DECISION-REQUEST FORMAT ONCE in the skill (single source of truth). Both charters reference the skill by name and instruct the agent to use the skill's format; they do NOT restate the full block.
- Option B: Copy the full format block into each charter for local convenience.

**Architect recommendation:** Option A. Single source of truth is the DRY, drift-proof choice and mirrors how the charters already reference `em-communication-discipline` (they name the skill, they do not duplicate its body). Option B guarantees three copies that will diverge on the next edit.

**Status:** ANSWERED.
**Decision:** **Option A.** The full format is locked below and lives ONLY in the skill. Each charter adds a one-line binding that names `em-communication-discipline` and points at its DECISION-REQUEST FORMAT as the single source of truth. No charter restates the block.

**LOCKED DECISION-REQUEST FORMAT (canonical wording -- lives in the skill only):**

- A short status ABOVE the block (lead-with-answer, exactly as the skill already requires).
- A clearly-marked decision block at the very END of the message, with nothing after it:

    ```
    DECISION NEEDED: <one line>
    Options:
      1. <option> -- impact: <one line>
      2. <option> -- impact: <one line>
    Recommendation: <which + one-line why>
    ```

- Rules that travel with the format:
    - ONE decision block per message; never bury a question in prose.
    - The block sits at the very end -- nothing follows it.
    - If no decision is needed, there is NO block -- just a short status.
    - The format is the CONTAINER for the recommendation, not a return to menuing. It stays consistent with the skill's existing "recommend, do not menu" rule: `Recommendation:` is mandatory and names one path.

**Normalization note.** The owner's paste uses an em-dash (`—`) as the impact separator. The canonical form normalizes this to a double hyphen (`--`) to stay byte-consistent with the rest of the skill (which uses `--` throughout) and with the repo markdown convention (no special glyphs; `-` bullets). The structural test (Q-C) asserts the semantic tokens (`DECISION NEEDED:`, `Options:`, `impact:`, `Recommendation:`), not the dash glyph, so either dash renders acceptably; F-57 MUST use `--`.

**Rationale:** One authoritative definition, referenced by name in both charters; no drift-prone duplication.

---

### Q-C: Enforcement depth -- structural test, not a prose linter

**Context.** Prose quality (is a real status short? is the recommendation good?) cannot be linted reliably. But the PRESENCE of the format in the skill and the PRESENCE of the binding in both charters can be asserted cheaply.

**Options.**

- Option A: Add a small stdlib-only structural test that asserts (a) the skill file contains the required format tokens and rule phrases, and (b) both EM charters reference the skill by name for the decision-request format.
- Option B: Attempt a prose-quality linter that scores real messages for "buried decision" / brevity.
- Option C: No test; rely on manual review only.

**Architect recommendation:** Option A. It is cheap, deterministic, stdlib-only, and it locks the two things that actually matter structurally: the format exists in the single source of truth, and both charters point at it. Option B is brittle and out of scope (we do not lint live prose). Option C leaves the SSOT and the bindings unguarded against a future accidental deletion.

**Status:** ANSWERED.
**Decision:** **Option A.** F-57 adds `spec-driven-development/cli/test_sdd053.py` (stdlib-only, `unittest`, following the `test_sdd045.py` convention). It asserts:

- (a) The skill (`.github/skills/operational/em-communication-discipline/SKILL.md`) contains, case-insensitively, all of: `DECISION-REQUEST FORMAT` (section heading), `DECISION NEEDED:`, `Options:`, `impact:`, `Recommendation:`, `one decision block per message`, `at the very end`, and `no decision` (the no-decision -> no-block rule).
- (b) BOTH charters -- `.github/agents/sprint-executive-manager.agent.md` and `.github/agents/principal-executive-manager.agent.md` -- contain a binding that names `em-communication-discipline` AND the phrase `decision-request format` (case-insensitive), proving each charter references the skill as the source of the format.
- (c) A stdlib-only audit of the new test module (no third-party imports), mirroring `test_sdd045.py`'s stdlib audit.

**Rationale:** Guards the single source of truth and both bindings with a deterministic, dependency-free test; avoids a brittle prose linter.

---

## Per-item SDD-ID decision

SDD-053 is small: one skill section, two one-line charter bindings, and one structural test. A single SDD-053 with acceptance criteria AC-1..AC-8 is sufficient. No genuine reason was found to fracture it into sub-IDs (the three artifacts move together and share one validation contract). **Decision: keep a single SDD-053.**

---

## Open Questions

- None blocking. Q-A, Q-B, Q-C answered.
- **ADR required: no.** SDD-053 is a skill + charter behavioral amendment; it changes no authority level, gate, or constitution article (Q-A).

## Out of Scope

- The actual skill edit, the two charter bindings, and the structural test (all F-57).
- Any `constitution/**` edit, new skill, dependency, schema migration, version bump, or Article X locked-function change.
- A prose-quality linter that scores live owner-facing messages (Q-C Option B, rejected).
- Rewording the skill's existing brevity / "recommend, do not menu" rules (SDD-044 owns those; SDD-053 only adds the format container).
