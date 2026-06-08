# Host Integration via `.github/` Symlink (SDD-016)

A guide for adopting the Evolving Multi-Agent Framework (SDD) into an
existing host repository without copying or forking the framework's `.github/`
directory.

Companion to the spec at
[`../specs/2026-06-06-symlink-portability/spec.md`](../specs/2026-06-06-symlink-portability/spec.md)
and the binding skill at
[`../../.github/skills/operational/host-integration-symlink/SKILL.md`](../../.github/skills/operational/host-integration-symlink/SKILL.md).

---

## Overview

`bootstrap.py host-link` installs the framework's `.github/` into a host
repository as a cross-platform link:

- **Linux / macOS**: a POSIX symbolic link (`os.symlink`).
- **Windows (developer mode)**: a POSIX-style symbolic link.
- **Windows (no privilege)**: a directory junction (`mklink /J`), created
  automatically when `os.symlink` raises `OSError`.

The host inherits every agent, skill, and prompt under the framework's
`.github/` instantly. Framework updates propagate live -- there is no copy
to refresh.

---

## Prerequisites

1. The framework repository is checked out somewhere on disk (e.g.
   `C:\projects\Evolving-Multi-Agent-Framework`).
2. The host repository is an existing git repo with at least one commit.
   The host's repository root is the directory containing its `.git/` folder.
