---
id: SDD-20260626MAKEPROMISESTRUE-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-make-promises-true
---

# CLARIFY: SDD-046 -- "Make promises true" (B-1 ledger, B-2 blocking checks, B-4 CI)

- Feature ID: SDD-046 (epic). Per-item codes carried verbatim from EMF-HARDENING-PLAN Part B: B-1, B-2, B-4.
- Sprint: PI-7 Sprint 15 (Sprint 2 of PI-7).
- Status: CLARIFY done. Owner: principal-product-manager (technical answers co-owned with principal-architect).
- Source audit: `spec-driven-development/docs/Temp/EMF-HARDENING-PLAN.md` Part B (lines 201-285).
- Sibling precedent (format + grouping template): `spec-driven-development/specs/2026-06-26-detach-clone-and-run-hardening/` (SDD-045, merged).

---

## Ground Rules

- This is a HOW-only clarification. The WHAT for B-1 is owner-LOCKED (Option 1 "make it real", confirmed 2026-06-26). CLARIFY may refine implementation shape; it may NOT re-open the B-1 fork or retract Article VII / RULES Rule 4.
- Every Evidence line below was re-verified LIVE against the repo on 2026-06-26 (not taken on faith from the audit). Mismatches are flagged inline.
- Constraints inherited and non-negotiable: stdlib-only (Article V); Article X locked functions immutable and `TestS1FootprintLockGuard` golden SHA-256 stays PASS; append-only ledger; no edits under `constitution/**`; baseline >= 501 passed / 2 skipped and only grows.
- This sprint dogfoods its own gate: Sprint 15 itself must close with its dispatch outcomes in the ledger (B-1 acceptance applied to Sprint 15).

---

## Scope -- epic decomposition

| Item | Title | In scope this sprint | Lock state |
|------|-------|----------------------|------------|
| B-1 | Make the ledger true | YES -- THE priority item | WHAT locked (Option 1). HOW open. |
| B-2 | Turn the rules you care about into blocking checks | YES -- >= 2 named rules | Rule selection open (this CLARIFY decides). |
| B-4 | Add CI so checks fire for everyone, every push | YES -- one workflow == doctor set | ADR-009 disposition open (this CLARIFY decides). |
| B-3 | Governance cross-reference consistency | NO -- delivered in SDD-045 (Sprint 14) | Out of scope; do not touch. |

---

## Per-item stale-check (Evidence verified LIVE on 2026-06-26)

| Item | Audit Evidence claim | Live re-verification | Match? |
|------|----------------------|----------------------|--------|
| B-1 | `tdd-gate` referenced by zero agents/prompts; ledger has rows only from PI-2; RULES Section 4 requires a ledger row at DONE | `fleet.py mark` signature confirmed (`--dispatch-id N --outcome {success,failed,blocked}`); `record_dispatch`/`mark_outcome` exist in `ledger_cli`; `/qa` and `/retro` prompts read fully -- NEITHER writes a ledger row | MATCH |
| B-2 | `tdd-gate/SKILL.md` is prose, referenced by nobody; only `schema_lint.py` is enforcing | `tdd-gate/SKILL.md` present, contains full "Mechanical Check" algorithm + `[NO-TEST-NEEDED]` escape hatch, wired to zero agents/prompts | MATCH |
| B-4 | No `.github/workflows/` exists; `ADR-009` references CI not present | `file_search '.github/workflows/*.yml'` -> NO files. `ADR-009` present, describes CI **OIDC deploy to Azure ACA production** (not a doctor/test CI) | MATCH (and see Q-D) |
| infra | doctor is the single enforcement surface | `run_doctor(root, *, run_tests=True)` exists in `bootstrap.py`, aggregates a `checks` list (ledger reachable+untracked, schema_lint, governance, origin-tokens, tests); `make doctor` and `make setup` both invoke `bootstrap.py` | MATCH -- this is the attach point for B-1 + B-2 |

No Evidence-line mismatches found. All three items are real, current gaps.

---

## Decision Summary

