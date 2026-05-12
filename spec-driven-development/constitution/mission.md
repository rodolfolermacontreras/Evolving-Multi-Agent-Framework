# Mission

## Project

Day-to-Day Agent -- AI-powered personal work management system

## Owner

Rodolfo Lerma, Senior Data Scientist (L63)
WWIC Central Analytics / Design & Analytics, Microsoft
Reporting chain: Rodolfo > Aziz (M+1) > Sam (M+2) > Nandini (M+3)

## Vision

A single-pane-of-glass operating system providing a 360-degree view of work life:

- Priorities and next actions
- Task completion and accountability tracking
- Meetings, notes, and follow-ups
- Reminders and scheduling
- Status reporting and stakeholder communication

The agent removes the cognitive overhead of tracking what to work on, what is done, and
what to report -- so Rodolfo can focus on the work itself.

## Users

Primary user: Rodolfo (single-user system, local data)
Indirect audience: Management chain (Aziz, Sam, Nandini) via generated status reports

## Success Criteria

The system succeeds when:

- Weekly status reports require no manual editing before sending
- The project board reflects true work state without manual sync
- Accountability logs capture daily progress without friction
- Meeting transcripts are automatically summarized and filed
- The inbox processes files without intervention
- All M365 data (calendar, tasks) is surfaced in a single view

## Core Values

1. RELIABILITY: Never lose data, corrupt state, or fail silently
2. SIMPLICITY: Prefer stdlib over dependencies. Prefer simple over clever.
3. TRANSPARENCY: Every LLM call is traceable. Every decision is auditable.
4. PRIVACY: All data stays local or within Microsoft tenant. No external data sharing.
5. VELOCITY: Small, frequent commits. Short feedback loops. TDD enforcement.

## Non-Negotiables

Source of truth: `.github/copilot-instructions.md`

- Never touch master branch
- Never commit directly to integration/improvements
- No package installs without discussion
- Always use .venv (never global Python)
- No emojis in code, docs, or commits
- No new docs unless explicitly asked
- Completed items are never deleted (mark done with date)
- Small, frequent commits -- format: `type: short description`
- Read before modifying
- Clean as you go (no orphan code, unused variables, stale scripts)
