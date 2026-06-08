---
description: Mirror locked SDD tasks into GitHub Issues or ADO-compatible payloads.
---

# /taskstoissues

Use this prompt after `/tasks` has locked a feature's `tasks.md` and before or during implementation tracking. The repo artifacts remain authoritative; external issues are a mirror only.

## Required Operating Rules

1. Run dry-run first:

   ```powershell
   python spec-driven-development/cli/taskstoissues.py push --spec-dir <spec-dir> --provider github --repo <owner/name>
   ```

2. Do not write externally unless the owner explicitly approves apply mode and provides a safe target repository:

   ```powershell
   python spec-driven-development/cli/taskstoissues.py push --spec-dir <spec-dir> --provider github --repo <owner/name> --apply
   ```

3. GitHub apply mode reads `GITHUB_TOKEN` first, then `GH_TOKEN`. Future ADO apply mode reserves `ADO_PAT`, `ADO_ORG_URL`, and `ADO_PROJECT`.
4. `tasks.md` wins all conflicts. Remote/local status drift writes `issue-conflicts.md`, exits non-zero, and does not mutate local lifecycle artifacts.
5. There are no implicit writes in v1: no commit hook, no dashboard-triggered sync, no webhook listener, and no background daemon.
6. Generated sync state stays beside the target feature's `tasks.md` as `issue-map.json` and `issue-conflicts.md`.

## Close-Out

Before reporting DONE, run:

```powershell
python spec-driven-development/cli/schema_lint.py
python -m pytest spec-driven-development/ --tb=no -q
```---
mode: agent
description: Mirror locked SDD tasks into GitHub Issues or ADO-compatible dry-run payloads.
---

# /taskstoissues

Use this prompt only after a feature's `tasks.md` and `validation.md` are locked.
The repository artifacts remain authoritative; issue trackers mirror task state.

## Operating Protocol

1. Run dry-run first:
   `python spec-driven-development/cli/taskstoissues.py push --spec-dir <spec-dir> --provider github --repo <owner/name>`
2. Review the generated payloads for title, body, labels, source links, and status.
3. Apply only after explicit owner/operator confirmation:
   `python spec-driven-development/cli/taskstoissues.py push --spec-dir <spec-dir> --provider github --repo <owner/name> --apply`
4. For GitHub apply mode, use `GITHUB_TOKEN` or `GH_TOKEN` from the environment. Never paste tokens into prompts, files, command output, or issue-map files.
5. Future ADO mode reserves `ADO_PAT`, `ADO_ORG_URL`, and `ADO_PROJECT`; Sprint 8 ADO behavior is dry-run/provider-contract only.
6. If conflicts are reported, stop and route to the owner. `tasks.md` wins and is not mutated by the bridge.

## Boundaries

- No commit hook triggers.
- No dashboard-triggered writes.
- No webhook listener.
- No background daemon.
- No host-project application files are written.
- No assignee, milestone, sprint-capacity, or dependency graph sync in v1.