---
id: SDD-20260608MODELUPGRADE-validation
type: validation
status: blocked
owner: principal-architect
updated: 2026-06-08
feature: 2026-06-08-model-upgrade-discipline
---

# Validation Contract: Model Upgrade Discipline (SDD-015)

- Spec ID: SDD-015
- Spec reference: `./spec.md`
- Status: **LOCKED at F-13 / TASKS 2026-06-08**
- Rule: zero unchecked REQUIRED items before SDD-015 implementation is considered complete. REQUIRED items cannot be loosened after lock without an explicit decision recorded here (Article X).

---

## Required Items (locked for F-14)

- [x] V-1. `docs/MODEL-UPGRADE-PROTOCOL.md` exists and defines full protocol triggers plus minor-patch log-only rules. Covers AC-1 / R1 / R8.
- [x] V-2. The protocol routes every in-scope model upgrade through `templates/level-2-decision.md` and explicitly maps evidence into money cost, complexity cost, maintenance burden, expected benefit, and alternatives considered. Covers AC-2 / R2 / R6.
- [x] V-3. Branch naming guidance and CLI behavior produce `model-upgrade/<old>-to-<new>` with safe slug components and rejection of empty or unsafe identifiers. Covers AC-3 / R3.
- [x] V-4. `templates/model-upgrade-workload.json` exists, is deterministic JSON, and includes at least one scenario for each required kind: `clarify`, `spec`, `plan-tasks`, `implement-report`, `review-report`. Covers AC-4 / R4.
- [x] V-5. `cli/model_upgrade.py compare` reads committed fixture inputs and captured old/new outputs, performs no network calls, and writes deterministic Markdown plus JSON comparison reports. Covers AC-5 / R5.
- [x] V-6. `templates/model-upgrade-pricing.json` exists and the CLI cost report calculates one-time, recurring, per-run, old-model, new-model, and delta cost values from committed inputs only. Covers AC-6 / R6.
- [x] V-7. Quality-delta output includes validation/test pass, spec-quality checklist score, commit/report quality delta, aggregate recommendation, and an owner-approval marker for ambiguous quality wins. Covers AC-7 / R7.
- [x] V-8. The protocol documents the rejection path: failed A/B, unclear cost benefit, or ambiguous quality without owner approval keeps the upgrade branch unmerged and records `reject` or `owner-review`. Covers R2 / R3 / R7.
- [ ] V-9. `decision-policy.md` references `docs/MODEL-UPGRADE-PROTOCOL.md`; because this is a constitution edit, `docs/ADR/016-model-upgrade-protocol-cross-reference.md` is accepted or an explicit owner waiver is recorded before the edit lands. Covers AC-8 / R9.
- [x] V-10. Import scan/test proves no third-party model, HTTP, benchmark, or data-analysis libraries are imported by `cli/model_upgrade.py`; stdlib-only Article V is preserved. Covers AC-9 / R10.
- [x] V-11. `python spec-driven-development/cli/schema_lint.py` exits 0 after F-14 implementation. Covers AC-10 / R11.
- [x] V-12. Full pytest suite exits 0 after F-14 implementation, with test count at or above the Sprint 8 baseline plus new SDD-015 tests. Covers AC-10 / R11.

---

## Manual / HITL Checks

- [ ] M-1. Owner or EM records approval for the first real model-upgrade proposal that uses this protocol before any model assignment changes land.
- [ ] M-2. Owner approval or ADR acceptance is recorded before `decision-policy.md` is edited in F-14.

Manual checks are not optional if their triggering condition occurs. M-2 is triggered by the Sprint 8 success criterion that `decision-policy.md` references the protocol.

---

## Optional / Best-Effort Items

- [ ] O-1. Example captured old/new output files are included under a non-secret fixture location to demonstrate report shape.
- [x] O-2. The protocol includes a short worked example for a hypothetical vendor swap using placeholder pricing.
- [ ] O-3. The CLI supports a `--threshold` option for owner-review thresholds while keeping deterministic defaults.

---

## Lock Notes

- CLARIFY closed 2026-06-08 after PM + Architect accepted Sprint 8 default answers for Q-J through Q-O.
- No constitution file is edited by F-13.
- F-14 cannot mark SDD-015 DONE without V-9. If ADR acceptance or owner waiver is unavailable, F-14 must stop as OWNER-ATTENTION.
- No REQUIRED item may be silently deferred from Sprint 8 close.


