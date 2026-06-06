---
id: SDD-20260516FLEE-clarification
type: clarification
status: done
owner: principal-architect
updated: 2026-06-06
feature: 2026-05-16-fleet-cli
---

# Clarification Log: fleet.py

- Date: 2026-05-16
- Author: Principal Executive Manager (routing), human decisions
- Feature: `spec-driven-development/specs/2026-05-16-fleet-cli/`
- Status: ready for spec

---

## Q1: Scope -- automate dispatch or generate packets for human review?

Question: Should fleet.py v1 auto-invoke VS Code agents (full automation) or generate dispatch packets + ledger rows for human-launched agents?
Recommended answer: Option A -- packet generation + ledger write. No programmatic Copilot Chat invocation exists.
Why this matters: Option B is blocked by a platform limitation. Option A is shippable and makes dispatch traceable.
Answer: Option A as recommended.
Status: answered

## Q2: Dispatch packet format -- JSON, Markdown, or both?

Question: What format should dispatch packets take?
Recommended answer: Option C -- JSON record to fleet.db via existing ledger functions + Markdown brief to stdout/file for the human.
Why this matters: JSON-only loses human readability. Markdown-only loses traceability. Both gives ledger traceability and a usable agent brief.
Answer: Option C as recommended.
Status: answered

## Q3: Task input -- parse tasks.md or require explicit CLI args?

Question: Should fleet.py read tasks.md from the feature directory automatically, or require all dispatch metadata as CLI args?
Recommended answer: Option A -- parse tasks.md automatically; human only specifies feature dir, task IDs, and agent. Fall back to explicit args if tasks.md is missing.
Why this matters: Option B makes every dispatch verbose (7+ flags). Option A makes it a one-liner.
Answer: Option A as recommended.
Status: answered

## Summary

- Resolved: 3 of 3
- Deferred: 0
- Still blocking: 0
- Recommendation: proceed to /spec
