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
| SDD-013 | "One feature, one session" rule -- one-line edit to principles.md + copilot-instructions.md | P1 | H | M | H | XS | -- | PI-4 Sprint 3 | **DONE** 2026-06-03 commit `5992ec8` (principles.md 1.0.0 -> 1.1.0) |
| SDD-014 | Friction Analysis section in Level-2 decision template | P1 | H | H | H | S | -- | PI-4 Sprint 3 | **DONE** 2026-06-03 commit `85b39be` (decision-policy.md 1.0.0 -> 1.1.0; template + example shipped) |
| SDD-015 | Model upgrades as Level-2 decisions w/ regression-test branch + A/B + cost analysis | P1 | H | H | H | S | -- | PI-5 Sprint 4 | **OWNER-ATTENTION/BLOCKED** 2026-06-08 F-14: implementation artifacts complete except required V-9 constitution cross-reference. ADR-016 drafted as proposed; `decision-policy.md` not edited because no accepted ADR or owner waiver exists. |
| SDD-016 | `.github/` symlink portability trick -- host-integration-symlink skill + bootstrap.py extension | P1 | H | H | H | M | -- | PI-5 Sprint 1 | **DONE** 2026-06-06 commit `30482d5` (host-link subcommand + tests; 200 -> 213) |
| SDD-017 | Hire `dev-env-manager` worker -- worktree, symlink, branch hygiene, env bootstrap | P1 | M | H | H | S | -- | PI-5 Sprint 1 | **DONE** 2026-06-06 commit `30482d5` (dev-env-manager-general rostered with host-integration-symlink skill) |
| SDD-018 | UI development lifecycle variant -- relaxed Article X with validation.md delta entries | P1 | M | H | M | M | -- | DONE (PI-5 Sprint 3, 2026-06-08) | DONE 2026-06-08 at F-11 close. Spec dir at `specs/2026-06-09-ui-lifecycle-variant/`. Commit chain: `df3bffb` (F-10 pass 1 scaffold + CLARIFY questions) -> `754fda6` (CLARIFY closed) -> `d81ac3d` (F-10 pass 2 + ADR-014 drafted) -> `7993fac` (T-018-02 schema_lint variant dispatch + 32 new tests) -> `3f6f520` (T-018-03 template stubs) -> `b46a32f` (T-018-04 state-dashboard retroactive-demo migration) -> `5233c29` (T-018-06 docs page) -> close commit. 16/16 REQUIRED + 3/3 OPTIONAL + 2/4 manual (M-3, M-4 self-attested at close; M-1, M-2 owner async for Article XII landing) + 1/2 UX (U-1 verified; U-2 owner async). Tests 273 -> 305 (+32). schema_lint clean. ADR-014 status `proposed` awaits owner Level-2 Article XII landing on top. State-dashboard retroactive-demo migration is the SDD-018 proof case. |
| SDD-019 | Serial gate on CLARIFY/SPEC (repo-wide) -- constitutional amendment; fleet.py enforcement | P1 | H | H | M | M | -- | PI-5 Sprint 2 | **DONE** 2026-06-09 (Sprint 7 F-09 completion). Core: commits `1c0454b` (plan), `524872b` (implementation). R7 (priority-weighted FIFO queue) + R8 (cutover-commit grandfather) closed in Sprint 7 F-09 via SDD-032 commit `557b672`. Article XI ratified in principles.md 1.2.0; ADR-013 committed. |
| SDD-020 | Cross-feature deduplication pass at /triage and /clarify -- pre-spec overlap scan | P1 | M | H | H | S | -- | PI-5 Sprint 2 | **DONE** 2026-06-09 (Sprint 7 F-09 completion). Core: commits `7d9a206` (plan), `8eb564d` (implementation). R6 (triple-destination log writers) closed via SDD-032 commit `8025a50`; R8 (/triage + /clarify prompt hooks) closed via SDD-032 commit `a6a25e4`. cli/dedup.py + 3-layer heuristic + log writers + prompt-hook wiring fully shipped. |

