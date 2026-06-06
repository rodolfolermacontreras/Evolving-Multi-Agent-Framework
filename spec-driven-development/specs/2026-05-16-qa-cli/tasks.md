---
id: SDD-20260516QACL-tasks
type: tasks
status: done
owner: principal-software-developer
updated: 2026-06-06
feature: 2026-05-16-qa-cli
---

# Task List: qa.py

- Spec Reference: `spec-driven-development/specs/2026-05-16-qa-cli/spec.md`
- Task ID Format: `T-NNN` (local)
- Owner: Principal Software Developer

---

## Task Breakdown

| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Write test_qa.py first (red). | `cli/test_qa.py` | Proves AC1-AC9 | M | None | AFK | No | pending |
| T-002 | [S] | Implement Stage 1 checks (validation parser, AC cross-ref, task status). | `cli/qa.py` | Proves AC1, AC2, AC3 | M | T-001 | AFK | No | pending |
| T-003 | [S] | Implement Stage 2 checks (bare except, debug print, import scan). | `cli/qa.py` | Proves AC4, AC5, AC9 | S | T-001 | AFK | No | pending |
| T-004 | [S] | CLI wiring, report renderer, exit codes, --help, manual checks. | `cli/qa.py`, `validation.md` | Proves AC6-AC10 | S | T-002, T-003 | AFK | No | pending |
