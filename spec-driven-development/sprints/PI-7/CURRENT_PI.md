---
id: SDD-PI-7-CURRENT_PI-sprint
type: sprint
status: active
owner: principal-product-manager
updated: 2026-06-26
sprint: PI-7
---

# PI-7: Hardening + Orchestration Maturity

- Status: **ACTIVE (launched 2026-06-26, owner-approved via Executive Manager).** Sprint 14 (PI-7 Sprint 1) CLOSED 2026-06-26 -- owner-approved commit + push; SDD-043/044/045 DONE; tests 481 -> 501; ADR-020 Accepted. PI-7 continues into Sprint 15 (PI-7 Sprint 2 -- "Make promises true", SDD-046). The PI-7 CLOSE is a separate owner-approved decision after Sprint 17.
- Theme: Make the framework genuinely team-portable -- a teammate clones the
  repo, runs one setup command, and builds their own project the same day with
  no trace of the original author -- and fix the two-tier orchestration
  confusion so a single-sprint session stops drifting into project-level
  Executive Manager behavior.
- Started: 2026-06-26
- Owner: principal-executive-manager
- Predecessor: PI-6 (Dashboard Reinvestment + Carryover Cleanup) CLOSED
  2026-06-26 as DONE-WITH-CARRYOVER at commit `4ad0521`.
- Authorization: Owner approval 2026-06-26 via Executive Manager. Owner
  direction (verbatim intent): make the framework team-portable and fix the
  two-tier orchestration confusion -- this is the Alpha-gating priority. Owner
  communication rule (effective 2026-06-26): in ALL human-facing output
  (status, progress, questions to the owner) use SHORT, PLAIN language;
  agent-to-agent detail is fine.
- Spec source for the audit work: the tracked file
  [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md)
  (Parts A-D; each item's "Acceptance" block seeds that feature's
  `validation.md`).

---

## Goal

After PI-7 a teammate can `git clone` the framework, run one setup command, get
a clean lint-passing test-passing checkout with their own empty ledger and no
fingerprints of anyone else, and start building their own project that day. In
parallel, the orchestration layer grows up: a sprint runs under a sprint-scoped
Executive Manager that knows it answers to a higher project EM and cannot invent
sprints or PIs, and every human-facing principal speaks in short plain language.
The framework stops promising things it does not deliver (the ledger becomes
real or the claim is retracted; the rules that matter block on violation), and
the god-module gets broken up so the codebase stays maintainable.

---

## PI Objectives

### 1. Two-tier Executive Manager: Sprint EM agent (SDD-043)
**Why**: When the owner opens a fresh session and activates
`principal-executive-manager` to run one sprint, that agent behaves as if it is
the top-level project EM -- it can author new sprints, make PI-level calls, and
lose the boundary of its sprint. We need a NEW sprint-scoped orchestrator that
knows it reports up to the project EM at sprint close, routes feature work to
PM / Architect / SW Dev, and CANNOT create sprints or PIs (it may only SUGGEST
to the project EM). The constraints must live in the agent IDENTITY file, not
just the kickoff prompt, so they hold even if a kickoff is paraphrased.

**Success Criteria**: A new `.github/agents` Sprint EM file exists with
identity-level scope constraints; an ADR records the two-tier EM model; the
SPRINT-NN kickoff template activates the Sprint EM (not the project EM); any
`constitution/principles.md` Article II reference change is owner-approved
(Level-2). The Sprint EM cannot author a new sprint/PI without escalating.

**Feature**: SDD-043. **Sprint**: 14 (PI-7 Sprint 1).

---

### 2. Plain-language human-facing communication discipline (SDD-044)
**Why**: The owner directed 2026-06-26 that all human-facing output be short and
plain. Today the `em-communication-discipline` skill scopes that habit to the
Executive Manager only. Every principal/EM that talks to the human should follow
the same rule: short, plain, to the point; agent-to-agent detail stays allowed.

**Success Criteria**: The `em-communication-discipline` skill (or its successor)
applies to ALL human-facing principals/EMs; the rule is explicit (status,
progress, questions to the owner = short plain language; internal detail
unrestricted). This is a skill amendment, not a constitution edit.

