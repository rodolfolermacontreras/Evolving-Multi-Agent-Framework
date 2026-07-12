# SPRINT 24 KICKOFF -- PI-9 Sprint 3 / Final brownfield bootstrap correctness sprint

You are leading **overall Sprint 24**, the **third and final sprint of PI-9
("Experience Polish")**. This sprint contains exactly one feature: **SDD-058**, the
owner-approved P1 brownfield bootstrap correctness defect. PI-9 remains ACTIVE
throughout the sprint and closes only after SDD-058 ships.

Owner authorization, verbatim: "Owner approved Option 1 on 2026-07-12: authorize
one final PI-9 sprint dedicated exclusively to the approved P1 brownfield
bootstrap correctness defect, then close PI-9 after it ships."

The first real brownfield adoption, a Node/Express Claude copilot application,
proved four product defects:

1. **B1 -- edited-proposal preservation:** `--apply` regenerates the proposal and
   destroys human-filled answers before applying it.
2. **B2 -- reusable-asset allowlist / no framework-state contamination:** apply
   copies this framework project's backlog, specs, sprints, dispatches, exec state,
   ledger history, and other operating state into the host.
3. **B3 -- host-specific identity/config scaffolding:** apply copies framework
   Copilot instructions and does not generate a host `project.config.json`.
4. **B4 -- truthful host readiness:** the current doctor is framework-shaped and
   cannot honestly serve as a generic host-readiness gate.

Do not choose the technical copy, refresh, or doctor contract in this kickoff.
The Architect must resolve those decisions through CLARIFY and an ADR-backed SPEC.
Because SDD-058 is cross-cutting, an ADR is mandatory, not optional: author it
after CLARIFY resolves the contract, review it with the full spec, and obtain
Architect plus owner approval before PLAN/TASKS or implementation begins.

---

## LEADER -- who runs this sprint

This sprint is led by the **Sprint Executive Manager** agent (SDD-043 / ADR-020),
not the project Executive Manager.

- Activate `sprint-executive-manager` and keep it sprint-scoped.
- It routes PM, Architect, Software Developer, and worker work; it does not make
  product, architecture, or implementation decisions.
- It reports up to the project Executive Manager at close.
- Bind **SDD-044**: all owner-facing communication is short and plain.
- Bind **SDD-053**: every owner decision uses the mandatory decision-request
  format, one decision per message, with the ask at the end.

---

## HARD PREREQUISITE -- STOP IF NOT MET

1. `git status --short` is clean before feature work begins.
2. `HEAD == origin/master`, and `d77d4ab` is an ancestor of `HEAD`. The Sprint 24
   establishment commit may legitimately advance the head beyond that clean
   Sprint 23 close baseline.
3. Sprint 23 is CLOSED; PI-9 is ACTIVE; Sprint 24 is the current final PI-9
   sprint; SDD-058 is its only backlog item.
4. `python -m pytest spec-driven-development/ --tb=no -q` returns **668 passed / 2
   skipped** at the baseline.
5. Public GitHub Actions CI is green for the baseline.
6. Schema, origin, and stale-doc lints are clean; Article X lock checks pass.
7. B-1, B-2, and B-4 remain live: genuine ledger outcomes, TDD/DONE blocking
   checks, and public CI are mandatory.
8. Owner authorization above is recorded. Separate owner approval is still
   required before any push and before destructive apply against a real host.

If any prerequisite fails, STOP as OWNER-ATTENTION. Do not weaken or waive a gate.

---

## 0. How to use this prompt

1. Read `_SHARED_ONBOARDING.md`, this kickoff, PI-9 `CURRENT_PI.md`, SDD-058 in
   `BACKLOG.md`, and the original preserved evidence in `IDEAS.md`.
2. Verify every hard prerequisite directly.
3. Activate the Sprint Executive Manager.
4. Use one context-isolated unit per feature (Article VII): fresh chat or
   Sprint-EM-routed subagent dispatch. There is only one feature in this sprint.
5. Enforce Article XI serial gates: no competing feature may occupy CLARIFY or
   SPEC. Do not force-release without the governed reason and ledger record.
