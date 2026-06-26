---
name: host-integration-symlink
description: "Use when adopting the SDD framework into a brownfield host repo via .github/ symlink (or Windows junction). Owns the cross-platform install path, conflict detection, and rollback. Loaded by the dev-env-manager-general worker when dispatched on SDD-016 host-link tasks."
argument-hint: "Which host repo path is the target, and which conflict mode (abort/backup/force)?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Host Integration Symlink

Installs the framework's `.github/` directory into a host repo as a symbolic
link (or Windows junction) so the host inherits SDD's agents, skills, and
prompts without copying the tree. SDD wraps the host; it does not replace it.

## Why This Matters

A host project adopting SDD has three bad alternatives without this skill:

1. Copy `.github/` from the framework into the host (creates a fork that
   silently drifts on every framework update).
2. Migrate the host into a fresh greenfield bootstrap (destructive).
3. Maintain two separate Copilot agent surfaces (the host's and the
   framework's), and accept the confusion.

The symlink (Linux/macOS) or junction (Windows) makes the host's `.github/`
a live pointer into the framework. Framework updates propagate immediately.
No copy. No drift.

## Canonical Instruction

Use `cli/bootstrap.py host-link --target <host-repo>` to install the link.
Dry-run first. Apply only with explicit owner approval and an explicit
conflict mode if the host already has a `.github/`.

## Protocol

1. **Confirm `--target`**. The brief MUST name an absolute or unambiguously
   relative path to a host git repo. Do not infer.
2. **Dry-run first**. Run `python bootstrap.py host-link --target <path>`
   (no `--apply`). Read the report. Confirm the planned action matches the
   brief.
3. **Choose a conflict mode** if `<target>/.github/` already exists:
   - **abort** (default): no flag. Bail out and ask the dispatcher how to
     proceed.
   - **`--backup`**: timestamped move to `<target>/.github.bak.<timestamp>`.
     Preferred when host content is non-trivial or recoverable.
   - **`--force`**: recursive delete. Destructive; only use when the host's
     `.github/` is known-empty or known-stale and the dispatcher has
     explicitly approved.
4. **Escalate on any unrecognised host state**:
   - `.github/` is already a symlink (someone installed before).
   - `.github/workflows/` has uncommitted changes in the host.
   - The host has hooks under `.github/` that would conflict with the
     framework's hooks.
   - Any platform-specific oddity (e.g. WSL mount, network drive,
     case-insensitive FS).

## Conflict Decision Tree

```
target/.github exists?
  no  -> create link directly. done.
  yes -> --backup or --force?
           neither -> ABORT. print remediation.
           --backup -> move to .github.bak.<ts>, then create link.
           --force  -> rmtree(.github), then create link.
```

`--backup` and `--force` are mutually exclusive at the argparse layer.

## Platform Notes

- **Linux / macOS**: `os.symlink(target, link, target_is_directory=True)`.
  Native and visible to git as a symlink.
- **Windows (developer mode)**: same as POSIX; symlink is preferred.
- **Windows (no privilege)**: `os.symlink` raises `OSError`. Fall back to
  `subprocess.run(["cmd", "/c", "mklink", "/J", link_path, source])`.
  Junctions are absolute-path only -- the implementation resolves the
  framework path before the call.

## Compliance Example

Task: install the framework's `.github/` into the host at
`C:\projects\day-to-day` (no existing `.github/`).

Compliant flow:

1. Run `python bootstrap.py host-link --target C:\projects\day-to-day`.
2. Read the dry-run report.
3. Run again with `--apply`.
4. Confirm `C:\projects\day-to-day\.github` exists and resolves to the
   framework's `.github/`.
5. Report the commit SHA (or "no commit -- filesystem-only change") and the
   path of the link.

## Escape Hatch

If the dry-run reports anything you did not expect (existing `.github/`,
non-git-repo target, missing framework `.github/`), STOP. Do not pass
`--apply`. Route the issue back to the dispatching principal with the
exact dry-run output.

## Rollback Procedure

To remove a previously installed link without touching host content:

```
rm <host>/.github                # POSIX
del <host>\.github               # Windows (junction)
```

If `--backup` was used and the host wants their original `.github/` back:

```
mv <host>/.github.bak.<timestamp> <host>/.github
```

Document any rollback in the dispatch report.

## Captures-as-Lesson Hatch

If you discover a recurring host-state pattern (e.g. "many hosts have a
`.github/dependabot.yml` that conflicts"), file a `lesson-capture`
candidate. Do not modify the host's workflow.

## Completion Checklist

Before reporting done:

- The link exists and resolves to the framework's `.github/`.
- No host content under `.github/` was lost (either intact via abort, or
  preserved via timestamped backup).
- The dispatch report names the conflict mode used and any backup path.
- Cross-platform behavior was verified or documented as untested.
