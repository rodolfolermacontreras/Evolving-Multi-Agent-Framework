# Sessions

This folder holds **persistent session memory** for the framework — the cross-session context that lets a fresh agent (Copilot, Claude, Cursor, or any other) pick up where a previous session left off.

Per Article VII (every artifact is a file), session checkpoints are committed to git, not stored in agent-local memory. Per Article II (single human entry point), the Executive Manager reads from here on session start to refresh its big-picture awareness.

---

## Files

| File | Purpose |
|---|---|
| `SESSION-MEMORY.md` | The most recent checkpoint. Read this on session start. Includes commit chain, architecture mental model, current state, what's deferred, ranked next-session recommendations. |
| `framework-foundations-strategy.md` | Strategic memo on evolution loops, greenfield/brownfield convergence, SDD+TDD integration, adoption barriers. Still relevant for PI-2 and PI-3 planning. |
| `inspiration-repos-research-findings.md` | Synthesis of research subagent reports on the 4 cited inspirations (Spec-Kit, Matt Pocock, DeepLearning.AI SDD course, sc-spec companion). Includes factual corrections and convergent findings. |

---

## When to update

- **End of every working session** that another session will pick up: update `SESSION-MEMORY.md` with the new state. Use the `handoff` skill format (see `.github/skills/operational/handoff/SKILL.md`).
- **After any major decision** that affects future direction: append a memo (datestamped filename) here.
- **After research investigations**: persist the findings here so future sessions don't repeat the work.

---

## Naming convention

- `SESSION-MEMORY.md` — always the latest checkpoint (overwritten each session). For history, use `git log` on this file.
- Themed memos: `kebab-case-topic.md` (e.g. `framework-foundations-strategy.md`).
- Datestamped artifacts (research reports, PI summaries): `YYYY-MM-DD-topic.md`.

---

## How agents use this folder

On session start, an agent following `INSTRUCTIONS.md` (at repo root) will:
1. Read `SESSION-MEMORY.md` to get up to speed.
2. Optionally read other memos if relevant to the user's current ask.
3. At end of session, update `SESSION-MEMORY.md` and commit.

This keeps the framework genuinely *evolving* — every session leaves the institutional memory stronger than it found it.