6. Append evidence to `exec/sprint-progress.md`; never rewrite history.
7. Do not hand-edit generated `exec/state.md`, `exec/state.html`, or
   `exec/work-index.md`; regenerate them only through the canonical builder when
   the lifecycle calls for it.

---

## 1. Sprint goal

After Sprint 24, brownfield bootstrap safely converts an approved proposal into a
clean, host-specific SDD installation without destroying human edits or importing
the framework project's identity and runtime history, and it communicates an
honest host-readiness contract.

Capacity: one full cross-cutting feature, SDD-058 only.

Primary risk: ambiguous refresh/copy/readiness semantics could preserve the
original data-loss or contamination defect under a different name. Resolve the
contract before implementation and prove it on clean representative fixtures.

### Product boundaries

- **B1:** preserve edited proposals. CLARIFY must define preserve-edits versus
  explicit refresh semantics and conflict behavior.
- **B2:** define the exact reusable-asset allowlist. A host begins with clean
  runtime state: no framework backlog, specs, sprints, dispatches, exec snapshots,
  ledger rows, reorder history, or other framework project state.
- **B3:** generate host-specific `.github/copilot-instructions.md` and
  `project.config.json`. CLARIFY must define the generated host identity and config
  fields from evidence, defaults, and human-required values.
- **B4:** define host-mode doctor or an honest documented/enforced contract that
  does not present framework self-checks as host readiness.
- Preserve migration/backward compatibility for existing proposal/adoption flows.
- Include dry-run, diff, and backup/rollback safety in the contract.
- No destructive apply against a real host without explicit owner approval.

### Explicit exclusions

- SDD-035 Azure decommission remains out-of-band.
- Sprint 23 retro reconciliation is a separate cleanup.
- SDD-034 is excluded.
- Dashboard work is excluded.
- No unrelated backlog, housekeeping, constitution change, dependency, schema
  migration, cloud work, or feature may enter Sprint 24.

---

## 2. Required sequence -- serial gates

| Order | Phase | Owner | Required outcome |
|-------|-------|-------|------------------|
| 1 | CLARIFY | PM + Architect | Close every product question below; confirm one repo-wide CLARIFY lock holder; record recommendations and owner decisions. |
| 2 | SPEC + ADR | Architect, PM requirements review, owner approval | Full cross-cutting spec and Article X validation contract; mandatory ADR authored from the closed CLARIFY decisions, reviewed with the spec, and accepted by the Architect and owner. No PLAN/TASKS or implementation before approval. |
| 3 | PLAN + TASKS | Architect + Software Developer | After the SPEC/ADR gate passes, define the implementation approach and atomic TDD tasks with explicit file scopes, fixture matrix, safety checks, and acceptance traceability. |
| 4 | TDD IMPLEMENT + two-stage QA | Software Developer + workers | Failing tests first; implementation; spec-compliance review before code-quality review; Windows/POSIX and cross-stack evidence. |
| 5 | CLOSE | Sprint EM + PM + Architect + Software Developer | All validation and B-gates green; owner pre-push approval; push; public CI green; SDD-058 DONE; Sprint 24 close; then report up for PI-9 close execution. |

Do not parallelize CLARIFY or SPEC. Implementation may parallelize only after the
Software Developer proves disjoint file scopes with SDD-049; otherwise serialize.

---

## 3. Mandatory CLARIFY topics

Resolve and record all of these before SPEC approval:

1. **Preserve edits vs refresh semantics:** what `--apply` does with an existing,
   edited proposal; how a user explicitly requests refresh; how conflicts and
   partially edited proposals are surfaced without silent data loss.
2. **Exact allowlist:** which reusable framework assets may be copied and which
   project/runtime/history paths are forbidden. Default-deny anything not listed.
3. **Generated host identity/config:** exact host-specific Copilot-instruction
   content and `project.config.json` fields; archaeology-derived versus required
   human values; validation for missing/ambiguous identity.
4. **Clean runtime state:** initial backlog/spec/sprint/dispatch/exec/ledger state,
   directory creation, ignored files, and proof that no framework rows or PI names
   survive.
5. **Host-mode doctor definition:** what host readiness means, which checks are
   portable, which are framework-only, exit behavior, and the honest fallback if
   a host-mode doctor is not shipped.
