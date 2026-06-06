---
id: SDD-PI-4-TRIAGESCOTTF-session
type: session
status: active
owner: principal-software-developer
updated: 2026-06-06
sprint: PI-4
---

# Triage Report: Scott Feedback Bundle (14 items)

**Triaged by:** Principal Product Manager
**Date:** 2026-06-03
**Approved by:** Human (Rodolfo Lerma) on 2026-06-03
**Source:** Scott Epperly meeting transcript 2026-06-02, captured in [IDEAS.md](../../backlog/IDEAS.md) commit `b86c967`
**Routed via:** Principal Executive Manager

---

## Per-Item Triage

### Item 1 -- `.github/` symlink portability trick

**Intake Summary**
- Request: Host repo's root `.github/` is gitignored and empty; each project ships its own `.github/` and a bootstrap script symlinks the contents up. VS Code sees the agents/skills/prompts; git sees nothing.
- Category: Feature (tooling) + operational skill
- Assumptions: Symlink approach works cross-platform with admin-less Developer Mode on Windows; PowerShell + Bash variants both produced by bootstrap.

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=H, I=H, C=H, E=M
- Execution Flag: **HITL** (constitution-adjacent: host-integration policy)
- Recommended Next Phase: **CLARIFY** (Windows Developer Mode requirement; collision behavior across multiple parallel brownfield clones)

**Rationale**
- Value: Removes the single biggest objection to brownfield adoption -- host-repo pollution.
- Risk: Symlinks on Windows are still friction-prone without Developer Mode. Need fallback (copy-and-watch script).
- Urgency: PI-3 just closed declaring portability validated; we have NOT yet proved the host stays clean across multiple branches/developers. This is the unfinished homework.
- Missing context: Did the Day-to-Day brownfield bootstrap actually leave host `.gitignore` and history clean? Need an audit.

---

### Item 2 -- Serial gate on CLARIFY and SPEC (repo-wide)

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=H, I=H, C=M, E=M
- Execution Flag: **HITL** (constitutional change)
- Recommended Next Phase: **CLARIFY**

**Rationale**: Eliminates a class of bugs (cross-spec conflicts) by design, not by review. Risk: reduces throughput. Need escape hatch (architect override + audit log).

---

