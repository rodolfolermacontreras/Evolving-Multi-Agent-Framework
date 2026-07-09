---
id: SDD-20260709FOVL-clarify
type: clarification
status: done
owner: principal-architect
updated: 2026-07-09
feature: 2026-07-09-file-overlap-detector
---

# CLARIFY: SDD-049 -- File-overlap conflict detector for fleet dispatch

- Feature ID: SDD-049
- Sprint: PI-9 / Sprint 1 (Sprint 22); design + implementation F-60
- Source: SDD-047 D-3 (the honest placeholder left when the "conflict detection"
  over-claim was removed from `GENERALIZATION_SDD.md` + `constitution/roadmap.md`).

---

## Questions, recommendations, answers

### Q-C -- block vs warn on overlap
- Question: when two tasks in the same dispatch batch declare the same IN-scope
  file, should the tool hard-block the dispatch or only warn?
- Recommendation: block by default, with an explicit `--allow-overlap` override
  flag (consistent with the force-as-deliberate-Level-2 governance in ADR-017) so
  the safe path is automatic and the override is a deliberate act.
- Answer (owner-approved default 2026-07-09, "jump to these two"): **block by
  default; `--allow-overlap` downgrades to a warning and proceeds.**
- Status: RESOLVED.

### Q-scope -- what counts as a task's IN-scope file set
- Question: where does the detector read each task's declared files from?
- Recommendation: reuse the existing `tasks.md` `File Scope` column, parsed with
  the same rules `render_brief` already uses (split on `,`/`;`, strip backticks),
  so there is a single declared-scope source of truth. Placeholder/"none" tokens
  name no file and never conflict.
- Answer: **reuse the `File Scope` column via a shared `parse_file_scope` helper.**
- Status: RESOLVED.

### Q-lock -- Article X impact
- Question: does the detector touch any Article X locked render/load function?
- Recommendation / Answer: **No.** The detector lives entirely in `cli/fleet.py`,
  a leaf CLI with no locked function. `TestS1FootprintLockGuard` stays GREEN.
- Status: RESOLVED.

### Q-level -- decision level
- Answer: **Level-1, no ADR, no `constitution/**` edit, no version bump.** Leaf-CLI
  behavior addition, stdlib-only (Article V). No new rule; it automates an existing
  manual discipline. Architect-confirmed.
- Status: RESOLVED.

---

## Lock

CLARIFY closed at F-60 design. The validation contract (`validation.md`) is LOCKED
from this point; implementation must satisfy every REQUIRED item with evidence.
