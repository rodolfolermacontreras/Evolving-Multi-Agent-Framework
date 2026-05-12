"""Git worktree management scaffold.

Purpose:
    Wrap repository worktree operations using the Day-to-Day convention of
    ``../wt-{shortname}`` and feature branch naming under ``feature/``.
"""

from __future__ import annotations

from pathlib import Path


def build_worktree_path(repo_root: Path, short_name: str) -> Path:
    """Return the conventional worktree path for a short feature name."""
    return repo_root.parent / f"wt-{short_name}"


def build_branch_name(short_name: str) -> str:
    """Return the conventional feature branch name."""
    return f"feature/{short_name}"


def create_worktree(repo_root: Path, short_name: str) -> None:
    """Create a worktree for the given feature.

    TODO:
        Implement the git worktree wrapper and safety checks for existing paths,
        branch reuse, and integration branch ancestry.
    """

    target = build_worktree_path(repo_root, short_name)
    branch = build_branch_name(short_name)
    print(f"TODO: create worktree at {target} for branch {branch}")