| Q | Item | Locked decision | Level |
|---|------|-----------------|-------|
| Q-A | B-1 | doctor's B-1 check is a hard CHECK (fail), not a warn, for the current PI; "current PI" read from the newest active `sprints/PI-*/CURRENT_PI.md` marker via a NEW read-only helper | L1 (architect) |
| Q-B | B-1 | `fleet.py mark` becomes the documented one-line close step; `/qa` and `/retro` prompts gain an explicit "write ledger row" close step; no new subcommand invented | L1 |
| Q-C | B-2 | Ship exactly TWO blocking rules: (1) TDD gate, (2) DONE-completeness. File-scope deferred to an OPTIONAL item (O-1) | L1 |
| Q-D | B-4 | One workflow `.github/workflows/doctor.yml` invoking `make doctor`; SUPERSEDE ADR-009 with a NEW ADR-021 (doctor-CI), authored in F-39 | L1 |
| Q-E | B-2 | Prose skills point AT the enforcing scripts (skill keeps the algorithm, gains a "Enforced by:" pointer); scripts are the source of truth for pass/fail | L1 |
| Q-F | all | New CLI modules are stdlib-only and expose a `main(argv)` per CLI-PATTERN.md, so doctor and CI call the identical entrypoint | L0 (convention) |

---

### Q-A -- B-1: warn or hard-fail, and how is "current PI" determined?

- Context: the audit's Option-1 acceptance says "closing a feature with unlogged dispatches fails a check" AND "doctor warns if the current PI has zero rows." Two different strengths (fail vs warn).
- Options:
  - A1: doctor only WARNS on zero current-PI rows. Low friction, weak promise.
  - A2: doctor's current-PI dispatch check is a hard CHECK (counts toward red doctor) when the current PI has zero dispatch rows. Strong, dogfoodable this sprint.
  - A3: separate "close-gate" check distinct from doctor.
- Recommendation: **A2**. The promise being repaired is a hard one (RULES Section 4 lists a ledger row in the DONE checklist). A warn does not make the promise true. "Current PI" is read from the highest-numbered active `sprints/PI-*/CURRENT_PI.md` marker (the same source `state_builder` already globs) via a NEW read-only helper in `bootstrap.py` -- no edit to any Article X locked function. The check counts `dispatches` rows WHERE `pi = <current PI name>`; zero rows for an active PI fails the check.

### Q-B -- B-1: what is the exact close step, and where is it wired?

- Context: `/qa` (Phase 8) and `/retro` (Phase 9) prompts currently produce verdicts/retros with NO ledger write. The close flow has no ledger touchpoint.
- Options:
  - B1: invent a new `fleet.py close` subcommand.
  - B2: reuse the existing `fleet.py mark --dispatch-id N --outcome ...` as the documented close one-liner; add a "write ledger row(s)" step to `/qa` and `/retro` prompts.
- Recommendation: **B2**. `mark` already exists and writes the right row. No new surface area, no new tests for a new subcommand. The prompts gain one explicit close step each ("Before declaring the feature DONE, record each dispatch outcome with `fleet.py mark`; doctor will verify the current PI has rows"). This is the lowest-friction path the audit asked for.

### Q-C -- B-2: which two (or three) rules become blocking checks?

- Context: audit lists three candidates -- TDD gate, file-scope (>3 production files), DONE-completeness. Acceptance requires >= 2 named rules that fail a command, each with a test proving it catches a real violation. Audit warns false positives erode trust; "start with the TDD gate where the logic is already specified."
- Options:
  - C1: TDD gate + file-scope.
  - C2: TDD gate + DONE-completeness.
  - C3: all three.
