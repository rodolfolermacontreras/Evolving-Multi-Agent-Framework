# Executive State

Generated date: 2026-07-07
Current PI: PI-7 (Hardening + Orchestration Maturity)
Active sprint: Symbolic -- AI fleet compresses wall-clock time
Active focus: Continue current sprint anchor 'two-tier-executive-manager' (SDD-043)

PI progress: 4/7 commitments complete (57%)

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
| d2-proof-config-cutover | BACKLOG | - | directory exists, no artifacts yet |
| detach-clone-and-run-hardening | IMPLEMENT | active | validation 0% (0/23) |
| make-promises-true | REVIEW | active | validation 96% (25/26) |
| plain-language-comms-discipline | IMPLEMENT | active | validation 0% (0/12) |
| sdd-047-de-author | REVIEW | done | Status: done but RETRO missing |
| sdd-048-maintainability | TASKS | active | tasks.md present |
| two-tier-executive-manager | IMPLEMENT | active | validation 0% (0/17) |

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
| 2026-06-27T02:10:33Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-048-maintainability | Extract `state_builder_markdown.py`: decompose `render_markdown` (762 lines) into per-section helpers (header/lifecycle/features/backlog/dispatches/decisions/footer) via `string.Template` (stdlib). Re-import. | principal-software-developer |
| 2026-06-27T02:10:33Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-048-maintainability | Prove the lightweight path on ONE real <5-file feature end-to-end; its lock holder validates (Article X intact). | principal-software-developer |
| 2026-06-27T02:10:32Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-048-maintainability | Add `"article_xi_cutover": "2026-06-08"` to config; in `fleet.py` resolve cutover via stdlib `json` with `ARTICLE_XI_CUTOVER` fallback constant + retained comment; keep `_is_grandfathered` default sourced from resolved value. | principal-software-developer |
| 2026-06-27T02:10:32Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-048-maintainability | Extract `doc_count.py` (leaf): `_iter_in_scope_artifacts`, `_resolve_sprint_id`, `build_doc_count`, `build_doc_count_by_sprint`, `render_count_table`, `cmd_count`. Re-import into `state_builder.py`. | principal-software-developer |
| 2026-06-26T23:06:41Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-047-de-author | **LEVEL-2 (owner-gated)** constitution de-author under ADR-022 | principal-software-developer |
| 2026-06-26T23:06:39Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-047-de-author | schema_lint rule: orphan skill fails (TDD first) | principal-software-developer |
| 2026-06-26T23:06:37Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-047-de-author | A-6 lint reads config-derived personal-name denylist (TDD first) | principal-software-developer |
| 2026-06-26T23:06:36Z | C:\Training\Projects\Evolving-Multi-Agent-Framework\spec-driven-development\specs\2026-06-26-sdd-047-de-author | Create `project.config.json` (owner/team/repo_url) + stdlib reader helper | principal-software-developer |
| 2026-06-26T18:42:17Z | spec-driven-development/specs/2026-06-26-make-promises-true | SDD-046 implement: make promises true (B-1/B-2/B-4) | principal-software-developer |
| 2026-06-26T18:42:16Z | spec-driven-development/specs/2026-06-26-make-promises-true | SDD-046 design: lock validation contract (make promises true) | principal-architect |

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

- PI-6 carryovers remain open and carried forward: SDD-038 (color tokens), SDD-034 (content-shingle dedup), PI-4 housekeeping (domain-skill annotations + GH Actions Node.js bump), SDD-042 (pill-nav follow-up), SDD-039 (incidental wording cleanup), Current-Sprint widget repoint.
- SDD-041 Option B (reorder -> backend re-optimization) remains open and carried forward.
- SDD-049 (true file-overlap detector, P3) remains open and carried forward. SDD-035 (Azure decommission) remains out-of-band.

---

_Auto-generated by `cli/state_builder.py`. SDD-002 contract: 7-section format. Visual dashboard: `python state_builder.py serve`._
