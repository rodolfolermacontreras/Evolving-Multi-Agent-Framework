# Executive State

Generated date: 2026-07-10
Current PI: PI-9 (Experience Polish)
Active sprint: Symbolic -- AI fleet compresses wall-clock time
Active focus: Finish implementation of 'azure-decommission'

PI progress: 0/1 commitments complete (0%)

## Spec Pipeline

| Feature | Stage | Status | Notes |
|---------|-------|--------|-------|
| fleet-ledger | DONE | done | validation required-complete, RETRO present |
| fleet-bridge-dashboard | CLARIFY | - | DESIGN.md only (pre-spec design exploration) |
| cloud-dashboard | CLARIFY | - | DESIGN.md only (pre-spec design exploration) |
| dashboard-about-and-freshness | DONE | done | validation required-complete, RETRO present |
| fleet | DONE | done | validation required-complete, RETRO present |
| fleet-cli | DONE | done | validation required-complete, RETRO present |
| qa-cli | DONE | done | validation required-complete, RETRO present |
| retro-cli | DONE | done | validation required-complete, RETRO present |
| retro-closure | TASKS | - | tasks.md present |
| schema-lint | DONE | done | validation required-complete, RETRO present |
| state-builder | DONE | done | validation required-complete, RETRO present |
| state-dashboard | DONE | done | validation required-complete, RETRO present |
| day-to-day-brownfield-bootstrap | DONE | done | validation required-complete, RETRO present |
| live-ui-v2 | DONE | done | validation required-complete, RETRO present |
| principal-agent-hygiene | DONE | done | Status: done (no validation file) |
| friction-analysis-template | DONE | done | validation required-complete |
| filesystem-data-contracts | DONE | done | validation required-complete |
| symlink-portability | DONE | done | validation required-complete |
| cross-feature-dedup | REVIEW | done | Status: done but validation required items unchecked |
| host-gitignore-protection | DONE | done | validation required-complete |
| serial-clarify-spec-gate | REVIEW | done | Status: done but validation required items unchecked |
| ado-github-bridge | DONE | done | validation required-complete |
| azure-decommission | IMPLEMENT | active | validation required 33% (4/12) |
| end-of-session-self-review | DONE | done | validation required-complete |
| first-class-user-gates | DONE | done | validation required-complete |
| model-upgrade-discipline | DONE | done | validation required-complete |
| stakeholder-pressure-defense | DONE | done | validation required-complete |
| sprint-6-completion | DONE | done | validation required-complete, RETRO present |
| ui-lifecycle-variant | DONE | done | validation required-complete, RETRO present |
| state-builder-fixes | DONE | done | validation required-complete |
| dashboard-dispatches-health-pills | DONE | active | validation required-complete |
| dashboard-lifecycle-reorder | DONE | active | validation required-complete |
| d2-proof-config-cutover | BACKLOG | - | directory exists, no artifacts yet |
| detach-clone-and-run-hardening | DONE | done | validation required-complete |
| make-promises-true | DONE | done | validation required-complete |
| plain-language-comms-discipline | DONE | done | validation required-complete |
| sdd-047-de-author | DONE | done | validation required-complete |
| sdd-048-maintainability | DONE | done | validation required-complete |
| two-tier-executive-manager | DONE | done | validation required-complete |
| dashboard-truth | DONE | done | validation required-complete, RETRO present |
| decision-request-format | DONE | done | validation required-complete |
| doc-freshness-staledoc-guard | DONE | done | validation required-complete |
| roadmap-repair-status-backfill | DONE | done | validation required-complete |
| file-overlap-detector | DONE | done | validation required-complete |
| reorder-backend-reoptimization | DONE | done | validation required-complete |
| fresh-checkout-ci-doctor-repair | DONE | active | validation required-complete |
| sprint-23-dashboard-polish | DONE | active | validation required-complete |

## Sprint Plan

### PI-2 Sprint A

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-002 | state_builder.py -- auto-generate exec/state.md from ledger and artifacts | P2 | 10.8 | Approved |
| SDD-003 | fleet.py -- dispatch packets and ledger writes | P2 | 6.4 | Approved |

### PI-2 Sprint B

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-004 | qa.py -- two-stage review automation | P2 | 4.8 | Approved |
| SDD-005 | retro.py -- sprint retro generator | P2 | 9.6 | Approved |
| SDD-006 | Schema validation lint for agent/skill/prompt YAML frontmatter | P2 | 6.3 | Approved |

### PI-3 Sprint A (proposed)

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-009 | Dashboard data-freshness -- live values reflect new commits/ledger writes without manual redeploy | P2 | 4.0 | Triaged 2026-05-16; bundled spec dir `2026-05-16-dashboard-about-and-freshness`; needs /clarify to choose option (a) document-as-expected, (b) GH Actions OIDC auto-redeploy (REC-3 from cloud-dashboard SECURITY-REVIEW), or (c) runtime repo sync (volume mount or git pull on startup) |
| SDD-010 | Dashboard "About / Where we are" section -- newcomer-facing purpose + high-level project state (meta-aware) | P2 | 3.0 | Triaged 2026-05-16; bundled with SDD-009 in spec dir `2026-05-16-dashboard-about-and-freshness`; pure content addition to `state_builder.py` HTTP handler |