**Feature**: SDD-044. **Sprint**: 14 (PI-7 Sprint 1).

---

### 3. Detach: clone-and-run portability (SDD-045 -- A-1/A-4/A-5/A-6/B-3)
**Why**: The audit's fastest "this is a team tool now" win. A teammate cannot
currently clone and run cleanly: the personal ledger (`fleet.db`) is committed
so they inherit the author's rows; there is no one-command setup; there is no
`doctor` health check; nothing stops origin-token or identity regression; and
the governance docs disagree on the article range (B-3). Closing these makes the
clone-and-run experience real and the governance self-consistent.

**Success Criteria**: `fleet.db` is gitignored and removed from tracking, and
setup creates a fresh empty ledger; one setup command takes a clone to a
productive state; a `doctor` / health check reports green or names the failure;
an origin-token + identity lint exists; RULES.md and principles.md agree on the
article range. Per-item SDD-IDs assigned at Sprint 14 CLARIFY.

**Feature**: SDD-045 (epic). **Sprint**: 14 (PI-7 Sprint 1). **Spec source**:
`docs/Temp/EMF-HARDENING-PLAN.md` Part A (A-1/A-4/A-5/A-6) + B-3.

---

### 4. Make promises true (SDD-046 -- B-1/B-2/B-4)
**Why**: The single most important credibility move. The framework claims
universal dispatch logging, but the ledger is effectively empty post-PI-2 -- a
teammate who reads the claim and opens the ledger concludes the process is
paperwork. B-1 makes the ledger true or retracts the claim; B-2 turns the rules
that matter (TDD gate first) into blocking checks instead of honor-system prose;
B-4 adds the CI that ADR-009 already claims exists.

**Success Criteria**: The ledger is either filled by the work (mandatory logging
at close) or the universal-logging claim is retracted -- decided at Sprint 15
CLARIFY (owner fork); at least the TDD gate becomes a blocking check; one
GitHub Actions workflow runs the `doctor` set on push. Per-item SDD-IDs assigned
at Sprint 15 CLARIFY.

**Feature**: SDD-046 (epic). **Sprint**: 15 (PI-7 Sprint 2). **Spec source**:
`docs/Temp/EMF-HARDENING-PLAN.md` Part B (B-1/B-2/B-4).

---

### 5. De-author the content (SDD-047 -- A-2/A-3/D-1/D-3)
**Why**: A teammate should see no personal fingerprints, no dead skills, and no
over-claims. A-2 moves owner/identity into config instead of a hardcoded name;
A-3 scrubs origin-project leakage (engine.py / FastAPI / Day-to-Day tokens) from
generic files; D-1 wires or deletes the dead skills; D-3 renames the over-claimed
"conflict detection" to the "serial CLARIFY/SPEC gate" the code actually
implements.

**Success Criteria**: Owner/identity is config-driven; no origin-project tokens
remain in generic framework files; every shipped skill is referenced or removed;
the naming matches the implementation. Per-item SDD-IDs assigned at Sprint 16
CLARIFY.

**Feature**: SDD-047 (epic). **Sprint**: 16 (PI-7 Sprint 3). **Spec source**:
`docs/Temp/EMF-HARDENING-PLAN.md` Parts A (A-2/A-3) + D (D-1/D-3).

---

### 6. Maintainability and right-sizing (SDD-048 -- C-1/C-2/C-3/D-2)
**Why**: The god-module has to go and small features must stop drowning in
ceremony. C-1 splits `state_builder.py` behind its existing tests; C-2 records
the stdlib-vs-templating decision as an ADR (owner fork); C-3 replaces the
hardcoded grandfather date; D-2 adds a lightweight-spec path for small (<5-file)
features.

**Success Criteria**: `state_builder.py` is decomposed with the suite still
green and the Article X lock held; an ADR records the stdlib-only vs one-dep
templating decision; the grandfather date is computed/config-driven; a
lightweight-spec path exists for small features. The Sprint 13 carryover Option B
(reorder -> backend re-optimization) folds in IF capacity allows -- a later
feature, not the anchor. Per-item SDD-IDs assigned at Sprint 17 CLARIFY.