### Item 3 -- Cross-feature deduplication pass at triage and clarify

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=M, I=H, C=H, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **SPEC** (scope clear; bundle with item 2's constitutional change)

**Rationale**: Catches the failure mode Scott reported (3 atomic bug reports -> 3 features -> 1 underlying issue missed). Reuse the work-index from the 2026-06-03 pre-work-check skill -- same data source.

---

### Item 4 -- End-of-session self-review loop

**Classification**
- Priority: **P2** (agree with EM)
- RICE gut: R=M, I=M, C=M, E=M
- Execution Flag: **AFK**
- Recommended Next Phase: **CLARIFY** (what defines "session"? VS Code session, branch, sprint?)

**Rationale**: Formalizes meta-learning that today is ad-hoc. Scott has it working in production. Architect must first confirm transcript accessibility.

---

### Item 5 -- UI development lifecycle variant (relaxed Article X)

**Classification**
- Priority: **P1** (**OVERRIDE** from EM's P2)
- RICE gut: R=M, I=H, C=M, E=M
- Execution Flag: **HITL** (constitutional)
- Recommended Next Phase: **CLARIFY** (ADR vs. separate command; what counts as "UI work")

**Rationale**: We are CURRENTLY in PI-4 doing dashboard polish under strict Article X and feeling exactly the pain Scott described. Fixing this is unblocking live work.

---

### Item 6 -- ADO / GitHub Issues sync bridge

**Classification**
- Priority: **P2** (agree with EM)
- RICE gut: R=H, I=M, C=M, E=L
- Execution Flag: **AFK** (once authenticated)
- Recommended Next Phase: **CLARIFY** (GitHub-only first, or ADO co-equal)

**Rationale**: Scott literally said this is the gap keeping him from adopting. Schedule for PI-5; ship GitHub-only first.

---

### Item 7 -- First-class user gates as uniform construct

**Classification**
- Priority: **P2** (agree with EM)
- RICE gut: R=M, I=M, C=H, E=M
- Execution Flag: **AFK**
- Recommended Next Phase: **CLARIFY** (gate inventory pre-spec)

**Rationale**: Makes lifecycle queryable and dashboard-actionable. Synergistic with item 2.

---

### Item 8 -- Hire `dev-env-manager` worker role

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=M, I=H, C=H, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **SPEC** (scope clear; co-spec with item 1)

**Rationale**: Pulls scattered worktree/symlink/branch hygiene into a specialist. First task: own item 1's implementation.

---

### Item 9 -- Map Microsoft self-improving skills paper to our skill mechanism

**Classification**
- Priority: **P3** (agree with EM)
- RICE gut: R=L, I=L, C=L, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **TASKS** (single-task dispatch; no spec needed)

**Rationale**: May yield framework polish; may yield nothing. Hard-cap the timebox. Confirm paper citation before dispatch.

---

### Item 10 -- Model upgrades as Level-2 decisions with regression-test branch

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=H, I=H, C=H, E=S
- Execution Flag: **HITL**
- Recommended Next Phase: **SPEC** (after item 11 ships)

**Rationale**: Defends against bad upgrades AND gives a citable answer to stakeholders. Active GPT-5.5 / Foundry pressure now. Cloud-Security Architect co-signs (model = supply-chain dependency).

---

### Item 11 -- Mandatory Friction Analysis section in Level-2 decision template

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=H, I=H, C=H, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **SPEC** (template change, scope clear)

**Rationale**: Foundational. Items 10 and 14 are blocked on this template existing. Keep tight; one page max.

---

### Item 12 -- Trim agent traceability scope

**Classification**
- Priority: **P4** (**OVERRIDE** from EM's P3 -- defer indefinitely)
- RICE gut: R=L, I=L, C=L, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **PARKED**

**Rationale**: Removing ledger data without measured pain is premature. We have not yet established what we DO use per-feature snapshots for. **Re-evaluation trigger:** PI-5 retrospective.

---

### Item 13 -- "One feature, one session" rule

**Classification**
- Priority: **P1** (agree with EM)
- RICE gut: R=H, I=M, C=H, E=XS
- Execution Flag: **AFK**
- Recommended Next Phase: **SKIP TO IMPLEMENT** (one-line edit, no spec needed per spec-sizing rule)

**Rationale**: Closes a loophole without changing behavior. Cheap. Recommend short rule in `principles.md` + operational guidance in `copilot-instructions.md`.

---

### Item 14 -- Stakeholder-pressure defense pattern

**Classification**
- Priority: **P3** (agree with EM)
- RICE gut: R=M, I=M, C=M, E=S
- Execution Flag: **AFK**
- Recommended Next Phase: **BLOCKED on item 11**, then SPEC

**Rationale**: Turns a personal habit into a framework feature. Hard dependency on item 11.

---

## Proposed Epic Groupings

**Epic A -- Brownfield Distribution Bootstrap** (items 1, 8) -- **fits PI-4 polish**
Symlink portability + dev-env-manager worker. Together they finish the PI-3 brownfield story we declared closed but did not fully prove. dev-env-manager's first task is to own item 1's implementation.

**Epic B -- Constitutional Anti-Conflict Gates** (items 2, 3, 13, plus item 7 as architectural follow-on) -- **fits PI-4 + PI-5**
Serial CLARIFY/SPEC gate + cross-feature dedup + one-feature-one-session rule, all addressing the same failure class: context contamination across features.

**Epic C -- Decision Discipline & Stakeholder Defense** (items 11, 10, 14) -- **fits PI-4**
Friction Analysis template (foundation) -> Model upgrades as Level-2 (first concrete application) -> Stakeholder pressure defense pattern (reusable playbook). Sequence is strict: 11 -> 10 -> 14.

**Epic D -- Framework Evolution & Adoption** (items 4, 5, 6, 9) -- **fits PI-5 (item 5 pulled into PI-4)**
Meta-learning loop, UI variant ADR, ADO/GitHub Issues bridge, self-improving skills research memo.

**Standalone deferred:** item 12 (trim traceability) -- parked, re-evaluate at PI-5 retro.

---

## Dependency Map

- **Item 11 MUST precede item 10** -- item 10's policy references the template.
- **Item 11 MUST precede item 14** -- item 14 is the playbook that invokes the template.
- **Item 2 SHOULD precede item 3** -- item 3 is the triage-level enforcement of item 2's principle. Can be specced together.
- **Item 1 AND item 8 MUST be co-specced** -- dev-env-manager owns the symlink work; specifying separately creates ownership confusion.
- **Item 7 SHOULD follow item 2** -- item 2 establishes which gates matter; item 7 generalizes the construct.
- **Item 13 has NO dependencies** -- ship first as the trivial quick win.
- **Item 4 is BLOCKED on transcript accessibility audit** -- Architect must confirm before spec.

---

## P1 Items Ready for Immediate Action

| # | Item | Recommended Next Phase | Why |
|---|------|----------------------|-----|
| 1 | Item 13 -- One feature one session | **SKIP to IMPLEMENT** | One-line edit. Bypass spec per sizing rule. |
| 2 | Item 11 -- Friction Analysis template | **SPEC directly** | Scope clear; foundation for items 10 and 14. |
| 3 | Item 10 -- Model upgrades as Level-2 | **SPEC** (after item 11) | Constitutional amendment; HITL gate. |
| 4 | Item 1 + Item 8 -- Symlink + dev-env-manager | **CLARIFY** | Cross-platform symlink behavior + role scope need clarification. |
| 5 | Item 2 + Item 3 -- Serial gate + Cross-dedup | **CLARIFY** | Constitutional change; needs human approval and tooling design. |
| 6 | Item 5 -- UI lifecycle variant (overridden to P1) | **CLARIFY** | ADR scope vs. separate command; UI/logic boundary undefined. |

---

## Items Recommended for REJECTION or DEFERRAL

**REJECTED:** None. All 14 items have legitimate framework value.

**DEFERRED-INDEFINITELY:**
- **Item 12 -- Trim agent traceability scope.** Removing ledger data without measured pain is premature optimization. **Re-evaluation trigger:** PI-5 retrospective.

---

## Roll-up

- **Total items:** 14
- **P1:** 8 (items 1, 2, 3, 5, 8, 10, 11, 13)
- **P2:** 3 (items 4, 6, 7)
- **P3:** 2 (items 9, 14)
- **P4 / DEFERRED:** 1 (item 12)
- **REJECTED:** 0

**Recommended commitment to PI-4 (current):** items 13, 11, 10, 1+8, 5 (6 items / 5 specs)

**Recommended commitment to PI-5:** items 2+3, 7, 4, 6, 14 (6 items / 5 specs)

**Recommended for backlog (unscheduled):** items 9, 12

**Top 3 most urgent:**
1. **Item 13 (One feature, one session)** -- trivial one-line edit, prevents context contamination starting today. Zero risk, immediate value.
2. **Item 11 (Friction Analysis template)** -- foundation for two other P1 items and direct defense against active stakeholder model-upgrade pressure.
3. **Item 1 + Item 8 (Symlink + dev-env-manager bundle)** -- closes the unfinished PI-3 portability story. Without this, "brownfield validated" is a false claim.

---

## Scope Conflict Flag (EM addendum 2026-06-03)

PI-4 is already actively committed to two work streams:
1. **Live UI v2** -- 14 LOCKED tasks (Sprint 1)
2. **Alpha Release Housekeeping** -- 6 tasks (Sprint 2)

The PM's "recommended PI-4 commitment" above (6 additional Scott items, 5 additional specs) would substantially expand PI-4 scope. Human approved the triage outcome but the scope expansion question is **deferred to the human** for a sprint-planning conversation. Options on the table:
- (a) Add a Sprint 3 to PI-4 for the Scott items (expand scope)
- (b) Defer entire Scott bundle to PI-5 (clean separation)
- (c) Hybrid: absorb only item 13 (trivial) and item 11 (defends against active stakeholder pressure) into PI-4 Sprint 2 housekeeping; defer the other 4 P1 items to PI-5
- (d) Pause Alpha Release housekeeping and substitute Scott items (re-prioritize)

EM recommends **(c)**: smallest scope-creep, addresses active pressure, keeps Live UI v2 and Alpha Release on track.