Source: Scott Epperly meeting 2026-06-02 transcript; full triage report at `sprints/PI-4/triage-scott-feedback-2026-06-03.md`.

### Sprint 5 Architect Audit Bundle (filed 2026-06-07; P1)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-027 | Host `.gitignore` protection -- blocks first real-host dispatch (bootstrap host-link must guarantee host `.gitignore` already ignores `.github/` or the install must add it) | P1 | H | H | H | S | -- | PI-5 Sprint 2 | **DONE** 2026-06-09 (Sprint 7 F-09 pull-in). Core: commits `d922a5b` (plan), `302bee5` (implementation). R12 (HOST-INTEGRATION.md docs) closed via SDD-033 in SDD-032 close commit. Core protection layer + all 4 modes shipped. |

Source: Sprint 5 Architect audit (YELLOW verdict, 2026-06-07); none blocking sprint close.

### Sprint 6 Completion Carry-Over (filed 2026-06-08)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-032 | Sprint 6 completion bundle: SDD-019 R7/R8 + SDD-020 R6/R8 | P1 | H | H | H | S | -- | PI-5 Sprint 3 | **DONE** 2026-06-09 (Sprint 7 F-09 close). Spec dir `specs/2026-06-09-sprint-6-completion/`. Commit chain: `557b672` (T-032-01/02 fleet.py R7/R8) -> `8025a50` (T-032-03 dedup.py R6) -> `a6a25e4` (T-032-04/05 prompt hooks R8) -> close commit. 7/7 REQUIRED + 2/2 OPTIONAL checked; no deferral. 259 -> 273 tests; schema_lint clean. | All 4 LOCKED REQUIRED items from Sprint 6 close commit `4a6941c` closed in single implementation pass per Option 3 hybrid ratification. Both gates (Article XI queue/grandfather + dedup log writers + prompt hooks) now fully operational ahead of SDD-018 (Sprint 7 F-10). |

Source: Owner ratification 2026-06-08 via Executive Manager routing (Option 3 hybrid; Level-2 decision; absorbs 5 deferred REQUIRED items from Sprint 6 close commit `4a6941c`).

### Post-Sprint-7 Bundle (filed 2026-06-08)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-035 | Decommission Azure dashboard; concentrate UI investment locally | P1 | H | H | H | M | -- | Out-of-band 2026-06 (Phase A.3 scaffold pending) | Pending Level-2 approval; Architect scaffolds spec dir as Phase A.3 (LOCKED at scaffold per SDD-032 pattern) | Level-2 decision: REVERSES the 2026-05-16 cloud-deploy commitment that shipped SDD-007 (Azure Container Apps + Entra ID + scale-to-zero + OIDC CI/CD). Owner direction 2026-06-08 via EM: "Azure not sustainable, especially if we want to share this tool to others. Concentrate all efforts on local dashboard (UI)." Cost burn + governance ambiguity (cloud-vs-local source of truth) + portability blocker for team share. Requires teardown checklist, ADR documenting the reversal, docs purge (SDD-007 status -> DECOMMISSIONED, PROVISIONED.md retired, README + roadmap purge of Azure refs). NOT folded into Sprint 8 -- Sprint 8 already heavy with SDD-022 + SDD-015 (14 Level-1 surfaces per F-11 close report). |
| SDD-036 | Local dashboard pattern import (lifecycle pipeline + 4-card docs + drag-to-reorder w/ safeguards) | P1 | H | H | M | L | -- | Unscheduled (PI-6 anchor candidate) | Unscheduled; CLARIFY-heavy (dependency-lock semantics + audit-trail schema + new frontmatter field design); sequencing precondition SDD-018 satisfied (DONE Sprint 7) | Imports the 3 highest-value patterns from Scott's WWIC Analyst Backlog UI per `docs/Scott_Example/UI_LEARNINGS_FROM_SCOTT.md`: (1) lifecycle status pipeline rendered horizontally on every feature card + sprint card mapping IDEA->BACKLOG->CLARIFY->SPEC->PLAN->TASKS->IMPLEMENT->REVIEW->DONE; (2) 4-card documentation row (Constitution / Spec / Sprint / ADRs) replacing scattered per-feature links; (3) drag-to-reorder backlog WITH SAFEGUARDS -- required audit-trail ledger row per drag (who/when/from-rank/to-rank/reason field) + dependency-lock (drag respects `depends_on` frontmatter; cycle-creating drags greyed-out with tooltip; force via Level-2 escalation only). Owner correction 2026-06-08: "leadership meetings happen without the PM; drag-to-reorder must be possible without ceremony -- the framework value-add is the audit trail, not blocking the human." Requires NEW `depends_on` frontmatter field in spec dir frontmatter -- schema_lint extension needed. PI-6 anchor candidate alongside SDD-037 + SDD-038 as dashboard reinvestment bundle. NOTE: ADO mirror model + per-row inline IDs (Scott patterns previously declined) BECOME RELEVANT after SDD-022 (Sprint 8) ships the ADO/GitHub Issues bridge -- PM must reconsider those two at SDD-022 close and decide whether to fold into SDD-036 v2 or carry to PI-6. |

