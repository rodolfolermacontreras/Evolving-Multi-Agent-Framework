---
name: git-workflow
description: "Use when creating branches, setting up worktrees, merging features, or any git operation. Enforces master read-only, integration/improvements dev track, and ../wt-{name} worktree conventions."
license: MIT
metadata:
  author: rodolfolermacontreras
  version: '1.0'
---

# Git Workflow

Enforces git conventions for the Day-to-Day Agent parallel development framework: master is read-only production, integration/improvements is the dev track, feature branches live in ../wt-{name} worktrees.

## When to Use

Load this skill when:
- Creating a new feature branch
- Setting up a worktree for parallel work
- Merging completed features
- Cleaning up finished or abandoned work
- Confused about which branch to commit to

Do NOT load when:
- Reading code (no git operations needed)
- Running tests in existing workspace

## Process

### Branch Decision Tree

1. **On master?** STOP. Read-only. No commits, merges, or rebases allowed.
2. **On integration/improvements?** Create a feature branch + worktree before proceeding.
3. **On a feature branch in a worktree?** Proceed with development.

### Creating a Feature Branch

```powershell
# 1. Ensure you're on integration/improvements
git checkout integration/improvements
git pull

# 2. Create feature branch
git branch feature/f{N}.{M}-short-name

# 3. Create worktree at ../wt-{shortname}
git worktree add ..\wt-short-name feature/f{N}.{M}-short-name

# 4. Work in the worktree
cd ..\wt-short-name
```

### Merging a Completed Feature

```powershell
# 1. Ensure all tests pass in worktree
cd ..\wt-short-name
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=. -v --tb=short

# 2. Return to main repo
cd ..\Day_to_Day

# 3. Merge into integration/improvements (NOT master)
git checkout integration/improvements
git merge --no-ff feature/f{N}.{M}-short-name

# 4. Clean up worktree and branch
git worktree remove ..\wt-short-name
git branch -d feature/f{N}.{M}-short-name
```

### Cleaning Up Failed Experiments

```powershell
# 1. Remove worktree
git worktree remove ..\wt-short-name --force

# 2. Delete branch (use -D to force)
git branch -D feature/f{N}.{M}-short-name

# 3. Do NOT merge into integration/improvements
```

## Examples

### Example 1: Starting Work on Calendar Sync Feature

```powershell
git checkout integration/improvements
git pull
git branch feature/f2.1-calendar-sync
git worktree add ..\wt-calendar-sync feature/f2.1-calendar-sync
cd ..\wt-calendar-sync

# Now ready to implement. Tests run from Day_to_Day/.venv:
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=.
```

### Example 2: Merging Completed Feature

```powershell
# In worktree, final verification
cd ..\wt-calendar-sync
..\Day_to_Day\.venv\Scripts\python.exe -m pytest tests\ --rootdir=. -v --tb=short
# All pass

# Return to main repo
cd ..\Day_to_Day
git checkout integration/improvements
git merge --no-ff feature/f2.1-calendar-sync
git push

# Clean up
git worktree remove ..\wt-calendar-sync
git branch -d feature/f2.1-calendar-sync
```

## Common Mistakes

- Committing directly to master - NEVER. Master is read-only production.
- Committing directly to integration/improvements - All work goes through feature branches.
- Creating worktrees without feature branches - Each worktree needs its own branch.
- Forgetting to run tests before merge - Baseline 743 tests must all pass.
- Merging feature branches into master - Features merge to integration/improvements only.
- Not cleaning up worktrees after merge - Leaves orphan directories.
- Creating worktrees in subdirectories of Day_to_Day - They must be siblings at ../wt-{name}.

## Reference

Full details: `docs/GIT_PARALLEL_FRAMEWORK.md`
