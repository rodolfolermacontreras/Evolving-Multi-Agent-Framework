"""Read-only repository evidence, inventory, and path-safety primitives.

This module is deliberately Python-stdlib-only.  It never mutates the repository
it inspects and never follows filesystem links while collecting observations.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable, Sequence
from urllib.parse import SplitResult, urlsplit, urlunsplit

_EVIDENCE_SCHEMA = "sdd-058-repository-evidence@1"
_INVENTORY_SCHEMA = "sdd-058-inventory@1"
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
_SENSITIVE_REMOTE = re.compile(
    r"(?:\$\{[^}]+\}|(?:token|secret|password|passwd|credential|api[_-]?key))",
    re.IGNORECASE,
)


class BrownfieldInventoryError(RuntimeError):
    """Base class for bounded, presentation-safe inventory failures."""


class PathSafetyError(BrownfieldInventoryError):
    """A path failed lexical, containment, or link-safety validation."""


class RepositoryValidationError(BrownfieldInventoryError):
    """The requested target is not the exact root of a committed repository."""


class RepositoryEvidenceError(BrownfieldInventoryError):
    """Repository evidence could not be collected without disclosure risk."""


@dataclass(frozen=True, slots=True)
class RepositoryEvidence:
    schema_version: str
    target_head: str
    project_name: str
    remotes: tuple[str, ...]
    default_branch: str
    stack: tuple[str, ...]
    quality_candidates: tuple[str, ...]
    conventions: tuple[str, ...]
    source_documents: tuple[str, ...]
    evidence_digest: str


@dataclass(frozen=True, slots=True)
class PathObservation:
    path: str
    kind: str
    ownership_hint: str
    sha256: str | None
    byte_length: int | None
    portable_mode: int | None
    link_kind: str | None
    receipt_hash: str | None


@dataclass(frozen=True, slots=True)
class InventorySnapshot:
    schema_version: str
    target_head: str
    evidence: RepositoryEvidence
    observations: tuple[PathObservation, ...]
    recovery_markers: tuple[str, ...]
    fingerprint_hits: tuple[str, ...]


def _display_purpose(purpose: str) -> str:
    value = " ".join(str(purpose).split())
    return value if value else "path"


def _path_error(purpose: str, reason: str) -> PathSafetyError:
    return PathSafetyError(f"Unsafe {_display_purpose(purpose)}: {reason}.")


def _is_reparse(info: os.stat_result) -> bool:
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _link_kind(path: Path, info: os.stat_result | None = None) -> str | None:
    info = info if info is not None else path.lstat()
    if stat.S_ISLNK(info.st_mode):
        return "symlink"
    if _is_reparse(info):
        # Python cannot portably distinguish every Windows reparse subtype.
        return "junction" if path.is_dir() else "reparse"
    return None


def _portable_relative(raw: str | os.PathLike[str], purpose: str) -> tuple[str, ...]:
    text = os.fspath(raw)
    if not isinstance(text, str):
        raise _path_error(purpose, "path must be text")
    if not text or text == ".":
        raise _path_error(purpose, "empty path")
    if any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise _path_error(purpose, "control character")

    windows = PureWindowsPath(text)
    posix = PurePosixPath(text.replace("\\", "/"))
    if windows.is_absolute() or posix.is_absolute() or text.startswith(("\\", "//")):
        raise _path_error(purpose, "absolute path")
    if windows.drive:
        raise _path_error(purpose, "drive-qualified path")

    parts = tuple(part for part in text.replace("\\", "/").split("/") if part not in ("", "."))
    if not parts:
        raise _path_error(purpose, "empty path")
    if any(part == ".." or ".." in part.split("\\") for part in parts):
        raise _path_error(purpose, "traversal outside root")

    for part in parts:
        if part.casefold() == ".git":
            raise _path_error(purpose, "path enters .git")
        if part.endswith(".") or part.endswith(" "):
            raise _path_error(purpose, "reserved trailing dot or space")
        stem = part.split(".", 1)[0].upper()
        if stem in _WINDOWS_RESERVED:
            raise _path_error(purpose, "reserved name")
    return parts


def safe_relative_path(
    raw: str | os.PathLike[str],
    root: Path,
    purpose: str,
    *,
    allow_missing: bool,
) -> Path:
    """Return a contained path after lexical, link, and special-file checks."""

    parts = _portable_relative(raw, purpose)
    root = Path(root)
    try:
        root_info = root.lstat()
    except OSError as error:
        raise _path_error(purpose, "root is unavailable") from error
    if _link_kind(root, root_info):
        raise _path_error(purpose, "root is a link, junction, or reparse point")
    if not stat.S_ISDIR(root_info.st_mode):
        raise _path_error(purpose, "root is not a directory")

    root_resolved = root.resolve(strict=True)
    candidate = root.joinpath(*parts)
    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if not allow_missing:
                raise _path_error(purpose, "path is missing")
            break
        except OSError as error:
            raise _path_error(purpose, "path cannot be inspected safely") from error
        if _link_kind(current, info):
            raise _path_error(purpose, "path traverses a link, junction, or reparse point")
        if index < len(parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise _path_error(purpose, "parent is not a directory")
        if index == len(parts) - 1 and not (
            stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
        ):
            raise _path_error(purpose, "special file")

    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as error:
        raise _path_error(purpose, "path resolves outside root") from error
    return candidate


def validate_path_set(paths: Iterable[str | os.PathLike[str]]) -> tuple[str, ...]:
    """Normalize a path set and reject case-fold collisions and tree overlap."""

    normalized = tuple("/".join(_portable_relative(path, "path set",)) for path in paths)
    ordered = tuple(sorted(normalized, key=lambda value: (value.casefold(), value)))
    folded: list[tuple[str, tuple[str, ...]]] = []
    for value in ordered:
        parts = tuple(part.casefold() for part in value.split("/"))
        for previous, previous_parts in folded:
            if parts == previous_parts:
                raise _path_error("path set", "case-fold duplicate")
            shorter = min(len(parts), len(previous_parts))
            if parts[:shorter] == previous_parts[:shorter]:
                raise _path_error("path set", "ancestor/descendant overlap")
        folded.append((value, parts))
    return ordered


def _run_git(target: Path, arguments: Sequence[str], *, required: bool = True) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(target), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
        )
    except (OSError, UnicodeError) as error:
        raise RepositoryEvidenceError("Git evidence could not be read safely.") from error
    if completed.returncode != 0:
        if required:
            raise RepositoryEvidenceError("Required Git evidence is unavailable.")
        return ""
    return completed.stdout.strip()


def validate_repository_root(target: Path) -> Path:
    """Validate and return the exact, non-linked root of a committed worktree."""

    supplied = Path(target)
    try:
        info = supplied.lstat()
    except OSError as error:
        raise RepositoryValidationError("Repository target is unavailable.") from error
    if _link_kind(supplied, info):
        raise PathSafetyError("Repository target must not be a link, junction, or reparse point.")
    if not stat.S_ISDIR(info.st_mode) or supplied.name.casefold() == ".git":
        raise RepositoryValidationError("Target must be the exact repository root.")

    resolved = supplied.resolve(strict=True)
    try:
        root_text = _run_git(resolved, ("rev-parse", "--show-toplevel"))
    except RepositoryEvidenceError as error:
        raise RepositoryValidationError("Target must be a Git repository root.") from error
    try:
        discovered = Path(root_text).resolve(strict=True)
    except OSError as error:
        raise RepositoryValidationError("Git reported an invalid repository root.") from error
    if discovered != resolved:
        raise RepositoryValidationError("Target must be the exact committed repository root.")
    try:
        _run_git(resolved, ("rev-parse", "--verify", "HEAD^{commit}"))
    except RepositoryEvidenceError as error:
        raise RepositoryValidationError("Repository must have a committed HEAD.") from error
    return resolved


def read_repository_head(target: Path) -> str:
    """Read current HEAD from the exact validated repository root."""

    root = validate_repository_root(target)
    return _run_git(root, ("rev-parse", "HEAD"))


def _sanitize_remote(raw: str) -> str:
    value = raw.strip()
    if not value:
        raise RepositoryEvidenceError("A Git remote is empty or invalid.")
    if _SENSITIVE_REMOTE.search(value):
        raise RepositoryEvidenceError("A Git remote contains unsupported sensitive material.")

    # Local fixture/file remotes are represented without machine-specific roots.
    if value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", value):
        return f"local://{Path(value).name}"

    if "://" in value:
        split = urlsplit(value)
        if not split.scheme or not split.hostname:
            raise RepositoryEvidenceError("A Git remote is malformed.")
        username = split.username if split.username == "git" and split.password is None else None
        host = split.hostname
        if split.port is not None:
            host = f"{host}:{split.port}"
        netloc = f"{username}@{host}" if username else host
        return urlunsplit(SplitResult(split.scheme, netloc, split.path, "", ""))

    # Conventional SCP-style SSH keeps only the non-secret `git` account.
    scp = re.fullmatch(r"(?:(?P<user>[^@/:]+)@)?(?P<host>[^/:]+):(?P<path>.+)", value)
    if scp:
        user = scp.group("user")
        if user not in (None, "git"):
            raise RepositoryEvidenceError("A Git remote contains unsupported credentials.")
        prefix = "git@" if user == "git" else ""
        return f"{prefix}{scp.group('host')}:{scp.group('path')}"
    raise RepositoryEvidenceError("A Git remote uses an unsupported form.")


def _project_metadata(target: Path) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    package = target / "package.json"
    pyproject = target / "pyproject.toml"
    if package.is_file() and not package.is_symlink():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            name = data.get("name") if isinstance(data, dict) else None
            scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise RepositoryEvidenceError("Project metadata could not be read safely.") from error
        quality = tuple(sorted(str(key) for key in scripts if key in {"test", "lint", "typecheck", "build"}))
        return (name if isinstance(name, str) and name else target.name, ("node",), quality)
    if pyproject.is_file() and not pyproject.is_symlink():
        try:
            text = pyproject.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise RepositoryEvidenceError("Project metadata could not be read safely.") from error
        match = re.search(r"(?ms)^\[project\]\s*.*?^name\s*=\s*[\"']([^\"']+)[\"']", text)
        return (match.group(1) if match else target.name, ("python",), ("pytest",))
    return (target.name, ("unknown",), ())


def collect_repository_evidence(target: Path) -> RepositoryEvidence:
    """Collect deterministic, secret-free repository evidence without writes."""

    root = validate_repository_root(target)
    head = _run_git(root, ("rev-parse", "HEAD"))
    branch = _run_git(root, ("symbolic-ref", "--quiet", "--short", "HEAD"), required=False)
    if not branch:
        branch = _run_git(root, ("rev-parse", "--abbrev-ref", "HEAD"))

    remote_lines = _run_git(root, ("remote", "get-url", "--all", "origin"), required=False).splitlines()
    # Sanitization happens before immutable evidence construction.
    remotes = tuple(sorted({_sanitize_remote(item) for item in remote_lines if item.strip()}))
    tracked = _run_git(root, ("ls-files", "-z"), required=False)
    source_documents = tuple(sorted(
        path.replace("\\", "/") for path in tracked.split("\0") if path
    ))
    project_name, stack, quality = _project_metadata(root)
    conventions = tuple(sorted(
        path for path in source_documents
        if path in {".editorconfig", ".gitignore", "CONTRIBUTING.md", "README.md"}
        or path.startswith(".github/workflows/")
    ))

    digest_input = {
        "schema_version": _EVIDENCE_SCHEMA,
        "target_head": head,
        "project_name": project_name,
        "remotes": remotes,
        "default_branch": branch,
        "stack": stack,
        "quality_candidates": quality,
        "conventions": conventions,
        "source_documents": source_documents,
    }
    digest = hashlib.sha256(
        json.dumps(digest_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return RepositoryEvidence(
        _EVIDENCE_SCHEMA, head, project_name, remotes, branch, stack, quality,
        conventions, source_documents, digest,
    )


def _observe(path: Path, relative: str) -> PathObservation:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return PathObservation(relative, "absent", "unknown", None, None, None, None, None)
    except OSError as error:
        raise RepositoryEvidenceError("A managed path could not be inspected safely.") from error

    mode = stat.S_IMODE(info.st_mode)
    link = _link_kind(path, info)
    if link:
        return PathObservation(relative, "link", "unknown", None, None, mode, link, None)
    if stat.S_ISREG(info.st_mode):
        try:
            data = path.read_bytes()
        except OSError as error:
            raise RepositoryEvidenceError("A managed file could not be read safely.") from error
        return PathObservation(
            relative, "file", "unknown", hashlib.sha256(data).hexdigest(), len(data), mode, None, None
        )
    if stat.S_ISDIR(info.st_mode):
        return PathObservation(relative, "directory", "unknown", None, None, mode, None, None)
    return PathObservation(relative, "special", "unknown", None, None, mode, None, None)


def _fingerprint_hits(root: Path, fingerprints: tuple[bytes, ...]) -> tuple[str, ...]:
    if not fingerprints:
        return ()
    hits: set[str] = set()
    for directory, names, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(directory)
        names[:] = sorted(name for name in names if name != ".git" and not _link_kind(base / name))
        for name in sorted(files):
            path = base / name
            try:
                info = path.lstat()
                if _link_kind(path, info) or not stat.S_ISREG(info.st_mode):
                    continue
                data = path.read_bytes()
            except OSError as error:
                raise RepositoryEvidenceError("Fingerprint evidence could not be read safely.") from error
            relative = path.relative_to(root).as_posix()
            for fingerprint in fingerprints:
                if fingerprint in data:
                    hits.add(relative)
    return tuple(sorted(hits))


def inventory_target(
    target: Path,
    managed_paths: Iterable[str | os.PathLike[str]],
    forbidden_fingerprints: Iterable[str],
) -> InventorySnapshot:
    """Build a deterministic non-following snapshot of relevant host facts."""

    root = validate_repository_root(target)
    evidence = collect_repository_evidence(root)
    normalized = validate_path_set(managed_paths)
    observations = tuple(
        _observe(safe_relative_path(path, root, "managed inventory path", allow_missing=True), path)
        for path in normalized
    )
    fingerprints: list[bytes] = []
    for value in forbidden_fingerprints:
        if not isinstance(value, str) or not value:
            raise RepositoryEvidenceError("Forbidden fingerprints must be non-empty text.")
        fingerprints.append(value.encode("utf-8"))
    hits = _fingerprint_hits(root, tuple(fingerprints))
    recovery_markers = tuple(
        path for path in normalized
        if any(part.startswith((".sdd-stage", ".sdd-backup", ".sdd-journal")) for part in path.split("/"))
        and (root / Path(*path.split("/"))).exists()
    )
    return InventorySnapshot(
        _INVENTORY_SCHEMA, evidence.target_head, evidence, observations,
        tuple(sorted(recovery_markers)), hits,
    )