Source: Owner Q&A session via EM 2026-06-08 (Azure decommission Q1; Scott UI re-evaluation Q2; drag-to-reorder correction; SDD-039 timing). See `docs/TEAM-SHARE-ONEPAGER.md` (committed at `22b6d22`) for downstream context.

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
| SDD-021 | End-of-session self-review loop -- skill that detects inefficiencies + proposes agent deltas via /evolve | P2 | M | M | M | M | -- | PI-5 Sprint 5 | Allocated to PI-5 Sprint 5 (= overall Sprint 9) 2026-06-06; CLARIFY; blocked on Architect transcript-accessibility audit |
| SDD-022 | ADO / GitHub Issues sync bridge -- `/taskstoissues` pattern (GitHub-first, ADO fast-follow) | P2 | H | M | M | L | -- | PI-5 Sprint 4 | **DONE** 2026-06-08 F-14: `/taskstoissues` stdlib CLI, no-network tests, prompt wrapper, GitHub provider boundary, ADO dry-run provider, and validation 16/16 REQUIRED checked. |
| SDD-023 | First-class user gates as uniform construct -- declared approver per phase + ledger record + dashboard surface | P2 | M | M | H | M | -- | PI-5 Sprint 5 | Allocated to PI-5 Sprint 5 (= overall Sprint 9) 2026-06-06; CLARIFY (gate inventory pre-spec); synergistic with SDD-019 |

### Sprint 5 Architect Audit Bundle (filed 2026-06-07; P2)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-028 | Real-Windows junction integration test (or documented limitation) -- replace mocked `mklink` test with one that actually creates and traverses a junction on Windows | P2 | M | M | M | S | -- | PI-5 Sprint 2 | **DONE** 2026-06-07 commit `4a8c03c` (documented limitation + platform-conditional skip) |
| SDD-029 | Distinguish stale-symlink from real-directory conflict in `bootstrap.py host-link` -- separate error class + remediation hint when target is a broken link vs a populated dir | P2 | M | M | H | S | -- | PI-5 Sprint 2 | **DONE** 2026-06-07 commit `4a8c03c` (stale-symlink vs real-directory distinction + tests) |

Source: Sprint 5 Architect audit (YELLOW verdict, 2026-06-07); none blocking sprint close.

