# Product Backlog

Prioritized backlog with RICE scoring. Managed by Principal Product Manager.

## Priority Levels
- P1 (Must): Blocks daily usage or breaks existing features
- P2 (Should): Improves daily workflow significantly
- P3 (Could): Nice-to-have, quality-of-life
- P4 (Won't): Defer to future PI

## Format
| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|

## P1 - Must Have

### Scott Feedback Bundle (triaged 2026-06-03; PI-4/PI-5 commitment pending human decision)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-013 | "One feature, one session" rule -- one-line edit to principles.md + copilot-instructions.md | P1 | H | M | H | XS | -- | PI-4 (proposed) | Triaged; SKIP TO IMPLEMENT (bypass spec per sizing rule); routed to Architect |
| SDD-014 | Friction Analysis section in Level-2 decision template -- foundation for SDD-015 + SDD-016 | P1 | H | H | H | S | -- | PI-4 (proposed) | Triaged; SPEC directly; routed to Architect; defends active GPT-5.5 / Foundry stakeholder pressure |
| SDD-015 | Model upgrades as Level-2 decisions w/ regression-test branch + A/B + cost analysis | P1 | H | H | H | S | -- | PI-4 (proposed) | Triaged; SPEC after SDD-014; HITL; Architect + Cloud-Security co-sign |
| SDD-016 | `.github/` symlink portability trick -- host-integration-symlink skill + bootstrap.py extension | P1 | H | H | H | M | -- | PI-4 (proposed) | Triaged; CLARIFY (Windows Dev Mode, cross-platform); co-spec with SDD-017 |
| SDD-017 | Hire `dev-env-manager` worker -- worktree, symlink, branch hygiene, env bootstrap | P1 | M | H | H | S | -- | PI-4 (proposed) | Triaged; SPEC; co-spec with SDD-016; first task is SDD-016 implementation |
| SDD-018 | UI development lifecycle variant -- relaxed Article X with validation.md delta entries | P1 | M | H | M | M | -- | PI-4 (proposed) | Triaged (P2 -> P1 override; live dashboard pain); CLARIFY (ADR vs separate command) |
| SDD-019 | Serial gate on CLARIFY/SPEC (repo-wide) -- constitutional amendment; fleet.py enforcement | P1 | H | H | M | M | -- | PI-5 (proposed) | Triaged; CLARIFY; HITL; bundle with SDD-020 |
| SDD-020 | Cross-feature deduplication pass at /triage and /clarify -- pre-spec overlap scan | P1 | M | H | H | S | -- | PI-5 (proposed) | Triaged; SPEC; bundle with SDD-019 |

Source: Scott Epperly meeting 2026-06-02 transcript; full triage report at `sprints/PI-4/triage-scott-feedback-2026-06-03.md`.

## P2 - Should Have

| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|
| SDD-002 | state_builder.py -- auto-generate exec/state.md from ledger and artifacts | P2 | 8 | 3 | 0.9 | 2 | 10.8 | PI-2 Sprint A | Approved |
| SDD-003 | fleet.py -- dispatch packets and ledger writes | P2 | 8 | 3 | 0.8 | 3 | 6.4 | PI-2 Sprint A | Approved |
| SDD-004 | qa.py -- two-stage review automation | P2 | 6 | 2 | 0.8 | 2 | 4.8 | PI-2 Sprint B | Approved |
| SDD-005 | retro.py -- sprint retro generator | P2 | 6 | 2 | 0.8 | 1 | 9.6 | PI-2 Sprint B | Approved |
| SDD-006 | Schema validation lint for agent/skill/prompt YAML frontmatter | P2 | 7 | 2 | 0.9 | 2 | 6.3 | PI-2 Sprint B | Approved |
| SDD-009 | Dashboard data-freshness -- live values reflect new commits/ledger writes without manual redeploy | P2 | 5 | 2 | 0.8 | 2 | 4.0 | PI-3 Sprint A (proposed) | Triaged 2026-05-16; bundled spec dir `2026-05-16-dashboard-about-and-freshness`; needs /clarify to choose option (a) document-as-expected, (b) GH Actions OIDC auto-redeploy (REC-3 from cloud-dashboard SECURITY-REVIEW), or (c) runtime repo sync (volume mount or git pull on startup) |
| SDD-010 | Dashboard "About / Where we are" section -- newcomer-facing purpose + high-level project state (meta-aware) | P2 | 3 | 1 | 1.0 | 1 | 3.0 | PI-3 Sprint A (proposed) | Triaged 2026-05-16; bundled with SDD-009 in spec dir `2026-05-16-dashboard-about-and-freshness`; pure content addition to `state_builder.py` HTTP handler |

### Scott Feedback Bundle (P2)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-021 | End-of-session self-review loop -- skill that detects inefficiencies + proposes agent deltas via /evolve | P2 | M | M | M | M | -- | PI-5 (proposed) | Triaged; CLARIFY; blocked on Architect transcript-accessibility audit |
| SDD-022 | ADO / GitHub Issues sync bridge -- `/taskstoissues` pattern (GitHub-first, ADO fast-follow) | P2 | H | M | M | L | -- | PI-5 (proposed) | Triaged; CLARIFY; Scott named this the gap keeping him from adopting |
| SDD-023 | First-class user gates as uniform construct -- declared approver per phase + ledger record + dashboard surface | P2 | M | M | H | M | -- | PI-5 (proposed) | Triaged; CLARIFY (gate inventory pre-spec); synergistic with SDD-019 |

## P3 - Could Have

| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|
| SDD-001 | Fleet Bridge Dashboard -- single-page ops console rendering fleet hierarchy, dispatch ledger, and spec lifecycle | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design exploration complete; partially shipped via state-dashboard v0.2 + v2.1 |
| SDD-007 | Cloud-deployed live Bridge dashboard on Azure Container Apps with Entra ID auth, scale-to-zero, OIDC CI/CD | P3 | 1 | 3 | 0.9 | 3 | 0.9 | Shipped 2026-05-16 | DEPLOYED (v1 live, see PROVISIONED.md) |
| SDD-008 | Bridge dashboard v3 -- D3 force-directed agent network graph + WebSocket live push + click-to-expand drill-downs + sprint history + dependency arrows | P3 | 1 | 3 | 0.7 | 8 | 0.26 | Unscheduled | Backlog; UX feedback applied at v2.1 (header/pulse/progress-ring/swim-lanes/activity-feed); v3 requires new JS deps + WebSocket = ADR + new principal-architect decision |

### Scott Feedback Bundle (P3)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-024 | Map Microsoft self-improving skills paper against our skill mechanism -- 1-page memo | P3 | L | L | L | S | -- | Unscheduled | Triaged; single-task dispatch; needs paper citation confirmed first |
| SDD-025 | Stakeholder-pressure defense pattern -- playbook invoking SDD-014 Friction Analysis template | P3 | M | M | M | S | -- | PI-5 (proposed) | Triaged; BLOCKED on SDD-014 |

Notes:
- Design spec pre-built at `specs/2026-05-13-fleet-bridge-dashboard/DESIGN.md`
- Depends on: Fleet Ledger v0.1 (done), `cli/fleet.py` (PI-2)
- Next step when prioritized: `/clarify` then `/spec`
- Rationale for P3: high demo value but does not unblock PI-2 CLI maturity work; becomes more valuable after fleet dispatches real work

## P4 - Won't (this PI)
(empty)

### Scott Feedback Bundle (deferred indefinitely)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-026 | Trim agent traceability scope -- stop per-feature instruction snapshots; keep dispatch + outcome + promotions | P4 | L | L | L | S | -- | DEFERRED | PM override (EM P3 -> P4); re-evaluation trigger: PI-5 retrospective after ledger has accumulated 2 PIs of usage data; removing data without measured pain is premature optimization |

---

## insights_ai Project Follow-ups (retrospective intake 2026-05-07)

Note: These are work items for Rodolfo's insights_ai project (separate from Day-to-Day Agent features). Triaged from PROJECT_STATUS.md Update #31 open items.

| ID | Title | Priority | R | I | C | E | RICE | Tag | Status |
|----|-------|----------|---|---|---|---|------|-----|--------|
| IAI-02 | Nandini CVP demo (May 8) | P1 | 10 | 3 | 1.0 | 1 | 30.0 | [HITL] | Scheduled |
| IAI-03 | Merge 112 commits to dev | P1 | 8 | 2 | 1.0 | 1 | 16.0 | [BLOCKED on IAI-01] | Pending |
| IAI-01 | Full 178-leader batch re-run (Sprint 14.5) | P1 | 9 | 3 | 1.0 | 2 | 13.5 | [AFK] | Awaiting batch window |
| IAI-04 | ZS QC second-round validation | P1 | 7 | 2 | 0.8 | 1 | 11.2 | [BLOCKED on ZS] | Awaiting ZS feedback |
| IAI-05 | Azure Static Web App AAD auth deployment | P2 | 6 | 1 | 0.8 | 2 | 2.4 | [AFK] | Config ready, not deployed |
| IAI-06 | SEGMENT_MAPPING EPS/MG gap (61 sellers) | P4 | 3 | 0.5 | 0.5 | 2 | 0.375 | [AFK] | Documented, deferred |
