# Clarification Log: state_builder.py

- Date: 2026-05-16
- Author: Principal Executive Manager (routing), human decisions
- Feature: `spec-driven-development/specs/2026-05-16-state-builder/`
- Status: ready for spec

---

## Q1: Data sources

Question: Should state_builder read only fleet.db, or also scan Markdown artifacts on disk?
Recommended answer: Both.
Why this matters: Ledger-only output is incomplete -- feature names, gate status, and backlog RICE scores live in Markdown files. A ledger-only builder would produce dispatch counts without the pipeline context the Executive Manager depends on.
Answer: Both sources. The builder reads fleet.db AND scans specs/, backlog/, sprints/, and roster/ directories.
Status: answered

## Q2: Output format

Question: Should the builder produce the full 7-section state.md or a smaller subset?
Recommended answer: Full 7 sections (header, spec pipeline, sprint plan, fleet summary, recently completed, blockers, next milestones).
Why this matters: A partial builder still requires manual edits, defeating the purpose.
Answer: Full 7-section output.
Status: answered

## Q3: Sprint Plan section source

Question: Should the Sprint Plan section be fed via CLI args (A), a new structured file (B), or derived from BACKLOG.md sprint assignments (C)?
Recommended answer: Option C -- derive from BACKLOG.md.
Why this matters: Options A and B introduce a new input to maintain. Option C reuses the existing single source of truth.
Answer: Option C as recommended.
Status: answered

## Summary

- Resolved: 3 of 3
- Deferred: 0
- Still blocking: 0
- Recommendation: proceed to /spec