### Shipped 2026-05-16

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-007 | Cloud-deployed live Bridge dashboard on Azure Container Apps with Entra ID auth, scale-to-zero, OIDC CI/CD | P3 | 0.9 | DEPLOYED (v1 live, see PROVISIONED.md) |

## Fleet

- Principals: 6
- Generic workers: 5
- Specialists: 1
- Total agents: 12
- Skills: 34 across 5 categories

## Recently Completed

| When | Feature | Task | Agent |
|------|---------|------|-------|
| 2026-07-10T22:34:14Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-65 independent code-quality and accessibility review | gem-critic+ux-designer |
| 2026-07-10T22:30:19Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-65 Stage 1 spec compliance review | qa-engineer-general |
| 2026-07-10T22:28:26Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-65 lifecycle token injector TDD implementation | developer-general |
| 2026-07-10T22:28:26Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-65 exact historical wording repair | developer-cli-specialist-1 |
| 2026-07-10T21:26:59Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-64 SDD-057 and SDD-056 implementation with focused tests | developer-general |
| 2026-07-10T21:26:59Z | spec-driven-development/specs/2026-07-10-sprint-23-dashboard-polish | F-64 Stage 1 spec compliance review and re-review | qa-engineer-general |
| 2026-07-09T15:09:43Z | specs/2026-07-09-reorder-backend-reoptimization | SDD-054 reorder backend re-optimization (design+TDD impl+QA) | principal-software-developer |
| 2026-07-09T14:31:58Z | specs/2026-07-09-file-overlap-detector | SDD-049 file-overlap detector (design+TDD impl+QA) | principal-software-developer |
| 2026-07-09T13:59:03Z | sprints/PI-9 | PI-8 close + PI-9 open (governance) | sprint-executive-manager |
| 2026-07-08T22:14:11Z | spec-driven-development/specs/2026-07-08-decision-request-format | SDD-053 IMPLEMENT+QA: skill DECISION-REQUEST FORMAT + 2 EM charter bindings + test_sdd053.py (596 passed) | principal-software-developer |

## Blockers

### Pending User Gates

| Feature | Gate | Blocks | Evidence Need | Next Action |
|---------|------|--------|---------------|-------------|
| 2026-06-08-first-class-user-gates | GATE-001 (`clarify-owner-answer`) | `clarify-close` | owner-quote, em-synthesis | Record owner answer evidence before CLARIFY close. |
| 2026-06-08-first-class-user-gates | GATE-002 (`adr-acceptance`) | `adr-dependent-edit` | accepted-adr, owner-quote | Record accepted ADR or owner evidence before ADR-dependent edits. |
| 2026-06-08-first-class-user-gates | GATE-003 (`constitution-edit`) | `constitution-edit` | accepted-adr, owner-quote | Record ADR plus owner evidence before constitution edits. |
| 2026-06-08-first-class-user-gates | GATE-004 (`level-2-decision`) | `feature-close` | owner-quote, accepted-adr, commit-stamp | Record Level-2 approval evidence before the affected feature close. |
| 2026-06-08-first-class-user-gates | GATE-005 (`external-write`) | `external-write` | owner-quote, issue-comment, cli-record | Record approval evidence before external writes. |
| 2026-06-08-first-class-user-gates | GATE-006 (`model-upgrade`) | `model-upgrade` | owner-quote, accepted-adr, cli-record | Record model-upgrade approval before model assignment changes. |
| 2026-06-08-first-class-user-gates | GATE-007 (`required-validation-exception`) | `feature-close` | owner-quote, commit-stamp | Keep REQUIRED items unchecked unless owner-approved exception evidence exists. |
| 2026-06-08-first-class-user-gates | GATE-008 (`sprint-close`) | `sprint-close` | owner-quote, em-synthesis, commit-stamp | Record sprint close approval before claiming sprint CLOSED. |
| 2026-06-08-first-class-user-gates | GATE-009 (`push-approval`) | `push` | owner-quote, commit-stamp | Record explicit owner approval before push. |
| 2026-06-08-first-class-user-gates | GATE-010 (`pi-close`) | `pi-close` | owner-quote | Record owner approval before PI close. |

_Generated executive surfaces are visibility only; they are not approval evidence._

_none -- no dispatches without outcome older than 24h_

## Next Milestones

- Sprint 22: Close PI-8, open PI-9, and ship the experience pair -- SDD-049 (true pre-dispatch file-overlap conflict detector in `cli/fleet.py`) + SDD-041 Option B (backlog reorder -> backend re-optimization on the safeguarded `move()`/audit path).

---

_Auto-generated by `cli/state_builder.py`. SDD-002 contract: 7-section format. Visual dashboard: `python state_builder.py serve`._
