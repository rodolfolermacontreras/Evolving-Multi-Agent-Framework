# Feedback to the Executive Manager: Add a Human-Readable Navigation Layer

## Context for this change

The framework already records everything it does — the SQLite ledger is a complete, machine-queryable audit trail, and the Azure dashboard gives a live runtime view. Both are working as intended. But there is a gap, and it is a real one: **at any given moment it is hard for a human to open the repo and see where we are** — which PI is active, which sprint is in flight, what document governs it, what was decided, and who did the work. The ledger answers this only if you query it; the dashboard answers it only while it's up and you're looking at it.

A previous project we ran had weaker tooling but much stronger *navigability*: you could open one tracker, follow it down, and always know the state of the whole effort at a glance. We want to bring that property into this framework **without removing anything that exists**. This is purely additive — a durable, version-controlled, Markdown navigation layer that sits *alongside* the ledger and dashboard, not in place of them.

Think of it as three complementary views of the same truth:
- **Ledger (SQLite)** — the complete audit trail. Authoritative, machine-readable, not glanceable.
- **Dashboard (Azure)** — the live runtime view. Real-time, external, ephemeral.
- **Tracker + INDEX (Markdown, in-repo)** — the durable human map. Glanceable, diffable, travels with the repo. *This is what we are adding.*

## The structure

Retire the flat `Temp` folder concept. Replace it with a `Management` folder under `docs`, organized by Program Increment, then by Sprint:

```
spec-driven-development/docs/
  HIGH_LEVEL_DEV_TRACKER.md          <- top of the pyramid; spans all PIs
  Management/
    PI-1/
      INDEX.md                       <- PI-level navigation + decisions + agent notes
      Sprint-1/
        SPRINT_1_DETAILED_<TITLE>.md <- full spec / task decomposition / validation contract
        AGENT_NOTES.md               <- on-the-ground notes from the worker(s)
      Sprint-2/
        ...
    PI-2/
      INDEX.md
      Sprint-1/
        ...
    PI-N/
      INDEX.md
      ...
```

The principle is a strict three-tier drill-down, each layer linking to the one below:

**Open the tracker → see which PI is live → open that PI's INDEX → see which sprint is live and why decisions were made → open the sprint folder for full detail.**

That single path is what restores "I always know where we are."

## What each layer holds

### `HIGH_LEVEL_DEV_TRACKER.md` (docs root)
The bird's-eye view, and nothing more. Every PI from 1 to N with a status (Proposed / Active / Closed) and a one-line summary, the currently active PI and sprint clearly marked, the top 3 next moves, and current blockers (for example, the feature blocked on human-in-the-loop Azure OIDC provisioning). Each PI line **links to that PI's `INDEX.md`**. No design detail lives here — it is abstraction only. Updated every session.

### `Management/PI-#/INDEX.md` (per PI)
The hinge of the whole system. For its PI it carries: the PI goal/theme (e.g. PI-1 generalization, PI-2 fleet maturity, PI-3 portability validation); the list of sprints with status; **what was actually done**, feature by feature (SDD-001, SDD-002, ...); the **key design decisions**, each linking to its ADR; **where the full spec lives**, linking down into the relevant `Sprint-#/` folder; and the **on-the-ground notes and lessons** captured by the agents who did the work. Anyone reading the tracker plus the relevant INDEX should understand both *what* happened and *why*, without having to open every sprint file.

### `Management/PI-#/Sprint-#/` (per sprint)
The deep detail — the equivalent of the old detailed sprint document, now with room to breathe: the full spec and task decomposition (T-001, ...), the locked validation contract, dispatch/owner assignments, validation results, and a separate `AGENT_NOTES.md` where the worker agents record what they actually did, hit, and learned on the ground. Superseded files are archived here, not deleted.

## Keeping it honest (important)

A hand-maintained Markdown tracker rots the moment updating it becomes optional. To prevent the navigation layer from drifting out of sync with the ledger and reality, bind its updates to ceremonies that already exist rather than leaving them to discretion:

- Updating the active `Sprint-#/` files is part of each **dispatch/REVIEW** cycle.
- Updating the PI `INDEX.md` (decisions, what-was-done, lessons) is part of **DONE** and **/replan**.
- Updating `HIGH_LEVEL_DEV_TRACKER.md` happens **every session**.

Where possible, **generate the mechanical parts of the INDEX from the ledger** (sprint list, dispatch counts, status) so the two cannot disagree, and reserve human/agent prose for the parts the ledger can't capture — design rationale and ground notes. The ledger stays the source of truth; the INDEX is its readable projection plus the narrative the ledger lacks.

## Onboarding and rules updates this implies

- Add the tracker to the agent read-order so a fresh agent learns the map early: after the core read sequence, it should open `HIGH_LEVEL_DEV_TRACKER.md`, then the active PI's `INDEX.md`, before touching its sprint.
- Add a rule: **no work on a sprint without a corresponding `Management/PI-#/Sprint-#/` folder and a tracker entry.** Untracked work is not permitted — this is the same traceability discipline applied to navigation.
- The Executive Manager owns the tracker and the PI INDEX files; this is its honest-abstraction layer. It maintains these *instead of* absorbing sprint detail, which keeps its context light while still giving the human a complete view.

## One question before you implement

We currently use `SPRINT_#_DETAILED_<TITLE>.md` for the detail file. Now that each sprint has its own folder, confirm whether you want to keep that filename inside the folder or simplify it (e.g. `SPEC.md` + `AGENT_NOTES.md` per sprint folder, with the descriptive title carried by the folder name `Sprint-#-<title>`). Propose your preferred convention and we'll lock it before generating the structure.
