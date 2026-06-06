---
id: SDD-PI-3-CURRENT_PI-sprint
type: sprint
status: done
owner: principal-product-manager
updated: 2026-06-06
sprint: PI-3
---

# PI-3: Portability Validation + Live UI v2 + Navigation Layer

- Status: **DONE** (all 5 sprints complete)
- Theme: Validate framework portability via brownfield bootstrap, spec the Live UI v2, curate PI-2 lessons, establish navigation layer, unblock dashboard deployment
- Started: 2026-05-25
- Closed: 2026-06-02
- Owner: principal-executive-manager

---

## Goal

Validate the framework's portability by bootstrapping SDD onto the Day-to-Day Agent project (brownfield), spec a Live UI v2 with a dedicated UI Designer Principal, curate PI-2 lessons into framework improvements, establish a durable navigation layer for the repo, and unblock the dashboard auto-deploy pipeline.

---

## Sprint Summary

| Sprint | Title | Status | Key Outcome |
|--------|-------|--------|-------------|
| S1 | Dashboard Freshness Unblock | **DONE** | Azure provisioning (app reg, federated credential, RBAC), deploy workflow YAML, About section. 68 tests. Deploy GREEN (1m13s). |
| S2 | Day-to-Day Brownfield Bootstrap | **DONE** | 83 files bootstrapped onto Day-to-Day (constitution, agents, skills, scaffold). Markdown export dogfood feature delivered. 1069 tests. Two-stage review passed. |
| S3 | PI-2 Lessons Curation | **DONE** | 7 parallel dispatches. 4 skills updated to v1.1. Tech debt spec filed for PI-4. All 6 open lessons curated. |
| S4 | Live UI v2 Spec | **DONE** | 6 dispatches. 7 artifacts: clarification, DESIGN_TOKENS, spec (37KB), mockup (34KB), plan, tasks, validation (LOCKED). design-tokens skill v1.0 shipped. |
| S5 | Management Navigation Layer | **DONE** | 14 tasks. ADR-0011, Rule 13, Management/ structure, build-index CLI subcommand. Three-tier navigation pyramid operational. |

---

## Key Decisions

| ADR | Title | Status |
|-----|-------|--------|
| ADR-0010 | Hire Principal UI Designer | Accepted 2026-05-26 |
| ADR-0011 | Three-Tier Navigation Layer | Accepted 2026-05-25 |

---

## Spec Artifacts

| Spec ID | Title | Location | Status |
|---------|-------|----------|--------|
| SDD-S1 | Dashboard Freshness Unblock | `docs/Management/PI-3/Sprint-1-dashboard-freshness-unblock/SPEC.md` | DONE |
| SDD-S2-001 | Day-to-Day Brownfield Bootstrap | `specs/2026-05-26-day-to-day-brownfield-bootstrap/` | DONE |
| SDD-009 | Navigation Layer | `docs/Management/PI-3/Sprint-5-management-navigation-layer/SPEC.md` | DONE |
| SDD-010 | UI Designer Hire | `docs/ADR/010-hire-principal-ui-designer.md` | DONE |
| SDD-013 | Live UI v2 | `specs/2026-05-26-live-ui-v2/` | DONE (spec phase; implementation planned for PI-4) |

---

## Commit Highlights

### S1 (Dashboard Freshness)
- Azure app registration, federated credential, Contributor roles on Container App + ACR
- `.github/workflows/deploy-dashboard.yml` (OIDC + ACR build/push + container app revision)
- About section in `cli/state_builder.py`, 5 new tests
- Deploy workflow tests, 3 new tests
- Total: 68/68 tests on framework repo

### S2 (Brownfield Bootstrap)
- Part 1: 77 files bootstrapped onto Day-to-Day (constitution, agents, skills, scaffold, ADR-001, CONTEXT.md, backlog)
- Part 2: `agent/status_report_markdown.py` renderer, `GET /api/reports/{date}/export.md` route, 4 new tests
- Total: 1069/1069 tests on Day-to-Day repo

### S3 (Lessons Curation)
- 4 skills amended v1.0 -> v1.1 (constitution-sync, to-spec, testing-conventions, tdd-gate)
- LESSON-004 through LESSON-010 curated
- Tech debt spec filed for PI-4

### S4 (Live UI v2 Spec)
- 59 CSS design tokens, static mockup (34KB), full spec (37KB)
- Plan, tasks, validation contract (LOCKED) for PI-4 implementation
- design-tokens skill v1.0 shipped

### S5 (Navigation Layer)
- ADR-0011 + Rule 13 (Management/ structure governance)
- Three-tier navigation: Tracker -> PI INDEX -> Sprint SPEC + AGENT_NOTES
- build-index CLI subcommand operational
- PI-1 and PI-2 backfilled with provenance markers

---

## Lessons Captured

See `lessons.md` in this directory.

---

## Cross-References

- Management index: `docs/Management/PI-3/INDEX.md`
- Roadmap: `constitution/roadmap.md` (PI-3 section)
- Session memory: `sessions/SESSION-MEMORY.md`
