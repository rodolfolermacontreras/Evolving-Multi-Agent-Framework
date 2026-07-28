"""Immutable proposal baseline validation and three-way refresh planning.

This module deliberately contains no normal apply operation.  It reads proposal
state and produces immutable plans; mutation belongs to the transaction layer.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping

import brownfield_inventory

BASELINE_SCHEMA_VERSION = "1"
BASELINE_BUNDLE_VERSION = "brownfield-core@1"
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class BaselineValidationError(ValueError):
    """Raised when stored baseline evidence cannot be trusted."""


class LegacyBaselineRequiredError(BaselineValidationError):
    """Raised when a reviewed legacy proposal has no baseline manifest."""


class ProposalConflictError(ValueError):
    """Raised when a conflict lacks an exact supported resolution."""


class RefreshOutcome(str, Enum):
    """The exhaustive byte-exact outcomes of a three-way comparison."""

    UNCHANGED = "unchanged"
    UPSTREAM_ONLY = "upstream-only"
    USER_ONLY = "user-only"
    CONVERGENT = "convergent"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class BaselineFile:
    path: str
    sha256: str
    byte_length: int
    baseline_path: str
    renderer_id: str
    renderer_version: str
    evidence_dependencies: tuple[str, ...]
    text_policy: str


@dataclass(frozen=True)
class BaselineManifest:
    schema_version: str
    source_revision: str
    evidence_digest: str
    bundle_version: str
    generated_at: str
    files: tuple[BaselineFile, ...]


@dataclass(frozen=True)
class ProposalCandidate:
    """A deterministic, uncommitted proposal-generation result."""

    evidence: object
    identity_draft: object
    framework_root: Path
    generated_at: str


@dataclass(frozen=True)
class ProposalRefreshItem:
    path: str
    outcome: RefreshOutcome
    baseline_bytes: bytes
    reviewed_bytes: bytes
    candidate_bytes: bytes
    result_bytes: bytes | None
    reviewed_destination: str
    candidate_destination: str
    baseline_destination: str
    resolution: str | None = None


@dataclass(frozen=True)
class ProposalRefreshPlan:
    items: tuple[ProposalRefreshItem, ...]
    conflicts: tuple[str, ...]
    requires_resolution: bool
    legacy_baseline_adoption: bool = False
    requires_exact_approval: bool = True


def generate_proposal(
    evidence: object,
    identity_draft: object,
    framework_root: Path,
    date: object,
) -> ProposalCandidate:
    """Describe explicit proposal generation without writing proposal state."""

    root = Path(framework_root)
    generated_at = date.isoformat() if hasattr(date, "isoformat") else str(date)
    return ProposalCandidate(evidence, identity_draft, root, generated_at)


def _validation_error(detail: str) -> BaselineValidationError:
    return BaselineValidationError(
        f"Invalid proposal baseline: {detail}; regenerate or explicitly adopt the baseline."
    )


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise _validation_error(f"missing or invalid {field}")
    return value


def _safe_relative_path(value: Any, field: str) -> str:
    path = _required_string(value, field)
    posix = PurePosixPath(path)
    windows = PureWindowsPath(path)
    if (
        "\\" in path
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in ("", ".", "..") for part in posix.parts)
    ):
        raise _validation_error(f"unsafe {field} path")
    return path


def _read_snapshot(proposal_root: Path, relative: str) -> bytes:
    try:
        snapshot = brownfield_inventory.safe_relative_path(
            relative, proposal_root, "baseline snapshot", allow_missing=False
        )
    except brownfield_inventory.PathSafetyError:
        raise _validation_error("baseline snapshot is missing or outside the proposal") from None
    if not snapshot.is_file():
        raise _validation_error("baseline snapshot is not a regular file")
    try:
        return snapshot.read_bytes()
    except OSError:
        raise _validation_error("baseline snapshot cannot be read") from None


def load_and_validate_baseline(proposal_root: Path) -> BaselineManifest:
    """Load and fully validate the lossless baseline without mutating files."""

    root = Path(proposal_root)
    lexical_manifest = root / "baseline-manifest.json"
    try:
        lexical_manifest.lstat()
    except FileNotFoundError:
        raise LegacyBaselineRequiredError(
            "Legacy proposal baseline is missing; use explicit baseline adoption."
        ) from None
    except OSError:
        raise _validation_error("baseline manifest is unsafe or outside the proposal") from None
    try:
        manifest_path = brownfield_inventory.safe_relative_path(
            "baseline-manifest.json", root, "baseline manifest", allow_missing=False
        )
    except brownfield_inventory.PathSafetyError:
        raise _validation_error("baseline manifest is unsafe or outside the proposal") from None
    if not manifest_path.is_file():
        raise _validation_error("baseline manifest is not a regular file")
    try:
        raw = json.loads(manifest_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise _validation_error("baseline manifest is malformed") from None
    if not isinstance(raw, dict):
        raise _validation_error("baseline manifest must be an object")

    schema_version = _required_string(raw.get("schema_version"), "schema version")
    if schema_version != BASELINE_SCHEMA_VERSION:
        raise _validation_error(f"unsupported schema version {schema_version!r}")
    bundle_version = _required_string(raw.get("bundle_version"), "bundle version")
    if bundle_version != BASELINE_BUNDLE_VERSION:
        raise _validation_error(f"unsupported bundle version {bundle_version!r}")
    source_revision = _required_string(raw.get("source_revision"), "source revision")
    evidence_digest = _required_string(raw.get("evidence_digest"), "evidence digest")
    generated_at = _required_string(raw.get("generated_at"), "generated date")
    raw_files = raw.get("files")
    if not isinstance(raw_files, list):
        raise _validation_error("files must be a list")

    files: list[BaselineFile] = []
    seen: set[str] = set()
    previous: str | None = None
    for raw_file in raw_files:
        if not isinstance(raw_file, dict):
            raise _validation_error("baseline file entry must be an object")
        path = _safe_relative_path(raw_file.get("path"), "reviewed")
        if path in seen:
            raise _validation_error(f"duplicate reviewed path {path!r}")
        if previous is not None and path <= previous:
            raise _validation_error("baseline file paths must use strict sorted order")
        seen.add(path)
        previous = path

        baseline_path = _safe_relative_path(raw_file.get("baseline_path"), "snapshot")
        digest = _required_string(raw_file.get("sha256"), "hash")
        if not _SHA256_RE.fullmatch(digest):
            raise _validation_error(f"invalid hash for {path!r}")
        byte_length = raw_file.get("byte_length")
        if isinstance(byte_length, bool) or not isinstance(byte_length, int) or byte_length < 0:
            raise _validation_error(f"invalid byte length for {path!r}")
        renderer_id = _required_string(raw_file.get("renderer_id"), "renderer id")
        renderer_version = _required_string(
            raw_file.get("renderer_version"), "renderer version"
        )
        dependencies = raw_file.get("evidence_dependencies")
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) and item for item in dependencies
        ):
            raise _validation_error(f"invalid evidence dependencies for {path!r}")
        text_policy = _required_string(raw_file.get("text_policy"), "text policy")

        snapshot = _read_snapshot(root, baseline_path)
        if len(snapshot) != byte_length:
            raise _validation_error(f"baseline snapshot length mismatch for {path!r}")
        if hashlib.sha256(snapshot).hexdigest() != digest:
            raise _validation_error(f"baseline snapshot hash mismatch for {path!r}")
        files.append(
            BaselineFile(
                path,
                digest,
                byte_length,
                baseline_path,
                renderer_id,
                renderer_version,
                tuple(dependencies),
                text_policy,
            )
        )

    return BaselineManifest(
        schema_version,
        source_revision,
        evidence_digest,
        bundle_version,
        generated_at,
        tuple(files),
    )


def classify_refresh(baseline: bytes, reviewed: bytes, candidate: bytes) -> RefreshOutcome:
    """Classify byte sequences using the ADR-026 three-way truth table."""

    if reviewed == baseline:
        return RefreshOutcome.UNCHANGED if candidate == baseline else RefreshOutcome.UPSTREAM_ONLY
    if candidate == baseline:
        return RefreshOutcome.USER_ONLY
    if reviewed == candidate:
        return RefreshOutcome.CONVERGENT
    return RefreshOutcome.CONFLICT


def _candidate_map(candidates: Mapping[str, bytes]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for raw_path, value in candidates.items():
        path = _safe_relative_path(raw_path, "candidate")
        if not isinstance(value, bytes):
            raise _validation_error(f"candidate bytes are invalid for {path!r}")
        if path in result:
            raise _validation_error(f"duplicate candidate path {path!r}")
        result[path] = value
    return result


def _resolved_result(
    path: str,
    outcome: RefreshOutcome,
    reviewed: bytes,
    candidate: bytes,
    resolutions: Mapping[str, str] | None,
) -> tuple[bytes | None, str | None]:
    if outcome is RefreshOutcome.UPSTREAM_ONLY:
        return candidate, None
    if outcome in (RefreshOutcome.UNCHANGED, RefreshOutcome.USER_ONLY, RefreshOutcome.CONVERGENT):
        return reviewed, None
    if resolutions is None:
        return None, None
    choice = resolutions.get(path)
    if choice not in ("reviewed", "candidate"):
        raise ProposalConflictError(
            f"Conflict resolution for {path!r} requires exact choice 'reviewed' or 'candidate'."
        )
    return (reviewed if choice == "reviewed" else candidate), choice


def plan_refresh(
    proposal_root: Path,
    candidates: Mapping[str, bytes],
    *,
    resolutions: Mapping[str, str] | None = None,
) -> ProposalRefreshPlan:
    """Build a deterministic, non-mutating three-way refresh plan."""

    root = Path(proposal_root)
    baseline = load_and_validate_baseline(root)
    candidate_map = _candidate_map(candidates)
    expected = {item.path for item in baseline.files}
    if set(candidate_map) != expected:
        raise _validation_error("candidate paths must exactly match baseline paths")
    if resolutions is not None and any(path not in expected for path in resolutions):
        raise ProposalConflictError("Resolution path does not identify a baseline conflict.")

    items: list[ProposalRefreshItem] = []
    conflicts: list[str] = []
    for baseline_file in baseline.files:
        path = baseline_file.path
        baseline_bytes = _read_snapshot(root, baseline_file.baseline_path)
        try:
            reviewed_path = brownfield_inventory.safe_relative_path(
                path, root, "reviewed proposal", allow_missing=False
            )
        except brownfield_inventory.PathSafetyError:
            raise _validation_error(f"reviewed proposal file is unsafe for {path!r}") from None
        try:
            reviewed_bytes = reviewed_path.read_bytes()
        except OSError:
            raise _validation_error(f"reviewed proposal file is missing for {path!r}") from None
        candidate_bytes = candidate_map[path]
        outcome = classify_refresh(baseline_bytes, reviewed_bytes, candidate_bytes)
        result_bytes, resolution = _resolved_result(
            path, outcome, reviewed_bytes, candidate_bytes, resolutions
        )
        if outcome is RefreshOutcome.CONFLICT and resolution is None:
            conflicts.append(path)
        items.append(
            ProposalRefreshItem(
                path,
                outcome,
                baseline_bytes,
                reviewed_bytes,
                candidate_bytes,
                result_bytes,
                path,
                f".candidate/{path}",
                baseline_file.baseline_path,
                resolution,
            )
        )
    if resolutions is not None and conflicts:
        raise ProposalConflictError(
            "Every proposal conflict requires an explicit per-file resolution."
        )
    return ProposalRefreshPlan(tuple(items), tuple(conflicts), bool(conflicts))


def plan_baseline_adoption(
    proposal_root: Path,
    candidates: Mapping[str, bytes],
    *,
    resolutions: Mapping[str, str] | None = None,
) -> ProposalRefreshPlan:
    """Preview explicit side-by-side baseline adoption for a legacy proposal."""

    root = Path(proposal_root)
    if (root / "baseline-manifest.json").exists() or (root / ".baseline").exists():
        raise BaselineValidationError(
            "Baseline state already exists; validate it instead of legacy baseline adoption."
        )
    candidate_map = _candidate_map(candidates)
    if resolutions is not None and any(path not in candidate_map for path in resolutions):
        raise ProposalConflictError("Resolution path does not identify an adoption item.")

    items: list[ProposalRefreshItem] = []
    conflicts: list[str] = []
    for path in sorted(candidate_map):
        try:
            reviewed_path = brownfield_inventory.safe_relative_path(
                path, root, "reviewed proposal", allow_missing=False
            )
        except brownfield_inventory.PathSafetyError:
            raise BaselineValidationError(
                f"Legacy reviewed proposal file is unsafe for {path!r}; baseline adoption stopped."
            ) from None
        try:
            reviewed = reviewed_path.read_bytes()
        except OSError:
            raise BaselineValidationError(
                f"Legacy reviewed proposal file is missing for {path!r}; baseline adoption stopped."
            ) from None
        candidate = candidate_map[path]
        outcome = RefreshOutcome.CONVERGENT if reviewed == candidate else RefreshOutcome.CONFLICT
        result, resolution = _resolved_result(path, outcome, reviewed, candidate, resolutions)
        if outcome is RefreshOutcome.CONFLICT and resolution is None:
            conflicts.append(path)
        items.append(
            ProposalRefreshItem(
                path,
                outcome,
                candidate,
                reviewed,
                candidate,
                result,
                path,
                f".candidate/{path}",
                f".baseline/{path}",
                resolution,
            )
        )
    if resolutions is not None and conflicts:
        raise ProposalConflictError(
            "Every legacy baseline conflict requires an explicit per-file resolution."
        )
    return ProposalRefreshPlan(
        tuple(items),
        tuple(conflicts),
        bool(conflicts),
        legacy_baseline_adoption=True,
        requires_exact_approval=True,
    )
