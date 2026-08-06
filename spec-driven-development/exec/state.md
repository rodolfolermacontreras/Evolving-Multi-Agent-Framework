# Executive State

Generated date: 2026-08-06
Current PI: No active PI
Active sprint: Symbolic -- AI fleet compresses wall-clock time
Active focus: No feature scheduled

## Spec Pipeline

| Feature | Stage | Status | Notes |
|---------|-------|--------|-------|
| fleet-ledger | DONE | done | explicit completed terminal disposition |
| cloud-dashboard | DONE | done | explicit completed terminal disposition |
| dashboard-about-and-freshness | DONE | done | explicit completed terminal disposition |
| fleet | DONE | done | explicit completed terminal disposition |
| fleet-cli | DONE | done | explicit completed terminal disposition |
| qa-cli | DONE | done | explicit completed terminal disposition |
| retro-cli | DONE | done | explicit completed terminal disposition |
| retro-closure | DONE | done | explicit completed terminal disposition |
| schema-lint | DONE | done | explicit completed terminal disposition |
| state-builder | DONE | done | explicit completed terminal disposition |
| state-dashboard | DONE | done | explicit completed terminal disposition |
| day-to-day-brownfield-bootstrap | DONE | done | explicit completed terminal disposition |
| live-ui-v2 | DONE | done | explicit completed terminal disposition |
| principal-agent-hygiene | DONE | done | explicit completed terminal disposition |
| friction-analysis-template | DONE | done | explicit completed terminal disposition |
| filesystem-data-contracts | DONE | done | explicit completed terminal disposition |
| symlink-portability | DONE | done | explicit completed terminal disposition |
| cross-feature-dedup | DONE | done | explicit completed terminal disposition |
| host-gitignore-protection | DONE | done | explicit completed terminal disposition |
| serial-clarify-spec-gate | DONE | done | explicit completed terminal disposition |
| ado-github-bridge | DONE | done | explicit completed terminal disposition |
| end-of-session-self-review | DONE | done | explicit completed terminal disposition |
| first-class-user-gates | DONE | done | explicit completed terminal disposition |
| model-upgrade-discipline | DONE | done | explicit completed terminal disposition |
| stakeholder-pressure-defense | DONE | done | explicit completed terminal disposition |
| sprint-6-completion | DONE | done | explicit completed terminal disposition |
| ui-lifecycle-variant | DONE | done | explicit completed terminal disposition |
| state-builder-fixes | DONE | done | explicit completed terminal disposition |
| dashboard-dispatches-health-pills | DONE | active | validation required-complete |
| dashboard-lifecycle-reorder | DONE | active | validation required-complete |
| d2-proof-config-cutover | DONE | done | explicit completed terminal disposition |
| detach-clone-and-run-hardening | DONE | done | explicit completed terminal disposition |
| make-promises-true | DONE | done | explicit completed terminal disposition |
| plain-language-comms-discipline | DONE | done | explicit completed terminal disposition |
| sdd-047-de-author | DONE | done | explicit completed terminal disposition |
| sdd-048-maintainability | DONE | done | explicit completed terminal disposition |
| two-tier-executive-manager | DONE | done | explicit completed terminal disposition |
| dashboard-truth | DONE | done | explicit completed terminal disposition |
| decision-request-format | DONE | done | explicit completed terminal disposition |
| doc-freshness-staledoc-guard | DONE | done | explicit completed terminal disposition |
| roadmap-repair-status-backfill | DONE | done | explicit completed terminal disposition |
| file-overlap-detector | DONE | done | explicit completed terminal disposition |
| reorder-backend-reoptimization | DONE | done | explicit completed terminal disposition |
| fresh-checkout-ci-doctor-repair | DONE | active | validation required-complete |
| sprint-23-dashboard-polish | DONE | done | explicit completed terminal disposition |
| brownfield-bootstrap-correctness | DONE | done | explicit completed terminal disposition |
| truth-reconciliation-maintenance | REVIEW | review | owning artifact review veto |

## Sprint Plan

### Carried forward after PI-5 close

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-034 | Dedup heuristic upgrade -- content-shingle for spec.md problem statements (replaces title-shingle only) | P3 | -- | Filed 2026-06-08 via Executive Manager. Surfaced by F-10 pass 1 Article XI live contention test: SDD-020 dedup scan returned 100% false-positive overlaps (6 SOFT/ADVISORY all title-shingle artifacts); real prior art (`2026-05-26-live-ui-v2/`, `2026-05-16-state-dashboard/`, `2026-05-16-dashboard-about-and-freshness/`) was found manually by PM+Architect, not the scanner. Upgrade dedup heuristic to also consider Problem Statement / Goal section content-shingles, not just titles. Not pulled into Sprint 8, Sprint 9, or the PI-5 close stamp; carried forward because Sprint 8 primary SDD-022 + SDD-015 and Sprint 9 primary SDD-021 + SDD-023 + SDD-025 consumed their close criteria. |

### DEFERRED

| ID | Title | Priority | RICE | Status |
|----|-------|----------|------|--------|
| SDD-026 | Trim agent traceability scope -- stop per-feature instruction snapshots; keep dispatch + outcome + promotions | P4 | -- | PM override (EM P3 -> P4); re-evaluation trigger: PI-5 retrospective after ledger has accumulated 2 PIs of usage data; removing data without measured pain is premature optimization |

## Fleet

- Principals: 6
- Generic workers: 5
- Specialists: 1
- Total agents: 12
- Skills: 34 across 5 categories

## Recently Completed

_no successful dispatches yet_

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

_no active PI -- plan next PI_

---

_Auto-generated by `cli/state_builder.py`. SDD-002 contract: 7-section format. Visual dashboard: `python state_builder.py serve`._
