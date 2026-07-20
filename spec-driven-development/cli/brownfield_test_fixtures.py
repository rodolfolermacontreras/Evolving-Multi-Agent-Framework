"""Disposable git fixtures for SDD-058 brownfield tests.

This test-only module is intentionally Python-stdlib-only. Every write is
confined to a caller-owned temporary root.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

SENTINEL_NAME = ".sdd-disposable-fixture.json"
_SENTINEL_SCHEMA = "sdd-058-disposable-root@1"
_GIT_ENV = {
    "GIT_AUTHOR_NAME": "SDD Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "SDD Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_CONFIG_NOSYSTEM": "1",
}


@dataclass(frozen=True)
class GitHostFixture:
    """A committed host repository backed by an offline bare remote."""

    kind: str
    root: Path
    remote: Path
    branch: str
    head: str


@dataclass(frozen=True)
class DisposableFixtureRoot:
    """Sentinel-bound parent for all mutation-capable fixture paths."""

    root: Path
    sentinel: Path


@dataclass(frozen=True)
class PathState:
    """Portable byte and metadata state used by no-real-host assertions."""

    kind: str
    sha256: str | None
    size: int | None
    portable_mode: int | None
    link_target: str | None


class InjectedFixtureFailure(RuntimeError):
    """Deterministic failure raised at an explicitly selected test boundary."""


class FailureInjector:
    """Callable failure switch for later transaction and rename tests."""

    def __init__(self, fail_at: str | None = None) -> None:
        self.fail_at = fail_at
        self.seen: list[str] = []

    def __call__(self, boundary: str) -> None:
        self.seen.append(boundary)
        if boundary == self.fail_at:
            raise InjectedFixtureFailure(boundary)


def _canonical(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def _sentinel_payload(root: Path) -> dict[str, str]:
    canonical = _canonical(root)
    binding = hashlib.sha256(
        f"{_SENTINEL_SCHEMA}\0{canonical}".encode("utf-8")
    ).hexdigest()
    return {"schema": _SENTINEL_SCHEMA, "root": canonical, "binding": binding}


def create_disposable_root(tmp_path: Path, name: str = "sdd-058-fixtures") -> DisposableFixtureRoot:
    """Create a uniquely bound disposable root directly below ``tmp_path``."""

    tmp_path = tmp_path.resolve()
    root = tmp_path / name
    root.mkdir()
    sentinel = root / SENTINEL_NAME
    sentinel.write_text(
        json.dumps(_sentinel_payload(root), sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return DisposableFixtureRoot(root=root, sentinel=sentinel)


def sentinel_identifies(root: Path) -> bool:
    """Return true only when a regular sentinel is bound to this exact root."""

    try:
        sentinel = root / SENTINEL_NAME
        if root.is_symlink() or sentinel.is_symlink() or not sentinel.is_file():
            return False
        payload = json.loads(sentinel.read_text(encoding="utf-8"))
        return payload == _sentinel_payload(root)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False


def _git(*args: str, cwd: Path | None = None) -> str:
    env = os.environ.copy()
    env.update(_GIT_ENV)
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _write(root: Path, relative: str, data: str, *, newline: str = "\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8", newline=newline)


def _initialize_git_host(parent: Path, name: str, branch: str) -> tuple[Path, Path]:
    root = parent / name
    remote = parent / f"{name}.git"
    root.mkdir()
    _git("init", "--quiet", f"--initial-branch={branch}", str(root))
    _git("init", "--quiet", "--bare", f"--initial-branch={branch}", str(remote))
    _git("remote", "add", "origin", str(remote), cwd=root)
    return root, remote


def _commit_and_push(root: Path, branch: str) -> str:
    _git("add", "--all", cwd=root)
    _git("commit", "--quiet", "-m", "fixture baseline", cwd=root)
    _git("push", "--quiet", "--set-upstream", "origin", branch, cwd=root)
    return _git("rev-parse", "HEAD", cwd=root)


def build_node_express_fixture(disposable: DisposableFixtureRoot) -> GitHostFixture:
    """Build a realistic committed Node/Express host on explicit ``main``."""

    if not sentinel_identifies(disposable.root):
        raise ValueError("disposable root sentinel is missing or does not match")
    root, remote = _initialize_git_host(disposable.root, "node-express-host", "main")
    _write(root, "package.json", json.dumps({
        "name": "fixture-express-service",
        "private": True,
        "scripts": {"test": "node --test", "lint": "node --check src/app.js"},
        "dependencies": {"express": "4.21.2"},
    }, sort_keys=True, indent=2) + "\n")
    _write(root, "package-lock.json", json.dumps({
        "name": "fixture-express-service", "lockfileVersion": 3,
        "requires": True, "packages": {},
    }, sort_keys=True, indent=2) + "\n")
    _write(root, "src/app.js", "const express = require('express');\nmodule.exports = express();\n")
    _write(root, "test/app.test.js", "const test = require('node:test');\ntest('fixture', () => {});\n")
    _write(root, "jsconfig.json", '{"compilerOptions":{"checkJs":true}}\n')
    _write(root, "README.md", "# Fixture Express Service\n")
    _write(root, ".gitignore", "node_modules/\n.env\n")
    _write(root, ".github/dependabot.yml", "version: 2\nupdates: []\n")
    _write(root, "host-owned/windows-notes.txt", "first\nsecond\n", newline="\r\n")
    _write(root, ".sdd-proposal/constitution/mission.md", "# Mission\r\n\r\nHuman reviewed bytes.\r\n", newline="")
    _write(root, ".sdd-proposal/host-identity.json", '{"schema_version":1,"project_name":"fixture-express-service"}\n')
    head = _commit_and_push(root, "main")
    return GitHostFixture("node-express", root, remote, "main", head)


def build_python_fixture(disposable: DisposableFixtureRoot) -> GitHostFixture:
    """Build a materially different committed Python host on explicit ``trunk``."""

    if not sentinel_identifies(disposable.root):
        raise ValueError("disposable root sentinel is missing or does not match")
    root, remote = _initialize_git_host(disposable.root, "python-library-host", "trunk")
    _write(root, "pyproject.toml", "[project]\nname = \"fixture-python-library\"\nversion = \"0.1.0\"\nrequires-python = \">=3.12\"\n")
    _write(root, "src/fixture_library/__init__.py", '"""Fixture library."""\n\ndef identity(value):\n    return value\n')
    _write(root, "tests/test_identity.py", "from fixture_library import identity\n\ndef test_identity():\n    assert identity(1) == 1\n")
    _write(root, ".github/workflows/ci.yml", "name: fixture-ci\non: [push]\njobs: {}\n")
    _write(root, "README.md", "# Fixture Python Library\n")
    _write(root, ".gitignore", "__pycache__/\n.venv/\n")
    _write(root, "host-owned/posix-notes.txt", "alpha\nbeta\n")
    executable = root / "tools" / "quality-check"
    _write(root, "tools/quality-check", "#!/usr/bin/env python3\nprint('fixture')\n")
    if os.name != "nt":
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    head = _commit_and_push(root, "trunk")
    return GitHostFixture("python-library", root, remote, "trunk", head)


def make_link(link: Path, target: Path) -> bool:
    """Create a directory link when supported; return false without skipping tests."""

    try:
        link.symlink_to(target, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        return False


def snapshot_paths(paths: Iterable[Path]) -> dict[str, PathState]:
    """Capture byte, link, and portable-mode state without following links."""

    result: dict[str, PathState] = {}
    for path in sorted((Path(item) for item in paths), key=lambda item: item.as_posix()):
        key = str(path.resolve(strict=False)).replace("\\", "/")
        try:
            info = path.lstat()
        except FileNotFoundError:
            result[key] = PathState("absent", None, None, None, None)
            continue
        mode = stat.S_IMODE(info.st_mode)
        if path.is_symlink():
            result[key] = PathState("link", None, None, mode, os.readlink(path))
        elif path.is_file():
            data = path.read_bytes()
            result[key] = PathState("file", hashlib.sha256(data).hexdigest(), len(data), mode, None)
        elif path.is_dir():
            digest = hashlib.sha256()
            count = 0
            for child in sorted(path.rglob("*"), key=lambda item: item.as_posix()):
                relative = child.relative_to(path).as_posix()
                child_info = child.lstat()
                digest.update(relative.encode("utf-8") + b"\0")
                if child.is_symlink():
                    digest.update(b"L" + os.readlink(child).encode("utf-8"))
                elif child.is_file():
                    digest.update(b"F" + child.read_bytes())
                else:
                    digest.update(b"D")
                digest.update(str(stat.S_IMODE(child_info.st_mode)).encode("ascii") + b"\0")
                count += 1
            result[key] = PathState("directory", digest.hexdigest(), count, mode, None)
        else:
            result[key] = PathState("special", None, None, mode, None)
    return result


def snapshot_git_status(repository: Path) -> str:
    """Return a stable porcelain snapshot without writing repository state."""

    return _git("status", "--porcelain=v1", "--untracked-files=all", cwd=repository)


def copy_sentinel(source_root: Path, destination_root: Path) -> Path:
    """Copy only a sentinel to construct a negative authorization fixture."""

    destination_root.mkdir()
    destination = destination_root / SENTINEL_NAME
    shutil.copyfile(source_root / SENTINEL_NAME, destination)
    return destination


def replace_with_injection(source: Path, destination: Path, injector: Callable[[str], None]) -> None:
    """Small deterministic rename primitive used by later failure tests."""

    injector("before-replace")
    os.replace(source, destination)
    injector("after-replace")