**Feature**: SDD-048 (epic). **Sprint**: 17 (PI-7 Sprint 4). **Spec source**:
`docs/Temp/EMF-HARDENING-PLAN.md` Part C (C-1/C-2/C-3) + D-2.

---

## Sprint Allocation

| Sprint | Overall | Title | Items | Size | Why this order |
|--------|---------|-------|-------|------|----------------|
| **PI-7 Sprint 1** | Sprint 14 | Detach + Orchestration Maturity -- **CLOSED 2026-06-26** | SDD-043 (Sprint EM) + SDD-044 (plain-language comms) + SDD-045 (A-1/A-4/A-5/A-6/B-3) -- all DONE | L | Highest-trust, demo-first slice. Clone-and-run becomes real, governance becomes self-consistent, and the orchestration layer grows up (Sprint EM + plain comms) before the heavier hardening lands. Sprint EM is foundational, so it ships in the first PI-7 sprint. CLOSED: tests 481 -> 501, schema lint clean, ADR-020 Accepted, owner-approved commit + push. |
| **PI-7 Sprint 2** | Sprint 15 | Make promises true | SDD-046 (B-1/B-2/B-4) | M | The credibility sprint. B-1 (ledger truth) is the single most important move; B-2 (TDD gate) and B-4 (CI) make the rules that matter block for everyone on every push. After B-1 the ledger dogfoods the mandatory-logging fix. |
| **PI-7 Sprint 3** | Sprint 16 | De-author the content | SDD-047 (A-2/A-3/D-1/D-3) | M | No personal fingerprints, no dead skills, no over-claims. Runs after the structural fixes so identity/config moves land on a stable base. |
| **PI-7 Sprint 4** | Sprint 17 | Maintainability + right-sizing | SDD-048 (C-1/C-2/C-3/D-2) + Option B (reorder re-optimization) if capacity | L | Kill the god-module and add the lightweight-spec path last, behind the existing tests. Sprint 13 carryover Option B folds in here only if capacity allows. PI-7 CLOSE is a separate owner-approved decision after Sprint 17. |

**Unscheduled / carry-forward into PI-7 (triaged separately, not anchored here):**

- **SDD-038** -- aesthetic lifecycle color tokens (PI-6 carryover).
- **SDD-034** -- content-shingle dedup heuristic upgrade (PI-6 carryover).
- **PI-4 housekeeping** -- domain-skill annotations + GH Actions Node.js bump
  (PI-6 carryover).
- **SDD-042 pill-nav follow-up** + **SDD-039 incidental "fresh session" wording
  cleanup** + **Current Sprint widget repoint** (IDEAS.md, 2026-06-25/26).
- **SDD-041 Option B** -- reorder triggers backend re-optimization (folds into
  Sprint 17 if capacity).
- **SDD-035** -- Azure decommission remains out-of-band.

---

## Owner forks to resolve at the relevant sprint CLARIFY

1. **Sprint EM naming / tier** -- HANDLED. Folded into Sprint 14 (SDD-043); the
   Sprint EM is a sprint-scoped orchestrator with identity-level constraints,
   resolved during Sprint 14 CLARIFY/ADR, not deferred.
2. **B-1 ledger: mandatory logging (Option 1) vs retract the universal-logging
   claim (Option 2)** -> resolve at **Sprint 15 CLARIFY**. This is the audit's
   single most important move; surface it explicitly to the owner.
3. **C-2 dashboard: keep stdlib-only vs allow one templating dependency** ->
   resolve at **Sprint 17 CLARIFY** with an ADR (Article V is in play; a new
   dependency is a Level-2 owner decision).

---

## Risks (ROAM)