### Post-Sprint-7 Bundle (filed 2026-06-08)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-037 | Local dashboard ledger visibility (Dispatches card + health pills) | P2 | M | M | H | S | -- | Unscheduled (PI-6; bundle with SDD-036) | Unscheduled; depends on SDD-036 lifecycle pipeline component existing (same dashboard surface); best bundled in one PI-6 sprint with SDD-036 | Adopts Scott's patterns 3+4: (a) Dispatches card surfacing fleet ledger contents per feature/sprint (agent, role, task, status, when) -- the ledger has more data than Scott but it's locked in SQLite and nobody opens it; this makes it human-readable in the dashboard; (b) Health pills strip in dashboard header (constitution semver consistency, skill frontmatter schema validity, ledger reachability, stale-tracker pills). Click-through to failure detail. Cheap; large reliability payoff. PI-6 anchor candidate alongside SDD-036 + SDD-038. |
| SDD-039 | Article VII wording clarification -- fresh session OR subagent dispatch both satisfy isolation | P2 | M | M | H | XS | -- | Sprint 9 default; Sprint 8 carry-over IF capacity | Allocated to Sprint 9 as housekeeping shoulder alongside SDD-021/023/025; may ship out-of-band between Sprint 8 and Sprint 9 if quiet window opens | Owner observation 2026-06-08 via EM: "why I keep getting this request, to open another working session. The AGENT should be able to route the request to the right Principal, and they can also communicate with the Executive Manager or the workers. Why keep asking me to open a new session for each task, that is impractical." Root cause: current SPRINT-04..07 kickoff prompts and the Article VII corollary in `principles.md` say "fresh chat session" as a LITERAL requirement when the underlying principle is CONTEXT ISOLATION. Subagent dispatch satisfies context isolation equally (isolated context window, single-message return). Fix: amend `principles.md` Article VII corollary + amend all 4 kickoff prompts (SPRINT-04, 05, 06, 07) + new kickoff template wording to say "fresh chat session OR subagent dispatch -- both satisfy the context-isolation property." One-day fix; no code change; `principles.md` version bump 1.3.0 -> 1.4.0 (corollary wording change is content, qualifies as MINOR per semver). Owner direction 2026-06-08: "wait until Sprint 7 closes and route as normal" -- Sprint 7 closed at `4f81df6` + `0913583`. Sprint 8 already heavy with 14 Level-1 surfaces across SDD-022 + SDD-015 (per F-11 close report) -- PM must resist scope creep. |

Source: Owner Q&A session via EM 2026-06-08 (Azure decommission Q1; Scott UI re-evaluation Q2; drag-to-reorder correction; SDD-039 timing). See `docs/TEAM-SHARE-ONEPAGER.md` (committed at `22b6d22`) for downstream context.

## P3 - Could Have

| ID | Title | Priority | Reach | Impact | Confidence | Effort | RICE | Sprint | Status |
|----|-------|----------|-------|--------|------------|--------|------|--------|--------|
| SDD-001 | Fleet Bridge Dashboard -- single-page ops console rendering fleet hierarchy, dispatch ledger, and spec lifecycle | P3 | 4 | 2 | 0.9 | 3 | 2.4 | Unscheduled | Design exploration complete; partially shipped via state-dashboard v0.2 + v2.1 |
| SDD-007 | Cloud-deployed live Bridge dashboard on Azure Container Apps with Entra ID auth, scale-to-zero, OIDC CI/CD | P3 | 1 | 3 | 0.9 | 3 | 0.9 | Shipped 2026-05-16 | DEPLOYED (v1 live, see PROVISIONED.md) |
| SDD-008 | Bridge dashboard v3 -- D3 force-directed agent network graph + WebSocket live push + click-to-expand drill-downs + sprint history + dependency arrows | P3 | 1 | 3 | 0.7 | 8 | 0.26 | Unscheduled | Backlog; UX feedback applied at v2.1 (header/pulse/progress-ring/swim-lanes/activity-feed); v3 requires new JS deps + WebSocket = ADR + new principal-architect decision |

### Scott Feedback Bundle (P3)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-024 | Map Microsoft self-improving skills paper against our skill mechanism -- 1-page memo | P3 | L | L | L | S | -- | Unscheduled | Triaged; single-task dispatch; not PI-bound (reconfirmed PI-5 plan 2026-06-06); needs paper citation confirmed first |
| SDD-025 | Stakeholder-pressure defense pattern -- playbook invoking SDD-014 Friction Analysis template | P3 | M | M | M | S | -- | PI-5 Sprint 5 | Allocated to PI-5 Sprint 5 (= overall Sprint 9) 2026-06-06; unblocked by SDD-014 (shipped PI-4 Sprint 3 commit `85b39be`) |

