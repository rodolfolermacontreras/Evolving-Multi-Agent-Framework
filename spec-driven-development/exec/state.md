# Executive State

Generated date: 2026-06-26
Current PI: PI-6 (Dashboard Reinvestment + Carryover Cleanup)
Active sprint: Symbolic -- AI fleet compresses wall-clock time
Active focus: Continue current sprint anchor 'state-builder-fixes' (SDD-040)

PI progress: 0/0 commitments complete (0%)

## Spec Pipeline

| Feature | Stage | Status | Notes |
|---------|-------|--------|-------|
| fleet-ledger | DONE | done | validation 100%, RETRO present |
| fleet-bridge-dashboard | CLARIFY | - | DESIGN.md only (pre-spec design exploration) |
| cloud-dashboard | CLARIFY | - | DESIGN.md only (pre-spec design exploration) |
| dashboard-about-and-freshness | DONE | done | Status: done, RETRO present |
| fleet | DONE | done | validation 100%, RETRO present |
| fleet-cli | DONE | done | validation 100%, RETRO present |
| qa-cli | DONE | done | validation 100%, RETRO present |
| retro-cli | DONE | done | validation 100%, RETRO present |
| retro-closure | TASKS | - | tasks.md present |
| schema-lint | DONE | done | validation 100%, RETRO present |
| sprint-c-validation | BACKLOG | - | directory exists, no artifacts yet |
| state-builder | DONE | done | validation 100%, RETRO present |
| state-dashboard | DONE | done | validation 100%, RETRO present |
| day-to-day-brownfield-bootstrap | DONE | done | Status: done, RETRO present |
| live-ui-v2 | DONE | done | validation 100%, RETRO present |
| principal-agent-hygiene | REVIEW | done | Status: done but RETRO missing |
| friction-analysis-template | REVIEW | done | Status: done but RETRO missing |
| filesystem-data-contracts | REVIEW | done | Status: done but RETRO missing |
| symlink-portability | REVIEW | done | Status: done but RETRO missing |
| cross-feature-dedup | REVIEW | done | Status: done but RETRO missing |
| host-gitignore-protection | REVIEW | done | Status: done but RETRO missing |
| serial-clarify-spec-gate | REVIEW | done | Status: done but RETRO missing |
| ado-github-bridge | REVIEW | done | Status: done but RETRO missing |
| azure-decommission | IMPLEMENT | active | validation 17% (4/23) |
| end-of-session-self-review | REVIEW | done | Status: done but RETRO missing |
| first-class-user-gates | REVIEW | done | Status: done but RETRO missing |
| model-upgrade-discipline | REVIEW | done | Status: done but RETRO missing |
| stakeholder-pressure-defense | REVIEW | done | Status: done but RETRO missing |
| sprint-6-completion | DONE | done | validation 100%, RETRO present |
| ui-lifecycle-variant | DONE | done | Status: done, RETRO present |
| state-builder-fixes | REVIEW | done | Status: done but RETRO missing |
| dashboard-dispatches-health-pills | REVIEW | active | validation 97% (35/36) |
| dashboard-lifecycle-reorder | REVIEW | active | validation 84% (16/19) |

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
| 2026-06-08T15:06:06+00:00 | None | Dedup scan (all) | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [SOFT] Cross-feature deduplication pass at triage and clarify | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [SOFT] Map Microsoft self-improving skills paper against our skill mechanism | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [SOFT] Model upgrades as Level-2 decisions with regression-test branch | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [SOFT] Mandatory Friction Analysis section in Level-2 decision template | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [ADVISORY] Feature Spec: Sprint 6 Completion Bundle (SDD-032) | dedup-scanner |
| 2026-06-08T15:06:06+00:00 | None | [ADVISORY] Feature Spec: UI Lifecycle Variant (SDD-018) | dedup-scanner |
| 2026-05-16T20:35:57Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-05-16-retro-closure | Write RETRO.md for qa-cli feature (SDD-004). | developer-general |
| 2026-05-16T20:35:57Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-05-16-retro-closure | Write RETRO.md for retro-cli feature (SDD-005). | developer-general |
| 2026-05-16T20:35:56Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-05-16-retro-closure | Write RETRO.md for fleet-cli feature (SDD-003). | developer-general |

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

_no PI commitments registered_

---

_Auto-generated by `cli/state_builder.py`. SDD-002 contract: 7-section format. Visual dashboard: `python state_builder.py serve`._