3. Python 3.10+ is available on PATH (for running `bootstrap.py`).
4. The host operator has decided whether the framework's CI workflows
   appearing in their GitHub Actions tab is acceptable (see "CI / Actions
   Trade-Off" below).

---

## End-to-End Walkthrough

### Step 1. Dry-run

From the framework checkout:

```bash
cd /path/to/Evolving-Multi-Agent-Framework
python spec-driven-development/cli/bootstrap.py host-link \
    --target /path/to/host-repo
```

Output:

```
host-link dry-run (no filesystem changes will occur):
  target host repo : /path/to/host-repo
  link path        : /path/to/host-repo/.github
  framework source : /path/to/Evolving-Multi-Agent-Framework/.github
  existing .github: absent -- would create link directly
Re-run with --apply to perform the action.
```

If the dry-run output does not match your expectation, STOP. Do not
proceed.

### Step 2. Apply

If the dry-run report is correct, re-run with `--apply`:

```bash
python spec-driven-development/cli/bootstrap.py host-link \
    --target /path/to/host-repo --apply
```

Output:

```
host-link complete: symlink created at /path/to/host-repo/.github -> /path/to/Evolving-Multi-Agent-Framework/.github

Next steps for the host operator:
  - Inspect .github/ from the host root; framework agents/skills are now visible.
  - Review docs/HOST-INTEGRATION.md for the CI/Actions trade-off and rollback procedure.
```

On Windows without developer mode, the link kind reports as `junction`
instead of `symlink`. The behavior is otherwise identical.

### Step 3. Verify

```bash
cd /path/to/host-repo
ls -la .github            # POSIX
dir .github               # Windows
```

The output should show `.github` as a link to the framework's `.github/`
(POSIX) or as a `<JUNCTION>` entry (Windows).

VS Code Copilot Chat from the host root will now discover the framework's
agents and skills automatically (they appear under the host's `.github/`).

---

## Conflict Decision Tree

If `<target>/.github/` already exists, the tool aborts by default. You have
three opt-in resolutions:

```
target/.github exists?
  no  -> create link directly. done.
  yes -> --backup or --force?
           neither -> ABORT. tool prints remediation and exits 1.
           --backup -> mv .github -> .github.bak.<timestamp>, then create link.
           --force  -> rmtree(.github), then create link. DESTRUCTIVE.
```

`--backup` and `--force` are mutually exclusive at the CLI layer
(argparse enforces).

### Choosing the conflict mode

| Situation | Recommended mode |
|-----------|------------------|
| Host has an existing real `.github/` with workflows you want to preserve | `--backup` |
| Host has a placeholder `.github/` (e.g. only a `dependabot.yml`) you want gone | `--force` (with explicit owner approval) |
| Host has an existing symlinked `.github/` from a prior install | STOP and ask the dev-env-manager-general worker to evaluate |
| Host's `.github/` has uncommitted changes | STOP. Resolve the host's own changes first. |

`--backup` is the safer default for any real host.

---

## CI / Actions Trade-Off (Decision C6)

When the host's `.github/` becomes a link to the framework's `.github/`,
the framework's CI workflows under `.github/workflows/` are now visible to
the host's GitHub. They appear in the host's Actions tab and run on any
trigger matching their filters.

Currently the framework ships:

- `.github/workflows/deploy-dashboard.yml` -- triggered on push to `master`
  with path filters that reference framework-only paths
  (`spec-driven-development/exec/state.md`, `cli/state_builder.py`,
  itself, and `Dockerfile`). It will not fire on host code changes unless
  the host happens to use the same paths.

### Three mitigation options

The host operator picks ONE before going live:

1. **Accept** (recommended for early adoption). Read the workflows in the
   framework's `.github/workflows/` and verify the path filters do not
   match anything in your host. This is the simplest path and works for
   most hosts.
2. **Override at the repository level** in GitHub's Actions settings.
   Repository settings allow per-workflow disable. The framework's workflows
   stay on disk (visible as definitions) but never execute in the host's
   context.
3. **Split the link** (out of scope for v1). A future iteration may add
   `--no-workflows` or per-subdirectory linking. For now, this requires a
   manual setup: copy `.github/agents/`, `.github/skills/`, `.github/prompts/`
   individually instead of using `host-link`. Loses the live-update benefit
   for those subdirectories.

If you cannot pick option 1 or 2, do not run `host-link --apply` against
this host. Wait for the v2 iteration or open an issue.

---

## `.gitignore` Conflict Protection (SDD-027)

`host-link` runs a pre-flight check against the host's root `.gitignore`
to prevent two failure modes that would surface only AFTER the link is
live:

- **Framework runtime files leaking into the host's git history.** Files
  like `spec-driven-development/ledger/fleet.db`, `exec/state.md`, and
  `__pycache__/` are byproducts of framework execution; they must not be
  tracked by the host.
- **Framework agent / skill / prompt files being silently ignored.** The
  host's `.github/agents/`, `.github/skills/`, `.github/prompts/`,
  `.github/instructions/`, and `copilot-instructions.md` MUST be tracked
  or Copilot Chat will silently lose them.

The check is driven by a manifest at
`spec-driven-development/cli/host_gitignore_manifest.json` containing two
arrays:

- `must_be_ignored` -- paths that the host's `.gitignore` MUST cover
  (exact match or glob).
- `must_be_tracked` -- paths that the host's `.gitignore` MUST NOT
  block.

### `--gitignore-mode` flag

`host-link --gitignore-mode <mode>` controls how the check responds.
Default mode is `prompt`.

| Mode | Behavior on conflict |
|------|---------------------|
| `strict` | Abort immediately with a non-zero exit code. Use in CI / dev-env-manager automation. |
| `prompt` (default) | Print findings, ask the operator to acknowledge before proceeding. Use in interactive installs. |
| `warn` | Print findings, continue anyway. Use when you have already manually validated the host. |
| `skip` | Skip the check entirely. Equivalent to `--no-gitignore-check`. |

### `--no-gitignore-check` opt-out

For environments where the protection check is provably redundant (e.g. a
fresh host repo with no `.gitignore` yet, or a vendored offline install),
pass `--no-gitignore-check`. The flag disables the layer entirely; it
does NOT silently downgrade to `warn`.

### Remediation when the check fires

If `host-link` reports a `must_be_ignored` entry the host is failing to
ignore, edit the host's root `.gitignore` to add the missing pattern:

```gitignore
# Evolving Multi-Agent Framework runtime artifacts (SDD-027)
spec-driven-development/ledger/fleet.db
spec-driven-development/exec/state.html
spec-driven-development/exec/state.md
spec-driven-development/exec/work-index.md
spec-driven-development/sessions/SESSION-MEMORY.md
__pycache__/
*.pyc
.pytest_cache/
```

If the check reports a `must_be_tracked` entry the host's `.gitignore` is
covering, REMOVE the offending pattern (or carve a `!` exception):

```gitignore
# Host ignores everything under .github except the framework's stuff
.github/*
!.github/agents/
!.github/skills/
!.github/prompts/
!.github/instructions/
!.github/copilot-instructions.md
```

Re-run `host-link` (still in dry-run) and confirm the check passes
before adding `--apply`.

### Choosing the right mode

| Situation | Recommended mode |
|-----------|------------------|
| First-time interactive install | `prompt` (default) |
| Repeat install / dev-env-manager bootstrap | `strict` |
| Vendored offline install where no `.gitignore` exists | `--no-gitignore-check` |
| You have manually validated the host but cannot edit its `.gitignore` | `warn` |
| Smoke test only; will not commit to host yet | `skip` |

---

## Rollback

### To remove the link entirely

```bash
# POSIX
rm /path/to/host-repo/.github

# Windows (junction)
del /path/to/host-repo/.github
```

Neither command touches the framework's `.github/` -- they only remove the
link itself.

### To restore a `--backup` snapshot

```bash
mv /path/to/host-repo/.github.bak.<timestamp> /path/to/host-repo/.github
```

If the link is still in place, remove it first (see above), then move the
backup back.

### After a `--force` install

`--force` is destructive. There is no automatic rollback. Restore from your
git history if the deleted `.github/` was committed; otherwise, restore from
your filesystem backup.

---

## Troubleshooting

| Symptom | Diagnosis |
|---------|-----------|
| `ERROR: Target is not a git repository` | Run `git init` and commit at least once in the host before linking. |
| `ERROR: Host .github/ already exists` | Use `--backup` or `--force`. See decision tree above. |
| `ERROR: mklink /J fallback failed` (Windows) | The host process lacks the privilege to create junctions. Run from an elevated shell or enable Windows developer mode. |
| VS Code does not see the framework agents in the host | Restart VS Code. The Copilot extension caches agent discovery; the symlink is correct but the cache is stale. |
| Host `git status` shows `.github` as untracked | This is expected. The host operator decides whether to commit the link or add `.github/` to the host's `.gitignore`. |

---

## Future Enhancements (out of scope for v1)

- `host-link --pin <commit-sha>` to pin the framework at a tagged commit
  (creates a worktree and links to it).
- `host-link --no-workflows` to link only `.github/agents/`,
  `.github/skills/`, and `.github/prompts/` while leaving the host's
  workflows untouched.
- Auto-detection of the host context from within agent code (no current
  skill needs it).
- A `/env host-link` slash command as a friendlier wrapper.

---

## See also

- Skill: [`../../.github/skills/operational/host-integration-symlink/SKILL.md`](../../.github/skills/operational/host-integration-symlink/SKILL.md)
- Worker: [`../../.github/agents/dev-env-manager-general.agent.md`](../../.github/agents/dev-env-manager-general.agent.md)
- Spec: [`../specs/2026-06-06-symlink-portability/spec.md`](../specs/2026-06-06-symlink-portability/spec.md)
- Validation: [`../specs/2026-06-06-symlink-portability/validation.md`](../specs/2026-06-06-symlink-portability/validation.md)
- Clarification log: [`../specs/2026-06-06-symlink-portability/clarification-log.md`](../specs/2026-06-06-symlink-portability/clarification-log.md)