### Sprint 5 Architect Audit Bundle (filed 2026-06-07; P3)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status |
|----|-------|----------|---|---|---|---|------|--------|--------|
| SDD-030 | ADR-0011: cross-platform link strategy -- document the symlink-vs-junction-vs-copy decision tree and the Windows developer-mode/admin requirement | P3 | M | L | H | S | -- | Unscheduled | Unscheduled; revisit after PI-5 Sprint 2. |
| SDD-031 | Automate O2 (skill body content) grep test -- harness that asserts loaded skill files contain expected anchor strings, replacing the manual O2 check | P3 | L | L | M | S | -- | Unscheduled | Unscheduled; revisit after PI-5 Sprint 2. |

Source: Sprint 5 Architect audit (YELLOW verdict, 2026-06-07); none blocking sprint close.

### Sprint 6 Completion Carry-Over (filed 2026-06-08)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-033 | SDD-027 R12: HOST-INTEGRATION.md docs refresh for host `.gitignore` protection | P3 | L | L | H | XS | -- | PI-5 Sprint 3 | **DONE** 2026-06-09 (Sprint 7 F-09 pull-in). Closed in SDD-032 close commit. Documented `--gitignore-mode` flag, four modes (strict/prompt/warn/skip), `--no-gitignore-check`, manifest file (`cli/host_gitignore_manifest.json`), and full remediation procedure. | Doc-only deferral from Sprint 6; pulled into F-09 with remaining capacity per task brief option. |
| SDD-034 | Dedup heuristic upgrade -- content-shingle for spec.md problem statements (replaces title-shingle only) | P3 | L | M | M | M | -- | Unscheduled | Filed 2026-06-08 via Executive Manager. Surfaced by F-10 pass 1 Article XI live contention test: SDD-020 dedup scan returned 100% false-positive overlaps (6 SOFT/ADVISORY all title-shingle artifacts); real prior art (`2026-05-26-live-ui-v2/`, `2026-05-16-state-dashboard/`, `2026-05-16-dashboard-about-and-freshness/`) was found manually by PM+Architect, not the scanner. Upgrade dedup heuristic to also consider Problem Statement / Goal section content-shingles, not just titles. Not blocking SDD-018; the manual prior-art review is sufficient for now. | Cheap to spec; medium to implement. Pull into a future sprint with capacity. Accepted by owner as a known limitation 2026-06-08; filed for visibility. |

Source: Owner ratification 2026-06-08 via Executive Manager routing (Option 3 hybrid; Level-2 decision; doc-only deferral from Sprint 6 close commit `4a6941c`).

### Post-Sprint-7 Bundle (filed 2026-06-08)

| ID | Title | Priority | R | I | C | E | RICE | Sprint | Status | Notes |
|----|-------|----------|---|---|---|---|------|--------|--------|-------|
| SDD-038 | Local dashboard aesthetic tokens (Scott-pattern-aligned, IDE-native) | P3 | M | L | H | S | -- | Unscheduled (PI-6 polish; ships after SDD-036 + SDD-037) | Unscheduled; P3 because aesthetic without structure is bikeshedding | Adopts Scott's pattern 5: monospace dark IDE-native aesthetic, near-zero chrome, color-as-information. Define OUR OWN color tokens for lifecycle states (one color per state, used consistently across dashboard + rendered Markdown views + agent UIs). Do NOT photocopy Scott's specific palette or token names. Adopt the principle of consistent state-colors across surfaces. |

Source: Owner Q&A session via EM 2026-06-08 (Azure decommission Q1; Scott UI re-evaluation Q2; drag-to-reorder correction; SDD-039 timing). See `docs/TEAM-SHARE-ONEPAGER.md` (committed at `22b6d22`) for downstream context.

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
