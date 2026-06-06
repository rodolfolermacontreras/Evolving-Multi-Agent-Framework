---
id: SDD-PI-5-S1-clarification
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-06
feature: symlink-portability
sprint: PI-5 / Sprint 1
spec: spec.md
---

# Clarification Log -- SDD-016 + SDD-017 (Brownfield Portability Bundle)

This log answers C1..C9 raised by F-04 prompt section 3. Defaults are chosen by
the PM + Architect (consolidated worker session per owner directive
2026-06-06). Owner approval is captured implicitly by the same directive
("get sprint 5 done"); any disagreement surfaces in the post-sprint status
block delivered to the Executive Agent.

The locked answers become the binding constraints for `spec.md` and
`validation.md`. Re-opening a closed C-row requires an Article X amendment.

---

## C1 -- Install mode: automatic or explicit?

**Question**: Is the symlink installed by `bootstrap.py` automatically, or
only via an explicit flag?

**Answer**: **Explicit subcommand only.** Add a new `host-link` subcommand to
`bootstrap.py` (sibling to `greenfield` and `brownfield`):

```
python bootstrap.py host-link --target <host-repo-path> [--apply] [--backup] [--force]
```

**Rationale**:
- Mirrors the existing two-subcommand pattern (greenfield/brownfield); reduces
  cognitive load for the user.
- `host-link` is opt-in by construction -- there is no path by which an
  automatic invocation can affect a host.
