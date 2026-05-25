# ADR-011: Three-Tier Navigation Layer (Management/ Structure)

- Date: 2026-05-25
- Status: accepted

## Context

The framework records all work in two complementary systems: a SQLite ledger
(`ledger/fleet.db`) that is authoritative and machine-queryable, and an Azure
dashboard (`exec/state.html`) that provides a live runtime view. Both are
working as intended. However, external feedback from a parallel team adopting
the framework identified a gap: **at any given moment it is hard for a human
to open the repo and see where we are** -- which PI is active, which sprint
is in flight, what document governs it, what was decided, and who did the
work. The ledger answers this only if you query it; the dashboard answers it
only while it is up and you are looking at it.

The current `HIGH_LEVEL_DEV_TRACKER.md` provides a sprint board but
terminates at flat `docs/Temp/` files with no PI-level narrative, no
hierarchical navigation, and no ceremony binding to prevent drift. The
`exec/state.md` is an auto-generated snapshot for executive briefings, not a
navigable map for humans or agents onboarding mid-PI. No existing artifact
gives a fresh reader the path "which PI -> which sprint -> what was decided
and why -> who did the work" in under 60 seconds by following Markdown links.

The parallel team's previous framework had weaker underlying tooling but
stronger navigability. They proposed bringing that navigability property into
this framework without removing anything that exists.

## Decision

Adopt a **three-tier human-readable navigation layer** in the repository,
implemented as a `docs/Management/` directory hierarchy:

```
HIGH_LEVEL_DEV_TRACKER.md   (Tier 1: bird's-eye, links to PI INDEXes)
  -> Management/PI-N/INDEX.md   (Tier 2: PI narrative, links to sprint folders)
    -> Management/PI-N/Sprint-N-{title}/SPEC.md + AGENT_NOTES.md   (Tier 3: deep detail)
```

This is the third complementary view of the same truth:
- **Ledger (SQLite)** -- complete audit trail. Authoritative, machine-readable,
  not glanceable.
- **Dashboard (Azure)** -- live runtime view. Real-time, external, ephemeral.
- **Tracker + Management/ (Markdown, in-repo)** -- durable human map.
  Glanceable, diffable, travels with the repo.

The navigation layer is purely additive. The ledger and dashboard remain
authoritative for their respective dimensions.

Naming convention: folders carry the descriptive title in kebab-case
(`Sprint-N-<kebab-title>/`). Required files inside: `SPEC.md` (the
coordination doc, migrated from `SPRINT_#_DETAILED_*.md`) and
`AGENT_NOTES.md` (on-the-ground notes from workers). Optional per-sprint
artifacts: `RETRO.md`, `mockup.html`, `DESIGN_TOKENS.md`.

The flat `docs/Temp/` directory is deprecated. Existing sprint detail docs
migrate to `Management/PI-3/Sprint-N-{title}/SPEC.md` via `git mv` to
preserve history.

Mechanical sections of PI INDEX files (sprint list, dispatch counts, last
outcome) are auto-generated from the ledger by `cli/state_builder.py
build-index` using `<!-- BEGIN/END auto-generated -->` marker blocks. Human-
authored prose (rationale, lessons, design decisions) lives outside the
markers and is preserved across regenerations.

Update discipline is bound to existing ceremonies, not left to discretion:
- `SPEC.md` updated each dispatch/REVIEW cycle.
- PI `INDEX.md` updated at DONE and `/replan`.
- `HIGH_LEVEL_DEV_TRACKER.md` updated every session.

A new Rule 13 ("No untracked sprint work") enforces that no sprint may begin
without a corresponding `Management/PI-#/Sprint-#-{title}/` folder and
tracker entry.

## Consequences

Positive:
- Restores the "open the repo and know where we are in 60 seconds" property
  that the parallel team's previous framework had.
- Provides a version-controlled, diffable navigation map that travels with
  the repo (no external service dependency).
- Backfilled PI-1 and PI-2 INDEXes give the full project history a
  navigable structure for the first time.
- Auto-generated mechanical sections prevent the most rot-prone parts of the
  INDEX from drifting out of sync with the ledger.
- Ceremony binding (Rule 13 + DONE definition amendments) makes navigation
  layer updates non-optional.

Negative:
- Adds a maintenance surface: three tiers of Markdown that must be kept
  current alongside the ledger and dashboard.
- PI-1 backfill is archaeology -- some sprint-level groupings are subjective
  and reconstructed from the commit log, not from formal sprint records.
  Mitigated by marking provenance as "reconstructed."
- Rule 13 is a behavior change. Mitigated by applying it prospectively; all
  existing in-flight work is grandfathered via the migration.

Neutral:
- File moves (`git mv` from `Temp/` to `Management/`) appear in git history
  as renames, not deletions.
- Existing `specs/YYYY-MM-DD-{slug}/` feature dirs are unchanged; sprint
  folders link to them, not the reverse.

## Alternatives Considered

- **Extend the tracker only (no hierarchy).** Rejected: the tracker is
  already at its natural ceiling as a flat file with a sprint board. Adding
  PI-level narrative, per-sprint ground notes, and historical backfill would
  bloat it beyond glanceability -- the very property it is supposed to
  provide.
- **Extend the dashboard to cover navigation.** Rejected: the dashboard is
  ephemeral and external. It requires a running service and a browser. The
  navigation layer must be durable, version-controlled, and readable from a
  cold `git clone`.
- **Generate the entire navigation layer from the ledger.** Rejected for
  Phase 1: the ledger captures dispatches, outcomes, and status, but not
  design rationale, lessons, or on-the-ground notes. Those require human or
  agent prose. Phase 2 auto-generates the mechanical parts only; full
  automation is deferred to PI-4 after usage data validates the format.
- **Use a GitHub Wiki.** Rejected: Wikis are a separate repository, not
  diffable alongside code, not discoverable by agents reading the repo, and
  not portable across Git hosts.
- **Do nothing; rely on the ledger + dashboard.** Rejected: this is the
  status quo that the parallel team identified as the adoption blocker.
  "The tooling is strong but the repo is not glanceable."