6. **Migration and backward compatibility:** behavior for existing proposals,
   already-adopted hosts, legacy flags, and reruns/idempotence.
7. **Safety:** dry-run output, human-readable diff, backup/restore or rollback,
   failure atomicity, and explicit approval before destructive real-host apply.
8. **Fixture realism:** a clean realistic Node/Express host matching the original
   evidence plus at least one materially different cross-stack host fixture.

The PM owns product boundaries. The Architect owns technical design and ADRs.
Do not turn recommendations in this kickoff into unreviewed architecture.

---

## 4. Hard constraints

- **Article VII:** one feature, one context-isolated unit; project EM remains
  high-level.
- **Article XI:** CLARIFY and SPEC are repo-wide serial gates.
- **Article X:** validation is authored and approved before implementation, then
  locked at TASKS. No validation backfill after code.
- **B-1:** record genuine Sprint 24 dispatch/review/close outcomes in the local
  ledger before close; never fabricate rows.
- **B-2:** TDD gate and DONE-completeness checks remain blocking.
- **B-4:** public CI must be green after the owner-approved push.
- **Stdlib-only framework CLI constraint:** no new runtime or test dependency.
- **No framework-state contamination:** exact fixture assertions must prove no
  framework backlog/spec/sprint/dispatch/exec/ledger/reorder history or framework
  identity enters a host.
- **Representative clean fixtures:** Windows and POSIX path/line-ending behavior;
  realistic Node/Express plus at least one cross-stack host.
- **Safety:** no destructive real-host apply without owner approval. Prefer
  isolated temporary fixtures for automated/manual proof.
- **Git discipline:** explicit path staging only; never `git add -A` or
  `git add .`. No push without recorded owner pre-push approval.
- **No hand edits to generated exec surfaces.** Use the canonical builder only.
- **No silent REQUIRED deferral, history scrub, scope substitution, or PI close.**
  Sprint 24 may prepare and execute its close only after the feature ships; PI-9
  remains ACTIVE until then.

---

## 5. Close criteria

1. B1-B4 each have approved requirements, acceptance criteria, and passing
   evidence with no silent weakening.
2. Edited proposal answers survive apply exactly as the approved contract defines;
   refresh is explicit, observable, and non-destructive by default.
3. Apply copies only approved reusable assets and creates clean runtime state;
   no framework project state or identity contaminates either fixture.
4. Host-specific Copilot instructions and project config are generated and
   validated from the approved fields/defaults.
5. Host readiness is truthful: host-mode doctor passes its defined fixtures, or
   the approved honest docs/contract is enforced and cannot be mistaken for a
   passing host gate.
6. Migration/backward compatibility, rerun/idempotence, dry-run/diff/backup, and
   failure/rollback behavior pass the locked contract.
7. Clean fixture matrix passes on Windows/POSIX with realistic Node/Express plus
   at least one cross-stack host.
8. Full suite is at least 668 passed / 2 skipped with no regression; focused RED
   and GREEN evidence is recorded.
9. Schema/origin/stale-doc/governance checks, Article X lock checks, local doctor,
   B-1, and B-2 are green.
10. PM verifies every acceptance criterion; the mandatory ADR was accepted by
   the Architect and owner before PLAN/TASKS; two-stage QA passes in order.
11. Owner approves the exact pre-push package; only then push. Public CI/B-4 must
    finish green before Sprint 24 is CLOSED or SDD-058 is marked DONE.
12. Sprint EM reports the shipped result up to project EM. PI-9 close follows the
    owner-authorized sequence after SDD-058 ships; do not pre-close PI-9.

---

## 6. Do NOT do

- Do not create a second feature or pull in any excluded item.
- Do not implement before CLARIFY -> SPEC/ADR -> PLAN/TASKS completes.
- Do not let kickoff wording decide technical copy/refresh/doctor architecture.
- Do not copy the framework tree and then clean it after the fact unless the
  approved Architect contract explicitly proves that approach safe; B2 is an
  allowlist/default-deny product requirement.
- Do not overwrite an edited proposal silently.
- Do not run destructive apply on a real host without explicit owner approval.
- Do not claim host readiness using framework-only checks.
- Do not hand-edit generated exec state, weaken gates, fabricate evidence, scrub
  history, commit, or push without the required approvals.