- Dry-run is the default; `--apply` is required to mutate the filesystem
  (analogous to brownfield's `--apply` semantics).

**Cross-references**: AC-3, R3.

---

## C2 -- Windows handling: symlink or junction?

**Question**: Windows symlinks require admin or developer mode; junctions do
not. Which does `bootstrap.py` use, and how does it detect?

**Answer**: **Try symlink first (`os.symlink(target, link_path,
target_is_directory=True)`); on OSError (PermissionError or
WinError 1314), fall back to a Windows junction via
`subprocess.run(["cmd", "/c", "mklink", "/J", link_path, target])`.**

**Rationale**:
- Symlinks are first-class on Linux/macOS and on Windows when developer mode
  is enabled. Use them when available -- they support relative paths and are
  visible to git as a symlink.
- Junctions work on every Windows installation without elevation and are
  sufficient for our use case (the link target is a directory).
- The decision is made at runtime per platform/permissions, not via a flag.
- Junctions are absolute-path only; the implementation resolves the framework
  path to an absolute path before the `mklink /J` call.

**Cross-references**: AC-5, R5.

---

## C3 -- Conflict handling: host already has `.github/`?

**Question**: What does `bootstrap.py` do if the host already has a
`.github/`?

**Answer**: **Abort by default with a clear remediation message. Two
explicit opt-in flags unlock the action:**

| Flag | Behavior |
|------|----------|
| (none) | Abort. Print: "Host `.github/` already exists at <path>. Use `--backup` to move it aside, or `--force` to overwrite (destructive)." Exit 1. |
| `--backup` | Move host `.github/` to `.github.bak.YYYY-MM-DD-HHMMSS/` (timestamped to avoid collisions), then create the symlink/junction. |
| `--force` | Delete host `.github/` (destructive). Recursive remove. Then create the symlink/junction. Print a single-line warning before acting. |

`--backup` and `--force` are mutually exclusive. Both require `--apply` (they
do nothing in dry-run mode).

**Rationale**:
- Abort-by-default is the safest brownfield discipline (`respect-existing`
  skill).
- `--backup` preserves the host's prior content as a recoverable artifact.
- `--force` is included for the case where the host has placeholder
  `.github/` (e.g. a stale skeleton) the user explicitly wants gone.
- Timestamp suffix prevents `--backup` collisions across re-runs.

**Cross-references**: AC-4, R4.

---

## C4 -- Framework detection: am I inside a host?

**Question**: How does the framework detect it is running inside a host (as
opposed to standalone in its own repo)?

**Answer**: **Out of scope for SDD-016 v1.** The `host-link` subcommand
requires the user to pass `--target <host-repo-path>` explicitly. There is no
auto-detection in this iteration.

**Rationale**:
- Explicit `--target` removes ambiguity and matches the existing
  `bootstrap.py` pattern (greenfield/brownfield both require `--target`).
- Framework-side runtime detection ("am I running from a symlinked
  `.github/`?") is a future concern, only useful if some skill or agent needs
  to branch on it. No current skill does.
- Deferring this avoids the `framework_root()` ambiguity introduced by
  symlinks (the existing implementation walks parents to find the framework
  repo root; symlink targets resolve correctly because `Path.resolve()` follows
  links).

**Cross-references**: Out of scope acknowledged in spec section "Out of Scope".

---

## C5 -- Live vs. pinned: does the symlink propagate constitutional changes?

**Question**: Does the symlink propagate constitutional changes live (i.e.
when the framework repo is updated, the host sees it), or is there a
versioning pin?

**Answer**: **Live by construction (symlink semantics).** No version pin in
v1. The host always sees the framework's current `master`. If a host wants
pinning, they can check out the framework repo at a tagged commit before
running `host-link`; the symlink resolves to that worktree's current state.

**Rationale**:
- Symlinks are live by definition. Adding a pin would require copy mode,
  which defeats the purpose of SDD-016.
- The host-side `git status` will not show framework drift because the
  symlink target is outside the host's worktree (git does not traverse into
  symlinked external directories by default).
- Future enhancement (out of scope): a `host-link --pin <commit-sha>` mode
  that creates a worktree at the pinned commit and links to it.

**Cross-references**: Out of scope in spec.

---

## C6 -- Host CI: does `.github/workflows/` become a live target?

**Question**: Does the host's existing CI (GitHub Actions) get affected when
`.github/workflows/` becomes a symlink target?

**Answer**: **Yes -- and this is documented in `docs/HOST-INTEGRATION.md`
with three mitigation options for the host operator.**

When the host's `.github/` becomes a symlink to the framework's `.github/`,
the framework's workflows appear in the host's Actions tab and run on any
trigger that fires in the host repo. The framework workflows currently in
play:

- `deploy-dashboard.yml` -- triggered on push to master with path filters that
  reference `spec-driven-development/exec/state.md`. The host will not trigger
  this filter unless the host happens to have a path matching the filter.

**Mitigation options documented in HOST-INTEGRATION.md** (host operator
chooses one):

1. **Accept** -- the workflow's path filters are narrow enough that they will
   not fire on host changes. Verify by reading the workflow file before
   linking.
2. **Override at host level** -- the host can place its own `.github/workflows/`
   files under a non-symlinked path (e.g. by linking only
   `.github/agents/` and `.github/skills/`, not all of `.github/`). Out of
   scope for v1 -- v1 links all of `.github/` atomically.
3. **Disable in the host's GitHub settings** -- repository Actions settings
   allow per-workflow disable. Host operator's choice.

**v1 behavior**: link all of `.github/`. Document the trade-off. Do not split
the link (future enhancement only).

**Cross-references**: AC-8 (docs), R6 (warning emitted at install time).

---

## C7 -- `dev-env-manager-general`: worker or principal?

**Question**: Is `dev-env-manager` a worker dispatched per-task, or a
Principal that the EM can route to directly?

**Answer**: **Generic worker.** Hire under
`.github/agents/dev-env-manager-general.agent.md`. Add row to
`roster/agents.json` with `kind: generic`, `role: dev-env-manager`,
`specialization: null`. Earns promotion to specialist only after demonstrated
competence across multiple dispatches (per Article V).

**Rationale**:
- The scope (worktree creation/cleanup, symlink install, branch hygiene
  checks, env-var validation) is concrete and bounded -- it is task work,
  not strategy.
- The four existing Principals (EM, PM, Architect, SW Dev) cover the
  strategic dimensions. Adding a fifth Principal for env concerns would
  violate Article IV (specialization over generalism) -- env work is a
  worker concern.
- A Principal needs a permanent reasoning role across many sprints; a
  dev-env-manager worker is invoked per dispatch and otherwise idle.

**Cross-references**: AC-6, agent file + roster row.

---

## C8 -- Agent file scope?

**Question**: What is the agent file scope?

**Answer**: **Three additive files** plus two roster updates:

| Artifact | Path | Notes |
|----------|------|-------|
| Agent file | `.github/agents/dev-env-manager-general.agent.md` | Use `developer-general.agent.md` as the structural template. Add a section describing the dev-env-manager scope. |
| Skill pack | `.github/skills/operational/host-integration-symlink/SKILL.md` | New skill. The worker loads it when dispatched on host-link work. |
| Roster row | `spec-driven-development/roster/agents.json` | Add: `id: dev-env-manager-general`, `kind: generic`, `role: dev-env-manager`, `specialization: null`, `created_at: 2026-06-06`, `provenance: "Hired via consolidated Sprint 5 worker session per owner directive 2026-06-06 to own SDD-016 + SDD-017 (brownfield portability)."` |
| Skill registry row | `spec-driven-development/roster/skills.json` | Add: `id: host-integration-symlink`, `category: operational`, `description: "Installs the framework's .github/ into a host repo via cross-platform symlink/junction; handles conflict detection and rollback per SDD-016."` |

**Cross-references**: AC-6, AC-7.

---

## C9 -- Dispatch mechanism?

**Question**: How does this worker discover work?

**Answer**: **Dispatch via `cli/fleet.py dispatch` with `worker_role:
dev-env-manager` (existing fleet pattern). No new slash command in v1.**

**Rationale**:
- Reuses the existing dispatch mechanism; no new entry points to maintain.
- The user-facing entry is `bootstrap.py host-link` (the CLI subcommand).
  When invoked interactively, the user runs it directly. When invoked via
  the fleet, the SW Dev dispatches the dev-env-manager worker to run it.
- A `/env <action>` slash command is a reasonable future enhancement but is
  not required for v1 and would create a redundant entry point alongside
  `bootstrap.py host-link`.

**Cross-references**: AC-6, agent file scope.

---

## Summary

All nine clarification rows are CLOSED. The spec.md in this directory codifies
these answers; the validation.md REQUIRED set (R1..R7) provides the
verification harness.

Re-opening any C-row requires an Article X amendment with a Friction Analysis
per `templates/level-2-decision.md`.
