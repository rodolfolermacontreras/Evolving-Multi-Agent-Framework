"""Preview-bound brownfield transaction, rollback, and recovery mechanics.

The module deliberately contains only mutation mechanics.  Callers must provide an
already validated preview, explicit authorization, a dedicated same-volume
workspace, candidate bytes, and a staged structural readiness callback.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import uuid
import weakref
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Callable, Mapping

from brownfield_manifest import Preview, preview_hash as calculate_preview_hash

_SENTINEL_NAME = ".sdd-disposable-fixture.json"
_SENTINEL_SCHEMA = "sdd-058-disposable-root@1"
_ATOMIC_JOURNAL_REPLACE = os.replace
_TRANSACTION_AUTHORIZATIONS: dict[str, ApplyAuthorization] = {}
_JOURNAL_REQUIRED_KEYS = {
    "schema_version", "transaction_id", "target_fingerprint", "target_head",
    "preview_hash", "state", "stage_root", "backup_root", "operations",
    "target", "workspace", "lock_path", "recovery_command",
    "reviewed_proposal_path", "target_identity", "workspace_identity",
    "backup_parent_identity", "backup_root_identity",
}
_JOURNAL_OPTIONAL_KEYS = {"reviewed_proposal"}
_OPERATION_KEYS = {
    "sequence", "destination", "operation", "preimage", "candidate",
    "backup", "state",
}


class TransactionError(RuntimeError):
    """Base transaction-domain error."""


class AuthorizationError(TransactionError):
    pass


class FixtureAuthorizationError(AuthorizationError):
    pass


class PreflightError(TransactionError):
    pass


class StagingError(TransactionError):
    pass


class TransactionLockedError(TransactionError):
    pass


class RecoveryRequiredError(TransactionError):
    pass


class CleanupNotEligibleError(TransactionError):
    pass


class InjectedInterruption(BaseException):
    """Simulate process termination without entering normal rollback handling."""


class FailureInjector:
    def __init__(self, fail_at: str | None = None) -> None:
        self.fail_at = fail_at
        self.seen: list[str] = []

    def __call__(self, boundary: str) -> None:
        self.seen.append(boundary)
        if boundary == self.fail_at:
            if ":" in boundary or "preimage-journal-flush" in boundary:
                raise InjectedInterruption(boundary)
            raise TransactionError(f"injected failure: {boundary}")


def _ATOMIC_DESTINATION_REPLACE(source: Path, destination: Path) -> None:
    os.replace(source, destination)


class AuthorizationKind(Enum):
    OWNER_RECEIPT = "owner-receipt"
    VERIFIED_FIXTURE = "verified-fixture"


class OperationState(Enum):
    PREPARED = "prepared"
    APPLIED = "applied"
    VERIFIED = "verified"


class JournalState(Enum):
    STAGING = "staging"
    STAGED = "staged"
    BACKED_UP = "backed-up"
    PROMOTING = "promoting"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling-back"
    ROLLED_BACK = "rolled-back"
    RECOVERY_REQUIRED = "recovery-required"


@dataclass(frozen=True)
class ApplyAuthorization:
    kind: AuthorizationKind
    target_fingerprint: str
    target_identity: tuple[int, int]
    workspace_location: str
    workspace_identity: tuple[int, int]
    target_head: str
    preview_hash: str
    backup_location: str
    backup_root_identity: tuple[int, int]
    recovery_command: str
    approved_by: str
    approved_at: str
    fixture_root: Path | None


class _LiveCapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: weakref.WeakValueDictionary[str, ApplyAuthorization] = (
            weakref.WeakValueDictionary()
        )

    def register(self, capability: ApplyAuthorization) -> None:
        self._capabilities[uuid.uuid4().hex] = capability

    def contains(self, capability: ApplyAuthorization) -> bool:
        return any(candidate is capability for candidate in tuple(self._capabilities.values()))


_OWNER_RECEIPTS = _LiveCapabilityRegistry()
_FIXTURE_AUTHORIZATIONS = _LiveCapabilityRegistry()


@dataclass(frozen=True)
class TransactionOperation:
    sequence: int
    destination: str
    operation: str
    preimage: dict[str, object]
    candidate: dict[str, object]
    backup: dict[str, object] | None
    state: OperationState


@dataclass(frozen=True)
class TransactionJournal:
    schema_version: str
    transaction_id: str
    target_fingerprint: str
    target_identity: dict[str, int]
    workspace_identity: dict[str, int]
    backup_parent_identity: dict[str, int]
    backup_root_identity: dict[str, int]
    target_head: str
    preview_hash: str
    state: JournalState
    stage_root: str
    backup_root: str
    operations: tuple[TransactionOperation, ...]


@dataclass(frozen=True)
class TransactionContext:
    transaction_id: str
    authorization: ApplyAuthorization
    target: Path
    workspace: Path
    stage_root: Path
    backup_root: Path
    journal_path: Path
    lock_path: Path
    preview_hash: str
    target_head: str
    operations: tuple[TransactionOperation, ...]
    reviewed_proposal: Path
    target_identity: tuple[int, int]
    workspace_identity: tuple[int, int]
    backup_parent_identity: tuple[int, int]
    backup_root_identity: tuple[int, int]


@dataclass(frozen=True)
class StagedCandidate:
    root: Path
    operations: tuple[TransactionOperation, ...]


@dataclass(frozen=True)
class TransactionResult:
    exit_code: int
    status: str
    verified: bool
    recovery_command: str
    message: str


@dataclass(frozen=True)
class RecoveryInspection:
    state: str
    operation_states: dict[str, str]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def target_fingerprint(target: Path) -> str:
    return _sha(_canonical(Path(target)).encode("utf-8"))


def _filesystem_identity(path: Path) -> tuple[int, int]:
    path = Path(path)
    if is_link_or_reparse_point(path) or not path.is_dir():
        raise TransactionError("trusted root is absent, linked, or reparsed")
    metadata = path.stat(follow_symlinks=False)
    identity = (int(metadata.st_dev), int(metadata.st_ino))
    if identity[1] == 0:
        raise TransactionError("trusted root does not expose a stable filesystem identity")
    return identity


def _require_filesystem_identity(path: Path, expected: tuple[int, int]) -> None:
    if _filesystem_identity(path) != expected:
        raise TransactionError("trusted root filesystem identity changed")


def _trusted_identity_path(
    path: Path, root: Path, expected: tuple[int, int], *, allow_root: bool = False
) -> Path:
    _require_filesystem_identity(root, expected)
    return _trusted_existing_path(path, root, allow_root=allow_root)


def _target_destination(context: TransactionContext, destination: str) -> Path:
    _require_filesystem_identity(context.target, context.target_identity)
    return _mutation_destination(context.target, destination)


def _workspace_path(
    context: TransactionContext, path: Path, *, allow_root: bool = False
) -> Path:
    return _trusted_identity_path(
        path, context.workspace, context.workspace_identity, allow_root=allow_root
    )


def _backup_path(context: TransactionContext, path: Path) -> Path:
    return _trusted_identity_path(
        path, context.backup_root, context.backup_root_identity, allow_root=True
    )


def _identity_json(identity: tuple[int, int]) -> dict[str, int]:
    return {"device": identity[0], "inode": identity[1]}


def _identity_from_json(value: object) -> tuple[int, int]:
    if not isinstance(value, dict) or set(value) != {"device", "inode"}:
        raise _journal_error()
    device = value.get("device")
    inode = value.get("inode")
    if type(device) is not int or type(inode) is not int or device < 0 or inode <= 0:
        raise _journal_error()
    return device, inode


def _validate_registered_authorization(authorization: ApplyAuthorization) -> None:
    if authorization.kind is AuthorizationKind.OWNER_RECEIPT:
        if not _OWNER_RECEIPTS.contains(authorization):
            raise AuthorizationError("owner authorization is not a registered live capability")
    elif authorization.kind is AuthorizationKind.VERIFIED_FIXTURE:
        if not _FIXTURE_AUTHORIZATIONS.contains(authorization):
            raise AuthorizationError("verified-fixture authorization is not a registered live capability")
        if authorization.fixture_root is None or not _bound_sentinel(authorization.fixture_root):
            raise AuthorizationError("verified fixture proof is no longer valid")
    else:
        raise AuthorizationError("unsupported authorization kind")


def load_owner_authorization(receipt_path: Path) -> ApplyAuthorization:
    try:
        payload = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
        required = {
            "schema_version", "kind", "target_fingerprint", "target_head",
            "preview_hash", "backup_location", "recovery_command",
            "approved_by", "approved_at", "target_identity",
            "workspace_location", "workspace_identity", "backup_root_identity",
        }
        if payload["kind"] != AuthorizationKind.OWNER_RECEIPT.value:
            raise AuthorizationError("only owner-receipt authorization is deserializable")
        if set(payload) != required or payload["schema_version"] != "3":
            raise AuthorizationError("owner receipt has an invalid schema")
        auth = ApplyAuthorization(
            AuthorizationKind.OWNER_RECEIPT,
            str(payload["target_fingerprint"]), _identity_from_json(payload["target_identity"]),
            str(payload["workspace_location"]), _identity_from_json(payload["workspace_identity"]),
            str(payload["target_head"]),
            str(payload["preview_hash"]), str(payload["backup_location"]),
            _identity_from_json(payload["backup_root_identity"]),
            str(payload["recovery_command"]), str(payload["approved_by"]),
            str(payload["approved_at"]), None,
        )
    except AuthorizationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise AuthorizationError("owner receipt is unreadable or invalid") from exc
    _OWNER_RECEIPTS.register(auth)
    return auth


def _bound_sentinel(root: Path) -> bool:
    try:
        sentinel = root / _SENTINEL_NAME
        if is_link_or_reparse_point(root) or is_link_or_reparse_point(sentinel) or not sentinel.is_file():
            return False
        canonical = _canonical(root)
        expected = {
            "schema": _SENTINEL_SCHEMA,
            "root": canonical,
            "binding": _sha(f"{_SENTINEL_SCHEMA}\0{canonical}".encode("utf-8")),
        }
        return json.loads(sentinel.read_text(encoding="utf-8")) == expected
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False


def _strict_descendant(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return path.resolve() != parent.resolve()
    except ValueError:
        return False


def _has_link_component(path: Path, stop: Path | None = None) -> bool:
    current = path.absolute()
    stop_resolved = stop.resolve() if stop else None
    while True:
        if is_link_or_reparse_point(current):
            return True
        if stop_resolved is not None and current.resolve() == stop_resolved:
            return False
        if current.parent == current:
            return False
        current = current.parent


def authorize_verified_fixture(
    *, target: Path, fixture_root: Path, workspace: Path, preview_hash: str, target_head: str,
    backup_location: str, recovery_command: str,
) -> ApplyAuthorization:
    target = Path(target)
    fixture_root = Path(fixture_root)
    if not _bound_sentinel(fixture_root):
        raise FixtureAuthorizationError("fixture sentinel is absent, copied, or not root-bound")
    if not _strict_descendant(target, fixture_root):
        raise FixtureAuthorizationError("target must be a strict fixture-root descendant")
    if _has_link_component(target, fixture_root):
        raise FixtureAuthorizationError("linked fixture targets are forbidden")
    if not target.is_dir() or not (target / ".git").is_dir():
        raise FixtureAuthorizationError("target must be a disposable fixture git repository")
    # A nested repository is the mutation target; neither the sentinel root nor any
    # ancestor/real framework checkout can be authorized by this internal route.
    if (target / "INSTRUCTIONS.md").exists() and (target / "spec-driven-development").exists():
        raise FixtureAuthorizationError("real framework roots cannot be fixture-authorized")
    backup = Path(backup_location).resolve()
    if not _strict_descendant(backup, fixture_root) or _has_link_component(backup, fixture_root):
        raise FixtureAuthorizationError("fixture backup must remain below the bound fixture root")
    workspace = Path(workspace).resolve()
    if not _strict_descendant(workspace, fixture_root) or _has_link_component(workspace, fixture_root):
        raise FixtureAuthorizationError("fixture workspace must remain below the bound fixture root")
    auth = ApplyAuthorization(
        AuthorizationKind.VERIFIED_FIXTURE, target_fingerprint(target), _filesystem_identity(target),
        str(workspace), _filesystem_identity(workspace), target_head, preview_hash, str(backup),
        _filesystem_identity(backup), recovery_command, "verified-fixture", "in-memory",
        fixture_root.resolve(),
    )
    _FIXTURE_AUTHORIZATIONS.register(auth)
    return auth


def device_id(path: Path) -> int:
    path = Path(path)
    while not path.exists() and path.parent != path:
        path = path.parent
    return path.stat().st_dev


def is_link_or_reparse_point(path: Path) -> bool:
    path = Path(path)
    try:
        return path.is_symlink() or bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return path.is_symlink()


def is_supported_regular_path(path: Path) -> bool:
    path = Path(path)
    return not path.exists() or (path.is_file() and not is_link_or_reparse_point(path))


def probe_replace_access(path: Path) -> bool:
    path = Path(path)
    try:
        if path.exists():
            with path.open("rb+"):
                pass
        return os.access(path.parent, os.W_OK)
    except OSError:
        return False


def fsync_file(path: Path) -> None:
    with Path(path).open("rb+") as stream:
        os.fsync(stream.fileno())


def fsync_directory(path: Path) -> None:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        create_file.restype = wintypes.HANDLE
        flush_file_buffers = kernel32.FlushFileBuffers
        flush_file_buffers.argtypes = [wintypes.HANDLE]
        flush_file_buffers.restype = wintypes.BOOL
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [wintypes.HANDLE]
        close_handle.restype = wintypes.BOOL
        handle = create_file(str(Path(path)), 0x40000000, 0x00000007, None, 3, 0x02000000, None)
        if handle == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_last_error(), "directory durability handle could not be opened")
        try:
            if not flush_file_buffers(handle):
                raise OSError(ctypes.get_last_error(), "directory durability flush failed")
        finally:
            close_handle(handle)
        return
    descriptor = os.open(Path(path), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _safe_destination(target: Path, destination: str) -> Path:
    pure = PurePosixPath(destination)
    if pure.is_absolute() or not destination or any(part in {"", ".", ".."} for part in pure.parts):
        raise PreflightError(f"unsafe destination: {destination}")
    path = target.joinpath(*pure.parts)
    try:
        path.parent.resolve().relative_to(target.resolve())
    except ValueError as exc:
        raise PreflightError(f"destination escapes target: {destination}") from exc
    return path


def _mutation_destination(target: Path, destination: str) -> Path:
    path = _safe_destination(target, destination)
    if _has_link_component(path, target) or is_link_or_reparse_point(path):
        raise TransactionError(f"mutation destination is linked or reparsed: {destination}")
    return path


def _evidence_deletion_path(workspace: Path, path: Path) -> Path:
    workspace = Path(workspace)
    path = Path(path)
    evidence_root = workspace.parent
    try:
        relative = path.relative_to(evidence_root).as_posix()
    except ValueError as exc:
        raise TransactionError("transaction evidence escapes its workspace") from exc
    resolved = _safe_destination(evidence_root, relative)
    if _has_link_component(resolved, evidence_root) or is_link_or_reparse_point(resolved):
        raise TransactionError("transaction evidence is linked or reparsed")
    return resolved


def _authorized_evidence_path(
    workspace: Path,
    path: Path,
    authoritative_root: Path,
    expected_identity: tuple[int, int],
) -> Path:
    resolved = _evidence_deletion_path(workspace, path)
    _require_filesystem_identity(authoritative_root, expected_identity)
    return resolved


def _path_record(path: Path) -> dict[str, object]:
    exists = path.exists()
    return {
        "exists": exists,
        "sha256": _sha(path.read_bytes()) if exists else None,
        "size": path.stat().st_size if exists else 0,
        "portable_mode": stat.S_IMODE(path.stat().st_mode) if exists else None,
    }


def _pid_active(pid: int) -> bool:
    # The lock is created and consumed locally by this process.  A differing PID
    # is treated as stale and requires explicit recovery rather than probing an
    # unrelated process (which is neither portable nor race-free on Windows).
    return pid == os.getpid()


def preflight(
    preview: Preview, authorization: ApplyAuthorization, target: Path,
    workspace: Path, *, target_head: str, candidate_bytes: Mapping[str, bytes],
    reviewed_proposal: Path,
) -> TransactionContext:
    target = Path(target).resolve()
    workspace = Path(workspace).resolve()
    proposal = Path(reviewed_proposal).resolve()
    actual_preview_hash = calculate_preview_hash(preview)

    _validate_registered_authorization(authorization)

    if authorization.target_fingerprint != target_fingerprint(target):
        raise AuthorizationError("authorization target fingerprint is stale")
    if authorization.target_identity != _filesystem_identity(target):
        raise AuthorizationError("authorization target filesystem identity is stale")
    if Path(authorization.workspace_location).resolve() != workspace:
        raise AuthorizationError("authorization workspace does not match")
    if authorization.workspace_identity != _filesystem_identity(workspace):
        raise AuthorizationError("authorization workspace filesystem identity is stale")
    if authorization.target_head != target_head:
        raise AuthorizationError("authorization target head is stale")
    if authorization.preview_hash != actual_preview_hash:
        raise AuthorizationError("authorization preview hash is stale")
    if not authorization.recovery_command:
        raise AuthorizationError("authorization recovery command is required")
    if Path(authorization.backup_location).resolve() == target or target in Path(authorization.backup_location).resolve().parents:
        raise AuthorizationError("backup cannot be the target or inside it")
    if authorization.backup_root_identity != _filesystem_identity(
        Path(authorization.backup_location).resolve()
    ):
        raise AuthorizationError("authorization backup filesystem identity is stale")
    if not target.is_dir() or is_link_or_reparse_point(target):
        raise PreflightError("target must be a regular directory")
    if workspace.parent != target.parent or workspace == target:
        raise PreflightError("transaction workspace must be a sibling of target")
    if is_link_or_reparse_point(workspace) or ".git" in workspace.parts:
        raise PreflightError("linked or git-internal workspaces are forbidden")
    if device_id(workspace) != device_id(target):
        raise PreflightError("workspace and target must use the same volume")
    lock_path = workspace / "transaction.lock"
    journal_path = workspace / "transaction.json"
    if journal_path.exists():
        existing = _read_journal(journal_path)
        if existing.get("state") == JournalState.RECOVERY_REQUIRED.value:
            raise RecoveryRequiredError("the retained transaction requires explicit recovery")
    if lock_path.exists():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise RecoveryRequiredError("unreadable transaction lock requires recovery")
        if _pid_active(int(lock.get("pid", -1))):
            raise TransactionLockedError("an active transaction holds this workspace")
        raise RecoveryRequiredError("a stale transaction lock requires explicit recovery")
    if journal_path.exists():
        raise RecoveryRequiredError("an existing transaction journal requires recovery or cleanup")
    try:
        proposal.relative_to(target)
    except ValueError as exc:
        raise PreflightError("reviewed proposal must be inside target") from exc
    if proposal.exists() and (not proposal.is_dir() or _has_link_component(proposal, target)):
        raise PreflightError("reviewed proposal is not a regular directory")

    operations: list[TransactionOperation] = []
    needed = 0
    for item in preview.items:
        if item.category not in {"create", "replace", "runtime-initialize"}:
            continue
        path = _safe_destination(target, item.destination)
        if _has_link_component(path, target):
            raise PreflightError(f"link/reparse destination is forbidden: {item.destination}")
        if not is_supported_regular_path(path):
            raise PreflightError(f"unsupported special destination: {item.destination}")
        if path.exists() and not probe_replace_access(path):
            raise PreflightError(f"destination is locked: {item.destination}")
        data = candidate_bytes.get(item.destination)
        if data is None or _sha(data) != item.after_sha256:
            raise PreflightError(f"candidate hash mismatch: {item.destination}")
        preimage = _path_record(path)
        if preimage["sha256"] != item.before_sha256:
            raise PreflightError(f"preview preimage is stale: {item.destination}")
        needed += len(data) + int(preimage["size"])
        operations.append(TransactionOperation(
            len(operations), item.destination, item.operation, preimage,
            {"sha256": item.after_sha256, "size": len(data)}, None,
            OperationState.PREPARED,
        ))
    if shutil.disk_usage(workspace).free < max(needed * 2, 1):
        raise PreflightError("insufficient staging and backup capacity")

    transaction_id = uuid.uuid4().hex
    stage_root = workspace / f"stage-{transaction_id}"
    backup_root = Path(authorization.backup_location).resolve()
    if backup_root == workspace or workspace in backup_root.parents:
        raise PreflightError("backup root must not contain the workspace")
    context = TransactionContext(
        transaction_id, authorization, target, workspace, stage_root, backup_root,
        journal_path, lock_path, actual_preview_hash, target_head, tuple(operations), proposal,
        _filesystem_identity(target), _filesystem_identity(workspace),
        _filesystem_identity(backup_root.parent),
        _filesystem_identity(backup_root),
    )
    workspace.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps({"schema_version": "1", "transaction_id": transaction_id, "pid": os.getpid()}, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    _write_journal(context, JournalState.STAGING, context.operations)
    _TRANSACTION_AUTHORIZATIONS[transaction_id] = authorization
    return context


def bind_commit_artifacts(
    context: TransactionContext,
    artifacts: Mapping[str, bytes],
) -> None:
    """Reject candidate bytes that were absent from the approved preview."""

    del context, artifacts
    raise PreflightError("commit artifact is absent from the approved preview")


def _operation_json(operation: TransactionOperation) -> dict[str, object]:
    value = asdict(operation)
    value["state"] = operation.state.value
    return value


def _proposal_record(context: TransactionContext) -> dict[str, object] | None:
    record_path = _backup_path(context, context.backup_root / "reviewed-proposal")
    proposal_path = _trusted_identity_path(
        context.reviewed_proposal, context.target, context.target_identity
    )
    proposal_relative = context.reviewed_proposal.relative_to(context.target).as_posix()
    proposal_was_absent = any(
        operation.destination.startswith(proposal_relative + "/")
        and not operation.preimage["exists"]
        for operation in context.operations
    ) and not record_path.exists()
    if not proposal_path.exists() or proposal_was_absent:
        return {"exists": False, "preview_hash": context.preview_hash}
    if not record_path.exists():
        return None
    files = sorted(path for path in proposal_path.rglob("*") if path.is_file())
    if len(files) == 1:
        source = _trusted_identity_path(files[0], context.target, context.target_identity)
        backup = _backup_path(context, record_path / source.relative_to(proposal_path))
        return {"path": str(source), "sha256": _sha(source.read_bytes()), "backup_path": str(backup), "bytes_preserved": backup.read_bytes() == source.read_bytes()}
    digest = hashlib.sha256()
    for source in files:
        source = _trusted_identity_path(source, context.target, context.target_identity)
        digest.update(source.relative_to(proposal_path).as_posix().encode())
        digest.update(source.read_bytes())
    return {"path": str(context.reviewed_proposal), "sha256": digest.hexdigest(), "backup_path": str(record_path), "bytes_preserved": True}


def _write_journal(
    context: TransactionContext, state: JournalState,
    operations: tuple[TransactionOperation, ...], *, include_proposal: bool = True,
) -> None:
    journal = TransactionJournal(
        "1.1", context.transaction_id, target_fingerprint(context.target),
        _identity_json(context.target_identity), _identity_json(context.workspace_identity),
        _identity_json(context.backup_parent_identity), _identity_json(context.backup_root_identity),
        context.target_head,
        context.preview_hash, state, str(context.stage_root), str(context.backup_root), operations,
    )
    payload = asdict(journal)
    payload["state"] = state.value
    payload["operations"] = [_operation_json(operation) for operation in operations]
    payload["target"] = str(context.target)
    payload["workspace"] = str(context.workspace)
    payload["lock_path"] = str(context.lock_path)
    payload["recovery_command"] = context.authorization.recovery_command
    payload["reviewed_proposal_path"] = str(context.reviewed_proposal)
    proposal = _proposal_record(context) if include_proposal else None
    if proposal is not None:
        payload["reviewed_proposal"] = proposal
    journal_parent = _workspace_path(context, context.journal_path.parent, allow_root=True)
    journal_parent.mkdir(parents=True, exist_ok=True)
    temporary = _workspace_path(context, context.journal_path.with_suffix(".json.tmp"))
    temporary.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    temporary = _workspace_path(context, temporary)
    journal_path = _workspace_path(context, context.journal_path)
    _ATOMIC_JOURNAL_REPLACE(temporary, journal_path)
    journal_path = _workspace_path(context, journal_path)
    fsync_file(journal_path)
    fsync_directory(_workspace_path(context, journal_path.parent, allow_root=True))


def stage_candidate(
    context: TransactionContext,
    materializer: Callable[[Path, TransactionOperation], None],
    structural_check: Callable[..., object], *, injector: FailureInjector | None = None,
) -> StagedCandidate:
    try:
        if injector:
            injector("before-stage-reset")
        stage_root = _workspace_path(context, context.stage_root)
        if stage_root.exists():
            stage_root = _workspace_path(context, context.stage_root)
            shutil.rmtree(stage_root)
        stage_root = _workspace_path(context, context.stage_root)
        stage_root.mkdir(parents=True)
        for operation in context.operations:
            materializer(stage_root, operation)
        stage_root = _workspace_path(context, context.stage_root)
        staged_paths = tuple(stage_root.rglob("*"))
        if any(is_link_or_reparse_point(path) for path in staged_paths):
            raise StagingError("staged candidate contains a linked or reparsed path")
        actual = {path.relative_to(stage_root).as_posix() for path in staged_paths if path.is_file()}
        expected = {operation.destination for operation in context.operations}
        if actual != expected:
            raise StagingError("staged candidate is incomplete or contains unapproved paths")
        for operation in context.operations:
            path = _trusted_identity_path(
                stage_root / PurePosixPath(operation.destination), context.workspace,
                context.workspace_identity,
            )
            if is_link_or_reparse_point(path) or _sha(path.read_bytes()) != operation.candidate["sha256"]:
                raise StagingError(f"staged candidate hash mismatch: {operation.destination}")
        report = structural_check(stage_root, context.operations, context)
        if getattr(report, "exit_code", 1) != 0:
            raise StagingError("staged structural readiness failed")
        _write_journal(context, JournalState.STAGED, context.operations)
        return StagedCandidate(stage_root, context.operations)
    except StagingError:
        raise
    except Exception as exc:
        raise StagingError("candidate materialization or structural readiness failed") from exc


def backup(context: TransactionContext, *, injector: FailureInjector | None = None) -> None:
    if not _workspace_path(context, context.stage_root).is_dir():
        raise TransactionError("complete staging is required before backup")
    operations: list[TransactionOperation] = []
    try:
        if injector:
            injector("before-backup-create")
        backup_root = _backup_path(context, context.backup_root)
        if any(backup_root.iterdir()):
            raise TransactionError("authorized backup root must be empty before backup")
        for operation in context.operations:
            source = _target_destination(context, operation.destination)
            backup_record = None
            if operation.preimage["exists"]:
                destination = backup_root / "destinations" / PurePosixPath(operation.destination)
                destination_parent = _backup_path(context, destination.parent)
                destination_parent.mkdir(parents=True, exist_ok=True)
                source = _target_destination(context, operation.destination)
                destination = _backup_path(context, destination)
                shutil.copyfile(source, destination)
                if operation.preimage["portable_mode"] is not None:
                    destination = _backup_path(context, destination)
                    destination.chmod(int(operation.preimage["portable_mode"]))
                destination = _backup_path(context, destination)
                fsync_file(destination)
                fsync_directory(_backup_path(context, destination.parent))
                persisted = _path_record(destination)
                if (
                    persisted["sha256"] != operation.preimage["sha256"]
                    or persisted["size"] != operation.preimage["size"]
                    or persisted["portable_mode"] != operation.preimage["portable_mode"]
                ):
                    raise TransactionError(f"backup verification failed: {operation.destination}")
                backup_record = {"path": str(destination), "sha256": operation.preimage["sha256"]}
            operations.append(replace(operation, backup=backup_record))
        if _trusted_identity_path(context.reviewed_proposal, context.target, context.target_identity).exists():
            proposal_source = _trusted_identity_path(
                context.reviewed_proposal, context.target, context.target_identity
            )
            proposal_paths = tuple(proposal_source.rglob("*"))
            if any(is_link_or_reparse_point(source) for source in proposal_paths):
                raise TransactionError("reviewed proposal backup contains a linked or reparsed path")
            proposal_backup = _backup_path(context, backup_root / "reviewed-proposal")
            shutil.copytree(proposal_source, proposal_backup, copy_function=shutil.copy2)
            for source in proposal_paths:
                if is_link_or_reparse_point(source):
                    raise TransactionError("reviewed proposal backup contains a linked or reparsed path")
                if source.is_dir():
                    continue
                if not source.is_file():
                    raise TransactionError("reviewed proposal backup contains a special path")
                source = _trusted_identity_path(source, context.target, context.target_identity)
                copied = _backup_path(
                    context, proposal_backup / source.relative_to(proposal_source)
                )
                if is_link_or_reparse_point(copied) or not copied.is_file():
                    raise TransactionError("reviewed proposal backup is incomplete")
                fsync_file(copied)
                fsync_directory(_backup_path(context, copied.parent))
                source_record = _path_record(source)
                copied_record = _path_record(copied)
                if copied_record != source_record:
                    raise TransactionError("reviewed proposal backup verification failed")
        fsync_directory(_backup_path(context, backup_root))
    except (OSError, TransactionError) as exc:
        raise TransactionError("backup could not be durably verified") from exc
    updated = tuple(operations)
    object.__setattr__(context, "operations", updated)
    _write_journal(context, JournalState.BACKED_UP, updated)


def _transition(
    context: TransactionContext, operations: list[TransactionOperation], index: int,
    state: OperationState, injector: FailureInjector | None,
) -> None:
    name = PurePosixPath(operations[index].destination).name
    category = "runtime-initialize" if operations[index].destination.endswith("fleet.db") else ("replace" if operations[index].preimage["exists"] else "create")
    before = f"{category}:{state.value}:before-flush"
    after = f"{category}:{state.value}:after-flush"
    if injector:
        injector(before)
    operations[index] = replace(operations[index], state=state)
    _write_journal(context, JournalState.PROMOTING, tuple(operations))
    if injector:
        injector(after)


def promote(context: TransactionContext, *, injector: FailureInjector | None = None) -> TransactionResult:
    data = _read_journal(_workspace_path(context, context.journal_path))
    if data["state"] != JournalState.BACKED_UP.value:
        raise TransactionError("complete backup and preimage journal are required before promotion")
    operations = list(context.operations)
    try:
        if injector:
            injector("before-preimage-journal-flush")
        _write_journal(context, JournalState.PROMOTING, tuple(operations))
        if injector:
            injector("after-preimage-journal-flush")
            injector("before-first-promotion")
        for index, operation in enumerate(operations):
            destination = _target_destination(context, operation.destination)
            destination_parent = _trusted_identity_path(
                destination.parent, context.target, context.target_identity, allow_root=True
            )
            destination_parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.parent / f".{destination.name}.{context.transaction_id}.candidate"
            source = _trusted_identity_path(
                context.stage_root / PurePosixPath(operation.destination), context.workspace,
                context.workspace_identity,
            )
            temporary_relative = temporary.relative_to(context.target).as_posix()
            temporary = _target_destination(context, temporary_relative)
            shutil.copyfile(source, temporary)
            temporary = _target_destination(context, temporary_relative)
            fsync_file(temporary)
            _transition(context, operations, index, OperationState.PREPARED, injector)
            destination = _target_destination(context, operation.destination)
            temporary = _target_destination(context, temporary_relative)
            _ATOMIC_DESTINATION_REPLACE(temporary, destination)
            _transition(context, operations, index, OperationState.APPLIED, injector)
            destination = _target_destination(context, operation.destination)
            if _sha(destination.read_bytes()) != operation.candidate["sha256"]:
                raise TransactionError(f"candidate verification failed: {operation.destination}")
            _transition(context, operations, index, OperationState.VERIFIED, injector)
            if injector:
                category = "runtime-initialize" if operation.destination.endswith("fleet.db") else ("replace" if operation.preimage["exists"] else "create")
                injector(f"after-{category}")
        object.__setattr__(context, "operations", tuple(operations))
        _write_journal(context, JournalState.COMMITTED, tuple(operations))
        return TransactionResult(0, "committed", True, context.authorization.recovery_command, "transaction committed")
    except InjectedInterruption:
        raise
    except Exception:
        for operation in operations:
            try:
                destination = _target_destination(context, operation.destination)
            except TransactionError:
                continue
            temporary = destination.parent / f".{destination.name}.{context.transaction_id}.candidate"
            temporary_relative = temporary.relative_to(context.target).as_posix()
            temporary = _target_destination(context, temporary_relative)
            if temporary.exists():
                _target_destination(context, temporary_relative).unlink()
        object.__setattr__(context, "operations", tuple(operations))
        return rollback(context)


def _result(context: TransactionContext, exit_code: int, status: str, verified: bool, message: str) -> TransactionResult:
    return TransactionResult(exit_code, status, verified, context.authorization.recovery_command, message)


def _mark_recovery_required(context: TransactionContext, operations: tuple[TransactionOperation, ...]) -> TransactionResult:
    _write_journal(context, JournalState.RECOVERY_REQUIRED, operations)
    return _result(context, 3, "recovery-required", False, f"Recovery required. Run: {context.authorization.recovery_command}")


def rollback(context: TransactionContext, *, injector: FailureInjector | None = None) -> TransactionResult:
    operations = context.operations
    try:
        _write_journal(context, JournalState.ROLLING_BACK, operations)
        if injector:
            injector("open-handle")
        for operation in reversed(operations):
            destination = _target_destination(context, operation.destination)
            if operation.preimage["exists"]:
                if injector:
                    injector("rollback-replace")
                destination = _target_destination(context, operation.destination)
                if not operation.backup:
                    raise TransactionError("replacement backup is absent")
                temporary = destination.parent / f".{destination.name}.{context.transaction_id}.rollback"
                backup_source = _backup_path(context, Path(str(operation.backup["path"])))
                temporary_relative = temporary.relative_to(context.target).as_posix()
                temporary = _target_destination(context, temporary_relative)
                shutil.copyfile(backup_source, temporary)
                if operation.preimage["portable_mode"] is not None:
                    temporary = _target_destination(context, temporary_relative)
                    temporary.chmod(int(operation.preimage["portable_mode"]))
                temporary = _target_destination(context, temporary_relative)
                fsync_file(temporary)
                destination = _target_destination(context, operation.destination)
                temporary = _target_destination(context, temporary_relative)
                os.replace(temporary, destination)
                if operation.preimage["portable_mode"] is not None:
                    destination = _target_destination(context, operation.destination)
                    destination.chmod(int(operation.preimage["portable_mode"]))
            else:
                if destination.exists():
                    if injector:
                        injector("rollback-remove")
                    destination = _target_destination(context, operation.destination)
                    destination.unlink()
                parent = destination.parent
                while parent != context.target and parent != context.reviewed_proposal:
                    try:
                        relative_parent = parent.relative_to(context.target).as_posix()
                        _target_destination(context, relative_parent).rmdir()
                    except OSError:
                        break
                    parent = parent.parent
            destination = _target_destination(context, operation.destination)
            record = _path_record(destination)
            if record["exists"] != operation.preimage["exists"] or record["sha256"] != operation.preimage["sha256"]:
                raise TransactionError("rollback hash verification failed")
            if record["exists"] and record["portable_mode"] != operation.preimage["portable_mode"]:
                raise TransactionError("rollback mode verification failed")
        _write_journal(context, JournalState.ROLLED_BACK, operations)
        return _result(context, 1, "rolled-back", True, "transaction failed; verified rollback completed")
    except Exception:
        return _mark_recovery_required(context, operations)


def _read_journal(path: Path) -> dict[str, object]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecoveryRequiredError("transaction journal is unreadable") from exc


def _journal_error() -> RecoveryRequiredError:
    return RecoveryRequiredError("transaction journal is invalid or outside its authorized roots")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_content_record(
    record: object, *, preimage: bool
) -> dict[str, object]:
    expected = {"exists", "sha256", "size", "portable_mode"} if preimage else {"sha256", "size"}
    if not isinstance(record, dict) or set(record) != expected:
        raise _journal_error()
    exists = record.get("exists", True)
    digest = record.get("sha256")
    size = record.get("size")
    mode = record.get("portable_mode") if preimage else None
    if type(exists) is not bool or type(size) is not int or size < 0:
        raise _journal_error()
    if exists:
        if not _is_sha256(digest) or (preimage and (type(mode) is not int or not 0 <= mode <= 0o777)):
            raise _journal_error()
    elif digest is not None or size != 0 or mode is not None:
        raise _journal_error()
    return record


def _trusted_existing_path(path: Path, root: Path, *, allow_root: bool = False) -> Path:
    path = Path(path).absolute()
    root = Path(root).absolute()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise _journal_error() from exc
    if not allow_root and not relative.parts:
        raise _journal_error()
    current = root
    if is_link_or_reparse_point(current):
        raise _journal_error()
    for part in relative.parts:
        current = current / part
        if current.exists() and is_link_or_reparse_point(current):
            raise _journal_error()
    if is_link_or_reparse_point(path):
        raise _journal_error()
    try:
        resolved = path.resolve(strict=False)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise _journal_error() from exc
    return path


def _validated_journal(
    journal_path: Path, *, workspace: Path, target: Path
) -> dict[str, object]:
    workspace = Path(workspace).absolute()
    target = Path(target).absolute()
    journal_path = Path(journal_path).absolute()
    trusted_parent = workspace.parent
    if journal_path != workspace / "transaction.json":
        raise _journal_error()
    _trusted_existing_path(workspace, trusted_parent)
    _trusted_existing_path(journal_path, workspace)
    _trusted_existing_path(target, trusted_parent)
    payload = _read_journal(journal_path)
    if not isinstance(payload, dict) or not _JOURNAL_REQUIRED_KEYS.issubset(payload):
        raise _journal_error()
    if set(payload) - (_JOURNAL_REQUIRED_KEYS | _JOURNAL_OPTIONAL_KEYS):
        raise _journal_error()
    if payload.get("schema_version") != "1.1":
        raise _journal_error()
    transaction_id = payload.get("transaction_id")
    if not isinstance(transaction_id, str) or len(transaction_id) != 32:
        raise _journal_error()
    try:
        int(transaction_id, 16)
        JournalState(str(payload["state"]))
    except (TypeError, ValueError) as exc:
        raise _journal_error() from exc
    if Path(str(payload["workspace"])).absolute() != workspace:
        raise _journal_error()
    if Path(str(payload["target"])).absolute() != target:
        raise _journal_error()
    if payload["target_fingerprint"] != target_fingerprint(target):
        raise _journal_error()
    target_identity = _identity_from_json(payload["target_identity"])
    workspace_identity = _identity_from_json(payload["workspace_identity"])
    backup_parent_identity = _identity_from_json(payload["backup_parent_identity"])
    backup_root_identity = _identity_from_json(payload["backup_root_identity"])
    try:
        _require_filesystem_identity(target, target_identity)
        _require_filesystem_identity(workspace, workspace_identity)
    except TransactionError as exc:
        raise _journal_error() from exc
    expected_stage = workspace / f"stage-{transaction_id}"
    expected_lock = workspace / "transaction.lock"
    if Path(str(payload["stage_root"])).absolute() != expected_stage:
        raise _journal_error()
    if Path(str(payload["lock_path"])).absolute() != expected_lock:
        raise _journal_error()
    _trusted_existing_path(expected_stage, workspace)
    _trusted_existing_path(expected_lock, workspace)
    backup = Path(str(payload["backup_root"])).absolute()
    _trusted_existing_path(backup, trusted_parent)
    try:
        _require_filesystem_identity(backup.parent, backup_parent_identity)
        _require_filesystem_identity(backup, backup_root_identity)
    except TransactionError as exc:
        raise _journal_error() from exc
    proposal = Path(str(payload["reviewed_proposal_path"])).absolute()
    _trusted_existing_path(proposal, target)
    try:
        lock = json.loads(expected_lock.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _journal_error() from exc
    if set(lock) != {"schema_version", "transaction_id", "pid"}:
        raise _journal_error()
    if lock.get("schema_version") != "1" or lock.get("transaction_id") != transaction_id:
        raise _journal_error()
    operations = payload.get("operations")
    if not isinstance(operations, list):
        raise _journal_error()
    for sequence, item in enumerate(operations):
        if not isinstance(item, dict) or set(item) != _OPERATION_KEYS:
            raise _journal_error()
        if item.get("sequence") != sequence:
            raise _journal_error()
        destination = str(item.get("destination", ""))
        _safe_destination(target, destination)
        _trusted_existing_path(target / PurePosixPath(destination), target)
        preimage = _validate_content_record(item.get("preimage"), preimage=True)
        _validate_content_record(item.get("candidate"), preimage=False)
        if item.get("operation") not in {"copy", "render", "seed"}:
            raise _journal_error()
        backup_record = item.get("backup")
        if backup_record is not None:
            if not isinstance(backup_record, dict) or set(backup_record) != {"path", "sha256"}:
                raise _journal_error()
            if not preimage["exists"] or not _is_sha256(backup_record.get("sha256")):
                raise _journal_error()
            if backup_record["sha256"] != preimage["sha256"]:
                raise _journal_error()
            expected = backup / "destinations" / PurePosixPath(destination)
            if Path(str(backup_record["path"])).absolute() != expected:
                raise _journal_error()
            _trusted_existing_path(expected, backup)
        elif preimage["exists"] and payload["state"] not in {
            JournalState.STAGING.value,
            JournalState.STAGED.value,
        }:
            raise _journal_error()
        try:
            OperationState(str(item["state"]))
        except ValueError as exc:
            raise _journal_error() from exc
    return payload


def _operation_from_json(item: dict[str, object]) -> TransactionOperation:
    return TransactionOperation(
        int(item["sequence"]), str(item["destination"]), str(item["operation"]),
        dict(item["preimage"]), dict(item["candidate"]),
        dict(item["backup"]) if item.get("backup") else None,
        OperationState(str(item["state"])),
    )


def _validate_journal_authorization(
    payload: dict[str, object], authorization: ApplyAuthorization
) -> None:
    _validate_registered_authorization(authorization)
    expected = {
        "target_fingerprint": authorization.target_fingerprint,
        "target_identity": _identity_json(authorization.target_identity),
        "workspace": str(Path(authorization.workspace_location).resolve()),
        "workspace_identity": _identity_json(authorization.workspace_identity),
        "target_head": authorization.target_head,
        "preview_hash": authorization.preview_hash,
        "backup_root": str(Path(authorization.backup_location).resolve()),
        "backup_root_identity": _identity_json(authorization.backup_root_identity),
        "recovery_command": authorization.recovery_command,
    }
    for key, value in expected.items():
        actual = payload.get(key)
        if key == "backup_root":
            actual = str(Path(str(actual)).resolve())
        if actual != value:
            raise AuthorizationError(f"transaction journal does not match authorization: {key}")


def live_fixture_authorization(
    journal_path: Path, *, workspace: Path, target: Path
) -> ApplyAuthorization:
    payload = _validated_journal(journal_path, workspace=workspace, target=target)
    authorization = _TRANSACTION_AUTHORIZATIONS.get(str(payload["transaction_id"]))
    if authorization is None or authorization.kind is not AuthorizationKind.VERIFIED_FIXTURE:
        raise AuthorizationError("no live fixture authorization exists for this transaction")
    _validate_journal_authorization(payload, authorization)
    return authorization


def _context_from_journal(
    journal_path: Path, *, workspace: Path, target: Path,
    authorization: ApplyAuthorization,
) -> TransactionContext:
    payload = _validated_journal(journal_path, workspace=workspace, target=target)
    _validate_journal_authorization(payload, authorization)
    return TransactionContext(
        str(payload["transaction_id"]), authorization, Path(str(payload["target"])),
        Path(str(payload["workspace"])), Path(str(payload["stage_root"])),
        Path(str(payload["backup_root"])), Path(journal_path), Path(str(payload["lock_path"])),
        str(payload["preview_hash"]), str(payload["target_head"]),
        tuple(_operation_from_json(item) for item in payload["operations"]),
        Path(str(payload["reviewed_proposal_path"])),
        _identity_from_json(payload["target_identity"]),
        _identity_from_json(payload["workspace_identity"]),
        _identity_from_json(payload["backup_parent_identity"]),
        _identity_from_json(payload["backup_root_identity"]),
    )


def inspect_recovery(
    journal_path: Path, *, workspace: Path, target: Path,
    authorization: ApplyAuthorization,
) -> RecoveryInspection:
    payload = _validated_journal(journal_path, workspace=workspace, target=target)
    _validate_journal_authorization(payload, authorization)
    target = Path(target)
    states: dict[str, str] = {}
    for item in payload["operations"]:
        _require_filesystem_identity(target, _identity_from_json(payload["target_identity"]))
        destination = _mutation_destination(target, str(item["destination"]))
        if not destination.exists():
            states[str(item["destination"])] = "absent"
            continue
        digest = _sha(destination.read_bytes())
        preimage = item["preimage"]
        candidate = item["candidate"]
        if preimage.get("exists") and digest == preimage.get("sha256"):
            states[str(item["destination"])] = "preimage"
        elif digest == candidate.get("sha256"):
            states[str(item["destination"])] = "candidate"
        else:
            states[str(item["destination"])] = "unknown"
    return RecoveryInspection(str(payload["state"]), states)


def recover(
    journal_path: Path, *, action: str, workspace: Path, target: Path,
    authorization: ApplyAuthorization,
) -> TransactionResult:
    if action != "rollback":
        raise TransactionError("only explicit rollback recovery is supported")
    context = _context_from_journal(
        Path(journal_path), workspace=workspace, target=target,
        authorization=authorization,
    )
    inspection = inspect_recovery(
        journal_path, workspace=workspace, target=target,
        authorization=authorization,
    )
    if "unknown" in inspection.operation_states.values():
        return _mark_recovery_required(context, context.operations)
    # Restore every path, including candidates whose flushed journal state is stale.
    return_value = rollback(context)
    if return_value.exit_code == 1:
        return _result(context, 0, "rolled-back", True, "startup recovery completed")
    return return_value


def startup_recover(
    journal_path: Path, *, action: str, workspace: Path, target: Path,
    authorization: ApplyAuthorization,
) -> TransactionResult:
    return recover(
        journal_path, action=action, workspace=workspace, target=target,
        authorization=authorization,
    )


def cleanup(
    journal_path: Path, *, workspace: Path, target: Path,
    authorization: ApplyAuthorization,
) -> TransactionResult:
    journal_path = Path(journal_path)
    payload = _validated_journal(journal_path, workspace=workspace, target=target)
    _validate_journal_authorization(payload, authorization)
    if payload["state"] not in {JournalState.COMMITTED.value, JournalState.ROLLED_BACK.value}:
        raise CleanupNotEligibleError("only committed or rolled-back transactions are cleanup-eligible")
    stage = Path(str(payload["stage_root"]))
    backup = Path(str(payload["backup_root"]))
    workspace = Path(str(payload["workspace"]))
    workspace_identity = authorization.workspace_identity
    for path in (stage, backup):
        if path.exists():
            authoritative_root = backup if path == backup else workspace
            expected_identity = (
                authorization.backup_root_identity
                if path == backup
                else workspace_identity
            )
            shutil.rmtree(
                _authorized_evidence_path(
                    workspace, path, authoritative_root, expected_identity
                )
            )
    _authorized_evidence_path(
        workspace, journal_path, workspace, workspace_identity
    ).unlink()
    lock = Path(str(payload["lock_path"]))
    if lock.exists():
        _authorized_evidence_path(
            workspace, lock, workspace, workspace_identity
        ).unlink()
    fsync_directory(
        _authorized_evidence_path(
            workspace, workspace, workspace, workspace_identity
        )
    )
    return TransactionResult(0, "cleaned", True, str(payload["recovery_command"]), "transaction evidence cleaned explicitly")