| Risk | Impact | Probability | ROAM | Owner | Mitigation |
|------|--------|-------------|------|-------|------------|
| SDD-043 Sprint EM touches `constitution/principles.md` Article II (EM model) -- a Level-2 constitution edit needing an ADR + owner approval | High | Medium | Owned | PM + Architect | Sprint 14 CLARIFY decides whether the Article II change is needed at all; if so, author the ADR and get recorded owner approval BEFORE editing the constitution and bump the version. |
| A-1 stops committing `fleet.db` -- `git rm --cached` plus a setup that creates a fresh DB risks breaking the dashboard's ledger read on a clean clone | Medium | Medium | Owned | SW Dev + Architect | Sprint 14 setup must create a fresh empty ledger (init from schema) so `doctor` and the dashboard still find a DB; CI runs `doctor` on a clean checkout to prove it. |
| B-1 fork (mandatory logging vs retract claim) is a credibility-defining decision the team disagrees on | High | Medium | Owned | PM + EM | Surface the fork to the owner at Sprint 15 CLARIFY with both options costed; do not pick silently. Either outcome must leave the dashboard and the claim consistent. |
| C-1 splitting the 3082-line `state_builder.py` god-module regresses the Article X locked render functions | High | Medium | Mitigated | SW Dev + Architect | C-1 is a behind-the-tests refactor: `TestS1FootprintLockGuard` golden hashes must stay byte-identical; locked functions move wholesale, not rewritten. |
| Audit epics (SDD-045..048) hide too much scope behind four rows and slip | Medium | Medium | Mitigated | PM | Each epic's CLARIFY assigns per-item SDD-IDs with their own `validation.md` from the audit Acceptance blocks; sprint close requires 100% REQUIRED on the per-item validations, not the epic row. |
| Plain-language comms (SDD-044) is treated as cosmetic and not actually adopted | Low | Medium | Accepted | EM | The skill amendment makes it a checkable discipline; the owner will see it directly in every human-facing report. Drift is self-correcting because the owner reads the output. |

---

## Dependencies

**Internal**:
- PI-6 close commit `4ad0521` is the PI-7 base. Tests at 481 passed + 2 skipped
  is the floor; PI-7 must hold or improve this baseline.
- `docs/Temp/EMF-HARDENING-PLAN.md` is the spec source for the audit epics; each
  feature's `validation.md` is built from its "Acceptance" block. Verify each
  "Evidence" line against the live repo before acting (the plan was written
  against an earlier `master`).
- `cli/state_builder.py`: SDD-048 (C-1) splits this; the Article X locked render
  functions and `TestS1FootprintLockGuard` golden hashes are immutable.
- `cli/fleet.py` + `ledger/fleet.db` + `ledger/schema.sql`: SDD-045 (A-1) and
  SDD-046 (B-1) touch the ledger -- gitignore/init on detach, then truth on B-1.
- `.github/agents/`: SDD-043 adds the Sprint EM agent file.
- `.github/skills/` `em-communication-discipline`: SDD-044 amends this skill.
- `constitution/principles.md` + `docs/RULES.md`: B-3 (governance consistency)
  and a possible SDD-043 Article II reference change.

**External**:
- None. PI-7 is entirely in-repo and stdlib-only (the C-2 fork may propose one
  dependency, but that is an owner decision gated at Sprint 17 CLARIFY).

---

## Success Metrics

- All four PI-7 sprints close DONE with full per-item validation contracts
  (100% REQUIRED each), tests at or above the 481 floor, and schema lint clean.
- A teammate on a clean machine runs `git clone` + one setup command and reaches
  a lint-clean, test-passing checkout with their own empty ledger and no trace
  of the original author.
- `doctor` (and CI) is green, and a teammate can break a rule on purpose and
  watch it go red.
- The dashboard reads a ledger that the work is actually filling (or the
  universal-logging claim is gone) -- consistent either way.
- The constitution and the rules docs agree on the article range and say nothing
  the repo contradicts.
- A single-sprint session runs under the Sprint EM without inventing a new
  sprint/PI, and every human-facing report reads short and plain.

---

## Cross-references

- BACKLOG: PI-7 Hardening Bundle (filed 2026-06-26) -- SDD-043..048.
- Audit / spec source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md).
- Predecessor PI close: PI-6 CLOSED 2026-06-26 at `4ad0521`
  ([`../PI-6/CURRENT_PI.md`](../PI-6/CURRENT_PI.md)).
- Sprint 14 kickoff: [`../../feature-prompts/SPRINT-14-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-14-KICKOFF.prompt.md).