- Recommendation: **C2 (TDD gate + DONE-completeness)**.
  - TDD gate is the anchor -- its algorithm already exists in `tdd-gate/SKILL.md` (port prose to `cli/tdd_gate_check.py`); fails when production paths changed without a test change and no `[NO-TEST-NEEDED]` tag.
  - DONE-completeness is a static, deterministic check on a closed feature dir (has spec.md, validation.md with all REQUIRED `[ ]` boxes checked, and a retro). It has near-zero false-positive risk and SYNERGIZES with B-1 (both express "a feature cannot be DONE unless..."), so the two B-2 rules and the B-1 close-gate reinforce one stay-honest story.
  - File-scope is DEFERRED to optional O-1: it requires diff/commit-range analysis and carries the highest false-positive risk on legitimate refactors -- exactly the "erodes trust" failure the audit flags. Land it later once the TDD gate's diff plumbing is proven.

### Q-D -- B-4: what disposition for ADR-009, and what does the workflow run?

- Context: ADR-009 (`009-ci-oidc-deploys-to-production.md`, status: proposed) adopts GitHub Actions OIDC federation for CI auto-deploy to Azure Container Apps **production**. SDD-046 B-4 needs a CI that runs the **doctor set** (tests + schema_lint + B-2 checks + origin lint) on push/PR -- no deploy, no Azure. Azure dashboard was decommissioned (ADR-015 / SDD-035), so ADR-009's premise (auto-deploy to ACA) is moot.
- Options:
  - D1: amend ADR-009 in place to describe doctor-CI. Rejected -- materially different decision (deploy vs validate), and rewriting a proposed ADR's core decision hides history.
  - D2: SUPERSEDE ADR-009 with a NEW ADR (doctor-CI), mark ADR-009 status `superseded`, and record why (Azure decommissioned, CI scope is validation-only).
- Recommendation: **D2**. New ADR number = **ADR-021** (highest existing is 020). The workflow `.github/workflows/doctor.yml` invokes `make doctor` (== `python spec-driven-development/cli/bootstrap.py doctor`) so local and CI run the byte-identical entrypoint -- they cannot drift. ADR-021 is AUTHORED IN F-39 (implement), not in F-38; F-38 only records the supersede decision and assigns the number (authoring an ADR is out of F-38's "spec-dir artifacts only" scope).

### Q-E -- B-2: relationship between the prose skills and the new scripts.

- Decision: the enforcing script is the source of truth for pass/fail. The prose skill (`tdd-gate/SKILL.md`) keeps its algorithm for human readers but gains an "Enforced by: `spec-driven-development/cli/tdd_gate_check.py`" pointer (audit acceptance: "the corresponding prose skills point at the enforcing script"). No skill becomes the gate; the script is the gate.

### Q-F -- F: CLI shape so doctor and CI never diverge.

- Decision: each new check is a stdlib-only module under `spec-driven-development/cli/` exposing `main(argv: list[str]) -> int` (CLI-PATTERN.md). `run_doctor` calls the in-process function; CI calls `make doctor` which calls the same `run_doctor`. One code path, two invocations.

---

## OWNER-ATTENTION

- B-1 WHAT is owner-locked (Option 1). Nothing in this CLARIFY changes that. The only owner-visible behavior change is: an active PI with zero dispatch rows now turns `doctor` red, and Sprint 15 must log its own dispatches before close. No constitution edit is required (Article VII and RULES Rule 4 are made TRUE rather than retracted).
- ADR-009 will be marked `superseded` by ADR-021 in F-39. Flagging because ADR status changes are governance-visible.

---

## Carry-forward to SPEC

1. B-1 -> FR set for: `fleet.py mark` as documented close step; `/qa` + `/retro` ledger-write close step; doctor hard-check on current-PI dispatch rows; current-PI read via new read-only helper.
2. B-2 -> FR set for: `cli/tdd_gate_check.py` (TDD gate) and `cli/done_check.py` (DONE-completeness); both wired into `run_doctor`; prose skills point at scripts; each rule has a test catching a real violation.
3. B-4 -> FR set for: `.github/workflows/doctor.yml` == `make doctor`; ADR-009 superseded by ADR-021 (authored F-39).
4. Cross-cutting -> stdlib-only; locked-fn guard PASS; schema_lint clean; baseline >= 501/2 grows; Sprint 15 dogfoods B-1 at its own close.
