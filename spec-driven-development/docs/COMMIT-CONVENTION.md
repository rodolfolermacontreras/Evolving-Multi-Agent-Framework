---
id: SDD-FDC-001-commit-convention
type: spec
status: active
owner: principal-architect
updated: 2026-06-06
feature: filesystem-data-contracts
sprint: PI-4 / Sprint 4
---

# Commit Message Convention

This repo uses a lightweight `type(scope): short` convention so commit history
is searchable, role-routable, and machine-parseable. It is **documentation +
opt-in** only -- there is no CI gate, and the hook is never auto-installed
(per ADR-012 / FDC D3).

## Format

```
<type>(<scope>): <short imperative description>

<optional body paragraph(s)>

<optional footers, including:>
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

- The first line MUST be <= 72 characters where reasonable.
- The subject is imperative ("add", "fix", "refactor"), not past tense.
- A blank line separates subject from body.
- A blank line separates body from footers.
- No emojis anywhere.

## Validated regex (used by the opt-in hook)

```
^(feat|fix|refactor|test|docs|chore|spec|plan|tasks|triage|close|ideas|retro)(\([\w-]+\))?: .+
```

If the first line matches, the hook exits 0. Otherwise it prints a pointer to
this document and exits non-zero.

## Allowed `type` values

| Type | Meaning |
|------|---------|
| `feat` | A user- or framework-visible feature shipped. |
| `fix` | A bug fix. |
| `refactor` | Internal restructuring, no behavior change. |
| `test` | Tests-only change (add coverage, fix flake, etc.). |
| `docs` | Documentation only (READMEs, ADRs, prompts, this file). |
| `chore` | Mechanical maintenance (regenerate `exec/state.md`, bump unused metadata, sweep). |
| `spec` | New or amended `specs/**/spec.md`. |
| `plan` | New or amended `specs/**/plan.md`. |
| `tasks` | New or amended `specs/**/tasks.md`. |
| `triage` | Backlog grooming / `backlog/BACKLOG.md` edits. |
| `close` | A sprint or PI close commit. |
| `ideas` | New entries in `backlog/IDEAS.md`. |
| `retro` | A retrospective doc landing. |

## Scope hint

`<scope>` is optional but recommended. It is a kebab-case identifier for the
feature or subsystem the commit touches. Examples in current history:

- `fdc` -- filesystem data contracts (SDD-FDC-001)
- `sprint-4` -- Sprint 4 mechanics
- `fleet-ledger` -- the fleet ledger module
- `state-builder` -- the executive state builder

A single commit that spans multiple unrelated scopes is a smell -- split it.

## Examples

### Valid

```
feat(fdc): T-FDC-04 add build_doc_count rollup helper

Walks specs/** + sprints/** markdown, reuses parse_frontmatter from
schema_lint, seeds zero-counts for every known enum key. Pure function;
state_builder.py S1 functions untouched. Tests added: 154 -> 158.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

```
test(fdc): T-FDC-02 add S1 footprint lock guard against 257b081
```

```
fix(state-builder): use try/finally for sqlite connection in load_decisions
```

```
docs(fdc): document frontmatter contract enums
```

```
chore: regenerate exec/ state -- Sprint 4 close
```

```
spec(fdc): amend R5/AC-5 anchor b7ce642 -> 257b081 (Article X)
```

### Invalid (will be rejected by the opt-in hook)

```
Updated the rollup helper                          # missing type
update: something                                  # 'update' is not in the allowed list
feat add the rollup helper                         # missing colon
feat(fdc):add the rollup helper                    # missing space after colon
feat(): blank scope                                # empty scope
fix Refactored everything                          # missing colon, capitalized
```

## Installing the opt-in hook

Two install paths. Pick one.

### Path A -- `git config core.hooksPath` (recommended)

```powershell
# From the repo root.
git config core.hooksPath spec-driven-development/cli/hooks
```

This points all hooks under `spec-driven-development/cli/hooks/` at the active
hookset for this clone. Other clones are unaffected. To unset:

```powershell
git config --unset core.hooksPath
```

### Path B -- copy the hook

```powershell
# From the repo root.
Copy-Item spec-driven-development/cli/hooks/commit-msg .git/hooks/commit-msg
# On POSIX systems also: chmod +x .git/hooks/commit-msg
```

The hook is overwritten on each `git clone`; you must re-copy after cloning
afresh.

## Uninstalling

- Path A: `git config --unset core.hooksPath`.
- Path B: delete `.git/hooks/commit-msg`.

Either way, uninstalled state is the same as before installation -- the hook
never modifies anything outside its execution.

## What the hook does NOT do

- It does not block CI (there is no CI gate -- D3).
- It does not run linters, tests, or `state_builder.py` regeneration.
- It does not edit your message; it only accepts or rejects the first line.
- It does not import any third-party packages (stdlib only).

## Why this convention exists

- Routes commits to the right principal in retro queries
  (`git log --grep "^spec("`, `git log --grep "^feat(fdc)"`).
- Enables a simple `state_builder.py count` augmentation in a future PI to
  bucket commits by `type`.
- Makes the Article VII "one feature, one session" rule auditable -- a
  feature commit chain shares a scope.

## References

- ADR-012 (`docs/ADR/012-filesystem-frontmatter-data-contract.md`) -- D3
  records that the commit-message convention is doc + opt-in, never auto-install
  and never CI-gated.
- `spec-driven-development/cli/hooks/commit-msg` -- the opt-in hook script.
- `specs/2026-06-04-filesystem-data-contracts/spec.md` -- AC-6.
