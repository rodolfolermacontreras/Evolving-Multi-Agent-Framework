# Day-to-Day Brownfield Bootstrap -- Clarification Log

**Sprint:** PI-3/S2
**Owner:** principal-product-manager (lead), principal-architect (spec)
**Date:** 2026-05-26
**Status:** ANSWERED -- ready for SPEC

---

## Required Decision (HITL Gate -- S2/T-001)

### Q1: Which Day-to-Day feature to dogfood?

S2 needs one small feature from the Day-to-Day Agent backlog to walk through
the full SDD lifecycle (IDEA -> SPEC -> TASKS -> IMPLEMENT -> REVIEW -> DONE)
inside the Day-to-Day repo after bootstrapping SDD onto it.

**Criteria for a good dogfood feature:**
- Small scope (1-3 files changed, completable in a single sprint)
- Exercises the spec/plan/tasks/implement/review lifecycle meaningfully
- Does not depend on external services or complex infrastructure
- Ideally touches an area where the Day-to-Day project has existing tests

**Candidates the PM suggests (pick one or propose your own):**
- (a) A UI improvement or new dashboard widget
- (b) A new API endpoint or data model extension
- (c) A test coverage improvement for an under-tested module
- (d) A documentation improvement with a clear AC

### Q2: Is the Day-to-Day repo available locally?

The bootstrap script needs `../day-to-day-microsoft` to exist. Confirm:
- Is the repo cloned at `C:\Training\Projects\day-to-day-microsoft`?
- Is it on a clean branch (main/master)?

---

## Answers

| Q | Answer | Date |
|---|--------|------|
| Q1 | **(b) New API endpoint: "Export report as Markdown download" (backlog item F8).** Small scope (2-3 files: one route, one test, optionally a download button in a template). Pure stdlib, no new dependencies. Clear AC: `GET /api/reports/{date}/export.md` returns 200 with `Content-Type: text/markdown` and `Content-Disposition: attachment`. Exercises the full SDD loop end-to-end. | 2026-06-01 |
| Q2 | Repo is **not** at `C:\Training\Projects\day-to-day-microsoft` -- actual path is `C:\Training\Microsoft\Day_to_Day`. Repo is clean: branch `integration/improvements`, synced with origin, master merged at `4be0e56`. Bootstrap tooling should target the actual path. | 2026-06-01 |
