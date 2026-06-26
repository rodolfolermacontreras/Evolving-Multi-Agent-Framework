# ADR-022: De-author the constitution (owner/identity + over-claim rename)

- Date: 2026-06-26
- Status: accepted
- Related: SDD-047 (A-2 / A-3 / D-3); EMF-HARDENING-PLAN Parts A + D

## Context

SDD-047 (PI-7 Sprint 16, "de-author") strips the personal and origin
fingerprints out of the framework so a teammate who clones it cannot tell who
wrote it or which project it grew out of. Most of that work lands in
Level-0/1 surfaces (agent definitions, skills, `INSTRUCTIONS.md`,
README-as-instruction, a new `project.config.json`, the A-6 lint, the skill
library). Three target lines, however, live under `constitution/**`:

- `constitution/mission.md` (line 17) names the owner.
- `constitution/decision-policy.md` (line 57) names the owner as "human owner".
- `constitution/roadmap.md` (line 78) carries the over-claimed
  "Conflict-detection workflow ... deferred" wording that D-3 renames to the
  serial CLARIFY/SPEC gate the code actually implements.

Per `constitution/decision-policy.md` and the Sprint 16 Hard Constraints, any
change to `constitution/**` wording is a **Level-2 decision**: it requires an
ADR, recorded owner approval, and a constitution version bump. It cannot be made
silently or by a Level-0/Level-1 agent.

## Decision (accepted 2026-06-26)

1. **mission.md**: replace the hardcoded owner name with a reference to the
   host project's owner as defined in `project.config.json` (`owner`). The
   constitution describes the role ("the host project's owner"), not a person.
2. **decision-policy.md**: change "Authority: Rodolfo (human owner)" to
   "Authority: the host project's owner (human)", resolving identity to config.
3. **roadmap.md**: rename the "Conflict-detection workflow validated against a
   real two-worker collision (deferred)" line to describe the serial
   CLARIFY/SPEC gate (`fleet.py` `_scan_lock_state`), with a true file-overlap
   detector filed separately as SDD-049.
4. Bump the constitution version per the existing versioning convention and
   record this ADR + owner approval in the change log.

## Status / blocker

This ADR is **accepted**. The owner ratified it on 2026-06-26 (Level-2 approval
recorded in the Sprint 16 session). The corresponding edits (tasks T-047-13)
are now unblocked and applied: mission.md, decision-policy.md, and roadmap.md
de-authored and version-bumped; SDD-049 filed for the true file-overlap
detector.

## Consequences

Positive:
- The constitution stops welding the framework to one person.
- The over-claim is removed at its constitutional source, not just in guidance.

Negative / cost:
- A constitution version bump and a second (owner-available) session to land the
  three edits.

## Alternatives considered

- **Move owner/identity entirely out of the constitution.** Rejected: the
  constitution legitimately references the role of "owner"; only the *name* must
  leave. Config reference keeps the role and removes the person.
- **Leave the constitution as-is and exempt it from A-6.** Rejected: that would
  leave a personal fingerprint in the most-read governance files and contradict
  the SDD-047 goal.
